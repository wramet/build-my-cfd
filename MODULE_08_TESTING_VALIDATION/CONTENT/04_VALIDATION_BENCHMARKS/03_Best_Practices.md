# Best Practices

Best Practices for Validation

---

## Learning Objectives

After completing this section, you will be able to:

- **Establish** proper documentation standards for validation cases
- **Organize** validation case directories for maximum reproducibility
- **Perform** mesh independence studies to verify solution convergence
- **Conduct** sensitivity analysis to understand parameter impacts
- **Report** validation errors using appropriate metrics and visualizations
- **Define** acceptance criteria for validation success
- **Apply** version control practices to validation workflows
- **Identify** and avoid common validation pitfalls

---

## Overview

> Follow best practices for **reliable, reproducible validation**

Validation is not just about comparing numbers—it's about establishing a rigorous, repeatable process that others can trust. Best practices ensure your validation work withstands scrutiny and provides meaningful confidence in your CFD simulations. This section covers the essential practices that separate professional validation from ad-hoc comparisons.

---

## 1. Documentation Standards

### Why Documentation Matters

Proper documentation transforms validation from a personal exercise into a scientific contribution. Without documentation, validation results cannot be reproduced, verified, or built upon by others. Documentation is the foundation of scientific credibility in CFD.

### Essential Documents

| Document | Purpose | Key Contents |
|----------|---------|--------------|
| **README.md** | Quick case overview | Case description, geometry, BCs, solver settings |
| **Validation Report** | Detailed analysis | Methodology, results, discussion, conclusions |
| **Reference Data** | Data provenance | Sources, experimental conditions, uncertainty estimates |
| **Change Log** | Version history | Modifications made during validation process |

### README Template

```markdown
# Validation Case: [Name]

## Case Description
[Brief physical description of the problem]

## Geometry
- Dimensions: [specify]
- Domain: [specify]
- Reynolds number: [value]

## Boundary Conditions
- Inlet: [specify]
- Outlet: [specify]
- Walls: [specify]

## Solver Settings
- Solver: [name]
- Schemes: [specify]
- Tolerances: [specify]

## Reference Data
- Source: [citation/link]
- Conditions: [specify]
- Uncertainty: ±[value]

## Results
- Validation metrics: [summary]
- Status: [PASS/FAIL/INCONCLUSIVE]
```

---

## 2. Case Organization

### Directory Structure

A well-organized case directory enables reproducibility and collaboration. The recommended structure separates input files, reference data, and results clearly.

```
validation/
├── README.md                           # Case overview and quick reference
├── case/                               # OpenFOAM case directory
│   ├── Allrun                          # Automated execution script
│   ├── Allclean                        # Cleanup script
│   ├── system/
│   │   ├── controlDict                 # Time/solver control
│   │   ├── fvSchemes                   # Discretization schemes
│   │   └── fvSolution                  # Linear solver settings
│   ├── 0/                             # Initial/boundary conditions
│   └── constant/
│       └── polyMesh/                   # Mesh files
├── experimental/                       # Reference experimental data
│   ├── README.md                       # Data source documentation
│   ├── raw_data/                       # Original data files
│   └── processed_data.csv              # Cleaned, formatted data
├── results/                           # Validation results
│   ├── plots/                          # Comparison plots
│   ├── tables/                         # Numerical comparisons
│   └── convergence/                    # Mesh/time-step studies
├── scripts/                           # Helper scripts
│   ├── postProcess.py                 # Automated post-processing
│   └── computeMetrics.py              # Error metrics
└── validation_report.md               # Detailed validation report
```

### Why This Structure Works

- **Separation of concerns:** Input, reference, and results are clearly separated
- **Reproducibility:** `Allrun` script contains exact execution commands
- **Transparency:** Raw and processed data are both preserved
- **Automation:** Scripts enable consistent, repeatable analysis

---

## 3. Mesh Independence Study

### What is Mesh Independence?

Mesh independence (also called grid convergence) verifies that your solution no longer changes significantly with mesh refinement. If results change when you refine the mesh, your solution is not mesh-independent and cannot be trusted for validation.

### Why It Matters

- **Verification prerequisite:** Must establish mesh independence before validation
- **Accuracy assurance:** Ensures numerical errors are acceptably small
- **Resource optimization:** Identifies the coarsest mesh that gives acceptable results
- **Credibility:** Peer reviewers and stakeholders expect mesh studies

### Systematic Approach

The following script automates a mesh refinement study across three resolution levels:

```bash
#!/bin/bash
# meshStudy.sh - Automated mesh independence study
# Purpose: Verify solution convergence with mesh refinement

echo "Starting mesh independence study..."
echo "====================================="

# Define mesh refinement levels
# Add more levels for higher-order convergence studies
for level in coarse medium fine; do
    echo "Processing $level mesh..."
    
    # Create independent case directory
    cp -r case case_$level
    cd case_$level
    
    # Use appropriate mesh dict for this level
    blockMesh -dict system/blockMeshDict.$level
    
    # Run solver (adjust as needed)
    simpleFoam > log.simpleFoam 2>&1
    
    # Extract probe data for comparison
    postProcess -func 'probes' -noZero
    
    # Store key quantities for convergence analysis
    postProcess -func "forceCoeffs" -noZero
    
    cd ..
    echo "Completed $level mesh"
done

# Compare results across mesh levels
python3 scripts/plotConvergence.py \
    --dirs case_coarse case_medium case_fine \
    --output results/convergence/

echo "Mesh study complete. Review convergence plots."
```

### Interpreting Results

Plot your quantity of interest (e.g., drag coefficient, velocity at a point) against cell count or characteristic mesh size:

**Acceptable convergence:** Results change by less than 1-2% between the two finest meshes

```python
# Example convergence check
def check_mesh_convergence(values, tolerance=0.02):
    """
    Check if last two values are within tolerance
    values: list of results from coarse to fine
    tolerance: acceptable relative change (default 2%)
    """
    if len(values) < 2:
        return False, "Need at least 2 mesh levels"
    
    relative_change = abs(values[-1] - values[-2]) / abs(values[-2])
    
    if relative_change <= tolerance:
        return True, f"Converged: {relative_change:.1%} change"
    else:
        return False, f"Not converged: {relative_change:.1%} change > {tolerance:.1%}"
```

> **Cross-reference:** See [02_Mesh_BC_Verification.md](02_Mesh_BC_Verification.md) for detailed mesh quality analysis and GCI (Grid Convergence Index) calculations.

---

## 4. Sensitivity Analysis

### Understanding Parameter Sensitivity

Sensitivity analysis identifies which numerical parameters most affect your results. This helps you:
- Focus computational resources on critical parameters
- Understand uncertainty sources in your simulation
- Build confidence through systematic testing

### Key Parameters to Test

| Parameter | Typical Range | Default | Impact |
|-----------|---------------|---------|--------|
| **Mesh size** | 10k - 1M cells | 100k | High - affects accuracy and runtime |
| **Time step (CFL)** | 0.1 - 10 | 1.0 | High - affects temporal accuracy |
| **Solver tolerance** | 1e-6 - 1e-4 | 1e-5 | Medium - affects convergence |
| **Relaxation factors** | 0.3 - 0.9 | 0.7 | Medium - affects stability vs speed |
| **Turbulence model** | k-ε, k-ω SST, LES | k-ω SST | High - affects physics modeling |
| **Near-wall treatment** | Wall functions, low-Re | Depends on y+ | High - affects boundary layer resolution |

### Practical Sensitivity Study Template

```python
# sensitivity_study.py
import numpy as np
import pandas as pd
from itertools import product

def run_sensitivity_analysis(base_case, parameters):
    """
    Run parameter sweep and collect results
    
    base_case: dict with base case configuration
    parameters: dict with parameter ranges to test
    """
    results = []
    
    # Generate all parameter combinations
    keys = parameters.keys()
    values = parameters.values()
    combinations = [dict(zip(keys, v)) for v in product(*values)]
    
    for i, params in enumerate(combinations):
        print(f"Run {i+1}/{len(combinations)}: {params}")
        
        # Modify case with current parameters
        case_config = {**base_case, **params}
        
        # Run simulation (pseudo-code)
        result = run_openfoam_case(case_config)
        
        # Store results
        results.append({
            'params': params,
            'output': result,
            'run_id': i
        })
    
    return pd.DataFrame(results)

# Example usage
parameters = {
    'mesh_level': ['coarse', 'medium', 'fine'],
    'relaxation_factor': [0.5, 0.7, 0.9],
    'solver_tolerance': [1e-6, 1e-5, 1e-4]
}

results = run_sensitivity_analysis(base_case, parameters)
results.to_csv('results/sensitivity_study.csv', index=False)
```

### Analyzing Sensitivity Results

```python
# Compute sensitivity metrics
def compute_sensitivity(df, param_name, output_metric):
    """
    Compute normalized sensitivity coefficient
    S = (∂y/∂x) × (x/y)
    """
    base_value = df[df[param_name] == default[param_name]][output_metric].mean()
    
    sensitivities = []
    for value in df[param_name].unique():
        subset = df[df[param_name] == value]
        output_mean = subset[output_metric].mean()
        
        sens = ((output_mean - base_value) / base_value) / \
               ((value - default[param_name]) / default[param_name])
        
        sensitivities.append({
            'parameter': param_name,
            'value': value,
            'sensitivity': sens
        })
    
    return pd.DataFrame(sensitivities)
```

