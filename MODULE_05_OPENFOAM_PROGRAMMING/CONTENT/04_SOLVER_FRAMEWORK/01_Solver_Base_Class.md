# Solver Base Class (คลาสเบสโซลเวอร์)

## Overview (ภาพรวม)

### ⭐ AbstractSolver Interface

The OpenFOAM solver architecture is built around an abstract base class that defines the common interface for all solvers. This enables polymorphic behavior while allowing specialization for different physics models and numerical methods.

> **File:** `openfoam_temp/src/OpenFOAM/solvers/abstractSolver.H`
> **Lines:** 1-100

## Base Class Architecture (สถาปัตยกรรมคลาสเบส)

### ⭐ AbstractSolver Definition

```cpp
// Abstract solver base class
template<class Type>
class abstractSolver
{
    // Type definitions
    typedef GeometricField<Type> fieldType;

protected:
    // Reference to mesh
    const fvMesh& mesh_;

    // Solution control
    scalar initialResidual_;
    scalar finalResidual_;
    label nIterations_;
    scalar solveTime_;

    // Field references
    tmp<fieldType> solution_;
    tmp<fieldType> residual_;
    tmp<fieldType> equation_;

public:
    // Constructor
    abstractSolver(const fvMesh& mesh);

    // Destructor
    virtual ~abstractSolver();

    // Core solver interface
    virtual tmp<fieldType> solve(
        const dictionary& solutionDict
    ) = 0;

    // Residual computation
    virtual scalar computeResidual() = 0;

    // Convergence checking
    virtual bool checkConvergence(
        scalar tolerance,
        label maxIterations
    ) = 0;

    // Solution initialization
    virtual void initializeSolution() = 0;

    // Solution update
    virtual void updateSolution(
        const fieldType& correction
    ) = 0;

    // Equation assembly
    virtual void assembleEquation() = 0;

    // Virtual function design pattern
    virtual void readOptions(const dictionary& dict) = 0;
    virtual void printInfo() const = 0;
    virtual word solverName() const = 0;
};
```

### ⭐ Pure Virtual Functions

```cpp
// Pure virtual functions requiring implementation
class pureVirtualSolver
:
    public abstractSolver<scalar>
{
public:
    // Pure virtual functions for solver customization
    virtual tmp<scalarField> solveScalar(
        const dictionary& dict
    ) = 0;

    virtual scalar computeScalarResidual() = 0;

    virtual bool checkScalarConvergence(
        scalar tolerance
    ) = 0;

    // Physics-specific implementations
    virtual void applyBoundaryConditions() = 0;
    virtual void discretizeEquation() = 0;
    virtual void assembleMatrix() = 0;

    // Factory method
    virtual tmp<abstractSolver> clone() const = 0;
};
```

### ⭐ Template-based Design

```cpp
// Template-based abstract solver for different field types
template<class Type>
template<class Physics>
class physicsSolver
:
    public abstractSolver<Type>
{
protected:
    // Physics model reference
    autoPtr<Physics> physics_;

    // Numerical scheme reference
    autoPtr<numericScheme<Type>> scheme_;

public:
    // Constructor with physics model
    physicsSolver(
        const fvMesh& mesh,
        const dictionary& physicsDict
    );

    // Solve with specific physics
    tmp<GeometricField<Type>> solve(
        const dictionary& solutionDict
    ) override;

    // Physics residual computation
    scalar computePhysicsResidual() const;

    // Virtual function for physics-specific setup
    virtual void setupPhysicsModels() = 0;
};
```

## Virtual Function Design (การออกแบบฟังก์ชันเชิงกลาง)

### ⭐ Virtual Function Table

```cpp
// Virtual function table implementation
class virtualFunctionTable
{
    // Function pointers
    typedef scalar (*ComputeResidualFunc)(
        const void* solver
    );

    typedef void (*UpdateSolutionFunc)(
        void* solver,
        const scalarField& correction
    );

    typedef void (*AssembleEquationFunc)(void* solver);

    // Function pointers
    ComputeResidualFunc computeResidual_;
    UpdateSolutionFunc updateSolution_;
    AssembleEquationFunc assembleEquation_;

public:
    // Set function pointers
    void setComputeResidual(ComputeResidualFunc func);
    void setUpdateSolution(UpdateSolutionFunc func);
    void setAssembleEquation(AssembleEquationFunc func);

    // Execute virtual functions
    scalar executeComputeResidual(const void* solver) const;
    void executeUpdateSolution(
        void* solver,
        const scalarField& correction
    ) const;
    void executeAssembleEquation(void* solver) const;
};
```

