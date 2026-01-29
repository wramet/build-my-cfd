# Two-Phase Patterns for R410A

> **[!INFO]** 📚 Learning Objective
> ใช้ design patterns สำหรับ R410A two-phase flow simulation

---

## Phase Change Model Strategy

```cpp
class IPhaseChangeModel {
public:
    virtual volScalarField massTransferRate(
        const volScalarField& T,
        const volScalarField& alpha
    ) const = 0;
};

class SimpleEvaporationModel : public IPhaseChangeModel {
public:
    volScalarField massTransferRate(
        const volScalarField& T,
        const volScalarField& alpha
    ) const override {
        return lambda_ * max(T - TSat_, 0.0) * alpha;
    }
};

class ChenEvaporationModel : public IPhaseChangeModel {
public:
    volScalarField massTransferRate(
        const volScalarField& T,
        const volScalarField& alpha
    ) const override {
        // Chen correlation implementation
    }
};
```

---

*Last Updated: 2026-01-28*
