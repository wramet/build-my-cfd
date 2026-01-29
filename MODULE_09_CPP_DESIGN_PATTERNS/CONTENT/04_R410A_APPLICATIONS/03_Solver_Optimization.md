# Solver Optimization Patterns for R410A

> **[!INFO]** 📚 Learning Objective
> Performance patterns สำหรับ R410A evaporator simulation

---

## Property Caching Strategy

```cpp
class CachedPropertyEvaluator {
private:
    struct CacheEntry {
        double value;
        double timestamp;
    };

    std::map<std::tuple<double, double, double>, CacheEntry> cache_;

public:
    double getDensity(double T, double p, double alpha) {
        auto key = std::make_tuple(T, p, alpha);
        auto it = cache_.find(key);

        if (it != cache_.end() && !isExpired(it->second)) {
            return it->second.value;
        }

        double value = calculateDensity(T, p, alpha);
        cache_[key] = {value, currentTime()};
        return value;
    }
};
```

---

*Last Updated: 2026-01-28*
