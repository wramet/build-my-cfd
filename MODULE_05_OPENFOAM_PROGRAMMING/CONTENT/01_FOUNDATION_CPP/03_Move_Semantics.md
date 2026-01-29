# Move Semantics in C++ for CFD Applications

Move semantics enable efficient resource transfer in C++ by allowing "moving" resources instead of expensive copying. This is particularly important for CFD applications dealing with large field arrays and mesh data.

## Understanding Move Semantics

### Why Move Semantics Matter in CFD

CFD simulations often involve:

- **Large field arrays** with millions of elements
- **Mesh data structures** with complex connectivity
- **Property databases** with extensive cached data
- **Solver states** that need efficient transfer

Without move semantics, these would require expensive copies:

```cpp
// Without move semantics: expensive copy
VolVectorField U1(mesh, "U1", vector::zero);
VolVectorField U2 = U1;  // O(n) copy operation

// With move semantics: efficient transfer
VolVectorField U1(mesh, "U1", vector::zero);
VolVectorField U2 = std::move(U1);  // O(1) transfer
```

### Basic Move Operations

```cpp
#include <utility>
#include <vector>

// Move constructor example
class CFDField {
private:
    double* data_;
    size_t size_;

public:
    // Constructor
    CFDField(size_t size) : size_(size) {
        data_ = new double[size];
    }

    // Copy constructor (expensive)
    CFDField(const CFDField& other) : size_(other.size_) {
        data_ = new double[size_];
        std::copy(other.data_, other.data_ + size_, data_);
    }

    // Move constructor (efficient)
    CFDField(CFDField&& other) noexcept
    : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    // Destructor
    ~CFDField() {
        delete[] data_;
    }

    // Copy assignment
    CFDField& operator=(const CFDField& other) {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = new double[size_];
            std::copy(other.data_, other.data_ + size_, data_);
        }
        return *this;
    }

    // Move assignment
    CFDField& operator=(CFDField&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    // Getter
    const double* data() const { return data_; }
    size_t size() const { return size_; }
};
```

## rvalue References and Perfect Forwarding

### rvalue References

```cpp
#include <iostream>

// Function that takes rvalue reference
template<typename T>
void process(T&& value) {
    if constexpr (std::is_lvalue_reference_v<T>) {
        std::cout << "Processing lvalue reference" << std::endl;
    } else {
        std::cout << "Processing rvalue reference (move)" << std::endl;
    }
}

int main() {
    int x = 42;
    int y = 100;

    // Pass lvalue
    process(x);        // T is int& (lvalue reference)

    // Pass rvalue
    process(y + 58);  // T is int&& (rvalue reference)

    // Pass rvalue using std::move
    process(std::move(y));  // T is int&& (rvalue reference)

    return 0;
}
```

### Perfect Forwarding

```cpp
#include <utility>

// Template that forwards arguments perfectly
template<typename Func, typename... Args>
auto forwardToSolver(Func&& func, Args&&... args) {
    // Perfect forwarding preserves value category
    return std::forward<Func>(func)(std::forward<Args>(args)...);
}

// Example solver functions
void solveSteadyState(VolVectorField& U, VolScalarField& p) {
    std::cout << "Solving steady state..." << std::endl;
}

void solveTransient(VolVectorField&& U, VolScalarField&& p, scalar dt) {
    std::cout << "Solving transient with dt = " << dt << std::endl;
}

// Usage
class SolverDispatcher {
public:
    template<typename... Args>
    void dispatch(SolverType type, Args&&... args) {
        switch (type) {
            case SolverType::STEADY:
                forwardToSolver(solveSteadyState, std::forward<Args>(args)...);
                break;
            case SolverType::TRANSIENT:
                forwardToSolver(solveTransient, std::forward<Args>(args)...);
                break;
        }
    }
};
```

## Efficient Field Operations with Move Semantics

### Field Class with Move Support

