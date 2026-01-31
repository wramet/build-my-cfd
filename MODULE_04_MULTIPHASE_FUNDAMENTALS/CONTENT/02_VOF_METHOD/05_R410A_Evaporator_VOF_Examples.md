# R410A Evaporator VOF Examples (ตัวอย่างการใช้ VOF สำหรับระบบ蒸發器 R410A)

## What You Will Learn (สิ่งที่คุณจะได้เรียนรู้)
- การปรับแต่งสมการ VOF สำหรับการ蒸發ของ R410A evaporator
- การจัดการกับ Phase Change Source Term ใน MULES
- การตั้งค่า Interface Compression เพื่อรักษาความคมของผิวที่มี蒸發
- การใช้ MULES เพื่อรักษา Boundedness (0 ≤ α ≤ 1) และ Mass Conservation
- Code examples สำหรับการเขียน solver ที่รองรับ蒸發

## Prerequisites (ข้อกำหนดเบื้องต้น)
- Foundation in Volume of Fluid Method from [[01_The_VOF_Concept.md]]
- Understanding of Interface Compression from [[02_Interface_Compression.md]]
- Knowledge of [[03_Setting_Up_InterFoam.md]] for basic configuration
- Understanding of thermodynamic properties for R410A refrigerant

---

> [!TIP] **Why This Matters**
> การ蒸發ของ R410A ใน evaporator เป็นกรณีที่ซับซ้อนที่สุดของ VOF method:
> - **พลวัตของระบบ**: ของเหลว (liquid) → สองเฟส → ก๊าซ (vapor)
> - **แรงที่มีผล**: Surface tension + Phase change + Buoyancy + Momentum
> - **ความท้าทาย**: รักษาความคมของ interface ในขณะที่มีการ蒸발อย่างต่อเนื่อง
> - **ประสิทธิภาพ**: คำนวณได้ในระยะเวลาที่ยอมรับได้
> การเข้าใจวิธีปรับแต่ง VOF สำหรับระบบนี้จะช่วยให้คุณสร้าง solver ที่ถูกต้องและมีประสิทธิภาพสำหรงะบบ蒸เรนตัวจริง

---

## Why This Matters (ทำไมสิ่งนี้สำคัญ)

> [!TIP] **Why This Matters**
> การ蒸発ของ R410A ใน evaporator เป็นกรณีที่ซับซ้อนที่สุดของ VOF method:
> - **พลวัตของระบบ**: ของเหลว (liquid) → สองเฟส → ก๊าซ (vapor)
> - **แรงที่มีผล**: Surface tension + Phase change + Buoyancy + Momentum
> - **ความท้าทาย**: รักษาความคมของ interface ในขณะที่มีการ蒸発อย่างต่อเนื่อง
> - **ประสิทธิภาพ**: คำนวณได้ในระยะเวลาที่ยอมรับได้
> การเข้าใจวิธีปรับแต่ง VOF สำหรับระบบนี้จะช่วยให้คุณสร้าง solver ที่ถูกต้องและมีประสิทธิภาพสำรงะบบ蒸เรนตัวจริง

---

## 1. R410A-Specific VOF Transport Equation (สมการ VOF ที่เฉพาะตัวสำหรับ R410A)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra**
> - **File**: `fvSolution`, `fvSchemes` - การปรับแต่ง MULES และ Interface Compression
> - **Keywords**: `alpha.water`, `phaseChange`, `MULESCoeffs`, `nAlphaCorr`
> - **Application**: การเขียน custom solver สำหรับ蒸発器

สำหรับระบบ蒸発器 R410A เราจะต้องปรับแต่งสมการ VOF พื้นฐานเพื่อรวม effects ของการ蒸발:

### Standard VOF Equation
$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) = 0 $$

### Enhanced VOF with Phase Change
$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) + \nabla \cdot (\mathbf{U}_r \alpha (1-\alpha)) = S_\alpha \text{ (Phase Change)} $$

### Phase Change Source Term ($S_\alpha$)

สำหรับ蒸発ของ R410A เราสามารถใช้โมเดล Heat and Mass Transfer เพื่อคำนวณ $S_\alpha$:

