# MODULE_05 Section 03: Mesh Database (Mesh Topology with Clean API)
# ฐานข้อมูลเมช (โทโพโลยีเมชด้วย Clean API)

## 1. Overview - Why Mesh Database Architecture Matters in CFD
## 1. ภาพรวม - ทำไมสถาปัตยกรรมฐานข้อมูลเมชจึงสำคัญใน CFD

In Computational Fluid Dynamics (CFD), the mesh database is the **foundational data structure** that represents the computational domain. A well-designed mesh architecture directly impacts:

ในพลศาสตร์ของไหลเชิงคำนวณ (CFD) ฐานข้อมูลเมชคือ **โครงสร้างข้อมูลพื้นฐาน** ที่แสดงโดเมนการคำนวณ การออกแบบสถาปัตยกรรมเมชที่ดีส่งผลกระทบโดยตรงต่อ:

1. **Performance** - Efficient memory layout and cache utilization
2. **Scalability** - Parallel computation and load balancing
3. **Maintainability** - Clean API for algorithm development
4. **Accuracy** - Proper geometric representation and connectivity

1. **ประสิทธิภาพ** - การจัดเรียงหน่วยความจำและการใช้แคชอย่างมีประสิทธิภาพ
2. **ความสามารถในการขยาย** - การคำนวณแบบขนานและการกระจายโหลด
3. **ความสามารถในการบำรุงรักษา** - API ที่สะอาดสำหรับการพัฒนาอัลกอริทึม
4. **ความแม่นยำ** - การแสดงรูปทรงเรขาคณิตและการเชื่อมต่อที่เหมาะสม

The mesh topology defines how cells, faces, and vertices connect, forming the **graph structure** upon which discretization operators (gradient, divergence, Laplacian) are built. For R410A evaporator simulation, proper cylindrical mesh representation is critical for capturing phase change phenomena accurately.

โทโพโลยีเมชกำหนดวิธีการเชื่อมต่อเซลล์ หน้า และจุดยอด ก่อให้เกิด **โครงสร้างกราฟ** ที่ตัวดำเนินการแยกส่วน (เกรเดียนต์ ไดเวอร์เจนซ์ ลาปลาเชียน) ถูกสร้างขึ้น สำหรับการจำลองการระเหยของ R410A การแสดงเมชทรงกระบอกที่เหมาะสมมีความสำคัญต่อการจับปรากฏการณ์การเปลี่ยนเฟสอย่างแม่นยำ

## 2. OpenFOAM Approach - polyMesh, primitiveMesh, meshObject Hierarchy
## 2. วิธีการของ OpenFOAM - polyMesh, primitiveMesh, meshObject Hierarchy

### 2.1 OpenFOAM Mesh Class Hierarchy
### 2.1 ลำดับชั้นคลาสเมชของ OpenFOAM

```
objectRegistry
├── polyMesh (core mesh class)
│   ├── primitiveMesh (connectivity data)
│   ├── boundaryMesh (boundary patches)
│   └── meshObjectRegistry (attached objects)
```

**File References:**
- `src/OpenFOAM/meshes/polyMesh/polyMesh.H`
- `src/OpenFOAM/meshes/primitiveMesh/primitiveMesh.H`
- `src/OpenFOAM/meshes/MeshObject/MeshObject.H`

### 2.2 Core Mesh Components
### 2.2 ส่วนประกอบหลักของเมช

```cpp
// OpenFOAM mesh data structures
class polyMesh : public objectRegistry {
    // Points (vertices)
    pointField points_;

    // Faces (connectivity)
    faceList faces_;

    // Owner-neighbor addressing
    labelList owner_;
    labelList neighbour_;

    // Boundary patches
    PtrList<polyPatch> boundaries_;

    // Cell shapes (tet, hex, prism, etc.)
    cellShapeList cellShapes_;
};
```

**Mathematical Representation:**
- Cell volume: $V_{cell} = \int_V dV$
- Face area vector: $\vec{S}_f = \int_{face} \vec{n} dS$
- Face center: $\vec{x}_f = \frac{1}{S_f} \int_{face} \vec{x} dS$

**การแสดงทางคณิตศาสตร์:**
- ปริมาตรเซลล์: $V_{cell} = \int_V dV$
- เวกเตอร์พื้นที่หน้า: $\vec{S}_f = \int_{face} \vec{n} dS$
- จุดศูนย์กลางหน้า: $\vec{x}_f = \frac{1}{S_f} \int_{face} \vec{x} dS$

