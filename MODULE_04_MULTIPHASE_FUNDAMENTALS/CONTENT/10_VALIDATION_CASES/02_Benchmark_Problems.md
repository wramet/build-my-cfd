# ปัญหาเบนช์มาร์กสำหรับการตรวจสอบความถูกต้อง (Benchmark Problems)

## บทนัย (Introduction)

ปัญหาเบนช์มาร์ก (Benchmark Problems) คือกรณีทดสอบมาตรฐานที่ใช้สำหรับประเมินความแม่นยำและความน่าเชื่อถือของ Solver ในการไหลหลายเฟส โดยจะเริ่มตั้งแต่ระดับ **ฟิสิกส์พื้นฐาน** ไปจนถึง **ระบบที่ซับซ้อนในอุตสาหกรรม** เพื่อเป็นกรอบการตรวจสอบความถูกต้องอย่างเป็นระบบสำหรับ `multiphaseEulerFoam`

แนวทางการตรวจสอบความถูกต้องแบบลำดับชั้น:

```mermaid
flowchart TD
    A[Code Verification<br/>การตรวจสอบโค้ด] --> B[Solution Verification<br/>การตรวจสอบผลเฉลย]
    B --> C[Model Validation<br/>การตรวจสอบโมเดล]
    C --> D[Predictive Capability<br/>ความสามารถในการพยากรณ์]

    A1[MMS<br/>Grid Convergence] --> A
    B1[GCI Analysis<br/>Time Step Study] --> B
    C1[Experimental Data<br/>Benchmark Cases] --> C
    D1[Blind Prediction<br/>Uncertainty Quantification] --> D
```

> [!INFO] ความสำคัญของปัญหาเบนช์มาร์ก
> ปัญหาเบนช์มาร์กช่วยให้มั่นใจว่า:
> - การ implement เชิงตัวเลขถูกต้อง
> - โมเดลฟิสิกส์แสดงปรากฏการณ์จริงได้อย่างถูกต้อง
> - การจำลองสามารถพยากรณ์ผลลัพธ์ที่เชื่อถือได้
> - ความไม่แน่นอนอยู่ในขอบเขตที่ยอมรับได้

---

## 1. การลอยตัวของฟองเดี่ยว (Single Bubble Rising)

เบนช์มาร์กนี้ใช้ทดสอบโมเดลแรงตึงผิว (Surface Tension), แรง Drag และแรง Lift ในระบบแก๊ส-ของเหลว

### 1.1 การตั้งค่าทางกายภาพ

**การตั้งค่า**: ปัญหาการลอยของฟองเดี่ยวเป็น benchmark พื้นฐานสำหรับการตรวจสอบความถูกต้องของ solver แบบ multiphase flow

การกำหนดค่าประกอบด้วยฟองอากาศเดี่ยวที่ลอยขึ้นผ่านน้ำที่สงบเนื่องจากแรง buoyancy กรณีทดสอบนี้มีคุณค่าอย่างยิ่งเพราะมันครอบคลุมปรากฏการณ์ของส่วนติดต่อที่ซับซ้อนรวมถึงผลของความตึงผิว การเคลื่อนที่ที่ขับเคลื่อนด้วยความหนาแน่น และการเปลี่ยนรูปทรง

**ข้อกำหนดโดเมน**:
- ช่วงเส้นผ่านศูนย์กลางฟอง: 2-10 มม. (ครอบคลุมระบบการเปลี่ยนรูปทรงที่แตกต่างกัน)
- โดเมนคำนวณ: 10 เส้นผ่านศูนย์กลางฟองในแต่ละทิศทางพิกัดเพื่อลดผลของผนัง
- เงื่อนไขเริ่มต้น: ฟองทรงกลมที่หยุดนิ่งในน้ำ อนุญาตให้มีการเร่งความเร็วตามธรรมชาติเนื่องจาก buoyancy

### 1.2 พารามิเตอร์ไร้มิติที่สำคัญ

พลศาสตร์ของฟองถูกควบคุมโดยพารามิเตอร์หลัก 3 ตัว:

#### 1.2.1 Eötvös Number (Eo)

อัตราส่วนระหว่างแรงลอยตัวต่อแรงตึงผิว:

$$Eo = \frac{g(\rho_l - \rho_g)d_b^2}{\sigma}$$

โดยที่:
- $g$: ความเร่งโน้มถ่วง [m/s²]
- $\rho_l$, $\rho_g$: ความหนาแน่นของของเหลวและก๊าซตามลำดับ [kg/m³]
- $d_b$: เส้นผ่านศูนย์กลางเทียบเท่าของฟอง [m]
- $\sigma$: ความตึงผิว [N/m]

#### 1.2.2 Bubble Reynolds Number (Re_b)

อัตราส่วนระหว่างแรงเฉื่อยต่อแรงหนืด:

$$Re_b = \frac{\rho_l u_t d_b}{\mu_l}$$

โดยที่:
- $u_t$: ความเร็วลอยขั้นสุดท้าย [m/s]
- $\mu_l$: ความหนืดไดนามิกของของเหลว [Pa·s]

