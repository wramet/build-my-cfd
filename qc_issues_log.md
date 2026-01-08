# QC Issues Log - บันทึกปัญหาที่พบจากการตรวจสอบ

ไฟล์นี้ใช้บันทึกปัญหา syntax และ formatting ที่พบระหว่างการตรวจสอบ Quality Control เพื่อนำไปปรับปรุง checklist ในอนาคต

---

## 📅 2026-01-06: Day 01 LaTeX Syntax Issues

**ไฟล์:** `daily_learning/2026-01-01.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `LATEX-001` | Inline LaTeX | ใช้ backticks ครอบ inline math: `` `$...$` `` ทำให้ Obsidian ไม่ render เป็นสมการ | 🔴 Critical |
| `LATEX-002` | Block LaTeX | ใช้ backticks ครอบ block math: `` `$$...$$` `` ทำให้ Obsidian แสดงเป็น code block แทน | 🔴 Critical |

### ตัวอย่างที่ผิด vs ที่ถูก

**Inline Math:**
```markdown
❌ ผิด: `$\frac{\partial \rho}{\partial t}$`
✅ ถูก: $\frac{\partial \rho}{\partial t}$
```

**Block Math:**
```markdown
❌ ผิด:
`$$
\nabla \cdot \mathbf{U} = 0
$$`

✅ ถูก:
$$
\nabla \cdot \mathbf{U} = 0
$$
```

### จุดที่พบปัญหา (ก่อนแก้ไข)

| Section | บรรทัดโดยประมาณ | จำนวน |
|---------|-----------------|-------|
| Learning Objectives | 9-28 | 8 |
| Section 2.1.1 (Tables) | 42-64 | 15 |
| Section 2.1.2 (RTT) | 76-88 | 5 |
| Section 2.2.1 | 103-119 | 9 |
| Section 2.2.2 (Derivation) | 125-187 | 11 blocks + inline |

**รวมทั้งหมด:** ~48 inline + 11 block equations

### สาเหตุที่น่าจะเป็นไปได้

1. **การ Generate ด้วย LLM:** บาง LLM อาจเพิ่ม backticks ครอบ LaTeX เพื่อป้องกัน parsing issues
2. **Copy-Paste จาก Source อื่น:** การคัดลอกจาก editor ที่ใช้ syntax ต่างกัน
3. **Template ที่ไม่ถูกต้อง:** อาจมี template ที่กำหนด pattern ผิด

### การแก้ไข

- ✅ แก้ไขแบบ Manual โดยเอา backticks ออกจากทั้ง inline และ block LaTeX
- ✅ ตรวจสอบด้วย `grep -c '\`\$' filename.md` เพื่อยืนยันว่าไม่เหลือปัญหา

### ข้อเสนอแนะสำหรับ QC Checklist

```markdown
## LaTeX Syntax Check (เพิ่มใน quality_control_checklist.md)

### Pre-check Command
```bash
# ตรวจหา backtick-wrapped LaTeX
grep -c '`\$' <filename>.md
# ถ้าผลเป็น 0 = ผ่าน, มากกว่า 0 = มีปัญหา
```

### Visual Check
- [ ] Inline math `$...$` ไม่มี backticks ครอบ
- [ ] Block math `$$...$$` ไม่มี backticks ครอบ
- [ ] Preview ใน Obsidian แสดงสมการถูกต้อง (ไม่เป็นกล่องสีเทา)
```

---

## 📝 หมายเหตุ

- เพิ่มปัญหาใหม่ที่พบได้โดยใช้ format เดียวกันกับด้านบน
- ปรับปรุง `quality_control_checklist.md` ตามข้อเสนอแนะหลังจากสะสมปัญหาเพียงพอ

---

## 📅 2026-01-06: Day 02 Markdown Table & LaTeX Issues

**ไฟล์:** `daily_learning/2026-01-02.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `TABLE-001` | Markdown Table | ใช้ `\|` สำหรับ absolute value ใน LaTeX ภายใน table cell ทำให้ parser เข้าใจผิดว่าเป็นตัวแบ่งคอลัมน์ | 🔴 Critical |
| `LATEX-003` | LaTeX Typography | ใช้ text ภาษาอังกฤษใน superscript โดยไม่ใช้ `\text{}` เช่น `$F_f^{owner}$` ทำให้ฟอนต์เอียงและห่างกัน | 🟡 Minor |

### ตัวอย่างที่ผิด vs ที่ถูก

**Absolute Value in Tables:**
```markdown
❌ ผิด: | $f_x$ | ... | $f_x = |C_N - C_f| / |C_N - C_P|$ |
   (| ถูกตีความเป็น column separator)

