# ปรากฏการณ์ระหว่างเฟส (Interfacial Phenomena)

## ภาพรวม

==ปรากฏการณ์ระหว่างเฟส== เป็นฟิสิกส์พื้นฐานที่ควบคุมการปฏิสัมพันธ์ระหว่างเฟสต่างๆ ในระบบหลายเฟส ซึ่งมีความสำคัญอย่างยิ่งต่อการทำนายพฤติกรรมของของไหลหลายเฟสได้อย่างแม่นยำ

ปรากฏการณ์เหล่านี้รวมถึง:
- **แรงตึงผิว** (Surface Tension)
- **แรงฉุดระหว่างเฟส** (Interphase Drag Forces)
- **การถ่ายเทความร้อนระหว่างเฟส** (Interphase Heat Transfer)
- **การถ่ายเทมวลและการเปลี่ยนแปลงเฟส** (Mass Transfer and Phase Change)
- **แรงระหว่างเฟสเพิ่มเติม** (Additional Interfacial Forces)

---

## 1. แรงตึงผิว (Surface Tension, $\sigma$)

แรงตึงผิวเป็นแรงที่กระทำที่รอยต่อระหว่างสองเฟส ซึ่งมีแนวโน้มที่จะลดพื้นที่ผิวให้น้อยที่สุด

![[surface_tension_and_contact_angle.png]]

### 1.1 สมการ Young-Laplace

ความแตกต่างของความดันข้ามพื้นผิวสัมผัสที่มีความโค้ง:

$$\Delta p = \sigma \kappa = \sigma \left(\frac{1}{R_1} + \frac{1}{R_2}\right) \tag{1.1}$$

**นิยามตัวแปร:**
- $\Delta p$: ความแตกต่างของความดันข้ามพื้นผิว [Pa]
- $\sigma$: แรงตึงผิว [N/m]
- $\kappa$: ความโค้งเฉลี่ย [1/m]
- $R_1, R_2$: รัศมีความโค้งหลัก [m]

### 1.2 มุมสัมผัส (Contact Angle, $\theta$)

มุมที่รอยต่อระหว่างเฟสพบกับผนังของแข็ง

![[wetting_behavior_comparison.png]]

#### กฎของ Young (Young's Law)

$$\gamma_{sv} = \gamma_{sl} + \gamma_{lv} \cos(\theta_c) \tag{1.2}$$

**นิยามตัวแปร:**
- $\gamma_{sv}$: พลังงานพื้นผิวระหว่างผนังกับระยะไกล
- $\gamma_{sl}$: พลังงานพื้นผิวระหว่างผนังกับของเหลว
- $\gamma_{lv}$: พลังงานพื้นผิวระหว่างของเหลวกับระยะไกล

#### การจำแนกประเภทตามมุมสัมผัส

| ประเภท | ช่วงมุม | ลักษณะ |
|---------|---------|---------|
| **Hydrophilic** | $\theta < 90^°$ | การเปียก (Wetting) |
| **Hydrophobic** | $\theta > 90^°$ | ไม่เปียก (Non-wetting) |
| **Superhydrophilic** | $\theta < 10^°$ | เปียกอย่างยิ่ง |
| **Superhydrophobic** | $\theta > 150^°$ | ไม่เปียกอย่างยิ่ง |

### 1.3 ความหนาแน่นพื้นที่รอยต่อ (Interfacial Area Density, $\mathcal{A}_i$)

ปริมาณพื้นที่รอยต่อต่อหน่วยปริมาตร ($m^2/m^3$) ซึ่งมีความสำคัญต่อการคำนวณอัตราการถ่ายเทระหว่างเฟส

#### สำหรับฟอง/หยดทรงกลมที่มีเส้นผ่านศูนย์กลาง $d$:

$$\mathcal{A}_i = \frac{6 \alpha_d}{d} \tag{1.3}$$

**นิยามตัวแปร:**
- $\mathcal{A}_i$: ความหนาแน่นพื้นที่รอยต่อ [m²/m³]
- $\alpha_d$: เศษส่วนปริมาตรของเฟสที่กระจายตัว [-]
- $d$: เส้นผ่านศูนย์กลางของฟอง/หยด [m]

### 1.4 ตัวเลขไร้มิติที่สำคัญสำหรับแรงตึงผิว

![[bubble_shapes_weber_number.png]]

#### ตารางตัวเลขไร้มิติ

| ตัวเลขไร้มิติ | สมการ | ความหมายทางกายภาพ |
|----------------|----------|---------------------|
| **Weber Number (We)** | $\text{We} = \frac{\rho U^2 L}{\sigma}$ | อัตราส่วนของแรงเฉื่อยต่อแรงตึงผิว |
| **Eötvös Number (Eo)** | $\text{Eo} = \frac{g(\rho_c - \rho_d)L^2}{\sigma}$ | อัตราส่วนของแรงลอยตัวต่อแรงตึงผิว |
| **Morton Number (Mo)** | $\text{Mo} = \frac{g \mu_c^4 (\rho_c - \rho_d)}{\rho_c^2 \sigma^3}$ | คุณสมบัติของของไหลสำหรับพลศาสตร์ของฟอง |

#### ผลกระทบทางกายภาพของแรงตึงผิว

##### ความดันส่วนโค้ง (Curvature Pressure)
ความแตกต่างของความดันข้ามพื้นผิวสัมผัสที่มีความโค้งตามสมการ Young-Laplace

##### มุมสัมผัส (Contact Angles)
พฤติกรรมการเปียก (wetting) ที่ผนังซึ่งกำหนดโดยกฎของ Young

##### ความยาวคาปิลลารี (Capillary Length)
ความสำคัญสัมพัทธ์ของแรงตึงผิวเทียบกับแรงโน้มถ่วง:

$$L_c = \sqrt{\frac{\sigma}{\rho g}} \tag{1.4}$$

---

## 2. แรงฉุดระหว่างเฟส (Drag Forces Between Phases)

### 2.1 ทฤษฎีพื้นฐาน

==แรงฉุดระหว่างเฟส== เป็นกลไกพื้นฐานของการถ่ายเทพลังงานโมเมนตัมที่ควบคุมการมีปฏิสัมพันธ์ระหว่างเฟส