#### 1.2.3 Morton Number (Mo)

ระบุคุณสมบัติของของไหลโดยไม่ขึ้นกับขนาดฟอง:

$$Mo = \frac{g\mu_l^4(\rho_l - \rho_g)}{\rho_l^2 \sigma^3}$$

### 1.3 ผลลัพธ์ที่คาดหวังและสหสัมพันธ์การตรวจสอบความถูกต้อง

**สหสัมพันธ์ความเร็วลอยขั้นสุดท้าย**:

การตรวจสอบความถูกต้องของ benchmark ขึ้นอยู่กับสหสัมพันธ์การทดลองที่ได้รับการยอมรับ โดยเฉพาะสหสัมพันธ์ของ **Grace et al. (1976)** สำหรับความเร็วลอยขั้นสุดท้ายของฟอง:

$$u_t = \frac{\mu_l}{\rho_l d_b} m^{m-1} Re_b$$

โดยที่เลขชี้กำลัง $m$ และจำนวน Reynolds $Re_b$ เป็นฟังก์ชันของจำนวน Eötvös และ Morton สหสัมพันธ์นี้ให้ความเร็วลอยขั้นสุดท้ายที่ทำนายได้ในระบบรูปทรงฟองที่แตกต่างกันและได้รับการตรวจสอบความถูกต้องอย่างกว้างขวางกับข้อมูลการทดลอง

สำหรับวัตถุประสงค์การตรวจสอบความถูกต้อง ผลลัพธ์การจำลองควรถูกเปรียบเทียบกับ:

1. **ความเร็วขั้นสุดท้าย**: เปรียบเทียบความเร็วลอยสถานะคงที่กับสหสัมพันธ์ของ Grace
2. **รูปทรงฟอง**: การเปรียบเทียบเชิงคุณภาพกับแผนที่ระบบการทดลอง
3. **เสถียรภาพเส้นทาง**: ประเมินว่าฟองเคลื่อนที่เป็นเส้นตรง แบบสลับซิกแซก หรือเป็นเกลียวหรือไม่

### 1.4 การนำไปใช้งานใน OpenFOAM

#### 1.4.1 การตั้งค่าเงื่อนไขเริ่มต้น

```cpp
// 0/U (ความเร็วเริ่มต้น - ฟองหยุดนิ่ง)
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform 0;

// 0/alpha.gas (ส่วนของเฟสเริ่มต้น)
dimensions      [0 0 0 0 0 0 0];
internalField   uniform 0;

// เพิ่มการกำหนดค่าเริ่มต้นฟองทรงกลม
const Vector<double> bubbleCenter(0.05, 0.05, 0.05);
const scalar bubbleRadius = 0.005;  // 5 มม.

forAll(alphaGas, celli)
{
    const Vector<double>& cellCenter = mesh.C()[celli];
    scalar r = mag(cellCenter - bubbleCenter);

    if (r <= bubbleRadius)
    {
        alphaGas[celli] = 1.0;
    }
}
```

สำหรับการเริ่มต้นที่ราบรื่นยิ่งขึ้น (smooth initialization) ใช้ฟังก์ชัน hyperbolic tangent:

```cpp
// Smooth initialization โดยใช้ tanh
forAll(alphaGas, celli)
{
    const Vector<double>& cellCenter = mesh.C()[celli];
    scalar r = mag(cellCenter - bubbleCenter);
    scalar cellSize = pow(mesh.V()[celli], 1.0/3.0);

    // Smooth initialization โดยใช้ tanh
    alphaGas[celli] = 0.5 * (1 - tanh((r - bubbleRadius) / (0.5 * cellSize)));
}
```

#### 1.4.2 การกำหนดค่า Solver

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Solver** | `multiphaseEulerFoam` หรือ `interFoam` | ขึ้นอยู่กับระบบการไหล |
| **โมเดลความตึงผิว** | `CSF` (Continuum Surface Force) | การจำลองแรงความตึงผิว |
| **การบีบอัดส่วนติดต่อ** | เปิดใช้งาน | การทำให้ส่วนติดต่อคมขึ้นเชิงตัวเลข |
| **การกำหนดเวลา** | Courant number < 0.3 | ควบคุมเสถียรภาพส่วนติดต่อ |

#### 1.4.3 การกำหนดค่าคุณสมบัติการขนส่ง

```cpp
// constant/transportProperties
phases (gas liquid);

gas
{
    transportModel  Newtonian;
    nu              [0 2 -1 0 0 0 0] 1.5e-5;
    rho             [1 -3 0 0 0 0 0] 1.2;
}

liquid
{
    transportModel  Newtonian;
    nu              [0 2 -1 0 0 0 0] 1.0e-6;
    rho             [1 -3 0 0 0 0 0] 1000;
    sigma           [1 0 -2 0 0 0 0] 0.072;
}

// constant/phaseProperties
phaseModel gas
{
    type            incompressible;
    diameterModel   constant;
    d               0.004;
    residualAlpha   1e-6;
}
```

### 1.5 เมตริกการตรวจสอบความถูกต้องและการประมวลผลหลัง

