## 🛠️ คู่มือการใช้งาน: การนำโปรแกรม Custom Patterns ไปใช้

### ขั้นตอน: โมเดลทางกายภาพใหม่

#### ขั้นที่ 1: การวิเคราะห์ทางกายภาพ

การนำโมเดลทางกายภาพแบบกำหนดเองไปใช้ใน OpenFOAM เริ่มต้นจากการวิเคราะห์ทางคณิตศาสตร์อย่างเข้มงวด สำหรับตัวอย่างสหสัมพันธ์การถ่ายเทความร้อนของเรา เราจำเป็นต้องสร้างความสัมพันธ์มิติขั้นพื้นฐานที่ควบคุมปรากฏการณ์ทางกายภาพ

สหสัมพันธ์จำนวน Nusselt $Nu = a \cdot Re^b \cdot Pr^c$ แทนสัมประสิทธิ์การถ่ายเทความร้อนไร้มิติ โดยที่:

- **จำนวน Nusselt ($Nu$)**: $\frac{hL}{k}$ - อัตราส่วนของการถ่ายเทความร้อนแบบ convection เทียบกับ conduction
- **จำนวน Reynolds ($Re$)**: $\frac{\rho u L}{\mu} = \frac{uL}{\nu}$ - อัตราส่วนของแรนเฉื่อยยเทียบกับแรนหนืด
- **จำนวน Prandtl ($Pr$)**: $\frac{c_p \mu}{k}$ - อัตราส่วนของ diffusion โมเมนตัมเทียบกับ diffusion ความร้อน

การวิเคราะห์มิติช่วยให้แน่ใจว่าการนำไปใช้งานสุดท้ายของเรายังคงความสม่ำเสมอทางกายภาพ เนื่องจากกลุ่มไร้มิติทั้งสามมีการ normalise อย่างเหมาะสม สหสัมพันธ์จะผลิตผลลัพธ์ไร้มิติที่สามารถปรับขนาดเพื่อรับสัมประสิทธิ์การถ่ายเทความร้อนจริง $h$:

$$h = \frac{Nu \cdot k}{L} = \frac{a \cdot Re^b \cdot Pr^c \cdot k}{L}$$

พื้นฐานทางคณิตศาสตร์นี้ให้กรอบการทำงานสำหรับการนำไปใช้งานในเชิงคำนวณใน OpenFOAM

#### ขั้นที่ 2: การออกแบบ Interface (Strategy)

การนำรูปแบบ Strategy ไปใช้งานต้องการการออกแบบคลาสฐานนามธรรมอย่างระมัดระวังที่กำหนด interface สำหรับโมเดลการถ่ายเทความร้อนทั้งหมด ลำดับชั้นการสืบทอดช่วยให้เกิดพหุภาคีขณะทำงาน (runtime polymorphism) ในขณะที่ยังคงความปลอดภัยของประเภทขณะคอมไพล์ (compile-time type safety)

```cpp
class heatTransferModel
{
public:
    // Runtime type information for factory selection
    TypeName("heatTransferModel");

    // Virtual destructor for proper cleanup
    virtual ~heatTransferModel() {}

    // Pure virtual strategy method - must be implemented by derived classes
    virtual tmp<volScalarField> h
    (
        const phaseModel& phase1,
        const phaseModel& phase2
    ) const = 0;

    // Factory method for creating models from dictionary specifications
    static autoPtr<heatTransferModel> New
    (
        const dictionary& dict,
        const phaseModel& phase1, 
        const phaseModel& phase2
    );

protected:
    // Protected constructor for base class initialization
    heatTransferModel
    (
        const dictionary& dict,
        const phaseModel& phase1,
        const phaseModel& phase2
    )
    :
        dict_(dict),
        phase1_(phase1),
        phase2_(phase2)
    {}

private:
    // Dictionary reference for parameter access
    const dictionary& dict_;
    
    // Reference to interacting phases
    const phaseModel& phase1_;
    const phaseModel& phase2_;
};
```

การออกแบบ interface นี้ให้ประโยชน์หลายประการ:

