<<<< ID: DIA_2911dc27 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
M1[01 Verification Fundamentals]:::explicit --> M2[02 Test Framework Development]:::implicit
M2 --> M3[03 Validation Benchmarks]:::implicit
M3 --> M4[04 QA, Automation & Profiling]:::success

<<<< END >>>>

<<<< ID: DIA_ea0e13b3 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
A[Physical Validation]:::explicit --> B[Regression Testing]:::implicit
B --> C[Integration Testing]:::implicit
C --> D[Unit Testing]:::implicit

<<<< END >>>>

<<<< ID: DIA_ea910102 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
A[Physical Reality]:::explicit -- Modeling --> B[Mathematical Model]:::implicit
B -- Programming --> C[Computer Code]:::implicit
C -- Simulation --> D[Numerical Results]:::explicit

B -. "Validation (Right Thing?)" .-> A
C -. "Verification (Thing Right?)" .-> B

<<<< END >>>>

<<<< ID: DIA_49f7f57e >>>>
sequenceDiagram
participant Main as main()
participant Case as setRootCase
participant Time as createTime
participant Mesh as createMesh
participant Test as Test Object
Note over Main: Initialization Phase
Main->>Case: Initialize Case
Main->>Time: Initialize Time
Main->>Mesh: Initialize Mesh
Main->>Test: Create("FieldOperationTest")

Note over Main, Test: Execution Phase
activate Test
Test->>Test: Perform Testing Operations
Test-->>Main: pass/fail assertion
deactivate Test

Main->>Test: report()

<<<< END >>>>

<<<< ID: DIA_24e45a3b >>>>
classDiagram
class TestSuite {
+name: String
+runAll()
+report()
+getStatistics()
}
class TestCase {
+name: String
+setUp()
+run()
+tearDown()
}
class TestAssertion {
+expected: scalar
+actual: scalar
+tolerance: scalar
+check()
+compare()
}
TestSuite "1" *-- "many" TestCase : Contains
TestCase "1" *-- "many" TestAssertion : Executes

<<<< END >>>>

<<<< ID: DIA_e64de580 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
A[C++ Test Source]:::explicit -- wmake --> B[Executable Binary]:::implicit
C[Base Case Directory]:::context -- Allrun --> D[Initialized Case]:::implicit
B --> E[Run Test Binary -case D]:::implicit
D --> E
E --> F[Standard Output/Log]:::context
F --> G[Test Report Markdown/CSV]:::success

<<<< END >>>>

<<<< ID: DIA_ccf26dc4 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[กำหนดฟังก์ชันเชิงวิเคราะห์ phi_exact]:::explicit --> B[คำนวณเทอมต้นกำเนิด S = L phi_exact]:::implicit
B --> C[นำเทอม S ไปใช้ใน OpenFOAM Solver]:::implicit
C --> D[รันการจำลองเพื่อหาค่า phi_numerical]:::implicit
D --> E[เปรียบเทียบ phi_numerical กับ phi_exact]:::implicit
E --> F{ความผิดพลาดน้อยและ\nลู่เข้าด้วยลำดับที่\nถูกต้องหรือไม่?}:::warning
F -- ใช่ --> G[โค้ดได้รับการตรวจสอบแล้ว]:::success
F -- ไม่ใช่ --> H[มีบั๊กในโค้ดหรือระเบียบวิธี]:::explicit

<<<< END >>>>

<<<< ID: DIA_c1ce4127 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
A[Physical Reality]:::explicit -->|Compare| B(Validation):::explicit
B --> C[Mathematical Model]:::implicit
C -->|Discretization| D[Numerical Model]:::implicit
D -->|Verification| E[Computer Code]:::implicit
E --> F[Simulation Results]:::explicit

<<<< END >>>>

<<<< ID: DIA_90ab45c1 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
A[เริ่มจับเวลา: Start Timer]:::context --> B[วนลูป Solver: Solver Iterations]:::implicit
B --> C[ตรวจสอบการลู่เข้า: Check Convergence]:::implicit
C -- ยังไม่ลู่เข้า: No --> B
C -- ลู่เข้าแล้ว: Yes --> D[หยุดจับเวลา: Stop Timer]:::implicit
D --> E[คำนวณ Wall Time vs CPU Time]:::implicit
E --> F[รายงานเมตริกประสิทธิภาพ: Report Performance Metrics]:::success

<<<< END >>>>

<<<< ID: DIA_0ef76152 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[เริ่ม Profiling: Start Profiling]:::explicit --> B[รัน 1 CPU: Run with 1 CPU]:::implicit
B --> C[บันทึกเวลา T1: Record Time T1]:::implicit
C --> D[รัน N CPUs: Run with N CPUs]:::implicit
D --> E[บันทึกเวลา Tn: Record Time Tn]:::implicit
E --> F{คำนวณ Efficiency: Calculate Efficiency}:::warning
F -- มากกว่า 80%: > 80% --> G[การปรับขนานดี: Good Scaling]:::success
F -- น้อยกว่า 50%: < 50% --> H[วิเคราะห์ Bottleneck: Network/IO/Serial]:::explicit
H --> I[ปรับปรุงโค้ดหรือการ Decompose]:::implicit

<<<< END >>>>

<<<< ID: DIA_5acb6868 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[เริ่ม Performance Profiling]:::explicit --> B[รัน Solver และจับเวลา]:::implicit
B --> C[ระบุส่วนที่ใช้เวลานานที่สุด]:::implicit
C --> D{ประเภท Bottleneck}:::warning
D -- Computation: คำนวณหนัก --> E[เปลี่ยน Numerical Scheme หรือ Algorithm]:::implicit
D -- Communication: ส่งข้อมูลบ่อย --> F[ปรับ Decomposition หรือใช้ GSLIB]:::implicit
D -- I/O: อ่าน/เขียนช้า --> G[ลดการ Output หรือใช้ Parallel I/O]:::implicit
E --> H[ทดสอบอีกครั้ง]:::implicit
F --> H
G --> H
H --> I{ดีขึ้นหรือไม่?}:::warning
I -- ใช่ --> J[บันทึกและนำไปใช้]:::success
I -- ไม่ --> K[ลองวิธีอื่นหรือยอมรับ]:::explicit

<<<< END >>>>

<<<< ID: DIA_4348d8f9 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
Issue[Issue Detected: FAIL/Diverge]:::explicit --> MeshCheck[Run checkMesh]:::implicit
MeshCheck -- Fail --> FixMesh[Fix Topology/Quality]:::warning
MeshCheck -- OK --> FieldCheck[Run checkFields]:::implicit
FieldCheck -- Fail --> FixBC[Fix Boundary/Initial Conditions]:::warning
FieldCheck -- OK --> DebugSwitch[Enable DebugSwitches in controlDict]:::implicit
DebugSwitch --> Analyze[Analyze Detailed Matrix/PISO Logs]:::success

<<<< END >>>>

<<<< ID: DIA_96298b64 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Code Version 1: Stable]:::implicit --> B[Generate Reference Database]:::implicit
B --> C[Modify Code / New Feature]:::explicit
C --> D[Run Version 2: New]:::implicit
D --> E{Compare New vs Reference}:::warning
E -- Within Tolerance --> F[PASS: Regression Safe]:::success
E -- Out of Tolerance --> G[FAIL: Regression Detected]:::explicit
G --> H[Debug / Revert Changes]:::implicit

<<<< END >>>>

<<<< ID: DIA_7cc2f171 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
A[Old Case Format]:::context --> B{Compatibility Layer}:::implicit
B -- Direct Support --> C[Execution Success]:::success
B -- Deprecated --> D[Warning Message]:::explicit
B -- Incompatible --> E[Automatic Converter Script]:::implicit
E --> F[New Case Format]:::success
F --> C

<<<< END >>>>

<<<< ID: DIA_49862bb3 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[OpenFOAM Development]:::explicit --> B{Code Works?}:::warning
B -- No --> C[Debug & Fix]:::explicit
B -- Yes --> D[QA Process]:::implicit
D --> E[Performance Profiling]:::implicit
D --> F[Regression Testing]:::implicit
D --> G[Advanced Debugging]:::implicit
E --> H[Optimized Solver]:::success
F --> I[Verified Correctness]:::success
G --> J[Stable Solver]:::success
H --> K[Production Ready]:::success
I --> K
J --> K
K --> L[Reliable CFD Software]:::success

<<<< END >>>>

<<<< ID: DIA_21da87d0 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Design Solver]:::explicit --> B[Implementation]:::implicit
B --> C[Unit Testing]:::implicit
C --> D[Performance Profiling]:::implicit
D --> E[Regression Testing]:::implicit
E --> F{All Tests Pass?}:::warning
F -- No --> G[Debug & Fix]:::explicit
G --> B
F -- Yes --> H[Release / Deploy]:::success
H --> I[Monitor in Production]:::implicit
I --> J[Collect Feedback]:::implicit
J --> A

<<<< END >>>>

<<<< ID: DIA_fe402298 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
Level3[Validation Test: Hours]:::explicit --> Level2[Integration Test: Minutes]:::implicit
Level2 --> Level1[Unit Test: Seconds]:::implicit

<<<< END >>>>

<<<< ID: DIA_d7a7b50e >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Start Test]:::explicit --> B[Unit Tests]:::implicit
B --> C{All Passed?}:::warning
C -- No --> D[Fix Code]:::explicit
D --> B
C -- Yes --> E[Integration Tests]:::implicit
E --> F{All Passed?}:::warning
F -- No --> D
F -- Yes --> G[Validation Tests]:::implicit
G --> H{Results Validated?}:::warning
H -- No --> I[Refine Model]:::explicit
I --> G
H -- Yes --> J[Generate Test Report]:::success
J --> K[Archive Results]:::implicit
K --> L[Test Complete]:::success

<<<< END >>>>

<<<< ID: DIA_fac04151 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Raw Mesh]:::explicit --> B{checkMesh}:::warning
B -- OK --> C[Test Field Operations]:::implicit
B -- Error --> Error[Fix Mesh Topology]:::explicit
C --> D[Test Interpolation]:::implicit
D --> E[Test Differentiation]:::implicit
E --> F[Test BC Consistency]:::implicit
F --> Result([Mesh/BC Verified]):::success

<<<< END >>>>

<<<< ID: DIA_8c3f152d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Physical Problem]:::context --> B[Governing Equations]:::implicit
B --> C[Discretization]:::implicit
C --> D[Numerical Solution]:::implicit
D --> E{Validation}:::warning
E -->|Compare with| F[Experimental Data]:::explicit
E -->|Compare with| G[Analytical Solutions]:::explicit
E -->|Compare with| H[Benchmark Cases]:::explicit
F --> I{Acceptable Agreement?}:::warning
G --> I
H --> I
I -- Yes --> J[Validated Model]:::success
I -- No --> K[Refine Model/BCs/Mesh]:::explicit
K --> B

<<<< END >>>>

<<<< ID: DIA_c375dc85 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Select Benchmark Case]:::explicit --> B[Define Geometry & BCs]:::implicit
B --> C[Generate Mesh M1]:::implicit
C --> D[Run Simulation S1]:::implicit
D --> E[Compare with Reference]:::warning
E --> F{Error < Threshold?}:::warning
F -- No --> G[Refine to M2]:::implicit
G --> H[Run Simulation S2]:::implicit
H --> I{S2-S1 Converged?}:::warning
I -- No --> G
I -- Yes --> J[Final Results Analysis]:::success
F -- Yes --> J
J --> K[Document Results]:::implicit
K --> L[Validation Complete]:::success

<<<< END >>>>

<<<< ID: DIA_4a0b15fd >>>>
flowchart TB
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
Start([เริ่ม ./Alltest]):::explicit --> Init[ตั้งค่า Environment]:::implicit
Init --> Scan[สแกนไดเรกทอรีย่อยทั้งหมด]:::implicit
Scan --> Filter{กรองเฉพาะที่มี Allrun?}:::warning
Filter -- ใช่ --> Queue[เพิ่มเข้าคิว]:::implicit
Filter -- ไม่ --> Skip[ข้าม]:::context
Queue --> ExecLoop{วนลูปทุก Test Case}:::implicit
ExecLoop --> ChangeDir[cd ไปยัง Test Directory]:::implicit
ChangeDir --> LogSetup[สร้าง Log File]:::implicit
LogSetup --> RunTest[Execute ./Allrun]:::implicit
RunTest --> Check{Exit Code = 0?}:::warning
Check -- ใช่ --> Success[บันทึก: PASS]:::success
Check -- ไม่ --> Fail[บันทึก: FAIL<br/>Copy Log ไปยัง Failed/]:::explicit
Success --> ExecLoop
Fail --> ExecLoop
ExecLoop -- จบ --> Summary[สรุปผลการทดสอบ]:::implicit
Summary --> FinalExit{ทุก Test ผ่าน?}:::warning
FinalExit -- ใช่ --> EndSuccess([Exit 0]):::success
FinalExit -- ไม่ --> EndFail([Exit 1]):::explicit
Skip --> ExecLoop

<<<< END >>>>

<<<< ID: DIA_5b2b66e9 >>>>
sequenceDiagram
participant Dev as Developer
participant Git as GitHub Repository
participant Action as GitHub Action (Runner)
participant Cont as OpenFOAM Container
participant Build as Build System
participant Test as Test Suite
participant Report as Report Generator
participant Badge as Status Badge
Dev->>Git: Push Code / Pull Request
Git->>Action: Trigger Workflow
activate Action
Note over Action: Checkout Repository
Action->>Cont: Pull Container (openfoam/openfoam10)
Cont-->>Action: Container Ready
Note over Action: Source Environment
Action->>Build: ./Allwmake
Build-->>Action: Build Logs
alt Build Success
    Action->>Test: ./Alltest
    Test->>Test: Run All Test Cases
    Test-->>Action: Test Results
    Action->>Report: Generate Summary
    Report-->>Action: Test Report
    Action->>Git: Upload Artifacts
    alt All Tests Pass
        Action->>Badge: Update: ✓ Success
        Action-->>Git: Exit Code: 0
    else Some Tests Fail
        Action->>Badge: Update: ✗ Failed
        Action-->>Git: Exit Code: 1
    end
else Build Failure
    Action->>Badge: Update: ✗ Build Error
    Action-->>Git: Exit Code: 1
end
deactivate Action

<<<< END >>>>

<<<< ID: DIA_187a375f >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
subgraph Preparation["ขั้นตอนเตรียมการ"]
    A["Database<br/>Pre-generated Meshes"]:::context --> B["Checkmark<br/>Reference Values"]:::explicit
end

subgraph Execution["ขั้นตอนดำเนินการ"]
    B --> C["Execute<br/>Run Simulation"]:::implicit
    C --> D["Compare<br/>Validate Results"]:::implicit
end

subgraph Cleanup["ขั้นตอนทำความสะอาด"]
    D --> E["Trash Bin<br/>Remove Temporary Files"]:::context
    D --> F["Archive<br/>Store Results"]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_23c55592 >>>>
flowchart TB
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
Start([./Alltest --parallel]):::explicit --> Analyze[วิเคราะห์ Test Cases]:::implicit
Analyze --> Categorize{จัดกลุ่ม<br/>ตาม Dependencies}:::implicit

Categorize --> Group1[Group 1:<br/>Unit Tests]:::implicit
Categorize --> Group2[Group 2:<br/>Integration Tests]:::implicit
Categorize --> Group3[Group 3:<br/>Solver Tests]:::implicit

Group1 --> P1[Processor 1]:::implicit
Group2 --> P2[Processor 2]:::implicit
Group3 --> P3[Processor 3]:::implicit

P1 --> R1[Results 1]:::implicit
P2 --> R2[Results 2]:::implicit
P3 --> R3[Results 3]:::implicit

R1 --> Merge[รวมผลลัพธ์]:::implicit
R2 --> Merge
R3 --> Merge

Merge --> Final[สรุปผล]:::success

<<<< END >>>>

<<<< ID: DIA_d4b7eee8 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
Start([Start Validation Driver]):::explicit --> Setup[1. Setup Time & Mesh]:::implicit
Setup --> Models[2. Select Physics Models]:::implicit
Models --> Solve[3. Solver Execution Loop]:::implicit
Solve --> Extract[4. Extract Key Data: Drag, Flux, etc.]:::implicit
Extract --> Compare{5. Compare vs Reference}:::warning
Compare -- PASS --> Log[Log Success]:::success
Compare -- FAIL --> Warn[Log Warning/Failure]:::explicit
Log --> Report([Generate Final Report]):::implicit
Warn --> Report

<<<< END >>>>

<<<< ID: DIA_5bd3c39d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Input Values: A, B]:::explicit --> B{Assertion Type}:::implicit
B -- Integer/Boolean --> C[Check Exact Equality A == B]:::implicit
B -- Floating Point --> D[Check with Tolerance]:::implicit
D --> E{Tolerance Type}:::implicit
E -- Absolute --> F[Check: |A-B| < epsilon_abs]:::implicit
E -- Relative --> G[Check: |A-B|/|A| < epsilon_rel]:::implicit
E -- Combined --> H[Check: |A-B| < max epsilon_abs, epsilon_rel*|A|]:::implicit
F --> I[Result: PASS/FAIL]:::warning
G --> I
H --> I
C --> I
I -- PASS --> J[Continue Testing]:::success
I -- FAIL --> K[Report Error & Stop/Continue]:::explicit

<<<< END >>>>

<<<< ID: DIA_8fa23015 >>>>
classDiagram
class TestCase {
<<Abstract Interface>>
+string name_
+run()*
+setUp()*
+tearDown()*
+reportResults()
}
class ScalarFieldOperationTest {
+run()
-testFieldCreation()
-testFieldArithmetic()
-testFieldGradient()
-testFieldLaplacian()
}
class VectorFieldOperationTest {
+run()
-testVectorCreation()
-testVectorOperations()
-testDivergence()
}
class MatrixTest {
+run()
-testMatrixCreation()
-testLUSolve()
-testMatrixVectorProduct()
}
TestCase <|-- ScalarFieldOperationTest
TestCase <|-- VectorFieldOperationTest
TestCase <|-- MatrixTest
class TestRunner {
    +List~TestCase~ tests_
    +addTest(TestCase)
    +runAll()
    +generateReport()
}
TestRunner --> TestCase : manages

<<<< END >>>>

<<<< ID: DIA_2e07541c >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
A[Testing Framework Design]:::explicit --> B[Isolation]:::implicit
A --> C[Reproducibility]:::implicit
A --> D[Automation]:::implicit

B --> B1[แต่ละ Test Case เป็นอิสระ]:::implicit
B --> B2[ไม่มี Side Effects ระหว่าง Tests]:::implicit
B --> B3[Fail ใน Test หนึ่งไม่กระทบ Test อื่น]:::implicit

C --> C1[ใช้ Seed เดียวกันสำหรับ Random]:::implicit
C --> C2[Fix Version ของ Dependencies]:::implicit
C --> C3[Store Reference Data ใน VCS]:::implicit

D --> D1[One-command Execution]:::implicit
D --> D2[Automated Reporting]:::implicit
D --> D3[CI/CD Integration]:::implicit

<<<< END >>>>

<<<< ID: DIA_59dbe276 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
A[Case Dictionary]:::explicit --> B[phaseSystem::New]:::implicit
A --> C[dragModel::New]:::implicit
A --> D[turbulenceModel::New]:::implicit

subgraph "Factory Layer"
B
C
D
end

B --> E[mixturePhaseSystem Object]:::success
C --> F[SchillerNaumann Object]:::success
D --> G[kEpsilon Object]:::success

subgraph "Strategy Implementation"
E
F
G
end

E --> H[multiphaseEulerFoam Solver]:::context
F --> H
G --> H

subgraph "Solver Loop"
H
end

<<<< END >>>>

<<<< ID: DIA_336f36b9 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Sequential Time]:::explicit --> B[Parallel Execution]:::implicit
B --> C[Compute Time Processor 1]:::implicit
B --> D[Compute Time Processor 2]:::implicit
B --> E[Compute Time Processor N]:::implicit
C --> F[Max Compute Time]:::warning
D --> F
E --> F
F --> G[Communication Overhead]:::explicit
G --> H[Actual Parallel Time]:::success
A --> I[Actual Speedup Calculation]:::success
H --> I

<<<< END >>>>

<<<< ID: DIA_b4639fce >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Dictionary File<br/>type: "kEpsilon"]:::explicit --> B[Factory Call<br/>turbulenceModel::New()]:::implicit
B --> C[Parse Dictionary<br/>Read type keyword]:::implicit
C --> D[Lookup in Selection Table<br/>Hash table search]:::implicit
D --> E{Found?}:::warning
E -->|Yes| F[Call Registered Constructor<br/>kEpsilon::New(U, phi, transport)]:::implicit
E -->|No| G[Fatal Error with Available Types<br/>Built from table entries]:::explicit
F --> H[Dynamic Memory Allocation<br/>new kEpsilonModel(...)]:::implicit
H --> I[Wrap in autoPtr<br/>Smart pointer management]:::implicit
I --> J[Return to Caller<br/>Ready for use]:::success

<<<< END >>>>

<<<< ID: DIA_9e3c10ec >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[1. Physical Analysis]:::explicit --> B[2. Interface Design]:::implicit
B --> C[3. Implementation]:::implicit
C --> D[4. Factory Registration]:::implicit
D --> E[5. Build System]:::implicit
E --> F[6. Case Configuration]:::implicit
F --> G[7. Testing & Validation]:::success

<<<< END >>>>

<<<< ID: DIA_0f10599b >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[MyHeatTransfer.C]:::explicit --> B{addToRunTimeSelectionTable}:::implicit
B --> C[Static Registration Object]:::implicit
C --> D[Global Selection Table]:::success

E[Case Dictionary]:::explicit --> F[heatTransferModel::New]:::implicit
F --> G{Lookup 'myHeatTransfer'}:::implicit
G --> D
D --> H[Create MyHeatTransfer Instance]:::implicit
H --> I[Configure with Parameters]:::implicit
I --> J[Return autoPtr]:::success

<<<< END >>>>

<<<< ID: DIA_2c38aeb5 >>>>
classDiagram
class dragModel {
<<interface>>
+K(phase1, phase2)*
}
class SchillerNaumann {
+K(phase1, phase2)
}
class Ergun {
+K(phase1, phase2)
}
class Gibilaro {
+K(phase1, phase2)
}
dragModel <|.. SchillerNaumann
dragModel <|.. Ergun
dragModel <|.. Gibilaro

<<<< END >>>>

<<<< ID: DIA_cc44cde6 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
A[Design Pattern Matrix]:::explicit --> B[Plugin Capability]:::implicit
A --> C[Numerical Flexibility]:::implicit
A --> D[Developer Efficiency]:::implicit

B --> B1[Factory Method + Registry]:::implicit
B --> B2[Dependency Injection]:::implicit

C --> C1[Strategy Pattern]:::implicit
C --> C2[Template Method]:::implicit

subgraph "Object Creation"
B1
B2
end

subgraph "Algorithm Execution"
C1
C2
end

<<<< END >>>>

<<<< ID: DIA_4be6ee77 >>>>
sequenceDiagram
participant T as Time Loop
participant L as functionObjectList
participant F as Concrete functionObject
participant S as Solver Engine
loop Every Time Step
    T->>L: 1. execute()
    L->>F: 1.1 execute() (if time)
    F-->>L: Done
    L-->>T: Done

    T->>S: 2. solvePhysics()
    S-->>T: Results (U, p, etc.)

    T->>L: 3. write()
    L->>F: 3.1 write() (if time)
    F-->>L: File I/O Done
    L-->>T: Done
end

<<<< END >>>>

<<<< ID: DIA_8761c6e2 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[OpenFOAM Platform]:::implicit --> B[Core Engine<br/>Numerical Solvers]:::implicit
A --> C[Plugin API<br/>Base Classes]:::implicit
A --> D[Dynamic Loader<br/>dlopen / libs]:::implicit

C --> C1[functionObjects]:::implicit
C --> C2[Boundary Conditions]:::implicit
C --> C3[Physics Models]:::implicit

D --> E[User-defined Libraries<br/>.so / .dylib]:::explicit
E --> C1
E --> C2
E --> C3

subgraph "The App Store"
C1
C2
C3
end

<<<< END >>>>

<<<< ID: DIA_30a72c41 >>>>
timeline
title Registration vs. Usage Lifecycle
Static Initialization : All built-in functionObjects register with global table
Program Start : main() begins execution
Dynamic Loading : libs() entry in controlDict triggers dlopen()
Library Registration : Static initializers in .so file register new types
Runtime Usage : Solver reads 'type forces', looks up in table, creates object

<<<< END >>>>

<<<< ID: DIA_916beeed >>>>
sequenceDiagram
participant S as Solver (New method)
participant OS as Operating System
participant L as Shared Library (.so)
participant T as Global Selection Table
S->>OS: Call dlopen(libName, RTLD_GLOBAL)
OS->>L: Map library into memory
L->>L: Run Static Constructors
L->>T: Register types (addToRunTimeSelectionTable)
T-->>S: Update Table Pointers
S->>T: Lookup and Create Object

<<<< END >>>>

<<<< ID: DIA_a038d8cc >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[1. กำหนด Interface Header]:::explicit --> B[2. Implement Source Code]:::implicit
B --> C[3. สร้าง Build Configuration]:::implicit
C --> D[4. Compile Library]:::implicit
D --> E[5. กำหนดค่า controlDict]:::implicit
E --> F[6. ทดสอบและ Validate]:::success

<<<< END >>>>

<<<< ID: DIA_80b09e47 >>>>
stateDiagram-v2
[] --> Construction: functionObject::New()
Construction --> Initialized: read(dict)
Initialized --> Executing: execute() called
Executing --> Executing: Each time step
Executing --> Writing: write() called
Writing --> Executing: Continue simulation
Executing --> []: Destruction

<<<< END >>>>

<<<< ID: DIA_ad5b881e >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
subgraph "Eager Evaluation (Traditional)"
E1[A + B]:::explicit --> E2[Temp 1]:::implicit
E2 --> E3[Temp 1 + C]:::implicit
E3 --> E4[Final Result]:::success
end

subgraph "Lazy Evaluation (OpenFOAM)"
L1[A + B + C]:::explicit --> L2{Expression Tree}:::implicit
L2 --> L3[Single Pass Evaluation]:::implicit
L3 --> L4[Final Result]:::success
end

<<<< END >>>>

<<<< ID: DIA_ff4365d4 >>>>
classDiagram
class ExpressionTemplate~Derived~ {
<<interface>>
+evaluate(cell)
}
class FieldExpression {
-field_
+evaluate(cell)
}
class BinaryExpression~LHS, RHS, Op~ {
-lhs_
-rhs_
+evaluate(cell)
}
ExpressionTemplate <|-- FieldExpression
ExpressionTemplate <|-- BinaryExpression

<<<< END >>>>

<<<< ID: DIA_6bc6e7a3 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Start Evaluation: operator=]:::explicit --> B[Recursive Tree Traversal]:::implicit
B --> C[Compute Cell 0: All terms combined]:::implicit
C --> D[Compute Cell 1: All terms combined]:::implicit
D --> E[Compute Cell N: All terms combined]:::implicit
E --> F[Update Boundary Fields]:::implicit
F --> G[End: Final Field Updated]:::success

<<<< END >>>>

<<<< ID: DIA_f5f6fb3d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Field Expression]:::explicit --> B[Expression Template AST]:::implicit
B --> C[Compiler Loop Fusion]:::implicit
C --> D[SIMD Pattern Matching]:::implicit
D --> E[AVX/SSE Instruction Generation]:::implicit
E --> F[SIMD-optimized Machine Code]:::success

subgraph "Compile-Time"
B
C
D
end

subgraph "Hardware-Level"
E
F
end

<<<< END >>>>

<<<< ID: DIA_425bfe4a >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
Step1["1. Define Functor"]:::explicit --> Step2["2. Define Expression Class"]:::implicit
Step2 --> Step3["3. Overload Operator"]:::implicit
Step3 --> Step4["4. Use in Solver"]:::success

<<<< END >>>>

<<<< ID: DIA_0a932c24 >>>>
classDiagram
class ExpressionTemplate~Derived~ {
<<interface>>
+derived() const
+evaluate(cellI, mesh)
}
class BinaryExpression~LHS, RHS, Op~ {
-lhs_
-rhs_
-op_
+evaluate(cellI, mesh)
}
ExpressionTemplate <|-- BinaryExpression : CRTP

<<<< END >>>>

<<<< ID: DIA_805a978c >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Performance Anti-Patterns]:::explicit --> B[Expression Splitting]:::warning
A --> C[Manual Index Access]:::warning
A --> D[Excessive tmp Dereferencing]:::warning

B --> B1[Multiple Allocations]:::implicit
B --> B2[Poor Cache Locality]:::implicit

C --> C1[Skip Boundary Updates]:::implicit
C --> C2[Broken SIMD Vectorization]:::implicit

D --> D1[Forced Materialization]:::implicit
D --> D2[Memory Copy Overhead]:::implicit

<<<< END >>>>

<<<< ID: DIA_b40e2288 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Memory Architecture]:::explicit --> B[RAII]:::implicit
A --> C[Reference Counting]:::implicit
A --> D[Registry]:::implicit
A --> E[Move Semantics]:::implicit

B --> B1[Resource Safety]:::success
C --> C1[Shared Data Efficiency]:::success
D --> D1[Centralized Management]:::success
E --> E1[Zero-copy Ownership Transfer]:::success

F[Design Patterns]:::explicit --> G[autoPtr]:::implicit
F --> H[tmp]:::implicit
F --> I[refCount]:::implicit
F --> J[objectRegistry]:::implicit

G --> G1[Exclusive Ownership]:::success
H --> H1[Temporary/Persistent Dual Mode]:::success
I --> I1[Lightweight Reference Counting]:::success
J --> J1[Hierarchical Object Management]:::success

<<<< END >>>>

<<<< ID: DIA_4c720e49 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Memory Architecture]:::explicit --> B[RAII]:::implicit
A --> C[Reference Counting]:::implicit
A --> D[Registry]:::implicit
A --> E[Move Semantics]:::implicit

B --> B1[Resource Safety]:::success
C --> C1[Shared Data Efficiency]:::success
D --> D1[Centralized Management]:::success
E --> E1[Zero-copy Ownership Transfer]:::success

<<<< END >>>>

<<<< ID: DIA_610d19cb >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[OpenFOAM Memory Management]:::explicit --> B[Exclusive Ownership<br/>autoPtr&lt;T&gt;]:::implicit
A --> C[Shared Ownership<br/>tmp&lt;T&gt;]:::implicit
A --> D[Reference Counting<br/>refCount Class]:::implicit
A --> E[Centralized Registry<br/>objectRegistry]:::implicit

B --> F[Automatic Cleanup]:::success
C --> G[Zero-copy Sharing]:::success
D --> G
E --> H[Object Lookup & Persistence]:::success

<<<< END >>>>

<<<< ID: DIA_4304f36f >>>>
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

<<<< END >>>>

<<<< ID: DIA_ed6481b3 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Debugging Checklist]:::explicit --> B[Check Pointer Ownership]:::implicit
A --> C[Verify refCount Status]:::implicit
A --> D[Inspect objectRegistry]:::implicit

B --> B1{Who deletes?}:::warning
B1 -->|Manual| E[Risk: Double Delete]:::warning
B1 -->|Smart Ptr| F[Safe: RAII]:::success

C --> C1{Circular Refs?}:::warning
C1 -->|Yes| G[Risk: Memory Leak]:::warning
C1 -->|No| H[Safe]:::success

D --> D1{Registered?}:::warning
D1 -->|Yes| I[Use isTemporary=false]:::implicit
D1 -->|No| J[Use isTemporary=true]:::implicit

<<<< END >>>>

<<<< ID: DIA_c23aaf3d >>>>
stateDiagram-v2
[*] --> Created: new volScalarField
Created --> Wrapped: tmp<T> tField(raw) [count=1]
Wrapped --> Shared: tCopy = tField [count=2]
Shared --> InUse: solve(*tField, tCopy)
InUse --> OneRefLeft: tCopy out of scope [count=1]
OneRefLeft --> Cleanup: tField out of scope [count=0]
Cleanup --> []: delete raw object

<<<< END >>>>

<<<< ID: DIA_cd291c5b >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[สร้างวัตถุ<br/>refCount = 0]:::explicit --> B[ref()<br/>refCount++]:::implicit
B --> C[ใช้งานวัตถุ<br/>refCount > 0]:::implicit
C --> D[unref()<br/>refCount--]:::implicit
D --> E{refCount == 0?}:::warning
E -->|No| C
E -->|Yes| F[ลบวัตถุ<br/>return true]:::success

<<<< END >>>>

<<<< ID: DIA_d6a42cdc >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Time Registry<br/>runTime]:::explicit --> B[Mesh Registry<br/>mesh]:::implicit
A --> C[Global Databases]:::implicit
B --> D[volScalarField: p]:::success
B --> E[volVectorField: U]:::success
B --> F[Boundary Conditions]:::success

subgraph "Parent Level"
A
end

subgraph "Child Level (Mesh-local)"
B
end

subgraph "Object Level"
D
E
F
end

<<<< END >>>>

<<<< ID: DIA_bf99c5a9 >>>>
classDiagram
class autoPtr {
-T* ptr_
+T* operator->()
+T& operator*()
+T* release()
}
class tmp {
    -T* ptr_
    -bool isTemporary_
    +bool isTmp()
    +T* ptr()
}

class refCount {
    -mutable int refCount_
    +void ref()
    +bool unref()
    +int count()
    +bool unique()
}

class objectRegistry {
    -const Time& time_
    -const objectRegistry& parent_
    -fileName dbDir_
    -mutable label event_
    -HashTable~Pair<bool>~ cacheTemporaryObjects_
    -bool cacheTemporaryObjectsSet_
    -HashSet~word~ temporaryObjects_
    +lookupObject() const
    +store()
}

class GeometricField {
    <<inherits>>
    refCount
}

autoPtr --> GeometricField : manages
tmp --> GeometricField : manages
GeometricField --|> refCount : inherits
objectRegistry --> GeometricField : stores

<<<< END >>>>

<<<< ID: DIA_6879a22f >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[tmp&lt;T&gt; Object]:::explicit --> B{isTemporary_?}:::warning
B -->|True| C[Temporary Mode]:::implicit
B -->|False| D[Persistent Mode]:::implicit

C --> E[Increments/Decrements<br/>Reference Count]:::implicit
E --> F[Delete Object when<br/>count == 0]:::success

D --> G[No Reference Counting]:::implicit
G --> H[Managed by objectRegistry]:::success

<<<< END >>>>

<<<< ID: DIA_c1ea2f8f >>>>
classDiagram
class GeometricField~Type, PatchField, GeoMesh~ {
+Field~Type~ internalField_
+FieldField~PatchField~Type~, GeoMesh~ boundaryField_
+GeoMesh& mesh_
+operator+=()
}
class Type {
<<Physical Quantity>>
scalar, vector, tensor
}
class PatchField {
<<Boundary Behavior>>
fixedValue, zeroGradient
}
class GeoMesh {
<<Discretization>>
fvMesh, faMesh, pointMesh
}
GeometricField --* Type
GeometricField --* PatchField
GeometricField --* GeoMesh

<<<< END >>>>

<<<< ID: DIA_e698a06d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[PDESolver<FieldType, Policy>]:::explicit --> B[Algorithm Layer<br/>Navier-Stokes, Heat Eq]:::implicit
B --> C{Policy Injection}:::warning
C --> D[GaussDiscretization<br/>Standard FVM]:::implicit
C --> E[LeastSquaresDiscretization<br/>Unstructured Reconstruction]:::implicit
C --> F[CustomResearchPolicy<br/>Experimental Scheme]:::implicit
D --> G[Optimized Machine Code]:::success
E --> G
F --> G

<<<< END >>>>

<<<< ID: DIA_fec0b9f8 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Template Blueprint<br/>GeometricField&lt;Type&gt;]:::explicit --> B{Compiler Instantiation}:::warning
B --> C[volScalarField<br/>Type = scalar]:::implicit
B --> D[volVectorField<br/>Type = vector]:::implicit
B --> E[volTensorField<br/>Type = tensor]:::implicit
C --> F[SIMD Optimized Code]:::success
D --> G[Vector Register Optimization]:::success
E --> H[Matrix Operation Optimization]:::success

<<<< END >>>>

<<<< ID: DIA_9cf9ea28 >>>>
classDiagram
class GeometricField {
+internalField_
+boundaryField_
}
class StatisticalField~Type~ {
-runningMean_
-runningVariance_
+updateStatistics()
+mean()
+variance()
}
GeometricField <|-- StatisticalField

<<<< END >>>>

<<<< ID: DIA_8286f8c9 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
GF[GeometricField]:::explicit --> IF[internalField_<br/>Field&lt;Type&gt;]:::implicit
GF --> BF[boundaryField_<br/>FieldField&lt;PatchField&lt;Type&gt;&gt;]:::implicit
GF --> M[mesh_<br/>const GeoMesh&]:::context
GF --> D[dimensions_<br/>dimensionSet]:::context
GF --> N[name_<br/>word]:::context

subgraph "Core Data"
IF
BF
end

subgraph "Context & Metadata"
M
D
N
end

<<<< END >>>>

<<<< ID: DIA_6e07365f >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Generic Template<br/>magSqr&lt;Type&gt;]:::explicit --> B{Type Check}:::warning
B -->|scalar| C[Specialization&lt;scalar&gt;<br/>return s * s]:::implicit
B -->|vector| D[Specialization&lt;vector&gt;<br/>return v.x*v.x + v.y*v.y + v.z*v.z]:::implicit
B -->|tensor| E[Specialization&lt;tensor&gt;<br/>return sum of all components squared]:::implicit

C --> F[Optimized FPU Instruction]:::success
D --> G[SIMD Vectorization]:::success
E --> H[Cache-friendly Matrix Op]:::success

<<<< END >>>>

<<<< ID: DIA_51dbe0d1 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Compiler Error Produced]:::explicit --> B{Length of Message}:::warning
B -->|> 100 lines| C[Template Instantiation Error]:::implicit
B -->|< 10 lines| D[Simple Syntax Error]:::implicit
C --> E[Look for 'candidate' and 'deduction failed']:::implicit
E --> F[Check Argument Types vs. Template Parameters]:::implicit
F --> G[Verify Header Inclusion & Namespaces]:::implicit
G --> H[Resolved Code]:::success

<<<< END >>>>

<<<< ID: DIA_0598d213 >>>>
classDiagram
class dragModel {
<<abstract>>
+Kd(alpha1, alpha2, U1, U2)*
}
class SchillerNaumann {
+Kd(alpha1, alpha2, U1, U2)
}
class MorsiAlexander {
+Kd(alpha1, alpha2, U1, U2)
}
class CustomDragModel {
+Kd(alpha1, alpha2, U1, U2)
}
dragModel <|-- SchillerNaumann
dragModel <|-- MorsiAlexander
dragModel <|-- CustomDragModel

<<<< END >>>>

<<<< ID: DIA_a252c2ea >>>>
sequenceDiagram
participant S as Solver Code
participant O as dragModel Object
participant V as dragModel vtable
participant I as SchillerNaumann::K()
Note over S: call drag.K()
S->>O: 1. Load __vptr
O->>V: 2. Lookup offset for K()
V->>S: 3. Return function pointer
S->>I: 4. Execute implementation
I-->>S: 5. Return result

<<<< END >>>>

<<<< ID: DIA_8756b398 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[1. Create .H File]:::explicit --> B[Inherit from Base Class]:::implicit
B --> C[Add TypeName Macro]:::implicit
C --> D[Declare Constructor]:::implicit
D --> E[Override Virtual Methods]:::implicit

E --> F[2. Create .C File]:::explicit
F --> G[Implement Constructor]:::implicit
G --> H[Implement Virtual Methods]:::implicit
H --> I[Add addToRunTimeSelectionTable]:::implicit

I --> J[3. Create Make/files]:::explicit
J --> K[Create Make/options]:::explicit
K --> L[4. Run wmake libso]:::implicit

L --> M{Compile Success?}:::warning
M -->|No| N[Debug Compilation Errors]:::explicit
N --> F

M -->|Yes| O[5. Test Registration]:::implicit
O --> P[listRegisteredModels]:::implicit
P --> Q{Model Found?}:::warning

Q -->|No| R[Check Macro Syntax]:::explicit
R --> I

Q -->|Yes| S[6. Use in Dictionary]:::success
S --> T[Run Simulation]:::success

<<<< END >>>>

<<<< ID: DIA_e5989f5a >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Public correct Method]:::explicit --> B[preCorrect Hook]:::implicit
B --> C[correctThermo Pure Virtual]:::explicit
C --> D[correctTurbulence Virtual]:::implicit
D --> E[correctSpecies Virtual]:::implicit
E --> F[postCorrect Hook]:::implicit
F --> G[updateFields Final]:::success

<<<< END >>>>

<<<< ID: DIA_798a0fe7 >>>>
classDiagram
class dictionary {
+lookup(word)
}
class volScalarField {
+operator+(field)
}
class phaseModel {
<<abstract>>
+rho()*
+mu()*
+Cp()*
+correct()
}
class purePhaseModel {
+rho()
+mu()
+Cp()
}
class mixturePhaseModel {
+rho()
+mu()
+Cp()
}
dictionary <|-- phaseModel
volScalarField <|-- phaseModel
phaseModel <|-- purePhaseModel
phaseModel <|-- mixturePhaseModel

<<<< END >>>>

<<<< ID: DIA_6b62e4e8 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[1. Math Formulation]:::explicit --> B[2. Class Inheritance]:::implicit
B --> C[3. Logic Implementation]:::implicit
C --> D[4. Factory Registration]:::implicit
D --> E[5. wmake Compilation]:::implicit
E --> F[6. Validation & Testing]:::success

subgraph "The Developer Workflow"
A
B
C
D
E
F
end

<<<< END >>>>

<<<< ID: DIA_2613a06e >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
A[powerLawViscosity.C]:::explicit --> B[EXE_INC: Include Paths]:::implicit
A --> C[EXE_LIBS: Link Libraries]:::implicit

B --> B1[finiteVolume/lnInclude]:::context
B --> B2[transportModels/lnInclude]:::context
B --> B3[thermophysicalModels/lnInclude]:::context

C --> C1[libfiniteVolume.so]:::context
C --> C2[libtransportModels.so]:::context
C --> C3[libthermophysicalModels.so]:::context

<<<< END >>>>

<<<< ID: DIA_c92d770f >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Start: powerLawViscosity]:::explicit --> B[Add Temperature Field Reference]:::implicit
B --> C[Implement Arrhenius Function]:::implicit
C --> D[Update mu Method: mu = f, gammaDot, T]:::implicit
D --> E[Add Numerical Safeguards for T]:::implicit
E --> F[Test with Non-isothermal Case]:::implicit
F --> G[Final: temperatureDependentPowerLaw]:::success

<<<< END >>>>

<<<< ID: DIA_061d6d90 >>>>
classDiagram
class viscosityModel {
<<abstract>>
+nu()*
+correct()*
}
class constantViscosity {
+nu()
+correct()
}
class powerLawViscosity {
+nu()
+correct()
}
viscosityModel <|-- constantViscosity
viscosityModel <|-- powerLawViscosity

<<<< END >>>>

<<<< ID: DIA_548d5159 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
classDef warning fill:#fff3e0,stroke:#e65100,stroke-width:2px
A[Error Encountered]:::explicit --> B{Error Type?}:::warning
B -->|Compilation| C[Check Make/options & Headers]:::implicit
B -->|Linking| D[Check Make/files & Symbols]:::implicit
B -->|Runtime: Unknown Type| E[Check libs entry & Registration]:::implicit
B -->|Runtime: Numerical| F[Check Math Logic & Constants]:::implicit

C --> G[Fixed Code]:::implicit
D --> G
E --> G
F --> G
G --> H[Success]:::success

<<<< END >>>>

<<<< ID: DIA_f9c9cea1 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
Step1[Step 1: Separate Compilation<br/>wmake libso]:::explicit --> Step2[Step 2: Dynamic Loading<br/>controlDict libs]:::implicit
Step2 --> Step3[Step 3: Dictionary Selection<br/>RASModel myCustomModel]:::implicit
Step3 --> Step4[Step 4: Factory Dispatch<br/>turbulenceModel::New]:::implicit
Step4 --> Step5[Step 5: Execution<br/>turbulence->correct()]:::success

<<<< END >>>>

<<<< ID: DIA_8c2df45a >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px
A[Source Directories]:::explicit --> B{wmakeLnInclude}:::implicit
B --> C[lnInclude/ Directory]:::context

C --> D[Link to model.H]:::context
C --> E[Link to utility.H]:::context
C --> F[Link to baseClass.H]:::context

G[Compiler]:::implicit -->|Include Path: -IlnInclude| C
G --> D
G --> E
G --> F

<<<< END >>>>

<<<< ID: DIA_bc8bf176 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
A[Case Dictionary]:::explicit --> B[RTS Registry]:::implicit
B --> C[Factory Method]:::implicit
C --> D[Custom Model Object]:::success
D --> E[Solver Loop]:::implicit
E --> F[Physics Results]:::success

subgraph "The Integration Chain"
B
C
D
end

<<<< END >>>>

<<<< ID: DIA_1ae0aaab >>>>
graph LR
classDef cv fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
classDef flux fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
subgraph "Computational Domain"
    CV1["Control Volume 1"]:::cv
    CV2["Control Volume 2"]:::cv
    CV3["Control Volume 3"]:::cv
    CV4["Control Volume 4"]:::cv
    CV5["Control Volume 5"]:::cv
    CV6["Control Volume 6"]:::cv
end

subgraph "Fluxes Across Boundaries"
    F12["Flux 1→2"]:::flux
    F23["Flux 2→3"]:::flux
    F34["Flux 3→4"]:::flux
    F45["Flux 4→5"]:::flux
    F56["Flux 5→6"]:::flux
    F61["Flux 6→1"]:::flux
    F13["Flux 1→3"]:::flux
    F24["Flux 2→4"]:::flux
    F35["Flux 3→5"]:::flux
    F46["Flux 4→6"]:::flux
end

CV1 -- "Mass, Momentum, Energy" --> F12
F12 --> CV2
CV2 --> F23
F23 --> CV3
CV3 --> F34
F34 --> CV4
CV4 --> F45
F45 --> CV5
CV5 --> F56
F56 --> CV6
CV6 --> F61
F61 --> CV1

CV1 -.-> F13
F13 -.-> CV3
CV2 -.-> F24
F24 -.-> CV4
CV3 -.-> F35
F35 -.-> CV5
CV4 -.-> F46
F46 -.-> CV6

<<<< END >>>>

<<<< ID: DIA_bd6c027e >>>>
graph LR
classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
subgraph "Continuous Domain"
    A["Continuous Fluid<br/>Domain"]:::process --> B["Mathematical<br/>Fields"]:::process
    B --> C["Differential<br/>Equations"]:::process
    C --> D["Analytical<br/>Solutions"]:::process
end

subgraph "Discretized Domain"
    E["Control Volume<br/>Grid"]:::storage --> F["Computational<br/>Mesh"]:::storage
    F --> G["Cell-centered<br/>Values"]:::storage
    G --> H["Algebraic<br/>Equations"]:::storage
    H --> I["Numerical<br/>Solution"]:::storage
end

A -.->|Discretization| E
D -.->|Transformation| H

subgraph "Key Relationships"
    J["Flux Conservation<br/>at Cell Faces"]:::decision
    K["Local Mass<br/>Balance"]:::decision
    L["Numerical<br/>Integration"]:::decision
end

F --> J
J --> K
K --> L

<<<< END >>>>

<<<< ID: DIA_ce62df07 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
subgraph Fluxes
    In["Mass Influx<br/>ρ u S"]:::explicit
    Out["Mass Outflux<br/>-(ρ u S)_out"]:::explicit
end

In --> Balance["Mass Balance<br/>Net Flux"]:::implicit
Out --> Balance

Balance --> Accum["Accumulation<br/>∂ρ/∂t V"]:::implicit

Accum --> Eq["Continuity Equation<br/>∂ρ/∂t + ∇·(ρu) = 0"]:::success

<<<< END >>>>

<<<< ID: DIA_5b08afd1 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffebee,stroke:#b71c1c,stroke-width:2px
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
subgraph Forces["Forces Acting on Element"]
    P["Pressure Forces<br/>-∇p"]:::explicit
    V["Viscous Forces<br/>∇·τ"]:::explicit
    B["Body Forces<br/>ρg"]:::explicit
end

P --> Net["Net Force<br/>ΣF"]:::implicit
V --> Net
B --> Net

Net -->|Newton's 2nd Law| Acc["Acceleration<br/>ρ Du/Dt"]:::implicit

Acc --> Inertia["Inertial Response<br/>Unsteady + Convective"]:::success

<<<< END >>>>

<<<< ID: DIA_ba358f80 >>>>
graph LR
classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
A["Control Volume<br/>Energy Balance"]:::process --> B["<b>Energy In</b><br/>ρcₚ u·∇T"]:::process
B --> C["<b>Energy Storage</b><br/>ρcₚ ∂T/∂t"]:::process
A --> D["<b>Conduction</b><br/>k∇²T"]:::process
C --> E["<b>Temperature Field</b><br/>T(x,y,z,t)"]:::storage
D --> E

F["<b>Heat Transfer Mechanisms</b>"]:::decision --> G["<b>Convection</b><br/>Fluid movement"]:::decision
F --> H["<b>Conduction</b><br/>Molecular diffusion"]:::decision
F --> I["<b>Generation</b><br/>Source terms Q"]:::decision

G --> J["<b>Transport Term</b><br/>ρcₚ u·∇T"]:::process
H --> K["<b>Diffusion Term</b><br/>k∇²T"]:::process
I --> L["<b>Source Term</b><br/>Q/(ρcₚ)"]:::process

J --> E
K --> E
L --> E

<<<< END >>>>

<<<< ID: DIA_ebbd3de7 >>>>
graph TD
%% Layout: Center the CV, Inputs top, Outputs bottom
subgraph Control_Volume ["Control Volume (Finite Volume)"]
direction TB
CV_Node["Cell P

(State State ρ, Y_i)"]:::implicit
end
subgraph Fluxes ["Fluxes & Sources (Changes)"]
    direction LR
    Conv_In["Convective Flux In<br/>ρ u Y_i"]:::explicit
    Diff_In["Diffusion Flux In<br/>J_i"]:::explicit
    Source["Reaction Source<br/>ω_i"]:::explicit
end

subgraph Conservation ["Conservation Equation"]
    Eq["∂(ρY_i)/∂t + ∇·(ρuY_i) = -∇·J_i + ω_i"]:::implicit
end

%% Connections
Conv_In -->|Transport| CV_Node
Diff_In -->|Gradient| CV_Node
Source -->|Production/Destruction| CV_Node

CV_Node -->|Resulting Balance| Eq

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#666;

<<<< END >>>>

<<<< ID: DIA_f18540fa >>>>
graph TD
%% Zero Split-Attention: Inputs at top, calculation flow down
subgraph Inputs ["Input State Variables"]
P["Pressure (p)"]:::explicit
T["Temperature (T)"]:::explicit
R["Gas Constant (R)"]:::implicit
end
subgraph Calculation ["EOS Logic: ρ = p / (R*T)"]
    direction TB
    Mult(("&times;")):::context
    Div(("&divide;")):::context
end

subgraph Output ["Derived Property"]
    Rho["Density (ρ)"]:::implicit
end

%% Flow
R --> Mult
T --> Mult
P --> Div
Mult -->|RT| Div
Div -->|Result| Rho

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_712e162b >>>>
graph LR
%% Spatial Layout: Linear stencil
subgraph Stencil ["Finite Volume Stencil"]
direction LR
    %% Cells (Implicit/Stable)
    C_WW["CV i-2"]:::implicit
    C_W["CV i-1"]:::implicit
    C_P["CV i"]:::implicit
    C_E["CV i+1"]:::implicit
    C_EE["CV i+2"]:::implicit

    %% Fluxes (Explicit/Interface)
    F_WW["Flux<br/>i-3/2"]:::explicit
    F_W["Flux<br/>i-1/2"]:::explicit
    F_E["Flux<br/>i+1/2"]:::explicit
    F_EE["Flux<br/>i+3/2"]:::explicit
end

%% Connections
C_WW --- F_WW --- C_W
C_W --- F_W --- C_P
C_P --- F_E --- C_E
C_E --- F_EE --- C_EE

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_49617e5f >>>>
graph LR
%% Spatial Layout: 1D Grid
subgraph Mesh ["1D Computational Mesh"]
direction LR
N_W["Node W

(West Neighbor)"]:::implicit
Face_w["Face w

(Interface)"]:::explicit
N_P["Node P

(Current Cell)"]:::implicit
Face_e["Face e

(Interface)"]:::explicit
N_E["Node E

(East Neighbor)"]:::implicit
end
subgraph Coefficients ["Matrix Coefficients"]
    direction TB
    aW["a_W (West Coeff)"]:::context
    aP["a_P (Diagonal Coeff)"]:::context
    aE["a_E (East Coeff)"]:::context
end

%% Semantic Coupling
N_W -.->|Contributes via| aW
N_P -.->|Contributes via| aP
N_E -.->|Contributes via| aE

%% Structural Connections
N_W --- Face_w --- N_P --- Face_e --- N_E

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_569d545e >>>>
graph LR
%% Spatial Layout: P -> Face -> N
subgraph Owner ["Owner Cell"]
P["Cell P

φ = 10"]:::implicit
end
subgraph Interface ["Flux Interface"]
    F["Face f<br/>Flux = ρ·u·A"]:::explicit
end

subgraph Neighbor ["Neighbor Cell"]
    N["Cell N<br/>φ = 20"]:::implicit
end

%% Connections
P -->|Convection u > 0| F
F -->|Transport| N

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_b31c556b >>>>
graph TD
%% Semantic Grouping
subgraph Geometry ["Cell Centered Geometry"]
direction TB
    subgraph Cells [Control Volumes]
        P["Owner Cell P<br/>(Center x_P)"]:::implicit
        N["Neighbor Cell N<br/>(Center x_N)"]:::implicit
    end

    subgraph Interface [Face Properties]
        f["Face f<br/>(Center x_f)"]:::explicit
        Sf["Surface Vector S_f<br/>(Normal * Area)"]:::explicit
    end
end

%% Spatial Relationship
P ---|Distance d_Pf| f
f ---|Distance d_fN| N

%% Property attachment
f -.- Sf

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_dcff32db >>>>
graph LR
%% Spatial Layout: P -> f -> N with vectors annotated
subgraph Mesh ["Finite Volume Mesh"]
P["Cell P

(Owner)"]:::implicit
f["Face f

(Interface)"]:::explicit
N["Cell N

(Neighbor)"]:::implicit
end
subgraph Vectors ["Geometric Vectors"]
    dPN["d_PN (P to N)"]:::context
    Sf["S_f (Face Normal Area)"]:::context
    dPf["d_Pf (P to Face)"]:::context
end

%% Connections
P --- f --- N

%% Vector overlays (Semantic Coloring)
P -.->|Vector| dPN -.-> N
P -.->|Vector| dPf -.-> f
f -.->|Vector| Sf

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#e0f7fa,stroke:#006064,stroke-width:1px,stroke-dasharray: 5 5;

<<<< END >>>>

<<<< ID: DIA_c8356c80 >>>>
graph TD
%% Process Flow: From Field to Matrix
subgraph Data ["Field Data"]
VolField["Volume Field

(Cell Centers)"]:::implicit
SurfField["Surface Field

(Face Centers)"]:::explicit
end
subgraph Discretization ["Discretization Steps"]
    Interp["Interpolation<br/>(Linear/Upwind/TVD)"]:::context
    Grad["Gradient Calc<br/>(Gauss Theorem)"]:::context
end

subgraph Matrix ["Linear System (Ax=b)"]
    Diag["Diagonal A_D"]:::implicit
    OffDiag["Off-Diagonal A_O"]:::implicit
    Source["Source Vector b"]:::explicit
end

%% Flow
VolField --> Interp --> SurfField
SurfField --> Grad -->|Matrix Assembly| Matrix
Grad --> Diag
Grad --> OffDiag
Grad --> Source

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_1ef894ea >>>>
graph TD
%% Star Topology / Stencil
subgraph Center ["Diagonal Element"]
P["Cell P

(a_P)"]:::implicit
end
subgraph Neighbors ["Off-Diagonal Elements"]
    N1["Neighbor 1<br/>(a_N1)"]:::explicit
    N2["Neighbor 2<br/>(a_N2)"]:::explicit
    N3["Neighbor 3<br/>(a_N3)"]:::explicit
    N4["Neighbor 4<br/>(a_N4)"]:::explicit
end

%% Connections (Faces)
N1 <-->|Face 1| P
N2 <-->|Face 2| P
N3 <-->|Face 3| P
N4 <-->|Face 4| P

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_54f39b96 >>>>
graph TD
%% Layout: Linear process loop
Assembly["Matrix Assembly

(Ax = b)"]:::implicit
subgraph SolverLoop ["Iterative Solver"]
    Init["Initialize"]:::context
    Iter["Iteration k"]:::explicit
    ResCalc["Compute Residual"]:::explicit
    Check{"Converged?"}:::context
end

Solution["Final Solution"]:::implicit

%% Flow
Assembly --> Init --> Iter --> ResCalc --> Check
Check -- No --> Iter
Check -- Yes --> Solution

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_f84998f4 >>>>
graph TD
%% Hierarchy: Domain -> CV -> Balance
subgraph Domain ["Computational Domain"]
CV["Control Volume (Cell)"]:::implicit
Faces["Bounding Faces"]:::explicit
end
subgraph Balance ["Conservation Balance"]
    InFlux["Flux In"]:::explicit
    OutFlux["Flux Out"]:::explicit
    Source["Source Term"]:::explicit
    Net["Net Change (d/dt)"]:::implicit
end

%% Logic
CV --- Faces
Faces --> InFlux
Faces --> OutFlux
InFlux & OutFlux & Source --> Net

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_3b8b0bcb >>>>
graph LR
%% Transformation: Continuous -> Discrete
subgraph Continuous ["Continuous Physics"]
PDE["Partial Differential Eq"]:::implicit
Field_C["Continuous Fields"]:::implicit
end
subgraph Discretization ["Discretization"]
    Mesh["Mesh / Grid"]:::explicit
    Disc["Algebraic Approximation"]:::context
end

subgraph Discrete ["Discrete Math"]
    Matrix["System Ax=b"]:::implicit
    Field_D["Cell Centered Values"]:::implicit
end

%% Flow
PDE -->|Discretize| Disc
Field_C -->|Sample| Mesh
Mesh --> Disc --> Matrix --> Field_D

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_62056859 >>>>
graph TD
%% Inheritance Hierarchy
subgraph Core ["Core Mesh Classes"]
polyMesh["polyMesh

(Topology & Shapes)"]:::implicit
fvMesh["fvMesh

(Finite Volume Methods)"]:::implicit
dynamicFvMesh["dynamicFvMesh

(Moving/Topological Changes)"]:::explicit
end
%% Relations
polyMesh -->|Inheritance| fvMesh
fvMesh -->|Inheritance| dynamicFvMesh

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_3add5ac2 >>>>
graph LR
%% Timeline
TimeCont["Continuous Time t"]:::implicit
subgraph DiscreteSteps ["Time Steps"]
    t0["t_0"]:::context
    dt1["&Delta;t"]:::explicit
    t1["t_1"]:::implicit
    dt2["&Delta;t"]:::explicit
    t2["t_2"]:::implicit
end

TimeCont --> t0 --> dt1 --> t1 --> dt2 --> t2

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_6bc08fde >>>>
graph TD
%% Taxonomy of Schemes
Root["Time Integration Schemes"]:::implicit
subgraph Explicit ["Explicit Methods"]
    ExpEuler["Explicit Euler"]:::explicit
    PropExp["First Order<br/>Conditionally Stable (CFL)"]:::context
end

subgraph Implicit ["Implicit Methods"]
    ImpEuler["Implicit Euler"]:::implicit
    PropImp["First Order<br/>Unconditionally Stable"]:::context
    
    CN["Crank-Nicolson"]:::implicit
    PropCN["Second Order<br/>Marginally Stable"]:::context
end

Root --> Explicit
Root --> Implicit

ExpEuler --- PropExp
ImpEuler --- PropImp
CN --- PropCN

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_76aa7290 >>>>
graph TD
%% Logic of ddt contribution
Term["Time Derivative

∂(ρφ)/∂t"]:::implicit
subgraph Discretization ["Discretization"]
    Euler["Euler Scheme"]:::context
    Eq["(ρφ_new - ρφ_old) / &Delta;t"]:::explicit
end

subgraph MatrixContrib ["Matrix Contributions"]
    Diag["Diagonal (a_P)<br/>Add: ρV/&Delta;t"]:::implicit
    Source["Source (b)<br/>Add: (ρV/&Delta;t)*φ_old"]:::explicit
end

Term --> Euler --> Eq
Eq --> Diag
Eq --> Source

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_db422d76 >>>>
graph TD
%% Algorithm Flowcharts
subgraph SIMPLE ["SIMPLE (Steady)"]
S_Pred["Momentum Predictor"]:::implicit
S_Pres["Pressure Correction"]:::explicit
S_Turb["Turbulence Update"]:::context
end
subgraph PISO ["PISO (Transient)"]
    P_Pred["Momentum Predictor"]:::implicit
    P_Loop["Pressure Loop (2-3x)"]:::explicit
    P_Turb["Turbulence Update"]:::context
end

subgraph PIMPLE ["PIMPLE (Hybrid)"]
    Pi_Outer["Outer Loop"]:::context
    Pi_Pred["Momentum Predictor"]:::implicit
    Pi_Inner["Inner PISO Loop"]:::explicit
end

%% Internal flows implied by proximity in subgraphs
S_Pred --> S_Pres --> S_Turb
P_Pred --> P_Loop --> P_Turb
Pi_Outer --> Pi_Pred --> Pi_Inner

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_10448eb1 >>>>
graph TD
%% Source Term Linearization
Source["Source Term S(φ)"]:::implicit
subgraph Explicit ["Explicit Treatment"]
    Exp["S_u (Constant part)"]:::explicit
    NoteExp["Added to Source Vector b"]:::context
end

subgraph Implicit ["Implicit Treatment"]
    Imp["S_p (Linear part)"]:::implicit
    NoteImp["Added to Diagonal a_P<br/>Must be negative for stability"]:::context
end

Source -->|Linearization| Exp
Source -->|Linearization| Imp
Exp --- NoteExp
Imp --- NoteImp

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_7345a3de >>>>
graph LR
%% Mind map style
BestPractices["CFD Best Practices"]:::implicit
subgraph Mesh ["Mesh Quality"]
    Ortho["Non-Orthogonality < 50°"]:::explicit
    Skew["Skewness < 0.5"]:::explicit
end

subgraph Numerics ["Numerics"]
    Time["Courant Number < 1"]:::explicit
    Schemes["Bounded Schemes for div"]:::implicit
end

subgraph Setup ["Setup"]
    BCs["Robust BCs"]:::implicit
    Init["Reasonable Initialization"]:::context
end

BestPractices --> Mesh
BestPractices --> Numerics
BestPractices --> Setup

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_134a42b9 >>>>
graph TD
%% Geometric Relation
subgraph Connection ["Cell Connectivity"]
P["Cell P"]:::implicit
N["Cell N"]:::implicit
d["Vector d (P to N)"]:::context
end
subgraph FaceGeometry ["Face Geometry"]
    f["Face f"]:::implicit
    n["Normal Vector n"]:::explicit
end

subgraph Analysis ["Non-Orthogonality"]
    Angle["Angle θ between d and n"]:::explicit
    Limit["Limit: θ < 70°"]:::context
    Correction["Non-Ortho Correction Required"]:::explicit
end

d & n --> Angle
Angle --> Limit --> Correction

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_0c7d3404 >>>>
graph TD
%% Decision Tree
Pe{"Peclet Number (Pe)"}:::context
subgraph DiffusionDominated ["Pe < 2 (Diffusion Dominated)"]
    Central["Central Differencing"]:::implicit
    Acc["High Accuracy"]:::context
end

subgraph Balanced ["2 < Pe < 10"]
    TVD["TVD / Limited Linear"]:::implicit
    Stab["Balanced Stability"]:::context
end

subgraph ConvectionDominated ["Pe > 10 (Convection Dominated)"]
    Upwind["Upwind"]:::explicit
    Diss["Dissipative / Stable"]:::context
end

Pe --> DiffusionDominated
Pe --> Balanced
Pe --> ConvectionDominated

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_121bb062 >>>>
graph TD
%% Decomposition
Domain["Global Domain"]:::implicit
subgraph Decomp ["Decomposition"]
    Proc0["Processor 0"]:::explicit
    Proc1["Processor 1"]:::explicit
    Proc2["Processor 2"]:::explicit
    Proc3["Processor 3"]:::explicit
end

subgraph Comm ["Communication"]
    MPI["MPI Boundaries<br/>(Halo Cells)"]:::context
end

Domain --> Decomp
Proc0 & Proc1 & Proc2 & Proc3 <--> MPI

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_6d5cee0e >>>>
graph TD
%% Troubleshooting Logic
Crash["Simulation Crash"]:::explicit
subgraph Diagnostics ["Diagnosis"]
    Div["Divergence?"]:::context
    BC["BC Error?"]:::context
    Mesh["Bad Mesh?"]:::context
end

subgraph Actions ["Corrective Actions"]
    Relax["Increase Under-Relaxation"]:::implicit
    DT["Reduce Time Step"]:::implicit
    Schemes["Use Upwind Schemes"]:::implicit
    FixMesh["CheckNonOrtho / Refine"]:::implicit
end

Crash --> Div & BC & Mesh
Div --> Relax & DT & Schemes
Mesh --> FixMesh

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_82709631 >>>>
graph LR
%% Grid Convergence
subgraph Meshes ["Mesh Levels"]
M1["Coarse"]:::implicit
M2["Medium"]:::implicit
M3["Fine"]:::implicit
end
subgraph Analysis ["Richardson Extrapolation"]
    Result["Key Variable &phi;"]:::context
    GCI["Grid Convergence Index"]:::explicit
    Exact["Extrapolated Value"]:::implicit
end

M1 & M2 & M3 --> Result --> GCI --> Exact

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_86120e4a >>>>
graph TD
%% SIMPLE Loop
Start((Start)):::context
subgraph Loop ["Iteration"]
    Pred["Momentum Predictor (UEqn)"]:::explicit
    Pres["Pressure Equation (pEqn)"]:::implicit
    Corr["Momentum Correction"]:::context
end

End((End)):::context

Start --> Loop --> End

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_19889a33 >>>>
graph TD
%% PISO Loop
TimeStep["New Time Step"]:::context
subgraph Predictor ["Predictor Step"]
    Mom["Solve Momentum"]:::explicit
end

subgraph PISO_Loop ["PISO Loop (Correctors)"]
    Press["Solve Pressure"]:::implicit
    Vel["Correct Velocity"]:::context
    Repeat["Repeat 2-3 times"]:::context
end

TimeStep --> Predictor --> PISO_Loop

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_680add8c >>>>
graph TD
%% Hierarchy: Domain -> CV -> Balance (Same as 41ee07fe)
subgraph Domain ["Computational Domain"]
CV["Control Volume (Cell)"]:::implicit
Faces["Bounding Faces"]:::explicit
end
subgraph Balance ["Conservation Balance"]
    Fluxes["Fluxes (Mass/Mom/Energy)"]:::explicit
    Source["Source Terms"]:::explicit
    Time["Unsteady Term"]:::implicit
end

CV --- Faces
Faces --> Fluxes
Fluxes & Source & Time --> Balance

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_c8ab18cd >>>>
graph LR
%% Force Balance
subgraph Forces ["Applied Forces"]
Press["Pressure (-∇p)"]:::explicit
Visc["Viscous (∇·τ)"]:::explicit
Body["Body (ρg)"]:::explicit
end
subgraph Motion ["Fluid Response"]
    Net["Net Force"]:::context
    Acc["Acceleration (Du/Dt)"]:::implicit
end

Press & Visc & Body --> Net --> Acc

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_3e7e095d >>>>
graph TD
%% Same as 8e806cf7
subgraph Geometry ["Cell Centered Geometry"]
direction TB
    subgraph Cells [Control Volumes]
        P["Owner P"]:::implicit
        N["Neighbor N"]:::implicit
    end

    subgraph Interface [Face Properties]
        f["Face f"]:::explicit
        Sf["Area Vector S_f"]:::explicit
    end
end

P --- f --- N
f -.- Sf

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_44e71ca7 >>>>
graph TD
%% Same as fff42db2
subgraph Matrix ["Matrix Row"]
Diag["Diagonal a_P"]:::implicit
Off["Off-Diagonal a_N"]:::explicit
Src["Source b"]:::explicit
end
Diag --> Off & Src

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_5dcae4f6 >>>>
graph TD
%% Same as 6d62d99b
subgraph VectorCheck ["Orthogonality Check"]
d["Vector PN"]:::implicit
S["Vector Sf"]:::explicit
Theta["Angle θ"]:::context
end
d & S --> Theta
Theta -->|High| Correction["Correction Terms"]:::explicit

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_5e807302 >>>>
graph LR
%% Pipe Flow BCs
subgraph Boundaries ["Boundary Conditions"]
Inlet["Inlet

(fixedValue U)"]:::explicit
Outlet["Outlet

(fixedValue p)"]:::explicit
Wall["Wall

(noSlip)"]:::implicit
end
subgraph Flow ["Flow Domain"]
    Pipe["Fluid Volume"]:::context
end

Inlet --> Pipe --> Outlet
Wall -.->|Constraint| Pipe

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_4b912010 >>>>
graph LR
%% Symmetry vs Slip
subgraph Symmetry ["Symmetry Plane"]
SymCond["Normal Vel = 0

Normal Grad = 0"]:::implicit
end
subgraph Slip ["Slip Wall"]
    SlipCond["Normal Vel = 0<br/>Shear Stress = 0"]:::explicit
end

SymCond -->|Mirror| Physics1["Virtual Mirror"]:::context
SlipCond -->|Frictionless| Physics2["Smooth Wall"]:::context

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_bbbdf813 >>>>
graph TD
%% Mathematical Conflict
subgraph Conflict ["Over-Specification"]
Inlet["Inlet: Fixed U"]:::explicit
Outlet["Outlet: Fixed U (?)"]:::explicit
Problem["Mass Conservation Violation"]:::explicit
end
subgraph Solution ["Correct Approach"]
    InletFixed["Inlet: Fixed U"]:::implicit
    OutletOpen["Outlet: ZeroGradient U<br/>Fixed Pressure"]:::implicit
end

Inlet & Outlet --> Problem
Problem -.->|Fix| Solution

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_92d463d6 >>>>
graph LR
%% Domain Extension
subgraph BadDomain ["Problematic Domain"]
Out1["Outlet (Too Close)"]:::explicit
Recirc["Backflow/Instability"]:::explicit
end
subgraph GoodDomain ["Extended Domain"]
    Ext["Extension Length"]:::implicit
    Out2["Outlet (Developed)"]:::implicit
    Stable["Stable Outflow"]:::implicit
end

Out1 --> Recirc
Recirc -.->|Remedy| Ext
Ext --> Out2 --> Stable

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_0a2a990e >>>>
graph LR
%% Backward Facing Step
subgraph Geometry ["Geometry"]
Inlet["Inlet"]:::explicit
Step["Step Corner"]:::context
Wall["Walls"]:::implicit
Outlet["Outlet"]:::explicit
end
subgraph Physics ["Flow Physics"]
    Sep["Separation Point"]:::explicit
    Recirc["Recirculation Zone"]:::explicit
    Reattach["Reattachment"]:::implicit
end

Inlet --> Step --> Sep --> Recirc --> Reattach --> Outlet
Wall -.-> Physics

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_e20f7458 >>>>
graph TD
%% Wall Functions
subgraph Input ["Mesh Parameters"]
y_dist["Wall Distance y"]:::context
y_plus["y+ Value"]:::explicit
end
subgraph Logic ["Wall Function Logic"]
    Viscous["Viscous Sublayer<br/>(y+ < 5)"]:::implicit
    LogLaw["Log Law Region<br/>(30 < y+ < 300)"]:::implicit
    Buffer["Buffer Layer<br/>(Avoid!)"]:::explicit
end

subgraph Output ["Boundary Condition"]
    Nut["Calculated nut"]:::implicit
    Shear["Wall Shear Stress"]:::implicit
end

y_dist --> y_plus
y_plus --> Viscous & LogLaw & Buffer
Viscous & LogLaw --> Nut --> Shear

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_6809c833 >>>>
graph TD
%% BC Types
subgraph Dirichlet ["Fixed Value (Dirichlet)"]
InletV["Inlet Velocity"]:::explicit
WallT["Wall Temp"]:::explicit
end
subgraph Neumann ["Zero Gradient (Neumann)"]
    OutletV["Outlet Velocity"]:::implicit
    WallP["Wall Pressure"]:::implicit
end

subgraph Mixed ["Mixed / Special"]
    Slip["Slip Wall"]:::context
    InletOutlet["InletOutlet"]:::context
end

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_5494ad1b >>>>
graph LR
%% Profiles
subgraph Inlet ["Inlet Profiles"]
Uniform["Uniform Block"]:::implicit
Parabolic["Parabolic (Laminar)"]:::implicit
Power["Power Law (Turbulent)"]:::implicit
Table["CSV/Table Data"]:::explicit
end
%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_058134a5 >>>>
graph LR
%% P-V Coupling
Inlet["Inlet (Fix U, Grad P)"]:::explicit
Domain["Domain (Coupling)"]:::implicit
Outlet["Outlet (Fix P, Grad U)"]:::explicit
Inlet --> Domain --> Outlet

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_81a8f465 >>>>
graph TD
%% Slip Detail
subgraph SlipCond ["Slip Condition"]
Normal["Normal Component

U · n = 0"]:::implicit
Tangential["Tangential Component

Grad U = 0"]:::explicit
end
%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_dc670f41 >>>>
graph LR
%% Cyclic
subgraph Patch1 ["Cyclic Patch 1"]
Face1["Faces"]:::explicit
end
subgraph Patch2 ["Cyclic Patch 2"]
    Face2["Faces"]:::explicit
end

subgraph Transform ["Transformation"]
    Map["Topology Mapping"]:::implicit
    Rot["Rotation/Translation"]:::implicit
end

Face1 <-->|Coupled| Map <--> Face2

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_c91820e3 >>>>
graph LR
%% BC Taxonomy
Base["Boundary Conditions"]:::implicit
Basic["Basic"]:::context
Basic --> Fix["fixedValue"]:::explicit
Basic --> Zero["zeroGradient"]:::implicit

Special["Derived"]:::context
Special --> IO["inletOutlet"]:::explicit
Special --> Wall["wallFunctions"]:::implicit
Special --> Cyc["cyclic"]:::context

Base --> Basic & Special

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_b9a209d3 >>>>
graph TD
%% inletOutlet Logic
subgraph Logic ["inletOutlet Logic"]
Calc["Calculate Flux φ"]:::context
Check{"φ > 0 ?

(Outflow)"}:::explicit
    Zero["Apply zeroGradient"]:::implicit
    Fixed["Apply fixedValue"]:::explicit
end

Calc --> Check
Check -->|Yes| Zero
Check -->|No| Fixed

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_3de378f8 >>>>
graph LR
%% Cyclic Duplicate - same structure
P1["Patch 1"]:::explicit
Trans["Transform"]:::implicit
P2["Patch 2"]:::explicit
P1 <--> Trans <--> P2

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_e8ebfc03 >>>>
graph TD
%% BL Structure
Wall["Wall Surface"]:::explicit
subgraph Layers ["Boundary Layer Structure"]
    Visc["Viscous Sublayer<br/>Linear u+=y+"]:::implicit
    Buff["Buffer Layer<br/>Transition"]:::context
    Log["Log-Law Region<br/>Logarithmic"]:::implicit
end

Free["Free Stream"]:::explicit

Wall --> Visc --> Buff --> Log --> Free

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_a46eeb59 >>>>
graph LR
%% CHT
subgraph Fluid ["Fluid Domain"]
F_Cell["Fluid Cell"]:::implicit
F_T["Temp T_f"]:::context
end
subgraph Interface ["Coupled Interface"]
    C_Cond["Continuity: T_f = T_s"]:::explicit
    C_Flux["Flux: k_f&nabla;T = k_s&nabla;T"]:::explicit
end

subgraph Solid ["Solid Domain"]
    S_Cell["Solid Cell"]:::implicit
    S_T["Temp T_s"]:::context
end

F_Cell --> Interface --> S_Cell

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_54040db3 >>>>
graph TD
%% Overset
subgraph Background ["Background Mesh"]
BgCells["Fluid Cells"]:::implicit
Hole["Hole (Inactive)"]:::context
end
subgraph Overset ["Overset Mesh"]
    OvCells["Fluid Cells"]:::implicit
    Fringe["Fringe (Interpolated)"]:::explicit
end

BgCells -- "Interpolates to" --> Fringe
OvCells -- "Masks" --> Hole

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_444cbfc6 >>>>
graph LR
%% Timeline Profile
Start["t=0"]:::context
RampUp["Ramp Up"]:::explicit
Steady["Steady State"]:::implicit
Osc["Oscillation"]:::explicit
RampDown["Ramp Down"]:::explicit
End["t=End"]:::context
Start --> RampUp --> Steady --> Osc --> RampDown --> End

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_ffbe30a2 >>>>
graph TD
%% Thai BCs
Root["เงื่อนไขขอบเขต (Boundary Conditions)"]:::implicit
subgraph Variables ["ตัวแปร"]
    U["ความเร็ว (U)"]:::explicit
    P["ความดัน (p)"]:::explicit
    Turb["ความปั่นป่วน (k, ε)"]:::explicit
end

subgraph Types ["ประเภท"]
    FV["fixedValue"]:::implicit
    ZG["zeroGradient"]:::implicit
    IO["inletOutlet"]:::implicit
    WF["Wall Functions"]:::implicit
end

Root --> Variables --> Types

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_66257ad7 >>>>
graph TD
%% Thai Slip
Slip["เงื่อนไข Slip"]:::implicit
subgraph Components ["องค์ประกอบ"]
    Norm["แนวฉาก: U·n = 0"]:::explicit
    Tang["แนวสัมผัส: ∂U/∂n = 0"]:::explicit
end

Slip --> Components

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_4d74bb28 >>>>
graph TD
%% Thai Wall Layers
Wall["ผนัง (Wall)"]:::explicit
Visc["ชั้นย่อยหนืด (Viscous Sublayer)"]:::implicit
Log["ชั้นลอการิทึม (Log-Law)"]:::implicit
Outer["ชั้นนอก (Outer Layer)"]:::context
Wall --> Visc --> Log --> Outer

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_a4ae02ca >>>>
graph TD
%% Math Forms
subgraph MathTypes ["Mathematical Definitions"]
Dir["Dirichlet (Value)"]:::explicit
Neu["Neumann (Gradient)"]:::implicit
Rob["Robin (Mixed)"]:::context
end
subgraph Physical ["Physical BCs"]
    Inlet["Inlet"]:::explicit
    Outlet["Outlet"]:::implicit
    Wall["Wall"]:::context
end

Dir -.-> Inlet
Neu -.-> Outlet
Dir -.-> Wall

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_5527c528 >>>>
graph TD
%% PDE Classification
subgraph Equations ["PDE Types"]
Ell["Elliptic

(Equilibrium)"]:::implicit
Par["Parabolic

(Diffusion)"]:::implicit
Hyp["Hyperbolic

(Wave/Advection)"]:::explicit
end
subgraph Requirements ["BC Requirements"]
    AllBounds["BCs on All Boundaries"]:::implicit
    Open["Open Boundaries Allowed"]:::explicit
end

Ell --> AllBounds
Par --> Open
Hyp --> Open

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_6b676523 >>>>
graph TD
%% OF Class Hierarchy
Base["fvPatchField"]:::implicit
subgraph Primitive ["Primitive Types"]
    FV["fixedValue"]:::explicit
    FG["fixedGradient"]:::explicit
    MX["mixed"]:::explicit
end

subgraph Derived ["Derived Types"]
    IO["inletOutlet"]:::context
    Wall["wallFunctions"]:::context
    Cyc["cyclic"]:::context
end

Base --> Primitive
Base --> Derived

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

<<<< END >>>>

<<<< ID: DIA_ac281111 >>>>
graph LR
%% BC Mistakes
subgraph Scenario ["Wall Boundary Setup"]
Wall["Wall Patch"]:::implicit
end
subgraph Wrong ["Incorrect"]
    ZeroV["fixedValue (0 0 0)"]:::explicit
    Spike["Velocity Spikes"]:::explicit
    BadTau["Wrong Shear Stress"]:::explicit
end

subgraph Right ["Correct"]
    NoSlip["noSlip"]:::implicit
    Smooth["Smooth Profile"]:::implicit
    GoodTau["Correct Shear Stress"]:::implicit
end

Wall --> Wrong
Wall --> Right
ZeroV --> Spike --> BadTau
NoSlip --> Smooth --> GoodTau

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_cd5cf466 >>>>
graph TD
%% Pressure Drift
subgraph Problem ["Pressure Drift"]
Cause["All Neumann BCs"]:::explicit
Symptom["Unbounded Pressure Rise"]:::explicit
end
subgraph Solution ["Fix"]
    Action["Pin Pressure at Point"]:::implicit
    Result["Stable Solution"]:::implicit
end

Cause --> Symptom
Symptom -.->|Reference Cell| Action
Action --> Result

%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef explicit fill:#ffebee,stroke:#c62828,stroke-width:2px;

<<<< END >>>>

<<<< ID: DIA_6d495d64 >>>>
graph LR
A["Pipe Inlet

(Fixed Velocity)"] --> B["Main Flow Region

(Forward Flow)"]
B --> C["Recirculation Zone 1

(Reverse Flow)"]
B --> D["Recirculation Zone 2

(Reverse Flow)"]
C --> E["Reattachment Point"]
D --> E
E --> F["Pipe Outlet

(Potential Backflow)"]
F --> G["Outlet Boundary

(inletOutlet Condition)"]
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

class B,E implicit;
class A,G explicit;
class C,D,F volatile;

<<<< END >>>>

<<<< ID: DIA_513ee5f4 >>>>
graph TD
A["Boundary Condition

(OpenFOAM Concept)"]:::context --> B["Dirichlet

(Fixed Value)"]:::implicit
A --> C["Neumann

(Fixed Gradient)"]:::implicit
A --> D["Robin/Mixed

(Linear Combination)"]:::implicit
A --> E["Calculated

(Computed)"]:::implicit
A --> F["Coupled

(Multi-region)"]:::implicit
B --> B1["fixedValue<br/>φ = φ₀"]:::explicit
B --> B2["timeVaryingFixedValue<br/>φ = f(t)"]:::explicit
B --> B3["uniformFixedValue<br/>φ = constant"]:::explicit

C --> C1["fixedGradient<br/>∇φ⋅n = g₀"]:::explicit
C --> C2["zeroGradient<br/>∇φ⋅n = 0"]:::explicit

D --> D1["mixed<br/>aφ + b∂φ/∂n = c"]:::explicit
D --> D2["convectiveHeatTransfer<br/>Newton's Law"]:::explicit

E --> E1["calculated<br/>Field Dependent"]:::explicit
E --> E2["wallFunction<br/>Turbulence Model"]:::explicit

F --> F1["cyclic<br/>Periodic"]:::explicit
F --> F2["regionCoupled<br/>Conjugate Heat"]:::explicit
F --> F3["processor<br/>MPI Comm"]:::explicit

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_fa1b9445 >>>>
graph LR
A["Computational Domain Ω"]:::context --> B["Boundary Surface ∂Ω"]:::implicit
B --> C["FixedValue Boundary"]:::implicit
C --> D["Field φ Assignment"]:::implicit
D --> E["φ = φ₀(x,t)"]:::explicit
F["Velocity Inlet"]:::volatile --> G["u = u_inlet(x,t)"]:::explicit
H["Temperature Wall"]:::volatile --> I["T = T_wall"]:::explicit
J["Pressure Outlet"]:::volatile --> K["p = p_ambient"]:::explicit

C --> F
C --> H
C --> J

L["OpenFOAM Implementation"]:::context --> M["fixedValue"]:::implicit
M --> N["value uniform <constant>"]:::explicit
M --> O["timeVaryingValue <function>"]:::explicit

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_525ce480 >>>>
graph LR
A["Boundary ∂Ω"]:::context --> B["Normal Vector n"]:::implicit
B --> C["Gradient ∇φ"]:::implicit
C --> D["Normal Derivative ∂φ/∂n"]:::implicit
D --> E["Flux g₀(x,t)"]:::explicit
F["Control Volume"]:::context --> A
G["Field Variable φ"]:::context --> C

H["Adiabatic Wall"]:::volatile --> I["∂T/∂n = 0"]:::explicit
J["Heat Flux"]:::volatile --> K["-k∂T/∂n = q''ₙ"]:::explicit
L["Symmetry Plane"]:::volatile --> M["∂φ/∂n = 0"]:::explicit

I --> D
K --> D
M --> D

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_ea91973c >>>>
graph LR
A["Mixed Boundary Condition"]:::context --> B["Field Value Contribution"]:::implicit
A --> C["Normal Gradient Contribution"]:::implicit
B --> D["a ϕ term"]:::implicit
C --> E["b ∂ϕ/∂n term"]:::implicit
D --> F["Dirichlet Component"]:::implicit
E --> G["Neumann Component"]:::implicit
A --> H["General Form:<br/>aϕ + b∂ϕ/∂n = c"]:::explicit

F --> J["Prescribed Value"]:::explicit
G --> K["Prescribed Flux"]:::explicit

J --> L["Fixed Temperature"]:::volatile
K --> M["Fixed Heat Flux"]:::volatile

L --> N["Convection Boundary"]:::volatile
M --> N
N --> O["Robin Condition"]:::implicit
O --> P["Combined BC"]:::context

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_bd94ffc8 >>>>
graph TD
A["fvPatchField<Type>

(Abstract base)"]:::context --> B["fixedValueFvPatchField"]:::implicit
A --> C["fixedGradientFvPatchField"]:::implicit
A --> D["mixedFvPatchField"]:::implicit
A --> E["zeroGradientFvPatchField"]:::implicit
A --> F["calculatedFvPatchField"]:::implicit
A --> G["cyclicFvPatchField"]:::implicit
A --> H["processorFvPatchField"]:::implicit
A --> I["Specialized Derived Classes"]:::implicit
B --> J["Dirichlet BC<br/>φ = φ₀"]:::explicit
C --> K["Neumann BC<br/>∂φ/∂n = g₀"]:::explicit
D --> L["Robin BC<br/>aφ + b∂φ/∂n = c"]:::explicit
E --> M["Zero Flux<br/>∂φ/∂n = 0"]:::explicit
F --> N["Computed<br/>Field Dependent"]:::explicit
G --> O["Periodic<br/>φ₁ = φ₂"]:::explicit
H --> P["Parallel<br/>MPI Comm"]:::explicit

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_f6b2a1fd >>>>
graph LR
A["Dictionary File

(0/U, 0/p)"]:::explicit --> B["Runtime Selection

Mechanism"]:::implicit
B --> C["Virtual Function

Table Lookup"]:::implicit
C --> D["Dynamic Class

Instantiation"]:::implicit
D --> E["Specific Boundary

Object Created"]:::volatile
F["fixedValue"]:::context --> C
G["zeroGradient"]:::context --> C
H["mixed"]:::context --> C
I["calculated"]:::context --> C
J["cyclic"]:::context --> C

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_6b2220d3 >>>>
graph LR
A["Inlet Velocity Profile"]:::context --> B["Time: 0-2s

Ramp Up"]:::explicit
B --> C["Linear Ramp

0 to 5 m/s"]:::implicit
C --> D["Time: 2-8s

Steady"]:::explicit
D --> E["Constant Flow

5 m/s"]:::implicit
E --> F["Time: 8-12s

Oscillation"]:::explicit
F --> G["Sinusoidal

Variation"]:::implicit
G --> H["Time: 12-15s

Ramp Down"]:::explicit
H --> I["Linear Ramp

5 to 0 m/s"]:::implicit
I --> J["Outlet Flow

End"]:::volatile
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_58538170 >>>>
graph TD
A["Region 1: Fluid"]:::implicit --> B["Coupled Thermal Interface"]:::explicit
B --> C["Region 2: Solid"]:::implicit
A --> A1["Temperature T1"]:::context
A --> A2["Heat Flux q1"]:::context
A --> A3["Fluid Flow"]:::context

B --> B1["turbulentTemperature<br/>CoupledBaffleMixed"]:::explicit
B --> B2["Thermal Continuity"]:::implicit
B --> B3["Heat Flux Conservation"]:::implicit

C --> C1["Temperature T2"]:::context
C --> C2["Heat Flux q2"]:::context
C --> C3["Solid Properties"]:::context

A1 -- "Conjugate" --> B2
B2 -- "Continuity" --> C1
A2 -- "Energy Balance" --> B3
B3 -- "Equal Flux" --> C2

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_e1dc5bdf >>>>
graph LR
Wall["Wall Surface

y+ < 1"]:::volatile
Viscous["Viscous Sublayer

y+ < 5

u+ = y+"]:::implicit
Buffer["Buffer Layer

5 < y+ < 30

Transition"]:::explicit
Log["Logarithmic Layer

y+ > 30

u+ = (1/k) ln(y+) + B"]:::implicit
Outer["Outer Layer

Full Turbulence

u+ = u_tau"]:::context
Wall --> Viscous
Viscous --> Buffer
Buffer --> Log
Log --> Outer

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_87d90cc1 >>>>
graph LR
A["Base fvPatchField Class

Abstract"]:::context --> B["Basic Types"]:::implicit
A --> C["Derived Types"]:::implicit
A --> D["Specialized Types"]:::implicit
B --> B1["fixedValue<br/>φ = φ₀"]:::explicit
B --> B2["fixedGradient<br/>∇φ⋅n = g₀"]:::explicit
B --> B3["zeroGradient<br/>∇φ⋅n = 0"]:::explicit
B --> B4["calculated<br/>Dependent"]:::explicit

C --> C1["timeVaryingFixedValue<br/>φ = f(t)"]:::explicit
C --> C2["timeVaryingUniform<br/>φ = f(t) uniform"]:::explicit
C --> C3["uniformFixedValue<br/>φ = constant"]:::explicit
C --> C4["mixedFixedValue<br/>Blended"]:::explicit

D --> D1["turbulentInlet<br/>Random"]:::explicit
D --> D2["wallFunction<br/>Modeled"]:::explicit
D --> D3["codedFixedValue<br/>User code"]:::explicit
D --> D4["regionCoupled<br/>Multi-region"]:::explicit

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_88196586 >>>>
flowchart TD
A["Physical Problem"]:::context --> B["Pre-Processing"]:::implicit
B --> C["Solving"]:::explicit
C --> D["Post-Processing"]:::implicit
D --> E["Engineering Insights"]:::success
B --> B1["Geometry & Mesh"]:::context
B --> B2["Boundary Conditions"]:::context
B --> B3["Physical Properties"]:::context
B --> B4["Solver Parameters"]:::context

C --> C1["Discretization"]:::context
C --> C2["Numerical Solution"]:::context
C --> C3["Convergence Monitoring"]:::context

D --> D1["Visualization"]:::context
D --> D2["Data Extraction"]:::context
D --> D3["Validation"]:::context

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_59cda0b6 >>>>
graph LR
A["Physical Domain"]:::context --> B["blockMesh Utility"]:::explicit
B --> C["Structured Mesh"]:::implicit
C --> D["Grid Cells"]:::implicit
D --> E["Discrete Geometry"]:::implicit
C --> F["Cell Centers"]:::implicit
C --> G["Cell Faces"]:::implicit
C --> H["Boundary Faces"]:::implicit

F --> I["Field Variables"]:::explicit
G --> J["Flux Calculations"]:::explicit
H --> K["Boundary Conditions"]:::volatile

I --> L["CFD Equations"]:::success
J --> L
K --> L

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_ae8a0fbf >>>>
graph TD
A["Start Time Step"]:::context --> B["Predict Velocity

(Momentum Predictor)"]:::implicit
B --> C["Solve Momentum Eq

(Discretized Matrix)"]:::implicit
C --> D["Pressure Correction

p' = p_new - p*"]:::explicit
D --> E["Solve Pressure Eq

∇²p' = Mass Source"]:::explicit
E --> F["Correct Velocity

Flux Update"]:::implicit
F --> G["Update Pressure

Field Update"]:::implicit
G --> H{"PISO Correctors

Complete?"}:::explicit
H -->|No| I["Loop Correction"]:::context
I --> E
H -->|Yes| J["Advance Time"]:::implicit
J --> K{"End of Sim?"}:::explicit
K -->|No| A
K -->|Yes| L["Finish"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_3ec3b944 >>>>
graph LR
A["Pre-Processing"]:::implicit --> B["Solving"]:::explicit
B --> C["Post-Processing"]:::implicit
C --> D["Validation"]:::explicit
D --> E["Engineering Decisions"]:::success
A --> A1["Mesh Generation"]:::context
A --> A2["Boundary Conditions"]:::context
A --> A3["Physical Properties"]:::context

B --> B1["FVM Discretization"]:::context
B --> B2["PISO Algorithm"]:::context
B --> B3["Convergence Check"]:::context

C --> C1["ParaView Visualization"]:::context
C --> C2["Data Extraction"]:::context
C --> C3["Quantitative Analysis"]:::context

D --> D1["Grid Independence"]:::context
D --> D2["Benchmark Comparison"]:::context
D --> D3["Experimental Validation"]:::context

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_753a4efe >>>>
graph TD
A["Cavity Geometry

(Square Box)"]:::context --> B["Moving Lid

(Source of Energy)"]:::volatile
B --> C["Primary Vortex

(Central Rotation)"]:::implicit
C --> D["Secondary Vortices

(Corner Eddies)"]:::implicit
D --> E["Boundary Layers

(Wall Shear)"]:::implicit
E --> F["Shear Layer

(Velocity Gradient)"]:::explicit
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_e583ee43 >>>>
graph TD
A["lidDrivenCavity/

(Case Root)"]:::context --> B["0/

(Initial Fields)"]:::implicit
A --> C["constant/

(Mesh/Properties)"]:::implicit
A --> D["system/

(Solver Settings)"]:::implicit
B --> B1["U<br/>(Velocity)"]:::explicit
B --> B2["p<br/>(Pressure)"]:::explicit

C --> C1["polyMesh/<br/>(Geometry)"]:::explicit
C --> C2["transportProperties<br/>(Viscosity)"]:::explicit

D --> D1["controlDict<br/>(Time/Write)"]:::explicit
D --> D2["fvSchemes<br/>(Discretization)"]:::explicit
D --> D3["fvSolution<br/>(Solvers)"]:::explicit
D --> D4["blockMeshDict<br/>(Mesh Gen)"]:::explicit

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_6fb70ce6 >>>>
graph LR
A["Cavity Lid Driven Flow

Boundary Conditions"]:::context
subgraph "Lid Boundary (movingWall)"
    B["Velocity: U = 1 0 0<br/>fixedValue"]:::volatile
    C["Pressure: ∂p/∂n = 0<br/>zeroGradient"]:::implicit
end

subgraph "Wall Boundaries (fixedWalls)"
    D["Left Wall: U = 0<br/>No-slip"]:::implicit
    E["Right Wall: U = 0<br/>No-slip"]:::implicit
    F["Bottom Wall: U = 0<br/>No-slip"]:::implicit
    G["Pressure: ∂p/∂n = 0<br/>zeroGradient"]:::implicit
end

subgraph "Front/Back (frontAndBack)"
    H["Type: empty<br/>(2D Constraint)"]:::context
end

A --> B
A --> C
A --> D
A --> E
A --> F
A --> G
A --> H

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_0e3fd762 >>>>
graph LR
A["Simulation Start

t = 0.0 s"]:::context --> B["Time Step 1

Δt = 0.005 s"]:::implicit
B --> C["Time Step 2

t = 0.010 s"]:::implicit
C --> D["... Time Steps ..."]:::context
D --> E["Output 1

t = 0.100 s"]:::explicit
E --> F["... Time Steps ..."]:::context
F --> G["Output 2

t = 0.200 s"]:::explicit
G --> H["... Time Steps ..."]:::context
H --> I["Output 3

t = 0.300 s"]:::explicit
I --> J["... Time Steps ..."]:::context
J --> K["Output 4

t = 0.400 s"]:::explicit
K --> L["... Time Steps ..."]:::context
L --> M["Final Output

t = 0.500 s"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_82c37e8b >>>>
graph TD
A["สร้างไดเรกทอรีเคส

(mkdir -p)"]:::context --> B["สร้าง Mesh

(blockMesh)"]:::implicit
B --> C["กำหนด Boundary Conditions

(0/U, 0/p)"]:::explicit
C --> D["ตั้งค่าคุณสมบัติของไหล

(transportProperties)"]:::explicit
D --> E["ตั้งค่า Solver

(system/controlDict)"]:::explicit
E --> F["รันการจำลอง

(icoFoam)"]:::volatile
F --> G["ตรวจสอบการลู่เข้า

(Monitor Residuals)"]:::implicit
G --> H["ประมวลผลภายหลัง

(paraFoam)"]:::success
H --> I["วิเคราะห์ผลลัพธ์

(Analysis)"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_9d15d49e >>>>
graph LR
A["Square Cavity

Domain"]:::context --> B["Moving Top Lid

Source"]:::volatile
B --> C["Stationary Walls

Sinks"]:::implicit
C --> D["Primary Vortex

(Center)"]:::explicit
D --> E["Secondary Vortices

(Corners)"]:::explicit
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_9b2051f8 >>>>
graph TD
A["Start Time Step"]:::context --> B["Predict Velocity

U* from prev time"]:::implicit
B --> C["Solve Momentum

Discretized Eq"]:::implicit
C --> D["Pressure Correction

p' calculation"]:::explicit
D --> E["Solve Pressure Eq

Continuity Enforced"]:::explicit
E --> F["Correct Velocity

Flux Update"]:::implicit
F --> G["Update Pressure

p = p* + p'"]:::implicit
G --> H{"PISO Loop

Done?"}:::explicit
H -->|No| I["Correct Again"]:::context
I --> E
H -->|Yes| J["Next Step"]:::implicit
J --> K{"Sim End?"}:::explicit
K -->|No| A
K -->|Yes| L["Finish"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_2d892615 >>>>
graph LR
A["Pre-Processing

(Setup)"]:::implicit --> B["Solving

(Run)"]:::explicit
B --> C["Post-Processing

(Analyze)"]:::success
A --> A1["Geometry & Mesh"]:::context
A --> A2["Boundary Conditions"]:::context
A --> A3["Physical Properties"]:::context
A --> A4["Solver Settings"]:::context

B --> B1["Discretization"]:::context
B --> B2["PISO Algorithm"]:::context
B --> B3["Convergence Check"]:::context

C --> C1["Visualization"]:::context
C --> C2["Data Extraction"]:::context
C --> C3["Validation"]:::context

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_be34cc31 >>>>
graph LR
subgraph Pre ["1. Pre-processing (การเตรียมข้อมูล)"]
direction TB
A["📂 1. ตั้งค่าไดเรกทอรี

(Case Setup)"]:::implicit
B["🕸️ 2. สร้าง Mesh

(Meshing)"]:::implicit
C["boundary 3. กำหนดเงื่อนไขขอบเขต

(Boundary Conditions)"]:::explicit
A --> B --> C
end
subgraph Solve ["2. Solving (การคำนวณ)"]
    direction TB
    D["⚙️ 4. ตั้งค่าพารามิเตอร์<br/>(Control Dict)"]:::implicit
    E["🚀 5. รันการจำลอง<br/>(Run Simulation)"]:::volatile
    D --> E
end

subgraph Post ["3. Post-processing (การวิเคราะห์ผล)"]
    direction TB
    F["📊 6. ประมวลผลภาพ<br/>(Visualization)"]:::implicit
    G["✅ 7. ตรวจสอบความถูกต้อง<br/>(Validation)"]:::success
    F --> G
end

C ==> D
E ==> F

G -.->|ผลไม่ผ่าน| B
G -.->|ปรับค่า| D

classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_a5efe0a7 >>>>
graph LR
A["Moving Lid

U = 1 m/s"]:::volatile --> B["Shear Stress Generation

τ = μ(∂u/∂y)"]:::explicit
B --> C["Momentum Transfer

(Downward)"]:::implicit
C --> D["Primary Vortex

(Clockwise)"]:::implicit
D --> E["Flow Circulation

(Cavity Loop)"]:::success
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_6bc4f7dc >>>>
flowchart LR
A["Top Wall

U = 1 m/s"]:::volatile --> B["Right Wall

Flow Down"]:::implicit
B --> C["Bottom Wall

Flow Return"]:::implicit
C --> D["Left Wall

Flow Up"]:::implicit
D --> A
E["Vortex Center<br/>(0.5, 0.4)"]:::explicit -.-> A
E -.-> B
E -.-> C
E -.-> D

classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_964cc6a7 >>>>
graph TD
subgraph "Moffatt Eddies Hierarchy (Re=10)"
A["Primary Vortex

(Clockwise Dominant)"]:::volatile
B["Corner Eddy 1

(Counter-Clockwise)"]:::explicit
C["Corner Eddy 2

(Clockwise Weak)"]:::implicit
D["Corner Eddy 3

(Counter-Clockwise Tiny)"]:::context
end
A --> B
B --> C
C --> D

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_5ca7dcef >>>>
flowchart TD
A["Cavity Geometry

(Square Box)"]:::context --> B["Moving Lid

(Source)"]:::volatile
B --> C["Primary Vortex

(Core Flow)"]:::implicit
C --> D["Secondary Vortices

(Corner Eddies)"]:::implicit
D --> E["Boundary Layers

(Wall Interaction)"]:::explicit
E --> F["Shear Layer

(Gradients)"]:::explicit
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_2ed2557e >>>>
flowchart TD
A["lidDrivenCavity/

(Root)"]:::context --> B["0/

(Fields)"]:::implicit
A --> C["constant/

(Mesh/Props)"]:::implicit
A --> D["system/

(Settings)"]:::implicit
A --> E["Allrun/

(Script)"]:::explicit
B --> B1["U (Velocity)"]:::context
B --> B2["p (Pressure)"]:::context
B --> B3["k (Turbulence)"]:::context
B --> B4["ω/ε (Dissipation)"]:::context

C --> C1["polyMesh/"]:::context
C --> C2["transportProperties"]:::context
C --> C3["turbulenceProperties"]:::context

D --> D1["controlDict"]:::context
D --> D2["fvSchemes"]:::context
D --> D3["fvSolution"]:::context
D --> D4["blockMeshDict"]:::context

E --> E1["blockMesh<br/>(Meshing)"]:::explicit
E --> E2["icoFoam<br/>(Solving)"]:::volatile
E --> E3["paraFoam<br/>(Viewing)"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_abef25ab >>>>
flowchart TD
A["Start Step"]:::context --> B["Predict Velocity

U*"]:::implicit
B --> C["Solve Momentum"]:::implicit
C --> D["Pressure Correction

p'"]:::explicit
D --> E["Solve Pressure"]:::explicit
E --> F["Correct U"]:::implicit
F --> G["Update p"]:::implicit
G --> H{"Corrections

Done?"}:::explicit
H -->|No| I["Iterate"]:::context
I --> E
H -->|Yes| J["Next Step"]:::implicit
J --> K{"Finished?"}:::explicit
K -->|No| A
K -->|Yes| L["End"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_986cbad8 >>>>
graph LR
A["Re = 10

Single Primary Vortex"]:::implicit --> B["Re = 100

Vortex Shift & Asymmetry"]:::explicit
B --> C["Secondary Vortices

Corner Formation"]:::explicit
C --> D["Thin Boundary Layers

High Gradients"]:::volatile
subgraph "Physical Interpretation"
    E["Re = Inertia / Viscous"]:::context
    F["High Re = Momentum Dominated"]:::context
    G["Complexity Increases"]:::context
end

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_b221b159 >>>>
graph LR
A["Mesh Configuration"]:::context --> B["Coarse Mesh

(20x20)"]:::implicit
A --> C["Fine Mesh

(40x40)"]:::implicit
B --> B1["Δx = 0.005 m"]:::context
B --> B2["Higher Error"]:::volatile

C --> C1["Δx = 0.0025 m"]:::context
C --> C2["Lower Error"]:::success

B2 --> D["Grid Independence Check"]:::explicit
C2 --> D

D --> E["Error Metric<br/>< 2% Difference"]:::explicit
D --> F["Comparison"]:::explicit

F --> F1["Vortex Center (+1-3%)"]:::context
F --> F2["Max Velocity (+2-5%)"]:::context
F --> F3["Resolution Improved"]:::success
F --> F4["Convergence Improved"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_830c5a5c >>>>
graph TD
A["Start Step"]:::context --> B["Predict U*"]:::implicit
B --> C["Solve Momentum"]:::implicit
C --> D["Calcu p'"]:::explicit
D --> E["Solve Pressure"]:::explicit
E --> F["Correct U"]:::implicit
F --> G["Update p"]:::implicit
G --> H{"Loop Done?"}:::explicit
H -->|No| I["Iterate"]:::context
I --> E
H -->|Yes| J["Next Step"]:::implicit
J --> K{"End?"}:::explicit
K -->|No| A
K -->|Yes| L["Finish"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_5ffa9f7e >>>>
graph TD
A["lidDrivenCavity/

(Root)"]:::context --> B["0/

(Init)"]:::implicit
A --> C["constant/

(Mesh)"]:::implicit
A --> D["system/

(Control)"]:::implicit
A --> E["Allrun/

(Exec)"]:::explicit
B --> B1["U, p"]:::context
C --> C1["polyMesh, transport"]:::context
D --> D1["controlDict, fvSchemes"]:::context
E --> E1["blockMesh"]:::explicit
E --> E2["icoFoam"]:::volatile
E --> E3["paraFoam"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_31f2a089 >>>>
graph LR
A["Cell P

(Center)"]:::implicit --> E["Vector d

(Owner-Neighbor)"]:::implicit
E --> D["Cell Q

(Neighbor)"]:::implicit
B["Face<br/>(Normal Vector n)"]:::context --> C["Non-orthogonality<br/>Angle θ"]:::explicit
B --> F["Face Plane"]:::context

A --> B
D --> B

C --> G["Quality Check:<br/>θ < 70° (Good)<br/>θ > 70° (Poor)"]:::volatile

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_738d4035 >>>>
graph TD
A["Foundation Module"]:::context --> B["CFD Fundamentals"]:::implicit
A --> C["OpenFOAM Basics"]:::implicit
B --> D["Single Phase Flow"]:::implicit
C --> D
D --> E["Lid-Driven Cavity

(Current Focus)"]:::explicit
E --> F["Multiphase Fundamentals"]:::implicit
D --> G["OpenFOAM Programming"]:::implicit
F --> H["Advanced Topics"]:::implicit
G --> I["Utilities & Automation"]:::implicit
H --> J["Testing & Validation"]:::success
I --> J
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_8a965373 >>>>
graph LR
subgraph Inputs
Rho["Density ρ"]:::explicit
Vel["Velocity u"]:::explicit
end
subgraph "Control Volume Analysis"
    In["Mass In<br/>ρu dy dz"]:::implicit --> CV["Control Volume<br/>dx dy dz"]:::context
    CV --> Out["Mass Out<br/>(ρu + ∂/∂x)"]:::implicit
    CV --> Acc["Accumulation<br/>∂ρ/∂t"]:::volatile
end

Rho --> In
Vel --> In

subgraph Balance
    Eq["Conservation Eq<br/>∂ρ/∂t + ∇·(ρu) = 0"]:::success
end

In --> Eq
Out --> Eq
Acc --> Eq

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_9c4c7972 >>>>
graph TD
subgraph Forces["Applied Forces"]
P["Pressure Forces

-∇p"]:::implicit
V["Viscous Forces

∇⋅τ"]:::implicit
B["Body Forces

f"]:::implicit
end
P --> Sum["Net Force<br/>ΣF"]:::explicit
V --> Sum
B --> Sum

Sum -->|Newton's 2nd Law| Acc["Acceleration<br/>ρ Du/Dt"]:::volatile

Acc --> Inertia["Inertial Terms<br/>∂u/∂t + (u⋅∇)u"]:::context

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_6e1961a6 >>>>
graph TD
B["Energy In

(เข้า)"]:::implicit --> A["Control Volume

(CV)"]:::context
A --> C["Energy Out

(ออก)"]:::implicit
A --> D["Energy Storage

(สะสม)"]:::volatile
B1["Kinetic<br/>(จลน์)"]:::context --> B
B2["Internal<br/>(ภายใน)"]:::context --> B
B3["Pressure Work<br/>(งาน P)"]:::context --> B

C1["Convection<br/>(พา)"]:::context --> C
C2["Conduction<br/>(นำ)"]:::context --> C
C3["Radiation<br/>(รังสี)"]:::context --> C

D --> D1["Temp Change"]:::context
D --> D2["Phase Change"]:::context

E["Energy Conservation<br/>E_in - E_out = dE/dt"]:::success
F["OpenFOAM<br/>fvScalarMatrix EEqn"]:::explicit

B --> E
C --> E
E --> F

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_36d6ae2b >>>>
graph LR
A["Control Volume

(dx, A)"]:::context --> B["Mass In

ρuA"]:::implicit
A --> C["Mass Out

(ρu + Δ)A"]:::implicit
A --> D["Accumulation

∂ρ/∂t A dx"]:::volatile
B --> E["Balance<br/>Acc = In - Out"]:::explicit
C --> E
D --> E

E --> F["Continuity Eq<br/>∂ρ/∂t + ∂(ρu)/∂x = 0"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_14f7916a >>>>
graph LR
F_inertial["Inertial Forces

ρu⋅∇u"]:::implicit --> ForceBalance["Force Balance

(2D Flow)"]:::context
F_pressure["Pressure Forces

-∇p"]:::implicit --> ForceBalance
F_viscous["Viscous Forces

μ∇²u"]:::implicit --> ForceBalance
F_external["External Forces

f"]:::implicit --> ForceBalance
subgraph "X-Momentum"
    XMomentum["X-Comp:<br/>ρ Duₓ/Dt = -∂p/∂x + μ∇²uₓ + fₓ"]:::success
end

subgraph "Y-Momentum"
    YMomentum["Y-Comp:<br/>ρ Duᵧ/Dt = -∂p/∂y + μ∇²uᵧ + fᵧ"]:::success
end

ForceBalance --> XMomentum
ForceBalance --> YMomentum

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_99328fb6 >>>>
graph TD
A["Fluid Domain"]:::context --> B["Inlet Boundary"]:::volatile
A --> C["Outlet Boundary"]:::volatile
A --> D["Wall Boundaries"]:::volatile
B --> E["Inlet Velocity<br/>Profile"]:::explicit
C --> F["Outlet Zero<br/>Gradient"]:::explicit

E --> G["Profile Development<br/>Along Length"]:::implicit
G --> H["Fully Developed<br/>Flow Region"]:::success

subgraph "Velocity Evolution"
    I["Initial<br/>(Uniform)"]:::context
    J["Developing<br/>(Entrance)"]:::implicit
    K["Developed<br/>(∂u/∂x = 0)"]:::success
end

I --> J --> K

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_09e4c6c9 >>>>
graph LR
A["Convection

∇·(uT)"]:::implicit --> B["Flow Stream

(Motion)"]:::context
C["Diffusion

∇·(D∇T)"]:::implicit --> D["Molecular

(Spreading)"]:::context
B --> E["Combined Transport<br/>Scalar Field"]:::explicit
D --> E

E --> F["Conservation<br/>Balance"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_24ccfc04 >>>>
graph LR
A["Start SIMPLE"]:::context --> B["Momentum Predictor

(Solve U w/ old p)"]:::implicit
B --> C["Pressure Correction

(Enforce Continuity)"]:::explicit
C --> D["Velocity Correction

(Update U)"]:::implicit
D --> E{"Converged?"}:::explicit
E -->|No| B
E -->|Yes| F["Solution Complete"]:::success
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_0d5c5fe2 >>>>
graph TD
subgraph "FVM Process"
A["Control Volume

(Cell P)"]:::context --> B["Face Fluxes

(Summation)"]:::implicit
B --> C["Gauss Theorem

(Vol -> Surf)"]:::implicit
C --> D["Spatial Discretization

(Gradient schemes)"]:::explicit
D --> E["Temporal Discretization

(Time schemes)"]:::explicit
E --> F["Linear System

(Ax = b)"]:::success
end
subgraph "Topology"
    P["Cell P"]:::volatile --> W["West"]:::context
    P --> E_cell["East"]:::context
    P --> N["North"]:::context
    P --> S["South"]:::context
end

subgraph "Fluxes"
    PW["Flux w"]:::implicit
    PE["Flux e"]:::implicit
    PN["Flux n"]:::implicit
    PS["Flux s"]:::implicit
end

P -- "Flux" --> PW
P -- "Flux" --> PE
P -- "Flux" --> PN
P -- "Flux" --> PS

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_8547f713 >>>>
graph LR
A["Cell P

Center"]:::context --> B["Face Geometry

Sf"]:::implicit
B --> C["Face Velocity<br/>Uf (Interp)"]:::implicit
B --> D["Face Pressure<br/>pf (Interp)"]:::implicit

C --> E["Mass Flux<br/>phi = ρ⋅Uf⋅Sf"]:::explicit
E --> F["Convection Term<br/>∇⋅(ρUU)"]:::success

D --> G["Pressure Force<br/>pf⋅Sf"]:::explicit
G --> H["Pressure Gradient<br/>-∇p"]:::success

F --> I["Momentum Eq<br/>fvVectorMatrix"]:::success
H --> I

J["Diffusion Term<br/>∇⋅(μ∇U)"]:::implicit --> I

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_1f9a7cbf >>>>
graph LR
A["Init Pressure"]:::context --> B["Solve Momentum"]:::implicit
B --> C["Solve Pressure"]:::explicit
C --> D["Correct Velocity"]:::implicit
D --> E["Correct Pressure"]:::implicit
E --> F{"Algorithm?"}:::explicit
F -->|"SIMPLE"| G{"Converged?"}:::explicit
F -->|"PISO"| H{"Correct Loop"}:::explicit
F -->|"PIMPLE"| I{"Large Δt?"}:::explicit

G -->|"No"| J["Under-Relax"]:::volatile
J --> B
G -->|"Yes"| K["Next Step"]:::success

H -->|"Loop"| C
H -->|"Done"| L["Next Step"]:::success

I -->|"Yes (SIMPLE mode)"| M["Relax"]:::volatile
I -->|"No (PISO mode)"| N["No Relax"]:::implicit

M --> O{"Inner Loop"}:::explicit
N --> P["Next Step"]:::success

O -->|"Iterate"| B
O -->|"Done"| P

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_66860804 >>>>
graph TD
A["Governing Equations"]:::context --> B["Select Solver"]:::implicit
B --> C{Compressible?}:::explicit
C -->|Yes| D["rhoSimpleFoam<br/>rhoPimpleFoam<br/>sonicFoam"]:::volatile
C -->|No| E["simpleFoam<br/>pimpleFoam<br/>icoFoam"]:::implicit

D --> F["Thermophysical Props"]:::explicit
E --> G["Transport Props"]:::explicit

F --> H["Init Fields (0/)"]:::context
G --> H

H --> I["fvSchemes"]:::context
I --> J["fvSolution"]:::context

J --> K["Run Sim"]:::volatile
K --> L{Converged?}:::explicit

L -->|No| M["Adjust Params"]:::explicit
M --> K

L -->|Yes| N["Post-Processing"]:::success

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_fac31c55 >>>>
graph LR
subgraph Forces
A["Convective

Inertial"]:::implicit
B["Pressure

Gradient"]:::implicit
C["Viscous

Shear"]:::implicit
D["Gravity/Body"]:::implicit
end
subgraph "Dimensionless Numbers"
    H["Reynolds Number<br/>Re = ρUL/μ"]:::explicit
    I["Froude Number<br/>Fr = U/√(gL)"]:::explicit
    J["Euler Number<br/>Eu = ΔP/ρU²"]:::explicit
end

A --> H
C --> H

A --> I
D --> I

B --> J
A --> J

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_e6ebf534 >>>>
graph LR
A["Froude Number

Fr = U/√(gL)"]:::explicit --> B{"Flow State"}:::implicit
B -->|Fr < 1| C["Subcritical<br/>(Tranquil)"]:::implicit
B -->|Fr = 1| D["Critical<br/>(Transition)"]:::volatile
B -->|Fr > 1| E["Supercritical<br/>(Rapid)"]:::volatile

C --> F["Slow / Deep<br/>Wave travels up"]:::context
D --> G["Critical Depth<br/>Max Energy"]:::context
E --> H["Fast / Shallow<br/>No upstream wave"]:::context

I["Free Surface"]:::context --> J["Waves"]:::implicit
I --> K["Hydraulic Jump"]:::explicit

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_4be9e924 >>>>
graph LR
A["Velocity U"]:::context --> B["Mach Number

Ma = U/c"]:::explicit
B --> C{"Regime"}:::implicit
C -->|Ma < 0.3| D["Incompressible<br/>ρ const"]:::implicit
C -->|0.3 < Ma < 0.8| E["Subsonic<br/>ρ varies"]:::explicit
C -->|0.8 < Ma < 1.2| F["Transonic<br/>Shocks"]:::volatile
C -->|Ma > 1.2| G["Supersonic<br/>Strong Shocks"]:::volatile

D --> H["Solver:<br/>simpleFoam"]:::success
E --> I["Solver:<br/>rhoSimpleFoam"]:::success
F --> J["Solver:<br/>sonicFoam"]:::success
G --> J

classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
classDef explicit fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
classDef volatile fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

<<<< END >>>>

<<<< ID: DIA_bf4f9f01 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
subgraph "Physics_Regimes"
    direction TB
    Gases["Gases (Pr < 1)<br/>Thermal Layer > Velocity Layer<br/>High Thermal Diffusivity"]:::implicit
    Liquids["Liquids (Pr > 1)<br/>Thermal Layer < Velocity Layer<br/>High Momentum Diffusivity"]:::implicit
end

subgraph "Engineering_Context"
    direction TB
    Apps["Critical Applications<br/>Heat Exchangers<br/>Gas Turbines"]:::context
end

Gases --> Apps
Liquids --> Apps

<<<< END >>>>

<<<< ID: DIA_3076cdde >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Params["Flow Parameters<br/>St = fL/U ≈ 0.2<br/>Re = ρUL/μ"]:::implicit
Object["Cylinder<br/>Bluff Body"]:::context
Flow["Fluid Flow<br/>Vortex Shedding<br/>Von Kármán Street"]:::explicit

Params --> Object
Object --> Flow

<<<< END >>>>

<<<< ID: DIA_09cc2e3d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Domain["Computational Domain<br/>Fluid Volume"]:::context
Inlet["Inlet<br/>Fixed Value<br/>u=U₀, p=p₀"]:::explicit
Outlet["Outlet<br/>Zero Gradient<br/>∂u/∂n=0"]:::explicit
Wall["Wall<br/>No-slip (u=0)<br/>Adiabatic"]:::implicit
Sym["Symmetry<br/>Slip/Reflection<br/>∂/∂n=0"]:::implicit

Inlet --> Domain
Domain --> Outlet
Wall --- Domain
Sym --- Domain

<<<< END >>>>

<<<< ID: DIA_409cc704 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Layer3["Upper Layer<br/>z > 30m"]:::implicit
Layer2["Log-Law Region<br/>z₀ < z < 30m<br/>u(z) = (u*/κ)·ln(z/z₀)"]:::implicit
Layer1["Roughness Layer<br/>z < z₀"]:::implicit
Ground["Earth Surface<br/>z = 0"]:::context

Layer3 --> Layer2
Layer2 --> Layer1
Layer1 --> Ground

<<<< END >>>>

<<<< ID: DIA_a7a95ea5 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Wall["Wall<br/>y+=0"]:::context
Viscous["Viscous Sublayer<br/>y+ < 5<br/>Linear: u+ = y+"]:::implicit
Buffer["Buffer Layer<br/>5 < y+ < 30<br/>Transition"]:::implicit
Log["Log-Law Region<br/>30 < y+ < 300<br/>u+ = (1/κ)ln(Ey+)"]:::implicit
Outer["Outer Layer<br/>y+ > 300<br/>Wake Region"]:::implicit

Wall --> Viscous
Viscous --> Buffer
Buffer --> Log
Log --> Outer

<<<< END >>>>

<<<< ID: DIA_e8096360 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fluid["Fluid Domain<br/>Convection"]:::context
Interface["CHT Interface<br/>q_fluid = q_solid<br/>T_fluid = T_solid"]:::explicit
Solid["Solid Domain<br/>Conduction (κ)"]:::context
Ext["External Wall<br/>h=10, Ta=300K"]:::implicit

Fluid <--> Interface
Interface <--> Solid
Solid --- Ext

<<<< END >>>>

<<<< ID: DIA_77ae9c0e >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
T0["t=0s<br/>Start"]:::context
T1["t=2s<br/>Ramp Up"]:::explicit
T2["t=5s<br/>Steady (10 m/s)"]:::implicit
T3["t=6s<br/>Ramp Down"]:::explicit
T4["t=7s<br/>Stop"]:::context

T0 --> T1 --> T2 --> T3 --> T4

<<<< END >>>>

<<<< ID: DIA_cb773622 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Theory["Continuum Mechanics<br/>Conservation Laws"]:::context
PDE["Navier-Stokes Equations<br/>Partial Differential Eqns"]:::implicit
FVM["Finite Volume Method<br/>Discretization"]:::explicit
Code["OpenFOAM<br/>Numerical Solution"]:::explicit

Theory --> PDE
PDE --> FVM
FVM --> Code

<<<< END >>>>

<<<< ID: DIA_67d22166 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start(("Start")):::context
Pred["Momentum Predictor<br/>Solve U (guessed p)"]:::explicit
Corr["Pressure Corrector<br/>Solve pEqn (Mass Cont.)"]:::explicit
Update["Update Fields<br/>Correct U & Fluxes"]:::explicit
Check{"Converged?"}:::implicit
End(("End")):::context

Start --> Pred
Pred --> Corr
Corr --> Update
Update --> Check
Check -- No --> Pred
Check -- Yes --> End

<<<< END >>>>

<<<< ID: DIA_7c1908ed >>>>
graph TB
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
subgraph "Laminar_Regime"
    L_Char["Laminar Flow<br/>Re < Re_crit<br/>Orderly/Streamlined"]:::implicit
    L_Math["Direct Navier-Stokes<br/>No Modeling Req."]:::implicit
    L_Char --> L_Math
end

subgraph "Turbulent_Regime"
    T_Char["Turbulent Flow<br/>Re > Re_crit<br/>Chaotic/Mixing"]:::explicit
    T_Math["RANS / LES<br/>Turbulence Modeling Req."]:::explicit
    T_Char --> T_Math
end

<<<< END >>>>

<<<< ID: DIA_d165d5e5 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Choice["Initial Conditions"]:::context
Zero["Zero Fields<br/>Poor Stability"]:::explicit
Approx["Potential Flow<br/>Good Stability"]:::implicit
Map["Map Fields<br/>Best Stability"]:::implicit

Choice --> Zero
Choice --> Approx
Choice --> Map

<<<< END >>>>

<<<< ID: DIA_84a0fdc0 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Field["volVectorField U"]:::context
Int["Internal Field<br/>uniform (0 0 0)"]:::implicit
BCs["Boundary Conditions<br/>Inlet: fixedValue<br/>Wall: noSlip"]:::explicit
Dims["Dimensions<br/>[0 1 -1 0 0 0 0]"]:::implicit

Field --> Int
Field --> BCs
Field --> Dims

<<<< END >>>>

<<<< ID: DIA_5ff8cf79 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("Setup"):::context
Mesh["checkMesh"]:::explicit
Fields["foamListFields"]:::explicit
Dims["Dimension Check"]:::implicit
Run("Run Simulation"):::implicit

Start --> Mesh
Mesh --> Fields
Fields --> Dims
Dims -- Pass --> Run
Dims -- Fail --> Start

<<<< END >>>>

<<<< ID: DIA_a755dce0 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Vars["Variables<br/>P, T, ρ"]:::context
EOS["Equation of State<br/>p = ρRT"]:::implicit
Regime["Flow Regime"]:::context
Comp["Compressible<br/>rhoPimpleFoam"]:::explicit
Incomp["Incompressible<br/>simpleFoam"]:::implicit

Vars --> EOS
EOS --> Regime
Regime --> Comp
Regime --> Incomp

<<<< END >>>>

<<<< ID: DIA_95c19b91 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Flow{"Flow Type?"}:::context
Incomp["Incompressible<br/>Ma < 0.3<br/>ρ = const"]:::implicit
Comp["Compressible<br/>Ma > 0.3<br/>ρ = f(p,T)"]:::explicit

Flow --> Incomp
Flow --> Comp

<<<< END >>>>

<<<< ID: DIA_c244638a >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Theory["Continuum Mechanics"]:::context
Vars["Field Variables<br/>u(x,t), p(x,t)"]:::implicit
FVM["Finite Volume<br/>Discretization"]:::explicit
Solver["OpenFOAM Solver"]:::explicit

Theory --> Vars
Vars --> FVM
FVM --> Solver

<<<< END >>>>

<<<< ID: DIA_b7a8e4ed >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start(("Start")):::context
Pred["Momentum Predictor"]:::explicit
Corr["Pressure Corrector"]:::explicit
Update["Update Fields"]:::explicit
Check{"Convergence"}:::implicit
End(("End")):::context

Start --> Pred
Pred --> Corr
Corr --> Update
Update --> Check
Check -- No --> Pred
Check -- Yes --> End

<<<< END >>>>

<<<< ID: DIA_1c2ad4ea >>>>
graph TB
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
subgraph "Laminar"
    L["Laminar<br/>Smooth / Low Re"]:::implicit
    L_Eq["Direct Navier-Stokes"]:::implicit
    L --> L_Eq
end

subgraph "Turbulent"
    T["Turbulent<br/>Chaotic / High Re"]:::explicit
    T_Eq["RANS / LES Models"]:::explicit
    T --> T_Eq
end

<<<< END >>>>

<<<< ID: DIA_9124d8e4 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start{"Analyze Material"}:::context
Q1{"Yield Stress?"}:::explicit
HB["Herschel-Bulkley"]:::implicit
Q2{"Newtonian Plateaus?"}:::explicit
BC["Bird-Carreau"]:::implicit
PL["Power-Law"]:::implicit

Start --> Q1
Q1 -- Yes --> HB
Q1 -- No --> Q2
Q2 -- Yes --> BC
Q2 -- No --> PL

<<<< END >>>>

<<<< ID: DIA_dbd87954 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Base["viscosityModel"]:::context
Gen["generalisedNewtonian"]:::implicit
Strain["strainRateViscosityModel"]:::implicit
Models["Concrete Models:<br/>- BirdCarreau<br/>- HerschelBulkley<br/>- PowerLaw"]:::explicit

Base --> Gen --> Strain --> Models

<<<< END >>>>

<<<< ID: DIA_06a71b8a >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Newton["Newtonian<br/>μ = constant<br/>τ = μ·γ̇"]:::implicit
NonNewton["Non-Newtonian<br/>μ = f(γ̇)<br/>τ = μ(γ̇)·γ̇"]:::explicit

Newton --> NonNewton

<<<< END >>>>

<<<< ID: DIA_74a852b2 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Pre["การประมวลผลล่วงหน้า<br/>(Preprocessing)"]:::context
Mesh["สร้างเมช<br/>(Meshing)"]:::implicit
Setup["กำหนดค่า<br/>Properties/BCs"]:::explicit
Run["รันการจำลอง<br/>(Run Simulation)"]:::explicit
Post["การประมวลผลผลลัพธ์<br/>(Post-processing)"]:::context

Pre --> Mesh --> Setup --> Run --> Post

<<<< END >>>>

<<<< ID: DIA_8f342deb >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("เริ่ม"):::context
Newton["รันแบบจำลองนิวตัน<br/>(Initial Guess)"]:::implicit
NonNewton["เปลี่ยนเป็นนอนนิวตัน<br/>(Complex Model)"]:::explicit
Check{"ตรวจสอบการลู่เข้า"}:::implicit
End("เสร็จสิ้น"):::context

Start --> Newton --> NonNewton --> Check
Check -- ยัง --> NonNewton
Check -- ใช่ --> End

<<<< END >>>>

<<<< ID: DIA_ba1d5538 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Step1["1. แบบจำลองนิวตัน<br/>(Stabilize)"]:::implicit
Step2["2. กฎกำลัง (Power Law)<br/>(Intermediate)"]:::explicit
Step3["3. แบบจำลองซับซ้อน<br/>(Final Physics)"]:::explicit

Step1 --> Step2 --> Step3

<<<< END >>>>

<<<< ID: DIA_ebc69ba0 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Call["viscosityModel::New"]:::context
Read["Read Dictionary"]:::implicit
Table["Runtime Selection Table"]:::implicit
Create["Construct Object"]:::explicit
Error["Fatal Error"]:::explicit

Call --> Read --> Table
Table -- Found --> Create
Table -- Not Found --> Error

<<<< END >>>>

<<<< ID: DIA_23b517cb >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Newton["ของไหลนิวตัน<br/>μ คงที่<br/>น้ำ, อากาศ"]:::implicit
NonNewton["ของไหลนอนนิวตัน<br/>μ แปรผันตาม γ̇<br/>เลือด, โพลีเมอร์"]:::explicit

Newton --> NonNewton

<<<< END >>>>

<<<< ID: DIA_967a0e05 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Base["viscosityModel<br/>(Base Class)"]:::context
Inter["strainRateViscosityModel<br/>(Intermediate)"]:::implicit
Concrete["Implementations:<br/>BirdCarreau, PowerLaw..."]:::explicit

Base --> Inter --> Concrete

<<<< END >>>>

<<<< ID: DIA_ea71e9c6 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Root["การประยุกต์ใช้<br/>นอนนิวตัน"]:::context
Poly["โพลีเมอร์<br/>(ฉีด, อัดรีด)"]:::implicit
Food["อาหาร<br/>(ซอส, แป้ง)"]:::explicit
Bio["ชีวการแพทย์<br/>(เลือด)"]:::implicit
Const["ก่อสร้าง<br/>(ซีเมนต์)"]:::explicit

Root --> Poly
Root --> Food
Root --> Bio
Root --> Const

<<<< END >>>>

<<<< ID: DIA_079b62db >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Init["อ่านค่า transportProperties"]:::context
Loop["วงรอบเวลา (Time Loop)"]:::implicit
Calc["คำนวณ γ̇ และ μ<br/>μ = f(γ̇)"]:::explicit
Bound["จำกัดค่า μ<br/>min/max"]:::explicit
Solve["แก้สมการโมเมนตัม"]:::implicit

Init --> Loop --> Calc --> Bound --> Solve --> Loop

<<<< END >>>>

<<<< ID: DIA_049f0af0 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Entry["Dictionary Entry"]:::context
Selector["viscosityModel::New"]:::implicit
Factory["Factory Lookup"]:::implicit
Result["Return autoPtr"]:::explicit

Entry --> Selector --> Factory --> Result

<<<< END >>>>

<<<< ID: DIA_697eca2d >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Static["Static Initialization"]:::context
Ctor["Constructor"]:::implicit
Reg["Register to Factory"]:::explicit
Runtime["Available at Runtime"]:::implicit

Static --> Ctor --> Reg --> Runtime

<<<< END >>>>

<<<< ID: DIA_9c0a9136 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Root["Stabilization Strategies"]:::context
Relax["Field Relaxation<br/>U:0.7, p:0.3"]:::implicit
Bound["Viscosity Bounding<br/>nuMin / nuMax"]:::implicit
Iter["Iterative Coupling<br/>Picard"]:::implicit

Root --> Relax
Root --> Bound
Root --> Iter

<<<< END >>>>

<<<< ID: DIA_a7ccecc8 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fluid["Fluid Flow"]:::context
Therm["Thermal"]:::implicit
Struct["Structural"]:::explicit
Chem["Chemical"]:::implicit

Fluid <--> Therm
Fluid <--> Struct
Fluid <--> Chem
Therm <--> Struct

<<<< END >>>>

<<<< ID: DIA_45c0e04b >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("Iterate"):::context
Fluid["Solve Fluid Domain"]:::implicit
Inter["Exchange Interface"]:::explicit
Solid["Solve Solid Domain"]:::implicit
Check{"Converged?"}:::context

Start --> Fluid --> Inter --> Solid --> Check
Check -- No --> Fluid

<<<< END >>>>

<<<< ID: DIA_685d7f9a >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("Time Step"):::context
Solid["Solid Region<br/>solveSolid.H"]:::implicit
Fluid["Fluid Region<br/>solveFluid.H"]:::implicit
Map["Interface Mapping<br/>mappedWall"]:::explicit
Check{"Convergence"}:::context

Start --> Solid --> Fluid --> Map --> Check
Check -- No --> Solid

<<<< END >>>>

<<<< ID: DIA_0baf4c53 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Prep["Pre-processing<br/>Weights & Coeffs"]:::context
Runtime["Runtime Loop"]:::implicit
Sample["Sample & Map<br/>AMI Interpolation"]:::explicit
Update["Update Boundary"]:::implicit

Prep --> Runtime --> Sample --> Update

<<<< END >>>>

<<<< ID: DIA_a22d987b >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Solid["Solid (f=0)"]:::implicit
Mushy["Mushy Zone<br/>(0 < f < 1)"]:::explicit
Liquid["Liquid (f=1)"]:::implicit

Solid <--> Mushy <--> Liquid

<<<< END >>>>

<<<< ID: DIA_d48b0ffc >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Si["Surface i"]:::context
Sj["Surface j"]:::context
View["View Factor Fi-j<br/>Geometry & Distance"]:::implicit
Rad["Radiation Exchange<br/>Qi-j"]:::explicit

Si --- View --- Sj
View --> Rad

<<<< END >>>>

<<<< ID: DIA_3f40bcbe >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fluid["Fluid Domain<br/>Air"]:::implicit
Solid["Solid Domain<br/>Aluminum"]:::implicit
Map["Mapped Boundary<br/>Heat Transfer"]:::explicit

Fluid <--> Map <--> Solid

<<<< END >>>>

<<<< ID: DIA_29ad73d1 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fluid["Fluid Solver<br/>pimpleFoam"]:::implicit
Force["Forces"]:::explicit
Solid["Solid Solver<br/>solidDisplacement"]:::implicit
Disp["Displacement"]:::explicit
Mesh["Mesh Motion<br/>dynamicFvMesh"]:::implicit

Fluid --> Force --> Solid --> Disp --> Mesh --> Fluid

<<<< END >>>>

<<<< ID: DIA_b8db45f9 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Sample["Sample Interface"]:::context
Res["Calculate Residuals"]:::implicit
Aitken["Aitken Relaxation"]:::explicit
Update["Update Fields"]:::implicit
Check{"Converged?"}:::context

Sample --> Res --> Aitken --> Update --> Check
Check -- No --> Sample

<<<< END >>>>

<<<< ID: DIA_391c1df5 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fluid["Fluid Domain<br/>Convection"]:::implicit
Interface["Interface<br/>Coupling"]:::explicit
Solid["Solid Domain<br/>Conduction"]:::implicit

Fluid <--> Interface <--> Solid

<<<< END >>>>

<<<< ID: DIA_b78bb9e1 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
OF["OpenFOAM"]:::implicit
Star["StarCCM+"]:::context
Compare["Comparison"]:::explicit
Metrics["Metrics<br/>Temp & Convergence"]:::implicit

OF --> Compare
Star --> Compare
Compare --> Metrics

<<<< END >>>>

<<<< ID: DIA_fd0f05ed >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Inputs["Phase Masses"]:::context
Check["Conservation Check"]:::explicit
Error["Error Metrics"]:::implicit
Decide{"Pass/Fail"}:::implicit

Inputs --> Check --> Error --> Decide

<<<< END >>>>

<<<< ID: DIA_556f7e5e >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
In["Inlet Momentum"]:::context
CV["Control Volume"]:::implicit
Out["Outlet Momentum"]:::context
Bal["Balance Check"]:::explicit

In --> CV --> Out
CV --> Bal

<<<< END >>>>

<<<< ID: DIA_d5141bd5 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("Simulation"):::context
Loop["Time Loop"]:::implicit
Check["Conservation Checks<br/>Mass, Momentum, Energy"]:::explicit
Report["Report & Log"]:::implicit

Start --> Loop --> Check --> Report --> Loop

<<<< END >>>>

<<<< ID: DIA_f3de9fa4 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Bench["Benchmark Data<br/>Analytic/Exp/Commercial"]:::context
Sim["Setup Simulation"]:::implicit
Run["Run & Check"]:::explicit
Valid{"Criteria Met?"}:::implicit
Fix["Debug Mesh/Schemes"]:::explicit

Bench --> Sim --> Run --> Valid
Valid -- No --> Fix --> Sim
Valid -- Yes --> Done("Validated"):::context

<<<< END >>>>

<<<< ID: DIA_3fbbcc72 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fluid["Solve Fluid<br/>(Dirichlet BC)"]:::implicit
Force["Calc Interface Force"]:::explicit
Solid["Solve Solid<br/>(Neumann BC)"]:::implicit
Disp["Update Displacement"]:::explicit
Mesh["Deform Mesh"]:::implicit
Check{"Converged?"}:::context

Fluid --> Force --> Solid --> Disp --> Mesh --> Check
Check -- No --> Fluid

<<<< END >>>>

<<<< ID: DIA_1cd6ef10 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Create["Create regIOobject"]:::context
CheckIn["checkIn"]:::explicit
Reg["Registered"]:::implicit
Use["Use in Sim"]:::implicit
Clean["checkOut / Destruct"]:::explicit

Create --> CheckIn --> Reg --> Use --> Clean

<<<< END >>>>

<<<< ID: DIA_c137b891 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Time["Time (Global Registry)"]:::context
FM["fluidMesh"]:::implicit
SM["solidMesh"]:::implicit
Fields["Fields: U, p, T"]:::explicit

Time --> FM & SM
FM --> Fields
SM --> Fields

<<<< END >>>>

<<<< ID: DIA_a07b4d31 >>>>
classDiagram
class objectRegistry:::implicit {
+lookupObject()
+checkIn()
+checkOut()
}
class regIOobject:::implicit {
+write()
+db()
}
class fvMesh:::explicit {
+thisDb()
}
class volScalarField:::explicit {
+internalField()
}
objectRegistry <|-- fvMesh
regIOobject <|-- fvMesh
regIOobject <|-- volScalarField
fvMesh "1" *-- "*" volScalarField

<<<< END >>>>

<<<< ID: DIA_b5bc6bdc >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
DB["Time Database"]:::context
R1["Region 1 Registry"]:::implicit
R2["Region 2 Registry"]:::implicit
Obj1["Mesh & Fields 1"]:::explicit
Obj2["Mesh & Fields 2"]:::explicit

DB --> R1 & R2
R1 --> Obj1
R2 --> Obj2

<<<< END >>>>

<<<< ID: DIA_648c0530 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
PBE["PBE Equation"]:::context
Trans["Convection / Growth"]:::implicit
Source["Source Terms"]:::explicit
Mech["Coalescence / Breakup"]:::implicit
Rates["Birth / Death Rates"]:::explicit

PBE --> Trans
PBE --> Source
Source --> Mech
Mech --> Rates

<<<< END >>>>

<<<< ID: DIA_65435de5 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
NS["Solve N-S"]:::implicit
Kernels["Calc Kernels"]:::explicit
Moments["Solve Moments"]:::implicit
Diam["Update Diameter"]:::explicit
Forces["Update Forces"]:::implicit
Check{"Converged?"}:::context

NS --> Kernels --> Moments --> Diam --> Forces --> Check
Check -- No --> NS

<<<< END >>>>

<<<< ID: DIA_b7f47088 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Raw["Raw Fluxes"]:::context
Detect["Detect Unbounded"]:::implicit
Lambda["Calc Limiter (λ)"]:::explicit
Correct["Correct Fluxes"]:::implicit
Solve["Solve Alpha"]:::explicit

Raw --> Detect --> Lambda --> Correct --> Solve

<<<< END >>>>

<<<< ID: DIA_962b4be6 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Alpha["Solve Alpha (MULES)"]:::explicit
Thermo["Update Thermo"]:::implicit
Mom["Solve Momentum"]:::implicit
Press["Pressure Loop"]:::explicit
Energy["Energy / Species"]:::implicit
Check{"PIMPLE Conv?"}:::context

Alpha --> Thermo --> Mom --> Press --> Energy --> Check
Check -- No --> Thermo

<<<< END >>>>

<<<< ID: DIA_69155b33 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Drop["Pressure Drop<br/>p < p_sat"]:::context
Nucl["Nucleation"]:::explicit
Grow["Bubble Growth"]:::implicit
Trans["Transport"]:::implicit
Coll["Collapse"]:::explicit

Drop --> Nucl --> Grow --> Trans --> Coll

<<<< END >>>>

<<<< ID: DIA_6078649e >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Mom["Momentum / Pressure"]:::implicit
Check{"p < p_sat?"}:::context
Evap["Evaporation (+αv)"]:::explicit
Cond["Condensation (-αv)"]:::explicit
Update["Update Props"]:::implicit
Loop{"Converged?"}:::context

Mom --> Check
Check -- Yes --> Evap
Check -- No --> Cond
Evap --> Update
Cond --> Update
Update --> Loop
Loop -- No --> Mom

<<<< END >>>>

<<<< ID: DIA_a24513c1 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Vel{"Flow Velocity"}:::context
Low["Low (< 20m/s)<br/>Schnerr-Sauer"]:::implicit
High["High (> 50m/s)<br/>Kunz/Merkle"]:::explicit
Geom{"Geometry"}:::context
Simple["interPhaseChangeFoam"]:::implicit
Complex["compressibleInter..."]:::explicit

Vel --> Low & High
Low --> Geom
Geom --> Simple & Complex
High --> Complex

<<<< END >>>>

<<<< ID: DIA_0f0e66c5 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Wall["Wall Heat Flux"]:::context
Layer["Thermal Layer"]:::implicit
Check{"TL > Tsat?"}:::context
Boil["Boiling / Nucleation"]:::explicit
Conv["Single Phase Convection"]:::implicit

Wall --> Layer --> Check
Check -- Yes --> Boil
Check -- No --> Conv

<<<< END >>>>

<<<< ID: DIA_9e221270 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Fields["Update p, U, T"]:::implicit
Mass["Correct Mass Transfer"]:::explicit
Source["Update Sources (Su, Sp)"]:::implicit
Solve["Solve Alpha & Energy"]:::explicit
Check{"Converged?"}:::context

Fields --> Mass --> Source --> Solve --> Check
Check -- No --> Fields

<<<< END >>>>

<<<< ID: DIA_9bfc5573 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Base["interfacialForce"]:::context
Types["Types:<br/>Drag, Lift, VirtualMass<br/>WallLubrication"]:::implicit
Models["Models:<br/>SchillerNaumann, Tomiyama<br/>Antal"]:::explicit

Base --> Types --> Models

<<<< END >>>>

<<<< ID: DIA_f4dddd59 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Root["Advanced Multiphase"]:::context
Phenom["Phenomena:<br/>Phase Change, Cavitation<br/>PBE"]:::implicit
Forces["Forces:<br/>Lift, Drag, Lubrication"]:::implicit
Solver["reactingTwoPhaseEulerFoam"]:::explicit

Root --> Phenom & Forces
Phenom --> Solver
Forces --> Solver

<<<< END >>>>

<<<< ID: DIA_3c6e7352 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Files["Files<br/>chem.inp, therm.dat"]:::context
Setup["Setup<br/>Combustion & ODE Solver"]:::implicit
Run["Run reactingFoam"]:::explicit
Check{"Converged?"}:::context
Post["Post-Processing"]:::implicit

Files --> Setup --> Run --> Check
Check -- No --> Run
Check -- Yes --> Post

<<<< END >>>>

<<<< ID: DIA_a78ea6a3 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Theory["Turbulent Combustion"]:::context
PaSR["PaSR<br/>Timescales: τ_mix, τ_chem"]:::implicit
EDC["EDC<br/>Fine Structures"]:::implicit
Scales["Scales<br/>Kolmogorov, Residence"]:::explicit

Theory --> PaSR & EDC
PaSR --> Scales
EDC --> Scales

<<<< END >>>>

<<<< ID: DIA_c708072b >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Input["Input: k, ε, T, Y"]:::context
Times["Calc τ_mix & τ_chem"]:::implicit
Chi["Calc Reacting Fraction χ"]:::explicit
ODE["Solve Chemistry ODEs"]:::explicit
Rates["Return Rates ω"]:::context

Input --> Times --> Chi --> ODE --> Rates

<<<< END >>>>

<<<< ID: DIA_88f06019 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Input["Input: k, ε, ν"]:::context
Struct["Calc Fine Fraction ξ*<br/>Calc Time τ*"]:::implicit
ODE["Solve Chemistry ODEs"]:::explicit
Rates["Return Rates ω"]:::context

Input --> Struct --> ODE --> Rates

<<<< END >>>>

<<<< ID: DIA_5767118d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Select{"Chemistry Speed?"}:::context
Fast["Fast<br/>PaSR"]:::implicit
Slow["Finite Rate<br/>EDC"]:::explicit
Cost{"Budget?"}:::context

Select -- Fast --> Fast
Select -- Slow --> Slow
Slow -- Low Budget --> Fast

<<<< END >>>>

<<<< ID: DIA_e350063a >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Speed{"Speed?"}:::context
PaSR["PaSR<br/>Fast/Cheap"]:::implicit
EDC["EDC<br/>Accurate/Expensive"]:::explicit

Speed -- Fast --> PaSR
Speed -- Slow --> EDC

<<<< END >>>>

<<<< ID: DIA_d17851f9 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Space["Spatial Scales<br/>L (1m) -> η (1e-6m)"]:::implicit
Time["Temporal Scales<br/>Flow (0.1s) -> Chem (1e-9s)"]:::explicit
Problem["Stiff ODEs"]:::context

Space --> Problem
Time --> Problem

<<<< END >>>>

<<<< ID: DIA_91f80b4b >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Prep["Chemkin Files"]:::context
Config["Thermophysics & Model"]:::implicit
Setup["ODE Solver & BCs"]:::implicit
Run["Run Simulation"]:::explicit

Prep --> Config --> Setup --> Run

<<<< END >>>>

<<<< ID: DIA_7c63be99 >>>>
classDiagram
class chemistryModel:::context {
+solve(dt)
+omega()
}
class StandardChemistryModel:::implicit
class ReactionThermophysicalTransportModel:::explicit {
+thermo()
}
chemistryModel <|-- StandardChemistryModel
StandardChemistryModel --> ReactionThermophysicalTransportModel

<<<< END >>>>

<<<< ID: DIA_84acd5aa >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Step1["Step 1: Chemistry<br/>Solve ODEs (Frozen Flow)"]:::explicit
Source["Extract Sources"]:::implicit
Step2["Step 2: Transport<br/>Solve Flow (Frozen Chem)"]:::implicit

Step1 --> Source --> Step2

<<<< END >>>>

<<<< ID: DIA_f90c5067 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Flow["Fluid Time Step"]:::context
Sub1["Chem Sub-step 1"]:::explicit
Sub2["Chem Sub-step 2"]:::explicit
SubN["... Sub-step N"]:::explicit
Update["Update Source Terms"]:::implicit

Flow --> Sub1 --> Sub2 --> SubN --> Update

<<<< END >>>>

<<<< ID: DIA_f187205c >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Files["Input Files<br/>chem.inp / therm.dat"]:::context
Reader["chemkinReader"]:::implicit
Data["Internal Data Structures<br/>speciesTable, reactionList"]:::explicit

Files --> Reader --> Data

<<<< END >>>>

<<<< ID: DIA_d6266906 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Raw["Raw Text"]:::context
Parse["Lexical/Syntax Analysis"]:::implicit
Objects["C++ Objects<br/>speciesTable, ReactionList"]:::explicit

Raw --> Parse --> Objects

<<<< END >>>>

<<<< ID: DIA_31603b6d >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Sim["Reacting Flow"]:::context
Trans["Transport Eqns<br/>Mass Fractions Y_i"]:::implicit
Kinetics["Kinetics ODEs<br/>Reaction Rates ω_i"]:::explicit
Model["Combustion Model<br/>PaSR / EDC"]:::implicit

Sim --> Trans & Kinetics & Model

<<<< END >>>>

<<<< ID: DIA_a9fac630 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Eq["Species Transport"]:::context
Conv["Convection<br/>ρuYᵢ"]:::implicit
Diff["Diffusion<br/>Jᵢ"]:::implicit
React["Reaction<br/>Rᵢ"]:::explicit

Eq --> Conv & Diff & React

<<<< END >>>>

<<<< ID: DIA_448514f9 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Loop["Species Loop"]:::context
Calc["Calc Rates & Transport"]:::implicit
Solve["Solve Eqn"]:::explicit
Bound["Bound 0 < Y < 1"]:::implicit
Sum{"ΣY = 1?"}:::context
Correct["Normalize"]:::explicit

Loop --> Calc --> Solve --> Bound --> Sum
Sum -- No --> Correct --> Sum
Sum -- Yes --> Next("Next"):::context

<<<< END >>>>

<<<< ID: DIA_ee4b783f >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Dist{"Distance y/d"}:::context
Far["Far (>>1)<br/>Normal Lift"]:::implicit
Near["Near (~1)<br/>Reduced Lift"]:::implicit
Contact["Contact (<<1)<br/>Lubrication"]:::explicit

Dist --> Far & Near & Contact

<<<< END >>>>

<<<< ID: DIA_01d37cd3 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
VV["Verification & Validation"]:::context
Code["Code Verification<br/>Math Correct?"]:::implicit
Sol["Solution Verification<br/>Num. Error?"]:::implicit
Mod["Model Validation<br/>Physics Correct?"]:::explicit
Pred["Prediction<br/>Real World"]:::explicit

VV --> Code --> Sol --> Mod --> Pred

<<<< END >>>>

<<<< ID: DIA_f20840ef >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Setup["Meshes: Coarse, Med, Fine"]:::context
Run["Run Simulations"]:::implicit
Calc["Calc Order (p) & GCI"]:::explicit
Check{"GCI < 3%?"}:::context
Pass["Mesh Independent"]:::implicit
Fail["Refine Mesh"]:::explicit

Setup --> Run --> Calc --> Check
Check -- Yes --> Pass
Check -- No --> Fail

<<<< END >>>>

<<<< ID: DIA_09ab9261 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Res["3 Mesh Results"]:::context
Metrics["Calc GCI & Error Norms"]:::implicit
Check{"GCI < 3% & Asymptotic?"}:::context
Acc["Acceptable"]:::implicit
Ref["Refine"]:::explicit

Res --> Metrics --> Check
Check -- Yes --> Acc
Check -- No --> Ref

<<<< END >>>>

<<<< ID: DIA_bf16d9aa >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Code["Code Verification<br/>MMS"]:::implicit
Sol["Solution Verification<br/>Mesh Independence"]:::implicit
Mod["Validation<br/>Compare Exp Data"]:::explicit
Pred["Prediction<br/>Blind Tests"]:::explicit

Code --> Sol --> Mod --> Pred

<<<< END >>>>

<<<< ID: DIA_7cf43be6 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Plan["Plan"]:::context
Ver["Verification<br/>Code & Solution"]:::implicit
Val["Validation<br/>Model Physics"]:::explicit
UQ["UQ & Prediction"]:::explicit
Rep["Report"]:::context

Plan --> Ver --> Val --> UQ --> Rep

<<<< END >>>>

<<<< ID: DIA_dc11104f >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
In["Input Parameters"]:::context
Methods["UQ Methods<br/>Monte Carlo, PCE, Sobol"]:::implicit
Out["Output<br/>Risk & Reliability"]:::explicit

In --> Methods --> Out

<<<< END >>>>

<<<< ID: DIA_8dd6b1a1 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("Start"):::context
Code["Code Verification"]:::implicit
Sol["Solution Verification"]:::implicit
Val["Validation (Exp Data)"]:::explicit
UQ["UQ Analysis"]:::explicit
Check{"Accepted?"}:::context

Start --> Code --> Sol --> Val --> UQ --> Check
Check -- No --> Code

<<<< END >>>>

<<<< ID: DIA_715badf2 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Vol["Control Volume V"]:::context
P1["Phase 1 (V1)"]:::implicit
P2["Phase 2 (V2)"]:::implicit
Pk["Phase k (Vk)"]:::explicit

Vol --> P1 & P2 & Pk

<<<< END >>>>

<<<< ID: DIA_1ec9cf5a >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px
Start("Time Step"):::context
Props["Update Props"]:::implicit
Alpha["Solve Alpha (MULES)"]:::explicit
Mom["Solve Momentum"]:::implicit
Press["Pressure Correction"]:::explicit
Check{"Converged?"}:::context

Start --> Props --> Alpha --> Mom --> Press --> Check
Check -- No --> Alpha

<<<< END >>>>

<<<< ID: DIA_19d4cdf0 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Reference Equations]:::context --> B[Fundamentals]:::implicit
A --> C[Conservation Laws]:::implicit
A --> D[Interfacial Phenomena]:::explicit
A --> E[Closure Relations]:::explicit
A --> F[Special Cases]:::context

B --> B1[Phase Averaging]:::implicit
B --> B2[Conservation Framework]:::implicit

C --> C1[Mass]:::implicit
C --> C2[Momentum]:::implicit
C --> C3[Energy]:::implicit

D --> D1[Surface Tension]:::explicit
D --> D2[Interphase Forces]:::explicit
D --> D3[Heat Transfer]:::explicit

E --> E1[Viscosity Models]:::explicit
E --> E2[Drag Models]:::explicit
E --> E3[Turbulence Models]:::explicit

F --> F1[Incompressible]:::context
F --> F2[Granular]:::context
F --> F3[Compressible]:::context

<<<< END >>>>

<<<< ID: DIA_e7438918 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Multiphase Problem]:::context --> B{Dispersion Type}:::explicit
B -->|Dense Suspension| C[Eulerian-Euler]:::implicit
B -->|Dispersed Bubbles| D[VOF / Lagrangian]:::implicit
B -->|Stratified| C

A --> E{Phase Count}:::explicit
E -->|> 2 Phases| C
E -->|2 Phases| F[Hybrid / Both]:::implicit

A --> G{Scale}:::explicit
G -->|Industrial| C
G -->|Droplet Scale| H[Lagrangian]:::implicit

<<<< END >>>>

<<<< ID: DIA_d9878dc2 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Microscopic Flow<br>Discontinuous Interfaces]:::explicit --> B[Volume Averaging<br>Operator]:::context
B --> C[Phase-Averaged Variables]:::implicit
C --> D[Continuum Fields]:::implicit
D --> E[Governing Equations]:::implicit

<<<< END >>>>

<<<< ID: DIA_c769ed96 >>>>
graph TB
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Multiphase Basics]:::context --> B[Eulerian-Euler Framework]:::implicit
B --> C[Governing Equations]:::implicit
C --> D[Closure Models]:::explicit
D --> E[OpenFOAM Implementation]:::explicit
E --> F[Application]:::implicit

<<<< END >>>>

<<<< ID: DIA_0ace8497 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Problem Scope]:::context --> B{Volume Fraction<br>alpha_d}:::explicit
B -->|High > 0.1| C[Eulerian-Euler]:::implicit
B -->|Low < 0.001| D[Lagrangian]:::implicit
B -->|Medium| E{Phase Count}:::explicit
E -->|2 Phases| F[VOF or E-E]:::implicit
E -->|> 2 Phases| C

<<<< END >>>>

<<<< ID: DIA_86fb5c79 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start Time Step]:::context --> B[Solve alphaEqn.H]:::explicit
B --> C[Construct UEqn.H]:::implicit
C --> D[PIMPLE Loop]:::context
D --> E[Solve pEqn.H]:::implicit
E --> F[Correct Velocities]:::implicit
F --> G{Converged?}:::explicit
G -- No --> D
G -- Yes --> H[Update Turb/Thermo]:::implicit
H --> I[Next Time Step]:::context

<<<< END >>>>

<<<< ID: DIA_3d498e6b >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Particle Acceleration]:::explicit --> B[Fluid Displacement]:::explicit
B --> C[Virtual Mass Force]:::implicit
C --> D[Effective Mass Increase]:::implicit

<<<< END >>>>

<<<< ID: DIA_23f20000 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Accelerating Particle]:::explicit --> B[Fluid Displacement]:::explicit
A --> C[Pressure Field Dev]:::explicit
A --> D[Induced Flow Field]:::explicit

B --> E[Fluid Kinetic Energy]:::implicit
C --> F[Added Inertia]:::implicit
D --> G[Flow Field Change]:::implicit

E --> H[Virtual Mass Force]:::implicit
F --> H
G --> H

<<<< END >>>>

<<<< ID: DIA_29a90d0f >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Liquid-Liquid Systems]:::context --> B[Oil-Water]:::implicit
A --> C[Organic-Aqueous]:::implicit
A --> D[Emulsions]:::implicit

B --> B1[Extraction Columns]:::explicit
B --> B2[Separators]:::explicit
B --> B3[Mixing Tanks]:::explicit

C --> C1[Solvent Extraction]:::explicit
C --> C2[Phase Transfer]:::explicit
C --> C3[Reactors]:::explicit

D --> D1[Stable]:::implicit
D --> D2[Unstable]:::implicit
D --> D3[Multiple]:::implicit

<<<< END >>>>

<<<< ID: DIA_088749c5 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B{Flow Regime}:::explicit
B -->|Separated| C[VOF Method<br>interFoam]:::implicit
B -->|Dispersed| D{Alpha_d}:::explicit

D -->|Dense > 0.3| E[Euler-Euler + KTGF<br>multiphaseEulerFoam]:::implicit
D -->|Dilute < 0.3| F{Slip Vel}:::explicit

F -->|Low Slip| G[Homogeneous<br>Single Velocity]:::implicit
F -->|High Slip| H[Inhomogeneous<br>Separate Velocities]:::implicit

<<<< END >>>>

<<<< ID: DIA_792f8381 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B{Phase Types}:::explicit
B -->|Gas-Liquid| C{Regime}:::explicit
B -->|Liquid-Liquid| D{Regime}:::explicit
B -->|Gas-Solid| E{Conc.}:::explicit
B -->|Liquid-Solid| F{Conc.}:::explicit

C -->|Separated| C1[VOF/interFoam]:::implicit
C -->|Dispersed| C2{Eo Number}:::explicit

C2 -->|Spherical| C2a[Schiller-Naumann<br>Ranz-Marshall]:::implicit
C2 -->|Deformed| C2b[Tomiyama Drag/Lift]:::implicit
C2 -->|Cap Bubbles| C2c[Tomiyama + Wall<br>+ Turb Disp]:::implicit

D -->|Separated| D1[VOF/interFoam]:::implicit
D -->|Dispersed| D2{Viscosity Ratio}:::explicit

D2 -->|High| D2a[Grace Drag]:::implicit
D2 -->|Low| D2b[Schiller-Naumann]:::implicit

E -->|Dilute| E1[Lagrangian/DPM]:::implicit
E -->|Dense| E2[Euler-Euler + KTGF]:::implicit

F -->|Dilute| F1[EE + Wen-Yu]:::implicit
F -->|Dense| F2[EE + KTGF + Ergun]:::implicit

C2a & C2b & C2c & D2a & D2b & E1 & E2 & F1 & F2 --> G{Density Ratio}:::explicit

G -->|Heavy| G1[Ignore Virtual Mass]:::implicit
G -->|Light| G2[Virtual Mass 0.5]:::implicit

G1 & G2 --> H{Reynolds Num}:::explicit

H -->|Laminar| H1[RANS k-epsilon]:::implicit
H -->|Turbulent| H2[LES/DES]:::implicit

H1 & H2 --> I[Setup OpenFOAM]:::context
I --> J[Stability Test]:::explicit
J -->|Stable| K[Add Complexity]:::implicit
J -->|Unstable| L[Relaxation/TimeStep]:::explicit
L --> J
K --> M[Validation]:::implicit

<<<< END >>>>

<<<< ID: DIA_14e4f03e >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B{Conc. Alpha}:::explicit
B -->|< 0.1| C[Dilute: Schiller-Naumann]:::implicit
B -->|> 0.3| D[Dense: KTGF + Ergun]:::implicit
B -->|0.1 - 0.3| E[Medium: Wen-Yu]:::implicit

C & E --> F{Slip Vel}:::explicit
F -->|Low| G[Homogeneous]:::implicit
F -->|High| H[Inhomogeneous]:::implicit

H & G --> I{Polydisperse?}:::explicit
I -->|Yes| J[PBM / MUSIG]:::implicit
I -->|No| K[Single Size Group]:::implicit

J & K --> L{Phase System}:::explicit
L -->|Gas-Liq| M[Tomiyama + VM]:::implicit
L -->|Gas-Sol| N[Wen-Yu + JJ]:::implicit
L -->|Liq-Liq| O[Grace + Film]:::implicit

<<<< END >>>>

<<<< ID: DIA_a6840d48 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
Start[Select Drag Model]:::explicit --> Phase{Phase Type}:::explicit

Phase -->|Gas-Liquid| BubbleSize{Size}:::explicit
Phase -->|Gas-Solid| SolidConc{Conc.}:::explicit
Phase -->|Liquid-Liquid| DropSize{Size}:::explicit

BubbleSize -->|< 1mm| SN[Spherical: Schiller-Naumann]:::implicit
BubbleSize -->|> 1mm| Tomiyama[Deformed: Tomiyama]:::implicit

SolidConc -->|Dilute| WY[Wen-Yu]:::implicit
SolidConc -->|Dense| Gidaspow[Gidaspow / Ergun]:::implicit

DropSize -->|Eo < 0.5| SchillerSmall[Spherical: Schiller-Naumann]:::implicit
DropSize -->|Eo > 0.5| Grace[Deformed: Grace]:::implicit

<<<< END >>>>

<<<< ID: DIA_107ccddc >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Select Turb Model]:::explicit --> B{System Type}:::explicit

B -->|Gas-Liquid| C{Gas Fraction}:::explicit
B -->|Gas-Solid| D{Concentration}:::explicit
B -->|Liquid-Liquid| E[Both Phases]:::implicit

C -->|Low| C1[Standard k-epsilon]:::implicit
C -->|High| C2[Mixture k-epsilon]:::implicit

D -->|Dilute| D1[Dispersed Phase]:::implicit
D -->|Dense| D2[Per-Phase k-epsilon]:::implicit

E --> F[Mixture k-epsilon / SST]:::implicit

<<<< END >>>>

<<<< ID: DIA_c39d3fa0 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
Start[Select Heat Transfer]:::explicit --> App{Goal}:::explicit

App -->|High Precision| Pe{Peclet Num}:::explicit
App -->|Engineering| Eng[Ranz-Marshall]:::implicit

Pe -->|High > 10^4| CHT[Conjugate Heat Transfer]:::implicit
Pe -->|Low <= 10^4| Fried[Friedlander]:::implicit

Eng --> Basic[Standard Application]:::context
CHT --> Advanced[PBM + Heat Transfer]:::implicit
Fried --> Simple[Simple Application]:::context

<<<< END >>>>

<<<< ID: DIA_28aa3e7c >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Stability Strategy]:::explicit --> B{Density Ratio}:::explicit
B -->|High > 100| C[Under-relax: 0.2-0.3]:::implicit
B -->|Low < 10| D[Under-relax: 0.5-0.7]:::implicit

C --> E[Implicit Virtual Mass]:::implicit
D --> F[Explicit Virtual Mass]:::implicit

E --> G[Adaptive Time Stepping]:::explicit
F --> H[Larger Time Step Possible]:::explicit

<<<< END >>>>

<<<< ID: DIA_a3f716ee >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
Start[Select Phase Model]:::explicit --> Alpha{Volume Fraction}:::explicit

Alpha -->|< 0.1| Dilute[Dilute Regime]:::implicit
Alpha -->|0.1 - 0.3| Intermediate[Intermediate Regime]:::implicit
Alpha -->|> 0.3| Dense[Dense Regime]:::implicit

Dilute --> D1[One-way Coupling]:::explicit
Intermediate --> I1[Two-way Coupling]:::explicit
Dense --> D2[Four-way Coupling]:::explicit

D1 --> D1a[Lagrangian / Dispersed]:::implicit
I1 --> I1a[Two-Fluid Model]:::implicit
D2 --> D2a[KTGF / Granular]:::implicit

<<<< END >>>>

<<<< ID: DIA_d2e00de2 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
Start[Consider MUSIG]:::explicit --> Check1{Size Distribution}:::explicit
Check1 -->|Wide Sigma| UseMUSIG[Use MUSIG]:::implicit
Check1 -->|Narrow Sigma| NoMUSIG[Single Size Group]:::implicit

UseMUSIG --> Check2{Size Dependent?}:::explicit
Check2 -->|Significant| Adv[Coalescence & Breakup]:::implicit
Check2 -->|Negligible| Basic[Basic MUSIG]:::implicit

Adv --> Final[PBM + Size Groups]:::implicit

<<<< END >>>>

<<<< ID: DIA_2faed6be >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Computational Domain]:::context --> B[Proc 0: Subdomain]:::implicit
A --> C[Proc 1: Subdomain]:::implicit
A --> D[Proc 2: Subdomain]:::implicit
A --> E[Proc 3: Subdomain]:::implicit

B & C & D & E --> F[Ghost Cells]:::explicit

F --> G[Processor Boundaries]:::context
G --> H[Data Exchange]:::explicit

<<<< END >>>>

<<<< ID: DIA_0f49a413 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Original Distribution]:::context --> B{Load Calculation}:::explicit
B --> C[Cell Count]:::explicit
B --> D[Turbulence Model]:::explicit
B --> E[Interface Area]:::explicit

C & D & E --> F[Load Estimation]:::implicit

F --> G[Graph Partitioning<br>Metis/Scotch]:::implicit
G --> H[Redistribution]:::explicit
H --> I[Balanced Load]:::implicit

<<<< END >>>>

<<<< ID: DIA_ef9f59bf >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[initSwapFields<br>Non-blocking Send]:::explicit
B --> C[Perform Other Computations]:::implicit
C --> D[swapFields<br>Complete Transfer]:::explicit
D --> E[Continue Algorithm]:::implicit

<<<< END >>>>

<<<< ID: DIA_c4623b26 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
Start([Start Time Step]):::context --> Init[Read Controls]:::context
Init --> Courant[Calc CoNum<br>Adjust dt]:::explicit

Courant --> PIMPLE_Start{PIMPLE Loop}:::explicit

PIMPLE_Start --> Alpha[Solve Alpha<br>alphaEqns.H]:::explicit
Alpha --> Alpha_Check{Sum Alpha = 1?}:::explicit
Alpha_Check -->|No| Alpha_Normalize[Normalize Alpha]:::explicit
Alpha_Normalize --> Alpha_Check
Alpha_Check -->|Yes| Momentum[Solve Momentum<br>UEqns.H]:::implicit

Momentum --> Pressure_Construct[Construct P Eqn]:::implicit
Pressure_Construct --> Pressure_Solve[Solve Pressure<br>pEqn.H]:::implicit
Pressure_Solve --> Velocity_Correct[Correct Flux/Vel]:::explicit

Velocity_Correct --> Energy_Check{Solve Energy?}:::explicit
Energy_Check -->|Yes| Energy[Solve Energy<br>EEqns.H]:::implicit
Energy --> Turbulence
Energy_Check -->|No| Turbulence[Correct Turbulence]:::implicit

Turbulence --> Converged{Converged?}:::explicit
Converged -->|No| PIMPLE_Start
Converged -->|Yes| Output_Check{Write Output?}:::context

Output_Check -->|Yes| Write[Write Results]:::context
Write --> Next_Time{End Time?}:::context
Output_Check -->|No| Next_Time

Next_Time -->|No| PIMPLE_Start
Next_Time -->|Yes| End([End Simulation]):::context

<<<< END >>>>

<<<< ID: DIA_de35e0a2 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start PIMPLE Loop]:::context --> B[Momentum Predictor]:::implicit
B --> C[Solve Momentum Eqns]:::implicit
C --> D[Construct Pressure Eqn]:::implicit
D --> E[Solve Pressure Eqn]:::implicit
E --> F[Correct Vel & Flux]:::explicit
F --> G[Solve Energy]:::implicit
G --> H{Convergence?}:::explicit
H -->|No| C
H -->|Yes| I[End Loop]:::context

<<<< END >>>>

<<<< ID: DIA_5b04e9e4 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start Time Loop]:::context --> B[Read Controls]:::context
B --> C[Calc Courant]:::explicit
C --> D[Solve Alpha]:::explicit
D --> E[Solve Momentum]:::implicit
E --> F[Solve Pressure]:::implicit
F --> G[Solve Energy]:::implicit
G --> H{Converged?}:::explicit
H -->|No| D
H -->|Yes| I[Write Results]:::context
I --> J{End Time?}:::context
J -->|No| A
J -->|Yes| K[End]:::context

<<<< END >>>>

<<<< ID: DIA_ce8963e4 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start Time Step]:::context --> B[Predict Velocity u*]:::implicit
B --> C[Solve Momentum]:::implicit
C --> D[Solve Pressure]:::implicit
D --> E[Correct Velocity]:::explicit
E --> F[Correct Vol Fractions]:::explicit
F --> G[Solve Energy]:::implicit
G --> H{Converged?}:::explicit
H -->|No| C
H -->|Yes| I[Next Time Step]:::context

<<<< END >>>>

<<<< ID: DIA_77838d7f >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Domain]:::context --> B[Proc 0]:::implicit
A --> C[Proc 1]:::implicit
A --> D[Proc 2]:::implicit
A --> E[Proc 3]:::implicit

B & C & D & E --> F[Ghost Cells]:::explicit
F --> G[Communication]:::explicit

<<<< END >>>>

<<<< ID: DIA_29f14a21 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[phaseSystem]:::context --> B[phaseModel Dict]:::context
A --> C[HeatTransfer]:::implicit
A --> D[MomentumTransfer]:::implicit
A --> E[MassTransfer]:::implicit

B --> B1[Phase 1: Water]:::explicit
B --> B2[Phase 2: Air]:::explicit
B --> B3[Phase N]:::explicit

C --> C1[Symmetric]:::implicit
C --> C2[Upwind]:::implicit

D --> D1[Drag Models]:::explicit
D --> D2[Lift Models]:::explicit
D --> D3[Virtual Mass]:::explicit
D --> D4[Turb Dispersion]:::explicit

<<<< END >>>>

<<<< ID: DIA_d0ac125d >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[PIMPLE Loop]:::context --> B{Flow Solve?}:::explicit
B -->|No| C{Thermophysics?}:::explicit
C -->|Yes| D[Solve Thermo]:::implicit
D --> E[fluid.solve]:::implicit
E --> F[fluid.correct]:::implicit
F --> G[YEqns.H]:::implicit
G --> H[EEqns.H]:::implicit
H --> I[pEqnComps.H]:::implicit

B -->|Yes| J{Face Momentum?}:::explicit
J -->|Yes| K[pUf/UEqns.H]:::implicit
K --> L[pUf/pEqn.H]:::implicit
J -->|No| M[pU/UEqns.H]:::implicit
M --> N[pU/pEqn.H]:::implicit

I & L & N --> O[Next Iteration]:::context
O --> A

<<<< END >>>>

<<<< ID: DIA_508db8bc >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[phaseSystem]:::context --> B[Drag Model]:::implicit
A --> C[Heat Transfer]:::implicit
A --> D[Mass Transfer]:::implicit
A --> E[Virtual Mass]:::implicit
A --> F[Lift]:::implicit
A --> G[Wall Lub]:::implicit
A --> H[Turb Disp]:::implicit

B --> B1[SchillerNaumann]:::explicit
B --> B2[Ergun]:::explicit

C --> C1[RanzMarshall]:::explicit
C --> C2[Gunn]:::explicit

D --> D1[Henry]:::explicit
D --> D2[HertzKnudsen]:::explicit

<<<< END >>>>

<<<< ID: DIA_ef2cc399 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[Solve Alpha]:::explicit
B --> C[Predict Momentum]:::implicit
C --> D[PISO Loop: P-Corr]:::implicit
D --> E{Converged?}:::explicit
E -->|No| D
E -->|Yes| F[SIMPLE Loop: Relax]:::implicit
F --> G{Converged?}:::explicit
G -->|No| C
G -->|Yes| H[Next Step]:::context

<<<< END >>>>

<<<< ID: DIA_bdde39a8 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Ch.0: CFD Basics]:::context --> B[Ch.1: Multiphase Concepts]:::implicit
B --> C[Ch.2: Governing Eqns]:::implicit
C --> D[Ch.3: Interphase]:::implicit
D --> E[Ch.4: Advanced]:::implicit
E --> F[Ch.5: Validation]:::implicit
F --> G[Real Applications]:::implicit

<<<< END >>>>

<<<< ID: DIA_02b8512b >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
Start[Check Topology]:::context --> Sep{Large Interface?}:::explicit
Sep -- Yes --> VOF[VOF: interFoam]:::implicit
Sep -- No --> Disp{Dispersed?}:::explicit
Disp -- Yes --> Dense{Dense?}:::explicit
Dense -- Yes --> EEDense[multiphaseEulerFoam]:::implicit
Dense -- No --> EEDilute[DPMFoam]:::implicit
Disp -- Mixed --> Trans[Blended Models]:::implicit

<<<< END >>>>

<<<< ID: DIA_33d72a01 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Turbulent Eddies]:::explicit --> B[Velocity Fluctuations]:::explicit
B --> C[Particle Dispersion]:::implicit
C --> D[Enhanced Mixing]:::implicit
D --> E[Homogenized Distribution]:::implicit

<<<< END >>>>

<<<< ID: DIA_1f76d9f0 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Calc mu_t]:::explicit --> B[Compute Phase Fraction]:::explicit
B --> C[Calc D_TD]:::implicit
C --> D[Compute Force F_TD]:::implicit
D --> E[Add to Momentum]:::implicit

<<<< END >>>>

<<<< ID: DIA_19f82700 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Calc k]:::explicit --> B[Calc epsilon]:::explicit
B --> C[Compute Length Scale]:::explicit
C --> D[Calc Coeff D_TD]:::implicit
D --> E[Compute Force]:::implicit

<<<< END >>>>

<<<< ID: DIA_afb86884 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Particle Props]:::explicit --> B[Time Scale tau_p]:::explicit
C[Turbulence Props]:::explicit --> D[Time Scale tau_t]:::explicit

B & D --> E[Stokes Number St]:::implicit
E --> F[Compute Sigma_TD]:::implicit
F --> G[Calc D_TD]:::implicit

<<<< END >>>>

<<<< ID: DIA_33b79917 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B{Drag Valid?}:::explicit
B -->|Yes| C[Add Drag]:::implicit
B -->|No| D{Turb Disp Valid?}:::explicit
C --> D
D -->|Yes| E[Add Turb Disp]:::implicit
D -->|No| F{Lift Valid?}:::explicit
E --> F
F -->|Yes| G[Add Lift]:::implicit
F -->|No| H{Virtual Mass Valid?}:::explicit
G --> H
H -->|Yes| I[Add Virtual Mass]:::implicit
H -->|No| J[Return Total Force]:::context
I --> J

<<<< END >>>>

<<<< ID: DIA_5185d407 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[Calc k, epsilon]:::explicit
B --> C[Eval Alpha Gradient]:::explicit
C --> D[Calc D_disp]:::implicit
D --> E[Calc Force F_disp]:::implicit
E --> F[Add to Momentum]:::implicit
F --> G[End]:::context

<<<< END >>>>

<<<< ID: DIA_5a79de56 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[dragModel Base]:::context --> B[SchillerNaumann]:::implicit
A --> C[IshiiZuber]:::implicit
A --> D[MorsiAlexander]:::implicit
A --> E[SyamlalOBrien]:::implicit
A --> F[Tomiyama]:::implicit

B --> B1[Virtual Cd()]:::explicit
C --> C1[Virtual Cd()]:::explicit
D --> D1[Virtual Cd()]:::explicit
E --> E1[Virtual Cd()]:::explicit
F --> F1[Virtual Cd()]:::explicit

<<<< END >>>>

<<<< ID: DIA_d80a8500 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B{Particle Type}:::explicit
B -->|Spherical| C{Reynolds Num}:::explicit
B -->|Non-Spherical| D[Haider-Levenspiel]:::implicit
B -->|Deformable| E{System}:::explicit

C -->|Re < 1000| F[Schiller-Naumann]:::implicit
C -->|Re > 1000| F

E -->|Gas-Liquid| G{Contamination}:::explicit
E -->|Fluidized Bed| H[Syamlal-OBrien]:::implicit

G -->|Clean| I[Grace / Ishii-Zuber]:::implicit
G -->|Contaminated| J[Tomiyama]:::implicit

F --> K{Concentration}:::explicit
K -->|High| L[Hindered Settling]:::explicit
K -->|Low| M[Basic Model]:::implicit

D --> N[Shape Factor]:::explicit
H --> O[Dense Effects]:::explicit
L --> O

M & N & O & I & J --> P[Set phaseProperties]:::context
P --> Q[Set Under-Relaxation]:::explicit
Q --> R[Validate]:::implicit

<<<< END >>>>

<<<< ID: DIA_db778246 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Total Drag Force]:::context --> B[Form Drag]:::implicit
A --> C[Friction Drag]:::implicit
A --> D[Wave Drag]:::implicit
A --> E[Added Mass]:::implicit

B --> B1[Pressure Delta]:::explicit
B --> B2[Separation]:::explicit
B --> B3[Wake]:::explicit

C --> C1[Viscous Shear]:::explicit
C --> C2[No-slip]:::explicit
C --> C3[Boundary Layer]:::explicit

D --> D1[Deformation]:::explicit
D --> D2[Surface Waves]:::explicit
D --> D3[Interfacial]:::explicit

E --> E1[Virtual Mass]:::explicit
E --> E2[Apparent Inertia]:::explicit
E --> E3[Acceleration]:::explicit

<<<< END >>>>

<<<< ID: DIA_50ce0227 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Single Particle]:::context --> B[Volume Averaging]:::explicit
B --> C[Multiphase System]:::implicit

A --> A1[Single Drag Formula]:::context
C --> C1[Multi Drag Formula]:::implicit

B --> B1[Interfacial Area Density]:::explicit
B1 --> B2[a_i = 6*alpha/d]:::explicit

C1 --> D[Exchange Coeff K]:::implicit
D --> E[K = F / u_rel]:::implicit

<<<< END >>>>

<<<< ID: DIA_db4b8085 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[Analysis]:::context
B --> C{Particle Type}:::explicit
C -->|Spherical| C1{Reynolds Num}:::explicit
C -->|Deformable| C2{System}:::explicit

C1 -->|< 1000| D1[Schiller-Naumann]:::implicit
C1 -->|> 1000| D2[Morsi-Alexander]:::implicit

C2 -->|Bubbles/Drops| E1[Ishii-Zuber]:::implicit
C2 -->|Fluidized Bed| E2[Syamlal-OBrien]:::implicit

D1 & D2 & E1 & E2 --> F[Stability Check]:::explicit
F --> G[Validation]:::implicit

<<<< END >>>>

<<<< ID: DIA_3e55f2ec >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Drag Force Components]:::context --> B[Form Drag]:::implicit
A --> C[Friction Drag]:::implicit
A --> D[Wave Drag]:::implicit
A --> E[Added Mass]:::implicit

B --> B1[Pressure Diff]:::explicit
B --> B2[Separation]:::explicit

C --> C1[Viscous Stress]:::explicit
C --> C2[No-Slip]:::explicit

D --> D1[Surface Waves]:::explicit
D --> D2[Deformation]:::explicit

E --> E1[Virtual Mass]:::explicit
E --> E2[Transient Accel]:::explicit

<<<< END >>>>

<<<< ID: DIA_42541262 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[CAD Geometry STL]:::context --> B[Background blockMesh]:::implicit
B --> C[Castellation / Feat Detect]:::explicit
C --> D[Refinement Boxes]:::explicit
D --> E[Surface Snapping]:::implicit
E --> F[Boundary Layers]:::implicit
F --> G[Final Mesh Quality]:::explicit
G --> H[Export]:::context

<<<< END >>>>

<<<< ID: DIA_f53e0743 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Mesh Quality]:::context --> B[Face Metrics]:::implicit
A --> C[Cell Metrics]:::implicit

B --> D[Orthogonality]:::explicit
D --> D1[Ideal: 90 deg]:::context
D --> D2[cos theta formula]:::context

B --> E[Skewness]:::explicit
E --> E1[Center deviation]:::context
E --> E2[dist formula]:::context

C --> F[Aspect Ratio]:::explicit
F --> F1[Max/Min length]:::context
F --> F2[Ideal < 10]:::context

C --> G[Determinant]:::explicit
G --> G1[Jacobian]:::context
G --> G2[Ideal approx 1]:::context

<<<< END >>>>

<<<< ID: DIA_03a4a7fc >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[CAD]:::context --> B[Surface Prep]:::explicit
B --> C[blockMesh]:::implicit
C --> D[snappyHexMesh]:::implicit
D --> E[Quality Check]:::explicit
E --> F[Case Setup]:::explicit
F --> G[Solver Run]:::implicit
G --> H[Post-Process]:::context
H --> I[Analysis]:::context

<<<< END >>>>

<<<< ID: DIA_16edaf03 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Workflow Management]:::explicit --> B[Project Success]:::implicit
C[Physics Simulation]:::explicit --> B

<<<< END >>>>

<<<< ID: DIA_f31c3767 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
CAD[CAD File]:::context --> STEP[STEP/IGES]:::implicit
STEP --> STL[STL Conversion]:::implicit
STL --> CHECK{Quality?}:::explicit
CHECK -->|Pass| MESH[Meshing]:::implicit
CHECK -->|Fail| REPAIR[Repair Tool]:::explicit
REPAIR --> CHECK

<<<< END >>>>

<<<< ID: DIA_27496a7e >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
START[Background Mesh]:::context --> CAST[Castellation]:::explicit
CAST --> SNAP[Snapping]:::explicit
SNAP --> LAYER[Layer Addition]:::explicit
LAYER --> FINAL[Final Mesh]:::implicit

<<<< END >>>>

<<<< ID: DIA_38927339 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Hardware Resources]:::context --> B[Memory RAM]:::explicit
A --> C[CPU Cores]:::explicit

B --> B1[Per-Core Memory]:::implicit
B --> B2[Comm Buffers]:::implicit

C --> C1[Process Binding]:::implicit
C --> C2[NUMA Awareness]:::implicit

B1 & C1 --> D[Optimal Performance]:::implicit

<<<< END >>>>

<<<< ID: DIA_018320c1 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Setup Case]:::context --> B[Generate Mesh]:::explicit
B --> C[Quality Check]:::explicit
C --> D{OK?}:::explicit
D -->|No| B
D -->|Yes| E[Decompose Domain]:::implicit
E --> F[Submit Job]:::context
F --> G[Run MPI Solver]:::implicit
G --> H[Monitor]:::explicit
H --> I{Converged?}:::explicit
I -->|No| G
I -->|Yes| J[Reconstruct]:::implicit
J --> K[Post-Process]:::context

<<<< END >>>>

<<<< ID: DIA_a0fd03e5 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Complete Mesh]:::context --> B[decomposeParDict]:::explicit
B --> C[Select Method]:::explicit
C --> D{Method}:::explicit

D -->|Simple| E[Coefficients]:::implicit
D -->|Hierarchical| F[Order & Coeffs]:::implicit
D -->|Scotch| G[Weights]:::implicit
D -->|Manual| H[Cell File]:::implicit

E & F & G & H --> I[Run decomposePar]:::implicit

I --> J{Success?}:::explicit
J -->|No| K[Check Mesh]:::explicit
K --> L[Review Dict]:::explicit
L --> C

J -->|Yes| M[Proc Dirs]:::implicit
M --> N[Verify Dist]:::implicit
N --> O[Ready]:::context
O --> P[Run MPI]:::context
P --> Q[Reconstruct]:::context

<<<< END >>>>

<<<< ID: DIA_f4053f54 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B{Mesh Type}:::explicit
B -->|Structured| C[Use Simple]:::implicit
B -->|Unstructured| D{Size}:::explicit

D -->|< 5M| E[Use Scotch]:::implicit
D -->|> 5M| F{Memory}:::explicit

F -->|Plenty| E
F -->|Limited| G[Use Hierarchical]:::implicit

C & E & G --> H{Perf OK?}:::explicit
H -->|Yes| I[Keep]:::implicit
H -->|No| J[Manual/Weights]:::explicit

I & J --> K[Run Sim]:::context

<<<< END >>>>

<<<< ID: DIA_b0537ed8 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start Parallel]:::context --> B[Profiling]:::explicit
B --> C[Monitor Resources]:::explicit
C --> D[Log Usage]:::explicit
D --> E{Perf OK?}:::explicit

E -->|Yes| F[Continue]:::implicit
E -->|No| G[Identify Bottleneck]:::explicit

G --> H{Type}:::explicit
H -->|CPU| I[Check Decomp]:::implicit
H -->|Memory| J[Reduce Mesh / Add RAM]:::implicit
H -->|I/O| K[Optimize Write]:::implicit

I --> L[Adjust Dict]:::explicit
L --> B

F --> M{Converged?}:::explicit
M -->|No| C
M -->|Yes| N[Analyze Logs]:::implicit
N --> O[Stats]:::implicit
O --> P[Report]:::context

<<<< END >>>>

<<<< ID: DIA_9050d072 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Solver Selection]:::context --> B{Mesh Size}:::explicit
B -->|< 100K| C[PCG / PBiCGStab]:::implicit
B -->|100K - 1M| D{Problem}:::explicit
B -->|> 1M| E[GAMG]:::implicit

D -->|Incomp| E
D -->|Comp| F[PBiCGStab]:::implicit

E --> G{Geometry}:::explicit
G -->|Regular| H[Simple Decomp]:::implicit
G -->|Irregular| I[Scotch Decomp]:::implicit

C & F & H & I --> J[Run]:::context

<<<< END >>>>

<<<< ID: DIA_c1017fc7 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Parallel Simulation]:::explicit --> B{I/O Strategy}:::explicit
B --> C[Master Process I/O]:::implicit
B --> D[Collective I/O]:::implicit
B --> E[Independent I/O]:::implicit

C --> C1[Pros: Simple<br>Cons: Serial bottleneck]:::context
D --> D1[Pros: High Perf<br>Cons: Needs Parallel FS]:::context
E --> E1[Pros: Scalable<br>Cons: Complex Mgmt]:::context

<<<< END >>>>

<<<< ID: DIA_4f62e4db >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Setup]:::context --> B[Mesh]:::explicit
B --> C[Check]:::explicit
C --> D{OK?}:::explicit
D -->|No| B
D -->|Yes| E[Decompose]:::implicit
E --> F[Run]:::implicit
F --> G[Monitor]:::explicit
G --> H{Done?}:::explicit
H -->|No| F
H -->|Yes| I[Reconstruct]:::implicit
I --> J[Post]:::context
J --> K[Vis]:::context

<<<< END >>>>

<<<< ID: DIA_6c0403bf >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Setup]:::context --> B[Mesh]:::explicit
B --> C[Check]:::explicit
C --> D{OK?}:::explicit
D -->|No| B
D -->|Yes| E[Decompose]:::implicit
E --> F[Run]:::implicit
F --> G[Monitor]:::explicit
G --> H{Done?}:::explicit
H -->|No| F
H -->|Yes| I[Reconstruct]:::implicit
I --> J[Post]:::context

<<<< END >>>>

<<<< ID: DIA_997ac5a4 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Resources]:::context --> B[Memory]:::explicit
A --> C[CPU]:::explicit

B --> B1[Per-Core RAM]:::implicit
B --> B2[Comm Buffer]:::implicit

C --> C1[Binding]:::implicit
C --> C2[NUMA]:::implicit

B1 & C1 --> D[Performance]:::implicit

<<<< END >>>>

<<<< ID: DIA_0e67f8ec >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[YAML Config]:::explicit --> B[CaseGenerator Class]:::implicit
B --> C[Create Dirs]:::implicit
B --> D[Create Dicts]:::implicit
D --> D1[blockMeshDict]:::explicit
D --> D2[controlDict]:::explicit
D --> D3[Schemes/Solution]:::explicit
B --> E[Mesh Gen]:::explicit
E --> F[Batch Solve]:::implicit
F --> G[QA]:::explicit
G --> H[Report]:::context

<<<< END >>>>

<<<< ID: DIA_d0d23e39 >>>>
graph LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Case]:::context --> B[checkMesh]:::explicit
B --> C[Log Parse]:::implicit
C --> D[Analysis]:::implicit
D --> E[Report]:::implicit
E --> F[Plots]:::implicit
F --> G[QA Assessment]:::explicit

<<<< END >>>>

<<<< ID: DIA_03f03570 >>>>
graph TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Create Mesh]:::explicit --> B[Check Quality]:::explicit
B --> C{Sufficient?}:::explicit
C -->|Yes| D[Proceed]:::implicit
C -->|No| E[Identify Issues]:::explicit
E --> F[Optimize/Refine]:::explicit
F --> B

D --> G[Final Validation]:::implicit
G --> H[Ready]:::context

<<<< END >>>>

<<<< ID: DIA_9151aef6 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Raw CAD]:::context --> B{Format}:::explicit
B --> C[STEP]:::implicit
B --> D[IGES]:::implicit
B --> E[STL]:::implicit

C --> F[Parametric Surface]:::implicit
D --> G[Legacy]:::context
E --> H[Triangulation]:::implicit

F & G & H --> I[Geometry Repair]:::explicit
I --> J[Feature Extraction]:::explicit
J --> K[Validation]:::implicit
K --> L[Meshing]:::context

<<<< END >>>>

<<<< ID: DIA_fcacf1e5 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Geometry]:::context --> B[Surface Prep]:::explicit
B --> C[Features]:::explicit
C --> D[blockMesh]:::implicit
D --> E[snappyHexMesh]:::implicit
E --> F[Snapping]:::implicit
F --> G[Layers]:::implicit
G --> H[Check]:::explicit
H --> I{OK?}:::explicit
I -->|No| J[Refine]:::explicit
J --> E
I -->|Yes| K[Final Mesh]:::context

<<<< END >>>>

<<<< ID: DIA_e32512ed >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Geometry]:::context
B{Strategy}:::explicit
C[blockMesh]:::implicit
D[snappyHexMesh]:::implicit
E[External]:::implicit
F[cgMesh]:::implicit

A --> B
B --> C & D & E & F

C --> G[Structured]:::implicit
D --> H[Surface]:::implicit
E --> I[Hybrid]:::implicit
F --> J[Advanced]:::implicit

G --> K[QA]:::explicit
H --> L[Boundaries]:::explicit
I --> M[Optim]:::explicit
J --> N[Special]:::explicit
K --> O[Automated]:::implicit

<<<< END >>>>

<<<< ID: DIA_225b066c >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Geo Analysis]:::context --> B{Topology}:::explicit
B --> C[H-Grid]:::implicit
B --> D[O-Grid]:::implicit
B --> E[C-Grid]:::implicit
B --> F[Multi-Block]:::implicit

C --> G[Channel]:::context
D --> H[Circular]:::context
E --> I[Airfoil]:::context
F --> J[Complex]:::context

G & H & I & J --> K[Vertex Def]:::explicit
K --> L[Block Conn]:::explicit
L --> M[Grading]:::explicit
M --> N[QA]:::implicit

<<<< END >>>>

<<<< ID: DIA_1fb0d420 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
Main[main<br>Production]:::implicit --> Dev[develop<br>Integration]:::implicit
Dev --> Feature1[feature/mesh]:::explicit
Dev --> Feature2[feature/physics]:::explicit
Dev --> Feature3[feature/BC]:::explicit
Dev --> Hotfix[hotfix/bug]:::explicit
Main --> Hotfix

<<<< END >>>>

<<<< ID: DIA_9b6b00b7 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
Start([Start]):::context --> Checkout[Checkout Develop]:::implicit
Checkout --> Branch[Create Feature Branch]:::implicit
Branch --> Edit[Edit Code/Dicts]:::explicit
Edit --> Stage[git add]:::implicit
Stage --> Commit[git commit]:::implicit
Commit --> Test[Run Local Test]:::explicit
Test --> TestPass{Pass?}:::explicit
TestPass -->|Yes| Push[git push]:::implicit
TestPass -->|No| Edit
Push --> PR[Pull Request]:::explicit
PR --> Review{Review?}:::explicit
Review -->|Changes| Edit
Review -->|Approve| Merge[Merge]:::implicit
Merge --> Cleanup[Delete Branch]:::context
Cleanup --> End([End]):::context

<<<< END >>>>

<<<< ID: DIA_5cee9a5a >>>>
sequenceDiagram
participant A as Engineer A
participant Git as Git Repository
participant B as Engineer B
A->>Git: git checkout -b feature/new-mesh
A->>Git: git commit -m "mesh: add refinement"
A->>Git: git push origin feature/new-mesh

B->>Git: git checkout develop
B->>Git: git pull
B->>Git: git checkout -b feature/bc-update
B->>Git: git commit -m "bc: update inlet profile"

Note over A,B: Parallel Work
A->>Git: Create Pull Request
B->>Git: Create Pull Request

B->>Git: Review & Approve PR
A->>Git: Merge feature/new-mesh
B->>Git: Merge feature/bc-update

Note over Git: Develop Updated

<<<< END >>>>

<<<< ID: DIA_bc86f2b2 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
Repo[Git Repo]:::context --> Monorepo[Monorepo]:::implicit
Repo --> Multirepo[Multi-Repo]:::implicit

Monorepo --> Cases1[Cases/]:::explicit
Cases1 --> Case1[NACA0012]:::context
Cases1 --> Case2[NACA4412]:::context
Cases1 --> Case3[Step Flow]:::context

Monorepo --> Shared[Shared/]:::explicit
Shared --> Scripts[Scripts/]:::context
Shared --> MeshTemplates[Templates/]:::context
Shared --> Documentation[Docs/]:::context

<<<< END >>>>

<<<< ID: DIA_039b8611 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Update Case]:::explicit --> B[Run Mesh Test]:::implicit
B --> C{Quality?}:::explicit
C -->|Fail| D[Adjust Mesh]:::explicit
D --> B
C -->|Pass| E[Run Regression Sim]:::implicit
E --> F{Results OK?}:::explicit
F -->|No| G[Check Physics]:::explicit
G --> E
F -->|Yes| H[Approve Production]:::implicit

<<<< END >>>>

<<<< ID: DIA_25eec330 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Sim Complete]:::context --> B[Extract Data]:::explicit
B --> C[Generate Report]:::implicit
A --> D[Update README]:::implicit
D --> E[Archive in docs/]:::implicit
C --> E
E --> F[Publish]:::context

<<<< END >>>>

<<<< ID: DIA_9ff31f77 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
subgraph ROOT[project_root/]
    DOC[docs/]:::implicit
    SCR[scripts/]:::implicit
    CAS[cases/]:::implicit
    RES[resources/]:::explicit
    RSL[results/]:::explicit
    TST[tests/]:::implicit

    subgraph DOC_SUB[Documentation]
        D1[Specs]:::context
        D2[Theory]:::context
        D3[Reports]:::context
    end

    subgraph SCR_SUB[Automation]
        S1[Python]:::context
        S2[Bash]:::context
        S3[ParaView]:::context
    end

    subgraph CAS_SUB[Simulation]
        C1[Templates]:::context
        C2[Validation]:::context
        C3[Production]:::context
    end
end

ROOT --> DOC & SCR & CAS & RES & RSL & TST
DOC --> DOC_SUB
SCR --> SCR_SUB
CAS --> CAS_SUB

<<<< END >>>>

<<<< ID: DIA_787f8df9 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[Create Dir Struct]:::implicit
B --> C[Store CAD resources]:::explicit
C --> D[Prep Templates cases]:::explicit
D --> E[Write Scripts]:::implicit
E --> F[Run Sim]:::implicit
F --> G[Collect Results]:::implicit
G --> H[Document]:::context

<<<< END >>>>

<<<< ID: DIA_3e69dc79 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
subgraph PHASE1[Phase 1: Setup]
    A1[Define Problem]:::context --> A2[Gather CAD]:::explicit
    A2 --> A3[Dir Structure]:::implicit
end

subgraph PHASE2[Phase 2: Prep]
    B1[Base Case]:::explicit --> B2[Automation]:::implicit
    B2 --> B3[Config]:::explicit
    B3 --> B4[Git Init]:::implicit
end

subgraph PHASE3[Phase 3: Validation]
    C1[Run Validation]:::implicit --> C2[Compare]:::explicit
    C2 --> C3{Valid?}:::explicit
    C3 -->|No| C4[Adjust]:::explicit
    C4 --> C1
    C3 -->|Yes| C5[Document]:::implicit
end

subgraph PHASE4[Phase 4: Prod]
    D1[Run Prod]:::implicit --> D2[Monitor]:::explicit
    D2 --> D3[Post-Process]:::implicit
    D3 --> D4[Report]:::implicit
end

subgraph PHASE5[Phase 5: Docs]
    E1[Update Readme]:::implicit --> E2[Findings]:::implicit
    E2 --> E3[Archive]:::context
end

PHASE1 --> PHASE2
PHASE2 --> PHASE3
PHASE3 --> PHASE4
PHASE4 --> PHASE5

<<<< END >>>>

<<<< ID: DIA_8d44414d >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
subgraph INPUTS[Inputs]
    CAD[CAD]:::explicit
    STL[STL]:::explicit
    EXP[Exp Data]:::explicit
    CFG[Config]:::explicit
end

subgraph PROCESS[Processing]
    PRE[Pre-proc]:::implicit
    MESH[Meshing]:::implicit
    SOLV[Solver]:::implicit
    POST[Post-proc]:::implicit
end

subgraph OUTPUTS[Outputs]
    PLOTS[Plots]:::implicit
    TABS[Tables]:::implicit
    REPS[Reports]:::implicit
    DOCS[Docs]:::implicit
end

CAD --> PRE
STL --> MESH
CFG --> SOLV
EXP --> POST

PRE --> MESH
MESH --> SOLV
SOLV --> POST

POST --> PLOTS & TABS
PLOTS --> REPS
TABS --> DOCS

<<<< END >>>>

<<<< ID: DIA_5f0dbea6 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Def Problem]:::context --> B[Geo & Mesh]:::explicit
B --> C[Setup]:::explicit
C --> D[Init Cond]:::explicit
D --> E[Run]:::implicit
E --> F{Converged?}:::explicit
F -->|No| G[Adjust]:::explicit
G --> E
F -->|Yes| H[Post-Proc]:::implicit
H --> I[Verify]:::explicit
I --> J{Valid?}:::explicit
J -->|No| K[Review Physics]:::explicit
K --> C
J -->|Yes| L[Docs]:::implicit
L --> M[Archive]:::context

<<<< END >>>>

<<<< ID: DIA_b755983b >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Pre-Processing]:::explicit --> B[Meshing]:::implicit
B --> C[Setup]:::explicit
C --> D[Run Solver]:::implicit
D --> E[Post-Processing]:::explicit
E --> F[Reporting]:::implicit

A1[CAD / Domain]:::context --> A
B1[blockMesh / snappy]:::context --> B
C1[BCs / Config]:::context --> C
D1[Parallel / HPC]:::context --> D
E1[Data / Vis]:::context --> E
F1[Docs]:::context --> F

<<<< END >>>>

<<<< ID: DIA_9ca4df29 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Mapping]:::explicit --> B[Pilot]:::explicit
B --> C[Validation]:::implicit
C --> D[Scaling]:::implicit
D --> E[Production]:::implicit

<<<< END >>>>

<<<< ID: DIA_e8598107 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[Geometry]:::explicit
B --> C[Repair]:::explicit
C --> D[Meshing]:::implicit
D --> E{Quality?}:::explicit
E -->|Pass| F[Setup]:::implicit
E -->|Fail| D
F --> G[Solver]:::implicit
G --> H{Conv?}:::explicit
H -->|No| G
H -->|Yes| I[Post]:::implicit
I --> J[Extract]:::explicit
J --> K[Vis]:::explicit
K --> L[Report]:::implicit
L --> M[End]:::context

<<<< END >>>>

<<<< ID: DIA_79b72683 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Geo Module]:::explicit --> D[Orchestrator]:::implicit
B[Mesh Module]:::explicit --> D
C[Solver Module]:::explicit --> D
D --> E[Post Module]:::explicit
D --> F[Report Module]:::explicit

<<<< END >>>>

<<<< ID: DIA_2cc980f5 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Ph1: Basic Scripting]:::explicit --> B[Ph2: Parametric]:::explicit
B --> C[Ph3: HPC]:::implicit
C --> D[Ph4: Automation]:::implicit

A1[Bash]:::explicit --> A
B1[Python]:::explicit --> B
C1[SLURM]:::implicit --> C
D1[CI/CD]:::implicit --> D

<<<< END >>>>

<<<< ID: DIA_cd1886f3 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Solver Output]:::explicit --> B[Processing]:::explicit
B --> C[Rendering]:::implicit
C --> D[Analysis]:::implicit
D --> E[Reporting]:::implicit

<<<< END >>>>

<<<< ID: DIA_bd9f746c >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Rapid Check]:::explicit --> B[paraFoam]:::implicit
C[Deep Analysis]:::explicit --> D[ParaView + VTK]:::implicit
E[Auto Plots]:::explicit --> F[Python]:::implicit

B & D --> G[Visuals]:::implicit
F --> H[Report]:::implicit

<<<< END >>>>

<<<< ID: DIA_68767ca1 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Solver Done]:::context --> B[foamToVTK]:::explicit
B --> C[ParaView 3D]:::implicit
B --> D[Python Extraction]:::implicit

C --> E[Animation]:::implicit
D --> F[2D Plots]:::implicit

E & F --> G[Report]:::implicit
G --> H[Docs]:::context

<<<< END >>>>

<<<< ID: DIA_a1434cf5 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[Results]:::explicit --> B[postProcess Data]:::explicit
B --> C[Python Load]:::implicit
C --> D[Analysis]:::implicit
D --> E[Plotting]:::implicit
E --> F[Report PDF]:::implicit

<<<< END >>>>

<<<< ID: DIA_e096ad29 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Case]:::context --> B[foamToVTK]:::explicit
B --> C{Data Type}:::explicit
C -->|Volume| D[Cell Data]:::implicit
C -->|Surface| D2[Boundary Data]:::implicit
C -->|Lagrangian| E[Particle Data]:::implicit

D & D2 & E --> F[VTK Files]:::implicit
F --> G[ParaView]:::explicit
G --> H[Export]:::context

<<<< END >>>>

<<<< ID: DIA_772657d8 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[VTK Files]:::explicit --> B[Python Script]:::explicit
B --> C[Create Objects]:::implicit
C --> D[Camera/Light]:::implicit
D --> E[Batch Render]:::implicit
E --> F[Image/Video]:::implicit

<<<< END >>>>

<<<< ID: DIA_51fa3bb3 >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Start]:::context --> B[Analysis]:::explicit
B --> C[Algorithm]:::implicit
C --> D[C++ Code]:::explicit
D --> E[Make/files]:::implicit
E --> F[Make/options]:::implicit
F --> G[wmake]:::explicit
G --> H{Compile?}:::explicit
H -->|No| I[Fix]:::explicit
I --> D
H -->|Yes| J[Test]:::implicit
J --> K{Works?}:::explicit
K -->|No| I
K -->|Yes| L[Ready]:::implicit
L --> M[Doc]:::context
M --> N[End]:::context

<<<< END >>>>

<<<< ID: DIA_4b067c60 >>>>
flowchart LR
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000,stroke-dasharray: 5 5
A[Surface Files]:::context --> B[surfaceCheck]:::explicit
B --> C[surfaceFeatures]:::explicit
C --> D[blockMesh]:::implicit
D --> E[snappyHexMesh]:::implicit
E --> F[checkMesh]:::explicit
F --> G{Pass?}:::explicit
G -- No --> E
G -- Yes --> H[setFields]:::explicit
H --> I[decomposePar]:::explicit
I --> J[Solver MPI]:::implicit
J --> K[reconstructPar]:::explicit
K --> L[postProcess]:::explicit
L --> M[foamToVTK]:::explicit
M --> N[ParaView]:::context

<<<< END >>>>

<<<< ID: DIA_ce414cef >>>>
flowchart TD
classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
A[1. Mesh Gen]:::implicit --> B[2. Mesh Valid]:::explicit
B --> C{OK?}:::explicit
C -->|No| D[Fix/Refine]:::explicit
D --> A
C -->|Yes| E[3. Decompose]:::implicit
E --> F[4. Parallel Run]:::implicit
F --> G[5. Reconstruct]:::implicit
G --> H[6. Post-Process]:::explicit
H --> I[7. Analysis]:::explicit

<<<< END >>>>

<<<< ID: DIA_981a5fe8 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[blockMesh<br/>Generate Base Mesh]:::explicit
B[checkMesh 1<br/>Initial Validation]:::implicit
C{Quality OK?}:::context
D[snappyHexMesh<br/>Refine & Snap]:::explicit
E[checkMesh 2<br/>Final Validation]:::implicit
F{Quality OK?}:::context
G[Start Simulation<br/>Ready]:::implicit

%% Edges
A --> B
B --> C
C -->|Pass| D
C -->|Fail| A
D --> E
E --> F
F -->|Pass| G
F -->|Fail| D

<<<< END >>>>

<<<< ID: DIA_eec82c03 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B[Check Mesh]:::implicit
B --> C{Mesh OK?}:::context
C -->|No| D[Refine Mesh]:::explicit
D --> B
C -->|Yes| E[Select Solver & Schemes]:::explicit
E --> F[Set Parameters]:::explicit
F --> G[Run Simulation]:::implicit
G --> H{Converge?}:::context
H -->|No| I[Diagnose]:::explicit
I --> J[Adjust Params/Mesh]:::explicit
J --> G
H -->|Yes| K[Post-Processing]:::implicit
K --> L[Validation]:::implicit
L --> M[Finish]:::context

<<<< END >>>>

<<<< ID: DIA_61d106e5 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start: main]:::context --> B[setRootCase.H]:::implicit
B --> C[createTime.H]:::implicit
C --> D[createMesh.H]:::implicit
D --> E[createFields.H]:::implicit
E --> F{Time Loop?}:::explicit
F -->|Yes| G[Read Time Directory]:::explicit
G --> H[Process Fields]:::explicit
H --> I[Write Results]:::implicit
I --> F
F -->|No| J[End: Return 0]:::context

<<<< END >>>>

<<<< ID: DIA_45241fc2 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Source Files .C]:::explicit --> B[wmake]:::explicit
B --> C[Dependencies Check]:::implicit
C --> D[Compilation]:::explicit
D --> E[Linking Libraries]:::implicit
E --> F[Executable Binary]:::implicit
F --> G[$FOAM_USER_APPBIN/]:::implicit

<<<< END >>>>

<<<< ID: DIA_0539e7ef >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Time Database]:::implicit --> B[Mesh Object Registry]:::implicit
A --> C[Case Directory Files]:::explicit
B --> D[Geometric Fields: p, U, T]:::explicit
B --> E[Surface Fields: phi]:::explicit
B --> F[Boundary Conditions]:::explicit
D --> G[Internal Field]:::implicit
D --> H[Boundary Field]:::implicit
H --> I[Patch 0: inlet]:::implicit
H --> J[Patch 1: outlet]:::implicit
H --> K[Patch 2: walls]:::implicit

<<<< END >>>>

<<<< ID: DIA_cd5fb7dd >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Original Domain]:::explicit --> B[Decompose]:::explicit
B --> C[Processor 0]:::implicit
B --> D[Processor 1]:::implicit
B --> E[Processor 2]:::implicit
B --> F[Processor N]:::implicit
C --> G[Reconstruct]:::explicit
D --> G
E --> G
F --> G
G --> H[Final Result]:::implicit

<<<< END >>>>

<<<< ID: DIA_c8a53731 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Geometry Prep]:::explicit --> B[blockMesh/snappyHexMesh]:::explicit
B --> C[checkMesh]:::context
C -->|Pass| D[decomposePar]:::explicit
C -->|Fail| B
D --> E[Solver Execution]:::implicit
E --> F[reconstructPar]:::explicit
F --> G[postProcess]:::implicit
G --> H[Visualization]:::implicit

<<<< END >>>>

<<<< ID: DIA_8a6dd167 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Mesh Generation]:::explicit --> B[Mesh Validation]:::context
B --> C[Initialization]:::explicit
C --> D[Decomposition]:::explicit
D --> E[Solver Execution]:::implicit
E --> F[Reconstruction]:::explicit
F --> G[Postprocessing]:::implicit
G --> H[Export VTK]:::implicit
H --> I[Analysis]:::implicit

<<<< END >>>>

<<<< ID: DIA_cd95bbc6 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Subgraphs
subgraph Pre [Pre-Solver Phase]
    P1[Geometry]:::explicit
    P2[Mesh Gen]:::explicit
    P3[Refinement]:::explicit
    P4[Quality Check]:::context
    P5[BC Setup]:::explicit
end

subgraph Sol [Solution Phase]
    S1[Decompose]:::explicit
    S2[Solver Run]:::implicit
    S3[Reconstruct]:::explicit
end

subgraph Post [Post-Solver Phase]
    Pst1[Forces]:::implicit
    Pst2[Wall Data]:::implicit
    Pst3[Visualization]:::implicit
    Pst4[Analysis]:::context
end

%% Links
P4 --> S1
P5 --> S1
S3 --> Pst1
Pst1 --> Pst2
Pst2 --> Pst3
Pst3 --> Pst4

<<<< END >>>>

<<<< ID: DIA_72aa8d32 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Manual Mesh<br/>4-8 Hrs]:::explicit --> B[blockMesh<br/>10-30 Mins]:::implicit
B --> C[Define Blocks & Grading]:::implicit
C --> D[Structured Quality Mesh]:::implicit
D --> E[Time Saved: 90-95%]:::implicit

<<<< END >>>>

<<<< ID: DIA_57fd2cc9 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[OpenFOAM Fields]:::implicit --> B[foamToVTK]:::explicit
A --> C[foamToEnsight]:::explicit
A --> D[sampleDict]:::explicit

B --> E[ParaView]:::implicit
C --> F[Ensight]:::implicit
D --> G[Python/MATLAB]:::implicit

E --> H[Actionable Data]:::context
F --> H
G --> H

<<<< END >>>>

<<<< ID: DIA_929f3be9 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start Simulation]:::context --> B[checkMesh]:::implicit
B --> C{Mesh OK?}:::context
C -->|No| D[Fix Mesh]:::explicit
D --> B

C -->|Yes| E[checkBoundaryConditions]:::implicit
E --> F{BC OK?}:::context
F -->|No| G[Fix BC]:::explicit
G --> E

F -->|Yes| H[Check Dimensions]:::implicit
H --> I{Units OK?}:::context
I -->|No| J[Fix Units]:::explicit
J --> H

I -->|Yes| K[Run Solver]:::implicit
K --> L[Monitor Residuals]:::implicit
L --> M{Converged?}:::context
M -->|No| N[Adjust Settings]:::explicit
N --> K
M -->|Yes| O[Success]:::implicit

<<<< END >>>>

<<<< ID: DIA_ff0ce5d7 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Base Mesh<br>blockMesh]:::explicit --> B[Castellated Mesh<br>Refinement]:::implicit
B --> C[Snap to Surface<br>Projection]:::implicit
C --> D[Boundary Layers<br>Add Layers]:::implicit
D --> E[Final Mesh<br>checkMesh]:::implicit

<<<< END >>>>

<<<< ID: DIA_a3d9495c >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Geometry CAD/STL]:::explicit --> B[blockMesh]:::explicit
B --> C[snappyHexMesh]:::explicit
C --> D[checkMesh]:::context
D -->|Fail| C
D --> E[setFields]:::explicit
E --> F[decomposePar]:::explicit
F --> G[mpirun Parallel Solver]:::implicit
G -->|Monitor| L[foamMonitor]:::context
G --> H[reconstructPar]:::explicit
H --> I[foamToVTK]:::explicit
I --> J[postProcess]:::implicit
J --> K[Visualization]:::implicit

<<<< END >>>>

<<<< ID: DIA_d8a5b19e >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Completed Simulation]:::context --> B[Data Validation]:::implicit
B --> C[Field Extraction]:::explicit
B --> D[Force Analysis]:::explicit
B --> E[Surface Integration]:::explicit

C --> F[Python Processing]:::implicit
D --> F
E --> F

F --> G[Statistical Analysis]:::implicit
F --> H[Visualization]:::implicit
F --> I[Theory Check]:::context

G --> J[Report]:::implicit
H --> J
I --> J
J --> K[Final Output]:::implicit

<<<< END >>>>

<<<< ID: DIA_8fecba0c >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[CFD Solver]:::implicit --> B[Forces Function]:::explicit
B --> C[Output Files]:::context
C --> D[Processing Script]:::explicit
D --> E[Convergence Check]:::implicit
E --> F{Converged?}:::context
F -->|No| G[Continue/Adjust]:::explicit
F -->|Yes| H[Averaging]:::implicit
H --> I[Data Comparison]:::implicit
I --> J[Validation]:::implicit
J --> K[Optimization]:::implicit

<<<< END >>>>

<<<< ID: DIA_6c09b649 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Mesh Quality Check]:::explicit --> B[Setup Forces]:::explicit
B --> C[Run & Monitor]:::implicit
C --> D[Extract Forces]:::implicit
D --> E[Validation]:::implicit
E --> F[Optimize]:::explicit

<<<< END >>>>

<<<< ID: DIA_0a5f62f7 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Existing Case]:::context --> B{Analyze}:::context
B --> C[Backup]:::explicit
C --> D{Strategy}:::context
D --> E[Minor Changes]:::implicit
D --> F[Major Changes]:::implicit
E --> G[Modify Incrementally]:::explicit
F --> H[Test Components]:::explicit
G --> I[Test Run]:::implicit
H --> I
I --> J{Verify}:::context
J -->|Pass| K[Document & Deploy]:::implicit
J -->|Fail| L[Debug]:::explicit
L --> G

<<<< END >>>>

<<<< ID: DIA_1c6f3cf5 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Raw CFD Data]:::explicit --> B{Validation}:::context
B --> C[Field Extraction]:::implicit
C --> D[Derived Calc]:::implicit
D --> E[Boundary Layer]:::implicit
E --> F[Turbulence Stats]:::implicit
F --> G[Visualization]:::implicit
G --> H[Theory Check]:::context
H --> I[Reporting]:::implicit

<<<< END >>>>

<<<< ID: DIA_50240044 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Raw CFD Data]:::explicit --> B[Field Extraction]:::implicit
A --> C[Force Analysis]:::implicit
A --> D[Surface Integration]:::implicit

B --> E[Probes]:::context
B --> F[Sampling]:::context
B --> G[Vol Integrate]:::context

C --> H[Coefficients Cd/Cl]:::implicit
C --> I[Force Decomposition]:::implicit

D --> J[Wall Shear/y+]:::implicit
D --> K[Heat Transfer]:::implicit

E --> L[Engineering Insights]:::explicit
F --> L
G --> L
H --> L
I --> L
J --> L
K --> L

<<<< END >>>>

<<<< ID: DIA_a8a316d0 >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Case Directory]:::context --> B[Time Directories]:::explicit
B --> C[0/, 0.1/, ...]:::explicit
C --> D[Field Files]:::implicit
D --> E[volScalarField]:::implicit
D --> F[volVectorField]:::implicit
D --> G[volTensorField]:::implicit

A --> H[postProcessing/]:::context
H --> I[probes/]:::implicit
H --> J[forces/]:::implicit
H --> K[graphs/]:::implicit

<<<< END >>>>

<<<< ID: DIA_7cdc0219 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Define Objectives]:::explicit --> B[Identify Quantities]:::explicit
B --> C[Select Utilities]:::implicit
C --> D[Config functionObjects]:::implicit
D --> E[Run Simulation]:::implicit
E --> F[Runtime Monitor]:::context
F --> G[Convergence Check]:::context
G --> H{Converged?}:::context
H -->|No| E
H -->|Yes| I[Batch Post-Processing]:::implicit
I --> J[Validation]:::implicit
J --> K[Engineering Analysis]:::explicit
K --> L[Reporting]:::explicit

<<<< END >>>>

<<<< ID: DIA_ba3d8aae >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Near-Wall Region]:::context -->|F1 -> 1| B[k-omega Model]:::implicit
C[Free-Stream Region]:::context -->|F1 -> 0| D[k-epsilon Model]:::implicit
B --> E[Blended Model]:::explicit
D --> E

<<<< END >>>>

<<<< ID: DIA_187609fa >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Turbulent Flow]:::context --> B[Spatial Filtering]:::explicit
B --> C[Resolved Scales<br/>Large Eddies]:::implicit
B --> D[Subgrid-Scale SGS<br/>Small Eddies]:::implicit
C --> E[Solved Directly]:::implicit
D --> F[Modeled]:::implicit

<<<< END >>>>

<<<< ID: DIA_bb04ec64 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Turbulent Flow]:::context --> B{Unsteady?}:::context
B -->|No| C[RANS]:::implicit
B -->|Yes| D{Resources?}:::context
D -->|No| E[Hybrid RANS-LES]:::implicit
D -->|Yes| F{Complex Geom?}:::context
F -->|Low| G[Smagorinsky]:::implicit
F -->|High| H[Dynamic/WALE]:::implicit

<<<< END >>>>

<<<< ID: DIA_936db73f >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Turbulence Modeling]:::explicit --> B[RANS: Statistical]:::implicit
A --> C[LES: Filtered]:::implicit
A --> D[DNS: Resolved]:::implicit
B --> B1[k-epsilon]:::implicit
B --> B2[k-omega SST]:::implicit
C --> C1[Smagorinsky]:::implicit
C --> C2[WALE]:::implicit

<<<< END >>>>

<<<< ID: DIA_98cf552d >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Wall y+ = 0]:::explicit
B[Viscous Sublayer y+ < 5]:::implicit
C[Buffer Layer 5 < y+ < 30]:::context
D[Log-Law Region 30 < y+ < 300]:::implicit
E[Outer Region y+ > 300]:::context

A --> B --> C --> D --> E

<<<< END >>>>

<<<< ID: DIA_82630404 >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B{Precision?}:::context
B -->|High| C[Wall-Resolved y+~1]:::explicit
B -->|Medium| D{Resources?}:::context
D -->|Limited| E[Wall Functions y+ 30-300]:::implicit
D -->|OK| C

C --> F[Fine Mesh / High Cost]:::explicit
E --> G[Coarse Mesh / Low Cost]:::implicit

<<<< END >>>>

<<<< ID: DIA_f5ae15a2 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B{Reynolds No?}:::context
B -->|Low < 10^5| C[Low-Re y+ < 1]:::implicit
B -->|High > 10^6| D{Precision?}:::context

D -->|High| E[Wall-Resolved y+ < 1]:::implicit
D -->|Med| F{Resources?}:::context

F -->|Limited| G[Wall Function y+ 30-300]:::explicit
F -->|OK| H[Wall-Resolved y+ < 1]:::implicit

C --> I{Heat Transfer?}:::context
I -->|Yes| E
I -->|No| J[Wall Function y+ 30-100]:::explicit

E --> K[Fine Mesh]:::implicit
G --> L[Coarse Mesh]:::explicit
J --> L

<<<< END >>>>

<<<< ID: DIA_31ad31f7 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Integral Scale<br/>Large Eddies]:::explicit -->|Energy Cascade| B[Inertial Subrange]:::implicit
B -->|Transfer| C[Kolmogorov Scale<br/>Small Eddies]:::implicit
C -->|Dissipation| D[Heat]:::context

<<<< END >>>>

<<<< ID: DIA_6603bcb6 >>>>
classDiagram
class turbulenceModel {
+virtual tmp~volScalarField~ nut() const
+virtual tmp~volScalarField~ k() const
+virtual void correct()
}
class RASModel {
    +simulationType RAS
    +dictionary coeffDict_
}

class eddyViscosity {
    +volScalarField nut_
    +volScalarField k_
    +virtual void correctNut()
}

class kEpsilon {
    +volScalarField epsilon_
    +virtual tmp~volScalarField~ epsilonGen() const
}

turbulenceModel <|-- RASModel
RASModel <|-- eddyViscosity
eddyViscosity <|-- kEpsilon

<<<< END >>>>

<<<< ID: DIA_52c019b7 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[U field]:::implicit -->|Coupled| B[Pressure Eq]:::implicit
C[T field]:::implicit -->|Density Change| D[Rho]:::implicit
D -->|Buoyancy| A
D -->|Density| E[Momentum Eq]:::implicit
C -->|Source Term| F[Energy Eq]:::implicit
E -->|Solve| G[U new]:::explicit
B -->|Solve| H[p new]:::explicit
F -->|Solve| I[T new]:::explicit

<<<< END >>>>

<<<< ID: DIA_a17fcd65 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Rayleigh Number]:::context --> B{Ra Value}:::context
B -->|< 10^3| C[Conduction]:::implicit
B -->|10^3 - 10^9| D[Laminar Convection]:::implicit
B -->|> 10^9| E[Turbulent Convection]:::explicit

C --> F[No Motion]:::context
D --> G[Stable Rolls]:::implicit
E --> H[Chaotic]:::explicit

<<<< END >>>>

<<<< ID: DIA_ef4cd3eb >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Fluid Domain]:::implicit <-->|Heat Flux| B[Interface]:::explicit
B <-->|Heat Flux| C[Solid Domain]:::implicit
B -->|T_f = T_s| D[Temp Continuity]:::explicit
B -->|Flux Balance| E[Flux Continuity]:::explicit

<<<< END >>>>

<<<< ID: DIA_d6e290af >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Hot Fluid Inlet]:::explicit --> B[Shell Side]:::implicit
B --> C[Tube Walls]:::implicit
C --> D[Tube Side]:::implicit
D --> E[Cold Fluid Outlet]:::explicit
C --> F[Heat Transfer]:::explicit
F --> G[Temp Distribution]:::implicit

<<<< END >>>>

<<<< ID: DIA_27d56d67 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start Time Step]:::context --> B[Momentum Predictor]:::implicit
B --> C[Solve Momentum]:::implicit
C --> D[Intermediate U*]:::explicit
D --> E[PISO Loop]:::implicit
E --> F{Correct < nCorr?}:::context
F -->|Yes| G[Solve Pressure]:::explicit
G --> H[Correct U]:::explicit
H --> F
F -->|No| I[Update Fields]:::implicit
I --> J[Next Time Step]:::context

<<<< END >>>>

<<<< ID: DIA_7825a5ae >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start Time Step]:::context --> B[PIMPLE Outer Loop]:::implicit
B --> C{Outer < nOuter?}:::context
C -->|Yes| D[Momentum Predictor]:::implicit
D --> E[PISO Inner Loop]:::implicit
E --> F{Inner < nCorr?}:::context
F -->|Yes| G[Solve Pressure]:::explicit
G --> H[Correct U]:::explicit
H --> F
F -->|No| I[Under-Relaxation]:::context
I --> C
C -->|No| J[Final Update]:::implicit
J --> K[Next Time Step]:::context

<<<< END >>>>

<<<< ID: DIA_2a1fe01e >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B{Time Dependent?}:::context
B -->|Transient| C{Newtonian?}:::context
B -->|Steady| D{Turbulence?}:::context

C -->|Yes| E{Time Step?}:::context
C -->|No| F[nonNewtonianIcoFoam]:::implicit

E -->|Small dt| G[icoFoam]:::explicit
E -->|Large dt| H[pimpleFoam]:::explicit

D -->|Yes| I{Rotating?}:::context
D -->|No| J[simpleFoam]:::implicit

I -->|Yes| K[SRFSimpleFoam]:::explicit
I -->|No| J

<<<< END >>>>

<<<< ID: DIA_1b071dd5 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Incompressible Flow]:::context --> B{Time Dependent?}:::context
B -->|Yes| C{Turbulent?}:::context
B -->|No| D[simpleFoam]:::implicit
C -->|No| E[icoFoam]:::explicit
C -->|Yes| F{Large Steps?}:::context
F -->|Yes| G[pimpleFoam]:::explicit
F -->|No| E
D --> H[SIMPLE Algo]:::implicit
E --> I[PISO Algo]:::implicit
G --> J[PIMPLE Algo]:::implicit

<<<< END >>>>

<<<< ID: DIA_b9f8a036 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B[Check Mesh]:::implicit
B --> C{Quality OK?}:::context
C -->|No| D[Fix Mesh]:::explicit
D --> B
C -->|Yes| E[Set Initial Conditions]:::implicit
E --> F[Set BCs]:::implicit
F --> G[Set controlDict]:::implicit
G --> H[Set fvSchemes]:::implicit
H --> I[Set fvSolution]:::implicit
I --> J[Run Solver]:::explicit
J --> K[Check Residuals]:::implicit
K --> L{Converged?}:::context
L -->|No| M[Adjust Params]:::explicit
M --> K
L -->|Yes| N[Check Physics]:::implicit
N --> O{Stable?}:::context
O -->|No| M
O -->|Yes| P[Success]:::implicit
P --> Q[Analysis]:::context

<<<< END >>>>

<<<< ID: DIA_d5f14016 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Iteration Start]:::context --> B[Momentum Predictor]:::implicit
B --> C[Pressure Correction]:::explicit
C --> D[Correct U]:::implicit
D --> E[Correct p]:::implicit
E --> F[Transport Eqns]:::implicit
F --> G{Converged?}:::context
G -->|No| A
G -->|Yes| H[End]:::context

<<<< END >>>>

<<<< ID: DIA_800a3ec0 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Physical Reality]:::explicit --> B[Math Model]:::implicit
B --> C[Numerical Solution]:::implicit
C --> D[Computer Impl]:::implicit

D -.->|Verification| C
C -.->|Validation| B
B -.->|Validation| A

<<<< END >>>>

<<<< ID: DIA_1df3f904 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[CAD Model]:::explicit --> B[Simplify]:::implicit
B --> C[Create Domains]:::implicit
C --> D[Interfaces]:::implicit
D --> E[Generate Mesh]:::explicit
E --> F[Check Quality]:::context
F --> G[Run Simulation]:::implicit

<<<< END >>>>

<<<< ID: DIA_eefd837a >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Object]:::explicit --> B[Upstream 5-10L]:::implicit
A --> C[Downstream 15-20L]:::implicit
A --> D[Side 5-10L]:::implicit
A --> E[Top 5-10L]:::implicit

<<<< END >>>>

<<<< ID: DIA_3e4022cb >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Geometry Prep]:::explicit --> B[Block Mesh]:::implicit
B --> C[Surface Refine]:::implicit
C --> D[Boundary Layers]:::implicit
D --> E[Quality Check]:::context
E --> F[Ready]:::implicit

<<<< END >>>>

<<<< ID: DIA_a3fe37cb >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Pipe Flow]:::context --> B{Re Number}:::context
B -->|< 2300| C[Laminar]:::implicit
B -->|2300 - 4000| D[Transitional]:::implicit
B -->|> 4000| E[Turbulent]:::explicit

C --> F[Parabolic Profile]:::implicit
E --> G[Plug-like Profile]:::implicit

F --> H[f = 64/Re]:::context
G --> I[Colebrook-White]:::context

<<<< END >>>>

<<<< ID: DIA_e554a347 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Inflow]:::context --> B[Inlet]:::implicit
B --> C[Static Mixer]:::explicit
C --> D[Split/Merge]:::implicit
D --> E[Chaotic Mixing]:::implicit
E --> F[Outlet]:::implicit
F --> G[Outflow]:::context

C --> H[Dean Vortices]:::implicit
C --> I[Flow Division]:::implicit
C --> J[Recombination]:::implicit

<<<< END >>>>

<<<< ID: DIA_07a10cb3 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Large Domain]:::context --> B[Decomposition]:::explicit
B --> C1[Proc 0]:::implicit
B --> C2[Proc 1]:::implicit
B --> C3[Proc N]:::implicit
C1 --> D[MPI Comm]:::explicit
C2 --> D
C3 --> D
D --> E[Parallel Solve]:::implicit
E --> F[Reconstruct]:::explicit

<<<< END >>>>

<<<< ID: DIA_4c74af54 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Fine Grid]:::explicit --> B[Pre-smooth]:::implicit
B --> C[Residual]:::implicit
C --> D[Restrict]:::implicit
D --> E[Solve Coarse]:::explicit
E --> F[Prolongate]:::implicit
F --> G[Correct]:::implicit
G --> H[Post-smooth]:::implicit
H --> I{Converged?}:::context
I -->|No| B
I -->|Yes| J[Done]:::context

<<<< END >>>>

<<<< ID: DIA_4fbe5c8c >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Monitor Load]:::context --> B{Imbalanced?}:::context
B -->|No| A
B -->|Yes| C[Trigger Repartition]:::explicit
C --> D[Calc Partition]:::implicit
D --> E[Migrate Data]:::implicit
E --> F[Consistency Check]:::implicit
F --> G[Resume]:::implicit
G --> A

<<<< END >>>>

<<<< ID: DIA_8daad0c8 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Serial Case]:::implicit --> B[decomposePar]:::explicit
B --> C[mpirun]:::explicit
C --> D[reconstructPar]:::explicit
D --> E[Post-Process]:::implicit

<<<< END >>>>

<<<< ID: DIA_6c56d4a9 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[N-S Equations]:::context --> B[Spatial Filtering]:::explicit
B --> C[Large Eddies]:::implicit
B --> D[Small Eddies]:::implicit
C --> E[Resolved]:::implicit
D --> F[Modeled SGS]:::explicit

<<<< END >>>>

<<<< ID: DIA_1480b2e8 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Inlet]:::context --> B[Near-Wall RANS]:::implicit
B --> C[Separated LES]:::explicit
C --> D[Outlet]:::context

<<<< END >>>>

<<<< ID: DIA_f5b989c0 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Laminar]:::context --> B{Mechanism}:::context
B --> C[Natural T-S Waves]:::implicit
B --> D[Bypass High Tu]:::explicit
B --> E[Separation Induced]:::explicit
C --> F[Turbulent]:::implicit
D --> F
E --> F

<<<< END >>>>

<<<< ID: DIA_8cb9ef07 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B{Resolution?}:::context
B -->|Basic| C[RANS]:::implicit
B -->|High| D{Re Number?}:::context

D -->|Low| E[LES]:::explicit
D -->|High| F{Separation?}:::context

F -->|Limited| G[DES/DDES]:::implicit
F -->|Massive| H[SAS]:::implicit

C --> I{Anisotropy?}:::context
I -->|High| J[RSM]:::explicit
I -->|Low| K[k-eps / k-omega]:::implicit

E --> L{Transition?}:::context
L -->|Yes| M[gamma-ReTheta]:::explicit
L -->|No| N[Standard LES]:::implicit

<<<< END >>>>

<<<< ID: DIA_758745f7 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B[Solve Mesh]:::implicit
B --> C[Error Indicators]:::implicit
C --> D{Refine?}:::context
D -->|Yes| E[Mark Cells]:::explicit
D -->|No| F[Continue]:::implicit
E --> G[Update Topology]:::explicit
G --> H[Interpolate]:::implicit
H --> F

<<<< END >>>>

<<<< ID: DIA_6a411566 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Subgraphs
subgraph Element [Element K]
    A[Element Center]:::implicit --> B[Interior Solution]:::implicit
    B --> C[Boundary Flux]:::explicit
end

C --> D[Numerical Flux]:::explicit
D --> E[Neighbor]:::context
E --> C

<<<< END >>>>

<<<< ID: DIA_5b94cfcb >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Fine Grid]:::explicit --> B[Pre-smooth]:::implicit
B --> C[Residual]:::implicit
C --> D[Restrict]:::implicit
D --> E[Coarse Solve]:::explicit
E --> F[Prolongate]:::implicit
F --> G[Post-smooth]:::implicit
G --> H[Update]:::implicit

<<<< END >>>>

<<<< ID: DIA_9f695885 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Current CFD]:::implicit --> B[Digital Twins]:::implicit
B --> C[Real-time Sim]:::explicit
C --> D[AI-Physics]:::explicit
D --> E[Quantum CFD]:::context

<<<< END >>>>

<<<< ID: DIA_a986e8d5 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Cell P]:::implicit --> B[Neighbor N]:::implicit
A --> C[Face f]:::explicit
B --> C
C --> D[Flux Calculation]:::explicit

<<<< END >>>>

<<<< ID: DIA_0bbb5220 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Linear Interp]:::implicit --> B[Decoupled P]:::explicit
B --> C[Checkerboard]:::explicit
C --> D[Oscillations]:::explicit

<<<< END >>>>

<<<< ID: DIA_dbb64b49 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B[Predictor]:::implicit
B --> C[PISO Loop]:::explicit
C --> D[Solve P]:::implicit
D --> E[Correct U & Flux]:::implicit
E --> F{More Loops?}:::context
F -->|Yes| D
F -->|No| G[Next Step]:::context

<<<< END >>>>

<<<< ID: DIA_ea9565cb >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start Step]:::context --> B[Outer Loop]:::explicit
B --> C[Momentum Solve]:::implicit
C --> D[Inner PISO Loop]:::explicit
D --> E[Pressure Solve]:::implicit
E --> F[Correct U]:::implicit
F --> G{Inner Converged?}:::context
G -->|No| D
G -->|Yes| H[Relax Fields]:::implicit
H --> I{Outer Converged?}:::context
I -->|No| B
I -->|Yes| J[Next Step]:::context

<<<< END >>>>

<<<< ID: DIA_ed2036ea >>>>
quadrantChart
title Stability vs Time Step
x-axis "Small dt (Co < 1)" --> "Large dt (Co > 1)"
y-axis "Low Stability" --> "High Stability"
quadrant-1 "PISO optimal"
quadrant-2 "PIMPLE robust"
quadrant-3 "SIMPLE steady"
quadrant-4 "All stable"

<<<< END >>>>

<<<< ID: DIA_0f70a479 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Init p*, u*]:::context --> B[Predictor: Solve U]:::implicit
B --> C[Solve P Correction]:::explicit
C --> D[Correct Velocity]:::implicit
D --> E[Update Pressure]:::implicit
E --> F[Under-Relaxation]:::explicit
F --> G{Converged?}:::context
G -->|No| A
G -->|Yes| H[End]:::context

<<<< END >>>>

<<<< ID: DIA_8e02e8e3 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Not Converging]:::explicit --> B{Pattern?}:::context
B -->|Oscillatory| C[Relaxation Issues]:::implicit
B -->|Increasing| D[Mesh Issues]:::implicit
B -->|Stalled| E[Criteria Issues]:::implicit

C --> F[Reduce Factors]:::explicit
F --> F1[alpha_p: 0.1-0.2]:::implicit
F --> F2[alpha_u: 0.3-0.5]:::implicit

D --> H[Check Mesh]:::explicit
H --> H1[Skewness < 0.85]:::implicit
H --> H2[Non-Ortho < 70]:::implicit
H1 --> I[Fix Mesh]:::explicit
H2 --> I

E --> J[Adjust Criteria]:::explicit
J --> J1[Relax Tolerance]:::implicit
J --> J2[Increase Iters]:::implicit

F1 --> G[Test]:::context
F2 --> G
I --> L{Converged?}:::context
J1 --> K[Re-run]:::context
J2 --> K
G --> L
K --> L
L -->|Yes| M[Solved]:::implicit
L -->|No| N[Debug]:::explicit

<<<< END >>>>

<<<< ID: DIA_21752c76 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B{Steady State?}:::context
B -->|Yes| C[SIMPLE]:::implicit
B -->|No| D{Time Accurate?}:::context

D -->|Yes| E{Co < 1?}:::context
D -->|No| F{Complex Physics?}:::context

E -->|Yes| G[PISO]:::implicit
E -->|No| H[PIMPLE + nCorr]:::implicit

F -->|Yes| I[PIMPLE]:::implicit
F -->|No| G

C --> J{Converged?}:::context
G --> K{Converged?}:::context
I --> L{Converged?}:::context

J -->|No| M[Relaxation]:::explicit
K -->|No| N[Reduce dt]:::explicit
L -->|No| O[Outer Corr]:::explicit

M --> J
N --> K
O --> L

J -->|Yes| P[Success]:::implicit
K -->|Yes| P
L -->|Yes| P

<<<< END >>>>

<<<< ID: DIA_d8b127a7 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Guess p*, u*]:::context --> B[Predictor]:::implicit
B --> C[P-Correction]:::explicit
C --> D[U-Correction]:::implicit
D --> E[P-Update]:::implicit
E --> F[Relaxation]:::explicit
F --> G{Converged?}:::context
G -->|No| A
G -->|Yes| H[End]:::context

<<<< END >>>>

<<<< ID: DIA_f855df6e >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Collocated Grid]:::context --> B[Linear Interp]:::implicit
B --> C[Checkerboard P]:::explicit
C --> D[Oscillations]:::explicit

E[Rhie-Chow]:::implicit --> F[Coupling]:::implicit
F --> G[Smooth P]:::implicit
G --> H[Physical]:::implicit

<<<< END >>>>

<<<< ID: DIA_ec786f6e >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph fvMesh [fvMesh: FVM Layer]
    FV1[Discretization]:::implicit
    FV2[Field Storage]:::implicit
    FV3[Solver API]:::implicit
end

subgraph polyMesh [polyMesh: Topology Layer]
    PM1[Polygonal Topology]:::explicit
    PM2[Boundary Patches]:::explicit
    PM3[Parallel Support]:::explicit
end

subgraph primitiveMesh [primitiveMesh: Geometry Layer]
    PR1[Calculations]:::implicit
    PR2[Quality Metrics]:::implicit
    PR3[On-demand]:::implicit
end

fvMesh --> polyMesh
polyMesh --> primitiveMesh

<<<< END >>>>

<<<< ID: DIA_28986662 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
M[fvMesh / objectRegistry]:::implicit --> P[volScalarField: p]:::explicit
M --> U[volVectorField: U]:::explicit
M --> T[volScalarField: T]:::explicit

<<<< END >>>>

<<<< ID: DIA_878891df >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[fvMesh<br/>Finite Volume]:::implicit --> B[polyMesh<br/>Topology]:::explicit
B --> C[primitiveMesh<br/>Geometry Engine]:::context

<<<< END >>>>

<<<< ID: DIA_19d1affe >>>>
sequenceDiagram
participant S as Solver
participant M as primitiveMesh (Cache)
participant C as Geometry Calculator
S->>M: request mesh.V()
alt Data in Cache
    M-->>S: Return cached volumes
else Cache Empty
    M->>C: trigger calcCellVolumes()
    C-->>M: return calculated data
    M->>M: store in Cache
    M-->>S: Return volumes
end

<<<< END >>>>

<<<< ID: DIA_dead754d >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
C1[Cell 1]:::implicit -->|"face<br/>(owner: 1, neigh: 2)"| C2[Cell 2]:::implicit
C2 -->|"boundary face<br/>(owner: 2)"| B[Boundary Patch]:::explicit

<<<< END >>>>

<<<< ID: DIA_3b3bb85b >>>>
classDiagram
class primitiveMesh {
<<Abstract>>
+cellCentres()
+cellVolumes()
+faceAreas()
#calcGeometry()
}
class polyMesh {
+points()
+faces()
+owner()
+neighbour()
+boundaryMesh()
}
class fvMesh {
+C()
+V()
+Sf()
+phi()
+schemes()
}
polyMesh --|> primitiveMesh : inherits
fvMesh --|> polyMesh : inherits

<<<< END >>>>

<<<< ID: DIA_2aca4674 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Start]:::context --> B[Get Ref cellCentres]:::implicit
B --> C[Geometry Cached]:::implicit
C --> D[Mesh Changes]:::explicit
D --> E[clearGeom Called]:::explicit
E --> F[Cache Cleared]:::explicit
F --> G[Ref Invalidated]:::explicit
G --> H[Undefined Behavior]:::explicit

<<<< END >>>>

<<<< ID: DIA_d3cf386c >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
P[Owner Cell]:::implicit -->|Normal| F[Face]:::explicit
F -->|Normal| N[Neighbor Cell]:::implicit
N -.->|Negative Flux| F

<<<< END >>>>

<<<< ID: DIA_7e9a62ea >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Create Ref]:::explicit --> B[Process Now]:::implicit
B --> C[Clean Up]:::implicit
C --> D{Repeat?}:::context
D -->|Yes| A
D -->|No| E[Done]:::context

<<<< END >>>>

<<<< ID: DIA_dca47e0d >>>>
mindmap
root((OpenFOAM Mesh))
Architecture
primitiveMesh
Geometry/Lazy Eval
polyMesh
Topology/Connectivity
fvMesh
CFD Fields/Registry
Key Concepts
Lazy Evaluation
Owner-Neighbour
Object Registry
Best Practices
Use References
Avoid unnecessary edits
Check Mesh Quality

<<<< END >>>>

<<<< ID: DIA_51291e57 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
subgraph Layer3 [Layer 3: Finite Volume]
    FVM[fvMesh<br/>Discretization & Fields]:::implicit
end

subgraph Layer2 [Layer 2: Topology]
    PM[polyMesh<br/>Connectivity & Parallel]:::explicit
end

subgraph Layer1 [Layer 1: Geometry]
    PSM[primitiveMesh<br/>Math & Metrics]:::implicit
end

FVM --> PM
PM --> PSM

<<<< END >>>>

<<<< ID: DIA_a5338787 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[List Type]:::implicit --> B[Field Type]:::implicit
B --> C[DimensionedField]:::implicit
C --> D[GeometricField]:::explicit
C --> E[regIOobject]:::implicit
D --> F[GeometricBoundaryField]:::explicit
F --> G[FieldField PatchField]:::explicit

H[volScalarField]:::explicit -.->|typedef| D
I[volVectorField]:::explicit -.->|typedef| D
J[volTensorField]:::explicit -.->|typedef| D
K[surfaceScalarField]:::explicit -.->|typedef| D

<<<< END >>>>

<<<< ID: DIA_9cee6661 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph GF [GeometricField]
    direction LR
    subgraph IF [Internal Field]
        direction TB
        IF1[Cell 0]:::implicit
        IF2[Cell 1]:::implicit
        IF3[...]:::implicit
        IF4[Cell N-1]:::implicit
    end

    subgraph BF [Boundary Field]
        direction TB
        BF1[Patch 0]:::explicit
        BF2[Patch 1]:::explicit
        BF3[...]:::explicit
    end
end

<<<< END >>>>

<<<< ID: DIA_a477d031 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
Mesh[Computational Mesh]:::implicit
Mesh --> C[Cell Centers<br/>volField]:::implicit
Mesh --> F[Face Centers<br/>surfaceField]:::explicit
Mesh --> P[Points<br/>pointField]:::implicit

<<<< END >>>>

<<<< ID: DIA_1b3d4f86 >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
GF[GeometricField]:::explicit --> DF[DimensionedField: Internal]:::implicit
GF --> BF[BoundaryField]:::explicit

<<<< END >>>>

<<<< ID: DIA_b6669044 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
P1((Point 1)):::implicit --> C1[Cell A]:::implicit
P1 --> C2[Cell B]:::implicit
P2((Point 2)):::implicit --> C1
P2 --> C3[Cell C]:::implicit
P3((Point 3)):::implicit --> C2
P3 --> C4[Cell D]:::implicit

CC1((Cell Center A)):::explicit -.-> P1
CC1 -.-> P2
CC2((Cell Center B)):::explicit -.-> P1
CC2 -.-> P3

<<<< END >>>>

<<<< ID: DIA_91ee03f1 >>>>
mindmap
root((Field Types))
volField
Cell Centers
State Vars p/U/T
Internal + Boundary
surfaceField
Face Centers
Flux phi
Interpolation
pointField
Vertices
Mesh Motion
Vis
DimensionedField
Internal Only
No Boundaries
Memory Efficient

<<<< END >>>>

<<<< ID: DIA_236ed73a >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Input A]:::implicit
B[Input B]:::implicit

A -- "Multiplication" --> C[Result Sum Dims]:::implicit
B -- "Multiplication" --> C

A -- "Addition" --> D{Compare Dims}:::context
B -- "Addition" --> D

D -- "Match" --> E[Result Dims]:::implicit
D -- "Mismatch" --> F[FATAL ERROR]:::explicit

<<<< END >>>>

<<<< ID: DIA_85970482 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Excel Spreadsheet]:::explicit --> B[Manual Ops]:::explicit
A --> C[No Unit Check]:::explicit
A --> D[Sequential]:::explicit

E[OpenFOAM Field]:::implicit --> F[Auto Ops]:::implicit
E --> G[Dimension Check]:::implicit
E --> H[Parallel Vectorized]:::implicit

<<<< END >>>>

<<<< ID: DIA_e9643fa0 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[volScalarField p]:::implicit --> B[Internal Field]:::implicit
A --> C[Boundary Field]:::explicit
A --> D[dimensionSet]:::implicit
A --> E[Mesh Ref]:::implicit
A --> F[IOobject]:::implicit

B --> B1[Cell Values]:::implicit
B --> B2[Contiguous Mem]:::implicit

C --> C1[Patch Values]:::explicit
C --> C2[Boundary Conds]:::explicit

<<<< END >>>>

<<<< ID: DIA_5d7db196 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[GeometricField]:::implicit --> B[DimensionedField]:::implicit
B --> C[Field]:::implicit
C --> D[List]:::implicit
B --> E[regIOobject]:::implicit

A --> F[BoundaryField]:::explicit
F --> G[FieldField]:::explicit

H[volScalarField]:::explicit --> A
I[volVectorField]:::explicit --> A
J[volTensorField]:::explicit --> A
K[surfaceScalarField]:::explicit --> A

<<<< END >>>>

<<<< ID: DIA_712e9b0a >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[PatchField Parameter]:::implicit --> B[Policy Selection]:::implicit
B --> C[Compile Poly]:::implicit
B --> D[Type Safety]:::explicit
B --> E[Optimization]:::implicit

<<<< END >>>>

<<<< ID: DIA_4af7d226 >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
C1((Cell 1)):::implicit -- "U1" --> F[Face: Interpolation]:::explicit
C2((Cell 2)):::implicit -- "U2" --> F
F -- "Result" --> Uf[surfaceField: Uf]:::implicit

<<<< END >>>>

<<<< ID: DIA_2c03356a >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
W[Call runTime.write]:::explicit --> C{Check Interval}:::context
C -- "No" --> End[Continue]:::context
C -- "Yes" --> Scan[Scan Registry]:::implicit
Scan --> Loop[For each Object]:::implicit
Loop --> Write[obj.write]:::explicit
Write --> Done[Data Saved]:::implicit

<<<< END >>>>

<<<< ID: DIA_e1ba5e9a >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
subgraph Patterns [Design Patterns]
    T[Time: Controller]:::explicit --> R[Registry: Mediator]:::implicit
    R --> D[Data Objects: Observers]:::implicit
    D -- "Report Status" --> R
end

<<<< END >>>>

<<<< ID: DIA_87aae412 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph National [HQ: Time/runTime]
    T[Time Controller]:::explicit
    T --> |broadcasts| DT[Signals]:::explicit
end

subgraph Regional [Regional: objectRegistry]
    OR[Object Registry]:::implicit
    OR --> REG1[Region 1 Data]:::implicit
    OR --> REG2[Region 2 Data]:::implicit
end

subgraph Local [Local: GeometricField]
    FS1[Station 1]:::implicit
    FS2[Station 2]:::implicit
end

DT --> OR
REG1 --> FS1
REG2 --> FS2
FS1 --> OR
FS2 --> OR

<<<< END >>>>

<<<< ID: DIA_7a8b4a6d >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph BC [Boundary Conditions]
    BC1[Inlet]:::explicit
    BC2[Outlet]:::explicit
    BC3[Walls]:::explicit
end

subgraph IF [Internal Field]
    Val[Field Values]:::implicit
end

BC1 --> |Fixed| Val
BC2 --> |Gradient| Val
BC3 --> |Adiabatic| Val

<<<< END >>>>

<<<< ID: DIA_2e6a6dec >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph L1 [Level 1: Local]
    A1[Cell Values]:::implicit
end

subgraph L2 [Level 2: Regional]
    B1[BC Updates]:::explicit
    B2[Patch Calc]:::explicit
end

subgraph L3 [Level 3: National]
    C1[Field Ops]:::implicit
    C2[Solver Int]:::implicit
    C3[Reductions]:::implicit
end

A1 --> B1
A1 --> B2
B1 --> C1
B2 --> C1
C1 --> C2
C1 --> C3

<<<< END >>>>

<<<< ID: DIA_a1f8f0ac >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
Start([Start]):::context --> Loop{Running?}:::context
Loop -- Yes --> Increment[runTime++]:::implicit
Increment --> Physics[Solve Physics]:::explicit
Physics --> Write{Write?}:::context
Write -- Yes --> Disk[Save Data]:::implicit
Write -- No --> Loop
Disk --> Loop
Loop -- No --> End([End]):::context

<<<< END >>>>

<<<< ID: DIA_19242597 >>>>
mindmap
root((Geometric Fields))
Template Architecture
Type: scalar/vector
PatchField: fv/point
GeoMesh: vol/surface
Inheritance
Field
DimensionedField
GeometricField
volScalarField
Patterns
Template Metaprog
RAII
Policy-Based
Performance
Expression Templates
Cache Efficiency

<<<< END >>>>

<<<< ID: DIA_1ec48ee8 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[GeometricField Template]:::implicit --> B[Type Param]:::implicit
A --> C[PatchField Param]:::implicit
A --> D[GeoMesh Param]:::implicit

B --> B1[scalar/vector/tensor]:::explicit
C --> C1[fv/point/surface Patch]:::explicit
D --> D1[vol/surface/point Mesh]:::explicit

<<<< END >>>>

<<<< ID: DIA_d7c6d4da >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Field: Raw Data]:::implicit --> B[DimensionedField: Units]:::implicit
B --> C[GeometricField: BCs]:::implicit
C --> D[volScalarField]:::explicit
C --> E[volVectorField]:::explicit
C --> F[surfaceScalarField]:::explicit

<<<< END >>>>

<<<< ID: DIA_b67efe05 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[fieldA]:::implicit --> C[+ Operator]:::explicit
B[fieldB * 2.0]:::implicit --> C
C --> D[No Temp Alloc]:::implicit
D --> E[Direct Assign]:::explicit

<<<< END >>>>

<<<< ID: DIA_3ad73976 >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
Time[Time Registry]:::explicit --> Mesh[fvMesh Registry]:::implicit
Mesh --> p[p: volScalarField]:::implicit
Mesh --> U[U: volVectorField]:::implicit
Mesh --> T[T: volScalarField]:::implicit

<<<< END >>>>

<<<< ID: DIA_b375b58a >>>>
classDiagram
class IOobject {
+name()
+path()
+readOpt()
+writeOpt()
}
class regIOobject {
+checkOut()
+checkIn()
+write()
}
class volScalarField {
+internalField()
+boundaryField()
}
regIOobject --|> IOobject : inherits
volScalarField --|> regIOobject : inherits

<<<< END >>>>

<<<< ID: DIA_0204ba6a >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Field: Raw]:::implicit --> B[DimensionedField: Units]:::implicit
B --> C[GeometricField: Complete]:::implicit
C --> D[volScalarField]:::explicit
C --> E[volVectorField]:::explicit
C --> F[surfaceScalarField]:::explicit

<<<< END >>>>

<<<< ID: DIA_efa98a43 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Field Ops]:::explicit --> B{Type Check}:::implicit
B --> C[Rank Check]:::implicit
B --> D[Dim Analysis]:::implicit
B --> E[Topology Check]:::implicit
C --> F[Safety]:::explicit
D --> F
E --> F
F --> G[Valid Code]:::explicit

<<<< END >>>>

<<<< ID: DIA_afb32d3f >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[List]:::implicit --> B[Field]:::implicit
B --> C[DimensionedField]:::implicit
C --> D[GeometricField]:::implicit
D --> E1[volScalarField]:::explicit
D --> E2[volVectorField]:::explicit
D --> E3[surfaceScalarField]:::explicit

<<<< END >>>>

<<<< ID: DIA_a3a36655 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Current phi]:::explicit --> B[phi.oldTime]:::implicit
B --> C[phi.oldOldTime]:::implicit
A --> E[Iter History]:::implicit
E --> F[phi.prevIter]:::implicit

<<<< END >>>>

<<<< ID: DIA_c93a1d9f >>>>
graph TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph Trad [Traditional: Memory Heavy]
    T1[Temp1 = a + b]:::explicit --> T2[Result = Temp1 + c]:::explicit
end

subgraph OF [OpenFOAM: Loop Fusion]
    E[Expr Tree: a+b+c]:::implicit --> L[Single Loop]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_5a06e22b >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[OpenFOAM Fields]:::implicit --> B[Math Base]:::implicit
A --> C[Architecture]:::implicit
A --> D[Memory Mgmt]:::implicit
A --> E[Safety]:::implicit

B --> B1[Tensors]:::explicit
B --> B2[Conservation]:::explicit
B --> B3[Dim Analysis]:::explicit

C --> C1[Inheritance]:::explicit
C --> C2[Templates]:::explicit

D --> D1[Ref Counting]:::explicit
D --> D2[Lazy Eval]:::explicit

E --> E1[Type Check]:::explicit
E --> E2[Dim Check]:::explicit

<<<< END >>>>

<<<< ID: DIA_5e58b2fc >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[List]:::implicit --> B[Field]:::implicit
B --> C[DimensionedField]:::implicit
C --> D[GeometricField]:::implicit
D --> E1[volScalarField]:::explicit

A -.->|Raw| A1[Memory]:::context
B -.->|Math| B1[Refs]:::context
C -.->|Units| C1[Analysis]:::context
D -.->|Space| D1[BCs]:::context

<<<< END >>>>

<<<< ID: DIA_52c09fd0 >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Design]:::implicit --> B[Ref Counting]:::explicit
A --> C[Expr Templates]:::explicit
A --> D[Lazy Eval]:::explicit

B --> E[Efficiency]:::implicit
C --> F[Fusion]:::implicit
D --> G[Cache Opt]:::implicit

E --> H[Large Scale CFD]:::explicit
F --> H
G --> H

<<<< END >>>>

<<<< ID: DIA_bd1465c9 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
UList[UList]:::implicit
List[List]:::implicit
Field[Field]:::implicit
regIO[regIOobject]:::implicit
Dim[DimensionedField]:::implicit
Geo[GeometricField]:::implicit

vS[volScalarField]:::explicit
vV[volVectorField]:::explicit
sS[surfaceScalarField]:::explicit

UList --> List --> Field --> regIO --> Dim --> Geo
Geo --> vS
Geo --> vV
Geo --> sS

<<<< END >>>>

<<<< ID: DIA_a22b4753 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[p = p_rgh + rho * gh]:::implicit
B[AddOp]:::explicit
C[p_rgh]:::implicit
D[MulOp]:::explicit
E[rho]:::implicit
F[gh]:::implicit

A --> B
B --> C
B --> D
D --> E
D --> F

<<<< END >>>>

<<<< ID: DIA_0abbdfc9 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[UList: STL]:::implicit --> B[List: Managed]:::implicit
B --> C[Field: Math]:::implicit
C --> D[DimensionedField: Units]:::implicit
D --> E[GeometricField: BCs]:::implicit
E --> F1[volScalarField]:::explicit
E --> F2[volVectorField]:::explicit
E --> F3[surfaceScalarField]:::explicit

<<<< END >>>>

<<<< ID: DIA_d5dbf28b >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Global Domain]:::implicit --> B[Proc 0]:::explicit
A --> C[Proc 1]:::explicit
A --> D[Proc N]:::explicit

B <--> E[MPI Comm]:::implicit
C <--> E
D <--> E

<<<< END >>>>

<<<< ID: DIA_7e485ff3 >>>>
stateDiagram-v2
[] --> IOobject: Set Name/Path
IOobject --> Allocation: MUST_READ
Allocation --> Parsing: Read Dims/Vals
Parsing --> BCSetup: Init Patches
BCSetup --> Registered: Add to Registry
Registered --> []

<<<< END >>>>

<<<< ID: DIA_6cb3cf70 >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[New]:::implicit --> B[Read]:::implicit
B --> C[Solve]:::explicit
C --> D[Store Old]:::implicit
D --> C
C --> E[Destruct]:::explicit

<<<< END >>>>

<<<< ID: DIA_bfe44922 >>>>
mindmap
root((Geometric Fields))
Components
Internal Field
Boundary Field
Dimensions
Inheritance
UList > List
Field > regIOobject
GeometricField
Logic
Lazy Old-Time
Expression Templates
Loop Fusion
Safety
Compile-time Units
Tensor Check
Manifold Awareness

<<<< END >>>>

<<<< ID: DIA_1e4cb94a >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Overview]:::implicit --> B[Philosophy]:::implicit
B --> C[Hierarchy]:::implicit
C --> D[Lifecycle]:::implicit
D --> E[Type Safety]:::implicit
E --> F[Pitfalls]:::explicit
F --> G[Summary]:::implicit

<<<< END >>>>

<<<< ID: DIA_f444070d >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
Real[Real Data: P, U, L]:::implicit -- "Normalize" --> Norm[Norm Data: p*, U*]:::implicit
Norm -- "Grouping" --> DimLess[Dimensionless: Re, Fr]:::explicit

<<<< END >>>>

<<<< ID: DIA_a268d4c0 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Prototype]:::implicit --> B[Define Params]:::implicit
B --> C[Build Scale Model]:::explicit
C --> D[Wind Tunnel]:::explicit
D --> E[Extract Coeffs]:::implicit
E --> F[Scale Back]:::implicit

<<<< END >>>>

<<<< ID: DIA_c6a509d1 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Ref Quantities]:::implicit --> B[Calc DimLess Groups]:::implicit
B --> C[Create Fields]:::explicit
C --> D[Formulate Eqns]:::explicit
D --> E[Verify Consist]:::implicit
E --> F[Solve]:::explicit

<<<< END >>>>

<<<< ID: DIA_65c6f66f >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
C[Convection]:::implicit -- "Check" --> Match{Consistent?}:::context
D[Diffusion]:::implicit -- "Check" --> Match
S[Source]:::implicit -- "Check" --> Match

Match -- "OK" --> Run[Start]:::implicit
Match -- "Fail" --> Error[Fatal Error]:::explicit

<<<< END >>>>

<<<< ID: DIA_fca72881 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
Fluid[Fluid Solver P]:::implicit -->|Transfer Force| Sync{Sync?}:::context
Solid[Solid Solver Stress]:::implicit -->|Check Bnd| Sync
Sync -->|Valid| Move[Deform Mesh]:::explicit

<<<< END >>>>

<<<< ID: DIA_2fdffc17 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Formulation]:::context --> B[Analysis]:::implicit
B --> C{Consistent?}:::context
C -->|No| D[Revise]:::explicit
D --> B
C -->|Yes| E[Implement]:::explicit
E --> F[Compile Check]:::implicit
F --> G{Success?}:::context
G -->|No| H[Fix]:::explicit
H --> E
G -->|Yes| I[Run]:::implicit
I --> J[Validate]:::implicit

<<<< END >>>>

<<<< ID: DIA_c29c6069 >>>>
classDiagram
class dimensionSet {
-scalar exponents_[7]
+operator+()
+operator*()
+dimensionless() bool
+matches() bool
}
class dimensionedScalar {
    +word name_
    +dimensionSet dimensions_
    +scalar value_
}

dimensionSet --> dimensionedScalar

<<<< END >>>>

<<<< ID: DIA_93dcb24f >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Construction]:::implicit --> B[Compile Check]:::implicit
B --> C[Math Ops]:::explicit
C --> D[Runtime Check]:::implicit
D --> E[Field Merge]:::implicit

<<<< END >>>>

<<<< ID: DIA_ced6d730 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Error Start]:::explicit --> B[Read Msg]:::context
B --> C[ID Dimensions]:::implicit
C --> D[Convert Symbols]:::implicit
D --> E[Find Fail Op]:::explicit
E --> F{Check Physics}:::context
F -->|OK| G[Fix Code]:::explicit
F -->|Bad| H[Review Eqn]:::explicit
G --> I[Retest]:::implicit
H --> I
I --> J[Fixed]:::implicit

<<<< END >>>>

<<<< ID: DIA_b1717b97 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
A[Operation]:::context --> B{Compatible?}:::context
B -->|Match| C[Create Result]:::implicit
B -->|Mismatch| D[Error]:::explicit
C --> E[Compute]:::implicit
E --> F[Return]:::implicit

<<<< END >>>>

<<<< ID: DIA_9778e863 >>>>
mindmap
root((Dimensional Analysis))
dimensionSet
SI Units
Exponents
isDimensionless
Arithmetic
Add/Sub
Mul/Div
Pow/Sqrt
Non-Dimensionalization
Ref Scales
Similarity
Stability
Advanced
Coupling
Custom Units
Safety Net

<<<< END >>>>

<<<< ID: DIA_95f31bee >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Overview]:::context --> B[Safety Net]:::implicit
B --> C[The Blueprint]:::implicit
C --> D[Mechanics]:::implicit
D --> E[Arithmetic]:::explicit
E --> F[Consistency]:::implicit
F --> G[Non-Dim Tech]:::implicit
G --> H[Examples]:::explicit
H --> I[Advanced]:::implicit
I --> J[Summary]:::implicit
J --> K[Exercises]:::explicit

<<<< END >>>>

<<<< ID: DIA_14e4cbe8 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[lduMatrix: Sparse]:::implicit --> B[fvMatrix: FVM]:::implicit
C[GeometricField]:::explicit --> B
D[dimensionSet]:::implicit --> B
E[BCs]:::explicit --> B

B --> F[Fields]:::implicit
B --> G[Assembly]:::explicit
B --> H[Solver Ops]:::explicit

<<<< END >>>>

<<<< ID: DIA_5e26312d >>>>
flowchart LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[fvm::ddt]:::explicit --> D[Diagonal + Source]:::implicit
B[fvm::div]:::explicit --> U[Upper + Lower]:::implicit
C[fvm::laplacian]:::explicit --> All[Diag + Up + Low]:::implicit

subgraph LDU [fvMatrix LDU]
    D
    U
    All
end

<<<< END >>>>

<<<< ID: DIA_1ea9fa05 >>>>
graph LR
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
M[Matrix A]:::implicit --> D[Diagonal]:::explicit
M --> L[Lower]:::explicit
M --> U[Upper]:::explicit

<<<< END >>>>

<<<< ID: DIA_25f44544 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
A[Matrix Types]:::implicit --> B[Dense]:::implicit
A --> C[Sparse ldu]:::implicit
A --> D[fvMatrix]:::explicit

B --> E[Direct Solvers]:::implicit
C --> F[Iterative Solvers]:::implicit
D --> G[FVM BCs]:::implicit

F --> H[Krylov: PCG/PBiCG]:::explicit
F --> I[Multigrid: GAMG]:::explicit

<<<< END >>>>

<<<< ID: DIA_58b17905 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Nodes
F1[Fine: Smooth]:::implicit --> C[Coarse: Aggr]:::implicit
C --> CC[Coarsest: Solve]:::explicit
CC --> C2[Coarse: Correct]:::implicit
C2 --> F2[Fine: Smooth]:::implicit

subgraph Cycle [V-Cycle]
    F1
    C
    CC
    C2
    F2
end

<<<< END >>>>

<<<< ID: DIA_f9e1953f >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
classDef context fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575;
%% Nodes
Start[Start]:::context --> Q1{Size?}:::context

Q1 -->|Small| Small[PCG/PBiCG]:::implicit
Q1 -->|Large| Q2{Matrix Type?}:::context

Q2 -->|Symm| Sym[GAMG]:::explicit
Q2 -->|Asymm| NonSym[PBiCGStab + DILU]:::explicit

Small --> Check[Check Conv]:::implicit
Sym --> Check
NonSym --> Check

Check -->|Fail| Fix[Change Precond]:::explicit
Check -->|Pass| Done[Done]:::implicit

Fix --> Check

<<<< END >>>>

<<<< ID: DIA_d30ad778 >>>>
flowchart TD
%% Classes
classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
%% Subgraphs
subgraph Serial [Serial]
    A[Single Proc]:::implicit --> B[Process All]:::implicit
    B --> C[Solution]:::implicit
end

subgraph Parallel [Parallel]
    D[Decomp]:::explicit --> E1[Proc 1]:::implicit
    D --> E2[Proc 2]:::implicit
    E1 <--> F[Halo Exch]:::explicit
    E2 <--> F
    F --> G[Global Sol]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_49d8f7fd >>>>
flowchart TB
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000
subgraph Domain ["Parallel Domain Decomposition"]
    direction LR
    subgraph P1 ["Processor 1"]
        O1[Owned Cells<br/>(Internal)]:::implicit <-->|Coupling| G1[Ghost Cells<br/>(Halo)]:::explicit
    end

    subgraph P2 ["Processor 2"]
        G2[Ghost Cells<br/>(Halo)]:::explicit <-->|Coupling| O2[Owned Cells<br/>(Internal)]:::implicit
    end
end

G1 <==>|MPI Exchange<br/>Explicit Comm| G2
O1 -->|Discretization<br/>Implicit| O1
O2 -->|Discretization<br/>Implicit| O2

style P1 fill:#fff,stroke:#333
style P2 fill:#fff,stroke:#333

<<<< END >>>>

<<<< ID: DIA_5f532151 >>>>
flowchart TD
classDef implicit fill:#e3f2fd,stroke:#1565c0,color:#000
classDef explicit fill:#ffe0b2,stroke:#ef6c00,color:#000
classDef container fill:#f5f5f5,stroke:#333,color:#000
subgraph Hardware ["Compute Hardware"]
    P0[Proc 0]:::container
    P1[Proc 1]:::container
    P2[Proc 2]:::container
    P3[Proc 3]:::container
end

subgraph Assembly ["Matrix Assembly Pipeline"]
    Phase1[1. Internal Faces<br/>Diagonal + Off-Diagonal]:::implicit
    Phase2[2. Proc Boundaries<br/>Parallel Interfaces]:::explicit
    Phase3[3. Physical Boundaries<br/>Inlet/Outlet/Wall]:::implicit
    Phase4[4. Global Consistency<br/>Reduce Operations]:::explicit
end

P0 & P1 & P2 & P3 -->|Construct| Phase1
Phase1 --> Phase2
Phase2 --> Phase3
Phase3 --> Phase4
Phase4 --> System[Global Linear System<br/>Ax = b]:::implicit

<<<< END >>>>

<<<< ID: DIA_d570c989 >>>>
sequenceDiagram
participant P0 as Processor 0
participant P1 as Processor 1
participant P2 as Processor 2
participant P3 as Processor 3
rect rgb(255, 230, 230)
    Note over P0,P3: Phase 1: Explicit Communication (Non-Blocking)
    P0->>P1: Send Boundary
    P1->>P0: Send Boundary
    P0->>P3: Send Boundary
    P3->>P0: Send Boundary
end

rect rgb(230, 245, 255)
    Note over P0,P3: Phase 2: Implicit Computation (Hiding Latency)
    P0->>P0: Calc Interior
    P1->>P1: Calc Interior
    P2->>P2: Calc Interior
    P3->>P3: Calc Interior
end

rect rgb(255, 245, 230)
    Note over P0,P3: Phase 3: Synchronization
    P0->>P0: Wait()
    P1->>P1: Wait()
    P2->>P2: Wait()
    P3->>P3: Wait()
end

rect rgb(230, 255, 230)
    Note over P0,P3: Phase 4: Boundary Update
    P0->>P0: Update Ghost
    P1->>P1: Update Ghost
    P2->>P2: Update Ghost
    P3->>P3: Update Ghost
end

<<<< END >>>>

<<<< ID: DIA_4cba8f16 >>>>
flowchart TD
classDef serial fill:#e1bee7,stroke:#4a148c,color:#000
classDef parallel fill:#bbdefb,stroke:#0d47a1,color:#000
classDef boundary fill:#ffcdd2,stroke:#b71c1c,color:#000
subgraph Serial ["Serial Gauss-Seidel"]
    direction TB
    C1[Cell 1]:::serial --> C2[Cell 2]:::serial
    C2 --> C3[Cell 3]:::serial
    C3 --> C4[Cell 4]:::serial
end

subgraph Parallel ["Parallel Domain Decomposition"]
    direction TB
    subgraph Proc0 [Processor 0]
        P0_1[Cell 1]:::parallel --> P0_2[Cell 2]:::parallel
    end
    
    subgraph Proc1 [Processor 1]
        P1_3[Cell 3]:::parallel --> P1_4[Cell 4]:::parallel
    end

    P0_2 -.->|Boundary Lag<br/>Explicit Update| P1_3:::boundary
    P1_3 -.->|Boundary Lag<br/>Explicit Update| P0_2:::boundary
end

<<<< END >>>>

<<<< ID: DIA_641973e8 >>>>
flowchart TD
classDef matrix fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef solver fill:#ffecb3,stroke:#ff8f00,color:#000
classDef physics fill:#e1f5fe,stroke:#0277bd,color:#000
classDef root fill:#eee,stroke:#333,color:#000
Root[OpenFOAM Linear Algebra]:::root

subgraph Storage ["Matrix Storage Formats"]
    B[Dense Matrices]:::matrix
    C[Sparse LDU Matrix]:::matrix
    
    B --> B1[Square/Rectangular]:::matrix
    C --> C1[Lower-Diagonal-Upper]:::matrix
    C --> C2[Matrix-free Ops]:::matrix
end

subgraph Physics ["Physics Layer"]
    D[fvMatrix]:::physics
    D --> D1[Dimensions]:::physics
    D --> D2[Boundaries]:::physics
end

subgraph Algorithms ["Solver Algorithms"]
    E[Solver Hierarchy]:::solver
    E --> E1[Krylov: PCG/BiCG]:::solver
    E --> E2[Multigrid: GAMG]:::solver
    E --> E3[Precond: DIC/DILU]:::solver
end

Root --> B & C & D & E

<<<< END >>>>

<<<< ID: DIA_ceda6e5e >>>>
flowchart TD
classDef decision fill:#fff9c4,stroke:#fbc02d,color:#000
classDef implicit fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef explicit fill:#ffccbc,stroke:#d84315,color:#000
Start[Matrix System] --> Sym{Symmetric?}:::decision

Sym -- Yes --> SPD{Positive Definite?}:::decision
Sym -- No --> Diag{Diagonal Dominant?}:::decision

SPD -- Yes --> PCG[PCG + DIC/DILU<br/>(Pressure Poisson)]:::implicit
SPD -- No --> BiCG[BiCGStab + DILU<br/>(Momentum/Transport)]:::explicit

Diag -- Yes --> GAMG[GAMG + Smoother<br/>(Large Scale > 1M)]:::implicit
Diag -- No --> GMRES[GMRES + ILU<br/>(Ill-conditioned)]:::explicit

<<<< END >>>>

<<<< ID: DIA_f185fa31 >>>>
flowchart TD
classDef fine fill:#e3f2fd,stroke:#1565c0,color:#000
classDef medium fill:#bbdefb,stroke:#1976d2,color:#000
classDef coarse fill:#90caf9,stroke:#1e88e5,color:#000
classDef solve fill:#fff59d,stroke:#fbc02d,color:#000
subgraph Downstroke [Restriction Phase]
    L1[Fine Grid]:::fine -->|Smooth & Restrict| L2[Medium Grid]:::medium
    L2 -->|Smooth & Restrict| L3[Coarse Grid]:::coarse
end

L3 -->|Direct Solve| Base[Coarsest Solution]:::solve

subgraph Upstroke [Prolongation Phase]
    Base -->|Prolongate & Correct| R3[Coarse Grid]:::coarse
    R3 -->|Prolongate & Correct| R2[Medium Grid]:::medium
    R2 -->|Prolongate & Correct| R1[Fine Grid]:::fine
end

R1 --> Final[Final Solution]:::fine

<<<< END >>>>

<<<< ID: DIA_506351f3 >>>>
flowchart LR
classDef step fill:#f5f5f5,stroke:#333,color:#000
classDef finish fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
A[1. Matrices<br/>Overview]:::step --> B[2. Dense vs<br/>Sparse/LDU]:::step
B --> C[3. fvMatrix<br/>Architecture]:::step
C --> D[4. Linear Solvers<br/>& GAMG]:::step
D --> E[5. Parallel<br/>Algebra]:::step
E --> F[6. Common<br/>Pitfalls]:::step
F --> G[7. Summary<br/>& Exercises]:::finish

<<<< END >>>>

<<<< ID: DIA_0f9be093 >>>>
flowchart TD
classDef operator fill:#ffecb3,stroke:#ff6f00,color:#000
classDef field fill:#e1f5fe,stroke:#01579b,color:#000
Minus["operator- (Subtraction)"]:::operator
Plus["operator+ (Addition)"]:::operator

FieldD[Field d]:::field
FieldB[Field b]:::field
FieldC[Field c]:::field

Minus -->|Left Operand| Plus
Minus -->|Right Operand| FieldD
Plus -->|Left Operand| FieldB
Plus -->|Right Operand| FieldC

%% Visualizing: (b + c) - d

<<<< END >>>>

<<<< ID: DIA_4136b4c5 >>>>
flowchart LR
classDef input fill:#e1f5fe,stroke:#0288d1,color:#000
classDef op fill:#ffecb3,stroke:#f57f17,color:#000
classDef output fill:#c8e6c9,stroke:#388e3c,color:#000
subgraph Data [Input Data]
    U[Vector Field U]:::input
    V[Vector Field V]:::input
end

subgraph Operations [Algebraic Ops]
    Dot["& (Inner Product)"]:::op
    Cross["^ (Cross Product)"]:::op
    Outer["* (Outer Product)"]:::op
end

subgraph Results [Typed Output]
    S[Scalar Field]:::output
    Vec[Vector Field]:::output
    Ten[Tensor Field]:::output
end

U & V --> Dot --> S
U & V --> Cross --> Vec
U & V --> Outer --> Ten

<<<< END >>>>

<<<< ID: DIA_b88cf5f0 >>>>
flowchart LR
classDef bad fill:#ffcdd2,stroke:#c62828,color:#000
classDef good fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef result fill:#e0e0e0,stroke:#333,stroke-dasharray: 5 5,color:#000
C["C-Style: Manual Loops"]:::bad
OF["OpenFOAM: Field Algebra"]:::good
Solver[Solver Application]:::result

C -- "Hard to Read / Error Prone" --> Solver
OF -- "Clear / Type-Safe / Optimized" --> Solver

<<<< END >>>>

<<<< ID: DIA_0d178b78 >>>>
flowchart TB
classDef field fill:#e1f5fe,stroke:#0277bd,color:#000
classDef op fill:#ffecb3,stroke:#f57f17,color:#000
classDef result fill:#c8e6c9,stroke:#2e7d32,color:#000
subgraph Inputs [Field Inputs]
    A[Field A: x1, x2, ... xN]:::field
    B[Field B: y1, y2, ... yN]:::field
end

Op((+)):::op

subgraph Output [SIMD Operation]
    R[Result: x1+y1, x2+y2, ... xN+yN]:::result
end

A --> Op
B --> Op
Op --> R

<<<< END >>>>

<<<< ID: DIA_feac83e6 >>>>
flowchart LR
classDef root fill:#424242,stroke:#000,color:#fff
classDef safety fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef perf fill:#e3f2fd,stroke:#1565c0,color:#000
classDef practice fill:#fff9c4,stroke:#fbc02d,color:#000
Center((Field Algebra)):::root

subgraph Safety [Dimensional Safety]
    S1[SI Units Check]:::safety
    S2[Fatal Error Protection]:::safety
    S3[Algebraic Rules]:::safety
end

subgraph Perf [Performance]
    P1[Expression Templates]:::perf
    P2[Loop Fusion]:::perf
    P3[Zero-cost Abstraction]:::perf
end

subgraph BestPractice [Best Practices]
    B1[Use Parentheses]:::practice
    B2[Avoid Complexity]:::practice
    B3[Unit Consistency]:::practice
end

Center --- S1 & S2 & S3
Center --- P1 & P2 & P3
Center --- B1 & B2 & B3

<<<< END >>>>

<<<< ID: DIA_9d4dae49 >>>>
flowchart TD
classDef core fill:#e3f2fd,stroke:#1565c0,color:#000
classDef advanced fill:#fff3e0,stroke:#e65100,color:#000
classDef app fill:#e8f5e9,stroke:#2e7d32,color:#000
A[Field Algebra Overview]:::core --> B[Arithmetic Operations]:::core
B --> C[Operator Overloading]:::core
C --> D[Dimensional Checking]:::core
D --> E[Expression Templates]:::advanced
E --> F[Field Composition]:::advanced
F --> G[Performance Optimization]:::advanced
G --> H[Practical Applications]:::app

<<<< END >>>>

<<<< ID: DIA_5aad7eac >>>>
flowchart TD
classDef memory fill:#e3f2fd,stroke:#1565c0,color:#000
classDef container fill:#e8f5e9,stroke:#2e7d32,color:#000
classDef app fill:#fff9c4,stroke:#fbc02d,color:#000
subgraph L3 [Application Layer]
    I[Parallel Processing]:::app
    H[Field Algebra]:::app
    G[Solver Operations]:::app
end

subgraph L2 [Container Layer]
    F[DynamicList T]:::container
    E[Field T]:::container
    D[List T]:::container
end

subgraph L1 [Memory Management Layer]
    C[RAII Pattern]:::memory
    B[Smart Pointers]:::memory
    A[Reference Counting]:::memory
end

A --> D --> G
B --> E --> H
C --> F --> I

<<<< END >>>>

<<<< ID: DIA_d86a15e2 >>>>
pie title "Memory Distribution (Total: ~110MB)"
"Field Variables (50%)" : 56
"Solver Temporary (15%)" : 17
"Mesh Topology (10%)" : 11
"Boundary Data (10%)" : 11
"OS Overhead (10%)" : 11
"Peak Temporary (5%)" : 6

<<<< END >>>>

<<<< ID: DIA_1fc0aec7 >>>>
flowchart LR
classDef bad fill:#ffcdd2,stroke:#c62828,color:#000
classDef good fill:#c8e6c9,stroke:#2e7d32,color:#000
subgraph Generic ["Generic C++ (std::vector)"]
    A1[Vector]:::bad --> B1[Scattered RAM]:::bad
    B1 --> C1[Cache Misses]:::bad
    C1 --> D1[Slow Performance]:::bad
end

subgraph OF ["OpenFOAM (List)"]
    A2[List Field]:::good --> B2[Contiguous RAM]:::good
    B2 --> C2[SIMD Ready]:::good
    C2 --> D2[High-Speed CFD]:::good
end

<<<< END >>>>

<<<< ID: DIA_fc55dfde >>>>
flowchart TD
classDef intro fill:#e1f5fe,stroke:#0277bd,color:#000
classDef part fill:#f5f5f5,stroke:#616161,color:#000
classDef summary fill:#e8f5e9,stroke:#2e7d32,color:#000
A[บทนำ: Introduction]:::intro

subgraph Content [Course Content]
    B[ส่วนที่ 1: Memory Management]:::part
    C[ส่วนที่ 2: Container System]:::part
    D[ส่วนที่ 3: Integration]:::part
end

E[บทสรุป: Summary]:::summary

A --> B --> C --> D --> E

<<<< END >>>>

<<<< ID: DIA_1e7256c3 >>>>
flowchart TD
classDef memory fill:#e3f2fd,stroke:#1565c0,color:#000
classDef container fill:#fff3e0,stroke:#e65100,color:#000
classDef algo fill:#f3e5f5,stroke:#7b1fa2,color:#000
subgraph Mem [Memory Management]
    MP1[autoPtr: Exclusive]:::memory
    MP2[tmp: Ref Count]:::memory
    MP3[RAII: Auto Clean]:::memory
end

subgraph Cont [Containers]
    C1[List: Contiguous]:::container
    C2[DynamicList: Resizable]:::container
    C3[FixedList: Stack]:::container
    C4[PtrList: Polymorphic]:::container
end

subgraph Alg [CFD Algorithms]
    A1[Field Ops]:::algo
    A2[Linear Solver]:::algo
    A3[Boundary Conditions]:::algo
end

MP1 -.->|Manages| C4
MP2 -.->|Optimizes| Alg
MP3 -.->|Protects| Cont
C1 -->|Data for| A1
C4 -->|Data for| A3

<<<< END >>>>

<<<< ID: DIA_1f5c888b >>>>
flowchart TD
classDef perf fill:#4caf50,stroke:#1b5e20,color:#fff
classDef safe fill:#2196f3,stroke:#0d47a1,color:#fff
classDef use fill:#ff9800,stroke:#e65100,color:#fff
P[Performance]:::perf <--> S[Safety]:::safe
S <--> U[Usability]:::use
U <--> P

<<<< END >>>>

<<<< ID: DIA_1ec73a0f >>>>
flowchart LR
classDef integrated fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef modular fill:#e0e0e0,stroke:#616161,color:#000
classDef result fill:#ffecb3,stroke:#ff8f00,color:#000
subgraph Int [Integrated Approach]
    I1[Memory]:::integrated --- I2[Containers]:::integrated
    I2 --- I3[Algorithms]:::integrated
    I3 --- I1
end

subgraph Mod [Modular Approach]
    M1[Memory]:::modular -.- M2[Containers]:::modular
    M2 -.- M3[Algorithms]:::modular
end

Int -->|Optimization| R1[2-5x Faster]:::result
Mod -->|Standard| R2[Baseline]:::result

<<<< END >>>>

<<<< ID: DIA_bfdccfb1 >>>>
flowchart TD
classDef category fill:#cfd8dc,stroke:#455a64,color:#000
classDef item fill:#fff,stroke:#333,color:#000
Root[Container Taxonomy]:::category

subgraph Seq [Sequential]
    S1[UList: Basic View]:::item
    S2[List: Owner]:::item
    S3[FixedList: Compile-Time]:::item
    S4[DynamicList: Resizable]:::item
end

subgraph Map [Key-Value]
    M1[HashTable: Generic Key]:::item
    M2[Dictionary: String Key]:::item
end

subgraph Link [Linked]
    L1[SLList: Singly Linked]:::item
    L2[DLList: Doubly Linked]:::item
end

subgraph Ptr [Pointer]
    P1[PtrList: Owned Ptrs]:::item
    P2[UPtrList: View Ptrs]:::item
end

Root --> Seq & Map & Link & Ptr

<<<< END >>>>

<<<< ID: DIA_421c070b >>>>
flowchart TD
classDef role fill:#e1bee7,stroke:#4a148c,color:#000
classDef action fill:#fff9c4,stroke:#fbc02d,color:#000
classDef component fill:#e1f5fe,stroke:#0277bd,color:#000
Conductor[Conductor: Memory Mgmt]:::role -->|Coordinates| Musicians[Musicians: Containers]:::role
Musicians -->|Perform| Score[Score: CFD Algo]:::role

Conductor -.->|Uses| RAII[RAII / autoPtr / tmp]:::component
Musicians -.->|Uses| Lists[List / PtrList]:::component
Score -.->|Defines| NSE[Navier-Stokes Eq]:::component

RAII & Lists & NSE -->|Result| Harmony[High Performance]:::action

<<<< END >>>>

<<<< ID: DIA_4f8b985b >>>>
flowchart TB
classDef mem fill:#e1f5fe,stroke:#1565c0,color:#000
classDef con fill:#fff3e0,stroke:#e65100,color:#000
classDef alg fill:#e8f5e9,stroke:#2e7d32,color:#000
subgraph Memory [Memory Management]
    M1[autoPtr]:::mem
    M2[tmp]:::mem
    M3[refCount]:::mem
    M4[RAII]:::mem
end

subgraph Container [Containers]
    C1[List T]:::con
    C2[DynamicList T]:::con
    C3[FixedList T,N]:::con
    C4[PtrList T]:::con
end

subgraph Algorithm [CFD Algorithms]
    A1[fvc / fvm Ops]:::alg
    A2[LduMatrix]:::alg
    A3[Time Integration]:::alg
end

M1 <-->|Exclusive| C1
M2 <-->|Shared Ref| C2
M3 <-->|Ownership| C4
M4 <-->|Safety| A1
C1 <-->|SIMD Layout| A2
C2 <-->|Memory Align| A3

<<<< END >>>>

<<<< ID: DIA_4d2c1145 >>>>
flowchart TD
classDef normal fill:#e8f5e9,stroke:#2e7d32,color:#000
classDef error fill:#ffcdd2,stroke:#c62828,color:#000
classDef cleanup fill:#e1f5fe,stroke:#1565c0,color:#000
Start(Function Start) --> Alloc[RAII Allocation: Mesh, P, U]:::normal
Alloc --> Ops[CFD Operations]:::normal
Ops --> Check{Error?}

Check -- No --> Continue[Continue Execution]:::normal
Check -- Yes --> Unwind[Stack Unwinding]:::error

Unwind --> D1[~Boundaries: Delete All]:::cleanup
D1 --> D2[~U: Decr Ref / Delete]:::cleanup
D2 --> D3[~p: Decr Ref / Delete]:::cleanup
D3 --> D4[~Mesh: Delete]:::cleanup

D4 --> Safe[Resources Cleaned]:::normal

<<<< END >>>>

<<<< ID: DIA_0bfc96d5 >>>>
flowchart LR
classDef step fill:#fff9c4,stroke:#fbc02d,color:#000
classDef auto fill:#c8e6c9,stroke:#2e7d32,color:#000
A[Check-In<br/>Constructor]:::step --> B[Stay<br/>Usage]:::step
B --> C[Check-Out<br/>Destructor]:::step
C --> D[Room Cleaning<br/>RAII Auto-Cleanup]:::auto

<<<< END >>>>

<<<< ID: DIA_13cd663b >>>>
sequenceDiagram
participant C as Code
participant O as Object
participant R as Resource
rect rgb(225, 245, 255)
    Note over C,R: Initialization
    C->>O: Constructor()
    O->>R: Allocate Memory
end

rect rgb(255, 255, 224)
    Note over C,R: Usage Scope
    C->>O: Use Object
    O->>R: Read/Write
end

rect rgb(225, 255, 225)
    Note over C,R: Automatic Cleanup (RAII)
    C->>O: End of Scope
    O->>O: Destructor()
    O->>R: Free Memory
end

<<<< END >>>>

<<<< ID: DIA_957a8b47 >>>>
flowchart TD
classDef base fill:#eee,stroke:#333,color:#000
classDef exclusive fill:#f8bbd0,stroke:#880e4f,color:#000
classDef shared fill:#bbdefb,stroke:#0d47a1,color:#000
classDef item fill:#fff,stroke:#333,color:#000
RC[refCount Base]:::base

RC --> Auto[autoPtr T: Exclusive]:::exclusive
RC --> Tmp[tmp T: Shared]:::shared

Auto --> F1[Field Classes]:::item
Auto --> F2[Matrix Classes]:::item
Auto --> F3[Mesh Objects]:::item

Tmp --> T1[Expression Templates]:::item
Tmp --> T2[Temporary Fields]:::item
Tmp --> T3[Intermediate Results]:::item

<<<< END >>>>

<<<< ID: DIA_2b8d7efb >>>>
stateDiagram-v2
classDef active fill:#e8f5e9,stroke:#2e7d32
classDef dead fill:#ffcdd2,stroke:#c62828
[*] --> Created: Constructor (Ref=1)
Created --> Shared: Copy/Assign (Ref++)
Shared --> Shared: More Usage (Ref++)

Shared --> Decrement: Destructor called
Decrement --> Shared: Ref > 0
Decrement --> Destroyed: Ref == 0

Destroyed --> [*]: Memory Freed

Created:::active
Shared:::active
Destroyed:::dead

<<<< END >>>>

<<<< ID: DIA_95faac02 >>>>
flowchart TD
classDef normal fill:#e8f5e9,stroke:#2e7d32,color:#000
classDef error fill:#ffcdd2,stroke:#c62828,color:#000
classDef cleanup fill:#bbdefb,stroke:#0d47a1,color:#000
Start(Try Block) --> Alloc[Allocate: U, p, File]:::normal
Alloc --> Exec[Solve Navier-Stokes]:::normal
Exec --> Check{Exception?}

Check -- No --> Finish[Normal Completion]:::normal
Check -- Yes --> Unwind[Stack Unwinding]:::error

Unwind --> C1[~ofstream: Close File]:::cleanup
C1 --> C2[~autoPtr: Delete p]:::cleanup
C2 --> C3[~autoPtr: Delete U]:::cleanup

C3 --> Catch[Catch Block]:::error
Catch --> Safe[System Stable]:::normal
Finish --> Safe

<<<< END >>>>

<<<< ID: DIA_c64e3767 >>>>
flowchart LR
classDef state fill:#fff9c4,stroke:#fbc02d,color:#000
classDef action fill:#e1f5fe,stroke:#0277bd,color:#000
classDef result fill:#c8e6c9,stroke:#2e7d32,color:#000
A[A: Ref=1]:::state -->|Assign B=A| B[A & B: Ref=2<br/>Shared Data]:::state
B --> Check{Modify B?}

Check -- No --> B
Check -- Yes --> COW[Deep Copy]:::action

COW --> ResA[A: Ref=1<br/>Orig Data]:::result
COW --> ResB[B: Ref=1<br/>New Data]:::result

<<<< END >>>>

<<<< ID: DIA_1e99ed30 >>>>
flowchart TD
classDef q fill:#e0e0e0,stroke:#333,shape:diamond,color:#000
classDef auto fill:#f8bbd0,stroke:#880e4f,color:#000
classDef tmp fill:#bbdefb,stroke:#0d47a1,color:#000
Q1{Exclusive Ownership?}:::q

Q1 -- Yes --> Auto[Use autoPtr T]:::auto
Q1 -- No --> Tmp[Use tmp T]:::tmp

Auto --> A1[Factory Functions]
Auto --> A2[Large Non-Copyable]

Tmp --> T1[Expression Templates]
Tmp --> T2[Return Optimization]

<<<< END >>>>

<<<< ID: DIA_d81282c8 >>>>
flowchart LR
classDef step fill:#f5f5f5,stroke:#333,color:#000
classDef startend fill:#000,stroke:#000,color:#fff
S((Start)):::startend --> C1[1. Why Special Containers?]:::step
C1 --> C2[2. Memory Basics: RAII]:::step
C2 --> C3[3. Container Systems]:::step
C3 --> C4[4. Integration & Practice]:::step
C4 --> E((End)):::startend

<<<< END >>>>

<<<< ID: DIA_e285ea91 >>>>
flowchart LR
classDef data fill:#e1f5fe,stroke:#0288d1,color:#000
classDef op fill:#fff9c4,stroke:#fbc02d,color:#000
classDef result fill:#ffccbc,stroke:#d84315,color:#000
U[Vector Field U]:::data --> Op[Curl: ∇×U]:::op
Op --> W[Vorticity ω]:::result
W --> Analysis[Rotation Analysis]:::data

<<<< END >>>>

<<<< ID: DIA_c3cce3ca >>>>
flowchart LR
classDef vec fill:#e1f5fe,stroke:#0277bd,color:#000
classDef scal fill:#ffecb3,stroke:#ff6f00,color:#000
classDef op fill:#e0e0e0,stroke:#333,stroke-dasharray: 5 5,color:#000
U[Vector U]:::vec -- fvc::curl --> V[Vorticity]:::vec
T[Scalar T]:::scal -- fvm::laplacian --> H[Heat Matrix]:::scal

<<<< END >>>>

<<<< ID: DIA_c64a534b >>>>
flowchart TD
classDef explicit fill:#ffccbc,stroke:#bf360c,stroke-width:2px,color:#000
classDef implicit fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
classDef logic fill:#fff9c4,stroke:#fbc02d,color:#000
subgraph FVC [fvc:: Explicit Calculus]
    D1[Known Field Values]:::explicit --> Op1[Calculate Now]:::logic
    Op1 --> R1[New Field Value]:::explicit
end

subgraph FVM [fvm:: Implicit Calculus]
    D2[Unknown Future Values]:::implicit --> Op2[Build Coefficients]:::logic
    Op2 --> Mat[fvMatrix: Ax = b]:::implicit
    Mat --> Solve[Linear Solver]:::logic
    Solve --> R2[Future Field Value]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_c549d6d1 >>>>
flowchart LR
classDef implicit fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef explicit fill:#ffccbc,stroke:#bf360c,color:#000
classDef check fill:#fff9c4,stroke:#fbc02d,color:#000
Mom[Momentum Pred<br/>Implicit]:::implicit --> Flux[Flux Calc<br/>Explicit]:::explicit
Flux --> P[Pressure Eq<br/>Implicit]:::implicit
P --> Corr[Vel Correction<br/>Explicit]:::explicit

Corr --> Conv{Converged?}:::check
Conv -- No --> P
Conv -- Yes --> Next[Next Time Step]:::implicit

<<<< END >>>>

<<<< ID: DIA_c257097b >>>>
flowchart LR
classDef s fill:#e1f5fe,stroke:#0277bd,color:#000
classDef v fill:#e8f5e9,stroke:#2e7d32,color:#000
classDef t fill:#f3e5f5,stroke:#7b1fa2,color:#000
Scalar[Scalar p]:::s -->|fvc::grad| Vector[Vector gradP]:::v
Vector -->|fvc::grad| Tensor[Tensor gradU]:::t

<<<< END >>>>

<<<< ID: DIA_c3eaae75 >>>>
flowchart LR
classDef math fill:#fff9c4,stroke:#fbc02d,color:#000
classDef disc fill:#c8e6c9,stroke:#2e7d32,color:#000
V["Volume Integral: ∫∇·U dV"]:::math -->|Gauss Thm| S["Surface Integral: ∮U·dA"]:::math
S -->|Discretize| Sum["Sum: Σ(Flux · Area)"]:::disc

<<<< END >>>>

<<<< ID: DIA_dca7b12b >>>>
flowchart LR
classDef flow fill:#e1f5fe,stroke:#0277bd,color:#000
classDef cell fill:#e0e0e0,stroke:#333,color:#000
classDef res fill:#fff9c4,stroke:#fbc02d,color:#000
In[Inflow]:::flow --> C{Cell}:::cell
C --> Out[Outflow]:::flow

C --> Bal[Div=0: Balanced]:::res
C --> Src[Div>0: Source]:::res
C --> Sink[Div<0: Sink]:::res

<<<< END >>>>

<<<< ID: DIA_8232d3fe >>>>
flowchart LR
classDef theory fill:#e1bee7,stroke:#4a148c,color:#000
classDef step fill:#fff9c4,stroke:#fbc02d,color:#000
classDef code fill:#c8e6c9,stroke:#2e7d32,color:#000
Vol[Integral Form]:::theory -->|Gauss| Surf[Surface Form]:::theory
Surf -->|Summation| Disc[Discrete Faces]:::step
Disc -->|Code| Res[fvc::div(phi)]:::code

<<<< END >>>>

<<<< ID: DIA_c9890284 >>>>
flowchart LR
classDef root fill:#333,stroke:#000,color:#fff
classDef branch fill:#e0e0e0,stroke:#333,color:#000
classDef leaf fill:#fff,stroke:#333,color:#000
Root((Vector Calculus)):::root

subgraph NS [Namespaces]
    N1[fvc: Explicit]:::branch
    N2[fvm: Implicit]:::branch
end

subgraph Ops [Operators]
    O1[grad / div]:::branch
    O2[curl / laplacian]:::branch
end

subgraph Th [Theory]
    T1[Gauss Theorem]:::branch
    T2[Discretization]:::branch
end

Root --- NS & Ops & Th
NS --- N1 & N2
Ops --- O1 & O2
Th --- T1 & T2

<<<< END >>>>

<<<< ID: DIA_ea2dd331 >>>>
flowchart TD
classDef section fill:#f5f5f5,stroke:#333,color:#000
classDef topic fill:#e3f2fd,stroke:#1565c0,color:#000
A[Overview]:::section --> B[fvc vs fvm]:::topic
B --> C[Gradient & Divergence]:::topic
C --> D[Curl & Laplacian]:::topic
D --> E[Applications]:::section

<<<< END >>>>

<<<< ID: DIA_dfd3c1da >>>>
classDiagram
class dimensionedType~T~ {
+word name
+dimensionSet dims
+Type value
+operators()
}
class dimensionSet {
    +scalar exponents[7]
    +operator*()
    +operator/()
}

class dimensionedScalar {
    +scalar value
}

class dimensionedVector {
    +vector value
}

dimensionedType~T~ *-- dimensionSet
dimensionedType~T~ <|-- dimensionedScalar
dimensionedType~T~ <|-- dimensionedVector

<<<< END >>>>

<<<< ID: DIA_42b23ae7 >>>>
flowchart TD
classDef action fill:#e1f5fe,stroke:#0277bd,color:#000
classDef check fill:#fff9c4,stroke:#fbc02d,color:#000
classDef fail fill:#ffcdd2,stroke:#c62828,color:#000
classDef pass fill:#c8e6c9,stroke:#2e7d32,color:#000
Code[Write Code]:::action --> Check{Dim Check}:::check

Check -- Pass --> Run[Runtime Execution]:::pass
Check -- Fail --> Err[Compiler Error]:::fail

Err --> Fix[Fix Dimensions]:::action
Fix --> Code

<<<< END >>>>

<<<< ID: DIA_d053dc5b >>>>
flowchart LR
classDef file fill:#e0e0e0,stroke:#333,color:#000
classDef ok fill:#c8e6c9,stroke:#2e7d32,color:#000
classDef fail fill:#ffcdd2,stroke:#c62828,color:#000
subgraph Sources [Input Files]
    F1[p = 101325 Pa]:::file
    F2[p = 101325 (No Unit)]:::file
    F3[p = 14.7 PSI]:::file
end

Solver((Solver))

F1 -->|Consistent| OK[Run]:::ok
F2 -->|Ambiguous| OK
F3 -->|Mismatch| Err[Physics Error]:::fail

<<<< END >>>>

<<<< ID: DIA_a79ceff8 >>>>
flowchart TD
classDef base fill:#e3f2fd,stroke:#1565c0,color:#000
classDef ext fill:#fff3e0,stroke:#e65100,color:#000
A[Standard 7 SI Dimensions]:::base

subgraph Extensions
    B[Extended Systems]:::ext
    C[Currency / Info]:::ext
end

A --> B & C

<<<< END >>>>

<<<< ID: DIA_82aa6013 >>>>
flowchart LR
classDef plain fill:#ffcdd2,stroke:#c62828,color:#000
classDef dim fill:#c8e6c9,stroke:#2e7d32,color:#000
subgraph Raw [No Dimensioning]
    A1[1M Ops]:::plain --> B1[0.01s]:::plain
end

subgraph Dims [With Dimensioning]
    A2[1M Ops]:::dim --> B2[0.012s]:::dim
end

B1 -.->|Small Overhead| B2

<<<< END >>>>

<<<< ID: DIA_353b57aa >>>>
flowchart LR
classDef type fill:#e1f5fe,stroke:#0277bd,color:#000
classDef op fill:#fff9c4,stroke:#fbc02d,color:#000
DS[dimensionedScalar]:::type -->|.value()| S[scalar]:::type
S -->|constructor| DS2[dimensionedScalar]:::type

DS -->|operator+| DS
S -->|operator*| DS

<<<< END >>>>

<<<< ID: DIA_c4991009 >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
subgraph Inputs [" Explicit Inputs "]
    direction TB
    A["Source Code<br/>Templates"]:::explicit
    F["Physical Quantities"]:::explicit
    G["Mathematical Operations"]:::explicit
end

subgraph System [" Compiler System "]
    direction TB
    B["Template Metaprogramming<br/>Compile-time Processing"]:::implicit
    C["Type System<br/>Dimension Analysis"]:::implicit
    D["Dimension Safety<br/>Unit Validation"]:::implicit
end

subgraph Output [" Result "]
    E["Compiled Binary<br/>Runtime Execution"]:::implicit
end

subgraph Comparison [" Paradigm Shift "]
    H["Traditional Approach<br/>Runtime Errors"]:::explicit -.-> I["Template Metaprogramming<br/>Compile-time Safety"]:::implicit
end

A --> B
G --> B
B --> C
F --> C
C --> D
D --> E

<<<< END >>>>

<<<< ID: DIA_4e19676b >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
subgraph UserSpace [" Module 1: Basic Usage (Explicit) "]
    direction TB
    A["Field Types"]:::explicit --> B["Basic Operations"]:::explicit
    B --> C["Simple Applications"]:::explicit
    C --> D["User Level"]:::explicit
end

subgraph DevSpace [" Advanced Module: Extension (Implicit) "]
    direction TB
    E["Template Metaprogramming"]:::implicit --> F["Custom Physics Models"]:::implicit
    F --> G["Framework Design"]:::implicit
    G --> H["Developer Level"]:::implicit
end

subgraph Bridges [" Knowledge Evolution "]
    I["How to Use"]:::context --> J["Why It Works"]:::context
    J --> K["How to Extend"]:::context
end

D -.-> I
I -.-> E
H -.-> K

<<<< END >>>>

<<<< ID: DIA_3fbf4341 >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
A["Source Code<br/>With Dimensions"]:::explicit --> B["C++ Template<br/>Metaprogramming"]:::implicit
B --> C["Compile-Time<br/>Dimension Analysis"]:::implicit
C --> D["Dimensional<br/>Consistency Check"]:::implicit
D --> E{"Valid?"}:::implicit

E -->|Yes| F["Zero Runtime<br/>Overhead"]:::implicit
E -->|No| G["Compile-Time<br/>Error"]:::error

F --> H["Type-Safe<br/>Mathematical Operations"]:::implicit
H --> I["Physically<br/>Correct Calculations"]:::implicit
G --> J["Debug Source<br/>Code"]:::explicit

<<<< END >>>>

<<<< ID: DIA_06e85516 >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
A["dimensioned&lt;Type&gt;"]:::implicit

subgraph Components
    B["Name (word)"]:::explicit
    C["Dimensions (dimensionSet)"]:::implicit
    D["Value (Type)"]:::explicit
end

A --> B & C & D

B --> B1["ตัวระบุสตริง"]:::explicit

subgraph Units [" 7 Base SI Units "]
    direction TB
    C1["มวล M"]:::implicit
    C2["ความยาว L"]:::implicit
    C3["เวลา T"]:::implicit
    C4["อุณหภูมิ Θ"]:::implicit
    C5["จำนวนโมล N"]:::implicit
    C6["กระแสไฟฟ้า I"]:::implicit
    C7["ความเข้มแสง J"]:::implicit
end
C --> C1 & C2 & C3 & C4 & C5 & C6 & C7

D --> D1["สเกลาร์/เวกเตอร์/เทนเซอร์"]:::explicit

<<<< END >>>>

<<<< ID: DIA_fb1f4449 >>>>
classDiagram
class DimensionedBase~Derived~ {
+operator+(Derived)
+operator-(Derived)
}
class dimensioned~Type~ {
+add(a, b)
}
DimensionedBase <|-- dimensioned : Inherits with self-type
style DimensionedBase fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
style dimensioned fill:#ffccbc,stroke:#d84315,stroke-width:2px

<<<< END >>>>

<<<< ID: DIA_54c0e9d0 >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
subgraph Inputs [" Field Inputs "]
    p["p (Field)"]:::explicit
    rho["rho (Field)"]:::explicit
    T["T (Field)"]:::explicit
end

subgraph Tree [" Expression Tree "]
    Op1["/"]:::implicit
    Op2["*"]:::implicit
end

Op1 --> p & rho
Op2 --> Op1 & T

<<<< END >>>>

<<<< ID: DIA_f66717f9 >>>>
graph LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
A["p / rho * T"]:::explicit --> B["Expression Tree<br/>Multiply(Divide(p, rho), T)"]:::implicit
B --> C["Single Loop Execution<br/>(Loop Fusion)"]:::implicit
C --> D["Result Field"]:::implicit

<<<< END >>>>

<<<< ID: DIA_82c9ce16 >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
A[นักพัฒนาเขียนโค้ด]:::explicit --> B{การดำเนินการ: A + B}:::implicit
B --> C[คอมไพเลอร์ตรวจสอบประเภทข้อมูล]:::implicit
C --> D{มิติข้อมูลตรงกันหรือไม่?}:::implicit

D -- ไม่ตรง --> E[ข้อผิดพลาดคอมไพล์: หยุดทำงาน]:::error
E --> G[แก้ไขข้อผิดพลาดฟิสิกส์ตั้งแต่เนิ่นๆ]:::explicit

D -- ตรง --> F[สร้างไบนารีที่มีประสิทธิภาพ]:::implicit
F --> H[การจำลองทำงานรวดเร็ว]:::implicit

<<<< END >>>>

<<<< ID: DIA_83a5b54b >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
A[Template Instantiation]:::explicit --> B{Type Check}:::implicit
B -->|dimensioned~Type~| C[Extract dimensionSet from Type]:::implicit
B -->|Other Type| D[Error: Not a dimensioned type]:::error

C --> E{Operation Type}:::implicit
E -->|Add/Sub| F["Check Dimension Equality<br>static_assert(dimsA == dimsB)"]:::implicit
E -->|Multiply| G["Add Dimension Exponents<br>dimsResult = dimsA + dimsB"]:::implicit
E -->|Divide| H["Subtract Dimension Exponents<br>dimsResult = dimsA - dimsB"]:::implicit
E -->|Power| I["Multiply Dimension Exponents<br>dimsResult = dimsA * exponent"]:::implicit

F --> J{Dimensions Match?}:::implicit
J -->|Yes| K[Generate Operation Code]:::implicit
J -->|No| L[Compile Error<br>Dimension Mismatch]:::error

G --> K
H --> K
I --> K

K --> M[Compile Success<br>Zero Runtime Overhead]:::implicit
L --> N[Compile Failure<br>Early Error Detection]:::error

<<<< END >>>>

<<<< ID: DIA_365b5ef1 >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
A[PhysicsPlugin Base]:::implicit

subgraph Plugins [" Specific Implementations "]
    B[TurbulenceModel Plugin]:::explicit
    C[ReactionModel Plugin]:::explicit
    D[HeatTransfer Plugin]:::explicit
    E[Custom Physics Plugin]:::explicit
end

A --> B & C & D & E

B & C & D & E --> F[Dimensional Consistency Check]:::implicit

subgraph Verification [" Safety Layer "]
    F --> G[Compile-time Verification]:::implicit
    F --> H[Runtime Validation]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_1fa634a0 >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
subgraph Domains [" Physics Domains (Inputs) "]
    A[Fluid Domain]:::explicit
    C[Structural Domain]:::explicit
    F[Thermal Domain]:::explicit
end

subgraph Interface [" Interface Layer "]
    B[Unit Conversion Layer]:::implicit
    D[Dimensional Consistency Check]:::implicit
    E[Compatible Interface]:::implicit
    G[Pressure-Temperature Coupling]:::implicit
end

A -->|Force/Volume| B
C -->|Displacement| B
F -->|Temperature| B

B --> D
D --> E
B --> G

<<<< END >>>>

<<<< ID: DIA_bf8c971f >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
subgraph Sources [" Diverse Inputs "]
    H[International Team 1]:::explicit --> A[SI Units]:::explicit
    I[International Team 2]:::explicit --> B[Imperial Units]:::explicit
    J[International Team 3]:::explicit --> C[CGS Units]:::explicit
    E[Natural Units]:::explicit
end

subgraph System [" Unification System "]
    D[Unit Conversion System]:::implicit
    F[Dimensional Consistency Check]:::implicit
    G[Standardized Workflow]:::implicit
end

A & B & C & E --> D
D --> F --> G

<<<< END >>>>

<<<< ID: DIA_a06ee1c1 >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
subgraph Theory [" Mathematical Foundation "]
    A[Buckingham Pi Theorem]:::context
    C[Dimensional Homogeneity]:::context
    B[Dimensional Analysis Framework]:::implicit
end

subgraph Implementation [" OpenFOAM Core "]
    D[OpenFOAM Implementation]:::implicit
    E[Compile-time Checks]:::implicit
    F[Runtime Checks]:::implicit
    G[Physical Consistency]:::implicit
end

subgraph Outcome [" Simulation Quality "]
    H[Reliable CFD Simulations]:::explicit
end

A & C --> B --> D
D --> E & F --> G --> H

<<<< END >>>>

<<<< ID: DIA_16cfeea2 >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
A[Dimensional Code]:::explicit --> B{Template Metaprogramming}:::implicit

subgraph Techniques [" Optimization Techniques "]
    B --> C[Compile-Time Resolution]:::implicit
    B --> D[Expression Templates]:::implicit
    B --> E[Loop Fusion]:::implicit
end

C & D & E --> F[Optimized Machine Code]:::implicit
F --> G[Zero Runtime Overhead]:::implicit

<<<< END >>>>

<<<< ID: DIA_ff92e86e >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
Start((เริ่มบทเรียน)):::explicit --> PhysicsAware[1. ระบบที่ตระหนักถึงฟิสิกส์]:::implicit
PhysicsAware --> Mechanisms[2. กลไก dimensionSet & dimensionedType]:::implicit
Mechanisms --> TMP[3. Template Metaprogramming]:::implicit
TMP --> Pitfalls[4. ปัญหาและแนวทางแก้ไข]:::implicit
Pitfalls --> Math[5. ความเชื่อมโยงทางคณิตศาสตร์]:::implicit
Math --> End((สรุปและแบบฝึกหัด)):::explicit

<<<< END >>>>

<<<< ID: DIA_88519419 >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
A[ตัวแปรที่มีมิติ]:::explicit --> B[สร้างเมทริกซ์มิติ A]:::implicit
B --> C[คำนวณ Null Space]:::implicit
C --> D[สกัดคำตอบจำนวนเต็ม]:::implicit
D --> E[สร้างกลุ่มไร้มิติ]:::implicit
E --> F[Re, Fr, Ma, ฯลฯ]:::implicit

<<<< END >>>>

<<<< ID: DIA_40217087 >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
NS["Navier-Stokes Equation"]:::explicit

subgraph Terms [" Equation Terms "]
    T1["Unsteady<br>[M L^-2 T^-2]"]:::context
    T2["Convection<br>[M L^-2 T^-2]"]:::context
    T3["Pressure<br>[M L^-2 T^-2]"]:::context
    T4["Viscous<br>[M L^-2 T^-2]"]:::context
    T5["Source<br>[M L^-2 T^-2]"]:::context
end

NS --> T1 & T2 & T3 & T4 & T5

T1 & T2 & T3 & T4 & T5 --> Check{Dimensionally<br>Homogeneous?}:::implicit

Check -->|Yes| Valid[Valid for Simulation]:::implicit
Check -->|No| Error[Dimensional Inconsistency Detected]:::explicit

<<<< END >>>>

<<<< ID: DIA_415544e3 >>>>
flowchart LR
%% Classes
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
subgraph "symmTensor Memory Layout"
    direction TB
    XY[Comp: XY]:::implicit -->|"Mirror"| YX[Virtual: YX]:::context
    XZ[Comp: XZ]:::implicit -->|"Mirror"| ZX[Virtual: ZX]:::context
    YZ[Comp: YZ]:::implicit -->|"Mirror"| ZY[Virtual: ZY]:::context
end

<<<< END >>>>

<<<< ID: DIA_e31f5f54 >>>>
flowchart TD
%% Classes
classDef rank0 fill:#e1bee7,stroke:#4a148c,stroke-width:2px,color:#000
classDef rank1 fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000
classDef rank2 fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000
S[Rank 0: Scalar<br/>1 Component]:::rank0 -->|Magnitude only| V[Rank 1: Vector<br/>3 Components]:::rank1
V -->|Magnitude + Direction| T[Rank 2: Tensor<br/>9 Components]:::rank2
T -->|Magnitude + Directions + Transformations| HT[Higher Order Tensors]:::rank2

<<<< END >>>>

<<<< ID: DIA_9a0bf4cc >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
T[เมทริกซ์เทนเซอร์ที่ซับซ้อน]:::explicit

subgraph Decomposition [" Decomposition "]
    T -->|eigenValues| V[3 ขนาดหลัก: λ]:::implicit
    T -->|eigenVectors| D[3 ทิศทางหลัก: v]:::implicit
end

subgraph Insight [" Physical Interpretation "]
    V & D --> P[ข้อมูลเชิงลึกทางฟิสิกส์: ความเค้น/ความเครียดสูงสุด]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_8c27b794 >>>>
mindmap
root((Tensor Algebra))
Types
Full Tensor (9)
Symmetric (6)
Spherical (1)
Operations
Dot (&) / Double Dot (&&)
Trace / Det / Inv
Deviatoric / Skew
Analysis
Eigenvalues
Eigenvectors
Invariants
Physics
Stress / Strain
Reynolds Stress
Conductivity

<<<< END >>>>

<<<< ID: DIA_645652c7 >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
subgraph Inputs [" Operands "]
    T[เทนเซอร์ T]:::explicit
    V1[เวกเตอร์ A]:::explicit
    V2[เวกเตอร์ B]:::explicit
end

subgraph Results [" Result Types "]
    V[ผลลัพธ์เวกเตอร์]:::implicit
    S[ผลลัพธ์สเกลาร์]:::implicit
    T_Res[ผลลัพธ์เทนเซอร์]:::implicit
end

T -- "& dot" --> V
T -- "&& double dot" --> S
V1 -- "* outer" --> T_Res
V2 -- "* outer" --> T_Res

<<<< END >>>>

<<<< ID: DIA_5716ffba >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
T["Tensor Types"]:::context

subgraph Variants [" Optimized Storage "]
    T --> T9["tensor<br/><b>9 Components</b><br/>Full Matrix"]:::implicit
    T --> T6["symmTensor<br/><b>6 Components</b><br/>Symmetric Matrix"]:::implicit
    T --> T1["sphericalTensor<br/><b>1 Component</b><br/>Identity Scale"]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_7e427cc9 >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000
A[Physical Quantity]:::explicit --> B{Symmetry?}:::decision

B -->|No Symmetry| C[tensor<br/>9 components<br/>100% memory]:::implicit

B -->|Symmetric| D{Isotropic?}:::decision

D -->|Yes| E[sphericalTensor<br/>1 component<br/>11% memory]:::implicit
D -->|No| F[symmTensor<br/>6 components<br/>67% memory]:::implicit

<<<< END >>>>

<<<< ID: DIA_bce9a10b >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
A[Template&lt;Cmpt&gt;]:::context

subgraph Storage [" Underlying Storage "]
    B[MatrixSpace&lt;tensor&lt;Cmpt&gt;, Cmpt, 3, 3&gt;]:::implicit
    C[VectorSpace&lt;symmTensor&lt;Cmpt&gt;, Cmpt, 6&gt;]:::implicit
    D[VectorSpace&lt;sphericalTensor&lt;Cmpt&gt;, Cmpt, 1&gt;]:::implicit
end

subgraph Types [" User Types "]
    E[tensor: 9 components]:::explicit
    F[symmTensor: 6 components]:::explicit
    G[sphericalTensor: 1 component]:::explicit
end

A --> B & C & D
B --> E
C --> F
D --> G

<<<< END >>>>

<<<< ID: DIA_dbb1852b >>>>
graph LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
A["โครงสร้าง OpenFOAM CFD"]:::context --> B["ประเภทข้อมูลพื้นฐาน (Primitive Types)"]:::context

subgraph Primitives [" Core Types "]
    C["label<br/>ประเภทจำนวนเต็ม"]:::implicit
    D["scalar<br/>เลขทศนิยม"]:::implicit
    E["word<br/>ประเภทสตริง"]:::implicit
end

B --> C & D & E

subgraph UsageC [" Label Usage "]
    C --> C1["การทำดัชนีเมช"]:::explicit
    C --> C2["ตัวนับลูป"]:::explicit
    C --> C3["ขนาดอาร์เรย์"]:::explicit
end

subgraph UsageD [" Scalar Usage "]
    D --> D1["ปริมาณทางฟิสิกส์"]:::explicit
    D --> D2["ค่าตัวเลข"]:::explicit
    D --> D3["การดำเนินการทางคณิตศาสตร์"]:::explicit
end

subgraph UsageE [" Word Usage "]
    E --> E1["ชื่อฟิลด์"]:::explicit
    E --> E2["เส้นทางไฟล์"]:::explicit
    E --> E3["เงื่อนไขขอบเขต"]:::explicit
end

<<<< END >>>>

<<<< ID: DIA_0425068e >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
subgraph AddSub [ "Addition / Subtraction" ]
    A[Operation: Q1 + Q2]:::explicit --> B{Are dimensions equal?}:::implicit
    B -->|Yes| C[Perform numerical operation]:::implicit
    B -->|No| D[Error: Incompatible units]:::error
end

subgraph MultDiv [ "Multiplication / Division" ]
    E[Operation: Q1 * Q2]:::explicit --> F[Add dimension exponents]:::implicit
    F --> G[Return new dimensionedType]:::implicit

    H[Operation: Q1 / Q2]:::explicit --> I[Subtract dimension exponents]:::implicit
    I --> J[Return new dimensionedType]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_e94c61f7 >>>>
mindmap
root((dimensionSet))
M(Mass - kg)
L(Length - m)
T(Time - s)
Theta(Temperature - K)
I(Current - A)
N(Quantity - mol)
J(Luminous - cd)

<<<< END >>>>

<<<< ID: DIA_4d463241 >>>>
classDiagram
class dimensionedType {
+dimensionSet dimensions
+value()
}
dimensionedType <|-- dimensionedScalar
dimensionedType <|-- dimensionedVector
dimensionedType <|-- dimensionedTensor
note for dimensionedType "Tracks physical dimensions"
style dimensionedType fill:#e3f2fd,stroke:#1565c0,stroke-width:2px

<<<< END >>>>

<<<< ID: DIA_876529cc >>>>
sequenceDiagram
participant P1 as autoPtr A
participant Obj as Data Object
participant P2 as autoPtr B
Note over P1,Obj: A owns Object
P1->>P2: Transfer Ownership (Assignment)
Note over P1: A is now NULL (Empty)
Note over P2,Obj: B now owns Object
Note over P2,Obj: When B goes out of scope, Object is deleted

<<<< END >>>>

<<<< ID: DIA_195590c6 >>>>
graph LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
subgraph References [" Smart Pointers (tmp) "]
    T1["tmp<br/>Ref Count: 1"]:::explicit
    T2["tmp<br/>Ref Count: 2"]:::explicit
    T3["tmp<br/>Ref Count: 3"]:::explicit
end

subgraph Shared [" Shared Resource "]
    Obj["Data Object<br/>(Large Field)"]:::implicit
end

T1 & T2 & T3 --- Obj

<<<< END >>>>

<<<< ID: DIA_8b7aeb76 >>>>
graph LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
subgraph Hardware [" Hardware Variations (Volatile) "]
    A["32-bit System<br/>Single Precision"]:::explicit
    B["64-bit System<br/>Double Precision"]:::explicit
    D["Supercomputer<br/>Mixed Precision"]:::explicit
end

subgraph Abstraction [" OpenFOAM Abstraction Layer "]
    C["Platform-Independent<br/>Type System"]:::implicit
    E["label<br/>Integer Type"]:::implicit
    F["scalar<br/>Floating Point Type"]:::implicit
    G["vector<br/>3D Vector Type"]:::implicit
    H["tensor<br/>3x3 Tensor Type"]:::implicit
end

subgraph Result [" Consistent Behavior "]
    I["CFD Application Code"]:::context
end

A & B & D --> C
C --> E & F & G & H
E & F & G & H --> I

<<<< END >>>>

<<<< ID: DIA_d195753e >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
A["OpenFOAM Primitive Types Hierarchy"]:::implicit

subgraph Foundation [" Foundation Layer "]
    B["Basic Primitives"]:::implicit
    C["label"]:::implicit
    D["scalar"]:::implicit
    E["word"]:::implicit
end

subgraph Advanced [" Advanced Layer "]
    F["Advanced Primitives"]:::implicit
    G["dimensionedType"]:::explicit
    H["autoPtr"]:::explicit
    I["tmp"]:::explicit
    J["List"]:::explicit
end

A --> B
B --> C & D & E
B --> F
F --> G & H & I & J

<<<< END >>>>

<<<< ID: DIA_6320bf8c >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
A[Source Code]:::explicit --> B{Compile Time}:::context

B -->|WM_LABEL_SIZE=32| C[label = int32_t]:::implicit
B -->|WM_LABEL_SIZE=64| D[label = int64_t]:::implicit
B -->|WM_SP| E[scalar = float]:::implicit
B -->|WM_DP| F[scalar = double]:::implicit

C & D & E & F --> G[Consistent Behavior]:::context

<<<< END >>>>

<<<< ID: DIA_b4ed587b >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
A[Contiguous Memory]:::implicit

subgraph Mechanisms [" Hardware Mechanisms "]
    B[Cache Line Utilization]:::context
    C[SIMD Vectorization]:::context
    D[Prefetching Effectiveness]:::context
end

subgraph Benefits [" Performance Benefits "]
    E[Reduced Cache Misses]:::implicit
    F[Parallel Operations]:::implicit
    G[Hidden Memory Latency]:::implicit
end

H[↑ Performance]:::explicit

A --> B & C & D
B --> E
C --> F
D --> G
E & F & G --> H

<<<< END >>>>

<<<< ID: DIA_fa7d9f15 >>>>
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
subgraph Before [" Before Assignment "]
    B[fieldPtr: owns object]:::explicit
    C[anotherPtr: empty]:::context
end

subgraph After [" After Assignment "]
    E[fieldPtr: empty]:::context
    F[anotherPtr: owns object]:::explicit
end

Before --> After

<<<< END >>>>

<<<< ID: DIA_b2692ea0 >>>>
classDiagram
UList <|-- List
List <|-- Field
Field <|-- volField
dimensionedType <|-- dimensionedScalar
dimensionedType <|-- dimensionedVector
autoPtr --> "*Owns" Object
tmp --> "*References" Object
note for dimensionedType "ติดตามมิติทางกายภาพ"
note for autoPtr "ความเป็นเจ้าของแบบผูกขาด"
note for tmp "การนับการอ้างอิงพร้อมการคัดลอกเมื่อมีการเขียน"

style UList fill:#f5f5f5,stroke:#616161,stroke-width:2px
style List fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
style Field fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
style volField fill:#ffccbc,stroke:#d84315,stroke-width:2px

<<<< END >>>>

<<<< ID: DIA_27da7a35 >>>>
flowchart TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
subgraph AddSub [ "การบวก / การลบ" ]
    A[การดำเนินการ: Q1 + Q2]:::explicit --> B{มิติเท่ากันหรือไม่?}:::implicit
    B -->|ใช่| C[ดำเนินการทางตัวเลข]:::implicit
    B -->|ไม่ใช่| D[ข้อผิดพลาด: หน่วยไม่เข้ากัน]:::error
end

subgraph MultDiv [ "การคูณ / การหาร" ]
    E[การดำเนินการ: Q1 * Q2]:::explicit --> F[บวกเลขชี้กำลังของมิติ]:::implicit
    F --> G[ส่งคืน dimensionedType ใหม่]:::implicit

    H[การดำเนินการ: Q1 / Q2]:::explicit --> I[ลบเลขชี้กำลังของมิติ]:::implicit
    I --> J[ส่งคืน dimensionedType ใหม่]:::implicit
end

<<<< END >>>>

<<<< ID: DIA_b1e0ea12 >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
UList["UList<T><br/>(No Memory Ownership)"]:::implicit --> List["List<T><br/>(Allocated Memory)"]:::implicit
List --> Field["Field<T><br/>(Algebraic Ops)"]:::implicit
Field --> GeometricField["GeometricField<T><br/>(Physical Field: p, U)"]:::explicit

<<<< END >>>>

<<<< ID: DIA_259b511d >>>>
graph TD
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
classDef context fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
Start((เริ่มต้น)):::explicit --> Basic[พื้นฐาน Primitives]:::context
Basic --> Types[ประเภทข้อมูลพื้นฐาน]:::implicit
Types --> Dimensions[มิติทางฟิสิกส์]:::implicit
Dimensions --> Memory[การจัดการหน่วยความจำ]:::implicit
Memory --> Containers[คอนเทนเนอร์]:::implicit
Containers --> Fields[คลาสฟิลด์]:::implicit
Fields --> Mesh[โครงสร้าง Mesh]:::implicit
Mesh --> Solvers[ระบบ Solver]:::explicit

<<<< END >>>>

