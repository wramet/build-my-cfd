# ประเด็นสำคัญที่ควรจดจำ (Key Points to Remember)

## 1. กฎการอนุรักษ์: รากฐานของ CFD (Conservation Laws: Foundation of CFD)

**พลศาสตร์ของไหลเชิงคำนวณ (CFD) ทั้งหมด** ถูกสร้างขึ้นบนหลักการพื้นฐานของการอนุรักษ์มวล โมเมนตัม และพลังงาน

กฎการอนุรักษ์เหล่านี้แสดงถึงข้อจำกัดทางกายภาพที่ควบคุมพฤติกรรมของของไหล และก่อตัวเป็นแกนกลางทางคณิตศาสตร์ของการจำลอง CFD ทั้งหมด:

- **การอนุรักษ์มวล (Mass conservation)**: มั่นใจได้ว่าของไหลจะไม่สามารถถูกสร้างขึ้นหรือถูกทำลายได้ภายในโดเมน (domain)
- **การอนุรักษ์โมเมนตัม (Momentum conservation)**: เป็นไปตามกฎข้อที่สองของนิวตันที่ประยุกต์ใช้กับตัวกลางต่อเนื่อง (continuous media)
- **การอนุรักษ์พลังงาน (Energy conservation)**: รักษาความเป็นไปตามกฎข้อที่หนึ่งของอุณหพลศาสตร์ตลอดทั่วทั้งโดเมนการคำนวณ

ใน OpenFOAM หลักการเหล่านี้ถูกนำไปใช้งานผ่านวิธีไฟไนต์วอลุ่ม (finite volume method) โดยที่รูปแบบอินทิกรัลของสมการอนุรักษ์จะถูกประยุกต์ใช้กับแต่ละปริมาตรควบคุม (control volume)

### สมการการขนส่งทั่วไป (General Transport Equation)

สำหรับคุณสมบัติทั่วไป $\phi$ สมการการอนุรักษ์สามารถแสดงได้ในรูปแบบดังนี้:
$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

โดยที่:
- $\rho$ = ความหนาแน่น (density)
- $\mathbf{u}$ = เวกเตอร์ความเร็ว (velocity vector)
- $\Gamma$ = สัมประสิทธิ์การแพร่ (diffusion coefficient)
- $S_\phi$ = พจน์แหล่งกำเนิด (source terms)

สมการการขนส่งทั่วไปนี้ทำหน้าที่เป็นแม่แบบ (template) สำหรับสมการอนุรักษ์ทั้งหมดใน CFD โดยที่ $\phi$ จะแทนปริมาณทางกายภาพที่แตกต่างกันไปตามสมการเฉพาะที่กำลังทำการแก้ปัญหา

### การประยุกต์ใช้ทฤษฎีบทการลู่ออกของเกาส์ (Application of Gauss's Divergence Theorem)
![[Pasted image 20251223200317.png]]

