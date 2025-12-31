# Integration with Solver Workflows

การเชื่อมโยง Utilities เข้ากับ Solver Workflow ใน OpenFOAM

---

## Learning Objectives 🎯

หลังจากอ่านบทนี้ คุณจะสามารถ:

- **อธิบาย (Explain)** ประโยชน์ของการใช้ integrated workflow approach ที่เป็นระบบ เทียบกับ ad-hoc approach ที่ไม่เป็นระบบ
- **ออกแบบ (Design)** solver workflow script ที่เชื่อมโยง pre-processing, solving, และ post-processing เข้าด้วยกัน
- **นำไปใช้ (Implement)** function objects สำหรับ on-the-fly post-processing ระหว่าง simulation
- **แก้ไขปัญหา (Troubleshoot)** ปัญหาทั่วไปในการ integrate utilities กับ solver workflows
- **สร้าง (Create)** complete workflow scripts สำหรับ automated simulation pipelines

---

## What? What is Solver Workflow Integration? 📋

**Solver Workflow Integration** คือการเชื่อมโยง utilities และ tools ต่างๆ ของ OpenFOAM เข้ากับ solver execution ในรูปแบบของ automated workflow ที่เป็นระบบ โดยแบ่งเป็น 3 ระยะหลัก:

### 1. Pre-Processing Phase
- Mesh generation (`blockMesh`, `snappyHexMesh`)
- Mesh quality checking (`checkMesh`)
- Initial field setup (`setFields`, `funkySetFields`)
- Domain decomposition (`decomposePar`)

### 2. Solving Phase
- Serial or parallel solver execution
- Runtime monitoring and control
- Function objects for on-the-fly processing

### 3. Post-Processing Phase
- Solution reconstruction (`reconstructPar`)
- Field computation (`postProcess`)
- Data export (`foamToVTK`, `foamToEnsight`)
- Visualization and analysis

---

## Why? Benefits of Integrated Workflow 🤔

### ✅ **Why use integrated workflow instead of ad-hoc commands?**

| Aspect | Ad-Hoc Approach | Integrated Workflow |
|--------|----------------|---------------------|
| **Consistency** | คำสั่งอาจไม่สม่ำเสมอ ลืม step ง่าย | Standardized ทุกครั้ง |
| **Reproducibility** | ยากต่อการทำซ้ำ | Fully reproducible |
| **Error Reduction** | Human error สูง | Automated validation |
| **Time Efficiency** | Manual intervention | เดินอัตโนมัติ |
| **Scalability** | Difficult to scale | Easy parallel scaling |
| **Documentation** | Scattered notes | Self-documenting scripts |

### 🎯 **Key Benefits**

1. **Reduced Human Error**
   - Automated sequence eliminates manual command errors
   - Built-in validation checks between phases
   - Consistent parameter settings

2. **Improved Reproducibility**
   - Same workflow produces identical results
   - Version-controlled scripts document entire process
   - Easy to share and replicate

3. **Enhanced Productivity**
   - "Fire-and-forget" automation
   - Automatic error handling and recovery
   - Batch processing capabilities

4. **Better Resource Management**
   - Optimal parallel decomposition
   - Automatic cleanup of intermediate files
   - Efficient disk space usage

5. **Seamless Integration**
   - Function objects enable on-the-fly analysis
   - No need to store all time steps
   - Real-time monitoring capabilities

---

## How? Implementing Solver Workflows 🛠️

### 1. Pre-Processing Scripts

การเตรียมข้อมูลเบื้องต้นก่อนการคำนวณ:

```bash
#!/bin/bash
# File: Allrun.pre
# Purpose: Execute all pre-processing steps

# Echo phase information
echo "========================================"
echo "Starting Pre-Processing Phase"
echo "========================================"

# 1. Generate base mesh
echo "[1/5] Running blockMesh..."
blockMesh > log.blockMesh 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: blockMesh failed. Check log.blockMesh"
    exit 1
fi

# 2. Refine mesh with snappyHexMesh (if applicable)
if [ -f system/snappyHexMeshDict ]; then
    echo "[2/5] Running snappyHexMesh..."
    snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: snappyHexMesh failed. Check log.snappyHexMesh"
        exit 1
    fi
fi

# 3. Check mesh quality
echo "[3/5] Checking mesh quality..."
checkMesh > log.checkMesh 2>&1
if [ $? -ne 0 ]; then
    echo "WARNING: Mesh quality issues detected. Check log.checkMesh"
fi

# 4. Set initial fields
echo "[4/5] Setting initial fields..."
if [ -f system/setFieldsDict ]; then
    setFields > log.setFields 2>&1
fi

# 5. Decompose for parallel run
echo "[5/5] Decomposing case..."
decomposePar > log.decomposePar 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: decomposePar failed. Check log.decomposePar"
    exit 1
fi

echo "========================================"
echo "Pre-Processing completed successfully!"
echo "========================================"
```

