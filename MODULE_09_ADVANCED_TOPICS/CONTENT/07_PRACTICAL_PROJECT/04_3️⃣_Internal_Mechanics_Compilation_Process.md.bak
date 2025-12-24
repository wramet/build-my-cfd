## 3️⃣ กลไกภายใน: กระบวนการคอมไพล์

### 🔨 **ระบบ Build ของ wmake**

ระบบ build แบบกำหนดเองของ OpenFOAM `wmake` เป็นเฟรมเวิร์กการคอมไพล์ที่ซับซ้อนซึ่งออกแบบมาโดยเฉพาะสำหรับการจัดการ dependencies ที่ซับซ้อนและโครงสร้างแบบโมดูลาร์ของไลบรารี CFD เมื่อคุณ build แบบจำลองการขนส่งแบบกำหนดเองโดยใช้ `wmake libso` ระบบจะประสานงานกระบวนการหลายขั้นตอนที่เกินกว่าการคอมไพล์แบบง่าย

ลำดับการคอมไพล์เริ่มต้นด้วย `wmake` ที่แยกวิเคราะห์ไดเรกทอรี `Make/files` เพื่อระบุไฟล์ต้นฉบับทั้งหมดที่ต้องการคอมไพล์ ไฟล์นี้โดยทั่วไปจะมีรายการเช่น:

```
customViscosityModel.C
EXE = $(FOAM_USER_LIBBIN)/libcustomViscosityModel
```

ในเวลาเดียวกัน `wmake` อ่านไฟล์ `Make/options` เพื่อดึงข้อมูล flags ของคอมไพเลอร์และข้อมูล dependencies:

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/transportModels/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/basic/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -ltransportModels \
    -lthermophysicalModels
```

กระบวนการคอมไพล์จริงทำตามขั้นตอนเหล่านี้:

1. **การประมวลผล Header**: `wmake` สร้างไดเรกทอรี symbolic link (`lnInclude`) ที่มีไฟล์ header ที่จำเป็นทั้งหมดก่อน ขั้นตอนนี้สำคัญมากสำหรับสถาปัตยกรรมที่ใช้ template หนักของ OpenFOAM เพราะมันช่วยให้มั่นใจว่า header dependencies ทั้งหมดสามารถเข้าถึงได้ระหว่างการคอมไพล์

2. **การคอมไพล์ซอร์ส**: แต่ละไฟล์ `.C` จะถูกคอมไพล์โดยใช้ compiler flags ที่ระบุ สำหรับแบบจำลองการขนส่ง โดยทั่วไปจะเกี่ยวข้องกับการคอมไพล์คลาสหลักและฟังก์ชันยูทิลิตี้ที่รองรับ

3. **การลิงก์ออบเจกต์**: ไฟล์ออบเจกต์ที่คอมไพล์แล้ว (`.o` files) จะถูกลิงก์เข้าด้วยกันเพื่อสร้างไลบรารีแชร์ (`.so` file) ไลบรารีแชร์นี้สามารถโหลดแบบไดนามิกโดย solvers ของ OpenFOAM ได้ขณะ runtime

4. **การติดตั้งไลบรารี**: ไลบรารีที่เสร็จสมบูรณ์จะถูกคัดลอกไปยัง `$FOAM_USER_LIBBIN` (โดยทั่วไปคือ `~/.OpenFOAM/$(WM_PROJECT_VERSION)/platforms/linux64GccDPInt32Opt/lib`) ทำให้พร้อมใช้งานสำหรับแอปพลิเคชัน OpenFOAM ทั้งหมด

พื้นฐานคณิตศาสตร์ของแบบจำลองการขนส่งของคุณจะถูกคอมไพล์เป็นโค้ดเครื่องที่มีประสิทธิภาพระหว่างกระบวนการนี้ ตัวอย่างเช่น หากแบบจำลองของคุณ implement สมการความหนืดกฎกำลัง:

$$\mu_{\text{eff}} = K \dot{\gamma}^{n-1}$$

ความสัมพันธ์นี้จะถูกแปลเป็นโค้ด C++ ที่ปรับให้เหมาะสมซึ่งคอมไพเลอร์ประมวลผลเป็นคำสั่งที่ทำงานได้ ระบบ `wmake` ช่วยให้มั่นใจว่าโครงสร้างพื้นฐาน OpenFOAM ทั้งหมดที่จำเป็นสำหรับการประเมินนิพจน์ดังกล่าวได้รับการลิงก์และพร้อมใช้งานอย่างถูกต้อง

### 🧩 **การแก้ไข Dependencies**

กลไกการแก้ไข dependencies ในระบบ build ของ OpenFOAM มีลำดับชั้นและช่วยให้มั่นใจว่าโมดูลที่จำเป็นทั้งหมดพร้อมใช้งานก่อนเริ่มการคอมไพล์ ตัวแปร `EXE_INC` (executable include paths) และ `EXE_LIBS` (executable libraries) ใน `Make/options` มีจุดประสงค์ที่แตกต่างกันแต่เสริมซึ่งกันและกัน:

**การแก้ไข Include Path (`EXE_INC`)**:
flags `-I` บอก C++ preprocessor ว่าจะค้นหาไฟล์ header จากที่ใด สำหรับแบบจำลองความหนืดแบบกำหนดเอง dependencies ทั่วไปประกอบด้วย:

- **finiteVolume**: จัดเตรียมเฟรมเวิร์กการ discretize แบบ finite volume รวมถึงคลาสเช่น `volScalarField`, `fvMesh` และตัวดำเนินการ finite volume (`fvm::div()`, `fvc::grad()`)
- **transportModels**: มีคลาสฐานเช่น `viscosityModel` ที่แบบจำลองแบบกำหนดเองของคุณจะสืบทอดมา
- **thermophysicalModels**: นำเสนอแบบจำลองคุณสมบัติทางอุณหพลศาสตร์ที่อาจจำเป็นสำหรับการคำนวณความหนืดที่ขึ้นกับอุณหภูมิ

**การลิงก์ไลบรารี (`EXE_LIBS`)**:
flags `-l` ระบุไลบรารีที่จะลิงก์กับไฟล์ออบเจกต์ที่คอมไพล์แล้ว นี่คือที่ที่การ implement จริงของคลาสที่อ้างอิงใน headers ของคุณจะเชื่อมต่อกับโค้ดของคุณ

กราฟ dependencies สำหรับแบบจำลองการขนส่งทั่วไปทำตามรูปแบบนี้:

```
customViscosityModel.so
    ↓ depends on
