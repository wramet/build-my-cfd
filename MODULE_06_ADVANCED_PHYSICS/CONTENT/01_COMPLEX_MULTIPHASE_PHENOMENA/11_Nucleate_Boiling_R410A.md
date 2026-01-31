## Nucleate Boiling Modeling for R410A

### English Title (โมเดลการต้มฟองของ R410A)

**Difficulty**: Advanced | **Key Solvers**: `reactingTwoPhaseEulerFoam`, `chtMultiRegionFoam`

---

## 📚 Prerequisites (ความรู้พื้นฐานที่ต้องมี)

Before studying nucleate boiling in R410A, ensure you understand:

### Required Knowledge
- **Basic Phase Change Physics** — Vapor formation and growth mechanisms
- **Heat Transfer Fundamentals** — Convective and boiling heat transfer
- **Wall Function Theory** — Near-wall treatment in CFD
- **R410A Properties** — Thermophysical properties from previous section

---

## 🎯 Learning Objectives (วัตถุประสงค์การเรียนรู้)

By the end of this section, you will be able to:

### WHAT (Define and Analyze)
1. **Characterize Nucleate Boiling Regimes** — Identify ONB, nucleate boiling, and critical heat flux
2. **Model Bubble Dynamics** — Understand nucleation, growth, and departure mechanisms
3. **Predict Boiling Curves** — Relate heat flux to wall superheat for R410A

### WHY (Engineering Significance)
4. **Enhance Heat Transfer** — Achieve 10-100× higher coefficients than single-phase
5. **Avoid Boiling Crisis** — Prevent critical heat flux and dryout conditions
6. **Optimize Evaporator Design** — Select proper tube geometry and operating conditions

### HOW (Implementation in OpenFOAM)
7. **Configure Wall Boiling Models** — Set up nucleate source terms in energy equation
8. **Implement Bubble Dynamics** — Model nucleation site density and departure
9. **Calculate Heat Transfer Coefficients** — Implement R410A-specific correlations

---

## 1. Boiling Curve for R410A (เส้นโค้งการต้มฟองของ R410A)

### Boiling Curve Visualization

```
Heat Flux (q")
    |
    |     CHF
    |      ●
    |      |
    |      |
    |      |    Nucleate Boiling
    |      |    /
    |      |   /
    |      |  /
    |      | /
    |      |/
    |_____●_______________ Wall Superheat (ΔT)
       ONB
```

### Key Points in R410A Evaporators

| Regime | Heat Flux Range | Wall Superheat | Heat Transfer Mechanism |
|--------|-----------------|----------------|------------------------|
| **Single-phase convection** | 1-5 kW/m² | ΔT < 2°C | Forced convection |
| **Onset of Nucleate Boiling (ONB)** | 5-10 kW/m² | ΔT = 2-5°C | First bubble formation |
| **Nucleate Boiling** | 10-20 kW/m² | ΔT = 5-15°C | Bubble growth and departure |
| **Critical Heat Flux (CHF)** | 15-25 kW/m² | ΔT = 15-25°C | Film formation, dryout |
| **Film Boiling** | < 5 kW/m² | ΔT > 25°C | Vapor film, poor heat transfer |

### R410A-Specific Characteristics

⭐ **Lower Surface Tension**: σ ≈ 0.05 N/m (25% lower than water)
- **Effect**: Smaller bubble departure diameters
- **Impact**: Higher nucleation site density
- **Boiling Enhancement**: 20-30% higher heat transfer than water at same conditions

⭐ **Density Ratio**: ρ_l/ρ_v ≈ 17:1 (vs 1000:1 for water)
- **Effect**: Lower bubble rise velocity
- **Impact**: Longer bubble residence time near wall
- **Boiling Enhancement**: Increased interfacial area

---

## 2. Heat Transfer Correlations for R410A (สมการการถ่ายเทความร้อนสำหรับ R410A)

### Cooper's Pool Boiling Correlation

⭐ **Cooper's Correlation for R410A:**
$$ h_{nb} = 55 P_r^{0.12} (-\log_{10} P_r)^{-0.55} M^{-0.5} q^{0.67} $$

For R410A at 1.0 MPa:
- P_r = P/P_critical = 1.0/4.9 = 0.204
- M = 72.6 g/mol = 0.0726 kg/mol
- Result: h_nb ≈ 5000-8000 W/m²·K

