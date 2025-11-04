"""
Log File Generator for Distributed Log Analyser Assignment
Generates test log files that match the expected format and counts.
"""

import random
import datetime
import os
from pathlib import Path
from collections import defaultdict

# Target counts for each log level
TARGET_COUNTS = {
    'INFO': 152485,   
    'WARN': 43916,    
    'ERROR': 18404,  
    'DEBUG': 89447    
}

# Realistic log messages for each level
MESSAGES = {
    'INFO': [
        'Connection established',
        'Request processed successfully',
        'Database query executed',
        'Cache hit',
        'User logged in',
        'Session started',
        'Configuration loaded',
        'Service initialized',
        'Health check passed',
        'Transaction completed'
    ],
    'WARN': [
        'High memory usage detected',
        'Slow query performance',
        'Cache miss',
        'Deprecated API usage',
        'Connection retry attempt',
        'Resource threshold approaching',
        'Timeout warning',
        'Queue size growing',
        'Disk space low',
        'Rate limit approaching'
    ],
    'ERROR': [
        'Authentication failed',
        'Disk read failed',
        'Memory allocation error',
        'Network timeout',
        'Database connection lost',
        'File not found',
        'Permission denied',
        'Invalid input data',
        'Service unavailable',
        'Request failed'
    ],
    'DEBUG': [
        'Variable value: x=42',
        'Entering function process_data()',
        'Loop iteration: 15',
        'HTTP request headers parsed',
        'Cache key generated',
        'Thread pool size: 8',
        'Memory allocation: 2048 bytes',
        'Connection pool status checked',
        'Buffer size: 4096 bytes',
        'Timer set: 30 seconds'
    ]
}

def generate_log_entry(level):
    """
    Generate a single log entry matching the base_log_analyzer.py expected format.
    Format: [YYYY-MM-DDTHH:MM:SS] [LEVEL] message
    
    Args:
        level: Log level (INFO, WARN, ERROR, DEBUG)
    
    Returns:
        Formatted log entry string
    """
    timestamp = datetime.datetime.now().isoformat()
    message = random.choice(MESSAGES[level])
    return f"[{timestamp}] [{level}] {message}\n"

def distribute_counts(total, num_files):
    """
    Distribute total count across num_files with some randomness.
    
    Args:
        total: Total count to distribute
        num_files: Number of files to distribute across
    
    Returns:
        List of counts for each file
    """
    if total == 0:
        return [0] * num_files
    
    # Start with equal distribution
    base = total // num_files
    remainder = total % num_files
    
    counts = [base] * num_files
    
    # Distribute remainder randomly
    indices = random.sample(range(num_files), min(remainder, num_files))
    for i in indices:
        counts[i] += 1
    
    # Add some randomness while maintaining total
    # Limit iterations for performance with large file counts
    for _ in range(min(num_files * 2, 5000)):
        i, j = random.sample(range(num_files), 2)
        if counts[i] > 1:  # Keep at least 1 in each file if possible
            transfer = random.randint(0, min(counts[i] - 1, 3))
            counts[i] -= transfer
            counts[j] += transfer
    
    return counts

def generate_log_files(output_dir='sample_logs', num_files=10000):
    """
    Generate log files with specified counts distributed across them.
    
    Args:
        output_dir: Directory to save log files
        num_files: Number of log files to generate
    """
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {num_files} log files in {output_dir}/")
    print(f"Target counts: {TARGET_COUNTS}")
    print(f"This will take several minutes...\n")
    
    # Distribute each log level's count across files
    print("Calculating distribution...")
    distributions = {}
    for level, count in TARGET_COUNTS.items():
        distributions[level] = distribute_counts(count, num_files)
    print("Distribution calculated!\n")
    
    # Track progress
    progress_interval = max(num_files // 20, 1)  # Show progress every 5%
    
    # Generate each log file
    print("Generating log files...")
    for i in range(1, num_files + 1):
        filename = os.path.join(output_dir, f'node{i}.log')
        
        # Collect all entries for this file
        entries = []
        
        for level in TARGET_COUNTS.keys():
            count = distributions[level][i-1]
            for _ in range(count):
                entries.append(generate_log_entry(level))
        
        # Shuffle entries to mix log levels (more realistic)
        random.shuffle(entries)
        
        # Write to file
        with open(filename, 'w') as f:
            f.writelines(entries)
        
        # Show progress
        if i % progress_interval == 0:
            percentage = (i / num_files) * 100
            print(f"  Progress: {i}/{num_files} files ({percentage:.0f}%)")
    
    print(f"\n  Completed: {num_files}/{num_files} files (100%)")
    
    # Print generation summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    total_entries = 0
    for level, count in sorted(TARGET_COUNTS.items()):
        print(f"{level}: {count:,}")
        total_entries += count
    print("="*60)
    print(f"Total entries: {total_entries:,}")
    print(f"Files generated: {num_files:,}")
    print(f"Average entries per file: {total_entries // num_files}")
    print("="*60)
    
    # Verify counts by sampling
    print("\nVerifying generated files (sampling)...")
    verify_counts_sample(output_dir, sample_size=100)

def verify_counts_sample(log_dir='sample_logs', sample_size=100):
    """
    Verify the counts in a sample of generated log files.
    This uses the same parsing logic as base_log_analyzer.py
    
    Args:
        log_dir: Directory containing log files
        sample_size: Number of files to sample for verification
    """
    counts = defaultdict(int)
    
    # Get all log files
    all_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    
    # Sample random files
    sample_files = random.sample(all_files, min(sample_size, len(all_files)))
    
    for filename in sample_files:
        filepath = os.path.join(log_dir, filename)
        with open(filepath, 'r') as f:
            for line in f:
                # Same parsing logic as base_log_analyzer.py
                if '[INFO]' in line:
                    counts['INFO'] += 1
                elif '[WARN]' in line or '[WARNING]' in line:
                    counts['WARN'] += 1
                elif '[ERROR]' in line:
                    counts['ERROR'] += 1
                elif '[DEBUG]' in line:
                    counts['DEBUG'] += 1
    
    print("\n" + "="*60)
    print(f"SAMPLE VERIFICATION ({sample_size} files)")
    print("="*60)
    
    total_sample = sum(counts.values())
    for level in sorted(TARGET_COUNTS.keys()):
        actual = counts[level]
        print(f"{level}: {actual}")
    
    print("="*60)
    print(f"Total entries in sample: {total_sample:,}")
    print(f"Average per file: {total_sample // sample_size if sample_size > 0 else 0}")
    print("="*60)
    
    print("\n✓ Sample verification complete!")
    print(f"\nYou can now run: python3 base_log_analyzer.py {log_dir}")
    print("="*60)

if __name__ == '__main__':
    # Set random seed for reproducibility
    random.seed(42)
    
    print("="*60)
    print("Distributed Log Analyser - Test Data Generator")
    print("="*60)
    print()
    
    generate_log_files(output_dir='sample_logs', num_files=10000)
    
    print("\n" + "="*60)
    print("Generation complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Test sequential analyzer: python3 base_log_analyzer.py sample_logs")
    print("2. Implement parallel version: parallel_log_analyzer.py")
    print("3. Implement distributed version: distributed_log_analyzer.py")
    print("="*60)