transportModels.so
    ↓ depends on  
finiteVolume.so
    ↓ depends on
OpenFOAM.so (core library)
```

**ความซับซ้อนของ Template Instantiation**:
OpenFOAM ใช้ C++ templates อย่างกว้างขวาง ซึ่งทำให้การแก้ไข dependencies ซับซ้อนขึ้น เมื่อคุณประกาศฟิลด์เช่น:

```cpp
volScalarField muEff(
    IOobject(
        "muEff",
        mesh.time().timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);
```

นี่จะกระตุ้น template instantiation ที่ต้องการไฟล์ header จำนวนมากจากไลบรารี finiteVolume และ OpenFOAM core ระบบ `wmake` จัดการความซับซ้อนนี้โดย:

1. สร้างไดเรกทอรี `lnInclude` ที่ครอบคลุมด้วย headers ที่จำเป็นทั้งหมด
2. ใช้การติดตาม dependencies เพื่อคอมไพล์ใหม่เฉพาะเมื่อ dependencies เปลี่ยนแปลง
3. จัดการลำดับ template instantiation เพื่อป้องกันความขัดแย้งในการคอมไพล์

**ตัวแปรสภาพแวดล้อมการ Build**:
OpenFOAM ใช้ตัวแปรสภาพแวดล้อมเพื่อจัดการเส้นทาง build และการตั้งค่าคอมไพเลอร์:

- `WM_PROJECT_VERSION`: เวอร์ชัน OpenFOAM (เช่น "10")
- `WM_OPTIONS`: การตั้งค่าแพลตฟอร์มและคอมไพเลอร์ (เช่น "linux64GccDPInt32Opt")
- `FOAM_LIBBIN`: ไดเรกทอรีไลบรารีระบบ
- `FOAM_USER_LIBBIN`: ไดเรกทอรีไลบรารีผู้ใช้

### 🔗 **Symbolic Links สำหรับการค้นพบ Header**

ระบบไดเรกทอรี `lnInclude` เป็นหนึ่งในคุณสมบัติสถาปัตยกรรมที่เด่นที่สุดของ OpenFOAM ซึ่งออกแบบมาเพื่อแก้ปัญหาการพึ่งพา header ที่ซับซ้อนซึ่งเป็นสิ่งที่หลีกเลี่ยงไม่ได้ในโค้ด C++ ที่ใช้ template หนัก เมื่อคุณ execute `wmakeLnInclude` ระบบจะดำเนินการที่ซับซ้อนซึ่งเกินกว่าการสร้าง symbolic link แบบธรรมดา

**กลไกการค้นพบ Header**:
กระบวนการเริ่มต้นด้วย `wmake` ที่สแกนโครงสร้างไดเรกทอรีต้นฉบับเพื่อระบุไฟล์ header ทั้งหมด (`.H` files) สำหรับแบบจำลองการขนส่งทั่วไป อาจรวมถึง:

```
customViscosityModel/
├── customViscosityModel.H      # การประกาศคลาสหลัก
├── customViscosityModel.C      # การ implement
└── Make/
    ├── files
    └── options
```

กระบวนการสร้าง symbolic link สร้าง namespace แบบแบนใน `lnInclude/` ที่มี headers ทั้งหมดจากไดเรกทอรีปัจจุบันและไดเรกทอรีที่พึ่งพาทั้งหมด แนวทางนี้แก้ไขปัญหาสำคัญหลายประการ:

**Template Instantiation โดยไม่มี Circular Dependencies**:
ใน template metaprogramming headers มักต้อง include ซึ่งกันและกันในรูปแบบที่ซับซ้อน พิจารณาสถานการณ์นี้:

```cpp
// customViscosityModel.H
class customViscosityModel
:
    public viscosityModel
{
    // ขึ้นอยู่กับ volScalarField จาก finiteVolume
    const volScalarField& T_;
};
```

โดยไม่มี `lnInclude` คอมไพเลอร์จะต้องนำทางผ่านเส้นทาง include ที่ซับซ้อนเพื่อค้นหาการประกาศของ `volScalarField` ด้วย symbolic links headers ที่จำเป็นทั้งหมดจะปรากฏเหมือนอยู่ในไดเรกทอรีเดียวกัน ทำให้กระบวนการคอมไพล์ง่ายขึ้นอย่างมาก

**การติดตาม Dependencies และการคอมไพล์เพิ่มเติม**:
ระบบ `wmake` ใช้การเปรียบเทียบ timestamp เพื่อกำหนดสิ่งที่ต้องการคอมไพล์ใหม่ เมื่อไฟล์ header เปลี่ยนแปลง:

1. **การตรวจจับ Header ที่แก้ไข**: `wmake` ตรวจสอบว่าไฟล์ `.H` ใดมี timestamp ใหม่กว่าไฟล์ออบเจกต์ที่เกี่ยวข้อง
2. **การวิเคราะห์ Dependency Chain**: ระบบตรวจสอบว่าไฟล์ต้นฉบับใดขึ้นอยู่กับ header ที่แก้ไข
3. **การคอมไพล์ใหม่เฉพาะส่วน**: มีเพียงไฟล์ต้นฉบับที่ได้รับผลกระทบเท่านั้นที่ถูกคอมไพล์ใหม่ ไม่ใช่ทั้งโปรเจกต์

**การเข้าถึง Header ข้ามโมดูล**:
เมื่อแบบจำลองแบบกำหนดเองของคุณขึ้นอยู่กับโมดูล OpenFOAM หลายโมดูล ระบบ `lnInclude` จะสร้าง symbolic links ไปยัง headers จากไลบรารีที่พึ่งพาทั้งหมด:

```bash
# โครงสร้าง lnInclude ตัวอย่างหลังจาก wmakeLnInclude
lnInclude/
├── customViscosityModel.H              # Header ภายใน
├── viscosityModel.H                    # จาก transportModels
├── volFields.H                         # จาก finiteVolume  
├── tmp.H                              # จาก OpenFOAM core
└── [hundreds of other headers...]
```

โครงสร้างนี้ช่วยให้คอมไพเลอร์สามารถค้นหา header ใดๆ ได้โดยไม่ต้องมีการจัดการเส้นทาง include ที่ซับซ้อน

**การซิงโครไนซ์ Header อัตโนมัติ**:
ระบบ `wmake` อัปเดตไดเรกทอรี `lnInclude` โดยอัตโนมัติเมื่อ:

- ไฟล์ต้นฉบับถูกเพิ่มหรือลบออกจากโปรเจกต์
- Dependencies เปลี่ยนแปลงใน `Make/options`
- ไฟล์ header ถูกแก้ไขหรือเปลี่ยนชื่อ

**การปรับปรุงประสิทธิภาพการ Build**:
แนวทาง symbolic link ให้ประโยชน์ด้านประสิทธิภาพหลายประการ:

1. **ลดเวลาการคอมไพล์**: Headers ไม่ต้องการการค้นหาข้ามไดเรกทอรีหลายๆ ไดเรกทอรี
2. **ลดการใช้หน่วยความจำ**: คอมไพเลอร์สามารถใช้การแคช header ที่มีประสิทธิภาพมากขึ้น
3. **การคอมไพล์แบบขนาน**: ไฟล์หลายไฟล์สามารถคอมไพล์พร้อมกันโดยไม่มีความขัดแย้งของ header

**ประโยชน์ด้านการดีบักและการพัฒนา**:
โครงสร้าง header แบบแบนใน `lnInclude` ทำให้การดีบักง่ายขึ้น:

- ข้อความผิดพลาดของคอมไพเลอร์แสดงเส้นทางไฟล์ที่ชัดเจน
- การแก้ไขสัญลักษณ์ของ IDE ทำงานได้น่าเชื่อถือมากขึ้น
- การนำทางโค้ดถูกทำให้ง่ายขึ้นสำหรับนักพัฒนา

ระบบ `lnInclude` เป็นการแก้ปัญหาที่ซับซ้อนของการจัดการ dependencies สำหรับไลบรารี C++ template ขนาดใหญ่ ช่วยให้สถาปัตยกรรมแบบโมดูลาร์ของ OpenFOAM ทำงานได้ในขณะที่ยังคงรักษาเวลาการคอมไพล์ที่มีประสิทธิภาพ
