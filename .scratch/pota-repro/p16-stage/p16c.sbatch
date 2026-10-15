#!/bin/bash
#SBATCH --job-name=p16c-attemptb
#SBATCH --partition=sapphire
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p16-run/p16c-%j.out
module load MATLAB/2025b
matlab -batch "run('/data/gpfs/projects/punim2657/Temp/potsac-p16-run/p16c_fit.m')"
