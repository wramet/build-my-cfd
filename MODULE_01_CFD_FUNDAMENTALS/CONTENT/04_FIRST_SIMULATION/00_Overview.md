# Day 04: R410A Evaporator Simulation Tutorial
# วันที่ 4: บทช่วยสอนการจำลองการระเหยของสารทำความเย็น R410A

## 1. Overview / ภาพรวม

### What is an R410A Evaporator Simulation?
### การจำลองการระเหยของสารทำความเย็น R410A คืออะไร?

An R410A evaporator simulation models the phase-change heat transfer process inside a horizontal tube where subcooled liquid R410A refrigerant absorbs heat from the tube walls, undergoes evaporation, and exits as a superheated vapor or two-phase mixture. This involves solving coupled conservation equations for mass, momentum, and energy with a phase-change model in a cylindrical coordinate system.

การจำลองการระเหยของสารทำความเย็น R410A เป็นการจำลองกระบวนการถ่ายเทความร้อนพร้อมการเปลี่ยนเฟสภายในท่อแนวนอน โดยสารทำความเย็น R410A ในสถานะของเหลวอิ่มตัวยวดิ่ง (subcooled liquid) ดูดซับความร้อนจากผนังท่อ เกิดการระเหย และออกจากท่อในสถานะไอร้อนยวดยิ่ง (superheated vapor) หรือส่วนผสมสองเฟส กระบวนการนี้ต้องแก้สมการอนุรักษ์มวล โมเมนตัม และพลังงาน ที่เชื่อมโยงกัน พร้อมกับแบบจำลองการเปลี่ยนเฟส ในระบบพิกัดทรงกระบอก

### Why Simulate R410A Evaporators?
### ทำไมต้องจำลองการระเหยของสารทำความเย็น R410A?

R410A is a common refrigerant in air conditioning and heat pump systems. Accurate simulation of its evaporation process is crucial for:
- **System Efficiency Optimization**: Predicting heat transfer coefficients and pressure drops.
- **Component Design**: Sizing evaporator tubes and optimizing fin designs.
- **Transient Behavior Analysis**: Understanding system response during startup and load changes.
- **Environmental Impact Reduction**: Minimizing refrigerant charge and improving COP (Coefficient of Performance).

R410A เป็นสารทำความเย็นที่ใช้ทั่วไปในระบบปรับอากาศและปั๊มความร้อน การจำลองกระบวนการระเหยอย่างแม่นยำมีความสำคัญสำหรับ:
- **การเพิ่มประสิทธิภาพระบบ**: ทำนายค่าสัมประสิทธิภาพการถ่ายเทความร้อนและการสูญเสียแรงดัน
- **การออกแบบส่วนประกอบ**: กำหนดขนาดท่อระเหยและออกแบบครีบให้เหมาะสม
- **การวิเคราะหาพฤติกรรมชั่วขณะ**: ทำความเข้าใจการตอบสนองของระบบระหว่างการเริ่มทำงานและการเปลี่ยนแปลงภาระ
- **การลดผลกระทบต่อสิ่งแวดล้อม**: ลดปริมาณสารทำความเย็นและเพิ่มค่า COP (สัมประสิทธิภาพสมรรถนะ)

### How is This Simulation Different from Lid-Driven Cavity?
### การจำลองนี้แตกต่างจาก Lid-Driven Cavity อย่างไร?

| Aspect / ด้าน | Lid-Driven Cavity | R410A Evaporator |
|--------------|-------------------|------------------|
| **Physics / ฟิสิกส์** | Single-phase incompressible flow | Two-phase flow with phase change |
| **Geometry / เรขาคณิต** | 2D Cartesian square | 2D/3D Cylindrical (axisymmetric) |
| **Equations / สมการ** | Navier-Stokes only | Mass, momentum, energy with source terms |
| **Boundary Conditions / เงื่อนไขขอบเขต** | Moving wall, no-slip | Inlet mass flow, wall heat flux, pressure outlet |
| **Solution Method / วิธีการแก้** | Pressure-velocity coupling (SIMPLE) | Coupled with energy and phase fraction |

---

## 2. Mathematical Formulation / สูตรทางคณิตศาสตร์

### 2.1 Governing Equations / สมการควบคุม

#### Volume of Fluid (VOF) Method with Phase Change
#### วิธีปริมาตรของไหล (VOF) พร้อมการเปลี่ยนเฟส

