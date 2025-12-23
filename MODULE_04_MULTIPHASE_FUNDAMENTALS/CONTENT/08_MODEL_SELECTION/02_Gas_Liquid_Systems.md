# ระบบก๊าซ-ของเหลว (Gas-Liquid Systems)

## 1. บทนำ (Introduction)

ระบบก๊าซ-ของเหลวเป็นหัวใจสำคัญในงานวิศวกรรมเคมีและโรงไฟฟ้า พฤติกรรมของการไหลถูกกำหนดโดยแรงลอยตัว (Buoyancy) และการเสียรูปของฟองอากาศ (Bubble deformation)

> [!INFO] จุดสำคัญของระบบ Gas-Liquid
> ระบบนี้มีอัตราส่วนความหนาแน่นสูง ($\rho_l/\rho_g \approx 1000:1$) ทำให้แรงลอยตัวมีบทบาทสำคัญและต้องการความระมัดระวังเป็นพิเศษในการจำลองเชิงตัวเลข

---

## 2. การจำแนกตามระบอบการไหล (Flow Regimes)

### 2.1 การไหลแบบฟอง (Bubbly Flow, $\alpha_g < 0.3$)

ฟองอากาศกระจายตัวเป็นอิสระในของเหลว แบ่งตามขนาดดังนี้:

#### ฟองขนาดเล็ก ($Eo < 1$, $We < 1$)

ฟองก๊าซขนาดเล็กทรงกลมเป็นรีจีมที่ง่ายที่สุดในการไหลของก๊าซ-ของเหลว

**ลักษณะเฉพาะ:**
- **จำนวน Eötvös** $Eo < 1$: แรงตึงผิวมีอำนาจเหนือกว่าแรงลอยตัว
- **จำนวน Weber** $We < 1$: แรงเฉื่อยไม่เพียงพอที่จะทำให้ฟองก๊าศเปลี่ยนรูป
- รูปทรงกลมเกือบสมบูรณ์แบบและการเปลี่ยนรูปต่ำ

**สมการควบคุมการเคลื่อนที่:**
$$\mathbf{f}_D = \frac{1}{8} C_D \rho_l \pi d^2 |\mathbf{u}_g - \mathbf{u}_l| (\mathbf{u}_g - \mathbf{u}_l)$$

**สัมประสิทธิ์การลากต้าน** $C_D$ ใช้สหสัมพันธ์ Schiller-Naumann:
$$C_D = \begin{cases}
24(1 + 0.15Re_g^{0.687})/Re_g & \text{for } Re_g < 1000 \\
0.44 & \text{for } Re_g \geq 1000
\end{cases}$$

**การถ่ายเทความร้อน:**
$$Nu = 2 + 0.6Re^{1/2}Pr^{1/3}$$

```cpp
// OpenFOAM implementation for small bubbles
phases
{
    gas
    {
        type            gas;
        equationOfState perfectGas;
        thermodynamics  hConst;
        transport       sutherland;
    }

    liquid
    {
        type            incompressible;
        equationOfState rhoConst;
        thermodynamics  hConst;
        transport       const;
    }
}

phaseInteraction
{
    dragModel       Schiller-Naumann;
    liftModel       Saffman-Mei;
    heatTransferModel   Ranz-Marshall;

    Schiller-NaumannCoeffs
    {
        switch1 1000;
        Cd1     24;
        Cd2     0.44;
    }
}
```

**การเลือกโมเดล:**
- **Schiller-Naumann**: ให้การทำนายแรงลากต้านที่แม่นยำสำหรับอนุภาคทรงกลม
- **Saffman-Mei**: จับแรงยกขึ้นบนอนุภาคทรงกลมขนาดเล็ก (ทิศทางบวก)
- **Ranz-Marshall**: ได้รับการตรวจสอบความถูกต้องอย่างกว้างขวาง

#### ฟองขนาดใหญ่ ($Eo > 10$, $We > 1$)

ฟองก๊าซที่เปลี่ยนรูปแสดงความแตกต่างจากรูปทรงกลมอย่างมีนัยสำคัญ โดยมีรูปทรงแบบรีและรูปแบบการไหลเวียนภายใน

**ช่วงของตัวเลขที่ไม่มิติ:**
- **จำนวน Eötvös** $Eo > 10$: ผลของแรงลอยตัวเริ่มแข่งขันกับแรงตึงผิว
- **จำนวน Weber** $We > 1$: แรงเฉื่อยเพียงพอที่จะทำให้รูปร่างฟองก๊าซเปลี่ยนแปลง

