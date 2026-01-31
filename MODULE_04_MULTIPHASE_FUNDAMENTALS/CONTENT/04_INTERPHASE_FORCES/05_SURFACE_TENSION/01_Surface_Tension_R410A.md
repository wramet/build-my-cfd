# 5. Surface Tension Forces in R410A Evaporation (แรงตัวผิวผิวของ R410A ในการระเหย)

## 5.1 R410A Surface Tension Coefficient (สัมประสิทธิ์แรงตัวผิวผิวของ R410A)

### ⭐ R410A Surface Tension Properties

Surface tension is a critical property in two-phase flow that significantly affects the behavior of evaporating refrigerants like R410A. At saturation conditions:

```
σ ≈ 0.008 N/m at Tsat for R410A
```

> **File:** `boundary_conditions_report.json`
> **Lines:** 157-159
> **Code:**
> ```json
> "R410A": {
>   "surfaceTension": 0.008,
>   "temperatureDependence": "exponential"
> }
> ```

### Temperature Dependence Model

The surface tension of R410A varies with temperature following an exponential relationship:

$$
\sigma(T) = \sigma_0 \left[1 - k(T - T_{sat})\right]
$$

where:
- $\sigma_0 = 0.008$ N/m (surface tension at saturation temperature)
- $k \approx 1.5 \times 10^{-4}$ K$^{-1}$ (temperature coefficient)
- $T_{sat}$ = saturation temperature (45.6°C for R410A at 15.5 bar)

> **NOTE:** The temperature coefficient $k$ represents the rate of surface tension change with temperature, which is critical for accurate two-phase flow modeling in varying temperature environments like evaporator tubes.

### Comparison with Other Refrigerants

| Refrigerant | σ at Tsat (N/m) | Application |
|-------------|----------------|-------------|
| R410A | 0.008 | Residential AC, Heat pumps |
| R134a | 0.006 | Automotive refrigeration |
| R32 | 0.007 | Modern refrigerants |
| R407C | 0.007 | Retrofit replacements |

> **⭐ Physical Significance:** Lower surface tension (like R134a) promotes easier bubble formation but reduces capillary forces in microchannels, while higher surface tension (like R410A) increases capillary effects but requires higher energy for bubble formation.

## 5.2 Continuum Surface Force (CSF) Model (โมเดลแรงผิวผิวต่อเนื่อง)

### ⭐ CSF Model Theory

The Continuum Surface Force (CSF) model treats surface tension as a volumetric force in the momentum equation:

$$
\mathbf{F}_s = \sigma \kappa \rho \nabla \alpha
$$

where:
- $\mathbf{F}_s$ = surface tension force vector [N/m³]
- $\sigma$ = surface tension [N/m]
- $\kappa$ = curvature of the interface [1/m]
- $\rho$ = density [kg/m³]
- $\nabla \alpha$ = gradient of the volume of fluid [1/m]

### Surface Curvature Calculation

The curvature $\kappa$ is calculated from the interface normal:

$$
\kappa = -\nabla \cdot \mathbf{n}
$$

where $\mathbf{n}$ is the interface normal:

$$
\mathbf{n} = \frac{\nabla \alpha}{|\nabla \alpha|}
$$

> **File:** `openfoam_temp/src/interfacialModels/surfaceTension/surfaceTensionModel/surfaceTensionModel.H`
> **Lines:** 32-35
> **Code:**
> ```cpp
> virtual tmp<volScalarField> curvature() const = 0;
> virtual tmp<volVectorField> fSt() const = 0;
> ```

### Implementation in OpenFOAM

The CSF force is added to the momentum equation as a source term:

```cpp
// In momentum equation
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U) + fvm::div(rhoPhi, U)
    + fvm::laplacian(mu, U)
    == fvModels.source(rho, U)
);

// Add surface tension force
tmp<volVectorField> surfaceTensionForce = interfaceModel->fSt();
UEqn -= surfaceTensionForce;
```

> **⭐ Verification:** The surface tension force $\mathbf{F}_s$ must be applied consistently throughout the domain, including boundaries where interface boundaries may exist.

## 5.3 Surface Tension Effects in Evaporator Tubes (ผลกระทบของแรงตัวผิวผิวในท่อระเหย)

### ⭐ Capillary Forces in Small Tubes

For microchannel evaporators, capillary forces become dominant:

$$
\Delta P_{cap} = \frac{4\sigma \cos\theta}{D_h}
$$

