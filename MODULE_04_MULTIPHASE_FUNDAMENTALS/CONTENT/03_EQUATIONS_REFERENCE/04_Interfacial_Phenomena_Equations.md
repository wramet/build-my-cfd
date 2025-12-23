# สมการปรากฏการณ์ระหว่างเฟส (Interfacial Phenomena Equations)

## 1. ผลของแรงตึงผิว (Surface Tension Effects) 

แรงตึงผิว (\sigma) สร้างความแตกต่างของความดันข้ามพื้นผิวรอยต่อที่โค้ง และกำหนดพฤติกรรมการเคลื่อนที่ของรอยต่อ

### 1.1 สมการ Young-Laplace
อธิบายความกระโดดของความดัน (\Delta p) ข้ามรอยต่อที่มีความโค้ง (\kappa):

$$\Delta p = \sigma \kappa \tag{4.1}$$

**ความโค้งเฉลี่ย (\kappa):**
$$\kappa = \nabla \cdot \mathbf{n} = \nabla \cdot \left( \frac{\nabla \alpha}{|\nabla \alpha|} \right) \tag{4.2}$$

**กรณีพิเศษ:**
- **ทรงกลม:** $\Delta p = \frac{2\sigma}{R}$
- **ทรงกระบอก:** $\Delta p = \frac{\sigma}{R}$

### 1.2 แบบจำลอง Continuum Surface Force (CSF)
ใน OpenFOAM, แรงตึงผิวจะถูกแปลงเป็นแรงต่อหน่วยปริมาตรเพื่อให้คำนวณร่วมกับสมการโมเมนตัมได้:

$$\mathbf{F}_{st} = \sigma \kappa \nabla \alpha \tag{4.3}$$

---

## 2. ผลของ Marangoni (Marangoni Effects)

เกิดจากความไม่สม่ำเสมอของแรงตึงผิวตามแนวพื้นผิวรอยต่อ (\nabla_s \sigma) ซึ่งขับเคลื่อนการไหลขนานกับรอยต่อ

### 2.1 สมการความเค้น Marangoni
$$\boldsymbol{\tau}_{Marangoni} = \nabla_s \sigma = \frac{\partial \sigma}{\partial T} \nabla_s T + \frac{\partial \sigma}{\partial C} \nabla_s C \tag{4.4}$$

โดยที่ $\nabla_s = (\mathbf{I} - \mathbf{n}\mathbf{n}) \cdot \nabla$ คือ Surface Gradient Operator

### 2.2 จำนวน Marangoni (Ma)
$$\text{Ma} = \frac{|\partial \sigma/\partial T| \Delta T L}{\mu \alpha}$$
ระบุอัตราส่วนระหว่างแรงขับเคลื่อนเทอร์โมคาปิลลารีต่อการกระจายพลังงานหนืด

---

## 3. มุมสัมผัสและการเปียก (Contact Angle and Wetting)

กำหนดพฤติกรรมที่รอยต่อระหว่างสามเฟส (Solid-Liquid-Gas) มาบรรจบกัน

### 3.1 สมการ Young (สมดุลสถิต)
$$\cos \theta_e = \frac{\sigma_{sg} - \sigma_{sl}}{\sigma_{lg}} \tag{4.5}$$

### 3.2 มุมสัมผัสดินามิกส์ (Dynamic Contact Angle)
เมื่อเส้นสัมผัสเคลื่อนที่ด้วยความเร็ว $U$, มุมสัมผัสจะเปลี่ยนไปตามกฎ Hoffman-Voinov-Tanner:
$$\theta_d^3 = \theta_e^3 + 9 \text{Ca} \ln\left(\frac{L}{L_{micro}}\right) \tag{4.6}$$
โดยที่ $\text{Ca} = \mu U / \sigma$ คือ Capillary Number

---

## 💻 การนำไปใช้ใน OpenFOAM

### การตั้งค่ามุมสัมผัสใน `0/alpha`
```cpp
wall
{
    type            constantAlphaContactAngle;
    theta0          60; // มุมสัมผัสสมดุล (องศา)
    limit           gradient;
    value           uniform 0;
}
```

### การคำนวณความโค้งใน Solver
```cpp
// Interface normal
volVectorField n = fvc::grad(alpha);
volVectorField nHat = n/(mag(n) + delta);

// Curvature
volScalarField kappa = -fvc::div(nHat);
```

การเข้าใจสมการเหล่านี้มีความสำคัญอย่างยิ่งในการจำลองปรากฏการณ์ Microfluidics, การเชื่อม (Welding), และการไหลที่มีพื้นผิวอิสระ (Free surface flows) ให้แม่นยำ
