# OpenFOAM Content Quality Control Checklist

รายการตรวจสอบความถูกต้องของเนื้อหาก่อนส่งมอบงาน (Must be checked before marking task as complete).

## 0. ความถูกต้องทางฟิสิกส์ (Physics Accuracy)
- [ ] **Equation Validity**: สมการ (Governing Equations) ต้องถูกต้องแม่นยำและสอดคล้องกับ Conservation Laws
- [ ] **Dimensional Consistency**: หน่วย (Units) และมิติ (Dimensions) ของตัวแปรต้องสอดคล้องกันทั้งสมการ
- [ ] **Physical Interpretation**: คำอธิบายปรากฏการณ์ต้องไม่บิดเบือนข้อเท็จจริงทางฟิสิกส์
  - *ตัวอย่างที่ผิด*: อธิบายว่า $\nu_t$ (Turbulent viscosity) เป็นคุณสมบัติของของไหล (ที่จริงเป็นคุณสมบัติของการไหล)
- [ ] **Assumption Clarity**: ระบุสมมติฐาน (Assumptions) ของโมเดลให้ชัดเจนเสมอ (เช่น Incompressible, Newtonian, Steady-state)

## 1. การจัดวางและรูปแบบ (Layout & Formatting)
- [ ] **Clean Headers**: ห้ามมี Attributes `{#...}` ต่อท้ายหัวข้อ (Obsidian ไม่รองรับ)
  - *ผ่าน*: `## 1. Theory`
  - *ไม่ผ่าน*: `## 1. Theory {#theory}`
- [ ] **Wiki-Link TOC**: สารบัญต้องใช้รูปแบบ Wiki-links เพื่อความยืดหยุ่น
  - *ผ่าน*: `- [[#1. Theory|1. Theory]]`
  - *ไม่ผ่าน*: `- [1. Theory](#1-theory)`
- [ ] **Callout Syntax**: ใช้รูปแบบ `> [!TYPE] Title` สำหรับกล่องข้อความ
  - Types ที่แนะนำ: `INFO`, `TIP`, `WARNING`, `DANGER`, `SUCCESS`
  - **Foldable**: ใช้ `> [!TYPE]- Title` (มีเครื่องหมายลบ) เพื่อพับเก็บเนื้อหายาวๆ หรือเฉลย
- [ ] **LaTeX Math**:
  - `$$...$$` ต้อง **ไม่มี** backticks ครอบ (Obsidian rend ering limitation)
    - *ผ่าน*: `$$ \nabla \cdot U = 0 $$`
    - *ไม่ผ่าน*: `` `$$ \nabla \cdot U = 0 $$` ``
  - Inline `$...$` ต้องไม่มี backticks ครอบเช่นกัน
  - **Typography Rules**:
    - Vectors: ใช้ `\mathbf{U}` ( ตัวหนา) เท่านั้น (ห้ามใช้ `\vec{U}`)
    - Subscripts: ใช้ `\text{}` สำหรับคำบรรยาย (e.g., `\rho_{\text{liquid}}`)
    - Brackets: ใช้ `\left( ... \right)` สำหรับสมการเศษส่วน
