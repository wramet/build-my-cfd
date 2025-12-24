# 07 การพิจารณาด้านประสิทธิภาพ (Performance Considerations)

## บทนท

ความยืดหยุ่นทางสถาปัตยกรรมของ OpenFOAM ผ่าน inheritance และ polymorphism มาพร้อมกับค่าใช้จ่ายด้านประสิทธิภาพที่ต้องเข้าใจ หมวดนี้วิเคราะห์ผลกระทบด้านประสิทธิภาพของ virtual function calls, ระบบ RTS, และรูปแบบการออกแบบต่างๆ ที่ใช้ใน OpenFOAM พร้อมกับกลยุทธ์ในการปรับแต่งให้เหมาะสม

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/MovingPhaseModel/MovingPhaseModel.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงโครงสร้างพื้นฐานของ GeometricField ซึ่งเป็นคลาสหลักที่ใช้จัดเก็บข้อมูลฟิลด์ใน OpenFOAM การจัดเก็บข้อมูลแบบติดต่อกัน (contiguous array) ช่วยให้ CPU สามารถดึงข้อมูลจากหน่วยความจำได้อย่างมีประสิทธิภาพ
- **Explanation (คำอธิบาย):** เค้าโครงหน่วยความจำแบบติดต่อกันเป็นพื้นฐานสำคัญของประสิทธิภาพใน OpenFOAM เมื่อข้อมูลถูกจัดเก็บเรียงต่อกัน CPU สามารถ prefetch ข้อมูลล่วงหน้าและใช้ SIMD instructions ได้อย่างเต็มประสิทธิภาพ รูปแบบการเข้าถึงแบบสุ่มจะได้รับประโยชน์จากการจัดลำดับโทโพโลยีของ mesh
- **Key Concepts (แนวคิดสำคัญ):**
  - **Contiguous Memory Layout:** การจัดเก็บข้อมูลแบบติดต่อกันเปิดให้ใช้งาน vectorization และ prefetching ที่เหมาะสมที่สุด
  - **Cache-Friendly Access:** การเข้าถึงข้อมูลแบบต่อเนื่องช่วยลด cache miss และเพิ่มประสิทธิภาพ
  - **Sequential Access:** รูปแบบการเข้าถึงแบบเรียงลำดับเป็นที่ต้องการสำหรับประสิทธิภาพสูงสุด

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงความแตกต่างระหว่าง Structure of Arrays (SoA) และ Array of Structures (AoS) ซึ่งเป็นรูปแบบการจัดเก็บข้อมูลที่สำคัญใน OpenFOAM รูปแบบ SoA ถูกนำมาใช้อย่างแพร่หลายเนื่องจากเหมาะสมกับการประมวลผลแบบ vector
- **Explanation (คำอธิบาย):** เค้าโครง SoA แยกคอมโพเนนต์ของเวกเตอร์ออกจากกัน ทำให้สามารถใช้ SIMD instructions กับทุกคอมโพเนนต์ได้พร้อมกัน ในขณะที่ AoS จะเก็บคอมโพเนนต์แบบ interleaved ซึ่งไม่เหมาะสมกับ vectorization นี่เป็นเหตุผลที่ OpenFOAM เลือกใช้ SoA สำหรับการจัดเก็บข้อมูลเวกเตอร์
- **Key Concepts (แนวคิดสำคัญ):**
  - **Structure of Arrays (SoA):** รูปแบบที่เหมาะสมกับ SIMD และ vectorization
  - **Vectorization:** การดำเนินการ SIMD บนอาร์เรย์คอมโพเนนต์ทั้งหมด
  - **Memory Access Pattern:** รูปแบบการเข้าถึงหน่วยความจำที่ส่งผลต่อประสิทธิภาพ

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงโครงสร้าง LduMatrix ซึ่งเป็นรูปแบบการจัดเก็บเมทริกซ์กระจัดกระจายหลักใน OpenFOAM โครงสร้างนี้ถูกออกแบบมาเพื่อใช้หน่วยความจำอย่างมีประสิทธิภาพสำหรับระบบสมการเชิงเส้นที่เกิดจากการ discretization ของ finite volume method
- **Explanation (คำอธิบาย):** รูปแบบ LDU (Lower-Diagonal-Upper) เป็น specialized form ของ Compressed Sparse Row (CSR) format ที่เหมาะสมกับโครงสร้าง mesh แบบ finite volume โดยเฉพาะ เมทริกซ์มีความกระจัดกระจายสูงแต่มี pattern ที่ชัดเจน ทำให้สามารถจัดเก็บเฉพาะส่วนที่ไม่เป็นศูนย์ได้อย่างมีประสิทธิภาพ
- **Key Concepts (แนวคิดสำคัญ):**
  - **Sparse Matrix Storage:** การจัดเก็บเมทริกซ์กระจัดกระจายที่มีประสิทธิภาพ
  - **LDU Decomposition:** การแยกเมทริกซ์เป็นส่วน lower, diagonal, และ upper
  - **Memory Efficiency:** การใช้หน่วยความจำ O(n) สำหรับ mesh ที่มี n cells

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystemSolve.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงตัวอย่างการใช้งาน solver ต่างๆ ใน OpenFOAM โดยแต่ละ solver มีคุณสมบัติและประสิทธิภาพที่แตกต่างกันขึ้นอยู่กับประเภทของปัญหาและขนาดของระบบสมการ
- **Explanation (คำอธิบาย):** การเลือก solver ที่เหมาะสมเป็นสิ่งสำคัญสำหรับประสิทธิภาพโดยรวม Diagonal solver มีความเร็วสูงแต่มีข้อจำกัดในการลู่เข้า GAMG (Geometric-Algebraic Multigrid) เหมาะสำหรับระบบขนาดใหญ่ และ PCG (Preconditioned Conjugate Gradient) มีความยืดหยุ่นสูงแต่ต้องการ preconditioning ที่เหมาะสม
- **Key Concepts (แนวคิดสำคัญ):**
  - **Solver Selection:** การเลือก solver ที่เหมาะสมกับประเภทปัญหา
  - **Preconditioning:** เทคนิคในการปรับปรุงความเร็วในการลู่เข้า
  - **Complexity Analysis:** การวิเคราะห์ความซับซ้อนของแต่ละ solver

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงการตั้งค่าการแบ่งโดเมน (domain decomposition) สำหรับการคำนวณแบบขนานใน OpenFOAM การแบ่งโดเมนที่ดีช่วยให้แต่ละโปรเซสเซอร์ทำงานได้อย่างสมดุลและลด overhead ในการสื่อสารระหว่างโปรเซสเซอร์
- **Explanation (คำอธิบาย):** การทำ load balancing ส่งผลต่อทั้งประสิทธิภาพ solver และ scalability โดยรวม เมธอดที่ใช้กราฟ (Scotch, Metis) ช่วยลดพื้นที่ระหว่าง subdomains ซึ่งช่วยลด overhead ในการสื่อสาร
- **Key Concepts (แนวคิดสำคัญ):**
  - **Domain Decomposition:** การแบ่งโดเมนสำหรับการคำนวณแบบขนาน
  - **Graph Partitioning:** การใช้กราฟในการแบ่งโดเมนอย่างมีประสิทธิภาพ
  - **Load Balancing:** การกระจายงานอย่างสมดุลระหว่างโปรเซสเซอร์
  - **Communication Overhead:** ต้นทุนในการสื่อสารระหว่างโปรเซสเซอร์

