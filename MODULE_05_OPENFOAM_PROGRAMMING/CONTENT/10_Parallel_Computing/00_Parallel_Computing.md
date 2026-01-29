# Parallel Computing in OpenFOAM (การคำนวณเชิงขนานใน OpenFOAM)

## Overview (ภาพรวม)

Parallel computing in OpenFOAM enables the simulation of large-scale computational fluid dynamics (CFD) problems by distributing computational work across multiple processors. This is essential for complex R410A evaporator simulations that require high mesh resolution and fine temporal discretization.

⭐ **Key Point**: OpenFOAM uses domain decomposition to partition the computational domain into subdomains, each processed by a separate processor while maintaining communication across processor boundaries.

### 1. Domain Decomposition Principles (หลักการแบ่งโดเมน)

Domain decomposition is the foundation of parallel computing in OpenFOAM. The computational domain is partitioned into smaller subdomains that are distributed across multiple processors.

```cpp
// From: domainDecomposition.H:88
// The complete mesh
autoPtr<fvMesh> completeMesh_;

// The processor meshes
PtrList<fvMesh> procMeshes_;

// For each complete cell, the processor index
labelList cellProc_;
```

#### Decomposition Process (กระบวนการแบ่งโดเมน)

1. **Mesh Partitioning**: The computational mesh is divided into N subdomains
2. **Cell Distribution**: Cells are assigned to processors based on decomposition method
3. **Boundary Creation**: Processor boundaries are created where subdomains meet
4. **Addressing Mapping**: Local-to-global addressing is established for data exchange

#### Decomposition Methods (วิธีการแบ่งโดเมน)

OpenFOAM provides several decomposition methods through the `decompositionMethod` base class:

```cpp
// From: decompositionMethod.H:50-51
class decompositionMethod
{
protected:
    label nProcessors_;

    // Optional constraints
    PtrList<decompositionConstraint> constraints_;
```

**Available Methods:**

- **scotch**: Graph-based partitioning using Scotch library
- **metis**: Graph partitioning using METIS library
- **hierarchical**: Simple coordinate-based decomposition
- **simple**: Block-based decomposition with slight rotation
- **manual**: User-specified decomposition
- **multiLevel**: Multi-level hierarchical decomposition
- **structured**: 2D decomposition for structured meshes

```cpp
// Example: decomposeParDict configuration
numberOfSubdomains  4;

method          scotch;

scotchCoeffs
{
    /*
    processorWeights
    (
        1
        1
        1
        1
    );
    writeGraph  true;
    strategy "b";
    */
}
```

### 2. Processor Boundaries and Communication (เขตแดนระหว่างโปรเซสเซอร์และการสื่อสาร)

When a mesh is decomposed, processor patches are created at the boundaries between subdomains. These patches require special handling for data exchange.

#### Processor Patch Types (ประเภทแผนย่อยโปรเซสเซอร์)

```cpp
// From: domainDecomposition.H:124-126
//- Labels of finite volume faces for each processor boundary
//  (constructed on demand)
mutable PtrList<surfaceLabelField::Boundary> procFaceAddressingBf_;
```

1. **Processor Cyclic**: Boundary faces between adjacent subdomains
2. **Non-Conformal Processor Cyclic**: For non-matching meshes
3. **Mapped Processor Wall**: For mapped boundaries across processors

#### Communication Patterns (รูปแบบการสื่อสาร)

OpenFOAM uses MPI (Message Passing Interface) for inter-processor communication:

```cpp
// From: UPstream.H:64-70
enum class commsTypes
{
    blocking,      // Synchronous communication
    scheduled,     // Scheduled communication
    nonBlocking    // Non-blocking communication
};
```

**Communication Operations:**

```cpp
// Example: MPI-based allReduce operation
template<class Type, class BinaryOp>
void allReduce
(
    Type& Value,
    int count,
    MPI_Datatype MPIType,
    MPI_Op op,
    const BinaryOp& bop,
    const int tag,
    const label communicator
);
```

