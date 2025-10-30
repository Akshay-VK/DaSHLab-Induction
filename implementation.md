# Task 1: Implementing a Distributed Log Analyser

## Welcome

You'll start from a simple sequential program and progressively turn it into a **parallel** and finally a **distributed** system. By the end, you'll have hands-on experience with **MPI**, **fault tolerance**, and **coordination** - the very concepts that power systems like Google Search, Netflix, and Hadoop.

---

## Index

- [What Are Distributed Systems?](#what-are-distributed-systems)
- [What Is MPI?](#what-is-mpi)
- [Setting Up Your Environment](#setting-up-your-environment)
- [Recommended Resources](#recommended-resources)
- [The Assignment: Distributed Log Analyser](#the-assignment-distributed-log-analyser)
- [Stage 1: Parallel Log Analyser (MPI Basics)](#stage-1-parallel-log-analyser-mpi-basics)
- [Stage 2: Distributed Coordination & Fault Tolerance](#stage-2-distributed-coordination--fault-tolerance)
- [Bonus Challenges (Optional)](#bonus-challenges-optional)
- [Project Structure](#project-structure)
- [Development Tips](#development-tips)
- [What We're Looking For](#what-were-looking-for)
- [Closing Note](#closing-note)

---

## What Are Distributed Systems?

A **Distributed System** is a collection of independent computers that appear to the user as a single coherent system.

You've already seen examples without realising:
- Google Docs (collaborative editing from many devices)
- Online multiplayer games
- Distributed databases like MongoDB or Cassandra

Distributed systems are powerful because they:
- **Scale** across multiple nodes
- **Recover** from failures
- **Share** workloads efficiently

But they're also tricky because nodes can **crash**, **lag**, or **disagree** about the current state, and we need clever ways to keep things consistent.

---

## What Is MPI?

**MPI (Message Passing Interface)** is a standard for parallel and distributed programming. It allows multiple processes to communicate by passing messages, instead of sharing memory.

You can think of it like a group chat for programs:
- Each process has a **rank** (its unique ID)
- Processes send and receive messages using functions like `send()` and `recv()`
- One process (often rank 0) acts as the **master**, while others are **workers**

### Basic Usage Example

```python3
from mpi4py import MPI

# Initialise the MPI environment:
# COMM_WORLD is the default communicator that includes all processes.
comm = MPI.COMM_WORLD

rank = comm.Get_rank()

# Get the total number of running processes:
size = comm.Get_size()

if rank == 0:
    # Master process (rank 0) sends a message:
    data = {"message": "Hello from master!"}
    comm.send(data, dest=1)
else:
    # Worker processes receive the message from master:
    data = comm.recv(source=0)
    print(f"Process {rank} received:", data)
```

Try running it using:

```bash
mpirun -np 2 python3 mpi_intro.py
```

---

## Setting Up Your Environment

Before you begin, you'll need to set up MPI and Python dependencies on your system.

### Prerequisites

- Python 3.7+
- MPI Implementation (OpenMPI or MPICH)
- mpi4py (Python bindings for MPI)

### Installation Instructions

#### macOS

```bash
# Install OpenMPI using Homebrew
brew install open-mpi

# Install Python MPI bindings
pip3 install mpi4py
```

#### Ubuntu/Debian Linux

```bash
# Install OpenMPI
sudo apt-get update
sudo apt-get install -y openmpi-bin openmpi-common libopenmpi-dev

# Install Python MPI bindings
pip3 install mpi4py
```

#### Windows

```bash
# Install Microsoft MPI
# Download from: https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi

# Install Python MPI bindings
pip install mpi4py
```

### Verifying Your Installation

Test that MPI is correctly installed:

```bash
# Check MPI version
mpirun --version

# Test with a simple MPI program
mpirun -np 4 python3 -c "from mpi4py import MPI; print(f'Hello from rank {MPI.COMM_WORLD.Get_rank()}')"
```

You should see output from four different processes with ranks 0-3.

### Additional Dependencies

The base log analyser uses only Python standard library modules; but you may want to install additional packages for your implementation:

```bash
# For advanced data structures and analysis (optional)
pip3 install numpy

# For better progress tracking (optional)
pip3 install tqdm
```

### Troubleshooting

Issue: `mpirun` command not found
- Make sure MPI binaries are in your PATH
- On Linux, you may need to load the MPI module: `module load mpi/openmpi-x86_64`

Issue: `ImportError: No module named 'mpi4py'`
- Ensure you're using the correct Python interpreter: `python3 -m pip install mpi4py`
- If using virtual environments, activate it before installing

Issue: Processes don't communicate
- Check firewall settings if running on multiple machines
- Verify MPI is correctly configured with `ompi_info` (OpenMPI) or `mpichversion` (MPICH)

---

## Recommended Resources

Here are a few resources to get started. You **DO NOT** need to go through all of them; pick what works best for your learning style.

### Distributed Systems Concepts

- [MIT 6.824 Lecture 1 (Intro to Distributed Systems)](https://www.youtube.com/watch?v=cQP8WApzIQQ) - excellent overview of distributed systems fundamentals
- [A friendly introduction to distributed systems (by Tyler Treat)](https://medium.com/@copyconstruct/distributed-systems-theory-for-the-distributed-systems-engineer-94c49f8a3c97) - comprehensive blog post on distributed systems theory

### MPI Programming

- [Official mpi4py tutorial](https://mpi4py.readthedocs.io/en/stable/tutorial.html) - official documentation and examples
- [Intro to MPI by Lawrence Livermore National Lab](https://hpc-tutorials.llnl.gov/mpi/) - comprehensive MPI tutorial
- [mpi4py Examples](https://github.com/mpi4py/mpi4py/tree/master/demo) - collection of example programs

### Additional Learning Materials

- [Parallel Programming with MPI (YouTube Playlist)](https://www.youtube.com/playlist?list=PLvv0ScY6vfd_ocTP2ZLicgqKnvq50OCXM) - video tutorials
- [Introduction to Parallel Programming with MPI and OpenMP](https://www.openmp.org/resources/tutorials-articles/) - combined MPI and OpenMP resources

---

## The Assignment: Distributed Log Analyser

You'll build a system that analyses large sets of log files (like server logs) across multiple processes and nodes.

---

## Stage 1: Parallel Log Analyser (MPI Basics)

### Goal

Take a simple sequential log analyser and parallelize it using MPI so multiple processes can analyse logs simultaneously.

### What You'll Do

1. **Understand the base code**: Study the provided `base_log_analyser.py` to understand how sequential log analysis works.

2. **Create `parallel_log_analyser.py`** with the following architecture:
   - Rank 0 (Master):
     - Distributes log files to worker processes
     - Collects partial results from all workers
     - Aggregates and displays final results
   - Other Ranks (Workers):
     - Receive assigned log files from master
     - Analyse their assigned files
     - Send counts back to master

3. **Implement work distribution**: Decide how to partition log files among workers (round-robin, chunks, etc.).

4. **Merge results**: Aggregate partial counts from all workers at the master process.

5. **Measure performance**: Compare execution time with sequential version for different numbers of processes.

### Testing Your Implementation

First, test the base sequential analyser:

```bash
python3 base_log_analyser.py ./sample_logs
```

Then run your parallel version with different numbers of processes:

```bash
# Single process (should match sequential)
mpirun -np 1 python3 parallel_log_analyser.py ./sample_logs

# Multiple processes
mpirun -np 2 python3 parallel_log_analyser.py ./sample_logs
mpirun -np 4 python3 parallel_log_analyser.py ./sample_logs
```

### Expected Output

```
Found 10 log file(s) to analyse
Starting parallel analysis...

=================================================
ANALYSIS RESULTS
=================================================
DEBUG: 89
ERROR: 18
INFO: 152
WARN: 43
=================================================
Total time: 0.35s
Speedup: 2.3x
=================================================
```

### Deliverables

1. **`parallel_log_analyser.py`** - your parallel implementation

2. **`report_stage1.txt`** containing:
   - **Execution times** for 1, 2, 4, and 8 processes (if possible)
   - **Speedup calculations** (sequential_time / parallel_time)
   - **Efficiency analysis** (speedup / number_of_processes)
   - **Work distribution strategy** explanation
   - **Challenges faced** and how you solved them
   - **Observations** about scalability

---

## Stage 2: Distributed Coordination & Fault Tolerance

Now that your program can parallelize tasks, let's make it more *distributed* and *resilient*; just like real-world systems that keep running even if one node crashes.

### Goal

Enhance your MPI program to handle:

- **Worker failures**: detect and recover from crashed processes
- **Dynamic load balancing**: adapt to varying workloads
- **Periodic checkpointing**: save progress to recover from crashes

### What You'll Do

#### 1. Dynamic Scheduling

Instead of static work assignment, implement a dynamic task queue:

- **Master process**:
  - Maintains a queue of pending log files
  - Waits for work requests from workers
  - Assigns next file to requesting worker
  - Tracks which files are assigned to which workers

- **Worker processes**:
  - Request a file from master
  - Process the assigned file
  - Send results back to master
  - Request next file (repeat until no work remains)

**Implementation hint**: Use message tags to distinguish between work requests, work assignments, and result submissions.

#### 2. Fault Detection & Recovery

Make your system resilient to worker failures:

- **Timeout mechanism**:
  - Master should use non-blocking receives with timeouts
  - If a worker doesn't respond within a reasonable time, mark it as failed

- **Work reassignment**:
  - Track which files were assigned to which workers
  - If a worker fails, reassign its unfinished files to other workers
  - Ensure no file is processed twice (unless recovering from failure)

- **Heartbeat messages** (optional but recommended):
  - Workers periodically send "alive" messages
  - Master monitors for missing heartbeats

**Implementation hint**: Use `MPI.Request.Test()` or `MPI.COMM_WORLD.Iprobe()` for non-blocking message checks.

#### 3. Checkpointing

Implement periodic state saving:

- **What to checkpoint**:
  - Completed file counts (aggregated results)
  - List of processed files
  - The processed files themselves
  - List of pending files

- **When to checkpoint**:
  - After every N files processed (e.g., N=5)
  - Before program termination
  - Periodically based on time intervals (optional)

- **Checkpoint format**
    - All checkpoints should be saved in a dedicated checkpoint directory.
    - Each checkpoint itself should be a directory containing:
        - `checkpoint.json` (template provided below)
        - All files present in the `processed_files` list
    ```json
    {
        "timestamp": "2025-10-29T14:30:00",
        "counts": {
        "INFO": 152,
        "WARN": 43,
        "ERROR": 18
        },
        "processed_files": ["node1.log", "node2.log"],
        "pending_files": ["node3.log", "node4.log"],
        "failed_workers": [2]
    }
    ```

- **Recovery mechanism**:
  - On startup, check the checkpoints directory for the most recent checkpoint.
  - Load the corresponding `checkpoint.json` to restore its state and resume from there.
  - Skip already processed files

#### 4. Consistency Handling

Choose and implement a consistency model:

- **Eventual Consistency**:
  - Workers send results immediately
  - Master updates counts as results arrive
  - Faster, but may show incomplete intermediate states

- **Strong Consistency**:
  - Workers complete all assigned work before sending results
  - Master waits for all results before updating
  - Slower, but guarantees complete, consistent state

**In your report**: Explain which model you chose and why, discussing trade-offs.

### Testing Fault Tolerance

#### Test 1: Normal Operation

```bash
mpirun -np 4 python3 distributed_log_analyser.py ./sample_logs
```

#### Test 2: Simulated Worker Crash

Add this code to simulate a crash in one worker:

```python3
if rank == 2:
    import time
    time.sleep(5)  # Work for a bit
    print(f"[Rank {rank}] Simulating crash...")
    import sys
    sys.exit(1)  # Crash!
```

**Expected behaviour**:
- Master detects that rank 2 stopped responding
- Master reassigns rank 2's unfinished files to other workers
- Program completes successfully without hanging

#### Test 3: Recovery from Checkpoint

```bash
# Start analysis
mpirun -np 4 python3 distributed_log_analyser.py ./sample_logs

# Interrupt it (Ctrl+C) after some files are processed

# Restart - should resume from checkpoint
mpirun -np 4 python3 distributed_log_analyser.py ./sample_logs
```

**Expected behaviour**:
- Second run loads `checkpoint.json`
- Skips already processed files
- Continues from where it left off

### Expected Output

```
Loading checkpoint from previous run...
Resuming from checkpoint: 5 files already processed
Found 10 log file(s) to analyse (5 remaining)
Starting distributed analysis...

[Master] Assigning node6.log to worker 1
[Master] Assigning node7.log to worker 2
[Worker 1] Processing node6.log
[Master] Worker 2 timeout detected - marking as failed
[Master] Reassigning node7.log to worker 3
[Worker 3] Processing node7.log
...

=================================================
ANALYSIS RESULTS
=================================================
DEBUG: 89
ERROR: 18
INFO: 152
WARN: 43
=================================================
Total time: 2.14s
Files processed: 10
Failed workers: 1
Checkpoints saved: 3
=================================================
```

### Deliverables

1. **`distributed_log_analyser.py`** - your fault-tolerant distributed implementation

2. **`checkpoint.json`** - example checkpoint file from a run

3. **`report_stage2.txt`** explaining:
   - **Fault detection mechanism**: how you detect failed workers
   - **Recovery strategy**: how work is reassigned after failures
   - **Checkpointing design**: what you save and when
   - **Consistency model**: which model you chose and why (with trade-offs)
   - **Test results**: output from normal, crash, and recovery scenarios
   - **Design decisions**: any interesting implementation choices
   - **Limitations**: what failure scenarios your system can't handle

---

## Bonus Challenges (Optional)

If you finish early or want to go deeper into distributed systems concepts:

### 1. Leader Election (Backup Master)

Implement a backup master process that takes over if the primary master fails. Use a leader election algorithm (e.g., Bully Algorithm or Ring Algorithm). Test by simulating master failure mid-execution.

**Resources**: [Leader Election Algorithms](https://www.cs.cornell.edu/courses/cs6410/2018fa/slides/18-leader-election.pdf)

### 2. Streaming Log Analysis

Process logs _as_ they're being written (like `tail -f`). Workers continuously monitor log files for new entries. Implement real-time aggregation and display.

### 3. Replicated Log Storage

Implement log replication across multiple nodes. Ensure consistency between replicas. Handle replica failures gracefully.

**Concepts**: Primary-backup replication, quorum-based consistency

### 4. Load Balancing Optimizations

Implement _work stealing_; idle workers can steal work from busy workers. Predict file processing time based on file size. Assign larger files to faster workers (if running on heterogeneous systems).

### 5. Visualization Dashboard

Create a real-time dashboard showing:
- Active workers and their status
- Current task assignments
- Aggregated results so far
- Failed workers and recovery status

**Tools**: Simple web interface with Flask/FastAPI, or terminal UI with `curses`

---


### Generating Test Logs

You can create test log files using this simple script:

```python3
# utils/generate_logs.py
import random
import datetime

LOG_LEVELS = ['INFO', 'WARN', 'ERROR', 'DEBUG']
MESSAGES = [
    'Connection established',
    'Request processed',
    'Database query executed',
    'Cache miss',
    'Authentication failed',
    'Disk read failed',
    'Memory allocation error',
    'Network timeout'
]

def generate_log_file(filename, num_lines=1000):
    with open(filename, 'w') as f:
        for i in range(num_lines):
            timestamp = datetime.datetime.now().isoformat()
            level = random.choice(LOG_LEVELS)
            message = random.choice(MESSAGES)
            f.write(f"[{timestamp}] [{level}] {message}\n")

# Generate multiple log files
for i in range(1, 11):
    generate_log_file(f'sample_logs/node{i}.log', num_lines=5000)
```

---

## Development Tips

### Getting Started

Start small; begin with 2 processes before scaling up. Test incrementally, and verify whether each feature works before adding the next. Use the sequential version, and compare outputs to ensure correctness.

### Debugging MPI Programs

Print statements are your friend:
```python3
print(f"[Rank {rank}] Sending data to rank {dest}", flush=True)
```
Note: Use `flush=True` to ensure immediate output.

Check message matching. Ensure sends and receives match in source/destination ranks, message tags, and communicator.

Avoid deadlocks; don't have all processes waiting for receives simultaneously. Use non-blocking communication (`Isend`/`Irecv`) when appropriate. Master-worker pattern helps avoid circular dependencies.

Debug with fewer processes; issues are easier to trace with 2-3 processes.

### Performance Optimization

Minimize communication overhead; send larger chunks of data less frequently. Aggregate results before sending.

Balance the workload by monitoring if some workers finish much faster than others. Consider file sizes when distributing work.

Profile your code:
```python3
import time
start = time.time()
# ... work ...
print(f"Processing took {time.time() - start:.2f}s")
```

### Common Pitfalls

- Forgetting to call MPI.Finalize() at the end of your script (While Python's garbage collection often handles this, explicitly calling it is good practice to ensure all MPI resources are released cleanly).
- Rank assumptions: always check `comm.Get_rank()`, don't assume rank values
- Hardcoded process counts: make your code work with any number of processes
- Blocking receives which can cause deadlocks: use timeouts for fault tolerance
- File access conflicts: ensure multiple processes don't write to the same file simultaneously

### Testing Checklist

- [ ] Sequential version produces correct output
- [ ] Parallel version with 1 process matches sequential output
- [ ] Parallel version with multiple processes matches sequential output
- [ ] Speedup increases (roughly) with more processes
- [ ] No deadlocks or hangs
- [ ] Fault tolerance: handles worker crashes gracefully
- [ ] Checkpoint saves correctly
- [ ] Recovery from checkpoint works
- [ ] No file is processed twice (unless recovering from failure)

---

## What We're Looking For

This assignment is designed to evaluate your **thinking process** and **problem-solving approach**, not just your ability to write code.

**Key questions to consider**:

- How do you efficiently distribute work among processes?
- How do you detect and recover from failures?
- How do you maintain consistency across distributed processes?
- What trade-offs exist between performance and reliability?

Your ability to understand these concepts and explain your design decisions clearly is far more valuable than perfect code.

### Evaluation Criteria

Your work will be evaluated on:

**Code Quality (30%)**
- Correctness: does it produce accurate results?
- Functionality: do all required features work?
- Code structure: is it well-structured, commented and readable?
- Error handling: does it handle edge cases gracefully?

**Performance (20%)**
- Speedup: does parallelization improve execution time?
- Efficiency: how well does it scale with more processes?
- Load balancing: is work distributed fairly?

**Fault Tolerance (20%)**
- Crash recovery: does it handle worker failures?
- Checkpointing: can it resume from saved state?
- Robustness: does it recover gracefully?

**Report & Analysis (30%)**
- Clarity: are your explanations clear and well-structured?
- Depth: do you explain design decisions and trade-offs?
- Insights: do you provide thoughtful analysis of results?
- Completeness: did you address all required points?

**Bonus Points (up to +15%)**
- Implementing optional challenges
- Creative optimizations
- Exceptional documentation

---

## Closing Note

By completing this project, you'll have built a mini version of what large-scale distributed systems like Hadoop and Spark do behind the scenes. You'll understand the real challenges that distributed systems engineers face every day.

Remember: it's okay if your code isn't perfect. Focus on learning the concepts, experimenting with different approaches, and documenting your journey. We'd rather see a well-thought-out partial solution with clear explanations than a complete but poorly understood implementation.