การทำงานแบบไฟไนต์วอลุ่มใน OpenFOAM จะทำให้สมการอินทิกรัลเหล่านี้กลายเป็นค่าไม่ต่อเนื่อง (discretize) โดยการประยุกต์ใช้ทฤษฎีบทการลู่ออกของเกาส์ (Gauss's divergence theorem):
$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_S \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

โดยที่:
- $\mathbf{F}$ = เวกเตอร์ฟลักซ์ (flux vector)
- $\mathbf{n}$ = เวกเตอร์แนวฉากที่พุ่งออกที่ผิวของเซลล์ (outward normal vector at cell faces)

การทำให้เป็นส่วนย่อย (discretization) นี้ช่วยให้มั่นใจได้ถึงการอนุรักษ์ที่แม่นยำในระดับไม่ต่อเนื่อง (discrete level) ทำให้วิธีไฟไนต์วอลุ่มเหมาะสมอย่างยิ่งสำหรับการประยุกต์ใช้งาน CFD ซึ่งคุณสมบัติการอนุรักษ์ถือเป็นเรื่องที่สำคัญที่สุด

---

## 2. สมการความต่อเนื่อง: หลักการอนุรักษ์มวล (Continuity Equation: Principle of Mass Conservation)

**สมการความต่อเนื่อง (continuity equation)** แสดงถึงหลักการพื้นฐานทางคณิตศาสตร์ที่ว่า มวลไม่สามารถถูกสร้างขึ้นหรือถูกทำลายได้ภายในระบบของไหล

สมการนี้ระบุว่าอัตราการสะสมมวลภายในปริมาตรควบคุมใด ๆ จะต้องเท่ากับฟลักซ์มวลสุทธิที่ไหลเข้าสู่ปริมาตรนั้น รวมกับแหล่งกำเนิดหรือแหล่งรับมวลใด ๆ

### กรณีการไหลแบบอัดตัวไม่ได้ (Incompressible Flow Case)

สำหรับการไหลแบบอัดตัวไม่ได้ซึ่งมีความหนาแน่นคงที่ สมการความต่อเนื่องจะลดรูปอย่างมากเหลือเพียง:
$$\nabla \cdot \mathbf{u} = 0$$

ข้อจำกัดนี้ทำให้มั่นใจได้ว่าการไหลจะมีลักษณะเป็นแบบ **โซเลนอยด์ (solenoidal หรือ divergence-free)** ซึ่งหมายความว่าปริมาตรขององค์ประกอบของไหลจะยังคงที่ในขณะที่เคลื่อนที่ผ่านสนามการไหล (flow field)

### กรณีการไหลแบบอัดตัวได้ (Compressible Flow Case)

ในสถานการณ์การไหลแบบอัดตัวได้ สมการความต่อเนื่องจะมีรูปแบบทั่วไปมากขึ้น:
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

สมการนี้คำนึงถึงการเปลี่ยนแปลงความหนาแน่นและเป็นสิ่งจำเป็นสำหรับการจับปรากฏการณ์ต่าง ๆ เช่น:
- คลื่นกระแทก (Shock waves)
- การแพร่กระจายของเสียง (Acoustic propagation)
- พลศาสตร์ของแก๊สความเร็วสูง (High-speed gas dynamics)

### การเชื่อมโยงความดันและความเร็วใน OpenFOAM (Pressure-Velocity Coupling in OpenFOAM)

ใน OpenFOAM สมการความต่อเนื่องมักจะถูกบังคับใช้ผ่านอัลกอริทึมการเชื่อมโยงความดันและความเร็ว (pressure-velocity coupling algorithms) ที่เชี่ยวชาญเฉพาะด้าน:

| อัลกอริทึม | ประเภทการจำลอง | คุณลักษณะ |
|-----------|------------------|------------------|
| **SIMPLE** | สภาวะคงตัว (Steady-state) | กึ่งอ้อม (Semi-implicit) พร้อมการวนซ้ำ |
| **PISO** | สภาวะไม่คงตัว (Transient) | Pressure-Implicit with Splitting of Operators |
| **PIMPLE** | สภาวะไม่คงตัวขนาดใหญ่ | การผสมผสานระหว่าง SIMPLE และ PISO |

#### อัลกอริทึม SIMPLE

อัลกอริทึม SIMPLE แก้ระบบสมการที่เชื่อมโยงกันผ่านกระบวนการวนซ้ำ:

1. **การทำนายโมเมนตัม (Momentum Prediction)**: แก้สมการโมเมนตัมโดยใช้สนามความดันปัจจุบัน
2. **การแก้ไขความดัน (Pressure Correction)**: สร้างสมการแก้ไขความดันจากเงื่อนไขความต่อเนื่อง
3. **การแก้ไขความเร็ว (Velocity Correction)**: อัปเดตสนามความเร็วตามการแก้ไขความดัน
4. **การอัปเดตเงื่อนไขขอบเขต (Boundary Condition Update)**: ประยุกต์ใช้ค่าที่ได้รับการแก้ไขที่ขอบเขต
5. **การตรวจสอบการลู่เข้า (Convergence Check)**: ตรวจสอบว่าค่าคงเหลือ (residuals) ต่ำกว่าเกณฑ์ที่กำหนด

สำหรับการจำลองแบบสภาวะไม่คงตัว (transient) อัลกอริทึม PISO จะเพิ่มขั้นตอนการแก้ไขเพิ่มเติมเพื่อรักษาความแม่นยำเชิงเวลาในขณะที่ยังคงมั่นใจได้ถึงการอนุรักษ์มวลในแต่ละขั้นตอนเวลา (time step)

---

## 3. สมการ Navier-Stokes: กฎข้อที่สองของนิวตันสำหรับของไหล (Navier-Stokes Equations: Newton's Second Law for Fluids)

**สมการ Navier-Stokes** แสดงถึงรูปแบบทางคณิตศาสตร์ของกฎข้อที่สองของการเคลื่อนที่ของนิวตันที่ประยุกต์ใช้กับองค์ประกอบของของไหล

โดยพื้นฐานแล้ว สมการเหล่านี้ระบุว่าแรงที่กระทำต่ออนุภาคของไหลเท่ากับมวลของอนุภาคคูณด้วยความเร่ง สมการเหล่านี้สร้างสมดุลระหว่าง:
- **แรงเฉื่อย (Inertial forces)**
- **แรงดัน (Pressure forces)**
- **แรงหนืด (Viscous forces)**
- **แรงภายนอก (External body forces)**

### สมการโมเมนตัมในรูปแบบอนุรักษ์ (Momentum Equation in Conservative Form)

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

โดยที่:
- $p$ = ความดัน (pressure)
- $\mu$ = ความหนืดพลวัต (dynamic viscosity)
- $\mathbf{f}$ = แรงภายนอก (เช่น แรงโน้มถ่วงหรือแรงแม่เหล็กไฟฟ้า)

#### การวิเคราะห์พจน์ (Term Analysis):

- **ฝั่งซ้ายมือ**: อนุพันธ์ย่อยของความเร็ว (substantial derivative)
  - ความเร่งเชิงเวลา (Temporal acceleration): $\frac{\partial \mathbf{u}}{\partial t}$
  - ความเร่งจากการพา (Convective acceleration): $(\mathbf{u} \cdot \nabla) \mathbf{u}$

- **ฝั่งขวามือ**: แรงที่ผิว (surface forces)
  - แรงจากเกรเดียนต์ของความดัน (Pressure gradient forces): $-\nabla p$
  - แรงหนืด (Viscous forces): $\mu \nabla^2 \mathbf{u}$

![[Pasted image 20251223200332.png]]
### การนำไปใช้งานใน OpenFOAM (OpenFOAM Implementation)

ใน OpenFOAM พจน์เหล่านี้จะถูกประยุกต์ใช้โดยการทำให้เป็นส่วนย่อยแบบไฟไนต์วอลุ่มด้วยฟังก์ชันเฉพาะทาง:

```cpp
// OpenFOAM Code Implementation
// Momentum equation discretization using finite volume method
// สมการโมเมนตัมที่ถูก discretize ด้วยวิธี finite volume method
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)         // Temporal derivative: ∂(ρU)/∂t
                             // เทอมอนุพันธ์เชิงเวลา
  + fvm::div(phi, U)         // Convective term: ∇·(ρUU)
                             // เทอมการพาแบบไม่เชิงเส้น (non-linear convection)
  - fvm::laplacian(mu, U)    // Diffusion term: ∇·(μ∇U)
                             // เทอมการแพร่ของความหนืด (viscous diffusion)
 ==
    -fvc::grad(p)            // Pressure gradient: -∇p
                             // เทอม gradient ของความดัน (treated explicitly)
);
```

**📂 แหล่งที่มา (Source)**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:46`

**คำอธิบาย (Explanation):**
- `fvm::ddt(rho, U)` - เทอมอนุพันธ์เชิงเวลาของความหนาแน่นและความเร็ว ใช้ implicit discretization เพื่อความเสถียรของการคำนวณ
- `fvm::div(phi, U)` - เทอมการพา (convection term) ที่เป็นเชิงเส้นขึ้นอยู่กับการไหล ซึ่งสำคัญมากในปัญหาการไหลแบบ turbulent
- `fvm::laplacian(mu, U)` - เทอมการแพร่ (diffusion term) ที่เกี่ยวข้องกับความหนืดของของไหล
- `fvc::grad(p)` - เทอม gradient ของความดัน ที่ถูก treat แบบ explicit ในการแก้สมการ

**แนวคิดสำคัญ (Key Concepts):**
- **Implicit (fvm) vs Explicit (fvc)**: fvm (finite volume method) ใช้สำหรับเทอมที่ต้องการ discretization แบบ implicit สำหรับเสถียรภาพเชิงตัวเลข ส่วน fvc (finite volume calculus) ใช้สำหรับเทอมที่คำนวณแบบ explicit
- **Matrix Assembly**: fvVectorMatrix เป็นโครงสร้างข้อมูลที่ใช้รวบรวมสมการเชิงเส้นสำหรับการแก้ปัญหา
- **Operator Splitting**: การแยกสมการออกเป็นส่วนต่างๆ (temporal, convection, diffusion, pressure) เพื่อให้สามารถ apply numerical schemes ที่เหมาะสมกับแต่ละเทอม

### รูปแบบไร้มิติและเลขเรย์โนลด์ (Dimensionless Form and Reynolds Number)

สมการ Navier-Stokes สามารถทำให้เป็นรูปแบบไร้มิติได้ดังนี้:
$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{Re} \nabla^{*2} \mathbf{u}^* + \mathbf{f}^*$$

โดยที่ **เลขเรย์โนลด์ (Reynolds number)** $Re = \frac{\rho UL}{\mu}$ บ่งบอกถึงอัตราส่วนของแรงเฉื่อยต่อแรงหนืด

- **ที่เลขเรย์โนลด์สูง**: ผลของความหนืดจะกลายเป็นสิ่งที่ละเลยได้ ยกเว้นในชั้นขอบเขต (boundary layers) บาง ๆ ใกล้ผนัง
- **ผลลัพธ์**: นำไปสู่การก่อตัวของโครงสร้างการไหลแบบปั่นป่วน (turbulent flow structures) ซึ่งต้องการแนวทางการสร้างแบบจำลองที่เชี่ยวชาญเฉพาะด้าน

---

## 4. สมการสถานะ: ความสัมพันธ์ทางอุณหพลศาสตร์ (Equation of State: Thermodynamic Relations)

**สมการสถานะ (Equation of State - EOS)** เป็นความสัมพันธ์พื้นฐานในพลศาสตร์ของไหลที่เชื่อมโยงคุณสมบัติทางอุณหพลศาสตร์ เช่น ความดัน ความหนาแน่น และอุณหภูมิ

### กฎของแก๊สอุดมคติ (Ideal Gas Law)

สำหรับการไหลแบบอัดตัวได้ กฎของแก๊สอุดมคติจะเชื่อมโยงความดัน ($p$) ความหนาแน่น ($ho$) และอุณหภูมิ ($T$):

$$p = \rho R T$$

**โดยที่:**
- $p$ คือ ความดันสัมบูรณ์ [Pa]
- $\rho$ คือ ความหนาแน่นของของไหล [kg/m³]
- $R$ คือ ค่าคงที่เฉพาะของแก๊ส [J/(kg·K)]
- $T$ คือ อุณหภูมิสัมบูรณ์ [K]

**ข้อสมมติ:**
- ของไหลมีพฤติกรรมเป็นแก๊สอุดมคติ
- ใช้ได้กับแก๊สส่วนใหญ่ที่อุณหภูมิและความดันปกติ
- ปฏิสัมพันธ์ระหว่างโมเลกุลมีน้อยมาก

### ของไหลที่อัดตัวไม่ได้ (Incompressible Fluid)

สำหรับของเหลว เช่น น้ำ ความหนาแน่นจะยังคงที่โดยพื้นฐาน:

$$\rho = \text{คงที่ (constant)}$$

**เงื่อนไขที่ใช้ได้:**
- การเปลี่ยนแปลงความดันมีค่าน้อยเมื่อเทียบกับ Bulk Modulus
- การเปลี่ยนแปลงอุณหภูมิไม่ส่งผลกระทบต่อความหนาแน่นอย่างมีนัยสำคัญ
- **เลขมัค (Mach number) โดยปกติจะต่ำกว่า 0.3**

### การนำไปใช้งานใน OpenFOAM (OpenFOAM Code Implementation)

```cpp
// Thermodynamic model for ideal gas
// โมเดลทางอุณหพลศาสตร์สำหรับแก๊สอุดมคติ
thermoType
{
    type            hePsiThermo;          // Enthalpy-based thermodynamics
    mixture         pureMixture;          // Single-component fluid
    transport       const;                // Constant transport properties
    thermo          hConst;               // Constant specific heat
    equationOfState perfectGas;           // Implementation: p = ρRT
    specie          specie;               // Species properties
    energy          sensibleEnthalpy;     // Enthalpy formulation
}

// Thermodynamic model for incompressible fluid
// โมเดลทางอุณหพลศาสตร์สำหรับของไหลที่อัดตัวไม่ได้
thermoType
{
    type            hePsiThermo;          // Enthalpy-based thermodynamics
    mixture         pureMixture;          // Single-component fluid
    transport       const;                // Constant transport properties
    thermo          hConst;               // Constant specific heat
    equationOfState incompressible;       // Implementation: ρ = constant
    specie          specie;               // Species properties
    energy          sensibleEnthalpy;     // Enthalpy formulation
}
```

**📂 แหล่งที่มา (Source)**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:41`

**คำอธิบาย (Explanation):**
- `perfectGas` - สมการสถานะสำหรับแก๊สอุดมคติ ใช้กับปัญหา compressible flow เช่น การไหลของอากาศที่ความเร็วสูง
- `incompressible` - สมการสถานะสำหรับของไหลที่อัดตัวไม่ได้ ใช้กับของเหลวและการไหลของแก๊สที่ความเร็วต่ำ
- `hePsiThermo` - คลาสพื้นฐานสำหรับการคำนวณคุณสมบัติทางอุณหพลศาสตร์แบบ enthalpy-based

**แนวคิดสำคัญ (Key Concepts):**
- **Thermophysical Models**: OpenFOAM มีระบบ thermophysical models ที่ยืดหยุ่น (flexible) ซึ่งสามารถปรับเปลี่ยนได้ตามประเภทของปัญหา
- **Equation of State Selection**: การเลือกสมการสถานะที่เหมาะสมมีความสำคัญต่อความถูกต้องของการจำลอง
- **Transport Properties**: คุณสมบัติการขนส่งเช่นความหนืด (viscosity) และการนำความร้อน (thermal conductivity) สามารถระบุได้ทั้งแบบค่าคงที่หรือขึ้นกับอุณหภูมิ

---

## 5. เลขไร้มิติ: ตัวควบคุมระบอบการไหล (Dimensionless Numbers: Flow Regime Controllers)

เลขไร้มิติเป็นพารามิเตอร์พื้นฐานในพลศาสตร์ของไหลที่บ่งบอกถึงความสำคัญสัมพัทธ์ของปรากฏการณ์ทางฟิสิกส์ที่แข่งขันกัน

### เลขเรย์โนลด์ (Reynolds Number - $Re$)

เลขเรย์โนลด์อาจกล่าวได้ว่าเป็นพารามิเตอร์ไร้มิติที่สำคัญที่สุดในกลศาสตร์ของไหล:

$$Re = \frac{\rho U L}{\mu} = \frac{\text{แรงเฉื่อย (Inertial Forces)}}{\text{แรงหนืด (Viscous Forces)}}$$

**การจำแนกระบอบการไหล (Flow Regime Classification):**

| เลขเรย์โนลด์ | ระบอบการไหล | ลักษณะการไหล |
|-----------------|--------------|----------------------|
| $Re < 2300$ | การไหลแบบราบเรียบ (Laminar) | การไหลที่ราบรื่น เป็นชั้น ๆ ไม่มีการผสมกัน |
| $2300 < Re < 4000$ | การไหลช่วงเปลี่ยนผ่าน (Transitional) | การเปลี่ยนผ่านจากการไหลแบบราบเรียบไปสู่ความปั่นป่วน |
| $Re > 4000$ | การไหลแบบปั่นป่วน (Turbulent) | การไหลที่วุ่นวาย มีการผสมกันและการผันผวน |

### เลขมัค (Mach Number - $Ma$)

เลขมัคแสดงถึงอัตราส่วนของความเร็วการไหลต่อความเร็วเสียงในบริเวณนั้น:

$$Ma = \frac{U}{c} = \frac{\text{ความเร็วการไหล (Flow Velocity)}}{\text{ความเร็วเสียง (Speed of Sound)}}$$

**ระบอบการไหลตามเลขมัค (Mach Number Flow Regimes):**

| เลขมัค | ระบอบการไหล | ผลของการอัดตัวได้ |
|-------------|-------------|------------------------|
| $Ma < 0.3$ | อัดตัวไม่ได้ (Incompressible) | การเปลี่ยนแปลงความหนาแน่นน้อยมากจนละเลยได้ |
| $0.3 < Ma < 0.8$ | ต่ำกว่าเสียง (Subsonic Compressible) | มีผลของการอัดตัวได้เล็กน้อย |
| $Ma = 1$ | ความเร็วเสียง (Sonic) | สภาวะวิกฤต การไหลที่ความเร็วเสียง |
| $0.8 < Ma < 1.2$ | ช่วงความเร็วเสียง (Transonic) | มีบริเวณที่ความเร็วต่ำกว่าและเหนือกว่าเสียงผสมกัน |
| $Ma > 1.2$ | เหนือเสียง (Supersonic) | การไหลเร็วกว่าเสียง มีการก่อตัวของคลื่นกระแทก |

### การเลือก Solver ใน OpenFOAM (OpenFOAM Solver Selection)

OpenFOAM มี solver ที่เชี่ยวชาญเฉพาะด้านสำหรับระบอบเลขมัคที่แตกต่างกัน:

```cpp
// Low Mach number (Ma < 0.3) - incompressible solvers
solver simpleFoam;        // Steady-state incompressible
solver pimpleFoam;        // Transient incompressible
solver icoFoam;          // Laminar transient incompressible

// Compressible flow solvers (Ma > 0.3)
solver rhoSimpleFoam;     // Steady compressible
solver rhoPimpleFoam;     // Transient compressible
solver sonicFoam;        // Transonic/supersonic flow
```

---

## 6. ไวยากรณ์ของ OpenFOAM: การแปลสัญลักษณ์ทางคณิตศาสตร์ (OpenFOAM Syntax: Translating Mathematical Notation)

**ไวยากรณ์ของ OpenFOAM (OpenFOAM syntax)** ถูกออกแบบมาโดยเฉพาะให้สะท้อนถึงสัญลักษณ์เวกเตอร์ (vector notation) ที่ใช้ในสมการพลศาสตร์ของไหลอย่างใกล้ชิด

### การแมปตัวดำเนินการทางคณิตศาสตร์กับฟังก์ชันของ OpenFOAM

ฟังก์ชันไฟไนต์วอลุ่ม (FVM) ใน OpenFOAM สอดคล้องโดยตรงกับตัวดำเนินการทางคณิตศาสตร์:

| ฟังก์ชันของ OpenFOAM | ตัวดำเนินการทางคณิตศาสตร์ | ความหมาย |
|------------------|---------------------|---------|
| `fvm::div(phi, U)` | $\nabla \cdot (\phi \mathbf{U})$ | ตัวดำเนินการไดเวอร์เจนซ์ (Divergence operator) |
| `fvm::laplacian(DT, T)` | $\nabla \cdot (DT \nabla T)$ | ตัวดำเนินการลาพลาเซียน (Laplacian operator) |
| `fvm::ddt(rho, U)` | $\frac{\partial (\rho \mathbf{U})}{\partial t}$ | อนุพันธ์เชิงเวลา (Temporal derivative) |
| `fvc::grad(p)` | $\nabla p$ | เกรเดียนต์ความดัน (Pressure gradient) |

ความสอดคล้องโดยตรงระหว่างสัญลักษณ์ทางคณิตศาสตร์และการนำไปใช้ในโค้ดช่วยลดภาระทางความคิด (cognitive load) ได้อย่างมากเมื่อต้องแปลสมการไปเป็นแอปพลิเคชันใน OpenFOAM

### ระบบประเภทฟิลด์ของ OpenFOAM (OpenFOAM Field Type System)

OpenFOAM ใช้ระบบเทมเพลต (template system) ที่ซับซ้อนสำหรับประเภทฟิลด์ซึ่งช่วยรักษาความสอดคล้องทางคณิตศาสตร์ทั่วทั้งชุดโค้ด:

#### ฟิลด์ทางเรขาคณิต (Geometric Fields)
- `volScalarField` - ปริมาณสเกลาร์ที่จุดศูนย์กลางเซลล์ (cell centers)
- `volVectorField` - ปริมาณเวกเตอร์ที่จุดศูนย์กลางเซลล์
- `volTensorField` - ปริมาณเทนเซอร์ที่จุดศูนย์กลางเซลล์

#### ฟิลด์ที่ผิว (Surface Fields)
- `surfaceScalarField` - ปริมาณสเกลาร์ที่ผิวของเซลล์ (cell faces)
- `surfaceVectorField` - ปริมาณเวกเตอร์ที่ผิวของเซลล์

#### คุณสมบัติเฉพาะทาง (Specialized Features)
- **ชุดมิติ (Dimensional Sets)**: การวิเคราะห์มิติและการตรวจสอบหน่วยโดยอัตโนมัติ
- **รูปแบบการประมาณค่า (Interpolation Schemes)**: Linear, upwind, central differencing และรูปแบบอันดับสูงอื่น ๆ

---

## 7. เงื่อนไขขอบเขต: สิ่งจำเป็นสำหรับผลเฉลยทางกายภาพ (Boundary Conditions: Essential for Physical Solutions)

**เงื่อนไขขอบเขต (boundary conditions)** มีความสำคัญอย่างยิ่งในการได้รับผลเฉลยที่เป็นเอกลักษณ์และถูกต้องตามหลักฟิสิกส์สำหรับปัญหา CFD

เนื่องจากสมการควบคุมเองนั้นยอมให้มีผลเฉลยจำนวนมหาศาลหากไม่มีข้อจำกัดที่เหมาะสม ในวิธีไฟไนต์วอลุ่ม เงื่อนไขขอบเขตจะต้องถูกกำหนดสำหรับตัวแปรทั้งหมดที่ขอบเขตโดเมนทั้งหมด

### ประเภทของเงื่อนไขขอบเขตใน OpenFOAM (Boundary Condition Types in OpenFOAM)

| ประเภท | ตัวอย่างใน OpenFOAM | การใช้งาน |
|------|------------------|-------|
| **เงื่อนไขดิริชเลต์ (Dirichlet conditions)** | `fixedValue` | ระบุค่าที่แน่นอนที่ขอบเขต |
| **เงื่อนไขนอยมันน์ (Neumann conditions)** | `fixedGradient` | ระบุเกรเดียนต์ (zero-gradient สำหรับการไหลที่พัฒนาเต็มที่) |
| **เงื่อนไขผสม (Mixed conditions)** | `mixed` | รวมการระบุค่าและเกรเดียนต์เข้าด้วยกัน |
| **ฟังก์ชันผนัง (Wall functions)** | ต่าง ๆ | การจัดการเฉพาะสำหรับการสร้างแบบจำลองความปั่นป่วนใกล้ผนัง |
| **เงื่อนไขขอบเขตเปิด (Open boundary conditions)** | `inletOutlet`, `outletInlet` | อนุญาตให้มีการไหลย้อนกลับและระบุเงื่อนไขตามทิศทางการไหลในบริเวณนั้น |

### ตัวอย่างเงื่อนไขขอบเขตใน OpenFOAM (OpenFOAM Boundary Condition Examples)

```cpp
// Example: Velocity inlet with turbulent profile
// ตัวอย่าง: ทางเข้าความเร็วที่มีโปรไฟล์แบบ turbulent
inlet
{
    type            fixedValue;
    value           uniform (10 0 0);  // m/s uniform velocity
                                      // ความเร็วคงที่ 10 m/s ในทิศทาง x
}

// Example: Pressure outlet with backflow prevention
// ตัวอย่าง: ทางออกความดันแบบ developed flow
outlet
{
    type            zeroGradient;      // Natural development
                                      // Gradient เป็นศูนย์ (fully developed)
}

// Example: No-slip wall
// ตัวอย่าง: ผนังแบบ no-slip
walls
{
    type            fixedValue;        // Fixed at zero for no-slip
    value           uniform (0 0 0);   // Zero velocity at wall
                                      // ความเร็วเป็นศูนย์ที่ผนัง
}

// Example: Symmetry plane
// ตัวอย่าง: ระนาบสมมาตร
symmetryPlane
{
    type            symmetry;          // Symmetry condition
                                      // เงื่อนไขสมมาตรที่ระนาบ
}
```

**📂 แหล่งที่มา (Source)**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:39`

**คำอธิบาย (Explanation):**
- `fixedValue` - กำหนดค่าคงที่ที่ boundary ใช้กับ inlet velocity หรือ wall temperature
- `zeroGradient` - gradient เป็นศูนย์ในทิศทางปกติของ boundary ใช้กับ outlet pressure หรือ developed flow
- `symmetry` - เงื่อนไขสมมาตรที่ไม่มี flux ผ่านระนาบ ใช้เพื่อลดขนาดโดเมนการคำนวณ

**แนวคิดสำคัญ (Key Concepts):**
- **Well-Posed Problems**: การกำหนด boundary conditions ที่เหมาะสมจำเป็นสำหรับปัญหาทางคณิตศาสตร์ที่สมบูรณ์ (well-posed mathematical problem)
- **Physical Realism**: boundary conditions ต้องสอดคล้องกับสภาพทางกายภาพจริงของปัญหา
- **Numerical Stability**: boundary conditions ที่ไม่เหมาะสมอาจทำให้เกิดความไม่เสถียรเชิงตัวเลข (numerical instability)

### ความสามารถของเงื่อนไขขอบเขตขั้นสูง (Advanced Boundary Condition Capabilities)

OpenFOAM มีความสามารถด้านเงื่อนไขขอบเขตที่ซับซ้อนซึ่งขยายไปไกลกว่าการระบุค่าและเกรเดียนต์พื้นฐาน:

- **เงื่อนไขที่เปลี่ยนตามเวลา (Time-varying conditions)**: `uniformFixedValue` พร้อมฟังก์ชันที่ขึ้นกับเวลา
- **ขอบเขตที่เชื่อมโยงกัน (Coupled boundaries)**: `thermalBaffle` สำหรับการถ่ายเทความร้อนแบบคอนจูเกต (conjugate heat transfer)
- **เงื่อนไขแบบวัฏจักร (Cyclic conditions)**: `cyclicAMI` สำหรับส่วนต่อประสานเครื่องจักรที่หมุนได้
- **ขอบเขตบรรยากาศ (Atmospheric boundaries)**: `atmBoundaryLayerInlet` สำหรับการสร้างแบบจำลองชั้นขอบเขตบรรยากาศ
- **การสร้างคลื่น (Wave generation)**: `waveAlpha` และ `waveSurfaceHeight` สำหรับการประยุกต์ใช้วิศวกรรมทางทะเล

---

## 8. เงื่อนไขเริ่มต้น: รากฐานของความเสถียรเชิงตัวเลข (Initial Conditions: Foundation of Numerical Stability)

การจำลองต้องเริ่มต้นจากจุดใดจุดหนึ่ง **เงื่อนไขเริ่มต้น (Initial Conditions)** (ในไดเรกทอรี `0/`) จะกำหนดสถานะที่เวลา $t=0$ เงื่อนไขเหล่านี้มีความสำคัญอย่างยิ่งต่อ **ความเสถียรเชิงตัวเลข (Numerical Stability)** และ **การลู่เข้า (Convergence)** ของการจำลอง CFD

### การกำหนดค่าเริ่มต้นของสนามความเร็ว (Velocity Field Initialization)

```cpp
// Velocity field initialization for OpenFOAM simulation
// การกำหนดค่าเริ่มต้นของฟิลด์ความเร็วใน OpenFOAM
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // m/s: Length/Time
internalField   uniform (0 0 0);   // Initial velocity field (zero)

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0); // Uniform inlet velocity 10 m/s
                                         // ความเร็วคงที่ 10 m/s ที่ทางเข้า
    }
    outlet
    {
        type            zeroGradient;     // Fully developed flow
                                         // Gradient เป็นศูนย์ที่ทางออก
    }
    walls
    {
        type            noSlip;           // No-slip condition
                                         // เงื่อนไขไม่มีการลื่นไถลที่ผนัง
    }
}
```

**📂 แหล่งที่มา (Source)**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:42`

