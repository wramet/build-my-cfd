# CONVENTIONS.md - CFD Engine Content Governance

> **Purpose:** This file governs all AI-generated content for the OpenFOAM/CFD learning project. Aider and other agents MUST read and follow these rules.

---

## Pillar 1: Accuracy & Consistency (ความถูกต้อง)

| Rule | Description |
|------|-------------|
| **OpenFOAM Version** | Reference OpenFOAM v2312 (ESI) by default. State explicitly if using foam-extend. |
| **Variable Naming** | Use OpenFOAM naming: `volScalarField p`, not `ScalarField pressure`. Camel case for classes. |
| **Dimensional Consistency** | All equations must include dimensions. Write `dimPressure` or `m^2/s^2` explicitly. |
| **No Hallucination** | If unsure about an API, state "verify in source" instead of guessing. |

---

## Pillar 2: Pedagogy & Clarity (ความเข้าใจง่าย)

| Rule | Description |
|------|-------------|
| **Chunking** | Max 1 concept per subsection. BUT each concept must be explained **completely** before moving on. |
| **Analogies First** | Start every new concept with a physical analogy before math. |
| **Code-First** | Show code snippet, then explain line-by-line. Not the reverse. |
| **Concept Check** | Every section ends with a Q&A or "ลองคิดดู" prompt. |
| **Trade-offs** | Always discuss "When to use" vs "When NOT to use" for patterns. |
| **Depth over Brevity** | **Never sacrifice technical depth for brevity.** If a concept requires 500 lines to explain properly, use 500 lines. |

---

## Pillar 3: DRY - Don't Repeat Yourself (ไม่ซ้ำซ้อน)

| Rule | Description |
|------|-------------|
| **Single Source of Truth** | Check `00_Overview.md` and `Glossary.md` before explaining a term. Link if exists. |
| **No Inter-Day Overlap** | Read the previous day's file. Do not re-explain its content. |
| **Modular Files** | Prefer atomic notes. Link between them using Wiki-links `[[concept]]`. |

---

## Pillar 4: Context Chain (ความต่อเนื่อง)

| Rule | Description |
|------|-------------|
| **Phase Context** | Always load `phase_N_context.md` for notation consistency. |
| **Previous Day** | Read `Day N-1` before generating `Day N`. Reference prior learning. |
| **Learning Ladder** | Days 01-30: Basic. Days 31-60: Intermediate. Days 61-90: Advanced. Adjust complexity. |

---

## Pillar 5: Verification (การตรวจสอบ)

| Rule | Description |
|------|-------------|
| **Pre-Flight Check** | Before outputting, run content through `quality_gate` skill checklist. |
| **Physics Audit** | Verify equations balance. Check units. Cross-ref with OpenFOAM source. |
| **Code Compile Check** | If C++ snippet, ensure it would compile (headers, namespaces). |

---

## Pillar 6: Tone & Voice (น้ำเสียง)

| Rule | Description |
|------|-------------|
| **Engineering Thai** | Thai explanations + English technical terms. Space between languages. |
| **Pronoun** | Use "เรา" (we) for collaborative tone. Never "คุณ" (you) in condescending way. |
| **Encouraging** | Acknowledge difficulty, then assure mastery is achievable. |

---

## Pillar 7: Progressive Disclosure (การค่อยๆ เปิดเผย)

| Rule | Description |
|------|-------------|
| **Scaffold** | Build on prior knowledge. Don't introduce `fvMatrix` before `fvMesh`. |
| **Hide Complexity** | Use `<details>` tags for advanced derivations. Main text stays simple. |
| **Forward Reference** | If topic requires future knowledge, say "we'll cover this in Day XX." |

---

## Pillar 8: Visualization (การแสดงผล)

| Rule | Description |
|------|-------------|
| **Every Concept = 1 Visual** | Each major concept needs a diagram, table, or code block. |
| **Mermaid Splitting** | If diagram has >4 classes, split into 2+ diagrams. |
| **Source Citation** | Link to official OpenFOAM docs or programmer's guide when possible. |

---

## Pillar 9: Technical Depth (ความลึกทางเทคนิค) ⭐ NEW

> **Critical:** Pedagogical structure must NOT come at the cost of technical completeness.

| Rule | Description |
|------|-------------|
| **OpenFOAM Source Reference** | Every Day MUST include actual OpenFOAM header file analysis (`.H` files). Show real class declarations. |
| **Implementation = Real Code** | Implementation sections must contain compilable C++ code, not pseudocode. |
| **Minimum Content** | Each Day should have **at least 1,000 lines** covering: Theory + OpenFOAM Ref + Design + Implementation + Test |
| **Header Paths** | Always cite the full path: `src/finiteVolume/interpolation/surfaceInterpolation/...` |
| **Compare with Our Code** | If we deviate from OpenFOAM standard, explain WHY with a "สิ่งที่เราทำต่างออกไป" section. |

**Content Structure (Minimum):**
1. **Theory Section (300+ lines):** Math derivation with LaTeX, physical interpretation
2. **OpenFOAM Reference (500+ lines):** Actual source code analysis with `surfaceInterpolationScheme`, `upwind`, etc.
3. **Class Design (100+ lines):** Mermaid diagrams of class hierarchy
4. **Implementation (200+ lines):** Our custom implementation with explanation
5. **Concept Checks (100+ lines):** Questions with hidden solutions

---

## Quick Reference: Skill Integration

| Skill | When to Invoke |
|-------|----------------|
| `auto_qc` | After drafting, before user review. Fixes Engineering Thai spacing. |
| `walkthrough_tutor` | During interactive teaching. Enforces Socratic method. |
| `quality_gate` | Final review. Checks physics, pedagogy, and style. |

---

**Last Updated:** 2026-01-24
