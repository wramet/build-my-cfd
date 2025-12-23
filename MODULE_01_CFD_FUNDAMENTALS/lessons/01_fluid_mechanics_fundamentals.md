# บทเรียนที่ 1: พื้นฐานกลศาสตร์ของไหล

## 🎯 วัตถุประสงค์การเรียนรู้

เมื่อจบบทเรียนนี้ คุณจะเข้าใจ:

- **แนวคิดพื้นฐาน**ของกลศาสตร์ของไหล
- **คุณสมบัติของไหล**และการวิเคราะห์มิติ
- **การจำแนกประเภท**ของการไหลและระบอบการไหล
- **สมมติฐานคอนตินิวอัม (continuum hypothesis)** และข้อจำกัด

---

## 🌊 บทนำสู่ของไหล

### คำนิยามของของไหล

**ของไหล (fluid)** คือสสารที่เปลี่ยนรูปอย่างต่อเนื่องภายใต้แรงเฉือน (shear stress) ไม่ว่าจะเล็กน้อยเพียงใดก็ตาม ของไหลแตกต่างจากของแข็งตรงที่ของไหลไม่สามารถต้านทานแรงเฉือนได้เมื่ออยู่ในสภาวะหยุดนิ่ง

#### ลักษณะสำคัญ

- **เปลี่ยนรูปได้อย่างต่อเนื่อง (Continuously deformable)**: ไหลภายใต้แรงเฉือนใดๆ
- **ปรับเปลี่ยนรูปร่างตามภาชนะ (Takes shape of container)**: ปรับให้เข้ากับรูปทรงเรขาคณิตของขอบเขต
- **โมเลกุลเคลื่อนที่ได้ (Molecular mobility)**: โมเลกุลสามารถเคลื่อนที่สัมพันธ์กันได้

### สถานะของไหล

#### ของเหลว (Liquids)

- **ความหนาแน่น (Density)**: เกือบคงที่เมื่อความดันเปลี่ยนแปลง
- **การอัดตัว (Compressibility)**: ต่ำมาก (เกือบจะอัดไม่ได้)
- **ปริมาตร (Volume)**: โดยทั่วไปคงที่
- **ผลกระทบที่ผิว (Surface effects)**: แรงตึงผิว (surface tension) มีความสำคัญที่รอยต่อ

#### ก๊าซ (Gases)

- **ความหนาแน่น (Density)**: แตกต่างกันอย่างมากตามความดันและอุณหภูมิ
- **การอัดตัว (Compressibility)**: สูง (การไหลแบบอัดตัวได้)
- **ปริมาตร (Volume)**: ขยายตัวเพื่อเติมเต็มพื้นที่ที่มีอยู่
- **สมการสถานะ (Equation of state)**: $p = \rho R T$ (ก๊าซในอุดมคติ)


[Diagram: Technical 3D isometric schematic of of molecular arrangement comparison between liquids and gases , on a neutral background. , engineering . clear labeling in white font. arrowheads for all vectors (n = red, u = blue). clear labeling in font using single letters (v, s, n, u) or short latex equations. , semi-transparent materials for volumes. , , clean , high contrast. velocity field shown as blue vectors (u). in font using single letters or latex equations. with semi-transparent materials. : engineering , , clean. Primary: Velocity field (u) as blue streamlines. Annotations: Sharp professional arrowheads (n = Red, u = Blue). Clear labels in sans-serif font using single letters or LaTeX. Ray-traced studio lighting on semi-transparent materials. Style: Engineering illustration, high-contrast, white background, 8k resolution.]
> **Prompt:** Technical 3D isometric schematic of of visualization comparing molecular arrangements in liquids versus gases. show liquid molecules closely packed with some order but still able to move past each other, with visible intermolecular forces. show gas molecules widely dispersed with high kinetic energy, moving randomly at high speeds. include for key properties: density differences, compressibility, molecular mobility, and average molecular distance. use contrasting colors - blue for liquid phase showing cohesive forces, red for gas phase showing high energy movement. include scale indicators and temperature/pressure context. scientific suitable for cfd documentation. 3/4 perspective view. , on a neutral background. , engineering . clear labeling in white font. pressure gradient from blue (low) to red (high). arrowheads for all vectors (n = red, u = blue). clear labeling in font using single letters (v, s, n, u) or short latex equations. , semi-transparent materials for volumes. , , clean , high contrast. velocity field shown as blue vectors (u). pressure scalar field as a surface gradient from blue to red. in font using single letters or latex equations. with semi-transparent materials. : engineering , , clean. Primary: Velocity field (u) as blue streamlines. Secondary: Pressure scalar field as a surface color gradient. Annotations: Sharp professional arrowheads (n = Red, u = Blue). Clear labels in sans-serif font using single letters or LaTeX. Ray-traced studio lighting on semi-transparent materials. Style: Engineering illustration, high-contrast, white background, 8k resolution.


---

## 📊 คุณสมบัติของไหล

### คุณสมบัติพื้นฐาน

