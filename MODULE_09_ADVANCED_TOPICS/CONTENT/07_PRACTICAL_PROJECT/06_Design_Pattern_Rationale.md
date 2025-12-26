# 06 เหตุผลเบื้องหลัง: การวิเคราะห์รูปแบบการออกแบบในโปรเจกต์

![[cfd_sandbox_plugins.png]]
`A clean scientific illustration of the "CFD Sandbox Architecture". Show a central, locked "OpenFOAM Core" box. Connected to it are various modular "User Plugin" boxes (representing custom models) that can be plugged in and unplugged. Highlight that the core box is never opened or modified. Use a minimalist palette, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

**ทำไมเราจึงต้องทำตามขั้นตอนที่ซับซ้อนเหล่านี้?** เพื่อให้โมเดลของเราไม่ได้เป็นแค่โค้ดที่รันได้ แต่เป็นส่วนหนึ่งของระบบนิเวศ OpenFOAM อย่างแท้จริง

---

## 🏭 **Factory Pattern: สนามทดลองการเขียนโค้ดของผู้ใช้เทียบกับเสถียรภาพของคลังหลัก**

Factory Pattern ใน OpenFOAM แสดงถึงวิธีแก้ปัญหาที่สวยงามสำหรับความท้าทายพื้นฐานของวิศวกรรมซอฟต์แวร์ในเฟรมเวิร์ก CFD: **การเปิดใช้งานความสามารถในการขยายตัวในขณะที่รักษาเสถียรภาพของคลังหลัก**

### **ปัญหาหลัก**

แอปพลิเคชันพลศาสตร์ของไหลเชิงคำนวณต้องการให้ผู้ใช้ implement แบบจำลองฟิสิกส์แบบกำหนดเอง (turbulence closures, thermophysical properties, reaction mechanisms, เป็นต้น) หากไม่มี architectural pattern ที่เหมาะสม สิ่งนี้จะต้องการ:

1. **การแก้ไขคลังหลักโดยตรง**: ผู้ใช้จำเป็นต้องแก้ไขไฟล์ซอร์ส OpenFOAM โดยตรง
2. **การคอมไพล์ใหม่ทั้งหมด**: การเพิ่มแบบจำลองแบบกำกำหนดเองหนึ่งรายการจำเป็นต้องสร้างคลัง OpenFOAM ทั้งหมดใหม่
3. **การทำลายความเข้ากันได้**: การเปลี่ยนแปลงอาจทำให้การจำลองหรือไฟล์ case ที่มีอยู่ใช้ไม่ได้
4. **ความสับสนของการควบคุมเวอร์ชัน**: การผสานการแก้ไขคลังหลักระหว่างการอัปเดต OpenFOAM จะกลายเป็นปัญหา

### **การแก้ปัญหาของ Factory: ตารางการเลือกขณะ Runtime**

ตารางการเลือกขณะ runtime สร้าง **sandbox architecture** ที่แยกความรับผิดชอบออกจากกันอย่างชัดเจน

#### ความรับผิดชอบของคลังหลัก

```cpp
// Abstract base class defines the interface contract
class turbulenceModel
{
public:
    // Factory method for runtime object creation
    // Uses dictionary lookup to instantiate appropriate model
    static autoPtr<turbulenceModel> New
    (
        const volVectorField& U,      // Velocity field
        const surfaceScalarField& phi, // Flux field
        const word& modelType          // Model name from dictionary
    );