แรงนี้เกิดขึ้นจากการเคลื่อนที่สัมพัทธ์ระหว่างเฟส และมีความสำคัญอย่างยิ่งต่อการทำนายพฤติกรรมของของไหลได้อย่างแม่นยำในการใช้งานทางอุตสาหกรรม เช่น:
- ฟลูอิดไดซ์เบด (fluidized beds)
- คอลัมน์ฟอง (bubble columns)
- เครื่องแยกเฟส (separators)

#### สมการแรงฉุด

แรงฉุดต่อหน่วยปริมาตาระหว่างเฟส $i$ และเฟส $j$:

$$\mathbf{F}_{d,ij} = K_{ij}(\mathbf{U}_j - \mathbf{U}_i) \tag{2.1}$$

**นิยามตัวแปร:**
- $\mathbf{F}_{d,ij}$: เวกเตอร์แรงฉุด [N/m³]
- $K_{ij}$: สัมประสิทธิ์การถ่ายเทพลังงานโมเมนตัมระหว่างเฟส [kg/(m³·s)]
- $\mathbf{U}_i, \mathbf{U}_j$: เวกเตอร์ความเร็วของเฟส [m/s]

> [!INFO] หมายเหตุ
> สูตรนี้ทำให้มั่นใจได้ว่าแรงฉุดจะต้านทานการเคลื่อนที่สัมพัทธ์ระหว่างเฟส ซึ่งสอดคล้องกับธรรมชาติทางกายภาพของแรงต้านหนืว

### 2.2 แบบจำลองแรงฉุด Schiller-Naumann

==แบบจำลอง Schiller-Naumann== เป็นหนึ่งในสมการสหสัมพันธ์แรงฉุดที่ใช้กันอย่างแพร่หลายที่สุดสำหรับอนุภาคทรงกลม

$$K = \frac{3}{4} C_D \frac{\alpha_d \rho_c |\mathbf{U}_d - \mathbf{U}_c|}{d_p} \tag{2.2}$$

**นิยามตัวแปร:**
- $C_D$: สัมประสิทธิ์แรงฉุด (drag coefficient)
- $\alpha_d$: เศษส่วนปริมาตรของเฟสที่กระจายตัว [-]
- $\rho_c$: ความหนาแน่นของเฟสต่อเนื่อง [kg/m³]
- $|\mathbf{U}_d - \mathbf{U}_c|$: ความเร็วสัมพัทธ์ [m/s]
- $d_p$: เส้นผ่านศูนย์กลางของอนุภาค [m]

#### ความสัมพันธ์ของสัมประสิทธิ์แรงฉุด

| เงื่อนไข | สมการสหสัมพันธ์ $C_D$ |
|-------------|-------------------------|
| $Re_p < 1000$ | $C_D = \frac{24}{Re_p}(1 + 0.15Re_p^{0.687})$ |
| $Re_p \geq 1000$ | $C_D = 0.44$ |

โดยที่ $Re_p = \frac{\rho_c |\mathbf{U}_d - \mathbf{U}_c| d_p}{\mu_c}$ คือ Particle Reynolds number

แบบจำลองนี้ให้การทำนายที่แม่นยำสำหรับระบบที่มีความเข้มข้นเจือจางถึงปานกลางที่มีอนุภาคทรงกลม ทำให้เหมาะสำหรับ:
- ของไหลแก๊ส-ของเหลว (gas-liquid)
- ของแข็ง-ของเหลว (solid-liquid)
- การเสียรูปของอนุภาคมีน้อยที่สุด

### 2.3 แบบจำลองแรงฉุด Ergun

==แบบจำลอง Ergun== ขยายการจำลองแรงฉุดไปยังสภาวะการบรรจุหนาแน่น (dense packing conditions) ซึ่งการมีปฏิสัมพันธ์ระหว่างอนุภาคต่ออนุภาคมีความสำคัญ:

$$K = 150 \frac{\alpha_d^2 \mu_c (1 - \alpha_c)}{d_p^2 \alpha_c^3} + 1.75 \frac{\alpha_d \rho_c |\mathbf{U}_d - \mathbf{U}_c|}{\alpha_c^3} \tag{2.3}$$

สมการสหสัมพันธ์นี้รวมเอาส่วนประกอบจาก:
- **แรงหนืว** (พจน์แรก): แรงต้านจากความหนืวของของไหล
- **แรงเฉื่อย** (พจน์ที่สอง): แรงต้านจากความเร็วสัมพัทธ์

เพื่ออธิบายฟิสิกส์ของของไหลที่ซับซ้อนใน:
- ชั้นบรรจุ (packed beds)
- ฟลูอิดไดซ์เบด (fluidized beds)
- ใกล้กับความเร็วขั้นต่ำของการฟลูอิดไดซ์

---

## 3. การถ่ายเทความร้อนระหว่างเฟส (Interphase Heat Transfer)

### 3.1 พื้นฐานการถ่ายเทความร้อนระหว่างเฟส

การถ่ายเทความร้อนระหว่างเฟสในของไหลหลายเฟสถูกควบคุมโดยสมการพื้นฐาน:

$$Q_{ij} = h_{ij} A_{ij} (T_j - T_i) \tag{3.1}$$

**นิยามตัวแปร:**
- $Q_{ij}$: อัตราการถ่ายเทความร้อนเชิงปริมาตร [W/m³]
- $h_{ij}$: สัมประสิทธิ์การถ่ายเทความร้อนระหว่างเฟส [W/(m²·K)]
- $A_{ij}$: ความหนาแน่นของพื้นที่ผิวสัมผัส [m²/m³]
- $(T_j - T_i)$: แรงขับเคลื่อนอุณหภูมิ [K]

สัมประสิทธิ์การถ่ายเทความร้อนขึ้นอยู่กับ:

$$h_{ij} = f(\text{Re}, \text{Pr}, \text{geometry})$$

โดยที่:
- $\text{Re}$: Reynolds number
- $\text{Pr}$: Prandtl number
- ปัจจัยทางเรขาคณิต: พิจารณาถึงรูปร่างของอนุภาคและการจัดเรียงตัว

### 3.2 แบบจำลองการถ่ายเทความร้อนแบบสองแรงต้าน (Two-Resistance Model)

