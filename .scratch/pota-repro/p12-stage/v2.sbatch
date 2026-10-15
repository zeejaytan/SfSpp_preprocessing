#!/bin/bash
#SBATCH --job-name=p12-v2
#SBATCH --partition=sapphire
#SBATCH --time=03:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p12-run/v2-%j.out
module load MATLAB/2025b
matlab -batch "run('/data/gpfs/projects/punim2657/Temp/potsac-p12-run/v2_fit.m')"
