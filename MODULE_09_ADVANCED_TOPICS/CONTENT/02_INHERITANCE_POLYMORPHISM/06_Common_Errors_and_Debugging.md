# Common Errors and Debugging

ข้อผิดพลาดที่พบบ่อย

---

## 1. Pure Virtual Not Implemented

### Problem

```
undefined reference to `vtable for MyClass'
```

### Solution

Implement all pure virtual functions:

```cpp
class MyClass : public Base
{
    virtual void required() override  // Implement!
    {
        // ...
    }
};
```

---

## 2. Missing Virtual Destructor

### Problem

Memory leak when deleting via base pointer

### Solution

```cpp
class Base
{
public:
    virtual ~Base() = default;  // Virtual destructor
};
```

---

## 3. Object Slicing

### Problem

```cpp
Derived d;
Base b = d;  // Slices! Loses derived data
```

### Solution

```cpp
// Use pointers or references
Base* ptr = &d;
Base& ref = d;
```

---

## 4. RTS Type Not Found

### Problem

```
Unknown turbulenceModel type "myModel"
```

### Solution

1. Check spelling in dictionary
2. Ensure `addToRunTimeSelectionTable` is in .C file
3. Link the library containing the model

---

## 5. Calling Virtual in Constructor

### Problem

```cpp
Base::Base()
{
    virtualMethod();  // Calls Base version, not Derived!
}
```

### Solution

Don't call virtual methods in constructors. Use two-phase init:

```cpp
obj.init();  // Call after construction
```

---

## 6. Covariant Return Confusion

### Problem

Incorrect override return type

### Solution

```cpp
class Base { virtual Base* clone(); };
class Derived : public Base
{
    virtual Derived* clone() override;  // Covariant OK
};
```

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| vtable undefined | Implement pure virtuals |
| Memory leak | Virtual destructor |
| Type not found | Check RTS registration |
| Wrong method called | Check override keyword |

---

## Concept Check

<details>
<summary><b>1. Object slicing คืออะไร?</b></summary>

**Loss of derived data** เมื่อ copy to base by value
</details>

<details>
<summary><b>2. virtual in constructor ทำไมไม่ work?</b></summary>

เพราะ derived **ยังไม่ constructed** — vtable points to base
</details>

<details>
<summary><b>3. override keyword ช่วยอะไร?</b></summary>

**Compiler check** ว่า actually overrides base method
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Exercise:** [08_Practical_Exercise.md](08_Practical_Exercise.md)
