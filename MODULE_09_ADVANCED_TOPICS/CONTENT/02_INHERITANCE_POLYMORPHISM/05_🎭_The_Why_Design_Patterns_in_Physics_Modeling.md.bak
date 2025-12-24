# 🎭 "ทำไม": Design Patterns ในการจำลองทางฟิสิกส์

## 1. Strategy Pattern: อัลกอริธึมที่สามารถสลับทดแทนกันได้

Strategy Pattern เป็นพื้นฐานของสถาปัตยกรรมแบบโมดูลาร์ของ OpenFOAM สำหรับการจำลองทางฟิสิกส์ ในบริบทของ drag models แต่ละ drag correlation (`SchillerNaumann`, `Ergun`, `WenYu` เป็นต้น) จะใช้งาน interface ทั่วไปเดียวกัน แต่ห่อหุ้ม physical correlations ที่แตกต่างกันไว้ โค้ด solver จะมอบหมายการคำนวณ drag จริงให้กับ strategy object โดยไม่ต้องรู้รายละเอียดการใช้งานเฉพาะ

**กรอบงานคณิตศาสตร์**: drag models ทั้งหมดใช้งาน interface:
$$K_d = \text{drag\_model}.K(\alpha_c, \alpha_d, \mathbf{u}_c, \mathbf{u}_d, \rho_c, \rho_d, \mu_c, \mu_d, d_p)$$

โดยแต่ละโมเดลจะให้ correlation ของตนเอง:
- **Schiller-Naumann**: $K_d = \frac{3}{4}C_D\frac{\alpha_c\alpha_d\rho_c|\mathbf{u}_c - \mathbf{u}_d|}{d_p}$
- **Ergun**: $K_d = 150\frac{\alpha_d^2\mu_c(1-\alpha_c)}{\alpha_c^3d_p^2} + 1.75\frac{\alpha_c\alpha_d\rho_c|\mathbf{u}_c - \mathbf{u}_d|}{d_p}$
- **Wen-Yu**: $K_d = \frac{3}{4}C_D\frac{\alpha_c(1-\alpha_c)^{2.65}\rho_c|\mathbf{u}_c - \mathbf{u}_d|}{d_p}$

**การใช้งานโค้ด**:
```cpp
// Base drag model interface
class dragModel {
public:
    virtual tmp<volScalarField> K
    (
        const phaseModel& continuous,
        const phaseModel& dispersed
    ) const = 0;
};

// Schiller-Naumann implementation
class SchillerNaumannDrag : public dragModel {
    tmp<volScalarField> K
    (
        const phaseModel& continuous,
        const phaseModel& dispersed
    ) const override {
        // Calculate Reynolds number
        volScalarField Re = continuous.rho()*continuous.U()*dispersed.d()/continuous.mu();
        
        // Calculate drag coefficient
        volScalarField Cd = 24.0/Re*(1.0 + 0.15*pow(Re, 0.687));
        
        // Calculate drag coefficient K
        return 3.0/4.0*Cd*continuous.rho()*mag(continuous.U() - dispersed.U())*
               dispersed.alpha()*continuous.alpha()/(dispersed.d());
    }
};
```

**ประโยชน์หลัก**:
- **Extensibility**: drag correlations ใหม่สามารถเพิ่มได้โดยใช้งาน interface โดยไม่ต้องแก้ไขโค้ด solver ที่มีอยู่
- **Runtime Configuration**: drag models สามารถเลือกผ่าน dictionary input โดยไม่ต้องคอมไพล์ใหม่
- **Validation**: แต่ละโมเดลสามารถทดสอบและตรวจสอบได้โดยอิสระ
- **Maintainability**: การแก้ไขข้อบกพร่องหรือการปรับปรุง drag model หนึ่งๆ ไม่กระทบกับอื่น

## 2. Template Method Pattern: การขยายแบบควบคุม

Template Method Pattern ถูกใช้งานอย่างกว้างขวางในลำดับชั้นของ phase model ของ OpenFOAM เพื่อกำหนดโครงสร้างอัลกอริธึมมาตรฐานในขณะที่อนุญาตให้ปรับแต่งแบบเลือกได้ Non-Virtual Interface (NVI) pattern ถูกใช้งานโดยที่ public methods เป็น non-virtual และเรียก private virtual methods