The volume fraction $\alpha$ represents the liquid phase ($\alpha = 1$: liquid, $\alpha = 0$: vapor). The governing equations are:

ปริมาตรส่วน $\alpha$ แทนเฟสของเหลว ($\alpha = 1$: ของเหลว, $\alpha = 0$: ไอ) สมการควบคุมคือ:

**Continuity Equation with Phase Change Source / สมการความต่อเนื่องพร้อมเทอมต้นกำเนิดการเปลี่ยนเฟส:**

$$
\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = S_m
$$

where $\rho = \alpha \rho_l + (1-\alpha) \rho_v$ is the mixture density, and $S_m$ is the mass source due to phase change.

โดยที่ $\rho = \alpha \rho_l + (1-\alpha) \rho_v$ คือความหนาแน่นของส่วนผสม และ $S_m$ คือเทอมต้นกำเนิดมวลจากการเปลี่ยนเฟส

**Volume Fraction Equation / สมการปริมาตรส่วน:**

$$
\frac{\partial \alpha}{\partial t} + \nabla \cdot (\alpha \mathbf{u}) + \nabla \cdot [\alpha (1-\alpha) \mathbf{u}_r] = \frac{S_m}{\rho_l}
$$

The third term is the compression term at the interface for sharpening.

เทอมที่สามคือเทอมการบีบอัดที่ส่วนต่อประสานเพื่อให้มีความคมชัด

**Momentum Equation / สมการโมเมนตัม:**

$$
\frac{\partial (\rho \mathbf{u})}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) = -\nabla p + \nabla \cdot [\mu (\nabla \mathbf{u} + \nabla \mathbf{u}^T)] + \rho \mathbf{g} + \mathbf{F}_\sigma
$$

where $\mu = \alpha \mu_l + (1-\alpha) \mu_v$ is the mixture viscosity, and $\mathbf{F}_\sigma$ is the surface tension force.

โดยที่ $\mu = \alpha \mu_l + (1-\alpha) \mu_v$ คือความหนืดของส่วนผสม และ $\mathbf{F}_\sigma$ คือแรงตึงผิว

**Energy Equation / สมการพลังงาน:**

$$
\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho h \mathbf{u}) = \nabla \cdot (k \nabla T) + S_e
$$

where $h$ is the specific enthalpy, $k = \alpha k_l + (1-\alpha) k_v$ is the mixture thermal conductivity, and $S_e$ is the energy source from phase change.

โดยที่ $h$ คือเอนทาลปีจำเพาะ, $k = \alpha k_l + (1-\alpha) k_v$ คือค่าการนำความร้อนของส่วนผสม และ $S_e$ คือเทอมต้นกำเนิดพลังงานจากการเปลี่ยนเฟส

### 2.2 Lee Phase Change Model / แบบจำลองการเปลี่ยนเฟสของ Lee

The mass transfer rate per unit volume is modeled as:

อัตราการถ่ายเทมวลต่อหน่วยปริมาตรถูกจำลองเป็น:

**Evaporation ($T_l > T_{sat}$): / การระเหย**

$$
S_m = r_{evap} \alpha \rho_l \frac{T_l - T_{sat}}{T_{sat}}
$$

**Condensation ($T_v < T_{sat}$): / การควบแนนน**

$$
S_m = r_{cond} (1-\alpha) \rho_v \frac{T_{sat} - T_v}{T_{sat}}
$$

where $r_{evap}$ and $r_{cond}$ are empirical coefficients (typically 0.1-100 s⁻¹), and $T_{sat}$ is the saturation temperature at local pressure.

โดยที่ $r_{evap}$ และ $r_{cond}$ คือสัมประสิทธิ์เชิงประจักษ์ (ทั่วไป 0.1-100 s⁻¹) และ $T_{sat}$ คืออุณหภูมิอิ่มตัวที่ความดันในพื้นที่

The energy source term is: / เทอมต้นกำเนิดพลังงานคือ:

$$
S_e = S_m \cdot h_{lv}
$$

where $h_{lv}$ is the latent heat of vaporization.

โดยที่ $h_{lv}$ คือความร้อนแฝงของการระเหย

### 2.3 Cylindrical Coordinate System / ระบบพิกัดทรงกระบอก

For axisymmetric simulations, the equations transform to:

