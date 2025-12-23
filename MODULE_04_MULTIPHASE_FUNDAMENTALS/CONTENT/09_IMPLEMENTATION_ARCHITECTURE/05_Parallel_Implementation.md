# การนำไปใช้งานแบบขนาน (Parallel Implementation)

## 1. บทนำ (Overview)

การจำลองการไหลหลายเฟสมีความซับซ้อนและต้องใช้ทรัพยากรการคำนวณสูงมาก `multiphaseEulerFoam` จึงถูกออกแบบมาให้รองรับการคำนวณแบบขนาน (Parallel Computing) อย่างเต็มรูปแบบผ่านกลยุทธ์การแบ่งโดเมน (Domain Decomposition) และการทำสมดุลภาระ (Load Balancing) ที่มีประสิทธิภาพ

---

## 2. การแบ่งโดเมน (Domain Decomposition)

การประมวลผลแบบขนานใน OpenFOAM อาศัยการแบ่งพื้นที่คำนวณ (Computational Domain) ออกเป็นส่วนย่อยๆ (Subdomains) และกระจายไปยังหน่วยประมวลผล (Processors) ต่างๆ

### 2.1 สถาปัตยกรรม `parallelPhaseModel`
คลาสนี้ขยายความสามารถของ `phaseModel` เพื่อจัดการการดำเนินการข้ามโปรเซสเซอร์:
- **Local Fields**: แต่ละโปรเซสเซอร์จะเก็บข้อมูลฟิลด์เฉพาะในโดเมนย่อยของตนเอง
- **Ghost Cells**: เซลล์ลับบริเวณขอบเขตโปรเซสเซอร์ที่ใช้เพื่อรักษาความต่อเนื่องของข้อมูล
- **Processor Synchronization**: การประสานข้อมูลข้ามขอบเขตผ่านคลาส `processorFvPatchField`

**การประสานข้อมูลฟิลด์ (`synchronizeFields`):**
```cpp
void parallelPhaseModel::synchronizeFields()
{
    const fvPatchList& patches = mesh().boundary();
    forAll(patches, patchi)
    {
        if (patches[patchi].type() == processorFvPatch::typeName)
        {
            const processorFvPatchField<vector>& procPatch = 
                refCast<const processorFvPatchField<vector>>(U_.boundaryField()[patchi]);
            
            procPatch.initSwapFields(); // เริ่มต้นการส่งข้อมูลแบบ Non-blocking
        }
    }
    forAll(patches, patchi)
    {
        if (patches[patchi].type() == processorFvPatch::typeName)
        {
            // ทำการแลกเปลี่ยนข้อมูลให้เสร็จสมบูรณ์
            refCast<processorFvPatchField<vector>>(U_.boundaryField()[patchi]).swapFields();
        }
    }
}
```

---

## 3. การทำสมดุลภาระ (Load Balancing)

ในการไหลหลายเฟส ภาระการคำนวณในแต่ละพื้นที่อาจไม่เท่ากัน (เช่น บริเวณที่มีอินเตอร์เฟซซับซ้อนจะใช้พลังงานมากกว่า) ดังนั้นจึงจำเป็นต้องมีการปรับสมดุลภาระอย่างเหมาะสม

### 3.1 คลาส `multiphaseLoadBalancer`
ใช้อัลกอริทึมที่ซับซ้อนเพื่อกระจายภาระการคำนวณใหม่แบบไดนามิก:
- **การคำนวณภาระ (Load Calculation)**: พิจารณาจากจำนวนเซลล์, ความซับซ้อนของโมเดลความปั่นป่วน (RAS/LES), และปรากฏการณ์ที่อินเตอร์เฟซ
- **Dynamic Re-partitioning**: ใช้ไลบรารีอย่าง Metis หรือ Scotch เพื่อแบ่งส่วน Mesh ใหม่ตามภาระงานที่เกิดขึ้นจริง

**ตัวอย่างการคำนวณภาระงาน:**
```cpp
scalarField multiphaseLoadBalancer::calculateLoad()
{
    scalarField load(Pstream::nProcs(), 0.0);
    // เพิ่มภาระงานตามความซับซ้อนของฟิสิกส์ในแต่ละเฟส
    forAll(phases_, phaseI)
    {
        if (phases_[phaseI].turbulence().modelType() == "LES")
            load[phaseI] += turbulenceLESWeight_ * phases_[phaseI].cellCount();
        
        load[phaseI] += sum(phases_[phaseI].interfaceArea()) * interfaceWeight_;
    }
    return load;
}
```

---

## 4. การสื่อสารระหว่างโปรเซสเซอร์ (Inter-Processor Communication)

OpenFOAM ใช้ MPI (Message Passing Interface) สำหรับการแลกเปลี่ยนข้อมูล:
- **Synchronization Points**: ฟิลด์ต่างๆ จะถูกซิงโครไนซ์ที่จุดวิกฤต เช่น ก่อนการแก้สมการ Advection และก่อนแก้สมการความดัน
- **Non-blocking Communication**: ใช้ `initSwapFields()` และ `swapFields()` เพื่อให้การส่งข้อมูลสามารถทำงานขนานไปกับการคำนวณได้

---

## 5. ประสิทธิภาพการประมวลผลแบบขนาน (Parallel Efficiency)

ประสิทธิภาพขึ้นอยู่กับอัตราส่วนระหว่างการสื่อสารกับการคำนวณ (Communication-to-Computation Ratio):

- **Speedup**: $S_N = \frac{T_1}{T_N}$
- **Efficiency**: $E_N = \frac{T_1}{N \cdot T_N} \times 100%$

**กฎของ Amdahl (Amdahl's Law):**
$$\text{Max Speedup} = \frac{1}{(1-P) + \frac{P}{N}}$$
โดยที่ $P$ คือสัดส่วนของโค้ดที่สามารถรันแบบขนานได้

---

## 6. สรุป (Summary)

สถาปัตยกรรมขนานของ `multiphaseEulerFoam` ช่วยให้สามารถจำลองระบบอุตสาหกรรมขนาดใหญ่ที่มีเซลล์คำนวณนับล้านเซลล์ได้อย่างมีประสิทธิภาพ:
1. **Scalability**: รองรับการสเกลได้ถึงระดับหลายพันคอร์
2. **Dynamic Adaptation**: ปรับแต่งภาระงานได้ตามสถานะของฟิสิกส์ที่เปลี่ยนไป
3. **Memory Efficiency**: จัดการหน่วยความจำแบบกระจาย (Distributed Memory) ได้อย่างดีเยี่ยม

*อ้างอิง: วิเคราะห์ตามซอร์สโค้ด OpenFOAM-10, parallelPhaseModel.C และกลไกการสื่อสาร Pstream*