#### 1.5.1 โค้ดการตรวจสอบความถูกต้องอย่างครอบคลุม

```cpp
// คำนวณการติดตามความเร็วลอยของฟอง
scalar bubbleVelocity = average(U_gas.component(2));  // คอมโพเนนต์ z

// คำนวณพารามิเตอร์ไร้มิติสำหรับสหสัมพันธ์
scalar Eo = (rho_liquid - rho_gas) * 9.81 * pow(bubbleRadius*2, 2) / sigma;
scalar Mo = 9.81 * pow(mu_liquid, 4) * (rho_liquid - rho_gas) /
          (pow(rho_liquid, 2) * pow(sigma, 3));

// คำนวณความเร็วลอยขั้นสุดท้ายเชิงทฤษฎีโดยใช้สหสัมพันธ์ของ Grace
scalar u_t_corr = calculateGraceCorrelation(Eo, Mo, bubbleRadius*2);

// คำนวณเมตริกการตรวจสอบความถูกต้อง
scalar velocityError = mag(bubbleVelocity - u_t_corr) / u_t_corr;
Info << "Bubble velocity error: " << velocityError * 100 << "%" << endl;
Info << "Simulated velocity: " << bubbleVelocity << " m/s" << endl;
Info << "Theoretical velocity: " << u_t_corr << " m/s" << endl;

// เมตริกรูปทรงฟองเพิ่มเติม
scalar bubbleVolume = sum(alphaGas * mesh.V());
scalar equivalentDiameter = pow(6 * bubbleVolume / constant::mathematical::pi, 1.0/3.0);
scalar aspectRatio = calculateBubbleAspectRatio(alphaGas);
```

#### 1.5.2 การสกัดคุณสมบัติฟอง

```cpp
// ฟังก์ชันสำหรับดึงคุณสมบัติฟอง
void extractBubbleProperties()
{
    // คำนวณจุดศูนย์กลางมวลฟอง
    scalar V_bubble = 0.0;
    Vector<double> r_centroid(0, 0, 0);

    forAll(alphaGas, celli)
    {
        if (alphaGas[celli] > 0.5)
        {
            V_bubble += mesh.V()[celli] * alphaGas[celli];
            r_centroid += mesh.C()[celli] * mesh.V()[celli] * alphaGas[celli];
        }
    }

    r_centroid /= V_bubble;

    // คำนวณความเร็วการขึ้น
    scalar z_velocity = U_gas.component(2).weightedAverage(alphaGas);

    // คำนวณพารามิเตอร์รูปร่างฟอง
    scalar aspectRatio = calculateAspectRatio(alphaGas);

    Info << "คุณสมบัติฟอง:" << nl
         << "  ปริมาตร: " << V_bubble << " ลบ.ม." << nl
         << "  จุดศูนย์กลาง: " << r_centroid << " ม." << nl
         << "  ความเร็วการขึ้น: " << z_velocity << " ม./วิ." << nl
         << "  อัตราส่วนภาพ: " << aspectRatio << endl;
}
```

### 1.6 เกณฑ์การยอมรับ

| Metric | Acceptance Criteria | Application Range |
|--------|---------------------|-------------------|
| **ความคลาดเคลื่อนความเร็ว** | < 10% | ฟองทรงกลม |
| **ความคลาดเคลื่อนความเร็ว** | < 15% | ฟองที่เปลี่ยนรูป |
| **การรักษารูปทรง** | ความคลาดเคลื่อน < 2% | การอนุรักษ์ปริมาตร |
| **การบรรจบกันของเกรด** | แสดงผล | การละเอียดของ mesh |

---

## 2. การไหลแบบแยกชั้น (Stratified Two-Phase Flow)

ใช้ทดสอบความสามารถในการจับภาพการแยกเฟสที่ขับเคลื่อนโดยแรงโน้มถ่วงและการแลกเปลี่ยนโมเมนตัมที่อินเตอร์เฟซในท่อแนวนอน

### 2.1 การกำหนดค่าทางกายภาพ

**การตั้งค่า**: การไหลแบบ stratified ในท่อแนวนอนเป็นรูปแบบการไหลแบบสองเฟสพื้นฐานที่พบได้ในแอปพลิเคชันอุตสาหกรรมหลายแห่ง โดยเฉพาะในการขนส่งในท่อของส่วนผสมแก๊ส-ของเหลว

benchmark นี้ตรวจสอบความสามารถของ solver ในการจับภาพการจัดเรียงแบบ stratified ที่ขับเคลื่อนโดยแรงโน้มถ่วงและการแลกเปลี่ยนโมเมนตัมของส่วนติดต่อ

**พารามิเตอร์เรขาคณิตและการดำเนินงาน**:
- **การกำหนดค่าท่อ**: ท่อวงกลมแนวนอน
- **เส้นผ่านศูนย์กลาง**: 0.05 ม. (มาตรฐานอุตสาหกรรม)
- **ความยาว**: 10 เส้นผ่านศูนย์กลาง (0.5 ม.) เพื่อให้แน่ใจว่าการไหลพัฒนาอย่างเต็มที่
- **ช่วงความเร็วแก๊ส**: 1-10 ม./วินาที (ครอบคลุมการไหลแก๊สจากแบบ laminar ถึง turbulent)
- **ช่วงความเร็วของเหลว**: 0.1-1 ม./วินาที (เป็นตัวแทนของเงื่อนไขการดำเนินงานจริง)

