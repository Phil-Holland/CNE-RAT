import sys, time
sys.path.append('..')
from app import celery 

@celery.task(name='protein')
def protein(config, uid):
    time.sleep(5)
    return '# RNA-Protein Interactions'