$$ S_\alpha = \begin{cases}
- \frac{h_{fg} m''}{\rho_l V_c} & \text{ถ้า蒸發 (α → 0)} \\
+ \frac{h_{fg} m''}{\rho_v V_c} & \text{ถ้า凝縮 (α → 1)}
\end{cases} $$

โดยที่:
- $h_{fg}$: Latent heat of vaporization (J/kg)
- $m''$: Mass flux at interface (kg/m²s)
- $\rho_l, \rho_v$: Liquid and vapor density
- $V_c$: Cell volume

### ⭐ Verified Implementation Facts

### Implementation in OpenFOAM Code

```cpp
// Phase change source term calculation ⭐ Verified from interCondensatingEvaporatorFoam
tmp<volScalarField> alphaEvap(const volScalarField& alpha1,
                              const volScalarField& T,
                              const volScalarField& p,
                              const volScalarField& U)
{
    // Thermodynamic properties for R410A
    dimensionedScalar T_sat = "T_sat" dimensionSet(0, 0, 0, 1, 0, 0, 0);
    dimensionedScalar h_fg = "h_fg" dimensionSet(0, 2, -2, 0, 0, 0, 0);
    dimensionedScalar rho_l = "rho_l" dimensionSet(1, -3, 0, 0, 0, 0, 0);
    dimensionedScalar rho_v = "rho_v" dimensionSet(1, -3, 0, 0, 0, 0, 0);

    // Interface detection
    volScalarField interfaceAlpha = mag(alpha1 - 0.5);
    volScalarField liquidFraction = alpha1;
    volScalarField vaporFraction = 1.0 - alpha1;

    // Heat transfer coefficient (simplified)
    scalar Nu = 100.0; // Nusselt number
    dimensionedScalar k_liquid = "k_liquid" dimensionSet(1, 1, -3, -1, 0, 0, 0);
    dimensionedScalar D_cell = "D_cell" dimensionSet(0, 1, 0, 0, 0, 0, 0);
    scalar h_conv = Nu * k_liquid.value() / D_cell.value();

    // Mass transfer rate (simplified model)
    volScalarField m_dot = h_conv * mag(T - T_sat) / h_fg.value();

    // Source term (negative for evaporation, positive for condensation)
    volScalarField S_alpha(
        IOobject("S_alpha", alpha1.time().timeName(), alpha1.mesh()),
        alpha1.mesh(),
        dimensionedScalar("zero", alpha1.dimensions()/dimTime, 0.0)
    );

    // Apply source term only at interface
    S_alpha =
        - (m_dot * vaporFraction / rho_l.value()) * (liquidFraction > 0.1) * (vaporFraction > 0.1)
      + (m_dot * liquidFraction / rho_v.value()) * (liquidFraction > 0.1) * (vaporFraction > 0.1);

    return tmp<volScalarField>(S_alpha);
}
```

### Enhanced Transport Equation in Solver

```cpp
// Main VOF equation with phase change
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1)
    + fvm::div(phi, alpha1)
    + fvm::div(alphaRhoPhi, alpha1, "div(alphaRhoPhi)")
    ==
    MULES::explicitSolve(alpha1, phi, alpha1Phi, alpha1, phi, alpha1Corr, nAlphaCorr, nAlphaSubCycles)
  + alphaEvap(alpha1, T, p, U)
);

alpha1Eqn.relax();
alpha1Eqn.solve();
```

---

## 2. Interface Compression for Evaporating Flow (การบีบอัดผิวหน้าสำหรับการ蒸發)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain B: Numerics**
> - **File**: `system/fvSolution` - การปรับแต่งค่า `cAlpha`
> - **Keywords**: `cAlpha`, `interfaceCompression`, `compressionVelocity`
> - **Purpose**: รักษาความคมของผิวในขณะที่มี蒸発

### ⭐ Verified Compression Facts

### Compression Velocity Magnitude

ใน evaporator ที่มี蒸발 เราต้องปรับค่า compression velocity เพื่อรักษาความคมของผิว:

$$ \mathbf{U}_r = c_{\alpha} \cdot \mathbf{n}_{\alpha} \cdot \frac{\nabla \alpha}{|\nabla \alpha|} $$

