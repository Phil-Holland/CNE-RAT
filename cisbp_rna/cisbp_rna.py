import sys
import os
import argparse
import time
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

def get_args():
    usage = "python %(prog)s [options] seqs.fasta"
    desc = "Scan a set of DNA sequences with motifs from CISBP-RNA."
    parser = argparse.ArgumentParser(usage=usage, description=desc)
    parser.add_argument("seqs.fasta", help="set of DNA sequences in FASTA format")

    args = parser.parse_args()

    return vars(args)


class CisbpRNA:
    
    def __init__(self, species=["drosophila_melanogaster", "homo_sapiens", "mus_musculus"]):

        # read in RBP database
        self.db = self._load_db()

        # read in PWMs
        self.pwms = self._load_pwms()
        
        self.species = species

    def _load_db(self):
        """Loads and returns formatted db."""

        db_path = "data/cisbp_rna/RBP_Information.txt"
        db = pd.read_csv(db_path, sep="\t", header=0)
        db.columns = db.columns.str.lower()
        db["rbp_name"] = db["rbp_name"].str.upper()
        db["rbp_species"] = db["rbp_species"].str.lower()

        return db
        
    def _load_pwms(self):
        """Loads and returns PWMs."""
        
        pwms = {}
        for file in glob.glob("data/cisbp_rna/pwms/*.txt"):
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

    def scan(self, seqs, threshold=6.0, ids=[]):
        """Scans a set of sequences for motif hits."""

        # create a directory for results
        date_time = time.strftime("%Y%m%d_%H-%M-%S", time.localtime())
        save_dir = os.path.join("results", date_time)
        os.mkdir(save_dir)

        # these are the columns from the database that we want to fetch
        cols = ["rbp_id", "rbp_name", "rbp_species", "family_name", "rbp_status", "motif_id"]

        for seq_record in seqs:
            
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
            save_name = "{}.txt".format(seq_record.id)
            save_path = os.path.join(save_dir, save_name)
            hits_df.to_csv(save_path, sep="\t", index=False)


def main():

    args = get_args()

    # load data from CISBP-RNA
    cisbp_rna = CisbpRNA()

    # parse and scan provided sequences
    seqs = SeqIO.parse(args["seqs.fasta"], "fasta", alphabet=IUPAC.IUPACUnambiguousDNA())
    cisbp_rna.scan(seqs)


if __name__ == "__main__":
    
    main()

