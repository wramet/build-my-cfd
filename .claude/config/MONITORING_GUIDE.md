# Performance Monitoring & Benchmarking Guide

This guide explains how to use the performance monitoring and benchmarking tools to measure the impact of optimizations.

## Quick Start

```bash
# 1. Run benchmark suite
python3 .claude/scripts/benchmark_performance.py --test all

# 2. Run workflow tests
python3 .claude/scripts/workflow_test.py --workflow all

# 3. Check monitoring stats
python3 .claude/scripts/performance_monitor.py --stats
```

---

## Available Tools

### 1. Benchmark Suite (`benchmark_performance.py`)

Runs unit tests for individual optimization features.

```bash
# Test all benchmarks
python3 .claude/scripts/benchmark_performance.py --test all

# Test specific feature
python3 .claude/scripts/benchmark_performance.py --test parallel
python3 .claude/scripts/benchmark_performance.py --test cache
python3 .claude/scripts/benchmark_performance.py --test hitrate
python3 .claude/scripts/benchmark_performance.py --test deps
```

**What it measures:**
- Parallel execution: Time savings from running agents in parallel
- Cache warmup: Time to cache common prefixes
- Cache hit rate: Effectiveness of cache (target: 80%)
- Dependency resolution: Accuracy of parallel agent detection

**Results saved to:** `/tmp/benchmark_results/benchmark_YYYYMMDD_HHMMSS.json`

---

### 2. Workflow Test (`workflow_test.py`)

End-to-end workflow testing with realistic agent simulation.

```bash
# Test all workflows
python3 .claude/scripts/workflow_test.py --workflow all

# Test specific workflow
python3 .claude/scripts/workflow_test.py --workflow sequential
python3 .claude/scripts/workflow_test.py --workflow parallel
python3 .claude/scripts/workflow_test.py --workflow compare
python3 .claude/scripts/workflow_test.py --workflow cache
```

**What it measures:**
- Sequential vs parallel execution time
- Cache effectiveness across multiple runs
- Real-world workflow performance

**Results saved to:** `/tmp/benchmark_results/workflow_test_YYYYMMDD_HHMMSS.json`

---

### 3. Performance Monitor (`performance_monitor.py`)

Continuous monitoring for production workflows.

```bash
# Show statistics (last 7 days by default)
python3 .claude/scripts/performance_monitor.py --stats

# Show statistics for last 30 days
python3 .claude/scripts/performance_monitor.py --stats --days 30

# Reset all metrics
python3 .claude/scripts/performance_monitor.py --reset
```

**What it tracks:**
- Workflow execution times
- Agent performance
- Cache hit rates
- Success rates

**Data stored in:** `/tmp/performance_monitor/`

---

### 4. Workflow Monitoring Wrapper (`monitor_workflow.py`)

Easy-to-use decorators and context managers for monitoring.

#### Using as a decorator:

```python
from .claude.scripts.monitor_workflow import monitor_workflow

@monitor_workflow("content_creation")
def create_daily_content(day):
    # Your workflow code here
    print(f"Creating content for day {day}")
    return "success"

# Usage
create_daily_content(13)
```

#### Using as a context manager:

```python
from .claude.scripts.monitor_workflow import time_workflow
import time

def my_workflow():
    with time_workflow("my_workflow", {"day": 13}):
        # Your workflow code here
        time.sleep(1)

# Usage
my_workflow()

# Check stats
from .claude.scripts.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
monitor.print_stats()
```

---

## Understanding the Results

### Benchmark Results

```
======================================================================
               PERFORMANCE BENCHMARK SUITE
======================================================================

BENCHMARK: Parallel Agent Execution
------------------------------------------------------------
Agents: ['researcher', 'engineer']
Sequential time: 75s
Parallel time: 40s
Time saved: 35s
Improvement: 46.7%

BENCHMARK: Prompt Cache Warmup
------------------------------------------------------------
Files warmed: 5
Total tokens cached: 11,338
Warmup time: 0.0s
Estimated cost saved (90%): $0.102

BENCHMARK: Cache Hit Rate (Realistic)
------------------------------------------------------------
Total requests: 50
Hits: 40
Misses: 10
Overall hit rate: 80.0%
Target: 80%
Status: ✅ PASS

BENCHMARK: Dependency Resolution
------------------------------------------------------------
Accuracy: 100.0%
Target: 100%
Status: ✅ PASS
```

### Workflow Test Results

```
======================================================================
                    SOURCE-FIRST WORKFLOW (SEQUENTIAL)
======================================================================
📚 Stage 1: Researcher - Extracting ground truth...
   ✓ Completed in 2.01s
🔧 Stage 2: Engineer - Analyzing code...
   ✓ Completed in 2.51s
✅ Stage 3: Verifier - Validating results...
   ✓ Completed in 1.51s

Total time: 6.02s

======================================================================
                    SOURCE-FIRST WORKFLOW (PARALLEL)
======================================================================
📚🔧 Stage 1: Researcher + Engineer (Running in PARALLEL)...
   ✓ Researcher completed in 2.50s
   ✓ Engineer completed in 2.00s
✅ Stage 2: Verifier - Validating results...
   ✓ Completed in 1.51s

Total time: 4.01s

COMPARISON SUMMARY
======================================================================
Sequential: 6.02s
Parallel:   4.01s
⚡ Time saved: 2.01s
📈 Improvement: 33.4%
```

### Monitoring Stats

```
======================================================================
                  PERFORMANCE MONITORING STATS
======================================================================

Period: Last 7 days
Workflows: 42
Total time: 1543.2s
Avg time: 36.7s

Agent Performance:
  researcher:
    Executions: 25
    Avg duration: 12.3s
    Success rate: 100.0%

  engineer:
    Executions: 18
    Avg duration: 15.7s
    Success rate: 94.4%

Cache Hit Rate: 84.7%
```

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Parallel execution improvement | ≥40% | 46.7% ✅ |
| Cache hit rate | ≥80% | 80% ✅ |
| Dependency resolution accuracy | 100% | 100% ✅ |
| Token cost reduction | ≥85% | TBD* |

\* Token cost reduction measured in actual production usage

---

## Troubleshooting

### Cache Hit Rate is 0%

**Cause:** Cache not being warmed or keys not matching.

**Solution:**
```bash
# Warm the cache manually
python3 .claude/skills/prompt-caching/warm_cache.py --project-root .

# Verify cache contents
python3 .claude/skills/prompt-caching/cache_manager.py --stats
```

### Parallel Execution Not Working

**Cause:** Agent dependencies not properly configured.

**Solution:**
```bash
# Check agent dependencies
python3 .claude/skills/parallel-agents/dependency_resolver.py \
    --agents "agent1,agent2" --check
```

### Metrics Not Being Recorded

**Cause:** Monitor not being called in workflows.

**Solution:** Add monitoring to your workflow scripts:
```python
from .claude.scripts.monitor_workflow import monitor_workflow

@monitor_workflow("my_workflow")
def my_function():
    # Your code
    pass
```

---

## Integration with CI/CD

Add benchmark to your CI pipeline:

```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmark

on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run benchmarks
        run: |
          python3 .claude/scripts/benchmark_performance.py --test all
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: /tmp/benchmark_results/
```

---

## Summary

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `benchmark_performance.py` | Unit tests for features | Development, CI/CD |
| `workflow_test.py` | End-to-end workflow testing | Before release |
| `performance_monitor.py` | Production monitoring | Ongoing |
| `monitor_workflow.py` | Easy workflow instrumentation | In your scripts |

For questions or issues, check the results files in `/tmp/benchmark_results/` for detailed JSON output.
