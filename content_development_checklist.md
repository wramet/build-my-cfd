# 📝 Content Development Checklist (Universal)

คู่มือตรวจสอบการพัฒนาเนื้อหาสำหรับเอกสารการเรียนรู้ทุกประเภท

---

## 🎯 หลักการพื้นฐาน: "3W Framework"

ทุกเนื้อหาต้องตอบ 3 คำถามนี้:

| คำถาม | ความหมาย | ตัวอย่าง |
|-------|----------|---------|
| **What** | คืออะไร/ทำอะไร | "Crank-Nicolson คือ time integration scheme" |
| **Why** | ทำไมต้องใช้/ข้อดีข้อเสีย | "ใช้เพราะ 2nd order accurate และ energy conserving" |
| **How** | ใช้อย่างไร/ตัวอย่าง | "ตั้งค่าใน fvSchemes: `default CrankNicolson 0.5;`" |

---

## ✅ Section 1: โครงสร้างเนื้อหา (Content Structure)

### 1.1 บทนำ (Introduction)
- [ ] มีคำอธิบายสั้นๆ ว่าหัวข้อนี้คืออะไร (1-2 ประโยค)
- [ ] มีบริบทว่าหัวข้อนี้อยู่ในภาพรวมอย่างไร
- [ ] มี prerequisites (ถ้ามี) — "ควรอ่าน X ก่อน"
- [ ] มี learning objectives — "หลังจบบทนี้จะสามารถ..."

### 1.2 เนื้อหาหลัก (Main Content)
- [ ] จัดลำดับจากง่ายไปยาก
- [ ] แต่ละหัวข้อย่อยมีความยาวเหมาะสม (ไม่ยาวเกินไป)
- [ ] มี transitions ระหว่างหัวข้อ
- [ ] ไม่มี orphan sections (หัวข้อที่โดดเดี่ยว)

### 1.3 สรุป (Summary)
- [ ] มี Quick Reference / Cheat Sheet
- [ ] มี Key Takeaways (3-5 ข้อ)
- [ ] มีลิงก์ไปเนื้อหาที่เกี่ยวข้อง

---

## ✅ Section 2: ความลึกของเนื้อหา (Content Depth)

### 2.1 คำอธิบายทฤษฎี
- [ ] **What**: อธิบายว่าคืออะไร
- [ ] **Why**: อธิบายว่าทำไมต้องใช้ / ข้อดีข้อเสีย
- [ ] **When**: อธิบายว่าใช้เมื่อไหร่ / สถานการณ์ที่เหมาะสม
- [ ] **How**: อธิบายกลไกการทำงาน

### 2.2 สูตรและการคำนวณ
- [ ] มีสูตรทางคณิตศาสตร์ (ถ้าเกี่ยวข้อง)
- [ ] มีคำอธิบายตัวแปรในสูตร
- [ ] มีตัวอย่างการคำนวณพร้อมค่าจริง
- [ ] มีที่มาของค่าคงที่/พารามิเตอร์

### 2.3 การเปรียบเทียบ
- [ ] มีตารางเปรียบเทียบทางเลือกต่างๆ (ถ้ามีหลายวิธี)
- [ ] ระบุ pros/cons ของแต่ละทางเลือก
- [ ] มีคำแนะนำว่าเมื่อไหร่ควรใช้อะไร

---

## ✅ Section 3: ตัวอย่างและโค้ด (Examples & Code)

### 3.1 ความสมบูรณ์ของตัวอย่าง
- [ ] โค้ดตัวอย่างพร้อมใช้งาน (copy-paste ได้)
- [ ] มี comments อธิบายทุกส่วนสำคัญ
- [ ] ระบุ context ว่าโค้ดอยู่ในไฟล์ไหน
- [ ] ระบุ version/compatibility (ถ้าจำเป็น)

### 3.2 Case Setup (สำหรับ Simulation)
- [ ] มี directory structure ครบถ้วน
- [ ] มี boundary conditions ครบทุก field ที่จำเป็น
- [ ] มี numerical settings (fvSchemes, fvSolution)
- [ ] มี controlDict settings ที่เหมาะสม

### 3.3 ความทันสมัย
- [ ] โค้ดใช้ syntax ที่ทันสมัย
- [ ] ไม่ใช้ deprecated functions/methods
- [ ] ตรงกับ version ที่ระบุ

---

## ✅ Section 4: Visual Content

### 4.1 Diagrams และ Flowcharts
- [ ] Algorithms มี flowchart (Mermaid)
- [ ] Workflows มี process diagram
- [ ] Hierarchies มี tree diagram
- [ ] Comparisons มี side-by-side layout

### 4.2 Tables
- [ ] Options/Choices มีตารางเปรียบเทียบ
- [ ] Parameters มีตารางค่าและคำอธิบาย
- [ ] Errors มีตาราง troubleshooting

### 4.3 ASCII Diagrams (สำหรับ technical)
- [ ] Data structures มี memory layout
- [ ] Mesh concepts มี cell/face diagrams
- [ ] Patterns มี schematic representation

---

## ✅ Section 5: Troubleshooting และ Common Mistakes

### 5.1 ตาราง Troubleshooting
- [ ] มีตาราง "ปัญหา | สาเหตุ | วิธีแก้"
- [ ] ครอบคลุม errors ที่พบบ่อยที่สุด 3-5 ข้อ
- [ ] ระบุ error messages ที่เห็นจริง (ถ้ามี)