| คุณสมบัติ | สัญลักษณ์ | นิยาม | หน่วย SI |
|-------------|-------------|---------|-----------|
| ความหนาแน่น | $\rho$ | มวลต่อหนึ่งหน่วยปริมาตร: $\rho = \frac{m}{V}$ | kg/m³ |
| ความดัน | $p$ | แรงตั้งฉากต่อหนึ่งหน่วยพื้นที่: $p = \frac{F_n}{A}$ | Pa = N/m² |
| อุณหภูมิ | $T$ | การวัดพลังงานความร้อน | K |
| ความหนืดพลวัต | $\mu$ | ความต้านทานต่อการเปลี่ยนรูป | Pa·s |
| ความหนืดจลนศาสตร์ | $\nu$ | $\nu = \frac{\mu}{\rho}$ | m²/s |

#### ค่าอ้างอิงทั่วไป

- **ของเหลว**: $\rho_{water} \approx 1000$ kg/m³
- **ก๊าซ**: $\rho_{air,STP} \approx 1.225$ kg/m³

#### ประเภทความดัน

- **ความดันสัมบูรณ์ (Absolute pressure)**: วัดจากสุญญากาศสมบูรณ์
- **ความดันเกจ (Gauge pressure)**: วัดจากความดันบรรยากาศ
- **ความดันพลวัต (Dynamic pressure)**: $\frac{1}{2}\rho U^2$

### คุณสมบัติอนุพันธ์

| คุณสมบัติ | สัญลักษณ์ | ความหมาย | หน่วย SI |
|-------------|-------------|-------------|-----------|
| ความร้อนจำเพาะความดันคงที่ | $c_p$ | พลังงานความร้อนต่อมวลต่ออุณหภูมิ (ความดันคงที่) | J/(kg·K) |
| ความร้อนจำเพาะปริมาตรคงที่ | $c_v$ | พลังงานความร้อนต่อมวลต่ออุณหภูมิ (ปริมาตรคงที่) | J/(kg·K) |
| สภาพนำความร้อน | $k$ | ความสามารถในการถ่ายเทความร้อน | W/(m·K) |
| แรงตึงผิว | $\sigma$ | พลังงานต่อหนึ่งหน่วยพื้นที่ที่รอยต่อ | N/m |

---

## 📐 การวิเคราะห์มิติและความคล้ายคลึง

### มิติพื้นฐาน

- **มวล (Mass)**: [M]
- **ความยาว (Length)**: [L]  
- **เวลา (Time)**: [T]
- **อุณหภูมิ (Temperature)**: [θ]
- **กระแสไฟฟ้า (Electric Current)**: [I]
- **ปริมาณสาร (Amount of Substance)**: [N]
- **ความเข้มของการส่องสว่าง (Luminous Intensity)**: [J]

### มิติคุณสมบัติของไหล

| Property | Symbol | Dimensions | SI Units |
|----------|--------|------------|----------|
| Density | $\rho$ | [M L⁻³] | kg/m³ |
| Velocity | $U$ | [L T⁻¹] | m/s |
| Pressure | $p$ | [M L⁻¹ T⁻²] | Pa |
| Dynamic Viscosity | $\mu$ | [M L⁻¹ T⁻¹] | Pa·s |
| Kinematic Viscosity | $\nu$ | [L² T⁻¹] | m²/s |

### 🔄 เลขไร้มิติ (Dimensionless Numbers)

#### เลขเรย์โนลด์ (Reynolds Number) ($\text{Re}$)

อัตราส่วนของแรงเฉื่อยต่อแรงหนืด:

$$
\text{Re} = \frac{\rho U L}{\mu} = \frac{U L}{\nu}
$$

**ความสำคัญทางกายภาพ**:

| ค่า Re | ระบอบการไหล | ลักษณะเฉพาะ |
|---------|---------------|----------------|
| $\text{Re} \ll 1$ | การไหลแบบคืบคลาน | แรงหนืดมีอิทธิพลเหนือกว่า |
| $1 < \text{Re} < 2000$ | การไหลแบบราบเรียบ | การไหลเป็นเลเยอร์ |
| $2000 < \text{Re} < 4000$ | การเปลี่ยนผ่าน | การเปลี่ยนจากราบเรียบเป็นปั่นป่วน |
| $\text{Re} \gg 1$ | การไหลแบบปั่นป่วน | แรงเฉื่อยมีอิทธิพลเหนือกว่า |

#### เลขมัค (Mach Number) ($\text{Ma}$)

อัตราส่วนของความเร็วการไหลต่อความเร็วเสียง:

$$
\text{Ma} = \frac{U}{a}
$$

**ระบอบการไหล (Flow regimes)**:

| ค่า Ma | ระบอบการไหล | คุณสมบัติ |
|---------|----------------|-------------|
| $\text{Ma} < 0.3$ | อัดตัวไม่ได้ | ความหนาแน่นคงที่ |
| $0.3 < \text{Ma} < 1$ | อัดตัวได้ความเร็วต่ำกว่าเสียง | ผลกระทบจากการอัดตัว |
| $\text{Ma} \approx 1$ | ทรานโซนิก | การเปลี่ยนผ่านระหว่างรอยเสียง |
| $\text{Ma} > 1$ | ความเร็วเหนือเสียง | คลื่นกระแทกและการบีบอัด |

#### เลขฟรูด (Froude Number) ($\text{Fr}$)

อัตราส่วนของแรงเฉื่อยต่อแรงโน้มถ่วง:

$$
\text{Fr} = \frac{U}{\sqrt{g L}}
$$

