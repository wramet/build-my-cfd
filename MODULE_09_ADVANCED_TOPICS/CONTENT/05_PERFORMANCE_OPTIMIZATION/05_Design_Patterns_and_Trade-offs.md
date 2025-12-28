# Design Patterns and Trade-offs

Patterns และ Trade-offs สำหรับ Performance

---

## Overview

> Balance **flexibility** vs **performance**

---

## 1. Template vs Virtual

| Approach | Flexibility | Performance |
|----------|-------------|-------------|
| Template | Compile-time | Fast |
| Virtual | Runtime | Small overhead |

```cpp
// Template: compile-time dispatch
template<class Scheme>
void solve(Scheme& s) { s.compute(); }

// Virtual: runtime dispatch
void solve(BaseScheme* s) { s->compute(); }
```

---

## 2. When Virtual Is Fine

```cpp
// Called once per time step
turbulence->correct();  // Virtual OK

// Not in tight loop
```

---

## 3. When Template Is Better

```cpp
// Inner loops benefit from inlining
template<class Type>
void process(Field<Type>& f)
{
    forAll(f, i) { f[i] = compute(f[i]); }
}
```

---

## 4. Hybrid Approach

```cpp
// Virtual for selection, template for operations
class Scheme
{
public:
    virtual void solve() = 0;  // Virtual selection
protected:
    template<class Type>
    void processField(Field<Type>& f);  // Template inner
};
```

---

## Quick Reference

| Use Case | Approach |
|----------|----------|
| Model selection | Virtual |
| Inner loops | Template |
| Both needed | Hybrid |

---

## Concept Check

<details>
<summary><b>1. Virtual overhead เท่าไหร่?</b></summary>

**~10-20 cycles** per call — significant only in tight loops
</details>

<details>
<summary><b>2. Template tradeoff คืออะไร?</b></summary>

**Fixed at compile-time** — can't change at runtime
</details>

<details>
<summary><b>3. Hybrid approach ทำอย่างไร?</b></summary>

**Virtual for selection**, template for inner operations
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Errors:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md)