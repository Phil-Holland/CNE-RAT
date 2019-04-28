import sys, time, subprocess, base64
sys.path.append('..')
from Bio import SeqIO
from io import StringIO
from app import celery
from .shared import create_working_dir, get_sequences_from_fasta
