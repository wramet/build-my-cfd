# Domain Decomposition

การแบ่งโดเมนสำหรับการประมวลผลแบบขนาน (Domain Decomposition for Parallel Computing)

---

## 📋 Learning Objectives | วัตถุประสงค์การเรียนรู้

After completing this section, you should be able to:

- **Explain** WHAT domain decomposition is and WHY it's essential for parallel CFD simulations
- **Understand** HOW different decomposition algorithms (scotch, simple, hierarchical, manual) work mathematically
- **Configure** decomposition parameters in `decomposeParDict` for optimal load balancing
- **Evaluate** decomposition quality using cell balance and interface metrics
- **Troubleshoot** common decomposition errors and performance bottlenecks
- **Apply** best practices for HPC cluster deployment

**Estimated Completion Time:** 45-60 minutes  
**Difficulty Level:** ⭐⭐⭐ (Intermediate)

---

## 🎯 Prerequisites | ข้อกำหนดเบื้องต้น

- Completed [00_Overview.md](00_Overview.md) - HPC fundamentals
- Basic understanding of OpenFOAM case structure
- Familiarity with mesh generation and boundary conditions
- Access to multi-core system or HPC cluster (optional for exercises)

---

## 📚 Overview | ภาพรวม

### WHAT is Domain Decomposition? | Domain Decomposition คืออะไร?

**Domain Decomposition** is the process of dividing a computational mesh into smaller sub-domains, each assigned to a separate processor core for simultaneous computation. This is the foundational technique for **parallel computing** in OpenFOAM, enabling large-scale simulations that would be impractical on a single processor.

**การแบ่งโดเมน (Domain Decomposition)** คือกระบวนการแบ่งเมชคอมพิวเตชันอลอออกเป็นโดเมนย่อยๆ โดยแต่ละโดเมนจะถูกมอบหมายให้กับแต่ละ core ของ processor เพื่อประมวลผลพร้อมกัน นี่คือเทคนิคพื้นฐานสำหรับ **การประมวลผลแบบขนาน (parallel computing)** ใน OpenFOAM ซึ่งทำให้สามารถจำลองได้ในขนาดใหญ่ที่ไม่สามารถทำได้ด้วย processor เดี่ยว

### WHY is it Important? | ทำไมถึงสำคัญ?

| Benefit | Description |
|---------|-------------|
| **Speed** | Reduce simulation time from weeks to hours/days through parallelization |
| **Scalability** | Handle meshes with 10M+ cells by distributing across multiple cores |
| **Resource Efficiency** | Utilize modern HPC architectures effectively |
| **Cost-Effectiveness** | Maximize ROI on cluster investments |

**ประโยชน์:**

- **ความเร็ว** - ลดเวลาจำลองจากหลายสัปดาห์เหลือเพียงชั่วโมงหรือวัน
- **การขยายขนาด** - รองรับเมช 10 ล้านเซลล์ขึ้นไป
- **ประสิทธิภาพทรัพยากร** - ใช้งานสถาปัตยกรรม HPC อย่างเต็มประสิทธิภาพ
- **ความคุ้มค่า** - สูงสุดการลงทุนใน HPC cluster

### HOW Does it Work? | หลักการทำงาน

```
Original Domain                    Decomposed Domain
┌─────────────────────┐            ┌─────┬─────┬─────┐
│                     │            │  0  │  1  │  2  │
│    Full Mesh        │    ────▶   ├─────┼─────┼─────┤
│    (1M cells)       │            │  3  │  4  │  5  │
│                     │            ├─────┼─────┼─────┤
│                     │            │  6  │  7  │  8  │
└─────────────────────┘            └─────┴─────┴─────┘
```

**Key Concepts:** แนวคิดสำคัญ:

1. **Sub-domains** - Geographic regions of the mesh assigned to each processor
2. **Processor Patches** - Boundary interfaces between adjacent sub-domains
3. **Halo Cells** - Ghost cell layers at processor boundaries for data exchange
4. **MPI Communication** - Message Passing Interface for inter-processor data transfer