1. **พฤติกรรมพหุภาคี**: โมเดลการถ่ายเทความร้อนต่างๆ สามารถเลือกได้ขณะทำงานผ่านกลไก factory
2. **Interface ที่สม่ำเสมอ**: การนำไปใช้งานทั้งหมดให้ signature ของเมธอด `h()` เหมือนกัน
3. **ความสามารถในการขยาย**: สามารถเพิ่มโมเดลใหม่ได้โดยไม่ต้องแก้ไขโค้ดที่มีอยู่
4. **การจัดการทรัพยากร**: คลาส `tmp` และ `autoPtr` ของ OpenFOAM จัดการหน่วยความจำอย่างมีประสิทธิภาพ

#### ขั้นที่ 3: การนำ Concrete Strategy ไปใช้งาน

การนำ concrete strategy ไปใช้งานแปลงสหสัมพันธ์ทางคณิตศาสตร์ของเราเป็นโค้ด C++ ที่มีประสิทธิภาพทางคำนวณ ในขณะที่ยังคงความสม่ำเสมอทางมิติและเสถียรภาพทางตัวเลข

```cpp
class MyHeatTransfer : public heatTransferModel
{
    // Model coefficients from dictionary specification
    dimensionedScalar a_, b_, c_;

public:
    TypeName("myHeatTransfer");

    MyHeatTransfer
    (
        const dictionary& dict,
        const phaseModel& phase1, 
        const phaseModel& phase2
    )
    :
        heatTransferModel(dict, phase1, phase2),
        a_(dict.lookup<dimensionedScalar>("a")),
        b_(dict.lookup<dimensionedScalar>("b")), 
        c_(dict.lookup<dimensionedScalar>("c"))
    {
        // Validate parameter ranges for numerical stability
        if (b_.value() < 0 || b_.value() > 2)
        {
            WarningIn("MyHeatTransfer::MyHeatTransfer")
                << "Unusual Reynolds exponent: " << b_ << endl;
        }
        
        if (c_.value() < 0 || c_.value() > 1.5)
        {
            WarningIn("MyHeatTransfer::MyHeatTransfer") 
                << "Unusual Prandtl exponent: " << c_ << endl;
        }
    }

    virtual tmp<volScalarField> h
    (
        const phaseModel& phase1,
        const phaseModel& phase2  
    ) const override
    {
        // Calculate dimensionless groups with numerical safeguards
        const volScalarField U_rel = mag(phase1.U() - phase2.U());
        
        // Reynolds number: Re = ρ*u*D/μ = u*D/ν
        // Use maximum to avoid division by zero in stagnant regions
        const volScalarField Re = max
        (
            U_rel * phase1.d() / max(phase2.nu(), dimensionedScalar("smallNu", dimensionSet(0,2,-1,0,0), 1e-12)),
            dimensionedScalar("smallRe", dimensionSet(0,0,0,0,0), 1e-6)
        );
        
        // Prandtl number: Pr = Cp*μ/k
        const volScalarField Pr = max
        (
            phase2.Cp() * phase2.mu() / max(phase2.kappa(), dimensionedScalar("smallK", dimensionSet(1,1,-3,-1,0), 1e-12)),
            dimensionedScalar("smallPr", dimensionSet(0,0,0,0,0), 1e-6)
        );
        
        // Nusselt correlation: Nu = a*Re^b*Pr^c
        const volScalarField Nu = a_ * pow(Re, b_) * pow(Pr, c_);
        
        // Convert to heat transfer coefficient: h = Nu*k/D
        return Nu * phase2.kappa() / phase1.d();
    }
};
```

รายละเอียดการนำไปใช้งานที่สำคัญ ได้แก่:

1. **เสถียรภาพทางตัวเลข**: ค่าต่ำสุดป้องกันการหารด้วยศูนย์และรับประกันการยกกำลังที่มีขอบเขต
2. **ความสม่ำเสมอทางมิติ**: การคำนวณระดับกลางทั้งหมดรักษามิติที่เหมาะสม
3. **การดำเนินการ field ที่มีประสิทธิภาพ**: ใช้ expression templates ของ OpenFOAM เพื่อประสิทธิภาพสูงสุด
4. **การตรวจสอบพารามิเตอร์**: Constructor ตรวจสอบช่วงค่าสัมประสิทธิ์ที่เหมาะสมทางกายภาพ

#### ขั้นที่ 4: การลงทะเบียนกับระบบ Factory

กลไกการลงทะเบียน factory ช่วยให้สามารถเลือกโมเดลแบบกำหนดเองของเราได้ขณะทำงานผ่านระบบการกำหนดค่าตามพจนานุกรมของ OpenFOAM

