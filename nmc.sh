#!/bin/bash
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_tmp.sh >/dev/null 2>&1 &
tmp_pid=$!

sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_pre.sh >/dev/null 2>&1 &
pre_pid=$!
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_rh.sh >/dev/null 2>&1 &
rh_pid=$!
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_pph.sh >/dev/null 2>&1 &
pph_pid=$!
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_uv.sh >/dev/null 2>&1 &
uv_pid=$!

#sleep 7m
wait ${tmp_pid}
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_tmax.sh >/dev/null 2>&1 &
tmx_pid=$!
sleep 2s
/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_merging/nmc_tmin.sh >/dev/null 2>&1 &
tmi_pid=$!

wait ${pre_pid}
wait ${rh_pid}
wait ${pph_pid}
wait ${uv_pid}

wait ${tmx_pid}
wait ${tmi_pid}

/bin/bash /space/cmadaas/dpl/NWFD01/code/nmc_grid2station/nmc_grid2station.sh >/dev/null 2>&1 &
