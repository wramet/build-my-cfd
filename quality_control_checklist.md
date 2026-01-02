# OpenFOAM Content Quality Control Checklist

รายการตรวจสอบความถูกต้องของเนื้อหาก่อนส่งมอบงาน (Must be checked before marking task as complete).

## 1. การจัดวางและรูปแบบ (Layout & Formatting)
- [ ] **Clean Headers**: ห้ามมี Attributes `{#...}` ต่อท้ายหัวข้อ (Obsidian ไม่รองรับ)
  - *ผ่าน*: `## 1. Theory`
  - *ไม่ผ่าน*: `## 1. Theory {#theory}`
- [ ] **Wiki-Link TOC**: สารบัญต้องใช้รูปแบบ Wiki-links เพื่อความยืดหยุ่น
  - *ผ่าน*: `- [[#1. Theory|1. Theory]]`
  - *ไม่ผ่าน*: `- [1. Theory](#1-theory)`
- [ ] **Callout Syntax**: ใช้รูปแบบ `> [!TYPE] Title` สำหรับกล่องข้อความ
  - Types ที่แนะนำ: `INFO`, `TIP`, `WARNING`, `DANGER`, `SUCCESS`
- [ ] **LaTeX Math**: สมการต้องอยู่ในบล็อก `$$...$$` หรือ Inline `$...$` อย่างถูกต้อง
- [ ] **Code Blocks**: ต้องระบุภาษาเสมอ (e.g., `cpp`, `bash`, `xml` สำหรับ dictionaries)

## 2. ภาษาและการแปล (Language & Translation)
- [ ] **Natural Tone**: ใช้ "Engineering Thai" (ภาษาช่าง/วิศวกร) ที่ลื่นไหล
  - *ผ่าน*: "รัน Solver", "เซ็ตค่า Boundary", "รัน Parallel"
  - *ไม่ผ่าน*: "ดำเนินการตัวแก้ปัญหา", "ตั้งค่าขอบเขต", "ทำงานแบบขนาน"
- [ ] **Terminology (ศัพท์เทคนิค)**:
  - ทับศัพท์คำที่วงการใช้กันแพร่หลาย (เช่น Field, Mesh, Scheme, Discretization, Flux, Gradient)
  - วงเล็บภาษาอังกฤษกำกับคำศัพท์สำคัญเมื่อใช้ครั้งแรก เช่น "การอนุรักษ์มวล (Mass Conservation)"
- [ ] **No Over-Translation**: **ห้ามแปล** ชื่อตัวแปร, ชื่อคลาส, หรือ Keyword ในโค้ดเด็ดขาด
  - *ผิด*: `volScalarField` -> `สนามสเกลาร์เชิงปริมาตร` (ในโค้ดต้องใช้ทับศัพท์)

## 3. รูปภาพและสื่อ (Visuals & Media)
- [ ] **Image Embedding**: รูปภาพต้องใช้ Syntax [[...]] ของ Obsidian
  - *ผ่าน*: `![[image.png]]` หรือ `![[image.png|500]]`
  - *ไม่ผ่าน*: `![text](http/link)` หรือ `![text](/abs/path)`
- [ ] **Image Location**: ไฟล์รูปภาพต้องย้ายไปเก็บที่โฟลเดอร์ `images/` หรือ `assets/` ในไดเรกทอรีเดียวกัน
- [ ] **Mermaid Diagram (Responsive Style)**:
  - **No Hardcoded Font**: ห้ามใส่ `fontSize` หรือ `fontFamily` แบบ Hardcode ใน `%%{init...}%%` เพื่อให้รองรับ Dark/Light mode และ Mobile
  - **Type**:
    - ใช้ `flowchart TD` (หรือ `LR`) แทน `graph` เพื่อการเรนเดอร์ที่ดีกว่า
    - ใช้ `classDiagram` สำหรับ Class Hierarchy โดยใช้ `direction LR` หาก Diagram กว้าง
  - **Inheritance**: ใช้เส้นลูกศรให้ถูกความหมาย UML (`<|--` for inheritance, `*--` for composition)
  - **Clean Labels**: หลีกเลี่ยง Label ที่ซ้ำซ้อนบนเส้นลูกศร (เช่น `: stores` บนเส้น inheritance)

## 4. โครงสร้างบทเรียน (Pedagogical Structure)
- [ ] **Learning Objectives**: ระบุวัตถุประสงค์การเรียนรู้ที่ชัดเจนตอนต้นบท
- [ ] **Concept Checks**: ต้องมีคำถามทดสอบความเข้าใจ 3-5 ข้อ พร้อมเฉลย (ซ่อนใน Quote หรือ Foldout)
- [ ] **Summary**: ต้องมีบทสรุปปิดท้าย Section หลักเสมอ สรุป Key Takeaway
- [ ] **Practical Tasks**: มีส่วนงานปฏิบัติ (Hands-on) ที่ชัดเจน ทำตามได้จริง และโค้ดนำไปรันได้

## 5. การตรวจสอบความถูกต้อง (Final QC)
- [ ] **Code Verification**: 
  - โค้ดตัวอย่างต้องถูกต้องตามหลัก Syntax C++ ของ OpenFOAM (เช็ค `;`, `}`, `namespace`)
  - ตรวจสอบชื่อ Class และ Function ให้ตรงกับเวอร์ชัน OpenFOAM ที่อ้างอิง
- [ ] **Broken Links**: ลิงก์ภายใน (Internal Links) ต้องคลิกแล้วกระโดดไปถูกที่
- [ ] **Metadata**: ส่วน Frontmatter ครบถ้วน
  - `tags`: [openfoam, cfd, ...]
  - `date`: YYYY-MM-DD
  - `topic`: หัวข้อหลัก
  - `difficulty`: beginner / intermediate / advanced / hardcore