**Implementation:**
```python
# Cooper correlation implementation
def cooper_boiling_coefficient(P, q, M=0.0726):
    # P: pressure [Pa]
    # q: heat flux [W/m²]
    # M: molecular weight [kg/mol]

    P_critical = 4.9e6  # Pa for R410A
    P_r = P / P_critical

    # Cooper correlation
    h_nb = 55 * (P_r**0.12) * ((-log10(P_r))**-0.55) * (M**-0.5) * (q**0.67)

    return h_nb
```

### Gorenflo Correlation

⭐ **Gorenflo Correlation for R410A:**
$$ h_{nb} = h_{nb,ref} \left(\frac{q}{q_{ref}}\right)^{0.95} F(P) $$

Reference values for R410A at 10°C:
- h_nb,ref = 5000 W/m²·K at q_ref = 10 kW/m²
- F(P) = 1.2 at P = 1.0 MPa
- q = heat flux [W/m²]

**Pressure Correction Function:**
$$ F(P) = \left(\frac{P}{P_{critical}}\right)^{0.1} \left(1 - \frac{P}{P_{critical}}\right)^{0.35} $$

### Rohsenow Correlation

⭐ **Rohsenow Correlation for Nucleate Boiling:**
$$ \frac{q}{h_{lv} \rho_v} = C_{sf} \left[\frac{q \mu_l h_{lv}}{k_l (T_w - T_{sat})}\right]^n \left[\frac{\rho_l (g(\rho_l - \rho_v))^{0.5}}{\sigma}\right]^{0.5} $$

For R410A:
- C_sf = 0.013 (surface-fluid constant)
- n = 1.0 (exponent)
- μ_l = 1.2e-4 Pa·s
- h_lv = 2.0e5 J/kg
- σ = 0.05 N/m

---

## 3. Wall Heat Flux Partitioning (การแบ่งส่วนฟ้าน้ำผนัง)

### Total Heat Flux Components

⭐ **Total Wall Heat Flux:**
$$ q_w = q_{fc} + q_{nb} + q_{evap} $$

**1. Forced Convection Component:**
$$ q_{fc} = h_{fc} (T_w - T_l) $$

⭐ **Forced Convection Coefficient for R410A:**
$$ h_{fc} = 0.023 Re^{0.8} Pr^{0.4} \frac{k_l}{D} $$

For R410A flow in a 10 mm tube:
- Re = 10,000 (typical)
- Pr = 0.9 (R410A liquid)
- k_l = 0.08 W/m·K
- Result: h_fc ≈ 500-1000 W/m²·K

**2. Nucleate Boiling Component:**
$$ q_{nb} = h_{nb} (T_w - T_{sat})^2 $$

⭐ **R410A Nucleate Boiling Heat Flux:**
- q_nb ≈ 5000-15000 W/m²·K at ΔT = 5-15°C
- Accounts for bubble-enhanced heat transfer

**3. Evaporative Heat Transfer:**
$$ q_{evap} = \dot{m} h_{lv} $$

Where ṁ is the phase change rate from the thermal model.

### Implementation in OpenFOAM

```cpp
// Calculate total wall heat flux
volScalarField qTotal
(
    IOobject::groupName("qTotal", alpha.group()),
    mesh,
    dimensionedScalar("qTotal", dimensionSet(0, 0, -3, 0, 0, 0, 0), 0.0)
);

// Forced convection component
volScalarField qFc
(
    IOobject::groupName("qFc", alpha.group()),
    mesh,
    dimensionedScalar("qFc", qTotal.dimensions(), 0.0)
);

// Calculate Re and Pr for R410A
volScalarField Re
(
    "Re",
    rho_l * mag(U) * tubeDiameter / mu_l
);

volScalarField Pr
(
    "Pr",
    mu_l * cp_l / k_l
);

// Dittus-Boelter correlation for forced convection
volScalarField Nu
(
    "Nu",
    0.023 * pow(Re, 0.8) * pow(Pr, 0.4)
);

volScalarField hFc
(
    "hFc",
    Nu * k_l / tubeDiameter
);

// Apply to wall boundary
forAll(qFc.boundaryField(), patchI)
{
    if (mesh.boundaryMesh()[patchI].type() == "wall")
    {
        qFc.boundaryFieldRef()[patchI] =
            hFc.boundaryField()[patchI] *
            (T.boundaryField()[patchI] - T_sat.boundaryField()[patchI]);
    }
}

// Nucleate boiling component
volScalarField qNb
(
    IOobject::groupName("qNb", alpha.group()),
    mesh,
    dimensionedScalar("qNb", qTotal.dimensions(), 0.0)
);

// Cooper correlation for nucleate boiling
forAll(qNb, cellI)
{
    scalar q_local = qFc[cellI];  // Use local heat flux
    scalar P_local = p[cellI];

    // Cooper correlation
    scalar P_r = P_local / 4.9e6;  // P_critical for R410A
    scalar M = 0.0726;  // Molecular weight [kg/mol]

    scalar h_nb = 55 * pow(P_r, 0.12)
                 * pow(-log10(P_r), -0.55)
                 * pow(M, -0.5)
                 * pow(q_local, 0.67);

    qNb[cellI] = h_nb * pow(T[cellI] - T_sat[cellI], 2);
}

// Apply to wall boundary
forAll(qNb.boundaryField(), patchI)
{
    if (mesh.boundaryMesh()[patchI].type() == "wall")
    {
        qNb.boundaryFieldRef()[patchI] =
            h_nb.boundaryField()[patchI] *
            pow(T.boundaryField()[patchI] - T_sat.boundaryField()[patchI], 2);
    }
}

// Total heat flux
qTotal = qFc + qNb + phaseChangeQ;
```

