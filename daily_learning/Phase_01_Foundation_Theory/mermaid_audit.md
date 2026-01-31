# Mermaid Diagram Audit - Phase 01

## Executive Summary
All markdown files in `Phase_01_Foundation_Theory` (01-12) were scanned for Mermaid diagrams. A total of **36** diagrams were identified.

**Recommendation:**
- **34** diagrams use standard syntax (`graph`, `flowchart`, `classDiagram`, `timeline`) and should be **RETAINED**.
- **2** diagrams in `03.md` use experimental `xychart-beta` syntax and are recommended for **REPLACEMENT** with static images to ensure consistent rendering across platforms.

## Detailed Inventory

### 01.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 167-172 | `graph TD` | Control Volume Ω | ✅ Keep |
| 238-244 | `graph TD` | Navier-Stokes Equation Terms | ✅ Keep |
| 355-360 | `graph TD` | Energy Balance for Control Volume | ✅ Keep |

### 02.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 35-46 | `flowchart TD` | Computational Domain | ✅ Keep |
| 152-164 | `flowchart TD` | Mathematical Transformation | ✅ Keep |
| 288-300 | `flowchart TD` | Mesh Quality Problem | ✅ Keep |
| 452-468 | `flowchart TD` | fvc vs fvm Operations | ✅ Keep |
| 623-640 | `flowchart TD` | R410A Evaporator Flux Calculations | ✅ Keep |

### 03.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 79-91 | `graph LR` | Face Interpolation Concept | ✅ Keep |
| 185-201 | `classDiagram` | surfaceInterpolationScheme Hierarchy | ✅ Keep |
| 335-349 | `graph LR` | NVD/TVD Diagram Concept | ✅ Keep |
| 441-449 | `xychart-beta` | TVD Limiter Comparison (ψ vs r) | ⚠️ **REPLACE** |
| 590-604 | `flowchart TD` | Divergence Calculation Steps | ✅ Keep |
| 673-682 | `xychart-beta` | TVD Limiter Functions | ⚠️ **REPLACE** |

### 04.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 191-214 | `flowchart TD` | Time Loop Workflow | ✅ Keep |
| 218-277 | `classDiagram` | ddtSchemes Class Hierarchy | ✅ Keep |

### 05.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 53-65 | `flowchart TD` | Time Step Reduction for R410A | ✅ Keep |

### 06.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 31-48 | `graph TD` | Classification of Boundary Conditions | ✅ Keep |
| 123-137 | `graph TD` | Boundary Conditions for Tube Flow | ✅ Keep |
| 355-373 | `graph TD` | Matrix Coefficient Assembly | ✅ Keep |

### 07.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 44-62 | `graph TD` | LDU Storage Layout | ✅ Keep |
| 100-114 | `graph TD` | Matrix-Vector Multiply Algorithm | ✅ Keep |
| 119-142 | `flowchart TD` | Iterative Solvers Overview | ✅ Keep |
| 191-207 | `graph TD` | Matrix Stiffness Visualization | ✅ Keep |
| 491-507 | `graph TD` | Preconditioner Types | ✅ Keep |

### 08.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 22-59 | `classDiagram` | lduMatrix::solver Class Hierarchy | ✅ Keep |
| 116-125 | `flowchart TD` | Jacobi Method Algorithm | ✅ Keep |
| 244-260 | `flowchart TD` | PBiCGStab Algorithm Flow | ✅ Keep |

### 09.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 28-39 | `timeline` | Evolution of Pressure-Velocity Coupling | ✅ Keep |
| 90-105 | `flowchart TD` | SIMPLE Algorithm Loop | ✅ Keep |
| 140-158 | `flowchart TD` | PISO Algorithm Loop | ✅ Keep |
| 207-221 | `flowchart LR` | Rhie-Chow Interpolation | ✅ Keep |
| 455-479 | `flowchart TD` | Algorithm Selection | ✅ Keep |
| 584-603 | `flowchart TD` | R410A Algorithm Selection | ✅ Keep |
| 612-654 | `flowchart TD` | R410A PIMPLE Loop | ✅ Keep |
| 738-774 | `classDiagram` | interFoam to R410A Structure | ✅ Keep |

### 10.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 20-38 | `graph TD` | Two-Phase Flow Representation | ✅ Keep |
| 56-82 | `graph TD` | Flow Regimes in Tubes | ✅ Keep |
| 182-203 | `graph LR` | Interface Compression | ✅ Keep |
| 224-244 | `flowchart TD` | MULES Algorithm | ✅ Keep |
| 304-348 | `classDiagram` | OpenFOAM VOF Class Hierarchy | ✅ Keep |

### 11.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 62-92 | `classDiagram` | phaseChangeModel Hierarchy | ✅ Keep |
| 161-173 | `graph TD` | Vertical Evaporation Flow Regimes | ✅ Keep |

### 12.md
| Lines | Type | Description | Status |
| :--- | :--- | :--- | :--- |
| 200-215 | `flowchart TD` | Boundary Condition Consistency | ✅ Keep |
| 236-286 | `classDiagram` | System Architecture | ✅ Keep |

## Replacement Strategy for `03.md`

The two `xychart-beta` diagrams depict quantitative data (TVD limiter functions) which is typically better suited for static plotting libraries (like Matplotlib) or standard images, rather than schematic diagrams.

**Affected Diagrams:**
1.  **Line 441:** "TVD Limiter Comparison for R410A Interface (ψ vs r)"
2.  **Line 673:** "TVD Limiter Functions ψ(r) vs Gradient Ratio r"

**Action:**
- Generate static images (PNG/SVG) for these plots.
- Replace the mermaid blocks in `03.md` with `![Description](path/to/image.png)`.