✅ ถูก: | $f_x$ | ... | $f_x = \lvert C_N - C_f \rvert / \lvert C_N - C_P \rvert$ |
```

**LaTeX Text Superscript:**
```markdown
❌ ผิด: $F_f^{owner}$ และ $F_f^{neighbor}$
   (ตัวอักษร owner/neighbor จะเอียงและห่างกันเหมือนกับ o×w×n×e×r)

✅ ถูก: $F_f^{\text{owner}}$ และ $F_f^{\text{neighbor}}$
```

### จุดที่พบปัญหา (ก่อนแก้ไข)

| Section | บรรทัด | ปัญหา |
|---------|--------|-------|
| 1.1.2 (ตาราง ตัวแปรสำคัญ) | 94-100 | `\|` in LaTeX breaking table, extra empty columns |
| 1.3.1 (Owner-Neighbor) | 151, 154 | Missing `\text{}` for superscripts |
| Section 4 (Common Bugs Table) | 1187 | `\|` in LaTeX breaking table |

### การแก้ไข

1. ✅ แปลง `|` เป็น `\lvert` และ `\rvert` สำหรับ absolute value
2. ✅ เพิ่ม `\text{}` ครอบ text ใน superscripts
3. ✅ ลบ empty columns ที่เกิดจาก broken table syntax

### ข้อเสนอแนะสำหรับ QC Checklist

```markdown
## Markdown Table Syntax Check (เพิ่มใน quality_control_checklist.md)

### Table + LaTeX Rules
- [ ] ห้ามใช้ `|` เปล่าๆ ใน LaTeX ภายใน table cells → ใช้ `\lvert`/`\rvert` หรือ `\vert` แทน
- [ ] ใช้ `\text{}` ครอบ text ภาษาอังกฤษใน math mode
- [ ] ตรวจสอบว่าจำนวน columns ในทุกแถวของตารางเท่ากัน
```

---

## 📅 2026-01-06: Day 03 Structural & Code Block Issues

**ไฟล์:** `daily_learning/2026-01-03.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `CODE-001` | Unclosed Code Block | Code ใน Section 2.3 ถูกตัดจบที่ `WarningInFunction` โดยไม่มี ``` ปิดท้าย | 🔴 Critical |
| `STRUCT-001` | Duplicate H1 Header | มี `# Day 03: ...` สองครั้ง (บรรทัด 10 และ 55) | 🟡 Moderate |
| `STRUCT-002` | Section Numbering | `### 4.1, 4.2, 4.3` อยู่ใต้ `## 3.` (ควรเป็น 3.1, 3.2, 3.3) | 🟡 Moderate |

### การแก้ไข

1. ✅ ปิด code block โดยเพิ่ม closing braces และ ``` พร้อม warning note
2. ✅ ลบ duplicate H1 ที่บรรทัด 55
3. ✅ แก้ section numbering: 4.1→3.1, 4.2→3.2, 4.3→3.3

---

## 📅 2026-01-06: Day 04 LaTeX & Typo Issues

**ไฟล์:** `daily_learning/2026-01-04.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `LATEX-001` | Backtick-wrapped LaTeX | ใช้ backticks ครอบ inline math เช่น `` `$\Delta t$` `` | 🔴 Critical |
| `TYPO-001` | Typo | เขียน "CRL" แทน "CFL" (Courant-Friedrichs-Lewy) | 🟡 Moderate |
| `STRUCT-003` | Truncated Content | Section 4.4 ถูกตัดกลางประโยค และกระโดดไป Section 2 | 🟡 Moderate |

### จุดที่พบปัญหา (ก่อนแก้ไข)

