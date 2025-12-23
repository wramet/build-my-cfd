# Rhie-Chow Interpolation

## 🎯 ความสำคัญ (Importance) 

ใน OpenFOAM ซึ่งใช้การจัดวางตัวแปรแบบ **Collocated Grid** (ทั้งความเร็วและความดันถูกเก็บไว้ที่จุดศูนย์กลางเซลล์) หากใช้การประมาณค่าแบบ Linear ปกติจะเกิดปัญหา **Pressure-Velocity Decoupling** ซึ่งนำไปสู่สนามความดันที่แกว่งแบบตารางหมากรุก (Checkerboard oscillations) 

**Rhie-Chow interpolation** (1983) เป็นเทคนิคที่ถูกพัฒนาขึ้นเพื่อแก้ปัญหานี้โดยเฉพาะ

---

## 📐 1. ปัญหา Checkerboard (The Checkerboard Problem)

เมื่อตัวแปรความดันถูกเก็บที่จุดศูนย์กลางเซลล์ เกรเดียนต์ความดันที่จุด $P$ (\nabla p_P) หากคำนวณจากเซลล์ข้างเคียง $W$ และ $E$ จะไม่รับรู้ถึงความแตกต่างของความดันระหว่างเซลล์ที่อยู่ติดกันโดยตรง:
$$\left( \frac{\partial p}{\partial x} \right)_P \approx \frac{p_E - p_W}{2\Delta x}$$ 
หาก $p$ มีลักษณะสลับฟันปลา (เช่น 10, 0, 10, 0) เกรเดียนต์ที่คำนวณได้จะเป็นศูนย์เสมอ ซึ่งไม่เป็นความจริงทางกายภาพ

---

## 🔢 2. การกำหนดสูตรทางคณิตศาสตร์ (Mathematical Formulation)

Rhie-Chow เสนอให้คำนวณความเร็วที่หน้าเซลล์ ($u_f$) โดยการเพิ่มเทอม Numerical Diffusion ที่ขึ้นกับเกรเดียนต์ความดัน:

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - \mathbf{D}_f (\nabla p_f - \overline{\nabla p}_f) \tag{2.1}$$ 

**นิยามตัวแปร:**
- $\overline{\mathbf{u}}_f$: ความเร็วที่หน้าเซลล์จากการเฉลี่ยแบบปกติ (Linear interpolation)
- $\mathbf{D}_f = \overline{(\frac{1}{a_P})}_f$: สัมประสิทธิ์การแพร่ประสิทธิผลที่หน้าเซลล์
- $\nabla p_f$: เกรเดียนต์ความดันที่คำนวณที่หน้าเซลล์โดยตรง (Compact stencil)
- $\overline{\nabla p}_f$: เกรเดียนต์ความดันจากการเฉลี่ยเกรเดียนต์ที่จุดศูนย์กลางเซลล์

**ความหมายทางกายภาพ:** เทอมในวงเล็บแสดงถึงความแตกต่างระหว่างเกรเดียนต์ "จริง" ที่หน้าเซลล์ กับเกรเดียนต์ "เฉลี่ย" หากค่าทั้งสองเท่ากัน เทอมนี้จะเป็นศูนย์

---

## 💻 3. OpenFOAM Implementation

ใน OpenFOAM, Rhie-Chow ถูกนำมาใช้โดยปริยายผ่านการสร้าง **Flux ($\phi$)** ที่หน้าเซลล์ ซึ่งมักพบในไฟล์ `pEqn.H`:

```cpp
// 1. คำนวณ rAU (1/aP)
volScalarField rAU(1.0/UEqn.A());

// 2. คำนวณ HbyA (H/aP)
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// 3. สร้าง Flux (phi) พร้อม Rhie-Chow correction
surfaceScalarField phiHbyA
(
    "phiHbyA",
    fvc::flux(HbyA) // การทำ interpolate(HbyA) & Sf()
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi) // Correction term
);

// 4. แก้สมการความดันโดยใช้ Laplacian
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
```

---

## ✅ 4. ประโยชน์ของ Rhie-Chow

1. **ขจัด Checkerboard oscillations**: ทำให้สนามความดันเรียบและลู่เข้าได้ง่าย
2. **รักษาความแม่นยำ**: ยังคงความแม่นยำระดับอันดับสอง (Second-order accuracy)
3. **รองรับ Unstructured Mesh**: สามารถใช้งานได้กับ Mesh ที่ซับซ้อนใน OpenFOAM ได้อย่างมีประสิทธิภาพ

---
**หัวข้อถัดไป**: [การเปรียบเทียบอัลกอริทึมต่างๆ](./05_Algorithm_Comparison.md)