<!-- IMAGE: IMG_07_001 -->
<!-- 
Purpose: เพื่อแสดงหลักการ "Domain Decomposition" ในงาน Parallel Computing. ภาพนี้ต้องโชว์การหั่น Mesh ก้อนใหญ่ให้กลายเป็นชิ้นย่อยๆ (Sub-domains) ตามจำนวน Processor และต้องเน้น "Halo Layer" หรือ "Processor Boundary" ซึ่งเป็นบริเวณที่ต้องมีการสื่อสารข้อมูลกัน
Prompt: "Parallel Computing Decomposition Visualization. **Main Object:** A complex 3D Mesh (e.g., Engine Block or Airfoil). **Decomposition:** The mesh is sliced into 4 colored zones (Red, Blue, Green, Yellow), each representing a CPU Core. **Exploded View:** The zones are slightly pulled apart to reveal the internal 'Processor Patches'. **Detail:** Zoom in to a boundary gap showing 'Halo Cells' sending data packets (arrows) across the gap. Label: 'MPI Communication'. STYLE: High-tech grid visualization, distinct zone colors, futuristic data flow aesthetics."
-->
![IMG_07_001: Domain Decomposition and Parallel Processing](../images/IMG_07_001.png)
> **Obsidian:** ![[IMG_07_001.jpg]]

---

## 🔬 Mathematical Formulation | การกำหนดรูปแบบทางคณิตศาสตร์

### Decomposition Problem | ปัญหาการแบ่งโดเมน

The domain decomposition problem can be formulated as a **graph partitioning problem**:

**ปัญหาการแบ่งโดเมนสามารถกำหนดเป็นปัญหาการแบ่งพาร์ติชันกราฟ (graph partitioning problem):**

$$
\min \left( \sum_{i=1}^{P} \frac{|V_i| - \bar{V}}{\bar{V}} \right) + \alpha \cdot \text{EdgeCut}(V_1, \ldots, V_P)
$$

Where: โดยที่:
-1$V = \{v_1, v_2, \ldots, v_N\}1= Set of mesh cells (เซลล์เมชทั้งหมด)
-1$P1= Number of processors (จำนวน processor)
-1$V_i1= Cells assigned to processor1$i1(เซลล์ที่มอบหมายให้ processor1$i$)
-1$\bar{V} = N/P1= Target cells per processor (เซลล์เป้าหมายต่อ processor)
-1$\text{EdgeCut}1= Number of edges crossing processor boundaries (จำนวนเส้นขอบที่ตัดข้ามขอบเขต processor)
-1$\alpha1= Weighting factor for communication cost (ปัจจัยถ่วงน้ำหนักสำหรับต้นทุนการสื่อสาร)

### Load Balance Metric | เมตริกความสมดุลโหลด

$$
\text{Load Balance} = \frac{N_{\max}}{\bar{N}} \times 100\%
$$

Where1$N_{\max}1is the maximum cells on any processor and1$\bar{N} = N/P1is the average.

**Ideal value:** ≤ 105% (within 5% imbalance)

**ค่าที่เหมาะสม:** ≤ 105% (ความไม่สมดุลไม่เกิน 5%)

### Communication Cost | ต้นทุนการสื่อสาร

$$
T_{\text{total}} = T_{\text{compute}} + T_{\text{communicate}} = \frac{N}{P} \cdot t_c + C \cdot t_s
$$

Where: โดยที่:
-1$T_{\text{compute}}1= Computation time (เวลาคำนวณ)
-1$T_{\text{communicate}}1= Communication time (เวลาสื่อสาร)
-1$t_c1= Time per cell operation (เวลาต่อการดำเนินการเซลล์เดียว)
-1$C1= Number of halo cells (จำนวน halo cell)
-1$t_s1= Time per MPI send/receive (เวลาต่อการส่ง/รับ MPI)

---

## 🛠️ Decomposition Methods | วิธีการแบ่งโดเมน

### Method Comparison | การเปรียบเทียบวิธีการ

| Method | Algorithm | Best For | Load Balance | Speed | Scalability |
|--------|-----------|----------|--------------|-------|-------------|
| **scotch** | Graph-based | Complex geometries | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **simple** | Geometric | Regular domains | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **hierarchical** | Multi-level | Large clusters | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **manual** | User-defined | Special cases | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **metis** | Graph-based | Alternative to scotch | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

