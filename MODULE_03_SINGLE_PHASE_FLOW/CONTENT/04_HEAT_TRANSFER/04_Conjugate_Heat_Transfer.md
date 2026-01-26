# Conjugate Heat Transfer (CHT)

การจำลอง Solid-Fluid Heat Transfer ใน OpenFOAM

---

## Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:
- เข้าใจโครงสร้าง multi-region case สำหรับ CHT simulation ได้อย่างถูกต้อง
- ตั้งค่า interface boundary conditions สำหรับ coupling ระหว่าง fluid และ solid
- กำหนด thermophysical properties สำหรับทั้ง fluid และ solid regions
- วิเคราะห์และประเมินผล heat transfer performance ด้วย overall heat transfer coefficient
- แก้ไขปัญหาที่พบบ่อยใน CHT simulations

---

## Quick Start

| Component | Purpose | Key File |
|-----------|---------|----------|
| Solver | Multi-region coupling | `chtMultiRegionFoam` |
| Regions | Define fluid/solid | `constant/regionProperties` |
| Interface BC | Temperature/flux coupling | `turbulentTemperatureCoupledBaffleMixed` |
| Properties | Material properties | `thermophysicalProperties` |

---

## 1. What is Conjugate Heat Transfer?

### 1.1 Concept Definition

**Conjugate Heat Transfer (CHT)** เป็นกระบวนการจำลอง heat transfer ที่เกิดขึ้นพร้อมกันในทั้ง:
- **Fluid Domain**: Convection (forced หรือ natural)
- **Solid Domain**: Conduction

โดยมีการ coupled heat transfer ผ่าน interface ระหว่างสอง domains นี้

### 1.2 Physical Importance

**WHY CHT Matters:**
- Heat exchangers: การถ่ายเทความร้อนระหว่าง fluids ผ่าน solid walls
- Electronics cooling: Heat dissipation จาก electronic components ไปยัง cooling fluid
- Building simulation: Heat transfer ผ่าน walls, windows
- Turbine cooling: Cooling flow ใน turbine blades
- Chemical reactors: Heat transfer ระหว่าง reaction zone และ cooling jackets

### 1.3 OpenFOAM Implementation

**HOW in OpenFOAM:**
- Solver: `chtMultiRegionFoam` — แก้สมการพร้อมกันสำหรับทุก regions
- Multi-region structure: แยก mesh และ properties สำหรับแต่ละ region
- Coupled BC: Automatic temperature และ heat flux matching ที่ interfaces

---

## 2. Multi-Region Case Structure

### 2.1 Directory Layout

```
case/
├── 0/
│   ├── fluid/                    ← Fluid region fields
│   │   ├── U                     # Velocity
│   │   ├── p                     # Pressure
│   │   ├── T                     # Temperature
│   │   ├── k                     # TKE
│   │   └── omega                 # Dissipation
│   └── solid/                    ← Solid region fields
│       └── T                     # Temperature only
│
├── constant/
│   ├── regionProperties          ← Define regions
│   ├── fluid/
│   │   ├── polyMesh/             ← Fluid mesh
│   │   └── thermophysicalProperties
│   └── solid/
│       ├── polyMesh/             ← Solid mesh
│       └── thermophysicalProperties
│
└── system/
    ├── fluid/                    ← Fluid solver settings
    │   ├── controlDict
    │   ├── fvSchemes
    │   └── fvSolution
    └── solid/                    ← Solid solver settings
        ├── controlDict
        ├── fvSchemes
        └── fvSolution
```

### 2.2 Interface Coupling Visualization

```
┌─────────────────────────────────────────────────────────┐
│                    FLUID DOMAIN                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │   U     │  │   p     │  │   T     │  │   k     │    │
│  │   ω     │  │  nut    │  │         │  │         │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│                                                           │
│                    ◄─────────────────────►               │
│                  INTERFACE BOUNDARY                        │
│                    ◄─────────────────────►               │
│                                                           │
│  ┌─────────┘                                              │
│  │   T     │  ← Only temperature field                  │
│  └─────────┘                                              │
│                                                           │
│                   SOLID DOMAIN                            │
└─────────────────────────────────────────────────────────┘

    Interface Conditions (coupled):
    ┌─────────────────────────────────────────┐
    │  Temperature:   T_fluid = T_solid       │
    │  Heat Flux:     q_f = q_s              │
    │  (coupled by BC automatically)          │
    └─────────────────────────────────────────┘
```

