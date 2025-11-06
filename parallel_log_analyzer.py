#!/usr/bin/env python3
"""
Base Sequential Log Analyser
This is the starting point for the distributed log analyser assignment.
Students will parallelize this code using MPI.
"""

from mpi4py import MPI
import math
import os
import sys
import time
from collections import defaultdict

# Initialise the MPI environment:
# COMM_WORLD is the default communicator that includes all processes.
comm = MPI.COMM_WORLD

rank = comm.Get_rank()

# Get the total number of running processes:
size = comm.Get_size()

def analyse_log_file(filepath):
    """
    Analyse a single log file and count occurrences of each log level.

    Args:
        filepath: Path to the log file

    Returns:
        Dictionary with counts for each log level (INFO, WARN, ERROR, etc.)
    """
    counts = defaultdict(int)

    try:
        with open(filepath, 'r') as f:
            for line in f:
                # Simple parsing: look for log levels in brackets
                # Example: [2025-03-27 12:02:03] [ERROR] Disk read failed
                if '[INFO]' in line:
                    counts['INFO'] += 1
                elif '[WARN]' in line or '[WARNING]' in line:
                    counts['WARN'] += 1
                elif '[ERROR]' in line:
                    counts['ERROR'] += 1
                elif '[DEBUG]' in line:
                    counts['DEBUG'] += 1
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return counts


def merge_counts(total_counts, new_counts):
    """
    Merge counts from one analysis into the total.

    Args:
        total_counts: Existing accumulated counts
        new_counts: New counts to add
    """
    for level, count in new_counts.items():
        total_counts[level] += count


def main():
    start_time=0
    if rank == 0:     
        if len(sys.argv) < 2:
            print("Usage: python base_log_analyser.py <log_directory>")
            sys.exit(1)

        log_dir = sys.argv[1]

        if not os.path.isdir(log_dir):
            print(f"Error: {log_dir} is not a valid directory")
            sys.exit(1)

        # Find all .log files in the directory
    
        log_files = []
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                log_files.append(os.path.join(log_dir, filename))

        if not log_files:
            print(f"No .log files found in {log_dir}")
            sys.exit(1)

        print(f"Found {len(log_files)} log file(s) to analyse")
        print("Starting sequential analysis...")

        start_time = time.time()

        # Sequential processing of all log files

        chunk_size = len(log_files) // size

        chunked = [log_files[i:i + chunk_size] for i in range(0, len(log_files), chunk_size)]
    else:
        chunked = None
    
    local_log = comm.scatter(chunked,root=0)
    total_counts = defaultdict(int)
    if local_log is not None:
        for log_file in local_log:
            # print(f"Analysing: {log_file}")
            counts = analyse_log_file(log_file)
            merge_counts(total_counts, counts)
        print("CHUNK done")
    
    all_counts_chunked = comm.gather(total_counts,root=0)


    if rank == 0:
        all_counts = defaultdict(int)
        if all_counts_chunked is not None:
            for counts in all_counts_chunked:
                merge_counts(all_counts, counts)

        end_time = time.time()

        # Print results
        print("\n" + "="*50)
        print("ANALYSIS RESULTS")
        print("="*50)

        for level in sorted(all_counts.keys()):
            print(f"{level}: {all_counts[level]}")

        print("="*50)
        print(f"Total time: {end_time - start_time:.2f}s")
        print("="*50)


if __name__ == "__main__":
    main()
