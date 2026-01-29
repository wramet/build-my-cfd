# Abstract Factory Pattern for CFD

> **[!INFO]** 📚 Learning Objective
> ใช้ Abstract Factory pattern สำหรับสร้าง property models, boundary conditions และ R410A property tables

---

## Property Model Factory

```cpp
class IPropertyModelFactory {
public:
    virtual std::unique_ptr<IDensityModel> createDensityModel() = 0;
    virtual std::unique_ptr<IViscosityModel> createViscosityModel() = 0;
};

class R410APropertyFactory : public IPropertyModelFactory {
public:
    std::unique_ptr<IDensityModel> createDensityModel() override {
        return std::make_unique<R410ADensityModel>();
    }
};
```

---

*Last Updated: 2026-01-28*
