# Testing and QA

การ Testing และ Quality Assurance

---

## Overview

> **Testing** = Ensure reliable simulations

---

## 1. Testing Levels

| Level | Scope |
|-------|-------|
| Unit | Single function |
| Integration | Components |
| System | Full case |
| Regression | Prevent breaks |

---

## 2. Allrun with Check

```bash
#!/bin/bash
./Allrun || exit 1

# Compare results
diff -q expected/results.txt postProcessing/results.txt
```

---

## 3. Automated Testing

```bash
#!/bin/bash
for case in tests/*/; do
    (cd "$case" && ./Allrun)
    if [ $? -ne 0 ]; then
        echo "FAILED: $case"
    fi
done
```

---

## Quick Reference

| Test Type | Purpose |
|-----------|---------|
| Regression | Catch breaks |
| Validation | Check physics |
| System | Full workflow |

---

## Concept Check

<details>
<summary><b>1. Regression test ทำอะไร?</b></summary>

**Verify changes don't break** existing functionality
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)