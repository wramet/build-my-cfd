# Learning Paths Quick Reference

Quick lookup for recommended learning paths by topic and level.

## By Topic

### CFD Fundamentals
| Level | Files | Time |
|-------|-------|------|
| Beginner | MODULE_01/.../01_Introduction.md → 02_FVM/00_Overview.md → 03_BC/00_Overview.md | 2 hrs |
| Intermediate | Full MODULE_01 | 6 hrs |
| Advanced | MODULE_01 + MODULE_05 (implementation) | 12+ hrs |

### Meshing
| Level | Files | Time |
|-------|-------|------|
| Beginner | MODULE_02/.../02_BLOCKMESH/00_Overview.md + 01_Basic.md | 2 hrs |
| Intermediate | Full blockMesh + snappyHexMesh basics | 6 hrs |
| Advanced | Full MODULE_02 + mesh quality | 10+ hrs |

### Single-Phase Simulation
| Level | Files | Time |
|-------|-------|------|
| Beginner | MODULE_03/.../01_INCOMP/00_Overview.md + 02_PV/00_Overview.md | 2 hrs |
| Intermediate | P-V coupling + turbulence modeling | 8 hrs |
| Advanced | Full MODULE_03 including V&V | 15+ hrs |

### Multiphase Simulation
| Level | Files | Time |
|-------|-------|------|
| Beginner | MODULE_04/.../01_FUND/00_Overview.md + 02_VOF/00_Overview.md | 2 hrs |
| Intermediate | VOF + Euler-Euler basics | 8 hrs |
| Advanced | Full MODULE_04 including interphase forces | 15+ hrs |

### OpenFOAM Programming
| Level | Files | Time |
|-------|-------|------|
| Beginner | MODULE_05/.../01_FOUND/00_Overview.md + 05_FIELDS/00_Overview.md | 2 hrs |
| Intermediate | Fields + fvc/fvm | 6 hrs |
| Advanced | Full MODULE_05 + custom solver | 20+ hrs |

## By Goal

### "ฉันอยาก run simulation แรก"
1. MODULE_02: blockMesh basics (1 hr)
2. MODULE_01: BC overview (30 min)
3. MODULE_03: simpleFoam overview (30 min)
4. Tutorial: cavity or pitzDaily (1 hr)

### "ฉันอยาก validate ผลลัพธ์"
1. MODULE_03/.../06_V&V/00_Overview.md (30 min)
2. MODULE_03/.../06_V&V/02_Mesh_Independence.md (45 min)
3. GCI calculation practice (1 hr)
4. Compare with benchmark (1 hr)

### "ฉันอยาก simulate free surface"
1. MODULE_04/.../01_FUND/00_Overview.md (30 min)
2. MODULE_04/.../02_VOF/00_Overview.md (30 min)
3. MODULE_04/.../02_VOF/03_Setting_Up.md (45 min)
4. Tutorial: damBreak (1 hr)

### "ฉันอยากเขียน solver เอง"
1. MODULE_05/.../01_FOUND/00_Overview.md (30 min)
2. MODULE_05/.../05_FIELDS/00_Overview.md (45 min)
3. MODULE_05/.../10_VECTOR/02_fvc_vs_fvm.md (60 min)
4. laplacianFoam source study (2 hrs)

## OpenFOAM Tutorials by Topic

| Topic | Tutorial Path |
|-------|---------------|
| First simulation | `incompressible/icoFoam/cavity/cavity` |
| RANS turbulence | `incompressible/simpleFoam/pitzDaily` |
| External aero | `incompressible/simpleFoam/motorBike` |
| VOF multiphase | `multiphase/interFoam/laminar/damBreak` |
| Bubbly flow | `multiphase/twoPhaseEulerFoam/RAS/bubbleColumn` |
| Heat transfer | `heatTransfer/buoyantSimpleFoam/hotRoom` |
| CHT | `heatTransfer/chtMultiRegionFoam/heatExchanger` |
| Moving mesh | `incompressible/pimpleFoam/RAS/propeller` |

## Recommended Order for Complete Learning

1. **Week 1**: CFD Fundamentals (MODULE_01)
2. **Week 2**: Meshing (MODULE_02)
3. **Week 3-4**: Single-Phase Solvers (MODULE_03)
4. **Week 5-6**: Multiphase (MODULE_04)
5. **Week 7-8**: OpenFOAM Programming (MODULE_05)
6. **Week 9+**: Advanced Topics (MODULE_06-10)

## Time Estimates

| Level | Definition | Time per module |
|-------|------------|-----------------|
| Beginner | Overview + basics | 2-3 hours |
| Intermediate | Full concepts | 6-8 hours |
| Advanced | Theory + code | 15-20 hours |
