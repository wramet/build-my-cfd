# Smart Pointers in C++ for CFD Applications

Modern C++ memory management is critical for building efficient CFD solvers. This section explores smart pointer patterns used in OpenFOAM-style architectures.

## Memory Management Challenges in CFD

CFD applications face unique memory management challenges:

- **Large mesh data structures** with millions of cells
- **Field arrays** that need shared access across solvers
- **Cyclic dependencies** between solvers and boundary conditions
- **Property caches** that require lifetime management

## Smart Pointer Types

### unique_ptr - Exclusive Ownership

`unique_ptr` provides exclusive ownership with compile-time guarantees. Perfect for mesh data structures where one component owns the data.

```cpp
#include <memory>
#include "fvMesh.H"

class MeshManager {
private:
    std::unique_ptr<fvMesh> mesh_;

public:
    // Constructor takes ownership
    MeshManager(std::unique_ptr<fvMesh> mesh)
    : mesh_(std::move(mesh)) {}

    // Transfer ownership
    std::unique_ptr<fvMesh> releaseMesh() {
        return std::move(mesh_);
    }

    // Access mesh (const and non-const)
    fvMesh& mesh() { return *mesh_; }
    const fvMesh& mesh() const { return *mesh_; }
};

// Usage in CFD solver
auto mesh = std::make_unique<fvMesh>(IOobject(...));
auto meshManager = std::make_unique<MeshManager>(std::move(mesh));
```

#### CFD Application: Mesh Ownership Transfer

```cpp
class MeshOptimizer {
private:
    std::unique_ptr<fvMesh> mesh_;
    std::vector<std::unique_ptr<cellSet>> refinedRegions_;

public:
    // Optimized mesh movement with ownership transfer
    void optimizeMesh(const dictionary& optimizationDict) {
        // Create refined regions
        auto refinedRegion = std::make_unique<cellSet>(
            *mesh_,
            "refinedCells",
            mesh_->nCells()
        );

        // Mark cells for refinement
        markCellsForRefinement(*refinedRegion, optimizationDict);

        // Transfer ownership to storage
        refinedRegions_.push_back(std::move(refinedRegion));

        // Perform optimization
        if (optimizationDict.getBool("parallelOptimize")) {
            optimizeParallel(*mesh_);
        } else {
            optimizeSerial(*mesh_);
        }
    }

    // Release mesh for solver use
    std::unique_ptr<fvMesh> releaseOptimizedMesh() {
        return std::move(mesh_);
    }
};
```

### shared_ptr - Shared Ownership

`shared_ptr` enables multiple owners. Essential for field data that needs concurrent access.

```cpp
#include <memory>
#include "volScalarField.H"

class FieldManager {
private:
    std::shared_ptr<volScalarField> pressure_;
    std::shared_ptr<volScalarField> temperature_;
    std::vector<std::weak_ptr<volScalarField>> dependentFields_;

public:
    // Create field with shared ownership
    void createPressureField(const fvMesh& mesh) {
        pressure_ = std::make_shared<volScalarField>(
            IOobject(
                "p",
                mesh.time().timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );
    }

    // Access shared fields
    std::shared_ptr<volScalarField> getPressure() {
        return pressure_;
    }

    // Register dependent field (weak reference to prevent cycles)
    void registerDependentField(std::shared_ptr<volScalarField> field) {
        dependentFields_.push_back(field);
    }
};

// Multi-solver field sharing
class SolverCoordinator {
private:
    std::shared_ptr<FieldManager> fieldManager_;
    std::vector<std::unique_ptr<fvSolver>> solvers_;

public:
    void addSolver(std::unique_ptr<fvSolver> solver) {
        // Share field manager with new solver
        solver->setFieldManager(fieldManager_);
        solvers_.push_back(std::move(solver));
    }
};
```

#### CFD Application: Multi-Phase Field Sharing

```cpp
class MultiphaseFieldManager {
private:
    // Shared field ownership
    std::shared_ptr<volScalarField> alpha1_;
    std::shared_ptr<volVectorField> U_;
    std::shared_ptr<volScalarField> p_;

    // Property caches
    std::shared_ptr<R410APropertyCache> propertyCache_;

public:
    // Initialize shared fields
    void initializeFields(const fvMesh& mesh) {
        // Volume fraction field
        alpha1_ = std::make_shared<volScalarField>(
            IOobject(
                "alpha1",
                mesh.time().timeName(),
                mesh,
                IOobject::READ_IF_PRESENT,
                IOobject::AUTO_WRITE
            ),
            mesh,
            dimensionedScalar("alpha1", dimless, 0.0)
        );

        // Velocity field
        U_ = std::make_shared<volVectorField>(
            IOobject(
                "U",
                mesh.time().timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );

        // Pressure field
        p_ = std::make_shared<volScalarField>(
            IOobject(
                "p",
                mesh.time().timeName(),
                mesh,
                IOobject::READ_IF_PRESENT,
                IOobject::AUTO_WRITE
            ),
            mesh,
            dimensionedScalar("p", dimPressure, 0.0)
        );
    }

    // Get shared references
    std::shared_ptr<volScalarField> getAlpha1() const { return alpha1_; }
    std::shared_ptr<volVectorField> getU() const { return U_; }
    std::shared_ptr<volScalarField> getP() const { return p_; }

    // Property access with cache
    std::shared_ptr<R410APropertyCache> getPropertyCache() const {
        return propertyCache_;
    }
};
```