การทำ load balancing ส่งผลต่อทั้งประสิทธิภาพ solver และ scalability โดยรวม เมธอดที่ใช้กราฟ (Scotch, Metis) ช่วยลดพื้นที่ระหว่าง subdomains ซึ่งช่วยลด overhead ในการสื่อสาร:
$$T_{parallel} = T_{compute} + T_{communicate} = \frac{T_{serial}}{p} + \alpha \log p + \beta \frac{N_{interface}}{p}$$

โดยที่ $p$ คือจำนวนโปรเซสเซอร์ $\alpha$ คือค่า latency และ $\beta$ ค่าต้นทุนของ bandwidth ต่อเซลล์ interface

## Virtual Function Call Overhead

### ต้นทุนของ Virtual Dispatch

การเรียก virtual function มีต้นทุนด้านประสิทธิภาพที่ต้องคำนึงถึง:

```cpp
// Virtual call mechanism
struct dragModel_vtable {
    void (*destructor)(dragModel*);
    tmp<surfaceScalarField> (*K)(const dragModel*);
};

class dragModel {
    dragModel_vtable* __vptr;  // Hidden vtable pointer
public:
    virtual ~dragModel() = 0;
    virtual tmp<surfaceScalarField> K() const = 0;
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงกลไกภายในของ virtual function calls ใน C++ ซึ่งเป็นพื้นฐานของระบบ polymorphism ใน OpenFOAM dragModel เป็นตัวอย่างที่ชัดเจนของการใช้ virtual functions เพื่อรองรับรูปแบบการคำนวณ drag ที่หลากหลาย
- **Explanation (คำอธิบาย):** Virtual function calls มีต้นทุนเล็กน้อยจากการทำ indirect jump ผ่าน vtable pointer และไม่สามารถถูก inlined ได้ใน compile time อย่างไรก็ตาม ใน OpenFOAM ต้นทุนนี้ถูกลดทอนโดยการใช้ virtual calls ในระดับ field ไม่ใช่ระดับเซลล์
- **Key Concepts (แนวคิดสำคัญ):**
  - **Virtual Table (vtable):** ตารางฟังก์ชันที่ใช้ในการ dispatch
  - **Indirect Call:** การเรียกฟังก์ชันผ่าน pointer
  - **Inlining Inhibition:** การที่ virtual calls ไม่สามารถถูก inlined ได้
  - **Branch Prediction:** ความสามารถของ CPU ในการทำนาย virtual targets

**การวิเคราะห์ต้นทุน**:
- **Indirect Jump**: ~5 CPU cycles สำหรับ pointer dereference และ jump
- **Inhibition of Inlining**: Virtual calls ไม่สามารถ inlined ได้ใน compile time
- **Cache Behavior**: Vtable pointers เล็กและ cache-friendly โดยทั่วไป
- **Branch Prediction**: Modern CPUs ทำนาย virtual targets ได้ดี

**การวัดประสิทธิภาพ**:
```cpp
// Direct call (inlinable)
inline scalar directDrag(scalar Re) {
    return 24.0/Re * (1.0 + 0.15*pow(Re, 0.687));
}
// เวลา: ~2-3 CPU cycles หลังจาก inlining

