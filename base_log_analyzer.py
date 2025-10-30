#!/usr/bin/env python3
"""
Base Sequential Log Analyser
This is the starting point for the distributed log analyser assignment.
Students will parallelize this code using MPI.
"""

import os
import sys
import time
from collections import defaultdict


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
    total_counts = defaultdict(int)
    for log_file in log_files:
        print(f"Analysing: {log_file}")
        counts = analyse_log_file(log_file)
        merge_counts(total_counts, counts)

    end_time = time.time()

    # Print results
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)

    for level in sorted(total_counts.keys()):
        print(f"{level}: {total_counts[level]}")

    print("="*50)
    print(f"Total time: {end_time - start_time:.2f}s")
    print("="*50)


if __name__ == "__main__":
    main()