| ปัญหา | บรรทัด | รายละเอียด |
|-------|--------|------------|
| Backtick LaTeX | 18, 41, 42, 47, 50, 52 | 6 จุดใน Learning Objectives |
| CRL typo | 33, 41, 301 | 3 จุดที่เขียน CRL แทน CFL |
| Truncated section | 211 | Section 4.4 ถูกตัดจบที่ "...ไม่ใช่ Temporal Scheme" |

### การแก้ไข

1. ✅ ลบ backticks ออกจาก inline LaTeX ทั้ง 6 จุด
2. ✅ แก้ CRL → CFL ทั้ง 3 จุด
3. ✅ เพิ่มเนื้อหาที่หายไปที่บรรทัด 211 พร้อม warning note

---

## 📅 2026-01-06: Day 05 LaTeX & Truncation Issues

**ไฟล์:** `daily_learning/2026-01-05.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `LATEX-001` | Backtick-wrapped LaTeX | ใช้ backticks ครอบ inline math: `` `$\mathbf{S}_f$` `` | 🔴 Critical |
| `TRUNC-001` | Truncated Content | Concept Check 3 ถูกตัดกลางประโยคแล้วกระโดดไป References | 🔴 Critical |

### จุดที่พบปัญหา (ก่อนแก้ไข)

| บรรทัด | ปัญหา |
|--------|-------|
| 22 | Backtick: `` `$\mathbf{S}_f = A_f...` `` |
| 215 | Backtick: `` `$\mathbf{S}_f` `` |
| 2062 | Backtick: `` `$\mathbf{S}_f` `` |
| 2113 | Backtick: `` `$\mathbf{S}_f` `` |
| 2273 | Content truncated mid-sentence, jumped to References |

### การแก้ไข

1. ✅ ลบ backticks ทั้ง 4 จุด
2. ✅ เพิ่มเนื้อหาที่หายไปใน Concept Check 3 (gradient formula และ explanation)

---

## 📅 2026-01-06: Day 06 Structure & Numbering Issues

**ไฟล์:** `daily_learning/2026-01-06.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `STRUCT-001` | Section Numbering | Section กระโดดจาก `## 1.2` ไป `# 3. Section 2` (ข้าม Section 2) | 🟡 Moderate |
| `STRUCT-002` | Duplicate Headers | มี `## 3.1` และ `## 3.2` ซ้ำกัน 2 ครั้ง (ที่ L206/L351 และ L681/L724) | 🟡 Moderate |
| `CODE-001` | C++ Template | `applyToMatrix()` รับ `Field<scalar>& source` แต่ใช้กับ template FieldType ที่อาจเป็น vector | 🟠 Minor (Tutorial style) |
| `TYPO-001` | Terminology | "Interpolated" ควรเป็น "Extrapolated" สำหรับ Zero Gradient | 🟢 Trivial |

### ลำดับ Section ที่พบ (ซ้ำซ้อน/กระโดด)

```
L19:  ## Learning Objectives
L52:  ## 1.1 Fundamental Types...
L131: ---## 1.2 Inlet... (ติดกับ ---)
L203: # 3. Section 2: OpenFOAM Reference
L206: ## 3.1 วิเคราะห์ Class: GeometricBoundaryField
L351: ## 3.2 วิเคราะห์ Class: fvPatchField
L525: ## 3.3 วิเคราะห์ Class: fvPatch
L678: # 4. Section 3: Class Design
L681: ## 3.1 ภาพรวมสถาปัตยกรรม  ← DUPLICATE!
L724: ## 3.2 รายละเอียดการออกแบบ  ← DUPLICATE!
```

### การแก้ไขที่แนะนำ (Refactor Needed)

ต้อง renumber sections ใหม่ทั้งหมด:
- `## 1.1, 1.2` → OK (Theory)
- `# 3. Section 2` → `## 2. OpenFOAM Reference`
- `## 3.1-3.3` (ใน Section 2) → `### 2.1-2.3`
- `# 4. Section 3` → `## 3. Class Design`
- `## 3.1-3.2` (ใน Section 3) → `### 3.1-3.2`

### สถานะ

⏸️ **ยังไม่แก้ไข** - ต้องการ refactor โครงสร้างใหม่ทั้งหมด

---

## 📅 2026-01-06: Day 07 Truncation Issues

**ไฟล์:** `daily_learning/2026-01-07.md`

**ผู้รายงาน:** External QC Review

### ปัญหาที่พบ