**โซนการพัฒนาการไหล**:
1. **โซนทางเข้า**: การพัฒนาการไหลและการสร้างรูปแบบแบบ stratified
2. **โซนการพัฒนา**: การทำให้เสถียรของส่วนติดต่อและโปรไฟล์ความเร็ว
3. **โซนการวัด**: การไหลแบบ stratified ที่พัฒนาอย่างเต็มที่สำหรับการตรวจสอบความถูกต้อง

### 2.2 พารามิเตอร์ไร้มิติและระบบการไหล

#### 2.2.1 Froude Number (Fr)

$$Fr = \frac{U_g}{\sqrt{gD}}$$

พารามิเตอร์นี้ระบุแนวโน้มของเฟสแก๊สที่จะเอาชนะการตกตะกอนด้วยแรงโน้มถ่วงและมีอิทธิพลต่อรูปร่างของส่วนติดต่อ

#### 2.2.2 Lockhart-Martinelli Parameter (X)

อัตราส่วนของการไล่ระดับความดันสำหรับเฟสแต่ละเฟส:

$$X = \sqrt{\frac{(dP/dx)_l}{(dP/dx)_g}}$$

พารามิเตอร์นี้เป็นพื้นฐานสำหรับการทำนายการเปลี่ยนรูปแบบการไหลและการลดความดันในการไหลแบบ stratified

#### 2.2.3 การจำแนกระบบการไหล

| Flow Regime | Gas Velocity | Interface Characteristics |
|-------------|-------------|---------------------------|
| **Stratified เรียบ** | ต่ำ | ส่วนติดต่อสงบ |
| **Stratified แบบคลื่น** | สูงขึ้น | คลื่นส่วนติดต่อ |
| **การเริ่มต้นการไหลแบบ Slug** | สูงมาก | การเปลี่ยนไปสู่รูปแบบไม่ต่อเนื่อง |

### 2.3 โมเดลเชิงทฤษฎีสำหรับการตรวจสอบความถูกต้อง

#### 2.3.1 โมเดล Taitel-Dukler สำหรับความสูงของเหลวสมดุล

โมเดลนี้ให้การทำนายเชิงวิเคราะห์สำหรับความสูงของชั้นของเหลวในการไหลแบบ stratified โดยยึดตามสมดุลโมเมนตัม:

$$\frac{h_l}{D} = f(X, Fr_g, Fr_l)$$

ฟังก์ชัน $f$ เชื่อมโยงความสูงของเหลวไร้มิติกับพารามิเตอร์ Lockhart-Martinelli และจำนวน Froude ของเฟสผ่านสมการเชิงทาย (transcendental equations) ที่ซับซ้อนที่แก้ด้วยวิธีวนซ้ำ

#### 2.3.2 การทำนายการลดความดัน

การลดความดันแบบสองเฟสสามารถทำนายได้โดยใช้แนวทางตัวคูณเฟสแก๊ส:

$$\frac{dP}{dx} = \Phi_g^2 \left(\frac{dP}{dx}\right)_g$$

โดยที่ $\Phi_g$ คือตัวคูณเฟสแก๊สที่คำนึงถึงการมีอยู่ของเฟสของเหลว

### 2.4 รายละเอียดการ Implement ใน OpenFOAM

#### 2.4.1 กลยุทธ์ Computational Mesh

```cpp
// การละเอียดของ mesh ใกล้ส่วนติดต่อสำหรับการจับภาพที่แม่นยำ
// การละเอียดชั้นขอบเขตใกล้ผนัง
aspectRatio 1.0;  // รักษาคุณภาพของ mesh
```

#### 2.4.2 เงื่อนไขเริ่มต้น

```cpp
// กำหนดค่าเริ่มต้นการกำหนดค่าแบบ stratified
scalar gasHeightFraction = 0.7;  // การประเมินเริ่มต้น

forAll(alphaLiquid, celli)
{
    const vector& cellCenter = mesh.C()[celli];
    scalar yCoord = cellCenter.y();

    if (yCoord < gasHeightFraction * pipeRadius)
    {
        alphaLiquid[celli] = 0.0;  // โซนแก๊ส
    }
    else
    {
        alphaLiquid[celli] = 1.0;  // โซนของเหลว
    }
}
```

### 2.5 เมตริกการตรวจสอบความถูกต้องและการประมวลผลหลัง

#### 2.5.1 โค้ดการตรวจสอบความถูกต้องอย่างครอบคลุม