### 2.3 Region Properties

**constant/regionProperties**

```cpp
regions
(
    fluid ( fluid )
    solid ( solid )
);
```

**Key Points:**
- กำหนดชื่อและจำนวน regions ที่ใช้ใน simulation
- แต่ละ region จะมี directory แยกกันใน `0/`, `constant/`, และ `system/`
- Region names ต้องตรงกับ patch names ที่ interface

---

## 3. Interface Boundary Conditions

### 3.1 Fluid Side Setup

**0/fluid/T**

```cpp
fluid_to_solid
{
    type    compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr    T;
    kappaMethod fluidThermo;
    value1$internalField;
}
```

### 3.2 Solid Side Setup

**0/solid/T**

```cpp
solid_to_fluid
{
    type    compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr    T;
    kappaMethod solidThermo;
    value1$internalField;
}
```

### 3.3 Interface Conditions

The coupled BC enforces:

**Temperature Continuity:**
$$T_{fluid} = T_{solid}$$

**Heat Flux Continuity:**
$$-k_f \frac{\partial T_f}{\partial n} = -k_s \frac{\partial T_s}{\partial n}$$

### 3.4 BC Parameters Explained

| Parameter | Purpose |
|-----------|---------|
| `type` | Coupled BC ที่ match temperature และ flux |
| `Tnbr` | Field name ใน neighboring region |
| `kappaMethod` | วิธีคำนวณ conductivity (fluidThermo/solidThermo) |
| `value` | Initial guess (ใช้1$internalField) |

**Critical Requirements:**
- Patch names ต้อง match ระหว่าง regions (`fluid_to_solid` ↔ `solid_to_fluid`)
- `Tnbr` ต้องชี้ไปที่ field ที่ถูกต้อง
- `kappaMethod` ต้องสอดคล้องกับ thermophysical model

---

## 4. Thermophysical Properties

### 4.1 Fluid Properties

**constant/fluid/thermophysicalProperties**

```cpp
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie { molWeight 28.96; }
    thermodynamics { Cp 1005; Hf 0; }
    transport { mu 1.8e-5; Pr 0.71; }
}
```

### 4.2 Solid Properties

**constant/solid/thermophysicalProperties**

```cpp
thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie { molWeight 28.96; }
    equationOfState { rho 8000; }
    thermodynamics { Cp 450; Hf 0; }
    transport { kappa 50; }
}
```

### 4.3 Thermo Model Comparison

| Aspect | heRhoThermo | heSolidThermo |
|--------|-------------|---------------|
| Domain | Fluid | Solid |
| Transport | mu (viscosity), Pr | kappa (conductivity) |
| Equation of State | PerfectGas/icoPolynomial | rhoConst |
| Terms | Convection + Conduction | Conduction only |

**Reference:** See [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md) for detailed thermophysical property configurations.

---

## 5. Performance Metrics

### 5.1 Overall Heat Transfer Coefficient

$$\frac{1}{U} = \frac{1}{h_h} + \frac{t_w}{k_w} + \frac{1}{h_c}$$

Where:
-1$U1= Overall heat transfer coefficient [W/m²·K]
-1$h_h1= Hot side convection coefficient
-1$t_w1= Wall thickness [m]
-1$k_w1= Wall thermal conductivity [W/m·K]
-1$h_c1= Cold side convection coefficient

### 5.2 Effectiveness

$$\varepsilon = \frac{Q_{actual}}{Q_{max}}$$

### 5.3 Post-Processing Functions

**system/controlDict**

```cpp
functions
{
    wallHeatFlux
    {
        type            wallHeatFlux;
        region          fluid;
        patches         (interface);
        writeFields     true;
    }
    
    interfaceTemp
    {
        type            surfaces;
        region          fluid;
        functionObjectLibs ("libsampling.so");
        surfaceFormat   raw;
        
        surfaces
        {
            interface
            {
                type            patch;
                patches         (interface);
                interpolate     true;
            }
        }
        
        fields          (T);
    }
}
```

