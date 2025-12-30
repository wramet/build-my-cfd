# 3. Container System

ระบบ Container ใน OpenFOAM — List, Field, HashTable และอื่นๆ

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:

- **เลือก** container type ที่เหมาะสมสำหรับ use case ที่แตกต่างกัน
- **อธิบาย** ความแตกต่างระหว่าง `Field<T>`, `List<T>`, `DynamicList<T>`, และ `FixedList<T,N>`
- **ใช้งาน** `forAll` macro และ `SubList<T>` อย่างมีประสิทธิภาพ
- **ประยุกต์** HashTable สำหรับ key-value storage ใน OpenFOAM
- **เปรียบเทียบ** performance trade-offs ระหว่าง container types

---

## Quick Reference: Container Types

| Container | When to Use | Memory | Performance | Key Features |
|-----------|-------------|--------|-------------|--------------|
| `List<T>` | Fixed-size array | Contiguous | High | Random access, `first()`, `last()`, `resize()` |
| `DynamicList<T>` | Growing/shrinking | Contiguous + growth space | Medium (reallocation) | `append()`, `reserve()`, automatic growth |
| `FixedList<T,N>` | Compile-time size | Static (stack) | Very High | No allocation, fixed N known at compile time |
| `Field<T>` | CFD data arrays | Contiguous | High (optimized) | `max()`, `sum()`, `average()`, `mag()`, component-wise ops |
| `HashTable<K,T>` | Key-value lookup | Hash buckets | O(1) average | `insert()`, `found()`, string keys, word/string hashing |
| `SubList<T>` | View into container | Zero (view) | High | No copy, slice notation, reference semantics |

---

## 1. List Types

### 1.1 List\<T> — Fixed-Size Array

**What**: Dynamic array with contiguous memory storage that can be resized at runtime.

**Why Use It**:
- General-purpose container for most array operations
- Efficient random access and iteration
- Memory-efficient when size is known upfront

**How to Use**:

```cpp
// Construction
List<scalar> values(100, 0.0);           // 100 elements, initialized to 0.0
List<vector> points(10);                  // 10 default-constructed vectors
List<label> empty;                        // Empty list

// Element access
values[0] = 1.0;
scalar first = values.first();            // First element
scalar last = values.last();              // Last element
vector& p = points[5];                    // Reference to element

// Size manipulation
label n = values.size();                  // Current size
values.resize(200);                       // Resize (preserves existing data)
values.setSize(150);                      // Set size (may truncate)
values.clear();                           // Remove all elements

// Transfer (move semantics)
List<scalar> moved = std::move(values);   // Efficient transfer
```

**Common Operations**:

```cpp
// Shallow copy (reference to same data)
List<scalar> ref(values);                 // Shares data

// Deep copy
List<scalar> copy;
copy = values;                            // Independent copy

// Sorting
sort(values);                             // Ascending
sort(values, std::greater<scalar>());     // Descending

// Statistical operations
scalar sumVal = sum(values);              // Requires <Field.hxx>
```

---

### 1.2 DynamicList\<T> — Growable Array

**What**: List with automatic capacity management for efficient append operations.

**Why Use It**:
- Number of elements unknown at initialization
- Frequent append operations (amortized O(1))
- Avoids repeated allocations when growing

**How to Use**:

```cpp
// Construction
DynamicList<label> indices;               // Empty list
DynamicList<scalar> data(100);            // Capacity hint

// Element addition
indices.append(5);
indices.append(10);
indices += 15;                            // Operator+=
data.push_back(3.14);                     // STL-style

// Capacity management
data.reserve(1000);                       // Pre-allocate space
label cap = data.capacity();              // Current capacity
data.setCapacity(2000);                   // Set exact capacity

// Size operations
indices.setSize(50, 0);                   // Resize with fill value
indices.shrink();                         // Free unused capacity

// Element access (same as List)
label first = indices[0];
label last = indices.last();

// Transfer to List
List<label> staticList = indices;         // Efficient transfer
```

**Performance Considerations**:

```cpp
// BAD: Repeated resize
DynamicList<label> bad;
for (label i = 0; i < 10000; i++) {
    bad.append(i);                        // Multiple reallocations
}

// GOOD: Pre-allocate
DynamicList<label> good;
good.reserve(10000);
for (label i = 0; i < 10000; i++) {
    good.append(i);                       // Single allocation
}
```