### weak_ptr - Breaking Cyclic References

`weak_ptr` observes shared objects without ownership. Prevents cycles in solver dependencies.

```cpp
#include <memory>
#include "fvSolver.H"

class BoundaryCondition;
class Solver;

class Solver {
private:
    std::shared_ptr<FieldManager> fieldManager_;
    std::vector<std::weak_ptr<BoundaryCondition>> boundaryConditions_;
    std::vector<std::weak_ptr<Solver>> coupledSolvers_;

public:
    void addBoundaryCondition(std::shared_ptr<BoundaryCondition> bc) {
        // Store weak reference to prevent cycle
        boundaryConditions_.push_back(bc);
    }

    void addCoupledSolver(std::shared_ptr<Solver> solver) {
        // Store weak reference for solver coupling
        coupledSolvers_.push_back(solver);
    }

    void solve() {
        // Convert weak to shared when needed
        for (const auto& weakSolver : coupledSolvers_) {
            if (auto sharedSolver = weakSolver.lock()) {
                exchangeBoundaryData(*sharedSolver);
            }
        }
    }
};

class BoundaryCondition {
private:
    std::weak_ptr<Solver> parentSolver_;
    std::weak_ptr<FieldManager> fieldManager_;

public:
    void setParentSolver(std::shared_ptr<Solver> solver) {
        parentSolver_ = solver;
    }

    void apply() {
        // Convert weak to shared
        if (auto sharedSolver = parentSolver_.lock()) {
            // Apply boundary condition using shared fields
            applyBoundaryCondition(
                sharedSolver->getFieldManager()->getPressure()
            );
        }
    }
};
```

## R410A Property Cache Example

A comprehensive example showing smart pointer usage for refrigerant property caching.

```cpp
#include <memory>
#include <unordered_map>
#include "volScalarField.H"
#include "R410AProperties.H"

class R410APropertyCache {
private:
    // Cache with shared ownership
    std::shared_ptr<std::unordered_map<
        double,
        std::shared_ptr<R410AProperties>
    >> temperatureCache_;

    // Cache statistics
    struct CacheStats {
        size_t hits{0};
        size_t misses{0};
        size_t evictions{0};
    };

    std::shared_ptr<CacheStats> stats_;

public:
    R410APropertyCache()
    : temperatureCache_(std::make_shared<
        std::unordered_map<double, std::shared_ptr<R410AProperties>>>()),
      stats_(std::make_shared<CacheStats>()) {}

    // Get properties with cache lookup
    std::shared_ptr<R410AProperties> getProperties(double temperature) {
        auto cache = temperatureCache_; // Shared copy

        // Check cache
        auto it = cache->find(temperature);
        if (it != cache->end()) {
            stats_->hits++;
            return it->second;
        }

        // Cache miss - create new entry
        stats_->misses++;
        auto props = std::make_shared<R410AProperties>(temperature);
        (*cache)[temperature] = props;

        // Evict old entries if cache is large
        if (cache->size() > 1000) {
            cache->clear();
            stats_->evictions++;
        }

        return props;
    }

    // Get cached enthalpy for temperature
    dimensionedScalar getEnthalpy(const volScalarField& T) {
        auto props = getProperties(T.average());
        return dimensionedScalar(
            "h",
            dimEnergy/dimMass,
            props->enthalpy()
        );
    }

    // Cache statistics
    CacheStats getStats() const {
        return *stats_;
    }
};

// CFD Solver with property caching
class R410AHeatExchangerSolver {
private:
    std::shared_ptr<MultiphaseFieldManager> fieldManager_;
    std::shared_ptr<R410APropertyCache> propertyCache_;
    std::unique_ptr<fvMesh> mesh_;

public:
    R410AHeatExchangerSolver(
        std::unique_ptr<fvMesh> mesh,
        std::shared_ptr<MultiphaseFieldManager> fieldManager
    )
    : mesh_(std::move(mesh)),
      fieldManager_(fieldManager),
      propertyCache_(std::make_shared<R410APropertyCache>()) {}

    // Solve with cached properties
    void solve() {
        auto& T = fieldManager_->getTemperature();
        auto& alpha = fieldManager_->getAlpha1();

        // Cache-aware property evaluation
        for (label cellI = 0; cellI < T.size(); ++cellI) {
            // Get properties with cache
            auto props = propertyCache_->getProperties(T[cellI]);

            // Update phase change source terms
            if (alpha[cellI] > 0.1 && alpha[cellI] < 0.9) {
                // Two-phase region - use cached properties
                dimensionedScalar h_fg = props->enthalpyVapor() - props->enthalpyLiquid();

                // Apply source term
                phaseChangeSource[cellI] =
                    alpha[cellI] * h_fg * evaporationRate[cellI];
            }
        }

        // Print cache statistics
        auto stats = propertyCache_->getStats();
        Info << "Property Cache: " << stats.hits << " hits, "
             << stats.misses << " misses, " << stats.evictons << " evictions"
             << endl;
    }
};
```