สำหรับการจำลองแบบสมาตรตามแนวแกน สมการจะแปลงเป็น:

**Continuity in Cylindrical Coordinates / สมการความต่อเนื่องในพิกัดทรงกระบอก:**

$$
\frac{\partial \rho}{\partial t} + \frac{1}{r} \frac{\partial (r \rho u_r)}{\partial r} + \frac{\partial (\rho u_z)}{\partial z} = S_m
$$

where $u_r$ is radial velocity and $u_z$ is axial velocity.

โดยที่ $u_r$ คือความเร็วในแนวรัศมี และ $u_z$ คือความเร็วในแนวแกน

---

## 3. Geometry and Mesh / เรขาคณิตและตาข่าย

### 3.1 Horizontal Tube Geometry / เรขาคณิตท่อแนวนอน

```cpp
// Geometry parameters for R410A evaporator tube
struct EvaporatorGeometry {
    double tube_length;      // Tube length in meters (ความยาวท่อ เมตร)
    double tube_radius;      // Tube inner radius in meters (รัศมีภายในท่อ เมตร)
    double wall_thickness;   // Tube wall thickness in meters (ความหนาผนังท่อ เมตร)

    // Constructor with default values (ค่าตั้งต้น)
    EvaporatorGeometry(double L = 1.0, double R = 0.005, double t = 0.001)
        : tube_length(L), tube_radius(R), wall_thickness(t) {}

    // Calculate mesh dimensions (คำนวณขนาดตาข่าย)
    std::pair<int, int> calculateMeshSize(double dr, double dz) const {
        int nr = static_cast<int>(tube_radius / dr) + 1;
        int nz = static_cast<int>(tube_length / dz) + 1;
        return {nr, nz};
    }
};
```

### 3.2 Axisymmetric Mesh Generation / การสร้างตาข่ายแบบสมาตรตามแนวแกน

```cpp
class AxisymmetricMesh {
private:
    std::vector<double> r_pos;  // Radial positions (ตำแหน่งในแนวรัศมี)
    std::vector<double> z_pos;  // Axial positions (ตำแหน่งในแนวแกน)
    int nr, nz;                 // Number of cells in r and z directions (จำนวนเซลล์ในแนว r และ z)

public:
    AxisymmetricMesh(const EvaporatorGeometry& geom,
                     double dr, double dz) {
        auto [nr_calc, nz_calc] = geom.calculateMeshSize(dr, dz);
        nr = nr_calc;
        nz = nz_calc;

        // Generate radial positions (สร้างตำแหน่งในแนวรัศมี)
        r_pos.resize(nr + 1);
        for (int i = 0; i <= nr; ++i) {
            r_pos[i] = i * dr;
        }

        // Generate axial positions (สร้างตำแหน่งในแนวแกน)
        z_pos.resize(nz + 1);
        for (int j = 0; j <= nz; ++j) {
            z_pos[j] = j * dz;
        }
    }

    // Calculate cell volume for axisymmetric coordinates (คำนวณปริมาตรเซลล์สำหรับพิกัดทรงกระบอก)
    double cellVolume(int i, int j) const {
        double r_face_inner = r_pos[i];
        double r_face_outer = r_pos[i + 1];
        double dz_cell = z_pos[j + 1] - z_pos[j];

        // Volume of cylindrical shell (ปริมาตรของเปลือกทรงกระบอก)
        return M_PI * (r_face_outer * r_face_outer -
                      r_face_inner * r_face_inner) * dz_cell;
    }

    // Calculate face areas for flux calculations (คำนวณพื้นที่หน้าสำหรับการคำนวณฟลักซ์)
    struct FaceAreas {
        double radial_inner;   // Area at inner radial face (พื้นที่ที่หน้าสัมผัสรัศมีด้านใน)
        double radial_outer;   // Area at outer radial face (พื้นที่ที่หน้าสัมผัสรัศมีด้านนอก)
        double axial_lower;    // Area at lower axial face (พื้นที่ที่หน้าสัมผัสแนวแกนด้านล่าง)
        double axial_upper;    // Area at upper axial face (พื้นที่ที่หน้าสัมผัสแนวแกนด้านบน)
    };

    FaceAreas calculateFaceAreas(int i, int j) const {
        FaceAreas areas;
        double r_inner = r_pos[i];
        double r_outer = r_pos[i + 1];
        double r_mid = 0.5 * (r_inner + r_outer);
        double dz = z_pos[j + 1] - z_pos[j];

        areas.radial_inner = 2 * M_PI * r_inner * dz;
        areas.radial_outer = 2 * M_PI * r_outer * dz;
        areas.axial_lower = M_PI * (r_outer * r_outer - r_inner * r_inner);
        areas.axial_upper = areas.axial_lower;

        return areas;
    }
};
```

