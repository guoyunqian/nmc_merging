#!/bin/bash
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_tmp.sh >/dev/null 2>&1 &
pid=$!

sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_pre.sh >/dev/null 2>&1 &
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_rh.sh >/dev/null 2>&1 &
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_pph.sh >/dev/null 2>&1 &
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_uv.sh >/dev/null 2>&1 &

#sleep 7m
wait ${pid}
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_tmax.sh >/dev/null 2>&1 &
pidtmx=$!
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_tmin.sh >/dev/null 2>&1 &
pidtmi=$!

wait ${pidtmx}
wait ${pidtmi}

/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_grid2station/nmc_grid2station.sh >/dev/null 2>&1 &
