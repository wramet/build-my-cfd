---
description: Walkthrough daily_learning content interactively with Source-First verification
---

# /walkthrough - Interactive Content Walkthrough (Source-First Enhanced)

> **🔒 Source-First Principle:** Ground Truth from source code > AI analysis. Verify at each stage.

Use this mode to tutor me through `daily_learning/` content step-by-step with **verified facts**.

**Core Logic:**
1. **Extract Ground Truth FIRST** from OpenFOAM source code
2. **Verify AI outputs** against ground truth before showing to user
3. You are the **Interface (Teacher)**. DeepSeek (via Terminal) is the **Knowledge Source (Researcher)**.

## Usage
```
/walkthrough <path-to-file>
```
Example:
- `/walkthrough daily_learning/Phase_01_Foundation_Theory/01.md`
- `/walkthrough 05.md`
- `/walkthrough 02.md เริ่มที่ Section 2` (to start from a specific section)

---

## Output Configuration

**Walkthrough files are stored in:** `daily_learning/walkthroughs/`

**Naming convention:** `day_XX_walkthrough.md` (e.g., `day_02_walkthrough.md`)

**Behavior:**
- On first section: **Create** the walkthrough file with frontmatter and the first section content.
- On subsequent sections: **Append** content to the same file.
- Each section is separated by a horizontal rule (`---`).

---

## Workflow Steps

### Step 0: Extract Ground Truth (NEW - Source-First) 🔒

**Before starting walkthrough, extract verified facts from source code:**

```bash
# Identify the topic from the daily_learning file
# Example: Section about "upwind scheme" → extract from interpolation/surfaceInterpolation

export DAY="XX"  # From filename
export TOPIC="[topic_from_content]"  # e.g., "surfaceInterpolation"

# Extract ground truth
python3 .agent/scripts/extract_facts.py \
    --mode hierarchy \
    --path "openfoam_temp/src/finiteVolume" \
    --output /tmp/walkthrough_gt_hierarchy.txt

python3 .agent/scripts/extract_facts.py \
    --mode formulas \
    --path "openfoam_temp/src/finiteVolume" \
    --output /tmp/walkthrough_gt_formulas.txt

# Structure into JSON
python3 .agent/scripts/extract_facts.py \
    --mode structure \
    --input /tmp/walkthrough_gt_hierarchy.txt \
    --output /tmp/walkthrough_verified_facts.json
```

**Why?** This ensures ALL subsequent AI analysis is constrained by verified facts.

### Step 1: Initialize & Scan
1. Check if the source file exists.
2. Quickly read the file structure (headers) to build a mental Table of Contents.
3. Check if `daily_learning/walkthroughs/day_XX_walkthrough.md` exists:
   - If yes: Read and append.
   - If no: Create with frontmatter.

### Step 2: Show Overview (in chat briefly)
Display brief message in chat:
> "📂 สร้างไฟล์ `daily_learning/walkthroughs/day_XX_walkthrough.md` แล้ว พร้อมเริ่มที่ Section X"
>
> "🔒 Ground Truth extracted from: [source paths]"

#### Phase A: Dual-Agent Recon + Verify (MODIFIED) 🔒

**Execute both agents simultaneously** to save time, THEN verify outputs.
- **DeepSeek (Theorist):** Explains math/physics from the source text.
- **GLM-4 (Scout):** Searches live web/docs for Class Hierarchy & Namespaces.

*Command Pattern:*
```bash
# 1. Prepare prompts
SECTION_NAME="[Current Section Name]"
TOPIC="[Brief Topic, e.g., gaussDivScheme openfoam]"

# 2. Run Agents in Parallel
(cat [filename] | llm -m deepseek-chat -s "You are a CFD Professor. Explain ONLY section '$SECTION_NAME' from this text. Focus on math/physics." "Explain this." > deepseek_out.md) & \
(python3 .agent/scripts/ask_glm.py "Explain OpenFOAM C++ class hierarchy, namespaces, and header locations for '$TOPIC'. Verify inheritance and key member functions." > glm_out.md) & \
wait

# 3. VERIFY GLM Output against Ground Truth (NEW)
python3 .agent/scripts/verify_glm_output.py \
    --glm-output glm_out.md \
    --ground-truth /tmp/walkthrough_verified_facts.json \
    --output /tmp/glm_verification.md

# 4. Check verification before proceeding
if grep -q "❌" /tmp/glm_verification.md; then
    echo "⚠️ GLM output contains unverified claims. Using ground truth instead."
    cat /tmp/walkthrough_verified_facts.json
else
    echo "✅ GLM output verified"
    cat deepseek_out.md glm_out.md
fi
```

