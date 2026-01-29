# Solver Composition Pattern

> **[!INFO]** 📚 Learning Objective
> ใช้ composition pattern สำหรับสร้าง complex solvers

---

## Component-Based Solver

```cpp
class ComposedSolver {
private:
    std::unique_ptr<IMomentumSolver> momentum_;
    std::unique_ptr<IPressureSolver> pressure_;

public:
    void solve() {
        momentum_->solve();
        pressure_->solve();
        pressure_->correctVelocity();
    }
};
```

---

*Last Updated: 2026-01-28*
