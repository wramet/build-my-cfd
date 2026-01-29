# MODULE_05 Section 01: Foundation Primitives (Vectors, Tensors, Smart Pointers)
# หน่วยที่ 05 ส่วนที่ 01: พื้นฐานดั้งเดิม (เวกเตอร์, เทนเซอร์, สมาร์ทพอยน์เตอร์)

## 1. Overview / ภาพรวม

### Why Foundation Primitives Matter / เหตุผลที่พื้นฐานดั้งเดิมมีความสำคัญ

In computational fluid dynamics (CFD), foundation primitives like vectors and tensors form the building blocks of all physical equations. For R410A evaporator simulation, these primitives represent:
- Velocity fields: $\mathbf{U} = (U_r, U_z)$ in cylindrical coordinates
- Stress tensors: $\boldsymbol{\tau}$ for two-phase refrigerant flow
- Temperature gradients: $\nabla T$ for heat transfer calculations

การจำลองการไหลของสารทำความเย็น R410A ในเครื่องระเหยต้องการการแสดงผลทางคณิตศาสตร์ที่แม่นยำ:
- เวกเตอร์ความเร็วในพิกัดทรงกระบอก: $\mathbf{U} = (U_r, U_z)$
- เทนเซอร์ความเค้นสำหรับการไหลสองเฟส: $\boldsymbol{\tau}$
- เกรเดียนต์อุณหภูมิสำหรับการถ่ายเทความร้อน: $\nabla T$

**Key Insight**: The choice of vector/tensor implementation affects:
- Memory efficiency for large-scale simulations
- Computational performance through SIMD optimization
- Code maintainability and safety

## 2. OpenFOAM Approach / วิธีการของ OpenFOAM

### Vector and Tensor Implementation / การนำเวกเตอร์และเทนเซอร์ไปใช้

OpenFOAM implements vectors and tensors as template classes in `src/OpenFOAM/primitives/`:

```cpp
// File: src/OpenFOAM/primitives/Vector/Vector.H
template<class Cmpt>
class Vector : public VectorSpace<Vector<Cmpt>, Cmpt, 3>
{
public:
    // Component access
    Cmpt& x() { return this->v_[0]; }
    Cmpt& y() { return this->v_[1]; }
    Cmpt& z() { return this->v_[2]; }

    // Vector operations
    Vector<Cmpt> operator^(const Vector<Cmpt>&) const;  // Cross product
    Cmpt operator&(const Vector<Cmpt>&) const;          // Dot product
};

// File: src/OpenFOAM/primitives/Tensor/Tensor.H
template<class Cmpt>
class Tensor : public VectorSpace<Tensor<Cmpt>, Cmpt, 9>
{
public:
    // Tensor operations
    Tensor<Cmpt> operator&(const Tensor<Cmpt>&) const;  // Inner product
    Vector<Cmpt> operator&(const Vector<Cmpt>&) const;  // Tensor-vector product
};
```

### Smart Pointers in OpenFOAM / สมาร์ทพอยน์เตอร์ใน OpenFOAM

OpenFOAM uses its own smart pointer system:

```cpp
// File: src/OpenFOAM/memory/autoPtr/autoPtr.H
template<class T>
class autoPtr
{
    mutable T* ptr_;

public:
    // Constructor with allocation
    explicit autoPtr(T* p = nullptr) : ptr_(p) {}

    // Destructor with cleanup
    ~autoPtr() { if (ptr_) delete ptr_; }

    // Access operators
    T& operator()() { return *ptr_; }
    T* operator->() { return ptr_; }

    // Release ownership
    T* release() { T* p = ptr_; ptr_ = nullptr; return p; }
};

// File: src/OpenFOAM/memory/refPtr/refPtr.H
template<class T>
class refPtr
{
    // Reference counting pointer
    mutable T* ptr_;
    mutable int* refCount_;
};
```

### Memory Management Patterns / รูปแบบการจัดการหน่วยความจำ

```cpp
// OpenFOAM field allocation pattern
volVectorField* U = new volVectorField(
    IOobject(
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

// Must manually delete or use autoPtr
autoPtr<volVectorField> Uptr(U);
```

## 3. Modern C++ Approach / วิธีการของ C++ รุ่นใหม่

### Eigen Library for Vectors/Tensors / ไลบรารี Eigen สำหรับเวกเตอร์และเทนเซอร์

