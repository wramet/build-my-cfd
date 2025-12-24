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
// Phase definitions for gas-liquid system
phases
{
    gas
    {
        // Gas phase type with compressible properties
        type            gas;
        // Equation of state: ideal gas law
        equationOfState perfectGas;
        // Thermodynamics: constant specific heat
        thermodynamics  hConst;
        // Transport: Sutherland's law for viscosity
        transport       sutherland;
    }

    liquid
    {
        // Liquid phase type with incompressible properties
        type            incompressible;
        // Equation of state: constant density
        equationOfState rhoConst;
        // Thermodynamics: constant specific heat
        thermodynamics  hConst;
        // Transport: constant transport properties
        transport       const;
    }
}

// Interfacial interaction models between phases
phaseInteraction
{
    // Drag model: Schiller-Naumann correlation for spherical particles
    dragModel       Schiller-Naumann;
    // Lift model: Saffman-Mei for small spherical particles
    liftModel       Saffman-Mei;
    // Heat transfer model: Ranz-Marshall correlation
    heatTransferModel   Ranz-Marshall;

    // Schiller-Naumann drag model coefficients
    Schiller-NaumannCoeffs
    {
        // Reynolds number switch for drag coefficient transition
        switch1 1000;
        // Coefficient for viscous regime (low Reynolds)
        Cd1     24;
        // Coefficient for inertial regime (high Reynolds)
        Cd2     0.44;
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:84-100`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block ด้านบนแสดงการตั้งค่าเฟสก๊าซและของเหลว พร้อมกับโมเดลอินเทอร์เฟซสำหรับฟองขนาดเล็กใน OpenFOAM

คำอธิบาย: โค้ดนี้กำหนดคุณสมบัติของเฟสก๊าซและของเหลว โดยเฟสก๊าซใช้สมการของสภาพแบบก๊าซสมบูรณ์ (perfectGas) ส่วนเฟสของเหลวเป็นอัดตัวไม่ได้ (incompressible) และใช้ความหนาแน่นคงตัว สำหรับโมเดลปฏิสัมพันธ์ระหว่างเฟส ใช้โมเดล Schiller-Naumann สำหรับการลากต้าน ซึ่งเหมาะสำหรับฟองทรงกลมขนาดเล็ก และโมเดล Saffman-Mei สำหรับแรงยกของอนุภาคทรงกลมขนาดเล็ก

แนวคิดสำคัญ:
- **PerfectGas**: สมการสถานะของก๊าศที่เชื่อมโยงความดัน ความหนาแน่น และอุณหภูมิ ตามกฎของก๊าศอุดมคติ
- **rhoConst**: สมการสถานะสำหรับของเหลวที่ไม่อัดตัวได้ ให้ความหนาแน่นคงตัว
- **Schiller-Naumann**: โมเดลการลากต้านสำหรับอนุภาคทรงกลม ครอบคลุมทั้งกรณี Reynolds ต่ำและสูง
- **Saffman-Mei**: โมเดลแรงยกสำหรับอนุภาคขนาดเล็กในกระแสการไหล

---

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
// Phase interaction models for large, deforming bubbles
phaseInteraction
{
    // Tomiyama drag model for deforming bubbles
    dragModel       Tomiyama;
    // Tomiyama lift model (can be negative for large bubbles)
    liftModel       Tomiyama;
    // Hinze scale for equilibrium bubble diameter
    diameterModel   HinzeScale;
    // Virtual mass model for acceleration effects
    virtualMassModel    constant;

    // Tomiyama drag model coefficients
    TomiyamaCoeffs
    {
        // Drag coefficient for high Reynolds number
        C1          0.44;
        // Coefficient for viscous regime
        C2          24.0;
        // Exponent for Reynolds number correction
        C3          0.15;
        // Coefficient for Eötvös number dependency
        C4          6.0;
        // Surface tension of water (N/m)
        sigma       0.072;
    }

    // Hinze scale coefficients for bubble breakup
    HinzeScaleCoeffs
    {
        // Maximum diameter coefficient
        Cmax        0.89;
        // Breakup coefficient
        Cbreakup    1.6;
    }

    // Constant virtual mass coefficients
    constantVirtualMassCoeffs
    {
        // Virtual mass coefficient (typically 0.5 for spherical bubbles)
        Cvm         0.5;
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/Make/files:1-20`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block นี้แสดงการตั้งค่าโมเดลปฏิสัมพันธ์ระหว่างเฟสสำหรับฟองขนาดใหญ่ที่มีการเปลี่ยนรูปใน OpenFOAM

คำอธิบาย: โค้ดนี้ใช้โมเดล Tomiyama สำหรับทั้งแรงลากต้านและแรงยก ซึ่งสามารถจับภาพการเปลี่ยนรูปของฟองก๊าซขนาดใหญ่ได้ดีกว่าโมเดล Schiller-Naumann โมเดล Tomiyama สำหรับแรงยกสามารถให้ค่าสัมประสิทธิ์แรงยกเป็นลบ ซึ่งสอดคล้องกับปรากฏการณ์ wall-peeling ที่พบในฟองก๊าซขนาดใหญ่ นอกจากนี้ยังมีโมเดล HinzeScale สำหรับทำนายเส้นผ่านศูนย์กลางฟองก๊าศสมดุล และโมเดลมวลเสมือน (virtual mass) สำหรับผลของมวลเพิ่มในระหว่างการเร่งความเร็ว

แนวคิดสำคัญ:
- **Tomiyama drag**: โมเดลการลากต้านที่คำนึงถึงผลของการเปลี่ยนรูปตามจำนวน Eötvös และ Weber
- **Tomiyama lift**: โมเดลแรงยกที่สามารถให้ค่าสัมประสิทธิ์แรงยกเป็นลบ สอดคล้องกับปรากฏการณ์ wall-peeling
- **HinzeScale**: ทำนายเส้นผ่านศูนย์กลางฟองก๊าศสมดุลจากการสมดุลระหว่างแรงตึงผิวและความปั่นพลุ้ง
- **Virtual mass**: ผลของมวลเพิ่มที่เกิดขึ้นเมื่อเฟสหนึ่งเร่งความเร็วผ่านเฟสอื่น

---

**การเลือกโมเดล:**
- **Tomiyama drag**: จับการเพิ่มขึ้นของสัมประสิทธิ์การลากต้านเนื่องจากการเปลี่ยนรูป
- **Tomiyama lift**: คำนึงถึงการเปลี่ยนเครื่องหมายของแรงยก (ทิศทางลบ - Wall Peeling)
- **Hinze scale**: ทำนายเส้นผ่านศูนย์กลางฟองก๊าศสมดุล
- **Virtual mass**: จำเป็นเนื่องจากผลของมวลเพิ่มในระหว่างการเร่งความเร็ว

---

### 2.2 การไหลแบบปลอก (Slug Flow, $0.3 < \alpha_g < 0.6$)

เกิดฟองขนาดใหญ่รูปกระสุน (Taylor bubbles) เต็มหน้าตัดท่อ

**ลักษณะเฉพาะ:**
- **ฟองก๊าซ Taylor** ขนาดใหญ่ครอบงำโครงสร้างการไหล
- ฟองก๊าศที่ยืดออกครอบคลุมส่วนสำคัญของหน้าตัดท่อ
- ต้องใช้แบบจำลอง **Shape-dependent Drag**
- ต้องพิจารณาฟิล์มของเหลวที่ผนัง (Wall Film)

**โครงสร้างการไหล** ประกอบด้วยสามโซนที่แตกต่างกัน:
1. **โซนฟองก๊าศ Taylor**: ฟองก๊าซขนาดใหญ่กับฟิล์มของเหลว
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
// Phase interaction models for slug flow with Taylor bubbles
phaseInteraction
{
    // Drag model dependent on bubble shape
    dragModel       shapeDependent;
    // Virtual mass model dependent on bubble shape
    virtualMassModel    shapeDependent;
    // Wall lubrication model for near-wall effects
    wallLubricationModel    Frank;

    // Shape-dependent drag coefficients
    shapeDependentDragCoeffs
    {
        // Taylor bubble parameters
        TaylorBubble
        {
            // Coefficient for viscous regime
            C1          16.0;
            // Coefficient for aspect ratio term
            C2          2.0;
            // Exponent for Reynolds number correction
            n           0.687;
        }

        // Small bubble parameters
        SmallBubble
        {
            // Reynolds number switch
            switch1     1000;
            // Viscous regime coefficient
            Cd1         24.0;
            // Inertial regime coefficient
            Cd2         0.44;
        }
    }

    // Shape-dependent virtual mass coefficients
    shapeDependentVirtualMassCoeffs
    {
        // Base virtual mass coefficient
        CvmBase         0.5;
        // Exponent for aspect ratio dependency
        aspectRatioExp  0.3;
    }

    // Frank wall lubrication model coefficients
    FrankCoeffs
    {
        // Primary coefficient for wall lubrication
        C1              0.01;
        // Secondary coefficient
        C2              0.001;
        // Turbulence viscosity coefficient
        Cmu             0.09;
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:126-145`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block นี้แสดงการตั้งค่าโมเดลปฏิสัมพันธ์ระหว่างเฟสสำหรับการไหลแบบปลอก (Slug Flow) ที่มีฟอง Taylor ใน OpenFOAM

คำอธิบาย: โค้ดนี้ใช้โมเดลที่ขึ้นอยู่กับรูปร่าง (shape-dependent) สำหรับทั้งแรงลากต้านและมวลเสมือน เนื่องจากฟอง Taylor มีรูปร่างที่ยืดออกและมีสัดส่วนแตกต่างจากฟองทรงกลม โมเดลการลากต้านและมวลเสมือนจึงต้องคำนึงถึงสัดส่วนรูปร่าง (aspect ratio) ของฟอง นอกจากนี้ยังมีโมเดลการหล่อลื่นผนัง (wall lubrication) ของ Frank สำหรับจับผลของผนังท่อต่อการกระจายตัวของฟอง

แนวคิดสำคัญ:
- **Shape-dependent drag**: โมเดลการลากต้านที่คำนึงถึงรูปร่างของฟอง ซึ่งสำคัญสำหรับฟอง Taylor ที่มีรูปร่างยาว
- **Shape-dependent virtual mass**: โมเดลมวลเสมือนที่ขึ้นอยู่กับสัดส่วนรูปร่างของฟอง
- **Wall lubrication**: โมเดลที่จับผลของแรงผนังที่กระทำต่อฟองก๊าศใกล้ผนัง
- **Taylor bubble**: ฟองก๊าซขนาดใหญ่ที่มีรูปร่างยาวคล้ายกระสุน ซึ่งเป็นลักษณะเฉพาะของการไหลแบบปลอก

---

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
// Phase interaction models for cap bubbles with high deformation
phaseInteraction
{
    // Tomiyama drag model for highly deformed bubbles
    dragModel       Tomiyama;
    // Tomiyama lift model (negative lift for large bubbles)
    liftModel       Tomiyama;
    // Burns turbulent dispersion model
    turbulentDispersionModel    Burns;
    // Gradient-based interfacial area model
    interfacialAreaModel    gradient;

    // Burns turbulent dispersion coefficients
    BurnsCoeffs
    {
        // Turbulent dispersion coefficient
        Ctd         1.0;
        // Length scale coefficient
        D           1.0;
    }

    // Gradient interfacial area coefficients
    gradientInterfacialAreaCoeffs
    {
        // Interfacial area coefficient
        Cia         1.0;
    }

    // Antal wall lubrication model
    wallLubricationModel    Antal;

    // Antal wall lubrication coefficients
    AntalCoeffs
    {
        // Primary wall lubrication coefficient
        Cw1         1.0;
        // Secondary wall lubrication coefficient
        Cw2         0.1;
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/turbulentDispersionModels/turbulentDispersionModel/turbulentDispersionModel.H:1-50`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block นี้แสดงการตั้งค่าโมเดลปฏิสัมพันธ์ระหว่างเฟสสำหรับฟองแคปที่มีการเปลี่ยนรูปสูงใน OpenFOAM

คำอธิบาย: โค้ดนี้ใช้โมเดล Tomiyama สำหรับทั้งแรงลากต้านและแรงยก ซึ่งเหมาะสำหรับฟองที่มีการเปลี่ยนรูปสูง เนื่องจากฟองแคปมีการเปลี่ยนรูปมากและจำนวน Reynolds สูง จึงจำเป็นต้องใช้โมเดลการกระจายความปั่นพลุ้ง (Burns model) เพื่อจับการผสมในกระแสการไหลที่มีความปั่นพลุ้งสูง นอกจากนี้ยังมีโมเดลพื้นที่อินเตอร์เฟซแบบ gradient สำหรับคำนวณพื้นที่อินเตอร์เฟซ และโมเดลการหล่อลื่นผนังของ Antal สำหรับจับผลของผนัง

แนวคิดสำคัญ:
- **Tomiyama drag/lift**: โมเดลที่ครอบคลุมทั้งสเปกตรัมการเปลี่ยนรูปของฟอง
- **Burns turbulent dispersion**: โมเดลการกระจายความปั่นพลุ้งสำหรับการจับการผสมในกระแสที่มีความปั่นพลุ้งสูง
- **Gradient area model**: โมเดลคำนวณพื้นที่อินเตอร์เฟซจากการไล่ระดับของปริมาตรเฟส
- **Antal wall lubrication**: โมเดลการหล่อลื่นผนังสำหรับฟองใกล้ผนัง

---

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
> โมเดล Tomiyama เหมาะสมที่สุดสำหรับระบบ Gas-Liquid ทั่วไป เนื่องจากสามารถจับภาพทั้งฟองขนาดเล็ก (ทรงกลม) แลงฟองขนาดใหญ่ (เปลี่ยนรูป) ในสมการเดียว

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
// Population balance model for bubble size distribution
populationBalance
{
    // Size group method for population balance
    populationBalanceModel    sizeGroup;

    // Definition of size groups for bubbles
    sizeGroups
    {
        // Size group 1: smallest bubbles
        SG1 { d: 0.001; x: 0.2; }
        // Size group 2: small bubbles
        SG2 { d: 0.002; x: 0.3; }
        // Size group 3: medium bubbles
        SG3 { d: 0.003; x: 0.3; }
        // Size group 4: large bubbles
        SG4 { d: 0.004; x: 0.2; }
    }

    // Coalescence models
    coalescenceModels
    {
        // Luo coalescence model
        LuoCoalescence
        {
            // Coalescence rate coefficient
            Cco         0.1;
            // Film drainage coefficient
            Co          0.0;
        }
    }

    // Breakup models
    breakupModels
    {
        // Luo breakup model
        LuoBreakup
        {
            // Breakup frequency coefficient
            C1          0.923;
            // Size ratio coefficient
            C2          1.0;
            // Critical velocity coefficient
            C3          2.45;
        }
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C:1-80`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block นี้แสดงการตั้งค่าโมเดลสมดุลประชากร (Population Balance Model) สำหรับการกระจายขนาดฟองก๊าศใน OpenFOAM

คำอธิบาย: โค้ดนี้ใช้วิธีกลุ่มขนาด (size group method) สำหรับแก้สมการสมดุลประชากร โดยแบ่งขนาดฟองก๊าศออกเป็น 4 กลุ่มตามเส้นผ่านศูนย์กลาง โมเดลการรวมตัวของ Luo ใช้สำหรับจำลองกระบวนการรวมตัวของฟอง ซึ่งขึ้นอยู่กับอัตราการไหลของฟิล์มระหว่างฟอง ส่วนโมเดลการแตกตัวของ Luo ใช้สำหรับจำลองกระบวนการแตกตัวของฟอง ซึ่งขึ้นอยู่กับอัตราการสลายตัวของความปั่นพลุ้ง

แนวคิดสำคัญ:
- **Size group method**: วิธีการแบ่งขนาดฟองออกเป็นกลุ่มๆ เพื่อแก้สมการสมดุลประชากร
- **Luo coalescence**: โมเดลการรวมตัวที่คำนึงถึงอัตราการไหลของฟิล์มระหว่างฟอง
- **Luo breakup**: โมเดลการแตกตัวที่คำนึงถึงผลของความปั่นพลุ้ง
- **Population balance**: สมการที่จำลองการเปลี่ยนแปลงของการกระจายขนาดฟองเนื่องจากการรวมตัวและแตกตัว

---

**การเลือกโมเดล:**
- **Tomiyama drag**: คำนึงถึงผลของการเปลี่ยนรูปตามขนาด
- **Population balance**: จับพลวัตของการรวมตัว/แตกตัว
- **Interfacial area transport**: แม่นยำกว่าโมเดลที่ใช้การไล่ระดับ

---

## 4. การนำไปใช้ใน OpenFOAM

### 4.1 ตัวอย่างการตั้งค่าสำหรับ Bubble Column

ตัวอย่างการตั้งค่าใน `phaseProperties` สำหรับระบบ Bubble Column:

```cpp
// Simulation type for two-phase Euler-Euler solver
simulationType  twoPhaseEulerFoam;

// Phase definitions for bubble column
phases
{
    // Water phase (continuous liquid phase)
    water
    {
        // Liquid phase type
        type            liquid;
        // Constant density equation of state
        equationOfState rhoConst;
        // Constant specific heat thermodynamics
        thermodynamics  hConst;
        // Constant transport properties
        transport       const;
        // Initial volume fraction (liquid-filled)
        value           uniform 0;
    }

    // Air phase (dispersed gas phase)
    air
    {
        // Gas phase type
        type            gas;
        // Perfect gas equation of state
        equationOfState perfectGas;
        // Constant specific heat thermodynamics
        thermodynamics  hConst;
        // Sutherland's law for viscosity
        transport       sutherland;
        // Initial volume fraction (gas-filled)
        value           uniform 1;
    }
}

// Interfacial interaction models
phaseInteraction
{
    // Tomiyama drag model for gas-liquid systems
    dragModel       Tomiyama;
    // Tomiyama lift model
    liftModel       Tomiyama;
    // Constant virtual mass model
    virtualMassModel    constant;
    // Burns turbulent dispersion model
    turbulentDispersionModel Burns;

    // Tomiyama drag model coefficients
    TomiyamaCoeffs
    {
        // Surface tension of water (N/m)
        sigma       0.072;
        // High Reynolds number coefficient
        C1          0.44;
        // Viscous regime coefficient
        C2          24.0;
        // Reynolds number exponent
        C3          0.15;
        // Eötvös number coefficient
        C4          6.0;
    }

    // Constant virtual mass coefficients
    constantVirtualMassCoeffs
    {
        // Virtual mass coefficient (0.5 for spherical bubbles)
        Cvm         0.5;
    }

    // Burns turbulent dispersion coefficients
    BurnsCoeffs
    {
        // Turbulent dispersion coefficient
        Ctd         1.0;
        // Length scale coefficient
        D           1.0;
    }
}

// Turbulence modeling
turbulence
{
    // Mixture k-epsilon turbulence model
    type            mixtureKEpsilon;

    // Mixture k-epsilon coefficients
    mixtureKEpsilonCoeffs
    {
        // Turbulent viscosity coefficient
        Cmu         0.09;
        // k-epsilon model C1 coefficient
        C1          1.44;
        // k-epsilon model C2 coefficient
        C2          1.92;
        // Epsilon dissipation rate Prandtl number
        sigmaEps    1.3;
        // Kinetic energy Prandtl number
        sigmaK      1.0;
        // Enable mixture viscosity
        muMixture   on;
        // Enable phase-specific turbulence
        phaseTurbulence  on;
    }

    // Dispersed turbulence model
    dispersedTurbulence
    {
        // Dispersed turbulence model type
        type        dispersedTurbulenceModel;

        // Dispersed Euler turbulence model
        dispersedMultiphaseTurbulence
        {
            // Dispersed Euler model
            type        dispersedEuler;
            // Prandtl number for turbulence
            sigma        1.0;
            // Turbulent viscosity coefficient
            Cmu          0.09;
            // Turbulent Prandtl number
            Prt          1.0;
        }
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:84-120`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block นี้แสดงการตั้งค่าแบบสมบูรณ์สำหรับระบบ Bubble Column ใน OpenFOAM

คำอธิบาย: โค้ดนี้กำหนดการจำลองสองเฟสโดยใช้ solver twoPhaseEulerFoam โดยมีน้ำเป็นเฟสต่อเนื่องและอากาศเป็นเฟสกระจาย สำหรับการปฏิสัมพันธ์ระหว่างเฟส ใช้โมเดล Tomiyama สำหรับทั้งแรงลากต้านและแรงยก ซึ่งเหมาะสำหรับระบบก๊าซ-ของเหลวทั่วไป นอกจากนี้ยังมีโมเดลมวลเสมือนและการกระจายความปั่นพลุ้งของ Burns สำหรับความปั่นพลุ้ง ใช้โมเดล mixtureKEpsilon ซึ่งเหมาะสำหรับระบบก๊าซ-ของเหลว

แนวคิดสำคัญ:
- **twoPhaseEulerFoam**: Solver สำหรับระบบสองเฟสโดยใช้แนวทาง Euler-Euler
- **Tomiyama models**: โมเดลที่เหมาะสำหรับระบบก๊าซ-ของเหลวทั่วไป
- **mixtureKEpsilon**: โมเดลความปั่นพลุ้งแบบ k-epsilon สำหรับเฟสผสม
- **Burns dispersion**: โมเดลการกระจายความปั่นพลุ้งสำหรับระบบก๊าซ-ของเหลว

---

### 4.2 การตั้งค่า Solver และ Relaxation Factors

เนื่องจากระบบ Gas-Liquid มีอัตราส่วนความหนาแน่นสูง ต้องใช้ค่า **Under-relaxation** ที่ต่ำสำหรับสนามความดันเพื่อรักษาเสถียรภาพ

```cpp
// Linear solver settings for stability
solver
{
    // Pressure solver - Geometric-Algebraic Multi-Grid
    p               GAMG
    {
        // Smoother for convergence acceleration
        smoother         GaussSeidel;
        // Number of sweeps per iteration
        nSweeps         1;
        // Absolute tolerance for convergence
        tolerance       1e-6;
        // Relative tolerance for convergence
        relTol          0.01;
    };

    // Final pressure solver (tighter tolerance)
    pFinal          GAMG
    {
        // Smoother for final convergence
        smoother         GaussSeidel;
        // Increased sweeps for final iteration
        nSweeps         2;
        // Stricter absolute tolerance
        tolerance       1e-8;
        // Zero relative tolerance for final
        relTol          0;
    };

    // Velocity solver - smooth solver
    U               smoothSolver
    {
        // Gauss-Seidel smoother
        smoother         GaussSeidel;
        // Number of sweeps
        nSweeps         2;
        // Absolute tolerance
        tolerance       1e-6;
        // Zero relative tolerance
        relTol          0;
    };

    // Volume fraction solver
    alpha           smoothSolver
    {
        // Gauss-Seidel smoother
        smoother         GaussSeidel;
        // Number of sweeps
        nSweeps         2;
        // Strict tolerance for volume fraction
        tolerance       1e-8;
        // Zero relative tolerance
        relTol          0;
    };
}

// Under-relaxation factors for numerical stability
relaxationFactors
{
    // Field under-relaxation factors
    fields
    {
        // Pressure under-relaxation (low for stability)
        p           0.3;
        // Velocity under-relaxation
        U           0.7;
        // Volume fraction under-relaxation
        alpha       0.7;
    }
    // Equation under-relaxation factors
    equations
    {
        // Pressure equation relaxation (no relaxation)
        p           1;
        // Velocity equation relaxation
        U           0.8;
        // Volume fraction equation relaxation
        alpha       0.8;
    }
}
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:150-180`

---

**คำอธิบายเพิ่มเติม:**

แหล่งข้อมูล: C++ code block นี้แสดงการตั้งค่า solver และค่า under-relaxation สำหรับระบบก๊าซ-ของเหลวใน OpenFOAM

คำอธิบาย: โค้ดนี้กำหนด solver สำหรับแต่ละตัวแปร โดยใช้ GAMG (Geometric-Algebraic Multi-Grid) สำหรับความดัน ซึ่งเป็นวิธีการที่มีประสิทธิภาพสำหรับปัญหา Elliptic สำหรับความเร็วและปริมาตรเฟส ใช้ smoothSolver พร้อมด้วย smoother แบบ Gauss-Seidel ค่า under-relaxation ถูกตั้งค่าต่ำสำหรับความดัน (0.3) เพื่อรักษาเสถียรภาพของการแก้สมการ ซึ่งเป็นสิ่งสำคัญสำหรับระบบก๊าซ-ของเหลวที่มีอัตราส่วนความหนาแน่นสูง

แนวคิดสำคัญ:
- **GAMG**: Geometric-Algebraic Multi-Grid solver สำหรับปัญหา Elliptic เช่น สมการความดัน
- **smoothSolver**: Solver ที่ใช้วิธีการทำให้เรียบ (smoothing) เพื่อเร่งการลู่เข้า
- **Gauss-Seidel**: วิธีการทำให้เรียบแบบวนซ้ำ
- **Under-relaxation**: เทคนิคการลดการเปลี่ยนแปลงของตัวแปรในแต่ละรอบการแก้สมการ เพื่อรักษาเสถียรภาพ

---

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