### 2.3 Owner-Neighbor Addressing
### 2.3 การกำหนดเจ้าของ-เพื่อนบ้าน

In OpenFOAM, each face has:
- **Owner cell**: Lower numbered cell
- **Neighbor cell**: Higher numbered cell (internal faces only)
- **Boundary faces**: Only owner cell exists

ใน OpenFOAM แต่ละหน้ามี:
- **เซลล์เจ้าของ**: เซลล์ที่มีหมายเลขต่ำกว่า
- **เซลล์เพื่อนบ้าน**: เซลล์ที่มีหมายเลขสูงกว่า (เฉพาะหน้าภายใน)
- **หน้าขอบเขต**: มีเฉพาะเซลล์เจ้าของเท่านั้น

```cpp
// OpenFOAM addressing example
forAll(mesh.faces(), faceI) {
    label own = mesh.faceOwner()[faceI];  // Always exists
    label nei = -1;  // Initialize as boundary

    if (mesh.isInternalFace(faceI)) {
        nei = mesh.faceNeighbour()[faceI];  // Internal face
    }
}
```

## 3. Modern C++ Approach - Clean API, RAII, Modern Containers
## 3. วิธีการของ Modern C++ - Clean API, RAII, คอนเทนเนอร์สมัยใหม่

### 3.1 Modern Mesh Class Design
### 3.1 การออกแบบคลาสเมชสมัยใหม่

```cpp
// Modern C++ Mesh class with clean API
class Mesh {
private:
    // Core data members using modern containers
    std::vector<Point3D> points_;
    std::vector<Face> faces_;
    std::vector<Cell> cells_;

    // Owner-neighbor addressing
    std::vector<size_t> faceOwner_;
    std::vector<std::optional<size_t>> faceNeighbor_;

    // Boundary patches
    std::vector<BoundaryPatch> boundaries_;

    // RAII-managed resources
    std::unique_ptr<MeshSearcher> searcher_;
    std::shared_ptr<MeshMetrics> metrics_;

public:
    // Clean API with const-correctness
    [[nodiscard]] const std::vector<Point3D>& points() const noexcept {
        return points_;
    }

    [[nodiscard]] const std::vector<Face>& faces() const noexcept {
        return faces_;
    }

    [[nodiscard]] size_t faceOwner(size_t faceIdx) const {
        if (faceIdx >= faceOwner_.size()) {
            throw std::out_of_range("Face index out of range");
        }
        return faceOwner_[faceIdx];
    }

    [[nodiscard]] std::optional<size_t> faceNeighbor(size_t faceIdx) const {
        if (faceIdx >= faceNeighbor_.size()) {
            throw std::out_of_range("Face index out of range");
        }
        return faceNeighbor_[faceIdx];
    }

    // RAII constructor
    explicit Mesh(std::vector<Point3D> points,
                  std::vector<Face> faces,
                  std::vector<size_t> owner);

    // Rule of Five
    ~Mesh() = default;
    Mesh(const Mesh&) = delete;
    Mesh& operator=(const Mesh&) = delete;
    Mesh(Mesh&&) noexcept = default;
    Mesh& operator=(Mesh&&) noexcept = default;
};
```

### 3.2 Supporting Data Structures
### 3.2 โครงสร้างข้อมูลสนับสนุน

```cpp
// Modern C++ geometric primitives
struct Point3D {
    double x, y, z;

    // Vector operations
    [[nodiscard]] double magnitude() const noexcept {
        return std::sqrt(x*x + y*y + z*z);
    }

    // Operator overloads
    Point3D operator+(const Point3D& other) const noexcept {
        return {x + other.x, y + other.y, z + other.z};
    }

    Point3D operator-(const Point3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }
};

class Face {
private:
    std::vector<size_t> pointIndices_;  // Vertex indices
    Point3D center_;                    // Face center
    Point3D normal_;                    // Unit normal
    double area_;                       // Face area

public:
    // Const accessors
    [[nodiscard]] const std::vector<size_t>& vertices() const noexcept {
        return pointIndices_;
    }

    [[nodiscard]] const Point3D& center() const noexcept { return center_; }
    [[nodiscard]] const Point3D& normal() const noexcept { return normal_; }
    [[nodiscard]] double area() const noexcept { return area_; }

    // Calculate geometric properties
    void computeGeometry(const std::vector<Point3D>& points);
};

class Cell {
private:
    std::vector<size_t> faceIndices_;  // Face indices
    Point3D center_;                   // Cell center
    double volume_;                    // Cell volume

public:
    [[nodiscard]] const std::vector<size_t>& faces() const noexcept {
        return faceIndices_;
    }

    [[nodiscard]] const Point3D& center() const noexcept { return center_; }
    [[nodiscard]] double volume() const noexcept { return volume_; }
};
```

