# 01 วิธีการตรวจสอบความถูกต้องทางกายภาพ (Physical Validation Methods)

การตรวจสอบความถูกต้องทางกายภาพ (Physical Validation) คือกระบวนการยืนยันว่าแบบจำลอง CFD ของเราให้ผลลัพธ์ที่ตรงกับความเป็นจริงทางฟิสิกส์ ซึ่งแตกต่างจาก **Verification** ที่เน้นตรวจสอบความถูกต้องทางคณิตศาสตร์ของการแก้สมการ ในขณะที่ **Validation** เน้นตรวจสอบว่าแบบจำลองสะท้อนพฤติกรรมทางฟิสิกส์ที่แท้จริงหรือไม่

## 1.1 การเปรียบเทียบกับผลเฉลยเชิงวิเคราะห์ (Analytical Solutions)

สำหรับปัญหาพื้นฐานที่มีสูตรคณิตศาสตร์รองรับ เราสามารถใช้สูตรเหล่านั้นเป็นบรรทัดฐาน (Benchmark) เพื่อยืนยันความถูกต้องของ Solver และการตั้งค่า Numerical Schemes

### ตัวอย่างที่ 1: การนำความร้อน 1 มิติ (1D Steady-State Heat Conduction)

**สมการควบคุม (Governing Equation):**
$$\frac{d}{dx}\left(k \frac{dT}{dx}\right) = 0$$

สำหรับค่าความนำความร้อนคงที่ ($k = \text{const}$):
$$\frac{d^2T}{dx^2} = 0$$

**เงื่อนไขขอบเขต:**
$$T(0) = T_0, \quad T(L) = T_L$$

**ผลเฉลยเชิงวิเคราะห์:**
$$T(x) = T_0 + (T_L - T_0)\frac{x}{L}$$

**การตั้งค่า OpenFOAM (ด้วย laplacianFoam):**

`0/T`:
```cpp
// Temperature field boundary conditions
// Source: Derived from laplacianFoam tutorial cases
// Key Concepts: fixedValue BC for Dirichlet conditions, zeroGradient for adiabatic walls

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 350;  // T_0 = 350 K (Dirichlet BC)
    }
    outlet
    {
        type            fixedValue;
        value           uniform 300;  // T_L = 300 K (Dirichlet BC)
    }
    walls
    {
        type            zeroGradient; // Adiabatic wall (no heat flux)
    }
}
```

**คำอธิบาย:**
- **Source:** ไฟล์การตั้งค่าเงื่อนไขขอบเขตสำหรับปัญหาการนำความร้อน พัฒนาจาก tutorial cases ของ laplacianFoam
- **Explanation:** การตั้งค่าเงื่อนไขขอบเขตชนิด Dirichlet (fixedValue) ที่ inlet และ outlet เพื่อกำหนดอุณหภูมิคงที่ ส่วน walls ใช้ zeroGradient เพื่อจำลองผนังที่ไม่มีการถ่ายเทความร้อน (adiabatic)
- **Key Concepts:** 
  - `fixedValue`: กำหนดค่าคงที่ที่ขอบเขต (Dirichlet boundary condition)
  - `zeroGradient`: อนุพันธ์เป็นศูนย์ ใช้สำหรับผนังแบบ adiabatic
  - `dimensions`: มิติของอุณหภูมิ [θ] ในระบบหน่วย SI

`system/fvSchemes`:
```cpp
// Numerical schemes for steady-state heat conduction
// Source: Standard OpenFOAM discretization schemes
// Key Concepts: Steady-state time scheme, Gaussian interpolation for gradients

ddtSchemes
{
    default         steadyState; // No time derivative for steady-state problems
}

gradSchemes
{
    default         Gauss linear; // Central differencing for gradient calculation
}

divSchemes
{
    default         none; // No divergence terms in Laplace equation
}

laplacianSchemes
{
    default         Gauss linear corrected; // Second-order accurate Laplacian with non-orthogonal correction
}
```