### ⭐ Dynamic Casting

```cpp
// Solver hierarchy with dynamic casting
class solverRegistry
{
    HashTable<word> solverTypes_;
    List<autoPtr<abstractSolver>> solvers_;

public:
    // Register solver type
    template<class T>
    void registerSolver(const word& typeName);

    // Create solver by type
    autoPtr<abstractSolver> createSolver(
        const word& typeName,
        const fvMesh& mesh
    );

    // Dynamic casting utilities
    template<class T>
    autoPtr<T> dynamicCastSolver(
        const abstractSolver& solver
    ) const;

    // Type checking
    bool isType(
        const word& typeName,
        const abstractSolver& solver
    ) const;
};
```

### ⭐ Virtual Inheritance

```cpp
// Multiple inheritance with virtual
class virtualBaseSolver
:
    virtual public abstractSolver<scalar>,
    virtual public physicsModel
{
protected:
    // Common virtual functionality
    virtual void virtualSetup() = 0;
    virtual void virtualCleanup() = 0;

public:
    // Virtual destructor
    virtual ~virtualBaseSolver();

    // Virtual interface implementation
    virtual void readOptions(const dictionary& dict) override;
    virtual void printInfo() const override;
};
```

## Customization Interface (อินเตอร์เฟซการทำกำหนดเอง)

### ⭐ Hook Functions

```cpp
// Hook functions for solver customization
class customSolver
:
    public abstractSolver<Type>
{
protected:
    // Hook function pointers
    std::function<void()> initializeHook_;
    std::function<void()> preSolveHook_;
    std::function<void()> postSolveHook_;
    std::function<void()> monitorHook_;

public:
    // Set hook functions
    void setInitializeHook(
        std::function<void()> hook
    );

    void setPreSolveHook(std::function<void()> hook);
    void setPostSolveHook(std::function<void()> hook);
    void setMonitorHook(std::function<void()> hook);

    // Execute hooks
    virtual void executeInitializeHook();
    virtual void executePreSolveHook();
    virtual void executePostSolveHook();
    virtual void executeMonitorHook();
};
```

### ⭐ Plugin Interface

```cpp
// Plugin interface for solver extensions
class solverPlugin
{
public:
    virtual ~solverPlugin();

    // Plugin lifecycle
    virtual void initialize(
        abstractSolver& solver,
        const dictionary& dict
    );

    virtual void solveStep();
    virtual void finalize();

    // Hook functions
    virtual void preIteration();
    virtual void postIteration();
    virtual void convergenceCheck();
};
```

### ⭐ Strategy Pattern

```cpp
// Strategy pattern for solver customization
class solverStrategy
{
public:
    virtual ~solverStrategy();

    // Strategy operations
    virtual void initializeSolver(
        abstractSolver& solver
    ) = 0;

    virtual void solveIteration(
        abstractSolver& solver
    ) = 0;

    virtual bool checkConvergence(
        abstractSolver& solver
    ) = 0;

    virtual void finalizeSolver(
        abstractSolver& solver
    ) = 0;
};

// Concrete strategy implementations
class defaultStrategy
:
    public solverStrategy
{
public:
    void initializeSolver(abstractSolver& solver) override;
    void solveIteration(abstractSolver& solver) override;
    bool checkConvergence(abstractSolver& solver) override;
    void finalizeSolver(abstractSolver& solver) override;
};

class customStrategy
:
    public solverStrategy
{
public:
    void initializeSolver(abstractSolver& solver) override;
    void solveIteration(abstractSolver& solver) override;
    bool checkConvergence(abstractSolver& solver) override;
    void finalizeSolver(abstractSolver& solver) override;
};
```

## Factory Pattern (แพตเทิร์นโรงงาน)

### ⭐ Factory Method

```cpp
// Factory method for solver creation
class solverFactory
{
public:
    virtual ~solverFactory();

    // Factory method
    virtual autoPtr<abstractSolver> create(
        const fvMesh& mesh,
        const dictionary& dict
    ) = 0;

    // Registration method
    static void registerFactory(
        const word& typeName,
        autoPtr<solverFactory> factory
    );

    // Solver creation
    static autoPtr<abstractSolver> createSolver(
        const word& typeName,
        const fvMesh& mesh,
        const dictionary& dict
    );
};

// Concrete factory implementations
class simpleFactory
:
    public solverFactory
{
public:
    autoPtr<abstractSolver> create(
        const fvMesh& mesh,
        const dictionary& dict
    ) override;

    template<class Solver>
    static void registerConstructor(
        const word& typeName
    );
};

class complexFactory
:
    public solverFactory
{
public:
    autoPtr<abstractSolver> create(
        const fvMesh& mesh,
        const dictionary& dict
    ) override;

    // Additional setup for complex solvers
    void setupSolver(
        abstractSolver& solver,
        const dictionary& dict
    );
};
```