### 3. MPI Integration in OpenFOAM (การรวม MPI ใน OpenFOAM)

OpenFOAM provides a comprehensive MPI abstraction layer through the `UPstream` class:

```cpp
// From: UPstream.H:59
class UPstream
{
private:
    // By default this is not a parallel run
    static bool parRun_;

    // My processor number
    static DynamicList<int> myProcNo_;
```

#### Key MPI Functions (ฟังก์ชันหลัยของ MPI)

1. **Point-to-Point Communication**: Direct communication between processors
2. **Collective Operations**: AllReduce, AllGather, Broadcast
3. **Non-blocking Communication**: Overlapping computation and communication

```cpp
// Communication structure for processor hierarchy
class commsStruct
{
    // procID of above processor
    label above_;

    // procIDs of processors directly below me
    labelList below_;

    // procIDs of all processors below (so not just directly below)
    labelList allBelow_;

    // procIDs of all processors not below
    labelList allNotBelow_;
};
```

### 4. Load Balancing Strategies (กลยุทธ์การจัดโหลด)

Effective load balancing is critical for parallel performance. OpenFOAM provides several strategies:

#### Weight-Based Decomposition (การแบ่งโดเมนตามน้ำหนัก)

```cpp
// From: decomposeParDict:69-72
//- Use the volScalarField named here as a weight for each cell in the
//  decomposition.  For example, use a particle population field to decompose
//  for a balanced number of particles in a lagrangian simulation.
weightField dsmcRhoNMean;
```

#### Constraint-Based Decomposition (การแบ่งโดเมนด้วยข้อจำกัด)

```cpp
// From: decomposeParDict:20-67
constraints
{
   preserveBaffles
   {
       // Keep owner and neighbour of baffles on same processor
       type    preserveBaffles;
   }

   preserveFaceZones
   {
       // Keep owner and neighbour on same processor for faces in zones
       type    preserveFaceZones;
       zones   (".*");
   }

   preservePatches
   {
       // Keep owner and neighbour on same processor for faces in patches
       type    preservePatches;
       patches (".*");
   }
}
```

### 5. Parallel I/O Considerations (ข้อควรพิจารณณาเกี่ยวกับ I/O ในโหมงานเชิงขนาน)

Parallel I/O presents unique challenges in CFD simulations:

#### I/O Strategies

1. **Collective I/O**: All processors participate in parallel read/write operations
2. **Distributed I/O**: Each processor handles its own data independently
3. **Master-Slave I/O**: Master processor handles all I/O operations

```cpp
// From: processorRunTimes.H:67-75
//- The complete run time
Time completeRunTime_;

//- Processor run times
PtrList<Time> procRunTimes_;

//- Processor zero time that can be used/queried when there is no
//  decomposition. Only allocated when procRunTimes_ is empty.
autoPtr<Time> proc0RunTime_;
```

#### File Organization (การจัดรูปแบบไฟล์)

In parallel runs, files are organized as:
- `processor0/`, `processor1/`, ... `processorN/`: Processor-specific data
- `constant/`: Shared mesh and boundary data
- `time directories/`: Time-dependent data

```bash
# Example parallel directory structure
r410a_evaporator/
├── constant/
│   ├── polyMesh/
│   └── transportProperties
├── system/
│   ├── controlDict
│   ├── decomposeParDict
│   └── fvSolution
└── 0.00001/
    ├── U
    ├── p
    ├── alpha1
    └── T
```

### 6. R410A Evaporator Parallel Simulation Setup (การติดตั้งการจำลองการระเหยของ R410A ในโหมงานเชิงขนาน)

#### Step 1: Prepare the Mesh (เตรียมเมช)

```bash
# Generate the base mesh
blockMesh
snappyHexMesh
checkMesh
```

#### Step 2: Configure Decomposition (ตั้งค่าการแบ่งโดเมน)

Create `system/decomposeParDict`:

