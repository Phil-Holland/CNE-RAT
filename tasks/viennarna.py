import sys, time, subprocess, base64, os
from Bio import SeqIO
from io import StringIO
sys.path.append('..')
from app import celery
from flask import Markup

# define the main report templates here, and fill out the contents later:
# overall report template
viennarna_template = """
# ViennaRNA Toolchain Output

## Overview

CNE sequence:

`{cne_id}`:
<pre>
{cne}
</pre>

Query sequences: 

{query_seqs}

---

{analyses}

"""

# a template used to display results for each CNE-RNA interaction
vienna_analysis_template = """
## Interaction {interaction_no}

Evaluating interactions between the CNE sequence and the 
following query sequence:

<pre>
{query}
</pre>

RNAcofold output:

<pre>
{cofold_output}
</pre>

<div class="row">
    <div class="column">
        <strong>Secondary structure prediction</strong>
        <hr>
        {cofold_ss_output}
    </div>
    <div class="column">
        <strong>Interaction dot-plot</strong>
        <hr>
        {cofold_dp_output}
        <hr>
        <p>
        The dot plot shows a matrix of squares with area proportional 
        to the pairing probability in the upper right half, and one square 
        for each pair in the minimum free energy structure in the lower 
        left half.
        </p>
    </div>
</div>

---
"""

def convert_ps_to_svg(filename, working_dir):
    p = subprocess.Popen(['dvisvgm', '-E', filename, '-v', '0', 
        '-o', filename + '.svg'],
        cwd=working_dir,
        stdout=subprocess.PIPE
    )
    output, err = p.communicate()
    output = output.decode("utf-8")

    contents = ''
    with open(working_dir + '/' + filename + '.svg') as f:
        contents = f.read()

    os.remove(working_dir + '/' + filename + '.svg')
    return contents

def get_sequences_from_fasta(fasta_string, limit=None):
    seq_io = StringIO(fasta_string)
    sequences_parsed = SeqIO.parse(seq_io, 'fasta')
    sequences = []
    for i, fasta in enumerate(sequences_parsed):
        # get sequence, and convert to uppercase
        sequence = str(fasta.seq).upper()
        seq_id = str(fasta.id)

        # make sure the sequence is only A,C,G,T/U
        for c in sequence:
            if not(c in ['A', 'C', 'G', 'T', 'U']):
                raise Exception('A sequence contains invalid character: %s' % c)
        sequences.append((seq_id, sequence))
        if limit:
            if i >= limit-1:
                break

    return sequences

@celery.task(name='viennarna')
def viennarna(config, working_dir):
    cne_sequences_fasta = config['config']['cne']
    query_sequences_fasta = config['config']['task_rna_rna_config']['query_sequences']    
    
    # parse the two fasta strings, and retrieve the sequences they contain
    cne_id, cne_sequence = get_sequences_from_fasta(cne_sequences_fasta, limit=1)[0]
    query_sequences = get_sequences_from_fasta(query_sequences_fasta)
    
    cofold_outputs = {}
    cofold_ss_outputs = {}
    cofold_dp_outputs = {}

    # iterate over all query sequences, and produce cofold output text for each
    for (seq_id, sequence) in query_sequences:
        print('Processing sequence: %s' % sequence)
        rnacofold_input = '>cofold\n{cne}&{query}'.format(
            cne=cne_sequence,
            query=sequence
        )
        p = subprocess.Popen(['RNAcofold', '-p'],
            cwd=working_dir, 
            stdout=subprocess.PIPE, 
            stdin=subprocess.PIPE
        )
        print('\"RNAcofold\" invoked with command: %s' % rnacofold_input)

        output, err = p.communicate(input=str.encode(rnacofold_input))
        output = output.decode("utf-8")
        cofold_outputs[seq_id] = output

        svg_ss = convert_ps_to_svg('cofold_ss.ps', working_dir)
        svg_dp = convert_ps_to_svg('cofold_dp.ps', working_dir)
        cofold_ss_outputs[seq_id] = svg_ss
        cofold_dp_outputs[seq_id] = svg_dp

    analyses = ''
    for i, (seq_id, sequence) in enumerate(query_sequences):
        analyses += vienna_analysis_template.format(
            interaction_no=str(i+1),
            query=sequence,
            cofold_output=cofold_outputs[seq_id],
            cofold_ss_output=cofold_ss_outputs[seq_id],
            cofold_dp_output=cofold_dp_outputs[seq_id]
        ) + '\n'

    # convert query sequence list into a presentable string
    query_sequences_display = ''
    for (seq_id, sequence) in query_sequences:
        query_sequences_display += '`%s`:\n\n<pre>%s</pre>\n\n' % (Markup.escape(seq_id), Markup.escape(sequence))

    return viennarna_template.format(
        cne=Markup.escape(cne_sequence),
        cne_id=Markup.escape(cne_id),
        query_seqs=query_sequences_display,
        analyses=analyses
    )