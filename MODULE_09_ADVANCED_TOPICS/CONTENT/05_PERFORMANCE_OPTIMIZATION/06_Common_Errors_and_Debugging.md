# Performance - Common Errors

ข้อผิดพลาดด้านประสิทธิภาพ

---

## 1. Allocation in Loop

### Problem

```cpp
while (runTime.loop())
{
    volScalarField temp(...);  // Allocate each iteration!
}
```

### Solution

```cpp
volScalarField temp(...);  // Outside loop
while (runTime.loop())
{
    temp = compute();  // Reuse
}
```

---

## 2. Not Using tmp

### Problem

```cpp
volScalarField result = fvc::grad(p).component(0);  // Creates temporary
```

### Solution

```cpp
tmp<volVectorField> gradP = fvc::grad(p);
volScalarField result = gradP().component(0);
```

---

## 3. Cell-by-Cell Virtual

### Problem

```cpp
forAll(cells, i)
{
    result[i] = model->compute(i);  // Virtual per cell!
}
```

### Solution

```cpp
result = model->computeField();  // Single virtual call
```

---

## 4. Unnecessary Copy

### Problem

```cpp
List<scalar> copy = original;  // Full copy
```

### Solution

```cpp
const List<scalar>& ref = original;  // Reference
```

---

## Quick Troubleshooting

| Problem | Fix |
|---------|-----|
| Slow loop | Allocate outside |
| Temp allocation | Use tmp |
| Virtual overhead | Batch operations |
| Copy overhead | Use references |

---

## Concept Check

<details>
<summary><b>1. Loop allocation ช้าไหม?</b></summary>

**มาก** — allocation+deallocation ทุก iteration
</details>

<details>
<summary><b>2. หา performance issues อย่างไร?</b></summary>

**Profile** ด้วย perf หรือ similar tool
</details>

<details>
<summary><b>3. virtual call ช้าเมื่อไหร่?</b></summary>

**ใน tight loops** — millions of calls per step
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Patterns:** [05_Design_Patterns_and_Trade-offs.md](05_Design_Patterns_and_Trade-offs.md)