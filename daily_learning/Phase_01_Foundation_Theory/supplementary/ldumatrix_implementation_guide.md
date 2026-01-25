# LduMatrix Implementation Guide | คู่มือการ Implement LduMatrix

> 📁 **แหล่งอ้างอิง:** [[day_02_walkthrough|Day 02 Walkthrough]] > Section 2.2.3
> 📅 **สร้างเมื่อ:** 2026-01-18

---

## 🎯 จุดประสงค์ของไฟล์นี้

ไฟล์นี้อธิบาย**รายละเอียดเชิงลึก**เกี่ยวกับการประกอบ (assembly) ของ LDU Matrix สำหรับ Finite Volume Method โดยเปรียบเทียบ:

1. **OpenFOAM Approach:** `fvMatrix<Type>` — High-level abstraction
2. **Our Approach:** `LduMatrix` — Educational, explicit implementation

---

## 📊 ภาพรวมโครงสร้าง LDU Matrix

### Matrix Equation

$$A \mathbf{x} = \mathbf{b}$$

โดย $A$ เก็บในรูปแบบ **LDU (Lower-Diagonal-Upper)**:

![LDU Matrix Structure](../assets/ldu_matrix_structure_diagram.png)

### Storage Arrays

| Array | ขนาด | เก็บอะไร |
|-------|------|----------|
| `diag_` | `nCells` | Diagonal coefficients ($a_{PP}$) |
| `upper_` | `nFaces` (internal) | Upper off-diagonal ($a_{PN}$) |
| `lower_` | `nFaces` (internal) | Lower off-diagonal ($a_{NP}$) |
| `source_` | `nCells` | RHS source term ($b_P$) |

---

## 🆚 OpenFOAM vs Our Implementation

### 1️⃣ OpenFOAM: `fvMatrix<Type>`

```cpp
// OpenFOAM uses high-level abstraction
fvMatrix<Type>& fvm = tfvm.ref();

forAll(owner, facei) {
    const label own = owner[facei];
    const label nei = neighbour[facei];
    const scalar coeff = gammaMagSf[facei] / mag(delta[facei]);

    // ซ่อน LDU structure ไว้ข้างใน
    fvm.diag()[own] += coeff;
    fvm.diag()[nei] += coeff;
    fvm.upper()[facei] -= coeff;
    fvm.lower()[facei] -= coeff;
}
```

**ข้อดี:**
- ✅ Code สั้น กระชับ
- ✅ Type-safe (รู้ว่า solve scalar/vector)
- ✅ จัดการ Boundary Conditions อัตโนมัติ

**ข้อเสีย:**
- ❌ ซ่อน implementation details
- ❌ เรียนรู้ยากว่าเกิดอะไรขึ้นข้างใน
- ❌ Debug ยากเมื่อมีปัญหา

---

### 2️⃣ Our Approach: `LduMatrix` (Explicit)

```cpp
// Our implementation exposes internal structure
class LduMatrix {
public:
    // เปิดเผย arrays โดยตรง
    std::vector<double> diag_;    // size = nCells
    std::vector<double> upper_;   // size = nInternalFaces
    std::vector<double> lower_;   // size = nInternalFaces
    std::vector<double> source_;  // size = nCells
    
    // Addressing (from mesh)
    std::vector<int> owner_;      // owner cell of each face
    std::vector<int> neighbour_;  // neighbour cell of each face
};
```

---

## 🔧 Step-by-Step Assembly Process

### Example: Laplacian Term $\nabla^2 \phi$

#### Step 1: Initialize Matrix

```cpp
LduMatrix matrix(mesh.nCells(), mesh.nInternalFaces());

// เริ่มต้นทุกค่าเป็น 0
std::fill(matrix.diag_.begin(), matrix.diag_.end(), 0.0);
std::fill(matrix.upper_.begin(), matrix.upper_.end(), 0.0);
std::fill(matrix.lower_.begin(), matrix.lower_.end(), 0.0);
std::fill(matrix.source_.begin(), matrix.source_.end(), 0.0);
```

#### Step 2: Loop Over Internal Faces