```bash
# system/decomposeParDict
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains  8;

method          scotch;

// R410A specific considerations:
// - Maintain phase continuity across processor boundaries
// - Preserve evaporator geometry integrity
scotchCoeffs
{
    strategy "b{sep=m{vert=100,low=h,asc=f}x}";
}

// Optional: Weight field for better load balancing
// weightField alpha1;  // Based on liquid fraction
```

#### Step 3: Decompose the Mesh (แบ่งเมช)

```bash
# Decompose for parallel execution
decomposePar
```

#### Step 4: Run in Parallel (รันในโหมงานเชิงขนาน)

```bash
# Run with 8 processors
mpirun -np 8 r410aEvaporator -parallel

# Or use OpenFOAM's parallel run scripts
simpleFoam -parallel
```

#### Step 5: Reconstruct Results (รวมผลลัพธ์)

```bash
# Reconstruct parallel results
reconstructPar
```

#### Step 6: Post-Processing (ประมวลผลหลังการจำลอง)

```python
# Example: Python script for parallel post-processing
import numpy as np
import matplotlib.pyplot as plt

def analyze_parallel_results():
    # Read data from all processors
    processor_dirs = ['processor{}'.format(i) for i in range(8)]

    # Analyze phase distribution
    for proc_dir in processor_dirs:
        alpha1_data = read_field('{}/0.00001/alpha1'.format(proc_dir))
        analyze_evaporation_rate(alpha1_data)

    # Global analysis
    plot_global_heat_transfer_coefficient()

    # Load balancing check
    check_load_balance(processor_dirs)
```

### Best Practices for Parallel R410A Simulation

#### Load Balancing (จัดโหลด)

```cpp
// Optimize decomposition for two-phase flow
decompositionMethod::decompose
(
    mesh,
    cellWeights,  // Based on liquid/vapor distribution
    blockedFace,  // Preserve baffles and walls
    specifiedProcessorFaces,
    specifiedProcessor,
    explicitConnections
);
```

#### Communication Optimization (เพิ่มประสิทธิภาพการสื่อสาร)

1. **Minimize Processor Boundaries**: Use appropriate decomposition methods
2. **Batch Communication**: Group small messages together
3. **Non-blocking Operations**: Overlap computation and communication

#### Memory Management (การจัดการหน่วยความจำ)

```cpp
// Use parallel-aware containers
PtrList<volScalarField> procFields;
autoPtr<processorRunTimes> runTimes;
```

### Common Issues and Solutions

#### Load Imbalance (ปัญหาการจัดโหลดไม่สมดุล)

**Symptom**: Some processors finish much earlier than others
**Solution**: Use weight-based decomposition or adjust decomposition method

#### Communication Overhead (ปัญหาการสื่อสารที่สูง)

**Symptom**: Performance scales poorly with processor count
**Solution**: Minimize processor boundaries, use hierarchical decomposition

#### Memory Errors (ข้อผิดพลาดด้านหน่วยความจำ)

**Symptom**: Out of memory errors in parallel
**Solution**: Reduce subdomain size, increase memory per processor

### Performance Optimization Techniques

```cpp
// Enable collective communication
UPstream::commsTypes = commsTypes::scheduled;

// Optimize MPI communication
MPI_Barrier(MPI_COMM_WORLD);
MPI_Allreduce(&sendBuffer, &recvBuffer, count, MPI_DOUBLE, MPI_SUM, 0);
```

## Conclusion (สรุป)

Parallel computing in OpenFOAM enables the simulation of complex R410A evaporator problems that would be infeasible on single processor systems. Understanding domain decomposition, processor boundaries, and communication patterns is essential for efficient parallel execution.

⭐ **Key Takeaway**: Proper decomposition configuration, load balancing, and communication optimization are critical for achieving good parallel performance in two-phase flow simulations.

---

**Next Section**: [Advanced Numerical Methods](../11_Advanced_Numerical_Methods/00_Advanced_Numerical_Methods.md)