**ความสำคัญ**: มีความสำคัญในการไหลแบบผิวอิสระ (free-surface flows), แรงต้านทานเรือ, การไหลในช่องเปิด

#### เลขเวเบอร์ (Weber Number) ($\text{We}$)

อัตราส่วนของแรงเฉื่อยต่อแรงตึงผิว:

$$
\text{We} = \frac{\rho U^2 L}{\sigma}
$$

**ความสำคัญ**: มีความสำคัญในการก่อตัวของหยดน้ำ, พลวัตของฟองอากาศ, การวิเคราะห์ละอองสเปรย์


```mermaid
graph TD
    A["Inertial Forces<br/><b>\(F_i = \rho U^2 L^2\)</b>"] --> D["Flow Characterization"]
    B["Viscous Forces<br/><b>\(F_v = \mu U L\)</b>"] --> D
    C["Gravity Forces<br/><b>\(F_g = \rho g L^3\)</b>"] --> D
    E["Surface Tension<br/><b>\(F_\sigma = \sigma L\)</b>"] --> D
    
    D --> F["Reynolds Number<br/><b>Re = \frac{\rho U L}{\mu}</b><br/>Inertial/Viscous"]
    D --> G["Froude Number<br/><b>Fr = \frac{U}{\sqrt{g L}}</b><br/>Inertial/Gravity"]
    D --> H["Weber Number<br/><b>We = \frac{\rho U^2 L}{\sigma}</b><br/>Inertial/Surface Tension"]
    D --> I["Mach Number<br/><b>Ma = \frac{U}{a}</b><br/>Flow Speed/Sound Speed"]
    
    F --> J["<b>Re < 2300:</b><br/>Laminar Flow<br/>Smooth, ordered"]
    F --> K["<b>Re > 4000:</b><br/>Turbulent Flow<br/>Chaotic, mixing"]
    
    G --> L["<b>Fr < 1:</b><br/>Subcritical<br/>Tranquil flow"]
    G --> M["<b>Fr > 1:</b><br/>Supercritical<br/>Rapid flow"]
    
    H --> N["<b>We > 1:</b><br/>Droplet formation<br/>Atomization"]
    H --> O["<b>We < 1:</b><br/>Surface tension<br/>dominates"]
    
    I --> P["<b>Ma < 0.3:</b><br/>Incompressible<br/>\(\rho = \text{constant}\)"]
    I --> Q["<b>Ma > 1:</b><br/>Compressible<br/>Shock waves"]
    
    %% Styling Definitions
    classDef force fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef dimensionless fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef regime fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    
    class A,B,C,E force;
    class D,F,G,H,I dimensionless;
    class J,K,L,M,N,O,P,Q regime;
```


---

## 🔬 สมมติฐานคอนตินิวอัม (Continuum Hypothesis)

### คำนิยาน

**สมมติฐานคอนตินิวอัม (continuum hypothesis)** สมมติว่าคุณสมบัติของไหลสามารถนิยามได้ทุกจุดในอวกาศ โดยถือว่าของไหลเป็นตัวกลางต่อเนื่องแทนที่จะเป็นโมเลกุลแยกส่วน


```mermaid
graph LR
    subgraph "Continuum Perspective"
        A["Control Volume<br/>dV"] --> B["Continuous Properties<br/>ρ, u, p, T"]
        B --> C["Differential Equations<br/>Navier-Stokes"]
    end
    
    subgraph "Molecular Perspective"
        D["Molecules<br/>Random Motion"] --> E["Statistical Properties<br/>Average velocity"]
        E --> F["Kinetic Theory<br/>Boltzmann Equation"]
    end
    
    A -.-> D
    B -.-> E
    C -.-> F
    
    G["Knudsen Number<br/>Kn = λ/L"] --> H{"Flow Regime"}
    H -->|"Kn < 0.01"| I["Continuum<br/>Valid"]
    H -->|"0.01 < Kn < 0.1"| J["Slip Flow<br/>Transition"]
    H -->|"Kn > 0.1"| K["Free Molecular<br/>Rarefied"]
    
    I --> A
    J --> L["Modified Continuum<br/>with Slip Conditions"]
    K --> D
    
    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    
    class A,B,C,G,I,J,K,L process
    class H decision
    class D,E,F storage
```


### เลขคนุดเซน (Knudsen Number) ($\text{Kn}$)

อัตราส่วนของระยะทางอิสระเฉลี่ยของโมเลกุลต่อความยาวลักษณะเฉพาะ:

$$
\text{Kn} = \frac{\lambda}{L}
$$

**ระบอบการไหล (Flow regimes)**:

| ค่า Kn | ระบอบการไหล | คำอธิบาย |
|---------|----------------|------------|
| $\text{Kn} < 0.01$ | การไหลแบบคอนตินิวอัม | Navier-Stokes ใช้ได้ |
| $0.01 < \text{Kn} < 0.1$ | การไหลแบบสลิป | มีสลิปที่ผนัง |
| $0.1 < \text{Kn} < 10$ | การไหลแบบเปลี่ยนผ่าน | ระหว่างคอนตินิวอัมและโมเลกุล |
| $\text{Kn} > 10$ | การไหลแบบโมเลกุลอิสระ | ไม่สามารถใช้ Navier-Stokes |

