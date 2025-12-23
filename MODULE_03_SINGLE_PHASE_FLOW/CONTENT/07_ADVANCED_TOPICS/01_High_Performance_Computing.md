# การประมวลผลสมรรถนะสูง (High-Performance Computing - HPC)

## 📖 บทนำ (Introduction)

การจำลอง CFD ขนาดใหญ่ที่มีจำนวนเซลล์นับล้านหรือพันล้านต้องการพลังการประมวลผลที่มหาศาล OpenFOAM ถูกออกแบบมาให้รองรับการทำงานแบบขนาน (Parallel Computing) ได้อย่างมีประสิทธิภาพผ่านมาตรฐาน MPI และเทคโนโลยี GPU ล่าสุด

---

## 📐 1. การแบ่งโดเมน (Domain Decomposition)

การทำงานแบบขนานใน OpenFOAM เริ่มจากการแบ่ง Mesh ขนาดใหญ่เป็นโดเมนย่อย (Sub-domains) โดยแต่ละโดเมนจะถูกประมวลผลแยกกันในแต่ละ CPU core

### 1.1 อัลกอริทึมการแบ่ง (Decomposition Methods)
- **simple**: แบ่งแบบเรขาคณิต (X, Y, Z)
- **scotch/metis**: ใช้อัลกอริทึม Graph Partitioning เพื่อลดการสื่อสารระหว่างโปรเซสเซอร์ให้น้อยที่สุด (แนะนำสำหรับงานทั่วไป)

### 1.2 การตั้งค่า (`system/decomposeParDict`)
```cpp
numberOfSubdomains  64;
method              scotch;
```

---

## ⚡ 2. การเร่งความเร็วด้วย GPU (GPU Acceleration)

OpenFOAM รุ่นใหม่รองรับการส่งการคำนวณพีชคณิตเชิงเส้น (Linear Algebra) ไปยัง GPU ผ่าน CUDA หรือ OpenCL:

- **Iterative Solver**: สามารถย้าย CG, BiCGStab หรือ AMG solver ไปรันบน GPU ได้
- **ประสิทธิภาพ**: ในบางกรณีสามารถเร่งความเร็วได้มากกว่า CPU หลายเท่า โดยเฉพาะในขั้นตอนการแก้ Pressure Equation ที่เป็นคอขวดหลัก

---

## 🔄 3. ขั้นตอนการทำงานแบบขนาน (Parallel Workflow)

```mermaid
graph LR
    A[Serial Case] --> B[decomposePar]
    B --> C[mpirun -np N solver -parallel]
    C --> D[reconstructPar]
    D --> E[Complete Result]
```

### คำสั่งที่สำคัญ:
```bash
# 1. แบ่งโดเมน
decomposePar

# 2. รันแบบขนาน (ตัวอย่าง 16 โปรเซสเซอร์)
mpirun -np 16 simpleFoam -parallel > log.simulation &

# 3. รวมผลลัพธ์เพื่อนำไปดูใน ParaView
reconstructPar
```

---

## 📊 4. ตัวชี้วัดประสิทธิภาพ (Performance Metrics)

- **Speedup ($S$)**: $S = T_1 / T_p$ (สัดส่วนเวลาที่ลดลงเมื่อเพิ่มโปรเซสเซอร์)
- **Efficiency ($E$)**: $E = S / p$ (ประสิทธิภาพการใช้โปรเซสเซอร์)

---
**หัวข้อถัดไป**: [ความปั่นป่วนขั้นสูง (LES & DES)](./02_Advanced_Turbulence.md)