    // Pure virtual interface - must be implemented by derived classes
    virtual tmp<volSymmTensorField> devReff() const = 0;
    virtual void correct() = 0;
};
```

**📂 Source:** `$FOAM_SRC/TurbulenceModels/turbulenceModels/turbulenceModel.H`

---

**คำอธิบายเพิ่มเติม:**

**แหล่งที่มา (Source):**  
ไฟล์นี้อยู่ในไดเรกทอรีหลักของ OpenFOAM (`$FOAM_SRC/TurbulenceModels/`) ซึ่งเป็นส่วนที่ถูกคอมไพล์เป็นคลังหลัก (core library) ของ OpenFOAM นี่คือตำแหน่งที่ abstract base class ถูกกำหนดขึ้นเพื่อเป็นสัญญา (contract) ระหว่าง core framework กับ user-defined models

**คำอธิบาย (Explanation):**  
โค้ดนี้แสดงให้เห็นถึงหัวใจของ Factory Pattern ใน OpenFOAM โดยมีสองส่วนสำคัญ:
1. **Factory Method (`New`)**: เป็น static method ที่ทำหน้าที่สร้างออบเจกต์ของ turbulence model ที่เหมาะสมตามชื่อที่ระบุใน dictionary โดยใช้กลไกของ runtime selection table
2. **Pure Virtual Interface**: กำหนดว่า turbulence model ใดๆ จำเป็นต้อง implement ฟังก์ชัน `devReff()` (คำนวณ effective deviatoric stress) และ `correct()` (แก้สมการความปั่นป่วน) ทำให้เกิด polymorphism ที่ solver สามารถเรียกใช้โมเดลใดๆ ได้โดยไม่ต้องรู้ว่าเป็นโมเดลชนิดใด

**แนวคิดสำคัญ (Key Concepts):**
- **Abstract Base Class**: คลาสที่มี pure virtual functions ซึ่งทำหน้าที่เป็น "interface" หรือ "contract" ที่กำหนดว่า derived classes ต้องทำอะไรบ้าง
- **Factory Method**: Pattern ที่แยกการสร้างออบเจกต์ออกจากการใช้งาน ทำให้สามารถเลือกประเภทของออบเจกต์ได้ขณะ runtime
- **autoPtr<T>**: Smart pointer ของ OpenFOAM ที่จัดการความเป็นเจ้าของและการทำลายออบเจกต์อัตโนมัติ
- **tmp<T>**: Smart pointer สำหรับ objects ชั่วคราวที่อาจใช้ร่วมกันหลายจุดในโค้ด

---

#### การ Implement โค้ดของผู้ใช้

```cpp
// User implements specific physics
class myCustomTurbulenceModel : public turbulenceModel
{
public:
    // Runtime type information - enables dictionary lookup
    TypeName("myCustomTurbulence");

    // Constructor with phase fields
    myCustomTurbulenceModel
    (
        const volVectorField& U,
        const surfaceScalarField& phi
    );

    // Implementation of virtual interface
    virtual tmp<volSymmTensorField> devReff() const override;
    virtual void correct() override;
};

