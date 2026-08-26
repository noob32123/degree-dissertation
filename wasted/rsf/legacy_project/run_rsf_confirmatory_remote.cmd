@echo off
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_rsf_confirmatory.py --episodes 600 --horizon 64 --calibration-seeds 4 --confirmatory-seeds 10 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs_rsf_confirmatory > H:\degree-dissertation\md_dqn_rsf\rsf_confirmatory.log 2> H:\degree-dissertation\md_dqn_rsf\rsf_confirmatory.err.log