**Key Components:**
- ✅ Error checking after each command
- ✅ Informative progress messages
- ✅ Conditional execution for optional utilities
- ✅ Proper exit codes for error handling

---

### 2. Solver Execution Scripts

การรัน solver ทั้งแบบ serial และ parallel:

```bash
#!/bin/bash
# File: Allrun.solve
# Purpose: Execute solver with proper configuration

# Get number of processors
NPROCS=$(getNumberOfProcessors)
echo "Running on $NPROCS processors"

# Check if this is a parallel run
if [ $NPROCS -gt 1 ]; then
    echo "========================================"
    echo "Starting Parallel Solver Execution"
    echo "========================================"
    
    # Parallel execution
    mpirun -np $NPROCS \
        simpleFoam -parallel \
        > log.solver 2>&1
    
    # Check solver exit status
    if [ $? -ne 0 ]; then
        echo "ERROR: Solver execution failed. Check log.solver"
        tail -50 log.solver
        exit 1
    fi
else
    echo "========================================"
    echo "Starting Serial Solver Execution"
    echo "========================================"
    
    # Serial execution
    simpleFoam > log.solver 2>&1
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Solver execution failed. Check log.solver"
        tail -50 log.solver
        exit 1
    fi
fi

echo "========================================"
echo "Solver execution completed successfully!"
echo "Final time: $(foamListTimes -latestTime)"
echo "========================================"
```

**Best Practices:**
- ✅ Automatic processor detection
- ✅ Unified interface for serial/parallel
- ✅ Comprehensive logging
- ✅ Error detection and reporting

---

### 3. Post-Processing Scripts

การประมวลผลหลังการคำนวณเสร็จสิ้น:

```bash
#!/bin/bash
# File: Allrun.post
# Purpose: Execute post-processing and visualization

echo "========================================"
echo "Starting Post-Processing Phase"
echo "========================================"

# Get latest time directory
LATEST_TIME=$(foamListTimes -latestTime)
echo "Latest time: $LATEST_TIME"

# 1. Reconstruct parallel results
NPROCS=$(getNumberOfProcessors)
if [ $NPROCS -gt 1 ]; then
    echo "[1/5] Reconstructing parallel results..."
    reconstructPar -latestTime > log.reconstructPar 2>&1
fi

# 2. Run postProcess functions
echo "[2/5] Computing derived fields..."
postProcess -func 'yPlus' -time $LATEST_TIME > log.yPlus 2>&1
postProcess -func 'wallShearStress' -time $LATEST_TIME > log.wss 2>&1

# 3. Export to VTK for ParaView
echo "[3/5] Exporting to VTK format..."
foamToVTK -latestTime > log.foamToVTK 2>&1

# 4. Generate plots (if Python scripts available)
echo "[4/5] Generating plots..."
if [ -f scripts/plot_results.py ]; then
    python3 scripts/plot_results.py $LATEST_TIME
fi

# 5. Generate summary report
echo "[5/5] Generating summary..."
echo "Simulation Summary:" > SUMMARY.txt
echo "Case: $(basename $(pwd))" >> SUMMARY.txt
echo "Latest Time: $LATEST_TIME" >> SUMMARY.txt
echo "Completion: $(date)" >> SUMMARY.txt

if grep -q "Finalise" log.solver; then
    echo "Status: CONVERGED" >> SUMMARY.txt
else
    echo "Status: CHECK LOGS" >> SUMMARY.txt
fi

echo "========================================"
echo "Post-Processing completed!"
echo "VTK files available in VTK/ directory"
echo "========================================"
```

**Features:**
- ✅ Automatic latest time detection
- ✅ Multiple post-processing functions
- ✅ Visualization export
- ✅ Summary report generation
- ✅ Convergence status checking

---

### 4. Complete Workflow Integration

รวมทุก phase เข้าด้วยกันใน master script:

```bash
#!/bin/bash
# File: Allrun
# Purpose: Master script for complete simulation workflow

# Start timing
START_TIME=$(date +%s)

# Function to print phase headers
print_header() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║  $1"
    echo "╚════════════════════════════════════════╝"
    echo ""
}

# Function to handle errors
error_exit() {
    echo "❌ ERROR: $1"
    echo "Workflow stopped at phase: $CURRENT_PHASE"
    exit 1
}

# Main workflow
print_header "OPENFOAM WORKFLOW - START"
echo "Case directory: $(pwd)"
echo "Start time: $(date)"
echo ""

# Phase 1: Pre-Processing
CURRENT_PHASE="PRE-PROCESSING"
print_header "PHASE 1: PRE-PROCESSING"
./Allrun.pre || error_exit "Pre-processing failed"

# Phase 2: Solving
CURRENT_PHASE="SOLVING"
print_header "PHASE 2: SOLVER EXECUTION"
./Allrun.solve || error_exit "Solver execution failed"

# Phase 3: Post-Processing
CURRENT_PHASE="POST-PROCESSING"
print_header "PHASE 3: POST-PROCESSING"
./Allrun.post || error_exit "Post-processing failed"

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))
SECONDS=$((ELAPSED % 60))

# Final summary
print_header "WORKFLOW COMPLETED SUCCESSFULLY"
echo "Total elapsed time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo "Results available in: $(foamListTimes -latestTime)"
echo "Check SUMMARY.txt for detailed report"
echo ""
echo "✅ All phases completed!"
```

---

### 5. Function Objects for On-the-Fly Processing

**Why use function objects?**
- ลดการเก็บข้อมูลที่ไม่จำเป็น (save disk space)
- ได้ผลลัพธ์ระหว่าง simulation (real-time monitoring)
- ลด post-processing time หลัง simulation

#### การตั้งค่าใน `system/controlDict`:

```cpp
// File: system/controlDict
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;
writeControl    timeStep;
writeInterval   100;

// Function objects for on-the-fly processing
functions
{
    // 1. Field averaging
    fieldAverage1
    {
        type            fieldAverage;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeControl    writeTime;
        
        fields
        {
            U
            {
                mean        on;
                prime2Mean  on;
                base        time;
            }
            p
            {
                mean        on;
                prime2Mean  on;
                base        time;
            }
        }
    }
    
    // 2. Force coefficients
    forces1
    {
        type            forces;
        functionObjectLibs ("libforces.so");
        writeControl    timeStep;
        writeInterval   1;
        
        patches         ("wall");
        rho             rhoInf;
        rhoInf          1.0;
        log             true;
    }
    
    coeffs1
    {
        $forces1;
        type            forceCoeffs;
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         10.0;
        lRef            1.0;
        ARef            1.0;
    }
    
    // 3. Wall y+ calculation
    yPlus1
    {
        type            yPlus;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeControl    writeTime;
        writeFields     true;
    }
    
    // 4. Probes for specific locations
    probeLocations
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        writeControl    timeStep;
        writeInterval   10;
        
        probeLocations
        (
            (0.5 0.5 0.0)
            (1.0 0.5 0.0)
            (1.5 0.5 0.0)
        );
        
        fields          (p U);
    }
    
    // 5. Surface sampling
    cuttingPlane
    {
        type            surfaces;
        functionObjectLibs ("libsampling.so");
        writeControl    writeTime;
        
        surfaceFormat   vtk;
        fields          (p U);
        
        surfaces
        {
            zNormal
            {
                type        cuttingPlane;
                planeType   pointAndNormal;
                pointAndNormalDict
                {
                    point   (0 0 0);
                    normal  (0 0 1);
                }
                interpolate true;
            }
        }
    }
    
    // 6. Residuals monitoring
    residuals1
    {
        type            residuals;
        functionObjectLibs ("libutilityFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   1;
        
        fields          (p U);
    }
}
```

#### การอ่านและใช้งาน function objects output:

```bash
# Function objects สร้าง directories ดังนี้:
postProcessing/
├── fieldAverage1/          # ค่าเฉลี่ยของ fields
├── forces1/                # แรงที่กระทำต่อ surfaces
├── coeffs1/                # สัมประสิทธิ์ drag/lift
├── yPlus1/                 # ค่า y+ บน wall
├── probeLocations/         # ค่าที่จุดวัด
├── cuttingPlane/           # ค่าบน cutting planes
└── residuals1/             # Residual evolution

# Plot force coefficients (Python)
python3 << EOF
import pandas as pd
import matplotlib.pyplot as plt

# Read force coefficients
df = pd.read_csv('postProcessing/coeffs1/0/coeffs.csv', 
                 sep='\t', skiprows=3)

# Plot drag and lift
plt.figure(figsize=(10, 6))
plt.plot(df['Time'], df['Cd'], label='Drag Coefficient')
plt.plot(df['Time'], df['Cl'], label='Lift Coefficient')
plt.xlabel('Time')
plt.ylabel('Coefficient')
plt.legend()
plt.grid(True)
plt.savefig('force_coefficients.png')
print("Plot saved to force_coefficients.png")
EOF
```

---

### 6. Advanced Workflow Techniques

#### 6.1 Conditional Execution

```bash
#!/bin/bash
# Allrun.advanced

# Check for previous results
if [ -d "0.001" ]; then
    echo "Found previous results. Continue from latest time?"
    read -p "Continue? (y/n): " choice
    
    if [ "$choice" == "y" ]; then
        # Modify controlDict for restart
        LATEST_TIME=$(foamListTimes -latestTime)
        sed -i "s/startFrom.*;/startFrom latestTime;/" system/controlDict
        echo "Restarting from time $LATEST_TIME"
    fi
fi

# Adaptive time stepping check
if grep -q "adjustTimeStep yes;" system/controlDict; then
    echo "Adaptive time stepping enabled"
    echo "Max Courant number will control time step size"
fi
```

#### 6.2 Parameter Sweeping

```bash
#!/bin/bash
# run_parameter_sweep.sh

# Sweep over velocity values
VELOCITIES=(5 10 15 20)

for U_INF in "${VELOCITIES[@]}"; do
    echo "========================================"
    echo "Running case for UInf = $U_INF m/s"
    echo "========================================"
    
    # Create case directory
    CASE_DIR="case_Uinf_${U_INF}"
    cp -r base_case $CASE_DIR
    cd $CASE_DIR
    
    # Modify boundary condition
    sed -i "s/UINF_VALUE/$U_INF/g" 0/U
    
    # Run simulation
    ./Allrun
    
    # Store results
    cd ..
    echo "Completed case: $CASE_DIR"
done

echo "All parameter sweep cases completed!"
```

#### 6.3 Batch Processing

```bash
#!/bin/bash
# run_batch_cases.sh

# Array of cases to run
CASES=(
    "case_01_lowRe"
    "case_02_mediumRe"
    "case_03_highRe"
)

# Loop through cases
for CASE in "${CASES[@]}"; do
    echo "Processing $CASE..."
    
    if [ -d "$CASE" ]; then
        cd $CASE
        ./Allrun || echo "WARNING: $CASE failed"
        cd ..
    else
        echo "ERROR: Directory $CASE not found"
    fi
done

echo "Batch processing complete!"
```

---

## Troubleshooting Common Issues 🔧

### ❌ **Issue 1: Pre-Processing Failures**

**Symptoms:**
- `blockMesh` fails with "patch name not found"
- `snappyHexMesh` fails with "no cells extracted"
- `checkMesh` reports high non-orthogonality

**Solutions:**

```bash
# Debug blockMesh
blockMesh -debug > log.blockMesh.debug 2>&1
# Check for syntax errors in blockMeshDict

# Fix snappyHexMesh issues:
# 1. Check geometry:
ls -l constant/triSurface/
# 2. Verify refinement levels:
grep -A 5 "refinementLevels" system/snappyHexMeshDict
# 3. Increase castellation if needed:
# In snappyHexMeshDict:
castellatedMeshControls
{
    maxGlobalCells  200000000;  // Increase
}

# Check mesh quality specifically
checkMesh -allGeometry -allTopology
```

**Prevention:**
- Always run `checkMesh` between mesh generation and solver
- Use intermediate quality checks
- Start with coarser mesh to test setup

---

### ❌ **Issue 2: Solver Execution Failures**

**Symptoms:**
- Solver crashes with "Floating point exception"
- Maximum iterations exceeded
- Time step continues to decrease

**Solutions:**

```bash
# 1. Check initial conditions
foamListTimes
ls -l 0/

# 2. Verify boundary conditions
grep -A 10 "boundaryField" 0/U

# 3. Relax solver settings
# In fvSolution:
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;      // Relax from 1e-08
        relTol          0.1;        // Increase from 0.01
    }
}

# 4. Adjust time step for stability
# In controlDict:
deltaT          0.001;      // Decrease from 0.01
maxCo           0.5;        // Add if not present

# 5. Check residuals
tail -100 log.solver | grep "Solving for"
```