| วิธี | อัลกอริทึม | เหมาะสำหรับ | ความสมดุลโหลด | ความเร็ว | การขยายขนาด |
|------|-----------|-------------|---------------|--------|-------------|
| **scotch** | กราฟ | เรขาคณิตซับซ้อน | ดีมาก | ปานกลาง | ดีมาก |
| **simple** | เรขาคณิต | โดเมนปกติ | ปานกลาง | เร็วมาก | ปานกลาง |
| **hierarchical** | หลายระดับ | cluster ขนาดใหญ่ | ดี | เร็ว | ดี |
| **manual** | ผู้ใช้กำหนด | กรณีพิเศษ | ต่ำ | เร็วมาก | ต่ำ |
| **metis** | กราฟ | ทางเลือก scotch | ดีมาก | ปานกลาง | ดี |

### 1. Scotch Method (Recommended) | วิธี Scotch (แนะนำ)

**Algorithm:** Recursive graph bisection using edge-cut minimization

**อัลกอริทึม:** การแบ่งกราฟแบบเรียกซ้ำโดยใช้การลด edge-cut

```cpp
// system/decomposeParDict
numberOfSubdomains 8;

method          scotch;

// Optional coefficients
scotchCoeffs
{
    // Processor weights (for heterogeneous clusters)
    processorWeights
    (
        1.0  // processor 0: standard weight
        1.0  // processor 1
        1.5  // processor 2: 50% more powerful
        1.0
        1.0
        1.5
        1.0
        1.0
    );
    
    // Strategy override (advanced)
    // strategy "b";
}
```

**Advantages:** ข้อดี:
- Automatic load balancing for complex geometries
- Minimizes inter-processor communication
- Handles non-uniform mesh refinement well

**When to Use:** เมื่อใดควรใช้:
- Complex geometries (automotive, aerospace)
- Non-uniform mesh density
- Production simulations requiring reliability

### 2. Simple Method | วิธี Simple

**Algorithm:** Cartesian division along coordinate axes

**อัลกอริทึม:** การแบ่งแบบ Cartesian ตามแกนพิกัด

```cpp
method          simple;

simpleCoeffs
{
    n           (4 2 1);     // Number of divisions in (x y z)
    
    delta       0.001;       // Cell size tolerance (optional)
}
```

**Mathematical Division:** การแบ่งทางคณิตศาสตร์:

$$
N_i = \text{round}\left(\frac{L_i \cdot N}{\sum_j L_j \cdot n_j}\right) \quad \text{for } i \in \{x, y, z\}
$$

Where1$L_i1is domain length in direction1$i1and1$n_i1is the division count.

**Advantages:** ข้อดี:
- Fastest decomposition method
- Predictable sub-domain shapes
- Easy to understand

**When to Use:** เมื่อใดควรใช้:
- Regular geometries (pipes, channels, boxes)
- Quick testing/debugging
- Homogeneous mesh density

### 3. Hierarchical Method | วิธี Hierarchical

**Algorithm:** Multi-level decomposition combining methods

**อัลกอริทึม:** การแบ่งหลายระดับที่รวมวิธีการต่างๆ

```cpp
method          hierarchical;

hierarchicalCoeffs
{
    // Level 1: Divide among nodes
    level1
    {
        method  simple;
        simpleCoeffs
        {
            n   (2 2 1);     // 4 nodes
        }
    }
    
    // Level 2: Divide within each node
    level2
    {
        method  scotch;
        numberOfSubdomains 4; // 4 cores per node
    }
}
```

**Use Case:** Use when spanning multiple compute nodes where inter-node communication is more expensive than intra-node.

**กรณีการใช้งาน:** ใช้เมื่อกระจายคำนวณข้ามหลายโหนดที่การสื่อสารระหว่างโหนดมีค่าใช้จ่ายสูงกว่าภายในโหนด

### 4. Manual Method | วิธี Manual

**Specify explicit cell-to-processor mapping using a cellZone:**

**ระบุการแม็ปเซลล์ไปยัง processor โดยตรงโดยใช้ cellZone:**

```cpp
method          manual;

manualCoeffs
{
    processorCellZone
    (
        processor0Zone
        processor1Zone
        processor2Zone
        processor3Zone
    );
}
```

**When to Use:** เมื่อใดควรใช้:
- Very specific load balancing requirements
- Debugging processor-specific issues
- Academic demonstrations

---

## 📁 Configuration File | ไฟล์การกำหนดค่า

