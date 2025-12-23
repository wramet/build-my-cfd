## 6️⃣ การใช้งาน & ตัวอย่างข้อผิดพลาด: ขั้นตอนการทำงานแบบเต็ม

### 🚀 **การ implement แบบ step-by-step**

#### **Step 1: สร้างโครงสร้าง Directory**
เพื่อเริ่ม implement custom viscosity model ให้สร้างโครงสร้าง directory ที่เหมาะสมในสภาพแวดล้อมผู้ใช้ OpenFOAM ของคุณ ข้อตกลง directory ของผู้ใช้ช่วยให้สามารถปรับแต่งส่วนตัวได้โดยไม่กระทบต่อการติดตั้ง OpenFOAM หลัก

```bash
cd $WM_PROJECT_USER_DIR
mkdir -p customViscosityModel/powerLawViscosity
cd customViscosityModel
mkdir Make
```

โครงสร้างนี้เป็นไปตามรูปแบบมาตรฐานของ OpenFOAM ซึ่ง source files จะอยู่ใน subdirectories และ build configuration จะอยู่ใน directory `Make`

#### **Step 2: เขียน Source Files**
การ implement ต้องการทั้งไฟล์ header (`.H`) และ source (`.C`) ไฟล์ header จะกำหนด interface ของ class โดยประกาศ member functions และ variables ในขณะที่ source file จะให้การ implement จริงของ mathematical formulation ของ viscosity model

power-law viscosity model ทำตามความสัมพันธ์ทางคณิตศาสตร์:
$$\mu_{eff} = K \cdot |\dot{\gamma}|^{n-1}$$

โดยที่ $K$ คือ consistency index, $n$ คือ power-law index, และ $|\dot{\gamma}|$ คือขนาดของ rate-of-strain tensor

#### **Step 3: กำหนดค่า Build System**
OpenFOAM ใช้ build system `wmake` ซึ่งต้องการไฟล์สองไฟล์ใน directory `Make`:

- `Make/files`: ระบุ source files ทั้งหมดที่จะ compile และระบุชื่อ output library
- `Make/options`: กำหนด compilation flags, include paths, และ library dependencies

ไฟล์เหล่านี้ทำให้มั่นใจได้ว่ามีการเชื่อมโยงที่เหมาะสมกับ core libraries ของ OpenFOAM และ compilation settings ที่ถูกต้อง

#### **Step 4: Build Library**
ดำเนินการ build process โดยใช้ custom build tool ของ OpenFOAM:

```bash
wmake libso
# Output: libcustomViscosityModels.so created in $FOAM_USER_LIBBIN
```

ตัวเลือก `libso` สร้าง shared library (`.so` file) ที่สามารถโหลดแบบ dynamic โดย OpenFOAM solvers library ที่ได้จะถูกวางไว้ใน user library bin directory เพื่อการค้นพบอัตโนมัติ

#### **Step 5: สร้าง Test Case**
ตรวจสอบความถูกต้องของการ implement โดยใช้ tutorial case มาตรฐาน:

```bash
# Copy a tutorial case
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity cavityPowerLaw
cd cavityPowerLaw
```

lid-driven cavity flow เป็น test case ที่ยอดเยี่ยมโดยมีพฤติกรรมและ boundary conditions ที่เป็นที่รู้จักซึ่งเหมาะสำหรับการตรวจสอบความถูกต้องของ non-Newtonian fluid

#### **Step 6: กำหนดค่า Viscosity Model**
แก้ไขไฟล์ `constant/transportProperties` เพื่อใช้ custom power-law model:

```cpp
transportModel  Newtonian;

// NewtonianCoeffs
// {
//     nu          nu [0 2 -1 0 0 0 0] 0.01;
// }

// Power-law viscosity model
viscosityModel  powerLaw;

powerLawCoeffs
{
    K           K [0 2 -1 0 0 0 0] 0.01;  // Consistency index
    n           n [0 0 0 0 0 0 0] 0.8;    // Power-law index
    nuMin       nuMin [0 2 -1 0 0 0 0] 0.001;  // Minimum viscosity
    nuMax       nuMax [0 2 -1 0 0 0 0] 1.0;    // Maximum viscosity
}
```

พารามิเตอร์ที่กำหนด:
- **K**: Consistency index ควบคุมขนาดพื้นฐานของ viscosity
- **n**: Power-law index โดยที่ n<1 แสดงถึง shear-thinning behavior
- **nuMin/nuMax**: ขอบเขตการจำกัดเพื่อป้องกัน numerical instabilities

#### **Step 7: Run Simulation**
ดำเนินการ incompressible flow solver พร้อมกับ output redirection:

```bash
icoFoam > log.icoFoam 2>&1
```

