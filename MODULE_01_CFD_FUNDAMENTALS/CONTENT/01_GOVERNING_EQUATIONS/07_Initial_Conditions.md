# Initial Conditions

การจำลองต้องเริ่มต้นจากจุดใดจุดหนึ่ง **Initial Conditions** (ในไดเรกทอรี `0/`) กำหนดสถานะที่ $t=0$ เงื่อนไขเหล่านี้มีความสำคัญอย่างยิ่งต่อ **Numerical Stability** และ **Convergence** ของการจำลอง CFD เนื่องจากเป็นจุดเริ่มต้นที่ Solver จะทำการวนซ้ำเพื่อหา Solution

การเลือก Initial Conditions สามารถส่งผลกระทบอย่างมีนัยสำคัญต่อ **Computational Efficiency** โดยเฉพาะอย่างยิ่งสำหรับ **Steady-State Problems** ที่การเริ่มต้นที่ดีสามารถลด Convergence Time ได้หลายเท่าตัว


```mermaid
graph LR
    Start["Start Simulation"] --> SelectIC["Select Initial<br/>Conditions"]
    SelectIC --> IC1["Realistic Physical<br/>Values"]
    SelectIC --> IC2["Zero Initial<br/>Conditions"]
    SelectIC --> IC3["Previous Solution<br/>Continuation"]

    IC1 --> GoodStab["High Numerical<br/>Stability"]
    IC2 --> PoorStab["Potential Numerical<br/>Instability"]
    IC3 --> BestStab["Excellent Numerical<br/>Stability"]

    GoodStab --> FastConv["Fast Convergence"]
    PoorStab --> SlowConv["Slow Convergence<br/>or Divergence"]
    BestStab --> FastestConv["Fastest Convergence"]

    FastConv --> Final["Stable Solution"]
    SlowConv --> Restart["Need to Adjust<br/>Initial Conditions"]
    FastestConv --> Final

    Restart --> SelectIC

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class Start,Final terminator;
    class SelectIC,Restart decision;
    class IC1,IC2,IC3,GoodStab,PoorStab,BestStab,FastConv,SlowConv,FastestConv process;
```


ใน OpenFOAM, Initial Conditions จะถูกระบุผ่าน **Field Dictionaries** ในไดเรกทอรี `0/` โดยแต่ละ Field (Velocity, Pressure, Temperature, เป็นต้น) จะมีไฟล์ของตัวเอง โครงสร้างเป็นไปตามรูปแบบที่สอดคล้องกัน

## Field Initialization Structure

ไฟล์ Field ของ OpenFOAM เป็นไปตามรูปแบบ **Dictionary** มาตรฐานที่รวมถึง:

- **Dimensional Specification**
- **Internal Field Initialization**
- **Boundary Condition Definitions**

ระบบมิติใช้หน่วย **Mass-Length-Time-Temperature-Moles-Current**: `[mass length time temperature moles current]`

### Velocity Field Initialization (`0/U`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];  // m/s: ความยาว/เวลา
internalField   uniform (0 0 0);   // ฟิลด์ความเร็วเริ่มต้น

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0); // ความเร็วขาเข้าแบบ Uniform 10 m/s
    }
    outlet
    {
        type            zeroGradient;     // การไหลที่พัฒนาเต็มที่
    }
    walls
    {
        type            noSlip;           // เงื่อนไข No-Slip
    }
    symmetry
    {
        type            symmetryPlane;    // ขอบเขตสมมาตร
    }
}
```


```mermaid
graph LR
    A["Velocity Field Initialization"] --> B["Internal Field<br/>uniform (0 0 0)"]
    A --> C["Boundary Conditions"]
    C --> D["Inlet<br/>fixedValue<br/>uniform (10 0 0)<br/>10 m/s"]
    C --> E["Outlet<br/>zeroGradient<br/>Fully Developed Flow"]
    C --> F["Walls<br/>noSlip<br/>Zero Velocity"]
    C --> G["Symmetry<br/>symmetryPlane<br/>Mirror Condition"]
    A --> H["Field Properties"]
    H --> I["volVectorField"]
    H --> J["Dimensions [0 1 -1 0 0 0 0]<br/>m/s: length/time"]

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    class A,B,C,H process;
    class D,E,F,G,I,J storage;
