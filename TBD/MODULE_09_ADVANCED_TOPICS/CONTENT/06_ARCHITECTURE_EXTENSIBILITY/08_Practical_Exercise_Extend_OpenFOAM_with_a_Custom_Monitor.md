# แบบฝึกปฏิบัติ: ขยายความสามารถของ OpenFOAM ด้วย Custom Monitor

## ภาพรวม

แบบฝึกปฏิบัตินี้จะแนะนำให้คุณสร้าง `gradientMonitor` functionObject แบบ custom ใน OpenFOAM ที่แสดงให้เห็นถึงการรวมกันอย่างทรงพลังระหว่าง template-based compile-time polymorphism กับ runtime selection mechanisms รูปแบบนี้เป็นพื้นฐานของสถาปัตยกรรมความสามารถในการขยายของ OpenFOAM

## ความต้องการของ FunctionObject

`gradientMonitor` functionObject จะทำให้สมบูรณ์สี่คุณสมบัติหลัก:

1. **การคำนวณ Gradient**: คำนวณขนาดความชันสูงสุดของ field ที่ระบุ
2. **การบันทึกข้อมูล**: เขียนค่า gradient ไปยัง log file ที่กำหนด
3. **การตรวจสอบ Threshold**: แจ้งเตือนเมื่อ gradient เกินขีดจำกัดที่สามารถกำหนดค่าได้
4. **ความยืดหยุ่นของ Type**: รองรับทั้ง scalar และ vector fields ผ่าน template specialization

## การ implement แบบ Template-based

### การกำหนด Class

```cpp
template<class Type>
class gradientMonitor
:
    public functionObject
{
private:
    // Private data members
    
    // Reference to the mesh database
    const fvMesh& mesh_;
    
    // Field name to monitor
    const word fieldName_;
    
    // Threshold value for warnings
    const scalar threshold_;
    
    // Output file stream
    autoPtr<OFstream> outputFile_;
    
    // Current time index for frequency control
    label currentTimeIndex_;

public:
    // Runtime type information
    TypeName("gradientMonitor");

    // Constructors
    gradientMonitor
    (
        const word& name,
        const Time& runTime,
        const dictionary& dict
    );

    // Destructor
    virtual ~gradientMonitor();

    // Member functions
    
    // Read the monitor settings
    virtual bool read(const dictionary& dict);
    
    // Execute the monitoring function
    virtual bool execute();
    
    // Write results
    virtual bool write();
    
    // Update mesh (if applicable)
    virtual void updateMesh(const mapPolyMesh&)
    {}

    // Move points (if applicable)
    virtual void movePoints(const polyMesh&)
    {}
};
```

### รายละเอียดการ implement

```cpp
template<class Type>
gradientMonitor<Type>::gradientMonitor
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    functionObject(name, runTime),
    mesh_(runTime.lookupObject<fvMesh>("region0")),
    fieldName_(dict.get<word>("fieldName")),
    threshold_(dict.getOrDefault<scalar>("threshold", 1e3)),
    currentTimeIndex_(-1)
{
    // Create output file
    const fileName outputPath
    (
        runTime.timePath()/"gradientMonitor_" + fieldName_
    );
    
    outputFile_.reset(new OFstream(outputPath));
    
    // Write header
    *outputFile_ << "# Time" << tab << "MaxGradient" << tab 
                 << "Location" << tab << "Warning" << endl;
    
    Info<< "    gradientMonitor: monitoring field " << fieldName_
        << " with threshold " << threshold_ << endl;
}

template<class Type>
bool gradientMonitor<Type>::execute()
{
    // Check execution frequency (default: every time step)
    if (mesh_.time().timeIndex() == currentTimeIndex_)
    {
        return true;
    }
    currentTimeIndex_ = mesh_.time().timeIndex();

    // Get reference to the field
    const GeometricField<Type, fvPatchField, volMesh>& field =
        mesh_.lookupObject<GeometricField<Type, fvPatchField, volMesh>>
        (
            fieldName_
        );

    // Calculate gradient using fvc::grad
    const typename GeometricField<Type, fvPatchField, volMesh>::GradFieldType
        gradField = fvc::grad(field);

    // Calculate gradient magnitude
    const volScalarField magGradField = mag(gradField);

    // Find maximum gradient magnitude and location
    const scalar maxGrad = max(magGradField).value();
    const label maxCell = findMax(magGradField);
    const vector maxLocation = mesh_.C()[maxCell];

    // Check threshold and issue warning if needed
    bool warning = maxGrad > threshold_;
    if (warning)
    {
        WarningInFunction
            << "Maximum gradient " << maxGrad << " exceeds threshold " 
            << threshold_ << " for field " << fieldName_
            << " at location " << maxLocation << endl;
    }

    // Write to output file
    if (outputFile_.valid())
    {
        *outputFile_ << mesh_.time().timeName() << tab 
                     << maxGrad << tab << maxLocation << tab 
                     << (warning ? "WARNING" : "OK") << endl;
        outputFile_().flush();
    }

    return true;
}

template<class Type>
bool gradientMonitor<Type>::read(const dictionary& dict)
{
    dict.readIfPresent("fieldName", fieldName_);
    dict.readIfPresent("threshold", threshold_);
    return true;
}

template<class Type>
bool gradientMonitor<Type>::write()
{
    return true;
}
```

