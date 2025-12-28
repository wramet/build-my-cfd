# Design Patterns - Practical Exercise

แบบฝึกหัด Design Patterns

---

## Exercise 1: Factory Pattern

### Task

สร้าง Factory สำหรับ source term

```cpp
class sourceFactory
{
public:
    static autoPtr<sourceModel> create(const dictionary& dict)
    {
        word type = dict.lookup("type");

        if (type == "constant")
            return autoPtr<sourceModel>(new constantSource(dict));
        else if (type == "function")
            return autoPtr<sourceModel>(new functionSource(dict));

        FatalError << "Unknown source type: " << type;
        return nullptr;
    }
};

// Usage
autoPtr<sourceModel> source = sourceFactory::create(dict);
```

---

## Exercise 2: Strategy Pattern

### Task

สร้าง interchangeable interpolation schemes

```cpp
class interpolationScheme
{
public:
    virtual scalar interpolate(scalar a, scalar b, scalar t) = 0;
};

class linearScheme : public interpolationScheme
{
    virtual scalar interpolate(scalar a, scalar b, scalar t) override
    {
        return a + t * (b - a);
    }
};

class cubicScheme : public interpolationScheme
{
    virtual scalar interpolate(scalar a, scalar b, scalar t) override
    {
        scalar t2 = sqr(t);
        return a + t2 * (3 - 2*t) * (b - a);
    }
};
```

---

## Exercise 3: Observer Pattern

```cpp
class fieldObserver
{
public:
    virtual void update(const volScalarField& field) = 0;
};

class fieldSubject
{
    List<fieldObserver*> observers_;
public:
    void attach(fieldObserver* o) { observers_.append(o); }
    void notify(const volScalarField& f)
    {
        forAll(observers_, i) { observers_[i]->update(f); }
    }
};
```

---

## Exercise 4: Singleton

```cpp
class meshRegistry
{
    static meshRegistry* instance_;
    meshRegistry() {}
public:
    static meshRegistry& instance()
    {
        if (!instance_) instance_ = new meshRegistry();
        return *instance_;
    }
};
```

---

## Quick Reference

| Pattern | When |
|---------|------|
| Factory | Create based on dict |
| Strategy | Interchangeable algorithms |
| Observer | Watch for changes |
| Singleton | Global access point |

---

## Concept Check

<details>
<summary><b>1. Factory vs direct new?</b></summary>

**Factory**: Selection at runtime, decouples user from concrete class
</details>

<details>
<summary><b>2. Strategy pattern ดีอย่างไร?</b></summary>

**Swap algorithms** without changing user code
</details>

<details>
<summary><b>3. Singleton ข้อเสียอะไร?</b></summary>

**Global state** — ทำให้ testing ยาก
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Factory:** [02_Factory_Pattern.md](02_Factory_Pattern.md)