==แบบจำลองสองแรงต้าน== พิจารณาแรงต้านความร้อนในทั้งสองเฟส ให้การทำนายที่แม่นยำยิ่งขึ้น

$$\frac{1}{U_{\text{total}}} = \frac{1}{h_i} + \frac{1}{h_j} \tag{3.2}$$

**นิยามตัวแปร:**
- $U_{\text{total}}$: สัมประสิทธิ์การถ่ายเทความร้อนโดยรวม

สัมประสิทธิ์การถ่ายเทความร้อนแต่ละตัวมักคำนวณโดยใช้สมการสหสัมพันธ์ Nusselt number:

$$\text{Nu} = \frac{h d_p}{k} \tag{3.3}$$

#### สมการสหสัมพันธ์ Nusselt ที่พบบ่อย

| สมการ | สูตร | เงื่อนไขการใช้งาน |
|---------|-------|-----------------|
| **Ranz-Marshall** | $\text{Nu} = 2 + 0.6\text{Re}^{1/2}\text{Pr}^{1/3}$ | อนุภาคเดี่ยวในของไหล |
| **Gunn** | $\text{Nu} = (7 - 10\alpha_c + 5\alpha_c^2)(1 + 0.7\text{Re}^{0.2}\text{Pr}^{1/3})$ | อนุภาคในระบบหนาแน่น |

---

## 4. การถ่ายเทมวลและการเปลี่ยนแปลงเฟส (Mass Transfer and Phase Change)

### 4.1 พื้นฐานการถ่ายเทมวล

การถ่ายเทมวลระหว่างเฟสเกิดขึ้นเนื่องจากความแตกต่างของความเข้มข้น อุณหภูมิ หรือศักย์เคมี

#### สมการพื้นฐานของอัตราการถ่ายเทมวล

$$\dot{m}_{ij} = k_{ij} A_{ij} (C_j - C_i) \tag{4.1}$$

**นิยามตัวแปร:**
- $\dot{m}_{ij}$: อัตราการถ่ายเทมวล [kg/(m³·s)]
- $k_{ij}$: สัมประสิทธิ์การถ่ายเทมวล [m/s]
- $A_{ij}$: ความหนาแน่นของพื้นที่ผิวสัมผัส [m²/m³]
- $(C_j - C_i)$: แรงขับเคลื่อนความเข้มข้น [kg/m³]

**หลักการเทียบเคียง (Analogies):** สัมประสิทธิ์การถ่ายเทมวลมักมีความสัมพันธ์กับสัมประสิทธิ์การถ่ายเทความร้อน:

| หลักการเทียบเคียง | สมการ | เงื่อนไข |
|-------------------|---------|-----------|
| Chilton-Colburn analogy | $\frac{h}{\rho c_p U} = \frac{k}{U} = \text{St}_m = \text{St}_h \text{Pr}^{2/3}$ | ทั่วไป |
| Reynolds analogy | $\text{St}_m = \text{St}_h$ | $\text{Pr} = \text{Sc} = 1$ |

### 4.2 กฎของเฮนรีและสมดุลแก๊ส-ของเหลว

