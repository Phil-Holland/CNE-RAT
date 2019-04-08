import sys, os
sys.path.append('..')
sys.path.append('../..')
from viennarna import viennarna

# a simple script to run the viennarna task locally
config = {
	'cne': '>cne\nACTTTTTTGAGTTAGTTTAAACACACCCGCA', 
	'rna_protein': False, 
	'rna_protein_config': {
	}, 
	'rna_rna': True, 
	'rna_rna_config': {
		'query_sequences': '>query1\nCAATCTATTGTAACAAAGAA\n\n>query2\nCAATCTACCGAAACAAAA',
		'vienna': True,
		'vienna_config': {
			'rnaduplex': True,
			'rnaduplex_config': {
				'deltaenergy': 10.2
			},
			'rnacofold': True,
			'rnacofold_config': {
				
			}
		},
		'inta': False,
		'inta_config': {
			
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