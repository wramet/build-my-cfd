# Implementation Walkthrough Prompt Template

You are providing step-by-step guidance for the **Implementation section** of a daily learning module.

## Theory Summary

```
{{THEORY_SUMMARY}}
```

## Code Summary

```
{{CODE_SUMMARY}}
```

## Ground Truth Facts

```
{{GROUND_TRUTH}}
```

## Task

Provide hands-on implementation guidance that connects theory and code.

### 1. Structure Your Response

#### **Implementation Overview**
- What we're building/implementing
- How it connects to theory
- Why this matters for CFD

#### **Step-by-Step Guide**

For each step:
1. **Objective**: What we're accomplishing
2. **Prerequisites**: What you need first
3. **Actions**: Specific commands or code to execute
4. **Verification**: How to confirm it worked
5. **⭐ Verified**: Mark verified steps

#### **Common Pitfalls**
- Things that typically go wrong
- How to avoid them
- Troubleshooting steps

#### **Testing & Validation**
- How to test your implementation
- Expected results
- Debugging tips

### 2. Verification Requirements

- **EVERY** compilation step must:
  - Use correct OpenFOAM commands
  - Include expected output
  - Be marked with ⭐ if verified

- **EVERY** file path reference must:
  - Match ground truth structure
  - Include full path from project root
  - Be marked with ⭐

- **ALL** command outputs should show:
  - Expected success indicators
  - Common error patterns
  - How to interpret results

### 3. Output Format

```markdown
### Implementation Walkthrough

#### Overview
[What, why, and how it connects]

#### Step 1: [Step Title]

**Objective:** [What we're doing]

**Prerequisites:**
- [Requirement 1]
- [Requirement 2]

**Actions:**

⭐ Verified from [source reference]

```bash
# Command with comments
```

**Expected Output:**
```
[Success output]
```

**Verification:**
```bash
# Check command
```

#### Step 2: [Step Title]
[Continue pattern]

#### Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| [Error] | [Reason] | [Fix] |

#### Testing & Validation

**Test 1: [Test Name]**
```bash
# Test command
```
**Expected:** [Result]
**Actual:** [How to verify]

#### Self-Check

<details>
<summary>Questions</summary>

1. What command compiles an OpenFOAM solver?
2. How do you verify the solver was created correctly?
3. What does [specific output] indicate?

<details>
<summary>Answers</summary>

1. wmake
2. Check that executable exists in $FOAM_USER_APPBIN
3. [Explanation]
</details>
</details>
```

### 4. Common Errors to Avoid

- ❌ Do NOT skip prerequisite steps
- ❌ Do NOT assume OpenFOAM environment is setup
- ❌ Do NOT use placeholder commands (use real ones)
- ❌ Do NOT omit verification steps
- ❌ Do NOT provide unverified file paths

### 5. Special Instructions

For OpenFOAM implementations:
- Use actual wmake commands and flags
- Show proper directory structure (Make/files, Make/options)
- Explain the OpenFOAM build system
- Connect back to theory (why this implementation approach)
- Include both success and failure scenarios

## Ground Truth Reference

Your ground truth contains:
- Actual OpenFOAM source code structure
- Real compilation commands and output
- File organization patterns
- Common OpenFOAM build practices

**Use this to verify ALL implementation steps!**
