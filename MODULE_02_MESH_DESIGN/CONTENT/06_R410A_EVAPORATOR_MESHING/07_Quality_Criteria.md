# Quality Criteria for R410A Mesh (เกณฑ์คุณภาพ Mesh สำหรับ R410A)

## Introduction to Mesh Quality Assessment

Proper mesh quality assessment is critical for accurate R410A evaporator simulations. This guide provides comprehensive quality criteria specifically tailored for the unique requirements of two-phase flow in R410A systems.

### ⭐ Why Quality Criteria Matter for R410A

**1. Two-Phase Flow Complexity**
- Sharp interfaces between liquid and vapor
- Surface tension effects at small scales
- Different flow regimes (annular, slug, bubbly)

**2. Heat Transfer Sensitivity**
- Temperature gradients near walls
- Phase change location accuracy
- Condensation/evaporation interface capture

**3. Numerical Stability**
- High aspect ratios in microchannels
- Curved geometries in U-bends
- Variable material properties

## Mesh Quality Metrics

### ⭐ Standard Quality Metrics

| Metric | Definition | Importance | Target Range |
|--------|------------|------------|--------------|
| Non-orthogonality | Angle between cell faces | Pressure solver | < 70° |
| Skewness | Deviation from ideal cell shape | Convergence | < 4.0 |
| Aspect ratio | Longest/shortest cell dimension | Stability | < 10 |
| Volume ratio | Max/min cell volume | Property interpolation | < 100 |
| Face validity | Face area and normal vectors | Mesh integrity | Positive |

### R410A-Specific Quality Requirements

```python
# R410A quality assessment function
def assess_r410a_mesh_quality(mesh_stats):
    """Evaluate mesh quality for R410A simulations"""

    quality_report = {
        'overall_quality': 'PASS',
        'critical_issues': [],
        'warnings': [],
        'recommendations': []
    }

    # Non-orthogonality check
    if mesh_stats['max_non_ortho'] > 70:
        quality_report['overall_quality'] = 'FAIL'
        quality_report['critical_issues'].append(
            f"High non-orthogonality: {mesh_stats['max_non_ortho']:.1f}°"
        )

    # Skewness check
    if mesh_stats['max_skewness'] > 4.0:
        quality_report['warnings'].append(
            f"High skewness: {mesh_stats['max_skewness']:.2f}"
        )
        if mesh_stats['max_skewness'] > 6.0:
            quality_report['critical_issues'].append(
                f"Critical skewness: {mesh_stats['max_skewness']:.2f}"
            )

    # Aspect ratio check for R410A
    if mesh_stats['max_aspect_ratio'] > 20:
        quality_report['warnings'].append(
            f"High aspect ratio: {mesh_stats['max_aspect_ratio']:.1f}"
        )

    # Y+ validation
    if hasattr(mesh_stats, 'y_plus_stats'):
        if mesh_stats['y_plus_stats']['max_y_plus'] > 5.0:
            quality_report['warnings'].append(
                f"High y+: {mesh_stats['y_plus_stats']['max_y_plus']:.1f}"
            )

    return quality_report
```

## Mandatory Quality Checks

### ⭐ checkMesh Commands for R410A

```bash
# Comprehensive mesh quality check
checkMesh -all -time 1 > r410a_mesh_quality.txt

# Focus on specific metrics
checkMesh -nonOrtho -time 1 > orthogonality_report.txt
checkMesh -skewness -time 1 > skewness_report.txt
checkMesh -volRatio -time 1 > volume_ratio_report.txt

# Visual quality assessment
checkMesh -all -time 1 -writeVTK
```

### Quality Check Results Analysis

```bash
# Extract key metrics from quality report
echo "=== Mesh Quality Summary ==="
grep "max non-orthogonality" r410a_mesh_quality.txt | awk '{print $5}'
grep "max skewness" r410a_mesh_quality.txt | awk '{print $3}'
grep "max aspect ratio" r410a_mesh_quality.txt | awk '{print $4}'
grep "max cell volume ratio" r410a_mesh_quality.txt | awk '{print $6}'

# Calculate percentage of good cells
awk '/cells: max/ {cells++} /non-ortho:/ {ortho++} END {print "Orthogonal cells:", ortho/cells*100 "%"}' r410a_mesh_quality.txt
```

## R410A-Specific Quality Criteria

### ⭐ Straight Tube Evaporator

| Quality Metric | Acceptable | Warning | Critical |
|----------------|------------|---------|----------|
| Non-orthogonality | < 50° | 50-70° | > 70° |
| Max skewness | < 3.0 | 3.0-4.0 | > 4.0 |
| Aspect ratio | < 10 | 10-15 | > 15 |
| Volume ratio | < 50 | 50-100 | > 100 |
| Y+ | < 1.0 | 1.0-5.0 | > 5.0 |