### Complete decomposeParDict Example | ตัวอย่าง decomposeParDict แบบสมบูรณ์

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Number of sub-domains (processors)
numberOfSubdomains 8;

// Decomposition method: scotch | simple | hierarchical | manual | metis
method          scotch;

// Optional: restrict decomposition to specific region
// decomposeRegion "region1";

// Optional: preserve patches (don't decompose)
// preserveBatches (inlet outlet);

//-----------------------------------------------------------------------------

// SCOTCH coefficients (if method = scotch)
scotchCoeffs
{
    // For heterogeneous clusters
    processorWeights
    (
        1.0
        1.0
        1.0
        1.0
        1.0
        1.0
        1.0
        1.0
    );
    
    // Decomposition strategy (advanced)
    // b: default balance
    // r: recursive
    // strategy "b";
}

//-----------------------------------------------------------------------------

// SIMPLE coefficients (if method = simple)
simpleCoeffs
{
    n       (4 2 1);     // (x y z) divisions
    delta   0.001;       // Cell size tolerance
}

//-----------------------------------------------------------------------------

// HIERARCHICAL coefficients (if method = hierarchical)
hierarchicalCoeffs
{
    level1
    {
        method  simple;
        simpleCoeffs { n (2 1 1); }
    }
    level2
    {
        method  scotch;
    }
}

//-----------------------------------------------------------------------------

// MANUAL coefficients (if method = manual)
manualCoeffs
{
    processorCellZone
    (
        proc0CellZone
        proc1CellZone
    );
}

//-----------------------------------------------------------------------------

// METIS coefficients (if method = metis)
metisCoeffs
{
    // Similar to scotch
    processorWeights
    (
        1.0
        1.0
        1.0
        1.0
    );
}

// ************************************************************************* //
```

---

## 🚀 Practical Workflow | ขั้นตอนการทำงานจริง

### Step 1: Verify Mesh | ตรวจสอบเมช

```bash
# Check mesh integrity
checkMesh

# View mesh statistics
foamListTimes
```

### Step 2: Configure Decomposition | กำหนดค่าการแบ่งโดเมน

```bash
# Edit decomposition dictionary
nano system/decomposeParDict
```

### Step 3: Decompose Case | แบ่งเคส

```bash
# Basic decomposition
decomposePar

# Force overwrite existing processor directories
decomposePar -force

# Decompose specific time directory
decomposePar -time 0

# Decompose all regions (for multi-region cases)
decomposePar -allRegions

# With cell-to-processor map output
decomposePar -cellDist
```

### Step 4: Verify Decomposition | ตรวจสอบการแบ่ง

```bash
# List processor directories
ls -ld processor*/

# Check decomposed mesh in each processor
ls processor*/constant/polyMesh/

# View decomposition statistics
decomposePar -verbose | grep "cells"

# Count cells per processor
for i in processor*; do
    echo "$i:1$(grep 'cells'1$i/constant/polyMesh/owner | wc -l) cells"
done
```

**Expected Output:** ผลลัพธ์ที่คาดหวัง:

```
processor0: 125430 cells
processor1: 125389 cells
processor2: 125412 cells
processor3: 125401 cells
...
Load balance: 1.003 (0.3% imbalance) ✓
```

### Step 5: Run Solver Parallel | รัน solver แบบขนาน

```bash
# Local machine multi-core
mpirun -np 8 simpleFoam -parallel

# HPC cluster with SLURM
srun -np 64 simpleFoam -parallel

# With hostfile specification
mpirun -np 8 --hostfile hosts.txt simpleFoam -parallel

# Background execution
nohup mpirun -np 8 simpleFoam -parallel > log.solve &
```

### Step 6: Monitor Execution | ติดตามการทำงาน

```bash
# Real-time log monitoring
tail -f log.simpleFoam

# Check processor activity
top -H

# Monitor with pyFoam
pyFoamPlotRunner.py --parallel simpleFoam
```

### Step 7: Reconstruct Results | รวมผลลัพธ์

```bash
# Reconstruct all time directories
reconstructPar

# Reconstruct latest time only
reconstructPar -latestTime

# Reconstruct specific time
reconstructPar -time 1000

# Reconstruct with time range
reconstructPar -time '0:100'

