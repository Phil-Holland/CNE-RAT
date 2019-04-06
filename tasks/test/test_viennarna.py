import sys, os
sys.path.append('..')
sys.path.append('../..')
from viennarna import viennarna

# a simple script to run the viennarna task locally
config = {
	'config': {
		'cne': '> cne\nACTTTTTTGAGTTAGTTTAAACACACCCGCA', 
		'email': 'test@test.com', 
		'send_email': False, 
		'task_rna_protein': True, 
		'task_rna_protein_config': {
		}, 
		'task_rna_rna': True, 
		'task_rna_rna_config': {
			'rna_rna_pipeline': 'both',
			'query_sequences': '> query1\nCAATCTATTGTAACAAAGAA\n\n> query2\nCAATCTACCGAAACAAAA'
		}
	}
}

working_dir = os.path.dirname(os.path.realpath(__file__))

print('Starting ViennaRNA task')
output = viennarna(config, working_dir)
#print('Finished. Output:\n')
#print(str(output))

file = open('test_viennarna_output.md','w')
file.write(output)
file.close() 