```cpp
#include <Eigen/Dense>
#include <memory>

// Vector operations with Eigen
Eigen::Vector3d velocity(1.0, 2.0, 3.0);
Eigen::Vector3d position(4.0, 5.0, 6.0);

// Dot product
double dotProduct = velocity.dot(position);

// Cross product (important for vorticity)
Eigen::Vector3d crossProduct = velocity.cross(position);

// Tensor as 3x3 matrix
Eigen::Matrix3d stressTensor;
stressTensor << 1.0, 0.1, 0.2,
                0.1, 2.0, 0.3,
                0.2, 0.3, 3.0;

// Tensor-vector product
Eigen::Vector3d force = stressTensor * velocity;
```

### Modern Smart Pointers / สมาร์ทพอยน์เตอร์รุ่นใหม่

```cpp
#include <memory>

// Unique ownership (replaces autoPtr)
auto velocityField = std::make_unique<Eigen::VectorXd>(mesh.nCells() * 3);

// Shared ownership (replaces refPtr)
auto propertyTable = std::make_shared<PropertyTable<R410A>>();

// Weak pointers for non-owning references
std::weak_ptr<PropertyTable<R410A>> weakRef = propertyTable;
```

### RAII and Move Semantics / RAII และการเคลื่อนย้ายความหมาย

```cpp
class R410AField
{
private:
    std::unique_ptr<Eigen::VectorXd> data_;
    std::string name_;

public:
    // Constructor with RAII
    R410AField(size_t size, const std::string& name)
        : data_(std::make_unique<Eigen::VectorXd>(size))
        , name_(name)
    {
        // Memory automatically managed
    }

    // Move constructor
    R410AField(R410AField&& other) noexcept
        : data_(std::move(other.data_))
        , name_(std::move(other.name_))
    {}

    // Move assignment
    R410AField& operator=(R410AField&& other) noexcept
    {
        if (this != &other) {
            data_ = std::move(other.data_);
            name_ = std::move(other.name_);
        }
        return *this;
    }

    // No copy operations (unique ownership)
    R410AField(const R410AField&) = delete;
    R410AField& operator=(const R410AField&) = delete;
};
```

## 4. Code Comparison / การเปรียบเทียบโค้ด

### Vector Operations Comparison / การเปรียบเทียบการดำเนินการเวกเตอร์

```cpp
// ============ OPENFOAM STYLE ============
#include "vector.H"
#include "tensor.H"

// Vector creation
Vector<double> v1(1.0, 2.0, 3.0);
Vector<double> v2(4.0, 5.0, 6.0);

// Dot product
double dot = v1 & v2;

// Cross product (vorticity calculation)
Vector<double> cross = v1 ^ v2;

// Tensor operations
Tensor<double> stress(
    1.0, 0.1, 0.2,
    0.1, 2.0, 0.3,
    0.2, 0.3, 3.0
);

// Tensor-vector product
Vector<double> force = stress & v1;

// ============ MODERN C++ STYLE ============
#include <Eigen/Dense>

// Vector creation
Eigen::Vector3d ev1(1.0, 2.0, 3.0);
Eigen::Vector3d ev2(4.0, 5.0, 6.0);

// Dot product
double edot = ev1.dot(ev2);

// Cross product
Eigen::Vector3d ecross = ev1.cross(ev2);

// Tensor as matrix
Eigen::Matrix3d estress;
estress << 1.0, 0.1, 0.2,
           0.1, 2.0, 0.3,
           0.2, 0.3, 3.0;

// Tensor-vector product
Eigen::Vector3d eforce = estress * ev1;
```

### Smart Pointer Comparison / การเปรียบเทียบสมาร์ทพอยน์เตอร์

```cpp
// ============ OPENFOAM STYLE ============
#include "autoPtr.H"
#include "refPtr.H"

// Single ownership
autoPtr<volVectorField> Uptr(new volVectorField(...));

// Reference counting
refPtr<surfaceScalarField> phiRef(phi);

// Manual memory management still common
scalarField* T = new scalarField(mesh.nCells());
// ... must remember to delete!

// ============ MODERN C++ STYLE ============
#include <memory>

// Single ownership (no delete needed)
auto U = std::make_unique<VolumeField<Eigen::Vector3d>>(...);

// Shared ownership
auto phi = std::make_shared<SurfaceField<double>>(...);

// Automatic RAII - no manual delete
{
    auto T = std::make_unique<Eigen::VectorXd>(mesh.nCells());
    // Memory automatically freed when out of scope
}
```

