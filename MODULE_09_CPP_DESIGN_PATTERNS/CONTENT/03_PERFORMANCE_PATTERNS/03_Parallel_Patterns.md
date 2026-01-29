# Parallel Patterns for CFD

> **[!INFO]** 📚 Learning Objective
> ใช้ parallel patterns สำหรับ domain decomposition และ ghost cell communication

---

## Domain Decomposition Pattern

```cpp
class ParallelMesh {
private:
    std::vector<SubDomain> subDomains_;
    std::vector<GhostLayer> ghostLayers_;

public:
    void decompose(int nProcs) {
        // Decompose mesh into subdomains
        auto domains = meshDecomposer_.decompose(mesh_, nProcs);

        // Create ghost layers
        for (auto& domain : domains) {
            ghostLayers_.push_back(createGhostLayer(domain));
        }
    }

    void syncFields(Field& field) {
        // Exchange ghost cell data
        for (auto& ghost : ghostLayers_) {
            ghost.exchange(field);
        }
    }
};
```

---

*Last Updated: 2026-01-28*
