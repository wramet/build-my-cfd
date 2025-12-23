# 03 Inheritance Hierarchy

## 🎯 **Overview**

The OpenFOAM field system implements one of the most sophisticated template metaprogramming architectures in computational physics. This hierarchical design transforms raw numerical data into mathematically rigorous, physically meaningful objects through progressive layers of abstraction.

> [!INFO] **Key Concept**
> The inheritance hierarchy isn't just about code organization—it's a **mathematical type system** that enforces physical laws at compile-time while maintaining computational efficiency.

---

## 📊 **Complete Inheritance Architecture**

```mermaid
flowchart TD
    UList["UList<Type>"]
    List["List<Type>"]
    Field["Field<Type>"]
    regIOobject["regIOobject"]
    DimensionedField["DimensionedField<Type, GeoMesh>"]
    GeometricField["GeometricField<Type, PatchField, GeoMesh>"]

    volScalarField["volScalarField"]
    volVectorField["volVectorField"]
    surfaceScalarField["surfaceScalarField"]
    pointScalarField["pointScalarField"]

    UList -->|STL-like interface| List
    List -->|Memory management| Field
    Field -->|Mathematical operations + reference counting| regIOobject
    regIOobject -->|I/O capabilities| DimensionedField
    DimensionedField -->|Physical units + mesh| GeometricField
    GeometricField -->|Boundary conditions + time| volScalarField
    GeometricField -->|Boundary conditions + time| volVectorField
    GeometricField -->|Boundary conditions + time| surfaceScalarField
    GeometricField -->|Boundary conditions + time| pointScalarField
```

**Text Representation**:

```
                            UList<Type> (STL-like interface)
                                    ↑
                            List<Type> (Memory-managed container)
                                    ↑
tmp<Field<Type>>::refCount  ←  Field<Type> (Mathematical operations + reference counting)
                                    ↑
                            regIOobject (I/O capabilities)
                                    ↑
                    DimensionedField<Type, GeoMesh> (Physical units + mesh)
                                    ↑
            GeometricField<Type, PatchField, GeoMesh> (Boundary conditions + time)
                                    ↑
        ┌─────────────────┬──────────────────┬──────────────────┐
        │                 │                  │                  │
volScalarField   volVectorField   surfaceScalarField   pointScalarField
(cell-centered)  (cell-centered)  (face-centered)      (vertex-centered)
```

---

## 🏗️ **Layer-by-Layer Analysis**

### **Layer 1: UList<Type> - The Foundation**

```cpp
template<class Type>
class UList
{
protected:
    Type* v_;           // Raw data pointer
    label size_;        // Number of elements

public:
    // Direct access without bounds checking (performance-critical)
    Type& operator[](const label i) { return v_[i]; }
    const Type& operator[](const label i) const { return v_[i]; }

    label size() const { return size_; }
};
```

**Purpose**: Provides a lightweight, STL-like interface to contiguous memory arrays with minimal overhead.

---

### **Layer 2: List<Type> - Memory Management**

```cpp
template<class Type>
class List : public UList<Type>
{
private:
    label capacity_;    // Allocated capacity (≥ size_)

public:
    // CFD-specific constructors
    List(const label meshSize);      // Mesh-sized allocation
    List(const fvMesh& mesh);        // Direct mesh reference

    // Automatic memory management
    void setSize(const label newSize);
    void resize(const label newSize);
    void clear();
};
```

**Key Features**:
- **Automatic memory allocation** - RAII-based management
- **Capacity tracking** - Minimizes reallocations
- **CFD-optimized** - Pre-allocated blocks for mesh-sized data

> [!TIP] **Design Philosophy**
> OpenFOAM optimizes for cache-friendly access patterns with contiguous memory blocks that align with mesh topology.

---

### **Layer 3: Field<Type> - Mathematical Operations**

```cpp
template<class Type>
class Field : public tmp<Field<Type>>::refCount, public List<Type>
{
public:
    // Mathematical operators with compile-time type checking
    Field<Type> operator+(const Field<Type>&) const;
    Field<Type> operator-(const Field<Type>&) const;
    Field<Type> operator*(const scalar&) const;
    Field<Type> operator/(const scalar&) const;

    // CFD-specific reduction operations
    Type sum() const;
    Type average() const;
    Type weightedAverage(const scalarField& weights) const;
};
```