**โครงสร้างอัลกอริธึม**: ฐาน `phaseModel` กำหนดโครงร่างของ correction algorithm:
```cpp
class phaseModel {
public:
    // Public non-virtual interface - controls algorithm flow
    virtual void correct() {
        // Template method calls
        preCorrect();           // Hook method - optional override
        correctThermo();        // Pure virtual - must implement
        correctTurbulence();    // Virtual - may override
        correctSpecies();       // Virtual - may override  
        postCorrect();          // Hook method - optional override
        updateFields();         // Fixed final step - cannot override
    }

private:
    // Pure virtual - derived classes MUST provide implementation
    virtual void correctThermo() = 0;
    
    // Virtual with default implementation - derived classes MAY override
    virtual void correctTurbulence() {
        // Default turbulence correction (may be no-op)
    }
    
    virtual void correctSpecies() {
        // Default species correction (may be no-op)
    }
    
    // Hook methods with default empty implementations
    virtual void preCorrect() {}
    virtual void postCorrect() {}
    
    // Final method - cannot be overridden
    virtual void updateFields() final {
        // Fixed base behavior - update all field references
        alpha2_ = 1.0 - alpha1_;
        rho_ = alpha1_*rho1_ + alpha2_*rho2_;
        // ... other field updates
    }
};
```

**กรอบงานคณิตศาสตร์**: template method ทำให้มั่นใจได้ถึงลำดับการประเมินที่สอดคล้องกัน:
$$\text{Correct}() = \begin{cases}
\text{PreCorrect}() & \text{optional pre-processing} \\
\text{CorrectThermo}() & \text{mandatory thermodynamic update} \\
\text{CorrectTurbulence}() & \text{optional turbulence update} \\
\text{CorrectSpecies}() & \text{optional species transport} \\
\text{PostCorrect}() & \text{optional post-processing} \\
\text{UpdateFields}() & \text{mandatory field consolidation}
\end{cases}$$

**ตัวอย่างการใช้งาน**:
```cpp
// Incompressible phase model
class incompressiblePhase : public phaseModel {
private:
    void correctThermo() override {
        rho_ = rho0_;  // Constant density
        // No temperature/pressure coupling for incompressible
    }
};

// Compressible phase model  
class compressiblePhase : public phaseModel {
private:
    void correctThermo() override {
        // Update thermophysical properties based on T, p
        thermo_->correct();
        rho_ = thermo_->rho();
    }
    
    void correctSpecies() override {
        // Update species concentrations
        forAll(species_, i) {
            species_[i].correct();
        }
    }
};
```

**ประโยชน์หลัก**:
- **Consistency**: phase models ทั้งหมดทำตามลำดับการแก้ไขเดียวกัน
- **Maintainability**: คลาสฐานควบคุมโครงสร้างอัลกอริธึม ป้องกันข้อผิดพลาดทั่วไป
- **Flexibility**: คลาสที่ได้รับสืบทอดสามารถปรับแต่งขั้นตอนเฉพาะในขณะที่รักษากระแสโดยรวม
- **Safety**: การดำเนินงานที่สำคัญ (เช่น `updateFields()`) ไม่สามารถถูกแทนที่โดยไม่ตั้งใจได้

## 3. Factory Method Pattern: การสร้างแบบแยกจากกัน

Factory Method Pattern เป็นศูนย์กลางของระบบการกำหนดค่า runtime ของ OpenFOAM รูปแบบเมธอด `New()` แยกการสร้างออบเจกต์ออกจากโค้ดไคลเอนต์ ทำให้สามารถกำหนดค่าโดย dictionary-driven และ plugin architectures ได้

**สถาปัตยกรรมหลัก**:
```cpp
// Base class with factory method
class dragModel {
public:
    // Factory method - creates appropriate model based on dictionary
    static autoPtr<dragModel> New
    (
        const dictionary& dict,
        const phaseModel& continuous,
        const phaseModel& dispersed
    );
    
    // Runtime polymorphism interface
    virtual tmp<volScalarField> K
    (
        const phaseModel& continuous, 
        const phaseModel& dispersed
    ) const = 0;
};

// Factory implementation
autoPtr<dragModel> dragModel::New
(
    const dictionary& dict,
    const phaseModel& continuous,
    const phaseModel& dispersed
) {
    // Read model name from dictionary
    const word dragModelType(dict.lookup("type"));
    
    // Constructor table lookup
    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(dragModelType);
    
    if (cstrIter == dictionaryConstructorTablePtr_->end()) {
        FatalErrorIn("dragModel::New")
            << "Unknown dragModel type " << dragModelType 
            << nl << nl << "Valid dragModel types are:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }
    
    // Create and return appropriate model
    return cstrIter()(dict, continuous, dispersed);
}
```

**กลไกการลงทะเบียน**:
```cpp
// In each derived class header (e.g., SchillerNaumannDrag.H)
addToRunTimeSelectionTable
(
    dragModel,
    SchillerNaumannDrag,
    dictionary
);

// Macro expansion creates:
namespace Foam
{
    // Static registration object
    dragModel::dictionaryConstructorTable::add
        addSchillerNaumannDragToRunTimeSelectionTable
        (
            "SchillerNaumann",
            SchillerNaumannDrag::New
        );
}
```

**การกำหนดค่า Dictionary**:
```cpp
// In transportProperties dictionary
dragModels
{
    water.air
    {
        type            SchillerNaumann;  // Factory selection key
        coefficient     0.44;            // Model-specific parameters
        residualRe      1e-3;
    }
    
    oil.water  
    {
        type            Ergun;           // Different model selection
        alphaMax        0.62;
        beta            150.0;
    }
}
```

