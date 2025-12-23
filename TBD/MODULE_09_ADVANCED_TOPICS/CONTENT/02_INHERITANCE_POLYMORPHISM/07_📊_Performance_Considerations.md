# 07_📊 พิจารณาด้านประสิทธิภาพ

## รูปแบบการเข้าถึงหน่วยความจำและประสิทธิภาพแคช

ประสิทธิภาพของ OpenFOAM ขึ้นอยู่กับรูปแบบการเข้าถึงหน่วยความจำและการใช้งาน CPU cache อย่างมาก เมธอดปริมาตรจำกัดทำงานบนโครงสร้างข้อมูลที่ใช้ mesh โดยฟิลด์จะถูกจัดเก็บเป็นอาร์เรย์แบบติดต่อกันในหน่วยความจำที่สอดคล้องกับการจัดลำดับของเซลล์

### เค้าโครงหน่วยความจำแบบติดต่อกัน

ฟิลด์ใน OpenFOAM ใช้เค้าโครงหน่วยความจำที่มีประสิทธิภาพสูง โดยข้อมูลจะถูกจัดเก็บในอาร์เรย์แบบติดต่อกัน:

```cpp
// OpenFOAM field memory layout
template<class Type>
class GeometricField {
    Type* field_;           // Contiguous data array
    label size_;           // Number of elements
    // Metadata stored separately
};

// Cache-friendly iteration
forAll(U, cellI) {
    U[cellI] = U[cellI] + dt*F[cellI];  // Sequential memory access
}
```

เค้าโครงนี้เปิดให้ใช้งาน vectorization และ prefetching ที่เหมาะสมที่สุดโดย CPU รูปแบบการเข้าถึงแบบสุ่ม ซึ่งพบได้บ่อยในการเข้าถึงเซลล์ข้างเคียง ได้รับประโยชน์จากการจัดลำดับโทโพโลยีของ mesh ที่ช่วยลด cache miss

### Structure of Arrays กับ Array of Structures

OpenFOAM ใช้แนวทาง "Structure of Arrays" (SoA) เพื่อ vectorization ที่ดีขึ้น:

```cpp
// Efficient: Structure of Arrays (vectorizable)
class UList {
    scalar* componentX_;   // All x-components contiguous
    scalar* componentY_;   // All y-components contiguous  
    scalar* componentZ_;   // All z-components contiguous
};

// Inefficient: Array of Structures (non-vectorizable)
struct Vector3D {
    scalar x, y, z;
};
Vector3D* vectors;  // Interleaved components
```

เค้าโครง SoA ช่วยให้สามารถทำงาน SIMD บนอาร์เรย์คอมโพเนนต์ทั้งหมดได้ ซึ่งเป็นสิ่งสำคัญสำหรับการดำเนินการฟิลด์เช่นการคำนวณเกรเดียนต์และผลคูณเมทริกซ์-เวกเตอร์

## ประสิทธิภาพของ Solver เชิงเส้น

### การจัดเก็บเมทริกซ์และรูปแบบความกระจัดกระจาย

OpenFOAM ใช้รูปแบบแถวกระจัดกระจายถ่วงน้ำหนัก (CSR) สำหรับการจัดเก็บเมทริกซ์ ซึ่งได้รับการปรับให้เหมาะสมกับรูปแบบความกระจัดกระจายปกติของ finite volume mesh:

```cpp
// LDU matrix structure (lower-diagonal-upper)
class LduMatrix {
    scalarList diagonal_;      // Main diagonal
    scalarList lower_;         // Lower coefficients
    scalarList upper_;         // Upper coefficients
    labelList lowerAddr_;      // Lower addressing
    labelList upperAddr_;      // Upper addressing
};
```

รูปแบบการจัดเก็บนี้ให้การใช้หน่วยความจำ $O(n)$ โดยที่ $n$ คือจำนวนเซลล์ พร้อมกับการคูณเมทริกซ์-เวกเตอร์ที่มีประสิทธิภาพ:
$$\mathbf{Ax} = \mathbf{Dx} + \mathbf{Lx}_{lower} + \mathbf{Ux}_{upper}$$

การเชื่อมต่อของ mesh แบบปกติช่วยให้แน่ใจได้ว่ามี bandwidth และ fill-in ที่เหมาะสมที่สุดในระหว่างการดำเนินการเมทริกซ์กระจัดกระจาย

### การเลือก Solver และ Preconditioning

Solver ต่างๆ มีคุณสมบัติด้านประสิทธิภาพที่แตกต่างกัน:

```cpp
// Diagonal solver (fast but limited convergence)
DiagonalSolver<fvScalarMatrix> UEqn_solver(UEqn);

// GAMG solver (multigrid, optimal for large systems)
GAMGSolver<fvScalarMatrix> pEqn_solver(pEqn);

// PCG solver with incomplete Cholesky preconditioning
PCG solver(pEqn, dict);
solver.preconditioner = new DICPreconditioner(pEqn);
```