**🔒 Verification Gate:**
- If GLM output fails verification → Use ground truth facts instead
- Only show verified content to user

#### Phase B: Orchestrator Synthesis + Verify (MODIFIED) 🔒

**Role:** You are the **Orchestrator**. Synthesize inputs from:
1. **deepseek_out.md:** Math/Theory/Logic
2. **glm_out.md (or ground truth):** Real-world Code Structure, Namespaces, Header paths
3. **Source Material:** Code examples/Tables from `daily_learning` file
4. **Ground Truth (from Step 0):** Verified facts from source code ⭐

**🔒 Before writing, verify:**
- Class hierarchy matches ground truth
- Mathematical formulas are correct
- No unverified technical claims

**Write/append to walkthrough file** using this format:

```markdown
## 🎯 [Section Number]: [หัวข้อปัจจุบัน]

**📍 ตำแหน่ง:** Day XX > Section Y > [Current Header]

### 📝 คำอธิบาย (Sythesized from DeepSeek + GLM-4 + Source + Ground Truth)

[Explain using "Engineering Thai" style. Integrate:
- **Theory:** Math derivation (from DeepSeek)
- **Code:** Correct Class/Namespace hierarchy (from GLM-4 or Ground Truth)
- **Practice:** Code examples detailed in Source File]

### 🔬 Verified Facts (Source-First) ⭐
> **Class Hierarchy:** [Verified from actual source code]
> ```
> [Verified Mermaid diagram]
> ```
>
> **Formulas:** [If applicable, verified formulas]
> `$formula$`

### 💡 Key Insight

> [The most important takeaway - as a blockquote]

### 🔗 เชื่อมโยง

[Link to previous concepts if applicable]

---
```
### 🔗 เชื่อมโยง

[Link to previous concepts if applicable]

---
```

#### Phase D: Notify User
After writing to the file, send a brief message via `notify_user`:
> "✅ เขียน Section X.X ลงในไฟล์แล้ว พร้อมไป Section X.X ถัดไปไหมครับ?"

### Step 4: Wait for User Signal
Wait for my response:
- **"Next/ต่อ/ไปเลย"** → Repeat Step 3 for the next section, **append** to the same file.
- **"Expand/งง"** → Run a new `llm` query asking for a simpler analogy, then update the section.
- **"Skip to X"** → Move to that section.
- **"Done/จบ"** → Finalize the walkthrough file.
- **[คำถาม]** → Append Q&A to the walkthrough file (see Step 5).

### Step 5: Q&A Handling
When user asks a question during a walkthrough session:

#### 5.1 Decide: Answer Directly or Brainstorm with DeepSeek?

| Question Type | Action |
|---------------|--------|
| **Simple/clarification** (เช่น "X คืออะไร?") | ตอบเองได้เลย |
| **Technical/design decision** (เช่น "ทำไมเลือก X แทน Y?") | **Brainstorm กับ DeepSeek** |
| **Project-specific** (เช่น "เหมาะกับโปรเจคเราไหม?") | **Brainstorm กับ DeepSeek** พร้อม context |

#### 5.2 Brainstorm with DeepSeek (สำหรับคำถามซับซ้อน)

```bash
echo "[User's question + relevant context]" | llm -m deepseek-chat -s "You are a C++/CFD expert. Provide a detailed, rigorous answer with code examples if applicable."
```

**Tips for good prompts:**
- เพิ่ม context ของโปรเจค (เช่น "สำหรับ phase change simulation, ทีมเล็ก")
- ขอ code examples ถ้าเป็นคำถาม design
- ขอ trade-offs analysis ถ้าเป็นคำถามเปรียบเทียบ

#### 5.3 Append to Walkthrough File

**Format สำหรับ Q&A ทั่วไป:**
```markdown
### ❓ Q&A: [Brief topic]

