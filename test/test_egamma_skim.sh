#!/bin/bash
python3 src/main.py skim \
  --filepath data/DT_2024/EGamma/Run2024H.txt \
  --golden_json /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/2024H_Golden.json \
  --triggerpath data/triggerlists/EGM_triggers_skim.txt \
  --out out_skim \
  --channel egamma \
  --nThreads 8 \
  --nsteps 20 \
  --step 1 \
  --correction_json data/corrections/summer24_corrections.json \
  --correction_key Run2024H \
  --progress_bar