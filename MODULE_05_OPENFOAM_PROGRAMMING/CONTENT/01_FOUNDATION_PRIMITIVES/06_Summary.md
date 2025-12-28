# Foundation Primitives - Summary

สรุป OpenFOAM Primitives — Quick Reference Card

> **ใช้หน้านี้สำหรับ:**
> - ดูสูตร/syntax อย่างรวดเร็ว
> - เปรียบเทียบ types ต่างๆ
> - เป็น cheat sheet ตอนเขียน code

---

## 1. Basic Types

| Type | Use | Example |
|------|-----|---------|
| `label` | Index | `label cellI = 0;` |
| `scalar` | Value | `scalar T = 300;` |
| `word` | Name | `word name = "p";` |
| `Switch` | Flag | `Switch active = true;` |

---

## 2. Mathematical Types

### Vector

```cpp
vector v(1, 2, 3);
scalar len = mag(v);
vector unit = v / mag(v);
scalar dot = v1 & v2;
vector cross = v1 ^ v2;
```

### Tensor

```cpp
tensor T(1,0,0, 0,1,0, 0,0,1);
scalar trace = tr(T);
tensor inv = inv(T);
symmTensor S = symm(T);
```

---

## 3. Dimensioned Types

```cpp
// Create
dimensionedScalar rho("rho", dimDensity, 1000);

// Access
word n = rho.name();
dimensionSet d = rho.dimensions();
scalar v = rho.value();

// Operations (dimension checked)
dimensionedScalar Re = rho * U * L / mu;
```

---

## 4. Smart Pointers

| Type | Pattern |
|------|---------|
| `autoPtr` | Unique ownership |
| `tmp` | Temporary result |
| `PtrList` | Polymorphic collection |

```cpp
// autoPtr
autoPtr<Model> model(Model::New(dict));

// tmp
tmp<volScalarField> tField = fvc::grad(p);
volScalarField& field = tField();

// PtrList
PtrList<volScalarField> fields(n);
fields.set(i, new volScalarField(...));
```

---

## 5. Containers

| Container | Method |
|-----------|--------|
| `List<T>` | `append()`, `remove()` |
| `Field<T>` | `max()`, `average()` |
| `HashTable` | `insert()`, `found()` |
| `DynamicList` | `append()` (grows) |

```cpp
// List
List<scalar> values(100, 0.0);

// Field
scalarField T(100, 300.0);
scalar maxT = max(T);

// HashTable
HashTable<scalar, word> props;
props.insert("rho", 1000);
```

---

## 6. Common Operations

| Operation | Code |
|-----------|------|
| Magnitude | `mag(v)` |
| Square | `sqr(x)` |
| Square root | `sqrt(x)` |
| Dot product | `a & b` |
| Cross product | `a ^ b` |
| Trace | `tr(T)` |
| Determinant | `det(T)` |
| Symmetric part | `symm(T)` |

---

## 7. forAll Macro

```cpp
forAll(field, i)
{
    field[i] = compute(i);
}

// Equivalent to:
for (label i = 0; i < field.size(); i++) { ... }
```

---

## Quick Reference Card

| Need | Solution |
|------|----------|
| Index | `label` |
| Value | `scalar` |
| 3D | `vector` |
| With units | `dimensionedScalar` |
| Unique ptr | `autoPtr` |
| Temp result | `tmp` |
| Array | `List`, `Field` |
| Map | `HashTable` |

---

## 🧠 Concept Check

<details>
<summary><b>1. & vs ^ ต่างกันอย่างไร?</b></summary>

- **&**: Dot product → scalar
- **^**: Cross product → vector
</details>

<details>
<summary><b>2. Field vs List ต่างกันอย่างไร?</b></summary>

**Field** มี CFD operations: `max()`, `min()`, `average()`, `sum()`
</details>

<details>
<summary><b>3. tmp ใช้เมื่อไหร่?</b></summary>

เมื่อฟังก์ชัน **return temporary field** เช่น `fvc::grad()`
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Exercises:** [07_Exercises.md](07_Exercises.md)