**คำถาม:** [User's question in original language]

**คำตอบ:**
[Answer - using Engineering Thai style]

---
```

**Format สำหรับ Brainstorm Session:**
```markdown
### ❓ Q&A: [Brief topic] (Brainstorm with DeepSeek)

**คำถาม:** [User's question]

**คำตอบ:** (Synthesized from DeepSeek)

[Detailed answer with code examples, tables, trade-offs as needed]

---
```

#### 5.4 Brief Chat Response
After writing to file:
> "✅ เขียนคำถาม-คำตอบลงไฟล์แล้ว ต่อไหมครับ?"

---

## Walkthrough File Template (First Section)

```markdown
---
title: "Day XX Walkthrough: [Lesson Title]"
date: YYYY-MM-DD
source: daily_learning/Phase_XX/XX.md
---

# Day XX: [Lesson Title] - Walkthrough Notes

> 🎓 **สไตล์การสอน:** Engineering Thai (คำศัพท์เทคนิคภาษาอังกฤษ อธิบายภาษาไทย)
> 📚 **Source:** DeepSeek + Claude synthesis

---

## 🎯 [First Section]
[Content...]

---
```

---

## Explanation Quality Guidelines (Revised 2026-01-20)

### 1️⃣ Always Include Trade-offs ⚠️

When explaining any design pattern, technique, or approach from OpenFOAM:

```markdown
### ⚠️ Trade-offs และข้อเสียของ [Pattern Name]

**ข้อเสีย:**
1. [Disadvantage 1 with code example if applicable]
2. [Disadvantage 2]
...

### 🎯 เมื่อไหร่ควร/ไม่ควรใช้

| ✅ ควรใช้ | ❌ ไม่ควรใช้ |
|----------|------------|
| [Use case 1] | [Anti-use case 1] |

**สำหรับ CFD Engine ของเรา:**
- [Recommendation based on our project context]
```

### 2️⃣ Dual-Pipeline Usage 🔄

| When to Use Dual-Pipeline | When to Answer Directly |
|---------------------------|------------------------|
| Verify info from OpenFOAM codebase | Simple definitions |
| Complex breakdown needed | Syntax explanation |
| Cross-reference multiple sources | Clarification of already-explained concepts |
| User asks for more detail | Simple Q&A |

### 3️⃣ Q&A for Complex Concepts ❓

Every section with non-trivial code should have:
```markdown
#### ❓ Q&A: [Concept] คืออะไร?

**คำถาม:** [What is it and what does it do?]

**คำตอบ:** [Clear explanation with problem → solution format]
```

### 4️⃣ Diagram Splitting Rule 📊

If a Mermaid diagram has:
- **> 4 classes:** Split into 2+ diagrams
- **Complex relationships:** Split by layer (Data vs Operations)
- **Rendering issues:** Check in Obsidian, adjust if too compressed

---

## Teaching Style Guidelines

| Rule | Description |
|------|-------------|
| **🔒 Source of Truth** | **Ground Truth from source code > AI output > Internal training**. Always verify technical claims against extracted facts. |
| **Language** | "Engineering Thai" (Technical terms in English, explanation in Thai) |
| **LaTeX** | Use for all math: `$\nabla \cdot U$` |
| **Code** | Use backticks: `volScalarField`, `fvm::ddt()` |
| **Verification** | Mark verified facts with ⭐ emoji. Label unverified content clearly. |

---

## Example Session

**User:** `/walkthrough 02.md เริ่มที่ Section 2`

**AI Actions:**
1. Reads `02.md` → Identifies Section 2 headers
2. Creates `daily_learning/walkthroughs/day_02_walkthrough.md` with frontmatter
3. Runs: `cat 02.md | llm -m deepseek-chat -s "..." "Explain section 2.1"`
4. Reads terminal output
5. Writes Section 2.1 content to walkthrough file
6. Notifies user: "✅ เขียน Section 2.1 แล้ว พร้อมไป 2.2 ไหมครับ?"
7. User says "ต่อ"
8. **Appends** Section 2.2 to the same file
9. Repeat until user says "Done"

---

## Notes
- **Step 0 (Extract Ground Truth) is mandatory** - ห้ามอธิบายโดยไม่ extract facts ก่อน
- **Verification is mandatory** - ห้ามใช้ AI output ที่ไม่ได้ verify กับ ground truth
- ถ้า `llm` command ไม่ทำงาน ให้แจ้ง User และ fallback เป็นการอธิบายจาก ground truth facts (not internal knowledge)
- ใช้ร่วมกับ `/qc` workflow ได้ (QC ก่อน แล้วค่อย Walkthrough)
- **Append mode**: หลังจาก section แรก ทุก section ใหม่จะถูก append ต่อท้ายไฟล์เดิม
- **Source-First Principle:** เมื่อมี conflict ระหว่าง AI output กับ ground truth → ใช้ ground truth เสมอ
