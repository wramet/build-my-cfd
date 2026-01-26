# DeepSeek V3 Content Expansion Template (English Edition)

## Purpose
Receive **Technical Skeleton** from DeepSeek R1 and **Expand** into a Full "Hardcore" Lesson in English.

## CRITICAL: Content Length Requirements

> [!IMPORTANT]
> **Content must be at least 1500 lines long.**
> - Theory Section: 300+ lines
> - OpenFOAM Reference: 400+ lines (including code snippets)
> - Class Design: 200+ lines
> - Implementation: 400+ lines (C++ code)
> - Build & Test: 150+ lines
> - Concept Checks: 100+ lines

---

## Output Structure (8 Main Sections)

### 1. Frontmatter + Title
```yaml
---
tags: [cfd-engine, evaporator, day-{N}]
date: 2026-01-{DD}
aliases: [{Title}]
difficulty: hardcore
topic: {Topic}
project: CFD Engine Development (90 Days)
language: en
---
```

### 2. Learning Objectives
- **4-6 objectives**, each with:
  - Action verb (Understand, Design, Implement, Test)
  - Specific topic
  - Relevant equations or code references

### 3. Section 1: Theory - 300+ lines
**Required Sub-sections:**

#### 1.1 Mathematical Foundations
- Key equations with LaTeX
- Detailed variable explanation (Table)
- Physical meaning
- **WARNING/TIP callouts**

#### 1.2 Design Decisions
- Trade-offs table
- Rationale for chosen approach

#### 1.3 Core Concepts
- Definitions and validity ranges
- Summary table
- **Common PITFALLS table**

### 4. Section 2: OpenFOAM Reference - 400+ lines
**Must include 3-5 key code snippets, each containing:**

```markdown
#### Snippet N: {Title}

**File:** `{path/to/file.C}`

```cpp
// Reference: OpenFOAM vXXXX
// Lines XX-XX (simplified for clarity)

// ACTUAL CODE HERE - minimum 20-30 lines per snippet
// Include comments explaining each part
```

**What This Does:**
1. {Point 1}
2. {Point 2}
3. {Point 3}

> [!TIP] **Key Takeaway for Your Engine**
> {Important lesson to apply}
```

**Comparison:**
- What We Can LEARN - 5+ points
- What We Do DIFFERENTLY - Table

### 5. Section 3: Class Design - 200+ lines
**Must include:**

#### Mermaid Class Diagram (Complete)
```mermaid
classDiagram
    class ClassName {
        +Type memberVar
        +Type methodName()
    }
    // All classes with relationships
```
**CRITICAL:** Quote all method signatures in Mermaid to handle special characters (e.g. `+calc("...")` instead of `+calc(...)`).

#### Class Specifications (For each class)
- Purpose
- Member Variables Table (Name | Type | Purpose)
- Key Methods with signatures

#### Design Rationale
- Why this design?
- Comparison with OpenFOAM (Table)

### 6. Section 4: Implementation - 400+ lines
**Must include:**

#### 4.1 Header File (.H)
- Complete header file (100+ lines)
- Documentation comments

#### 4.2 Implementation File (.C)
- Complete implementation (250+ lines)
- Every method must be implemented (no placeholders)
- CRITICAL: Include expansion term in pressure equation logic

#### 4.3 Implementation Notes
- Critical details
- How to avoid divergence
- Common bugs table

### 7. Section 5: Build & Test - 150+ lines
**Must include:**

#### 5.1 Build Instructions
- Prerequisites table
- CMakeLists.txt (complete)
- Build commands
- Common issues table

#### 5.2 Unit Tests
- 5-8 test functions using Catch2 or GoogleTest style
- Complete test code
- Expected output

#### 5.3 Validation
- Analytical benchmark or simple test case
- Expected results table

### 8. Section 6: Concept Checks - 100+ lines
**4-6 questions, each with:**

```markdown
### Question N: {Question text}

> **Answer:**
> {Detailed answer - minimum 10 lines}
> - Bullet points for key concepts
> - Equations where relevant
> - Implementation notes
> - Code references
```

### 9. References & Related Days
- References (3-5 items)
- Related Lessons (Previous/Next/See also)

---

## Callout Types to Use

```markdown
> [!WARNING] **Title**
> Critical information - ignore at your peril

> [!TIP] **Title**
> Best practice or optimization

> [!INFO] **Title**
> Background context

> [!IMPORTANT] **Title**
> Key concept to memorize
```

---

## Format Checklist

- [ ] Total length ≥ 1500 lines
- [ ] Learning Objectives: 4-6 items
- [ ] Theory: Equations complete + LaTeX valid
- [ ] OpenFOAM snippets: 3-5 examples (20+ lines each)
- [ ] Class diagram: Mermaid complete and valid syntax
- [ ] Implementation code: ≥ 300 lines total
- [ ] Unit tests: 5-8 tests
- [ ] Concept checks: 4-6 questions + detailed answers
- [ ] Callouts: WARNING, TIP, INFO, IMPORTANT
- [ ] Tables: Trade-offs, Pitfalls, Variables
- [ ] Headers: English Only

---

## Prompt for V3

```
You are a CFD Professor and Expert C++ Developer writing "Hardcore" learning material.

**CRITICAL REQUIREMENT:**
The content MUST be at least 1500 lines long. Be explicitly verbose, detailed, and thorough.
**LANGUAGE:**
Use **ENGLISH ONLY**. Do not use Thai or any other language.
**END MARKER:**
You MUST end your output with the exact string: ``. This is REQUIRED to verify completion.

**Input:** JSON skeleton from R1 Analysis

**Your Task:**
Expand the skeleton into a Full Lesson by:

1. **Theory Section (300+ lines):**
   - Expand every equation with detailed derivation and explanation.
   - Add physical meaning.
   - Use WARNING/TIP callouts liberally.
   - Include variable tables.

2. **OpenFOAM Reference (400+ lines):**
   - Provide 3-5 real code snippets (20+ lines each).
   - Explain "What This Does" line-by-line.
   - Compare with "Our Engine".

3. **Class Design (200+ lines):**
   - Create a Complete Mermaid classDiagram (quote all signatures).
   - List member variables and methods.
   - Explain design rationale.

4. **Implementation (400+ lines):**
   - Write Full C++ code (Header + Implementation).
   - Comment every significant line.
   - Highlight CRITICAL implementation details.

5. **Build & Test (150+ lines):**
   - Complete CMakeLists.txt.
   - Write 5-8 Unit Test functions.
   - Describe Validation case.

6. **Concept Checks (100+ lines):**
   - 4-6 deep comprehension questions.
   - Detailed answers (10+ lines each).

**JSON Skeleton:**
{R1_OUTPUT}

**Output:**
Complete Markdown file - ALL sections - minimum 1500 lines - English Only
```