## 4. Code Comparison - Side-by-Side Examples
## 4. การเปรียบเทียบโค้ด - ตัวอย่างแบบคู่ขนาน

### 4.1 Mesh Access Patterns
### 4.1 รูปแบบการเข้าถึงเมช

```cpp
// ========== OpenFOAM Style ==========
// File: src/OpenFOAM/meshes/polyMesh/polyMesh.H

// Access mesh components
const pointField& points = mesh.points();      // Returns reference
const faceList& faces = mesh.faces();          // Returns reference
const labelList& owner = mesh.faceOwner();     // Returns reference

// Face iteration
forAll(mesh.faces(), faceI) {
    const face& f = faces[faceI];
    label cellI = owner[faceI];

    // Access face vertices
    forAll(f, pointI) {
        const point& p = points[f[pointI]];
        // Process point...
    }
}

// ========== Modern C++ Style ==========
// File: R410A_CFD/include/mesh/Mesh.hpp

// Access mesh components (const-correct)
const auto& points = mesh.points();           // Returns const reference
const auto& faces = mesh.faces();             // Returns const reference

// Face iteration with range-based for
for (size_t faceIdx = 0; faceIdx < mesh.numFaces(); ++faceIdx) {
    const auto& face = mesh.faces()[faceIdx];
    size_t cellIdx = mesh.faceOwner(faceIdx);  // Value, not reference

    // Access face vertices (modern iteration)
    for (size_t vertexIdx : face.vertices()) {
        const auto& point = points[vertexIdx];
        // Process point with modern C++ features...
    }
}
```

### 4.2 Boundary Face Processing
### 4.2 การประมวลผลหน้าขอบเขต

```cpp
// ========== OpenFOAM Style ==========
// File: applications/solvers/basic/icoFoam/icoFoam.C

// Boundary face loop
forAll(mesh.boundary(), patchI) {
    const polyPatch& pp = mesh.boundary()[patchI];

    if (pp.coupled()) {
        // Coupled patch (processor, cyclic)
        forAll(pp, faceI) {
            label meshFaceI = pp.start() + faceI;
            // Process coupled face...
        }
    } else {
        // Regular boundary patch
        forAll(pp, faceI) {
            label meshFaceI = pp.start() + faceI;
            label cellI = mesh.faceOwner()[meshFaceI];
            // Process boundary face...
        }
    }
}

// ========== Modern C++ Style ==========
// File: R410A_CFD/src/mesh/BoundaryProcessor.cpp

// Boundary face processing with modern C++
for (const auto& patch : mesh.boundaries()) {
    if (patch.isCoupled()) {
        // Coupled patch - use parallel communication
        for (size_t localFaceIdx = 0; localFaceIdx < patch.size(); ++localFaceIdx) {
            size_t globalFaceIdx = patch.start() + localFaceIdx;
            // Process with async operations...
        }
    } else {
        // Regular boundary - use SIMD where possible
        #pragma omp simd
        for (size_t localFaceIdx = 0; localFaceIdx < patch.size(); ++localFaceIdx) {
            size_t globalFaceIdx = patch.start() + localFaceIdx;
            size_t cellIdx = mesh.faceOwner(globalFaceIdx);

            // Process with modern algorithms
            auto faceData = processBoundaryFace(globalFaceIdx, cellIdx);
            applyBoundaryCondition(patch.type(), faceData);
        }
    }
}
```

### 4.3 Geometric Calculations
### 4.3 การคำนวณทางเรขาคณิต