### ⭐ U-Bend Evaporator

| Quality Metric | Bend Region | Transition | Straight Section |
|----------------|-------------|------------|------------------|
| Non-orthogonality | < 60° | < 50° | < 40° |
| Max skewness | < 3.5 | < 3.0 | < 2.5 |
| Aspect ratio | < 12 | < 10 | < 8 |
| Volume ratio | < 100 | < 50 | < 30 |
| Curvature resolution | > 5 cells/bend | - | - |

### ⭐ Microchannel Evaporator

| Quality Metric | Microchannel | Minichannel | Standard |
|----------------|--------------|-------------|----------|
| Non-orthogonality | < 45° | < 55° | < 65° |
| Max skewness | < 2.5 | < 3.0 | < 4.0 |
| Aspect ratio | < 15 | < 12 | < 10 |
| Volume ratio | < 200 | < 100 | < 50 |
| Cell size uniformity | < 20% variation | < 15% | < 10% |

## Validation Procedure

### ⭐ Step-by-Step Quality Assessment

```bash
#!/bin/bash
# R410A mesh quality validation script

echo "=== R410A Mesh Quality Assessment ==="

# Step 1: Basic mesh check
echo "1. Running basic mesh quality check..."
checkMesh -all -time 1 > temp_quality.txt

# Step 2: Extract key metrics
echo "2. Extracting quality metrics..."
MAX_NON_ORTHO=$(grep "max non-orthogonality" temp_quality.txt | awk '{print $5}')
MAX_SKEWNESS=$(grep "max skewness" temp_quality.txt | awk '{print $3}')
MAX_ASPECT=$(grep "max aspect ratio" temp_quality.txt | awk '{print $4}')

echo "   - Max non-orthogonality: $MAX_NON_ORTHO°"
echo "   - Max skewness: $MAX_SKEWNESS"
echo "   - Max aspect ratio: $MAX_ASPECT"

# Step 3: Y+ validation
echo "3. Validating y+..."
yPlus -time 1 > yplus_report.txt
MAX_Y_PLUS=$(grep "max" yplus_report.txt | tail -1 | awk '{print $2}')
echo "   - Max y+: $MAX_Y_PLUS"

# Step 4: Overall assessment
echo "4. Quality assessment..."
if (( $(echo "$MAX_NON_ORTHO > 70" | bc -l) )); then
    echo "   ❌ FAIL: High non-orthogonality"
elif (( $(echo "$MAX_NON_ORTHO > 50" | bc -l) )); then
    echo "   ⚠️  WARNING: Moderate non-orthogonality"
else
    echo "   ✅ PASS: Good non-orthogonality"
fi

# Step 5: Save report
mv temp_quality.txt r410a_mesh_quality_final.txt
echo "5. Report saved to r410a_mesh_quality_final.txt"

# Cleanup
rm -f yplus_report.txt
```

### ⭐ Automated Quality Report

```python
#!/usr/bin/env python3
# R410A mesh quality report generator
import subprocess
import re

def generate_quality_report():
    """Generate comprehensive R410A mesh quality report"""

    # Run checkMesh
    result = subprocess.run(['checkMesh', '-all'],
                          capture_output=True, text=True)

    # Parse results
    metrics = {}
    for line in result.stdout.split('\n'):
        if 'max non-orthogonality' in line:
            metrics['non_ortho'] = float(line.split()[5])
        elif 'max skewness' in line:
            metrics['skewness'] = float(line.split()[3])
        elif 'max aspect ratio' in line:
            metrics['aspect_ratio'] = float(line.split()[4])
        elif 'max cell volume ratio' in line:
            metrics['volume_ratio'] = float(line.split()[6])

    # Generate report
    report = f"""
=== R410A Mesh Quality Report ===

Quality Metrics:
- Non-orthogonality: {metrics.get('non_ortho', 'N/A')}°
- Skewness: {metrics.get('skewness', 'N/A')}
- Aspect Ratio: {metrics.get('aspect_ratio', 'N/A')}
- Volume Ratio: {metrics.get('volume_ratio', 'N/A')}

Assessment:
"""

    # Add assessment
    if metrics.get('non_ortho', 0) > 70:
        report += "❌ FAIL: Non-orthogonality too high\n"
    elif metrics.get('non_ortho', 0) > 50:
        report += "⚠️  WARNING: Moderate non-orthogonality\n"
    else:
        report += "✅ PASS: Good non-orthogonality\n"

    # Save report
    with open('r410a_quality_report.md', 'w') as f:
        f.write(report)

    return report

# Generate and display report
print(generate_quality_report())
```

## Advanced Quality Assessment

### ⭐ Detailed Quality Visualization

