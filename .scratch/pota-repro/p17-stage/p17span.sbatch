#!/bin/bash
#SBATCH --job-name=p17span
#SBATCH --partition=sapphire
#SBATCH --time=01:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p17-run/p17span-%j.out
module load MATLAB/2025b
matlab -batch "addpath('/data/gpfs/projects/punim2657/Temp/potsac-p17-run'); p17_span({'H',1:11;'G',1:7;'D',1:32;'J',1:19;'A',1:8})"