```cpp
// In MyHeatTransfer.C - essential for factory pattern to work
addToRunTimeSelectionTable
(
    heatTransferModel,
    MyHeatTransfer,
    dictionary
);
```

มาโครนี้ขยายไปสู่โค้ดที่:
- ลงทะเบียนคลาสของเรากับ `heatTransferModel` factory
- เชื่อมโยงคลาสกับชื่อประเภท `"myHeatTransfer"`
- เปิดใช้งานการสร้างตามพจนานุกรมผ่าน `heatTransferModel::New()`

การลงทะเบียนต้องปรากฏในไฟล์ .C (ไม่ใช่ header) เพื่อให้แน่ใจว่าโค้ดการลงทะเบียนถูกสร้างและเชื่อมโยงเข้ากับไลบรารีสุดท้าย

#### ขั้นที่ 5: การสร้างการกำหนดค่าระบบ Build

ระบบ build `wmake` ของ OpenFOAM ต้องการการกำหนดค่าที่เหมาะสมสำหรับการคอมไพล์, เชื่อมโยง, และการจัดการ dependency

**Make/files**:
```makefile
# Source files to compile
MyHeatTransfer.C

# Target library location and name
# $(FOAM_USER_LIBBIN) expands to user's library directory
LIB = $(FOAM_USER_LIBBIN)/libMyHeatTransfer
```

**Make/options**:
```makefile
# Include paths for header files
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \      # Finite volume method
    -I$(LIB_SRC)/thermophysicalModels/lnInclude \ # Thermophysical properties
    -I$(LIB_SRC)/transportModels \             # Transport models
    -I$(LIB_SRC)/meshTools/lnInclude           # Mesh utilities

# Libraries to link against
EXE_LIBS = \
    -lfiniteVolume \                           # Finite volume functionality
    -lthermophysicalModels \                  # Thermophysical models
    -ltransportModels \                       # Transport model classes
    -lmeshTools                               # Mesh manipulation tools
```

การกำหนดค่า build ช่วยให้แน่ใจว่า:
- การค้นพบไฟล์ header อย่างเหมาะสมระหว่างการคอมไพล์
- การเชื่อมโยงกับไลบรารี OpenFOAM ที่จำเป็น
    - ค่าธงการคอมไพล์ที่สม่ำเสมอข้ามแพลตฟอร์ม
    - การติดตาม dependency สำหรับ builds เพิ่มเติม

#### ขั้นที่ 6: การ Build และทดสอบ

การคอมไพล์และการทดสอบตามขั้นตอนการพัฒนามาตรฐานของ OpenFOAM:

```bash
# Source OpenFOAM environment (if not already done)
source $WM_PROJECT_DIR/etc/bashrc

# Compile the library
wmake

# Verify library creation
ls -la $FOAM_USER_LIBBIN/libMyHeatTransfer*

# Check for compilation warnings
wmake libso 2>&1 | grep -i warning
```

หลังจากคอมไพล์สำเร็จ ให้ทดสอบการนำไปใช้งาน:

1. **การทดสอบยูนิต**: สร้างกรณีทดสอบขั้นต่ำเพื่อตรวจสอบความถูกต้องทางคณิตศาสตร์
2. **การทดสอบการผสมผสาน**: ใช้ในกรณีจำลองแบบหลายเฟสมาตรฐาน
3. **การทดสอบประสิทธิภาพ**: เปรียบเทียบประสิทธิภาพกับโมเดลการถ่ายเทความร้อนที่มีอยู่
4. **การทดสอบการถอยหลัง**: ตรวจสอบพฤติกรรมที่สม่ำเสมอข้าม OpenFOAM เวอร์ชันต่างๆ

#### ขั้นที่ 7: การใช้ในกรณีจำลอง

โมเดลการถ่ายเทความร้อนแบบกำหนดเองถูกเปิดใช้งานผ่านการกำหนดค่าพจนานุกรมในกรณีจำลอง:

```cpp
// In constant/phaseProperties or appropriate model dictionary
heatTransferModel
{
    // Must match the TypeName exactly (case-sensitive)
    type    myHeatTransfer;
    
    // Model coefficients - dimensional analysis ensures consistency
    a       0.023;  // Dimensionless correlation coefficient
    b       0.8;    // Reynolds number exponent
    c       0.4;    // Prandtl number exponent
    
    // Optional additional parameters
    debug   false;  // Enable/disable debugging output
}
```