**คำอธิบาย (Explanation):**
- `dimensions` - กำหนดหน่วยของปริมาณในระบบ [M L T K Mole A Cd]
- `internalField` - ค่าเริ่มต้นของฟิลด์ภายในโดเมน (สามารถเป็น uniform หรือ non-uniform)
- `boundaryField` - กำหนด boundary conditions สำหรับแต่ละ boundary patch
- `noSlip` - เงื่อนไข no-slip ซึ่งเป็นการรวมกันของ fixedValue (0 0 0) กับ zeroGradient

**แนวคิดสำคัญ (Key Concepts):**
- **Dimensional Consistency**: ระบบ dimensions ใน OpenFOAM ช่วยตรวจสอบความถูกต้องของหน่วย
- **Patch-based Definition**: boundary conditions ถูกกำหนดต่อ patch ซึ่งเป็นกลุ่มของ faces ที่มีเงื่อนไขเหมือนกัน
- **Field Initialization**: ค่าเริ่มต้นที่ดีช่วยให้การแก้ปัญหาลู่เข้า (converge) ได้เร็วขึ้น

### การกำหนดค่าเริ่มต้นของสนามความดัน (Pressure Field Initialization)

```cpp
// Pressure field initialization for incompressible flow
// การกำหนดค่าเริ่มต้นของฟิลด์ความดันสำหรับการไหลแบบอัดตัวไม่ได้
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];  // Pa: kg/(m·s²)
internalField   uniform 101325;    // Reference atmospheric pressure
                                    // ความดันบรรยากาศอ้างอิง

boundaryField
{
    inlet
    {
        type            zeroGradient; // Zero gradient at inlet
                                    // เกรเดียนต์เป็นศูนย์ที่ทางเข้า
    }
    outlet
    {
        type            fixedValue;
        value           uniform 101325; // Gauge pressure = 0
                                        // ความดันเกจ = 0 (ค่าอ้างอิงสัมพัทธ์)
    }
    walls
    {
        type            zeroGradient; // Zero gradient at walls
                                    // เกรเดียนต์เป็นศูนย์ที่ผนัง
    }
}
```