```cpp
// ========== OpenFOAM Style ==========
// File: src/OpenFOAM/meshes/primitiveMesh/primitiveMeshFaceCentresAndAreas.C

// Face area calculation
vector primitiveMesh::faceArea(const label faceI) const {
    const face& f = faces_[faceI];

    // Using Newell's method
    vector n = vector::zero;
    const point& p0 = points_[f[0]];

    forAll(f, pointI) {
        const point& p1 = points_[f[pointI]];
        const point& p2 = points_[f.nextLabel(pointI)];

        n.x() += (p1.y() - p0.y()) * (p2.z() - p0.z())
               - (p1.z() - p0.z()) * (p2.y() - p0.y());
        // Similar for y and z components...
    }

    return 0.5 * n;
}

// ========== Modern C++ Style ==========
// File: R410A_CFD/src/geometry/FaceGeometry.cpp

// Face area calculation with modern C++
std::pair<Point3D, double> Face::computeAreaAndNormal(
    const std::vector<Point3D>& points) const {

    if (pointIndices_.size() < 3) {
        throw std::invalid_argument("Face must have at least 3 vertices");
    }

    Point3D normal{0.0, 0.0, 0.0};
    const auto& p0 = points[pointIndices_[0]];

    // Newell's method with modern C++ features
    for (size_t i = 0; i < pointIndices_.size(); ++i) {
        size_t j = (i + 1) % pointIndices_.size();
        const auto& p1 = points[pointIndices_[i]];
        const auto& p2 = points[pointIndices_[j]];

        normal.x += (p1.y - p0.y) * (p2.z - p0.z)
                  - (p1.z - p0.z) * (p2.y - p0.y);
        normal.y += (p1.z - p0.z) * (p2.x - p0.x)
                  - (p1.x - p0.x) * (p2.z - p0.z);
        normal.z += (p1.x - p0.x) * (p2.y - p0.y)
                  - (p1.y - p0.y) * (p2.x - p0.x);
    }

    double area = 0.5 * normal.magnitude();
    Point3D unitNormal = normal * (1.0 / (2.0 * area + 1e-16));

    return {unitNormal, area};
}
```

## 5. R410A Context - Cylindrical Tube Mesh for Evaporator
## 5. บริบท R410A - เมชท่อทรงกระบอกสำหรับเครื่องระเหย

### 5.1 Cylindrical Mesh Generation
### 5.1 การสร้างเมชทรงกระบอก

For R410A evaporator simulation, we need specialized mesh generation:

สำหรับการจำลองการระเหย R410A เราต้องการการสร้างเมชแบบพิเศษ:

```cpp
// R410A evaporator tube mesh generator
class CylindricalTubeMesh : public Mesh {
private:
    // Tube parameters
    double radius_;
    double length_;
    double wallThickness_;

    // Mesh parameters
    size_t radialLayers_;      // O-grid layers
    size_t axialCells_;        // Structured axial cells
    size_t circumferentialCells_;  // θ-direction cells

public:
    CylindricalTubeMesh(double radius, double length,
                       size_t radialLayers, size_t axialCells,
                       size_t thetaCells);

    void generateOMesh();
    void addBoundaryLayer(double firstLayerThickness, double growthRatio);

    // Coordinate transformations
    [[nodiscard]] Point3D cylindricalToCartesian(double r, double z, double theta) const {
        return {
            r * std::cos(theta),
            r * std::sin(theta),
            z
        };
    }

    [[nodiscard]] std::tuple<double, double, double>
    cartesianToCylindrical(const Point3D& p) const {
        double r = std::sqrt(p.x * p.x + p.y * p.y);
        double theta = std::atan2(p.y, p.x);
        return {r, p.z, theta};
    }
};
```

### 5.2 O-Grid Mesh Structure
### 5.2 โครงสร้างเมช O-Grid

The O-grid structure provides:
1. **Orthogonal cells** near walls for boundary layer resolution
2. **Smooth transition** from wall to core region
3. **Reduced skewness** compared to pure structured grids

โครงสร้าง O-grid ให้:
1. **เซลล์ตั้งฉาก** ใกล้ผนังสำหรับความละเอียดชั้นขอบเขต
2. **การเปลี่ยนผ่านอย่างราบรื่น** จากผนังสู่บริเวณแกนกลาง
3. **ความเบ้ลดลง** เมื่อเทียบกับกริดโครงสร้างล้วน