---

## 4. R410A-Specific Boiling Considerations (ข้อพิจารณาเฉพาะสำหรับ R410A)

### Surface Tension Effects

⭐ **Boiling Number for R410A:**
$$ Bo = \frac{q}{G h_{lv}} $$

For R410A evaporator:
- q = 3 kW/m² (typical heat flux)
- G = 200 kg/m²s (mass flux)
- h_lv = 200 kJ/kg (latent heat)
- Bo = 3000/(200 × 200,000) ≈ 7.5e-5

**Effect on Boiling:**
- Low Bo indicates convective-dominated boiling
- Important for flow boiling correlation selection

### Bubble Dynamics

⭐ **Bubble Departure Diameter for R410A:**
$$ d_d \approx 0.5 \text{ mm} $$

**Departure Frequency:**
$$ f \approx 50-100 \text{ Hz} $$

**Nucleation Site Density:**
$$ n \approx 10^6 \text{ sites/m}^2 $$

### Wall Function Modifications

```cpp
// Modified wall function for R410A nucleate boiling
// In wallBoilingModel.C
scalar R410ABoilingModel::wallHeatTransferCoeff
(
    scalar Tw,
    scalar Tsat,
    scalar q,
    scalar G,
    scalar x
) const
{
    // Calculate wall superheat
    scalar dT = Tw - Tsat;

    // Forced convection component
    scalar Re = G * tubeDiameter / mu_l;
    scalar Pr = mu_l * cp_l / k_l;
    scalar Nu = 0.023 * pow(Re, 0.8) * pow(Pr, 0.4);
    scalar h_fc = Nu * k_l / tubeDiameter;
    scalar q_fc = h_fc * dT;

    // Nucleate boiling component
    scalar P_r = P / P_critical_;
    scalar h_nb = 55 * pow(P_r, 0.12)
                 * pow(-log10(P_r), -0.55)
                 * pow(M_, -0.5)
                 * pow(q, 0.67);
    scalar q_nb = h_nb * dT * dT;  // q = h * ΔT² for boiling

    // Total heat transfer
    scalar h_total = (q_fc + q_nb) / dT;

    return h_total;
}
```

### Critical Heat Flux Prediction

⭐ **Kutateladze-Zuber Correlation for CHF:**
$$ q_{CHF} = 0.13 \rho_v^{0.5} h_{lv} (\sigma g (\rho_l - \rho_v))^{0.25} $$

For R410A:
- ρ_v = 70 kg/m³
- h_lv = 200,000 J/kg
- σ = 0.05 N/m
- g = 9.81 m/s²
- ρ_l = 1200 kg/m³

Result: q_CHF ≈ 15-20 kW/m²

```cpp
// Calculate critical heat flux for R410A
scalar calculateCHF(scalar rho_v, scalar rho_l, scalar h_lv, scalar sigma)
{
    scalar g = 9.81;

    scalar q_chf = 0.13 * sqrt(rho_v) * h_lv
                 * pow(sigma * g * (rho_l - rho_v), 0.25);

    return q_chf;
}
```

---

## 5. OpenFOAM Implementation (การนำไปใช้ใน OpenFOAM)

### Wall Boiling Model Setup