**📂 แหล่งที่มา (Source)**: `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:42`

**คำอธิบาย (Explanation):**
- `volScalarField` - ฟิลด์สเกลาร์ที่จัดเก็บค่าที่จุดศูนย์กลางเซลล์ในเมช (mesh)
- Pressure reference - สำหรับการไหลแบบอัดตัวไม่ได้ ความดันจะถูกกำหนดเป็นค่าสัมพัทธ์ (relative) ไม่ใช่ค่าสัมบูรณ์
- Boundary condition consistency - ทางเข้าและทางออกมีเงื่อนไขที่แตกต่างกันเพื่อให้เกิดเกรเดียนต์ความดันที่ขับเคลื่อนการไหล

**แนวคิดสำคัญ (Key Concepts):**
- **Reference Pressure**: ในการไหลแบบอัดตัวไม่ได้ มีเพียงเกรเดียนต์ความดันเท่านั้นที่มีผลต่อการไหล ดังนั้นจึงต้องมีจุดอ้างอิงหนึ่งจุด
- **Pressure-Velocity Coupling**: เงื่อนไขขอบเขตของความดันและความเร็วต้องสอดคล้องกันเพื่อให้สอดคล้องกับสมการความต่อเนื่อง
- **Gauge vs Absolute Pressure**: การใช้ความดันเกจ (เทียบกับค่าอ้างอิง) ช่วยลดปัญหาความคลาดเคลื่อนเชิงตัวเลขจากค่าที่มีขนาดใหญ่