# Check reconstructed case
ls -la processor*/  # Should be empty or deleted
ls 0/ constant/     # Should contain reconstructed data
```

---

## 📊 Decomposition Quality Metrics | เมตริกคุณภาพการแบ่งโดเมน

### Key Metrics | เมตริกหลัก

| Metric | Formula | Target | Good | Poor |
|--------|---------|--------|------|-------|
| **Load Balance** |1$N_{\max} / \bar{N}1| ≤ 1.05 | ≤ 1.03 | > 1.10 |
| **Interface Ratio** |1$N_{\text{interface}} / N_{\text{total}}1| ≤ 0.05 | ≤ 0.03 | > 0.10 |
| **Halo Cell Ratio** |1$N_{\text{halo}} / N_{\text{interior}}1| ≤ 0.15 | ≤ 0.10 | > 0.25 |

### Analyze Quality with decomposePar | วิเคราะห์คุณภาพด้วย decomposePar

```bash
# Decompose with statistics
decomposePar -verbose 2>&1 | tee log.decompose

# Extract key metrics
grep -E "cells|load balance" log.decompose
```

**Sample Output:** ตัวอย่างผลลัพธ์:

```
Domain decomposition:
    Decomposing mesh of 1003456 cells into 8 sub-domains

    Sub-domain cell counts:
        processor0:    125431 cells
        processor1:    125389 cells
        processor2:    125412 cells
        processor3:    125401 cells
        processor4:    125398 cells
        processor5:    125423 cells
        processor6:    125407 cells
        processor7:    125395 cells

    Load balance: 1.003 (max/avg)
    Interface cells: 124567 (12.4% of total)
```

### Visualize Decomposition | การแสดงผลการแบ่ง

```bash
# Create cell-to-processor decomposition file
decomposePar -cellDist

# Visualize in ParaView
paraFoam -builtin
# - Add "cellDist" field to view processor assignment
# - Color by processor number to see decomposition pattern
```

---

## 🔧 Troubleshooting | การแก้ปัญหา

### Common Errors and Solutions | ข้อผิดพลาดทั่วไปและวิธีแก้ไข

#### Error 1: Excessive Load Imbalance | ความไม่สมดุลโหลดมากเกินไป

```
Symptom: solver.log shows large timing differences between processors
Cause: Poor decomposition for geometry/mesh
```

**Solutions:** วิธีแก้ไข:

```bash
# Switch from simple to scotch
# In decomposeParDict:
method scotch;  // Instead of simple

# Or use hierarchical for multi-node
method hierarchical;
```

#### Error 2: High Communication Overhead | ค่าใช้จ่ายการสื่อสารสูง

```
Symptom: Poor speedup despite good load balance
Cause: Too many inter-processor boundaries
```

**Solutions:** วิธีแก้ไข:

```bash
# Reduce number of processors (less communication)
numberOfSubdomains 4;  // Instead of 16

# Use hierarchical for multi-node clusters
method hierarchical;

# Coarsen mesh in boundary regions (if possible)
```

#### Error 3: Decomposition Failure | การแบ่งโดเมนล้มเหลว

```
Error message: "Cannot decompose mesh with more processors than cells"
```

**Solutions:** วิธีแก้ไข:

```bash
# Check cell count
checkMesh | grep "cells"

# Reduce processors to ≤ total cells / 1000 minimum
# For 5000 cells, use max 4-8 processors
numberOfSubdomains 4;
```

#### Error 4: Boundary Condition Issues | ปัญหาเงื่อนไขขอบเขต

```
Symptom: Reconstruction produces NaN or incorrect values
Cause: Decomposition split through critical boundary
```

**Solutions:** วิธีแก้ไข:

```bash
# Use scotch which respects boundaries better
method scotch;

# Or manually preserve important patches
method manual;
// Define cellZones to avoid splitting boundaries
```

#### Error 5: ReconstructPar Failures | ReconstructPar ล้มเหลว

```
Error message: "Cannot read file processorX/constant/..."
```

**Solutions:** วิธีแก้ไข:

```bash
# Verify all processor directories exist
ls processor*/

# Re-run decomposePar if corrupted
decomposePar -force

# Reconstruct with tolerance
reconstructPar -latestTime -parallel
```

### Debugging Commands | คำสั่งการดีบัก

```bash
# Detailed decomposition info
decomposePar -debug -info 2>&1 | tee log.debug