### 5.2 Common Mistakes / Pitfalls
- [ ] ระบุข้อผิดพลาดที่พบบ่อย
- [ ] อธิบายว่าทำไมถึงเป็นข้อผิดพลาด
- [ ] บอกวิธีหลีกเลี่ยง

### 5.3 Best Practices
- [ ] มี Dos and Don'ts
- [ ] มี Tips จากผู้เชี่ยวชาญ
- [ ] มี Performance considerations (ถ้าเกี่ยวข้อง)

---

## ✅ Section 6: Interactive Elements

### 6.1 Concept Check Questions
- [ ] มีคำถามตรวจสอบความเข้าใจ 2-3 ข้อ
- [ ] คำถามครอบคลุมเนื้อหาสำคัญ
- [ ] มีคำตอบซ่อนอยู่ (collapsible)
- [ ] คำถามหลากหลายระดับ (ง่าย → ยาก)

### 6.2 Exercises (ถ้าเหมาะสม)
- [ ] มีแบบฝึกหัดระดับ beginner
- [ ] มีแบบฝึกหัดระดับ intermediate
- [ ] มีแบบฝึกหัดระดับ advanced
- [ ] มี hints สำหรับแบบฝึกหัดยาก

---

## ✅ Section 7: Navigation และ Cross-References

### 7.1 Internal Links
- [ ] มีลิงก์ไปเอกสารก่อนหน้า/ถัดไป
- [ ] มีลิงก์ไป Overview ของหัวข้อ
- [ ] มีลิงก์ไปเนื้อหาที่เกี่ยวข้อง
- [ ] ลิงก์ทั้งหมดทำงานได้ถูกต้อง

### 7.2 External References
- [ ] มีการอ้างอิงแหล่งข้อมูล (ถ้าจำเป็น)
- [ ] มีลิงก์ไป official documentation
- [ ] มีลิงก์ไป tutorials เพิ่มเติม (ถ้ามี)

---

## ✅ Section 8: Quality Assurance

### 8.1 ภาษาและการเขียน
- [ ] ภาษาถูกต้องตลอดทั้งเอกสาร
- [ ] ไม่มีภาษาอื่นปน (จีน, อังกฤษที่ไม่จำเป็น)
- [ ] terminology สม่ำเสมอ
- [ ] ไม่มี typos

### 8.2 Formatting
- [ ] Headers มีลำดับถูกต้อง (H1 → H2 → H3)
- [ ] Code blocks มี syntax highlighting
- [ ] Lists มี format สม่ำเสมอ
- [ ] Callouts/Notes ใช้ถูกประเภท

### 8.3 Technical Accuracy
- [ ] ข้อมูลถูกต้องตาม physics/theory
- [ ] โค้ดตัวอย่างทดสอบแล้ว
- [ ] ค่าพารามิเตอร์สมเหตุสมผล
- [ ] สูตรถูกต้อง

---

## 📊 Scoring Guide

ใช้ checklist นี้เพื่อประเมินความสมบูรณ์ของเนื้อหา:

| Score | ระดับ | คำอธิบาย |
|-------|-------|----------|
| **90-100%** | ⭐⭐⭐ Excellent | พร้อมเผยแพร่ |
| **70-89%** | ⭐⭐ Good | ต้องปรับปรุงเล็กน้อย |
| **50-69%** | ⭐ Needs Work | ต้องเพิ่มเนื้อหาสำคัญ |
| **<50%** | ❌ Incomplete | ต้อง rewrite |

---

## 📝 Template: Content Review Notes

ใช้ template นี้บันทึกการ review:

```markdown
## Content Review: [ชื่อไฟล์]

**Date:** YYYY-MM-DD
**Reviewer:** [ชื่อ]
**Score:** X/100 (XX%)

### ✅ Passed
- Item 1
- Item 2

### ❌ Missing/Needs Improvement
- [ ] Item 1 — [คำอธิบาย]
- [ ] Item 2 — [คำอธิบาย]

### 📋 Action Items
1. [สิ่งที่ต้องทำ]
2. [สิ่งที่ต้องทำ]
```

---

## 🔄 Content Type-Specific Additions

### สำหรับ Tutorial/How-To
- [ ] มี step-by-step instructions
- [ ] มีหมายเลขขั้นตอนชัดเจน
- [ ] มี expected output ในแต่ละขั้นตอน
- [ ] มี screenshots/diagrams ประกอบ

### สำหรับ Concept/Theory
- [ ] มี analogies ที่ช่วยเข้าใจ
- [ ] มี physical intuition
- [ ] มีการเชื่อมโยงกับ real-world applications
- [ ] มี mathematical derivation (ถ้าเหมาะสม)

### สำหรับ Reference/API
- [ ] มี syntax ครบถ้วน
- [ ] มี parameter descriptions
- [ ] มี return values
- [ ] มี usage examples

### สำหรับ Troubleshooting Guide
- [ ] จัดกลุ่มตามประเภทปัญหา
- [ ] มี error messages ที่แน่นอน
- [ ] มี root cause analysis
- [ ] มี step-by-step fix

---

*Last Updated: 2025-12-30*
*Version: 1.0*
