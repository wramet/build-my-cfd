# 04 รากฐานคณิตศาสต์: การนับการอ้างอิงและความปลอดภัยของหน่วยความจำ

![[memory_safety_proof.png]]
`A clean scientific diagram illustrating the "Memory Safety State Machine". Show states for "Memory Allocated", "Multiple References", "Single Reference", and "Memory Freed". Use mathematical arrows with +1/-1 labels representing ref() and unref(). Use a minimalist palette, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

การจัดการหน่วยความจำใน OpenFOAM ไม่ใช่เพียงเรื่องของการเขียนโปรแกรม แต่มีรากฐานมาจากทฤษฎีการจัดการทรัพยากรและการพิสูจน์ความถูกต้องทางคณิตศาสตร์ เพื่อป้องกันปัญหาที่อาจเกิดขึ้นในการคำนาณขนาดใหญ่:

---

## การนับการอ้างอิงเป็นสถานะเครื่องจักร

กำหนดให้ $r(t) \in \mathbb{N}_0$ เป็นจำนวนการอ้างอิงของอ็อบเจกต์ในเวลา $t$ การดำเนินการ `ref()` และ `unref()` จะปรับเปลี่ยนค่านี้:

$$
\begin{aligned}
\text{ref()} &: r(t^+) = r(t) + 1 \\[4pt]
\text{unref()} &: r(t^+) = r(t) - 1 \quad \text{พร้อมเงื่อนไข } r(t) > 0
\end{aligned}
$$

อ็อบเจกต์จะ **ถูกลบ** เมื่อ $r(t^+) = 0$ หลังจากการดำเนินการ `unref()` ซึ่งนี้จะรับประกัน **ความไม่เปลี่ยนแปลงของความปลอดภัยหน่วยความจำ**:

$$
\forall t : r(t) = 0 \implies m(t) = 0
$$

โดยที่ $m(t) \in \{0,1\}$ บ่งบอกว่าหน่วยความจำถูกจอง ($1$) หรือถูกปล่อย ($0$) การ implement การนับการอ้างอิงที่ถูกต้องจะเป็นไปตามความไม่เปลี่ยนแปลงนี้ด้วยความน่าจะเป็น 1 ซึ่งจะรับประกันว่าไม่มีการรั่วไหลของหน่วยความจำ

---

## การวิเคราะห์ค่าใช้จ่ายหน่วยความจำ

สำหรับฟิลด์ที่มี $N$ องศาอิสระ (เช่น เซลล์, หน้า) แต่ละตัวมีขนาด $s$ ไบต์ การใช้หน่วยความจำทั้งหมดกับการนับการอ้างอิงคือ:

$$
M_{\text{total}} = N \cdot s + \underbrace{4}_{\text{refCount\_}} + \underbrace{\mathcal{O}(1)}_{\text{smart‑pointer overhead}}
$$

ค่าใช้จ่ายเพิ่มเติมเป็น **ค่าคงที่** (≈ 4 ไบต์) ไม่ขึ้นกับขนาดของฟิลด์ ทำให้เป็นเรื่องเล็กน้อยสำหรับฟิลด์ CFD ขนาดใหญ่ ($N \sim 10^6$–$10^9$)

---

## ประสิทธิภาพของ Atomic Operations

ในการรันแบบขนาน การนับการอ้างอิงแบบ atomic ใช้ `std::atomic<int>` พร้อมข้อจำกัดของ memory-order ต้นทุนของการเพิ่ม/ลดค่าแบบ atomic มีค่าประมาณ:

$$
t_{\text{atomic}} \approx t_{\text{non‑atomic}} + \text{memory‑barrier penalty}
$$

โดยค่าใช้จ่ายเพิ่มเติมขึ้นอยู่กับฮาร์ดแวร์ (โดยทั่วไป 10–50 ns) สำหรับฟิลด์ที่เข้าถึงโดยหลาย thread ค่าใช้จ่ายเพิ่มเติมนี้ยอมรับได้เมื่อเทียบกับต้นทุนของการคัดลอกข้อมูลฟิลด์

---

## การจัดแนว Cache-Line และ False Sharing

```mermaid
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
subgraph "Processor Cache (64-byte lines)"
CL1[Cache Line 1<br/>refCount_ A]:::implicit
CL2[Cache Line 2<br/>refCount_ B]:::implicit
CL3[Cache Line 3<br/>Unused/Padding]:::explicit
end
T1[Thread 1]:::explicit --> CL1
T2[Thread 2]:::explicit --> CL2
```
> **Figure 1:** แผนผังการจัดวางตัวนับการอ้างอิง (refCount_) บนหน่วยความจำแคช โดยมีการใช้ `alignas(64)` เพื่อแยกตัวแปรของแต่ละออบเจกต์ให้อยู่คนละ Cache Line ป้องกันปัญหา False Sharing ที่จะทำให้ประสิทธิภาพลงลงเมื่อมีการประมวลผลแบบขนาน (Parallel Processing)

เพื่อหลีกเลี่ยง **false sharing** ในการเข้าถึงแบบขนาน ตัวแปรสมาชิกที่สำคัญ (เช่น `refCount_`) ถูกวางไว้บน cache line ที่แยกกัน (64 ไบต์บน x86‑64) คำสั่งการจัดแนว `alignas(64)` จะทำให้แน่ใจว่า:

$$
\text{address}(refCount\_) \mod 64 = 0
$$

นี้จะป้องกันไม่ให้สอง thread ทำให้ cache line ของกันและกันเป็นโมฆะเมื่ออัปเดตจำนวนการอ้างอิงของอ็อบเจกต์ที่แตกต่างกัน

---

## รากฐานทางคณิตศาสตร์ของ Smart Pointers

### ความสัมพันธ์ระหว่าง autoPtr และ tmp

สำหรับการจัดการหน่วยความจำที่ถูกต้อง เราสามารถนิยาม semantic ของ smart pointers เป็นฟังก์ชันทางคณิตศาสตร์:

$$
\text{Ownership}(p) =
\begin{cases}
\text{Exclusive} & \text{if } p \in \text{autoPtr} \\
\text{Shared} & \text{if } p \in \text{tmp} \\
\text{None} & \text{if } p = \text{nullptr}
\end{cases}
$$

โดยที่:
- `autoPtr` รับประกันว่า $\forall t : |\{p \mid \text{owns}(p, t)\}| \leq 1$ (มีเจ้าของได้เพียงคนเดียว)
- `tmp` รับประกันว่า $\sum_i \text{refCount}_i(p) = r(p)$ ผลรวมของการอ้างอิงทั้งหมด

### ทฤษฎีบทของการจัดการหน่วยความจำที่ปลอดภัย

**ทฤษฎีบท:** ระบบการจัดการหน่วยความจำของ OpenFOAM เป็น **memory-safe** ถ้า:

1. $\forall p, t : r(p, t) = 0 \implies \text{deallocated}(p, t)$
2. $\forall p, t : \text{allocated}(p, t) \implies r(p, t) \geq 1$
3. $\nexists p, t_1, t_2 : \text{allocated}(p, t_1) \land \text{allocated}(p, t_2) \land t_1 \neq t_2$

**การพิสูจน์:** โดยการออกแบบของ `refCount`:
- เงื่อนไขที่ 1: `unref()` คืนค่า `true` เมื่อ `refCount_` ถึง 0 และ destructor ถูกเรียก
- เงื่อนไขที่ 2: constructor ของ `tmp` เรียก `ref()` ทุกครั้งที่สร้างการอ้างอิงใหม่
- เงื่อนไขที่ 3: RAII semantic รับประกันว่าออบเจกต์ถูกจัดสรรและคืนครั้งเดียว

∎

---

## การประยุกต์ใช้กับ Field Algebra

ในการคำนวณ CFD การดำเนินการฟิลด์สามารถแสดงเป็นนิพจน์เชิงฟังก์ชัน:

$$
\mathbf{C} = \alpha \mathbf{A} + \beta \mathbf{B}
$$

โดยที่ $\mathbf{A}, \mathbf{B}, \mathbf{C}$ เป็นฟิลด์และ $\alpha, \beta \in \mathbb{R}$

ระบบ `tmp` ช่วยให้สามารถเขียน:

```cpp
// Create a temporary field for alpha*A + beta*B operation
// Temporary field avoids unnecessary memory copies through reference counting
tmp<volScalarField> C = alpha*A + beta*B;
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystemSolve.C`

**คำอธิบาย:**
- **วัตถุประสงค์ (Source):** ไฟล์ `phaseSystemSolve.C` ใน multiphaseEulerFoam solver แสดงการใช้ `tmp<surfaceScalarField>` สำหรับการจัดการฟิลด์ชั่วคราวในการคำนวณระบบหลายเฟส โดยเฉพาะในส่วนของการคำนวณ effective flux ของเฟสที่เคลื่อนที่
- **การอธิบาย (Explanation):** การใช้ `tmp` ช่วยให้สามารถสร้างฟิลด์ชั่วคราวสำหรับเก็บผลลัพธ์ของนิพจน์ทางคณิตศาสตร์โดยไม่ต้องคัดลอกข้อมูลจริง ระบบจะใช้การนับการอ้างอิงเพื่อติดตามว่ามีส่วนไหนของโค้ดที่ยังต้องการใช้ฟิลด์นี้อยู่ และจะคืนหน่วยความจำโดยอัตโนมัติเมื่อไม่มีการอ้างอิงเหลืออยู่
- **แนวคิดสำคัญ (Key Concepts):**
  - **Reference Counting (การนับการอ้างอิง):** ระบบติดตามจำนวนการอ้างอิงถึงฟิลด์ เพื่อกำหนดเวลาที่จะคืนหน่วยความจำ
  - **Lazy Evaluation (การประเมินผลแบบล่าช้า):** การคำนวณเกิดขึ้นจริงเมื่อมีการเข้าถึงค่าในฟิลด์ ไม่ใช่เมื่อสร้างนิพจน์
  - **Expression Template (เทมเพลตนิพจน์):** เทคนิคการสร้าง expression tree เพื่อหลีกเลี่ยงการคัดลอกข้อมูลชั่วคราว
  - **Memory Safety (ความปลอดภัยของหน่วยความจำ):** การรับประกันว่าไม่มี memory leaks หรือ double delete ผ่าน RAII semantics

โดยไม่มีการคัดลอกข้อมูลจริงจนกว่าจำเป็น นี้คือ **lazy evaluation**:

$$
\text{Evaluate}(C, i) = \alpha \cdot \text{Evaluate}(A, i) + \beta \cdot \text{Evaluate}(B, i)
$$

สำหรับแต่ละ index $i$ การคำนวณเกิดขึ้นตามความต้องการ เก็บไว้ใน expression tree จนกว่าจะมีการเข้าถึง

---

## ข้อจำกัดและการแลกเปลี่ยน

### Trade-off: Reference Counting vs Manual Management

| แง่มุม | Reference Counting | Manual Management |
|---------|-------------------|-------------------|
| **ความปลอดภัย** | ✅ สูง (automatic cleanup) | ❌ ต่ำ (human error prone) |
| **ประสิทธิภาพ** | ⚠️ ค่าใช้จ่ายเล็กน้อย | ✅ เร็วที่สุด |
| **ความซับซ้อน** | ⚠️ ต้องการ refCount class | ✅ ง่าย (ตรงไปตรงมา) |
| **Parallel** | ⚠️ ต้องการ atomic ops | ✅ ไม่ต้องการ sync |
| **Memory Overhead** | 4 bytes/object | 0 bytes |

### สมการค่าใช้จ่ายทั้งหมด

$$
T_{\text{total}} = T_{\text{computation}} + T_{\text{memory}} + T_{\text{overhead}}
$$

โดยที่:

$$
T_{\text{overhead}} = \sum_{\text{operations}} (t_{\text{ref}} + t_{\text{unref}}) + n_{\text{atomic}} \cdot t_{\text{memory barrier}}
$$

สำหรับการจำลอง CFD ขนาดใหญ่ $T_{\text{computation}} \gg T_{\text{overhead}}$ ทำให้การค้าเสียเล็กน้อยในด้านประสิทธิภาพเป็นที่ยอมรับได้เมื่อเทียบกับประโยชน์ด้านความปลอดภัยและการบำรุงรักษาโค้ด

---

## การพิสูจน์ความถูกต้องของ Memory Safety

### การไม่มี Memory Leaks

**ข้อเสนอ:** ระบบ `tmp` + `refCount` ของ OpenFOAM ไม่มี memory leaks

**การพิสูจน์:**

สมมติให้:
- $\mathcal{O}$ เป็นเซตของออบเจกต์ทั้งหมด
- $\forall o \in \mathcal{O}$: นิยาม $r_o(t)$ เป็นจำนวนการอ้างอิงของ $o$ ในเวลา $t$

**พื้นฐาน:**
1. Constructor ของ `tmp` เรียก `o->ref()` ทุกครั้งที่สร้าง
2. Destructor ของ `tmp` เรียก `o->unref()` ทุกครั้งที่ทำลาย
3. `unref()` ลบออบเจกต์เมื่อ `refCount_` ถึง 0

**ขั้นตอนการพิสูจน์:**

*Case 1: ไม่มีการใช้ tmp*
- ถ้าไม่มี `tmp` ที่อ้างถึง $o$ แล้ว $r_o(t) = 0$
- โดยพื้นฐานที่ 3: $o$ จะถูกลบ
- ∴ ไม่มี leak

*Case 2: มีการใช้ tmp*
- สำหรับทุก `tmp<T> t` ที่อ้างถึง $o$: destructor จะเรียก `unref()`
- เมื่อ `tmp` ตัวสุดท้ายถูกทำลาย: $r_o(t) = 0$
- โดยพื้นฐานที่ 3: $o$ จะถูกลบ
- ∴ ไม่มี leak

**บทสรุป:** ในทุกกรณี ออบเจกต์จะถูกลบเมื่อไม่มีการอ้างอิง ∎

### การไม่มี Double Delete

**ข้อเสนอ:** ระบบไม่ลบออบเจกต์เดียวกันสองครั้ง

**การพิสูจน์:**

สมมติให้ $o$ เป็นออบเจกต์ที่มี $r_o(t) = 1$ และ `unref()` ถูกเรียก:

1. ก่อน `unref()`: $r_o = 1$
2. `unref()` ลด: $r_o \leftarrow r_o - 1 = 0$
3. ตรวจสอบ: $r_o == 0$ → คืนค่า `true`
4. Delete: `delete o` เกิดขึ้น
5. หลังจากนี้: การอ้างอิงใดๆ ถึง $o$ เป็น undefined behavior

หากมี `unref()` ที่สองพยายามถูกเรียก:
- ออบเจกต์ถูกลบแล้ว → segmentation fault หรือ undefined behavior
- แต่ระบบรับประกันว่า `unref()` จะถูกเรียกเพียงครั้งเดียว (จาก `tmp` ตัวสุดท้าย)

∴ ระบบป้องกัน double delete โดย semantic การเป็นเจ้าของ

---

## สรุปคุณสมบัติทางคณิตศาสตร์

### คุณสมบัติของระบบการจัดการหน่วยความจำ OpenFOAM

1. **Type Safety**: $\forall p : \text{typeof}(p) \in \{\text{autoPtr}, \text{tmp}, \text{raw ptr}\}$

2. **Memory Safety**: $\forall t : \sum_{\text{leaks}} = 0$

3. **Reference Consistency**: $\forall o, t : r_o(t) \geq 0$

4. **Ownership Uniqueness**: $\forall o, t : |\text{owners}(o, t)| \leq 1$ (สำหรับ `autoPtr`)

5. **Lifetime Determinism**: $\forall o : \exists t_{\text{delete}}(o)$ ซึ่ง deterministic หากทราบลำดับของ operations

---

## อ้างอิงเพิ่มเติม

- **Memory Model**: C++ Memory Model and Synchronization
- **Atomic Operations**: Herlihy & Shavit, "The Art of Multiprocessor Programming"
- **Reference Counting**: D. Lea, "Concurrent Programming in Java"
- **Cache Coherence**: M. Flynn, "Computer Architecture: Pipelined and Parallel Processor Design"