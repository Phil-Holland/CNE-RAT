import os
from Bio import SeqIO
from io import StringIO

# a collection of utility functions for different tasks to use

def create_working_dir(uid, name):
	'''Creates a working directory on the system, for a specific task'''

	working_dir = '/var/tmp/%s/%s' % (str(uid), str(name))
	if not os.path.exists(working_dir):
		os.makedirs(working_dir)

	return working_dir

def get_sequences_from_fasta(fasta_string, limit=None):
    seq_io = StringIO(fasta_string)
    sequences_parsed = SeqIO.parse(seq_io, 'fasta')
    sequences = []
    for i, fasta in enumerate(sequences_parsed):
        # get sequence, and convert to uppercase
        sequence = str(fasta.seq).upper()
        seq_id = str(fasta.id)

        # make sure the sequence is only A,C,G,T/U
        # since we are only working with RNA sequences, we can assume this must be true
        for c in sequence:
            if not(c in ['A', 'C', 'G', 'T', 'U']):
                raise Exception('A sequence contains invalid character: %s' % c)
        sequences.append((seq_id, sequence))
        if limit:
            if i >= limit-1:
                break

    return sequences