## Smart Pointer Best Practices for CFD

### 1. Ownership Design Patterns

```cpp
// ✅ Good: Clear ownership semantics
class MeshFactory {
private:
    std::unique_ptr<fvMesh> mesh_;

public:
    std::unique_ptr<fvMesh> createMesh() {
        return std::move(mesh_); // Transfer ownership
    }
};

// ❌ Bad: Unclear ownership
class MeshFactory {
private:
    fvMesh* mesh_;

public:
    fvMesh* createMesh() { return mesh_; } // Who owns this?
};
```

### 2. Preventing Memory Leaks in CFD

```cpp
class SolverIntegration {
private:
    std::vector<std::unique_ptr<fvSolver>> solvers_;
    std::vector<std::shared_ptr<FieldManager>> fieldManagers_;

public:
    // Automatic cleanup when destroyed
    ~SolverIntegration() {
        // Unique pointers automatically deleted
        // Shared pointers ref count goes to zero
    }

    // Add solver with proper ownership
    void addSolver(std::unique_ptr<fvSolver> solver) {
        solvers_.push_back(std::move(solver));
    }

    // Add field manager with shared ownership
    void addFieldManager(std::shared_ptr<FieldManager> manager) {
        fieldManagers_.push_back(manager);
    }
};
```

### 3. Thread Safety Considerations

```cpp
class ThreadSafeFieldManager {
private:
    std::shared_ptr<volScalarField> pressure_;
    mutable std::mutex mutex_;

public:
    // Thread-safe field access
    std::shared_ptr<volScalarField> getPressure() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return pressure_;
    }

    // Thread-safe field update
    void updatePressure(const volScalarField& newPressure) {
        std::lock_guard<std::mutex> lock(mutex_);
        pressure_ = std::make_shared<volScalarField>(newPressure);
    }
};
```

## Performance Considerations

### Smart Pointer Overhead

```cpp
#include <chrono>

void benchmarkSmartPointers() {
    const int N = 1000000;

    // Benchmark unique_ptr
    auto start = std::chrono::high_resolution_clock::now();
    {
        std::vector<std::unique_ptr<int>> uniqueVec;
        uniqueVec.reserve(N);

        for (int i = 0; i < N; ++i) {
            uniqueVec.push_back(std::make_unique<int>(i));
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto uniqueTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    // Benchmark raw pointers
    start = std::chrono::high_resolution_clock::now();
    {
        std::vector<int*> rawVec;
        rawVec.reserve(N);

        for (int i = 0; i < N; ++i) {
            rawVec.push_back(new int(i));
        }

        // Manual cleanup
        for (auto ptr : rawVec) {
            delete ptr;
        }
    }
    end = std::chrono::high_resolution_clock::now();
    auto rawTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    Info << "unique_ptr: " << uniqueTime.count() << " μs" << endl;
    Info << "raw_ptr: " << rawTime.count() << " μs" << endl;
}
```

### Cache-Friendly Data Access

```cpp
class CacheOptimizedField {
private:
    std::unique_ptr<double[]> data_;  // Contiguous memory
    label nCells_;

public:
    CacheOptimizedField(label nCells)
    : nCells_(nCells),
      data_(std::make_unique<double[]>(nCells)) {}

    // Cache-friendly access pattern
    void computeLaplacian() {
        for (label cellI = 0; cellI < nCells_; ++cellI) {
            // Access neighboring cells (spatial locality)
            label nbI = mesh_.cellCells()[cellI][0];

            // Cache-friendly computation
            data_[cellI] = (data_[nbI] - data_[cellI]) / delta_;
        }
    }
};
```

## Summary

Smart pointers provide robust memory management for CFD applications:

1. **unique_ptr**: For exclusive ownership (mesh, solvers)
2. **shared_ptr**: For shared ownership (fields, properties)
3. **weak_ptr**: For breaking cycles (solver coupling)

When implementing smart pointers in CFD code:
- Choose the right pointer type for your ownership pattern
- Consider thread safety for shared data
- Be aware of performance implications
- Use weak pointers to prevent memory leaks from cycles

The R410A property cache example demonstrates how these patterns work together to create efficient, maintainable CFD code.