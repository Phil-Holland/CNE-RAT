import sys, time
sys.path.append('..')
from app import celery 
from .shared import create_working_dir, get_sequences_from_fasta
import os
import glob
from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
import Bio
from Bio import SeqIO
from Bio.Seq import Seq
from Bio import motifs
from Bio.Alphabet import IUPAC

protein_template = """
# RNA-Protein Toolchain Output

## Overview

Query species: 

{query_species}

---

## Hits Table

{table}

"""

class CisbpRNA:
    
    def __init__(self, species=["drosophila_melanogaster", "homo_sapiens", "mus_musculus"]):

        # read in RBP database
        self.db = self._load_db()

        # read in PWMs
        self.pwms = self._load_pwms()
        
        self.species = species

    def _load_db(self):
        """Loads and returns formatted db."""

        dir_path = os.path.dirname(os.path.realpath(__file__))
        db_path = dir_path + "/data/cisbp_rna/RBP_Information.txt"
        db = pd.read_csv(db_path, sep="\t", header=0)
        db.columns = db.columns.str.lower()
        db["rbp_name"] = db["rbp_name"].str.upper()
        db["rbp_species"] = db["rbp_species"].str.lower()

        return db
        
    def _load_pwms(self):
        """Loads and returns PWMs."""
        
        pwms = {}
        dir_path = os.path.dirname(os.path.realpath(__file__))
        for file in glob.glob(dir_path + "/data/cisbp_rna/pwms/*.txt"):
            pwm_id = os.path.splitext(os.path.basename(file))[0]
            try:
                pwm = pd.read_csv(file, sep="\t", header=0, index_col=0)
                # biopython can only handle DNA motifs so we replace U with T
                pwm.rename(columns = {"U":"T"}, inplace=True)
                pwm = motifs.Motif(alphabet=IUPAC.IUPACUnambiguousDNA(), counts=pwm.to_dict(orient="list"))
                pwm = pwm.counts.normalize(pseudocounts=0.00001)
                pwms[pwm_id] = pwm
            except:
                # some pwm files are empty - we skip these
                continue 
        return pwms
    
    def _scan_seq(self, seq_record, threshold, ids):
        """Scans a single sequence for motif hits."""

        pwms = self.pwms
        hits = [] 
        for pwm_id, pwm in pwms.items():

            # get the PSSM for this PWM
            pssm = pwm.log_odds() 
            max_score = pssm.max 

            # scan the sequence with the PSSM - we use n * max_score as a threshold
            for position, score in pssm.search(seq_record.seq, 0.7*max_score, both=False):
                start = position + 1
                end = position + len(pssm.consensus)
                hit_seq = str(seq_record.seq[position:end].transcribe()) 
                hit_score = round(score, 3)
                hits.append([pwm_id, start, end, hit_seq, round(hit_score, 3), round(max_score, 3)])
            
        return hits

    def scan(self, seq_record, threshold=6.0, ids=[]):
        """Scans a sequence for motif hits."""

        # create a directory for results
        # date_time = time.strftime("%Y%m%d_%H-%M-%S", time.localtime())
        # save_dir = os.path.join("results", date_time)
        # os.mkdir(save_dir)

        # these are the columns from the database that we want to fetch
        cols = ["rbp_id", "rbp_name", "rbp_species", "family_name", "rbp_status", "motif_id"]
            
        # scan sequence for motif hits
        hits = self._scan_seq(seq_record, threshold, ids)

        # create a dataframe of results
        rbp_info = self.db.loc[:, cols]
        rbp_info["rbp_name"] = rbp_info["rbp_name"].str.upper()
        hits_df = pd.DataFrame(hits, columns=["motif_id", "start", "stop", "sequence", "score", "max_score"])
        hits_df = pd.merge(hits_df, rbp_info)
        hits_df = hits_df[hits_df["rbp_species"].isin(self.species)] # only keep results for specified species
        hits_df = hits_df.sort_values(by=["start"])

        # save results
        # save_name = "{}.txt".format(seq_record.id)
        # save_path = os.path.join(save_dir, save_name)
        # hits_df.to_csv(save_path, sep="\t", index=False)

        return hits_df

@celery.task(name='protein')
def protein(config, uid):
    cne_sequences_fasta = config['cne']
    cne_record = get_sequences_from_fasta(cne_sequences_fasta, 
        limit=1, return_record=True, dna_alphabet=True)[0]

    # build list of relevant species
    species = []
    species_display = ''
    if config['rna_protein_config']['drosophila_melanogaster'] == True:
        species.append('drosophila_melanogaster')
        species_display += '- *Drosophila melanogaster*\n'
    if config['rna_protein_config']['homo_sapiens'] == True:
        species.append('homo_sapiens')
        species_display += '- *Homo sapiens*\n'
    if config['rna_protein_config']['mus_musculus'] == True:
        species.append('mus_musculus')
        species_display += '- *Mus musculus*\n'

    # load data from CISBP-RNA
    cisbp_rna = CisbpRNA(species)

    hits_df = cisbp_rna.scan(cne_record)
    return protein_template.format(
        query_species=species_display,
        table=str(hits_df.to_html())
    )