# Memory Pools for Field Allocation

> **[!INFO]** 📚 Learning Objective
> ใช้ memory pools สำหรับ efficient field memory management

---

## Custom Allocator

```cpp
template<typename T>
class FieldAllocator {
private:
    std::vector<T*> pool_;
    size_t blockSize_;

public:
    FieldAllocator(size_t blockSize = 1000000)
        : blockSize_(blockSize) {}

    T* allocate(size_t n) {
        if (n <= blockSize_) {
            // Allocate from pool
            pool_.push_back(new T[blockSize_]);
            return pool_.back();
        }
        return new T[n];
    }

    ~FieldAllocator() {
        for (auto* ptr : pool_) {
            delete[] ptr;
        }
    }
};
```

---

*Last Updated: 2026-01-28*
