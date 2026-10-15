#!/bin/bash
#SBATCH --job-name=p18render
#SBATCH --partition=sapphire
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p18-run/p18render-%j.out
module load MATLAB/2025b
matlab -batch "addpath('/data/gpfs/projects/punim2657/Temp/potsac-p18-run'); p18_render(1:4)"