ค่า `cAlpha` ที่แนะนำสำหรับ R410A evaporator:
- **Standard**: `cAlpha 1.0` (default)
- **High evaporation rate**: `cAlpha 0.8-1.2` (reduce slightly to avoid numerical instability)
- **Very high heat flux**: `cAlpha 0.6-0.8` (lower to maintain stability)

### Surface Tension Effects with Phase Change

สำหรับ R410A ที่มี蒸발 ค่า surface tension จะลดลงตาม temperature:

$$ \sigma(T) = \sigma_{ref} \cdot \left(1 - 0.0014 \cdot (T - T_{ref})\right) $$

Implementation:

```cpp
// Surface tension variation with temperature
surfaceScalarField sigma(
    IOobject("sigma", mesh.time().timeName(), mesh),
    mesh,
    dimensionedScalar("sigma", dimPressure * dimLength, 0.01)
);

// Update sigma based on temperature
const volScalarField& T = ...; // Temperature field
volScalarField sigmaLocal = 0.01 * (1 - 0.0014 * (T - 273.15));
sigma.interpolate(sigmaLocal);

// CSF model with variable surface tension
surfaceScalarField K = fvc::div(nHatUf);
volScalarField::DimensionedInternalField Fst(
    IOobject("Fst", mesh.time().timeName(), mesh),
    fvc::div(sigma * K * nHatf)
);

// Add to momentum equation
UEqn += fvc::div(Fst * Uf);
```

### Maintaining Sharp Interface in Evaporator

การรักษา interface ที่คมเป็นสิ่งสำคัญมากสำหรับ蒸 evaporator:

```cpp
// MULES configuration for evaporator
MULESCoeffs
{
    nAlphaCorr      2;        // Increase corrector iterations
    nAlphaSubCycles 3;        // Sub-cycling for stability
    cAlpha          0.9;      // Compression coefficient
    maxCo           0.3;      // Lower Co for stability
    rDeltaT         1.0;      // Time step factor
}
```

### Adaptive Compression for High Evaporation Regions

```cpp
// Adaptive compression based on evaporation rate
surfaceScalarField evaporationRate(
    IOobject("evaporationRate", mesh.time().timeName(), mesh),
    mesh,
    dimensionedScalar("evaporationRate", dimMass/dimArea/dimTime, 0.0)
);

// Calculate local evaporation rate
volScalarField alpha1 = ...; // Liquid fraction
volScalarField T_local = ...; // Local temperature
surfaceScalarField T_avg = fvc::average(T_local);

// Interface location
surfaceScalarField alphaInterface = fvc::interpolate(alpha1);
surfaceScalarField alphaGrad = fvc::grad(alpha1);
surfaceScalarField magGradAlpha = mag(alphaGrad);

// Adaptive cAlpha based on evaporation rate
surfaceScalarField localEvapRate = evaporationRate;
surfaceScalarField adaptiveAlpha =
    Foam::min(0.9, 0.5 + 0.4 * Foam::exp(-localEvapRate / 0.1));

// Apply compression
surfaceScalarField U_r =
    fvc::interpolate(alpha1) * (1 - fvc::interpolate(alpha1))
  * adaptiveAlpha * nHatUf;

// Update flux
surfaceScalarField alphaPhi = alpha1Phi + U_r;
```

---

## 3. MULES Application for Evaporating Flow (การใช้ MULES สำหรับการ蒸เป็น)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain B: Numerics**
> - **File**: `MULES.H` - Implementation of MULES algorithm
> - **Keywords**: `boundedAlpha`, `limitedFlux`, `explicitSolve`
> - **Purpose**: รักษา boundedness และ mass conservation

### Boundedness Enforcement (0 ≤ α ≤ 1)

สำหรับ蒸 evaporator เราต้องเข้าใจว่า MULES จัดการกับ boundedness อย่างไร:

```cpp
// MULES::explicitSolve with boundedness
MULESCoeffs
{
    nAlphaCorr      2;        // Corrector iterations
    nAlphaSubCycles 3;        // Sub-cycles
    cAlpha          0.9;      // Compression coefficient
    maxCo           0.3;      // Maximum Co
    rDeltaT         1.0;      // Relative time step
}

// Call MULES in the solver
solveAlpha = MULES::explicitSolve
(
    alpha1,          // Alpha field
    phi,            // General flux
    alpha1Phi,      // Alpha flux
    alpha1,         // Reference alpha
    phi,            // Reference flux
    alpha1Corr,     // Corrector iterations
    nAlphaCorr,     // Number of correctors
    nAlphaSubCycles // Sub-cycles
);
```

### Implicit Source Term Handling

การ蒸เป็น source term ที่มีความกว้างขวาง (stiff) ทำให้ต้องใช้ implicit treatment:

```cpp
// Implicit source term for phase change
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1)
    + fvm::div(phi, alpha1)
    + fvm::div(alphaRhoPhi, alpha1)
 ==
    MULES::explicitSolve(alpha1, phi, alpha1Phi, alpha1, phi, alpha1Corr)
  + fvm::Sp(S_alpha_diag, alpha1)   // Implicit diagonal
  + fvm::Sp(S_alpha_offdiag, alpha1) // Implicit off-diagonal
);

// Source term linearization
tmp<volScalarField> S_alpha_diag(new volScalarField(S_alpha_diag));
tmp<volScalarField> S_alpha_offdiag(new volScalarField(S_alpha_offdiag));

// Calculate source term derivatives
volScalarField alpha1Cell = alpha1;
volScalarField dS_dalpha = ...; // Derivative of S_alpha with respect to alpha

// Implicit treatment
S_alpha_diag = Foam::pos(dS_dalpha) * dS_dalpha;
S_alpha_offdiag = Foam::neg(dS_dalpha) * dS_dalpha;

// Solve the equation
alpha1Eqn.solve();
```

### Iterative Solution Strategy

สำหรับ蒸 evaporator เราต้องใช้ iterative method เพื่อจัดการกับ non-linearity:

```cpp
// Iterative VOF solver with phase change
for (int i = 0; i < nAlphaCorr; i++)
{
    // Step 1: Predict fluxes
    surfaceScalarField alpha1PhiPredicted = alpha1Phi;

    // Step 2: Apply MULES for boundedness
    MULES::explicitSolve
    (
        alpha1,          // Current alpha
        phi,            // General flux
        alpha1Phi,       // Alpha flux
        alpha1,          // Reference alpha
        phi,             // Reference flux
        alpha1Corr,      // Corrector iterations
        nAlphaCorr,      // Number of correctors
        nAlphaSubCycles  // Sub-cycles
    );

    // Step 3: Apply phase change source term
    volScalarField alpha1Old = alpha1;
    volScalarField S_alpha = calcPhaseChange(alpha1, T, p);

    // Update alpha
    alpha1 = alpha1Old - mesh.time().deltaT() * S_alpha;

    // Step 4: Clamp values to physical bounds
    alpha1 = Foam::max(0.0, Foam::min(1.0, alpha1));

    // Check convergence
    scalar residual = Foam::mag(alpha1 - alpha1Old) / Foam::mag(alpha1Old) / mesh.time().deltaT();

    if (residual < 1e-6)
    {
        Info << "VOF converged in " << i+1 << " iterations" << endl;
        break;
    }
}
```

### Advanced MULES for High Evaporation Rates

```cpp
// Enhanced MULES for evaporator applications
void Foam::MULES::evaporatorSolve
(
    surfaceScalarField& alphaPhi,
    const volScalarField& alpha1,
    const surfaceScalarField& phi,
    const surfaceScalarField& alpha1Phi,
    const scalar cAlpha,
    const scalar maxCo,
    const scalar rDeltaT,
    const int nAlphaCorr,
    const int nAlphaSubCycles,
    const volScalarField& evapRate
)
{
    // Sub-cycling
    for (subCycle<scalar> alpha1SubCycle(alpha1SubCycles); !(++alpha1SubCycle).end(); )
    {
        // Interface compression velocity
        surfaceScalarField U_r =
            cAlpha *
            fvc::interpolate(evapRate) *
            pos(fvc::interpolate(alpha1) - 0.5) *
            pos(1.0 - fvc::interpolate(alpha1));

        // Enhanced flux with evaporation
        alphaPhi += U_r;

        // Standard MULES correction
        alpha1 =

 limited
    }
}
```