### แนวคิดปริมาตรควบคุม (Control Volume Concept)


```mermaid
graph LR
    subgraph "Control Volume Types"
        A["Differential Control Volume<br/>(dV = dx·dy·dz)"]
        B["Integral Control Volume<br/>(V = ∫∫∫ dV)"]
    end
    
    A --> C["Point-wise Analysis<br/>Governing Equations"]
    B --> D["Global Analysis<br/>Conservation Laws"]
    
    C --> E["Local Properties<br/>velocity u(x,y,z,t)<br/>pressure p(x,y,z,t)"]
    D --> F["Bulk Properties<br/>total mass flow rate<br/>average properties"]
    
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style C fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000;
    style D fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000;
    style E fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#000;
    style F fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000;

%% Styling Definitions
classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
```


- **ปริมาตรควบคุมเชิงอนุพันธ์**: องค์ประกอบปริมาตรขนาดเล็ก $\mathrm{d}V = \mathrm{d}x \,\mathrm{d}y \,\mathrm{d}z$
- **ปริมาตรควบคุมเชิงปริพันธ์**: ปริมาตรจำกัด $V$ ที่ล้อมรอบด้วยพื้นผิว $S$

---

## 📖 สถิตยศาสตร์ของไหล (Fluid Statics)

### การกระจายความดันสถิตยศาสตร์ (Hydrostatic Pressure Distribution)

$$
\frac{\mathrm{d}p}{\mathrm{d}z} = -\rho g
$$

สำหรับความหนาแน่นคงที่:

$$
p = p_0 + \rho g h
$$

**คำอธิบายตัวแปร**:
- $p$ = ความดัน ณ ความสูง h
- $p_0$ = ความดัน ณ จุดอ้างอิง
- $\rho$ = ความหนาแน่นของของไหล
- $g$ = ความเร่งเนื่องจากแรงโน้มถ่วง
- $h$ = ความสูงเหนือจุดอ้างอิง

### แรงลอยตัว (Buoyancy) (หลักการของอาร์คิมิดีส)

แรงลอยตัวเท่ากับน้ำหนักของของไหลที่ถูกแทนที่:

$$
F_b = \rho_{fluid} g V_{displaced}
$$


```mermaid
graph LR
    A["Hydrostatic Pressure Distribution"] --> B["Pressure gradient formula"]
    B --> C["dp/dz = -ρg"]
    C --> D["Integrated form"]
    D --> E["p = p0 + ρgh"]
    
    F["Buoyancy Force"] --> G["Archimedes Principle"]
    G --> H["Fb = ρfluid × g × Vdisplaced"]
    
    I["Key Variables:"] --> J["p = pressure at height h"]
    I --> K["p0 = reference pressure"]
    I --> L["ρ = fluid density"]
    I --> M["g = gravity acceleration"]
    I --> N["h = height above reference"]
    I --> O["Fb = buoyancy force"]
    I --> P["Vdisplaced = displaced volume"]
    
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    
    class A,B,C,D,E,F,G,H process;
    class I,J,K,L,M,N,O,P storage;
```


---

## 🌀 จลนศาสตร์ของไหล (Fluid Kinematics)

### วิธีการอธิบายการไหล (Flow Description Methods)

#### คำอธิบายแบบออยเลอร์ (Eulerian Description)
คุณสมบัติที่อธิบาย ณ จุดคงที่ในอวกาศ:
$$
\mathbf{u} = \mathbf{u}(\mathbf{x}, t)
$$

#### คำอธิบายแบบลากรางจ์ (Lagrangian Description)
คุณสมบัติที่อธิบายตามอนุภาคของไหล:
$$
\mathbf{x} = \mathbf{x}(\mathbf{x}_0, t)
$$


```mermaid
graph LR
    subgraph "Eulerian Description"
        A["Fixed Point in Space"] --> B["Properties measured at<br/>specific locations"]
        B --> C["u = u(x,t)"]
        C --> D["Field-based approach"]
        D --> E["Weather station analogy"]
    end
    
    subgraph "Lagrangian Description"
        F["Fluid Particle"] --> G["Properties follow<br/>individual particles"]
        G --> H["x = x(x₀,t)"]
        H --> I["Particle tracking approach"]
        I --> J["Drifter buoy analogy"]
    end
    
    K["Same Physical Flow"] --> A
    K --> F
    
    style Eulerian fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style Lagrangian fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef eulerian fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef lagrangian fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    class A,B,C,D,E eulerian;
    class F,G,H,I,J lagrangian;
```


### การแสดงภาพสนามการไหล (Flow Field Visualization)

#### เส้นกระแส (Streamlines)
เส้นโค้งที่สัมผัสกับเวกเตอร์ความเร็ว ณ แต่ละขณะ:
$$
\frac{\mathrm{d}\mathbf{x}}{\mathrm{d}s} = \mathbf{u}(\mathbf{x}, t)
$$

#### เส้นทางเดินอนุภาค (Pathlines)
วิถีจริงของอนุภาคของไหล:
$$
\frac{\mathrm{d}\mathbf{x}}{\mathrm{d}t} = \mathbf{u}(\mathbf{x}, t)
$$

#### เส้นสาย (Streaklines)
ตำแหน่งของอนุภาคทั้งหมดที่เคยผ่านจุดที่กำหนด