**สหสัมพันธ์การลากต้าน** ของ Tomiyama:
$$C_D = \max\left[\min\left\{\frac{24}{Re_g}(1 + 0.15Re_g^{0.687}), \frac{72}{Re_g}\right\}, \frac{8}{3}\frac{Eo}{Eo + 4}\right]$$

**แรงยก:**
$$\mathbf{f}_L = C_L \rho_l V_b (\mathbf{u}_g - \mathbf{u}_l) \times (\nabla \times \mathbf{u}_l)$$

โดยที่สัมประสิทธิ์แรงยก $C_L$ สามารถเป็นค่าลบสำหรับฟองก๊าซขนาดใหญ่ นำไปสู่ปรากฏการณ์ "wall-peeling"

**การเปลี่ยนแปลงเส้นผ่านศูนย์กลาง** ตามมาตราส่วน Hinze:
$$d_{max} = C \left(\frac{\sigma}{\rho_l}\right)^{3/5} \varepsilon^{-2/5}$$

โดยที่ $\varepsilon$ แทนอัตราการสลายตัวของความปั่นพลุ้งและ $C$ เป็นค่าคงที่จากการทดลอง

```cpp
// OpenFOAM implementation for deforming bubbles
phaseInteraction
{
    dragModel       Tomiyama;
    liftModel       Tomiyama;
    diameterModel   HinzeScale;
    virtualMassModel    constant;

    TomiyamaCoeffs
    {
        C1          0.44;
        C2          24.0;
        C3          0.15;
        C4          6.0;
        sigma       0.072; // แรงตึงผิวของน้ำ
    }

    HinzeScaleCoeffs
    {
        Cmax        0.89;
        Cbreakup    1.6;
    }

    constantVirtualMassCoeffs
    {
        Cvm         0.5;
    }
}
```

**การเลือกโมเดล:**
- **Tomiyama drag**: จับการเพิ่มขึ้นของสัมประสิทธิ์การลากต้านเนื่องจากการเปลี่ยนรูป
- **Tomiyama lift**: คำนึงถึงการเปลี่ยนเครื่องหมายของแรงยก (ทิศทางลบ - Wall Peeling)
- **Hinze scale**: ทำนายเส้นผ่านศูนย์กลางฟองก๊าซสมดุล
- **Virtual mass**: จำเป็นเนื่องจากผลของมวลเพิ่มในระหว่างการเร่งความเร็ว

---

### 2.2 การไหลแบบปลอก (Slug Flow, $0.3 < \alpha_g < 0.6$)

เกิดฟองขนาดใหญ่รูปกระสุน (Taylor bubbles) เต็มหน้าตัดท่อ

**ลักษณะเฉพาะ:**
- **ฟองก๊าซ Taylor** ขนาดใหญ่ครอบงำโครงสร้างการไหล
- ฟองก๊าซที่ยืดออกครอบคลุมส่วนสำคัญของหน้าตัดท่อ
- ต้องใช้แบบจำลอง **Shape-dependent Drag**
- ต้องพิจารณาฟิล์มของเหลวที่ผนัง (Wall Film)

**โครงสร้างการไหล** ประกอบด้วยสามโซนที่แตกต่างกัน:
1. **โซนฟองก๊าซ Taylor**: ฟองก๊าซขนาดใหญ่กับฟิล์มของเหลว
2. **โซนของเหลวชัก**: การแขวนฟองก๊าศขนาดเล็กในของเหลว
3. **โซนเปลี่ยนผ่าน**: โซนการผสมที่แกว่ง

**สมการโมเมนตัมแบบสองของไหล:**
$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k + \mathbf{M}_{k}^{wall}$$

โดยที่ $\mathbf{M}_{k}^{wall}$ แทนการถ่ายโอนโมเมนตัมผนัง

**สหสัมพันธ์ความหนาฟิล์ม** (Frokowiak et al.):
$$\delta_f = 0.2 D \left(\frac{\rho_l g D^2}{\sigma}\right)^{0.25} \left(\frac{U_{TB}}{\sqrt{gD}}\right)^{0.5}$$

**การลากต้านที่ขึ้นอยู่กับรูปร่าง:**
$$C_D = \frac{16}{Re_{TB}} \left[1 + 0.15Re_{TB}^{0.687}\right] + \frac{2}{3} \frac{D}{L_{TB}}$$

**สัมประสิทธิ์มวลเสมือน:**
$$C_{vm} = 0.5 + 0.3 \frac{L_{TB}}{D}$$