นี่จะรัน simulation ในขณะที่จับทั้ง standard output และ error streams สำหรับการ debug และวิเคราะห์

### 🐛 **ข้อผิดพลาดทั่วไปและวิธีแก้ไข**

#### **Error 1: "Unknown viscosity model powerLaw"**
```
--> FOAM FATAL ERROR:
Unknown viscosity model powerLaw
```

**สาเหตุ**: เกิดขึ้นเมื่อ OpenFOAM ไม่สามารถค้นหา compiled library ที่มี custom viscosity model implementation ได้

**วิธีแก้ไข**: ตรวจสอบความพร้อมใช้งานของ library และการกำหนดค่า path:
```bash
# 1. ตรวจสอบว่า library มีอยู่จริง
ls $FOAM_USER_LIBBIN/libcustomViscosityModels*

# 2. ตรวจสอบว่า library path อยู่ใน LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH | grep $FOAM_USER_LIBBIN

# 3. Rebuild หากจำเป็น
wclean libso
wmake libso
```

ตรวจสอบให้แน่ใจว่า library มีอยู่, path ถูกรวมอยู่ใน dynamic linker search path, และ rebuild ด้วย dependencies ที่เหมาะสมหากจำเป็น

#### **Error 2: "undefined reference to vtable"**
```
powerLawViscosity.C: undefined reference to `vtable for Foam::viscosityModels::powerLawViscosity'
```

**สาเหตุ**: virtual function table (vtable) ไม่ได้ถูกสร้างอย่างถูกต้อง โดยปกติเนื่องจากการ implement ของ pure virtual functions จาก base class ไม่สมบูรณ์

**วิธีแก้ไข**: ตรวจสอบการ implement ที่สมบูรณ์ของ pure virtual functions ทั้งหมดที่จำเป็นจาก `viscosityModel` base class ตรวจสอบว่า:
- มีการ implement ทุก pure virtual functions
- function signatures ตรงกับ base class ทุกประการ
- ไม่มี overridden functions ที่หายไป

#### **Error 3: "no matching function for call to addToRunTimeSelectionTable"**
```
error: no matching function for call to 'addToRunTimeSelectionTable'
```

**สาเหตุ**: constructor signature ไม่ตรงกันระหว่าง class implementation และ runtime selection table declaration

**วิธีแก้ไข**: ทำให้มั่นใจว่ามีความสอดคล้องกันระหว่าง declaration และ implementation:
```cpp
// In header file
declareRunTimeSelectionTable
(
    autoPtr,
    viscosityModel,
    dictionary,
    (
        const word& name,
        const dictionary& dict,
        const volVectorField& U,
        const surfaceScalarField& phi
    ),
    (name, dict, U, phi)
);

// In source file
addToRunTimeSelectionTable
(
    viscosityModel,
    powerLawViscosity,
    dictionary,
    (name, dict, U, phi)
);
```

parameter types และ order ต้องตรงกันอย่างแน่นอนระหว่าง declaration และ registration macro

### 📊 **การตรวจสอบความถูกต้อง: ตรวจสอบผลลัพธ์**

หลังจากการรัน simulation สำเร็จ ให้ตรวจสอบความถูกต้องของการ implement:

```bash
# Monitor shear rate field
foamMonitor -l postProcessing/samples/0/shearRate.xy

# Compare with Newtonian case
paraFoam
```

**เกณฑ์การตรวจสอบความถูกต้อง**:
- **การกระจายตัวของ Shear Rate**: ตรวจสอบว่า shear rate field แสดงรูปแบบที่คาดหวังตาม lid-driven cavity flow
- **โปรไฟล์ความเร็ว**: เปรียบเทียบโปรไฟล์ความเร็วกับ analytical solutions สำหรับ power-law fluids ใน cavity flow
- **พฤติกรรมการลู่เข้า**: ตรวจสอบการลู่เข้าของ residual เพื่อให้มั่นใจในเสถียรภาพเชิงตัวเลข

**พฤติกรรมที่คาดหวัง**:
- Shear-thinning fluids (n < 1) ควรแสดงความหนืดที่ลดลงใกล้ high-shear regions (moving lid)
- โปรไฟล์ความเร็วควรแสดงพฤติกรรมที่ไม่เป็นเชิงเส้นเมื่อเปรียบเทียบกับกรณี Newtonian
- ควรมีการลู่เข้าของ solution โดยไม่มี numerical instabilities

สำหรับการตรวจสอบความถูกต้องเชิงปริมาณ ให้เปรียบเทียบ drag coefficient ที่คำนวณบน moving lid กับ benchmarks ที่เผยแพร่สำหรับ power-law fluids ใน lid-driven cavity flow