```cpp
for (int facei = 0; facei < mesh.nInternalFaces(); ++facei) {
    // ดึง owner และ neighbour cell indices
    const int own = mesh.owner(facei);
    const int nei = mesh.neighbour(facei);
    
    // คำนวณ geometric coefficient
    // coeff = Γ × |Sf| / |d|
    const double gamma = diffusivity[facei];
    const double magSf = mesh.magSf(facei);
    const double delta = mesh.delta(facei);
    const double coeff = gamma * magSf / delta;
    
    // === ใส่ค่าเข้า Matrix อย่างชัดเจน ===
    
    // Diagonal: เพิ่ม coefficient ของตัวเอง
    matrix.diag_[own] += coeff;   // φ_P ใน row P
    matrix.diag_[nei] += coeff;   // φ_N ใน row N
    
    // Off-diagonal: connection ระหว่าง cells (เครื่องหมายลบ!)
    matrix.upper_[facei] = -coeff;  // φ_N ใน row P
    matrix.lower_[facei] = -coeff;  // φ_P ใน row N
}
```

#### Step 3: Visualize What Happens

```
สมมติ mesh 4 cells, 3 internal faces:
Cell 0 ──Face0── Cell 1 ──Face1── Cell 2 ──Face2── Cell 3

หลัง assembly:

       │ Cell 0  │ Cell 1  │ Cell 2  │ Cell 3  │
───────┼─────────┼─────────┼─────────┼─────────┤
Row 0  │ +coeff₀ │ -coeff₀ │    0    │    0    │  ← diag[0], upper[0]
Row 1  │ -coeff₀ │+c₀+c₁   │ -coeff₁ │    0    │  ← lower[0], diag[1], upper[1]
Row 2  │    0    │ -coeff₁ │+c₁+c₂   │ -coeff₂ │  ← lower[1], diag[2], upper[2]
Row 3  │    0    │    0    │ -coeff₂ │ +coeff₂ │  ← lower[2], diag[3]
```

---

## ⚠️ Non-Orthogonal Correction

### OpenFOAM Approach

```cpp
// OpenFOAM handles non-orthogonal correction implicitly
if (mesh.nonOrthogonal()) {
    // เพิ่ม correction term เข้า source
    fvm.source() += nonOrthCorrection;
}
```

### Our Approach (Phase 1: Skip)

```cpp
// Phase 1: ข้ามไปก่อน เพื่อให้ code ง่าย
// ใช้ได้กับ orthogonal mesh เท่านั้น!

// TODO Phase 2: เพิ่ม non-orthogonal correction
// const double correctionCoeff = ...;
// matrix.source_[own] += correctionCoeff;
// matrix.source_[nei] -= correctionCoeff;
```

**เหตุผลที่ข้าม:**
1. ลดความซับซ้อนในช่วง learning
2. Debug ง่ายกว่า
3. ใช้ได้กับ cartesian mesh (orthogonal) ก่อน
4. เพิ่มทีหลังได้เมื่อเข้าใจ core algorithm แล้ว

---

## 💡 Key Differences Summary

| Aspect | OpenFOAM `fvMatrix` | Our `LduMatrix` |
|--------|---------------------|-----------------|
| **Abstraction** | High-level | Low-level (explicit) |
| **Type Safety** | Template `<Type>` | Fixed `double` (Phase 1) |
| **BC Handling** | Automatic | Manual |
| **Non-Orthogonal** | Built-in | Skipped (Phase 1) |
| **Purpose** | Production | Educational |
| **Debugging** | Hard | Easy (visible arrays) |

---

## 🔗 Cross References

- [[day_02_walkthrough#2.2.3 gaussLaplacianScheme|← Back to Section 2.2.3]]
- [[../Phase_01_Foundation_Theory/02|Source: Day 02 FVM Basics]]

---

## 📝 Exercises

### Exercise 1: Trace the Assembly

สำหรับ mesh 3 cells, 2 internal faces:
1. เขียน owner/neighbour arrays
2. สมมติ coeff = 1.0 ทุกหน้า
3. เขียน diag, upper, lower arrays หลัง assembly

### Exercise 2: Add Source Term

แก้ code ให้รองรับ source term $S_P$:
```cpp
// Hint: source term เพิ่มเข้า source array โดยตรง
matrix.source_[cellI] += sourceValue[cellI] * cellVolume[cellI];
```
