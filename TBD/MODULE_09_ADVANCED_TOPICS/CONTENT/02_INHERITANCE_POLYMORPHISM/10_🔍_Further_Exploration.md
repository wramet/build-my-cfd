## 🔍 การสำรวจเพิ่มเติม

### ไฟล์ต้นฉบับหลัก

- `src/phaseSystemModels/phaseModel/phaseModel.H` - ลำดับชั้นโมเดลเฟสหลัก
- `src/phaseSystemModels/interfacialModels/dragModels/dragModel/dragModel.H` - รูปแบบการออกแบบ Strategy
- `src/OpenFOAM/db/runTimeSelection/runTimeSelectionTables.H` - นิยามมาโคร RTS
- `src/finiteVolume/fields/fvPatchFields/basic/calculated/calculatedFvPatchField.H` - พหุสัณฐานฟิลด์

### การอ้างอิงรูปแบบการออกแบบ

- **รูปแบบ Strategy**: ลำดับชั้น `dragModel`
- **รูปแบบ Template Method**: `phaseModel::correct()` ด้วยรูปแบบ NVI
- **รูปแบบ Factory Method**: วิธี `New()` ทั้งหมดพร้อมตาราง RTS
- **รูปแบบ Composite**: `phaseSystem` ที่จัดการ `PtrList<phaseModel>`

### เครื่องมือวิเคราะห์ประสิทธิภาพ

```bash
# วิเคราะห์ overhead ของการเรียกเชิงเสมือน
valgrind --tool=callgrind ./multiphaseEulerFoam
kcachegrind callgrind.out.*

# วัดเวลาการสร้างแบบจำลองจากโรงงาน
export FOAM_VERBOSE=1  # แสดงเวลาในการเลือกแบบจำลอง
```

---

*คู่มือนี้แปลงลำดับชั้นการสืบทอดที่ซับซ้อนของ OpenFOAM จากไวยากรณ์ C++ ที่น่ากลัวให้กลายเป็นรูปแบบการออกแบบที่เข้าใจง่ายซึ่งให้บริการวัตถุประสงค์ทางสถาปัตยกรรมที่เฉพาะเจาะจง ข้อเท็จจริงสำคัญ: **OpenFOAM ใช้พหุสัณฐานไม่ใช่ในฐานะเทคนิคการเขียนโปรแกรม แต่เป็นปรัชญาการสร้างแบบจำลองฟิสิกส์***