### Performance Considerations / การพิจารณาด้านประสิทธิภาพ

```cpp
// SIMD Optimization with Eigen
Eigen::MatrixXd A = Eigen::MatrixXd::Random(1000, 1000);
Eigen::MatrixXd B = Eigen::MatrixXd::Random(1000, 1000);

// Eigen uses expression templates and SIMD
Eigen::MatrixXd C = A * B;  // Optimized at compile time

// Batch operations for CFD fields
void computeVorticity(const Eigen::MatrixX3d& velocity,
                      Eigen::MatrixX3d& vorticity)
{
    // Eigen can vectorize this loop
    #pragma omp parallel for
    for (int i = 0; i < velocity.rows(); ++i) {
        // SIMD optimized operations
        vorticity.row(i) = velocity.row(i).cross(...);
    }
}
```

## 5. R410A Context / บริบทการใช้งาน R410A

### Cylindrical Coordinate System / ระบบพิกัดทรงกระบอก

For evaporator simulation, we need cylindrical coordinates $(r, \theta, z)$:

```cpp
class CylindricalVector
{
private:
    Eigen::Vector3d data_;  // (r, theta, z) components

public:
    // Convert to Cartesian for calculations
    Eigen::Vector3d toCartesian(double theta) const
    {
        double r = data_[0];
        double phi = data_[1];  // theta component
        double z = data_[2];

        return Eigen::Vector3d(
            r * cos(theta) - phi * sin(theta),
            r * sin(theta) + phi * cos(theta),
            z
        );
    }

    // Divergence in cylindrical coordinates
    double divergence(const CylindricalVector& grad) const
    {
        // ∇·U = (1/r) ∂(rU_r)/∂r + (1/r) ∂U_θ/∂θ + ∂U_z/∂z
        return (1.0/data_[0]) * (data_[0] * grad.r() + data_[0])
               + (1.0/data_[0]) * grad.theta()
               + grad.z();
    }
};
```

### Two-Phase Flow Tensors / เทนเซอร์สำหรับการไหลสองเฟส

```cpp
class R410AStressTensor
{
private:
    Eigen::Matrix3d stress_;
    double alpha_;  // Void fraction

public:
    // Effective stress for two-phase flow
    Eigen::Matrix3d effectiveStress(double mu_liquid,
                                    double mu_vapor) const
    {
        // Weighted average based on void fraction
        double mu_effective = alpha_ * mu_vapor
                            + (1.0 - alpha_) * mu_liquid;

        return mu_effective * stress_;
    }

    // Surface tension contribution
    Eigen::Matrix3d surfaceTension(const Eigen::Vector3d& normal,
                                   double sigma) const
    {
        // σ(δ_ij - n_i n_j)κ
        Eigen::Matrix3d I = Eigen::Matrix3d::Identity();
        Eigen::Matrix3d nn = normal * normal.transpose();

        return sigma * (I - nn);  // Curvature κ assumed included
    }
};
```

### Property Table Management / การจัดการตารางคุณสมบัติ

```cpp
class R410APropertyTable
{
private:
    // Smart pointer managed property data
    std::shared_ptr<std::vector<double>> temperature_;
    std::shared_ptr<std::vector<double>> pressure_;
    std::shared_ptr<std::vector<double>> density_;
    std::shared_ptr<std::vector<double>> enthalpy_;

public:
    R410APropertyTable(const std::string& dataFile)
    {
        // Load property data with shared ownership
        temperature_ = std::make_shared<std::vector<double>>();
        pressure_ = std::make_shared<std::vector<double>>();
        density_ = std::make_shared<std::vector<double>>();
        enthalpy_ = std::make_shared<std::vector<double>>();

        loadFromFile(dataFile);
    }

    // Multiple solvers can share the same property table
    std::shared_ptr<R410APropertyTable> clone() const
    {
        return std::make_shared<R410APropertyTable>(*this);
    }

    // Interpolate properties at given state
    Eigen::Vector4d interpolate(double T, double P) const
    {
        // Returns [ρ, h, μ, k] at (T, P)
        // Uses Eigen vectors for SIMD efficiency
        Eigen::Vector4d properties;

        // Bilinear interpolation implementation
        // ... (uses Eigen's optimized linear algebra)

        return properties;
    }
};
```

### Complete Field Implementation / การนำฟิลด์ไปใช้อย่างสมบูรณ์