==กฎของเฮนรี (Henry's Law)== กำหนดความสัมพันธ์สมดุลสำหรับระบบแก๊ส-ของเหลว:

$$C_{\text{gas}} = H \cdot p_{\text{gas}} \tag{4.2}$$

**นิยามตัวแปร:**
- $C_{\text{gas}}$: ความเข้มข้นของแก๊สในเฟสของเหลว [mol/m³]
- $p_{\text{gas}}$: ความดันย่อยของแก๊ส [Pa]
- $H$: ค่าคงที่ของเฮนรี [mol/(m³·Pa)]

ค่าคงที่ของเฮนรีแบบไร้มิติ:

$$K_{\text{GC}} = \frac{C_{\text{gas}}}{C_{\text{liquid}}} = HRT \tag{4.3}$$

### 4.3 กลไกการเปลี่ยนแปลงเฟส

#### การระเหยและการควบแน่น (Evaporation and Condensation)

ถูกควบคุมโดยสมการ Hertz-Knudsen:

$$\dot{m}_{evap} = \alpha \sqrt{\frac{M}{2\pi RT_{sat}}}(p_{sat} - p_{int}) \tag{4.4}$$

**นิยามตัวแปร:**
- $\alpha$: สัมประสิทธิ์การปรับตัว (accommodation coefficient)
- $M$: มวลโมเลกุล [kg/mol]
- $T_{sat}$: อุณหภูมิอิ่มตัว [K]
- $p_{sat}$: ความดันอิ่มตัว [Pa]
- $p_{int}$: ความดันที่พื้นผิวสัมผัส [Pa]

#### พลวัตการขยายตัวของฟอง (Bubble Growth Dynamics)

สำหรับการขยายตัวของฟองในของเหลวที่มีความร้อนยิ่งยวด สมการ Rayleigh-Plesset จะควบคุมพลวัต:

$$R\ddot{R} + \frac{3}{2}\dot{R}^2 = \frac{p_b - p_\infty}{\rho_l} - \frac{2\sigma}{\rho_l R} - \frac{4\mu_l \dot{R}}{\rho_l R} \tag{4.5}$$

**นิยามตัวแปร:**
- $R$: รัศมีของฟอง [m]
- $p_b$: ความดันในฟอง [Pa]
- $p_\infty$: ความดันที่ระยะไกล [Pa]
- $\sigma$: แรงตึงผิว [N/m]
- $\mu_l$: ความหนืวของของเหลว [Pa·s]

---

## 5. แรงระหว่างเฟสเพิ่มเติม (Additional Interfacial Forces)

### 5.1 แรงมวลเสมือน (Virtual Mass Force)

==แรงมวลเสมือน== พิจารณาถึงการเร่งความเร็วของของไหลโดยรอบเมื่ออนุภาคเร่งความเร็ว ซึ่งแสดงถึงผลกระทบของมวลที่เพิ่มเข้ามา (added mass effects):

$$\mathbf{F}_{vm} = C_{vm} \rho_c \alpha_d (\mathbf{a}_d - \mathbf{a}_c) \tag{5.1}$$

**นิยามตัวแปร:**
- $C_{vm}$: สัมประสิทธิ์มวลเสมือน (โดยทั่วไปคือ 0.5 สำหรับอนุภาคทรงกลม)
- $\rho_c$: ความหนาแน่นของเฟสต่อเนื่อง [kg/m³]
- $\alpha_d$: เศษส่วนปริมาตรของเฟสที่กระจายตัว [-]
- $(\mathbf{a}_d - \mathbf{a}_c)$: การเร่งความเร็วสัมพัทธ์ [m/s²]

แรงนี้จะมีความสำคัญในระบบที่มี:
- การเร่งความเร็วความถี่สูง เช่น การสั่นสะเทือนของคลื่นเสียง
- การไหลที่ไม่คงที่ (unsteady flows) ที่มีการเปลี่ยนแปลงตามเวลาอย่างรุนแรง

### 5.2 แรงยก (Lift Force)

==แรงยก== เกิดขึ้นจากความแตกต่างของความเร็ว (velocity gradients) ที่ตั้งฉากกับการเคลื่อนที่สัมพัทธ์ระหว่างเฟส:

$$\mathbf{F}_{lift} = C_L \rho_c \alpha_d (\mathbf{U}_d - \mathbf{U}_c) \times (\nabla \times \mathbf{U}_c) \tag{5.2}$$

**นิยามตัวแปร:**
- $C_L$: สัมประสิทธิ์แรงยก ซึ่งขึ้นอยู่กับ:
  - particle Reynolds number
  - อัตราการเฉือน (shear rate)
  - ระบบการไหล (flow regime)

สัมประสิทธิ์แรงยก Saffman-Mei ให้การทำนายที่แม่นยำสำหรับอนุภาคขนาดเล็ก:

$$C_L = \frac{2.255}{\sqrt{\text{Re}_p \text{Sr}}} \quad \text{สำหรับ} \quad \text{Re}_p \ll \text{Sr} \tag{5.3}$$

### 5.3 แรงหล่อลื่นผนัง (Wall Lubrication Force)

==แรงหล่อลื่นผนัง== ป้องกันการสะสมตัวของอนุภาคใกล้ผนัง โดยใช้แรงผลักที่เพิ่มขึ้นเมื่ออนุภาคเข้าใกล้ขอบเขตของแข็ง:

$$\mathbf{F}_{wl} = C_{wl} \rho_c \alpha_d |\mathbf{U}_d - \mathbf{U}_c|^2 n_w f(y) \tag{5.4}$$

**นิยามตัวแปร:**
- $C_{wl}$: สัมประสิทธิ์แรงหล่อลื่นผนัง
- $n_w$: เวกเตอร์แนวฉากของผนัง
- $f(y)$: ฟังก์ชันของระยะห่างจากผนัง ซึ่งโดยทั่วไปจะลดลงแบบเอกซ์โพเนนเชียล

#### ฟังก์ชันระยะห่างจากผนัง

$$f(y) = \frac{1}{y^2} - \frac{1}{(y + \epsilon)^2} \tag{5.5}$$

โดยที่:
- $y$: ระยะห่างจากผนัง [m]
- $\epsilon$: พารามิเตอร์ขนาดเล็กเพื่อป้องกันค่าอนันต์

### 5.4 แรงกระจายตัวจากความปั่นป่วน (Turbulent Dispersion Force)

==แรงกระจายตัวจากความปั่นป่วน== (Turbulent dispersion) พิจารณาถึงการเคลื่อนที่แบบสุ่มของอนุภาคอันเนื่องมาจากการผันผวนของความปั่นป่วน (turbulent fluctuations) ซึ่งส่งเสริมการผสมและป้องกันการแยกเฟสที่มากเกินไป:

$$\mathbf{F}_{td} = -C_{td} \rho_c k \nabla \alpha_d \tag{5.6}$$

**นิยามตัวแปร:**
- $C_{td}$: สัมประสิทธิ์แรงกระจายตัวจากความปั่นป่วน
- $k$: พลังงานจลน์จากความปั่นป่วน [m²/s²]

แรงนี้มักถูกจำลองโดยใช้:
- การประมาณการแพร่แบบเกรเดียนต์ (gradient diffusion approximations)
- วิธีการสมการ Langevin ที่ซับซ้อน

---

## 6. การนำไปใช้ใน OpenFOAM

### 6.1 สถาปัตยกรรมโมเดลรอยต่อ

OpenFOAM มีเฟรมเวิร์กที่ครอบคลุมสำหรับการจำลองปรากฏการณ์ระหว่างเฟส

#### สถาปัตยกรรมหลัก

```mermaid
flowchart TD
    A[phaseSystem] --> B[dragModel]
    A --> C[heatTransferModel]
    A --> D[massTransferModel]
    A --> E[virtualMassModel]
    A --> F[liftModel]
    A --> G[wallLubricationModel]
    A --> H[turbulentDispersionModel]

    B --> B1[SchillerNaumann]
    B --> B2[Ergun]

    C --> C1[RanzMarshall]
    C --> C2[Gunn]

    D --> D1[Henry]
    D --> D2[HertzKnudsen]
```

### 6.2 การตรวจจับและการติดตามรอยต่อ

#### OpenFOAM Code Implementation

การตรวจจับรอยต่อและการคำนวณความโค้ง:

```cpp
// Detect interface through void fraction gradient
volVectorField voidFractionGrad = fvc::grad(alpha1);

// Calculate curvature for surface tension
surfaceScalarField curvature = fvc::div(nHat);

// Phase topology indicator for flow pattern classification
volScalarField regimeIndicator = calculateRegime(alpha1, U1, U2);
```

> **📂 Source:** ไม่พบไฟล์ที่ตรงกันในฐานข้อมูล
> 
> **คำอธิบาย:**
> - **voidFractionGrad**: เวกเตอร์ความชันของเศษส่วนปริมาตร (void fraction) ใช้ในการระบุตำแหน่งของรอยต่อระหว่างเฟส ค่าความชันสูงบ่งชี้ถึงรอยต่อที่ชัดเจน
> - **curvature**: ค่าความโค้งของรอยต่อใช้ในการคำนวณแรงตึงผิวตามสมการ Young-Laplace
> - **regimeIndicator**: ตัวบ่งชี้โทโพโลยีของการไหลสำหรับการจำแนกรูปแบบการไหลที่แตกต่างกัน (เช่น bubbly flow, slug flow, churn flow)
>
> **หลักการสำคัญ:**
> - การตรวจจับรอยต่อใช้ความชันของเศษส่วนปริมาตรเนื่องจากการเปลี่ยนแปลงอย่างรวดเร็วระหว่างค่า α=0 และ α=1
> - ความโค้งคำนวณจากการ divergent ของเวกเตอร์หน่วยปกติของรอยต่อ
> - การจำแนกรูปแบบการไหลช่วยให้เลือกแบบจำลองที่เหมาะสมกับสภาวะการไหล

### 6.3 โครงสร้างคลาสแรงฉุด

#### คลาสพื้นฐานของแบบจำลองแรงฉุด

```cpp
// Base class for drag models
class dragModel
{
    // Calculate and return drag coefficient
    virtual tmp<volScalarField> K(const UDictionary&) = 0;

    // Runtime selection mechanism
    declareRunTimeSelectionTable
    (
        autoPtr,
        dragModel,
        dictionary,
        (
            const dictionary& dict,
            const phaseModel& phase1,
            const phaseModel& phase2
        ),
        (dict, phase1, phase2)
    );
};
```

> **📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModels/dragModel/dragModel.H
> 
> **คำอธิบาย:**
> - **tmp\<volScalarField\> K()**: ฟังก์ชันเสมือน (virtual function) ที่คำนวณและคืนค่าสัมประสิทธิ์แรงฉุด K ซึ่งเป็นค่าเชิงปริมาตร (volScalarField) ที่คำนวณที่แต่ละเซลล์ใน mesh
> - **declareRunTimeSelectionTable**: มาโครของ OpenFOAM สำหรับการเลือกแบบจำลองขณะ runtime ผ่านไฟล์ dictionary ทำให้สามารถเปลี่ยนแบบจำลองโดยไม่ต้องคอมไพล์โค้ดใหม่
>
> **หลักการสำคัญ:**
> - การใช้ polymorphism ผ่านฟังก์ชัน virtual ทำให้สามารถเพิ่มแบบจำลองใหม่ได้โดยไม่ต้องแก้ไขโค้ดหลัก
> - Runtime selection table เป็นเทคนิคที่ช่วยให้ OpenFOAM สามารถโหลดแบบจำลองที่กำหนดในไฟล์ case dictionary ได้อย่างยืดหยุ่น
> - แต่ละแบบจำลองแรงฉุดต้องสืบทอดจาก dragModel และ implement ฟังก์ชัน K()

#### การนำ Schiller-Naumann ไปใช้

```cpp
class SchillerNaumann : public dragModel
{
private:
    // Diameter of dispersed phase elements
    dimensionedScalar d_;

    // Calculate Reynolds number
    tmp<volScalarField> Re() const
    {
        return mag(this->U2_ - this->U1_) * d_ / this->nu1_;
    }

    // Calculate drag coefficient
    tmp<volScalarField> Cd(const volScalarField& Re) const
    {
        return pos(Re - 1000)*0.44 + neg(Re - 1000)*
               24*(1 + 0.15*pow(Re, 0.687))/Re;
    }
};
```

> **📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/dragModels/SchillerNaumann/SchillerNaumann.C
> 
> **คำอธิบาย:**
> - **d_**: เส้นผ่านศูนย์กลางของฟอง/หยด/อนุภาคในเฟสที่กระจายตัว ซึ่งเป็นค่าคงที่ (dimensionedScalar) ที่กำหนดในไฟล์ dictionary
> - **Re()**: ฟังก์ชันสมาชิกที่คำนวณ Particle Reynolds number จากความเร็วสัมพัทธ์ เส้นผ่านศูนย์กลาง และความหนืวของเฟสต่อเนื่อง
> - **Cd()**: ฟังก์ชันสมาชิกที่คำนวณสัมประสิทธิ์แรงฉุด โดยใช้สมการสหสัมพันธ์ Schiller-Naumann ที่มี 2 โหมด:
>   - โหมด laminar (Re < 1000): ใช้สมการที่มี correction factor
>   - โหมด turbulent (Re ≥ 1000): ใช้ค่าคงที่ 0.44
> - **pos() และ neg()**: ฟังก์ชันของ OpenFOAM ที่คืนค่า 1 เมื่อเงื่อนไขเป็นจริง และ 0 เมื่อเป็นเท็จ
>
> **หลักการสำคัญ:**
> - แบบจำลอง Schiller-Naumann เป็นแบบจำลองที่ได้รับความนิยมสูงสำหรับฟองและหยดทรงกลม
> - การใช้ pos() และ neg() ช่วยให้สลับโหมดได้อย่างราบรื่นโดยไม่มีการกระโดก (discontinuity) ที่ Re=1000
> - ความแม่นยำของแบบจำลองลดลงเมื่ออนุภาคมีการเสียรูปมาก

### 6.4 ระบบเฟสการถ่ายเทความร้อน

```cpp
template<class BasePhaseSystem>
class HeatTransferPhaseSystem : public BasePhaseSystem
{
private:
    // Heat transfer models for each phase pair
    HashTable<autoPtr<heatTransferModel>, phasePairKey> heatTransferModels_;

    // Interface temperature fields
    HashTable<volScalarField, phasePairKey> Tinterfaces_;

    // Heat source/sink terms
    volScalarField Q_;

    // Calculate heat transfer between all phase pairs
    void calculateHeatTransfer();

    // Update interface temperatures
    void updateTinterfaces();
};
```

> **📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/HeatTransferPhaseSystem/HeatTransferPhaseSystem.H
> 
> **คำอธิบาย:**
> - **heatTransferModels_**: HashTable ที่เก็บแบบจำลองการถ่ายเทความร้อนสำหรับแต่ละคู่เฟส (phase pair) ใช้ phasePairKey เป็นคีย์และ autoPtr\<heatTransferModel\> เป็นค่า
> - **Tinterfaces_**: HashTable ที่เก็บสนามอุณหภูมิของพื้นผิวสัมผัสสำหรับแต่ละคู่เฟส ใช้ในแบบจำลองสองแรงต้าน
> - **Q_**: สนามสเกลาร์ที่เก็บพจน์แหล่งความร้อน/อ่างความร้อน (heat source/sink) ในสมการอนุรักษ์พลังงาน
> - **calculateHeatTransfer()**: ฟังก์ชันสมาชิกที่คำนวณอัตราการถ่ายเทความร้อนระหว่างทุกคู่เฟส
> - **updateTinterfaces()**: ฟังก์ชันสมาชิกที่ปรับปรุงอุณหภูมิของพื้นผิวสัมผัส
>
> **หลักการสำคัญ:**
> - การใช้ HashTable ช่วยให้จัดการระบบหลายเฟสได้อย่างยืดหยุ่น โดยแต่ละคู่เฟสมีแบบจำลองและสนามอุณหภูมิของตัวเอง
> - Template class ช่วยให้สามารถสืบทอดจาก BasePhaseSystem ประเภทใดก็ได้ ทำให้สถาปัตยกรรมมีความยืดหยุ่นสูง
> - การถ่ายเทความร้อนถูกคำนวณในแต่ละ time step และผลลัพธ์ถูกนำไปใช้ในสมการพลังงาน

### 6.5 ระบบเฟสการถ่ายเทมวลและการเปลี่ยนแปลงเฟส

```cpp
template<class BasePhaseSystem>
class InterfaceCompositionPhaseChangePhaseSystem
:
    public HeatTransferPhaseSystem<BasePhaseSystem>
{
private:
    // Phase change models
    HashTable<autoPtr<phaseChangeModel>, phasePairKey> phaseChangeModels_;

    // Interface composition
    interfaceCompositionModel interfaceComposition_;

    // Mass transfer rates
    HashTable<volScalarField, phasePairKey> dmdt_;

    // Latent heat effects
    volScalarField HLatent_;
};
```

> **📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/InterfaceCompositionPhaseChangePhaseSystem/InterfaceCompositionPhaseChangePhaseSystem.H
> 
> **คำอธิบาย:**
> - **phaseChangeModels_**: HashTable ที่เก็บแบบจำลองการเปลี่ยนแปลงเฟสสำหรับแต่ละคู่เฟส รวมถึง evaporation, condensation, boiling
> - **interfaceComposition_**: แบบจำลององค์ประกอบของพื้นผิวสัมผัส ซึ่งติดตามความเข้มข้นของสสารต่างๆ ที่รอยต่อ
> - **dmdt_**: HashTable ที่เก็บอัตราการถ่ายเทมวล (dm/dt) สำหรับแต่ละคู่เฟส ซึ่งเป็นค่าที่มีหน่วย kg/(m³·s)
> - **HLatent_**: สนามสเกลาร์ที่เก็บผลกระทบจากความร้อนแฝง (latent heat) ในสมการการถ่ายเทความร้อน
>
> **หลักการสำคัญ:**
> - การเปลี่ยนแปลงเฟสถูกจำลองผ่านการถ่ายเทมวลระหว่างเฟสซึ่งขับเคลื่อนโดยความแตกต่างของความเข้มข้น อุณหภูมิ หรือความดัน
> - ความร้อนแฝงถูกนำมาพิจารณาเพื่อให้แน่ใจว่าพลังงานถูกอนุรักษ์เมื่อเกิดการเปลี่ยนแปลงเฟส
> - การสืบทอดจาก HeatTransferPhaseSystem ทำให้สามารถใช้ฟังก์ชันการถ่ายเทความร้อนที่มีอยู่แล้วได้
>
> **สำหรับข้อมูลเพิ่มเติมเกี่ยวกับการคำนวณการถ่ายเทมวล:**
> ```cpp
> // Correct mass transfer rates based on interface composition
> void correctDmdtfs()
> {
>     forAllConstIter(interfaceCompositionModelTable, interfaceCompositionModels_, iter)
>     {
>         const phaseInterface& interface = iter().interface();
>         *dmdtfs_[interface] = Zero;
>         
>         // Calculate mass transfer for each specie
>         forAll(interface, interfaceIter)
>         {
>             const phaseModel& phase = interfaceIter();
>             if (!iter().haveModelInThe(phase)) continue;
>             
>             forAllConstIter(hashedWordList, iter().modelInThe(phase).species(), specieIter)
>             {
>                 *dmdtfs_[interface] += (interfaceIter.index() == 0 ? +1 : -1) *
>                     (*(*dmidtfSus_[interface])[*specieIter] + 
>                      *(*dmidtfSps_[interface])[*specieIter]*phase.Y(*specieIter));
>             }
>         }
>     }
> }
> ```
>
> **คำอธิบาย:**
> - **correctDmdtfs()**: ฟังก์ชันที่คำนวณและปรับปรุงอัตราการถ่ายเทมวลโดยคำนึงถึงองค์ประกอบของพื้นผิวสัมผัส
> - **interfaceCompositionModels_**: ตาราง hash ที่เก็บแบบจำลององค์ประกอบของพื้นผิวสัมผัส
> - **dmdtfs_**: ตาราง hash ที่เก็บอัตราการถ่ายเทมวลรวม (total mass transfer rates) สำหรับแต่ละอินเทอร์เฟส
> - การวนซ้ำผ่านแต่ละ phase pair และแต่ละสสารเพื่อคำนวณอัตราการถ่ายเทมวลทั้งแบบ explicit (dmidtfSus) และ implicit (dmidtfSps)

### 6.6 ระบบแรงรวม (Comprehensive Force System)

คลาส `MomentumTransferPhaseSystem` รวมแรงระหว่างเฟสทั้งหมด:

```cpp
template<class BasePhaseSystem>
class MomentumTransferPhaseSystem
:
    public BasePhaseSystem
{
private:
    // Drag models
    HashTable<autoPtr<dragModel>, phasePairKey> dragModels_;

    // Lift models
    HashTable<autoPtr<liftModel>, phasePairKey> liftModels_;

    // Virtual mass models
    HashTable<autoPtr<virtualMassModel>, phasePairKey> virtualMassModels_;

    // Wall lubrication models
    HashTable<autoPtr<wallLubricationModel>, phasePairKey> wallLubricationModels_;

    // Turbulent dispersion models
    HashTable<autoPtr<turbulentDispersionModel>, phasePairKey> turbulentDispersionModels_;

    // Calculate all interfacial forces
    virtual tmp<surfaceScalarField> calculateKd
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const;

    // Calculate momentum transfer terms
    virtual void correctMomentumTransfer();
};
```

> **📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.H
> 
> **คำอธิบาย:**
> - **dragModels_**: HashTable ที่เก็บแบบจำลองแรงฉุดสำหรับแต่ละคู่เฟส
> - **liftModels_**: HashTable ที่เก็บแบบจำลองแรงยกสำหรับแต่ละคู่เฟส
> - **virtualMassModels_**: HashTable ที่เก็บแบบจำลองแรงมวลเสมือนสำหรับแต่ละคู่เฟส
> - **wallLubricationModels_**: HashTable ที่เก็บแบบจำลองแรงหล่อลื่นผนังสำหรับแต่ละคู่เฟส
> - **turbulentDispersionModels_**: HashTable ที่เก็บแบบจำลองแรงกระจายจากความปั่นป่วนสำหรับแต่ละคู่เฟส
> - **calculateKd()**: ฟังก์ชันเสมือนที่คำนวณสัมประสิทธิ์การถ่ายเทโมเมนตัมระหว่างเฟส
> - **correctMomentumTransfer()**: ฟังก์ชันเสมือนที่คำนวณพจน์การถ่ายเทโมเมนตัมในสมการโมเมนตัม
>
> **หลักการสำคัญ:**
> - การใช้ HashTable ทำให้สามารถจัดการแรงที่แตกต่างกันสำหรับแต่ละคู่เฟสได้อย่างยืดหยุ่น
> - แต่ละประเภทของแรงเป็น optional สามารถเปิด/ปิดการใช้งานได้ตามความต้องการ
> - Template class design ช่วยให้สามารถสืบทอดจาก BasePhaseSystem ประเภทใดก็ได้

#### สถาปัตยกรรมแบบจำลองแรง (Force Model Architecture)

แต่ละประเภทของแรงเป็นไปตามลำดับชั้นการสืบทอดที่สอดคล้องกัน:

```cpp
class interfacialMomentumTransferModel
{
public:
    // Calculate force component
    virtual tmp<volVectorField> Fi() const = 0;

    // Runtime selection mechanism
    declareRunTimeSelectionTable
    (
        autoPtr,
        interfacialMomentumTransferModel,
        dictionary,
        (
            const dictionary& dict,
            const phasePair& pair
        ),
        (dict, pair)
    );
};

class liftModel
:
    public interfacialMomentumTransferModel
{
protected:
    // Calculate lift coefficient
    virtual tmp<volScalarField> Cl() const = 0;

    // Force calculation implementation
    virtual tmp<volVectorField> Fi() const
    {
        return Cl()*rhoC()*alphaD()*
               (Ud() - Uc())*(curl(Uc()));
    }
};
```

> **📂 Source:** .applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels/liftModels/liftModel/liftModel.H
> 
> **คำอธิบาย:**
> - **interfacialMomentumTransferModel**: คลาสพื้นฐานสำหรับแบบจำลองการถ่ายเทโมเมนตัมระหว่างเฟสทั้งหมด กำหนด interface ทั่วไป
> - **Fi()**: ฟังก์ชันเสมือนบริสุทธิ์ (pure virtual) ที่ต้องถูก implement โดยแต่ละแบบจำลองเพื่อคำนวณแรง
> - **declareRunTimeSelectionTable**: มาโครสำหรับ runtime selection ทำให้สามารถเลือกแบบจำลองผ่าน dictionary ได้
> - **liftModel**: คลาสที่สืบทอดจาก interfacialMomentumTransferModel เฉพาะสำหรับแรงยก
> - **Cl()**: ฟังก์ชันเสมือนที่คำนวณสัมประสิทธิ์แรงยก
> - **Fi()**: การ implement ของแรงยก ซึ่งคำนวณจากสัมประสิทธิ์แรงยก ความหนาแน่น เศษส่วนปริมาตร ความเร็วสัมพัทธ์ และ vorticity
>
> **หลักการสำคัญ:**
> - การใช้ inheritance และ polymorphism ทำให้สามารถเพิ่มประเภทของแรงใหม่ได้อย่างยืดหยุ่น
> - แต่ละแรงมีการคำนวณที่เฉพาะเจาะจง แต่ใช้ interface ที่สอดคล้องกัน
> - Runtime selection ช่วยให้สามารถเปลี่ยนแบบจำลองโดยไม่ต้องคอมไพล์โค้ดใหม่

#### กลยุทธ์การผสมแรง (Force Blending Strategies)

แรงต่างๆ จะถูกผสมกันตามสภาวการไหลเฉพาะที่และเศษส่วนเฟส เพื่อให้แน่ใจว่าการเปลี่ยนผ่านจะราบรื่นและมีความเสถียรเชิงตัวเลข (numerical stability):

```cpp
class forceBlendingModel
{
public:
    // Calculate blending functions
    virtual tmp<volScalarField> dragBlending() const = 0;
    virtual tmp<volScalarField> liftBlending() const = 0;
    virtual tmp<volScalarField> wallBlending() const = 0;

    // Apply blended forces
    virtual tmp<volVectorField> blendedForce() const
    {
        return dragBlending()*dragForce() +
               liftBlending()*liftForce() +
               wallBlending()*wallLubricationForce();
    }
};
```

> **📂 Source:** ไม่พบไฟล์ที่ตรงกันในฐานข้อมูล
> 
> **คำอธิบาย:**
> - **dragBlending()**: ฟังก์ชันที่คำนวณฟังก์ชันการผสมสำหรับแรงฉุด ซึ่งขึ้นอยู่กับสภาวการไหลและเศษส่วนเฟส
> - **liftBlending()**: ฟังก์ชันที่คำนวณฟังก์ชันการผสมสำหรับแรงยก
> - **wallBlending()**: ฟังก์ชันที่คำนวณฟังก์ชันการผสมสำหรับแรงหล่อลื่นผนัง
> - **blendedForce()**: ฟังก์ชันที่นำแรงทั้งหมดมารวมกันโดยใช้ฟังก์ชันการผสมที่เหมาะสม
>
> **หลักการสำคัญ:**
> - การผสมแรงช่วยให้แน่ใจว่าแรงที่แตกต่างกันถูกนำไปใช้ในสภาวการณ์ที่เหมาะสม
> - ฟังก์ชันการผสมขึ้นอยู่กับตำแหน่ง (เช่น ระยะห่างจากผนังสำหรับ wall lubrication)
> - การเปลี่ยนผ่านที่ราบรื่นช่วยป้องกันปัญหาความไม่เสถียรเชิงตัวเลข
> - การใช้ฟังก์ชันการผสมที่แตกต่างกันสำหรับแรงที่แตกต่างกันทำให้สามารถปรับแต่งพฤติกรรมของแต่ละแรงได้อย่างอิสระ
> - แรงฉุดมักถูกนำไปใช้ทั่วทั้งโดเมน ในขณะที่แรงยกและแรงหล่อลื่นผนังมีความสำคัญเฉพาะใกล้ผนังหรือในบริเวณที่มีความเฉือนสูง

---

## 7. ปัญหาทางกายภาพทั่วไปและวิธีแก้ไข

### 7.1 การแพร่กระจายเชิงตัวเลขของพื้นผิวสัมผัส

> [!WARNING] ปัญหาทางกายภาพ
> พื้นผิวสัมผัสที่คมชัดจะค่อยๆ พร่ามัวอย่างผิดธรรมชาติเมื่อเวลาผ่านไป

**อาการ:**
- การทำให้พื้นผิวสัมผัสที่คมชัดค่อยๆ เรียบเนียน
- การผสมกันอย่างผิดธรรมชาติระหว่างเฟส
- การสูญเสียรายละเอียดขนาดเล็ก

**วิธีแก้ไข:**
- ใช้ Scheme การประมาณค่าอันดับสูง (higher-order discretization schemes)
- ใช้เทคนิคการบีบอัดพื้นผิวสัมผัส (interface compression methods)
- ปรับปรุง Mesh บริเวณพื้นผิวสัมผัสให้ละเอียดขึ้น
- ใช้ Scheme พิเศษสำหรับการติดตามพื้นผิวสัมผัส (interface tracking schemes)

### 7.2 ค่าเฟสแฟรกชันที่ผิดธรรมชาติ

> [!WARNING] ปัญหาทางกายภาพ
> เฟสแฟรกชันมีค่าติดลบหรือเกิน 1

**สาเหตุ:**
- Time step มีค่ามากเกินไป
- การลดค่าความผ่อนคลาย (under-relaxation) ไม่เพียงพอ
- คุณภาพ Mesh ไม่ดี
- Source terms มีค่าสูง

**วิธีแก้ไข:**
- ลดขนาด Time step
- เพิ่มค่าตัวคูณการลดค่าความผ่อนคลาย (under-relaxation factors)
- ปรับปรุงคุณภาพ Mesh (orthogonality, aspect ratio)
- ใช้ Scheme เชิงตัวเลขที่มีขอบเขต (bounded numerical schemes)

### 7.3 ความไม่เสถียรของการควบคู่โมเมนตัม

**อาการ:**
- ความเร็วแกว่งไปมา
- สนามความดันลู่ออก
- การระเบิดเชิงตัวเลข (Numerical blow-up)

**วิธีแก้ไข:**
- ใช้การจัดการแรงฉุดแบบ Implicit (implicit drag treatment)
- ใช้ Algorithm การกำจัดบางส่วน (partial elimination algorithm)
- เพิ่มการลดค่าความผ่อนคลาย (under-relaxation)
- ใช้ Linear solvers ที่มีความเสถียร (robust linear solvers)

### 7.4 ความไม่สมดุลของการถ่ายเทความร้อน

**ปัญหาทางกายภาพ**: การแลกเปลี่ยนพลังงานระหว่างเฟสละเมิดกฎการอนุรักษ์

**สาเหตุ:**
- ค่าสัมประสิทธิ์การถ่ายเทความร้อนไม่สอดคล้องกัน
- Scheme การอินทิเกรตเวลาที่แตกต่างกัน
- ข้อผิดพลาดจากการปัดเศษเชิงตัวเลข (Numerical round-off errors)

**วิธีแก้ไข:**
- ตรวจสอบให้แน่ใจว่าการคำนวณค่าสัมประสิทธิ์การถ่ายเทความร้อนมีความสอดคล้องกัน
- ใช้ Scheme การประมาณค่าเวลาเดียวกันสำหรับทุกเฟส
- ใช้การแก้ไขเพื่อการอนุรักษ์พลังงาน

---

## สรุป

ปรากฏการณ์ระหว่างเฟสเป็นฟิสิกส์พื้นฐานที่ควบคุมการปฏิสัมพันธ์ระหว่างเฟสต่างๆ ในระบบหลายเฟส การเข้าใจและจำลองปรากฏการณ์เหล่านี้อย่างถูกต้องเป็นสิ่งจำเป็นสำหรับการทำนายพฤติกรรมของของไหลหลายเฟสได้อย่างแม่นยำ

==ประเด็นสำคัญ:==
1. **แรงตึงผิว** ควบคุมรูปร่างของพื้นผิวสัมผัสและพฤติกรรมการเปียก
2. **แรงฉุด** เป็นกลไกหลักของการถ่ายเทโมเมนตัมระหว่างเฟส
3. **การถ่ายเทความร้อนและมวล** สำคัญสำหรับการทำนายอุณหภูมิและความเข้มข้น
4. **แรงเพิ่มเติม** (มวลเสมือน, แรงยก, แรงหล่อลื่นผนัง) จำเป็นสำหรับระบบที่ซับซ้อน
5. **การนำไปใช้ใน OpenFOAM** มีเฟรมเวิร์กที่ครอบคลุมสำหรับการจำลองปรากฏการณ์เหล่านี้

การตรวจสอบความถูกต้องและการแก้ไขปัญหาทางกายภาพเป็นสิ่งสำคัญเพื่อให้แน่ใจว่าการจำลองแสดงถึงฟิสิกส์จริง ไม่ใช่เพียงสิ่งประดิษฐ์เชิงตัวเลข