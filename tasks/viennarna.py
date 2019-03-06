import sys, time
sys.path.append('..')
from app import celery 

# Notes:
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 

@celery.task(name='viennarna')
def viennarna(config, working_dir):
    time.sleep(1)
    return '## viennarna - results!\nThis is markdown - writing to %s' % working_dir