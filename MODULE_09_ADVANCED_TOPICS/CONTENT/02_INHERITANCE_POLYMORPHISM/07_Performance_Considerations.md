# Performance Considerations

ข้อพิจารณาด้าน Performance

---

## Overview

> Virtual functions have **small overhead** but can impact tight loops

---

## 1. Virtual Function Cost

| Operation | Cost |
|-----------|------|
| Direct call | ~1 cycle |
| Virtual call | ~10-20 cycles |
| Virtual + cache miss | ~100+ cycles |

---

## 2. When It Matters

### Not Critical

```cpp
// Called once per time step
turbulence->correct();  // Virtual OK
```

### Critical

```cpp
// Called per cell (millions of times)
forAll(cells, cellI)
{
    result[cellI] = model->compute(cellI);  // Virtual per cell = slow!
}
```

---

## 3. Mitigation Strategies

### Batch Processing

```cpp
// Instead of per-cell virtual calls
forAll(cells, cellI)
{
    result[cellI] = model->compute(cellI);  // Bad
}

// Use single virtual call for whole field
result = model->computeField();  // Good
```

### Template-Based Dispatch

```cpp
// Compile-time selection instead of runtime
template<class Model>
void solve(Model& model)
{
    // No virtual calls - direct dispatch
    model.compute();
}
```

---

## 4. OpenFOAM Approach

| Level | Approach |
|-------|----------|
| Model selection | Runtime (virtual) |
| Field operations | Compile-time (templates) |
| Inner loops | Direct calls |

---

## 5. Profiling

```bash
# Profile with perf
perf record -g solver
perf report

# Look for high virtual call overhead
```

---

## Quick Reference

| Strategy | When |
|----------|------|
| Virtual | High-level selection |
| Template | Performance-critical |
| Batch | Process whole fields |

---

## 🧠 Concept Check

<details>
<summary><b>1. Virtual function ช้ากว่าเท่าไหร่?</b></summary>

ประมาณ **10-20x** สำหรับ direct call, แต่ส่วนใหญ่ไม่สำคัญ
</details>

<details>
<summary><b>2. เมื่อไหร่ที่ overhead สำคัญ?</b></summary>

เมื่อ call ใน **tight inner loop** ที่ run millions of times
</details>

<details>
<summary><b>3. แก้ปัญหาอย่างไร?</b></summary>

**Batch operations** — virtual call per field, not per cell
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Design Patterns:** [05_Design_Patterns_in_Physics.md](05_Design_Patterns_in_Physics.md)