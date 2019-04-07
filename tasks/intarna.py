import sys, time, subprocess, base64
sys.path.append('..')
from Bio import SeqIO
from io import StringIO
from app import celery 

intarna_template = """
# IntaRNA Tool Output

CNE sequence:

<pre>
{cne}
</pre>

Query sequences:
<pre>
{seq}
</pre>

IntaRNA output:

<pre>
{output}
</pre>

"""

@celery.task(name='intarna')
# def intarna(shared_cfg, tool_cfg):
#     time.sleep(1)
#     return str(shared_cfg)
def intarna(config, working_dir):
	#params - to get from config object in the future
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

	intarna_input = '-t {cne} -q {query} --energy=V'.format(
		cne = cne_sequence,
		query = seq1
	)
	print(intarna_input)

	#run inta
	p = subprocess.Popen(['IntaRNA', '-t', cne_sequence, '-q', seq1, '--energy=V'],
		cwd = working_dir,
		stdout = subprocess.PIPE,
		stdin = subprocess.PIPE,
		#env = inta
	)
	# output, err = p.communicate(input=str.encode(intarna_input))
	output, err = p.communicate()
	output = output.decode("utf-8")

	return intarna_template.format(
		cne = cne_sequence,
		seq = ',\n\n'.join(query_sequences),
		output = output
	)