### แนวปฏิบัติที่ดีที่สุดสำหรับเงื่อนไขเริ่มต้น (Best Practices for Initial Conditions)

1. **ความสอดคล้องทางฟิสิกส์ (Physical Consistency)**: ตรวจสอบให้แน่ใจว่าเงื่อนไขเริ่มต้นเป็นไปตามกฎการอนุรักษ์พื้นฐาน
2. **ความเสถียรเชิงตัวเลข (Numerical Stability)**: หลีกเลี่ยง **ความไม่ต่อเนื่อง (discontinuities)** ที่อาจทำให้เกิดความไม่เสถียรเชิงตัวเลข
3. **การเร่งการลู่เข้า (Convergence Acceleration)**: สำหรับ **ปัญหาในสภาวะคงตัว (steady-state problems)** ให้ใช้กลยุทธ์การกำหนดค่าเริ่มต้นที่ส่งเสริมการลู่เข้าอย่างรวดเร็ว
4. **ความสามารถในการเริ่มใหม่ (Restart Capabilities)**: จัดโครงสร้างเงื่อนไขเริ่มต้นเพื่ออำนวยความสะดวกในการ **เริ่มจำลองใหม่ (simulation restarts)**

---

## สรุปประเด็นสำคัญ (Summary of Key Points)