```cpp
// constant/thermophysicalProperties
thermophysicalModel
{
    type            pureMixture;
    mixture         R410A;

    // Include phase change model
    phaseChangeModel thermalPhaseChange;

    thermalPhaseChangeCoeffs
    {
        hLv     2.0e5;      // Latent heat [J/kg]
        Tsat    283.15;     // Saturation temperature [K]
        r       100;        // Mass transfer coefficient [1/s]
    }

    // Wall boiling model
    wallBoilingModel on;

    wallBoilingCoeffs
    {
        // Nucleate boiling parameters
        nucleationSites    1e6;     // sites/m²
        bubbleDiameter     0.0005;  // m
        departureFrequency  50;      // Hz

        // Heat transfer correlations
        boilingModel       cooper;  // cooper, gorenflo, rohsenow

        // R410A-specific properties
        surfaceTension     0.05;    // N/m
        densityRatio       17;      // ρ_l/ρ_v
        latentHeat         2.0e5;   // J/kg
    }
}
```

### Modified Wall Function Implementation

```cpp
// In wallBoilingFvPatchScalarField.C
void wallBoilingFvPatchScalarField::updateCoeffs()
{
    // Get basic wall function values
    const fvPatchScalarField& Tw = this->patch().lookupField("T");
    const fvPatchScalarField& alpha = this->patch().lookupField("alpha");

    // Calculate boiling parameters
    forAll(Tw, faceI)
    {
        // Wall superheat
        scalar dT = Tw[faceI] - Tsat[faceI];

        // Check if boiling occurs
        if (dT > dT_onset_)
        {
            // Forced convection
            scalar h_fc = wallFunction_->heatTransferCoeff()[faceI];
            scalar q_fc = h_fc * dT;

            // Nucleate boiling using Cooper correlation
            scalar P_local = p[faceI];
            scalar q_local = q_fc + q_nb_prev_[faceI];

            scalar P_r = P_local / P_critical_;
            scalar h_nb = 55 * pow(P_r, 0.12)
                         * pow(-log10(P_r), -0.55)
                         * pow(M_, -0.5)
                         * pow(q_local, 0.67);

            scalar q_nb = h_nb * dT * dT;

            // Total heat flux
            q_total_[faceI] = q_fc + q_nb;

            // Update phase change rate
            if (alpha[faceI] < 1.0)
            {
                m_dot_[faceI] = q_nb / h_lv_;
            }
            else
            {
                m_dot_[faceI] = 0;
            }
        }
        else
        {
            // Single-phase convection only
            scalar h_fc = wallFunction_->heatTransferCoeff()[faceI];
            q_total_[faceI] = h_fc * dT;
            m_dot_[faceI] = 0;
        }
    }
}
```

### Energy Equation with Boiling

```cpp
// In TEqn.H with boiling source
fvScalarMatrix TEqn
(
    fvm::ddt(rho*cp, T)
  + fvm::div(phiCp, T)
  - fvm::laplacian(k_eff, T)
 ==
    phaseChange->Sdot()          // Phase change source
  + wallBoiling->Qdot()          // Wall boiling source
  + fvOptions(source)            // Other sources
);

// Add boiling source to energy equation
if (wallBoiling->active())
{
    TEqn += fvm::SuSp(-wallBoiling->Qdot(), T);
}

TEqn.solve();
```

### Boundary Condition Setup

```cpp
// 0/T with wall boiling
wall
{
    type            compressible::turbulentTemperatureIntensityIntensityFvPatchScalarField;
    intensity       0.05;
    value           uniform 300;  // Initial guess

    // Wall boiling parameters
    boilingModel     cooper;
    nucleationSites  1e6;
    surfaceTension   0.05;
    latentHeat       2.0e5;
    criticalHeatFlux 1.5e4;     // W/m²
}
```

### Solver Configuration

```cpp
// system/fvSolution
PIMPLE
{
    nCorrectors      3;
    nAlphaCorr      1;
    nAlphaSubCycles 2;

    maxCo           0.3;      // Conservative for boiling
    maxAlphaCo      0.3;

    pRefCell        0;
    pRefValue       1e5;
}

// Relaxation factors for boiling
relaxationFactors
{
    alpha           0.5;
    U               0.7;
    p               0.3;
    T               0.5;      // Lower for stability
}
```

---

## 6. Verification and Validation (การตรวจสอบและยืนยัน)

### Boiling Heat Transfer Coefficient Validation