```cpp
void CylindricalTubeMesh::generateOMesh() {
    std::vector<Point3D> points;
    std::vector<Face> faces;
    std::vector<size_t> owner;

    // Generate points in cylindrical coordinates
    double dr = radius_ / radialLayers_;
    double dz = length_ / axialCells_;
    double dtheta = 2.0 * M_PI / circumferentialCells_;

    // O-grid point generation
    for (size_t i = 0; i <= radialLayers_; ++i) {
        double r = i * dr;
        for (size_t j = 0; j <= axialCells_; ++j) {
            double z = j * dz;
            for (size_t k = 0; k <= circumferentialCells_; ++k) {
                double theta = k * dtheta;

                // Transform to Cartesian
                points.push_back(cylindricalToCartesian(r, z, theta));
            }
        }
    }

    // Create hexahedral cells (structured O-grid)
    for (size_t i = 0; i < radialLayers_; ++i) {
        for (size_t j = 0; j < axialCells_; ++j) {
            for (size_t k = 0; k < circumferentialCells_; ++k) {
                // Calculate point indices for hex cell
                std::array<size_t, 8> cellPoints = {
                    // Bottom face (z = j)
                    i * (axialCells_ + 1) * (circumferentialCells_ + 1)
                    + j * (circumferentialCells_ + 1) + k,
                    // ... calculate all 8 vertices
                };

                // Create 6 faces for hex cell
                createHexCell(cellPoints, faces, owner);
            }
        }
    }

    // Initialize mesh with generated data
    initialize(std::move(points), std::move(faces), std::move(owner));
}
```

### 5.3 Boundary Layer Mesh
### 5.3 เมชชั้นขอบเขต

```cpp
void CylindricalTubeMesh::addBoundaryLayer(
    double firstLayerThickness, double growthRatio) {

    // Redistribute radial points for boundary layer
    std::vector<double> radialPositions(radialLayers_ + 1);

    // Geometric progression for boundary layer
    double totalBLThickness = firstLayerThickness *
        (std::pow(growthRatio, radialLayers_) - 1.0) /
        (growthRatio - 1.0);

    // Scale factor to fit within tube radius
    double scale = radius_ / totalBLThickness;

    // Generate boundary layer distribution
    double cumulativeThickness = 0.0;
    for (size_t i = 0; i <= radialLayers_; ++i) {
        if (i == 0) {
            radialPositions[i] = 0.0;
        } else {
            cumulativeThickness += firstLayerThickness *
                std::pow(growthRatio, i - 1);
            radialPositions[i] = cumulativeThickness * scale;
        }
    }

    // Regenerate mesh with new radial distribution
    regenerateWithRadialDistribution(radialPositions);
}
```

### 5.4 Mesh Quality Metrics for R410A Evaporator
### 5.4 เมตริกคุณภาพเมชสำหรับเครื่องระเหย R410A

```cpp
class MeshQualityChecker {
public:
    // Critical metrics for evaporator simulation
    struct QualityMetrics {
        double maxSkewness;           // Should be < 0.85
        double maxAspectRatio;        // Should be < 1000
        double minOrthogonality;      // Should be > 10 degrees
        double maxNonOrthogonality;   // Should be < 70 degrees
        double minVolume;             // Positive volumes only
    };

    [[nodiscard]] QualityMetrics checkEvaporatorMesh(
        const Mesh& mesh) const {

        QualityMetrics metrics{};

        // Check cell volumes (must be positive)
        for (const auto& cell : mesh.cells()) {
            double vol = cell.volume();
            metrics.minVolume = std::min(metrics.minVolume, vol);

            if (vol <= 0.0) {
                throw std::runtime_error("Negative cell volume detected");
            }
        }

        // Check face orthogonality
        for (size_t faceIdx = 0; faceIdx < mesh.numFaces(); ++faceIdx) {
            if (mesh.faceNeighbor(faceIdx).has_value()) {
                // Internal face
                double ortho = computeOrthogonality(mesh, faceIdx);
                metrics.minOrthogonality = std::min(
                    metrics.minOrthogonality, ortho);
                metrics.maxNonOrthogonality = std::max(
                    metrics.maxNonOrthogonality, 90.0 - ortho);
            }
        }

        return metrics;
    }

private:
    double computeOrthogonality(const Mesh& mesh, size_t faceIdx) const {
        const auto& face = mesh.faces()[faceIdx];
        size_t own = mesh.faceOwner(faceIdx);
        size_t nei = mesh.faceNeighbor(faceIdx).value();

        // Vector from owner to neighbor cell center
        auto d = mesh.cells()[nei].center() - mesh.cells()[own].center();

        // Face normal
        auto Sf = face.normal() * face.area();

        // Orthogonality angle
        double magD = std::sqrt(d.x*d.x + d.y*d.y + d.z*d.z);
        double magSf = std::sqrt(Sf.x*Sf.x + Sf.y*Sf.y + Sf.z*Sf.z);

        double cosTheta = (d.x*Sf.x + d.y*Sf.y + d.z*Sf.z) / (magD * magSf);
        return std::acos(std::abs(cosTheta)) * 180.0 / M_PI;
    }
};
```

