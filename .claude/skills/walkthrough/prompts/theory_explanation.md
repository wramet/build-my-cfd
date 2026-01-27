# Theory Explanation Prompt Template

You are analyzing the **Theory section** of a daily learning module for CFD/OpenFOAM.

## Input Content

```
{{THEORY_CONTENT}}
```

## Ground Truth Facts

```
{{GROUND_TRUTH}}
```

## Task

Provide an interactive walkthrough of the theory section with the following requirements:

### 1. Structure Your Response

For each subsection in the theory content:

#### **Concept Overview**
- Explain the core concept in simple terms
- Connect to previous knowledge where relevant
- Use ⭐ to mark statements verified from ground truth

#### **Mathematical Derivation**
- Show step-by-step derivation if applicable
- Explain each step clearly
- Use ⭐ to mark equations verified from ground truth

#### **Key Insights**
- Highlight important points
- Point out common pitfalls
- Use ⚠️ for insights from documentation (not verified)

#### **Self-Check Questions**
- 2-3 questions to test understanding
- Include answers in collapsible format

### 2. Verification Requirements

- **EVERY** technical claim must be marked:
  - ⭐ = Verified from ground truth source
  - ⚠️ = From documentation, needs verification
  - ❌ = Common misconception - correct it

- **EVERY** equation must:
  - Use proper LaTeX syntax
  - Include ground truth reference (file:line)
  - Be marked with ⭐

- **NO** nested LaTeX delimiters allowed

### 3. Output Format

```markdown
### Theory Walkthrough: [Subsection Title]

#### Concept Overview
[Explanation with ⭐ markers]

#### Mathematical Derivation
[Step-by-step with ⭐ markers]

> **File:** [source file path]
> **Lines:** [line numbers]

$$
[Equation]
$$

#### Key Insights
- [Insight 1 with marker]
- [Insight 2 with marker]

#### Self-Check
<details>
<summary>Questions</summary>

1. [Question 1]
2. [Question 2]

<details>
<summary>Answers</summary>

1. [Answer 1]
2. [Answer 2]
</details>
</details>
```

### 4. Common Errors to Avoid

- ❌ Do NOT use nested LaTeX (`$$...$...$$`)
- ❌ Do NOT make unverified technical claims
- ❌ Do NOT skip file references for equations
- ❌ Do NOT mix technical and non-technical verification

### 5. Special Instructions

For OpenFOAM-specific concepts:
- Connect to actual source code implementations
- Reference specific classes/methods from ground truth
- Explain why the math matters for CFD implementation

## Ground Truth Reference

Your ground truth contains:
- Class hierarchies from OpenFOAM source
- Method signatures and implementations
- Actual equations from source code
- File paths and line numbers

**Use this to verify ALL technical claims!**
