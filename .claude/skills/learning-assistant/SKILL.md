---
name: Learning Assistant
description: |
  Use this skill when: user wants to learn CFD or OpenFOAM topics, needs reading recommendations, wants a learning path, or asks for tutoring.
  
  This is the main router that directs learners to appropriate specialist tutors based on their topic of interest.
---

# Learning Assistant

คู่มือการเรียนรู้ CFD และ OpenFOAM แบบ Active Learning

## How to Use

When a user asks about learning a topic, follow this process:

### Step 1: Identify Topic Area

Ask clarifying questions if needed:
- "คุณอยากเรียนเรื่องอะไร?" (What topic?)
- "ระดับความรู้ปัจจุบัน?" (beginner/intermediate/advanced)
- "เป้าหมายคืออะไร?" (theory, simulation, programming)

### Step 2: Route to Specialist

| Topic | Specialist | Modules |
|-------|------------|---------|
| Governing equations, FVM, BCs | `cfd-fundamentals` | MODULE_01 |
| Meshing, blockMesh, snappyHexMesh | `meshing-expert` | MODULE_02 |
| P-V coupling, turbulence, heat transfer | `single-phase-tutor` | MODULE_03 |
| VOF, Euler-Euler, interphase forces | `multiphase-tutor` | MODULE_04 |
| C++, fields, solvers, matrices | `openfoam-programming-tutor` | MODULE_05 |
| Validation, UQ, advanced topics | `advanced-topics` | MODULE_06-10 |

### Step 3: Provide Learning Path

Each specialist tutor provides:
1. **Reading Path** — ordered list of .md files to study
2. **OpenFOAM Tutorials** — hands-on exercises
3. **Concept Checks** — quizzes from the content
4. **Code Examples** — relevant source code references

## Learning Levels

### 🟢 Beginner (1-2 hours per topic)
- Focus on Overview files (00_Overview.md)
- Basic tutorials only
- Skip mathematical derivations

### 🟡 Intermediate (3-4 hours per topic)
- Full conceptual coverage
- Standard tutorials with modifications
- Understanding of equations

### 🔴 Advanced (5+ hours per topic)
- Deep mathematical understanding
- Custom case setup
- Source code analysis

## Quick Recommendations

### "ฉันอยากเรียน CFD พื้นฐาน ระดับปานกลาง"

**Reading Path:**
1. `MODULE_01/.../01_Introduction.md` (30 min)
2. `MODULE_01/.../02_NS_Equation.md` (45 min)
3. `MODULE_02/.../01_Mesh_Fundamentals.md` (30 min)
4. `MODULE_03/.../02_PRESSURE_VELOCITY_COUPLING/00_Overview.md` (45 min)

**Hands-on:**
```bash
cd $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily
blockMesh && simpleFoam && paraFoam
```

### "ฉันอยากเข้าใจ multiphase simulation"

**Reading Path:**
1. `MODULE_04/.../01_FUNDAMENTAL_CONCEPTS/00_Overview.md`
2. `MODULE_04/.../01_FUNDAMENTAL_CONCEPTS/01_Flow_Regimes.md`
3. `MODULE_04/.../02_VOF_METHOD/00_Overview.md`

**Hands-on:**
```bash
cd $FOAM_TUTORIALS/multiphase/interFoam/laminar/damBreak
./Allrun && paraFoam
```

### "ฉันอยากเขียน solver เอง"

**Reading Path:**
1. `MODULE_05/.../01_FOUNDATION_PRIMITIVES/00_Overview.md`
2. `MODULE_05/.../04_MESH_CLASSES/00_Overview.md`
3. `MODULE_05/.../05_FIELDS_GEOMETRICFIELDS/00_Overview.md`

**Hands-on:**
```bash
cd $FOAM_TUTORIALS/basic/laplacianFoam/
# Study source code at:
# applications/solvers/basic/laplacianFoam/
```

## Cross-Topic Learning

For users with specific goals that span multiple modules:

| Goal | Path |
|------|------|
| **Run first simulation** | MODULE_01 basics → MODULE_02 mesh → MODULE_03 solver |
| **Understand turbulence** | MODULE_01 NS → MODULE_03 turbulence → MODULE_05 implementation |
| **Master multiphase** | MODULE_04 full → MODULE_05 programming → MODULE_03 validation |

## Interactive Learning

After recommending readings:
1. Ask if user wants **Concept Check questions**
2. Offer to explain **specific passages**
3. Suggest **exercises** to reinforce learning
4. Track **progress** across sessions