// Registration macro links the name to the constructor
addToRunTimeSelectionTable
(
    turbulenceModel,
    myCustomTurbulenceModel,
    dictionary
);
```

**📂 Source:** ไฟล์ `.H` และ `.C` ของผู้ใช้ใน `$FOAM_RUN/` หรือ `$FOAM_USER_LIBBIN/`

---

**คำอธิบายเพิ่มเติม:**

**แหล่งที่มา (Source):**  
นี่คือไฟล์โค้ดที่ผู้ใช้เขียนขึ้นเองในไดเรกทอรีของผู้ใช้ (user space) ซึ่งอาจอยู่ใน `$FOAM_RUN/` (สำหรับ development) หรือจะถูกคอมไพล์เป็น shared library ใน `$FOAM_USER_LIBBIN/` โค้ดนี้ไม่ได้อยู่ในคลังหลักของ OpenFOAM แต่สามารถถูกโหลดและใช้งานได้ผ่านกลไก plugin architecture

**คำอธิบาย (Explanation):**  
การ implement แบบจำลองกำหนดเองประกอบด้วยสามส่วนหลัก:
1. **Class Inheritance**: สืบทอดจาก `turbulenceModel` เพื่อรับส่วน interface และ contract ที่กำหนดไว้
2. **TypeName Macro**: ลงทะเบียนชื่อของคลาสนี้กับระบบ runtime type information (RTTI) ของ OpenFOAM ซึ่งช่วยให้ factory สามารถค้นหาคลาสนี้จากชื่อใน dictionary ได้
3. **addToRunTimeSelectionTable Macro**: เชื่อมโยงชื่อ "myCustomTurbulence" กับ constructor ของคลานี้ใน runtime selection table ทำให้ `turbulenceModel::New()` สามารถสร้างอินสแตนซ์ของคลาสนี้ได้เมื่อพบชื่อใน dictionary

**แนวคิดสำคัญ (Key Concepts):**
- **Inheritance**: กลไกที่ทำให้ derived class ได้รับ interface และ behavior ของ base class
- **TypeName**: Macro ของ OpenFOAM สำหรับลงทะเบียนข้อมูลประเภทขณะ runtime ซึ่งแตกต่างจาก C++ standard RTTI
- **Runtime Selection Table**: โครงสร้างข้อมูลแบบ hash table ที่เก็บการแมประหว่างชื่อ (string) กับ constructor pointers
- **Dictionary-driven Configuration**: การกำหนดค่าโมเดลผ่านไฟล์ case แทนการ hard-code ใน source code
- **Plugin Architecture**: รูปแบบสถาปัตยกรรมที่อนุญาตให้เพิ่มฟีเจอร์ใหม่โดยไม่ต้องแก้ไข core system

---

### 📚 **การแยกความรับผิดชอบ**

สถาปัตยกรรมนี้สร้างสัญญาที่ชัดเจนระหว่างคอมโพเนนต์ต่างๆ:

| คอมโพเนนต์ | ความรับผิดชอบหลัก | ตำแหน่งทั่วไป | ประโยชน์หลัก |
|-----------|----------------------|------------------|--------------|
| **Base Class** | กำหนด abstract interface, ลายเซ็น factory method, โครงสร้างข้อมูลทั่วไป | คลังหลัก OpenFOAM (`$FOAM_SRC/`) | รับประกัน API ที่สอดคล้องกัน, ทำให้ polymorphism เป็นไปได้, จัดเตรียมโครงสร้างพื้นฐาน factory |
| **Concrete Class** | Implement ฟิสิกส์/คณิตศาสตร์เฉพาะ, การลงทะเบียนด้วยตนเอง, การแยกวิเคราะห์พารามิเตอร์ | คลังผู้ใช้ (`$FOAM_USER_APPBIN/`) | ห่อหุ้มรายละเอียดฟิสิกส์, คอมไพล์ใหม่ได้โดยอิสระ, ควบคุมเวอร์ชันได้ |
| **Factory System** | การค้นหาประเภทขณะ runtime, การแมป constructor, การจัดการวงจรชีวิตของออบเจกต์ | ระบบรีจิสทรี OpenFOAM (`src/OpenFOAM/db/runTimeSelection/`) | แยกการเลือกจากการ implement, จัดการการจัดการหน่วยความจำ, เปิดใช้งานการโหลดแบบไดนามิก |
| **Dictionary Files** | การเลือกแบบจำลอง, การกำหนดค่าพารามิเตอร์, การตั้งค่าเฉพาะ case | ไฟล์ case (`system/`, `constant/`) | อนุญาตการกำหนดค่าขณะ runtime, ช่วยในการศึกษาพารามิเตอร์, แยกฟิสิกส์จากการตั้งค่า case |

---

## 🔄 **สถาปัตยกรรมปลั๊กอินของ OpenFOAM**

```mermaid
graph TD
    classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    Step1[Step 1: Separate Compilation<br/>wmake libso]:::explicit
    Step2[Step 2: Dynamic Loading<br/>controlDict libs]:::implicit
    Step3[Step 3: Dictionary Selection<br/>RASModel myCustomModel]:::implicit
    Step4[Step 4: Factory Dispatch<br/>turbulenceModel::New]:::implicit
    Step5[Step 5: Execution<br/>turbulence->correct()]:::success
    
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
```

> **Figure 1:** แผนผังลำดับขั้นตอนการทำงานของสถาปัตยกรรมปลั๊กอิน (Plugin Architecture) ใน OpenFOAM ซึ่งช่วยให้โมเดลที่ถูกคอมไพล์แยกออกมาสามารถถูกโหลดและใช้งานได้ทันทีผ่านการตั้งค่าในไฟล์กรณีจำลอง โดยไม่จำเป็นต้องแก้ไขและคอมไพล์ซอร์สโค้ดหลักใหม่

การ implement Factory Pattern นี้เปิดใช้งาน **plugin-like extensibility** ของ OpenFOAM ผ่านกลไกการเลือกขณะ runtime ที่ซับซ้อน:

### ขั้นที่ 1: การคอมไพล์แยกกัน

แบบจำลองแบบกำหนดเองถูกคอมไพล์เป็นคลังอิสระ:

```bash
# User compiles custom model separately as a shared library
wmake libso
```

**📂 Source:** Make/files และ Make/options ในไดเรกทอรีโปรเจกต์ผู้ใช้

---

**คำอธิบายเพิ่มเติม:**

**แหล่งที่มา (Source):**  
การคอมไพล์นี้เกิดขึ้นในไดเรกทอรีโปรเจกต์ของผู้ใช้ ซึ่งมักจะมีไฟล์ `Make/files` และ `Make/options` ที่ระบุ source files และ library dependencies ผลลัพธ์จะเป็นไฟล์ `.so` (shared library) ที่สามารถโหลดแบบไดนามิกได้

**คำอธิบาย (Explanation):**  
คำสั่ง `wmake libso` เป็น build system ของ OpenFOAM ที่:
1. คอมไพล์ source files (.C, .H) เป็น object files
2. เชื่อมโยง object files เป็น shared library (.so)
3. วาง library ไว้ใน `$FOAM_USER_LIBBIN/` หรือตำแหน่งที่ระบุ
4. สร้าง symbolic links สำหรับ dependencies ต่างๆ

**แนวคิดสำคัญ (Key Concepts):**
- **Shared Library (.so)**: ไฟล์โค้ดที่คอมไพล์แล้วซึ่งสามารถโหลดแบบไดนามิกขณะ runtime
- **Separate Compilation**: การคอมไพล์โค้ดแยกจาก core library ทำให้ไม่ต้องคอมไพล์ OpenFOAM ทั้งหมดใหม่
- **wmake Build System**: ระบบ build ของ OpenFOAM ที่จัดการ dependencies และ compilation flags อัตโนมัติ
- **Plugin Development Cycle**: วงจรการพัฒนาที่รวดเร็ว - แก้โค้ด → คอมไพล์ → ทดสอบ โดยไม่กระทบ core system

---

### ขั้นที่ 2: การโหลดขณะ Runtime

คลังถูกโหลดแบบไดนามิกเมื่อจำเป็น:

```cpp
// In controlDict: specify libraries to load dynamically
libs
(
    "libmyCustomModels.so"
);
```

**📂 Source:** `system/controlDict` ในไฟล์ case ของผู้ใช้

---

**คำอธิบายเพิ่มเติม:**

**แหล่งที่มา (Source):**  
ไฟล์ `system/controlDict` อยู่ในไดเรกทอรี case ของผู้ใช้ ซึ่งเป็นไฟล์ configuration ที่ควบคุมการทำงานของ solver และ runtime settings ต่างๆ

**คำอธิบาย (Explanation):**  
เมื่อ solver เริ่มทำงาน OpenFOAM จะ:
1. อ่าน `controlDict` เพื่อหา `libs` entry
2. ใช้ `dlopen()` (หรือ function ที่เทียบเท่า) เพื่อโหลด shared libraries ที่ระบุ
3. ทำให้ symbols และ classes ใน library พร้อมใช้งานใน runtime
4. Runtime selection tables ของ classes เหล่านั้นจะถูกลงทะเบียนโดยอัตโนมัติ

**แนวคิดสำคัญ (Key Concepts):**
- **Dynamic Loading**: การโหลดโค้ดขณะ runtime โดยไม่ต้อง link ตอน compile time
- **dlopen()**: System call บน Unix/Linux สำหรับโหลด shared libraries
- **Symbol Resolution**: กระบวนการทำให้ functions และ classes ใน library พร้อมใช้งาน
- **Constructor Registration**: เมื่อ library ถูกโหลด static constructors จะรันและลงทะเบียน classes กับ runtime selection tables

---

### ขั้นที่ 3: การเลือก Dictionary

แบบจำลองถูกเลือกผ่านการกำหนดค่า case:

```cpp
// In case file: constant/turbulenceProperties or similar
simulationType  RAS;
RAS
{
    RASModel        myCustomTurbulence;
    turbulence      on;
    
    // Standard model parameters
    Cmu             0.09;
    kappa           0.41;
    
    // Additional custom parameters
    customParameter 1.23;
}
```

**📂 Source:** `constant/turbulenceProperties` ในไดเรกทอรี case

---

**คำอธิบายเพิ่มเติม:**

**แหล่งที่มา (Source):**  
ไฟล์นี้อยู่ในไดเรกทอรี `constant/` ของ case ซึ่งเป็นไฟล์ configuration สำหรับระบุ turbulence model และพารามิเตอร์ที่เกี่ยวข้อง ชื่อไฟล์อาจแตกต่างกันไปตามประเภทของ solver (เช่น `constant/thermophysicalProperties` สำหรับ compressible solvers)

**คำอธิบาย (Explanation):**  
เมื่อ solver อ่านไฟล์นี้:
1. `simulationType` ระบุว่าจะใช้ RAS, LES, หรือ laminar
2. `RASModel` ระบุชื่อของ model ที่ต้องการใช้ ("myCustomTurbulence")
3. พารามิเตอร์อื่นๆ จะถูกส่งไปยัง constructor ผ่าน `dictionary` object
4. Factory จะใช้ชื่อนี้ในการค้นหาและสร้างอินสแตนซ์ของคลาสที่เหมาะสม

**แนวคิดสำคัญ (Key Concepts):**
- **Dictionary-driven Configuration**: การกำหนดค่าผ่านไฟล์ case แทน hard-coding
- **Parameter Injection**: การส่งค่าพารามิเตอร์จาก dictionary ไปยัง constructor
- **Model Selection**: การเลือก model ผ่านชื่อ string ที่ mapping กับ runtime selection table
- **Case-specific Settings**: แต่ละ case สามารถมีการตั้งค่า model ที่แตกต่างกันได้

---

### ขั้นที่ 4: การสร้างอินสแตนซ์และการดำเนินการ

ระบบ factory จัดการการสร้างออบเจกต์:

```cpp
// Runtime creation based on dictionary entry
autoPtr<turbulenceModel> turbulence
(
    turbulenceModel::New
    (
        U,
        phi,
        laminarTransport
    )
);