---

## 4. Boundary Conditions / เงื่อนไขขอบเขต

### 4.1 Inlet Condition (Subcooled Liquid) / เงื่อนไขทางเข้า (ของเหลวอิ่มตัวยวดยิ่ง)

```cpp
class InletBoundary {
private:
    double mass_flow_rate;    // kg/s
    double T_inlet;           // K (subcooled temperature)
    double alpha_inlet;       // Volume fraction (1.0 for liquid)

public:
    InletBoundary(double m_dot = 0.01, double T = 280.0, double alpha = 1.0)
        : mass_flow_rate(m_dot), T_inlet(T), alpha_inlet(alpha) {}

    // Calculate inlet velocity based on mass flow rate (คำนวณความเร็วทางเข้าจากอัตราการไหลของมวล)
    double calculateInletVelocity(double rho_liquid, double tube_area) const {
        return mass_flow_rate / (rho_liquid * tube_area);
    }

    // Apply boundary conditions to ghost cells (กำหนดเงื่อนไขขอบเขตให้เซลล์ปลอม)
    template<typename Field>
    void apply(Field& u, Field& v, Field& T, Field& alpha,
               double rho_l, double area, int inlet_face_index) {
        double u_in = calculateInletVelocity(rho_l, area);

        // Set values at inlet face (กำหนดค่าที่หน้าทางเข้า)
        u(inlet_face_index) = u_in;
        v(inlet_face_index) = 0.0;  // No radial velocity at inlet (ไม่มีความเร็วในแนวรัศมีที่ทางเข้า)
        T(inlet_face_index) = T_inlet;
        alpha(inlet_face_index) = alpha_inlet;
    }
};
```

### 4.2 Wall Condition (Heat Flux or Fixed Temperature) / เงื่อนไขผนัง (ฟลักซ์ความร้อนหรืออุณหภูมิคงที่)

```cpp
class WallBoundary {
public:
    enum class WallType {
        HEAT_FLUX,      // Constant heat flux (ฟลักซ์ความร้อนคงที่)
        FIXED_TEMP      // Fixed temperature (อุณหภูมิคงที่)
    };

private:
    WallType type;
    double q_wall;      // Heat flux (W/m²) for HEAT_FLUX
    double T_wall;      // Temperature (K) for FIXED_TEMP

public:
    WallBoundary(WallType t, double value) : type(t) {
        if (type == WallType::HEAT_FLUX) {
            q_wall = value;
        } else {
            T_wall = value;
        }
    }

    // Calculate wall temperature based on local conditions (คำนวณอุณหภูมิผนังจากสภาวะในพื้นที่)
    double calculateWallTemperature(double T_cell, double k_cell,
                                    double distance, double q_local = 0.0) const {
        if (type == WallType::FIXED_TEMP) {
            return T_wall;
        } else {
            // For heat flux: T_wall = T_cell + (q_wall * distance / k_cell)
            return T_cell + (q_wall * distance / k_cell);
        }
    }

    // Apply no-slip and thermal boundary conditions (กำหนดเงื่อนไขขอบเขตไม่ไถลและความร้อน)
    void applyNoSlipAndHeatTransfer(auto& u, auto& v,
                                    auto& T, int wall_index,
                                    const auto& k,
                                    const auto& dist_to_wall) {
        // No-slip condition (เงื่อนไขไม่ไถล)
        u[wall_index] = 0.0;
        v[wall_index] = 0.0;

        // Thermal boundary condition (เงื่อนไขขอบเขตความร้อน)
        for (int j = 0; j < T.size(); ++j) {
            if (type == WallType::FIXED_TEMP) {
                T[wall_index][j] = T_wall;
            } else {
                // For heat flux, set temperature in ghost cell based on flux
                T[wall_index][j] = calculateWallTemperature(
                    T[wall_index + 1][j], k[wall_index + 1][j],
                    dist_to_wall[wall_index][j]);
            }
        }
    }
};
```

