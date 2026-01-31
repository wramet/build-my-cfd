# Phase Change Model Verification for R410A (การตรวจสอบรูปแบบการเปลี่ยนเฟสของ R410A)

## Overview

This test case validates the phase change model implementation through a static evaporation scenario in a closed volume, ensuring mass conservation, energy balance, and phase transition accuracy.

## Test Case Configuration

### Geometry
- **Container:** Cubic volume 0.1m × 0.1m × 0.1m
- **Mesh:** Uniform 20×20×20 cells (8000 total)
- **Initial conditions:**
  - Liquid R410A: 60% of volume, 8°C
  - Vapor R410A: 40% of volume, 8°C
  - Pressure: 1.5 MPa
- **Boundary conditions:**
  - All walls: Adiabatic, no-slip
  - Closed system (no mass transfer)

### Phase Change Model

### 1. Mass Transfer Rate

The evaporation rate is based on the Hertz-Knudsen equation:

$$
\dot{m} = C \sqrt{\frac{M}{2\pi RT}} (p_{sat} - p_v)
$$

Where:
- $C$ = condensation coefficient (0.01-1.0)
- $M$ = molar mass
- $R$ = universal gas constant
- $T$ = temperature
- $p_{sat}$ = saturation pressure
- $p_v$ = vapor pressure

### 2. Energy Balance

Phase change includes latent heat:

$$
\frac{\partial}{\partial t}(\rho \alpha_h) + \nabla \cdot (\rho \alpha_h \mathbf{U}) = \dot{m}_{evap} - \dot{m}_{cond}
$$

$$
\frac{\partial}{\partial t}(\rho c_p T) + \nabla \cdot (\rho c_p \mathbf{U} T) = \nabla \cdot (k \nabla T) - \dot{m}_{evap} L_v
$$

### 3. OpenFOAM Implementation

```cpp
// Phase change source terms
fvScalarMatrix evaporationRate
(
    fvm::ddt(alpha1) + fvm::div(phi1, alpha1)
    ==
    fvm::Sp(-evaporationModel.mDot(), alpha1)
    + fvm::Sp(evaporationModel.mDot(), alpha2)
);

evaporationRate.solve();

// Energy equation with phase change
fvScalarMatrix TEqn
(
    fvm::ddt(rho*cp, T) + fvm::div(phi, T)
    - fvm::laplacian(alpha1*rho1*cp1/kappa1, T)
    - fvm::laplacian(alpha2*rho2*cp2/kappa2, T)
    ==
    fvm::Sp(-evaporationModel.mDot()*h_fg, T)
);

TEqn.solve();
```

### 4. Phase Change Model Class

```cpp
class R410APhaseChangeModel {
private:
    // Model parameters
    scalar condensationCoeff;
    scalar relaxationFactor;

    // Thermodynamic properties
    autoPtr<R410APropertyCalculator> properties;

    // Mesh fields
    volScalarField& alpha1;
    volScalarField& alpha2;
    volScalarField& T;
    volScalarField& p;

    // Source terms
    volScalarField mDotEvap;
    volScalarField mDotCond;

public:
    // Constructor
    R410APhaseChangeModel(
        volScalarField& alpha1,
        volScalarField& alpha2,
        volScalarField& T,
        volScalarField& p
    );

    // Update phase change rate
    void update();

    // Get source terms
    const volScalarField& mDotEvaporation() const { return mDotEvap; }
    const volScalarField& mDotCondensation() const { return mDotCond; }

    // Access properties
    const R410APropertyCalculator& thermodynamics() const { return *properties; }

private:
    // Calculate saturation properties
    void updateSaturationProperties();

    // Calculate mass transfer rates
    void calculateMassTransfer();

    // Check phase equilibrium
    bool isAtEquilibrium() const;

    // Apply relaxation
    void applyRelaxation();
};
```

### 5. Monitoring and Validation

```cpp
// Mass conservation monitoring
scalar totalMass = gSum(alpha1.mesh().V() * alpha1) + gSum(alpha2.mesh().V() * alpha2);

// Energy conservation monitoring
scalar totalEnergy = gSum(alpha1.mesh().V() * alpha1 * h1) + gSum(alpha2.mesh().V() * alpha2 * h2);

// Phase fraction monitoring
scalar liquidFraction = gSum(alpha1 * alpha1.mesh().V()) / gSum(alpha1.mesh().V());
scalar vaporFraction = gSum(alpha2 * alpha2.mesh().V()) / gSum(alpha2.mesh().V());

// Write monitoring data
if (runTime.time().value() % 1.0 < SMALL) {
    Info << "Time: " << runTime.time().value() << " s" << endl;
    Info << "Total mass: " << totalMass << " kg" << endl;
    Info << "Liquid fraction: " << liquidFraction << endl;
    Info << "Vapor fraction: " << vaporFraction << endl;
    Info << "Total energy: " << totalEnergy << " J" << endl;
}
```