**คำอธิบาย:**
- **Source:** ไฟล์การตั้งค่ารูปแบบการคำนวณเชิงตัวเลข (Numerical Schemes) สำหรับปัญหาสถานะคงที่
- **Explanation:** การเลือกใช้รูปแบบการกระจายความคิด (discretization schemes) ที่เหมาะสมกับสมการ Laplace: steadyState สำหรับไม่มีอนุพันธ์เชิงเวลา, Gauss linear สำหรับการคำนวณ gradient และ corrected สำหรับแก้ไขผลจากเมชที่ไม่ตั้งฉาก
- **Key Concepts:**
  - `steadyState`: ละเว้นเทอมอนุพันธ์เชิงเวลา ∂/∂t
  - `Gauss linear`: การใช้ Gaussian integration กับ interpolation แบบเส้นตรง (central differencing)
  - `corrected`: แก้ไขความคลาดเคลื่อนจาก non-orthogonal mesh

### ตัวอย่างที่ 2: การไหลแบบ Poiseuille ในท่อ (Laminar Pipe Flow)

**การไหลชั้นน้ำ (Laminar Flow) ในท่อรูปทรงกระบอกที่ขับเคลื่อนด้วยความดัน:**

**สมการ Navier-Stokes แบบย่อรูป (Reduced Form):**
$$-\frac{dp}{dx} + \mu \frac{1}{r}\frac{d}{dr}\left(r \frac{du}{dr}\right) = 0$$

**ผลเฉลยเชิงวิเคราะห์สำหรับโพรไฟล์ความเร็ว:**
$$u(r) = u_{max}\left(1 - \frac{r^2}{R^2}\right)$$

โดยที่ความเร็วสูงสุด:
$$u_{max} = -\frac{R^2}{4\mu} \frac{dp}{dx}$$

และอัตราการไหลเฉลี่ย (Average Velocity):
$$\bar{u} = \frac{u_{max}}{2}$$

**เงื่อนไขที่จำเป็น:**
- **Reynolds Number**: $Re = \frac{\rho \bar{u} D}{\mu} < 2300$ (Laminar flow criteria)
- **Fully Developed Flow**: $L/D > 0.06 \times Re$ (Entry length)

**การตั้งค่า OpenFOAM (ด้วย simpleFoam สำหรับ steady-state):**

`0/U`:
```cpp
// Velocity field boundary conditions for laminar pipe flow
// Source: Derived from simpleFoam incompressible flow solver
// Key Concepts: fixedValue inlet, zeroGradient outlet, no-slip walls

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (0.1 0 0);  // Uniform inlet velocity (m/s)
    }
    outlet
    {
        type            zeroGradient;       // Fully developed flow condition
    }
    walls
    {
        type            noSlip;             // Zero velocity at wall (u = 0)
    }
}
```

**คำอธิบาย:**
- **Source:** ไฟล์เงื่อนไขขอบเขตสำหรับสนามความเร็วในการไหลแบบชั้นน้ำในท่อ อ้างอิงจาก simpleFoam solver
- **Explanation:** การตั้งค่าเงื่อนไขขอบเขตที่สอดคล้องกับการไหลแบบ fully developed: inlet กำหนดความเร็วคงที่, outlet ใช้ zeroGradient เพื่อให้ความเร็วไม่เปลี่ยนตามระยะทาง, และ walls ใช้ noSlip เพื่อกำหนดความเร็วศูนย์ที่ผนัง
- **Key Concepts:**
  - `fixedValue`: กำหนดความเร็วคงที่ที่ inlet
  - `zeroGradient`: ความเร็วไม่เปลี่ยนแปลงในทิศทางการไหล (fully developed condition)
  - `noSlip`: เงื่อนไขไม่มีการลื่นไถลที่ผนัง (u_wall = 0)

`0/p`:
```cpp
// Pressure field boundary conditions for incompressible flow
// Source: Standard OpenFOAM pressure BC for SIMPLE algorithm
// Key Concepts: Fixed reference pressure, zeroGradient at inlet

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            zeroGradient;  // Pressure gradient not specified at inlet
    }
    outlet
    {
        type            fixedValue;
        value           uniform 0;     // Reference pressure (gauge pressure = 0)
    }
    walls
    {
        type            zeroGradient;  // Normal pressure gradient = 0 at wall
    }
}
```