---

## 6. Mini-Tutorial: Basic CHT Setup

### 6.1 Step-by-Step Workflow

**Step 1: Create Multi-Region Structure**

```bash
# Create region directories
mkdir -p 0/fluid 0/solid
mkdir -p constant/fluid/polyMesh constant/solid/polyMesh
mkdir -p system/fluid system/solid
```

**Step 2: Define Region Properties**

Create `constant/regionProperties`:
```cpp
regions
(
    fluid ( fluid )
    solid ( solid )
);
```

**Step 3: Generate Meshes**

```bash
# Mesh each region separately
blockMesh -region fluid
blockMesh -region solid

# OR use splitMeshRegions
blockMesh
splitMeshRegions -cellZones -overwrite
```

**Step 4: Setup Interface BCs**

Ensure matching patch names in both regions:
- Fluid: `fluid_to_solid`
- Solid: `solid_to_fluid`

**Step 5: Run Solver**

```bash
chtMultiRegionFoam
```

### 6.2 Validation Checklist

- [ ] Region names consistent in `regionProperties`
- [ ] Interface patches have matching names
- [ ] `kappaMethod` matches thermo type
- [ ] Thermophysical properties appropriate for materials
- [ ] Mesh is conformal at interface (node-to-node matching)
- [ ] Initial conditions specified for all fields

---

## 7. Best Practices

### 7.1 Mesh Guidelines

| Aspect | Recommendation | Rationale |
|--------|----------------|-----------|
| Interface Type | Conformal mesh | Direct node-to-node mapping |
| Cell Size Ratio | < 3:1 across interface | Avoid interpolation errors |
| Boundary Layer | Resolve thermal BL |1$y^+ < 11for conjugate problems |
| Quality | Non-orthogonality < 70 | Ensure flux accuracy |

### 7.2 Solver Settings

**system/fluid/fvSolution**

```cpp
solvers
{
    T
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.01;
        smoother        GaussSeidel;
    }
}

relaxationFactors
{
    fields
    {
        T               0.7;  // For stability
    }
}
```

### 7.3 Time Scale Considerations

**Thermal Time Scale:**

$$\tau_{thermal} = \frac{\rho c_p L^2}{k}$$

**Guidelines:**
- Solid typically has much larger1$\tau1than fluid
- Use adaptive time stepping based on max Courant number
- Consider quasi-steady approach if1$\tau_{solid} \gg \tau_{fluid}$

### 7.4 Stability Tips

1. **Start Simple**: Begin with constant properties
2. **Under-Relaxation**: Use T relaxation 0.3-0.7 for convergence
3. **Progressive Coupling**: Run fluid-only first, then add solid
4. **Monitor Imbalance**: Track energy balance at interface

---

## 8. Troubleshooting

### 8.1 Common Issues

| Problem | Symptoms | Solution |
|---------|----------|----------|
| Interface mismatch | Solver crash, "cannot find patch" | Check patch names match exactly |
| No heat transfer | T constant across interface | Verify `kappaMethod` settings |
| Slow convergence | Oscillating residuals | Lower T relaxation factor to 0.3 |
| Energy imbalance | Q_in ≠ Q_out | Check boundary definitions, mesh quality |
| Divergence | Residuals explode | Reduce time step, check mesh quality |

### 8.2 Error Messages

**"cannot find patch" in boundary:**
```cpp
// Check regionProperties
regions ( fluid ( fluid ) solid ( solid ) );

// Verify patch names match
// Fluid side: "fluid_to_solid"
// Solid side: "solid_to_fluid"
```

**"kappaMethod invalid":**
```cpp
// For heRhoThermo → use "fluidThermo"
// For heSolidThermo → use "solidThermo"
kappaMethod solidThermo;  // Must match thermoType
```

**"Maximum number of iterations exceeded":**
```cpp
// In fvSolution, increase solver tolerance
T { solver GAMG; tolerance 1e-6; relTol 0.1; }

// OR add under-relaxation
relaxationFactors { fields { T 0.5; } }
```

### 8.3 Debugging Workflow

1. **Check Mesh**: 
   ```bash
   checkMesh -region fluid
   checkMesh -region solid
   ```