## Test Cases Matrix

| Case ID | Initial Quality | Temperature (°C) | Pressure (MPa) | Relaxation Factor |
|---------|----------------|-----------------|---------------|-------------------|
| PC1     | 0.0            | 8               | 1.5           | 1.0               |
| PC2     | 0.2            | 8               | 1.5           | 1.0               |
| PC3     | 0.5            | 8               | 1.5           | 1.0               |
| PC4     | 0.8            | 8               | 1.5           | 1.0               |
| PC5     | 0.5            | 8               | 1.5           | 0.5               |
| PC6     | 0.5            | 8               | 1.5           | 0.1               |

## Expected Results

### Mass Conservation Verification

| Case ID | Initial Mass (kg) | Final Mass (kg) | Mass Error (%) | Convergence Steps |
|---------|------------------|----------------|----------------|-------------------|
| PC1     | 2.547           | 2.547          | 0.000          | 0                 |
| PC2     | 2.547           | 2.547          | 0.001          | 150               |
| PC3     | 2.547           | 2.547          | 0.002          | 300               |
| PC4     | 2.547           | 2.547          | 0.002          | 450               |
| PC5     | 2.547           | 2.547          | 0.001          | 600               |
| PC6     | 2.547           | 2.547          | 0.003          | 1200              |

### Energy Conservation Verification

| Case ID | Initial Energy (kJ) | Final Energy (kJ) | Energy Error (%) | Equilibrium Time (s) |
|---------|---------------------|------------------|------------------|---------------------|
| PC1     | 845.2              | 845.2            | 0.000            | 0.0                 |
| PC2     | 845.2              | 845.1            | 0.012            | 15.0                |
| PC3     | 845.2              | 845.0            | 0.024            | 30.0                |
| PC4     | 845.2              | 844.9            | 0.036            | 45.0                |
| PC5     | 845.2              | 845.1            | 0.012            | 60.0                |
| PC6     | 845.2              | 845.0            | 0.024            | 120.0               |

### Phase Distribution Evolution

```python
# Phase fraction evolution over time
time = [0, 5, 10, 15, 20, 25, 30]
liquid_fraction = [0.6, 0.55, 0.52, 0.50, 0.495, 0.492, 0.491]
vapor_fraction = [0.4, 0.45, 0.48, 0.50, 0.505, 0.508, 0.509]

# Temperature evolution
temperature = [8, 10, 12, 14, 15, 15.2, 15.3]
```

### Verification Criteria
- **Mass conservation:** Error < 1% for all cases
- **Energy conservation:** Error < 2% for all cases
- **Phase equilibrium:** Reached within 1000 steps
- **Stability:** No oscillations in mass/energy

## Test Script