## Runtime Registration และ Instantiation

### Template Specializations

```cpp
// Explicit instantiation for scalar fields
template class gradientMonitor<scalar>;

// Explicit instantiation for vector fields  
template class gradientMonitor<vector>;

// Add to runtime selection table for scalar fields
addNamedToRunTimeSelectionTable
(
    functionObject,
    gradientMonitor<scalar>,
    dictionary,
    scalarGradientMonitor
);

// Add to runtime selection table for vector fields
addNamedToRunTimeSelectionTable
(
    functionObject,
    gradientMonitor<vector>,
    dictionary,
    vectorGradientMonitor
);
```

### ตัวอย่างการใช้งาน

ใน `controlDict`, ผู้ใช้สามารถกำหนดค่า monitor ดังนี้:

```cpp
functions
{
    pressureGradientMonitor
    {
        type            scalarGradientMonitor;
        functionObjectLibs ("libmyFunctionObjects.so");
        fieldName       p;
        threshold       5e4;
        writeInterval   1;
    }
    
    velocityGradientMonitor  
    {
        type            vectorGradientMonitor;
        functionObjectLibs ("libmyFunctionObjects.so");
        fieldName       U;
        threshold       1e3;
        writeInterval   1;
    }
}
```

## การวิเคราะห์สถาปัตยกรรม

### ประโยชน์ของ Template Metaprogramming

1. **Compile-Time Type Safety**: Templates รับประกันความถูกต้องของ type ที่ compile time แทน runtime
2. **Performance**: ไม่มี overhead ของ virtual function สำหรับ operations หลัก
3. **Code Reusability**: Implementation เดียวทำงานได้กับหลาย field types

### ประโยชน์ของ Runtime Polymorphism

1. **Dynamic Configuration**: ผู้ใช้สามารถเลือก monitor types ผ่าน dictionary input
2. **Extensibility**: สามารถเพิ่ม specializations ใหม่โดยไม่ต้องแก้ไข code ที่มีอยู่
3. **Plugin Architecture**: Function objects สามารถถูกโหลดจาก shared libraries

### Hybrid Design Pattern

การ implementation นี้แสดงให้เห็นถึงแนวทางแบบ hybrid ของ OpenFOAM:

```cpp
// Compile-time: Template-based field operations
const GradFieldType gradField = fvc::grad(field);
const volScalarField magGradField = mag(gradField);

// Runtime: Dictionary-driven configuration
const word fieldName = dict.get<word>("fieldName");
const scalar threshold = dict.getOrDefault<scalar>("threshold", 1e3);
```

รูปแบบนี้ให้ **ประสิทธิภาพ** ของ templates กับ **ความยืดหยุ่น** ของ runtime polymorphism

## วัตถุประสงค์ทางการศึกษา

ผ่านแบบฝึกปฏิบัตินี้ คุณจะได้เรียนรู้:

1. **Template Design**: วิธีการเขียน OpenFOAM code แบบ type-agnostic
2. **FunctionObject Framework**: การเข้าใจ function object lifecycle
3. **Runtime Selection**: วิธีที่ OpenFOAM implement dynamic class loading
4. **Field Operations**: การใช้ finite volume calculus functions (`fvc::grad`)
5. **File I/O**: การจัดการ output stream ของ OpenFOAM
6. **Error Handling**: รูปแบบการรายงาน warning และ error อย่างถูกต้อง

## โอกาสในการขยายความสามารถ

หลังจาก implement monitor พื้นฐานแล้ว ให้พิจารณาส่วนขยายเหล่านี้:

1. **Multi-Field Support**: ตรวจสอบหลาย fields พร้อมกัน
2. **Temporal Analysis**: ติดตามการวิวัฒนาการของ gradient เป็นเวลา
3. **Spatial Analysis**: ระบุบริเวณที่มี gradient สูงอย่างต่อเนื่อง
4. **Adaptive Thresholds**: ปรับ thresholds อย่าง dynamic ตามสภาพการไหล
5. **Visualization Integration**: เขียน field data สำหรับ post-processing
6. **Parallel Communication**: จัดการ distributed memory parallelization

แบบฝึกปฏิบัตินี้เป็นพื้นฐานที่ดีเยี่ยมสำหรับการเข้าใจรูปแบบการขยายความสามารถของ OpenFOAM ขณะที่สร้างเครื่องมือ monitoring CFD ที่ใช้งานได้จริงซึ่งสามารถนำไปใช้ในการจำลองจริง
