# Integration and Best Practices

แนวทางปฏิบัติที่ดีสำหรับ Containers และ Memory

---

## 1. Avoid Unnecessary Copies

### Bad

```cpp
// Creates copy
List<scalar> copy = original;
```

### Good

```cpp
// Use reference
const List<scalar>& ref = original;

// Or move if transfer needed
List<scalar> moved = std::move(original);
```

---

## 2. Pre-allocate Memory

### Bad

```cpp
DynamicList<label> indices;
forAll(mesh.cells(), i)
{
    indices.append(i);  // Grows repeatedly
}
```

### Good

```cpp
DynamicList<label> indices(mesh.nCells());  // Reserve
forAll(mesh.cells(), i)
{
    indices.append(i);  // No reallocation
}
```

---

## 3. Use tmp for Temporaries

### Bad

```cpp
// Memory not freed until scope end
volScalarField* gradP = new volScalarField(fvc::grad(p));
delete gradP;  // Must remember to delete!
```

### Good

```cpp
// Automatic cleanup
tmp<volScalarField> tGradP = fvc::grad(p);
// Memory freed when tmp goes out of scope
```

---

## 4. Avoid Dangling References

### Bad

```cpp
const volScalarField& bad = computeField()();
// tmp destroyed, reference invalid!
```

### Good

```cpp
tmp<volScalarField> tField = computeField();
const volScalarField& good = tField();
// tmp alive, reference valid
```

---

## 5. Use forAll Consistently

### OpenFOAM Style

```cpp
forAll(field, i)
{
    field[i] = compute(i);
}
```

### Not Recommended

```cpp
for (int i = 0; i < field.size(); i++)  // Use label, not int
```

---

## 6. HashTable Keys

### Good Keys

```cpp
HashTable<scalar, word> byName;      // word is good key
HashTable<scalar, label> byIndex;    // label is good key
```

### Avoid

```cpp
HashTable<scalar, vector> byVector;  // Complex keys slow
```

---

## 7. PtrList Initialization

```cpp
PtrList<volScalarField> fields(n);

// Set each element
forAll(fields, i)
{
    fields.set(i, new volScalarField(...));
}

// Check before access
if (fields.set(i))
{
    volScalarField& f = fields[i];
}
```

---

## Quick Reference

| Practice | Why |
|----------|-----|
| Use references | Avoid copies |
| Pre-allocate | Avoid reallocations |
| Use tmp | Automatic cleanup |
| Keep tmp alive | Avoid dangling refs |
| Use forAll | Consistent style |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง pre-allocate?</b></summary>

**Avoid repeated reallocations** — ซึ่งช้าและ fragment memory
</details>

<details>
<summary><b>2. Dangling reference เกิดอย่างไร?</b></summary>

เมื่อ **tmp destroyed** ก่อนที่จะใช้ reference ที่ได้มา
</details>

<details>
<summary><b>3. forAll vs range-for ต่างกันอย่างไร?</b></summary>

**forAll** ให้ index `i` ซึ่งจำเป็นเมื่อต้องการ access multiple arrays ด้วย same index
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Summary:** [05_Summary_and_Exercises.md](05_Summary_and_Exercises.md)
