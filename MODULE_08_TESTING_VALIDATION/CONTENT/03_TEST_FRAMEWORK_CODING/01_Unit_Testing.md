# Unit Testing

การทดสอบ Unit Testing

---

## Overview

> **Unit test** = Test individual functions/classes in isolation

---

## 1. OpenFOAM Test Structure

```cpp
#include "TestCase.H"
#include "fvCFD.H"

class vectorTest : public Test::TestCase
{
public:
    void runTest()
    {
        vector a(1, 0, 0);
        vector b(0, 1, 0);
        
        // Test cross product
        vector c = a ^ b;
        ASSERT_EQ(c, vector(0, 0, 1));
    }
};
```

---

## 2. Basic Assertions

```cpp
// Equality
ASSERT_EQ(actual, expected);

// Floating point
ASSERT_NEAR(actual, expected, tolerance);

// Boolean
ASSERT_TRUE(condition);
ASSERT_FALSE(condition);
```

---

## 3. Testing Fields

```cpp
void testFieldOperations()
{
    // Create simple mesh
    fvMesh mesh(...);
    
    // Create field
    volScalarField T(mesh, dimensionedScalar("T", dimTemperature, 300));
    
    // Test operation
    volScalarField T2 = sqr(T);
    
    ASSERT_NEAR(T2[0], 90000, 1e-10);
}
```

---

## 4. Test Script

```bash
#!/bin/bash
# runUnitTests.sh

cd $FOAM_SRC/../test

for test in */; do
    echo "Running: $test"
    (cd "$test" && wmake && ./Test-$test)
    if [ $? -ne 0 ]; then
        echo "FAILED: $test"
        exit 1
    fi
done

echo "All tests passed"
```

---

## 5. Make Structure

```make
# Make/files
Test_vector.C

EXE = $(FOAM_USER_APPBIN)/Test_vector

# Make/options
EXE_INC = -I$(LIB_SRC)/finiteVolume/lnInclude
EXE_LIBS = -lfiniteVolume
```

---

## 6. Best Practices

| Practice | Why |
|----------|-----|
| Test one thing | Clear failure reason |
| Meaningful names | Document purpose |
| Independent tests | Order doesn't matter |
| Fast execution | Run often |

---

## Quick Reference

| Assert | Use |
|--------|-----|
| `ASSERT_EQ` | Exact equality |
| `ASSERT_NEAR` | Floating point |
| `ASSERT_TRUE` | Boolean true |
| `ASSERT_THROW` | Exception thrown |

---

## Concept Check

<details>
<summary><b>1. Unit test คืออะไร?</b></summary>

**Test single function/class** ไม่ใช่ whole system
</details>

<details>
<summary><b>2. ทำไมต้อง tolerance?</b></summary>

**Floating-point** ไม่ exactly equal
</details>

<details>
<summary><b>3. Independent tests ดีอย่างไร?</b></summary>

**Run in any order** — ไม่ depend on each other
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Validation:** [02_Validation_Coding.md](02_Validation_Coding.md)