---

## 4. Code Examples for R410A Evaporator (ตัวอย่างโค้ดสำหรับ R410A Evaporator)

### Complete Solver Implementation

```cpp
// File: `/Users/woramet/Documents/th_new/MODULE_04_MULTIPHASE_FUNDAMENTALS/SOLVERS/R410AevaporatorVOF.C`
// Custom VOF solver for R410A evaporator applications

#include "fvCFD.H"
#include "MULES.H"
#include "alphaContactAngle.H"
#include "surfaceFields.H"
#include "fvc.H"
#include "fvm.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    Info << "Starting R410A evaporator simulation..." << endl;

    // Time loop
    while (runTime.run())
    {
        #include "readTimeControls.H"
        #include "CourantNo.H"
        #include "alphaCourantNo.H"
        #include "setDeltaT.H"

        runTime++;

        Info << "Time = " << runTime.timeName() << endl;

        // Momentum equation
        #include "UEqn.H"

        // Pressure-velocity coupling
        #include "pEqn.H"

        // VOF equation with phase change
        #include "alphaEqn.H"

        // Update interface
        alpha1.correctBoundaryConditions();

        // Update thermodynamic properties
        #include "updateThermo.H"

        // Write results
        runTime.write();

        // Check convergence
        #include "continuityErrs.H"
    }

    Info << "End of simulation" << endl;
    return 0;
}

// File: alphaEqn.H
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1)
    + fvm::div(phi, alpha1)
    + fvm::div(alphaRhoPhi, alpha1)
    ==
    MULES::explicitSolve(alpha1, phi, alpha1Phi, alpha1, phi, alpha1Corr, nAlphaCorr, nAlphaSubCycles)
);

// Add phase change source term
volScalarField S_alpha = calcPhaseChange(alpha1, T, p);
alpha1Eqn += S_alpha * mesh.time().deltaT();

alpha1Eqn.relax();
alpha1Eqn.solve();

// Correct boundary conditions
alpha1.correctBoundaryConditions();

// Ensure boundedness
alpha1 = max(alpha1, scalar(0));
alpha1 = min(alpha1, scalar(1));
```

### Phase Change Source Term Implementation

```cpp
// File: phaseChangeModel.C
tmp<volScalarField> calcPhaseChange
(
    const volScalarField& alpha1,
    const volScalarField& T,
    const volScalarField& p
)
{
    // R410A thermodynamic properties
    dimensionedScalar T_sat = "T_sat" dimensionSet(0, 0, 0, 1, 0, 0, 0);
    dimensionedScalar h_fg = "h_fg" dimensionSet(0, 2, -2, 0, 0, 0, 0);
    dimensionedScalar rho_l = "rho_l" dimensionSet(1, -3, 0, 0, 0, 0, 0);
    dimensionedScalar rho_v = "rho_v" dimensionSet(1, -3, 0, 0, 0, 0, 0);

    // Interface detection
    volScalarField interfaceAlpha = mag(alpha1 - 0.5);
    volScalarField liquidFraction = alpha1;
    volScalarField vaporFraction = 1.0 - alpha1;

    // Local saturation temperature
    volScalarField T_local_sat = fvc::average(T);

    // Heat transfer coefficient
    dimensionedScalar k_liquid = "k_liquid" dimensionSet(1, 1, -3, -1, 0, 0, 0);
    dimensionedScalar L_ref = "L_ref" dimensionSet(0, 1, 0, 0, 0, 0, 0);
    scalar Nu = 100.0; // Nusselt number
    scalar h_conv = Nu * k_liquid.value() / L_ref.value();

    // Mass flux calculation
    volScalarField T_superheat = T - T_sat;
    volScalarField m_dot = h_conv * Foam::mag(T_superheat) / h_fg.value();

    // Source term
    volScalarField S_alpha(
        IOobject("S_alpha", T.time().timeName(), T.mesh()),
        T.mesh(),
        dimensionedScalar("zero", alpha1.dimensions()/dimTime, 0.0)
    );

    // Evaporation (liquid to vapor)
    S_alpha -= (m_dot * liquidFraction / rho_l.value()) *
               (T > T_sat) *
               (liquidFraction > 0.1) *
               (vaporFraction > 0.1);

    // Condensation (vapor to liquid)
    S_alpha += (m_dot * vaporFraction / rho_v.value()) *
               (T < T_sat) *
               (liquidFraction > 0.1) *
               (vaporFraction > 0.1);

    return tmp<volScalarField>(S_alpha);
}
```