where:
- $\Delta P_{cap}$ = capillary pressure [Pa]
- $\theta$ = contact angle (≈ 20° for R410A on copper)
- $D_h$ = hydraulic diameter [m]

> **Example:** For a 1mm tube diameter with R410A:
> $$\Delta P_{cap} = \frac{4 \times 0.008 \times \cos(20^\circ)}{0.001} = 300\, \text{Pa}$$

### Influence on Flow Regime Transitions

Surface tension affects critical flow transitions:

1. **Bubble to Slug Flow**
   - Low surface tension: Promotes bubble coalescence
   - High surface tension: Stabilizes individual bubbles

2. **Slug to Annular Flow**
   - Balance of gravity, shear, and surface tension forces
   - Critical Weber number: $We_{crit} \approx 30$

3. **Film Flow in Microchannels**
   - Surface tension stabilizes liquid films
   - Minimum film thickness affected by capillary forces

### Impact on Liquid Film Behavior

In annular flow, surface tension maintains liquid film integrity:

```cpp
// Surface tension correction for film thickness
volScalarField surfaceTensionCorrection
(
    fvc::div(interfaceModel->fSt())
);

// Update film thickness based on capillary number
Ca = mu_l * U / sigma;
```

> **⭐ Physical Insight:** Higher surface tension increases resistance to film breakup, leading to more stable liquid films in horizontal tubes.

## 5.4 Bond Number for R410A Flow (ตัวเลขบอนด์สำหรับการไหลของ R410A)

### ⭐ Bond Number Definition

The Bond number characterizes the relative importance of surface tension vs. gravity:

$$
Bo = \frac{(\rho_l - \rho_v) g L^2}{\sigma}
$$

where:
- $\rho_l - \rho_v$ = liquid-vapor density difference [kg/m³]
- $g$ = gravitational acceleration [m/s²]
- $L$ = characteristic length (tube diameter) [m]
- $\sigma$ = surface tension [N/m]

### Significance for Evaporator Design

For R410A in typical evaporator dimensions:

| Tube Diameter (mm) | Bond Number | Dominant Force |
|-------------------|-------------|----------------|
| 1 | 0.1 | Surface tension |
| 3 | 0.9 | Mixed (gravity-surface tension) |
| 6 | 3.6 | Gravity dominated |
| 12 | 14.4 | Gravity dominated |

> **⭐ Critical Design Insight:** For tube diameters below 3mm, surface tension dominates flow behavior, requiring special consideration for:
> - Flow regime prediction
> - Pressure drop calculations
> - Heat transfer enhancement

### Comparison of Surface Tension vs. Gravity

The relative importance can be visualized through force ratios:

$$
\frac{F_{gravity}}{F_{surface}} = \frac{(\rho_l - \rho_v) g V}{\sigma A}
$$

where $V/A = L/6$ for spherical bubbles.

For R410A bubbles in 5mm diameter tubes:
- Gravity force ≈ 1.2 × 10⁻⁵ N
- Surface tension force ≈ 8.0 × 10⁻⁶ N
- Ratio ≈ 1.5 (mixed regime)

### Design Implications for R410A Evaporators

1. **Microchannel Design (< 3mm)**
   - Surface tension dominates
   - Capillary pumping effects
   - Need for optimized fin geometries

2. **Conventional Tubes (3-12mm)**
   - Mixed gravity-surface tension regime
   - Account for both effects in correlations
   - Enhanced surface tension models

3. **Large Bore Tubes (> 12mm)**
   - Gravity dominated
   - Surface effects localized at interfaces
   - Standard models applicable

> **⭐ Verification Required:** Surface tension coefficients must be validated against experimental data for R410A specific to operating conditions.

## 5.5 Surface Tension Implementation in OpenFOAM (การใช้งานแรงตัวผิวผิวใน OpenFOAM)

### ⭐ Required Header Files

For surface tension implementation in OpenFOAM:

```cpp
#include "surfaceTensionModel.H"
#include "interfaceProperties.H"
#include "nusseltNumber.H"

// Main solver header
#include "fvCFD.H"
```

### Surface Tension Model Selection

The appropriate model depends on the flow regime:

1. **Continuum Surface Force (CSF)**
   ```cpp
   autoPtr<surfaceTensionModel> stModel
   (
       surfaceTensionModel::New(mesh, interface)
   );
   ```