```cpp
phaseInteraction
{
    dragModel       shapeDependent;
    virtualMassModel    shapeDependent;
    wallLubricationModel    Frank;

    shapeDependentDragCoeffs
    {
        TaylorBubble
        {
            C1          16.0;
            C2          2.0;
            n           0.687;
        }

        SmallBubble
        {
            switch1     1000;
            Cd1         24.0;
            Cd2         0.44;
        }
    }

    shapeDependentVirtualMassCoeffs
    {
        CvmBase         0.5;
        aspectRatioExp  0.3;
    }

    FrankCoeffs
    {
        C1              0.01;
        C2              0.001;
        Cmu             0.09;
    }
}
```

**ความท้าทายในการสร้างโมเดล:**
- **Shape-dependent drag**: จำเป็นสำหรับการจับพลวัตของฟองก๊าศ Taylor
- **Virtual mass**: สำคัญเนื่องจากการเร่งความเร็วฟองก๊าซขนาดใหญ่
- **Wall effects**: ฟิล์มของเหลวและการหล่อลื่นผนังมีผลต่อการไหลอย่างมีนัยสำคัญ

---

### 2.3 ฟองก๊าซแคป ($Eo > 4$, $We > 4$)

ฟองก๊าซแคปเป็นรีจีมที่เปลี่ยนรูปมากที่สุด ซึ่งมีลักษณะเฉพาะคือรูปทรงเห็ดหรือคล้ายแคป

**ลักษณะทางฟิสิกส์:**
- **จำนวน Eötvös สูง** ($Eo > 4$): แรงลอยตัวมีอำนาจเหนือกว่าแรงตึงผิว
- **จำนวน Weber ใหญ่** ($We > 4$): การเปลี่ยนรูปอย่างมีนัยสำคัญเนื่องจากผลของความเฉื่อย

**การไหลรอบฟองก๊าซแคป** แสดงโครงสร้าง wake ที่ซับซ้อนและการหลุดออกของ vortex

**สัมประสิทธิ์การลากต้าน**:
$$C_D \approx \frac{8}{3}$$

สำหรับจำนวน Reynolds สูง การลากต้านจะไม่ขึ้นอยู่กับขนาดและความเร็วของฟองก๊าศเป็นอย่างมีนัยสำคัญ

**แรงกระจายความปั่นพลุ้ง**:
$$\mathbf{f}_{TD} = -C_{TD} \rho_l k \nabla \alpha_g$$

โดยที่ $C_{TD}$ เป็นสัมประสิทธิ์การกระจายความปั่นพลุ้งและ $k$ เป็นพลังงานจลน์ของความปั่นพลุ้ง

**การเปลี่ยนแปลงความหนาแน่นของพื้นที่อินเตอร์เฟซ**:
$$\frac{\partial (\alpha_g a_i)}{\partial t} + \nabla \cdot (\alpha_g a_i \mathbf{u}_g) = S_{coalescence} + S_{breakup}$$

โดยที่ $a_i$ แทนพื้นที่อินเตอร์เฟซต่อหน่วยปริมาตร

```cpp
phaseInteraction
{
    dragModel       Tomiyama;
    liftModel       Tomiyama;
    turbulentDispersionModel    Burns;
    interfacialAreaModel    gradient;

    BurnsCoeffs
    {
        Ctd         1.0;
        D           1.0;
    }

    gradientInterfacialAreaCoeffs
    {
        Cia         1.0;
    }

    wallLubricationModel    Antal;

    AntalCoeffs
    {
        Cw1         1.0;
        Cw2         0.1;
    }
}
```

**ข้อควรพิจารณาในการสร้างโมเดล:**
- **โมเดล Tomiyama**: ใช้ได้ทั่วทั้งสเปกตรัมการเปลี่ยนรูป
- **Burns turbulent dispersion**: จำเป็นสำหรับการจับการผสมในการไหลที่มีจำนวน Reynolds สูง
- **Gradient area model**: คำนึงถึงพลวัตของอินเตอร์เฟซ
- **Wall lubrication**: สำคัญสำหรับการจับการกระจายฟองก๊าศใกล้ผนัง

---

## 3. แบบจำลองที่แนะนำ (Recommended Models)

### 3.1 การถ่ายเทโมเมนตัม

ใช้โมเดล **Tomiyama** เป็นมาตรฐาน เนื่องจากครอบคลุมทั้งการเปลี่ยนรูปและทิศทางของแรงยก:

$$C_D = \max\left[\min\left\{\frac{24}{Re_g}(1 + 0.15Re_g^{0.687}), \frac{72}{Re_g}\right\}, \frac{8}{3}\frac{Eo}{Eo + 4}\right] \tag{3.1}$$

> [!TIP] เคล็ดลับการเลือกแบบจำลอง Drag
> โมเดล Tomiyama เหมาะสมที่สุดสำหรับระบบ Gas-Liquid ทั่วไป เนื่องจากสามารถจับภาพทั้งฟองขนาดเล็ก (ทรงกลม) และฟองขนาดใหญ่ (เปลี่ยนรูป) ในสมการเดียว

### 3.2 การกระจายขนาดฟอง (PBM)

หากในระบบมีการรวมตัว (Coalescence) และการแตกตัว (Breakup) ของฟองที่มีนัยสำคัญ ควรใช้ **Population Balance Model (PBM)** ร่วมกับ MUSIG

**สมการสมดุลประชากร (PBE):**
$$\frac{\partial n(v)}{\partial t} + \nabla \cdot [\mathbf{u}_g n(v)] + \frac{\partial [G(v) n(v)]}{\partial v} = B_{breakup} - D_{breakup} + B_{coalescence} - D_{coalescence}$$

**โมเดลการแตกตัว** ของ Luo และ Svendsen:
$$B_{breakup} = \int_v^{\infty} \beta(v,v') \Omega_{breakup}(v') n(v') \, dv'$$

กับความถี่การแตกตัว:
$$\Omega_{breakup} = 0.923(1 - \alpha_g) \frac{\varepsilon^{1/3}}{d^{2/3}} \exp\left(-\frac{U_{crit}^2}{\varepsilon^{2/3} d^{2/3}}\right)$$

**โมเดลการรวมตัว** ของ Coulaloglou และ Tavlarides:
$$\Omega_{coalescence} = C_{co} \frac{\pi}{4} (d_i + d_j)^2 \mathbf{u}_{t,ij} \exp\left(-\frac{t_{ij}}{t_{c,ij}}\right)$$

```cpp
populationBalance
{
    populationBalanceModel    sizeGroup;

    sizeGroups
    {
        SG1 { d: 0.001; x: 0.2; }
        SG2 { d: 0.002; x: 0.3; }
        SG3 { d: 0.003; x: 0.3; }
        SG4 { d: 0.004; x: 0.2; }
    }

    coalescenceModels
    {
        LuoCoalescence
        {
            Cco         0.1;
            Co          0.0;
        }
    }

    breakupModels
    {
        LuoBreakup
        {
            C1          0.923;
            C2          1.0;
            C3          2.45;
        }
    }
}
```

**การเลือกโมเดล:**
- **Tomiyama drag**: คำนึงถึงผลของการเปลี่ยนรูปตามขนาด
- **Population balance**: จับพลวัตของการรวมตัว/แตกตัว
- **Interfacial area transport**: แม่นยำกว่าโมเดลที่ใช้การไล่ระดับ

---

## 4. การนำไปใช้ใน OpenFOAM

### 4.1 ตัวอย่างการตั้งค่าสำหรับ Bubble Column

ตัวอย่างการตั้งค่าใน `phaseProperties` สำหรับระบบ Bubble Column:

```cpp
simulationType  twoPhaseEulerFoam;

phases
{
    water
    {
        type            liquid;
        equationOfState rhoConst;
        thermodynamics  hConst;
        transport       const;
        value           uniform 0;
    }

    air
    {
        type            gas;
        equationOfState perfectGas;
        thermodynamics  hConst;
        transport       sutherland;
        value           uniform 1;
    }
}

phaseInteraction
{
    dragModel       Tomiyama;
    liftModel       Tomiyama;
    virtualMassModel    constant;
    turbulentDispersionModel Burns;

    TomiyamaCoeffs
    {
        sigma       0.072; // แรงตึงผิวของน้ำ (N/m)
        C1          0.44;
        C2          24.0;
        C3          0.15;
        C4          6.0;
    }

    constantVirtualMassCoeffs
    {
        Cvm         0.5;
    }

    BurnsCoeffs
    {
        Ctd         1.0;
        D           1.0;
    }
}

turbulence
{
    type            mixtureKEpsilon;

    mixtureKEpsilonCoeffs
    {
        Cmu         0.09;
        C1          1.44;
        C2          1.92;
        sigmaEps    1.3;
        sigmaK      1.0;
        muMixture   on;
        phaseTurbulence  on;
    }

    dispersedTurbulence
    {
        type        dispersedTurbulenceModel;

        dispersedMultiphaseTurbulence
        {
            type        dispersedEuler;
            sigma        1.0;
            Cmu          0.09;
            Prt          1.0;
        }
    }
}
```

### 4.2 การตั้งค่า Solver และ Relaxation Factors

เนื่องจากระบบ Gas-Liquid มีอัตราส่วนความหนาแน่นสูง ต้องใช้ค่า **Under-relaxation** ที่ต่ำสำหรับสนามความดันเพื่อรักษาเสถียรภาพ

```cpp
solver
{
    p               GAMG
    {
        smoother         GaussSeidel;
        nSweeps         1;
        tolerance       1e-6;
        relTol          0.01;
    };

    pFinal          GAMG
    {
        smoother         GaussSeidel;
        nSweeps         2;
        tolerance       1e-8;
        relTol          0;
    };

    U               smoothSolver
    {
        smoother         GaussSeidel;
        nSweeps         2;
        tolerance       1e-6;
        relTol          0;
    };

    alpha           smoothSolver
    {
        smoother         GaussSeidel;
        nSweeps         2;
        tolerance       1e-8;
        relTol          0;
    };
}

relaxationFactors
{
    fields
    {
        p           0.3;
        U           0.7;
        alpha       0.7;
    }
    equations
    {
        p           1;
        U           0.8;
        alpha       0.8;
    }
}
```

> [!WARNING] ข้อควรระวังเชิงตัวเลข
> ระบบ Gas-Liquid มักมีอัตราส่วนความหนาแน่นสูง ($\approx 1000:1$) ควรใช้ค่า **Under-relaxation** ที่ต่ำสำหรับสนามความดัน (เช่น 0.2 - 0.3) เพื่อรักษาเสถียรภาพ

---

## 5. สรุปการเลือกแบบจำลอง

### 5.1 ตารางสรุปการเลือกแบบจำลองตาม Flow Regime

| Flow Regime | ช่วง $\alpha_g$ | Drag Model | Lift Model | โมเดลเพิ่มเติมที่แนะนำ |
|-------------|----------------|------------|------------|---------------------------|
| **Bubbly (ฟองเล็ก)** | < 0.1 | Schiller-Naumann | Saffman-Mei | Ranz-Marshall (ถ้ามี heat transfer) |
| **Bubbly (ฟองใหญ่)** | 0.1 - 0.3 | Tomiyama | Tomiyama | Hinze Scale, Virtual Mass |
| **Slug** | 0.3 - 0.6 | Shape-dependent | Tomiyama/Frank | Wall Lubrication, Film Model |
| **Churn/Taylor** | > 0.6 | Tomiyama/Constant | Tomiyama | Burns Dispersion, Gradient Area |

### 5.2 ข้อควรพิจารณาเพิ่มเติม

**สำหรับระบบที่มีการรวมตัว/แตกตัวของฟอง:**
- ใช้ **PBM + MUSIG** เมื่อ $\sigma_d/d̄ > 0.3$ (การกระจายขนาดฟองกว้าง)
- ต้องการ **Size Groups** 5-10 กลุ่มสำหรับความแม่นยำที่ดี

**สำหรับระบบที่มีความปั่นพลุ้งสูง:**
- ใช้ **mixtureKEpsilon** สำหรับความปั่นพลุ้งของเฟสผสม
- เพิ่ม **Burns turbulent dispersion** สำหรับการจับการผสม

**สำหรับการไหลในท่อ (Pipe Flow):**
- ต้องพิจารณา **Wall lubrication force** (Antal/Frank model)
- ระมัดระวังเรื่อง **Wall peaking** ของ void fraction

---

## 6. แหล่งอ้างอิงเพิ่มเติม

1. **Tomiyama, A.** (1998). "Struggle with computational bubble dynamics." *Multiphase Science and Technology*, 10(4), 369-405.
2. **Luo, H., & Svendsen, H. F.** (1996). "Theoretical model for drop and bubble breakup in turbulent dispersions." *AIChE Journal*, 42(5), 1225-1233.
3. **Ishii, M., & Zuber, N.** (1979). "Drag coefficient and relative velocity in bubbly, droplet or particulate flows." *AIChE Journal*, 25(5), 843-855.
4. **Burns, A. D., Frank, T., Hamill, I., & Shi, J. M.** (2004). "The favre averaged drag model for turbulent dispersion in Eulerian multi-phase flows." *Proceedings of the 5th International Conference on Multiphase Flow*, Yokohama, Japan.

---