# Check processor boundaries
ls processor*/constant/polyMesh/patches/

# Verify mesh consistency
for i in processor*; do
    echo "Checking1$i"
    checkMesh -case1$i > check_$i.log 2>&1
done

# Compare cell counts
for i in processor*/; do
    grep "^nCells"1$i/constant/polyMesh/faces
done
```

---

## 💡 Practical Exercises | แบบฝึกหัดปฏิบัติ

### Exercise 1: Basic Decomposition | การแบ่งโดเมนเบื้องต้น

**Objective:** Decompose a cavity case and verify load balance

```bash
# 1. Navigate to tutorial case
cd1$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily

# 2. Create decomposeParDict
cat > system/decomposeParDict << EOF
numberOfSubdomains 4;
method simple;
simpleCoeffs { n (2 2 1); }
EOF

# 3. Decompose
decomposePar

# 4. Check balance
for i in processor*/; do
    cells=$(grep "nCells"1$i/constant/polyMesh/faces | head -1)
    echo "$i:1$cells"
done

# 5. Calculate load balance ratio
# (max cells) / (average cells)
```

**Expected Result:** Load balance < 1.05

### Exercise 2: Method Comparison | การเปรียบเทียบวิธีการ

**Objective:** Compare decomposition quality between methods

```bash
# 1. Test simple method
method simple;
simpleCoeffs { n (2 2 2); }
decomposePar -force
mv log.decompose log.simple

# 2. Test scotch method
method scotch;
decomposePar -force
mv log.decompose log.scotch

# 3. Compare load balance
grep "Load balance" log.simple log.scotch
```

**Questions:** คำถาม:
1. Which method achieves better load balance for this geometry?
2. What are the timing differences?

### Exercise 3: HPC Cluster Workflow | เวิร์กโฟลว์ HPC Cluster

**Objective:** Prepare case for SLURM submission

```bash
# 1. Create SLURM submission script
cat > submit.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=openfoam_sim
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=32
#SBATCH --time=4:00:00

module load openfoam

# Decompose
decomposePar -force

# Run
mpirun -np 64 simpleFoam -parallel

# Reconstruct
reconstructPar -latestTime
EOF

# 2. Submit job
sbatch submit.sh

# 3. Monitor
squeue -u1$USER
tail -f slurm-*.out
```

### Exercise 4: Visualization | การแสดงผล

**Objective:** Visualize decomposition in ParaView

```bash
# 1. Decompose with cell distribution
decomposePar -cellDist

# 2. Open ParaView
paraFoam -builtin

# 3. In ParaView:
#    - Apply mesh
#    - Color by "cellDist" field
#    - Observe processor assignment pattern
#    - Check for irregular boundaries
```

---

## 🎓 Key Takeaways | สรุปสิ่งสำคัญ

### Essential Concepts | แนวคิดพื้นฐาน

✅ **Decomposition splits mesh** into sub-domains for parallel processing  
✅ **Load balance < 1.05** is critical for performance  
✅ **Scotch method** is recommended for most production cases  
✅ **Communication overhead** increases with more processors  
✅ **Always verify** decomposition before long runs  

### Best Practices | แนวปฏิบัติที่ดีที่สุด

1. **Test decomposition** on small cases first
2. **Monitor load balance** with `-verbose` flag
3. **Use hierarchical** for multi-node clusters
4. **Preserve boundaries** when possible (scotch does this well)
5. **Document decomposition** parameters for reproducibility

### Quick Decision Guide | คู่มือการตัดสินใจเร็ว

```
Need to decompose → Regular geometry? ─Yes→ Use simple
                       ↓ No
                    Complex geometry? ─Yes→ Use scotch
                       ↓
                    Multi-node cluster? ─Yes→ Use hierarchical
                       ↓
                    Special requirements? ─Yes→ Use manual