### 4.3 Outlet Condition (Pressure Outlet) / เงื่อนไขทางออก (ความดันทางออก)

```cpp
class PressureOutletBoundary {
private:
    double P_out;  // Outlet pressure (Pa)

public:
    PressureOutletBoundary(double P = 101325.0) : P_out(P) {}

    // Apply zero-gradient for most variables (กำหนดเกรเดียนต์เป็นศูนย์สำหรับตัวแปรส่วนใหญ่)
    template<typename Field>
    void applyZeroGradient(Field& phi, int outlet_face_index) {
        // phi(outlet) = phi(interior)
        int interior_index = outlet_face_index - 1;
        phi[outlet_face_index] = phi[interior_index];
    }

    // Special treatment for pressure (การจัดการพิเศษสำหรับความดัน)
    void applyPressure(auto& p, int outlet_face_index) {
        p[outlet_face_index] = P_out;
    }

    // Handle backflow prevention (จัดการป้องกันการไหลย้อนกลับ)
    bool checkBackflow(const auto& u, int outlet_face_index) {
        // Check if velocity at outlet is negative (backflow)
        return u[outlet_face_index] < 0.0;
    }
};
```

---

## 5. Material Properties of R410A / คุณสมบัติของวัสดุ R410A

> **⭐ R410A Properties at 20°C (293 K) and 8 bar**
>
> **⭐ คุณสมบัติของ R410A ที่ 20°C (293 K) และ 8 บาร์**

| Property / คุณสมบัติ | Liquid / ของเหลว | Vapor / ไอ |
|---------------------------|------------------|--------|
| Density / ความหนาแน่น (kg/m³) | 1099.7 | 65.62 |
| Viscosity / ความหนืด (Pa·s) | 145.2 × 10⁻⁶ | 13.82 × 10⁻⁶ |
| Thermal Conductivity (W/m·K) | 0.0952 | 0.0187 |
| Specific Heat (J/kg·K) | 1612 | 1085 |
| Saturation Enthalpy (kJ/kg) | 246.2 | 452.8 |

### Property Table vs Temperature
### ตารางคุณสมบัติเทียบกับอุณหภูมิ

| T (°C) | P_sat (kPa) | ρ_liquid | ρ_vapor | h_liquid | h_vapor |
|---------|--------------|----------|----------|-----------|-----------|
| -20 | 354.6 | 1245.2 | 18.34 | 189.5 | 429.8 |
| -10 | 497.1 | 1210.8 | 25.96 | 203.2 | 436.1 |
| 0 | 678.9 | 1175.3 | 35.92 | 217.2 | 442.1 |
| 10 | 909.1 | 1138.4 | 48.87 | 231.5 | 447.7 |
| 20 | 1198.5 | 1099.7 | 65.62 | 246.2 | 452.8 |
| 30 | 1558.9 | 1058.6 | 87.21 | 261.4 | 457.2 |

---

## 6. Phase Change Implementation / การนำการเปลี่ยนเฟสไปใช้

### 6.1 Lee Model Implementation / การนำแบบจำลอง Lee ไปใช้

```cpp
class LeePhaseChangeModel {
private:
    double r_evap;  // Evaporation coefficient (s⁻¹)
    double r_cond;  // Condensation coefficient (s⁻¹)
    double latent_heat;  // Latent heat of vaporization (J/kg)

public:
    LeePhaseChangeModel(double r_e = 0.1, double r_c = 0.1, double h_lv = 200000.0)
        : r_evap(r_e), r_cond(r_c), latent_heat(h_lv) {}

    // Calculate mass transfer rate (คำนวณอัตราการถ่ายเทมวล)
    auto calculateMassSource(
        const auto& alpha,
        const auto& T,
        const auto& T_sat,
        const auto& rho_l,
        const auto& rho_v) {

        // Mass source from evaporation/condensation
        auto S_m = alpha * r_evap * rho_l * (T - T_sat) / T_sat;
        auto S_e = S_m * latent_heat;

        return std::make_pair(S_m, S_e);
    }

    // Update volume fraction field (อัปเดตฟิลด์ปริมาตรส่วน)
    void updateVolumeFraction(auto& alpha, const auto& S_m, double dt) {
        for (int i = 0; i < alpha.size(); ++i) {
            alpha[i] -= S_m[i] * dt / rho_l[i];
            alpha[i] = std::max(0.0, std::min(1.0, alpha[i]));
        }
    }
};
```

