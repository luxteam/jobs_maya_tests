#!/bin/bash
export PYTHONPATH=../jobs_launcher/:$PYTHONPATH

python3 ../jobs_launcher/common/scripts/generate_baselines.py --results_root ../Work/Results/Maya --baseline_root ../Work/Baseline