```mermaid
graph LR
    subgraph "Flow Field Visualization"
        A["<b>Streamlines</b><br/>Tangent to velocity vectors<br/>at each instant"] --> B["<b>Pathlines</b><br/>Actual trajectories<br/>of fluid particles"]
        B --> C["<b>Streaklines</b><br/>All particles that have<br/>passed through a point"]
        
        D["<b>Steady Flow</b><br/>Streamlines = Pathlines<br/>= Streaklines"] -.-> A
        E["<b>Unsteady Flow</b><br/>Streamlines ≠ Pathlines<br/>≠ Streaklines"] -.-> B
    end
    
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    class A,B,C process;
    class D,E decision;
```


### การจำแนกประเภทการไหล (Flow Classification)

#### การไหลแบบคงที่ (Steady) เทียบกับการไหลแบบไม่คงที่ (Unsteady)

- **การไหลแบบคงที่**: $\frac{\partial}{\partial t} = 0$
- **การไหลแบบไม่คงที่**: ขึ้นอยู่กับเวลา

#### การไหลแบบสม่ำเสมอ (Uniform) เทียบกับการไหลแบบไม่สม่ำเสมอ (Non-uniform)

- **การไหลแบบสม่ำเสมอ**: ไม่มีการเปลี่ยนแปลงเชิงพื้นที่ในทิศทางการไหล
- **การไหลแบบไม่สม่ำเสมอ**: มีการเปลี่ยนแปลงเชิงพื้นที่

#### การไหลแบบอัดตัวได้ (Compressible) เทียบกับการไหลแบบอัดตัวไม่ได้ (Incompressible)

- **อัดตัวไม่ได้**: $\nabla \cdot \mathbf{u} = 0$
- **อัดตัวได้**: ความหนาแน่นแปรผันตามความดันและอุณหภูมิ

#### การไหลแบบราบเรียบ (Laminar) เทียบกับการไหลแบบปั่นป่วน (Turbulent)

| ลักษณะ | การไหลแบบราบเรียบ | การไหลแบบปั่นป่วน |
|----------|----------------------|----------------------|
| การเคลื่อนที่ | เป็นเลเยอร์ เรียบเนียน | วุ่นวาย สุ่ม |
| การผสม | ต่ำมาก | สูงมาก |
| การพึ่งพาเวลา | ไม่มี | มีมาก |
| พลังงาน | แรงเฉือยต่ำ | การพลัดเปลี่ยนพลังงาน |

---

## 💪 ความเค้นในของไหล (Stress in Fluids)

### เทนเซอร์ความเค้น (Stress Tensor)

สถานะความเค้น ณ จุดหนึ่งอธิบายโดยเทนเซอร์ความเค้น $\boldsymbol{\tau}$:

$$
\boldsymbol{\tau} = \begin{bmatrix}
\tau_{xx} & \tau_{xy} & \tau_{xz} \\
\tau_{yx} & \tau_{yy} & \tau_{yz} \\
\tau_{zx} & \tau_{zy} & \tau_{zz}
\end{bmatrix}
$$


```mermaid
graph LR
    A["Fluid Cube"] --> B["Normal Stress σxx"]
    A --> C["Normal Stress σyy"]
    A --> D["Normal Stress σzz"]
    A --> E["Shear Stress τxy"]
    A --> F["Shear Stress τxz"]
    A --> G["Shear Stress τyz"]
    B --> H["σxx = Normal stress<br/>on x-face"]
    C --> I["σyy = Normal stress<br/>on y-face"]
    D --> J["σzz = Normal stress<br/>on z-face"]
    E --> K["τxy = Shear stress<br/>on x-face in y-direction"]
    F --> L["τxz = Shear stress<br/>on x-face in z-direction"]
    G --> M["τyz = Shear stress<br/>on y-face in z-direction"]
    
    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    
    class A process;
    class B,C,D decision;
    class E,F,G terminator;
    class H,I,J,K,L,M storage;
```


### ความดันและความเค้นหนืด (Pressure and Viscous Stress)

การแยกส่วนความเค้นรวม:
$$
\boldsymbol{\tau} = -p\mathbf{I} + \boldsymbol{\tau}_{viscous}
$$

#### ความเค้นความดัน (Pressure Stress)
ส่วนไอโซทรอปิก: $-p\mathbf{I}$

#### ความเค้นหนืด (Viscous Stress) (ของไหลแบบนิวตัน)

สำหรับของไหลแบบนิวตัน (Newtonian fluid):
$$
\tau_{ij} = \mu\left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right) - \frac{2}{3}\mu(\nabla \cdot \mathbf{u})\delta_{ij}
$$

---

## 🌪️ Vorticity และ Circulation

### Vorticity ($\boldsymbol{\omega}$)

การวัดการหมุนเฉพาะที่:
$$
\boldsymbol{\omega} = \nabla \times \mathbf{u}
$$

#### ส่วนประกอบใน 3 มิติ
$$
\boldsymbol{\omega} = \left(\frac{\partial w}{\partial y} - \frac{\partial v}{\partial z}, \frac{\partial u}{\partial z} - \frac{\partial w}{\partial x}, \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}\right)
$$

### Circulation ($\Gamma$)

