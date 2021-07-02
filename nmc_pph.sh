#!/bin/bash
CRTDIR=$(pwd)

cd "/space/cmadaas/dpl/NWFD01/workenv/fix-cmadaas-env/bin"

source activate

cd "/space/cmadaas/dpl/NWFD01/code/nmc_merging"

python3 ./nmc_merging.py -l ./logfiles/nmc_merging_pph.log -f ./config_pph/cfg_main.ini

deactivate

cd $CRTDIR

