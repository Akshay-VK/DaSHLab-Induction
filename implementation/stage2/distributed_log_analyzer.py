#!/usr/bin/env python3
"""
Base Sequential Log Analyser
This is the starting point for the distributed log analyser assignment.
Students will parallelize this code using MPI.
"""

from mpi4py import MPI
import math
import os
import json
import shutil
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

# Saves the checkpoint datato a checkpoint folder
def save_checkpoint(data: dict, file_paths: list[str], folder: str = "checkpoint"):
    if os.path.exists(folder):
        print(f"[INFO] Removing existing '{folder}' folder...")
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

    json_path = os.path.join(folder, "checkpoint.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"[INFO] Saved JSON data to {json_path}")

    for path in file_paths:
        if os.path.isfile(path):
            dest = os.path.join(folder, os.path.basename(path))
            shutil.copy2(path, dest)  # copy2 preserves metadata
            print(f"[INFO] Copied {path} to {dest}")
        else:
            print(f"[WARN] Skipped missing file: {path}")

    print(f"[DONE] Checkpoint saved in '{folder}'")

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
        maps=[]
        total_counts=defaultdict(int)
        recieved=0

        # Check and account for checkpoint files
        if os.path.exists("checkpoint/checkpoint.json"):
            print("[MASTER] Found checkpoint data. Resuming from checkpoint...")
            with open("checkpoint/checkpoint.json", "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)
            processed_files = checkpoint_data.get("processed_files", [])
            pending_files = checkpoint_data.get("pending_files", [])
            total_counts = checkpoint_data.get("counts", {})
            maps=[-1]*len(processed_files)+[0]*len(pending_files)
            recieved=len(processed_files)
            log_files=processed_files+pending_files
            print(f"[MASTER] Resuming with {len(pending_files)} pending log file(s).")
        else:
            # Otherwise do the entire thing
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    maps.append(0)
                    log_files.append(os.path.join(log_dir, filename))

        if not log_files:
            print(f"No .log files found in {log_dir}")
            sys.exit(1)

        print(f"Found {len(log_files)} log file(s) to analyse")
        print("Starting sequential analysis...")

        start_time = time.time()

        # Sequential processing of all log files

        timers=[0.0]*size

        results=[]
        # We find the first indices which needs to be assigned
        # We do this as there is a good chance we might not have enough files left to process in case of a restart (after loading checkpoints)
        first_indices=[]
        for(i) in range(len(log_files)):
            if maps[i]==0:
                first_indices.append(i)
                if len(first_indices)==10*(size-1):
                    break
        # We send the initial commands
        for i in range(1,size):
            command=[]
            for j in range(10):
                index=(i-1)*10+j
                if index<len(first_indices):
                    command.append({"file":log_files[first_indices[index]],"index":first_indices[index]})
            comm.send(command,i,tag=1)
            timers[i-1]=time.time()
            # We set the appropriate values to the map for state tracking
            for j in range(0,10):
                index=(i-1)*10+j
                if index<len(first_indices):
                    maps[first_indices[(i-1)*10+j]]=i

        rec=comm.irecv(source=MPI.ANY_SOURCE,tag=2)
        checkpointer=time.time()
        
        while 0 in maps or recieved < len(log_files):
            completed, result = rec.test()
            if not completed:
                # The checkpoint is handled here
                if time.time()-checkpointer>5.0:
                    checkpointer=time.time()
                    # Checkpoint file generation
                    print("[MASTER] Saving checkpoint...")
                    curr_counts=defaultdict(int)
                    for check_result in results:
                        merge_counts(curr_counts,new_counts=check_result)
                    completed_files=[]
                    todo_files=[]
                    for i in range(len(maps)):
                        if maps[i]==-1:
                            completed_files.append(log_files[i])
                        else:
                            todo_files.append(log_files[i])
                    checkpoint_data={
                        "timestamp":time.time(),
                        "counts":curr_counts,
                        "processed_files":completed_files,
                        "pending_files":todo_files,
                    }
                    save_checkpoint(data=checkpoint_data,file_paths=[],folder="checkpoint")
                curr=time.time()
                # We check for timeouts
                for t in timers:
                    if curr-t>5.0 and t>0.0:
                        print(f"[MASTER] Worker {timers.index(t)+1} timed out. Reassigning its tasks.")
                        # Reassign tasks
                        comm.send(None,timers.index(t)+1,tag=3)
                        for i in range(len(maps)):
                            if maps[i]==timers.index(t)+1:
                                maps[i]=0
                        timers[timers.index(t)]=0.0
            if result:
                recieved+=len(result["result"])
                # print("[MASTER] received ",recieved)

                # We store reslts and update the map
                results.extend(result["result"])
                maps=[-1 if i in result["index"] else maps[i] for i in range(len(maps))]
                # The worker's timer is reset to current time
                timers[result["worker"]-1]=time.time()

                rec=comm.irecv(source=MPI.ANY_SOURCE,tag=2)
                # We should only assign work if there are files left to be processed
                if 0 in maps:
                    next_files = []
                    i=0
                    # We find the next 10 pending files
                    while len(next_files)<10 and i<len(maps):
                        if maps[i]==0:
                            next_files.append(i)
                        i+=1

                    comm.send([{"file":log_files[next_file],"index":next_file} for next_file in next_files],result["worker"],tag=1)
                    maps=[maps[i] if i not in next_files else result["worker"] for i in range(len(maps))] # We update the map to reflect the new assignments
        
        # Once we are done with the processing, we tell all workers to stop
        for i in range(1,size):
            comm.send(None,i,tag=3)

        # Merge results
        for result in results:
            merge_counts(total_counts,new_counts=result)
        end_time = time.time()

        # Log checkpoint after completion
        completed_files=[]
        todo_files=[]
        for i in range(len(maps)):
            if maps[i]==-1:
                completed_files.append(log_files[i])
            else:
                todo_files.append(log_files[i])
        checkpoint_data={
            "timestamp":time.time(),
            "counts":total_counts,
            "processed_files":completed_files,
            "pending_files":todo_files,
        }
        save_checkpoint(data=checkpoint_data,file_paths=[],folder="checkpoint")

        # Print results
        print("\n" + "="*50)
        print("ANALYSIS RESULTS")
        print("="*50)

        for level in sorted(total_counts.keys()):
            print(f"{level}: {total_counts[level]}")

        print("="*50)
        print(f"Total time: {end_time - start_time:.2f}s")
        print("="*50)
    # elif rank == 2:
    #     time.sleep(5)  # Work for a bit
    #     print(f"[Rank {rank}] Simulating crash...")
    #     sys.exit(1)
    else:
        while True:
            task=comm.recv(source=0)
            if task is None: # Stop signal
                break
            # print(f"[WORKER] {rank} received task")
            # We process the assigned files and send back results
            comm.send({"result":[analyse_log_file(t["file"]) for t in task],"index":[t["index"] for t in task],"worker":rank},0,tag=2)

if __name__ == "__main__":
    main()