2. **Verify BCs**:
   ```bash
   # List boundary patches
   ls -d 0/fluid/* 0/solid/*
   ```

3. **Monitor Coupling**:
   ```cpp
   // Add to controlDict
   functions
   {
       interfaceHeatFlux
       {
           type            wallHeatFlux;
           region          fluid;
           patches         (interface);
       }
   }
   ```

---

## 9. Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ `turbulentTemperatureCoupledBaffleMixed`?</b></summary>

เพราะ BC นี้บังคับให้ **Temperature** และ **Heat Flux** ต่อเนื่องกันที่ interface โดยอัตโนมัติ — ไม่ต้องกำหนดค่าเอง solver จะคำนวณให้ สมการ coupled:

$$T_{fluid} = T_{solid}$$
$$-k_f \nabla T_f = -k_s \nabla T_s$$
</details>

<details>
<summary><b>2. Conformal mesh ดีกว่า AMI อย่างไรสำหรับ CHT?</b></summary>

Conformal mesh ให้ **direct node-to-node mapping** — ฟลักซ์ความร้อนแม่นยำกว่า ไม่มี interpolation error และลู่เข้าเร็วกว่า AMI (Arbitrary Mesh Interface) ใช้ interpolation ที่เพิ่มความคลาดเคลื่อนในการคำนวณ heat flux
</details>

<details>
<summary><b>3. `heRhoThermo` vs `heSolidThermo` ต่างกันอย่างไร?</b></summary>

- **heRhoThermo**: สำหรับ fluid มีทั้ง convection (velocity field) และ conduction
- **heSolidThermo**: สำหรับ solid มีแค่ conduction (Laplace equation:1$\nabla \cdot (k \nabla T) = 0$)

Fluid ต้องการ viscosity ($\mu$) และ Prandtl number ($Pr$), solid ต้องการ thermal conductivity ($\kappa$) โดยตรง
</details>

<details>
<summary><b>4. ทำไม solid region มีแค่ field T?</b></summary>

เพราะใน solid ไม่มี flow — ไม่มี velocity, pressure, หรือ turbulence quantities สมการ energy ใน solid เป็นแค่ heat conduction:

$$\rho c_p \frac{\partial T}{\partial t} = \nabla \cdot (k \nabla T)$$

ไม่มี convection term:1$(\mathbf{u} \cdot \nabla T)$
</details>

<details>
<summary><b>5. เลือก `kappaMethod` อย่างไร?</b></summary>

เลือกตาม `thermoType`:
- `heRhoThermo` (fluid) → `kappaMethod fluidThermo`
- `heSolidThermo` (solid) → `kappaMethod solidThermo`

ถ้าตั้งค่าผิด จะเกิด error: "kappaMethod invalid" หรือ heat flux ไม่ถูกต้อง
</details>

---

## 10. Key Takeaways

### Setup Checklist ✓

- [ ] **Structure**: Create multi-region directories (0/fluid, 0/solid, etc.)
- [ ] **regionProperties**: Define all regions with correct names
- [ ] **Meshes**: Generate conformal meshes at interface
- [ ] **Interface BCs**: Set `turbulentTemperatureCoupledBaffleMixed` with matching patches
- [ ] **Properties**: Configure `thermophysicalProperties` for each region
- [ ] **Solver Settings**: Use GAMG for T, add relaxation (0.7)
- [ ] **Validation**: Verify patch names match, check mesh quality

### Common Pitfalls to Avoid

1. **Non-matching patch names** — Most common error
2. **Incorrect kappaMethod** — Must match thermo type
3. **Non-conformal mesh** — Causes flux errors
4. **Wrong relaxation** — Too high = divergence, too low = slow convergence
5. **Forgotten solid fields** — Only T needed, but must be initialized

### Best Practices Summary

- Use conformal meshes whenever possible
- Start with constant properties before complex models
- Monitor heat flux balance at interface
- Consider thermal time scale differences between fluid/solid
- Use function objects to track interface temperature and flux

---

## Related Documents

- **บทก่อนหน้า:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md) — Natural convection fundamentals
- **พื้นฐาน:** [01_Energy_Equation_Fundamentals.md](01_Energy_Equation_Fundamentals.md) — Energy equation and thermophysical properties
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — Heat transfer module overview