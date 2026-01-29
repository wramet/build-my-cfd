# Template Method Pattern for Solvers

> **[!INFO]** 📚 Learning Objective
> ใช้ Template Method pattern สำหรับ solver algorithm skeleton

---

## Solver Algorithm Template

```cpp
class SolverTemplate {
public:
    void solve() {
        initialize();
        while (!converged()) {
            solveMomentum();
            solvePressure();
            solveAdditionalEquations();
        }
    }

protected:
    virtual void solveMomentum() = 0;
    virtual void solvePressure() = 0;
    virtual void solveAdditionalEquations() {}
};
```

---

*Last Updated: 2026-01-28*
