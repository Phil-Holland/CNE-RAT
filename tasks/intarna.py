import sys, time, subprocess, base64, os
sys.path.append('..')
from app import celery
from flask import Markup
from .shared import create_working_dir, get_sequences_from_fasta

intarna_template = """
# IntaRNA Toolchain Output

## Overview

Query sequences: 

{query_seqs}

---

{analyses}

"""

inta_analysis_template = """

## Query {interaction_no}

Evaluating interactions between the CNE sequence and the 
following query sequence:

<pre>
{query}
</pre>

Using IntaRNA command:

<pre>{input}</pre>

Output:

<pre style="max-height: 50pc; overflow-y: scroll;">
{output}
</pre>

"""

@celery.task(name='intarna')
def intarna(config, uid):
    # create a working directory, based on the task uid
    working_dir = create_working_dir(uid, 'intarna')

    # retrieve the relevent fields from the configuration object
    cne_sequences_fasta = config['cne']
    query_sequences_fasta = config['rna_rna_config']['query_sequences']

    prediction_mode = config['rna_rna_config']['inta_config']['prediction_mode']
    if prediction_mode not in ['H', 'M', 'E']:
        raise Exception('Prediction mode not one of "H", "M", or "E"')

    minpu = float(config['rna_rna_config']['inta_config']['minpu'])

    # parse the two fasta strings, and retrieve the sequences they contain
    cne_id, cne_sequence = get_sequences_from_fasta(cne_sequences_fasta, limit=1)[0]
    query_sequences = get_sequences_from_fasta(query_sequences_fasta)

    analyses = ''
    for i, (seq_id, sequence) in enumerate(query_sequences):
        print('Processing sequence: %s' % sequence)

        cmd = [
            'IntaRNA', 
            '-t', cne_sequence, 
            '-q', sequence,
            '--outMinPu=%s' % str(minpu),
            '--mode=%s' % prediction_mode,
            '--outMode=D',
            '--threads=0',
            '--energy=V'
        ]
        print('Running command: %s' % (' '.join(cmd)))
        p = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        output, err = p.communicate()
        output = output.decode("utf-8")

        analyses += inta_analysis_template.format(
            interaction_no=str(i+1),
            query=sequence,
            input=' '.join(cmd),
            output=output
        )

    # convert query sequence list into a presentable string
    query_sequences_display = ''
    for (seq_id, sequence) in query_sequences:
        query_sequences_display += '<pre>%s:\n%s</pre>\n\n' % (Markup.escape(seq_id), Markup.escape(sequence))

    return intarna_template.format(
        query_seqs=query_sequences_display,
        analyses=analyses
    )