// Virtual call (not inlinable)
virtual scalar virtualDrag(scalar Re) const = 0;
// เวลา: ~8-10 CPU cycles (รวม vtable lookup + indirect jump)
```

**📂 Source:** `.applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** ตัวอย่างนี้แสดงความแตกต่างในด้านประสิทธิภาพระหว่าง direct calls และ virtual calls ซึ่งเป็นสิ่งสำคัญในการทำความเข้าใจผลกระทบของ polymorphism ต่อประสิทธิภาพ
- **Explanation (คำอธิบาย):** Direct calls สามารถถูก inlined ได้ใน compile time ทำให้มีประสิทธิภาพสูงกว่ามาก ในขณะที่ virtual calls มีต้นทุนเพิ่มเติมจากการทำ indirect jump ความแตกต่างนี้เป็นเหตุผลที่ OpenFOAM พยายามใช้ virtual calls ในระดับที่สูงกว่า
- **Key Concepts (แนวคิดสำคัญ):**
  - **Inlining:** การแทนที่ฟังก์ชันด้วยโค้ดโดยตรง
  - **CPU Cycles:** หน่วยวัดประสิทธิภาพในระดับต่ำ
  - **Performance Trade-off:** การแลกเปลี่ยนระหว่างประสิทธิภาพและความยืดหยุ่น

### การย่อยระดับการเรียกใช้ (Call Granularity)

กลยุทธ์หลักในการลดผลกระทบของ virtual call overhead คือการเพิ่มระดับการเรียกใช้:

```cpp
// แย่: Virtual calls ในลูปชั้นใน
forAll(cells, i) {
    dragCoeff[i] = dragModel.K(cells[i]);  // Virtual call per cell
}
// 1,000,000 virtual calls สำหรับ mesh 1M cells

// ดี: Virtual call นอกลูป การคำนวณภายในเวกเตอร์
tmp<volScalarField> dragCoeffField = dragModel.K();  // 1 virtual call
// การคำนวณภายใน field operations (vectorized)
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงกลยุทธ์ที่สำคัญใน OpenFOAM ในการลดผลกระทบของ virtual call overhead โดยการกระจุกตัวการคำนวณให้มีขนาดใหญ่และทำ virtual calls นอกลูป
- **Explanation (คำอธิบาย):** OpenFOAM ใช้กลยุทธีการกระจุกตัวการคำนวณ (batch processing) อย่างกว้างขวางเพื่อลดจำนวน virtual calls โดยการดำเนินการกับทั้งฟิลด์พร้อมกันแทนที่จะทำทีละเซลล์ ช่วยลด overhead อย่างมาก
- **Key Concepts (แนวคิดสำคัญ):**
  - **Call Granularity:** ระดับของการเรียกฟังก์ชัน
  - **Batch Processing:** การประมวลผลแบบเป็นกลุ่ม
  - **Vectorization:** การดำเนินการแบบ vector ที่มีประสิทธิภาพ
  - **Field-Level Operations:** การดำเนินการในระดับฟิลด์

OpenFOAM ใช้กลยุทธ์นี้อย่างกว้างขวาง:
- **Field-Level Operations**: Virtual calls สำหรับทั้งฟิลด์ ไม่ใช่ต่อเซลล์
- **Expression Templates**: การดำเนินการฟิลด์ถูก fused และ vectorized
- **Batch Processing**: การคำนวณถูกกระจุกตัวในระดับเมทริกซ์

### Template vs. Virtual Trade-offs

OpenFOAM ใช้ hybrid approach:

```cpp
// Template สำหรับประสิทธิภาพสูง (compile-time polymorphism)
template<class Type>
class Field {
    inline Type& operator[](label i) { return data_[i]; }  // Inlinable
};

