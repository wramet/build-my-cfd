# Best Practices for OpenFOAM Automation

Best practices สำหรับ automation scripts ใน OpenFOAM workflows

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **เขียน** shell scripts ที่มี proper error handling
2. **implement** logging และ debugging techniques
3. **ออกแบบ** cleanup strategies สำหรับ temporary files
4. **สร้าง** reproducible simulation workflows
5. **หลีกเลี่ยง** common anti-patterns ใน automation

---

## 🏗️ 3W Framework

### What: Best Practices คืออะไร?

**Best practices** คือ patterns และ techniques ที่พิสูจน์แล้วว่าช่วยให้:
- Scripts ทำงานได้ reliable
- Debug ง่ายเมื่อมีปัญหา
- Reproducible results
- Maintainable code

### Why: ทำไมต้องมี Best Practices?

| Without Best Practices | With Best Practices |
|------------------------|---------------------|
| Silent failures | Clear error messages |
| Lost time | Quick debugging |
| Unreproducible results | Reproducible workflow |
| Hard to maintain | Clean, documented code |

### How: 5 Core Practices

1. **Error Handling** — จัดการ errors อย่างเหมาะสม
2. **Logging** — บันทึก output สำหรับ debugging
3. **Cleanup** — จัดการ temporary files
4. **Reproducibility** — ทำให้ simulation ทำซ้ำได้
5. **Parallel Safety** — ป้องกันปัญหาใน parallel runs

---

## 1. Error Handling

### Basic Error Handling

```bash
#!/bin/bash
set -e    # Exit on first error
set -u    # Error on undefined variables
set -o pipefail  # Catch errors in pipelines

# Trap errors
trap 'echo "Error on line $LINENO"' ERR
```

### Command-Level Handling

```bash
# ❌ Bad: Silent failure
blockMesh
simpleFoam

# ✅ Good: Check each command
blockMesh || { echo "blockMesh failed"; exit 1; }
simpleFoam || { echo "Solver failed"; exit 1; }

# ✅ Better: With cleanup
run_solver() {
    simpleFoam
    local status=$?
    if [ $status -ne 0 ]; then
        echo "Solver failed with status $status"
        cleanup_temp_files
        exit $status
    fi
}
```

### Validate Inputs

```bash
# Check required files exist
required_files=("system/controlDict" "constant/polyMesh/points")
for f in "${required_files[@]}"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Required file '$f' not found"
        exit 1
    fi
done

# Check OpenFOAM environment
if [ -z "$WM_PROJECT_DIR" ]; then
    echo "ERROR: OpenFOAM not sourced"
    exit 1
fi
```

---

## 2. Logging

### Basic Logging

```bash
# Redirect to log file
LOG_FILE="run_$(date +%Y%m%d_%H%M%S).log"

# Log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting simulation"
blockMesh 2>&1 | tee -a "$LOG_FILE"
log "Mesh created"
```

### Separate stdout and stderr

```bash
# Log both but separate
simpleFoam > >(tee stdout.log) 2> >(tee stderr.log >&2)
```

### Log Rotation

```bash
# Keep only last 5 logs
MAX_LOGS=5
ls -t run_*.log | tail -n +$((MAX_LOGS+1)) | xargs -r rm
```

---

## 3. Cleanup

### Standard Cleanup

```bash
cleanup() {
    log "Cleaning up..."
    rm -rf processor*  # Remove decomposed mesh
    rm -rf 0.[0-9]*    # Remove early timesteps
    log "Cleanup complete"
}

# Run cleanup on exit (success or failure)
trap cleanup EXIT
```

### Selective Cleanup

```bash
# Keep only latest result
keep_latest() {
    local latest=$(foamListTimes -latestTime)
    foamListTimes -rm -excludeFirst -excludeLast
    log "Kept only time=$latest"
}
```

### Before Parallel Run

```bash
# Clean before decomposition
clean_parallel() {
    rm -rf processor*
    rm -rf postProcessing
    rm -rf log.*
}

clean_parallel
decomposePar
```

---

## 4. Reproducibility

### Environment Documentation

