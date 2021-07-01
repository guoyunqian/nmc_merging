#!/bin/bash
CRTDIR=$(pwd)

cd "/space/cmadaas/dpl/NWFD01/workenv/fix-cmadaas-env/bin"

source activate

cd "/space/cmadaas/dpl/NWFD01/code/nmc_merging"

python3 ./nmc_merging.py -l ./logfiles/nmc_merging_uv.log -f ./config_uv/cfg_main.ini

deactivate

cd $CRTDIR

