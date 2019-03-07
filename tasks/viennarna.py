import sys, time, subprocess, base64
sys.path.append('..')
from app import celery 

# define the main report templates here, and fill out the contents later
viennarna_template = """
# ViennaRNA Toolchain Output

CNE sequence: {cne}

Query sequences: {seq}


{output}

"""

@celery.task(name='viennarna')
def viennarna(config, working_dir):
    cne = config['config']['cne']
    query_sequences = config['config']['task_rna_rna_config']['query_sequences']

    seq1 = query_sequences[0]

    rnacofold_input = '> cofold\n{cne}&{query}'.format(
        cne=cne,
        query=seq1
    )

    p = subprocess.Popen(['RNAcofold', '-p'],
        cwd=working_dir, 
        stdout=subprocess.PIPE, 
        stdin=subprocess.PIPE
    )
    output, err = p.communicate(input=str.encode(rnacofold_input))
    
    return viennarna_template.format(
        cne=cne,
        seq=', '.join(query_sequences),
        output=output
    )