```bash
# Create quality visualization script
cat > visualize_quality.py << 'EOF'
#!/usr/bin/env python3
import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def create_quality_plots():
    """Create quality metric plots"""

    # Run checkMesh and save VTK
    subprocess.run(['checkMesh', '-all', '-writeVTK'])

    # Read mesh points (simplified)
    # In practice, use PyVista or ParaView for full visualization

    # Create quality distribution plot
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

    # Non-orthogonality distribution
    ax1.hist(np.random.beta(2, 5, 1000) * 70, bins=30, alpha=0.7)
    ax1.set_xlabel('Non-orthogonality (°)')
    ax1.set_ylabel('Cell Count')
    ax1.set_title('Non-orthogonality Distribution')
    ax1.axvline(x=70, color='r', linestyle='--', label='Acceptable Limit')
    ax1.legend()

    # Skewness distribution
    ax2.hist(np.random.gamma(2, 1, 1000), bins=30, alpha=0.7)
    ax2.set_xlabel('Skewness')
    ax2.set_ylabel('Cell Count')
    ax2.set_title('Skewness Distribution')
    ax2.axvline(x=4.0, color='r', linestyle='--', label='Acceptable Limit')
    ax2.legend()

    # Aspect ratio distribution
    ax3.hist(np.random.exponential(5, 1000), bins=30, alpha=0.7)
    ax3.set_xlabel('Aspect Ratio')
    ax3.set_ylabel('Cell Count')
    ax3.set_title('Aspect Ratio Distribution')
    ax3.axvline(x=10, color='r', linestyle='--', label='Acceptable Limit')
    ax3.legend()

    # Y+ distribution
    y_plus = np.random.exponential(0.5, 1000)
    ax4.hist(y_plus[y_plus < 10], bins=30, alpha=0.7)
    ax4.set_xlabel('y+')
    ax4.set_ylabel('Cell Count')
    ax4.set_title('y+ Distribution')
    ax4.axvline(x=1.0, color='r', linestyle='--', label='Target')
    ax4.axvline(x=5.0, color='orange', linestyle='--', label='Maximum')
    ax4.legend()

    plt.tight_layout()
    plt.savefig('r410a_quality_metrics.png', dpi=150)
    print("Quality metrics visualization saved as r410a_quality_metrics.png")

if __name__ == "__main__":
    create_quality_plots()
EOF

# Run visualization
python3 visualize_quality.py
```

## Troubleshooting Common Quality Issues

### ⭐ Issue 1: High Non-orthogonality

**Problem**: Non-orthogonality > 70° in curved regions
**Symptoms**: Pressure solver instability, slow convergence

**Solutions**:
```bash
# Check specific regions
checkMesh -nonOrtho -time 1 -writeVTK

# Refine problematic areas
snappyHexMesh -overwrite

# Add intermediate vertices in curved regions
# In blockMeshDict, add more vertices along curved edges
```

### ⭐ Issue 2: Excessive Skewness

**Problem**: Skewness > 4.0 in transition zones
**Symptoms**: Numerical oscillations, divergence

**Solutions**:
```cpp
// Improve block grading
blocks
(
    hex (0 1 2 3 4 5 6 7) (40 100 1)
    grading
    (
        30 1 30 30 1 30 30 1 30 1 30 30  // Finer radial grading
    )
);

// Use unstructured refinement
refinementRegions
{
    skewnessHotspot
    {
        mode            distance;
        levels          ((0.001 2)(0.0005 3));
        distance        0.001;     // 1mm from high skewness
    }
}
```

### ⭐ Issue 3: High Aspect Ratio

**Problem**: Aspect ratio > 20 in narrow channels
**Symptoms**: Poor property interpolation, instability

**Solutions**:
```cpp
// Increase radial cells in microchannels
hex (0 1 2 3 4 5 6 7) (60 100 1)  // 60 radial instead of 40

// Use anisotropic grading
grading
(
    40 1 40 40 1 40 40 1 40 1 40 40  // Fine radial
    1 10 1    // Coarse axial
)
```

### ⭐ Issue 4: Poor y+ Values

**Problem**: y+ > 1 for low-Re turbulence models
**Symptoms**: Inaccurate wall heat transfer

**Solutions**:
```bash
# Check y+ distribution
yPlus -time 1 > yplus_check.txt

# Adjust boundary layer
# In boundary section:
boundaryLayer
{
    nLayers         30;         // More layers
    expansionRatio  1.2;        // Smaller growth ratio
    firstCellThickness 3e-6;    // 3 μm first cell
}
```

## Quality Optimization Strategies

### ⭐ Quality-Driven Mesh Generation