```python
#!/usr/bin/env python3
# R410A Phase Change Model Verification Script
# Author: CFD Engine Development Team
# Date: 2026-01-28

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from CoolProp.CoolProp import PropsSI

class PhaseChangeValidator:
    def __init__(self):
        self.container_volume = 0.1**3  # m³
        self.T_sat = 10 + 273.15  # K
        self.P_sat = 572.5e3     # Pa

    def r410a_properties(self, T, P, quality):
        """Get R410A properties"""
        # Liquid properties
        rho_l = PropsSI('D', 'P', P, 'T', T, 'R410A')
        cp_l = PropsSI('C', 'P', P, 'T', T, 'R410A')
        h_l = PropsSI('H', 'P', P, 'T', T, 'R410A') / 1000  # kJ/kg

        # Vapor properties
        rho_v = PropsSI('D', 'P', P, 'T', T, 'R410A')
        cp_v = PropsSI('C', 'P', P, 'T', T, 'R410A')
        h_v = PropsSI('H', 'P', P, 'T', T, 'R410A') / 1000  # kJ/kg

        # Latent heat
        h_fg = PropsSI('H', 'P', P, 'Q', 1.0, 'R410A') / 1000 - \
               PropsSI('H', 'P', P, 'Q', 0.0, 'R410A') / 1000

        return {
            'rho_l': rho_l, 'cp_l': cp_l, 'h_l': h_l,
            'rho_v': rho_v, 'cp_v': cp_v, 'h_v': h_v,
            'h_fg': h_fg
        }

    def calculate_equilibrium(self, initial_quality, relaxation_factor):
        """Calculate phase change to equilibrium"""
        # Initial conditions
        T_initial = 8 + 273.15  # K
        P_initial = 1.5e6      # Pa

        # Get properties
        props = self.r410a_properties(T_initial, P_initial, initial_quality)

        # Initial masses
        rho_l = props['rho_l']
        rho_v = props['rho_v']

        m_l_initial = initial_quality * self.container_volume * rho_l
        m_v_initial = (1 - initial_quality) * self.container_volume * rho_v

        # Energy balance
        E_total = m_l_initial * props['h_l'] + m_v_initial * props['h_v']

        # Iterative solution
        quality_history = [initial_quality]
        energy_history = [E_total / 1000]  # kJ
        mass_history = [m_l_initial + m_v_initial]

        quality = initial_quality
        time_steps = 0
        max_steps = 2000
        tolerance = 1e-6

        while time_steps < max_steps:
            # Check equilibrium
            p_vapor = P_initial  # Simplified - should calculate from ideal gas
            p_sat = PropsSI('P', 'T', T_initial, 'Q', quality, 'R10A')

            if abs(p_vapor - p_sat) < tolerance:
                break

            # Update quality (simplified model)
            if p_vapor > p_sat:
                # Condensation
                dm = relaxation_factor * 0.01 * min(1-quality, 0.1)
                quality -= dm
            else:
                # Evaporation
                dm = relaxation_factor * 0.01 * min(quality, 0.1)
                quality += dm

            quality_history.append(quality)

            # Update masses
            m_l = quality * self.container_volume * rho_l
            m_v = (1 - quality) * self.container_volume * rho_v

            # Check mass conservation
            total_mass = m_l + m_v
            mass_error = abs(total_mass - mass_history[0]) / mass_history[0] * 100
            mass_history.append(total_mass)

            # Check energy conservation
            E_current = m_l * props['h_l'] + m_v * props['h_v']
            energy_error = abs(E_current - energy_history[0]) / energy_history[0] * 100
            energy_history.append(E_current / 1000)

            time_steps += 1

            if time_steps % 100 == 0:
                print(f"Step {time_steps}: q={quality:.4f}, "
                      f"mass_err={mass_error:.4f}%, energy_err={energy_error:.4f}%")

        return {
            'quality_history': quality_history,
            'mass_history': mass_history,
            'energy_history': energy_history,
            'convergence_steps': time_steps,
            'final_quality': quality
        }

    def run_validation(self):
        """Run phase change validation suite"""
        test_cases = [
            {'initial_quality': 0.0, 'relaxation': 1.0},
            {'initial_quality': 0.2, 'relaxation': 1.0},
            {'initial_quality': 0.5, 'relaxation': 1.0},
            {'initial_quality': 0.8, 'relaxation': 1.0},
            {'initial_quality': 0.5, 'relaxation': 0.5},
            {'initial_quality': 0.5, 'relaxation': 0.1}
        ]

        print("R410A Phase Change Model Validation")
        print("="*50)
        print(f"Container volume: {self.container_volume:.6f} m³")
        print(f"Saturation temperature: {self.T_sat-273.15:.1f}°C")
        print(f"Saturation pressure: {self.P_sat/1000:.1f} kPa")
        print()

        results = []

        for i, case in enumerate(test_cases):
            print(f"Running Case {i+1}: "
                  f"q0={case['initial_quality']:.1f}, "
                  f"relax={case['relaxation']}")

            result = self.calculate_equilibrium(
                case['initial_quality'],
                case['relaxation']
            )

            # Calculate errors
            initial_mass = result['mass_history'][0]
            final_mass = result['mass_history'][-1]
            mass_error = abs(final_mass - initial_mass) / initial_mass * 100

            initial_energy = result['energy_history'][0]
            final_energy = result['energy_history'][-1]
            energy_error = abs(final_energy - initial_energy) / initial_energy * 100

            results.append({
                'Case': i+1,
                'Initial_Quality': case['initial_quality'],
                'Relaxation_Factor': case['relaxation'],
                'Convergence_Steps': result['convergence_steps'],
                'Final_Quality': result['final_quality'],
                'Mass_Error': mass_error,
                'Energy_Error': energy_error,
                'Time_to_Equilibrium': result['convergence_steps'] * 0.05  # 0.05 s per step
            })

            print(f"  Converged in {result['convergence_steps']} steps")
            print(f"  Final quality: {result['final_quality']:.4f}")
            print(f"  Mass error: {mass_error:.4f}%")
            print(f"  Energy error: {energy_error:.4f}%")
            print()

        return results

    def plot_results(self, results):
        """Plot validation results"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Mass conservation
        ax = axes[0, 0]
        cases = [r['Case'] for r in results]
        mass_errors = [r['Mass_Error'] for r in results]
        ax.bar(cases, mass_errors)
        ax.axhline(y=1.0, color='r', linestyle='--')
        ax.set_xlabel('Case Number')
        ax.set_ylabel('Mass Error (%)')
        ax.set_title('Mass Conservation')
        ax.grid(True)

        # Energy conservation
        ax = axes[0, 1]
        energy_errors = [r['Energy_Error'] for r in results]
        ax.bar(cases, energy_errors)
        ax.axhline(y=2.0, color='r', linestyle='--')
        ax.set_xlabel('Case Number')
        ax.set_ylabel('Energy Error (%)')
        ax.set_title('Energy Conservation')
        ax.grid(True)

        # Convergence steps
        ax = axes[1, 0]
        convergence_steps = [r['Convergence_Steps'] for r in results]
        ax.bar(cases, convergence_steps)
        ax.set_xlabel('Case Number')
        ax.set_ylabel('Steps to Convergence')
        ax.set_title('Convergence Performance')
        ax.grid(True)

        # Final quality
        ax = axes[1, 1]
        final_qualities = [r['Final_Quality'] for r in results]
        ax.bar(cases, final_qualities)
        ax.set_xlabel('Case Number')
        ax.set_ylabel('Final Quality')
        ax.set_title('Phase Equilibrium')
        ax.grid(True)

        plt.tight_layout()
        plt.savefig('phase_change_validation.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    validator = PhaseChangeValidator()
    results = validator.run_validation()

    # Save results
    df = pd.DataFrame(results)
    df.to_csv('r410a_phase_change_results.csv', index=False)

    validator.plot_results(results)

    print("Validation results saved to 'r410a_phase_change_results.csv'")
    print("Plot saved to 'phase_change_validation.png'")

if __name__ == "__main__":
    main()
```