การเลือก solver ขึ้นอยู่กับคุณสมบัติของเมทริกซ์:
- **Diagonal**: ความซับซ้อน $O(n)$ เหมาะสำหรับระบบที่มีเงื่อนไขดีและมี diagonal เด่น
- **GAMG**: ความซับซ้อน $O(n \log n)$ เหมาะที่สุดสำหรับสมการประเภท Poisson
- **PCG/PBiCG**: ความซับซ้อน $O(n^{1.5})$ ต้องการ preconditioning ที่มีประสิทธิภาพ

### พิจารณาด้านการขยายสเกลแบบขนาน

OpenFOAM ใช้การแบ่งโดเมนสำหรับการดำเนินการแบบขนาน:

```cpp
// Decomposition strategy impact on performance
decomposeParDict {
    method          scotch;     // Graph partitioning
    numberOfSubdomains  8;     // Number of processes
    simpleCoeffs {
        n           (2 2 2);   // 2×2×2 block decomposition
    }
}
```

การทำ load balancing ส่งผลต่อทั้งประสิทธิภาพ solver และ scalability โดยรวม เมธอดที่ใช้กราฟ (Scotch, Metis) ช่วยลดพื้นที่ระหว่าง subdomains ซึ่งช่วยลด overhead ในการสื่อสาร:
$$T_{parallel} = T_{compute} + T_{communicate} = \frac{T_{serial}}{p} + \alpha \log p + \beta \frac{N_{interface}}{p}$$

โดยที่ $p$ คือจำนวนโปรเซสเซอร์ $\alpha$ คือค่า latency และ $\beta$ ค่าต้นทุนของ bandwidth ต่อเซลล์ interface

## การปรับแต่ง Compiler และ Template Metaprogramming

### Expression Templates

OpenFOAM ใช้ expression templates เพื่อกำจัดวัตถุชั่วคราวในการดำเนินการฟิลด์:

```cpp
// Without expression templates (inefficient)
volVectorField U = U_old + dt*f;  // Creates temporary
volVectorField U_new = U + dt*grad(p);  // Another temporary

// With expression templates (efficient)
volVectorField U = U_old + dt*f + dt*grad(p);  // No temporaries
```

กลไกของ expression template สร้าง computation trees ในระหว่างการคอมไพล์ ซึ่งเปิดให้:
- **Loop fusion**: การรวมการดำเนินการหลายอย่างเป็นลูปเดียว
- **Temporary elimination**: ผลลัพธ์ระหว่างการคำนวณถูกคำนวณแบบ in-place
- **Compiler optimization**: การจัดสรร register และการจัดตารางคำสั่งที่ดีขึ้น

### Template Specialization

OpenFOAM ใช้ template specialization เพื่อประสิทธิภาพที่เหมาะสมที่สุด:

```cpp
// General template
template<class Type>
class Field {
    // Generic implementation
};

// Specialization for common scalar operations
template<>
class Field<scalar> {
    // Optimized scalar operations using BLAS
};

// Specialization for vector operations  
template<>
class Field<vector> {
    // Optimized vector operations using SIMD
};
```

แนวทางนี้ช่วยให้สามารถใช้ไลบรารีเฉพาะทาง (BLAS, LAPACK) สำหรับชนิดข้อมูลทั่วไปในขณะที่ยังคงอินเทอร์เฟซแบบ generic

### Inlining และการเพิ่มประสิทธิภาพการเรียกใช้ฟังก์ชัน

ฟังก์ชันสำคัญถูกกำหนดให้เป็น inline เพื่อกำจัด overhead ของการเรียกใช้ฟังก์ชัน:

```cpp
// Critical inline operations
inline scalar dot(const vector& a, const vector& b) {
    return a.x()*b.x() + a.y()*b.y() + a.z()*b.z();
}

// Template-based inline operations
template<class Type>
inline Type operator+(const UList<Type>& a, const UList<Type>& b) {
    Type result;
    forAll(a, i) {
        result[i] = a[i] + b[i];  // Inlined, no function call
    }
    return result;
}
```

คอมไพเลอร์สามารถเพิ่มประสิทธิภาพฟังก์ชัน inline เหล่านี้ผ่านการจัดสรร register การจัดลำดับคำสั่งใหม่ และ vectorization

## ประสิทธิภาพ I/O และการจัดการข้อมูล

### รูปแบบการจัดเก็บฟิลด์

OpenFOAM รองรับหลายรูปแบบการจัดเก็บฟิลด์ที่มีคุณสมบัติด้านประสิทธิภาพที่แตกต่างกัน:

```cpp
// Binary format (fast I/O, small files)
FoamFile {
    format      binary;
    class       volScalarField;
    object      p;
}

// ASCII format (portable, larger files)  
FoamFile {
    format      ascii;
    class       volScalarField;
    object      p;
}
```

รูปแบบไบนารีให้ความเร็ว I/O ที่เร็วกว่า 3-4 เท่าพร้อมขนาดไฟล์ที่เล็กลง 50-70% อย่างไรก็ตาม รูปแบบ ASCII ให้ความเข้ากันได้ระหว่างแพลตฟอร์มที่ดีขึ้นและการอ่านได้โดยมนุษย์

