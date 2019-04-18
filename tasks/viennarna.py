import sys, time, subprocess, base64, os
sys.path.append('..')
from app import celery
from flask import Markup
from .shared import create_working_dir, get_sequences_from_fasta

# define the main report templates here, and fill out the contents later:
# overall report template
viennarna_template = """
# ViennaRNA Toolchain Output

## Overview

Query sequences: 

{query_seqs}

---

{analyses}

"""

# a template used to display just the output of an RNAduplex run
vienna_duplex_template = """
### RNAduplex output:

Also returning interactions within an energy range of `{deltaenergy} kcal/mol` 
from the *minimum free energy* solution.

<pre style="max-height: 40pc; overflow-y: scroll;">
{duplex_output}
</pre>
"""

# a template used to display just the output of an RNAcofold run
vienna_cofold_template = """
### RNAcofold output:

<pre style="max-height: 40pc; overflow-y: scroll;">
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
"""

# a template used to display results for each CNE-RNA interaction
vienna_analysis_template = """
## Query {interaction_no}

Evaluating interactions between the CNE sequence and the 
following query sequence:

<pre>
{query}
</pre>

{duplex_report}

{cofold_report}

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

@celery.task(name='viennarna')
def viennarna(config, uid):
    # create a working directory, based on the task uid
    working_dir = create_working_dir(uid, 'viennarna')

    # retrieve the relevent fields from the configuration object
    cne_sequences_fasta = config['cne']
    query_sequences_fasta = config['rna_rna_config']['query_sequences']

    run_rnaduplex = config['rna_rna_config']['vienna_config']['rnaduplex']
    rnaduplex_de = config['rna_rna_config']['vienna_config']['rnaduplex_config']['deltaenergy']
    run_rnacofold = config['rna_rna_config']['vienna_config']['rnacofold']
    
    # parse the two fasta strings, and retrieve the sequences they contain
    _, cne_sequence = get_sequences_from_fasta(cne_sequences_fasta, limit=1)[0]
    query_sequences = get_sequences_from_fasta(query_sequences_fasta)

    # analyses report sections
    analyses = ''

    # iterate over all query sequences, and produce cofold output text for each
    for i, (seq_id, sequence) in enumerate(query_sequences):
        print('Processing sequence: %s' % sequence)

        duplex_output = None
        cofold_output = None
        cofold_ss_output = None
        cofold_dp_output = None

        if run_rnaduplex:
            duplex_input = '>cne\n{cne}\n\n>query\n{query}'.format(
                cne=cne_sequence,
                query=sequence
            )
            p = subprocess.Popen(['RNAduplex', '-s', '-e', str(float(rnaduplex_de))],
                cwd=working_dir, 
                stdout=subprocess.PIPE, 
                stdin=subprocess.PIPE
            )
            print('\"RNAduplex\" invoked with input: %s' % duplex_input)

            output, err = p.communicate(input=str.encode(duplex_input))
            output = output.decode("utf-8")
            duplex_output = output

        if run_rnacofold:
            rnacofold_input = '>cofold\n{cne}&{query}'.format(
                cne=cne_sequence,
                query=sequence
            )
            p = subprocess.Popen(['RNAcofold', '-p'],
                cwd=working_dir, 
                stdout=subprocess.PIPE, 
                stdin=subprocess.PIPE
            )
            print('\"RNAcofold\" invoked with input: %s' % rnacofold_input)

            output, err = p.communicate(input=str.encode(rnacofold_input))
            output = output.decode("utf-8")
            cofold_output = output

            svg_ss = convert_ps_to_svg('cofold_ss.ps', working_dir)
            svg_dp = convert_ps_to_svg('cofold_dp.ps', working_dir)
            cofold_ss_output = svg_ss
            cofold_dp_output = svg_dp

        duplex_report = ''
        if run_rnaduplex:
            duplex_report = vienna_duplex_template.format(
                deltaenergy=rnaduplex_de,
                duplex_output=duplex_output
            )

        cofold_report = ''
        if run_rnacofold:
            cofold_report = vienna_cofold_template.format(
                cofold_output=cofold_output,
                cofold_ss_output=cofold_ss_output,
                cofold_dp_output=cofold_dp_output
            )

        analyses += vienna_analysis_template.format(
            interaction_no=str(i+1),
            query=sequence,
            duplex_report=duplex_report,
            cofold_report=cofold_report
        ) + '\n'

    # convert query sequence list into a presentable string
    query_sequences_display = ''
    for (seq_id, sequence) in query_sequences:
        query_sequences_display += '<pre>%s:\n%s</pre>\n\n' % (Markup.escape(seq_id), Markup.escape(sequence))

    return viennarna_template.format(
        query_seqs=query_sequences_display,
        analyses=analyses
    )