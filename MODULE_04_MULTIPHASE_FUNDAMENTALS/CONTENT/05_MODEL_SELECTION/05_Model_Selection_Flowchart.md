# Model Selection Flowchart

คู่มือเลือก Drag, Lift, Turbulence, และ Heat Transfer models สำหรับ Multiphase Flow

---

## Quick Selection Guide

### Phase System → Drag Model

| System | Condition | Drag Model |
|--------|-----------|------------|
| **Gas-Liquid** | d < 1mm (spherical) | SchillerNaumann |
| **Gas-Liquid** | d > 1mm (deformed) | Tomiyama |
| **Gas-Solid** | Dilute (α < 0.2) | WenYu |
| **Gas-Solid** | Dense / Packed | Gidaspow / Ergun |
| **Gas-Solid** | Fluidized bed | SyamlalOBrien |
| **Liquid-Liquid** | Eo < 0.5 (spherical) | SchillerNaumann |
| **Liquid-Liquid** | Eo > 0.5 (deformed) | Grace |

---

## 1. Drag Model Selection

### Decision Flowchart

```
Is it Gas-Liquid?
├── Yes → Is bubble diameter > 1mm?
│   ├── Yes → Tomiyama (deformable)
│   └── No  → SchillerNaumann (spherical)
└── No  → Is it Gas-Solid?
    ├── Yes → Is αs > 0.4 (packed)?
    │   ├── Yes → Ergun or Gidaspow
    │   └── No  → WenYu or SyamlalOBrien
    └── No  → Liquid-Liquid
        └── Use Grace or SchillerNaumann based on Eo
```

### Key Parameters

**Particle Reynolds Number:**
$$Re_p = \frac{\rho_c u_{rel} d_p}{\mu_c}$$

**Eötvös Number:**
$$Eo = \frac{g(\rho_c - \rho_d)d_p^2}{\sigma}$$

| Re_p | Regime | Model |
|------|--------|-------|
| < 1 | Creeping | Stokes |
| 1-1000 | Transitional | Schiller-Naumann |
| > 1000 | Inertial | Ishii-Zuber |

### OpenFOAM Configuration

```cpp
// constant/phaseProperties
phaseInteraction
{
    dragModel       Tomiyama;  // or SchillerNaumann, WenYu, etc.
    
    TomiyamaCoeffs
    {
        C1    0.44;   // High Re drag
        C2    24.0;   // Low Re (24/Re)
        C3    0.15;   // Re exponent
        C4    6.0;    // Eo correction
    }
}
```

---

## 2. Lift Model Selection

| Condition | Lift Model | Notes |
|-----------|------------|-------|
| Solid particles, Re < 1000 | SaffmanMei | Shear-induced |
| Gas bubbles in liquid | Tomiyama | Sign reversal for large bubbles |
| Not important | NoLift | Faster computation |

**Lift Force:**
$$\mathbf{F}_L = C_L \rho_c V_b (\mathbf{u}_d - \mathbf{u}_c) \times (\nabla \times \mathbf{u}_c)$$

```cpp
phaseInteraction
{
    liftModel       Tomiyama;  // or SaffmanMei, NoLift
    
    TomiyamaCoeffs
    {
        CL    0.5;    // Positive = towards wall
    }
}
```

---

## 3. Turbulence Model Selection

| System | αd Range | Model |
|--------|----------|-------|
| Dilute bubbly | < 0.1 | kEpsilon |
| Dense bubbly | > 0.1 | mixtureKEpsilon |
| Gas-Solid dilute | < 0.1 | dispersedPhase |
| Gas-Solid dense | > 0.3 | perPhase kEpsilon |

### OpenFOAM Configuration

```cpp
// constant/turbulenceProperties
simulationType  RAS;

RAS
{
    RASModel    kEpsilon;  // or mixtureKEpsilon, kOmegaSST
    
    kEpsilonCoeffs
    {
        Cmu         0.09;
        C1          1.44;
        C2          1.92;
        sigmaK      1.0;
        sigmaEps    1.3;
    }
}
```

```cpp
// constant/phaseProperties
phaseInteraction
{
    turbulentDispersionModel    Simonin;  // or Burns, None
}
```

---

## 4. Heat Transfer Model Selection

**Peclet Number:**
$$Pe = Re_p \cdot Pr$$

| Pe | Regime | Model |
|----|--------|-------|
| < 10 | Conduction dominant | Spherical |
| > 10 | Convection dominant | RanzMarshall |
| High Re, turbulent | — | Gunn |

**Ranz-Marshall:**
$$Nu = 2 + 0.6 Re_p^{0.5} Pr^{0.33}$$

```cpp
phaseInteraction
{
    heatTransferModel    RanzMarshall;
    
    RanzMarshallCoeffs
    {
        Pr    0.7;  // Prandtl number
    }
}
```

---

## 5. Virtual Mass Model

| Condition | Model | Cvm |
|-----------|-------|-----|
| Heavy particles (ρd/ρc > 1000) | negligible | — |
| Light particles/bubbles | constant | 0.5 |
| Variable (research) | Zuber | f(α) |

```cpp
phaseInteraction
{
    virtualMassModel    constant;
    
    constantCoeffs
    {
        Cvm    0.5;  // Typically 0.5 for spheres
    }
}
```

---

## Complete Example

```cpp
// constant/phaseProperties
phases
{
    water { type liquid; }
    air   { type gas; }
}

phaseInteraction
{
    // Drag: deformable bubbles
    dragModel       Tomiyama;
    
    // Lift: bubble migration
    liftModel       Tomiyama;
    
    // Virtual mass: light bubbles
    virtualMassModel constant;
    constantCoeffs { Cvm 0.5; }
    
    // Turbulent dispersion
    turbulentDispersionModel Simonin;
    
    // Heat transfer
    heatTransferModel RanzMarshall;
}
```

---

## Troubleshooting

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| Unrealistic bubble velocities | Wrong drag model | Check Eo, use Tomiyama |
| Wall peaking incorrect | Lift model issue | Use Tomiyama lift |
| Unstable near packed bed | Wrong dense model | Switch to Gidaspow/Ergun |
| Poor heat transfer | Wrong Nu correlation | Check Pe, use Gunn if high Re |

---

## Concept Check

<details>
<summary><b>1. เมื่อไหร่ควรใช้ Tomiyama แทน Schiller-Naumann?</b></summary>

เมื่อ bubble diameter > 1mm หรือ Eo > 1 — เพราะ bubbles เริ่ม deform และ Schiller-Naumann ไม่รองรับ deformation effects
</details>

<details>
<summary><b>2. Gidaspow model ใช้เมื่อไหร่?</b></summary>

ใช้กับ Gas-Solid systems ที่มี solid fraction สูง — มันรวม Wen-Yu (dilute) กับ Ergun (packed) ด้วย blending function
</details>

<details>
<summary><b>3. ทำไม virtual mass สำคัญสำหรับ bubbles?</b></summary>

เพราะ bubbles มี density ต่ำกว่า liquid มาก — การเร่งตัวของ bubble ต้องเร่ง surrounding liquid ด้วย ซึ่ง virtual mass model จับ effect นี้
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [04_Solid_Solid_Systems.md](04_Solid_Solid_Systems.md)
- **บทถัดไป:** [../06_IMPLEMENTATION/00_Overview.md](../06_IMPLEMENTATION/00_Overview.md)