## Verification Gate Checklist

- [ ] **Mass conservation** error < 1% for all cases
- [ ] **Energy conservation** error < 2% for all cases
- [ ] **Phase equilibrium** reached within reasonable time
- [ ] **Stability** maintained across all relaxation factors
- [ ] **Convergence** achieved without oscillations
- [ ] **Source terms** properly balanced
- [ ] **Material properties** consistent throughout simulation
- [ ] **Boundary conditions** correctly implemented for closed system

## References

1. ⭐ **Hertz-Knudsen equation** - `openfoam_temp/src/heatTransferModels/twoPhase/phaseChange/hertzKnudsen/hertzKnudsen.H`
2. ⭐ **Mass transfer model** - `openfoam_temp/src/thermophysicalModels/twoPhaseMixture/twoPhaseMixtureProperties/phaseChange/phaseChangeModel.H`
3. ⭐ **Energy equation coupling** - `openfoam_temp/src/finiteVolume/cfdModels/thermo/twoPhaseEvaporation/twoPhaseEvaporation.H`
4. **ASHRAE Handbook** - Phase change correlations
5. **Bird, Stewart, Lightfoot** - Transport Phenomena fundamentals

## Common Issues

### 1. Mass Source Imbalance
- **Problem:** Mass not conserved during phase change
- **Fix:** Ensure source terms are equal and opposite
- **Solution:** Use `fvm::Sp(-mDot, alpha1)` and `fvm::Sp(mDot, alpha2)`

### 2. Energy Dissipation
- **Problem:** Energy not conserved during simulation
- **Fix:** Check latent heat inclusion in energy equation
- **Solution:** Include `-mDot * h_fg` source term in energy equation

### 3. Slow Convergence
- **Problem:** System takes too long to reach equilibrium
- **Fix:** Optimize relaxation factor
- **Solution:** Use adaptive relaxation based on residual history

## Next Steps

1. **Dynamic phase change** - Add heat source/sink to drive evaporation
2. **Interface tracking** - Improve sharp interface representation
3. **Multi-component mixtures** - Validate with oil-contaminated R410A
4. **Experimental data** - Compare with actual phase change measurements

---

**Created:** 2026-01-28
**Version:** 1.0
**Status:** Ready for validation