**Reference Counting Implementation**:

```cpp
class refCount
{
    mutable int count_;
public:
    refCount() : count_(0) {}
    void operator++() const { count_++; }
    void operator--() const { if (--count_ == 0) delete this; }
    int count() const { return count_; }
};
```

**Memory Efficiency Example**:

```cpp
// Field sharing example
volScalarField p1(mesh, dimensionSet(1,-1,-2,0,0,0), 0.0); // count = 1
{
    volScalarField p2(p1);  // Copy constructor - shares data, count = 2
    // Both p1 and p2 point to same memory!
    p2[0] = 101325.0;       // Modifies shared data
} // p2 destructor - count = 1, data NOT deleted

// p1 still valid with modified data
```

---

### **Layer 4: DimensionedField<Type, GeoMesh> - Physical Units**

```cpp
template<class Type, class GeoMesh>
class DimensionedField : public regIOobject, public Field<Type>
{
private:
    dimensionSet dimensions_;  // Physical unit tracking
    const GeoMesh& mesh_;      // Reference to mesh topology

public:
    // Dimensional safety enforcement
    DimensionedField operator+(const DimensionedField& other) const
    {
        if (dimensions_ != other.dimensions_) {
            FatalError << "Cannot add fields with different dimensions: "
                      << dimensions_ << " + " << other.dimensions_
                      << abort(FatalError);
        }
        // ... create result field
    }

    auto operator*(const DimensionedField& other) const
    {
        // Units multiply: (m/s) × (s) = (m)
        auto newDims = dimensions_ + other.dimensions_;
        using ResultType = decltype(Type() * Type());
        return DimensionedField<ResultType, GeoMesh>(
            *this * other, newDims, mesh_
        );
    }
};
```

**Dimensional Analysis System**:

| Quantity | Dimensions | SI Units | OpenFOAM Notation |
|----------|------------|----------|-------------------|
| Velocity | [L T⁻¹] | m/s | `dimensionSet(0,1,-1,0,0,0,0)` |
| Pressure | [M L⁻¹ T⁻²] | Pa | `dimensionSet(1,-1,-2,0,0,0,0)` |
| Density | [M L⁻³] | kg/m³ | `dimensionSet(1,-3,0,0,0,0,0)` |

> [!WARNING] **Compile-Time Safety**
> Operations that violate dimensional consistency **will not compile**:
> ```cpp
> // ❌ This won't compile - dimension mismatch
> volScalarField pressure(...);
> volVectorField velocity(...);
> auto invalid = pressure + velocity;  // Compiler error!
> ```

---

### **Layer 5: GeometricField<Type, PatchField, GeoMesh> - Spatial Context**

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh>
{
private:
    // Time management for transient simulations
    mutable label timeIndex_;
    mutable GeometricField* field0Ptr_;       // Old-time field
    mutable GeometricField* fieldPrevIterPtr_; // Previous iteration

    // Boundary condition management
    Boundary boundaryField_;

public:
    // Time advancement methods
    const GeometricField& oldTime() const;
    void storeOldTimes() const;
    void clearOldTimes() const;

    // Boundary condition management
    void correctBoundaryConditions();
    const Boundary& boundaryField() const;

    // Internal field access
    const Field<Type>& internalField() const;
    Field<Type>& ref();
};
```

**Time Management System**:

```cpp
// Demand-driven old-time storage
const GeometricField& oldTime() const {
    if (!field0Ptr_) {
        // Lazy allocation: create only when needed
        field0Ptr_ = new GeometricField(*this);  // Deep copy
        field0Ptr_->rename(name() + "OldTime");
    }
    return *field0Ptr_;
}

