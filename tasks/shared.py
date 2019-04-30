import os
from Bio import SeqIO
from Bio.Alphabet import IUPAC
from io import StringIO

# a collection of utility functions for different tasks to use

def create_working_dir(uid, name):
	"""Creates a working directory on the system, for a specific task
    
    Args:
        uid: the 'outer' directory name (the job's unique id)
        name: the 'inner' directory name (the task's name)

    Returns:
        a string path to the newly created directory
    """

	working_dir = '/var/tmp/%s/%s' % (str(uid), str(name))
	if not os.path.exists(working_dir):
		os.makedirs(working_dir)

	return working_dir

def get_sequences_from_fasta(fasta_string, limit=None, return_record=False, dna_alphabet=False):
    """parses a FASTA file of sequences, and returns each contained sequence

    Args:
        fasta_string: the contents of the FASTA file
        limit: how many sequences to parse
        return_record: whether to return the sequence as a string, or a 
            biopython record object
        dna_alphabet: whether to force to usage of the DNA alphabet
            (IUPAC.IUPACUnambiguousDNA)

    Returns:
        a list of sequences, in the intended format
    """
    seq_io = StringIO(fasta_string)
    sequences_parsed = None
    if dna_alphabet:
        sequences_parsed = SeqIO.parse(seq_io, 'fasta', alphabet=IUPAC.IUPACUnambiguousDNA())
    else:
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
        if return_record:
            sequences.append(fasta)
        else:
            sequences.append((seq_id, sequence))
        if limit:
            if i >= limit-1:
                break

    return sequences