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
- [ ] **LaTeX Math**: สมการต้องอยู่ในบล็อก `$$...$$` หรือ Inline `$...$` อย่างถูกต้อง

## 2. ภาษาและการแปล (Language & Translation)
- [ ] **Natural Tone**: ใช้ "Engineering Thai" (ภาษาช่าง/วิศวกร) ที่ลื่นไหล ไม่ใช่ภาษาแปล Google Translate
- [ ] **Terminology (ศัพท์เทคนิค)**:
  - ทับศัพท์คำที่วงการใช้กันแพร่หลาย (เช่น Field, Mesh, Scheme, Discretization)
  - วงเล็บภาษาอังกฤษกำกับคำศัพท์สำคัญเมื่อใช้ครั้งแรก เช่น "การอนุรักษ์มวล (Mass Conservation)"
- [ ] **No Over-Translation**: **ห้ามแปล** ชื่อตัวแปร, ชื่อคลาส, หรือ Keyword ในโค้ดเด็ดขาด
  - *ผิด*: `volScalarField` -> `สนามสเกลาร์เชิงปริมาตร` (ในโค้ดต้องใช้ทับศัพท์)

## 3. รูปภาพและสื่อ (Visuals & Media)
- [ ] **Image Embedding**: รูปภาพต้องใช้ Syntax [[...]] ของ Obsidian
  - *ผ่าน*: `![[image.png]]` หรือ `![[image.png|500]]`
  - *ไม่ผ่าน*: `![text](http/link)` หรือ `![text](/abs/path)`
- [ ] **Image Location**: ไฟล์รูปภาพต้องย้ายไปเก็บที่โฟลเดอร์ `assets/` ในไดเรกทอรีเดียวกัน
- [ ] **Mermaid Diagram**:
  - *Header*: ใส่ `%%{init: { "theme": "default", "useMaxWidth": false, "themeVariables": { "fontSize": "20px", "fontFamily": "Consolas, 'Courier New', monospace" } }}%%`
  - *Direction*: ใช้ `direction LR` ใน `classDiagram` เพื่อขยายออกด้านข้าง
  - *Structure*: สำหรับ Graph/Flowchart ใช้ `classDef` ช่วยจัด Styling

## 4. โครงสร้างบทเรียน (Pedagogical Structure)
- [ ] **Concept Checks**: ต้องมีคำถามทดสอบความเข้าใจ 3-5 ข้อ พร้อมเฉลย (ซ่อนใน Quote หรือ Foldout)
- [ ] **Summary**: ต้องมีบทสรุปปิดท้าย Section หลักเสมอ (ห้ามตัดจบดื้อๆ)
- [ ] **Practical Tasks**: มีส่วนงานปฏิบัติ (Hands-on) ที่ชัดเจนและทำตามได้จริง

## 5. การตรวจสอบความถูกต้อง (Final QC)
- [ ] **Code Check**: โค้ดตัวอย่างต้องถูกต้องตามหลัก Syntax C++ ของ OpenFOAM
- [ ] **Broken Links**: ลิงก์ภายใน (Internal Links) ต้องคลิกแล้วกระโดดไปถูกที่
- [ ] **Metadata**: ส่วน Frontmatter (`tags`, `date`, `topic`) ครบถ้วน
