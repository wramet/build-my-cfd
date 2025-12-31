# Daily Lesson Generator Skill

สร้างเนื้อหาการเรียนรู้รายวัน โดยดึงจาก MODULE_01-10

---

## Trigger Phrases

- "สร้างเนื้อหาวันนี้"
- "เนื้อหาวัน [DATE]"
- "สร้าง daily lesson"
- "เรียนต่อจากเมื่อวาน"

---

## Workflow

### 1. ตรวจสอบ Progress

1. อ่าน `daily_learning/README.md` เพื่อดู learning path
2. ดูไฟล์ล่าสุดใน `daily_learning/` เพื่อหาว่าเรียนถึงไหน
3. กำหนดหัวข้อวันนี้ตามลำดับ MODULE

### 2. สร้างเนื้อหาด้วย GLM-4.7

```bash
use-glm-4.7 && claude --dangerously-skip-permissions "[[PROMPT]]"
```

**Prompt ควรระบุ:**
- วันที่ (YYYY-MM-DD)
- Topic และ source files
- Level: HARDCORE - เน้น source code analysis
- โครงสร้างไฟล์ที่ต้องการ

### 3. Review และ Enhance

หลังสร้างเนื้อหา:
1. ตรวจสอบความครบถ้วน
2. ตรวจสอบ code examples ว่าถูกต้อง
3. เพิ่ม advanced insights (ถ้าจำเป็น)

### 4. Copy to iCloud

```bash
cp daily_learning/YYYY-MM-DD.md '/Users/woramet/Library/Mobile Documents/com~apple~CloudDocs/daily/'
```

---

## Content Level Guidelines

### HARDCORE Level

| Element | ต้องมี |
|---------|-------|
| **Source Code** | Line-by-line analysis จาก OpenFOAM source |
| **Class Hierarchy** | UML-style diagrams |
| **Data Flow** | ASCII diagrams แสดง data flow |
| **Memory Layout** | Visualization of data structures |
| **Hands-on** | ให้ไปอ่าน source files จริง |

### ไม่ควรมี

- Basic tutorials แบบ run Allrun
- Mathematical derivations (unless specifically requested)
- Easy explanations

---

## Output Locations

| Location | Purpose |
|----------|---------|
| `daily_learning/YYYY-MM-DD.md` | Source file ใน project |
| `iCloud/daily/YYYY-MM-DD.md` | Synced copy สำหรับอ่านทุกที่ |

---

## Related Skills

- [learning-assistant](../learning-assistant/SKILL.md) — Route questions
- [content-quality-checker](../content-quality-checker/SKILL.md) — QC content