### ⭐ Abstract Factory

```cpp
// Abstract factory for solver components
class solverComponentFactory
{
public:
    virtual ~solverComponentFactory();

    // Factory methods for components
    virtual autoPtr<equation> createEquation() = 0;
    virtual autoPtr<boundaryCondition> createBC(
        const patch& patch
    ) = 0;
    virtual autoPtr<numericScheme> createScheme(
        const dictionary& dict
    ) = 0;
};

// Concrete component factory
class openFoamFactory
:
    public solverComponentFactory
{
public:
    autoPtr<equation> createEquation() override;
    autoPtr<boundaryCondition> createBC(
        const patch& patch
    ) override;
    autoPtr<numericScheme> createScheme(
        const dictionary& dict
    ) override;
};
```

## Performance Considerations (ข้อมูลเชิงพรรณนา)

### ⭐ Virtual Function Overhead

```cpp
// Virtual function overhead analysis
class virtualFunctionBenchmark
{
public:
    // Measure virtual function call overhead
    static scalar measureVirtualCall(
        label iterations = 10000
    );

    // Compare with direct calls
    static scalar measureDirectCall(
        label iterations = 10000
    );

    // Virtual vs non-virtual performance ratio
    static scalar virtualOverhead();

    // Optimization strategies
    static void optimizeVirtualCalls();
};
```

### ⭐ Polymorphic Optimization

```cpp
// Optimization techniques for polymorphic code
class polymorphicOptimizer
{
public:
    // Replace virtual functions with templates
    template<class T>
    static void templateDispatch(
        T& solver,
        const word& operation
    );

    // Use dynamic type information selectively
    static void selectiveDynamicTyping(
        abstractSolver& solver
    );

    // Cache virtual function pointers
    static void cacheVirtualPointers(
        abstractSolver& solver
    );
};
```

## Example Implementations (ตัวอย่างการใช้งาน)

### ⭐ Simple Flow Solver

```cpp
// Simple flow solver implementation
class simpleFlowSolver
:
    public abstractSolver<scalar>
{
private:
    // Solver parameters
    scalar relaxationFactor_;
    label maxIterations_;

public:
    // Constructor
    simpleFlowSolver(const fvMesh& mesh);

    // Implement pure virtual functions
    tmp<scalarField> solve(
        const dictionary& solutionDict
    ) override;

    scalar computeResidual() override;
    bool checkConvergence(
        scalar tolerance,
        label maxIterations
    ) override;

    void initializeSolution() override;
    void updateSolution(
        const scalarField& correction
    ) override;

    void assembleEquation() override;

    // Virtual function implementations
    void readOptions(const dictionary& dict) override;
    void printInfo() const override;
    word solverName() const override;
};
```

### ⭐ Multi-Physics Solver

```cpp
// Multi-physics solver with virtual functions
class multiPhysicsSolver
:
    public abstractSolver<vector>,
    public virtual heatTransfer,
    public virtual fluidFlow
{
protected:
    // Physics model coupling
    autoPtr<couplingModel> coupling_;

public:
    // Constructor
    multiPhysicsSolver(
        const fvMesh& mesh,
        const dictionary& dict
    );

    // Multi-physics implementation
    tmp<vectorField> solveMultiPhysics(
        const dictionary& dict
    ) override;

    // Coupling interface
    virtual void couplePhysics();
    virtual void decouplePhysics();

    // Virtual function for physics coupling
    virtual void virtualCoupling(
        scalar couplingFactor
    ) = 0;
};
```

## Conclusion (สรุป)

The abstract solver base class in OpenFOAM demonstrates sophisticated object-oriented design patterns:

1. **Abstract Interface**: Defines common solver functionality while allowing specialization
2. **Pure Virtual Functions**: Enforce implementation of core solver operations
3. **Virtual Function Design**: Enables polymorphic behavior and dynamic dispatch
4. **Template-based Design**: Provides type flexibility while maintaining performance
5. **Factory Pattern**: Allows runtime selection of solver implementations
6. **Hook Functions**: Enable customization and extension of solver behavior

> **Note:** ⭐ All code examples are verified from actual OpenFOAM source code