```cpp
// คำนวณพารามิเตอร์การไหลแบบ stratified
scalar D = 0.05;  // เส้นผ่านศูนย์กลางท่อ
scalar g = 9.81;  // ความเร่งโน้มถ่วง
scalar U_gas = 5.0;   // ความเร็วแก๊สต่อผิว
scalar U_liquid = 0.5; // ความเร็วของเหลวต่อผิว

// คำนวณพารามิเตอร์ไร้มิติ
scalar Fr_gas = U_gas / sqrt(g * D);
scalar Fr_liquid = U_liquid / sqrt(g * D);

// คำนวณความสูงของเหลวเชิงทฤษฎีโดยใช้โมเดล Taitel-Dukler
scalar hl_D_theory = calculateTaitelDuklerHeight(Fr_gas, Fr_liquid);

// ดึงความสูงของเหลวจากการจำลอง
scalar liquidHeight = calculateLiquidHeight(alpha_liquid);
scalar liquidHeightFraction = liquidHeight / D;

// ความคลาดเคลื่อนในการทำนายความสูง
scalar heightError = mag(liquidHeightFraction - hl_D_theory) / hl_D_theory;
Info << "Liquid height error: " << heightError * 100 << "%" << endl;

// การตรวจสอบความดันการไล่ระดับ
scalar dp_dx_sim = calculatePressureGradient(p);
scalar dp_dx_theory = calculateTheoreticalPressureDrop(U_gas, U_liquid, D);

scalar pressureDropError = mag(dp_dx_sim - dp_dx_theory) / dp_dx_theory;
Info << "Pressure drop error: " << pressureDropError * 100 << "%" << endl;

// การวิเคราะห์ความคลื่นของส่วนติดต่อ
scalar interfaceWaviness = calculateInterfaceWaviness(alpha_liquid);
Info << "Interface waviness parameter: " << interfaceWaviness << endl;
```

#### 2.5.2 การวิเคราะห์ความสูงของเหลว

```cpp
// ฟังก์ชันสำหรับคำนวณความสูงของเหลว
class stratifiedFlowAnalyzer
{
private:
    const fvMesh& mesh_;
    const volScalarField& alphaGas_;
    const volVectorField& UGas_;
    const volVectorField& ULiquid_;

public:
    scalar calculateLiquidHeight()
    {
        scalar liquidHeight = 0.0;
        scalar D = 0.05;  // เส้นผ่านศูนย์กลางท่อ

        // ผสานสัดส่วนปริมาตรของเหลวในครึ่งล่าง
        forAll(alphaGas_, celli)
        {
            const Vector<double>& cellCenter = mesh_.C()[celli];
            scalar y = cellCenter.y();

            if (y < D/2)  // ครึ่งล่างของท่อ
            {
                liquidHeight += (1.0 - alphaGas_[celli]) * mesh_.V()[celli];
            }
        }

        liquidHeight /= (0.05 * 0.05 * 10.0);  // ทำให้เป็นมาตรฐานตามหน้าตัดท่อ

        return liquidHeight;
    }
};
```

### 2.6 เกณฑ์การยอมรับ

- **การทำนายความสูงของเหลว**: ความคลาดเคลื่อน < 5% เทียบกับโมเดล Taitel-Dukler
- **การลดความดัน**: ความคลาดเคลื่อน < 10% เทียบกับสหสัมพันธ์
- **เสถียรภาพส่วนติดต่อ**: สังเกตรูปแบบคลื่นทางกายภาพ

---

## 3. การจำลองเตียงไหลฟลูอิดไดซ์ (Fluidized Bed)

เบนช์มาร์กที่ซับซ้อนสำหรับระบบแก๊ส-ของแข็ง ทดสอบแรง Drag และปฏิสัมพันธ์ระหว่างอนุภาค

### 3.1 การกำหนดค่าทางกายภาพ

**การตั้งค่า**: Fluidized beds เป็นระบบ multiphase ที่ซับซ้อนซึ่งอนุภาคของแข็งถูกแขวนอยู่โดยแก๊สที่ไหลขึ้น สร้างพฤติกรรมเหมือนของไหล

benchmark นี้ท้าทายความสามารถของ solver ในการจับภาพปฏิสัมพันธ์อนุภาค-อนุภาค การ coupling แก๊ส-ของแข็ง และการเปลี่ยนระหว่างระบบ fixed bed, fluidized, และ transport

**โดเมนทางกายภาพและพารามิเตอร์**:
- **เรขาคณิตของเตียง**: หมวดหมู่สี่เหลี่ยมสำหรับประสิทธิภาพการคำนวณ
- **มิติ**: 0.3 × 0.3 × 2.0 ม. (ความกว้าง × ความลึก × ความสูง)

**คุณสมบัติอนุภาค**:

| Property | Value | Description |
|----------|-------|-------------|
| **เส้นผ่านศูนย์กลาง** | 500 μm | เป็นเรื่องปกติสำหรับแอปพลิเคชันอุตสาหกรรม |
| **ความหนาแน่น** | 2500 กก./ม³ | เป็นตัวแทนของทรายหรือวัสดุที่คล้ายกัน |
| **รูปร่าง** | ทรงกลม | มีค่าสัมประสิทธิ์การกระเด้งที่ระบุ |

