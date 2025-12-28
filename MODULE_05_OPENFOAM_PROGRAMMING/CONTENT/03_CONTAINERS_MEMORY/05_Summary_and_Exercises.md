# Containers & Memory - Summary and Exercises

สรุปและแบบฝึกหัด — ฝึกทำเพื่อเข้าใจจริง

> **ทำไมต้องทำ Exercises?**
> - อ่านอย่างเดียวไม่พอ — **ต้องเขียน code เอง**
> - ฝึก `autoPtr`, `tmp`, `PtrList` จนคล่อง
> - เตรียมพร้อมสำหรับ real-world usage

---

## Summary

### Container Types

| Container | Purpose |
|-----------|---------|
| `List<T>` | Dynamic array |
| `DynamicList<T>` | Growable list |
| `HashTable<T, Key>` | Key-value map |
| `PtrList<T>` | Pointer list |
| `Field<T>` | CFD array with ops |

### Memory Management

| Type | Ownership |
|------|-----------|
| `autoPtr<T>` | Unique |
| `tmp<T>` | Reference counted |

---

## Exercise 1: List Operations

```cpp
// Create and populate
List<scalar> values(100, 0.0);

forAll(values, i)
{
    values[i] = sqr(i);
}

// Access
scalar first = values.first();
scalar last = values.last();
label n = values.size();
```

---

## Exercise 2: DynamicList

```cpp
// Growable list
DynamicList<label> indices;

forAll(mesh.cells(), cellI)
{
    if (someCondition(cellI))
    {
        indices.append(cellI);
    }
}

// Convert to List
List<label> result = indices;
```

---

## Exercise 3: HashTable

```cpp
// Create hash table
HashTable<scalar, word> properties;

// Insert
properties.insert("density", 1000);
properties.insert("viscosity", 1e-6);

// Lookup
scalar rho = properties["density"];

// Check existence
if (properties.found("temperature"))
{
    scalar T = properties["temperature"];
}
```

---

## Exercise 4: autoPtr

```cpp
// Create with ownership
autoPtr<volScalarField> fieldPtr
(
    new volScalarField
    (
        IOobject("T", runTime.timeName(), mesh),
        mesh,
        dimensionedScalar("T", dimTemperature, 300)
    )
);

// Access
volScalarField& field = fieldPtr();

// Check validity
if (fieldPtr.valid()) { ... }

// Transfer ownership
autoPtr<volScalarField> newOwner = std::move(fieldPtr);
```

---

## Exercise 5: tmp

```cpp
// Return temporary from function
tmp<volScalarField> computeField()
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject("result", ...),
            mesh
        )
    );
}

// Use result
tmp<volScalarField> tField = computeField();
volScalarField& field = tField();

// Or with fvc
tmp<volVectorField> gradP = fvc::grad(p);
```

---

## Exercise 6: PtrList

```cpp
// List of pointers for polymorphism
PtrList<volScalarField> fields(3);

forAll(fields, i)
{
    fields.set
    (
        i,
        new volScalarField
        (
            IOobject("field" + name(i), ...),
            mesh
        )
    );
}

// Access
volScalarField& f = fields[0];
```

---

## Quick Reference

| Need | Use |
|------|-----|
| Fixed array | `List<T>` |
| Growing array | `DynamicList<T>` |
| Key-value | `HashTable<T, Key>` |
| Polymorphic list | `PtrList<T>` |
| Unique ownership | `autoPtr<T>` |
| Temporary | `tmp<T>` |

---

## 🧠 Concept Check

<details>
<summary><b>1. List vs DynamicList ต่างกันอย่างไร?</b></summary>

- **List**: Fixed size หลัง construction
- **DynamicList**: Grows with `append()`
</details>

<details>
<summary><b>2. autoPtr vs tmp ต่างกันอย่างไร?</b></summary>

- **autoPtr**: Unique ownership, move only
- **tmp**: Reference counted, can share
</details>

<details>
<summary><b>3. ทำไม fvc:: return tmp?</b></summary>

เพราะสร้าง **temporary field** → tmp เพื่อ automatic cleanup
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Container System:** [03_Container_System.md](03_Container_System.md)