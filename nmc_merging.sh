#!/bin/bash
CRTDIR=$(pwd)

cd "/space/cmadaas/dpl/NWFD01/workenv/fix-cmadaas-env/bin"

source activate

cd "/space/cmadaas/dpl/NWFD01/code/fix-mulblend"

python3 ./fix-mulblend.py

deactivate

cd $CRTDIR