void storeOldTimes() {
    if (field00Ptr_) delete field00Ptr_;  // Delete tⁿ⁻²

    // Time level shifting: tⁿ⁻² ← tⁿ⁻¹ ← tⁿ
    field00Ptr_ = field0Ptr_;
    field0Ptr_ = new GeometricField(*this);

    // Memory optimization: store only required history
    if (timeScheme == Euler) {
        delete field00Ptr_;  // Euler needs only one old time
        field00Ptr_ = nullptr;
    }
}
```

**Boundary Condition Architecture**:

```cpp
class Boundary {
private:
    PtrList<PatchField<Type>> patches_;

public:
    void evaluate() {
        // 1. Update coupled patches (processor, cyclic, etc.)
        // 2. Apply physical constraints (inlet, outlet, wall)
        // 3. Enforce continuity at patch interfaces
        // 4. Handle non-orthogonal correction
    }
};
```

---

## 🔧 **Specialized Field Types**

### **Volume Fields (Cell-Centered)**

```cpp
namespace Foam
{
    typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
    typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
    typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;
    typedef GeometricField<symmTensor, fvPatchField, volMesh> volSymmTensorField;
}
```

**Common Usage**:
- `volScalarField`: Pressure ($p$), Temperature ($T$), Density ($\rho$)
- `volVectorField`: Velocity ($\mathbf{u}$), Displacement ($\mathbf{d}$)
- `volTensorField`: Velocity gradient ($\nabla\mathbf{u}$), Stress ($\boldsymbol{\tau}$)

### **Surface Fields (Face-Centered)**

```cpp
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;
typedef GeometricField<vector, fvsPatchField, surfaceMesh> surfaceVectorField;
```

**Purpose**: Flux calculations, convective terms, interpolation

### **Point Fields (Vertex-Centered)**

```cpp
typedef GeometricField<scalar, pointPatchField, pointMesh> pointScalarField;
```

**Purpose**: Interpolation values, visualization, post-processing

---

## ⚡ **Expression Templates - Zero-Cost Abstraction**

### **Problem with Traditional C++**

```cpp
// ❌ Traditional C++ (inefficient - creates temporaries)
Field<scalar> temp1 = rho * gh;      // Allocation #1
Field<scalar> temp2 = p_rgh + temp1; // Allocation #2
p = temp2;                           // Assignment (third operation)
// Total: 2 full field allocations + 3 passes through data
```

### **OpenFOAM Expression Templates**

```cpp
template<class Op, class LHS, class RHS>
class FieldExpression {
    const LHS& lhs_;
    const RHS& rhs_;

public:
    FieldExpression(const LHS& lhs, const RHS& rhs)
        : lhs_(lhs), rhs_(rhs) {}

    auto operator[](label i) const {
        return Op::apply(lhs_[i], rhs_[i]);
    }
};

struct AddOp {
    template<class T1, class T2>
    static auto apply(const T1& a, const T2& b) { return a + b; }
};

struct MultiplyOp {
    template<class T1, class T2>
    static auto apply(const T1& a, const T2& b) { return a * b; }
};
```

**Result**:

```cpp
// ✅ OpenFOAM expression templates (efficient)
p = p_rgh + rho * gh;  // Single pass, zero temporary allocations
// Total: 0 field allocations + 1 pass through data
```

### **Expression Tree Structure**

When you write `p = p_rgh + rho*gh`, OpenFOAM creates an expression tree at compile-time:

```mermaid
flowchart TD
    A["p = p_rgh + rho * gh"]
    B["AddOp p_rgh, MultiplyOp"]
    C["p_rgh field"]
    D["MultiplyOp rho, gh"]
    E["rho field"]
    F["gh field"]

    A --> B
    B --> C
    B --> D
    D --> E
    D --> F
```

---

## 🧮 **Mathematical Operations**

### **Gradient Operation**

$$\nabla\phi \approx \text{fvc::grad}(\phi)$$

**Discrete Form**:
$$\int_{V_P} \nabla\phi \,dV = \sum_{f} \phi_f \mathbf{S}_f$$

**OpenFOAM Implementation**:
```cpp
volVectorField gradPhi = fvc::grad(phi);
```

### **Divergence Operation**

$$\nabla \cdot \mathbf{F} \approx \text{fvc::div}(F)$$

**Discrete Form**:
$$\int_{V_P} \nabla \cdot \mathbf{F} \,dV = \sum_{f} \mathbf{F}_f \cdot \mathbf{S}_f$$

**OpenFOAM Implementation**:
```cpp
volScalarField divF = fvc::div(F);
```

### **Laplacian Operation**

$$\nabla^2 \phi \approx \text{fvm::laplacian}(D, \phi)$$

**Discrete Form**:
$$\nabla \cdot (\Gamma \nabla \phi)|_P = \sum_f \Gamma_f \frac{\phi_N - \phi_P}{d_{PN}} \frac{S_f}{d_{PN}}$$

**OpenFOAM Implementation**:

```cpp
fvScalarMatrix TEqn(
    fvm::ddt(rho*cp, T)
  + fvm::div(phi, T)
  - fvm::laplacian(k, T)
 ==
    Q
);
```

---

## 📐 **Complete Memory Layout**

```cpp
class volScalarField_MemoryLayout {
    // From List<scalar>:
    scalar* v_;           // → Heap: [p0, p1, p2, ..., pN]
    label size_;          // Number of cells = mesh.nCells()
    label capacity_;      // Allocated capacity (≥ size_)

