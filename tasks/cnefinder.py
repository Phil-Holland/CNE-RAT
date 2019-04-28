import sys, time, subprocess, base64
import json, ftplib, re, requests
sys.path.append('..')
from Bio import SeqIO
from io import StringIO
from app import celery
from .shared import create_working_dir, get_sequences_from_fasta
from ftplib import FTP

@celery.task(name='cnefinder')
def cnefinder(config, uid):
    # create a working directory, based on the task uid
    working_dir = create_working_dir(uid, 'cnefinder')
    metadata_file = '.env'

    # retrieve relevant fields from configuration object
    ensembl_config = config['ensembl_request_config']

    reference_dataset = ensembl_config['ref_dataset']
    reference_url     = ensembl_config['ref_site']
    reference_mart    = ensembl_config['ref_mart']

    query_dataset = ensembl_config['query_dataset']
    query_url     = ensembl_config['query_site']
    query_mart    = ensembl_config['query_mart']

    ref_release = get_release_no(ref_url, ref_mart)
    query_release = get_release_no(query_url, query_mart)

    ref_info = [reference_dataset, reference_url, reference_mart, ref_release]
    query_info = [query_dataset, query_url, query_mart, query_release]

    # download FASTA files and return filenames
    fasta_filenames = [
        download_fasta_file(ref_info),
        download_fasta_file(query_info)]

    # create environment file in working directory
    json_to_env_file(config, working_dir, fasta_filenames, debug=True)


def get_release_no(ensembl_url, mart_name):
    """Gets the release number from XML MartURLLocation `database` attribute.

    Args:
        ensembl_url: the url of an ensembl host to access.
        martstring: the `name` of the chosen BioMart

    Returns:
        a string holding the release number of the BioMart with mart_name.
    """
    # TODO
    return ""


def download_fasta_file(info_list):
    """Downloads masked FASTA file from ensembl ftp server(s).

    Args:
        info_list: a list containing information pertaining to the
            reference ensembl dataset.

    info_list = [reference_dataset, reference_url, reference_mart, release_no]

    Returns:
        a string holding the name of the downloaded file.
    """
    dataset = info_list[0]
    url = info_list[1]
    release_no = info_list[3]

    non_standards = ["metazoa, plants, fungi, bacteria"]

    base = "ftp.ensembl.org"
    top = "/pub/{}/".format(release_no)
    for elem in non_standards:
        if elem in url:
            base = "ftp://ftp.ensemblgenomes"
            top = "/pub/{}/{}/".format(elem, release_no)
            break

    # Login to the ensembl ftp server
    ftp = FTP(base)
    ftp.login()
    ftp.cwd(top)

    # set up patterns to search for
    snd_word = dataset.split('_')[0][1:]
    pattern = r"{}.+_{}".format(dataset[0], snd_word)
    fasta_pattern = r".+_rm\.toplevel\.fa\.gz"

    # find species in list of subdirs
    genome_name = find_file_from_pattern(ftp, pattern)
    ftp.cwd(genome_name + "/dna/")

    # find masked fasta file of full genome
    fasta_file = find_file_from_pattern(ftp, fasta_pattern)

    # download file
    with open(fasta_file, 'wb') as f:
        ftp.retrbinary('RETR ' + fasta_file, f.write)

    return fasta_file


def retrlines_to_fnames(ftp):
    """Filters output of FTP.retrlines() to last `word` in each line.

    Args:
        ftp: the ftplib FTP object.

    Returns:
        A list of the last `word` on each line.
    """
    lines, names = [], []
    ftp.retrlines('LIST', lines.append)
    for line in lines:
        word_list = line.split()
        names.append(word_list[-1])

    return names


def find_file_from_pattern(ftp, pattern):
    """Returns a file/dir name in current ftp dir matching a pattern.

    Args:
        ftp: the ftplib FTP object.
        pattern: a regexp pattern to search for.

    Returns:
        A string of the first found item containing the pattern.
    """
    names = retrlines_to_fnames(ftp)
    path = ""
    for name in names:
        if re.search(pattern, name):
            path = name
            break

    return path


def json_to_env_file(config, working_dir, fasta_filenames, debug=True):
    """Produces .env file from JSON object.

    Args:
        config: JSON object passed from web-page form.
        working_dir: a string of the working dir for task.
        debug: a boolean flag that allows for additional
            debug printing.
    """
    envs = []
    for k, v in config.items():
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if 'site' in sub_k:
                    url = sub_v[:-1] if sub_v[-1] == '/' else sub_v
                    sub_v = url.split('.', 1)[1]
                envs.append("{}={}".format(sub_k.upper(), sub_v))
        else:
            envs.append("{}={}".format(k.upper(), v))

    if debug:
        print("Contents of config object:\n{}".format(envs))

    # add env variables for REF_GENOME_FILE and QUERY_GENOME_FILE
    envs.append("REF_GENOME_FILE={}/{}".format(working_dir, fasta_filenames[0]))
    envs.append("QUERY_GENOME_FILE={}/{}".format(working_dir, fasta_filenames[1]))

    # add misc env variables
    envs.append("GENES_REF_FILE={}/ref_genes".format(working_dir))
    envs.append("GENES_QUERY_FILE={}/query_genes".format(working_dir))
    envs.append("EXONS_REF_FILE={}/ref_exons".format(working_dir))
    envs.append("EXONS_QUERY_FILE={}/query_exons".format(working_dir))
    envs.append("OUTPUT_PATH={}/outfile.bed".format(working_dir))

    with open('.env', 'w') as f:
        for e in envs:
            f.write("{}\n".format(e))
