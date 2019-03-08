import sys, time, subprocess, base64
from Bio import SeqIO
from io import StringIO
sys.path.append('..')
from app import celery 

# define the main report templates here, and fill out the contents later
viennarna_template = """
# ViennaRNA Toolchain Output

CNE sequence:

```
{cne}
```

Query sequences: 

```
{seq}
```

RNAcofold output:

```
{output}
```

"""    

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

    seq1 = query_sequences[0]

    rnacofold_input = '> cofold\n{cne}&{query}'.format(
        cne=cne_sequence,
        query=seq1
    )
    print(rnacofold_input)

    p = subprocess.Popen(['RNAcofold', '-p'],
        cwd=working_dir, 
        stdout=subprocess.PIPE, 
        stdin=subprocess.PIPE
    )
    output, err = p.communicate(input=str.encode(rnacofold_input))
    output = output.decode("utf-8")

    return viennarna_template.format(
        cne=cne_sequence,
        seq=',\n\n'.join(query_sequences),
        output=output
    )