---

### 1.3 FixedList\<T, N> — Compile-Time Fixed Array

**What**: Array with size known at compile time, typically stored on stack.

**Why Use It**:
- Size is fixed and known at compile time (e.g., 3D vectors)
- Maximum performance (no heap allocation)
- Ideal for small, fixed-size data (RGB, dimensions)

**How to Use**:

```cpp
// Construction
FixedList<scalar, 3> rgb;                 // Uninitialized
FixedList<label, 4> counts{0, 1, 2, 3};   // Initializer list
FixedList<vector, 2> vecs(vector::zero);  // Uniform initialization

// Element access
rgb[0] = 1.0;                             // Red
rgb[1] = 0.5;                             // Green
rgb[2] = 0.0;                             // Blue

// Bounds-checked access
scalar r = rgb[0];                        // No bounds check
scalar g = rgb.at(1);                     // Bounds checked

// Size (compile-time constant)
constexpr label n = rgb.size();           // Always 3

// Operations
rgb = ZERO;                               // Set all to zero
std::fill(rgb.begin(), rgb.end(), 1.0);   // STL algorithms work

// Comparison
FixedList<scalar, 3> rgb2 = rgb;
if (rgb == rgb2) { ... }                  // Element-wise comparison
```

**Common Use Cases**:

```cpp
// Vector components (velocity, position)
FixedList<scalar, 3> velocity;             // [u, v, w]
FixedList<scalar, 3> position;             // [x, y, z]

// Tensor indices
FixedList<label, 6> symTensorIndices;      // xx, xy, xz, yy, yz, zz

// Boundary conditions at faces
FixedList<scalar, 4> patchValues;          // Fixed-size patch data
```

---

## 2. HashTable\<K, T>

**What**: Associative container using hash table for O(1) average lookup.

**Why Use It**:
- Dictionary-like storage (string keys → values)
- Property dictionaries and transport properties
- Fast lookups by name/word

**How to Use**:

```cpp
// Construction
HashTable<scalar, word> props;            // word keys (preferred)
HashTable<vector, string> vecTable;       // string keys
HashTable<label, label> idMap;            // label keys

// Insertion
props.insert("density", 1000);
props.set("viscosity", 1e-6);             // set() replaces if exists
props["pressure"] = 101325;               // Operator[] (creates if not exists)

// Lookup
scalar rho = props["density"];            // Creates entry if missing
if (props.found("temperature")) {         // Check existence
    scalar T = props.lookup("temperature"); // Throws if not found
}

// Removal
props.erase("viscosity");
props.clear();                            // Remove all

// Iteration
forAllIter(HashTable<scalar, word>, props, iter) {
    Info << iter.key() << ": " << iter.val() << endl;
}

// Const iteration
forAllConstIters(HashTable<scalar, word>, props, iter) {
    Info << iter.key() << ": " << iter() << endl;
}

// Size operations
label n = props.size();
bool empty = props.empty();
```

**Practical Example: Property Dictionary**:

```cpp
// Transport properties lookup
HashTable<scalar, word> transportProps;

// Read from dictionary
transportProps.insert("nu", 1e-6);        // Kinematic viscosity
transportProps.insert("rho", 1000);       // Density
transportProps.insert("Pr", 0.7);         // Prandtl number

// Usage in solver
scalar nu = transportProps["nu"];
scalar rho = transportProps["rho"];
scalar alpha = nu / transportProps["Pr"]; // Thermal diffusivity
```

---

## 3. Field\<T>

**What**: Specialized `List<T>` with CFD-specific mathematical operations and optimizations.

**Why Use It**:
- Field data (pressure, velocity, temperature)
- Element-wise operations without loops
- Parallel-aware operations for MPI
- Integrated with mesh (internalField, boundaryField)

**How to Use**:

```cpp
// Construction
scalarField p(1000, 101325);               // 1000 cells, initial value
vectorField U(1000, vector::zero);         // Zero velocity field
tensorField tau(500);                      // Empty tensor field

// Element-wise math operations
scalarField T2 = sqr(T);                   // T² element-wise
scalarField invT = 1.0 / T;                // Reciprocal
vectorField doubleU = 2.0 * U;             // Scalar multiplication

// Reduction operations (parallel-aware)
scalar maxT = max(T);                      // Maximum value
scalar minT = min(T);                      // Minimum value
scalar avgT = average(T);                  // Arithmetic mean
scalar sumT = sum(T);                      // Sum of all elements

// Vector operations
scalarField magU = mag(U);                 // Magnitude |U|
vectorField normalized = U / (mag(U) + SMALL); // Unit vectors
scalarField Ux = U.component(0);          // x-component

// Field algebra
scalarField rhoU = rho * U.component(0);  // Density * u-velocity
scalarField T_diff = T - Tambient;        // Temperature difference

// Boundary handling
scalarField internal = T.internalField(); // Get internal field
scalarField& boundary = T.boundaryField()[patchID]; // Reference to patch
```

**Practical CFD Operations**:

```cpp
// Compute cell volumes (example)
scalarField cellVolumes(mesh.nCells());
forAll(cellVolumes, i) {
    cellVolumes[i] = mesh.V()[i];
}

// Interpolate to faces
surfaceScalarField facePhi = fvc::interpolate(phi);

// Apply boundary conditions
U.correctBoundaryConditions();             // Update patch values based on BCs

// Field statistics
scalar totalMass = sum(rho * mesh.V());    // Mass = Σ(ρᵢ × Vᵢ)
scalar maxVelocity = max(mag(U)).value();  // Maximum velocity magnitude
```

---

## 4. forAll Macro

**What**: OpenFOAM iteration macro for cleaner, more consistent loop syntax.

**Why Use It**:
- **Consistency**: Standard style throughout OpenFOAM code
- **Clarity**: Makes iteration intent explicit
- **Safety**: Less error-prone than manual index loops
- **Concise**: Reduces boilerplate code

**How to Use**:

```cpp
scalarField field(100);

// Forward iteration
forAll(field, i) {
    field[i] = i * 1.5;
}

// Reverse iteration
forAllReverse(field, i) {
    field[i] *= 2.0;
}

// Multiple fields (same size)
scalarField T(100);
vectorField U(100);
forAll(T, i) {
    T[i] = 300;
    U[i] = vector::zero;
}

// Equivalent standard loops
for (label i = 0; i < field.size(); i++) { ... }
for (label i = field.size() - 1; i >= 0; i--) { ... }
```

**Iterator Macros**:

```cpp
// Non-const iterator
forAllIter(List<scalar>, values, iter) {
    *iter = 0.0;                           // Modify
}

// Const iterator
forAllConstIters(List<scalar>, values, iter) {
    Info << *iter << endl;                 // Read only
}

// HashTable iteration
HashTable<scalar, word> props;
forAllConstIters(HashTable<scalar, word>, props, iter) {
    Info << iter.key() << ": " << iter() << endl;
}
```

---

## 5. SubList\<T> and SubField\<T>

**What**: View into existing container without copying data (reference semantics).

**Why Use It**:
- **Memory efficiency**: No data duplication
- **Performance**: Zero-copy slicing
- **Convenience**: Work with portions of arrays
- **Safety**: Maintains reference to original data

**How to Use**:

```cpp
// Original data
List<scalar> fullData(100);
forAll(fullData, i) {
    fullData[i] = i * 1.0;
}

// SubList: View into List
SubList<scalar> middle(fullData, 20, 40);  // 20 elements starting at index 40
SubList<scalar> firstHalf(fullData, 50);   // First 50 elements (starts at 0)

// SubField: View into Field
scalarField temperature(1000, 300.0);
SubField<scalar> coreRegion(temperature, 500);  // First 500 cells
SubField<scalar> boundaryZone(temperature, 100, 900); // Last 100 cells

// Element access (no copy)
scalar val = middle[0];                    // Accesses fullData[40]
middle[5] = 999.0;                         // Modifies fullData[45]

// Size operations
label n = middle.size();                   // 20

// Conversion to List (creates copy)
List<scalar> copy = middle;                // Now independent
```

**Practical Use Cases**:

