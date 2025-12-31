---
name: Refactor Assistant
description: |
  Use this skill when: user asks to refactor content, clean up markdown, fix code style, remove redundant TOCs, or standardize file structure.
  
  Specialist in content maintenance and refactoring for the project.
---

# Refactor Assistant

ผู้ช่วยในการจัดระเบียบและปรับปรุงคุณภาพไฟล์ (Content Refactoring & Cleanup)

## Refactoring Rules

### 1. Structure Cleanup
- **Remove TOCs:** ลบ Table of Contents ที่สร้างด้วยมือ (Markdown มี TOC ในตัวอยู่แล้ว)
- **Flatten Headers:** อย่าซ้อน header ลึกเกินไป (Deep nesting is bad)
- **Standard Sections:**
  1. `00_Overview.md` ต้องมี Learning Objectives
  2. เนื้อหาหลัก
  3. Concept Check (ท้ายบท)
  4. Related Documents

### 2. Code Stylist
- **OpenFOAM Standard:**
  - Class name: `PascalCase`
  - Variable name: `camelCase`
  - Indentation: 4 spaces
  - `{` บนบรรทัดใหม่ (Allman style)
- **Markdown Code Blocks:**
  - ระบุภาษาเสมอ: `cpp`, `python`, `bash` (ห้ามใช้ `c++` ให้ใช้ `cpp`)

### 3. Link Validation
- **Relative Links:** ตรวจลอบลิงก์ข้ามไฟล์ `[Link](../Folder/File.md)`
- **Broken Links:** แจ้งเตือนเมื่อลิงก์ไปยังไฟล์ที่ไม่มีอยู่จริง

## Refactoring Workflows

### Scenario A: "Content นี้อ่านยากมาก ช่วยจัดหน้าให้หน่อย"
1. **Remove Clutter:** ลบ intro ที่เยิ่นเย้อ, ลบ TOC
2. **Add Headers:** เพิ่ม `## Why This Matters` และ `## Key Takeaways`
3. **Format Code:** จัด code block ให้สวยงาม

### Scenario B: "Code นี้ไม่ตรง Standard ของ OpenFOAM"
1. **Fix Naming:** เปลี่ยน `my_variable` -> `myVariable`
2. **Fix Braces:** ย้าย `{` ลงมาบรรทัดใหม่
3. **Add Comments:** เพิ่ม Doxygen style comments `//- Description`

## Trigger Examples

- "Refactor file นี้ให้หน่อย"
- "ลบ TOC ออกทั้งหมด"
- "จัด format code ให้ตรงตาม OpenFOAM standard"
