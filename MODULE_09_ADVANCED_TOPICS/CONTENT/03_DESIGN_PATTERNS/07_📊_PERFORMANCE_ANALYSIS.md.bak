## 📊 การวิเคราะห์ประสิทธิภาพ

### โอเวอร์เฮดของ Virtual Function ในบริบท CFD

**การวิเคราะห์ Benchmark**:
- การดำเนินการกับ Field (เช่น `U + V`): ~1000 ns
- การเรียก virtual function: ~2 ns
- **โอเวอร์เฮด**: ~0.2% ต่อการเรียก

**การอธิบายทางคณิตศาสตร์**:

กำหนด:
- $t_{\text{field}}$ = เวลาการดำเนินการกับ field
- $t_{\text{virtual}}$ = เวลาการส่งผ่านแบบ virtual
- $n$ = จำนวนการดำเนินการต่อ time step

เวลาทั้งหมดเมื่อใช้ virtual calls:
$$
T_{\text{virtual}} = n \cdot (t_{\text{field}} + t_{\text{virtual}})
$$

เวลาทั้งหมดเมื่อไม่ใช้ virtual calls (static dispatch):
$$
T_{\text{static}} = n \cdot t_{\text{field}}
$$

โอเวอร์เฮดสัมพัทธ์:
$$
\frac{T_{\text{virtual}} - T_{\text{static}}}{T_{\text{static}}} = \frac{t_{\text{virtual}}}{t_{\text{field}}} \approx 0.002 \ (0.2\%)
$$

**สรุป**: โอเวอร์เฮดของ virtual function น้อยมากเมื่อเปรียบเทียบกับการดำเนินการกับ field ความยืดหยุ่นที่ได้รับมีค่ามากกว่าค่าใช้จ่ายด้านประสิทธิภาพอย่างมีนัยสำคัญ

### การวิเคราะห์โอเวอร์เฮดของหน่วยความจำ

**Strategy Pattern**:
- แต่ละ strategy object: ~64 bytes (vtable pointer + member variables)
- การจำลองทั่วไป: 10-20 strategy objects
- **รวม**: ~1-2 KB (เล็กน้อยเมื่อเปรียบเทียบกับการจัดเก็บ field)

**Factory Registration**:
- Static tables: ~100 bytes ต่อ registered type
- OpenFOAM ทั่วไป: ~1000 registered types
- **รวม**: ~100 KB (ยังคงน้อย)

### ประสิทธิภาพเวลา Compile เทียบกับ Runtime

**โอเวอร์เฮดของ Template Instantiation**:
การใช้ templates ใน OpenFOAM ให้ polymorphism ระดับ compile ซึ่งขจัดโอเวอร์เฮดของ virtual function อย่างไรก็ตาม สิ่งนี้มาพร้อมกับต้นทุนของเวลาคอมไพล์ที่เพิ่มขึ้นและขนาดไบนารี

**การวิเคราะห์ Code Bloat**:
- Template instantiation สำหรับ `GeometricField<Type, PatchField, GeoMesh>` กับประเภททั่วไป:
  - `volScalarField`, `volVectorField`, `surfaceScalarField`: ~500 KB แต่ละตัว
  - Template code ทั้งหมด: ~2-5 MB ต่อ executable

**การปรับให้เหมาะสมระดับ Runtime**:
OpenFOAM ใช้การปรับให้เหมาะสมระดับ runtime หลายอย่าง:
1. **Expression Templates**: ช่วยให้ lazy evaluation ของการดำเนินการกับ field
2. **Operator Overloading**: ให้ไวยากรณ์ทางคณิตศาสตร์ตามธรรมชาติโดยไม่มีผลกระทบต่อประสิทธิภาพ
3. **Memory Pool Management**: ลดโอเวอร์เฮดการจัดสรรใน loop ที่แน่นหนา

### พิจารณาประสิทธิภาพแบบขนาน

**โอเวอร์เฮดการแบ่งโดเมน**:
- โอเวอร์เฮดการสื่อสารต่อคู่โปรเซสเซอร์: ~50-100 μs ต่อข้อความ
- การจำลอง CFD ทั่วไป: 10-100 ข้อความต่อ time step
- **โอเวอร์เฮดแบบขนานทั้งหมด**: ~1-10 ms ต่อ time step

**ผลกระทบการกระจายภาระงาน**:
การกระจายภาระงานที่ไม่ดีสามารถส่งผลกระทบต่อประสิทธิภาพอย่างมีนัยสำคัญ:
$$
\text{Speedup}_{\text{actual}} = \frac{T_{\text{sequential}}}{\max(T_i) + T_{\text{communication}}}
$$

