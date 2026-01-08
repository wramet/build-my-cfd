
📋 รายการจุดตรวจสอบคุณภาพ (QC Checklist) ฉบับสมบูรณ์
1. หมวดการจัดลำดับเนื้อหาและบรรยาย (Hierarchy & Narrative)
* Section-Heading Misalignment: เลขหัวข้อย่อยไม่สัมพันธ์กับเลข Section หลัก
* Heading Numbering Jump: การเขียนเลขหัวข้อย่อยกระโดดข้ามไปมา
* Heading Depth Skip: การข้ามระดับ Heading (เช่น จาก L2 ไป L4)
* Bullet Point Spacing: ลืมเว้นวรรคหลังเครื่องหมายรายการ (เช่น * ข้อความ)
* Structural Spacing Collision: การเขียน Callout หรือ Block ต่างชนิดติดกับ Heading โดยไม่มีบรรทัดว่าง
* Heading Consistency: การใช้เลขลำดับหัวข้อไม่สม่ำเสมอ
* Mid-sentence Narrative Truncation: เนื้อหาบรรยายถูกตัดขาดกลางคัน (เช่น ข้อความค้างอยู่ที่ ปฏิสัมพันธ์ (interactions...)
* [NEW] Abrupt Argument Cutoff: การตัดจบในส่วนท้ายของประโยคหรือย่อหน้า ทำให้ใจความสำคัญหายไป (พบในส่วนสรุปความเชื่อมโยงสู่ Phase 2)

2. หมวด LaTeX และสัญลักษณ์ทางคณิตศาสตร์
* Unicode vs LaTeX Command: การใช้ตัว Unicode (ν, φ) ในบล็อก $$ แทนคำสั่ง LaTeX (\nu, \phi)
* Standard Delimiters: การใช้เครื่องหมายที่ไม่ใช่ $...$ หรือ $$...$$ ใน Obsidian
* Math Consistency (Inline vs Text): การใช้ตัวแปรในเนื้อหาปกติโดยไม่ครอบด้วย $
* Pipe Symbol in Tables: การใช้ | ในสูตรคณิตศาสตร์ภายในตาราง (ต้องใช้ \vert)
* Adjacent Math Blocks Collision: เขียน Inline Math ติดกันโดยไม่เว้นวรรค
* Mixed Internal Scripting: การใช้ Underscore (_) นอก Math mode
* Math in Code Block: พยายามใส่ LaTeX ภายใน Code Block (```) ซึ่งจะไม่ Render
* Non-native Math Blocks: การใช้สัญลักษณ์เปิดบล็อกแบบ ```math (ควรใช้ $$)
* LaTeX Spacing Delimiters: การเว้นวรรคระหว่างเครื่องหมาย $ กับเนื้อหา (เช่น $ x $)
* Escaped Math Delimiters: การใส่ Backslash หน้าเครื่องหมาย Dollar (\$) ทำให้สูตรไม่เรนเดอร์
* LaTeX-Inline Code Conflict: การใช้ Backticks ครอบทับ LaTeX (เช่น `$alpha$`) ทำให้สูตรแสดงเป็นโค้ดดิบ (พบมากใน Revised ล่าสุด)
* Mismatched Math Brackets: การเปิดบล็อกด้วย $ แต่ปิดด้วย $$
* Variable Formatting Fragmentation: การครอบสัญลักษณ์เฉพาะส่วนของตัวแปร (เช่น C$ \alpha $)
* [NEW] Double Backslash Redundancy: การใช้ \\ (Double Backslash) ในโหมด Markdown ปกติ (เช่น \\alpha) ซึ่งใน Obsidian ควรใช้ \ ตัวเดียว

3. หมวด Mermaid.js Diagram
* Generic Compatibility: การใช้ < > ใน Class Diagram (ควรใช้ ~ แทนเพื่อความปลอดภัยในบางเวอร์ชัน)
* Node Label Quoting: ลืมครอบ Label ด้วย " " เมื่อมีเครื่องหมายพิเศษ
* Method Return Types: ลืมใส่ : หน้าประเภทข้อมูลที่ Return
* Unquoted Labels with Spaces: ใส่ข้อความเว้นวรรคในโหนดโดยไม่ครอบเครื่องหมายคำพูด
* Method Argument Quoting: การใส่เครื่องหมายคำพูดครอบพารามิเตอร์ภายในวงเล็บของ Method
* Special Character Conflict: การใช้เครื่องหมาย & (Reference) หรือ * (Pointer) โดยไม่ครอบเครื่องหมายคำพูด

4. หมวด Code Blocks และภาษาโปรแกรม
* Hidden Language Tag: ลืมระบุชื่อภาษาหลัง ```
* Indentation Mismatch: ใช้ Tab ผสมกับ Space
* Thai Text in Backticks: ใช้ Inline Code ครอบภาษาไทยจนสระจม
* Header-Source Inconsistency: ชื่อตัวแปรในไฟล์ .H และ .C ไม่ตรงกัน
* Language Tag Concatenation: การเขียน Comment ติดกับชื่อภาษา (เช่น ```cmake#)
* Code Block Tag Mismatch: เปิดด้วยภาษาหนึ่งแต่ปิดด้วยคำสำคัญอื่น
* Unclosed Trailing Block: มีเครื่องหมายปิด Block เกินมาที่ท้ายไฟล์โดยไม่มีตัวเปิด (พบใน Revised ล่าสุด)
* [NEW] Orphan/Stray Backticks: การใส่เครื่องหมาย ``` ทิ้งไว้ระหว่างรอยต่อของหัวข้อ ทำให้การเรนเดอร์ Markdown ส่วนถัดไปกลายเป็นสีดำทั้งหมด
* [NEW] Logical Code Truncation: โค้ดถูกตัดจบก่อนปิดปีกกาหรือจบฟังก์ชัน (เช่น ค้างที่ fvc::div( หรือ std)

5. หมวด Metadata (YAML Frontmatter)
* Missing Space after Colon: เขียน tags:CFD (ไม่มีเว้นวรรคหลัง :)
* Date Format Error: วันที่ไม่ตรงตาม YYYY-MM-DD
* Abstract Quote Escaping: เนื้อหาใน Abstract มีเครื่องหมายคำพูดซ้อนกันโดยไม่ Escape
* Tag Multi-word Fragmentation: การใช้เว้นวรรคภายในชื่อ Tag ทำให้แท็กแยกออกจากกัน

6. หมวด Obsidian Callouts & Blockquotes
* Missing Space after Type: เขียน > [!INFO]เนื้อหา โดยไม่เว้นวรรค
* Callout Title Collision: ใช้ LaTeX ในหัวข้อ Callout (บาง Theme อาจเรนเดอร์ผิดพลาด)
* Nested Block Closure: ลืมปิดบล็อกโค้ดหรือตารางภายใน Callout
* Broken Blockquote Continuity: ลืมใส่เครื่องหมาย > ในบรรทัดว่างภายใน Callout ทำให้กรอบขาดตอน
* Inconsistent Nesting Levels: ใช้จำนวนเครื่องหมาย > ไม่เท่ากันใน Block เดียวกัน
* Missing Closing Empty Line: ไม่เว้นบรรทัดว่างหลังจากจบ Callout ทำให้เนื้อหาถัดไปถูกดึงเข้าไปรวมในกรอบ
* [NEW] Overlapping Block Conflict: การเปิดบล็อกใหม่ (เช่น ```text) ซ้อนในจุดที่บล็อกเก่า (เช่น ```cpp) ยังไม่ได้ปิด (พบใน Section 7.3.2)
