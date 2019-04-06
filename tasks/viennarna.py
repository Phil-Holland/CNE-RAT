import sys, time, subprocess, base64, os
from Bio import SeqIO
from io import StringIO
sys.path.append('..')
from app import celery

# define the main report templates here, and fill out the contents later:
# overall report template
viennarna_template = """
# ViennaRNA Toolchain Output

CNE sequence:

<pre>
{cne}
</pre>

Query sequences: 

<pre>
{seq}
</pre>

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

<details><summary><a>Click to show/hide report</a></summary>

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
    </div>
</div>

</details>

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
def viennarna(config, working_dir):
    cne_sequences_fasta = config['config']['cne']
    query_sequences_fasta = config['config']['task_rna_rna_config']['query_sequences']

    cne_io = StringIO(cne_sequences_fasta)
    cne_sequences_parsed = SeqIO.parse(cne_io, 'fasta')
    cne_sequence = ''
    for fasta in cne_sequences_parsed:
        cne_sequence = str(fasta.seq)
        break

    query_io = StringIO(query_sequences_fasta)
    query_sequences_parsed = SeqIO.parse(query_io, 'fasta')
    query_sequences = []
    for fasta in query_sequences_parsed:
        query_sequences.append(str(fasta.seq))
    
    cofold_outputs = {}
    cofold_ss_outputs = {}
    cofold_dp_outputs = {}

    # iterate over all query sequences, and produce cofold output text for each
    for sequence in query_sequences:
        print('Processing sequence: %s' % sequence)
        rnacofold_input = '> cofold\n{cne}&{query}'.format(
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
        cofold_outputs[sequence] = output

        svg_ss = convert_ps_to_svg('cofold_ss.ps', working_dir)
        svg_dp = convert_ps_to_svg('cofold_dp.ps', working_dir)
        cofold_ss_outputs[sequence] = svg_ss
        cofold_dp_outputs[sequence] = svg_dp

    analyses = ''
    for i, sequence in enumerate(query_sequences):
        analyses += vienna_analysis_template.format(
            interaction_no=str(i+1),
            query=sequence,
            cofold_output=cofold_outputs[sequence],
            cofold_ss_output=cofold_ss_outputs[sequence],
            cofold_dp_output=cofold_dp_outputs[sequence]
        ) + '\n'

    return viennarna_template.format(
        cne=cne_sequence,
        seq='\n\n'.join(query_sequences),
        analyses=analyses
    )