```cpp
#include <vector>
#include <algorithm>

template<typename Type>
class VolField {
private:
    std::vector<Type> data_;
    word name_;

public:
    // Constructor
    VolField(const word& name, label size)
    : name_(name), data_(size) {}

    // Move constructor
    VolField(VolField&& other) noexcept
    : name_(std::move(other.name_)),
      data_(std::move(other.data_)) {}

    // Move assignment
    VolField& operator=(VolField&& other) noexcept {
        if (this != &other) {
            name_ = std::move(other.name_);
            data_ = std::move(other.data_);
        }
        return *this;
    }

    // Factory methods for creating fields
    static VolField<Type> createField(
        const word& name,
        const fvMesh& mesh,
        const dimensioned<Type>& initValue
    ) {
        VolField<Type> field(name, mesh.nCells());

        for (label cellI = 0; cellI < mesh.nCells(); ++cellI) {
            field[cellI] = initValue.value();
        }

        return field;
    }

    // Method that returns by value (RVO optimization)
    VolField<Type> interpolate(const VolField<Type>& other) const {
        VolField<Type> result(name_ + "_interpolated", data_.size());

        for (size_t i = 0; i < data_.size(); ++i) {
            result[i] = 0.5 * (data_[i] + other[i]);
        }

        return result;
    }

    // Method that moves data
    void moveDataFrom(VolField<Type>&& source) {
        data_ = std::move(source.data_);
    }

    // Accessors
    Type& operator[](label i) { return data_[i]; }
    const Type& operator[](label i) const { return data_[i]; }
    size_t size() const { return data_.size(); }
    const word& name() const { return name_; }
};
```

### R410A Property Cache with Move Semantics

```cpp
#include <unordered_map>
#include <utility>

class R410APropertyCache {
private:
    struct PropertyData {
        scalar density;
        scalar enthalpy;
        scalar viscosity;
        scalar thermalConductivity;

        PropertyData() : density(0), enthalpy(0), viscosity(0), thermalConductivity(0) {}

        PropertyData(PropertyData&& other) noexcept
        : density(other.density), enthalpy(other.enthalpy),
          viscosity(other.viscosity), thermalConductivity(other.thermalConductivity) {}

        PropertyData& operator=(PropertyData&& other) noexcept {
            if (this != &other) {
                density = other.density;
                enthalpy = other.enthalpy;
                viscosity = other.viscosity;
                thermalConductivity = other.thermalConductivity;
            }
            return *this;
        }
    };

    std::unordered_map<scalar, PropertyData> propertyMap_;

public:
    // Add properties with move semantics
    void addProperties(scalar temperature, PropertyData&& props) {
        propertyMap_.emplace(temperature, std::move(props));
    }

    // Get properties (returns by value)
    PropertyData getProperties(scalar temperature) const {
        auto it = propertyMap_.find(temperature);
        if (it != propertyMap_.end()) {
            return it->second;
        }
        return PropertyData();
    }

    // Efficient bulk property loading
    void loadPropertyBulk(std::vector<scalar>&& temperatures) {
        PropertyData bulkProps;

        // Compute bulk properties once
        bulkProps.density = computeBulkDensity(temperatures);
        bulkProps.enthalpy = computeBulkEnthalpy(temperatures);
        bulkProps.viscosity = computeBulkViscosity(temperatures);
        bulkProps.thermalConductivity = computeBulkThermalConductivity(temperatures);

        // Add to cache with move semantics
        for (auto temp : temperatures) {
            propertyMap_.emplace(temp, bulkProps);
        }
    }
};
```

## Return Value Optimization (RVO) and Named Return Value Optimization (NRVO)

### Understanding RVO

```cpp
// RVO example
class CFDMesh {
private:
    std::vector<vector> points_;
    std::vector<label> cells_;

public:
    // Function that returns mesh (RVO applies)
    CFDMesh createSimpleMesh() {
        CFDMesh mesh;

        // Add points
        mesh.addPoint(vector(0, 0, 0));
        mesh.addPoint(vector(1, 0, 0));
        mesh.addPoint(vector(0, 1, 0));

        // Add cells
        mesh.addCell({0, 1, 2});

        return mesh;  // RVO: mesh constructed directly in return location
    }

    // NRVO example
    CFDMesh createComplexMesh() {
        CFDMesh mesh;  // Named return value

        // Complex mesh construction
        generateMesh(mesh);

        return mesh;  // NRVO: mesh is moved to return location
    }
};
```