---

## 7. Solution Algorithm / อัลกอริทึมการแก้

### 7.1 PISO Algorithm with Phase Change
### อัลกอริทึม PISO พร้อมการเปลี่ยนเฟส

```cpp
class EvaporatorSolver {
private:
    // Fields
    std::vector<double> u, v;      // Velocities (radial, axial)
    std::vector<double> p;         // Pressure
    std::vector<double> T;         // Temperature
    std::vector<double> alpha;     // Volume fraction (liquid)

    // Models
    R410AProperties r410a;
    LeePhaseChangeModel phase_change;
    AxisymmetricMesh mesh;

public:
    void solveTimeStep(double dt) {
        // PISO loop for pressure-velocity coupling with phase change

        // 1. Predict velocity (momentum predictor)
        solveMomentumPredictor(dt);

        // 2. PISO loop (2-3 iterations)
        for (int corr = 0; corr < 2; ++corr) {
            solvePressureCorrection();
            correctVelocity();
        }

        // 3. Solve energy equation
        solveEnergyEquation(dt);

        // 4. Update void fraction
        solveVoidFraction(dt);
    }

private:
    void solveMomentumPredictor(double dt) {
        // Explicit momentum prediction
        for (int i = 1; i < u.size() - 1; ++i) {
            u[i] += dt * calculateMomentumRHS(i);
            v[i] += dt * calculateMomentumRHS_v(i);
        }
    }

    void solvePressureCorrection() {
        // Pressure correction from continuity
        solvePressureEquation();
    }

    void solveEnergyEquation(double dt) {
        // Energy equation with phase change source
        for (int i = 1; i < T.size() - 1; ++i) {
            T[i] += dt * calculateEnergyRHS(i);
        }
    }

    void solveVoidFraction(double dt) {
        // Update alpha based on phase change
        auto [S_m, S_e] = phase_change.calculateMassSource(
            alpha, T, T_sat, rho_l, rho_v);
        for (int i = 1; i < alpha.size() - 1; ++i) {
            alpha[i] += dt * (-S_m[i] / rho_l[i]);
            alpha[i] = std::clamp(alpha[i], 0.0, 1.0);
        }
    }
};
```

---

## 8. Expected Results / ผลลัพธ์ที่คาดหวัง

### 8.1 Flow Characteristics / ลักษณะการไหล

**Typical evaporator flow pattern:**
- **Inlet region**: Subcooled liquid (α = 1.0, T < T_sat)
- **Evaporation zone**: Two-phase mixture (0 < α < 1), T ≈ T_sat
- **Outlet region**: Superheated vapor (α = 0.0, T > T_sat) or two-phase

### 8.2 Heat Transfer Performance / สมรรปะสิทธิภาพการถ่ายเทความร้อน

| Metric / ตัวชี้ | Expected / ค่าที่คาดหวัง |
|--------------------|----------------------------|
| Heat Transfer Coefficient | 500-5000 W/m²·K (depending on mass flux) |
| Pressure Drop | 10-50 kPa per meter (typical for evaporators) |
| Outlet Quality | 0.8-1.0 (superheated or slightly two-phase) |
| Temperature Rise | 5-15 K (depending on heat load) |

### 8.3 Validation Metrics / เกณท์วัดค่าความถูกต้อง

**Mass Conservation:**
$$
\dot{m}_{in} = \dot{m}_{out} + \int \dot{m}_{phase-change} \, dV
$$

**Energy Balance:**
$$
\dot{Q}_{wall} = \dot{m}_{out} h_{out} - \dot{m}_{in} h_{in} + \dot{m}_{phase-change} h_{lv}
$$

---

## 9. Implementation Checklist / รายการอองการนำไปใช้

### Setup Checklist / รายการเตรียบ

**Geometry & Mesh:**
- [ ] Define tube geometry (length, radius, wall thickness)
- [ ] Generate axisymmetric mesh (radial × axial cells)
- [ ] Verify mesh quality (aspect ratio, non-orthogonality)

**Initial Conditions:**
- [ ] Set inlet: subcooled liquid (α = 1.0, T_in = 280 K)
- [ ] Set outlet: fixed pressure (P_out = 8-12 bar)
- [ ] Set walls: fixed temperature (T_wall = 285-295 K)
- [ ] Initialize fields (u, v, p, T, α)