```


## Advanced Initialization Strategies

### Non-Uniform Field Initialization

สำหรับ **Geometry** หรือ **Flow Physics** ที่ซับซ้อน การเริ่มต้นแบบ Uniform อาจไม่เพียงพอ OpenFOAM รองรับหลายวิธีในการสร้าง Initial Conditions ที่สมจริงทางกายภาพ

#### Mathematical Function Initialization

```cpp
// Example: โปรไฟล์ความเร็วแบบพาราโบลาสำหรับการไหลในท่อ
internalField   #codeStream
{
    code
    #{
        const vectorField& C = mesh().C();
        vectorField& U = *this;
        const scalar radius = 0.05; // รัศมีท่อ
        const scalar Umax = 2.0;    // ความเร็วสูงสุด

        forAll(C, i)
        {
            scalar r = sqrt(C[i].y()*C[i].y() + C[i].z()*C[i].z());
            scalar u_parabolic = Umax * (1.0 - sqr(r/radius));
            U[i] = vector(u_parabolic, 0, 0);
        }
    #};
};
```

> [!TIP] การใช้ `#codeStream` ช่วยให้สามารถสร้าง Field แบบ Non-uniform ได้อย่างยืดหยุ่นโดยใช้ C++ code ที่ทำงานในขณะ runtime

#### Perturbed Flow for Turbulence Development

```cpp
// Example: การเพิ่มการรบกวนแบบปั่นป่วน
internalField   #codeStream
{
    code
    #{
        const vectorField& C = mesh().C();
        vectorField& U = *this;
        const scalar Umean = 1.0;
        const scalar perturbation = 0.05; // การรบกวน 5%

        // กำหนด seed สำหรับตัวเลขสุ่มที่ทำซ้ำได้
        Random perturb(12345);

        forAll(C, i)
        {
            U[i] = vector(Umean, 0, 0)
                   + perturbation * Umean * vector(
                       perturb.scalar01() - 0.5,
                       perturb.scalar01() - 0.5,
                       perturb.scalar01() - 0.5
                   );
        }
    #};
};
```

## Pressure Field Initialization

การเริ่มต้น **Pressure Field** ต้องพิจารณาเป็นพิเศษสำหรับ **Flow Regimes** ที่แตกต่างกัน:

### Incompressible Flow (`0/p`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];  // Pa: kg/(m·s²)
internalField   uniform 101325;    // ค่าอ้างอิงความดันบรรยากาศ

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    outlet
    {
        type            fixedValue;
        value           uniform 101325; // ความดันเกจ = 0
    }
    walls
    {
        type            zeroGradient;
    }
}
```

### Compressible Flow (`0/p` for compressible solvers)

```cpp
// สำหรับการไหลแบบบีบอัดได้ ความดันสัมบูรณ์มีความสำคัญ
dimensions      [1 -1 -2 0 0 0 0];  // หน่วยความดันสัมบูรณ์
internalField   uniform 101325;    // ต้องใช้ความดันสัมบูรณ์

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 150000; // ความดันขาเข้าที่สูงขึ้น
    }
    outlet
    {
        type            fixedValue;
        value           uniform 101325; // ทางออกความดันบรรยากาศ
    }
}
```

### Comparison: Incompressible vs Compressible Pressure Initialization

| คุณสมบัติ | Incompressible Flow | Compressible Flow |
|-----------|---------------------|-------------------|
| หน่วยมิติ | `[0 2 -2 0 0 0 0]` (Pa) | `[1 -1 -2 0 0 0 0]` (Pa) |
| ค่าอ้างอิง | ความดันเกจ (Gauge) | ความดันสัมบูรณ์ (Absolute) |
| ชนิด Field | `volScalarField` | `volScalarField` |
| Boundary Type | `zeroGradient`/`fixedValue` | `fixedValue` ทั้งขาเข้า-ออก |

## Multiphase Flow Initialization

สำหรับการจำลอง **Multiphase**, **Phase Fraction Fields** ต้องให้ความสนใจเป็นพิเศษ

### Phase Fraction Field (`0/alpha.water`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      alpha.water;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];  // ไร้มิติ: สัดส่วนปริมาตร
internalField   uniform 0;        // เริ่มต้นไม่มีน้ำ

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1; // น้ำที่ทางเข้า
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
}
```

### Stratified Flow Initialization

```cpp
// Example: การไหลแบบแบ่งชั้นสองชั้น
internalField   #codeStream
{
    code
    #{
        const volScalarField& C = mesh().C().component(1); // พิกัด y
        const scalar interfaceHeight = 0.1; // ส่วนต่อประสานที่ y = 0.1 m

        forAll(C, i)
        {
            this->operator[](i) = (C[i] < interfaceHeight) ? 1.0 : 0.0;
        }
    #};
};
```