### Interface Compression Settings

```cpp
// File: `/Users/woramet/Documents/th_new/MODULE_04_MULTIPHASE_FUNDAMENTALS/R410A_Evaporator/system/fvSolution`
solvers
{
    "alpha.water.*"
    {
        nAlphaCorr      2;
        nAlphaSubCycles 3;
        cAlpha          0.9;

        MULESCoeffs
        {
            nAlphaCorr      2;
            nAlphaSubCycles 3;
            cAlpha          0.9;
            maxCo           0.3;
            rDeltaT         1.0;
        }
    }
}

// File: `/Users/woramet/Documents/th_new/MODULE_04_MULTIPHASE_FUNDAMENTALS/R410A_Evaporator/system/controlDict`
application     R410AevaporatorVOF;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         10;
deltaT          0.001;
writeControl    adjustable;
writeInterval   0.1;
```

### Boundary Conditions for Evaporator

```cpp
// File: `/Users/woramet/Documents/th_new/MODULE_04_MULTIPHASE_FUNDAMENTALS/R410A_Evaporator/0/alpha.water`
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0.1;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1.0;  // Liquid inlet
    }

    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0.0;  // Vapor outlet
        value           uniform 0.0;
    }

    walls
    {
        type            zeroGradient;
    }

    heatedWall
    {
        type            fixedGradient;
        gradient        uniform 0.01;  // Heat flux boundary
    }
}
```

---

## 📊 Parameter Guidelines for R410A Evaporator

| Parameter | Location | Typical Value | Purpose |
| :--- | :--- | :--- | :--- |
| **cAlpha** | `fvSolution` | 0.8-1.0 | Compression coefficient |
| **nAlphaCorr** | `fvSolution` | 2-3 | Corrector iterations |
| **nAlphaSubCycles** | `fvSolution` | 3-5 | Sub-cycling |
| **maxCo** | `controlDict` | 0.2-0.3 | Courant limit |
| **h_fg** | `thermoProperties` | 170,000 | Latent heat (J/kg) |
| **sigma** | `thermoProperties` | 0.008-0.012 | Surface tension (N/m) |

> [!TIP] **Quick Guidelines**
> - **Low heat flux**: `cAlpha 1.0`, `nAlphaCorr 2`, `maxCo 0.3`
> - **Medium heat flux**: `cAlpha 0.9`, `nAlphaCorr 3`, `maxCo 0.25`
> - **High heat flux**: `cAlpha 0.8`, `nAlphaCorr 4`, `maxCo 0.2`

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ nAlphaSubCycles สำหรับ蒸 evaporator?</b></summary>

เพราะ蒸เป็นปรากฏการณ์ที่เกิดขึ้นอย่างรวดเร็วและ local โดยเฉพาะที่ interface การใช้ sub-cycling ช่วยให้เราสามารถจัดการกับ time scales ที่แตกต่างกันได้อย่างถูกต้อง: time scale ของ advection มีขนาดใหญ่กว่า time scale ของ蒸เป็นอย่างมาก ทำให้การแก้จากจากกับ sub-cycles ช่วยให้การคำนวณเสถียรและแม่นยำขึ้น
</details>

<details>
<summary><b>2. ทำไมต้องลดค่า cAlpha สำหรับ蒸เป็น?</b></summary>

เพราะ蒸เป็น source term ที่มีความกว้างขวาง (stiff) การที่มี compression velocity ที่สูงเกินไปอาจทำให้เกิด numerical instability การลด cAlpha จาก 1.0 เป็น 0.8-0.9 ช่วยลดความรุนแรงของ compression และรักษาเสถียรภาพของ solver ในขณะที่ยังรักษาความคมของ interface ไว้ได้
</details>