**กรอบงานคณิตศาสตร์**: Factory ทำให้เลือกโมเดล runtime ได้:
$$K_d = \text{Factory}(\text{type}) \rightarrow K_{\text{specific}}(\text{parameters})$$

**ประโยชน์หลัก**:
- **Runtime Configuration**: โมเดลเลือกผ่าน dictionary โดยไม่ต้องคอมไพล์โค้ดใหม่
- **Plugin Architecture**: โมเดลใหม่สามารถเพิ่มเป็น plugins โดยไม่ต้องแก้ไขโค้ดที่มีอยู่
- **Type Safety**: การตรวจสอบระยะ compile time ของ model interfaces
- **Dependency Injection**: โมเดลถูกแทรกด้วย dependencies ที่จำเป็นทั้งหมด

## 4. Composite Pattern: ระบบลำดับชั้น

Composite Pattern ทำให้ OpenFOAM สามารถจัดการ phases แบบแยกและ phase systems ด้วย interfaces ที่สม่ำเสมอ ทำให้ระบบ multiphase ที่ซับซ้อนสามารถจัดการเป็น hierarchical collections ได้

**สถาปัตยกรรมหลัก**:
```cpp
// Composite class - manages collection of phases
class phaseSystem {
private:
    // Collection of individual phase models
    PtrList<phaseModel> phases_;
    
    // Phase interaction models
    PtrList<dragModel> dragModels_;
    PtrList<liftModel> liftModels_;
    
public:
    // Uniform interface for whole system
    virtual void correct() {
        // Operate on all phases uniformly
        forAll(phases_, phasei) {
            phases_[phasei].correct();
        }
        
        // Operate on all interactions uniformly  
        forAll(dragModels_, pairi) {
            dragModels_[pairi].correct();
        }
    }
    
    // Calculate system-level properties
    virtual tmp<volScalarField> totalDensity() const {
        tmp<volScalarField> trho = phases_[0].rho()*phases_[0].alpha();
        
        for(label i = 1; i < phases_.size(); i++) {
            trho.ref() += phases_[i].rho()*phases_[i].alpha();
        }
        
        return trho;
    }
};

// Leaf class - individual phase
class phaseModel {
protected:
    volScalarField alpha_;      // Volume fraction
    volScalarField rho_;        // Density  
    volVectorField U_;          // Velocity
    
public:
    // Same interface as composite for uniformity
    virtual void correct() {
        // Update individual phase properties
        correctThermo();
        correctTurbulence();
    }
    
    virtual tmp<volScalarField> rho() const {
        return tmp<volScalarField>(new volScalarField(rho_));
    }
};
```

**กรอบงานคณิตศาสตร์**: คุณสมบัติของระบบเป็น composites:
$$\rho_{\text{total}} = \sum_{i=1}^{N} \alpha_i \rho_i$$

$$\mathbf{U}_{\text{mixture}} = \frac{\sum_{i=1}^{N} \alpha_i \rho_i \mathbf{U}_i}{\sum_{i=1}^{N} \alpha_i \rho_i}$$

**การจับคู่โมเมนตัม**:
```cpp
class multiphaseEulerSystem : public phaseSystem {
public:
    // Solve momentum equations for all phases
    void solveMomentum() {
        forAll(phases_, phasei) {
            // Individual phase momentum
            fvVectorMatrix UEqn = fvm::ddt(rho_*U_) + 
                                fvm::div(rho_*U_, U_) - 
                                fvm::laplacian(mu_, U_);
            
            // Add interphase momentum transfer
            forAll(phases_, otherj) {
                if (phasei != otherj) {
                    // Drag force coupling
                    UEqn += Kd_*phases_[otherj].U();
                }
            }
            
            UEqn.relax();
            UEqn.solve();
        }
    }
};
```

**การอนุรักษ์ phase fraction**:
```cpp
void phaseSystem::solvePhaseFractions() {
    // Solve continuity for each phase
    forAll(phases_, phasei) {
        fvScalarField alphaEqn = 
            fvm::ddt(alpha_) + 
            fvm::div(phases_[phasei].phi(), alpha_);
            
        alphaEqn.relax();
        alphaEqn.solve();
    }
    
    // Enforce phase fraction constraint
    normalizeAlphas();
}
```

**ประโยชน์หลัก**:
- **Uniform Treatment**: interface เดียวกันสำหรับ phases แบบแยกและ phase systems
- **Scalability**: เพิ่ม/ลบ phases ได้อย่างง่ายโดยไม่ต้องเปลี่ยนโครงสร้าง solver
- **Hierarchical Organization**: ระบบที่ซับซ้อนสร้างจากส่วนประกอบที่ง่าย
- **Recursive Operations**: การดำเนินงานเผยแพร่ตามธรรมชาติผ่านลำดับชั้น