**Interpretation:**
- \|S\| > 1: High sensitivity - focus efforts here
- 0.1 < \|S\| < 1: Moderate sensitivity
- \|S\| < 0.1: Low sensitivity - default value acceptable

---

## 5. Error Reporting and Metrics

### Choosing Appropriate Metrics

No single metric tells the complete story. Use multiple complementary metrics to assess validation from different perspectives.

### Metric Categories

**1. Error Magnitude Metrics**
- **RMSE** (Root Mean Square Error): Penalizes large errors
- **MAE** (Mean Absolute Error): More interpretable than RMSE
- **Max Error:** Identifies worst-case discrepancies

**2. Correlation Metrics**
- **R²** (Coefficient of Determination): Measures correlation strength
- **Pearson r:** Linear correlation coefficient

**3. Relative Error Metrics**
- **MAPE** (Mean Absolute Percentage Error): Scale-independent
- **Normalized RMSE:** Accounts for data range

### Implementation with Context

The following Python script computes a comprehensive set of validation metrics:

```python
# metrics.py
"""
Validation Metrics Computation
Purpose: Calculate multiple error metrics for validation assessment

Usage:
    metrics = compute_metrics(simulation_data, experimental_data)
    plot_validation(simulation_data, experimental_data, metrics)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def compute_metrics(sim, exp, verbose=True):
    """
    Compute comprehensive validation metrics.
    
    Parameters:
    -----------
    sim : array-like
        Simulation results
    exp : array-like
        Experimental/reference data
    verbose : bool
        Print detailed metric breakdown
    
    Returns:
    --------
    dict : Dictionary containing all computed metrics
    """
    sim = np.asarray(sim)
    exp = np.asarray(exp)
    
    # Basic error metrics
    rmse = np.sqrt(np.mean((sim - exp)**2))
    mae = np.mean(np.abs(sim - exp))
    max_error = np.max(np.abs(sim - exp))
    
    # Relative errors (handle near-zero values)
    mask = np.abs(exp) > 1e-10  # Avoid division by zero
    if np.any(mask):
        mape = np.mean(np.abs((sim[mask] - exp[mask]) / exp[mask])) * 100
    else:
        mape = np.nan
    
    # Correlation metrics
    r2 = 1 - np.sum((sim - exp)**2) / np.sum((exp - np.mean(exp))**2)
    pearson_r, p_value = stats.pearsonr(sim, exp)
    
    # Normalized metrics
    data_range = np.max(exp) - np.min(exp)
    nrmse = rmse / data_range if data_range > 0 else np.nan
    
    metrics = {
        'RMSE': rmse,
        'MAE': mae,
        'Max_Error': max_error,
        'MAPE (%)': mape,
        'R2': r2,
        'Pearson_r': pearson_r,
        'P_value': p_value,
        'NRMSE': nrmse
    }
    
    if verbose:
        print("Validation Metrics:")
        print("-" * 40)
        for key, value in metrics.items():
            if key == 'P_value':
                print(f"{key}: {value:.2e}")
            elif isinstance(value, float):
                print(f"{key}: {value:.4f}")
        
        # Interpretation
        print("\nInterpretation:")
        print(f"R² = {r2:.3f}: ", end="")
        if r2 > 0.95:
            print("Excellent correlation")
        elif r2 > 0.85:
            print("Good correlation")
        elif r2 > 0.7:
            print("Moderate correlation")
        else:
            print("Poor correlation - investigate discrepancies")
    
    return metrics

def plot_validation(sim, exp, x_coord=None, title="Validation Results"):
    """
    Create comprehensive validation plots.
    
    Parameters:
    -----------
    sim : array-like
        Simulation results
    exp : array-like
        Experimental/reference data
    x_coord : array-like, optional
        X-coordinate for profile plots (e.g., spatial position)
    title : str
        Plot title
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # 1. Profile comparison
    ax1 = axes[0, 0]
    if x_coord is None:
        x_coord = np.arange(len(sim))
    ax1.plot(x_coord, exp, 'ko-', label='Experiment', linewidth=2, markersize=4)
    ax1.plot(x_coord, sim, 'r--', label='Simulation', linewidth=2)
    ax1.set_xlabel('Position')
    ax1.set_ylabel('Quantity')
    ax1.set_title('Profile Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Correlation scatter plot
    ax2 = axes[0, 1]
    ax2.scatter(exp, sim, alpha=0.6, edgecolors='k', linewidth=0.5)
    
    # Perfect correlation line
    min_val = min(np.min(exp), np.min(sim))
    max_val = max(np.max(exp), np.max(sim))
    ax2.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect match')
    
    ax2.set_xlabel('Experimental Data')
    ax2.set_ylabel('Simulation Data')
    ax2.set_title('Correlation Plot')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    # Add R² annotation
    r2 = 1 - np.sum((sim - exp)**2) / np.sum((exp - np.mean(exp))**2)
    ax2.text(0.05, 0.95, f'R² = {r2:.3f}', 
             transform=ax2.transAxes, fontsize=12,
             verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 3. Error distribution
    ax3 = axes[1, 0]
    errors = sim - exp
    ax3.hist(errors, bins=20, edgecolor='black', alpha=0.7)
    ax3.axvline(0, color='r', linestyle='--', linewidth=2)
    ax3.set_xlabel('Error (Simulation - Experiment)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Error Distribution')
    ax3.grid(True, alpha=0.3)
    
    # Add statistics
    mean_error = np.mean(errors)
    std_error = np.std(errors)
    ax3.text(0.95, 0.95, f'Mean: {mean_error:.3f}\nStd: {std_error:.3f}',
             transform=ax3.transAxes, fontsize=10,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # 4. Relative error plot
    ax4 = axes[1, 1]
    mask = np.abs(exp) > 1e-10
    if np.any(mask):
        rel_error = np.abs((sim[mask] - exp[mask]) / exp[mask]) * 100
        ax4.plot(x_coord[mask], rel_error, 'o-', color='purple', linewidth=2)
        ax4.axhline(5, color='g', linestyle='--', linewidth=1.5, label='5% threshold')
        ax4.set_xlabel('Position')
        ax4.set_ylabel('Relative Error (%)')
        ax4.set_title('Relative Error Distribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_yscale('log')  # Log scale for wide error ranges
    else:
        ax4.text(0.5, 0.5, 'Cannot compute relative error\n(near-zero experimental values)',
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_xticks([])
        ax4.set_yticks([])
    
    plt.tight_layout()
    return fig

# Example usage
if __name__ == "__main__":
    # Load data (replace with actual data loading)
    # simulation = np.loadtxt('results/simulation_profile.csv')
    # experiment = np.loadtxt('experimental/data.csv')
    # position = np.loadtxt('experimental/positions.csv')
    
    # For demonstration, create synthetic data
    position = np.linspace(0, 1, 50)
    experiment = np.sin(2 * np.pi * position)
    simulation = experiment + np.random.normal(0, 0.1, len(position))
    
    # Compute metrics
    metrics = compute_metrics(simulation, experiment)
    
    # Create plots
    fig = plot_validation(simulation, experiment, position, 
                         title="Backward-Facing Step Validation")
    plt.savefig('results/validation_comparison.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved to results/validation_comparison.png")
```

