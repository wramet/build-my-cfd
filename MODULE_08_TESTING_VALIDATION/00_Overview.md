# 🧪 Module 08: การทดสอบและการตรวจสอบความถูกต้อง (Testing and Validation)

> [!TIP] "ความเชื่อถือได้คือหัวใจของ CFD"
> โมดูลนี้จะเปลี่ยนคุณจากผู้รันการจำลองทั่วไป ให้กลายเป็นวิศวกร CFD มืออาชีพที่สามารถพิสูจน์ความถูกต้องของผลลัพธ์ได้อย่างเป็นระบบ

> [!TIP] ทำไม Testing & Validation สำคัญต่อ OpenFOAM?
> ใน OpenFOAM การที่คุณ "ได้ผลลัพธ์" ไม่ได้หมายความว่าผลลัพธ์นั้น **ถูกต้อง** โมดูลนี้จะสอนคุณให้ตอบคำถามข้อสำคัญเหล่านี้:
> - **Verification (การตรวจสอบ)**: คำณวณของเราแก้สมการถูกต้องหรือไม่? → เกี่ยวข้องกับ `system/fvSchemes`, `system/fvSolution`
> - **Validation (การยืนยัน)**: แบบจำลองทางคณิตศาสตร์ของเราสอดคล้องกับฟิสิกส์จริงหรือไม่? → เกี่ยวข้องกับการเปรียบเทียบกับ `0/` field data, `constant/` properties
> - **Code Testing**: โค้ดที่เราเขียนเองทำงานถูกต้องหรือไม่? → เกี่ยวข้องกับ `src/` directory structure, compilation, unit testing

## 🎯 ภาพรวมของโมดูล (Module Roadmap)

โครงสร้างการเรียนรู้ถูกออกแบบให้ครอบคลุมตั้งแต่พื้นฐานทางทฤษฎีไปจนถึงการปฏิบัติการจริงในระดับอุตสาหกรรม:

![[v_model_master_v_and_v.png]]
`A comprehensive V-Model diagram for CFD. The descending arm includes 'Physical Reality', 'Mathematical Model', and 'Discretized Code'. The ascending arm includes 'Numerical Results', 'Verified Code', and 'Validated Model'. Horizontal links connect 'Verification' to 'Math' and 'Validation' to 'Reality'. scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

```mermaid
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
M1[01 Verification Fundamentals]:::explicit --> M2[02 Test Framework Development]:::implicit
M2 --> M3[03 Validation Benchmarks]:::implicit
M3 --> M4[04 QA, Automation & Profiling]:::success
```

### 1. [[CONTENT/01_VERIFICATION_FUNDAMENTALS/00_Overview|01 Verification Fundamentals]]
- **เนื้อหา**: ปรัชญาการทดสอบ, MMS, Grid Convergence (GCI), Richardson Extrapolation
- **เป้าหมาย**: เข้าใจความถูกต้องเชิงคณิตศาสตร์ของโค้ด

> [!NOTE] **📂 OpenFOAM Context**
> เนื้อหา Verification ในบทนี้เกี่ยวข้องกับ:
> - **Numerical Accuracy**: การตรวจสอบว่าการ discretization และ solver settings ให้ผลลัพธ์ที่ converge อย่างถูกต้อง → `system/fvSchemes` (เช่น `gradSchemes`, `divSchemes`), `system/fvSolution` (เช่น `solvers`, `algorithms`)
> - **Grid Convergence**: การทดสอบว่า mesh ละเอียดพอหรือยัง → เกี่ยวข้องกับ `constant/polyMesh/`, mesh quality metrics
> - **Solution Verification**: การตรวจสอบว่า iterative tolerance ถูกต้องหรือไม่ → `system/fvSolution` ที่เกี่ยวข้องกับ `tolerance`, `relTol`

### 2. [[CONTENT/02_TEST_FRAMEWORK_CODING/00_Overview|02 Test Framework Development]]
- **เนื้อหา**: การเขียน Unit Testing ใน C++, การสร้างระบบ Assertion, การจัดการ Numerical Tolerance
- **เป้าหมาย**: พัฒนาระบบทดสอบอัตโนมัติภายในโครงสร้าง OpenFOAM

> [!NOTE] **📂 OpenFOAM Context**
> เนื้อหา Test Framework ในบทนี้เกี่ยวข้องกับ:
> - **Code Testing**: การเขียน unit test สำหรับ custom boundary conditions, source terms, หรือ new turbulence models → อยู่ใน `src/` directory structure (เช่น `src/finiteVolume/`, `src/turbulenceModels/`)
> - **Compilation System**: การทำให้ test suite รวมเข้ากับ OpenFOAM build system → `Make/files`, `Make/options`
> - **Assertion Framework**: การใช้ `Info`, `Warning`, `FatalError` ในการ debug → เป็น built-in OpenFOAM debugging tools

### 3. [[CONTENT/03_VALIDATION_BENCHMARKS/00_Overview|03 Validation Benchmarks]]
- **เนื้อหา**: การเปรียบเทียบกับ Experimental Data, การตรวจสอบ Mesh & BC, มาตรฐาน Best Practices
- **เป้าหมาย**: ยืนยันความสอดคล้องระหว่างแบบจำลองทางคณิตศาสตร์กับฟิสิกส์จริง

> [!NOTE] **📂 OpenFOAM Context**
> เนื้อหา Validation ในบทนี้เกี่ยวข้องกับ:
> - **Physics Validation**: การเปรียบเทียบ field variables เช่น `U`, `p`, `T` กับ experimental data → เกี่ยวข้องกับ `0/` directory (initial/boundary conditions), `constant/` (transport properties, turbulence properties)
> - **Mesh Independence**: การทดสอบว่า mesh ที่ใช้ละเอียดพอ → เกี่ยวข้องกับ `constant/polyMesh/`, mesh quality tools
> - **Boundary Conditions**: การตรวจสอบว่า BC ที่เลือกสอดคล้องกับ physical experiment → เกี่ยวข้องกับ `0/` boundary field definitions, `constant/boundaryData/`

### 4. [[CONTENT/04_QA_AUTOMATION_PROFILING/00_Overview|04 QA, Automation & Profiling]]
- **เนื้อหา**: Regression Testing, Performance Profiling, Advanced Debugging (GDB/Valgrind)
- **เป้าหมาย**: การประกันคุณภาพในระยะยาวและการเพิ่มประสิทธิภาพการคำนวณ

> [!NOTE] **📂 OpenFOAM Context**
> เนื้อหา QA & Automation ในบทนี้เกี่ยวข้องกับ:
> - **Regression Testing**: การทำให้แน่ใจว่า code changes ไม่ทำลาย existing functionality → ใช้ `system/controlDict` สำหรับ automated testing, `functionObjects` สำหรับ runtime monitoring
> - **Performance Profiling**: การตรวจสอบ computational efficiency, parallel scaling → เกี่ยวข้องกับ `system/decomposeParDict` (parallelization), profiling tools (GDB, Valgrind)
> - **Advanced Debugging**: การตรวจสอบ memory leaks, segmentation faults, performance bottlenecks → เกี่ยวข้องกับ compilation flags, debug builds, solver execution logs

---

## 🚀 จุดเริ่มต้นการเรียนรู้
หากคุณเพิ่งเริ่มต้น แนะนำให้ศึกษาจาก **[[CONTENT/01_VERIFICATION_FUNDAMENTALS/00_Overview|บทที่ 1]]** เพื่อสร้างความเข้าใจใน "กระบวนการคิด" เบื้องหลังการตรวจสอบความถูกต้องก่อนเริ่มลงมือเขียนโค้ด