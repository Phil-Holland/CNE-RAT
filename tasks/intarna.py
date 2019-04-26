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

**Using IntaRNA command:**

<pre>{input}</pre>

{output}

"""

inta_output_template = """

### Interaction Visualisation

A visual representation of the identified interaction is shown below. 
The target sequence is shown in the `5'-3'` direction, and the query sequence is 
shown in the `3'-5'` direction. 

Don't worry if your input sequences are not genes and don't have UTRs, the result 
is still correct. The notations just mark the ends of the sequences and are used 
to illustrate direction.

The coordinates of both interaction sites in their respective sequences are shown, 
marking the start and the end of each interaction site. Each formed base pair is 
illustrated by lines drawn between pairs of nucleotides from each sequence. Correct 
(complementary) pairing is marked by solid lines, while dashed lines symbolise 
unpaired nucleotides. Where more of these occur in a row, gaps are also introduced.

The interaction sites are provided again below the figure. 
`interaction seq 1` is the target sequence, while `interaction seq 2` is the query sequence.

<pre>
{interaction}
</pre>

### Energy Value Calculation

Displayed below is the overall interaction energy value (shown on the first line) followed by 
a breakdown of the components of its calculation.

- The `'E'` components are the terms of the energy of the intermolecular interaction (based on `RNAhybrid` 
and the Zuker and Stiegel algorithm).
- The `'ED'` components are the terms of the accessibility calculation, computed for each sequence 
(`'seq1'` is the target, `'seq 2'` is the query). These represent the energy needed to make each 
nucleotide available for intermolecular interaction (i.e. to ensure no RNA secondary structures are formed). 

The unpaired probability score (`Pu`) is derived from the `ED` values (and will approach the minimum Pu limit 
set in the configuration, if applicable).

<pre>
{energies}
</pre>

### Interaction Seed

The results below provide relevant information on the interaction seed.

The seed coordinates are provided for both interaction sites (`'seq1'` is the target, `'seq 2'` 
is the query), along with the free energy of the seed interaction (this will generally be higher than 
the whole interaction, due to the shorter interaction length), and the unpaired probabilities of the 
respective seed regions (these will generally be higher than for the whole interaction).

It is possible for an interaction to have identical seed and whole interaction details. This will 
especially occur if the `minimum Pu` parameter is used.

<pre>
{seeds}
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

        # has the tool returned a result?
        output_text = None
        if len(output.split('\n')) > 30:
            output_text = inta_output_template.format(
                interaction='\n'.join(output.split('\n')[1:15]),
                energies='\n'.join(output.split('\n')[16:28]),
                seeds='\n'.join(output.split('\n')[29:36])
            )
        else:
            output_text = '<pre>%s</pre>' %  output

        analyses += inta_analysis_template.format(
            interaction_no=str(i+1),
            query=sequence,
            input=' '.join(cmd),
            output=output_text
        )

    # convert query sequence list into a presentable string
    query_sequences_display = ''
    for (seq_id, sequence) in query_sequences:
        query_sequences_display += '<pre>%s:\n%s</pre>\n\n' % (Markup.escape(seq_id), Markup.escape(sequence))

    return intarna_template.format(
        query_seqs=query_sequences_display,
        analyses=analyses
    )



