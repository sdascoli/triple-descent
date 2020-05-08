import os
import time
import subprocess
import itertools
import argparse
import torch
import numpy as np

from utils import copy_py, who_am_i

def create_script(params):
    script = '''#!/bin/bash 
#SBATCH --gres=gpu:1
#SBATCH --mem=10GB
#SBATCH --nodes=1
#SBATCH --output={name}.out
#SBATCH --job-name={name}
#SBATCH --cpus-per-task=3

for ((i={seed[0]}; i<={seed[1]}; i++)); do
python main.py --name {name}-$i --noise {noise} --n {n} --seed $i --lr {lr} --d {d} --test_noise {test_noise} --loss_type {loss_type} --n_classes 2 --task classification --no_cuda False
done

wait
'''.format(**params)
    with open('{}.sbatch'.format(params['name']), 'w') as f:
        f.write(script)
    # with open('{}.params'.format(params['name']), 'wb') as f:
    #     torch.save(params, f)

def send_script(file):
    process = subprocess.Popen(['sbatch', file], stdout=subprocess.PIPE)

if __name__ == '__main__':
    
    exp_dir = 'r.{}'.format(int(time.time()))
    os.mkdir(exp_dir)
    copy_py(exp_dir) 
    os.chdir(exp_dir)

    grid = {
            'noise' : [0,0.1,0.2,0.5],
            'lr' : [0.001],#np.logspace(-2,0,3).astype(int),
            'n' : [100,1000,10000],#np.logspace(1,3,10).astype(int),
            'd' : [1,10,100],
            'seed' : [(0,2),(3,5)],
        'test_noise' : [False],
        'loss_type' : ['nll'],
        'epochs' : [10000]
    }

    def dict_product(d):
        keys = d.keys()
        for element in itertools.product(*d.values()):
            yield dict(zip(keys, element))

    for i, params in enumerate(dict_product(grid)):
        # params['name'] = '{noise:.2f}_{n:.2f}_{d:.2f}_{}'.format(**params)
        torch.save(grid, 'params.pkl')
        params['name'] = '{:06d}'.format(i)
        create_script(params)
        file_name = '{}.sbatch'.format(params['name'])
        send_script(file_name)