### Visualization Best Practices

1. **Always show both datasets** on the same plot for direct comparison
2. **Include error bars** when experimental uncertainty is available
3. **Use consistent scales** across multiple validation cases
4. **Show residuals** (simulation - experiment) to highlight discrepancies
5. **Include statistical measures** (RMSE, R²) directly on plots
6. **Use color-blind friendly palettes** for publications

---

## 6. Acceptance Criteria

### Defining Validation Success

Clear acceptance criteria prevent subjective validation assessments. Criteria should be **defined before running simulations** based on:
- Application requirements (engineering tolerance)
- Experimental uncertainty (can't validate more accurately than data)
- Industry standards (domain-specific norms)
- Regulatory requirements (for certification cases)

### Example Acceptance Criteria

| Quantity | Metric | Pass Criteria | Typical Application |
|----------|--------|---------------|---------------------|
| **Velocity magnitude** | Relative error | < 5% | Aerodynamics |
| **Pressure drop** | Relative error | < 10% | Internal flows |
| **Temperature** | Absolute error | < 2 K | Heat transfer |
| **Wall shear stress** | Relative error | < 15% | Boundary layer studies |
| **Drag coefficient** | Relative error | < 5% | External aerodynamics |
| **Lift coefficient** | Relative error | < 10% | External aerodynamics |
| **y+ value** | Range check | 1 < y+ < 5 (low-Re) or 30 < y+ < 300 (wall func) | Turbulent flows |
| **Mass conservation** | Absolute residual | < 1e-6 | All cases |
| **Correlation (R²)** | Statistical fit | > 0.85 | All cases |

### Application-Specific Criteria

**Aerodynamics (automotive, aerospace):**
- Cd, Cl: < 5% error
- Pressure distribution: < 10% error
- Separation location: within 5% chord length

**Heat Transfer:**
- Nusselt number: < 15% error
- Temperature: < 2 K or < 5% relative
- Heat flux: < 10% error

**Chemical Reacting Flows:**
- Species concentration: < 20% error (higher due to complexity)
- Flame position: within 10% of domain length
- Ignition delay: < 25% error

### Documentation Template

```markdown
## Validation Acceptance Criteria

### Pre-defined Criteria (set before simulation)

| Quantity | Required Accuracy | Justification |
|----------|-------------------|---------------|
| Velocity | < 5% | Engineering requirement for drag prediction |
| Pressure | < 10% | Experimental uncertainty = ±8% |
| Temperature | < 2 K | Safety margin requirement |

### Results

| Quantity | Measured Error | Status | Notes |
|----------|---------------|--------|-------|
| Velocity | 3.2% | ✅ PASS | Within criterion |
| Pressure | 11.5% | ❌ FAIL | Slightly exceeds - investigate turbulence model |
| Temperature | 1.3 K | ✅ PASS | Well within criterion |

### Overall Validation Status: CONDITIONAL PASS
- Temperature: PASS
- Velocity: PASS  
- Pressure: FAIL - requires further investigation before qualification
```

---

## 7. Version Control for Validation

### Why Version Control Matters

Validation is an iterative process. Version control (Git) ensures:
- **Reproducibility:** Exact code and settings are preserved
- **Traceability:** Know which code version produced which results
- **Collaboration:** Teams can work on validation without conflicts
- **Confidence:** Roll back if changes break validation

### Git Workflow for Validation

```bash
# Initialize validation case repository
git init validation_case
cd validation_case

# Create .gitignore for OpenFOAM
cat > .gitignore << EOF
# OpenFOAM generated files
*.foam
processor*/
postProcessing/
*.png
*.pdf

# Large binary files
*.gz
*.tar

# Editor files
*.swp
*~
EOF

# Initial commit of base case
git add .
git commit -m "Initial commit: base validation case setup

- Geometry and mesh configured
- Boundary conditions set per reference
- Solver: simpleFoam with k-omega SST
- Reference data: Smith et al. (2020)"

# Create development branch for experiments
git checkout -b experimental-variants

# After mesh study
git add case_mesh_coarse/ case_mesh_medium/ case_mesh_fine/
git commit -m "Add mesh independence study results

- Coarse (50k cells): Cd = 0.312
- Medium (200k cells): Cd = 0.328  
- Fine (800k cells): Cd = 0.331
- Converged between medium and fine (0.9% change)
- Selected: medium mesh for validation runs"

# Tag validated configuration
git tag -a v1.0-validation -m "Validated configuration

Validation results:
- Velocity error: 3.2% (PASS)
- Pressure error: 7.8% (PASS)
- R² correlation: 0.94 (PASS)

Reference: Smith et al., Exp. Fluids (2020)
DOI: 10.1007/s00348-020-03051-2"

# Continue development on separate branch
git checkout main
git checkout -b turbulence-model-study

# If new version fails validation, easily revert
git checkout v1.0-validation  # Go back to validated state

# Or compare versions
git diff v1.0-validation HEAD -- system/fvSchemes
```

### Recommended Tagging Scheme

| Tag Type | Format | Example | Purpose |
|----------|--------|---------|---------|
| Validated baseline | `vX.Y-validation` | `v1.0-validation` | Reference validated configuration |
| Experimental variant | `vX.Y-variant-name` | `v1.1-sst-kw` | Alternative setup worth preserving |
| Failed attempt | `vX.Y-failed-description` | `v1.2-failed-high-Re` | Document what didn't work (valuable info!) |

### Collaboration Best Practices

```bash
# Before starting work, pull latest changes
git pull origin main

# Create feature branch for your work
git checkout -b feature/validation-case-X

# Commit frequently with descriptive messages
git commit -m "Add mesh independence study for case X

Tested 3 mesh levels:
- Coarse: convergence achieved, 2.1% change from medium
- Medium: baseline for validation
- Fine: 0.8% change from medium - acceptable convergence

Selected medium mesh for final validation"

# Push your branch
git push origin feature/validation-case-X

# Create pull request for review
# (Use GitHub/GitLab web interface or gh CLI)

# After review and merge, update main
git checkout main
git pull origin main
```

---

## 8. Common Validation Pitfalls

### Awareness Prevents Mistakes

Even experienced practitioners encounter these validation pitfalls. Recognizing them early saves time and prevents false confidence in results.

### 1. Inadequate Mesh Independence

**Mistake:** Running validation on a single mesh without convergence study.

**Consequence:** Results may contain significant discretization errors that masquerade as validation failure or (worse) false success.

**Prevention:**
- Always perform mesh refinement study before validation
- Use at least 3 mesh levels for convergence assessment
- Document mesh metrics (cell count, non-orthogonality, skewness)
- Verify that key quantities change by < 2% between finest meshes

```python
# Quick mesh convergence check
def verify_mesh_convergence(metrics_dict, tolerance=0.02):
    """
    Check if validation metric is mesh-converged
    
    Parameters:
    -----------
    metrics_dict : dict
        {mesh_level: {metric_name: value}}
    tolerance : float
        Acceptable relative change (default 2%)
    """
    levels = sorted(metrics_dict.keys())
    
    for i in range(len(levels)-1):
        coarse_level = levels[i]
        fine_level = levels[i+1]
        
        coarse_val = metrics_dict[coarse_level]['target_metric']
        fine_val = metrics_dict[fine_level]['target_metric']
        
        rel_change = abs(fine_val - coarse_val) / abs(coarse_val)
        
        if rel_change > tolerance:
            print(f"⚠️  WARNING: {coarse_level} → {fine_level}: {rel_change:.1%} change")
            print(f"    Not converged! Refine mesh further.")
            return False
    
    print("✅ Mesh convergence verified")
    return True
```

### 2. Mismatched Boundary Conditions

**Mistake:** Using different boundary conditions than the reference experiment.

**Common errors:**
- Assuming "slip walls" when walls were actually rough
- Using uniform inlet when experiment had turbulence/non-uniformity
- Neglecting side-wall effects in "2D approximation"

**Prevention:**
- Carefully read experimental documentation
- Contact experimentalists if BC details unclear
- Document assumptions and their justification
- Test sensitivity to uncertain BCs

### 3. Ignoring Experimental Uncertainty

**Mistake:** Treating experimental data as ground truth without uncertainty.

**Reality:** All measurements have uncertainty. Validation error should be compared to experimental uncertainty, not zero.

**Best practice:**
```
If experimental uncertainty = ±5% and simulation error = 4%:
→ Validation is inconclusive (error < uncertainty)

If experimental uncertainty = ±2% and simulation error = 4%:
→ Validation FAILS (error exceeds uncertainty)
```

```python
def validate_with_uncertainty(sim_error, exp_uncertainty, confidence=0.95):
    """
    Assess validation considering experimental uncertainty
    
    Parameters:
    -----------
    sim_error : float
        Absolute error between simulation and experiment
    exp_uncertainty : float  
        Experimental uncertainty (same units as error)
    confidence : float
        Statistical confidence level (default 95%)
    
    Returns:
    --------
    status : str
        'PASS', 'INCONCLUSIVE', or 'FAIL'
    """
    if sim_error <= exp_uncertainty:
        return 'PASS', f"Error ({sim_error:.2f}) ≤ uncertainty ({exp_uncertainty:.2f})"
    elif sim_error <= 2 * exp_uncertainty:
        return 'INCONCLUSIVE', f"Error within 2× uncertainty - more data needed"
    else:
        return 'FAIL', f"Error ({sim_error:.2f}) significantly exceeds uncertainty ({exp_uncertainty:.2f})"
```

### 4. Cherry-Picking Results

**Mistake:** Showing only the best validation case and hiding failures.

**Why it's problematic:**
- Misleading representation of solver capability
- Prevents learning from failures
- Undermines scientific credibility

**Ethical practice:**
- Report ALL validation attempts
- Analyze WHY failures occurred
- Document lessons learned from unsuccessful validations
- Let stakeholders see the full picture

### 5. Overfitting to One Case

**Mistake:** Tuning model constants until validation passes for one specific case.

**Problem:** Tuned constants may fail catastrophically on different geometries/conditions.

**Prevention:**
- Use blind validation (withhold some data during tuning)
- Validate on multiple diverse cases
- Use physically justified constants, not just "what works"
- Document any tuning and its justification

### 6. Wrong Validation Metric

**Mistake:** Using inappropriate metric for the application.

**Examples:**
- Using R² alone (high R² can still have large absolute errors)
- Using relative error for near-zero quantities
- Not considering phase errors in transient simulations

**Solution:**
```python
# Select metric based on data characteristics
def choose_appropriate_metrics(experimental_data):
    """
    Recommend appropriate validation metrics based on data characteristics
    """
    metrics = []
    
    # Always include RMSE (error magnitude)
    metrics.append('RMSE')
    
    # If data spans orders of magnitude, use relative error
    if np.max(experimental_data) / np.min(experimental_data) > 10:
        metrics.append('MAPE')  # Mean Absolute Percentage Error
    else:
        metrics.append('MAE')  # Mean Absolute Error
    
    # Check if correlation makes sense
    if len(experimental_data) > 10:  # Sufficient data points
        metrics.append('R2')
    
    # If near-zero values exist, avoid purely relative metrics
    if np.any(np.abs(experimental_data) < 0.01):
        metrics.append('Max_Absolute_Error')
    
    return metrics
```

### 7. Neglecting Temporal Validation

**Mistake:** Validating only time-averaged statistics for transient simulations.

**Problem:** Good statistics don't guarantee correct transient physics (e.g., vortex shedding frequency, phase).

**Best practice for transient cases:**
- Validate frequency content (FFT comparison)
- Compare phase relationships
- Validate instantaneous flow fields at multiple time instants
- Verify time-step independence

```python
def validate_transient_signal(sim_time, sim_signal, exp_time, exp_signal):
    """
    Comprehensive transient validation
    """
    results = {}
    
    # Interpolate to common time grid
    common_time = np.linspace(min(sim_time[0], exp_time[0]), 
                              max(sim_time[-1], exp_time[-1]), 
                              1000)
    from scipy.interpolate import interp1d
    sim_interp = interp1d(sim_time, sim_signal, kind='linear')(common_time)
    exp_interp = interp1d(exp_time, exp_signal, kind='linear')(common_time)
    
    # Time-domain validation
    results['RMSE'] = np.sqrt(np.mean((sim_interp - exp_interp)**2))
    results['cross_correlation'] = np.corrcoef(sim_interp, exp_interp)[0, 1]
    
    # Frequency-domain validation
    from scipy.fft import fft, fftfreq
    sim_fft = np.abs(fft(sim_interp))
    exp_fft = np.abs(fft(exp_interp))
    results['dominant_frequency_error'] = \
        abs(fftfreq(len(sim_fft))[np.argmax(sim_fft)] - 
            fftfreq(len(exp_fft))[np.argmax(exp_fft)])
    
    return results
```

### 8. Documentation Gaps

**Mistake:** Incomplete documentation that prevents reproduction.

**Essential documentation elements:**
- ✅ Exact software version (e.g., OpenFOAM-9)
- ✅ Complete solver and scheme settings
- ✅ Initial conditions (not just BCs)
- ✅ Mesh quality metrics
- ✅ Convergence criteria and achieved residuals
- ✅ Reference data with source citations
- ✅ Processing scripts used for comparison

---

## 9. Validation Checklist

Use this checklist before claiming validation success:

### Pre-Validation

- [ ] Reference data obtained from credible source
- [ ] Experimental conditions fully documented
- [ ] Experimental uncertainty quantified
- [ ] Acceptance criteria defined BEFORE running simulations
- [ ] Geometry matches experiment (dimensions verified)

### Numerical Verification

- [ ] Mesh independence study completed (< 2% change between refinements)
- [ ] Time-step independence verified (for transient cases)
- [ ] Iterative convergence achieved (residuals plateaued)
- [ ] Domain independence verified (boundaries far enough)

### Physical Modeling

- [ ] Boundary conditions match experimental setup
- [ ] Material properties documented and justified
- [ ] Turbulence model selection justified
- [ ] Near-wall treatment appropriate for y+ values

### Results Analysis

- [ ] Multiple validation metrics computed
- [ ] Results compared to acceptance criteria
- [ ] Discrepancies investigated and explained
- [ ] Uncertainty quantification performed

### Documentation

- [ ] All settings documented in README
- [ ] Validation report written
- [ ] Code version tagged/committed
- [ ] Results reproducible by independent user

### Critical Assessment

- [ ] Results not cherry-picked (all cases reported)
- [ ] Limitations acknowledged
- [ ] Model适用范围 (applicability range) specified
- [ ] Recommendations for future work provided

---

## Key Takeaways

### Essential Practices

1. **Documentation is non-negotiable**
   - Comprehensive README files enable reproducibility
   - Validation reports provide permanent validation records
   - Version control preserves exact configurations

2. **Verification precedes validation**
   - Mesh independence must be established before validation
   - Numerical errors must be quantified and minimized
   - Time-step independence required for transient cases

3. **Multiple metrics provide complete picture**
   - No single metric captures all aspects of agreement
   - Use error magnitude (RMSE), correlation (R²), and relative error
   - Visual inspection complements quantitative metrics

4. **Context determines acceptance criteria**
   - Define criteria based on application requirements
   - Account for experimental uncertainty in assessment
   - Different applications require different accuracy levels

5. **Common pitfalls are avoidable**
   - Inadequate mesh studies are the most frequent failure
   - Mismatched boundary conditions invalidate comparisons
   - Cherry-picking results undermines scientific credibility

6. **Uncertainty is everywhere**
   - Experimental data always has uncertainty
   - Numerical solutions have discretization errors
   - Model assumptions introduce structural uncertainty

### Validation vs. Verification

Remember the distinction:
- **Verification:** "Are we solving the equations right?" (code correctness, mesh convergence)
- **Validation:** "Are we solving the right equations?" (physical correctness, comparison to reality)

Both are required for credible CFD.

### Professional Validation Workflow

```
Define acceptance criteria → Obtain reference data → Build geometry → 
Mesh independence study → Run simulation → Compute multiple metrics → 
Compare to criteria → Investigate discrepancies → Document findings → 
Version control validated configuration
```

---

## Concept Check

Test your understanding with these scenario-based questions:

<details>
<summary><b>1. Scenario: Your velocity profile shows R² = 0.98 but velocity magnitude is 30% higher than experiment everywhere. Is this valid?</b></summary>

**Answer: NO.**

R² measures correlation (pattern matching), not accuracy. High R² means the simulation has the same shape as experiment, but a consistent 30% bias indicates a serious error—likely incorrect boundary conditions, material properties, or units. The validation should FAIL despite the high R².

This demonstrates why multiple metrics (RMSE + R² + visual inspection) are necessary.

</details>

<details>
<summary><b>2. Scenario: Your mesh study shows 15% change from coarse to medium, but only 0.5% change from medium to fine. Which mesh should you use for validation?</b></summary>

**Answer: Use the FINE mesh.**

While medium→fine shows convergence (0.5% < 2% threshold), the large coarse→medium change (15%) indicates the solution is still evolving with refinement. The fine mesh provides additional confidence that you've reached the asymptotic convergence range.

Ideally, add one more refinement level to confirm the fine mesh is truly converged.

</details>

<summary><b>3. Scenario: Experimental data has ±8% uncertainty. Your simulation shows 6% error. Validation: PASS or FAIL?</b></summary>

**Answer: PASS (but with documentation).**

Since the simulation error (6%) is less than experimental uncertainty (±8%), you cannot distinguish simulation error from measurement error. The validation passes because the simulation is within the experimental confidence bounds.

However, you should document this as "validation within experimental uncertainty" rather than "strong validation."

</details>

<details>
<summary><b>4. Scenario: You've tuned the turbulence model constant from 0.09 (default) to 0.12 to match experimental data. Is this appropriate validation practice?</b></summary>

**Answer: Generally NO, with exceptions.**

**Problem:** Tuning to match one case is "overfitting"—the modified constant may fail on different geometries/flow conditions. This undermines predictive capability.

**When acceptable:**
- If the tuning is based on physical reasoning (e.g., accounting for surface roughness)
- If you document the tuning explicitly
- If you validate on multiple additional cases to ensure transferability
- If you use blind validation (withhold some data during tuning)

**Better approach:** Use default constants and investigate WHY the default model doesn't match. Understanding discrepancies is more valuable than "forcing" agreement.

</details>

<details>
<summary><b>5. Scenario: Your drag coefficient prediction matches experiment within 2%, but pressure distribution shows large discrepancies in separated regions. Is the simulation validated?</b></summary>

**Answer: INCONCLUSIVE / CONDITIONAL.**

**Correct approach:**
- Global agreement (drag) can hide local errors (pressure distribution)
- Separation regions are physically important—discrepancies there suggest model deficiencies
- Report: "Drag coefficient validated, but separation prediction requires improvement"

**Action:** 
- Don't claim full validation
- Investigate separation prediction (turbulence model, mesh resolution in shear layers)
- Document which aspects pass and which fail
- Consider this a "partial validation"

</details>

<details>
<summary><b>6. Scenario: A colleague claims validation but their repository lacks commit history, has only one mesh, and the README says "see reference paper for setup." Is their validation credible?</b></summary>

**Answer: RED FLAGS - not fully credible.**

**Missing elements:**
- No version control → can't reproduce exact code/settings
- Single mesh → mesh independence not verified
- Incomplete README → reproduction requires detective work

**For credible validation, they should provide:**
- Complete case files with all settings documented
- Mesh independence study
- Git history showing configuration evolution
- Processing scripts for result extraction
- Detailed validation report

This scenario illustrates why documentation standards are essential.

</details>

---

## Related Documents

- **Overview:** [00_Overview.md](00_Overview.md) - Validation framework and workflow
- **Physical Validation:** [01_Physical_Validation.md](01_Physical_Validation.md) - Detailed validation procedures
- **Mesh/BC Verification:** [02_Mesh_BC_Verification.md](02_Mesh_BC_Verification.md) - Mesh quality and boundary condition verification
- **Fundamentals:** 
  - [01_Introduction.md](../../01_TESTING_FUNDAMENTALS/01_Introduction.md) - Testing vs validation distinction
  - [02a_Method_of_Manufactured_Solutions_MMS.md](../../02_VERIFICATION_FUNDAMENTALS/02a_Method_of_Manufactured_Solutions_MMS.md) - Code verification methods
  - [02b_Richardson_Extrapolation_GCI.md](../../02_VERIFICATION_FUNDAMENTALS/02b_Richardson_Extrapolation_GCI.md) - Grid convergence analysis