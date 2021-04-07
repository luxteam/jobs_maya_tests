#!/bin/bash
DELETE_BASELINES=${1:False}

python3.9 ../jobs_launcher/common/scripts/generate_baselines.py --results_root ../Work/Results/Maya --baseline_root ../Work/GeneratedBaselines --remove_old $DELETE_BASELINES