### หลักการพื้นฐานที่ควรจำ (Fundamental Principles to Remember)

1. **กฎการอนุรักษ์ (Conservation Laws)** - รากฐานของ CFD ทั้งหมด:
   - การอนุรักษ์มวล → สมการความต่อเนื่อง
   - การอนุรักษ์โมเมนตัม → สมการ Navier-Stokes
   - การอนุรักษ์พลังงาน → สมการพลังงาน

2. **สมการการขนส่งทั่วไป (General Transport Equation)**:
   $$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

3. **วิธีไฟไนต์วอลุ่ม (Finite Volume Method)** ใช้ทฤษฎีบทการลู่ออกของเกาส์:
   $$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_S \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

### เลขไร้มิติที่สำคัญ (Important Dimensionless Numbers)

| เลขไร้มิติ | สูตร | ความสำคัญ |
|---------------------|---------|--------------|
| เรย์โนลด์ ($Re$) | $\frac{\rho U L}{\mu}$ | ทำนายระบอบการไหล (ราบเรียบ/ปั่นป่วน) |
| มัค ($Ma$) | $\frac{U}{c}$ | กำหนดผลของการอัดตัวได้ |
| ฟรูด ($Fr$) | $\frac{U}{\sqrt{gL}}$ | สำคัญสำหรับการไหลที่มีผิวอิสระ (free surface) |