```bash
# Save environment info
save_environment() {
    {
        echo "Date: $(date)"
        echo "User: $USER"
        echo "Host: $(hostname)"
        echo "OpenFOAM: $WM_PROJECT_VERSION"
        echo "Commit: $(cd $WM_PROJECT_DIR && git rev-parse HEAD 2>/dev/null || echo 'N/A')"
        echo "PATH: $PATH"
    } > environment.txt
}
```

### Git Integration

```bash
# Tag simulation with git commit
git_tag_simulation() {
    local case_dir=$1
    local commit=$(git rev-parse --short HEAD)
    cp -r "$case_dir" "${case_dir}_${commit}"
    echo "Tagged simulation with commit $commit"
}
```

### README Generation

```bash
# Auto-generate README
generate_readme() {
    cat > README.md << EOF
# Simulation: $(basename $PWD)

## Date
$(date)

## Commands
\`\`\`bash
blockMesh
simpleFoam
\`\`\`

## Settings
- Mesh: $(checkMesh 2>&1 | grep "cells:")
- Solver: simpleFoam
- Turbulence: $(grep turbulenceModel constant/turbulenceProperties | head -1)

## Results
- Final time: $(foamListTimes -latestTime)
EOF
}
```

---

## 5. Parallel Safety

### Complete Parallel Workflow

```bash
#!/bin/bash
set -e

NPROCS=8

# 1. Clean previous runs
rm -rf processor* log.*

# 2. Mesh and decompose
blockMesh
decomposePar

# 3. Run parallel
mpirun -np $NPROCS simpleFoam -parallel > log.simpleFoam 2>&1

# 4. Check success
if grep -q "End" log.simpleFoam; then
    echo "Simulation completed successfully"
else
    echo "ERROR: Simulation may have failed"
    exit 1
fi

# 5. Reconstruct
reconstructPar -latestTime
```

### Force Overwrite

```bash
# Always use -force for re-runs
decomposePar -force
reconstructPar -latestTime
```

---

## ❌ Anti-Patterns to Avoid

### Anti-Pattern 1: No Error Checking

```bash
# ❌ Bad
blockMesh
simpleFoam
paraFoam

# ✅ Good
blockMesh || exit 1
simpleFoam || exit 1
```

### Anti-Pattern 2: Hardcoded Paths

```bash
# ❌ Bad
cd /home/user/simulations/case1

# ✅ Good
CASE_DIR="${1:-.}"
cd "$CASE_DIR"
```

### Anti-Pattern 3: No Logging

```bash
# ❌ Bad: No record of what happened
simpleFoam

# ✅ Good: Keep log
simpleFoam 2>&1 | tee log.simpleFoam
```

### Anti-Pattern 4: Modifying Source Files In-Place

```bash
# ❌ Bad: Overwrites original
sed -i 's/endTime 100/endTime 200/' system/controlDict

# ✅ Good: Keep backup
cp system/controlDict system/controlDict.bak
sed -i 's/endTime 100/endTime 200/' system/controlDict
```

---

## 📋 Quick Reference

| Practice | Key Command/Pattern |
|----------|-------------------|
| Exit on error | `set -e` |
| Undefined vars | `set -u` |
| Pipeline errors | `set -o pipefail` |
| Error trap | `trap 'handler' ERR` |
| Logging | `tee log.file` |
| Cleanup trap | `trap cleanup EXIT` |
| Force overwrite | `decomposePar -force` |

---

## 🧠 Concept Check

<details>
<summary><b>1. set -e, set -u, set -o pipefail ทำหน้าที่อะไร?</b></summary>

- **set -e**: Exit ทันทีเมื่อ command fail
- **set -u**: Error เมื่อใช้ undefined variable
- **set -o pipefail**: Pipeline fail ถ้า command ใดใน pipe fail

**ใช้รวมกันเพื่อ early error detection**
</details>

<details>
<summary><b>2. ทำไมต้องใช้ trap?</b></summary>

**trap ช่วยให้:**
- จัดการ errors gracefully
- Cleanup เมื่อ script exit (success หรือ fail)
- Log ตำแหน่งที่เกิด error
</details>

---

## 📖 Related Documents

- [06_Integration_with_Solver_Workflows.md](06_Integration_with_Solver_Workflows.md) — Workflow integration
- [05_Creating_Custom_Utilities.md](05_Creating_Custom_Utilities.md) — Custom utilities
- [00_Overview.md](00_Overview.md) — Module overview