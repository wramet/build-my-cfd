# Solver Design Patterns (Design Patterns สำหรับ Solver)

> **[!INFO]** 📚 Learning Objective
> ประยุกต์ใช้ design patterns (Strategy, Template Method, Factory) ในการออกแบบ solver architecture สำหรับ CFD code ที่ยืดหยุ่นและ reusable กับ R410A evaporator

---

## 📋 Table of Contents (สารบัญ)

1. [Strategy Pattern for Discretization Schemes](#strategy-pattern-for-discretization-schemes-รูปแบบ-strategy-สำหรับ-discretization-schemes)
2. [Template Method for Solution Steps](#template-method-for-solution-steps-รูปแบบ-template-method-สำหรับขั้นตอนการแก้)
3. [Factory Pattern for Boundary Conditions](#factory-pattern-for-boundary-conditions-รูปแบบ-factory-สำหรับ-boundary-conditions)
4. [Observer Pattern for Convergence Monitoring](#observer-pattern-for-convergence-monitoring-รูปแบบ-observer-สำหรับการเฝ้าสังเกตการลู่เข้า)
5. [R410A Solver Pattern Integration](#r410a-solver-pattern-integration-การผสาน-pattern-สำหรับ-solver-r410a)

---

## Strategy Pattern for Discretization Schemes (รูปแบบ Strategy สำหรับ Discretization Schemes)

### What is Strategy Pattern?

**⭐ Definition:** Define a family of algorithms, encapsulate each one, and make them interchangeable

**⭐ Why use for discretization:**
1. **Runtime selection:** Choose scheme without recompiling
2. **Extensibility:** Add new schemes without modifying existing code
3. **Testing:** Test each scheme independently
4. **Configuration:** Select via input files

### Strategy Interface

```cpp
// Abstract strategy for discretization schemes
class IDiscretizationScheme {
public:
    virtual ~IDiscretizationScheme() = default;

    // Discretize divergence term
    virtual fvMatrix discretizeDivergence(
        const Field& field,
        const Field& flux
    ) const = 0;

    // Discretize Laplacian term
    virtual fvMatrix discretizeLaplacian(
        const Field& field,
        const Field& coeff
    ) const = 0;

    // Discretize time derivative
    virtual fvMatrix discretizeTimeDerivative(
        const Field& field,
        double dt
    ) const = 0;

    // Get scheme name
    virtual std::string getName() const = 0;

    // Get scheme order
    virtual int getOrder() const = 0;
};
```

### Concrete Strategies: Divergence Schemes

```cpp
// Upwind scheme: First-order, stable
class UpwindDivergenceScheme : public IDiscretizationScheme {
public:
    fvMatrix discretizeDivergence(
        const Field& field,
        const Field& flux
    ) const override {
        // Upwind: φ_f = φ_upwind
        // Stable but diffusive (first-order)

        fvMatrix matrix(field.size());

        for (size_t faceId = 0; faceId < mesh.numFaces(); ++faceId) {
            size_t owner = mesh.getFaceOwner(faceId);
            size_t neighbour = mesh.getFaceNeighbour(faceId);

            double flux_f = flux[faceId];
            double phi_owner = field[owner];

            // Determine upwind value
            double phi_upwind;
            if (flux_f > 0) {
                phi_upwind = phi_owner;
            } else if (neighbour != SIZE_MAX) {
                phi_upwind = field[neighbour];
            } else {
                // Boundary face
                phi_upwind = phi_owner;
            }

            // Add to matrix
            double contribution = flux_f * phi_upwind;
            matrix.add(owner, owner, contribution);
        }

        return matrix;
    }

    fvMatrix discretizeLaplacian(
        const Field& field,
        const Field& coeff
    ) const override {
        // Default: central difference for Laplacian
        return CentralDifferenceLaplacianScheme().discretizeLaplacian(field, coeff);
    }

    fvMatrix discretizeTimeDerivative(
        const Field& field,
        double dt
    ) const override {
        // Euler scheme
        return EulerTimeScheme().discretizeTimeDerivative(field, dt);
    }

    std::string getName() const override {
        return "upwind";
    }

    int getOrder() const override {
        return 1;
    }
};

// Central difference scheme: Second-order, unstable for high Re
class CentralDifferenceDivergenceScheme : public IDiscretizationScheme {
public:
    fvMatrix discretizeDivergence(
        const Field& field,
        const Field& flux
    ) const override {
        // Central: φ_f = (φ_owner + φ_neighbour) / 2
        // Accurate but may cause oscillations (second-order)

        fvMatrix matrix(field.size());

        for (size_t faceId = 0; faceId < mesh.numFaces(); ++faceId) {
            size_t owner = mesh.getFaceOwner(faceId);
            size_t neighbour = mesh.getFaceNeighbour(faceId);

            double flux_f = flux[faceId];
            double phi_owner = field[owner];
            double phi_neighbour = (neighbour != SIZE_MAX) ?
                                   field[neighbour] : phi_owner;

            // Interpolate to face
            double phi_face = 0.5 * (phi_owner + phi_neighbour);

            // Add to matrix
            double contribution = flux_f * phi_face;
            matrix.add(owner, owner, contribution);

            if (neighbour != SIZE_MAX) {
                matrix.add(neighbour, neighbour, -contribution);
            }
        }

        return matrix;
    }

    std::string getName() const override {
        return "centralDifference";
    }

    int getOrder() const override {
        return 2;
    }
};

// QUICK scheme: Quadratic Upwind Interpolation (third-order)
class QUICKDivergenceScheme : public IDiscretizationScheme {
public:
    fvMatrix discretizeDivergence(
        const Field& field,
        const Field& flux
    ) const override {
        // QUICK: Uses two upstream points for third-order accuracy
        // φ_f = 6/8 φ_upwind + 3/8 φ_downwind - 1/8 φ_far_upwind

        fvMatrix matrix(field.size());

        for (size_t faceId = 0; faceId < mesh.numFaces(); ++faceId) {
            size_t owner = mesh.getFaceOwner(faceId);
            size_t neighbour = mesh.getFaceNeighbour(faceId);

            double flux_f = flux[faceId];

            // Determine upwind direction
            size_t upwind, downwind, farUpwind;
            if (flux_f > 0) {
                upwind = owner;
                downwind = (neighbour != SIZE_MAX) ? neighbour : owner;
                farUpwind = getUpwindUpwind(owner);  // Cell further upstream
            } else {
                upwind = (neighbour != SIZE_MAX) ? neighbour : owner;
                downwind = owner;
                farUpwind = getUpwindUpwind(upwind);
            }

            double phi_upwind = field[upwind];
            double phi_downwind = field[downwind];
            double phi_far_upwind = field[farUpwind];

            // QUICK interpolation
            double phi_face = (6.0/8.0) * phi_upwind +
                            (3.0/8.0) * phi_downwind -
                            (1.0/8.0) * phi_far_upwind;

            // Add to matrix
            double contribution = flux_f * phi_face;
            matrix.add(upwind, upwind, contribution);
        }

        return matrix;
    }

    std::string getName() const override {
        return "QUICK";
    }

    int getOrder() const override {
        return 3;
    }

private:
    size_t getUpwindUpwind(size_t cellId) const {
        // Find the cell further upstream
        // This requires mesh connectivity
        // Simplified implementation
        auto neighbors = mesh.getCellNeighbors(cellId);
        return neighbors.empty() ? cellId : neighbors[0];
    }
};
```

### Context Class

```cpp
// Context: Uses strategy to discretize equations
class DiscretizationContext {
private:
    std::shared_ptr<IDiscretizationScheme> divergenceScheme_;
    std::shared_ptr<IDiscretizationScheme> laplacianScheme_;
    std::shared_ptr<IDiscretizationScheme> timeScheme_;
    std::shared_ptr<IMesh> mesh_;

public:
    DiscretizationContext(std::shared_ptr<IMesh> mesh)
        : mesh_(mesh) {}

    // Set schemes
    void setDivergenceScheme(std::shared_ptr<IDiscretizationScheme> scheme) {
        divergenceScheme_ = scheme;
    }

    void setLaplacianScheme(std::shared_ptr<IDiscretizationScheme> scheme) {
        laplacianScheme_ = scheme;
    }

    void setTimeScheme(std::shared_ptr<IDiscretizationScheme> scheme) {
        timeScheme_ = scheme;
    }

    // Use schemes to discretize momentum equation
    fvVectorMatrix discretizeMomentum(
        const volVectorField& U,
        const surfaceScalarField& phi,
        double nu,
        double dt
    ) {
        fvVectorMatrix UEqn(U.size());

        // Divergence term: ∇·(UU)
        if (divergenceScheme_) {
            UEqn += divergenceScheme_->discretizeDivergence(U, phi);
        }

        // Laplacian term: ν∇²U
        if (laplacianScheme_) {
            UEqn += laplacianScheme_->discretizeLaplacian(U, nu);
        }

        // Time derivative: ∂U/∂t
        if (timeScheme_) {
            UEqn += timeScheme_->discretizeTimeDerivative(U, dt);
        }

        return UEqn;
    }

    // Get current scheme information
    void printSchemeInfo() const {
        std::cout << "Current discretization schemes:\n";
        if (divergenceScheme_) {
            std::cout << "  Divergence: " << divergenceScheme_->getName()
                      << " (order: " << divergenceScheme_->getOrder() << ")\n";
        }
        if (laplacianScheme_) {
            std::cout << "  Laplacian: " << laplacianScheme_->getName()
                      << " (order: " << laplacianScheme_->getOrder() << ")\n";
        }
        if (timeScheme_) {
            std::cout << "  Time: " << timeScheme_->getName()
                      << " (order: " << timeScheme_->getOrder() << ")\n";
        }
    }
};
```

### Scheme Factory

```cpp
// Factory to create discretization schemes
class DiscretizationSchemeFactory {
public:
    static std::shared_ptr<IDiscretizationScheme> createDivergenceScheme(
        const std::string& name
    ) {
        if (name == "upwind" || name == "Gauss upwind") {
            return std::make_shared<UpwindDivergenceScheme>();
        } else if (name == "central" || name == "Gauss linear") {
            return std::make_shared<CentralDifferenceDivergenceScheme>();
        } else if (name == "QUICK") {
            return std::make_shared<QUICKDivergenceScheme>();
        } else {
            throw std::invalid_argument("Unknown divergence scheme: " + name);
        }
    }

    static std::shared_ptr<IDiscretizationScheme> createLaplacianScheme(
        const std::string& name
    ) {
        if (name == "linear" || name == "Gauss linear") {
            return std::make_shared<CentralDifferenceLaplacianScheme>();
        } else {
            throw std::invalid_argument("Unknown Laplacian scheme: " + name);
        }
    }

    static std::shared_ptr<IDiscretizationScheme> createTimeScheme(
        const std::string& name
    ) {
        if (name == "Euler" || name == "backward") {
            return std::make_shared<EulerTimeScheme>();
        } else if (name == "CrankNicolson") {
            return std::make_shared<CrankNicolsonTimeScheme>();
        } else {
            throw std::invalid_argument("Unknown time scheme: " + name);
        }
    }
};
```

---

## Template Method for Solution Steps (รูปแบบ Template Method สำหรับขั้นตอนการแก้)

### What is Template Method Pattern?

**⭐ Definition:** Define skeleton of algorithm, let subclasses override specific steps

**⭐ Why use for solvers:**
1. **Consistent structure:** All solvers follow same algorithm
2. **Customizable steps:** Each solver customizes specific parts
3. **Code reuse:** Common steps in base class
4. **Clear flow:** Easy to understand algorithm structure

### Template Method for Solver Algorithm

```cpp
// Abstract base class with template method
class SolverTemplate {
public:
    // Template method: defines algorithm structure
    void solve() {
        // Step 1: Initialize
        initialize();

        // Step 2: Main loop
        while (!isConverged() && !isFinished()) {
            // Step 2a: Pre-solve
            preSolve();

            // Step 2b: Solve momentum
            solveMomentum();

            // Step 2c: Solve pressure
            solvePressure();

            // Step 2d: Correct velocity
            correctVelocity();

            // Step 2e: Solve additional equations
            solveAdditionalEquations();

            // Step 2f: Update boundary conditions
            updateBoundaryConditions();

            // Step 2g: Check convergence
            checkConvergence();

            // Step 2h: Post-solve
            postSolve();

            // Step 2i: Advance time (for transient)
            if (isTransient()) {
                advanceTime();
            }
        }

        // Step 3: Finalize
        finalize();
    }

    // Default implementations (can be overridden)
    virtual void preSolve() {
        // Default: do nothing
    }

    virtual void postSolve() {
        // Default: write statistics
        writeStatistics();
    }

    virtual void solveAdditionalEquations() {
        // Default: no additional equations
    }

    virtual void writeStatistics() {
        std::cout << "Iteration: " << currentIteration_
                  << ", Residual: " << residual_ << "\n";
    }

protected:
    // Pure virtual: must be implemented by derived classes
    virtual void initialize() = 0;
    virtual void solveMomentum() = 0;
    virtual void solvePressure() = 0;
    virtual void correctVelocity() = 0;
    virtual void updateBoundaryConditions() = 0;
    virtual void checkConvergence() = 0;
    virtual void finalize() = 0;

    // Hooks for transient solvers
    virtual bool isTransient() const {
        return false;  // Default: steady-state
    }

    virtual void advanceTime() {
        // Default: do nothing
    }

    virtual bool isFinished() const {
        return false;  // Default: not finished
    }

    // State variables
    int currentIteration_;
    double residual_;
    bool converged_;

    std::shared_ptr<IMesh> mesh_;
    std::shared_ptr<FieldManager> fields_;
};
```

### Concrete Implementation: SIMPLE Solver

```cpp
// SIMPLE solver using template method
class SIMPLESolver : public SolverTemplate {
public:
    SIMPLESolver(std::shared_ptr<IMesh> mesh) {
        mesh_ = mesh;
        fields_ = std::make_shared<FieldManager>(mesh);
    }

protected:
    void initialize() override {
        // Read initial fields
        fields_->readFields(0.0);

        // Initialize solver parameters
        currentIteration_ = 0;
        residual_ = 1.0;
        converged_ = false;

        // Set under-relaxation factors
        momentumRelaxation_ = 0.7;
        pressureRelaxation_ = 0.3;
    }

    void solveMomentum() override {
        auto& U = fields_->getVelocityField();
        auto& phi = fields_->getFluxField();

        // Build momentum equation
        UEqn_ = fvVectorMatrix(
            fvm::div(phi, U) + fvm::laplacian(nu, U)
        );

        // Under-relax
        UEqn_.relax(momentumRelaxation_);

        // Solve (without pressure gradient)
        UEqn_.solve();
    }

    void solvePressure() override {
        auto& U = fields_->getVelocityField();
        auto& p = fields_->getPressureField();
        auto& phi = fields_->getFluxField();

        // Calculate rUA
        rUA_ = 1.0 / UEqn_.A();

        // Predict velocity
        U = rUA_ * UEqn_.H();

        // Calculate flux
        phi = fvc::interpolate(U) & mesh_->Sf();

        // Adjust flux
        adjustPhi(phi, U, p);

        // Pressure equation
        pEqn_ = fvScalarMatrix(
            fvm::laplacian(rUA_, p) == fvc::div(phi)
        );

        pEqn_.setReference(pRefCell_, pRefValue_);
        pEqn_.solve();
    }

    void correctVelocity() override {
        auto& U = fields_->getVelocityField();
        auto& p = fields_->getPressureField();

        // Correct velocity
        U -= rUA_ * fvc::grad(p);
        U.correctBoundaryConditions();
    }

    void updateBoundaryConditions() override {
        auto& U = fields_->getVelocityField();
        auto& p = fields_->getPressureField();

        U.correctBoundaryConditions();
        p.correctBoundaryConditions();
    }

    void checkConvergence() override {
        // Get residual from pressure solver
        residual_ = pEqn_.solverPerformance().initialResidual();
        converged_ = (residual_ < convergenceTolerance_);

        currentIteration_++;
    }

    void finalize() override {
        // Write final fields
        fields_->writeFields(currentIteration_);
    }

    // SIMPLE-specific: no additional equations
    void solveAdditionalEquations() override {
        // Do nothing
    }

private:
    fvVectorMatrix UEqn_;
    fvScalarMatrix pEqn_;
    volScalarField rUA_;

    double momentumRelaxation_;
    double pressureRelaxation_;
    double convergenceTolerance_ = 1e-6;

    size_t pRefCell_ = 0;
    double pRefValue_ = 0.0;
    double nu = 0.01;
};
```

### Concrete Implementation: R410A Solver

```cpp
// R410A solver: adds energy and phase change equations
class R410ASolver : public SolverTemplate {
public:
    R410ASolver(
        std::shared_ptr<IMesh> mesh,
        std::shared_ptr<R410APropertyModel> properties
    ) : properties_(properties) {
        mesh_ = mesh;
        fields_ = std::make_shared<FieldManager>(mesh);
    }

protected:
    void initialize() override {
        SIMPLESolver::initialize();

        // Create additional fields
        fields_->createScalarField("T");      // Temperature
        fields_->createScalarField("alpha");  // Phase fraction
    }

    void solveAdditionalEquations() override {
        // Solve energy equation
        solveEnergy();

        // Solve VOF equation (with phase change)
        solveVOF();

        // Update properties
        updateProperties();
    }

    void postSolve() override {
        SolverTemplate::postSolve();

        // Additional R410A statistics
        printR410AStatistics();
    }

private:
    void solveEnergy() {
        auto& T = fields_->getTemperatureField();
        auto& U = fields_->getVelocityField();
        auto& alpha = fields_->getPhaseFractionField();
        auto& p = fields_->getPressureField();

        // Get temperature-dependent properties
        volScalarField rho = properties_->density(T, p, alpha);
        volScalarField cp = properties_->specificHeat(T, p, alpha);
        volScalarField k = properties_->thermalConductivity(T, p, alpha);

        // Energy equation
        fvScalarMatrix TEqn(
            fvm::ddt(rho * cp, T)
          + fvm::div(rhoPhi * cp, T)
          - fvm::laplacian(k, T)
        );

        // Add phase change source term
        if (solvePhaseChange_) {
            volScalarField mDot = calculateMassTransferRate();
            TEqn -= mDot * latentHeat_;
        }

        TEqn.solve();
    }

    void solveVOF() {
        auto& alpha = fields_->getPhaseFractionField();
        auto& U = fields_->getVelocityField();

        // VOF equation
        fvScalarMatrix alphaEqn(
            fvm::ddt(alpha) + fvm::div(phi, alpha)
        );

        // Add phase change source term
        if (solvePhaseChange_) {
            volScalarField mDot = calculateMassTransferRate();
            alphaEqn -= mDot / rho_l;
        }

        alphaEqn.solve();

        // Clip to [0, 1]
        clipPhaseFraction(alpha);
    }

    void updateProperties() {
        auto& T = fields_->getTemperatureField();
        auto& p = fields_->getPressureField();
        auto& alpha = fields_->getPhaseFractionField();

        // Update all properties based on current T, p, alpha
        for (size_t cellId = 0; cellId < mesh_->numCells(); ++cellId) {
            double T_local = T[cellId];
            double p_local = p[cellId];
            double alpha_local = alpha[cellId];

            rho_[cellId] = properties_->density(T_local, p_local, alpha_local);
            mu_[cellId] = properties_->viscosity(T_local, p_local, alpha_local);
        }
    }

    void printR410AStatistics() {
        auto& T = fields_->getTemperatureField();
        auto& alpha = fields_->getPhaseFractionField();

        double T_avg = T.average();
        double alpha_avg = alpha.average();
        double vaporFraction = 1.0 - alpha_avg;

        std::cout << "R410A Statistics:\n";
        std::cout << "  Average temperature: " << T_avg << " K\n";
        std::cout << "  Liquid volume fraction: " << alpha_avg << "\n";
        std::cout << "  Vapor volume fraction: " << vaporFraction << "\n";
    }

    std::shared_ptr<R410APropertyModel> properties_;
    volScalarField rho_;
    volScalarField mu_;
    double latentHeat_ = 200000.0;
    double rho_l = 1000.0;
    bool solvePhaseChange_ = true;
};
```

---

## Factory Pattern for Boundary Conditions (รูปแบบ Factory สำหรับ Boundary Conditions)

### Boundary Condition Factory

```cpp
// Abstract boundary condition
class IBoundaryCondition {
public:
    virtual ~IBoundaryCondition() = default;

    virtual void apply(Field& field) const = 0;
    virtual std::string getName() const = 0;
    virtual bool isFixedValue() const = 0;
};

// Fixed value BC
class FixedValueBC : public IBoundaryCondition {
private:
    double value_;

public:
    FixedValueBC(double value) : value_(value) {}

    void apply(Field& field) const override {
        for (size_t faceId : boundaryFaces_) {
            // Set boundary face values
            field.setBoundaryValue(faceId, value_);
        }
    }

    std::string getName() const override {
        return "fixedValue";
    }

    bool isFixedValue() const override {
        return true;
    }

private:
    std::vector<size_t> boundaryFaces_;
};

// Zero gradient BC
class ZeroGradientBC : public IBoundaryCondition {
public:
    void apply(Field& field) const override {
        for (size_t faceId : boundaryFaces_) {
            // Set boundary face value equal to owner cell value
            size_t owner = mesh.getFaceOwner(faceId);
            double ownerValue = field[owner];
            field.setBoundaryValue(faceId, ownerValue);
        }
    }

    std::string getName() const override {
        return "zeroGradient";
    }

    bool isFixedValue() const override {
        return false;
    }

private:
    std::vector<size_t> boundaryFaces_;
};

// Factory
class BoundaryConditionFactory {
public:
    static std::unique_ptr<IBoundaryCondition> createBC(
        const std::string& type,
        double value = 0.0
    ) {
        if (type == "fixedValue") {
            return std::make_unique<FixedValueBC>(value);
        } else if (type == "zeroGradient") {
            return std::make_unique<ZeroGradientBC>();
        } else {
            throw std::invalid_argument("Unknown BC type: " + type);
        }
    }
};
```

---

## Observer Pattern for Convergence Monitoring (รูปแบบ Observer สำหรับการเฝ้าสังเกตการลู่เข้า)

### Observer Interface

```cpp
// Observer interface
class IConvergenceObserver {
public:
    virtual ~IConvergenceObserver() = default;

    virtual void onIterationStart(int iteration, double residual) = 0;
    virtual void onIterationEnd(int iteration, double residual) = 0;
    virtual void onConverged(int iteration, double residual) = 0;
};

// Subject (solver)
class ConvergenceSubject {
private:
    std::vector<std::shared_ptr<IConvergenceObserver>> observers_;

public:
    void attachObserver(std::shared_ptr<IConvergenceObserver> observer) {
        observers_.push_back(observer);
    }

    void notifyIterationStart(int iteration, double residual) {
        for (auto& observer : observers_) {
            observer->onIterationStart(iteration, residual);
        }
    }

    void notifyIterationEnd(int iteration, double residual) {
        for (auto& observer : observers_) {
            observer->onIterationEnd(iteration, residual);
        }
    }

    void notifyConverged(int iteration, double residual) {
        for (auto& observer : observers_) {
            observer->onConverged(iteration, residual);
        }
    }
};

// Concrete observer: Console logger
class ConsoleConvergenceLogger : public IConvergenceObserver {
public:
    void onIterationStart(int iteration, double residual) override {
        std::cout << "Iteration " << iteration << " started\n";
    }

    void onIterationEnd(int iteration, double residual) override {
        std::cout << "Iteration " << iteration
                  << ", Residual = " << residual << "\n";
    }

    void onConverged(int iteration, double residual) override {
        std::cout << "Converged at iteration " << iteration
                  << ", Residual = " << residual << "\n";
    }
};

// Concrete observer: File logger
class FileConvergenceLogger : public IConvergenceObserver {
private:
    std::ofstream logFile_;

public:
    FileConvergenceLogger(const std::string& filename) {
        logFile_.open(filename);
        logFile_ << "Iteration,Residual\n";
    }

    ~FileConvergenceLogger() {
        logFile_.close();
    }

    void onIterationEnd(int iteration, double residual) override {
        logFile_ << iteration << "," << residual << "\n";
        logFile_.flush();
    }

    // ... other methods
};
```

---

## R410A Solver Pattern Integration (การผสาน Pattern สำหรับ Solver R410A)

### Complete R410A Solver with All Patterns

```cpp
// R410A solver using multiple design patterns
class R410ASolverIntegrated : public SolverTemplate {
private:
    // Strategy: discretization schemes
    std::shared_ptr<IDiscretizationScheme> divergenceScheme_;
    std::shared_ptr<IDiscretizationScheme> laplacianScheme_;

    // Factory: boundary conditions
    BoundaryConditionFactory bcFactory_;

    // Observer: convergence monitoring
    ConvergenceSubject convergenceSubject_;

    // Components
    std::shared_ptr<R410APropertyModel> properties_;
    std::shared_ptr<PhaseChangeModel> phaseChange_;

public:
    R410ASolverIntegrated(
        std::shared_ptr<IMesh> mesh,
        std::shared_ptr<R410APropertyModel> properties,
        const SolverConfig& config
    ) : properties_(properties) {
        mesh_ = mesh;
        fields_ = std::make_shared<FieldManager>(mesh);

        // Create discretization schemes (Strategy pattern)
        divergenceScheme_ = DiscretizationSchemeFactory::createDivergenceScheme(
            config.divergenceScheme
        );
        laplacianScheme_ = DiscretizationSchemeFactory::createLaplacianScheme(
            config.laplacianScheme
        );

        // Attach convergence observers (Observer pattern)
        convergenceSubject_.attachObserver(
            std::make_shared<ConsoleConvergenceLogger>()
        );
        convergenceSubject_.attachObserver(
            std::make_shared<FileConvergenceLogger>("convergence.csv")
        );
    }

protected:
    void solveMomentum() override {
        convergenceSubject_.notifyIterationStart(currentIteration_, residual_);

        auto& U = fields_->getVelocityField();
        auto& phi = fields_->getFluxField();

        // Use strategy for discretization
        fvVectorMatrix UEqn(
            divergenceScheme_->discretizeDivergence(U, phi)
          + laplacianScheme_->discretizeLaplacian(U, nu)
        );

        UEqn.relax(momentumRelaxation_);
        UEqn.solve();

        convergenceSubject_.notifyIterationEnd(currentIteration_, residual_);
    }

    void updateBoundaryConditions() override {
        auto& U = fields_->getVelocityField();
        auto& p = fields_->getPressureField();
        auto& T = fields_->getTemperatureField();

        // Use factory to create BCs
        auto inletBC = bcFactory_.createBC("fixedValue", 0.1);  // 0.1 m/s
        auto wallBC = bcFactory_.createBC("zeroGradient");

        // Apply BCs
        inletBC->apply(U);
        wallBC->apply(U);
        wallBC->apply(T);  // Zero gradient for T at wall
    }

    void checkConvergence() override {
        residual_ = calculateResidual();

        if (residual_ < convergenceTolerance_) {
            converged_ = true;
            convergenceSubject_.notifyConverged(currentIteration_, residual_);
        }

        currentIteration_++;
    }

    void solveAdditionalEquations() override {
        // Template method hook: solve energy and VOF
        solveEnergy();
        solveVOF();
        updateProperties();
    }

private:
    void solveEnergy() {
        auto& T = fields_->getTemperatureField();
        auto& U = fields_->getVelocityField();
        auto& alpha = fields_->getPhaseFractionField();

        // Get properties
        volScalarField rho = properties_->density(T, p, alpha);
        volScalarField k = properties_->thermalConductivity(T, p, alpha);

        // Energy equation with strategy-based discretization
        fvScalarMatrix TEqn(
            divergenceScheme_->discretizeDivergence(T, U)
          + laplacianScheme_->discretizeLaplacian(T, k)
        );

        // Add phase change source
        volScalarField mDot = phaseChange_->evaporationRate(T, alpha, T_sat);
        TEqn -= mDot * latentHeat_;

        TEqn.solve();
    }
};
```

---

## 📚 Summary (สรุป)

### Design Patterns Summary

| Pattern | Purpose | CFD Application |
|---------|---------|-----------------|
| **Strategy** | Encapsulate algorithms | Discretization schemes |
| **Template Method** | Algorithm skeleton | Solver solution steps |
| **Factory** | Create objects without specifying class | Boundary conditions |
| **Observer** | Notify subscribers of events | Convergence monitoring |

### Key Benefits

1. **⭐ Flexibility:** Change schemes without modifying solver
2. **⭐ Reusability:** Common code in base classes
3. **⭐ Extensibility:** Add new schemes/solvers easily
4. **⭐ Testability:** Test components independently
5. **⭐ Configuration:** Select algorithms via input files

### R410A Integration

1. **⭐ Strategy:** Different discretization for two-phase flow
2. **⭐ Template Method:** Consistent algorithm structure
3. **⭐ Factory:** Create R410A-specific boundary conditions
4. **⭐ Observer:** Monitor phase change convergence

---

## 🔍 References (อ้างอิง)

| Topic | Reference |
|-------|-----------|
| Strategy pattern | Gang of Four, "Design Patterns" (1994) |
| Template method | Gang of Four, "Design Patterns" (1994) |
| Observer pattern | Gang of Four, "Design Patterns" (1994) |
| Discretization schemes | OpenFOAM Programmer's Guide |
| SIMPLE algorithm | Patankar, "Numerical Heat Transfer" (1980) |

---

*Last Updated: 2026-01-28*
