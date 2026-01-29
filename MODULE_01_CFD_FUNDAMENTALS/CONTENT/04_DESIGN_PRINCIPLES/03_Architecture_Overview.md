# CFD Code Architecture Overview (ภาพรวมสถาปัตยกรรมโค้ด CFD)

> **[!INFO]** 📚 Learning Objective
> เข้าใจสถาปัตยกรรมแบบเป็นชั้นๆ (layered architecture) สำหรับโปรแกรม CFD และการออกแบบระบบที่แยกส่วนกักบัน (separation of concerns) สำหรับ R410A evaporator simulation

---

## 📋 Table of Contents (สารบัญ)

1. [Layered Architecture for CFD](#layered-architecture-for-cfd)
2. [Separation of Concerns](#separation-of-concerns)
3. [Component Design](#component-design)
4. [Data Flow Architecture](#data-flow-architecture)
5. [R410A Evaporator Architecture](#r410a-evaporator-architecture)

---

## Layered Architecture for CFD

### What is Layered Architecture?

**⭐ Definition:** Organizing code into layers where each layer only depends on layers below it

**⭐ Why it's essential for CFD:**
1. **Modularity:** Each layer has single responsibility
2. **Testability:** Test layers independently
3. **Maintainability:** Change implementation without affecting other layers
4. **Reusability:** Reuse layers in different applications

### Standard CFD Architecture Layers

```mermaid
graph TB
    subgraph Application["Application Layer"]
        A[Main Program<br/>Solver Orchestration]
    end

    subgraph Solver["Solver Layer"]
        B[Time Integration<br/>Pressure-Velocity Coupling<br/>Turbulence Models]
    end

    subgraph Discretization["Discretization Layer"]
        C[FVM Operators<br/>Scheme Selection<br/>Matrix Assembly]
    end

    subgraph Field["Field Layer"]
        D[Field Storage<br/>Field Operations<br/>Boundary Conditions]
    end

    subgraph Mesh["Mesh Layer"]
        E[Topology<br/>Geometry<br/>Boundary Patches]
    end

    subgraph LinearAlgebra["Linear Algebra Layer"]
        F[Sparse Matrices<br/>Linear Solvers<br/>Preconditioners]
    end

    subgraph Utilities["Utilities Layer"]
        G[File I/O<br/>Parallel Comm<br/>Logging]
    end

    A --> B
    B --> C
    C --> D
    C --> F
    D --> E
    F --> G
    D --> G

    classDef app fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef solver fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef disc fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef field fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef mesh fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef linalg fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef util fill:#fff9c4,stroke:#f9a825,stroke-width:2px

    class A app
    class B solver
    class C disc
    class D field
    class E mesh
    class F linalg
    class G util
```

### Layer Responsibilities

| Layer | Responsibility | Examples | Dependencies |
|-------|---------------|----------|--------------|
| **Application** | Orchestration, I/O, user interface | `main()`, `controlDict` | All layers |
| **Solver** | Solution algorithms | SIMPLE, PISO, PIMPLE | Discretization, Field, Linear Algebra |
| **Discretization** | Approximate derivatives | `fvm::div()`, `fvc::grad()` | Field, Linear Algebra |
| **Field** | Store and manipulate data | `volVectorField`, `volScalarField` | Mesh, Utilities |
| **Mesh** | Geometry and topology | `polyMesh`, `fvMesh` | Utilities |
| **Linear Algebra** | Solve linear systems | `fvMatrix`, `GAMG`, `PCG` | Utilities |
| **Utilities** | Low-level services | File I/O, MPI, memory | None |

### OpenFOAM Layer Mapping

**⭐ Verified from:** OpenFOAM source code structure

| OpenFOAM Component | Layer | Directory |
|---------------------|-------|-----------|
| `icoFoam.C`, `simpleFoam.C` | Application | `applications/solvers/` |
| `pimpleFoam/pimpleLoop()` | Solver | `applications/solvers/incompressible/` |
| `fvm::div()`, `fvc::grad()` | Discretization | `src/finiteVolume/` |
| `GeometricField` | Field | `src/OpenFOAM/fields/` |
| `fvMesh`, `polyMesh` | Mesh | `src/finiteVolume/`, `src/OpenFOAM/meshes/` |
| `lduMatrix`, `GAMG` | Linear Algebra | `src/OpenFOAM/matrices/` |
| `OFstream`, `MPI` | Utilities | `src/OpenFOAM/db/IOstreams/`, `Pstream/` |

---

## Separation of Concerns

### What is Separation of Concerns?

**⭐ Definition:** Dividing a program into distinct sections, each addressing a separate concern

**⭐ Benefits for CFD:**
1. **Focus:** Each component does one thing well
2. **Clarity:** Easy to understand what each part does
3. **Flexibility:** Change one concern without affecting others
4. **Testing:** Test each concern independently

### Concerns in CFD

```mermaid
mindmap
    root((CFD Concerns))
        Mesh
            Topology
            Geometry
            Quality
        Fields
            Storage
            Interpolation
            Boundary Conditions
        Physics
            Equations
            Properties
            Models
        Numerics
            Discretization
            Schemes
            Stability
        Solvers
            Linear
            Nonlinear
            Coupled
        I_O
            Reading
            Writing
            Visualization
        Parallel
            Decomposition
            Communication
            Load Balancing
```

### Example: Proper Separation

**❌ BAD: Everything mixed together**

```cpp
class BadSolver {
public:
    void solve() {
        // 1. Mesh concern: read mesh
        std::ifstream meshFile("mesh.obj");
        // ... parse mesh

        // 2. Field concern: create fields
        std::vector<double> U;
        // ... initialize U

        // 3. Physics concern: define properties
        double nu = 0.01;
        double rho = 1.0;

        // 4. Numerics concern: discretize
        for (size_t i = 0; i < U.size(); ++i) {
            // FVM discretization
        }

        // 5. Solver concern: solve linear system
        // ... matrix solve

        // 6. I/O concern: write results
        std::ofstream out("results.vtk");
        // ... write VTK

        // 7. Parallel concern: MPI communication
        MPI_Send(...);
    }
};
```

**✅ GOOD: Separated concerns**

```cpp
// Mesh concern
class MeshReader {
public:
    virtual std::unique_ptr<Mesh> read(const std::string& filename) = 0;
};

// Field concern
class FieldFactory {
public:
    virtual std::unique_ptr<Field> createVelocityField(const Mesh& mesh) = 0;
};

// Physics concern
class PropertyModel {
public:
    virtual double viscosity(double T) const = 0;
    virtual double density(double T, double p) const = 0;
};

// Numerics concern
class DiscretizationScheme {
public:
    virtual fvMatrix discretize(const Field& field, const Mesh& mesh) = 0;
};

// Solver concern
class LinearSolver {
public:
    virtual Field solve(const fvMatrix& matrix) = 0;
};

// I/O concern
class ResultWriter {
public:
    virtual void write(const std::string& filename, const Field& field) = 0;
};

// Parallel concern
class ParallelCommunicator {
public:
    virtual void syncFields(Field& field) = 0;
};

// Orchestrator (application layer)
class SolverOrchestrator {
private:
    std::unique_ptr<MeshReader> meshReader_;
    std::unique_ptr<FieldFactory> fieldFactory_;
    std::unique_ptr<PropertyModel> properties_;
    std::unique_ptr<DiscretizationScheme> scheme_;
    std::unique_ptr<LinearSolver> solver_;
    std::unique_ptr<ResultWriter> writer_;
    std::unique_ptr<ParallelCommunicator> comm_;

public:
    void solve() {
        // 1. Read mesh
        auto mesh = meshReader_->read("mesh.obj");

        // 2. Create fields
        auto U = fieldFactory_->createVelocityField(*mesh);

        // 3. Get properties
        double nu = properties_->viscosity(300.0);

        // 4. Discretize
        auto matrix = scheme_->discretize(*U, *mesh);

        // 5. Solve
        *U = solver_->solve(matrix);

        // 6. Sync
        comm_->syncFields(*U);

        // 7. Write
        writer_->write("results.vtk", *U);
    }
};
```

### Interface Segregation

**⭐ Principle:** Clients shouldn't depend on interfaces they don't use

```cpp
// ❌ BAD: Fat interface
class FatMeshInterface {
public:
    // Geometry operations
    virtual Point getCellCenter(size_t cellId) = 0;
    virtual double getCellVolume(size_t cellId) = 0;

    // Topology operations
    virtual std::vector<size_t> getCellNodes(size_t cellId) = 0;
    virtual std::vector<size_t> getCellFaces(size_t cellId) = 0;

    // Mesh generation
    virtual void generateMesh() = 0;
    virtual void refineMesh() = 0;

    // Mesh quality
    virtual double checkQuality() = 0;
    virtual void improveQuality() = 0;

    // Parallel operations
    virtual void decompose(int nProcs) = 0;
    virtual void sync() = 0;
};

// ✅ GOOD: Segregated interfaces
class GeometryMesh {
public:
    virtual Point getCellCenter(size_t cellId) = 0;
    virtual double getCellVolume(size_t cellId) = 0;
};

class TopologyMesh {
public:
    virtual std::vector<size_t> getCellNodes(size_t cellId) = 0;
    virtual std::vector<size_t> getCellFaces(size_t cellId) = 0;
};

class MeshGenerator {
public:
    virtual void generateMesh() = 0;
    virtual void refineMesh() = 0;
};

class MeshQualityChecker {
public:
    virtual double checkQuality() = 0;
    virtual void improveQuality() = 0;
};

class ParallelMesh {
public:
    virtual void decompose(int nProcs) = 0;
    virtual void sync() = 0;
};

// Combine multiple interfaces through inheritance
class CompleteMesh :
    public GeometryMesh,
    public TopologyMesh,
    public MeshGenerator,
    public MeshQualityChecker,
    public ParallelMesh
{
    // Implement all interfaces
};

// User only depends on what they need
void calculateVolumes(GeometryMesh& mesh) {
    // Only geometry operations available
}
```

---

## Component Design

### Component Definition

**⭐ Component:** A cohesive, reusable unit with well-defined interface

**⭐ Characteristics:**
1. **High cohesion:** Related functionality grouped together
2. **Low coupling:** Minimal dependencies on other components
3. **Clear interface:** Well-defined API
4. **Replaceable:** Can swap implementations

### Core CFD Components

```mermaid
classDiagram
    class Component {
        <<interface>>
        +initialize()*
        +execute()*
        +finalize()*
    }

    class MeshComponent {
        +initialize()
        +getCellCenters()
        +getCellVolumes()
        +getBoundaryFaces()
    }

    class FieldComponent {
        +createField()
        +getField()
        +updateField()
        +destroyField()
    }

    class SolverComponent {
        +solve()
        +setTolerance()
        +getResiduals()
    }

    class IOComponent {
        +read()
        +write()
        +monitor()
    }

    Component <|-- MeshComponent
    Component <|-- FieldComponent
    Component <|-- SolverComponent
    Component <|-- IOComponent
```

### Component Example: Property Calculator

```cpp
// Abstract component interface
class PropertyCalculator {
public:
    virtual ~PropertyCalculator() = default;

    // Pure virtual interface
    virtual double calculateDensity(double T, double p) = 0;
    virtual double calculateViscosity(double T, double p) = 0;
    virtual double calculateConductivity(double T, double p) = 0;

    // Lifecycle
    virtual void initialize() {}
    virtual void finalize() {}
};

// CoolProp implementation
class CoolPropCalculator : public PropertyCalculator {
private:
    std::string fluidName_;

public:
    CoolPropCalculator(const std::string& fluid) : fluidName_(fluid) {
        initialize();
    }

    void initialize() override {
        // Initialize CoolProp
    }

    double calculateDensity(double T, double p) override {
        return CoolProp::PropsSI("D", "T", T, "P", p, fluidName_);
    }

    double calculateViscosity(double T, double p) override {
        return CoolProp::PropsSI("V", "T", T, "P", p, fluidName_);
    }

    double calculateConductivity(double T, double p) override {
        return CoolProp::PropsSI("L", "T", T, "P", p, fluidName_);
    }
};

// Lookup table implementation
class LookupTableCalculator : public PropertyCalculator {
private:
    InterpolationTable densityTable_;
    InterpolationTable viscosityTable_;
    InterpolationTable conductivityTable_;

public:
    LookupTableCalculator(const std::string& tableDir) {
        initialize();
        densityTable_.load(tableDir + "/density.dat");
        viscosityTable_.load(tableDir + "/viscosity.dat");
        conductivityTable_.load(tableDir + "/conductivity.dat");
    }

    double calculateDensity(double T, double p) override {
        return densityTable_.interpolate(T, p);
    }

    double calculateViscosity(double T, double p) override {
        return viscosityTable_.interpolate(T, p);
    }

    double calculateConductivity(double T, double p) override {
        return conductivityTable_.interpolate(T, p);
    }
};

// Polynomial approximation implementation
class PolynomialCalculator : public PropertyCalculator {
private:
    std::vector<double> densityCoeffs_;
    std::vector<double> viscosityCoeffs_;

public:
    PolynomialCalculator(const std::vector<double>& rhoCoeffs,
                         const std::vector<double>& muCoeffs)
        : densityCoeffs_(rhoCoeffs),
          viscosityCoeffs_(muCoeffs) {}

    double calculateDensity(double T, double p) override {
        double rho = 0.0;
        double Tn = 1.0;
        for (size_t i = 0; i < densityCoeffs_.size(); ++i) {
            rho += densityCoeffs_[i] * Tn;
            Tn *= T;
        }
        return rho;
    }

    double calculateViscosity(double T, double p) override {
        double mu = 0.0;
        double Tn = 1.0;
        for (size_t i = 0; i < viscosityCoeffs_.size(); ++i) {
            mu += viscosityCoeffs_[i] * Tn;
            Tn *= T;
        }
        return mu;
    }
};

// Factory for component creation
class PropertyCalculatorFactory {
public:
    enum class Type {
        COOLPROP,
        LOOKUP_TABLE,
        POLYNOMIAL
    };

    static std::unique_ptr<PropertyCalculator> create(
        Type type,
        const std::string& param
    ) {
        switch (type) {
            case Type::COOLPROP:
                return std::make_unique<CoolPropCalculator>(param);
            case Type::LOOKUP_TABLE:
                return std::make_unique<LookupTableCalculator>(param);
            case Type::POLYNOMIAL:
                // Parse coefficients from param
                return std::make_unique<PolynomialCalculator>(/* ... */);
        }
    }
};
```

### Component Wiring

```cpp
// Application component
class R410ASolverApp {
private:
    std::unique_ptr<PropertyCalculator> properties_;
    std::unique_ptr<MeshComponent> mesh_;
    std::unique_ptr<FieldComponent> fields_;
    std::unique_ptr<SolverComponent> solver_;
    std::unique_ptr<IOComponent> io_;

public:
    // Constructor: wire components together
    R410ASolverApp(const std::string& config) {
        // Read configuration
        auto cfg = loadConfig(config);

        // Create components based on config
        properties_ = PropertyCalculatorFactory::create(
            cfg.getPropertyType(),
            cfg.getPropertyParameter()
        );

        mesh_ = createMeshComponent(cfg.getMeshType());
        fields_ = createFieldComponent(cfg.getFieldType());
        solver_ = createSolverComponent(cfg.getSolverType());
        io_ = createIOComponent(cfg.getIOType());

        // Initialize all components
        properties_->initialize();
        mesh_->initialize();
        fields_->initialize();
        solver_->initialize();
        io_->initialize();
    }

    void run() {
        // Use components
        auto rho = properties_->calculateDensity(300.0, 1e6);
        auto meshData = mesh_->getCellCenters();
        auto U = fields_->createField("U");
        solver_->solve();
        io_->write("results.vtk");
    }
};
```

---

## Data Flow Architecture

### Data Flow in CFD Simulation

```mermaid
flowchart TD
    A[Input Files<br/>0/, constant/, system/] --> B[Parser<br/>Read & Validate]
    B --> C[Mesh Generator<br/>Create Mesh]
    C --> D[Field Factory<br/>Create Fields]
    D --> E[Property Calculator<br/>Get Properties]
    E --> F[Discretization<br/>Build Matrices]
    F --> G[Linear Solver<br/>Solve System]
    G --> H{Converged?}
    H -->|No| F
    H -->|Yes| I[Result Writer<br/>Output Files]
    I --> J[Visualizer<br/>ParaView]

    classDef input fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef process fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef output fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class A input
    class B,C,D,E,F,G,I,J output
```

### Time Step Data Flow

```mermaid
sequenceDiagram
    participant T as Time
    participant P as Properties
    participant F as Fields
    participant D as Discretization
    participant S as Solver
    participant W as Writer

    T->>T: Increment time
    T->>P: Update properties(T, p)
    P->>P: Calculate ρ, μ, k, cp
    T->>F: Get fields U, p, T
    F->>D: Send to discretization
    D->>D: Build momentum matrix
    D->>D: Build pressure matrix
    D->>S: Send matrices
    S->>S: Solve momentum
    S->>S: Solve pressure
    S->>S: Correct U, p
    S->>F: Update fields
    T->>T: Check convergence
    T->>W: Write if output time
```

### Data Ownership

```mermaid
graph LR
    A[Mesh] -->|owns| B[Cell Centers]
    A -->|owns| C[Face Areas]
    A -->|owns| D[Cell Volumes]

    E[Field Manager] -->|owns| F[Velocity Field]
    E -->|owns| G[Pressure Field]
    E -->|owns| H[Temperature Field]

    I[Solver] -->|references| E
    J[Discretization] -->|references| A
    J -->|references| E

    classDef owner fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef ref fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class A,E owner
    class I,J ref
```

---

## R410A Evaporator Architecture

### System Architecture

```mermaid
graph TB
    subgraph Application["Application Layer"]
        APP[R410A Evaporator App]
    end

    subgraph Physics["Physics Layer"]
        PROP[R410A Property Model]
        PC[Phase Change Model]
        TS[Surface Tension Model]
    end

    subgraph Solver["Solver Layer"]
        VOF[VOF Equation Solver]
        MOM[Momentum Solver]
        PRES[Pressure Solver]
        EN[Energy Solver]
    end

    subgraph Discretization["Discretization Layer"]
        DIV[Convection Schemes]
        GRAD[Gradient Schemes]
        LAP[Laplacian Schemes]
    end

    subgraph Fields["Field Layer"]
        ALPHA[Phase Fraction α]
        U[Velocity U]
        P[Pressure p]
        T[Temperature T]
        RHO[Density ρ]
    end

    subgraph Mesh["Mesh Layer"]
        TUBE[Tube Mesh Generator]
        BOUND[Boundary Manager]
    end

    subgraph Utils["Utilities Layer"]
        COOLPROP[CoolProp Wrapper]
        TABLE[Lookup Tables]
        VTK[VTK Writer]
    end

    APP --> VOF
    APP --> MOM
    APP --> PRES
    APP --> EN

    VOF --> PROP
    VOF --> PC
    MOM --> PROP
    EN --> PROP

    VOF --> DIV
    MOM --> DIV
    MOM --> LAP
    PRES --> GRAD
    PRES --> LAP
    EN --> DIV
    EN --> LAP

    VOF --> ALPHA
    MOM --> U
    PRES --> P
    EN --> T
    PROP --> RHO

    ALPHA --> TUBE
    U --> TUBE
    P --> TUBE

    TUBE --> BOUND

    PROP --> COOLPROP
    PROP --> TABLE
    APP --> VTK

    classDef app fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef phys fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef solver fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef field fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef mesh fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef util fill:#fff9c4,stroke:#f9a825,stroke-width:2px

    class APP app
    class PROP,PC,TS phys
    class VOF,MOM,PRES,EN solver
    class ALPHA,U,P,T,RHO field
    class TUBE,BOUND mesh
    class COOLPROP,TABLE,VTK util
```

### Component Architecture for R410A

```cpp
// === Physics Layer ===

class R410APropertyModel {
public:
    virtual double density(double T, double p, double alpha) const = 0;
    virtual double viscosity(double T, double p, double alpha) const = 0;
    virtual double conductivity(double T, double p, double alpha) const = 0;
    virtual double latentHeat(double T_sat) const = 0;
};

class PhaseChangeModel {
public:
    virtual double evaporationRate(
        const Field& T,
        const Field& alpha,
        double T_sat
    ) const = 0;
};

class SurfaceTensionModel {
public:
    virtual double sigma(double T, double alpha) const = 0;
    virtual vector surfaceForce(
        const Field& alpha,
        const Field& T
    ) const = 0;
};

// === Solver Layer ===

class VOFSolver {
private:
    std::shared_ptr<R410APropertyModel> properties_;
    std::shared_ptr<PhaseChangeModel> phaseChange_;

public:
    void solve(Field& alpha, const Field& U, double dt) {
        // ∂α/∂t + ∇·(αU) = ṁ/ρₗ
        auto mDot = phaseChange_->evaporationRate(T_, alpha_, T_sat_);
        auto rho_l = properties_->density(T_, p_, 1.0);

        fvScalarMatrix alphaEqn(
            fvm::ddt(alpha) + fvm::div(phi, alpha) == mDot / rho_l
        );
        alphaEqn.solve();
    }
};

class MomentumSolver {
private:
    std::shared_ptr<R410APropertyModel> properties_;
    std::shared_ptr<SurfaceTensionModel> surfaceTension_;

public:
    void solve(Field& U, const Field& p, const Field& alpha) {
        // Calculate mixture properties
        auto rho = properties_->density(T_, p_, alpha);
        auto mu = properties_->viscosity(T_, p_, alpha);

        // Build momentum equation
        fvVectorMatrix UEqn(
            fvm::ddt(rho, U) + fvm::div(rhoPhi, U)
            == -fvc::grad(p) + fvm::laplacian(mu, U)
            + surfaceTension_->surfaceForce(alpha, T_)
        );
        UEqn.solve();
    }
};

class EnergySolver {
private:
    std::shared_ptr<R410APropertyModel> properties_;
    std::shared_ptr<PhaseChangeModel> phaseChange_;

public:
    void solve(Field& T, const Field& U, const Field& alpha) {
        auto rho = properties_->density(T_, p_, alpha);
        auto cp = properties_->specificHeat(T_, p_, alpha);
        auto k = properties_->conductivity(T_, p_, alpha);
        auto L = properties_->latentHeat(T_sat);
        auto mDot = phaseChange_->evaporationRate(T_, alpha, T_sat);

        fvScalarMatrix TEqn(
            fvm::ddt(rho*cp, T) + fvm::div(rhoPhi*cp, T)
            == fvm::laplacian(k, T) - mDot * L
        );
        TEqn.solve();
    }
};

// === Application Layer ===

class R410AEvaporatorSimulation {
private:
    // Components
    std::shared_ptr<MeshManager> mesh_;
    std::shared_ptr<FieldManager> fields_;
    std::shared_ptr<R410APropertyModel> properties_;
    std::shared_ptr<PhaseChangeModel> phaseChange_;
    std::shared_ptr<SurfaceTensionModel> surfaceTension_;

    // Solvers
    std::unique_ptr<VOFSolver> vofSolver_;
    std::unique_ptr<MomentumSolver> momentumSolver_;
    std::unique_ptr<PressureSolver> pressureSolver_;
    std::unique_ptr<EnergySolver> energySolver_;

    // Fields
    Field* alpha_;
    Field* U_;
    Field* p_;
    Field* T_;

public:
    void initialize() {
        // Create mesh
        mesh_ = std::make_shared<TubeMeshGenerator>();
        mesh_->generate();

        // Create property model
        properties_ = std::make_shared<CoolPropR410A>();

        // Create physics models
        phaseChange_ = std::make_shared<SimpleEvaporationModel>(lambda);
        surfaceTension_ = std::make_shared<CSFModel>();

        // Create solvers
        vofSolver_ = std::make_unique<VOFSolver>(properties_, phaseChange_);
        momentumSolver_ = std::make_unique<MomentumSolver>(properties_, surfaceTension_);
        pressureSolver_ = std::make_unique<PressureSolver>();
        energySolver_ = std::make_unique<EnergySolver>(properties_, phaseChange_);

        // Create fields
        fields_ = std::make_shared<FieldManager>(mesh_);
        alpha_ = &fields_->createAlphaField();
        U_ = &fields_->createVelocityField();
        p_ = &fields_->createPressureField();
        T_ = &fields_->createTemperatureField();
    }

    void run() {
        while (time_.loop()) {
            // Update properties
            properties_->update(*T_, *p_, *alpha_);

            // Solve VOF equation
            vofSolver_->solve(*alpha_, *U_, time_.deltaT());

            // Solve momentum equation
            momentumSolver_->solve(*U_, *p_, *alpha_);

            // Solve pressure equation
            pressureSolver_->solve(*p_, *U_, *alpha_);

            // Solve energy equation
            energySolver_->solve(*T_, *U_, *alpha_);

            // Write output
            if (time_.outputTime()) {
                writeResults();
            }
        }
    }

private:
    void writeResults() {
        VTKWriter writer;
        writer.write("output_" + time_.timeName() + ".vtk", *mesh_, *fields_);
    }
};
```

### Architecture Diagram for R410A

```mermaid
classDiagram
    class R410AEvaporatorSimulation {
        -shared_ptr~MeshManager~ mesh_
        -shared_ptr~FieldManager~ fields_
        -shared_ptr~R410APropertyModel~ properties_
        -unique_ptr~VOFSolver~ vofSolver_
        -unique_ptr~MomentumSolver~ momentumSolver_
        -unique_ptr~EnergySolver~ energySolver_
        +initialize()
        +run()
        -writeResults()
    }

    class R410APropertyModel {
        <<interface>>
        +density(T, p, alpha)*
        +viscosity(T, p, alpha)*
        +conductivity(T, p, alpha)*
        +latentHeat(T_sat)*
    }

    class PhaseChangeModel {
        <<interface>>
        +evaporationRate(T, alpha, T_sat)*
    }

    class SurfaceTensionModel {
        <<interface>>
        +sigma(T, alpha)*
        +surfaceForce(alpha, T)*
    }

    class VOFSolver {
        -shared_ptr~R410APropertyModel~ properties_
        -shared_ptr~PhaseChangeModel~ phaseChange_
        +solve(alpha, U, dt)
    }

    class MomentumSolver {
        -shared_ptr~R410APropertyModel~ properties_
        -shared_ptr~SurfaceTensionModel~ surfaceTension_
        +solve(U, p, alpha)
    }

    class EnergySolver {
        -shared_ptr~R410APropertyModel~ properties_
        -shared_ptr~PhaseChangeModel~ phaseChange_
        +solve(T, U, alpha)
    }

    R410AEvaporatorSimulation o-- R410APropertyModel
    R410AEvaporatorSimulation o-- PhaseChangeModel
    R410AEvaporatorSimulation o-- SurfaceTensionModel
    R410AEvaporatorSimulation --> VOFSolver
    R410AEvaporatorSimulation --> MomentumSolver
    R410AEvaporatorSimulation --> EnergySolver
    VOFSolver o-- R410APropertyModel
    VOFSolver o-- PhaseChangeModel
    MomentumSolver o-- R410APropertyModel
    MomentumSolver o-- SurfaceTensionModel
    EnergySolver o-- R410APropertyModel
    EnergySolver o-- PhaseChangeModel
```

---

## 📚 Summary (สรุป)

### Architecture Principles

1. **⭐ Layered architecture:** Each layer depends only on layers below
2. **⭐ Separation of concerns:** Each component has single responsibility
3. **⭐ High cohesion, low coupling:** Related functionality together, minimal dependencies
4. **⭐ Interface segregation:** Small, focused interfaces
5. **⭐ Dependency injection:** Pass dependencies, don't create internally

### Layer Responsibilities

| Layer | Responsibility | Example |
|-------|---------------|---------|
| Application | Orchestration | `main()`, time loop |
| Physics | Physical models | Properties, phase change |
| Solver | Solution algorithms | VOF, momentum, pressure |
| Discretization | Numerical schemes | `fvm::div()`, `fvc::grad()` |
| Field | Data storage | `volScalarField`, `volVectorField` |
| Mesh | Geometry | `polyMesh`, boundary patches |
| Utilities | Low-level services | File I/O, MPI |

### R410A Architecture

1. **⭐ Property model:** Abstract interface → CoolProp or lookup tables
2. **⭐ Phase change model:** Pluggable evaporation models
3. **⭐ Solver composition:** VOF + momentum + pressure + energy
4. **⭐ Component wiring:** Dependency injection for flexibility

---

## 🔍 References (อ้างอิง)

| Concept | Reference |
|---------|-----------|
| Layered architecture | OpenFOAM source code organization |
| Separation of concerns | "Clean Architecture" by Robert C. Martin |
| Interface segregation | SOLID principles |
| Component design | "Patterns of Enterprise Application Architecture" |
| OpenFOAM architecture | `src/` directory structure |

---

*Last Updated: 2026-01-28*