2. **Sharp Interface Model**
   ```cpp
   autoPtr<surfaceTensionModel> stModel
   (
       surfaceTensionModel::New(mesh, interface, "sharp")
   );
   ```

### R410A Property Assignment

In the `createFields.H` file:

```cpp
// R410A properties
volScalarField sigma
(
    IOobject
    (
        "sigma",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("sigma", dimensionSet(1, 0, -2, 0, 0, 0, 0), 0.008)
);

// Temperature-dependent surface tension
if (runTime.time().value() > 0)
{
    volScalarField Tsat
    (
        IOobject
        (
            "Tsat",
            runTime.timeName(),
            mesh,
            IOobject::READ_IF_PRESENT,
            IOobject::AUTO_WRITE
        ),
        mesh,
        dimensionedScalar("Tsat", dimensionSet(0, 0, 0, 1, 0, 0, 0), 318.75) // 45.6°C
    );

    // Update surface tension based on temperature
    sigma *= (1 - 1.5e-4 * (T - Tsat));
}
```

### Surface Tension Source Term Implementation

```cpp
// In solver main loop
while (runTime.run())
{
    #include "readTimeControls.H"

    // Update interface properties
    interface.correct();

    // Calculate surface tension force
    tmp<volVectorField> fSt = stModel->fSt();

    // Add to momentum equation
    fvVectorMatrix UEqn
    (
        fvm::ddt(rho, U) + fvm::div(rhoPhi, U)
        == fvModels.source(rho, U)
        + fSt // Surface tension source term
    );

    // Solve momentum equation
    solve(UEqn);

    // Update alphaEqn
    solve(alphaEqn);
}
```

### Boundary Conditions for Surface Tension

At tube walls, contact angle must be specified:

```cpp
// In createFields.H or boundary files
interface.setBoundaryCondition
(
    "wall", // patch name
    "contactAngle", // condition type
    dimensionedScalar("contactAngle", dimensionSet(0, 0, 0, 0, 0, 0, 0),
                     Foam::degToRad(20.0)) // 20 degrees in radians
);
```

> **⭐ Critical Implementation Note:** Surface tension forces are local to interfaces and require accurate interface tracking. The computational domain must be fine enough to resolve interface curvature.

## 5.6 Validation and Testing (การตรวจสอบและทดสอบ)

### ⭐ Test Cases for R410A Surface Tension

1. **Static Bubble Test**
   - Verify Young-Laplace equation: $\Delta P = 2\sigma/R$
   - Compare numerical results with analytical solution

2. **Droplet Deformation**
   - Weber number variation: $We = \rho_l U^2 D/\sigma$
   - Observe deformation patterns

3. **Film Flow in Tubes**
   - Measure pressure drop with and without surface tension
   - Validate against experimental correlations

### Expected Results for R410A

| Test Case | Expected Behavior | Verification Criteria |
|-----------|-------------------|----------------------|
| Bubble Rise | Affected by Bond number | Terminal velocity within 5% of theory |
| Film Stability | Stable annular flow | No numerical instabilities |
| Capillary Rise | Height h = 2σ/(ρgL) | Error < 3% |

> **⭐ Final Verification:** All surface tension implementations must pass the Bond number sensitivity test to ensure proper scaling across different tube diameters.

## 5.7 Summary and Key Equations (สรุปและสมการสำคัญ)

### Summary of Surface Tension Effects in R410A Evaporation

1. **Surface Tension Value**: σ ≈ 0.008 N/m at Tsat
2. **Temperature Dependence**: Exponential decay with temperature
3. **CSF Model**: $\mathbf{F}_s = \sigma \kappa \rho \nabla \alpha$
4. **Bond Number**: $Bo = \frac{(\rho_l - \rho_v) g L^2}{\sigma}$

### Key Implementation Steps

1. Include surface tension headers
2. Assign R410A surface tension properties
3. Implement contact angle boundary conditions
4. Add surface tension source term to momentum equation
5. Validate with test cases

### Design Recommendations for R410A Evaporators

- For tube diameters < 3mm, surface tension dominates (Bo < 1)
- Include surface tension effects in all microchannel designs
- Use accurate R410A surface tension data
- Implement temperature-dependent models for varying conditions

> **⭐ Remember:** Surface tension is a critical property that affects bubble formation, flow regimes, heat transfer, and pressure drop in R410A evaporators. Proper implementation requires accurate property data and appropriate mesh resolution.