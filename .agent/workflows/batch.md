---
description: Batch generate Phase 1-6 (Days 01-90) using English First + Localization Pipeline
---

# ⚠️ STRICT WORKFLOW: Content Generation Pipeline

## AI Model Assignment (ห้ามเปลี่ยน!)

| ขั้นตอน | AI Model | วิธีการ |
|---------|----------|---------|
| **1. Generate Content (English)** | **DeepSeek V3** | รัน `scripts/generate_day_v3.py` |
| **2. Quality Control (QC)** | **Claude / Gemini (Agent)** | Agent ตรวจสอบและแก้ไขโดยตรง |
| **3. Translation (English → Thai)** | **Claude / Gemini (Agent)** | Agent แปลและเขียนไฟล์โดยตรง |
| **4. Final QC** | **Claude / Gemini (Agent)** | Agent ตรวจสอบไฟล์ Thai สุดท้าย |

> [!CAUTION]
> **ห้ามใช้ DeepSeek สำหรับ QC หรือ Translation โดยเด็ดขาด!**
> DeepSeek ใช้สำหรับการสร้างเนื้อหา English ต้นฉบับเท่านั้น

---

## Pipeline Steps

### Step 1: Generate English Content (DeepSeek)
```bash
python3 scripts/generate_day_v3.py \
  --day "XX" \
  --topic "Topic Name" \
  --skeleton "daily_learning/skeletons/dayXX_skeleton.json" \
  --output "daily_learning/drafts/dayXX_deepseek_english.md"
```

**Output:** `daily_learning/drafts/dayXX_deepseek_english.md`

---

### Step 2: Quality Control (Agent - Claude/Gemini)
Agent ต้องตรวจสอบ English draft โดย:
1. ตรวจ LaTeX syntax (`$...$` และ `$$...$$`)
2. ตรวจ Mermaid diagram syntax
3. ตรวจ Heading hierarchy (H1 → H2 → H3)
4. ตรวจ Code block closure
5. ตรวจความครบถ้วนของเนื้อหา (ทุก Section ที่กำหนดใน skeleton)

**Action:** แก้ไขไฟล์โดยตรงด้วย `replace_file_content` หรือ `multi_replace_file_content`

---

### Step 3: Translation (Agent - Claude/Gemini)
Agent ต้องแปลไฟล์ English → Engineering Thai โดย:
1. **แปล:** ข้อความภาษาอังกฤษ → "Engineering Thai" (ภาษาไทย + ศัพท์เทคนิคอังกฤษ)
2. **ไม่แตะ:** Code blocks, LaTeX equations, Mermaid diagrams, File paths
3. **ศัพท์เทคนิคที่ไม่แปล:** Finite Volume, Mesh, Flux, Gradient, Divergence, Owner-Neighbor, etc.

**Output File:** `daily_learning/Phase_XX_.../YYYY-MM-DD.md`

---

### Step 4: Final QC (Agent - Claude/Gemini)
Agent ตรวจสอบไฟล์ Thai final ตาม `quality_control_checklist.md`:
1. Frontmatter ถูกต้อง
2. Headers เป็น bilingual format
3. TOC ใช้ Wiki-links
4. LaTeX/Mermaid/Code blocks ไม่เสียหาย

---

## File Locations

| ประเภท | Path |
|--------|------|
| Skeletons | `daily_learning/skeletons/dayXX_skeleton.json` |
| English Drafts | `daily_learning/drafts/dayXX_deepseek_english.md` |
| Thai Finals (Phase 1) | `daily_learning/Phase_01_Foundation_Theory/YYYY-MM-DD.md` |
| QC Checklist | `quality_control_checklist.md` |
| **Governance Rules** | `CONVENTIONS.md` |

---

## Current Status Tracking

เมื่อรัน batch ให้ Agent อัพเดต status ใน `task.md` artifact ทุกครั้งที่เสร็จแต่ละ Day