### When RVO Doesn't Apply

```cpp
class FieldProcessor {
public:
    // Function that returns different types based on condition
    VolField<scalar> processField(const VolField<scalar>& input,
                                ProcessingMode mode) {
        if (mode == ProcessingMode::SMOOTH) {
            return smoothField(input);  // RVO applies
        } else {
            return sharpenField(input);  // RVO applies
        }
    }

private:
    VolField<scalar> smoothField(const VolField<scalar>& input) {
        VolField<scalar> result(input.size());
        // Apply smoothing...
        return result;
    }

    VolField<scalar> sharpenField(const VolField<scalar>& input) {
        VolField<scalar> result(input.size());
        // Apply sharpening...
        return result;
    }
};
```

## Efficient Solver Implementation

### Solver State with Move Semantics

```cpp
#include <queue>

class SolverState {
private:
    dictionary solutionDict_;
    std::unique_ptr<Time> time_;
    label nIter_;

public:
    // Constructor
    SolverState(const dictionary& dict, std::unique_ptr<Time> time)
    : solutionDict_(dict), time_(std::move(time)), nIter_(0) {}

    // Move constructor
    SolverState(SolverState&& other) noexcept
    : solutionDict_(std::move(other.solutionDict_)),
      time_(std::move(other.time_)),
      nIter_(other.nIter_) {}

    // Create new solver state (returns by value)
    SolverState createSubState(const word& subDictName) const {
        dictionary subDict = solutionDict_.subDict(subDictName);
        auto newTime = std::make_unique<Time>(*time_);

        return SolverState(subDict, std::move(newTime));
    }

    // Advance solver state
    SolverState advance(scalar dt) const {
        SolverState newState = *this;  // Copy

        // Update time
        newState.time_->setTime(newState.time_->value() + dt);
        newState.nIter_++;

        return newState;
    }
};

class MultiPhaseSolver {
private:
    std::queue<SolverState> solverQueue_;

public:
    void addSolverState(SolverState&& state) {
        solverQueue_.push(std::move(state));
    }

    SolverState getNextSolverState() {
        if (solverQueue_.empty()) {
            throw std::runtime_error("No solver states available");
        }

        SolverState state = std::move(solverQueue_.front());
        solverQueue_.pop();
        return state;
    }
};
```

### Parallel Solver with Move Semantics

```cpp
#include <vector>
#include <future>

class ParallelCFDSolver {
private:
    std::vector<std::future<VolField<scalar>>> futures_;

public:
    // Submit parallel computation
    template<typename Func>
    void submitParallelComputations(Func&& computeFunc,
                                 const std::vector<label>& cellRanges) {
        for (const auto& range : cellRanges) {
            // Launch async computation
            auto future = std::async(std::launch::async,
                std::forward<Func>(computeFunc), range);

            futures_.push_back(std::move(future));
        }
    }

    // Collect results with move semantics
    std::vector<VolField<scalar>> collectResults() {
        std::vector<VolField<scalar>> results;

        for (auto& future : futures_) {
            // Move result from future
            results.push_back(future.get());
        }

        futures_.clear();
        return results;
    }
};
```

## Move Semantics in CFD Algorithms

### Efficient Field Averaging

```cpp
template<typename Type>
class FieldAverager {
private:
    std::vector<VolField<Type>> fieldHistory_;

public:
    // Add field to history with move semantics
    void addField(VolField<Type>&& field) {
        fieldHistory_.push_back(std::move(field));
    }

    // Compute moving average (returns by value)
    VolField<Type> computeMovingAverage(int windowSize) const {
        if (fieldHistory_.empty()) {
            throw std::runtime_error("No fields in history");
        }

        VolField<Type> average = fieldHistory_.back();

        for (int i = 1; i < std::min(windowSize, static_cast<int>(fieldHistory_.size())); ++i) {
            // Add field with move semantics
            average = average + fieldHistory_[fieldHistory_.size() - i - 1];
        }

        average = average / std::min(windowSize, static_cast<int>(fieldHistory_.size()));

        return average;
    }

    // Clear old history efficiently
    void clearHistoryBefore(int timeStep) {
        // Use erase-remove idiom with move semantics
        fieldHistory_.erase(
            std::remove_if(fieldHistory_.begin(), fieldHistory_.end(),
                [timeStep](const VolField<Type>& field) {
                    return field.timeStep() < timeStep;
                }),
            fieldHistory_.end());
    }
};
```

