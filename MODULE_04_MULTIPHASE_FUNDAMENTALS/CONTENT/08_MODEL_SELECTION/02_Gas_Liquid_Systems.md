# ระบบก๊าซ-ของเหลว (Gas-Liquid Systems)

## 1. บทนำ (Introduction) 

ระบบก๊าซ-ของเหลวเป็นหัวใจสำคัญในงานวิศวกรรมเคมีและโรงไฟฟ้า พฤติกรรมของการไหลถูกกำหนดโดยแรงลอยตัว (Buoyancy) และการเสียรูปของฟองอากาศ (Bubble deformation)

---

## 2. การจำแนกตามระบอบการไหล (Flow Regimes)

### 2.1 การไหลแบบฟอง (Bubbly Flow, $\alpha_g < 0.3$)
ฟองอากาศกระจายตัวเป็นอิสระในของเหลว แบ่งตามขนาดดังนี้:

- **ฟองขนาดเล็ก ($Eo < 1$):** ทรงกลมสมบูรณ์
  - **Drag:** Schiller-Naumann
  - **Lift:** Saffman-Mei (ทิศทางบวก)
- **ฟองขนาดใหญ่ ($Eo > 10$):** รูปทรงคล้ายหมวก (Cap bubbles)
  - **Drag:** Tomiyama หรือค่าคงที่ $\approx 8/3$
  - **Lift:** Tomiyama (ทิศทางลบ - Wall Peeling)

### 2.2 การไหลแบบปลอก (Slug Flow, $0.3 < \alpha_g < 0.6$)
เกิดฟองขนาดใหญ่รูปกระสุน (Taylor bubbles) เต็มหน้าตัดท่อ
- ต้องใช้แบบจำลอง **Shape-dependent Drag**
- ต้องพิจารณาฟิล์มของเหลวที่ผนัง (Wall Film)

---

## 3. แบบจำลองที่แนะนำ (Recommended Models)

### 3.1 การถ่ายเทโมเมนตัม
ใช้โมเดล **Tomiyama** เป็นมาตรฐาน เนื่องจากครอบคลุมทั้งการเปลี่ยนรูปและทิศทางของแรงยก:

$$C_D = \max\[\min\[\frac{24}{Re_g}(1 + 0.15Re_g^{0.687}), \frac{72}{Re_g}\]], \frac{8}{3}\frac{Eo}{Eo + 4}\] \tag{2.1}

### 3.2 การกระจายขนาดฟอง (PBM)
หากในระบบมีการรวมตัว (Coalescence) และการแตกตัว (Breakup) ของฟองที่มีนัยสำคัญ ควรใช้ **Population Balance Model (PBM)** ร่วมกับ MUSIG

---

## 4. การนำไปใช้ใน OpenFOAM

ตัวอย่างการตั้งค่าใน `phaseProperties` สำหรับระบบ Bubble Column:

```openfoam
phaseInteraction
{
    dragModel       Tomiyama;
    liftModel       Tomiyama;
    virtualMassModel    constant;
    turbulentDispersionModel Burns;
    
    TomiyamaCoeffs
    {
        sigma       0.072; // แรงตึงผิวของน้ำ
    }
}
```

### ข้อควรระวังเชิงตัวเลข:
ระบบ Gas-Liquid มักมีอัตราส่วนความหนาแน่นสูง ($\approx 1000:1$) ควรใช้ค่า **Under-relaxation** ที่ต่ำสำหรับสนามความดัน (เช่น 0.2 - 0.3) เพื่อรักษาเสถียรภาพ

```