// Virtual functions สำหรับความยืดหยุ่น (runtime polymorphism)
class dragModel {
public:
    virtual tmp<volScalarField> K() const = 0;  // Runtime selection
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงแนวทาง hybrid ของ OpenFOAM ที่ใช้ทั้ง templates และ virtual functions เพื่อให้ได้ทั้งประสิทธิภาพและความยืดหยุ่น Field classes ใช้ templates สำหรับประสิทธิภาพสูง ในขณะที่ model classes ใช้ virtual functions สำหรับ runtime selection
- **Explanation (คำอธิบาย):** OpenFOAM ใช้ templates สำหรับ operations ที่ต้องการประสิทธิภาพสูงและรู้จักใน compile time และใช้ virtual functions สำหรับ models ที่ต้องการ runtime flexibility การผสมผสานนี้ช่วยให้ได้ประโยชน์จากทั้งสองแนวทาง
- **Key Concepts (แนวคิดสำคัญ):**
  - **Compile-Time Polymorphism:** การใช้ templates สำหรับประสิทธิภาพ
  - **Runtime Polymorphism:** การใช้ virtual functions สำหรับความยืดหยุ่น
  - **Hybrid Approach:** การผสมผสานทั้งสองแนวทาง
  - **Performance vs. Flexibility:** การแลกเปลี่ยนระหว่างประสิทธิภาพและความยืดหยุ่น

**ข้อดีและข้อเสีย**:

| Approach | Performance | Flexibility | Binary Size | Compilation Time |
|----------|-------------|-------------|-------------|------------------|
| Templates | ★★★★★ (inlinable) | ★★☆☆☆ (compile-time) | ★★☆☆☆ (code bloat) | ★★☆☆☆ (slow) |
| Virtual | ★★★☆☆ (indirect) | ★★★★★ (runtime) | ★★★★★ (compact) | ★★★★★ (fast) |

## ประสิทธิภาพของระบบ RTS

### ต้นทุนของ Factory Lookups

ระบบ Run-Time Selection มีต้นทุนเฉพาะในช่วงเริ่มต้น:

```cpp
// Runtime selection overhead (one-time cost)
autoPtr<dragModel> drag = dragModel::New(dict, phase1, phase2);
// 1. Dictionary lookup: O(1) hash table search
// 2. Constructor table lookup: O(1) hash table search
// 3. Dynamic allocation: ~100-1000 cycles (dependent on object size)
// 4. Virtual table setup: ~10 cycles

// Total: ~1100-2100 cycles (ONE-TIME cost during construction)
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงกระบวนการ runtime selection ใน OpenFOAM ซึ่งใช้ hash tables สำหรับการค้นหา models อย่างรวดเร็ว ต้นทุนหลักอยู่ที่การสร้าง objects ครั้งแรก หลังจากนั้นไม่มี overhead เพิ่มเติม
- **Explanation (คำอธิบาย):** ระบบ Run-Time Selection ของ OpenFOAM ถูกออกแบบมาให้มีต้นทุนต่ำในระยะยาว โดยมีต้นทุนหลักเฉพาะในช่วงเริ่มต้นเมื่อสร้าง objects การใช้ hash tables ทำให้การค้นหามีประสิทธิภาพสูง
- **Key Concepts (แนวคิดสำคัญ):**
  - **Runtime Selection:** การเลือก model ใน runtime
  - **Factory Pattern:** รูปแบบการออกแบบสำหรับการสร้าง objects
  - **Hash Table Lookup:** การค้นหาที่มีประสิทธิภาพสูง
  - **One-Time Cost:** ต้นทุนที่เกิดขึ้นครั้งเดียว

**ต้นทุนรายวัน**: หลังจากการสร้าง ไม่มีต้นทุนเพิ่มเติม
```cpp
// No runtime overhead after construction
tmp<volScalarField> K = drag.K();  // Same as direct virtual call
```

### ต้นทุนของ Static Registration

Static initialization มีต้นทุนเล็กน้อยระหว่างการเริ่มต้นโปรแกรม:

```cpp
// Registration during static initialization
namespace {
    phaseModel::dictionaryConstructorTable::entry_proxy
        addpurePhaseModelToRunTimeSelectionTable
        (
            "pure",
            purePhaseModel::New
        );
}
// Cost: ~100-200 cycles per registered model
// Occurs: Once during program startup (before main)
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/MovingPhaseModel/MovingPhaseModel.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงกลไก static registration ที่ใช้ใน OpenFOAM สำหรับลงทะเบียน models กับระบบ runtime selection การลงทะเบียนเกิดขึ้นโดยอัตโนมัติในช่วง static initialization
- **Explanation (คำอธิบาย):** Static registration ใช้ static initialization เพื่อลงทะเบียน models โดยอัตโนมัติก่อนที่โปรแกรมจะเริ่มทำงาน ต้นทุนในการลงทะเบียนแต่ละ model มีน้อย และเกิดขึ้นเพียงครั้งเดียว
- **Key Concepts (แนวคิดสำคัญ):**
  - **Static Registration:** การลงทะเบียนโดยอัตโนมัติในช่วง initialization
  - **Constructor Table:** ตารางที่เก็บ constructors ของ models
  - **Entry Proxy:** กลไกในการลงทะเบียน models
  - **Startup Overhead:** ต้นทุนในช่วงเริ่มต้นโปรแกรม

**สถิติการลงทะเบียน**:
- ปกติ OpenFOAM มี 50-100 models ต่อ solver
- ต้นทุนรวม: ~5,000-20,000 cycles
- การเปรียบเทียบ: เล็กน้อยเมื่อเทียบกับเวลาเริ่มต้นโปรแกรม (~1 วินาที)

### การเพิ่มประสิทธิภาพ Hash Tables

Runtime selection tables ใช้ hash tables สำหรับการค้นหา O(1):

```cpp
// Internal hash table implementation
typedef HashTable<dictionaryConstructorPtr, word> dictionaryConstructorTable;

// Lookup performance
dictionaryConstructorTable::iterator cstrIter =
    dictionaryConstructorTablePtr_->find(modelType);  // O(1) average
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงการใช้ HashTable ของ OpenFOAM สำหรับ runtime selection tables Hash tables ถูกใช้เพื่อให้การค้นหา models มีประสิทธิภาพสูง
- **Explanation (คำอธิบาย):** Runtime selection tables ใช้ hash tables สำหรับการค้นหาที่มีประสิทธิภาพ การใช้ hash functions ที่ดีและ collision resolution ที่เหมาะสมช่วยให้การค้นหามีประสิทธิภาพสูง
- **Key Concepts (แนวคิดสำคัญ):**
  - **Hash Table:** โครงสร้างข้อมูลสำหรับการค้นหาที่รวดเร็ว
  - **O(1) Lookup:** การค้นหาที่มีความซับซ้อนคงที่
  - **Hash Function:** ฟังก์ชันในการแปลงคีย์เป็น index
  - **Collision Resolution:** กลไกในการจัดการ collision

**ปัจจัยด้านประสิทธิภาพ**:
- **Hash Function**: `string::hash()` ที่มีประสิทธิภาพสูง
- **Collision Resolution**: Open addressing ที่มีประสิทธิภาพ
- **Memory Locality**: Compact storage สำหรับ cache efficiency

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

**📂 Source:** `.applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงประโยชน์ของ expression templates ใน OpenFOAM ซึ่งช่วยกำจัดวัตถุชั่วคราวและเพิ่มประสิทธิภาพในการดำเนินการฟิลด์ โดยการสร้าง computation trees ใน compile time
- **Explanation (คำอธิบาย):** Expression templates สร้าง computation trees ในระหว่างการคอมไพล์ ซึ่งเปิดให้มีการรวมการดำเนินการหลายอย่างเป็นลูปเดียวและกำจัดวัตถุชั่วคราว ช่วยเพิ่มประสิทธิภาพอย่างมาก
- **Key Concepts (แนวคิดสำคัญ):**
  - **Expression Templates:** เทคนิค metaprogramming สำหรับการเพิ่มประสิทธิภาพ
  - **Temporary Elimination:** การกำจัดวัตถุชั่วคราว
  - **Loop Fusion:** การรวมลูปหลายอย่างเป็นลูปเดียว
  - **Lazy Evaluation:** การประเมินผลแบบล่าช้า

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงการใช้ template specialization ใน OpenFOAM เพื่อให้มีประสิทธิภาพสูงสุดสำหรับชนิดข้อมูลทั่วไป เช่น scalar และ vector ซึ่งช่วยให้สามารถใช้ไลบรารีเฉพาะทางได้
- **Explanation (คำอธิบาย):** Template specialization ช่วยให้สามารถปรับแต่งการดำเนินการสำหรับชนิดข้อมูลเฉพาะได้ ช่วยให้สามารถใช้ไลบรารีเฉพาะทาง (BLAS, LAPACK) สำหรับชนิดข้อมูลทั่วไปในขณะที่ยังคงอินเทอร์เฟซแบบ generic
- **Key Concepts (แนวคิดสำคัญ):**
  - **Template Specialization:** การปรับแต่ง templates สำหรับชนิดข้อมูลเฉพาะ
  - **BLAS/LAPACK:** ไลบรารีสำหรับการดำเนินการเชิงเส้นที่มีประสิทธิภาพ
  - **SIMD:** การดำเนินการแบบ single instruction, multiple data
  - **Generic Interface:** อินเทอร์เฟซแบบ generic ที่รองรับหลายชนิดข้อมูล

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

**📂 Source:** `.applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงตัวอย่างของ inline functions ใน OpenFOAM ซึ่งช่วยกำจัด overhead ของการเรียกใช้ฟังก์ชันและเพิ่มประสิทธิภาพ โดยเฉพาะสำหรับ operations ที่ถูกเรียกใช้บ่อย
- **Explanation (คำอธิบาย):** การใช้ inline functions ช่วยกำจัด overhead ของการเรียกใช้ฟังก์ชันและเปิดให้มีการเพิ่มประสิทธิภาพเพิ่มเติมจาก compiler ช่วยให้โค้ดมีประสิทธิภาพสูงขึ้นโดยเฉพาะสำหรับ operations ที่ถูกเรียกใช้บ่อย
- **Key Concepts (แนวคิดสำคัญ):**
  - **Inlining:** การแทนที่ฟังก์ชันด้วยโค้ดโดยตรง
  - **Function Call Overhead:** ต้นทุนในการเรียกใช้ฟังก์ชัน
  - **Compiler Optimization:** การเพิ่มประสิทธิภาพโดย compiler
  - **Register Allocation:** การจัดสรร registers ที่มีประสิทธิภาพ

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystemSolve.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงการตั้งค่ารูปแบบไฟล์ใน OpenFOAM ซึ่งส่งผลต่อประสิทธิภาพ I/O และขนาดไฟล์ รูปแบบไบนารีมีประสิทธิภาพสูงกว่าแต่ไม่สามารถอ่านได้โดยมนุษย์
- **Explanation (คำอธิบาย):** รูปแบบไบนารีให้ความเร็ว I/O ที่เร็วกว่าและขนาดไฟล์ที่เล็กกว่า ในขณะที่รูปแบบ ASCII ให้ความเข้ากันได้ระหว่างแพลตฟอร์มที่ดีขึ้นและสามารถอ่านได้โดยมนุษย์
- **Key Concepts (แนวคิดสำคัญ):**
  - **Binary Format:** รูปแบบไบนารีที่มีประสิทธิภาพสูง
  - **ASCII Format:** รูปแบบข้อความที่อ่านได้โดยมนุษย์
  - **I/O Performance:** ประสิทธิภาพในการอ่านและเขียนข้อมูล
  - **File Size:** ขนาดไฟล์

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงกลยุทธ์ I/O แบบขนานใน OpenFOAM ซึ่งช่วยลดการแย่งชิงระบบไฟล์และเพิ่มประสิทธิภาพในการจำลองแบบขนานขนาดใหญ่
- **Explanation (คำอธิบาย):** ในการจำลองแบบขนาน OpenFOAM ใช้กลยุทธ์ I/O ที่ได้รับการปรับให้เหมาะสมเพื่อลดการแย่งชิงระบบไฟล์และเพิ่มประสิทธิภาพ โดยปกติจะให้ master process เป็นผู้เขียนข้อมูลเท่านั้น
- **Key Concepts (แนวคิดสำคัญ):**
  - **Master Process I/O:** การให้ master process เป็นผู้เขียนข้อมูล
  - **File System Contention:** การแย่งชิงระบบไฟล์
  - **Distributed I/O:** การกระจายการเขียนข้อมูล
  - **Parallel I/O:** การดำเนินการ I/O แบบขนาน

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงการใช้ smart pointers ใน OpenFOAM ซึ่งช่วยจัดการหน่วยความจำอย่างอัตโนมัติและป้องกันการรั่วไหลของหน่วยความจำ
- **Explanation (คำอธิบาย):** OpenFOAM ใช้ smart pointers ที่นับจำนวนการอ้างอิงเพื่อปรับให้เหมาะสมกับการใช้หน่วยความจำ ช่วยลดการจัดสรรหน่วยความจำและป้องกันการรั่วไหลของหน่วยความจำในขณะที่ยังคงประสิทธิภาพ
- **Key Concepts (แนวคิดสำคัญ):**
  - **Smart Pointers:** ตัวชี้อัจฉริยะที่จัดการหน่วยความจำอัตโนมัติ
  - **Reference Counting:** การนับจำนวนการอ้างอิง
  - **Automatic Cleanup:** การลบข้อมูลอัตโนมัติ
  - **Memory Management:** การจัดการหน่วยความจำ

แนวทางนี้ช่วยลดการจัดสรรหน่วยความจำและป้องกันการรั่วไหลของหน่วยความจำในขณะที่ยังคงประสิทธิภาพผ่าน move semantics และการแชร์การอ้างอิง

## กลยุทธ์การเพิ่มประสิทธิภาพ

### การใช้งาน Smart Pointers อย่างมีประสิทธิภาพ

Smart pointers ของ OpenFOAM มีคุณสมบัติด้านประสิทธิภาพที่แตกต่างกัน:

```cpp
// autoPtr: Move-only, no reference counting overhead
autoPtr<phaseModel> phase = phaseModel::New(dict, mesh);
// Cost: Zero overhead (compile-time move semantics)

// tmp: Reference-counted, copy-on-write semantics
tmp<volScalarField> field = phase.rho();
// Cost: Atomic increment/decrement (~20-50 cycles per copy)
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงความแตกต่างระหว่าง autoPtr และ tmp ซึ่งเป็น smart pointers ที่ใช้ใน OpenFOAM โดยมีคุณสมบัติและประสิทธิภาพที่แตกต่างกัน
- **Explanation (คำอธิบาย):** autoPtr มีประสิทธิภาพสูงกว่าเนื่องจากไม่มี reference counting overhead ในขณะที่ tmp มีต้นทุนเล็กน้อยจากการนับจำนวนการอ้างอิง แต่มีความยืดหยุ่นสูงกว่า
- **Key Concepts (แนวคิดสำคัญ):**
  - **autoPtr:** Smart pointer ที่ไม่มี reference counting overhead
  - **tmp:** Smart pointer ที่มี reference counting
  - **Move Semantics:** การย้ายความเป็นเจ้าของ
  - **Copy-on-Write:** การเขียนเมื่อมีการคัดลอก

**แนวทางการใช้งาน**:
- ใช้ `autoPtr` สำหรับ exclusive ownership ของ large objects
- ใช้ `tmp` สำหรับ field results ที่อาจถูกนำกลับมาใช้ใหม่
- หลีกเลี่ยงการ copy `tmp` ที่ไม่จำเป็น

### การลด Object Slicing

Object slicing เป็นข้อผิดพลาดที่ทำให้เกิด polymorphic behavior ที่ไม่ถูกต้อง:

```cpp
// ผิด: Object slicing เกิดขึ้น
void processPhase(phaseModel phase) {  // Pass by value
    phase.correct();  // เรียกเฉพาะ phaseModel::correct()
}

// ถูกต้อง: ใช้ reference หรือ pointer
void processPhase(const phaseModel& phase) {  // Reference
    phase.correct();  // Virtual dispatch ทำงานถูกต้อง
}
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/MovingPhaseModel/MovingPhaseModel.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงปัญหา object slicing ซึ่งเป็นข้อผิดพลาดที่พบบ่อยในการใช้ polymorphism ใน C++ และวิธีการแก้ไข
- **Explanation (คำอธิบาย):** Object slicing เกิดขึ้นเมื่อส่ง objects ของ derived classes โดยค่าไปยังฟังก์ชันที่รับ objects ของ base classes ทำให้ส่วนที่เพิ่มเติมของ derived classes ถูกตัดทิ้งไป
- **Key Concepts (แนวคิดสำคัญ):**
  - **Object Slicing:** การตัดส่วนเพิ่มเติมของ derived classes
  - **Polymorphic Behavior:** พฤติกรรม polymorphic ที่ถูกต้อง
  - **Reference Passing:** การส่งค่าแบบ reference
  - **Virtual Dispatch:** การ dispatch แบบ virtual

### Virtual Destructors

Virtual destructors จำเป็นสำหรับการ cleanup ที่เหมาะสม:

```cpp
// ผิด: Memory leak กับ derived classes
class dragModel {
public:
    ~dragModel() {}  // Non-virtual
};

// ถูกต้อง: Virtual destructor
class dragModel {
public:
    virtual ~dragModel() = default;  // Virtual
};
```

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงความสำคัญของ virtual destructors ในการทำ cleanup ที่เหมาะสมสำหรับ polymorphic classes ใน C++
- **Explanation (คำอธิบาย):** Virtual destructors จำเป็นสำหรับการ cleanup ที่เหมาะสมเมื่อลบ objects ผ่าน pointers ของ base classes ถ้าไม่มี virtual destructors จะเกิด memory leaks
- **Key Concepts (แนวคิดสำคัญ):**
  - **Virtual Destructor:** Destructor แบบ virtual
  - **Memory Leak:** การรั่วไหลของหน่วยความจำ
  - **Cleanup:** การทำความสะอาด
  - **Polymorphic Classes:** Classes ที่ใช้ polymorphism

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

**📂 Source:** `.applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงรูปแบบการผสานรวมตามเวลาที่แตกต่างกันใน OpenFOAM ซึ่งมีความซับซ้อนและคุณสมบัติด้านความเสถียรที่แตกต่างกัน
- **Explanation (คำอธิบาย):** รูปแบบการผสานรวมตามเวลาที่แตกต่างกันมีต้นทุนการคำนวณที่แตกต่างกัน Explicit methods มีต้นทุนต่ำแต่มีข้อจำกัดด้านความเสถียร ในขณะที่ implicit methods มีต้นทุนสูงแต่มีความเสถียรที่ดีกว่า
- **Key Concepts (แนวคิดสำคัญ):**
  - **Explicit Methods:** วิธีการ explicit ที่มีต้นทุนต่ำ
  - **Implicit Methods:** วิธีการ implicit ที่มีต้นทุนสูง
  - **Runge-Kutta:** วิธีการ Runge-Kutta ที่มีความแม่นยำสูง
  - **Time Integration:** การผสานรวมตามเวลา

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystemSolve.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงรูปแบบการ discretization เชิงพื้นที่ที่แตกต่างกันใน OpenFOAM ซึ่งมีความแม่นยำและความซับซ้อนในการคำนวณที่แตกต่างกัน
- **Explanation (คำอธิบาย):** รูปแบบการ discretization เชิงพื้นที่ที่แตกต่างกันมีความแม่นยำและความซับซ้อนในการคำนวณที่แตกต่างกัน รูปแบบระดับสูงให้ความแม่นยำที่ดีขึ้นแต่มีต้นทุนการคำนวณที่เพิ่มขึ้น
- **Key Concepts (แนวคิดสำคัญ):**
  - **Upwind Scheme:** รูปแบบ upwind ที่มีเสถียรภาพสูง
  - **Central Differencing:** รูปแบบ central differencing ที่มีความแม่นยำสูง
  - **High-Resolution Schemes:** รูปแบบระดับสูงที่มีความแม่นยำสูง
  - **TVD Schemes:** รูปแบบ TVD (Total Variation Diminishing)

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

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystemSolve.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงเทคนิคการเร่งการลู่เข้าที่ใช้ใน OpenFOAM ซึ่งช่วยเพิ่มประสิทธิภาพในการแก้ระบบสมการเชิงเส้น
- **Explanation (คำอธิบาย):** OpenFOAM ใช้วิธีการเร่งการลู่เข้าหลายวิธีเพื่อเพิ่มประสิทธิภาพในการแก้ระบบสมการเชิงเส้น วิธีการ multigrid บรรลุความซับซ้อนที่เหมาะสมที่สุด O(n) สำหรับปัญหาประเภท elliptic
- **Key Concepts (แนวคิดสำคัญ):**
  - **Residual Smoothing:** การทำให้ residual เรียบ
  - **Multigrid:** วิธีการ multigrid สำหรับการเร่งการลู่เข้า
  - **Convergence Acceleration:** เทคนิคการเร่งการลู่เข้า
  - **Linear Solvers:** ตัวแก้ระบบสมการเชิงเส้น

วิธีการ multigrid บรรลุความซับซ้อนที่เหมาะสมที่สุด $O(n)$ สำหรับปัญหาประเภท elliptic โดยการแยกส่วนประกอบของข้อผิดพลาดผ่านหลายระดับของเกรด

## สรุปแนวทางปฏิบัติที่ดี

### การออกแบบโค้ด

1. **Virtual calls ควรอยู่ในระดับสูง**: ใช้ที่ระดับ field/matrix ไม่ใช่ต่อเซลล์
2. **Field-level operations**: กระจุกตัวการคำนวณให้มีขนาดใหญ่
3. **Expression templates**: ใช้ประโยชน์จาก lazy evaluation
4. **Smart pointers**: เลือก `autoPtr` vs `tmp` อย่างระมัดระวัง

### การทดสอบประสิทธิภาพ

```cpp
// Profiling template
template<class Func>
scalar timeCall(Func&& f, label nIters = 1000) {
    clock_t start = clock();
    for (label i = 0; i < nIters; i++) {
        f();
    }
    return scalar(clock() - start) / CLOCKS_PER_SEC / nIters;
}

// Usage
auto tVirtual = timeCall([&]() { drag->K(); });
auto tDirect = timeCall([&]() { directDragCalc(); });
Info << "Virtual: " << tVirtual << "s, Direct: " << tDirect << "s" << endl;
```

**📂 Source:** `.applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`

**คำอธิบาย:**
- **Source (แหล่งที่มา):** โค้ดนี้แสดงเทมเพลตสำหรับการทดสอบประสิทธิภาพใน OpenFOAM ซึ่งช่วยในการวัดเวลาการดำเนินการของฟังก์ชันต่างๆ
- **Explanation (คำอธิบาย):** การทดสอบประสิทธิภาพเป็นสิ่งสำคัญในการหา bottleneck และปรับปรุงประสิทธิภาพ เทมเพลตนี้ช่วยให้สามารถวัดเวลาการดำเนินการของฟังก์ชันต่างๆ ได้อย่างง่ายดาย
- **Key Concepts (แนวคิดสำคัญ):**
  - **Profiling:** การทดสอบประสิทธิภาพ
  - **Performance Measurement:** การวัดประสิทธิภาพ
  - **Benchmarking:** การเปรียบเทียบประสิทธิภาพ
  - **Optimization:** การเพิ่มประสิทธิภาพ

### การปรับแต่ง

1. **Profile first**: ใช้ profilers เพื่อหา bottleneck จริง
2. **Measure impacts**: วัดก่อนและหลังการเพิ่มประสิทธิภาพ
3. **Consider trade-offs**: ประสิทธิภาพ vs. ความยืดหยุ่น vs. ความสามารถในการบำรุงรักษา
4. **Document decisions**: บันทึกเหตุผลการออกแบบเพื่อการอ้างอิงในอนาคต

สถาปัตยกรรม polymorphic ของ OpenFOAM ให้ความสมดุลที่ดีระหว่างประสิทธิภาพและความยืดหยุ่น ด้วยการทำความเข้าใจต้นทุนด้านประสิทธิภาพและการใช้กลยุทธ์ที่เหมาะสม นักพัฒนาสามารถสร้างโค้ดที่มีประสิทธิภาพสูงในขณะที่ยังคงประโยชน์ของความยืดหยุ่นทางสถาปัตยกรรม