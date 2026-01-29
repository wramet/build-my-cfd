# Phase Change Patterns for R410A

> **[!INFO]** 📚 Learning Objective
> Design patterns สำหรับ evaporation และ phase change ใน R410A

---

## Property Evaluation Pattern

```cpp
class R410APropertyEvaluator {
private:
    std::shared_ptr<IInterpolationTable> densityTable_;
    std::shared_ptr<IInterpolationTable> viscosityTable_;

public:
    double getDensity(double T, double p, double alpha) {
        double rho_l = densityTable_->lookup(T, p);
        double rho_v = densityTable_->lookup(T, p);
        return alpha * rho_l + (1.0 - alpha) * rho_v;
    }
};
```

---

*Last Updated: 2026-01-28*