### การปรับแต่ง I/O แบบขนาน

สำหรับการจำลองแบบขนานขนาดใหญ่ OpenFOAM ใช้กลยุทธ์ I/O ที่ได้รับการปรับให้เหมาะสม:

```cpp
// Master process I/O (reduces file system contention)
if (Pstream::master()) {
    p.write();  // Only master writes to disk
}
Pstream::scatter(p, Pstream::blocking);  // Broadcast to all processes

// Distributed I/O (for very large datasets)
if (Pstream::parRun()) {
    p.writeOpt(IOstream::BINARY, IOstream::COMPRESSED);
}
```

ประสิทธิภาพ I/O ขยายสัดส่วนเป็น:
$$T_{I/O}^{serial} \propto N$$
$$T_{I/O}^{parallel} \propto \frac{N}{p} + \alpha \log p$$

โดยที่ $N$ คือขนาดข้อมูลและ $p$ คือจำนวนโปรเซสที่เขียนข้อมูล

### การจัดการหน่วยความจำและพื้นที่เก็บข้อมูลชั่วคราว

OpenFOAM ใช้ smart pointers ที่นับจำนวนการอ้างอิงเพื่อปรับให้เหมาะสมกับการใช้หน่วยความจำ:

```cpp
// tmp class for automatic memory management
tmp<volScalarField> tphi = flux(U);  // Creates temporary field
phi = tphi();  // Extracts reference, automatic cleanup

// AutoPtr for owned objects  
autoPtr<surfaceScalarField> phiPtr(new surfaceScalarField(mesh));
// Automatic deletion when phiPtr goes out of scope
```

แนวทางนี้ช่วยลดการจัดสรรหน่วยความจำและป้องกันการรั่วไหลของหน่วยความจำในขณะที่ยังคงประสิทธิภาพผ่าน move semantics และการแชร์การอ้างอิง

## ความซับซ้อนของอัลกอริทึมและวิธีการเชิงตัวเลข

### ความซับซ้อนของการผสานรวมตามเวลา

รูปแบบการผสานรวมตามเวลาที่แตกต่างกันให้ต้นทุนการคำนวณที่แตกต่างกัน:

```cpp
// Explicit Euler: O(n) per timestep
U = U + dt*f(U);  // Single evaluation

// Implicit Euler: O(n^1.5) per timestep (linear solve)
solve(fvm::ddt(U) == f(U));  // Matrix solve required

// Runge-Kutta 4: O(4n) per timestep
k1 = f(U);
k2 = f(U + 0.5*dt*k1);  
k3 = f(U + 0.5*dt*k2);
k4 = f(U + dt*k3);
U = U + dt/6.0*(k1 + 2*k2 + 2*k3 + k4);  // Four evaluations
```

การเลือกวิธีการขึ้นอยู่กับ stiffness และความต้องการความแม่นยำ:
- **Explicit methods**: ต้นทุนต่ำต่อขั้นตอน ความเสถียรจำกัดโดยเงื่อนไข CFL
- **Implicit methods**: ต้นทุนสูงต่อขั้นตอน ความเสถียรแบบไม่มีเงื่อนไข
- **Adaptive methods**: ช่วงเวลาแปรผันตามการประเมินข้อผิดพลาด

### รูปแบบการ Discretization เชิงพื้นที่

รูปแบบการ discretization ที่แตกต่างกันมีความซับซ้อนในการคำนวณที่แตกต่างกัน:

```cpp
// First-order upwind: O(n) complexity
gradScheme = Gauss linear;  // Second-order accurate

// Second-order central differencing: O(n) complexity  
gradScheme = Gauss upwind;  // First-order, more stable

// High-resolution schemes: O(n log n) complexity
gradScheme = Gauss limitedLinearV 1;  // TVD scheme with limiting
```

รูปแบบระดับสูงให้ความแม่นยำที่ดีขึ้นแต่มีต้นทุนการคำนวณที่เพิ่มขึ้นและอาจเกิดปัญหาความเสถียร

### เทคนิคการเร่งการลู่เข้า

OpenFOAM ใช้วิธีการเร่งการลู่เข้าหลายวิธี:

```cpp
// Residual smoothing for faster convergence
solver {
    smoother      GaussSeidel;
    nSweeps      2;
    tolerance    1e-6;
    relTol       0.01;
}

// Multigrid acceleration
solver {
    smoother     GaussSeidel;
    preSweeps    2;
    postSweeps   2;
    nFinestSweeps 2;
    cacheAgglomeration true;
    agglomerator faceAreaPair;
    mergeLevels 1;
}
```

วิธีการ multigrid บรรลุความซับซ้อนที่เหมาะสมที่สุด $O(n)$ สำหรับปัญหาประเภท elliptic โดยการแยกส่วนประกอบของข้อผิดพลาดผ่านหลายระดับของเกรด
