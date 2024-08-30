#!/usr/bin/bash
#
# Author: Rohan Chhibba
# Updated: Feb 7, 2024
# 1: -------------------------------------------------------------------------
# slurm options: --------------------------------------------------------------
#SBATCH --job-name=shaded_planning_Paris
#SBATCH --mail-user=rchhibba@asu.edu
#SBATCH --mail-type=ALL
#SBATCH --cpus-per-task=1
#SBATCH -N 1
#SBATCH --mem=50G
#SBATCH -t 4-00:00:00
#SBATCH -p general
#SBATCH -q public
#SBATCH -G a100:1
#SBATCH --output=/home/%u/logs/Paris/%x-%j.log
# application: ----------------------------------------------------------------
# modules
# SBATCH --get-user-env
conda init
conda activate test4

# run the script
date
cd /home/rchhibba/shaded_planning/ParisAnalysis
python3 -u ParisVisualization.py
date
echo "Done."