```cpp
// Optimized blockMeshDict for R410A
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
|  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|   \\    /   O peration     | Version: 8.x                                    |
|    \\  /    A nd           | Web:      www.openfoam.com                      |
|     \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/

convertToMeters 0.001;

// Vertices with quality-optimized spacing
vertices
(
    // Fine spacing near walls for boundary layer
    (0, -0.002500, 0)      // Wall-adjacent vertex
    (0, -0.002550, 0)      // First BL cell edge
    (0, -0.002625, 0)      // Second BL cell edge
    (0, -0.002750, 0)      // Third BL cell edge
    // ... continue with graded spacing
    (0.01, -0.0025, 0)     // Coarse spacing in bulk
);

blocks
(
    // Optimized cell distribution
    hex (0 1 2 3 4 5 6 7) (30 200 1)  // Quality-optimized grading
    grading
    (
        // Fine near walls, coarse in bulk
        25 1 25 25 1 25 25 1 25 1 25 25
        1 20 1 1 20 1 1 20 1 1 20 1
    )
);

// Quality constraints in boundary
boundary
{
    wall
    {
        type wall;
        faces
        (
            // Wall faces
        );

        // Quality-optimized boundary layer
        boundaryLayer
        {
            nLayers         25;
            expansionRatio  1.2;
            firstCellThickness 4e-6;  // Optimized for R410A
            qualityControl  true;
            maxSkewness     2.0;      // Quality constraint
        }
    }
}
```

### ⭐ Quality Monitoring During Simulation

```bash
# Create quality monitoring script
cat > monitor_quality.sh << 'EOF'
#!/bin/bash
# R410A mesh quality monitoring during simulation

echo "=== R410A Mesh Quality Monitoring ==="

# Monitor quality at each time step
while true; do
    # Get latest time
    latest_time=$(foamListTimes -latest | tail -1)

    if [ -n "$latest_time" ]; then
        echo "Time: $latest_time"

        # Check quality
        checkMesh -all -time $latest_time > temp_quality.txt

        # Extract metrics
        MAX_NON_ORTHO=$(grep "max non-orthogonality" temp_quality.txt | awk '{print $5}')
        MAX_SKEWNESS=$(grep "max skewness" temp_quality.txt | awk '{print $3}')

        echo "  Non-orthogonality: $MAX_NON_ORTHO°"
        echo "  Skewness: $MAX_SKEWNESS"

        # Alert on degradation
        if (( $(echo "$MAX_NON_ORTHO > 80" | bc -l) )); then
            echo "  🚨 CRITICAL: Non-orthogonality increased!"
        fi

        if (( $(echo "$MAX_SKEWNESS > 5.0" | bc -l) )); then
            echo "  ⚠️  WARNING: Skewness increased!"
        fi
    fi

    sleep 60  # Monitor every minute
done
EOF

# Make executable and run
chmod +x monitor_quality.sh
# ./monitor_quality.sh &
```

## Final Quality Checklist

### ⭐ Quality Assessment Checklist

**Before Starting Simulation:**
- [ ] Run `checkMesh -all` - all metrics acceptable
- [ ] Verify y+ < 1 for low-Re models
- [ ] Check cell count is reasonable for available resources
- [ ] Validate geometry boundaries
- [ ] Confirm no negative cell volumes

**After Initial Iterations:**
- [ ] Monitor convergence history
- [ ] Check for numerical instabilities
- [ ] Verify mass conservation
- [ ] Inspect solution smoothness
- [ ] Review mesh quality evolution

**For Two-Phase Flow:**
- [ ] Interface resolution adequate (> 3 cells)
- [ ] Phase fraction gradients captured
- [ ] Surface tension effects resolved
- [ ] Wall heat transfer accurate

### ⭐ Quality Report Template

```markdown
# R410A Mesh Quality Report

## Case Information
- Case Name: [Your Case]
- Date: [Date]
- Mesh Type: [blockMesh/snappyHexMesh]

## Quality Metrics
| Metric | Value | Status | Target |
|--------|-------|--------|---------|
| Non-orthogonality | [value] | [PASS/WARN/FAIL] | < 70° |
| Max Skewness | [value] | [PASS/WARN/FAIL] | < 4.0 |
| Aspect Ratio | [value] | [PASS/WARN/FAIL] | < 10 |
| Volume Ratio | [value] | [PASS/WARN/FAIL] | < 100 |
| Y+ | [value] | [PASS/WARN/FAIL] | < 1.0 |

## R410A-Specific Assessment
- Interface Resolution: [PASS/FAIL]
- Boundary Layer: [PASS/WARN/FAIL]
- Two-Phase Compatibility: [PASS/WARN/FAIL]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Conclusion
Overall Quality: [ACCEPTABLE/NEEDS IMPROVEMENT/UNACCEPTABLE]
```

---

*Previous: [06_Dynamic_Refinement.md](06_Dynamic_Refinement.md) | Next: [08_Complete_Examples.md](08_Complete_Examples.md)*