### การแมปไวยากรณ์ของ OpenFOAM (OpenFOAM Syntax Mapping)

```cpp
fvm::ddt(rho, U)         // ∂(ρU)/∂t
fvm::div(phi, U)         // ∇·(ρUU)
fvm::laplacian(mu, U)    // ∇·(μ∇U)
fvc::grad(p)             // ∇p
```

### อัลกอริทึมการเชื่อมโยงความดันและความเร็ว (Pressure-Velocity Coupling Algorithms)

- **SIMPLE**: Semi-Implicit Method for Pressure-Linked Equations (สภาวะคงตัว)
- **PISO**: Pressure-Implicit with Splitting of Operators (สภาวะไม่คงตัว)
- **PIMPLE**: การรวมกันของ SIMPLE และ PISO (ไฮบริด)

### เงื่อนไขขอบเขตที่จำเป็น (Essential Boundary Conditions)

- **ดิริชเลต์ (Dirichlet)**: `fixedValue` - ระบุค่าที่แน่นอน
- **นอยมันน์ (Neumann)**: `zeroGradient` - ระบุเกรเดียนต์เป็นศูนย์
- **ผนัง (Wall)**: `noSlip` - ความเร็วเป็นศูนย์ที่ผนัง
- **สมมาตร (Symmetry)**: `symmetry` - ระนาบสมมาตร

---

> **[!TIP]** ความเข้าใจอย่างลึกซึ้งในประเด็นสำคัญเหล่านี้เป็นสิ่งจำเป็นสำหรับการจำลอง CFD ที่ประสบความสำเร็จด้วย OpenFOAM เนื่องจากทุกอย่างใน CFD ตั้งแต่การสร้างเมชไปจนถึงการแปลความหมายของผลลัพธ์นั้นมีรากฐานมาจากหลักการพื้นฐานเหล่านี้