## Summary
## สรุป

The mesh database architecture is critical for R410A evaporator CFD simulations. While OpenFOAM provides a robust foundation with its `polyMesh` system, modern C++ offers opportunities for:

สถาปัตยกรรมฐานข้อมูลเมชมีความสำคัญอย่างยิ่งสำหรับการจำลอง CFD ของเครื่องระเหย R410A ในขณะที่ OpenFOAM ให้พื้นฐานที่แข็งแกร่งด้วยระบบ `polyMesh` ของมัน Modern C++ ให้โอกาสสำหรับ:

1. **Cleaner API** - Type safety, const-correctness, and better error handling
2. **Modern memory management** - RAII, smart pointers, move semantics
3. **Better performance** - Cache-friendly data layouts, SIMD opportunities
4. **Maintainability** - Clear separation of concerns, testable interfaces

1. **API ที่สะอาดกว่า** - ความปลอดภัยของชนิด ความถูกต้องของ const และการจัดการข้อผิดพลาดที่ดีขึ้น
2. **การจัดการหน่วยความจำสมัยใหม่** - RAII, smart pointers, move semantics
3. **ประสิทธิภาพที่ดีขึ้น** - การจัดเรียงข้อมูลที่เป็นมิตรกับแคช โอกาสในการใช้ SIMD
4. **ความสามารถในการบำรุงรักษา** - การแยกความกังวลที่ชัดเจน อินเทอร์เฟซที่ทดสอบได้

For R410A evaporator applications, the cylindrical O-grid mesh with boundary layer refinement provides optimal balance between accuracy and computational efficiency, capturing both the bulk flow and near-wall phenomena critical for phase change simulations.

สำหรับแอปพลิเคชันเครื่องระเหย R410A เมชทรงกระบอก O-grid พร้อมการปรับปรุงชั้นขอบเขตให้ความสมดุลที่เหมาะสมระหว่างความแม่นยำและประสิทธิภาพการคำนวณ จับทั้งการไหลรวมและปรากฏการณ์ใกล้ผนังที่สำคัญสำหรับการจำลองการเปลี่ยนเฟส

---

**File Structure for R410A CFD Engine:**
```
R410A_CFD/
├── include/
│   ├── mesh/
│   │   ├── Mesh.hpp           # Modern mesh interface
│   │   ├── Point3D.hpp        # Geometric primitives
│   │   ├── Face.hpp           # Face connectivity
│   │   └── Cell.hpp           # Cell data
│   └── geometry/
│       ├── CylindricalMesh.hpp # R410A-specific mesh
│       └── MeshQuality.hpp    # Quality metrics
├── src/
│   ├── mesh/
│   │   ├── Mesh.cpp           # Implementation
│   │   └── MeshBuilder.cpp    # Factory methods
│   └── solvers/
│       └── R410AEvaporator/   # Application-specific
└── tests/
    ├── test_mesh.cpp          # Unit tests
    └── test_geometry.cpp      # Geometric tests
```

**โครงสร้างไฟล์สำหรับ R410A CFD Engine:**
```
R410A_CFD/
├── include/
│   ├── mesh/
│   │   ├── Mesh.hpp           # อินเทอร์เฟซเมชสมัยใหม่
│   │   ├── Point3D.hpp        # วัตถุดิบทางเรขาคณิต
│   │   ├── Face.hpp           # การเชื่อมต่อหน้า
│   │   └── Cell.hpp           # ข้อมูลเซลล์
│   └── geometry/
│       ├── CylindricalMesh.hpp # เมชเฉพาะ R410A
│       └── MeshQuality.hpp    # เมตริกคุณภาพ
├── src/
│   ├── mesh/
│   │   ├── Mesh.cpp           # การนำไปใช้
│   │   └── MeshBuilder.cpp    # วิธีการโรงงาน
│   └── solvers/
│       └── R410AEvaporator/   # เฉพาะแอปพลิเคชัน
└── tests/
    ├── test_mesh.cpp          # การทดสอบหน่วย
    └── test_geometry.cpp      # การทดสอบเรขาคณิต
```
