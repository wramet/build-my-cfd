# Boundary Condition Polymorphism

> **[!INFO]** 📚 Learning Objective
> ใช้ polymorphism สำหรับ boundary conditions

---

## BC Hierarchy

```cpp
template<typename T>
class FvPatchField {
public:
    virtual void updateCoeffs() = 0;
    virtual void evaluate() = 0;
};

class FixedValueFvPatchField : public FvPatchField<double> {
    void updateCoeffs() override {}
    void evaluate() override {}
};
```

---

*Last Updated: 2026-01-28*