```cpp
// Compare CFD results with correlations
void validateBoilingHeatTransfer()
{
    // Get wall data
    scalarField Tw = patch.T();
    scalarField Tl = patch.Tl();
    scalarField q_wall = patch.heatFlux();

    // Calculate experimental values
    scalarField dT = Tw - T_sat;
    scalarField h_exp = q_wall / dT;

    // Calculate correlation values
    scalarField h_cooper;
    forAll(h_exp, faceI)
    {
        scalar P_local = patch.p()[faceI];
        scalar q_local = q_wall[faceI];

        scalar P_r = P_local / 4.9e6;  // P_critical
        h_cooper[faceI] = 55 * pow(P_r, 0.12)
                         * pow(-log10(P_r), -0.55)
                         * pow(0.0726, -0.5)
                         * pow(q_local, 0.67);
    }

    // Calculate error
    scalar error = 0;
    forAll(h_exp, faceI)
    {
        error += mag(h_exp[faceI] - h_cooper[faceI]) / h_exp[faceI];
    }
    error /= h_exp.size();

    Info << "Boiling heat transfer validation:" << endl;
    Info << "  Average error: " << 100*error << "%" << endl;
}
```

### CHF Prediction Verification

```cpp
// Check for critical heat flux conditions
void checkCHF()
{
    scalar q_chf = 15e3;  // 15 kW/m² for R410A

    forAll(patch().faceLabels(), faceI)
    {
        if (patch().heatFlux()[faceI] > q_chf)
        {
            Warning << "CHF exceeded at face " << faceI
                    << ": q = " << patch().heatFlux()[faceI]
                    << " W/m²" << endl;

            // Implement dryout model
            implementDryout(faceI);
        }
    }
}
```

### Bubble Dynamics Validation

```cpp
// Monitor bubble statistics
void monitorBubbleDynamics()
{
    // Calculate bubble departure frequency
    scalar t0 = runTime.startTime().value();
    scalar t_current = runTime.value();

    if (bubbleDepartureTimes_.size() > 10)
    {
        scalar dt_avg = 0;
        for (label i = 1; i < bubbleDepartureTimes_.size(); i++)
        {
            dt_avg += bubbleDepartureTimes_[i] - bubbleDepartureTimes_[i-1];
        }
        dt_avg /= bubbleDepartureTimes_.size() - 1;

        scalar f_avg = 1.0 / dt_avg;

        Info << "Average bubble departure frequency: " << f_avg << " Hz" << endl;

        // Expected: 50-100 Hz for R410A
        if (f_avg < 50 || f_avg > 100)
        {
            Warning << "Bubble frequency outside expected range" << endl;
        }
    }
}
```

---

## 7. Common Issues and Solutions (ปัญหาทั่วไปและวิธีแก้ไข)

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Overprediction of heat transfer** | Too high nucleation site density | Reduce n to 1e5-1e6 sites/m² |
| **Temperature oscillations** | Unstable bubble dynamics | Reduce time step, add damping |
| **No boiling observed** | Wall temperature too low | Increase heat flux, check Tsat |
| **Unrealistic bubble sizes** | Wrong departure diameter model | Use R410A-specific correlations |
| **CHF not predicted** | Missing critical heat flux model | Implement Kutateladze correlation |

---

## 📋 Key Takeaways (สรุปสิ่งสำคัญ)

### Core Concepts
1. **R410A has enhanced boiling** due to lower surface tension and density ratio
2. **Boiling requires partitioning** into forced convection + nucleate components
3. **Critical heat flux** must be predicted to avoid dryout
4. **Bubble dynamics** affect local heat transfer coefficients

### Implementation Checklist
- ✅ Configure wall boiling model with R410A properties
- ✅ Implement Cooper or Gorenflo correlation for h_nb
- ✅ Partition heat flux into convective and boiling components
- ✅ Monitor for critical heat flux conditions
- ✅ Validate with experimental correlations

### Best Practices
- Start with single-phase validation before adding boiling
- Use conservative time steps (Co < 0.3) for stability
- Monitor bubble departure frequency (50-100 Hz for R410A)
- Implement CHF limits to prevent numerical instability
- Compare with pool boiling correlations for validation

---

## 📖 Further Reading

### Within This Module
- **[10_R410A_Phase_Change_Physics.md](10_R410A_Phase_Change_Physics.md)** — Basic phase change physics
- **[12_Film_Evaporation_R410A.md](12_Film_Evaporation_R410A.md)** — Thin film evaporation modeling
- **[13_Dryout_Prediction_R410A.md](13_Dryout_Prediction_R410A.md)** — Dryout mechanism and prediction

### External Resources
- **Cooper (1984)** — Heat transfer correlation for refrigerants
- **Gorenflo (1993)** — Pool boiling correlation database
- **Kandlikar (2001)** — Enhancement methods for boiling heat transfer
- **Collier & Thome (1994)** — Convective Boiling and Condensation