```

---

## 📖 Related Reading | หนังสืออ่านเพิ่มเติม

### Module References | อ้างอิงโมดูล

- **Next:** [02_Monitoring_and_Debugging.md](02_Monitoring_and_Debugging.md) - Performance monitoring and analysis
- **Previous:** [00_Overview.md](00_Overview.md) - HPC fundamentals and concepts
- **Related:** [02_PYTHON_AUTOMATION/04_Automated_Parametric_Study.md](../../02_PYTHON_AUTOMATION/04_Automated_Parametric_Study.md) - Parameter sweep automation

### OpenFOAM Documentation | เอกสาร OpenFOAM

- `decomposePar` - User Guide: Domain decomposition tools
- `reconstructPar` - User Guide: Result reconstruction
- **Running OpenFOAM in Parallel** - Programmer's Guide: Chapter 3

### External Resources | ทรัพยากรภายนอก

- **Scotch Project:** https://gforge.inria.fr/projects/scotch/
- **MPI Standard:** https://www.mpi-forum.org/
- **HPC Best Practices:** https://hpcbestpractices.org/

---

## 🧠 Concept Check | ทบทวนความเข้าใจ

<details>
<summary><b>1. Why is scotch generally preferred over simple for production cases?</b></summary>

**Answer:** Scotch uses graph-based algorithms that:
- Automatically optimize load balance for complex geometries
- Minimize inter-processor communication edges
- Handle non-uniform mesh refinement properly
- Are more reliable for industrial applications

However, simple is faster for testing and works well for regular geometries.
</details>

<details>
<summary><b>2. What is the ideal load balance ratio and why?</b></summary>

**Answer:** The ideal load balance is ≤ 1.05 (within 5% imbalance).

**Why:**
- Ensures no processor is significantly overworked
- Prevents idle time waiting for slowest processor
- Maintains good parallel efficiency
- Values > 1.10 indicate significant performance loss

**คำตอบ:** อัตราส่วนความสมดุลโหลดที่เหมาะสมคือ ≤ 1.05 (ความไม่สมดุลไม่เกิน 5%)

**ทำไม:**
- รับประกันว่าไม่มี processor ใดทำงานหนักเกินไป
- ป้องกันเวลาว่างที่รอ processor ที่ช้าที่สุด
- รักษาประสิทธิภาพการขนานที่ดี
- ค่า > 1.10 บ่งชี้การสูญเสียประสิทธิภาพอย่างมีนัยสำคัญ
</details>

<details>
<summary><b>3. How does hierarchical decomposition differ from simple/scotch?</b></summary>

**Answer:** Hierarchical decomposition:
- **Multi-level:** Decomposes first among nodes, then within each node
- **Aware of topology:** Optimizes for network communication costs
- **Best for:** Large clusters spanning multiple compute nodes
- **Example:** 2 nodes × 32 cores = hierarchical (2-level) instead of flat (64)

Simple/scotch are **single-level** and don't distinguish between inter-node and intra-node communication.
</details>

<details>
<summary><b>4. When should you use the manual decomposition method?</b></summary>

**Answer:** Manual decomposition is rarely used in production. Consider it when:
- Debugging processor-specific issues
- Demonstrating decomposition concepts (educational)
- Very specific load balancing requirements that algorithms can't meet
- Testing specific cell-to-processor assignments

For 99% of cases, use scotch or hierarchical instead.
</details>

<details>
<summary><b>5. What causes high communication overhead in parallel runs?</b></summary>

**Answer:** High communication overhead is caused by:

1. **Too many processors** for the mesh size (increased boundary area)
2. **Poor decomposition** creating irregular sub-domain shapes
3. **Geometry** with high surface-to-volume ratio
4. **Inadequate network** bandwidth between nodes

**Solutions:**
- Reduce processor count
- Use better decomposition method (scotch)
- Use hierarchical for multi-node
- Coarsen mesh if possible

**สิ่งที่ทำให้เกิดค่าใช้จ่ายการสื่อสารสูง:**
1. ใช้ processor มากเกินไปสำหรับขนาดเมช
2. การแบ่งโดเมนที่ไม่ดีสร้างรูปร่าง sub-domain ผิดปกติ
3. เรขาคณิตที่มีสัดส่วนพื้นที่ผิวต่อปริมาตรสูง
4. แบนด์วิดท์เครือข่ายไม่เพียงพอ

**วิธีแก้:**
- ลดจำนวน processor
- ใช้วิธีการแบ่งที่ดีกว่า (scotch)
- ใช้ hierarchical สำหรับหลายโหนด
- ทำเมชให้หยาบขึ้นถ้าเป็นไปได้
</details>

---

**Version:** 1.0  
**Last Updated:** 2024-01-15  
**Status:** ✅ Complete - Ready for Review