**คำอธิบาย:**
- **Source:** ไฟล์เงื่อนไขขอบเขตความดันสำหรับการไหลแบบไม่ยุบตัวได้ ใช้กับอัลกอริทึม SIMPLE
- **Explanation:** การตั้งค่าความดันอ้างอิง (reference pressure) ที่ outlet เป็นศูนย์ และใช้ zeroGradient ที่ inlet และ walls เพื่อให้สมการความดันสอดคล้องกับสมการความต่อเนื่อง
- **Key Concepts:**
  - `fixedValue uniform 0`: กำหนดความดันอ้างอิง (gauge pressure) ที่ outlet
  - `zeroGradient`: อนุพันธ์ปกติของความดันเป็นศูนย์
  - การใช้ gauge pressure แทน absolute pressure ในการคำนวณ

`constant/transportProperties`:
```cpp
// Fluid transport properties for laminar flow
// Source: OpenFOAM transport model definitions
// Key Concepts: Newtonian fluid model, kinematic viscosity specification

transportModel  Newtonian;

nu              nu [0 2 -1 0 0 0 0] 1e-06;  // Kinematic viscosity (m²/s)
```

**คำอธิบาย:**
- **Source:** ไฟล์คุณสมบัติการขนส่งของของไหล (Transport Properties) สำหรับของไหลแบบนิวตัน
- **Explanation:** การกำหนดชนิดของของไหลเป็นแบบนิวตัน (Newtonian) ซึ่งมีความหนืดคงที่ไม่ขึ้นกับอัตราการเฉือน และระบุค่าความหนืดจลน์ (kinematic viscosity) ในหน่วย SI
- **Key Concepts:**
  - `Newtonian`: แบบจำลองของไหลนิวตันที่มีความสัมพันธ์เชิงเส้นระหว่างความเค้นและอัตราการเฉือน
  - `nu`: ความหนืดจลน์ (kinematic viscosity = μ/ρ) มีหน่วย [L²/T]
  - หน่วย [0 2 -1 0 0 0 0] แทน m²/s ในระบบหน่วย SI

### วิธีการเปรียบเทียบผลลัพธ์:

1. **Plot Comparison**: พล็อตโพรไฟล์ความเร็ว $u(r)$ จาก CFD เทียบกับสมการเชิงวิเคราะห์
2. **Error Metrics**: คำนวณค่าความคลาดเคลื่อน:

$$L_2 \text{ Error} = \sqrt{\frac{\sum_{i=1}^{N} (u_{CFD,i} - u_{analytical,i})^2}{\sum_{i=1}^{N} u_{analytical,i}^2}}$$

> **[MISSING DATA]**: Insert specific simulation results/graphs for this section showing velocity profile comparison.

---

## 1.2 การตรวจสอบด้วยข้อมูลการทดลอง (Experimental Validation)

เมื่อปัญหาซับซ้อนเกินกว่าจะมีสูตรเชิงวิเคราะห์ (เช่น การไหลแบบ Turbulent, การไหลผ่านวัตถุทรงกลม) เราต้องใช้ข้อมูลจากการทดลองในห้องปฏิบัติการเพื่อเปรียบเทียบ

### หลักการของความเป็นเลิศทางมิติ (Dimensional Similarity)

เพื่อให้การเปรียบเทียบมีความถูกต้อง จำเป็นต้องมั่นใจว่า Dimensionless Parameters สำคัญตรงกัน:

**Reynolds Number Matching:**
$$Re = \frac{\rho U L}{\mu} = \frac{U L}{\nu}$$

เมื่อ:
- $\rho$ = ความหนาแน่นของของไหล (kg/m³)
- $U$ = ความเร็วลักษณะ (Characteristic Velocity) (m/s)
- $L$ = ความยาวลักษณะ (Characteristic Length) (m)
- $\mu$ = ความหนืดพลึง (Dynamic Viscosity) (Pa·s)
- $\nu$ = ความหนืดจลน์ (Kinematic Viscosity) (m²/s)

