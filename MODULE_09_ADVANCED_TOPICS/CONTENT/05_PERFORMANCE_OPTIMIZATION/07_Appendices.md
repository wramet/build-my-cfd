# Appendices

เอกสารเพิ่มเติม

---

## A. Compiler Flags

```bash
# Debug
wmake -j

# Optimized
export WM_COMPILE_OPTION=Opt
wmake -j
```

---

## B. Profiling Tools

| Tool | Use |
|------|-----|
| `perf` | CPU profiling |
| `valgrind` | Memory |
| `gprof` | Call graph |
| `vtune` | Intel profiling |

```bash
# Profile
perf record -g solver
perf report
```

---

## C. Common Optimizations

| Optimization | Flag |
|--------------|------|
| Inlining | `-finline-functions` |
| Vectorization | `-march=native` |
| Link-time | `-flto` |

---

## D. Memory Profiling

```bash
# Memory usage
valgrind --tool=massif solver

# Memory leaks
valgrind --leak-check=full solver
```

---

## E. Performance Checklist

- [ ] Use tmp for temporaries
- [ ] Avoid allocations in loops
- [ ] Use global reduction ops
- [ ] Check cache efficiency
- [ ] Profile before optimizing

---

## 🧠 Concept Check

<details>
<summary><b>1. เมื่อไหร่ควร profile?</b></summary>

**ก่อน optimize** — หา actual bottleneck ก่อน
</details>

<details>
<summary><b>2. WM_COMPILE_OPTION ทำอะไร?</b></summary>

**Select optimization level** — Debug vs Opt
</details>

<details>
<summary><b>3. perf ใช้ทำอะไร?</b></summary>

**CPU profiling** — หา hot functions
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)