> [!INFO] **Volume of Fluid (VOF) Method**
> Phase fraction field $\alpha$ แสดงถึงสัดส่วนปริมาตรของ phase หนึ่งๆ ในแต่ละ cell:
> - $\alpha = 1$: Cell เต็มไปด้วย phase นั้น (เช่น น้ำ)
> - $\alpha = 0$: Cell ไม่มี phase นั้น (เช่น อากาศ)
> - $0 < \alpha < 1$: Cell อยู่ที่ interface ระหว่างสอง phases


## Temperature and Species Initialization

สำหรับการถ่ายเทความร้อนและการไหลแบบมีปฏิกิริยา:

### Temperature Field (`0/T`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];  // หน่วยอุณหภูมิ
internalField   uniform 300;      // อุณหภูมิเริ่มต้น 300 K

boundaryField
{
    hotWall
    {
        type            fixedValue;
        value           uniform 400; // ผนังร้อน 400 K
    }
    coldWall
    {
        type            fixedValue;
        value           uniform 280; // ผนังเย็น 280 K
    }
    inlet
    {
        type            fixedValue;
        value           uniform 320; // อุณหภูมิขาเข้า 320 K
    }
}
```

### Species Concentration Fields

สำหรับ **Reacting Flows** หรือ **Mass Transfer**:

```cpp
// Example: ความเข้มของสารละลาย (0/Y_oxygen)
dimensions      [0 0 0 0 0 0 0];  // ไร้มิติ: mass fraction
internalField   uniform 0.21;     // ออกซิเจน 21% ในอากาศ

boundaryField
{
    fuelInlet
    {
        type            fixedValue;
        value           uniform 0;    // ไม่มีออกซิเจนที่ทางเข้าเชื้อเพลิง
    }
    airInlet
    {
        type            fixedValue;
        value           uniform 0.21; // ออกซิเจนในอากาศ
    }
    walls
    {
        type            zeroGradient;  // ผนังไร้การแพร่
    }
}
```

## Best Practices for Initial Conditions

### 1. Physical Consistency

ตรวจสอบให้แน่ใจว่า Initial Conditions เป็นไปตามกฎการอนุรักษ์พื้นฐาน:

- **ข้อจำกัดของ Continuity Equation**: $\nabla \cdot \mathbf{u} = 0$ (สำหรับการไหลแบบอัดตัวไม่ได้)
- **ข้อพิจารณาเกี่ยวกับ Momentum Balance**: แรงที่สอดคล้องกับความเร็วเริ่มต้น
- **ความสัมพันธ์ทาง Thermodynamic**: สมการสภาวะสำหรับการไหลแบบบีบอัดได้

> [!WARNING] **Non-Physical Initial Conditions**
> การเริ่มต้นด้วยค่าที่ไม่สอดคล้องกันทางฟิสิกส์อาจทำให้เกิด:
> - Numerical instability
> - การลู่เข้าที่ช้าลงอย่างมาก
> - การหายไปของ solution (divergence)

### 2. Numerical Stability

- หลีกเลี่ยง **Discontinuities** ที่อาจทำให้เกิด Numerical Instability
- ใช้การเปลี่ยนผ่านที่ราบรื่นระหว่างภูมิภาคต่างๆ
- ใช้ **Smoothing Techniques** สำหรับส่วนต่อประสานที่คมชัด

### 3. Convergence Acceleration

สำหรับ **Steady-State Problems** ให้ใช้กลยุทธ์การเริ่มต้นที่ส่งเสริม Convergence อย่างรวดเร็ว:

```cpp
// Example: การเริ่มต้นด้วยการใช้ผลเฉลยการไหลแบบศักย์
internalField   #codeStream
{
    code
    #{
        // การเริ่มต้นการไหลแบบศักย์สำหรับอากาศพลศาสตร์ภายนอก
        const vectorField& C = mesh().C();
        vectorField& U = *this;
        const vector Uinf = vector(10, 0, 0); // การไหลอิสระ
        const scalar radius = 1.0;

        forAll(C, i)
        {
            scalar r = mag(C[i] - vector(0, 0, 0));
            if (r > radius)
            {
                // การไหลแบบศักย์รอบทรงกระบอก
                scalar theta = atan2(C[i].y(), C[i].x());
                scalar Ur = Uinf.x() * (1 - sqr(radius/r)) * cos(theta);
                scalar Ut = -Uinf.x() * (1 + sqr(radius/r)) * sin(theta);
                U[i] = vector(Ur*cos(theta) - Ut*sin(theta),
                            Ur*sin(theta) + Ut*cos(theta), 0);
            }
            else
            {
                U[i] = vector::zero;
            }
        }
    #};
};
```

> [!TIP] **Potential Flow Initialization**
> การเริ่มต้นด้วย Potential flow solution ให้ค่าประมาณที่ดีเยี่ยมสำหรับ:
> - Flow รอบวัตถุทรงกระบอก
> - External aerodynamics
> - การลด iteration สำหรับ steady-state solvers

### 4. Restart Capabilities

จัดโครงสร้าง Initial Conditions เพื่ออำนวยความสะดวกในการ **Simulation Restarts**:

- รวม **Time Stamps** ในชื่อไฟล์
- เก็บสำเนาสำรองของ Initialization Fields
- จัดทำเอกสาร Initialization Parameters

```bash
# ตัวอย่างการสร้างไดเรกทอรีสำหรับ restart
cp -r 0/ 0_original/
# หลังจากการจำลองสำเร็จ
cp -r 1000/ 0_restart/
```

## Error Handling and Troubleshooting

### Common Issues

| ปัญหา | สาเหตุ | วิธีแก้ไข |
|--------|--------|------------|
| **Dimensional Inconsistency** | Field Dimensions ไม่ถูกต้อง | ตรวจสอบ `[mass length time temperature moles current]` |
| **Boundary Condition Mismatch** | Initial และ Boundary Conditions ไม่เข้ากัน | ตรวจสอบความเข้ากันได้ |
| **Mass Conservation** | Initial Conditions ละเมิด Continuity | ตรวจสอบ Conservation Laws |
| **Numerical Singularities** | การหารด้วยศูนย์หรือค่าไม่กำหนด | หลีกเลี่ยงค่าพิเศษในการเริ่มต้น |

### Validation Procedures

ตรวจสอบ Initial Conditions เสมอก่อนเริ่มการจำลอง:

```bash
# ตรวจสอบไฟล์ Field สำหรับข้อผิดพลาดทางไวยากรณ์
checkMesh -case .
foamListFields -case .

