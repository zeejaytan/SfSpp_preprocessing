#!/bin/bash
#SBATCH --job-name=p18probe
#SBATCH --partition=sapphire
#SBATCH --time=00:20:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p18-run/p18probe-%j.out
module load MATLAB/2025b
matlab -batch "addpath('/data/gpfs/projects/punim2657/Temp/potsac-p18-run'); p18_probemesh"