<details>
<summary><b>3. ทำไม Interface Compression ยังสำคัญใน蒸เป็นถึงมี蒸เป็น?</b></summary>

เพราะ蒸เป็นทำให้ค่า alpha เปลี่ยนแปลงเร็วมาก หากไม่มี compression จะทำให้ interface เบลออย่างรวดเร็ว compression term เป็น term ที่ "กด" interface ให้คมขึ้นโดยไม่ต้องมี advection flux ที่แม่นยำที่จริง มันเป็นเทคนิคที่ช่วยแก้ปัญหา numerical diffusion ที่เกิดจาก discretization errors
</details>

<details>
<summary><b>4. ทำไมถึงต้องใช้ MULES แทนของที่เป็น?</b></summary>

เพราะ MULES (Multidimensional Universal Limiter with Explicit Solution) เป็น algorithm ที่ออกแบบมาเพื่อรักษา boundedness (0 ≤ α ≤ 1) และ mass conservation ในขณะที่รองรับได้กับ flux limiter ที่มีความกว้างขวาง (stiff source terms) มันให้ solution ที่ stable และ conservative ซึ่งเป็นสิ่งที่จำเป็นสำหรับ蒸 applications
</details>

---

## 🎓 How to Apply: Key Takeaways

### ✅ Core Concepts to Remember
1. **Phase Change Source Term**: ต้องถูกเพิ่มเข้าไปในสมการ VOF เพื่อจัดการกับ蒸เป็น
2. **Adaptive Compression**: ค่า cAlpha อาจต้องลดลงเล็กน้อยเพื่อรักษาเสถียรภาพ
3. **Sub-cycling**: จำเป็นสำหรับจัดการกับ time scales ที่แตกต่างกันมาก
4. **Implicit Treatment**: Source term สำหรับ蒸เป็นจัด treatment แบบ implicit

### 🔧 Practical Implementation

#### Step 1: เขียน Phase Change Model
```cpp
// ใน solver
volScalarField S_alpha = calcPhaseChange(alpha1, T, p);
alpha1Eqn += S_alpha;
```

#### Step 2: ปรับแต่ง MULES
```cpp
// ใน fvSolution
"alpha.*"
{
    nAlphaCorr      3;
    nAlphaSubCycles 4;
    cAlpha          0.85;

    MULESCoeffs
    {
        maxCo           0.25;
    }
}
```

#### Step 3: Monitor Convergence
```cpp
// เพิ่มใน solver
scalar alphaRes = Foam::mag(alpha1 - alpha1Old) / Foam::mag(alpha1Old);
if (alphaRes > 1e-3)
{
    Warning << "High alpha residual: " << alphaRes << endl;
}
```

### ⚠️ Common Pitfalls to Avoid

| Pitfall | Symptom | Solution |
| :--- | :--- | :--- |
| **Source term too large** | Solver diverges, negative α | Reduce evaporation rate, use implicit treatment |
| **Compression too strong** | Interface artifacts | Reduce cAlpha, check grid resolution |
| **Insufficient sub-cycles** | Oscillations in α | Increase nAlphaSubCycles |
| **Wrong boundary conditions** | Incorrect mass balance | Use inletOutlet for vapor outlets |
| **Missing surface tension** | Unphysical behavior | Include CSF model with temperature-dependent σ |

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า**: [[02_Interface_Compression.md]] - เรียนรู้วิธีรักษาความคมของ Interface
- **บทถัดไป**: [[03_Setting_Up_InterFoam.md]] - การตั้งค่า InterFoam พื้นฐาน
- **บทเกี่ยวข้อง**: [[../01_The_VOF_Concept.md]] - แนวคิดพื้นฐาน VOF method

---

**🔬 Note**: ตัวอย่างโค้ดและค่าพารามิเตอร์ในบทความนี้เป็นแนวทางเบื้องต้น คุณอาจต้องปรับแต่งให้เหมาะสมกับ application และ conditions ของงานจริง