โดยที่ $T_i$ คือเวลาคำนวณบนโปรเซสเซอร์ $i$

**ข้อจำกัดของ Memory Bandwidth**:
ในการจำลองขนาดใหญ่ memory bandwidth มักจะกลายเป็นปัจจัยจำกัด:
- Memory bandwidth ทั่วไป: ~50-100 GB/s
- การดำเนินการกับ field: ~10-50 GB/s แบนด์วิดธ์ยั่งยืน
- **ประสิทธิภาพ**: ~20-80% ขึ้นอยู่กับรูปแบบการเข้าถึง

### การปรับให้เหมาะสมประสิทธิภาพ Solver

**การเลือก Linear Solver**:
Solver ต่างๆ ให้ลักษณะประสิทธิภาพที่แตกต่างกัน:

| Solver Type | Complexity | Memory Usage | Best For |
|-------------|------------|--------------|----------|
| Diagonal | O(n) | Low | Diagonally dominant systems |
| PCG | O(n√n) | Medium | Symmetric positive definite |
| GAMG | O(n log n) | High | Large-scale problems |
| SmoothSolver | O(n²) | Low-Medium | Small-medium problems |

**ผลกระทบของ Preconditioner**:
การเลือก preconditioner สามารถส่งผลต่อการลู่เข้าอย่างมีนัยสำคัญ:
- ไม่ใช้ preconditioning: 100-1000 iterations
- Diagonal preconditioning: 50-200 iterations  
- ILU/GAMG: 10-50 iterations

**การตรวจสอบการลู่เข้า**:
คลาส `SolverPerformance` ของ OpenFOAM ติดตาม:
```cpp
struct SolverPerformance {
    scalar finalResidual_;
    scalar initialResidual_;
    int nIterations_;
    bool converged_;
    scalar convergenceTolerance_;
};
```

### การปรับให้เหมาะสมการดำเนินการกับ Field

**Loop Unrolling**:
OpenFOAM ใช้ compiler directives เพื่อปรับให้เหมาะสมการดำเนินการกับ field:
```cpp
// In finiteVolume/fields/volFields/volFields.H
forAll(U, i) {
    U[i] = U[i] + V[i];  // Auto-vectorized
}
```

**การปรับให้เหมาะสม Cache**:
Fields ถูกจัดเก็บใน memory layout ที่เป็นมิตรกับ cache:
- **Row-major order**: ปรับปรุง spatial locality
- **Aligned allocation**: ทำให้มั่นใจถึงการใช้ cache line ที่เหมาะสมที่สุด
- **Memory prefetching**: ลด cache misses ในการดำเนินการขนาดใหญ่

### รูปแบบการเข้าถึงหน่วยความจำ

**Temporal Locality**:
OpenFOAM เวอร์ชันล่าสุดปรับให้เหมาะสม temporal locality ผ่าน:
- การนำ field กลับมาใช้ในการดำเนินการประกอบ
- การกำจัด field ชั่วคราว
- Register promotion สำหรับการดำเนินการกับ field ขนาดเล็ก

**Spatial Locality**:
การปรับให้เหมาะสมรวมถึง:
- การจัดสรรหน่วยความจำติดกันสำหรับข้อมูล field
- การดำเนินการแบบ block-based สำหรับการใช้ cache ที่ดีขึ้น
- SIMD vectorization สำหรับการดำเนินการแบบ element-wise

### การวิเคราะห์ Profiling และ Bottleneck

**เครื่องมือ Profiling**:
- `gprof`: การวิเคราะห์การเรียกฟังก์ชัน
- `perf`: การวิเคราะห์ hardware counter
- `valgrind`: การวิเคราะห์หน่วยความจำและการวิเคราะห์ cache
- `Intel VTune`: การปรับให้เหมาะสมประสิทธิภาพขั้นสูง

**Bottlenecks ทั่วไป**:
1. **Linear Solver Convergence**: 40-60% ของเวลาทำงาน
2. **Matrix Assembly**: 15-25% ของเวลาทำงาน
3. **Boundary Condition Updates**: 5-15% ของเวลาทำงาน
4. **File I/O**: 5-10% ของเวลาทำงาน

**กลยุทธ์การปรับให้เหมาะสม**:
1. **การปรับปรุงเชิงอัลกอริทึม**: การเลือก solver ที่ดีขึ้น
2. **การปรับให้เหมาะสมโครงสร้างข้อมูล**: ปรับปรุง memory layout
3. **การปรับให้เหมาะสมคอมไพเลอร์**: Vectorization, unrolling
4. **การปรับขนาดแบบขนาน**: การแบ่งโดเมนที่ดีขึ้น