ระบบ factory จะ:
- อ่านฟิลด์ `type` เพื่อเลือก `MyHeatTransfer`
- ส่งค่าสัมประสิทธิ์ไปยัง constructor
- ให้โมเดลที่กำหนดค่าไว้แก่ solver
- จัดการการตรวจสอบพารามิเตอร์และการรายงานข้อผิดพลาด

### รายการตรวจสอบการ Debugging

#### ปัญหาการลงทะเบียน Factory

ปัญหาการลงทะเบียน factory ปรากฏเป็นข้อผิดพลาดขณะทำงานเมื่อ solver พยายามสร้างโมเดลแบบกำหนดเองของคุณ การ debugging เชิงระบบ:

**การไม่ตรงกันของชื่อประเภท**:
```cpp
// Verify exact match between TypeName() and dictionary entry
TypeName("myHeatTransfer");  // Must match "type    myHeatTransfer;"
```

**ตำแหน่งการลงทะเบียน**:
```cpp
// Must be in .C file, not .H
addToRunTimeSelectionTable(heatTransferModel, MyHeatTransfer, dictionary);
```

**ลายเซ็น Constructor**:
```cpp
// Factory expects this exact signature
MyHeatTransfer
(
    const dictionary& dict,
    const phaseModel& phase1,
    const phaseModel& phase2
);
```

**การตรวจสอบเส้นทางไลบรารี**:
```bash
# Check library is discoverable
echo $LD_LIBRARY_PATH | grep $FOAM_USER_LIBBIN
ldd $FOAM_APPBIN/multiphaseEulerFoam | grep MyHeatTransfer
```

#### ปัญหาการนำ Strategy ไปใช้งาน

ปัญหาการนำฟังก์ชันเสมือนไปใช้งานทำให้เกิดความล้มเหลวในการคอมไพล์หรือพฤติกรรมที่ไม่กำหนด:

**การปฏิบัติตาม Interface**:
```cpp
// All pure virtual functions must be implemented
virtual tmp<volScalarField> h(const phaseModel&, const phaseModel&) const override = 0;
//                                                             ^^^^^^^^^ required
```

**การตรวจสอบการแทนที่**:
```cpp
// Use override keyword for compile-time checking
virtual tmp<volScalarField> h(...) const override { ... }
//                                         ^^^^^^^^ catches signature mismatches
```

**ความสม่ำเสมอทางมิติ**:
```cpp
// Verify return type matches interface
tmp<volScalarField> result = ...;  // Correct
// tmp<volVectorField> result = ...;  // Wrong dimensionality
```

**การจัดการเงื่อนไขขอบเขต**:
```cpp
// Ensure proper handling of patch boundaries
result.boundaryFieldRef() = ...;  // Set boundary values
result.correctBoundaryConditions(); // Update BCs
```

#### การปรับเพิ่มประสิทธิภาพ

ประสิทธิภาพทางคำนวณเป็นสิ่งสำคัญสำหรับการจำลองแบบที่ใช้งานจริง:

**ค่าใช้จ่ายของฟังก์ชันเสมือน**:
```bash
# Profile to measure impact
wmake libso profile
./application -case tutorial 2>&1 | grep "virtual function overhead"
```

**การเพิ่มประสิทธิภาพการดำเนินการ Field**:
```cpp
// Good: Uses expression templates
tmp<volScalarField> result = a_ * pow(Re, b_) * pow(Pr, c_);

// Bad: Creates temporary fields
volScalarField temp1 = a_ * pow(Re, b_);
volScalarField temp2 = temp1 * pow(Pr, c_);  // Unnecessary copy
```

**การจัดการหน่วยความจำ**:
```cpp
// Efficient: Reuse allocated memory
tmp<volScalarField> hCalc = tmp<volScalarField>
(
    new volScalarField(IOobject("h", mesh, IOobject::NO_READ, IOobject::NO_WRITE), mesh)
);

// Avoid: Repeated allocations
for (int i=0; i<maxIter; i++)
{
    volScalarField temp = ...;  // Expensive allocation each iteration
}
```

**การวิเคราะห์ประสิทธิภาพและการวัดประสิทธิภาพ**:
```bash
# Compare performance against baseline models
time multiphaseEulerFoam -case baselineCase
time multiphaseEulerFoam -case customModelCase

# Analyze memory usage
valgrind --tool=massif multiphaseEulerFoam -case testCase
```