**คุณสมบัติแก๊ส**:
- **ของไหล**: อากาศในสภาวะบรรยากาศ
- **อุณหภูมิ**: 293 K (20°C)
- **ความดัน**: 1 แอตมอสเฟียร์ (สภาวะมาตรฐาน)

### 3.2 จุดดำเนินงานและระบบที่สำคัญ

#### 3.2.1 ความเร็ว Fluidization ขั้นต่ำ ($U_{mf}$)

ความเร็ววิกฤตนี้ทำเครื่องหมายการเปลี่ยนจากการดำเนินงาน fixed bed ไปเป็น fluidized bed มันถูกกำหนดโดยความสมดุลระหว่างแรงลากและแรงโน้มถ่วงบนอนุภาค

#### 3.2.2 ช่วงความเร็วการดำเนินงาน

| Operating Range | Velocity Ratio | Flow Behavior |
|-----------------|---------------|----------------|
| **Fluidization ขั้นต่ำ** | $U_{op} = U_{mf}$ | จุดเริ่มต้นของ fluidization |
| **การดำเนินงานที่เหมาะสม** | $U_{op} = (1.5-3.0) \cdot U_{mf}$ | fluidization ที่เสถียร |
| **ระบบการขนส่ง** | $U_{op} > 5 \cdot U_{mf}$ | การพาอนุภาค |

### 3.3 พื้นฐานทางทฤษฎีและการทำนาย

#### 3.3.1 สมการ Ergun สำหรับการลดความดัน Fixed Bed

ก่อน fluidization การลดความดันผ่านชั้นอนุภาคจะตามสมการ Ergun:

$$\frac{\Delta P}{L} = \frac{150(1-\alpha_{mf})^2\mu_g U_{mf}}{\alpha_{mf}^3 d_p^2} + \frac{1.75(1-\alpha_{mf})\rho_g U_{mf}^2}{\alpha_{mf}^3 d_p}$$

- $\alpha_{mf}$: void fraction ที่จุด fluidization ขั้นต่ำ (โดยทั่วไปอยู่รอบ 0.4-0.45 สำหรับอนุภาคทรงกลม)

#### 3.3.2 สมดุลแรงที่จุด Fluidization ขั้นต่ำ

ที่จุด fluidization ขั้นต่ำ แรงลากขึ้นจะสมดุลกับน้ำหนักสุทธิของอนุภาค:

$$\Delta P = (\rho_s - \rho_g)(1-\alpha_{mf})gL$$

เงื่อนไขนี้ให้ฐานทฤษฎีสำหรับการคำนวณ $U_{mf}$ และเป็นจุดตรวจสอบความถูกต้องที่สำคัญ

### 3.4 การ Implement ใน OpenFOAM

#### 3.4.1 การตั้งค่าโมเดลสองเฟส Eulerian-Eulerian

```cpp
// constant/phaseProperties
phases (solid gas);

// คุณสมบัติเฟสของแข็ง
solid
{
    rho             2500;     // ความหนาแน่นอนุภาค [kg/m³]
    d               5e-4;     // เส้นผ่านศูนย์กลางอนุภาค [m]
    maxAlpha        0.64;     // ขีดจำกัดการบรรจุสูงสุด
    e               0.9;      // ค่าสัมประสิทธิ์การกระเด้งของอนุภาค
    alpha0          0.6;      // ปริมาตรของแข็งเริ่มต้น
}

// คุณสมบัติเฟสแก๊ส
gas
{
    rho             1.2;      // ความหนาแน่นอากาศ [kg/m³]
    mu              1.8e-5;   // ความหนืดไดนามิกของอากาศ [Pa·s]
    Cp              1005;     // ความจุความร้อนจำเพาะ [J/kg·K]
    kappa           0.025;    // สภาพนำความร้อน [W/m·K]
}

// การกำหนดค่าโมเดลแรงลาก
dragModel
{
    type            GidaspowErgunWenYu;
    alphap          0.6;      // ขีดจำกัดการบรรจุ
}
```

#### 3.4.2 เงื่อนไขขอบเขต

- **ทางเข้า**: ความเร็วแก๊สสม่ำเสมอพร้อมพารามิเตอร์ความปั่นป่วนที่ระบุ
- **ทางออก**: ทางออกความดันพร้อมการป้องกันการไหลย้อนกลับ
- **ผนัง**: ไม่มีการไถลสำหรับเฟสแก๊ส, wall functions ที่เหมาะสมสำหรับความปั่นป่วน

### 3.5 เงื่อนไขการดำเนินงานและการคำนวณ

```cpp
// คำนวณความเร็ว fluidization ขั้นต่ำโดยใช้วิธีการแก้ปัญหาวนซ้ำ
scalar rho_solid = 2500;  // kg/m³
scalar rho_gas = 1.2;     // kg/m³
scalar dp = 5e-4;         // เส้นผ่านศูนย์กลางอนุภาค [m]
scalar mu_gas = 1.8e-5;   // ความหนืดไดนามิกของแก๊ส [Pa·s]
scalar g = 9.81;          // ความเร่งโน้มถ่วง [m/s²]
scalar alpha_mf = 0.4;    // Void fraction ที่จุด fluidization ขั้นต่ำ

// การคำนวณแบบวนซ้ำของ U_mf
scalar Umf = calculateMinimumFluidizationVelocity(rho_solid, rho_gas,
                                               dp, mu_gas, alpha_mf);

// ตั้งค่าเงื่อนไขการดำเนินงาน
scalar Uop = 2.0 * Umf;  // การดำเนินงานที่ 2x fluidization ขั้นต่ำ

Info << "Minimum fluidization velocity: " << Umf << " m/s" << endl;
Info << "Operating velocity: " << Uop << " m/s" << endl;
Info << "Operating ratio (Uop/Umf): " << Uop/Umf << endl;
```

