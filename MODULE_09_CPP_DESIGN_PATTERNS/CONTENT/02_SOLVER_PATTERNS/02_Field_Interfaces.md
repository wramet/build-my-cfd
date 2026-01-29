# Abstract Field Interfaces

> **[!INFO]** 📚 Learning Objective
> กำหนด abstract interfaces สำหรับ field operations

---

## Field Interface

```cpp
template<typename T>
class IField {
public:
    virtual size_t size() const = 0;
    virtual T& operator[](size_t i) = 0;
    virtual T average() const = 0;
};
```

---

*Last Updated: 2026-01-28*