**Prevention:**
- Use `setFields` for better initial conditions
- Start with smaller time step, increase gradually
- Monitor residuals from start

---

### ❌ **Issue 3: Parallel Decomposition Issues**

**Symptoms:**
- `decomposePar` fails with "insufficient processor patches"
- Solver hangs during execution
- Reconstruction fails with "time directories inconsistent"

**Solutions:**

```bash
# 1. Check decomposition
decomposePar -debug
# Look for warning messages

# 2. Verify processor directories
ls -d processor*

# 3. Try different decomposition methods
# In decomposeParDict:
method          scotch;     // Or: simple, hierarchical, manual

# For simple method:
simpleCoeffs
{
    n           (4 2 1);    // Adjust for better balance
    delta       0.001;
}

# 4. Check load balancing
for i in processor*; do
    echo "$i: $(ls $i/0 | wc -l) cells"
done

# 5. Reconstruct properly
reconstructPar -allTime  # Include all time steps
```

**Prevention:**
- Use `scotch` for complex geometries
- Verify decomposition before long runs
- Keep processor count proportional to cell count

---

### ❌ **Issue 4: Post-Processing Errors**

**Symptoms:**
- `foamToVTK` fails with "No times selected"
- `postProcess` doesn't compute expected fields
- Missing files in postProcessing directories

**Solutions:**

```bash
# 1. Check available times
foamListTimes

# 2. Run postProcess with debug
postProcess -func 'yPlus' -debug

# 3. Verify function object syntax
# Check controlDict:
functions
{
    yPlus1
    {
        type            yPlus;  // Must match available type
        functionObjectLibs ("libfieldFunctionObjects.so");
    }
}

# 4. Force recreation of VTK
rm -rf VTK/
foamToVTK -latestTime

# 5. Check field availability
ls -l 0.1/  # Check if fields exist at that time
```

**Prevention:**
- Define function objects before simulation starts
- Verify field names match case requirements
- Check file permissions in case directory

---

### ❌ **Issue 5: Function Objects Not Executing**

**Symptoms:**
- Empty `postProcessing` directories
- Function object not called in log
- Incorrect output format

**Solutions:**

```bash
# 1. Check function object syntax
# Run with -debug option:
simpleFoam -debug 2>&1 | grep -A 5 "functionObject"

# 2. Verify library loading
# In controlDict, ensure libs are loaded:
libs
(
    "libforces.so"
    "libfieldFunctionObjects.so"
    "libsampling.so"
);

# 3. Check writeInterval
writeControl    timeStep;   // Ensure matches expectations
writeInterval   10;

# 4. Test individual function object
# Comment out all but one in controlDict

# 5. Check execution order
grep "functionObject::execute()" log.solver
```

**Prevention:**
- Start with one function object, add gradually
- Use `writeControl writeTime;` to reduce output
- Test function objects in short simulation first

---

## Quick Reference 📚

### Complete Workflow Scripts Summary

| Script | Purpose | Key Commands |
|--------|---------|--------------|
| `Allrun.pre` | Pre-processing | `blockMesh`, `snappyHexMesh`, `decomposePar` |
| `Allrun.solve` | Solver execution | `simpleFoam -parallel` |
| `Allrun.post` | Post-processing | `reconstructPar`, `postProcess`, `foamToVTK` |
| `Allrun` | Master workflow | Calls all above scripts |
| `Allclean` | Cleanup | Remove processor dirs, logs, VTK |

### Function Object Types

| Function | Library | Purpose |
|----------|---------|---------|
| `forces` | libforces.so | Compute forces on patches |
| `forceCoeffs` | libforces.so | Lift/drag coefficients |
| `fieldAverage` | libfieldFunctionObjects.so | Time averaging |
| `yPlus` | libfieldFunctionObjects.so | Wall y+ calculation |
| `probes` | libsampling.so | Point monitoring |
| `surfaces` | libsampling.so | Plane/surface sampling |
| `residuals` | libutilityFunctionObjects.so | Residual tracking |

### Common Utility Sequence

```
Setup → blockMesh → snappyHexMesh → checkMesh → setFields → 
decomposePar → SOLVER → reconstructPar → postProcess → 
foamToVTK → Visualization
```

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม function objects จึงดีกว่า post-processing ภายหลัง?</b></summary>

