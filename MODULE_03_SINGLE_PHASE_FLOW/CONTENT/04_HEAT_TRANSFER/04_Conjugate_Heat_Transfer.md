# Conjugate Heat Transfer (CHT)

การจำลอง Solid-Fluid Heat Transfer ใน OpenFOAM

---

## Quick Start

| Component | Purpose | Key File |
|-----------|---------|----------|
| Solver | Multi-region coupling | `chtMultiRegionFoam` |
| Regions | Define fluid/solid | `constant/regionProperties` |
| Interface BC | Temperature/flux coupling | `turbulentTemperatureCoupledBaffleMixed` |
| Properties | Material properties | `thermophysicalProperties` |

---

## 1. Multi-Region Case Structure

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

### Interface Coupling Visualization

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
│  ┌─────────┐                                              │
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

---

## 2. Region Properties

### constant/regionProperties

```cpp
regions
(
    fluid ( fluid )
    solid ( solid )
);
```

---

## 3. Interface Boundary Conditions

### Fluid Side (0/fluid/T)

```cpp
fluid_to_solid
{
    type    compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr    T;
    kappaMethod fluidThermo;
    value   $internalField;
}
```

### Solid Side (0/solid/T)

```cpp
solid_to_fluid
{
    type    compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr    T;
    kappaMethod solidThermo;
    value   $internalField;
}
```

### Interface Conditions

$$T_{fluid} = T_{solid}$$

$$-k_f \frac{\partial T_f}{\partial n} = -k_s \frac{\partial T_s}{\partial n}$$

---

## 4. Thermophysical Properties

### Fluid (constant/fluid/thermophysicalProperties)

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

### Solid (constant/solid/thermophysicalProperties)

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

---

## 5. Performance Metrics

### Overall Heat Transfer Coefficient

$$\frac{1}{U} = \frac{1}{h_h} + \frac{t_w}{k_w} + \frac{1}{h_c}$$

### Effectiveness

$$\varepsilon = \frac{Q_{actual}}{Q_{max}}$$

### Post-Processing

```cpp
// system/controlDict
functions
{
    wallHeatFlux
    {
        type    wallHeatFlux;
        region  fluid;
        patches (interface);
    }
}
```

---

## 6. Best Practices

| Aspect | Recommendation |
|--------|----------------|
| Mesh | Use conformal mesh at interface |
| Solver | GAMG for T, tolerance 1e-6 |
| Relaxation | T: 0.7 for stability |
| Time scale | Consider solid thermal inertia |

### Thermal Time Scale

$$\tau_{thermal} = \frac{\rho c_p L^2}{k}$$

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| Interface mismatch | Check patch names match |
| No heat transfer | Verify `kappaMethod` settings |
| Slow convergence | Lower T relaxation factor |
| Energy imbalance | Check boundary definitions |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ `turbulentTemperatureCoupledBaffleMixed`?</b></summary>

เพราะ BC นี้บังคับให้ **Temperature** และ **Heat Flux** ต่อเนื่องกันที่ interface โดยอัตโนมัติ — ไม่ต้องกำหนดค่าเอง solver จะคำนวณให้
</details>

<details>
<summary><b>2. Conformal mesh ดีกว่า AMI อย่างไรสำหรับ CHT?</b></summary>

Conformal mesh ให้ **direct node-to-node mapping** — ฟลักซ์ความร้อนแม่นยำกว่า ไม่มี interpolation error และลู่เข้าเร็วกว่า
</details>

<details>
<summary><b>3. `heRhoThermo` vs `heSolidThermo` ต่างกันอย่างไร?</b></summary>

- **heRhoThermo**: สำหรับ fluid มี convection term
- **heSolidThermo**: สำหรับ solid มีแค่ conduction (Laplace equation)
</details>

---

## Related Documents

- **บทก่อนหน้า:** [03_Buoyancy_Driven_Flows.md](03_Buoyancy_Driven_Flows.md)
- **ภาพรวม:** [00_Overview.md](00_Overview.md)