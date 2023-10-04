import os

curr_dir=os.getcwd()

lib_dir='/'.join(curr_dir.split('/')[:-1])+'/src'
lib_export='export PYTHONPATH=$PYTHONPATH:"{0}"'.format(lib_dir)

cnfg_file='/'.join(curr_dir.split('/')[:-2])
cnfg_export='export PPM_CNFG="{0}"'.format(cnfg_file)

assert 'PrincipalPathMethod' in os.listdir(lib_dir), "Error: PPM library missing"
assert 'config.json' in os.listdir(cnfg_file), "Error: config file missing"

print('\n'.join([lib_export,cnfg_export]))