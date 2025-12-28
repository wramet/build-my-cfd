# Common Errors and Debugging

ข้อผิดพลาดที่พบบ่อยใน Templates

---

## 1. Missing Template Keyword

### Problem

```cpp
template<class T>
void func(Container<T>& c)
{
    c.template get<int>();  // Need 'template' keyword
}
```

### Solution

Use `template` keyword when calling template member:

```cpp
c.template memberFunc<Type>();
```

---

## 2. Missing typename

### Problem

```cpp
template<class Container>
void func()
{
    Container::iterator it;  // Error: is iterator a type?
}
```

### Solution

```cpp
typename Container::iterator it;  // Tells compiler it's a type
```

---

## 3. Two-Phase Lookup

### Problem

```cpp
template<class T>
class Derived : public Base<T>
{
    void func()
    {
        value_ = 0;  // Error: value_ not found
    }
};
```

### Solution

```cpp
this->value_ = 0;  // Or Base<T>::value_
```

---

## 4. Undefined Reference

### Problem

```
undefined reference to `Container<vector>::process()'
```

### Cause

Template definition not visible at instantiation

### Solution

- Put definition in header, or
- Explicit instantiation in .C file:

```cpp
template class Container<vector>;
```

---

## 5. Type Deduction Failure

### Problem

```cpp
template<class T>
void func(T a, T b);

func(1, 1.0);  // Error: T is int or double?
```

### Solution

```cpp
func<double>(1, 1.0);  // Explicit type
```

---

## 6. Cryptic Error Messages

### Strategy

1. Read **first error** only
2. Look for **template instantiation** line
3. Check types being deduced
4. Simplify and test incrementally

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| "not a type" | Add `typename` |
| "undeclared" | Add `this->` |
| "undefined reference" | Add explicit instantiation |
| "ambiguous" | Specify type explicitly |

---

## 🧠 Concept Check

<details>
<summary><b>1. เมื่อไหร่ต้องใช้ typename?</b></summary>

เมื่อ accessing **dependent type** (type that depends on template parameter)
</details>

<details>
<summary><b>2. undefined reference แก้อย่างไร?</b></summary>

**Explicit instantiation** หรือ put definition in header
</details>

<details>
<summary><b>3. this-> ใช้ทำไม?</b></summary>

**Force two-phase lookup** to find base class members
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Exercise:** [07_Practical_Exercise.md](07_Practical_Exercise.md)