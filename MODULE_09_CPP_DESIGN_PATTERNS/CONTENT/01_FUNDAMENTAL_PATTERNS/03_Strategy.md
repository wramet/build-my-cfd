# Strategy Pattern for Discretization Schemes

> **[!INFO]** 📚 Learning Objective
> ใช้ Strategy pattern สำหรับ discretization schemes

---

## Strategy Interface

```cpp
class IDivergenceScheme {
public:
    virtual fvMatrix discretize(const Field& field, const Field& flux) const = 0;
};

class UpwindScheme : public IDivergenceScheme {
    fvMatrix discretize(const Field& field, const Field& flux) const override {
        // Upwind discretization
    }
};
```

---

*Last Updated: 2026-01-28*
