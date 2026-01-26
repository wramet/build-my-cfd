
def translate_sec4():
    path = "daily_learning/temp_qc/section_04.md"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Main Header
    content = content.replace("# 5. Section 4: Implementation", "# Section 4: Implementation | ส่วนที่ 4: การนำไปใช้")

    # Replace Intro Text
    old_intro = """This section provides the complete, compilable C++ implementation for the integrated solver architecture described in Day 19. We will implement the three core classes: `IntegratedEvaporatorSolver`, `MeshManager`, and `RefinementCriterion`, along with concrete refinement strategies."""
    new_intro = """This section provides the complete, compilable C++ implementation for the integrated solver architecture described in Day 19. We will implement the three core classes: `IntegratedEvaporatorSolver`, `MeshManager`, and `RefinementCriterion`, along with concrete refinement strategies. | ส่วนนี้จัดเตรียมการนำไปใช้ C++ ที่สมบูรณ์และสามารถคอมไพล์ได้สำหรับสถาปัตยกรรมของ solver ที่รวมศูนย์ตามที่อธิบายไว้ในวันที่ 19 เราจะ implement คลาสหลักสามคลาส: `IntegratedEvaporatorSolver`, `MeshManager`, และ `RefinementCriterion` พร้อมกับกลยุทธ์การ refinement ที่เป็นรูปธรรม"""
    content = content.replace(old_intro, new_intro)

    # Replace Subheaders if needed (usually bilingual already in source? No, grep showed English)
    # Check Step 2185. 
    # "## 5.1 Class Headers | ไฟล์ส่วนหัวของคลาส (Class Headers)" - This is ALREADY bilingual.
    # So I only need to fix the Main Header and Intro.

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    translate_sec4()