| รหัส | ประเภท | รายละเอียด | ความรุนแรง |
|------|--------|------------|------------|
| `TRUNC-001` | Truncated Content | Section 7.3 Convection Term: ตัดจบที่ "การไหลจาก $N$ ไป" | 🔴 Critical |
| `TRUNC-002` | Truncated Code | `ownerStartAddr()` code หยุดที่ `if` | 🔴 Critical |
| `TRUNC-003` | Truncated Content | Concept Check 5: ตัดจบที่ "เหตุผลที่ต้องแปลงจาก LDU" | 🟡 Moderate |
| `SYNTAX-001` | Code Block | มี ````text` แทน ```` ` ``` ```` ในหลายจุด | 🟢 Minor |

### การแก้ไข

| บรรทัด | ปัญหา | สถานะ |
|--------|-------|-------|
| L337 | Convection term truncated | ✅ เพิ่มเนื้อหาหาก $F_f < 0$ ครบ + summary |
| L832-834 | ownerStartAddr() code cut off | ✅ ปิด code block พร้อม warning note |
| L2419 | Concept Check 5 truncated | ⚠️ ต้อง regenerate เนื้อหาใหม่ |

### หมายเหตุ

- มี ````text` ใช้แทน ```` ` ``` ```` ประมาณ 19 จุด - เป็น minor issue
- ควร regenerate Section 7 (Concept Checks) ทั้งหมดใหม่

---

## 📅 2026-01-06: Days 08-12 Comprehensive QC Review

### Day 08: Iterative Solvers (PCG & PBiCGStab)

| รหัส | ประเภท | รายละเอียด | บรรทัด | ความรุนแรง |
|------|--------|------------|--------|------------|
| `YAML-001` | Duplicate Key | มี `tags:` ซ้ำ 2 ครั้งใน frontmatter | L5, L? | 🔴 Critical |
| `TRUNC-001` | Truncated LaTeX | BiCGStab beta_k สมการถูกตัด | L349 | 🔴 Critical |
| `TRUNC-002` | Truncated Code | IterativeSolverDriver string literal ไม่ปิด | L1668 | 🔴 Critical |
| `TRUNC-003` | Truncated Content | Concept Check answer cut off | ? | 🟡 Moderate |

### Day 09: Pressure-Velocity Coupling (SIMPLE, PISO, Rhie-Chow)

| รหัส | ประเภท | รายละเอียด | บรรทัด | ความรุนแรง |
|------|--------|------------|--------|------------|
| `CODE-001` | Unclosed Code Block | Code blocks ไม่สมดุล (5 ปิด vs 54 เปิด) | หลายจุด | 🔴 Critical |
| `TRUNC-001` | Truncated Code | RhieChowInterpolator code ถูกตัด | Section 3.3.3 | 🔴 Critical |
| `TRUNC-002` | Truncated Code | UnderRelaxationManager ไม่ครบ | Section 4.2.4 | 🔴 Critical |
| `TRUNC-003` | Truncated Content | Concept Check 4 derivation หายไป | Section 7.4 | 🟡 Moderate |

### Day 10: VOF Interface Tracking (Alpha Equation)

