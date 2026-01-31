# 05 Surface Tension in R410A Evaporation (แรงตัวผิวผิวในการระเหย R410A)

## Overview

This section covers the critical role of surface tension forces in R410A two-phase flow during evaporation in tube heat exchangers. Surface tension significantly affects flow regimes, heat transfer, and pressure drop, especially in microchannel designs common in modern evaporators.

### Learning Objectives (วัตถุประสงค์การเรียนรู้)

1. Understand R410A surface tension properties and temperature dependence
2. Learn the Continuum Surface Force (CSF) model implementation
3. Analyze surface tension effects in evaporator tubes
4. Calculate Bond numbers for different tube geometries
5. Implement surface tension in OpenFOAM simulations

### Module Structure (โครงสร้างโมดูล)

1. **01_Surface_Tension_R410A.md** - Complete technical content
   - R410A surface tension coefficients
   - CSF model theory and implementation
   - Effects in evaporator tubes
   - Bond number calculations
   - OpenFOAM implementation guide

### Prerequisites (ข้อกำหนดเบื้องต้น)

- Understanding of two-phase flow fundamentals
- Basic knowledge of interphase forces
- Familiarity with OpenFOAM architecture
- R410A thermodynamic properties

### Verification Status (สถานะการตรวจสอบ)

- ⭐ Surface tension values verified from experimental data
- ⭐ CSF model equations cross-referenced with OpenFOAM source
- ⭐ Bond number calculations validated for typical evaporator dimensions
- ⭐ Implementation steps verified against OpenFOAM examples

### Key Takeaways (ข้อควรจำสำคัญ)

1. Surface tension in R410A is approximately 0.008 N/m at saturation temperature
2. Temperature dependence must be included for accurate modeling
3. Surface tension dominates flow in microchannels (< 3mm diameter)
4. The CSF model treats surface tension as a volumetric force
5. Bond number determines relative importance of surface tension vs. gravity

### Integration with Module 04 (การรวมกับโมดูล 04)

This section complements the existing interphase forces:
- **01_DRAG** - Drag forces in two-phase flow
- **02_LIFT** - Lift forces between phases
- **03_VIRTUAL_MASS** - Virtual mass effects
- **04_TURBULENT_DISPERSION** - Turbulent dispersion forces
- **05_SURFACE_TENSION** - Surface tension effects (NEW)

### Recommended Learning Path (เส้นทางการเรียนรู้แนะนำ)

1. Review existing interphase force models
2. Study R410A thermodynamic properties
3. Understand surface tension physics in two-phase flow
4. Implement CSF model in simple test cases
5. Apply to full evaporator tube simulation