    // From DimensionedField<scalar, volMesh>:
    dimensionSet dimensions_;  // Stack: [1,-1,-2,0,0,0] (Pa)
    const volMesh& mesh_;      // Reference to mesh object

    // From GeometricField<scalar, fvPatchField, volMesh>:
    label timeIndex_;          // Current time index
    volScalarField* field0Ptr_; // → Heap: Old-time field (or nullptr)
    Boundary boundaryField_;   // → Heap: Array of fvPatchField objects
};
```

---

## 🔬 **Advanced Features**

### **Template Specialization for Performance**

```cpp
template<>
class AddOp<volScalarField, volScalarField> {
    inline scalar operator[](label i) const {
        return leftField_[i] + rightField_[i];
    }

    void evaluate(volScalarField& result) {
        // Use SIMD instructions directly
        vectorizedAdd(leftField_.data(), rightField_.data(),
                      result.data(), nCells_);
    }
};
```

### **Compile-Time Operation Selection**

```cpp
template<class OpType, class FieldType>
void evaluateExpression(FieldType& result, const OpType& expr) {
    if constexpr (std::is_same_v<OpType, AddOp<FieldType, FieldType>>) {
        evaluateAddition(result, expr);
    } else if constexpr (std::is_same_v<OpType, MultiplyOp<FieldType, FieldType>>) {
        evaluateMultiplication(result, expr);
    } else {
        // Fallback to generic evaluation
        forAll(result, i) result[i] = expr[i];
    }
}
```

---

## 🖥️ **Parallel Computing: Domain Decomposition**

### **Memory Layout in Parallel**

```cpp
class ParallelField {
    // Local processor data:
    scalar* internalCells_;     // Cells owned by this processor

    // Ghost cell data for communication:
    scalar* neighbourCells_;    // Cells from neighbouring processors

    // Communication buffers:
    List<scalar> sendBuffer_;   // Data to send to neighbours
    List<scalar> recvBuffer_;   // Data to receive from neighbours

    // Processor mapping:
    labelList procNeighbours_;  // Which processors share boundaries
    labelList recvProc_;        // Which processor sends each ghost cell
};
```

### **Communication Algorithm**

```cpp
void updateBoundaryConditions() {
    // 1. Pack boundary values to send
    forAll(procNeighbours_, i) {
        packBoundaryData(procNeighbours_[i], sendBuffer_[i]);
    }

    // 2. Non-blocking communication
    forAll(procNeighbours_, i) {
        MPI_Isend(sendBuffer_[i].data(), sendBuffer_[i].size(),
                  MPI_DOUBLE, procNeighbours_[i], 0, MPI_COMM_WORLD, &reqSend[i]);
        MPI_Irecv(recvBuffer_[i].data(), recvBuffer_[i].size(),
                  MPI_DOUBLE, procNeighbours_[i], 1, MPI_COMM_WORLD, &reqRecv[i]);
    }

    // 3. Wait for communication to complete
    MPI_Waitall(nNeighbours, reqRecv, MPI_STATUSES_IGNORE);

    // 4. Unpack received data
    forAll(procNeighbours_, i) {
        unpackBoundaryData(procNeighbours_[i], recvBuffer_[i]);
    }
}
```

---

## ⚡ **Performance Optimization: SIMD Vectorization**

### **Modern CPU Optimization**

```cpp
// Compiler auto-vectorization with OpenFOAM fields:
void multiplyFields(const volScalarField& rho, const volScalarField& T,
                    volScalarField& rhoT) {
    const scalar* rhoPtr = rho.begin();
    const scalar* TPtr = T.begin();
    scalar* rhoTPtr = rhoT.begin();
    const label nCells = rho.size();

    // Compiler generates SIMD instructions:
    // AVX-256: Process 8 doubles per cycle
    for (label i = 0; i < nCells; i++) {
        rhoTPtr[i] = rhoPtr[i] * TPtr[i];
    }
    // Becomes (conceptually):
    // for (i = 0; i < nCells; i += 8) {
    //     __m256d rho_vec = _mm256_load_pd(&rhoPtr[i]);
    //     __m256d T_vec = _mm256_load_pd(&TPtr[i]);
    //     __m256d result = _mm256_mul_pd(rho_vec, T_vec);
    //     _mm256_store_pd(&rhoTPtr[i], result);
    // }
}
```

---

## 💾 **Memory Access Patterns: Cache Optimization**

### **Optimizing for CPU Cache Performance**

```cpp
class CacheOptimizedField {
    // Data arranged for optimal cache line usage (64-byte cache lines):
    struct alignas(64) CacheLine {
        scalar values[8];  // 8 doubles = 64 bytes = one cache line
    };