- [ ] **Hyperlinks**: ใช้ Wiki-links `[[Page Name]]` เสมอ (ห้ามใช้ Plain text อ้างถึงบทเรียนอื่น)
- [ ] **Code Blocks**:
  - ต้องระบุภาษาเสมอ (e.g., `cpp`, `bash`, `cmake`)
  - **ห้าม** ใช้ `text` เป็นตัวปิด block (เช่น ` ```text `); ให้ใช้ ` ``` ` เปล่าๆ เท่านั้น
  - จำนวนเปิด ` ``` ` และปิด ` ``` ` ต้องเท่ากันในทั้งไฟล์

## 2. การอ่านง่ายและลื่นไหล (Readability & Flow) - **CRITICAL**
- [ ] **Short Paragraphs**: จำกัดความยาวพารากราฟไม่เกิน 3-5 บรรทัด (หลีกเลี่ยง "Wall of Text")
- [ ] **Visual Scannability**: 
  - ใช้ **ตัวหนา (Bold)** เน้นคำสำคัญหรือ Concept หลัก
  - ใช้ Bullet points หรือ Numbered lists เมื่อต้องอธิบายขั้นตอนหรือรายการ
- [ ] **Sectioning**: แบ่งเนื้อหาเป็นข้อย่อยๆ (Header 3, 4) เพื่อให้พักสายตา
- [ ] **Natural Flow**: ภาษาต้องลื่นไหลแบบ "Engineering Thai" ไม่รู้สึกเหมือนอ่าน Google Translate

## 3. ความถูกต้องทางเทคนิค (Technical Accuracy)
- [ ] **Natural Tone**: ใช้ "Engineering Thai" (ภาษาช่าง/วิศวกร) ที่ลื่นไหล
  - *ผ่าน*: "รัน Solver", "เซ็ตค่า Boundary", "รัน Parallel"
  - *ไม่ผ่าน*: "ดำเนินการตัวแก้ปัญหา", "ตั้งค่าขอบเขต", "ทำงานแบบขนาน"
- [ ] **Terminology (ศัพท์เทคนิค)**:
  - ทับศัพท์คำที่วงการใช้กันแพร่หลาย (เช่น Field, Mesh, Scheme, Discretization, Flux, Gradient)
  - วงเล็บภาษาอังกฤษกำกับคำศัพท์สำคัญเมื่อใช้ครั้งแรก เช่น "การอนุรักษ์มวล (Mass Conservation)"
- [ ] **No Over-Translation**: **ห้ามแปล** ชื่อตัวแปร, ชื่อคลาส, หรือ Keyword ในโค้ดเด็ดขาด
  - *ผิด*: `volScalarField` -> `สนามสเกลาร์เชิงปริมาตร` (ในโค้ดต้องใช้ทับศัพท์)

## 4. รูปภาพและสื่อ (Visuals & Media)
- [ ] **Image Embedding**: รูปภาพต้องใช้ Syntax [[...]] ของ Obsidian
  - *ผ่าน*: `![[image.png]]` หรือ `![[image.png|500]]`
  - *ไม่ผ่าน*: `![text](http/link)` หรือ `![text](/abs/path)`
- [ ] **Image Location**: ไฟล์รูปภาพต้องย้ายไปเก็บที่โฟลเดอร์ `images/` หรือ `assets/` ในไดเรกทอรีเดียวกัน
- [ ] **Mermaid Diagram (Responsive Style)**:
  - **No Hardcoded Font**: ห้ามใส่ `fontSize` หรือ `fontFamily` แบบ Hardcode ใน `%%{init...}%%` เพื่อให้รองรับ Dark/Light mode และ Mobile
  - **Type**:
    - ใช้ `flowchart TD` (หรือ `LR`) แทน `graph` เพื่อการเรนเดอร์ที่ดีกว่า
    - ใช้ `classDiagram` สำหรับ Class Hierarchy โดยใช้ `direction LR` หาก Diagram กว้าง
    - ใช้ `direction TB` สำหรับ Flowchart ที่ยาว
  - **Inheritance**: ใช้เส้นลูกศรให้ถูกความหมาย UML (`<|--` for inheritance, `*--` for composition)
  - **Clean Labels**: หลีกเลี่ยง Label ที่ซ้ำซ้อนบนเส้นลูกศร (เช่น `: stores` บนเส้น inheritance)

## 5. โครงสร้างบทเรียน (Pedagogical Structure)
- [ ] **Learning Objectives**: ระบุวัตถุประสงค์การเรียนรู้ที่ชัดเจนตอนต้นบท
- [ ] **Concept Checks**: ต้องมีคำถามทดสอบความเข้าใจ 3-5 ข้อ พร้อมเฉลย (ซ่อนใน Quote หรือ Foldout)
- [ ] **Summary**: ต้องมีบทสรุปปิดท้าย Section หลักเสมอ สรุป Key Takeaway
- [ ] **Practical Tasks**: มีส่วนงานปฏิบัติ (Hands-on) ที่ชัดเจน ทำตามได้จริง และโค้ดนำไปรันได้

## 6. การตรวจสอบความถูกต้อง (Final QC)
- [ ] **Code Verification**: 
  - โค้ดตัวอย่างต้องถูกต้องตามหลัก Syntax C++ ของ OpenFOAM (เช็ค `;`, `}`, `namespace`)
  - ตรวจสอบชื่อ Class และ Function ให้ตรงกับเวอร์ชัน OpenFOAM ที่อ้างอิง
- [ ] **Content Completeness (Truncation Check)**:
  - ไฟล์ต้องไม่จบกลางประโยค หรือจบด้วย `**` หรือ `\`
  - เช็คคำว่า `Condition` หรือ `if` ที่ท้าย code blocks ว่าไม่ขาดหาย
- [ ] **Structure Integrity**:
  - ลำดับ Header ต้องต่อเนื่อง (e.g., ไม่กระโดดจาก 1.2 ไป 3.1)
  - ไม่มี Duplicate Headers (เช็คหัวข้อซ้ำ)
- [ ] **Broken Links**: ลิงก์ภายใน (Internal Links) ต้องคลิกแล้วกระโดดไปถูกที่
- [ ] **Metadata**: ส่วน Frontmatter ครบถ้วน
  - `tags`: [openfoam, cfd, ...]
  - `date`: YYYY-MM-DD
  - `topic`: หัวข้อหลัก
  - `difficulty`: beginner / intermediate / advanced / hardcore

## 7. Common Pitfalls & Automated Checks (ตรวจสอบด้วย grep)
- [ ] **Backtick-wrapped LaTeX**: `grep '`$$' filename.md` (ต้องไม่พบผลลัพธ์)
- [ ] **Duplicate Frontmatter Keys**: `grep -c '^tags:' filename.md` (ต้องได้ 1)
- [ ] **Unclosed Code Blocks**: `grep -c '^```' filename.md` (ต้องเป็นเลขคู่เสมอ)
- [ ] **Table Integrity**: เช็คว่าไม่มี `|` เปล่าๆ ใน Math mode (ใช้ `\lvert`, `\vert` แทน)