# 05 — Chemkin Parsing

การแปลงไฟล์ Chemkin สำหรับ OpenFOAM

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- อธิบายโครงสร้างและรูปแบบของไฟล์ Chemkin ได้
- แปลงไฟล์ Chemkin เป็นรูปแบบ OpenFOAM ด้วย `chemkinToFoam`
- เขียนและแก้ไขไฟล์ `chem.inp` พร้อมคำอธิบายรายละเอียด
- แก้ปัญหาที่เกิดขึ้นระหว่างการแปลงไฟล์
- ตั้งค่า OpenFOAM เพื่ออ่าน chemistry จากไฟล์ที่แปลงแล้ว

---

## 📋 Key Takeaways

- **Chemkin** เป็นมาตรฐานอุตสาหกรรมสำหรับ chemistry mechanisms ที่รองรับโดย OpenFOAM
- มี 3 ไฟล์หลัก: `chem.inp` (reactions), `thermo.dat` (thermodynamics), `tran.dat` (transport)
- คำสั่ง `chemkinToFoam` แปลงไฟล์ Chemkin เป็น OpenFOAM format
- Modified Arrhenius equation: $k = A \cdot T^n \cdot \exp(-E_a/RT)$ ใช้กำหนด rate ของทุกปฏิกิริยา
- การตรวจสอบผลลัพธ์หลังแปลงเป็นสิ่งสำคัญเพื่อหลีกเลี่ยงข้อผิดพลาดในการจำลอง

---

## 🔍 What — What is Chemkin Format?

**Chemkin** เป็น **standard format** สำหรับ chemistry mechanisms ที่ใช้กันอย่างแพร่หลายในวงการ combustion simulation

### ทำไม Chemkin ถึงสำคัญ?

| ข้อดี | คำอธิบาย |
|--------|----------|
| **Standard อุตสาหกรรม** | ใช้ใน literature และ commercial software จำนวนมาก |
| **Database ขนาดใหญ่** | GRI-Mech, USC Mech II, San Diego Mech, ฯลฯ |
| **Validation แล้ว** | Mechanisms ได้รับการทดสอบและยอมรับในวงการวิชาการ |
| **ใช้ร่วมกันได้** | ไม่ต้องเขียน reactions เองทั้งหมด |

---

## 🤔 Why — Why Use Chemkin with OpenFOAM?

OpenFOAM รองรับ Chemkin format เพื่อให้:
1. **ใช้โค้ดเดิมได้** —  mechanisms ที่มีอยู่สามารถนำมาใช้ได้ทันที
2. **ลดความผิดพลาด** — ไม่ต้องพิมพ์ reactions ด้วยมือ
3. **อัปเดตง่าย** — เมื่อมี mechanisms ใหม่ สามารถดาวน์โหลดและแปลงได้เลย
4. **ร่วมมือกับชุมชน** — ใช้ mechanisms ที่สร้างโดยผู้เชี่ยวชาญทั่วโลก

---

## 🔧 How — How to Use Chemkin with OpenFOAM

### 1. ไฟล์ Chemkin มีอะไรบ้าง?

| ไฟล์ | เนื้อหา | ตัวอย่างข้อมูล |
|------|---------|------------------|
| **thermo.dat** | คุณสมบัติ thermodynamic | $C_p(T)$, $H(T)$, $S(T)$ |
| **chem.inp** | ปฏิกิริยาเคมีและ kinetic parameters | Species, reactions, Arrhenius coefficients |
| **tran.dat** | Transport properties | $\mu$ (viscosity), $k$ (conductivity), $D$ (diffusion) |

### 2. ตัวอย่างไฟล์ chem.inp พร้อมคำอธิบาย

```chem
ELEMENTS
H O C N END

SPECIES
H2 O2 H2O CO2 CO N2 OH H O HCO CH2 CH3 CH4 HO2 H2O2 CH2O CH3O CH3OH
END

THERMO all
H2/1986BurcatH2CO/N05
...

REACTIONS    CAL/MOLE   MOLES
CH4 + 2O2 => CO2 + 2H2O   1.5E11  0.0  24370
CH4 + O2 <=> CH3 + OH      2.0E13  0.0  24400
CH3 + O2 <=> CH2O + OH     5.0E11  0.0  15000

LOW / TROE
```