// Polymorphic usage - works with any turbulence model
turbulence->correct();
Reff = turbulence->devReff();
```

**📂 Source:** ไฟล์ solver (เช่น `simpleFoam.C`, `pimpleFoam.C`) ใน `$FOAM_APPBIN/solvers/`

---

**คำอธิบายเพิ่มเติม:**

**แหล่งที่มา (Source):**  
โค้ดนี้อยู่ในไฟล์ solver ของ OpenFOAM (เช่น `applications/solvers/incompressible/simpleFoam/simpleFoam.C`) ซึ่งเป็นส่วนหนึ่งของคลังหลัก OpenFOAM

**คำอธิบาย (Explanation):**  
ขั้นตอนการทำงานมีดังนี้:

1. **Factory Invocation**: `turbulenceModel::New()` ถูกเรียกพร้อมกับ arguments ที่จำเป็น
2. **Dictionary Lookup**: Factory อ่าน dictionary เพื่อหาชื่อ model ("myCustomTurbulence")
3. **Constructor Dispatch**: Factory ค้นหา runtime selection table และเรียก constructor ที่เหมาะสม
4. **Object Creation**: Constructor สร้างอินสแตนซ์ของ `myCustomTurbulenceModel`
5. **Polymorphic Access**: ผ่าน pointer ของ base class (`turbulenceModel`) solver สามารถเรียก virtual functions ได้โดยไม่ต้องรู้ว่าเป็น derived class ใด

**แนวคิดสำคัญ (Key Concepts):**
- **Runtime Polymorphism**: ความสามารถในการเรียกใช้ methods ของ derived class ผ่าน base class pointer
- **Virtual Function Table (vtable)**: กลไกของ C++ ที่ทำให้ polymorphism ทำงานได้
- **Late Binding**: การ resolve function call ขณะ runtime แทน compile time
- **Interface Segregation**: Solver ไม่ต้องรู้รายละเอียดของแต่ละ model เพียงแค่รู้ interface

---

## 🎯 **ประโยชน์ของสถาปัตยกรรม**

รูปแบบการออกแบบนี้ให้ประโยชน์ที่สำคัญหลายประการ:

### **ความยืดหยุ่นในการพัฒนา**
- **ไม่มีการแก้ไขคลังหลัก**: ผู้ใช้ไม่ต้องยุ่งกับซอร์สโค้ด OpenFOAM
- **การทดสอบแยกกัน**: แบบจำลองแบบกำหนดเองสามารถพัฒนาและทดสอบแยกจากกันได้
- **การพัฒนาแบบเพิ่มหน่วย**: แบบจำลองใหม่สามารถเพิ่มโดยไม่กระทบฟังก์ชันการทำงานที่มีอยู่

### **ประสิทธิภาพการดำเนินงาน**
- **การคอมไพล์แบบเลือก**: เฉพาะคอมโพเนนต์ที่เปลี่ยนแปลงเท่านั้นที่ต้องคอมไพล์ใหม่
- **ประสิทธิภาพหน่วยความจำ**: แบบจำลองถูกโหลดเฉพาะเมื่อจำเป็น
- **ประสิทธิภาพ**: ค่าใช้จ่ายของ polymorphism ขณะ runtime เล็กน้อยเมื่อเทียบกับความยืดหยุ่นในการพัฒนา

### **การบำรุงรักษา**
- **ความเข้ากันได้ของเวอร์ชัน**: แบบจำลองแบบกำหนดเองอยู่รอดการอัปเดต OpenFOAM
- **Interfaces ที่ชัดเจน**: สัญญาที่กำหนดไว้ดีระหว่างคอมโพเนนต์
- **สถาปัตยกรรมแบบโมดูล**: แต่ละคอมโพเนนต์มีความรับผิดชอบเดียว

### **ความสามารถในการขยายตัว**
- **แบบจำลองแบบลำดับชั้น**: แบบจำลองใหม่สามารถสืบทอดจากแบบจำลองที่มีอยู่ได้
- **การผสานระหว่างโดเมน**: รูปแบบเดียวกันทำงานสำหรับฟิสิกส์, ตัวเลข, meshing, utilities
- **การผสานรวมของบุคคลที่สาม**: ผู้ขายเชิงพาณิชย์สามารถจัดจำหน่ายแบบจำลองกรรมสิทธิ์เป็นปลั๊กอิน

---

## 💎 **สรุปแนวคิดหลัก**

สถาปัตยกรรมที่ใช้ factory เป็นพื้นฐานของความสำเร็จของ OpenFOAM ทั้งในฐานะแพลตฟอร์มการวิจัยและเครื่องมือ CFD สำหรับการผลิต ทำให้สามารถพัฒนาได้ในขณะที่รักษาความเข้ากันได้แบบย้อนหลังและความสามารถในการขยายตัว

### **หลักการออกแบบที่สำคัญ**

1. **การแยกส่วนที่ชัดเจน (Separation of Concerns)**
   - คลังหลักกำหนด interface
   - ผู้ใช้ implement ฟิสิกส์
   - ระบบ factory จัดการการเชื่อมต่อ

2. **การเปิดกว้างแต่ปิดกับการแก้ไข (Open-Closed Principle)**
   - เปิดสำหรับการขยาย (กำหนดโมเดลใหม่)
   - ปิดสำหรับการแก้ไข (ไม่ต้องแก้คลังหลัก)

3. **การพึ่งพาผ่าน interface (Dependency Inversion)**
   - Solvers พึ่งพา abstract base classes
   - ไม่พึ่งพา concrete implementations

4. **การสร้างแบบไดนามิก (Dynamic Instantiation)**
   - Dictionary-driven object creation
   - Runtime type resolution
   - Plugin-like modularity

สถาปัตยกรรมนี้เป็นตัวอย่างที่ยอดเยี่ยมของการออกแบบซอฟต์แวร์เชิงวัตถุที่เหมาะสมกับแอปพลิเคชันทางวิทยาศาสตร์ ซึ่งต้องการทั้งความยืดหยุ่นในการวิจัยและเสถียรภาพในการใช้งานเชิงการผลิต