```cpp
class R410AEvaporatorField
{
private:
    // Smart pointer managed fields
    std::unique_ptr<Eigen::MatrixX3d> velocity_;      // (U_r, U_θ, U_z)
    std::unique_ptr<Eigen::VectorXd> temperature_;
    std::unique_ptr<Eigen::VectorXd> pressure_;
    std::unique_ptr<Eigen::VectorXd> voidFraction_;   // α for two-phase

    // Shared property table
    std::shared_ptr<R410APropertyTable> properties_;

public:
    R410AEvaporatorField(size_t nCells,
                         std::shared_ptr<R410APropertyTable> props)
        : velocity_(std::make_unique<Eigen::MatrixX3d>(nCells, 3))
        , temperature_(std::make_unique<Eigen::VectorXd>(nCells))
        , pressure_(std::make_unique<Eigen::VectorXd>(nCells))
        , voidFraction_(std::make_unique<Eigen::VectorXd>(nCells))
        , properties_(std::move(props))  // Transfer ownership
    {
        // Initialize fields
        velocity_->setZero();
        temperature_->setConstant(283.15);  // 10°C initial
        pressure_->setConstant(101325.0);   // 1 atm
        voidFraction_->setZero();           // Start with liquid
    }

    // Compute mass flux
    Eigen::VectorXd massFlux() const
    {
        Eigen::VectorXd flux(velocity_->rows());

        for (int i = 0; i < velocity_->rows(); ++i) {
            // Get density from property table
            Eigen::Vector4d props = properties_->interpolate(
                (*temperature_)[i],
                (*pressure_)[i]
            );

            double rho = props[0];
            double alpha = (*voidFraction_)[i];

            // Two-phase density
            double rho_mixture = alpha * rho_vapor + (1 - alpha) * rho_liquid;

            // Mass flux = ρ * |U|
            flux[i] = rho_mixture * (*velocity_).row(i).norm();
        }

        return flux;
    }

    // Move semantics for efficient transfer
    R410AEvaporatorField(R410AEvaporatorField&&) = default;
    R410AEvaporatorField& operator=(R410AEvaporatorField&&) = default;

    // No copying (unique ownership of large data)
    R410AEvaporatorField(const R410AEvaporatorField&) = delete;
    R410AEvaporatorField& operator=(const R410AEvaporatorField&) = delete;
};
```

## Summary / สรุป

### Key Takeaways / ประเด็นสำคัญ

1. **Performance**: Eigen library provides SIMD optimization and expression templates that can outperform OpenFOAM's primitives for large-scale operations.

2. **Memory Safety**: Modern smart pointers (`unique_ptr`, `shared_ptr`) provide automatic memory management without the manual `new`/`delete` patterns common in OpenFOAM.

3. **Code Clarity**: RAII and move semantics make resource management explicit and exception-safe.

4. **R410A Specific**: Cylindrical coordinates and two-phase flow require careful tensor operations that benefit from Eigen's mathematical completeness.

### Migration Strategy / กลยุทธ์การย้ายระบบ

```cpp
// Hybrid approach during migration
class OpenFOAMCompatLayer
{
public:
    // Convert OpenFOAM vector to Eigen
    static Eigen::Vector3d toEigen(const Vector<double>& v)
    {
        return Eigen::Vector3d(v.x(), v.y(), v.z());
    }

    // Convert Eigen to OpenFOAM vector
    static Vector<double> toOpenFOAM(const Eigen::Vector3d& v)
    {
        return Vector<double>(v.x(), v.y(), v.z());
    }

    // Wrap OpenFOAM autoPtr as unique_ptr
    template<typename T>
    static std::unique_ptr<T> wrapAutoPtr(autoPtr<T>& ptr)
    {
        return std::unique_ptr<T>(ptr.ptr());
    }
};
```

### File References / การอ้างอิงไฟล์

**OpenFOAM Source Files:**
- `src/OpenFOAM/primitives/Vector/Vector.H`
- `src/OpenFOAM/primitives/Tensor/Tensor.H`
- `src/OpenFOAM/memory/autoPtr/autoPtr.H`
- `src/OpenFOAM/memory/refPtr/refPtr.H`

**Modern C++ Equivalents:**
- `<Eigen/Dense>` for vectors/tensors
- `<memory>` for smart pointers
- `<algorithm>` for STL algorithms

This foundation enables building a high-performance, memory-safe R410A evaporator simulation engine that combines OpenFOAM's CFD expertise with modern C++ best practices.