**Boundary Conditions:**
- [ ] Inlet: Fixed mass flow rate, subcooled liquid
- [ ] Outlet: Fixed pressure, zero-gradient for other variables
- [ ] Walls: No-slip velocity, fixed T or heat flux
- [ ] Axis: Axisymmetric (zero gradient)

**Solver Settings:**
- [ ] Time step: Satisfy CFL < 0.5
- [ ] Under-relaxation factors: 0.3-0.7 for pressure
- [ ] Convergence criteria: Residuals < 1e-4
- [ ] Output: Write every 0.01-0.05 seconds

### Verification / การตรวจสอบ

- [ ] Mass conservation: $\dot{m}_{in} \approx \dot{m}_{out}$
- [ ] Energy balance: $Q_{in} + Q_{wall} = Q_{out}$
- [ ] Void fraction bounded: 0 ≤ α ≤ 1
- [ ] No unphysical velocities
- [ ] Temperature within realistic range

---

## 10. Comparison with Lid-Driven Cavity
## 10. เปรียบเทียบกับ Lid-Driven Cavity

| Aspect / ด้าน | Lid-Driven Cavity | R410A Evaporator |
|--------------|-------------------|------------------|
| **Physics / ฟิสิกส์** | Single-phase incompressible | Two-phase flow with phase change |
| **Geometry / เรขาคณิต** | 2D Cartesian square | 2D/3D Cylindrical (axisymmetric) |
| **Equations / สมการ** | Navier-Stokes only | Mass, momentum, energy with source terms |
| **Boundary Conditions / เงื่อนไขขอบเขต** | Moving wall, no-slip | Inlet mass flow, wall heat flux, pressure outlet |
| **Solution Method / วิธีการแก้** | Pressure-velocity coupling (SIMPLE) | Coupled with energy and phase fraction |
| **Validation / การตรวจสอบ** | Ghia et al. (1982) | Experimental evaporator data |

---

## Key Takeaways / ประเด็นสำคัญ

### 🎯 Core Concepts

1. **R410A evaporator simulation** involves two-phase flow with phase change - This is the target application for the custom CFD engine
   **การจำลองเครื่องงาน R410A เกี่ยวกับการไหลสองเฟสพร้อมกับการเปลี่ยนเฟส - นี่คือ application หลักของ custom CFD engine

2. **Cylindrical coordinates are essential** for tube flow - Cartesian coordinates don't work well for pipes
   **พิกัดทรงกระบอกเป็นสิ่งทางสำหรับการไหลในท่อ - พิกัด Cartesian ไม่ทำงงานดีสำหรับท่อ

3. **Energy equation is coupled** with phase change - latent heat cannot be ignored
   **สมการพลังงานเชื่อมโยงกับการเปลี่ยนเฟส - ความร้อนแฝงไม่สามาระเพิเพิเหตุ

4. **Expansion term in continuity** accounts for density changes during evaporation
   **เทอม expansion ในสมการความต่อเนื่องอธิบาย density ระหว่างการระเหย**

### 🔧 Implementation Focus

**Key differences from lid-driven cavity:**
- Geometry: Square box → Horizontal tube
- Physics: Single-phase → Two-phase with evaporation
- Equations: 2 equations (mass + momentum) → 4 equations (mass, momentum, energy, void fraction)
- Boundary conditions: Lid moving → Inlet mass flow + heat flux walls

**⭐ This is the RIGHT simulation for R410A evaporator application**

---

## 📖 References / เอกสารที่เกี่ยวข้อง

1. **Thome, J.R.** "Two-phase heat transfer in microchannels" (2004)
2. **Kandlikar, S.** "Heat transfer and pressure drop in microchannels" (2010)
3. **Carey, V.P.** "Liquid-vapor phase change" (2020)
4. **OpenFOAM User Guide** - interFoam and compressibleInterFoam solvers
5. **ASHRAE Handbook - Fundamentals** - Refrigerant properties
6. **MODULE_05 (Two-Phase Flow)** for detailed VOF implementation
7. **MODULE_07 (Refrigerant Properties)** for CoolProp integration

---

*Last Updated: 2026-01-27*
*⭐ Content aligned with R410A evaporator simulation goal*
*⚠️ Requires CoolProp library for property calculations*