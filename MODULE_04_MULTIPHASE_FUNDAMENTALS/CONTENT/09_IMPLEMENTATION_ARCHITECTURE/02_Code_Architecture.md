# สถาปัตยกรรมโค้ดของ MultiphaseEulerFoam (Code Architecture)

## 1. บทนำ (Overview)

`multiphaseEulerFoam` เป็น Solver ที่แสดงถึงความก้าวหน้าสูงสุดของ OpenFOAM ในด้านการไหลหลายเฟส โดยใช้สถาปัตยกรรม **Object-Oriented** และ **Advanced C++ Templates** เพื่อจัดการกับระบบที่มีจำนวนเฟสเท่าใดก็ได้ที่ใช้สนามความดันร่วมกัน แต่รักษาคุณสมบัติเฉพาะของแต่ละเฟสไว้ได้อย่างอิสระ

---

## 2. ลำดับชั้นของคลาสหลัก (Core Class Hierarchy)

### 2.1 คลาส `phaseModel`
เป็นคลาสที่เก็บข้อมูลและพฤติกรรมของหนึ่งเฟส (Single phase) โดยห่อหุ้มฟิลด์และคุณสมบัติทางเทอร์โมไดนามิกส์ที่จำเป็น:

| ฟิลด์ (Field) | ประเภท (Type) | คำอธิบาย |
|-------|------|-------------|
| `alpha()` | `volScalarField` | สัดส่วนปริมาตร (Volume fraction) |
| `U()` | `volVectorField` | ความเร็วของเฟส (Velocity) |
| `rho()` | `volScalarField` | ความหนาแน่น (Density) จากเทอร์โมฟิสิกส์ |
| `thermo()` | Reference | ออบเจ็กต์ `thermophysicalProperties` |
| `turbulence()` | Reference | ออบเจ็กต์ `multiphaseTurbulenceModel` |

### 2.2 คลาส `phaseSystem`
ทำหน้าที่เป็นศูนย์กลาง (Central Hub) ในการจัดการคอลเลกชันของ `phaseModel` และควบคุมการโต้ตอบระหว่างเฟส (Inter-phase coupling):
- **Phase Storage**: เก็บรายการของเฟสทั้งหมดในรูปแบบ `PtrListDictionary<phaseModel>`
- **Interaction Models**: จัดการแรง Drag, Lift, Virtual Mass และการถ่ายเทความร้อน/มวล
- **Solution Strategy**: ประสานงานลำดับการแก้สมการของทุกเฟส

---

## 3. การจัดระเบียบโครงสร้างข้อมูล (Data Structure Organization)

### 3.1 การจัดเก็บฟิลด์ (Field Storage)
OpenFOAM จัดเก็บฟิลด์ในคลาสคอนเทนเนอร์ที่ใช้เทมเพลตเพื่อให้การเข้าถึงมีประสิทธิภาพสูงสุด:
- **`HashTable`**: ใช้สำหรับการเข้าถึงฟิลด์ตามชื่อด้วยความเร็วระดับ $O(1)$
- **Type Safety**: แยกเก็บฟิลด์ตามประเภทข้อมูล (Scalar, Vector, Tensor) เพื่อความปลอดภัยในการคำนวณ

```cpp
// ตัวอย่างคอนเทนเนอร์จัดเก็บฟิลด์เฟส
class phaseFieldContainer {
private:
    HashTable<volScalarField*, word> scalarFields_;
    HashTable<volVectorField*, word> vectorFields_;
    // การเข้าถึงฟิลด์พร้อมการตรวจสอบขอบเขต
    volScalarField& scalarField(const word& name);
};
```

---

## 4. การจัดการหน่วยความจำ (Memory Management)

### 4.1 Lazy Allocation
เพื่อเพิ่มประสิทธิภาพสูงสุด OpenFOAM จะไม่จัดสรรหน่วยความจำให้ฟิลด์ทั้งหมดล่วงหน้า แต่จะสร้างขึ้นจริงเมื่อมีการเรียกใช้งานครั้งแรกเท่านั้น (Lazy Creation) ช่วยลดการใช้หน่วยความจำในกรณีที่บางฟิลด์ไม่ได้ถูกใช้งานในเคสนั้นๆ

