# Compilation and Machine Code

การ Compile และ Machine Code

---

## Overview

> Compiler optimizations are crucial for performance

---

## 1. Compilation Flags

```bash
# Debug (no optimization)
export WM_COMPILE_OPTION=Debug
wmake

# Optimized
export WM_COMPILE_OPTION=Opt
wmake
```

---

## 2. Optimization Levels

| Flag | Effect |
|------|--------|
| `-O0` | No optimization |
| `-O1` | Basic optimization |
| `-O2` | Most optimizations |
| `-O3` | Aggressive |

---

## 3. Key Optimizations

### Inlining

```cpp
// Compiler can inline small functions
inline scalar sqr(scalar x) { return x*x; }
```

### Vectorization

```cpp
// Loop can use SIMD
forAll(field, i)
{
    field[i] = a * field[i];  // SIMD possible
}
```

---

## 4. wmake System

```bash
# Build all
wmake

# Parallel build
wmake -j

# Clean
wclean
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Build | `wmake` |
| Clean | `wclean` |
| Optimized | `WM_COMPILE_OPTION=Opt` |
| Debug | `WM_COMPILE_OPTION=Debug` |

---

## Concept Check

<details>
<summary><b>1. -O3 ดีกว่า -O2 เสมอไหม?</b></summary>

**ไม่เสมอ** — อาจทำให้ binary ใหญ่ขึ้น, บาง optimizations อาจ fail
</details>

<details>
<summary><b>2. Debug build ช้ากว่าเท่าไหร่?</b></summary>

**2-10x** ช้ากว่า — แต่ดีกว่าสำหรับ debugging
</details>

<details>
<summary><b>3. inline keyword จำเป็นไหม?</b></summary>

**ไม่จำเป็นเสมอ** — compiler ตัดสินใจ inline เอง
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Patterns:** [05_Design_Patterns_and_Trade-offs.md](05_Design_Patterns_and_Trade-offs.md)