```cpp
// 1. Boundary field operations
scalarField internalField(mesh.nCells());
scalarField& patchField = boundaryField[patchID];
SubField<scalar> boundaryView(patchField, patchSize);

// Compute boundary average without copy
scalar patchAvg = average(boundaryView);

// 2. Multi-zone processing
scalarField allCells(mesh.nCells());
labelList zone1Cells = ...;                // Cell indices for zone 1
labelList zone2Cells = ...;                // Cell indices for zone 2

// Process zones without creating new arrays
forAll(zone1Cells, i) {
    label cellI = zone1Cells[i];
    allCells[cellI] = ...;                 // Zone 1 operation
}

// 3. Parallel decomposition
scalarField globalField(10000);
label nProc = Pstream::nProcs();
label mySize = globalField.size() / nProc;
label start = Pstream::myProcNo() * mySize;

SubField<scalar> myPortion(globalField, mySize, start);
```

**SubList vs Copy**:

```cpp
// SubList: Zero-copy reference
SubList<scalar> view(original, 100);
view[0] = 5.0;                             // Modifies original

// Copy: Independent data
List<scalar> copy = original(0, 100);      // Creates copy
copy[0] = 5.0;                             // Does NOT modify original
```

---

## 6. Sorting and Searching

**What**: Algorithms for ordering and finding elements in containers.

**How to Use**:

```cpp
List<scalar> values = {3.0, 1.0, 4.0, 1.5, 2.0};

// In-place sorting
sort(values);                              // Ascending: {1.0, 1.5, 2.0, 3.0, 4.0}
sort(values, std::greater<scalar>());      // Descending

// Stable sort (preserves order of equal elements)
stableSort(values);

// Sort with index tracking
labelList order;
sortedOrder(values, order);                // order = {1, 3, 4, 0, 2}
// Apply ordering
List<scalar> sortedValues(values, order);  // Create reordered list

// Binary search (requires sorted input)
label idx = findLower(values, 2.0);        // First position where values[idx] >= 2.0

// Linear search
label pos = findIndex(values, 1.5);        // Returns index of 1.5 (or -1 if not found)
List<label> indices = findIndices(values, 1.0);  // All indices matching 1.0
```

---

## 7. Best Practices

### 7.1 Choosing the Right Container

```
Use FixedList<T,N> when:
  └─ Size is known at compile time
  └─ Performance is critical (no allocation)
  └─ Small data (vectors, dimensions)

Use List<T> when:
  └─ Size is known at runtime
  └─ Number of elements is stable
  └─ General-purpose array needed

Use DynamicList<T> when:
  └─ Size is unknown
  └─ Frequent append operations
  └─ Building list incrementally

Use Field<T> when:
  └─ CFD field data (pressure, velocity, temperature)
  └─ Mathematical operations needed (max, sum, average)
  └─ Parallel operations required

Use HashTable when:
  └─ Key-value storage needed
  └─ String/word keys (properties, dictionaries)
  └─ Fast lookup by name required

Use SubList<T> when:
  └─ Working with portion of data
  └─ Memory efficiency critical
  └─ Temporary view sufficient
```

### 7.2 Performance Tips

```cpp
// 1. Pre-allocate when size is known
DynamicList<label> list;
list.reserve(1000);                        // Avoid reallocations

// 2. Use references to avoid copies
void processList(const List<scalar>& list); // Reference, not value

// 3. Use SubList for views (not copies)
SubList<scalar> view(original, size);      // Not: List<scalar> copy = ...;

// 4. Move instead of copy when possible
List<scalar> target = std::move(source);   // Transfer ownership

// 5. Use Field operations instead of loops
scalar avgT = average(T);                  // Not: manual sum/size loop

// 6. Prefer forAll over manual loops
forAll(field, i) { ... }                   // Clearer intent
```

### 7.3 Common Pitfalls

```cpp
// 1. Unintended shallow copy
List<scalar> a(100, 1.0);
List<scalar> b = a;                        // Shares data!
b[0] = 999.0;                              // Also modifies a[0]

// Solution: Use explicit copy or transfer
List<scalar> c;
c = a;                                     // Deep copy

// 2. HashTable operator[] auto-creates
HashTable<scalar, word> table;
scalar val = table["missing"];             // Creates entry with default value!

// Solution: Use found() + lookup()
if (table.found("density")) {
    scalar val = table.lookup("density");  // Safe
}

// 3. SubList lifetime dependency
SubList<scalar> dangerous = getTemporaryView();
// If original data is destroyed, dangerous becomes invalid!

// 4. Forgotten reserve()
DynamicList<label> slow;
for (label i = 0; i < 10000; i++) {
    slow.append(i);                        // Multiple reallocations
}

// Solution: Pre-allocate
DynamicList<label> fast;
fast.reserve(10000);
```

