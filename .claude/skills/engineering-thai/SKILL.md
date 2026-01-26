# Engineering Thai Translation Standards

## What is Engineering Thai?

Engineering Thai = Thai language explanations + English technical terms

**Formula:**
```
[Thai explanation] + [English technical term] + [optional Thai glossary first time]
```

## Core Principles

1. **Preserve Technical Terms** - Keep standard CFD terminology in English
2. **Natural Thai Flow** - Explanations should read naturally in Thai
3. **Bilingual Headers** - All section titles should be bilingual
4. **Preserve Code** - Never translate code, LaTeX, or file paths

## Technical Terms Dictionary (Never Translate)

| English | Thai (for reference) | Usage |
|---------|---------------------|-------|
| Finite Volume Method | วิธีการปริมาต่อเนื่องจำกัด | Always English |
| Mesh | ตาข่าย | Always English |
| Cell | เซลล์ | English first, then (เซลล์) |
| Face | หน้าเซลล์ | English first, then (หน้าเซลล์) |
| Owner | Owner | Always English |
| Neighbor | Neighbor | Always English |
| Gradient | Gradient | Always English |
| Divergence | Divergence | Always English |
| Laplacian | Laplacian | Always English |
| Flux | Flux | Always English |
| Convection | Convection | Always English |
| Diffusion | Diffusion | Always English |
| Interpolation | Interpolation | Always English |
| Discretization | Discretization | Always English |
| Boundary Condition | Boundary Condition (เงื่อนไขขอบ) | English with Thai gloss first time |
| Gauss | Gauss | Always English |
| Upwind | Upwind | Always English |
| Linear | Linear | Always English |
| Limited | Limited | Always English |
| TVD (Total Variation Diminishing) | TVD | Always English |

## Bilingual Header Format

### Standard Format

```markdown
## English Title (ชื่อภาษาไทย)
```

### Examples

```markdown
## Introduction (บทนำ)
## Mathematical Foundation (พื้นฐานคณิตศาสตร์)
## OpenFOAM Implementation (การ implement ใน OpenFOAM)
## Code Examples (ตัวอย่างโค้ด)
## Troubleshooting (การแก้ปัญหา)
```

## Translation Examples

### Example 1: Concept Explanation

**English:**
```
The Finite Volume Method divides the domain into control volumes and conserves flux across cell faces.
```

**Engineering Thai:**
```
Finite Volume Method แบ่งโดเมนเป็น control volumes และรักษา flux ที่ขอบของ cell faces
```

### Example 2: Technical Explanation

**English:**
```
The gradient of a scalar field φ is calculated using Gauss theorem:
```

**Engineering Thai:**
```
Gradient ของ scalar field φ คำนวณโดยใช้ทฤษฎีบทของ Gauss:
```

### Example 3: Code Explanation

**English:**
```
In OpenFOAM, use `fvc::grad` to calculate the gradient of a field:
```

**Engineering Thai:**
```
ใน OpenFOAM ให้ใช้ `fvc::grad` ในการคำนวณ gradient ของ field:
```

## What NOT to Translate

### Code Blocks (never touch)

```cpp
// Calculate face flux
surfaceScalarField phi = linearInterpolate(U) & mesh.Sf();
```

### LaTeX (never touch)

$$
\nabla \cdot \mathbf{U} = 0
$$

### File Paths (never touch)

```
openfoam_temp/src/finiteVolume/fields/fvFields/fvPatchFields
```

### Command Examples (never touch)

```bash
blockMeshDict
```

## Common Translation Mistakes

### ❌ Mistake 1: Translating Technical Terms

**Wrong:**
```
วิธีการปริมาต่อเนื่องจำกัด
```

**Correct:**
```
Finite Volume Method
```

### ❌ Mistake 2: Translating Code

**Wrong:**
```cpp
// คำนวณปริมาตระหว่างผิว
surfaceScalarField flux = ...;
```

**Correct:**
```cpp
// Calculate face flux
surfaceScalarField flux = ...;
```

### ❌ Mistake 3: Losing Technical Precision

**Wrong:**
```
เกรเดียนต์ของสนามสเกลาร์
```

**Correct:**
```
Gradient ของ scalar field
```

## Grammar Guidelines

### 1. Verb Conjugation

Use English terms as nouns:
- ✅ การคำนวณ gradient
- ✅ gradient ของ field
- ❌ กระเด้น gradient

### 2. Pluralization

Keep English pluralization:
- ✅ cells, faces, boundaries
- ❌ เซลล์, เฟซ, บาวน์ดารี

### 3. Compound Words

No space between Thai and English:
- ✅ gradientของfield
- ✅ meshตัวนี้
- ❌ gradient ของ field (better: gradientของfield)

## First Mention Rule

When a technical term appears for the first time, provide Thai gloss:

**First mention:**
```
Mesh คือการแบ่งโดเมนเป็นชิ้นส่วนเล็กๆ เรียกว่า cells
```

**Subsequent mentions:**
```
แต่ละ mesh มีจำนวน cells ที่แตกต่างกัน
```

## Quality Checklist

After translating a section:

- [ ] All headers are bilingual
- [ ] Technical terms kept in English
- [ ] Code blocks untouched
- [ ] LaTeX intact
- [ ] File paths unchanged
- [ ] Thai flows naturally
- [ ] First mentions have Thai gloss
- [ ] No literal translation of idioms

## Tools

Use `translator` agent for consistent Engineering Thai translation:

```
/delegate translator "Translate section 3 to Engineering Thai"
```

---

**Related Skills:** `source-first`, `cfd-content-structure`