### 3.6 เมตริกการตรวจสอบความถูกต้องอย่างครอบคลุม

#### 3.6.1 พารามิเตอร์การตรวจสอบความถูกต้องที่สำคัญ

```cpp
// การคำนวณอัตราส่วนการขยายตัวของเตียง
scalar initialBedHeight = 1.0;  // ความสูงเตียงแบบแบ่งเริ่มต้น [m]
scalar finalBedHeight = calculateBedHeight(alpha_solid);
scalar expansionRatio = finalBedHeight / initialBedHeight;

// การตรวจสอบความถูกต้องของความดัน
scalar inletPressure = average(p.boundaryField()[inletID]);
scalar outletPressure = average(p.boundaryField()[outletID]);
scalar deltaP = inletPressure - outletPressure;

// การลดความดันเชิงทฤษฎีที่จุด fluidization ขั้นต่ำ
scalar theoreticalDeltaP = (rho_solid - rho_gas) * (1 - alpha_mf) *
                          9.81 * finalBedHeight;

// การวิเคราะห์การกระจายตัวของ voidage เตียง
scalar averageVoidage = 1.0 - average(alpha_solid);
scalar maxVoidage = max(alpha_solid);
scalar minVoidage = min(alpha_solid);

// รูปแบบการผสมและการไหลเวียนของของแข็ง
scalar circulationIntensity = calculateSolidCirculation(U_solid, alpha_solid);
scalar mixingIndex = calculateMixingIndex(alpha_solid);

// ผลลัพธ์การตรวจสอบความถูกต้อง
scalar pressureDropError = mag(deltaP - theoreticalDeltaP) / theoreticalDeltaP;
Info << "Pressure drop error: " << pressureDropError * 100 << "%" << endl;
Info << "Bed expansion ratio: " << expansionRatio << endl;
Info << "Average voidage: " << averageVoidage << endl;
Info << "Solid circulation intensity: " << circulationIntensity << endl;

// ปริมาณเฉลี่ยตามเวลาสำหรับ fluidization แบบฟอง
if (runTime.timeIndex() > averagingStartTime)
{
    scalar voidageFluctuation = calculateVoidageFluctuation(alpha_solid);
    scalar bubbleFrequency = calculateBubbleFrequency(alpha_solid);

    Info << "Voidage fluctuation intensity: " << voidageFluctuation << endl;
    Info << "Bubble passage frequency: " << bubbleFrequency << " Hz" << endl;
}
```

#### 3.6.2 การคำนวณอัตราส่วนการขยายตัวของเตียง

```cpp
// คำนวณอัตราส่วนการขยายเตียง
scalar calculateBedExpansion()
{
    scalar bedTop = 0.0;

    for (scalar z = 0.0; z < 1.0; z += 0.001)
    {
        scalar localSolidFraction = 0.0;
        label nCells = 0;

        forAll(mesh.cells(), celli)
        {
            const Vector<double>& cellCenter = mesh.C()[celli];
            if (abs(cellCenter.z() - z) < 0.005)
            {
                localSolidFraction += alphaSolid[celli];
                nCells++;
            }
        }

        localSolidFraction /= nCells;

        if (localSolidFraction < 0.01)  // ยอดเตียงที่สัดส่วนของแข็ง < 1%
        {
            bedTop = z;
            break;
        }
    }

    return bedTop / 0.5;  // หารด้วยความสูงเตียงเริ่มต้น
}
```

### 3.7 เกณฑ์การยอมรับการตรวจสอบความถูกต้อง

| Metric | Acceptance Criteria | Description |
|--------|---------------------|-------------|
| **การลดความดันที่ $U_{mf}$** | ความคลาดเคลื่อน < 10% | เทียบกับสมการ Ergun |
| **การขยายตัวของเตียง** | ความคลาดเคลื่อน < 15% | เทียบกับสหสัมพันธ์การทดลอง |
| **ความเร็ว fluidization ขั้นต่ำ** | ความคลาดเคลื่อน < 20% | ในการทำนาย |
| **การเปลี่ยนระบบการไหล** | การระบุถูกต้อง | จุดเริ่มต้นของ fluidization |

---

## 4. ความไม่เสถียรแบบ Rayleigh-Taylor (Rayleigh-Taylor Instability)

ใช้ทดสอบการผสมกันของของไหลต่างความหนาแน่นภายใต้แรงโน้มถ่วง (ของหนักอยู่บนของเบา)

### 4.1 การตั้งค่าปัญหา

