# Code Analysis Prompt Template

You are analyzing the **Code section** of a daily learning module for CFD/OpenFOAM.

## Input Content

```
{{CODE_CONTENT}}
```

## Ground Truth Facts

```
{{GROUND_TRUTH}}
```

## Task

Provide an interactive walkthrough of the code section with the following requirements:

### 1. Structure Your Response

For each code snippet/section:

#### **Code Context**
- What this code implements
- Where it fits in OpenFOAM architecture
- Why this implementation matters

#### **Class Hierarchy**
- Show the inheritance chain
- Mark each level with ⭐ if verified

#### **Implementation Details**
- Walk through key methods line-by-line
- Explain design choices
- Use ⭐ to mark verified facts

#### **Common Patterns**
- Identify recurring OpenFOAM patterns
- Show variations and alternatives
- Use ⚠️ for patterns from documentation

### 2. Verification Requirements

- **EVERY** class reference must:
  - Match ground truth hierarchy
  - Include file path reference
  - Be marked with ⭐

- **EVERY** method reference must:
  - Match ground truth signature
  - Include file path and line number
  - Be marked with ⭐

- **NO** hallucinated classes/methods

### 3. Mermaid Diagrams

Use class diagrams for inheritance:

```mermaid
classDiagram
    class "ClassName<Type>" {
        +publicMethod()*
        -privateField
        #protectedMethod()
    }
    "ClassName<Type>" --|> "ParentClass<Type>"
```

**Important:**
- Quote class names with `<Type>` in angle brackets
- Mark virtual methods with `*`
- Use proper relationship arrows

### 4. Output Format

```markdown
### Code Walkthrough: [Section Title]

#### Code Context
[What and why, with ⭐ markers]

#### Class Hierarchy
⭐ Verified from [source file]

```mermaid
[Class diagram]
```

#### Implementation Analysis

> **File:** `path/to/file.H`
> **Lines:** X-Y

```cpp
// Key code with line-by-line comments
```

**Explanation:**
- Line X: [What it does]
- Line Y: [Why it's designed this way]

#### Key Insights
- [Insight with marker]
- [Insight with marker]

#### Self-Check
<details>
<summary>Understanding Questions</summary>

1. [Question 1]
2. [Question 2]
3. [Question 3]

<details>
<summary>Answers</summary>

1. [Answer 1]
2. [Answer 2]
3. [Answer 3]
</details>
</details>
```

### 5. Common Errors to Avoid

- ❌ Do NOT show incorrect class hierarchies
- ❌ Do NOT skip intermediate inheritance levels
- ❌ Do NOT omit file references
- ❌ Do NOT quote Mermaid nodes incorrectly
- ❌ Do NOT mix verified and unverified without markers

### 6. Special Instructions

For OpenFOAM code:
- Show the full inheritance chain (all levels)
- Explain the template parameter system
- Connect code to the theory section concepts
- Explain design patterns (virtual methods, polymorphism)

## Ground Truth Reference

Your ground truth contains:
- Complete class hierarchies
- Method signatures with parameters
- Template parameter specifications
- File paths and line numbers

**Use this to verify ALL code references!**