# ตรวจสอบความสอดคล้องของมิติ
foamInfoDict -case .

# ตรวจสอบค่า Field ของคุณ
foamListTimes -case .
```


```mermaid
graph LR
    A["Initial Setup<br/>Check Directory Structure"] --> B["Mesh Validation<br/>checkMesh -case ."]
    B --> C["Field List<br/>foamListFields -case ."]
    C --> D["Dimensional Analysis<br/>foamInfoDict -case ."]
    D --> E{"Dimension<br/>Consistency Check"}
    E -->|Pass| F["Boundary<br/>Compatibility<br/>Verification"]
    E -->|Fail| G["Fix Dimensional<br/>Errors"]
    F --> H{"Conservation<br/>Laws Check"}
    H -->|Valid| I["Run Simulation<br/>Ready"]
    H -->|Violated| J["Adjust Initial<br/>Conditions"]
    G --> D
    J --> H

    %% Styling Definitions
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef terminator fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    class A,B,C,F,I process;
    class E,H decision;
    class G,J terminator;
```


## Summary

การเริ่มต้นตัวแปร Field อย่างเหมาะสมเป็น **พื้นฐานสำคัญ** สำหรับความสำเร็จของการจำลอง CFD โดยทำหน้าที่เป็น **รากฐาน** ที่ Numerical Solutions พัฒนาไปสู่ผลลัพธ์ที่มีความหมายทางกายภาพ

**Key Success Factors:**
- **Physical Consistency** - เป็นไปตามกฎธรรมชาติและกฎการอนุรักษ์
- **Numerical Stability** - หลีกเลี่ยงปัญหาการคำนวณและการหายไปของ solution
- **Convergence Efficiency** - ลดเวลาการคำนวณด้วยการเริ่มต้นที่เหมาะสม
- **Robust Error Handling** - ตรวจสอบและแก้ไขข้อผิดพลาดก่อนการจำลอง

การเข้าใจและใช้งาน Initial Conditions อย่างมีประสิทธิภาพจะช่วยให้สามารถ:
- เร่งการลู่เข้าของการจำลอง steady-state
- รักษาเสถียรภาพของการจำลอง transient
- ลดความเสี่ยงของ numerical divergence
- เพิ่มความน่าเชื่อถือของผลลัพธ์ CFD