### 4.2 Smart Pointers แบบ Reference-Counted
ใช้ `tmp<T>` และ `autoPtr<T>` เพื่อการจัดการหน่วยความจำอัตโนมัติ (Garbage collection) และป้องกันการรั่วไหลของหน่วยความจำ (Memory Leaks):

```cpp
// การใช้ tmp สำหรับการจัดการหน่วยความจำอัตโนมัติ
tmp<volScalarField> tfield = new volScalarField(mesh, ...);
volScalarField& field = tfield.ref(); // field จะถูกทำลายอัตโนมัติเมื่อสิ้นสุด Scope
```

---

## 5. การจัดการ Mesh และการควบคุมเวลา (Mesh & Time Management)

### 5.1 Adaptive Time Stepping (CFL Condition)
ระบบจะปรับก้าวเวลา ($\Delta t$) อัตโนมัติโดยอิงตามจำนวน Courant ($Co$) เพื่อรักษาเสถียรภาพของการคำนวณ:

**จำนวน Courant สำหรับความเร็ว:**
$$Co = \frac{|\mathbf{u}| \Delta t}{\Delta x}$$

**จำนวน Courant สำหรับสัดส่วนเฟส (Advection):**
$$Co_\alpha = \frac{|\mathbf{U}_\alpha| \Delta t}{\Delta x}$$

โดยที่ $\mathbf{u}$ คือความเร็วของไหล, $\mathbf{U}_\alpha$ คือความเร็วของอินเตอร์เฟส, และ $\Delta x$ คือขนาดของเซลล์

---

## 6. กลยุทธ์การแก้ปัญหาเชิงตัวเลข (Numerical Solution Strategy)

### 6.1 อัลกอริทึม PIMPLE
ใช้การวนซ้ำเพื่อแก้ความเชื่อมโยงระหว่างความดันและความเร็ว:
1. **Momentum Predictor**: ทำนายความเร็วเบื้องต้น
2. **Momentum Coupling**: แก้สมการโมเมนตัมของทุกเฟสพร้อมกัน
3. **Pressure Equation**: แก้สมการความดันร่วมเพื่อรักษาความต่อเนื่อง (Continuity)
4. **Correction**: แก้ไขค่าสัดส่วนเฟสและพลังงาน

### 6.2 การผ่อนคลาย (Under-Relaxation)
เพื่อป้องกันการแกว่ง (Oscillation) ของค่าที่คำนวณได้:
$$\phi^{new} = \phi^{old} + \lambda_{relax}(\phi^{calculated} - \phi^{old})$$

| ฟิลด์ (Field) | ค่า $\lambda$ ที่แนะนำ |
|-------|------------------|
| **Phase fractions** | 0.7 - 0.9 |
| **Momentum (U)** | 0.6 - 0.8 |
| **Pressure (p)** | 0.2 - 0.5 |

---

## 7. การประมวลผลแบบขนาน (Parallel Implementation)

รองรับการสลายตัวโดเมน (Domain Decomposition) และการสื่อสารผ่าน MPI:
- **Synchronization**: ฟิลด์ต่างๆ จะถูกประสานข้อมูลข้ามขอบเขตโปรเซสเซอร์ (Processor boundaries) ผ่านคลาส `processorFvPatchField`
- **Scalability**: การออกแบบที่ลดการสร้างวัตถุชั่วคราวช่วยให้สเกลการคำนวณในระบบขนาดใหญ่ได้ดี

สถาปัตยกรรมนี้ช่วยให้ `multiphaseEulerFoam` มีความยืดหยุ่นสูง สามารถปรับแต่งโมเดลแรงระหว่างเฟส หรือเพิ่มฟิสิกส์ใหม่ๆ เข้าไปได้โดยไม่ต้องแก้ไขโครงสร้างหลักของ Solver

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM-10, phaseModel.H, phaseSystem.H และกลไกการจัดการหน่วยความจำของ OpenFOAM*