---

## Key Takeaways

### Container Selection Guide
- **FixedList<T,N>**: Compile-time size, maximum performance
- **List<T>**: Runtime size, general-purpose arrays
- **DynamicList<T>**: Growing lists, append-heavy operations
- **Field<T>**: CFD data with mathematical operations
- **HashTable<K,T>**: Key-value storage, O(1) lookups
- **SubList<T>**: Zero-copy views into existing data

### Essential Operations
- **Iteration**: `forAll(container, i)` for forward, `forAllReverse` for backward
- **Views**: `SubList<T>(parent, size, start)` for zero-copy slicing
- **Sorting**: `sort()`, `stableSort()`, `sortedOrder()` for ordering
- **Field math**: `max()`, `min()`, `average()`, `sum()`, `mag()` for CFD operations

### Performance Principles
- Pre-allocate `DynamicList` with `reserve()` when size is predictable
- Use `SubList` instead of copying for temporary views
- Prefer `Field<T>` operations over manual loops for reduction operations
- Use `forAll` macro for consistent, readable iteration code
- Leverage move semantics (`std::move`) for efficient container transfers

### Memory Management
- `List<T>` assignment creates shallow copies (shared data)
- HashTable `operator[]` auto-creates entries; use `found()` + `lookup()` for safe access
- `SubList` is a view, not an owner—lifetime depends on parent container
- `FixedList` typically stack-allocated; others use heap allocation

---

## 📚 Related Documentation

### Within This Module
- **Memory Management**: [02_Memory_Management_Fundamentals.md](02_Memory_Management_Fundamentals.md) — Deep dive into reference counting, allocation patterns
- **Integration**: [04_Integration_and_Best_Practices.md](04_Integration_and_Best_Practices.md) — Using containers in OpenFOAM applications

### Cross-Module References
- **Field Operations**: [MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md](../../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md) — Field manipulation in solvers
- **Mesh Data**: [MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/01_MESHING_FUNDAMENTALS/02_OpenFOAM_Mesh_Structure.md](../../../MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/01_MESHING_FUNDAMENTALS/02_OpenFOAM_Mesh_Structure.md) — Mesh field storage

---

## 🧪 Concept Check

<details>
<summary><b>1. ควรใช้ container แบบไหนสำหรับ (a) 3D velocity vector, (b) รายการ cell indices ที่เพิ่มขึ้นเรื่อยๆ, (c) temperature field ที่ต้องคำนวณ average?</b></summary>

**a) FixedList<scalar, 3>** — ขนาดรู้ตั้งแต่ compile-time (x, y, z)  
**b) DynamicList<label>** — ขนาดไม่แน่นอน มีการ append เรื่อยๆ  
**c) scalarField** — ต้องใช้ average() operation และเป็น CFD data
</details>

<details>
<summary><b>2. SubList และการ copy List ต่างกันอย่างไร และเมื่อไหร่ควรใช้แบบไหน?</b></summary>

**SubList**: View ที่ไม่ copy data — ใช้เมื่อต้องการอ่าน/เขียนชั่วคราว ประหยัด memory  
**Copy**: สร้าง List ใหม่ที่เป็นอิสระ — ใช้เมื่อต้องการ data ที่แยกจาก original
</details>

<details>
<summary><b>3. ทำไม forAll(field, i) ถึงดีกว่า for (label i=0; i<field.size(); i++)?</b></summary>

**Consistency**: เป็น standard style ใน OpenFOAM ทั้งหมด  
**Clarity**: แสดง intent ชัดเจน (iterate over container)  
**Concise**: เขียนสั้นกว่า ลดโอกาส error จาก typing ผิด
</details>

<details>
<summary><b>4. ถ้าต้องการ lookup transport properties ด้วย string key ควรใช้ container แบบไหน?</b></summary>

**HashTable<scalar, word>** — รองรับ string/word keys, lookup O(1), ใช้ได้กับ insert(), found(), lookup() สำหรับ dictionary-like operations
</details>