### Mesh Adaptation with Move Semantics

```cpp
class MeshAdaptation {
private:
    std::unique_ptr<fvMesh> mesh_;
    std::vector<std::unique_ptr<cellSet>> refinedRegions_;

public:
    // Constructor with mesh ownership
    MeshAdaptation(std::unique_ptr<fvMesh> mesh)
    : mesh_(std::move(mesh)) {}

    // Adapt mesh and return adapted version (move semantics)
    std::unique_ptr<fvMesh> adaptMesh(const dictionary& adaptationDict) {
        // Create new adapted mesh
        auto adaptedMesh = std::make_unique<fvMesh>(*mesh_);

        // Mark refinement regions
        auto refinementRegions = identifyRefinementRegions(adaptationDict);

        // Move refinement regions to storage
        refinedRegions_.insert(
            refinedRegions_.end(),
            std::make_move_iterator(refinementRegions.begin()),
            std::make_move_iterator(refinementRegions.end()));

        // Perform mesh adaptation
        adaptMeshGeometry(*adaptedMesh, refinementRegions);

        return adaptedMesh;
    }

    // Efficient mesh data transfer
    void transferMeshData(std::unique_ptr<fvMesh>&& sourceMesh) {
        mesh_ = std::move(sourceMesh);
    }
};
```

## Performance Optimization Techniques

### Avoiding Copies in CFD Operations

```cpp
class OptimizedFieldOperations {
public:
    // Pass by value to enable move semantics
    VolField<scalar> smoothField(VolField<scalar> field, scalar relaxationFactor) {
        // Move optimization: field is moved here, can modify in place
        for (auto& value : field) {
            value = relaxationFactor * value + (1 - relaxationFactor) * value;
        }

        return field;  // Return modified field (potential RVO)
    }

    // Perfect forwarding for solver parameters
    template<typename Solver, typename... Args>
    void runSolver(Solver&& solver, Args&&... args) {
        // Forward solver and arguments perfectly
        std::forward<Solver>(solver).solve(std::forward<Args>(args)...);
    }

    // Efficient field combination
    VolField<scalar> combineFields(
        VolField<scalar>&& field1,
        VolField<scalar>&& field2,
        std::function<scalar(scalar, scalar)> combineFunc) {

        VolField<scalar> result(std::move(field1));

        for (size_t i = 0; i < result.size(); ++i) {
            result[i] = combineFunc(result[i], field2[i]);
        }

        return result;
    }
};
```

### Memory Pool for Field Objects

```cpp
class FieldMemoryPool {
private:
    struct FieldBlock {
        std::vector<char> storage;
        std::vector<bool> used;
        size_t blockSize_;
        size_t alignment_;

        FieldBlock(size_t blockSize, size_t alignment, size_t count)
        : blockSize_(blockSize), alignment_(alignment) {
            storage.reserve(blockSize * count);
            used.assign(count, false);
        }
    };

    std::vector<FieldBlock> blocks_;

public:
    template<typename Type>
    VolField<Type> allocateField(const word& name, label size) {
        size_t requiredSize = sizeof(Type) * size;

        // Find suitable block or allocate new one
        for (auto& block : blocks_) {
            // Try to allocate from existing block
        }

        // Allocate new block if needed
        blocks_.emplace_back(requiredSize, alignof(Type), 100);

        // Return field allocated from memory pool
        return VolField<Type>(name, size);
    }

    template<typename Type>
    void deallocateField(VolField<Type>&& field) {
        // Move field to deallocate and return to pool
        field.clear();  // Efficiently clear data
        // Field destructor will handle deallocation
    }
};
```

## Benchmarking Move Semantics Performance