    CacheLine* data_;      // → Heap: [line0, line1, line2, ...]

    // Memory access optimization:
    void processAdjacentCells() {
        // ✅ Sequential access - cache friendly
        for (label i = 0; i < nCells; i += 8) {
            CacheLine& line = data_[i/8];
            // Process all 8 values in same cache line
            for (int j = 0; j < 8; j++) {
                line.values[j] = compute(line.values[j]);
            }
        }
    }

    void processRandomCells() {
        // ❌ Random access - cache misses
        for (label i = 0; i < nCells; i++) {
            label randomCell = randomIndices[i];
            (*this)[randomCell] = compute((*this)[randomCell]);
        }
    }
};
```

| Access Pattern | Cache Performance | Description |
|----------------|------------------|-------------|
| Sequential Access | ✅ High (5% miss) | Cache-friendly, process in order |
| Random Access | ❌ Low (30% miss) | Cache-unfriendly, causes cache misses |

---

## 📊 **Performance Comparison**

| Metric | Traditional Method | OpenFOAM Expression Templates |
|--------|-------------------|------------------------------|
| **Test Case** | 1M cells, 1000 time steps | 1M cells, 1000 time steps |
| **Memory Allocations** | 16 GB allocated/freed | 16 MB (1000× reduction) |
| **Cache Misses** | ~30% | ~5% (6× improvement) |
| **Runtime** | ~45 seconds | ~12 seconds (3.75× speedup) |
| **CPU Utilization** | Moderate | Better vectorization |

### **Performance Gain Factors**

1. **Memory reduction**: 1000× fewer allocations
2. **Cache efficiency**: 6× fewer cache misses
3. **CPU utilization**: Better vectorization

---

## 🎯 **Key Design Principles**

### **1. Mathematical Type Safety**

```cpp
// Tensor algebra enforcement
volScalarField kineticEnergy("kE", 0.5 * magSqr(U));  // ✓ Correct
volVectorField momentum("rhoU", rho * U);             // ✓ Correct
// auto invalid = pressure * velocity;  // ✗ Compile error
```

### **2. Physical Consistency**

```cpp
// Dimensional analysis at compile-time
dimensionedScalar p("p", dimPressure, 101325);
dimensionedScalar U("U", dimVelocity, 10.0);
// p + U;  // ✗ Dimension mismatch error
```

### **3. Performance Transparency**

```cpp
// Zero-cost abstraction
tmp<volScalarField> divU = fvc::div(U);
// tmp object automatically deleted when scope ends
```

---

## 🔗 **Related Topics**

- [[04_⚙️_Key_Mechanisms_The_Inheritance_Chain]] - Detailed implementation analysis
- [[05_🧠_Under_the_Hood_Complete_Inheritance_Hierarchy]] - Runtime behavior
- [[08_🔬_DeepSeek-Enhanced_Analysis]] - Mathematical type theory

---

> [!INFO] **Summary**
> The OpenFOAM inheritance hierarchy represents a **mathematical safety system** where:
> - **Type safety** enforces tensor algebra rules
> - **Dimensional analysis** prevents physical inconsistencies
> - **Expression templates** eliminate temporary allocations
> - **Reference counting** optimizes memory usage
> - **Template metaprogramming** enables compile-time optimizations
>
> This architecture transforms abstract PDEs into efficient, parallel, CFD code while respecting fundamental physical laws.
