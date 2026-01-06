# DeepSeek R1 Analysis Template

## Purpose
สร้าง **Technical Skeleton** สำหรับ Daily Lesson โดย R1 จะวิเคราะห์:
1. Mathematical formulations จาก governing equations
2. OpenFOAM class structure และ code logic
3. Key algorithms และ implementation patterns

## Output Format: JSON Structure

```json
{
  "day": "01",
  "title": "Governing Equations Foundation",
  "date": "2026-01-01",
  "difficulty": "hardcore",
  
  "learning_objectives": [
    {
      "verb": "เข้าใจ (Understand)",
      "topic": "Expansion term ในสมการ Continuity",
      "equation": "∇·U = ṁ(1/ρv - 1/ρl)",
      "importance": "Critical for phase change - ไม่มีเทอมนี้ solver จะ diverge"
    },
    {
      "verb": "ออกแบบ (Design)",
      "topic": "Core data structures สำหรับ CFD engine",
      "components": ["Mesh", "Fields", "BoundaryConditions"]
    },
    {
      "verb": "Implement",
      "topic": "Pressure-velocity coupling (SIMPLE/PISO)",
      "challenge": "การจัดการ source term จากการเปลี่ยนสถานะ"
    }
  ],
  
  "theory_sections": [
    {
      "id": "1.1",
      "title_en": "Continuity Equation with Phase Change",
      "title_th": "สมการ Continuity ที่มีการเปลี่ยนสถานะ",
      "equations": [
        {
          "name": "General form",
          "latex": "\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{U}) = 0",
          "explanation": "Conservation of mass ในรูปแบบทั่วไป"
        },
        {
          "name": "With phase change",
          "latex": "\\nabla \\cdot \\mathbf{U} = \\dot{m} \\left( \\frac{1}{\\rho_v} - \\frac{1}{\\rho_l} \\right)",
          "explanation": "Expansion term - ทำให้ divergence ไม่เป็นศูนย์"
        }
      ],
      "variables": [
        {"symbol": "ṁ", "name": "mass transfer rate", "unit": "kg/m³·s"},
        {"symbol": "ρv", "name": "vapor density", "unit": "kg/m³"},
        {"symbol": "ρl", "name": "liquid density", "unit": "kg/m³"}
      ],
      "warning": "Expansion term นี้ทำให้เกิดการเปลี่ยนแปลง velocity อย่างรุนแรงที่ interface - ต้องจัดการใน pressure equation"
    }
  ],
  
  "openfoam_analysis": [
    {
      "class": "volScalarField",
      "header": "src/finiteVolume/fields/volFields/volFields.H",
      "purpose": "เก็บ scalar field (p, T, alpha) ที่ cell centers",
      "key_members": [
        {"name": "internalField_", "type": "Field<scalar>", "purpose": "Internal field values"},
        {"name": "boundaryField_", "type": "GeometricBoundaryField", "purpose": "Boundary conditions"}
      ],
      "key_methods": [
        {"name": "correctBoundaryConditions()", "purpose": "Update BC values after solve"},
        {"name": "component()", "purpose": "Extract component for tensors"}
      ],
      "usage_example": "volScalarField p(IOobject(...), mesh);"
    },
    {
      "class": "fvMatrix",
      "header": "src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.H",
      "purpose": "Sparse matrix system A*x = b จาก FVM discretization",
      "matrix_structure": {
        "diagonal": "D() - owner cell coefficients",
        "upper": "upper() - owner→neighbor coefficients",
        "lower": "lower() - neighbor→owner coefficients",
        "source": "source() - RHS vector b"
      },
      "operators": [
        {"namespace": "fvm::", "type": "implicit", "returns": "fvMatrix", "examples": ["ddt", "div", "laplacian"]},
        {"namespace": "fvc::", "type": "explicit", "returns": "GeometricField", "examples": ["grad", "div", "laplacian"]}
      ]
    }
  ],
  
  "implementation_skeleton": {
    "classes": [
      {
        "name": "Solver",
        "responsibility": "Main solver class - SIMPLE/PISO algorithm",
        "key_methods": [
          {"name": "solveMomentum()", "purpose": "Solve U equation"},
          {"name": "solvePressure()", "purpose": "Solve p equation WITH expansion term"},
          {"name": "solveAlpha()", "purpose": "Solve alpha equation WITH compression"},
          {"name": "solveEnergy()", "purpose": "Solve T equation WITH latent heat"}
        ],
        "critical_implementation": "solvePressure() MUST include mDot*(1/rho_v - 1/rho_l) as source"
      }
    ],
    "algorithm_steps": [
      "1. solveMomentum() → U*",
      "2. solvePressure() → p (with expansion source)",
      "3. Correct velocity: U = U* - grad(p)/rho",
      "4. solveAlpha() → alpha (with compression)",
      "5. solveEnergy() → T (with latent heat)",
      "6. updateProperties() → rho, mu, k based on alpha",
      "7. Check convergence, repeat outer loop"
    ]
  },
  
  "concept_checks": [
    {
      "question": "ทำไมสมการ Continuity ถึงมีเทอมทางขวาที่ไม่เป็นศูนย์?",
      "answer_key_points": [
        "Single-phase incompressible: ∇·U = 0 เพราะ ρ คงที่",
        "Phase change: มี mass transfer ระหว่าง phase",
        "R410A density ratio ~22:1 → expansion มหาศาล",
        "ต้องใส่ใน pressure equation ไม่งั้น diverge"
      ],
      "implementation_note": "ใน Solver::solvePressure() line xxx"
    }
  ],
  
  "pitfalls": [
    {
      "symptom": "Solver diverges",
      "cause": "Missing expansion term in pressure equation",
      "fix": "Add mDot*(1/rho_v - 1/rho_l) to pEqn source"
    },
    {
      "symptom": "Interface smears over 5-10 cells",
      "cause": "No compression in alpha equation",
      "fix": "Add compressive flux limiter"
    }
  ],
  
  "connections": {
    "previous_day": null,
    "next_day": "Day 02: Finite Volume Method Basics",
    "key_link": "Today's equations → Day 02's discretization"
  }
}
```

## Prompt Template for R1

```
คุณคือ CFD Expert ที่กำลังวิเคราะห์ OpenFOAM source code สำหรับสร้าง technical skeleton

**Day {DAY_NUMBER}: {TOPIC}**

**Context:**
- Project: CFD Engine สำหรับ Refrigerant Evaporator
- Level: Hardcore (ละเอียดมาก)
- Phase 1 Context: {PHASE_1_CONTEXT}
- Previous Day: {PREVIOUS_DAY_SUMMARY}

**Files to Analyze:**
{FILE_LIST}

**Your Task:**
1. วิเคราะห์ Mathematical equations ที่เกี่ยวข้อง
2. วิเคราะห์ OpenFOAM class structure และ key algorithms
3. สร้าง JSON skeleton ตาม template ข้างบน
4. ระบุ CRITICAL implementation details (เช่น expansion term)
5. สร้าง Concept checks พร้อม answer key points

**Output:**
JSON skeleton เท่านั้น - ไม่ต้องมี explanation อื่น
```