**On-the-fly processing:**
- ✅ ลด disk space - เก็บเฉพาะ derived quantities
- ✅ Real-time monitoring - เห็นผลระหว่าง simulation
- ✅ ลดเวลา post-processing - คำนวณเสร็จพร้อมกับ simulation
- ✅ ป้องกัน data loss - simulation crash ก็มีบางผลลัพธ์

**Post-processing หลัง:**
- ❌ ต้องเก็บทุก time step ใช้ disk มาก
- ❌ รอจน simulation เสร็จสิ้นถึงจะรู้ผล
- ❌ ใช้เวลานานหลัง simulation
</details>

<details>
<summary><b>2. Workflow scripts ควร return exit code อย่างไร?</b></summary>

**Correct error handling:**

```bash
# Good: Check exit status
command > log.command 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: command failed"
    exit 1  # Non-zero = error
fi

# Bad: Ignore errors
command  # ไม่ check exit status

# Chain with && (short-circuit)
command1 && command2 && command3
# หยุดถ้า command ใดๆ  fails
```

**Key points:**
- Exit code 0 = success
- Exit code non-zero = failure
- Master script ต้อง propagate errors อย่างถูกต้อง
</details>

<details>
<summary><b>3. เมื่อไหร่ควรใช้ serial vs parallel execution?</b></summary>

**Guidelines:**

| Cell Count | Execution Type | Reasoning |
|------------|----------------|-----------|
| < 100K | Serial | Overhead ของ parallel ไม่คุ้ม |
| 100K - 1M | Small parallel (2-8 cores) | Balance speed vs overhead |
| > 1M | Large parallel (16+ cores) | Scaling ดี |
| Debugging | Serial | Log ชัดเจน, error messages เต็มรูปแบบ |

**Rule of thumb:** 10,000 - 100,000 cells per core สำหรับ OpenFOAM
</details>

---

## Key Takeaways 🎯

### ✅ **Core Concepts**

1. **Integrated Workflow Benefits**
   - Consistency, reproducibility, error reduction
   - Time efficiency through automation
   - Scalability and documentation

2. **Three-Phase Structure**
   - Pre-process: Mesh, fields, decomposition
   - Solve: Serial/parallel with function objects
   - Post-process: Reconstruct, compute, visualize

3. **Function Objects Enable On-the-Fly Processing**
   - Reduce disk storage requirements
   - Provide real-time monitoring
   - Eliminate redundant calculations

4. **Robust Error Handling is Essential**
   - Check exit codes after each command
   - Provide informative error messages
   - Enable graceful failure recovery

5. **Standardized Scripts Improve Productivity**
   - Consistent structure across projects
   - Easy to maintain and modify
   - Self-documenting workflows

### 🔗 **Practice Integration**

- **Scripts:** Build modular `Allrun.pre`, `Allrun.solve`, `Allrun.post` files
- **Function Objects:** Configure in `system/controlDict` for on-the-fly analysis
- **Error Handling:** Always check `$?` after critical commands
- **Logging:** Redirect stdout/stderr to log files for debugging
- **Automation:** Use master `Allrun` script for complete pipeline

### 📊 **Workflow Checklist**

- [ ] Pre-processing: `blockMesh` → `snappyHexMesh` → `checkMesh`
- [ ] Initial conditions: `setFields` → `decomposePar`
- [ ] Solver execution: Configure function objects first
- [ ] Post-processing: `reconstructPar` → `postProcess` → `foamToVTK`
- [ ] Validation: Check convergence, examine residuals
- [ ] Documentation: Generate summary reports

---

## 📖 Related Documentation

- **ภาพรวม Utilities:** [00_Overview.md](00_Overview.md)
- **หมวดหมู่ Utilities:** [01_Utility_Categories_and_Organization.md](01_Utility_Categories_and_Organization.md)
- **Architecture และ Design Patterns:** [02_Architecture_and_Design_Patterns.md](02_Architecture_and_Design_Patterns.md)
- **Utilities สำหรับ CFD Tasks:** [03_Essential_Utilities_for_Common_CFD_Tasks.md](03_Essential_Utilities_for_Common_CFD_Tasks.md)
- **การสร้าง Custom Utilities:** [05_Creating_Custom_Utilities.md](05_Creating_Custom_Utilities.md)