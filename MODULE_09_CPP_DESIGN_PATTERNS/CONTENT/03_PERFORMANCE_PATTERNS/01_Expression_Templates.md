# Expression Templates for Field Operations

> **[!INFO]** 📚 Learning Objective
> ใช้ expression templates สำหรับ lazy field evaluation และ compile-time optimization

---

## Overview

Expression templates ช่วยลด overhead ของ temporary objects ใน field operations

## Basic Expression Template

```cpp
// Expression wrapper
template<typename Expr>
class Expression {
private:
    const Expr& expr_;

public:
    explicit Expression(const Expr& expr) : expr_(expr) {}

    double operator[](size_t i) const { return expr_[i]; }
    size_t size() const { return expr_.size(); }
};

// Binary expression
template<typename LHS, typename RHS, typename Op>
class BinaryExpression {
private:
    const LHS& lhs_;
    const RHS& rhs_;
    Op op_;

public:
    BinaryExpression(const LHS& lhs, const RHS& rhs, Op op)
        : lhs_(lhs), rhs_(rhs), op_(op) {}

    double operator[](size_t i) const {
        return op_(lhs_[i], rhs_[i]);
    }

    size_t size() const {
        return lhs_.size();
    }
};

// Usage: no temporary created
auto result = field1 + field2 + field3;  // Lazy evaluation
```

---

*Last Updated: 2026-01-28*