| รหัส | ประเภท | รายละเอียด | บรรทัด | ความรุนแรง |
|------|--------|------------|--------|------------|
| `LATEX-001` | Backtick-wrapped LaTeX | ใช้ \`$$...\` แทน $$...$$ | L65,80,108,123,144+ | 🔴 Critical |
| `LATEX-002` | Extra Backtick | มี \` เกินหน้า $mu | Section 6 | 🟡 Moderate |

### Day 11: Phase Change Theory (Lee Model & Linearization)

| รหัส | ประเภท | รายละเอียด | บรรทัด | ความรุนแรง |
|------|--------|------------|--------|------------|
| `TRUNC-001` | Truncated Content | Key Observation จบที่ "ดังนั้น **" | L215 | 🔴 Critical |
| `SYNTAX-001` | Code Block Lang | ใช้ \`\`\`text แทน \`\`\`cpp/cmake | หลายจุด | 🟢 Minor |

### Day 12: Integration & Testing (CFD Engine Phase 1)

| รหัส | ประเภท | รายละเอียด | บรรทัด | ความรุนแรง |
|------|--------|------------|--------|------------|
| `TRUNC-001` | Truncated Code | Section 3.2.3 code หยุดที่ "Condition " | Section 3.2.3 | 🔴 Critical |
| `TRUNC-002` | Truncated Code | Phase1Exam code หยุดที่ "std" | Section 4.2.3 | 🔴 Critical |
| `TRUNC-003` | Truncated Content | เอกสารจบกลางประโยค "alpha (∇·(αU" | End of doc | 🔴 Critical |
| `SYNTAX-001` | Duplicate Callout Title | Concept Check 1 ชื่อซ้ำ | Section 6 | 🟢 Minor |

---

## 🔧 สรุป: Major Issues Summary

| Day | Critical Issues | ต้อง Regenerate |
|-----|----------------|-----------------|
| 08 | 3 (tags, 2 truncations) | ⚠️ BiCGStab section |
| 09 | 3 (unclosed code blocks) | ⚠️ RhieChow, UnderRelax |
| 10 | 1 (backtick-LaTeX) | ❌ ไม่จำเป็น |
| 11 | 1 (truncation) | ⚠️ Key Observation |
| 12 | 3 (truncations) | ⚠️ หลาย sections |

---

---

## �� QC Checklist Template (จากการวิเคราะห์ Issues ทั้งหมด)

### ✅ Pre-Generation Checklist
- [ ] กำหนด parameters ทั้งหมดก่อน generate (section count, code blocks)
- [ ] ใช้ output ที่รองรับ long-form content

### ✅ Syntax Validation Checklist

#### YAML Frontmatter
- [ ] ไม่มี duplicate keys (เช่น `tags:` ซ้ำ 2 ครั้ง)
- [ ] ค่า `date`, `title`, `tags` ถูกต้อง

#### LaTeX
- [ ] ไม่มี backtick ครอบ `$$` blocks: ❌ `` `$$...$$` `` → ✅ `$$...$$`
- [ ] ไม่มี backtick เกินหน้า `$`: ❌ `` `$\mu` `` → ✅ `$\mu$`
- [ ] ใช้ `\|` สำหรับ norm แทน `||` (optional)

#### Code Blocks
- [ ] จำนวน ` ``` ` เปิดและปิดเท่ากัน
- [ ] ใช้ภาษาที่ถูกต้อง: `cpp`, `cmake`, `bash` (ไม่ใช่ `text`)
- [ ] Code block ปิดก่อน header ใหม่

#### Content Completeness
- [ ] ไม่มีประโยคถูกตัดกลางคัน (ลงท้ายด้วย `**`, `\`, `//`, etc.)
- [ ] ทุก section มีเนื้อหาครบถ้วน (ไม่หยุดที่ `if`, `std`, `Condition `)
- [ ] Concept Checks มีคำตอบครบ

#### Structure
- [ ] ไม่มี header ซ้ำ (เช่น `## 3.1` สองครั้ง)
- [ ] Section numbering ต่อเนื่อง (ไม่ข้ามจาก 1 ไป 3)
- [ ] Callout titles ไม่ซ้ำซ้อน

### 🔴 Common Patterns ที่พบบ่อย

| Pattern | วิธีตรวจ | วิธีแก้ |
|---------|---------|--------|
| Backtick-LaTeX | `grep '\`$$' file.md` | ลบ backticks |
| Duplicate keys | `grep -c '^tags:' file.md` | รวมเป็น 1 บรรทัด |
| Unclosed code | ` grep -c '^```' ` เปิด vs ปิด | ปิด code block |
| Truncation | ค้นหา `**$`, `\$`, `//\n#` | Regenerate section |

---

## 📋 QC Checklist Template (จากการวิเคราะห์ Issues ทั้งหมด)

### ✅ Pre-Generation Checklist
- [ ] กำหนด parameters ทั้งหมดก่อน generate

### ✅ Syntax Validation

#### YAML Frontmatter
- [ ] ไม่มี duplicate keys

#### LaTeX
- [ ] ไม่มี backtick ครอบ `$$` blocks

#### Code Blocks
- [ ] จำนวน open/close ` ``` ` เท่ากัน
- [ ] ไม่มี truncation กลาง code

#### Content
- [ ] ไม่มีประโยคถูกตัดกลางคัน