```cpp
#include <chrono>
#include <iostream>

void benchmarkMoveSemantics() {
    const int fieldSize = 1000000;
    const int iterations = 100;

    // Benchmark copy semantics
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        VolField<scalar> field1("field1", fieldSize);
        VolField<scalar> field2 = field1;  // Copy
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto copyTime = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    // Benchmark move semantics
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        VolField<scalar> field1("field1", fieldSize);
        VolField<scalar> field2 = std::move(field1);  // Move
    }
    end = std::chrono::high_resolution_clock::now();
    auto moveTime = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "Copy semantics: " << copyTime.count() << " ms" << std::endl;
    std::cout << "Move semantics: " << moveTime.count() << " ms" << std::endl;
    std::cout << "Speedup: " << static_cast<double>(copyTime.count()) / moveTime.count() << "x" << std::endl;
}
```

## Best Practices for Move Semantics in CFD

### 1. Use std::move When Transferring Ownership

```cpp
class SolverManager {
private:
    std::vector<std::unique_ptr<fvSolver>> solvers_;

public:
    // ✅ Good: Transfer ownership with std::move
    void addSolver(std::unique_ptr<fvSolver> solver) {
        solvers_.push_back(std::move(solver));
    }

    // ❌ Bad: Unnecessary copy
    void addSolverBad(std::unique_ptr<fvSolver> solver) {
        auto copy = std::make_unique<fvSolver>(*solver);  // Expensive copy!
        solvers_.push_back(std::move(copy));
    }
};
```

### 2. Provide Both Copy and Move Operations

```cpp
class CFDResult {
private:
    std::vector<scalar> data_;

public:
    // Copy constructor (expensive but necessary)
    CFDResult(const CFDResult& other) : data_(other.data_) {}

    // Move constructor (efficient)
    CFDResult(CFDResult&& other) noexcept : data_(std::move(other.data_)) {}

    // Copy assignment
    CFDResult& operator=(const CFDResult& other) {
        if (this != &other) {
            data_ = other.data_;
        }
        return *this;
    }

    // Move assignment
    CFDResult& operator=(CFDResult&& other) noexcept {
        if (this != &other) {
            data_ = std::move(other.data_);
        }
        return *this;
    }
};
```

### 3. Use Perfect Forwarding for Flexible APIs

```cpp
class SolverFactory {
public:
    template<typename SolverType, typename... Args>
    std::unique_ptr<fvSolver> createSolver(Args&&... args) {
        // Perfect forwarding preserves value category
        return std::make_unique<SolverType>(
            std::forward<Args>(args)...);
    }
};

// Usage
auto solver = solverFactory.createSolver<R410ASolver>(
    mesh,                 // lvalue
    "solver",             // lvalue
    std::move(props),     // rvalue
    options               // lvalue
);
```

### 4. Enable RVO/NRVO When Possible

```cpp
// ✅ Good: RVO-friendly return
VolField<scalar> createInitialField(const fvMesh& mesh) {
    VolField<scalar> field("initial", mesh.nCells());
    // Initialize field...
    return field;  // RVO applies
}

// ❌ Bad: Prevents RVO
VolField<scalar> createInitialFieldBad(const fvMesh& mesh) {
    VolField<scalar> field("initial", mesh.nCells());
    // Initialize field...
    auto result = std::move(field);  // Unnecessary move
    return result;  // RVO prevented
}
```

## Summary

Move semantics provide significant performance benefits for CFD applications:

1. **Efficient Resource Transfer**: Avoid expensive copies of large field arrays
2. **Better Performance**: Enable zero-cost abstractions for CFD operations
3. **Clear Ownership Semantics**: Make resource management explicit
4. **Enable Parallel Processing**: Facilitate efficient data sharing between threads

Key takeaways:
- Use rvalue references (`&&`) to move resources
- Implement move constructors and move assignments for large objects
- Use perfect forwarding for flexible APIs
- Leverage RVO/NRVO when returning objects
- Provide both copy and move operations for flexibility

By applying move semantics in CFD code, you can achieve significant performance improvements while maintaining clean, maintainable code.