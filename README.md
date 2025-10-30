# Distributed Systems Induction Assignment | 2025

## Introduction

This project is designed to introduce you to the world of **Distributed Systems** - where multiple computers work together to solve a problem faster, more reliably, and at larger scale than any single machine could.

This assignment is a journey into both the theory and practice of building these powerful systems. It is divided into two equally important components, each carrying a 50% weightage towards your final evaluation:
- Practical Implementation: A hands-on coding challenge where you'll build a distributed log analyser.
- Theoretical Paper Reading: An analysis of some foundational academic papers that shaped the field.

Success in this induction requires engaging deeply with both parts. The code you write will bring the concepts from the papers to life, and the papers will provide the "why" behind the code you write.

For queries related to this assignment, contact one of (on Slack):
- Bhavya
- Kaaviya
- Manit

---

## Next Steps

Refer to [`implementation.md`](./implementation.md) for the coding task.

Refer to [`paper_reading.md`](./paper_reading.md) for the paper reading task.

---

## Repository Structure

```
DaSH-Lab-Induction-Assignment-2025/
│
├── README.md                                 # This file
├── implementation.md
├── paper_reading.md
│
├── implementation/                           # Implementation-related work
│   │
│   ├── base_log_analyser.py                  # Provided sequential implementation
│   │
│   ├── stage1/
│   │   ├── parallel_log_analyser.py          # Your Stage 1 implementation
│   │   ├── report_stage1.txt                 # Stage 1 analysis report
│   │   └── benchmarks/                       # Performance data (optional)
│   │       ├── time_1_process.txt
│   │       ├── time_2_process.txt
│   │       └── time_4_process.txt
│   │
│   ├── stage2/
│   │   ├── distributed_log_analyser.py       # Your Stage 2 implementation
│   │   ├── checkpoints/                      # Directory containing all checkpoints
│   │   │   ├── checkpoint_2025-10-29_14-30-00/     # Example checkpoint directory
│   │   │   │   ├── checkpoint.json           # Metadata (see template below)
│   │   │   │   ├── node1.log                 # Processed file 1
│   │   │   │   └── node2.log                 # Processed file 2
│   │   │   └── ...                           # Additional checkpoints (if any)
│   │   ├── report_stage2.txt                 # Stage 2 analysis report
│   │   └── tests/                            # Test scripts (optional)
│   │       ├── test_normal.sh
│   │       ├── test_crash.sh
│   │       └── test_recovery.sh
│   │
│   ├── sample_logs/                          # Test log files
│   │   ├── node1.log
│   │   ├── node2.log
│   │   ├── node3.log
│   │   └── ...
│   │
│   └── utils/                                # Helper scripts (optional)
│       ├── generate_logs.py                  # Script to generate test logs
│       └── visualize_performance.py          # Plot speedup graphs
│
└── paper-reading/                            # Paper reading and analysis
    └── analysis.md                           # Analysis of chosen paper
```

---

**Good luck, and welcome to the world of distributed systems!**