**เงื่อนไขอื่นที่อาจต้องพิจารณา:**
- **Mach Number**: $Ma = U/c$ (สำหรับการไหลที่บีบอัดได้)
- **Strouhal Number**: $St = fL/U$ (สำหรับการไหลที่ไม่เสถียร/Periodic)
- **Froude Number**: $Fr = U/\sqrt{gL}$ (สำหรับการไหลที่มีผลจากแรงโน้มถ่วง/Free Surface)

### ข้อควรพิจารณาสำคัญ:

1. **Reynolds Number Matching**: ต้องแน่ใจว่าการจำลองมีค่า $Re$ ตรงกับการทดลอง
   - ถ้าใช้ของไหลต่างกัน ต้องปรับความเร็ว $U$ หรือขนาด $L$ ให้ได้ $Re$ ตรงกัน

2. **Boundary Conditions**: พยายามจำลองเงื่อนไขขอบเขตให้เหมือนกับการตั้งค่าการทดลองมากที่สุด
   - **Inlet Turbulence Intensity**: $I = \frac{u'_{rms}}{U_{mean}} \times 100\%$
   - **Hydraulic Diameter**: สำหรับการคำนวณค่า $Re$ ในช่องทางที่ไม่ใช่รูปทรงกระบอก

3. **Measurement Uncertainty**: ต้องตระหนักว่าข้อมูลการทดลองก็มีความคลาดเคลื่อน (Error Bar)
   - ผลลัพธ์ CFD ไม่จำเป็นต้องตรงเป๊ะ 100% แต่ควรอยู่ในช่วงความเชื่อมั่น (Confidence Interval)

### การใช้งาน Probes ใน OpenFOAM:

สำหรับการเปรียบเทียบค่าที่ตำแหน่งเฉพาะ (Point-wise comparison):

`system/probes` (function object):
```cpp
// Point probes for monitoring field values at specific locations
// Source: OpenFOAM sampling function objects library
// Key Concepts: Point-wise monitoring, multi-field output

probes
{
    type            probes;
    functionObjectLibs ("libsampling.so");

    writeControl    timeStep;
    writeInterval   1;

    probeLocations
    (
        (0.05 0.0 0.0)    // Probe 1: x=5cm, centerline
        (0.05 0.01 0.0)   // Probe 2: x=5cm, y=1cm
        (0.05 0.02 0.0)   // Probe 3: x=5cm, y=2cm
    );

    fields
    (
        U               // Velocity field
        p               // Pressure field
    );
}
```

**คำอธิบาย:**
- **Source:** ไฟล์การตั้งค่า function object สำหรับการตรวจสอบค่าสนามที่ตำแหน่งจุดเฉพาะ อ้างอิงจาก libsampling.so library
- **Explanation:** การสร้าง probes เพื่อบันทึกค่าตัวแปร (เช่น ความเร็วและความดัน) ตามเวลาที่ตำแหน่งที่กำหนด ซึ่งมีประโยชน์สำหรับการเปรียบเทียบกับข้อมูลการทดลองที่วัดที่จุดต่างๆ
- **Key Concepts:**
  - `probeLocations`: พิกัด (x, y, z) ของจุดที่ต้องการตรวจสอบ
  - `functionObjectLibs`: Library ที่ใช้ในการประมวลผล
  - `writeControl/writeInterval`: ความถี่ในการบันทึกข้อมูล
  - สามารถเฝ้าสังเกตหลายฟิลด์พร้อมกัน (U, p, T, ฯลฯ)

หรือใช้งานผ่าน `system/controlDict`:
```cpp
// Line sampling for profile extraction along a path
// Source: OpenFOAM sets sampling function object
// Key Concepts: Uniform sampling, line integration, field interpolation

functions
{
    probeLines
    {
        type            sets;
        functionObjectLibs ("libsampling.so");
        writeControl    timeStep;
        writeInterval   1;

        setFormat       raw;           // Output format: raw, csv, vtk

        sets
        (
            centerline
            {
                type            uniform;    // Uniform point distribution
                axis            distance;   // Sample along distance
                start           (0 0 0);    // Start point
                end             (0.1 0 0);  // End point
                nPoints         100;        // Number of sampling points
            }
        );

        fields
        (
            U               // Velocity magnitude and components
            p               // Pressure field
        );
    }
}
```

**คำอธิบาย:**
- **Source:** ไฟล์การตั้งค่า function object สำหรับการสุ่มตัวอย่างข้อมูลตามเส้นทาง (Line sampling) ใน controlDict
- **Explanation:** การสร้างเส้นทางการสุ่มตัวอย่างเพื่อดึงโพรไฟล์ของตัวแปรตามระยะทาง ซึ่งเหมาะสำหรับการเปรียบเทียบโพรไฟล์ความเร็วหรือความดัน
- **Key Concepts:**
  - `type sets`: การสุ่มตัวอย่างตามเซตของจุดหรือเส้น
  - `uniform`: การกระจายจุดสุ่มตัวอย่างแบบสม่ำเสมอ
  - `axis distance`: การสุ่มตามระยะทางจากจุดเริ่มต้น
  - `nPoints`: จำนวนจุดที่ใช้ในการสุ่มตัวอย่าง

### ตัวอย่างเทคนิคการตรวจสอบ:

1. **PIV (Particle Image Velocimetry) Comparison**: การเปรียบเทียบสนามความเร็ว (Velocity Field)
   - Export ข้อมูลจาก OpenFOAM เป็น CSV หรือ VTK
   - เปรียบเทียบ Vector field ทั้ง 2 มิติหรือ 3 มิติ

2. **Point-wise comparison**: การเปรียบเทียบค่าความดันหรืออุณหภูมิที่ตำแหน่งเฉพาะ (Probes)
   - ใช้ `probes` function object ใน OpenFOAM
   - Plot ค่าตามเวลา (Time history)

3. **Integral Quantities**: การเปรียบเทียบปริมาณรวม
   - แรงลาก (Drag Force): $F_D = \frac{1}{2}\rho U^2 A C_D$
   - แรงยก (Lift Force): $F_L = \frac{1}{2}\rho U^2 A C_L$

> **[MISSING DATA]**: Insert specific experimental validation results showing CFD vs Experimental comparison with error bars.

---

## 1.3 การศึกษาความเป็นอิสระของเมช (Mesh Independence Study)

ความถูกต้องทางกายภาพจะไม่สมบูรณ์หากผลลัพธ์ยังเปลี่ยนไปตามความละเอียดของเมช การทดสอบความเป็นอิสระของเมช (Mesh Independence Study) หรือที่เรียกว่า **Grid Convergence Study** จึงเป็นขั้นตอนสำคัญ

### หลักการของ Grid Convergence:

เมื่อเราละเอียดเมชมากขึ้น (Refine mesh):
- ค่าตัวแปรที่สนใจ (เช่น Drag Coefficient, $C_D$) จะเข้าสู่ค่าที่ลู่เข้า (Asymptotic value)
- Truncation error จะลดลงตามลำดับของ schemes (Order of accuracy)

### เวิร์กโฟลว์การทำ Mesh Independence:

1. **Generate Coarse Mesh**: เริ่มจากเมชอย่างง่าย (M1)
2. **Run Simulation**: บันทึกค่าตัวแปรสำคัญ (เช่น $C_D$, $Nu$)
3. **Refine Mesh**: เพิ่มความละเอียด (M2, M3, ...) โดยทั่วไปใช้อัตราส่วน 2 เท่า
4. **Compare Key Metrics**: เปรียบเทียบตัวแปรสำคัญระหว่างเมชที่ต่างกัน
5. **Check Convergence**: หากผลต่าง < 1-2% ถือว่า Mesh Independent

### Grid Convergence Index (GCI):

วิธีการมาตรฐานในการประเมินความคลาดเคลื่อนจากเมช:

**นิยาม:**
- $N_1, N_2, N_3$ = จำนวน cells ในเมชละเอียด, กลาง, หยาบ (ตามลำดับ)
- $\phi_1, \phi_2, \phi_3$ = ค่าตัวแปรที่สนใจจากแต่ละเมช
- $r = N_2/N_1$ = อัตราส่วนการ refine (โดยปกติ $r > 1$)

**Step 1: คำนวณค่าความคลาดเคลื่อนสัมพัทธ์:**
$$\epsilon_{32} = \left| \frac{\phi_3 - \phi_2}{\phi_3} \right|, \quad \epsilon_{21} = \left| \frac{\phi_2 - \phi_1}{\phi_2} \right|$$

**Step 2: คำนวณ Order of Convergence ($p$):**
$$p = \frac{\ln|\epsilon_{32}/\epsilon_{21}|}{\ln(r)}$$

**Step 3: คำนวณ GCI:**
$$GCI_{21} = \frac{1.25 \epsilon_{21}}{r^p - 1}$$

**เกณฑ์:** หาก $GCI_{21} < 5\%$ ถือว่าค่าผลลัพธ์มีความเป็นอิสระจากเมช

### การตั้งค่า OpenFOAM สำหรับ Mesh Refinement:

**ใช้ `blockMesh` สำหรับการสร้างเมชหลายระดับ:**

`system/blockMeshDict` (Mesh M1 - Coarse):
```cpp
// Block mesh dictionary for coarse grid generation
// Source: OpenFOAM blockMesh utility
// Key Concepts: Hexahedral blocking, cell count specification, grading

convertToMeters 0.01;  // Scale factor: convert units to meters

vertices
(
    (0 0 0)    // Vertex 0: origin
    (10 0 0)   // Vertex 1: x-direction
    (10 5 0)   // Vertex 2: top-right
    (0 5 0)    // Vertex 3: top-left
    // ... (other vertices for 3D)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (50 25 1) simpleGrading (1 1 1);
    //    ^^^^^^^^^^^^^    ^^^^^^^^    ^^^^^^^^^^^^^^^^
    //    Cell corners      Cells       Grading ratios
);

patches
(
    wall inlet ((0 4 7 3))
    wall outlet ((1 5 6 2))
    // ... (other boundary patches)
);
```

**คำอธิบาย:**
- **Source:** ไฟล์การตั้งค่า blockMesh สำหรับสร้างเมชหยาบ (Coarse mesh) ใช้อัตราส่วนการแบ่งเซลล์ต่ำ
- **Explanation:** การกำหนดรูปทรงเรขาคณิตและการแบ่งเซลล์สำหรับเมชระดับแรก โดยระบุจุดยอด (vertices) และบล็อก (blocks) พร้อมจำนวนเซลล์ในแต่ละทิศทาง
- **Key Concepts:**
  - `convertToMeters`: ตัวคูณแปลงหน่วยจากการสร้างเมชเป็นหน่วยจริง
  - `vertices`: พิกัดมุมของโดเมนที่จะสร้างเมช
  - `blocks`: นิยามบล็อก hexahedral และจำนวนเซลล์ (nx ny nz)
  - `simpleGrading`: อัตราส่วนการขยายเซลล์ (1 = สม่ำเสมอ)

`system/blockMeshDict` (Mesh M2 - Fine):
```cpp
// Refined block mesh dictionary (2x refinement)
// Source: OpenFOAM blockMesh utility with increased resolution
// Key Concepts: Mesh refinement ratio, systematic grid doubling

convertToMeters 0.01;

vertices
(
    // ... (same vertices as coarse mesh)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 50 1) simpleGrading (1 1 1);
    //    ^^^^^^^^^^^^^    ^^^^^^^^
    //    Same corners      2x refinement in x and y
);

patches
(
    // ... (same boundary definitions)
);
```

**คำอธิบาย:**
- **Source:** ไฟล์การตั้งค่า blockMesh สำหรับสร้างเมชละเอียด (Fine mesh) โดยเพิ่มอัตราส่วนการแบ่งเซลล์เป็น 2 เท่า
- **Explanation:** การปรับปรุงเมชโดยเพิ่มจำนวนเซลล์เป็นสองเท่าในแต่ละทิศทาง (จาก 50×25 เป็น 100×50) เพื่อศึกษาผลของความละเอียดเมชต่อค่าตัวแปร
- **Key Concepts:**
  - `Refinement factor`: อัตราส่วนการเพิ่มความละเอียด (ที่นี่ = 2)
  - การเก็บ geometry เดิมแต่เปลี่ยนจำนวนเซลล์
  - การรักษา grading ratios ให้เหมือนเดิมเพื่อการเปรียบเทียบที่เป็นธรรม

**หรือใช้ `refineMesh` utility:**
```bash
# Shell command for uniform mesh refinement
# Source: OpenFOAM refineMesh utility documentation
# Usage: Refines all cells in the mesh by factor of 2

# Refine mesh by factor of 2 (uniform refinement)
refineMesh -overwrite

# Output: New mesh with 8x cells (2x in each direction)
```

**คำอธิบาย:**
- **Source:** คำสั่ง shell สำหรับการเพิ่มความละเอียดเมชโดยอัตโนมัติ ใช้ refineMesh utility ของ OpenFOAM
- **Explanation:** วิธีการเพิ่มความละเอียดเมชแบบสม่ำเสมอ (uniform refinement) โดยใช้คำสั่ง refineMesh ซึ่งจะแบ่งเซลล์ทุกเซลล์เป็น 8 ส่วน (2 เท่าในแต่ละทิศทาง)
- **Key Concepts:**
  - `refineMesh`: Utility สำหรับเพิ่มความละเอียดเมชแบบ uniform
  - `-overwrite`: เขียนทับเมชเดิมแทนการสร้างไฟล์ใหม่
  - การ refine แบบ uniform ทำให้จำนวนเซลล์เพิ่ม 8 เท่า (2³ สำหรับ 3D)

### การวิเคราะห์ผลลัพธ์:

**ตารางบันทึกผล:**

| Mesh Level | Cells ($N$) | $C_D$ | $\Delta C_D$ (%) | GCI (%) |
|------------|-------------|-------|------------------|---------|
| M1 (Coarse)| 50,000      | ?     | -                | ?       |
| M2 (Medium)| 100,000     | ?     | ?                | ?       |
| M3 (Fine)  | 200,000     | ?     | ?                | ?       |

> **[MISSING DATA]**: Insert mesh convergence study results showing $C_D$ vs cell count and GCI calculations.

---

## 1.4 แหล่งข้อมูล Benchmark ที่น่าเชื่อถือ

สำหรับการตรวจสอบความถูกต้องของ Solver ใหม่หรือการปรับปรุง Model แนะนำให้ใช้ข้อมูลจากแหล่งต่อไปนี้:

1. **NACA Airfoils**: ข้อมูลทดลองเกี่ยวกับ Drag และ Lift สำหรับภาคตัดกระบอกนูน
2. **ERCOFTAC**: ฐานข้อมูลการไหล Turbulent ที่ได้รับการตรวจสอบแล้ว
3. **NASA Turbulence Modeling Resource**: Benchmark cases สำหรับ Turbulence models
4. **OpenFOAM Tutorials**: ชุดตัวอย่างที่มาพร้อมกับ OpenFOAM

---

## สรุป (Key Takeaways):

1. **Analytical Solutions** เหมาะสำหรับ Verification ของ Solver และ Numerical Schemes
2. **Experimental Data** จำเป็นสำหรับ Validation ของ Physics ที่ซับซ้อน
3. **Mesh Independence** เป็นขั้นตอนสำคัญก่อนที่จะสรุปผลลัพธ์ทางฟิสิกส์
4. **Uncertainty Quantification** ต้องนำรวมทั้งจากฝั่ง CFD และการทดลอง