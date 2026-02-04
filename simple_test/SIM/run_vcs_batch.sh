#!/bin/tcsh

#source dir.env

set SRUN=(srun --sym=vcs --constraint=centos7.9 -c 1 --pty --x11 -p design2 --mem=100G)

#rm -rf simv* csrc* *.log

$SRUN vcs -f filelist.f -debug_access -kdb -full64 -l comp.log -sverilog +lint=TFIPC-L +lint=PCWM

$SRUN ./simv -l run.log