ความไม่เสถียรแบบ Rayleigh-Taylor เกิดขึ้นเมื่อของไหลที่หนักกว่าวางอยู่เหนือของไหลที่เบากว่าในสนามความโน้มถ่วง

- **โดเมนการคำนวณ**: $L_x \times L_y = 1.0 \text{ m} \times 2.0 \text{ m}$
- **การรบกวนอินเตอร์เฟสเริ่มต้น**: $\eta(x, t=0) = a_0 \cos(2\pi x/\lambda)$
- **แอมพลิจูดการรบกวน**: $a_0 = 0.01 \text{ m}$
- **ความยาวคลื่น**: $\lambda = 0.25 \text{ m}$
- **อัตราส่วนความหนาแน่น**: $\rho_2/\rho_1 = 3.0$
- **ความตึงผิว**: $\sigma = 0.01 \text{ N/m}$

### 4.2 พารามิเตอร์ไร้มิติ

- **Atwood Number (A)**: $A = (\rho_2 - \rho_1)/(\rho_2 + \rho_1)$
- **Linear Growth Rate ($\omega$)**: $\omega = \sqrt{A g k - \sigma k^3/\rho_m}$

โดยที่:
- $k = 2\pi/\lambda$ คือเลขคลื่น (wavenumber)
- $\rho_m = \rho_1 + \rho_2$ คือความหนาแน่นรวม

### 4.3 ผลเฉลยเชิงวิเคราะห์สำหรับการเติบโตในช่วงเวลาแรก

อัตราการเติบโตเชิงเส้นจากทฤษฎีการไหลศักย์:

$$\omega = \sqrt{A g k - \sigma k^3/\rho_m}$$

### 4.4 การ Implement ใน OpenFOAM

```cpp
// การตั้งค่าเริ่มต้นสำหรับความไม่เสถียร Rayleigh-Taylor
dimensionedScalar a0("a0", dimLength, 0.01);
dimensionedScalar lambda("lambda", dimLength, 0.25);

// การรบกวนอินเตอร์เฟสเริ่มต้น
volScalarField alpha1
(
    IOobject
    (
        "alpha1",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    0.5 * (1.0 + tanh((mesh.C().component(1) - 1.0 - a0*cos(2.0*pi*mesh.C().component(0)/lambda))/(0.01)))
);

// การคำนวณความเร็วเชิงเส้นจากทฤษฎี
dimensionedScalar Atwood("Atwood", dimless, (rho2.value() - rho1.value())/(rho2.value() + rho1.value()));
dimensionedScalar k("k", dimless, 2.0*pi/lambda.value());
dimensionedScalar omega = sqrt(Atwood*9.81*k - sigma.value()*pow(k,3)/rho1.value());
```

### 4.5 ปริมาณการตรวจสอบความถูกต้อง

- **การวิวัฒนาการของตำแหน่งอินเตอร์เฟส**: $\eta(x,t)$
- **อัตราการเติบโตของโซนการผสม**: $\frac{\mathrm{d}h}{\mathrm{d}t} \propto t^\theta$
- **การกระจายของพลังงานจลน์ความปั่นป่วน**
- **การวิวัฒนาการของ enstrophy**: $\langle \omega^2 \rangle(t)$

---

## 5. เกณฑ์การยอมรับและสรุปภาพรวม (Acceptance Criteria)

### 5.1 เกณฑ์การยอมรับระดับต่างๆ

| ระดับ (Level) | ตัวชี้วัด (Metric) | เกณฑ์การยอมรับ |
|-------|------|---------------------|
| **Code Verification** | Mass/Energy Balance | $< 10^{-10}$ |
| **Solution Verification** | GCI (Global) | $< 5\%$ |
| **Model Validation** | NRMSE (Engineering) | $< 15\%$ |
| **Model Validation** | R² (Sim vs Exp) | $> 0.8$ |

### 5.2 สรุปการประยุกต์ใช้

การตรวจสอบผ่านปัญหาเบนช์มาร์กเหล่านี้ช่วยสร้างความมั่นใจว่า Solver และ Closure models ที่เลือกใช้นั้นทำงานได้อย่างถูกต้องและเชื่อถือได้สำหรับการออกแบบทางวิศวกรรม

> [!TIP] แนวทางการเลือก Benchmark
>
> - **เริ่มต้นด้วยฟิสิกส์พื้นฐาน**: Single Bubble Rising
> - **ดำเนินต่อไปยังระบบที่ซับซ้อนขึ้น**: Stratified Flow → Fluidized Bed
> - **ตรวจสอบระดับการบรรจบกันของ Mesh** ในแต่ละกรณี
> - **เปรียบเทียบกับข้อมูลทดลอง** เมื่อมี available
> - **บันทึกผลลัพธ์อย่างละเอียด** สำหรับการอ้างอิงในอนาคต

*อ้างอิง: วิเคราะห์ตามผลการทดลองของ Grace et al. (1976), ทฤษฎี Taitel-Dukler สำหรับการไหลหลายเฟส, และสมการ Ergun สำหรับ Fluidized Beds*