**คำอธิบาย:**
```
LINE 1: ELEMENTS block — กำหนดธาตุที่ใช้ใน mechanism
LINE 2: H O C N — ธาตุไฮโดรเจน ออกซิเจน คาร์บอน ไนโตรเจน
LINE 3: END — จบ ELEMENTS block

LINE 5: SPECIES block — กำหนด species ทั้งหมด
LINE 6: H2 O2 H2O ... — รายชื่อ species คั่นด้วยช่องว่าง
LINE 7: END — จบ SPECIES block

LINE 9: THERMO block — อ้างถึง thermo data
LINE 10: all — ใช้ thermo data สำหรับทุก species

LINE 12: REACTIONS block — เริ่มกำหนดปฏิกิริยา
LINE 12: CAL/MOLE — หน่วยของ activation energy (cal/mol)
LINE 13: CH4 + 2O2 => CO2 + 2H2O — สมการปฏิกิริยา
LINE 13: 1.5E11 — Pre-exponential factor (A)
LINE 13: 0.0 — Temperature exponent (n)
LINE 13: 24370 — Activation energy (Ea/R) in cal/mol

LINE 14: <=> — Reversible reaction (สามารถย้อนกลับได้)
LINE 15: LOW / TROE — Pressure-dependent reactions (advanced)
```

### 3. Modified Arrhenius Equation

ทุกปฏิกิริยาใน Chemkin ใช้ Modified Arrhenius equation:

$$k_f = A \cdot T^n \cdot \exp\left(-\frac{E_a}{RT}\right)$$

**ตัวแปร:**
- $k_f$ — Forward rate constant
- $A$ — Pre-exponential factor (หน่วยขึ้นกับ reaction order)
- $T$ — Temperature (K)
- $n$ — Temperature exponent (ไร้หน่วย)
- $E_a$ — Activation energy (cal/mol หรือ J/mol)
- $R$ — Universal gas constant

**ตัวอย่างใน chem.inp:**
```
CH4 + 2O2 => CO2 + 2H2O   1.5E11  0.0  24370
                          ↑ A     ↑ n  ↑ Ea/R (cal/mol)
```

### 4. แปลง Chemkin เป็น OpenFOAM Format

```bash
chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo
```

**อธิบาย arguments:**
- `chem.inp` — ไฟล์ reactions (จำเป็น)
- `thermo.dat` — ไฟล์ thermodynamic data (จำเป็น)
- `constant/reactions` — Output folder สำหรับ reactions
- `constant/thermo` — Output folder สำหรับ thermo data

**ตัวอย่างผลลัพธ์:**
```
Reading thermo file
Reading chemkin file
...
Writing OpenFOAM chemistry format files to:
  constant/reactions
  constant/thermo
```

### 5. การตั้งค่าใน OpenFOAM

หลังจากแปลงแล้ว ตั้งค่าใน `constant/chemistryProperties`:

```cpp
chemistryModel
{
    solver            rhoReactingFoam;
}

chemistryType
{
    chemistryReader chemkinReader;
    chemistrySolver ode;
}

thermoType
{
    type            heRhoThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}

// ใช้ไฟล์ที่แปลงแล้ว
chemkinReader
{
    chemkinFile     constant/reactions;
    thermoFile      constant/thermo;
}
```

---

## ⚠️ Common Pitfalls & Troubleshooting

### ปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | วิธีแก้ |
|--------|--------|---------|
| **species ไม่ตรงกัน** | Species ใน `chem.inp` ไม่ตรงกับ `thermo.dat` | ตรวจสอบชื่อ species ให้ตรงกันทุกตัว (case-sensitive) |
| **หน่วยผิด** | Activation energy ใช้ cal/mol แต่ OpenFOAM คาดเป็น J/mol | ใช้หน่วยเดียวกันทั้งไฟล์ หรือระบุใน REACTIONS block |
| **Reaction syntax error** | ขาด `=>` หรือ `<=>` หรือ coefficients ผิด | ตรวจสอบรูปแบบ: `A + B => C + D  A  n  Ea` |
| **Missing species** | Species ใน reaction ไม่มีใน SPECIES block | เพิ่ม species ที่ขาดไปใน SPECIES block |
| **File not found** | Path ของไฟล์ไม่ถูกต้อง | ใช้ absolute path หรือสัมพัทธ์จาก case directory |

### การ debug การแปลงไฟล์

```bash
# 1. ตรวจสอบ syntax ของ chem.inp
chemkinToFoam -help

# 2. ทดสอบแปลงและดู output
chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo 2>&1 | tee conversion.log

# 3. ตรวจสอบไฟล์ที่สร้าง
ls -la constant/reactions constant/thermo

# 4. เปรียบเทียบจำนวน species
grep "SPECIES" chem.inp
grep "species" constant/thermo
```

### Error Handling Examples

**Error: species H2 not found in thermo.dat**
```
Solution: เพิ่ม H2 ลงใน THERMO block หรือตรวจสอบการสะกดชื่อ
```

**Error: invalid reaction coefficient**
```
Solution: ตรวจสอบว่ามีเลข 3 ตัวท้าย reaction (A, n, Ea) และไม่มีอักขระพิเศษ
```

**Error: duplicate reaction**
```
Solution: ลบ reaction ที่ซ้ำกัน หรือใช้ DUP หากจงใจให้มี reactions ซ้ำ
```

---

## 📚 Quick Reference

| Task | Command/Syntax |
|------|----------------|
| Convert Chemkin | `chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo` |
| With transport | `chemkinToFoam chem.inp thermo.dat tran.dat constant/reactions constant/thermo` |
| Reader type | `chemkinReader` |
| Reaction format | `A + B => C + D  A  n  Ea` |
| Reversible | `A + B <=> C + D  A  n  Ea` |

---

## 🧠 Concept Check

<details>
<summary><b>1. Chemkin format ใช้ทำไม?</b></summary>

**Chemkin** เป็น **standard format** สำหรับ chemistry mechanisms ที่ใช้กันทั่วโลก

**ประโยชน์:**
- ใช้ mechanisms จาก literature ได้โดยตรง
- มี database ขนาดใหญ่ (GRI-Mech, USC Mech II, etc.)
- ไม่ต้องเขียน reactions เอง

</details>

<details>
<summary><b>2. ไฟล์ Chemkin มีอะไรบ้าง?</b></summary>

| ไฟล์ | เนื้อหา | ตัวอย่าง |
|------|---------|----------|
| **thermo.dat** | คุณสมบัติ thermodynamic | Cp, H, S |
| **chem.inp** | ปฏิกิริยาเคมี | CH4 + 2O2 → CO2 + 2H2O |
| **tran.dat** | Transport properties | μ, k, D |

**การแปลง:**
```bash
chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo
```

</details>

<details>
<summary><b>3. Modified Arrhenius equation คืออะไร?</b></summary>

ใน Chemkin ทุกปฏิกิริยาใช้ Modified Arrhenius:

$$k = A \cdot T^n \cdot \exp\left(-\frac{E_a}{RT}\right)$$

**ตัวอย่างใน chem.inp:**
```
CH4 + 2O2 => CO2 + 2H2O   1.5E11  0.0  24370
                          ↑ A     ↑ n  ↑ Ea (cal/mol)
```

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Reacting Flows
- **บทก่อนหน้า:** [04_Combustion_Models.md](04_Combustion_Models.md) — Combustion Models
- **บทถัดไป:** [06_Practical_Workflow.md](06_Practical_Workflow.md) — ขั้นตอนปฏิบัติ
- **Chemistry Models:** [03_Chemistry_Models.md](03_Chemistry_Models.md) — โมเดลเคมี