ปริพันธ์ตามเส้นของความเร็วรอบเส้นโค้งปิด:
$$
\Gamma = \oint_C \mathbf{u} \cdot \mathrm{d}\mathbf{l} = \int_S (\nabla \times \mathbf{u}) \cdot \mathrm{d}\mathbf{S} = \int_S \boldsymbol{\omega} \cdot \mathrm{d}\mathbf{S}
$$

**ทฤษฎี Circulation ของเคลวิน (Kelvin's Circulation Theorem)**: Circulation ถูกอนุรักษ์ในการไหลแบบไร้ความหนืด (inviscid), แบบบารอทรอปิก (barotropic) ที่มีแรงภายนอกแบบอนุรักษ์ (conservative body forces)


```mermaid
graph LR
    subgraph "Vorticity and Circulation Concepts"
        A["Velocity Field u(x,y,z)"] --> B["Calculate Vorticity ω = ∇ × u"]
        B --> C["Vorticity Components"]
        C --> Cx["ωx = ∂w/∂y - ∂v/∂z"]
        C --> Cy["ωy = ∂u/∂z - ∂w/∂x"]
        C --> Cz["ωz = ∂v/∂x - ∂u/∂y"]
        
        A --> D["Closed Curve C"]
        D --> E["Calculate Circulation Γ = ∮C u ⋅ dl"]
        E --> F["Apply Stokes Theorem"]
        F --> G["Γ = ∫S ω ⋅ dS"]
        
        H["Inviscid Flow"] --> I["Barotropic"]
        I --> J["Conservative Body Forces"]
        J --> K["Kelvin's Theorem: Γ = Constant"]
    end
    
    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
```


---

## 💧 การไหลแบบศักย์ (Potential Flow)

### ศักย์ความเร็ว (Velocity Potential) ($\phi$)

สำหรับการไหลแบบไร้การหมุน ($\nabla \times \mathbf{u} = 0$):
$$
\mathbf{u} = \nabla \phi
$$

**สมการลาปลาซ (Laplace equation)**:
$$
\nabla^2 \phi = 0
$$

### ฟังก์ชันกระแส (Stream Function) ($\psi$)

สำหรับการไหลแบบอัดตัวไม่ได้ 2 มิติ:
$$
u = \frac{\partial \psi}{\partial y}, \quad v = -\frac{\partial \psi}{\partial x}
$$


```mermaid
graph LR
    A["Velocity Potential φ"] --> B["Laplace Equation: ∇²φ = 0"]
    C["Stream Function ψ"] --> D["Flow Field: u = ∂φ/∂x, v = ∂φ/∂y"]
    E["Irrotational Flow"] --> F["Potential Flow"]
    G["Incompressible Flow"] --> H["Streamlines: ψ = constant"]
    I["Equipotential Lines"] --> J["φ = constant"]
    K["Orthogonal Grid"] --> L["Streamlines ⟂ Equipotentials"]
    M["Complex Potential"] --> N["W(z) = φ + iψ"]
    O["Conformal Mapping"] --> P["Flow Around Bodies"]
    
    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P process;
```


---

## 🏔️ ชั้นขอบเขต (Boundary Layers)

### แนวคิด

บริเวณบางๆ ใกล้กับพื้นผิวแข็งที่ผลกระทบจากความหนืดมีความสำคัญ

### ความหนาของชั้นขอบเขต (Boundary Layer Thickness) ($\delta$)

ระยะทางลักษณะเฉพาะจากผนังที่ความเร็วถึง 99% ของความเร็วการไหลอิสระ (free-stream velocity)

#### ชั้นขอบเขตแบบราบเรียบ (Laminar Boundary Layer) (Blasius Solution)
$$
\delta \approx \frac{5.0x}{\sqrt{\text{Re}_x}} = 5.0\sqrt{\frac{\nu x}{U_\infty}}
$$

#### ชั้นขอบเขตแบบปั่นป่วน (Turbulent Boundary Layer)
$$
\delta \approx \frac{0.37x}{\text{Re}_x^{1/5}}
$$

### ความเค้นเฉือยที่ผนัง (Wall Shear Stress)
$$
\tau_w = \mu\left(\frac{\partial u}{\partial y}\right)_{y=0}
$$

#### สัมประสิทธิ์แรงเสียดทานผิว (Skin Friction Coefficient)
$$
C_f = \frac{\tau_w}{\frac{1}{2}\rho U_\infty^2}
$$


```mermaid
graph TD
    A["Free Stream Flow"] --> B["Leading Edge"]
    B --> C["Laminar Boundary Layer"]
    C --> D["Transition Region"]
    D --> E["Turbulent Boundary Layer"]
    E --> F["Wake Region"]
    
    C --> G["δ ≈ 5.0x/√Re_x<br/>Blasius Solution"]
    E --> H["δ ≈ 0.37x/Re_x^1/5<br/>Turbulent Profile"]
    
    G --> I["τ_w = μ(∂u/∂y)_y=0<br/>Wall Shear Stress"]
    H --> J["C_f = τ_w/(½ρU_∞²)<br/>Skin Friction Coefficient"]
    
    K["Stream Function ψ<br/>u = ∂ψ/∂y<br/>v = -∂ψ/∂x"] --> C
    K --> E
    
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style D fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style E fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style F fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    style G fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style H fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style I fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style J fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style K fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
```


### OpenFOAM Code Implementation

```cpp
// Boundary layer thickness calculation in OpenFOAM
scalar delta = 5.0 * sqrt(nu * x / Uinf);
label wallCell = mesh.boundaryMesh()[wallPatchID].whichCell(x);
scalar yPlus = wallDist[wallCell] * sqrt(tauW[wallCell] / rho);
```

---

## 🌊 ปรากฏการณ์การไหลพื้นฐาน

### การแยกตัวของการไหล (Flow Separation)
เกิดขึ้นเมื่อชั้นขอบเขตหลุดออกจากพื้นผิวเนื่องจากความชันความดันที่ไม่เอื้ออำนวย (adverse pressure gradient)

### การก่อตัวของ Wake (Wake Formation)
บริเวณของการไหลที่ถูกรบกวนท้ายสิ่งกีดขวาง

### การหลุดของ Vortex (Vortex Shedding)
การก่อตัวของ Vortex สลับกันด้านหลังวัตถุที่มีรูปร่างทู่ (von Kármán vortex street)

### การไหลแบบ Jet และ Plume (Jet and Plume Flows)
กระแสของไหลความเร็วสูงที่พุ่งเข้าสู่ของไหลรอบข้าง


```mermaid
graph LR
    A["Free Stream<br/>U<span style='font-size:0.8em;'>∞</span>"] --> B["Boundary Layer<br/>Growth"]
    B --> C["Separation Point<br/>∂p/∂x < 0"]
    C --> D["Recirculation<br/>Zone"]
    D --> E["Wake Region<br/>Turbulent Flow"]
    E --> F["Vortex Shedding<br/>von Kármán Street"]
    
    G["Jet Flow<br/>High Velocity"] --> H["Mixing Layer<br/>Shear Instability"]
    H --> I["Plume Rise<br/>Buoyancy Driven"]
    
    J["Skin Friction<br/>τ<span style="font-size:0.8em;w</span> = μ(∂u/∂y)<span style="font-size:0.8em;y=0</span>"] --> K["Coefficient C<span style="font-size:0.8em;f</span><br/>= 2τ<span style="font-size:0.8em;w</span>/(ρU<span style="font-size:0.8em;∞</span>²)"]
    
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    style B fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    style C fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    style D fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    style F fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000;
    style G fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#000;
    style H fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000;
    style I fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000;
    style J fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#000;
    style K fill:#e0f7fa,stroke:#00acc1,stroke-width:2px,color:#000;
    
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
```


---

## 💻 สัญชาตญาณทางกายภาพสำหรับ CFD

### 🎯 เหตุใดพื้นฐานเหล่านี้จึงสำคัญสำหรับ CFD

#### การออกแบบ Mesh
- **ชั้นขอบเขต (Boundary layers)**: ต้องการความละเอียดสูงใกล้ผนัง
- **เลขเรย์โนลด์สูง (High Reynolds number)**: อาจต้องใช้แบบจำลองความปั่นป่วน (turbulence modeling)
- **ผลกระทบจากการอัดตัว (Compressible effects)**: อาจต้องใช้แผนการจับคลื่นกระแทก (shock-capturing schemes)

#### การเลือก Solver
- **คงที่ (Steady) เทียบกับไม่คงที่ (unsteady)**: เลือกการรวมเวลาที่เหมาะสม
- **อัดตัวได้ (Compressible) เทียบกับอัดตัวไม่ได้ (incompressible)**: สมการควบคุมที่แตกต่างกัน
- **ราบเรียบ (Laminar) เทียบกับปั่นป่วน (turbulent)**: การสร้างแบบจำลองเทียบกับการจำลองโดยตรง

#### เงื่อนไขขอบเขต (Boundary Conditions)
- **ความหมายทางกายภาพ**: ทำความเข้าใจว่าแต่ละ BC แสดงถึงอะไร
- **พฤติกรรมทางคณิตศาสตร์**: ความสมบูรณ์ของปัญหาค่าขอบเขต (boundary value problem)

#### เกณฑ์การลู่เข้า (Convergence Criteria)
- **พื้นฐานทางกายภาพ**: Residuals แสดงถึงความไม่สมดุลของสมการ
- **ขีดจำกัดความเสถียร**: ข้อจำกัดของ Time step จากฟิสิกส์

### ⚠️ ข้อผิดพลาดที่พบบ่อยใน CFD จากกลศาสตร์ของไหล

#### ความละเอียดของชั้นขอบเขตไม่เพียงพอ (Inadequate Boundary Layer Resolution)
- **ปัญหา**: การจัดการผนังที่ไม่ดี
- **วิธีแก้ไข**: $y^+ < 1$ สำหรับชั้นขอบเขตที่แก้ไขได้

#### การสร้างแบบจำลองความปั่นป่วนไม่ถูกต้อง (Incorrect Turbulence Modeling)
- **ปัญหา**: ใช้ Solver แบบราบเรียบสำหรับการไหลแบบปั่นป่วน
- **วิธีแก้ไข**: ตรวจสอบ Reynolds number, เลือกแบบจำลองที่เหมาะสม

#### ละเลยผลกระทบจากการอัดตัว (Compressibility Effects Neglected)
- **ปัญหา**: สมมติว่าการไหลเป็นแบบอัดตัวไม่ได้ที่ Mach number สูง
- **วิธีแก้ไข**: ตรวจสอบ Mach number, ใช้ compressible Solver หากจำเป็น

#### เงื่อนไขเริ่มต้นไม่ดี (Poor Initial Conditions)
- **ปัญหา**: สถานะเริ่มต้นที่ไม่เป็นไปตามหลักฟิสิกส์
- **วิธีแก้ไข**: เริ่มต้นจากเงื่อนไขที่สมเหตุสมผลทางกายภาพ

### OpenFOAM Code Implementation

```cpp
// Reynolds number calculation and flow regime check
scalar Re = rho * U * L / mu;

if (Re < 2000)
{
    Info << "Laminar flow regime detected" << endl;
}
else if (Re > 4000)
{
    Info << "Turbulent flow regime detected" << endl;
    // Select appropriate turbulence model
}
else
{
    Info << "Transition flow regime detected" << endl;
}
```

---

## 🧮 ตัวอย่างเชิงปฏิบัติ

### ตัวอย่างที่ 1: การไหลเหนือแผ่นเรียบ

คำนวณความหนาของชั้นขอบเขตที่ $x = 1$ m สำหรับอากาศที่ $U_\infty = 10$ m/s

**กำหนด**: $\nu_{air} = 1.5 \times 10^{-5}$ m²/s

**วิธีแก้**:

1. คำนวณเลขเรย์โนลด์:
   $$
   \text{Re}_x = \frac{U_\infty x}{\nu} = \frac{10 \times 1}{1.5 \times 10^{-5}} = 6.67 \times 10^5
   $$

2. ตรวจสอบระบอบการไหล:
   เนื่องจาก $\text{Re}_x < 5 \times 10^5$ จึงเป็นชั้นขอบเขตแบบราบเรียบ

3. คำนวณความหนาชั้นขอบเขต:
   $$
   \delta = 5.0\sqrt{\frac{\nu x}{U_\infty}} = 5.0\sqrt{\frac{1.5 \times 10^{-5} \times 1}{10}} = 6.1 \times 10^{-3} \text{ m}
   $$

### ตัวอย่างที่ 2: เลขเรย์โนลด์ของการไหลในท่อ

คำนวณเลขเรย์โนลด์สำหรับการไหลของน้ำในท่อขนาดเส้นผ่านศูนย์กลาง 10 cm ที่ความเร็ว 2 m/s

**กำหนด**: $\nu_{water} = 10^{-6}$ m²/s, $D = 0.1$ m

**วิธีแก้**:
$$
\text{Re} = \frac{U D}{\nu} = \frac{2 \times 0.1}{10^{-6}} = 2 \times 10^5
$$

เนื่องจาก $\text{Re} > 4000$ การไหลจึงเป็นแบบปั่นป่วน

### OpenFOAM Code Implementation

```cpp
// Boundary layer calculation example
scalar Re_x = Uinf * x / nu;
scalar delta;

if (Re_x < 5e5)
{
    // Laminar boundary layer
    delta = 5.0 * sqrt(nu * x / Uinf);
}
else
{
    // Turbulent boundary layer  
    delta = 0.37 * x / pow(Re_x, 0.2);
}

Info << "Boundary layer thickness at x = " << x 
     << " is " << delta << " m" << endl;
```

---

## 📚 สรุป

บทเรียนนี้ได้วางรากฐานของกลศาสตร์ของไหลที่จำเป็นสำหรับ CFD:

### 🔑 แนวคิดหลัก

- **คุณสมบัติของไหล (Fluid properties)** และการวิเคราะห์มิติ
- **สมมติฐานคอนตินิวอัม (Continuum hypothesis)** และขีดจำกัดความถูกต้อง
- **การจำแนกประเภทการไหล (Flow classification)** และระบอบการไหล
- **สมการพื้นฐาน (Fundamental equations)** ที่ควบคุมการเคลื่อนที่ของไหล

### 🔗 ความเกี่ยวข้องกับ CFD

- การทำความเข้าใจ**ปรากฏการณ์ทางกายภาพ (physical phenomena)** ช่วยในการตีความผลการจำลอง
- **การวิเคราะห์มิติ (Dimensional analysis)** เป็นแนวทางในการเลือกและตรวจสอบแบบจำลอง
- **ระบอบการไหล (Flow regimes)** กำหนดวิธีการเชิงตัวเลขที่เหมาะสม
- **เงื่อนไขขอบเขต (Boundary conditions)** ต้องสะท้อนความเป็นจริงทางกายภาพ

### 📈 ขั้นตอนต่อไป

พื้นฐานเหล่านี้จะมีความสำคัญเมื่อเรา:

- **อนุพันธ์สมการ Navier-Stokes** ในบทเรียนถัดไป
- **พัฒนาวิธีการเชิงตัวเลข (numerical methods)** สำหรับการแก้ปัญหา
- **นำเงื่อนไขขอบเขต (boundary conditions)** ไปใช้ใน OpenFOAM
- **ตรวจสอบความถูกต้องของผลลัพธ์ CFD (validate CFD results)** เทียบกับผลเฉลยเชิงวิเคราะห์

---

**บทเรียนถัดไป**: [บทเรียนที่ 2: สมการควบคุมการไหลของไหล](02_governing_equations.md)
