# Common Errors and Debugging

Common Errors and Debugging in OpenFOAM Template Programming

---

## 🎯 Learning Objectives

By the end of this section, you will be able to:

- **Identify** common template and inheritance errors in OpenFOAM programming
- **Diagnose** error patterns from compiler messages and runtime failures
- **Apply** prevention strategies to avoid these errors in your code
- **Utilize** debugging tools (gdb, valgrind, sanitizers) effectively
- **Implement** best practices for robust, maintainable OpenFOAM code

---

## 📋 Quick Reference Table

| Error Type | Detection | Prevention | Severity |
|------------|-----------|------------|----------|
| **Pure Virtual Not Implemented** | `undefined reference to vtable` | Implement all pure virtuals | 🔴 Critical |
| **Missing Virtual Destructor** | Valgrind memory leaks | Always use `virtual ~Base()` | 🔴 Critical |
| **Object Slicing** | Silent data loss | Use pointers/references | 🟡 High |
| **RTS Type Not Found** | Runtime error message | Check registration + linking | 🔴 Critical |
| **Virtual in Constructor** | Wrong method called | Two-phase initialization | 🟡 High |
| **Covariant Return Confusion** | Compiler errors | Understand covariant rules | 🟢 Medium |
| **Template Instantiation Errors** | Long compiler messages | Explicit instantiation | 🟡 High |

---

## 1. Pure Virtual Function Not Implemented

### **What** (Definition)

When a class inherits from an abstract base class but fails to implement one or more pure virtual functions, the compiler generates an undefined reference to the vtable.

### **Why** (Impact)

- **Compilation failure**: Linker cannot create the vtable
- **Runtime crashes**: If somehow linked, calls jump to invalid memory
- **Incomplete abstraction**: Your class doesn't fulfill the contract

### **How** (Detection & Prevention)

#### **Real OpenFOAM Error Messages**

```
undefined reference to `Foam::fvPatchField<Foam::Vector<double>>::vtable'
ld returned 1 exit status
```

```
undefined reference to `vtable for Foam::myTurbulenceModel'
```

#### **Detection Strategies**

```bash
# 1. Check for undefined vtable symbols
nm -C yourLibrary.o | grep "vtable"

# 2. Grep for pure virtual declarations
grep -rn "virtual.*= 0" src/

# 3. Verify all base class methods are implemented
grep -A5 "class.*:" yourClass.H | grep "virtual"
```

#### **Prevention Checklist**

- [ ] **Identify all pure virtual functions** in base classes
- [ ] **Implement each pure virtual** in derived class with `override` keyword
- [ ] **Match signature exactly** (const, noexcept, parameters)
- [ ] **Compile with `-Wall -Werror`** to catch missing implementations
- [ ] **Use IDE tools** to show unimplemented methods

#### **Correct Implementation**

```cpp
// ❌ WRONG: Missing implementation
class myTurbulenceModel : public turbulenceModel
{
    // Missing: virtual tmp<volSymmTensorField> R() const;
    // Missing: virtual tmp<volScalarField> k() const;
};
// Error: undefined reference to vtable

// ✅ CORRECT: Implement all pure virtuals
class myTurbulenceModel : public turbulenceModel
{
public:
    // Implement required interface
    virtual tmp<volSymmTensorField> R() const override
    {
        return turbulenceModel::R();
    }
    
    virtual tmp<volScalarField> k() const override
    {
        return turbulenceModel::k();
    }
    
    virtual tmp<volScalarField> epsilon() const override
    {
        // Your implementation
        return epsilon_;
    }
    
    virtual void correct() override
    {
        // Solve your turbulence equations
    }
};
```

#### **OpenFOAM Example: Custom Boundary Condition**

```cpp
// myFixedValueFvPatchField.H
class myFixedValueFvPatchField
:
    public fvPatchField<vector>
{
public:
    // Constructor
    myFixedValueFvPatchField
    (
        const fvPatch&,
        const DimensionedField<vector, volMesh>&
    );
    
    // ✅ MUST implement all pure virtuals from fvPatchField
    virtual tmp<fvPatchField<vector>> clone() const override;
    
    virtual void updateCoeffs() override;
    
    virtual void write(Ostream&) const override;
};

// myFixedValueFvPatchField.C
// ✅ Implement each function
void myFixedValueFvPatchField::updateCoeffs()
{
    if (updated())
    {
        return;
    }
    
    // Your physics here
    fvPatchField<vector>::operator==(this->patchInternalField());
}
```

---

## 2. Missing Virtual Destructor

### **What** (Definition)

When deleting a derived object through a base class pointer without a virtual destructor, only the base class destructor is called, causing resource leaks.

### **Why** (Impact)

- **Memory leaks**: Derived class members not freed
- **Resource leaks**: File handles, connections not closed
- **Undefined behavior**: Subtle corruption in complex hierarchies

### **How** (Detection & Prevention)

#### **Real OpenFOAM Error Pattern**

No compiler error! Silent leak detected by valgrind:

```
==12345== LEAK SUMMARY:
==12345==    definitely lost: 1,024 bytes in 1 blocks
==12345==    indirectly lost: 5,120 bytes in 5 blocks
```

#### **Detection Strategies**

```bash
# 1. Run valgrind on your solver
valgrind --leak-check=full --show-leak-kinds=all ./mySolver

# 2. Check base class destructors
grep -n "~" yourBaseClass.H
grep -n "virtual.*~" yourBaseClass.H

# 3. Use sanitizers (faster than valgrind)
export WM_COMPILE_CONTROL=+c++14-lang
wmake
foamRun -s -sanitize ./mySolver
```

#### **Prevention Checklist**

- [ ] **Always declare `virtual ~Base()`** in polymorphic base classes
- [ ] **Use `= default`** when no custom cleanup needed
- [ ] **Check all base classes** in your inheritance hierarchy
- [ ] **Run valgrind** on custom boundary conditions/models
- [ ] **Prefer smart pointers** (`autoPtr`, `tmp`) to manual `delete`

#### **Correct Implementation**

```cpp
// ❌ WRONG: No virtual destructor
class Base
{
public:
    Base() = default;
    // Missing: virtual ~Base() = default;
    
    virtual void method() = 0;
};

class Derived : public Base
{
    double* data_;
public:
    Derived() : data_(new double[1000]) {}
    ~Derived() { delete[] data_; }  // Never called!
};

Base* ptr = new Derived();
delete ptr;  // ~Derived() never called! Leak!

// ✅ CORRECT: Virtual destructor
class Base
{
public:
    Base() = default;
    virtual ~Base() = default;  // ✅ Virtual destructor
    
    virtual void method() = 0;
};

class Derived : public Base
{
    double* data_;
public:
    Derived() : data_(new double[1000]) {}
    virtual ~Derived() { delete[] data_; }  // ✅ Called!
};

Base* ptr = new Derived();
delete ptr;  // ~Derived() called, ~Base() called
```

#### **OpenFOAM Pattern: Using tmp/autoPtr**

```cpp
// ✅ OpenFOAM best practice: use smart pointers
autoPtr<turbulenceModel> model = turbulenceModel::New(mesh);
// Automatically deleted when going out of scope

tmp<volScalarField> tfield = new volScalarField(mesh);
// Reference-counted, safe and efficient

// ✅ If you must use raw pointers (rare in OpenFOAM)
class MyBase
{
public:
    virtual ~MyBase() = default;  // Always virtual
};
```

---

## 3. Object Slicing

### **What** (Definition)

When assigning a derived object to a base object by value, C++ copies only the base portion, "slicing off" the derived data.

### **Why** (Impact)

- **Silent data loss**: Derived class members discarded
- **Incorrect behavior**: Virtual dispatch fails
- **Hard to debug**: No compiler warning, wrong results at runtime

### **How** (Detection & Prevention)

#### **Real OpenFOAM Scenario**

```cpp
// ❌ Silent failure
fvPatchField<scalar> baseField = myCustomField;
// myCustomField's extra data sliced away!
```

#### **Detection Strategies**

```cpp
// 1. Static analysis
class Base { /* ... */ };
class Derived : public Base { int extra_; };

void func(Base b) {}  // ⚠️ Slices if passed Derived

// 2. Runtime checks (debug mode)
assert(sizeof(Derived) > sizeof(Base));  // Derived has more data

// 3. Code review grep
grep -rn "Base.*=" src/ | grep -v "\*"  // Find suspicious assignments
```

#### **Prevention Checklist**

- [ ] **Never pass polymorphic types by value**
- [ ] **Use pointers (`*`) or references (`&`)** for parameters
- [ ] **Mark base classes `final`** if not designed for inheritance
- [ ] **Use `auto&` or `const auto&`** in range-based loops
- [ ] **Prefer OpenFOAM `refPtr`** over raw references

#### **Correct Implementation**

```cpp
// ❌ WRONG: Slicing
void process(fvPatchField<scalar> field)  // By value!
{
    // If passed myCustomField, it's sliced here
}

myCustomField custom;
process(custom);  // Sliced! Custom data lost

// ✅ CORRECT: Use reference
void process(fvPatchField<scalar>& field)  // By reference
{
    // Preserves full type
}

void process(const fvPatchField<scalar>& field)  // Const reference
{
    // Read-only, no slicing
}

// ✅ CORRECT: Use pointer
void process(fvPatchField<scalar>* field)
{
    field->evaluate();  // Virtual dispatch works
}
```

#### **OpenFOAM Example: Patch Field Iteration**

```cpp
// ❌ WRONG: Slicing in loop
for (fvPatchField<scalar> field : patchFields)
{
    // field is a copy! Sliced!
}

// ✅ CORRECT: Reference
for (fvPatchField<scalar>& field : patchFields)
{
    field.evaluate();  // Correct type
}

// ✅ BEST: OpenFOAM forEach
forAll(patchFields, i)
{
    auto& field = patchFields[i];
    field.evaluate();
}

// ✅ Using OpenFOAM's refPtr
refPtr<volScalarField> fieldPtr = ...;
if (fieldPtr.valid())
{
    fieldRef().evaluate();  // Safe access
}
```

---

## 4. RTS (Run-Time Selection) Type Not Found

### **What** (Definition)

When OpenFOAM cannot find a runtime-selectable type (turbulence model, boundary condition, etc.) at runtime.

### **Why** (Impact)

- **Application crash**: Before solving begins
- **Frustration**: Silent failures due to linking issues
- **Common issue**: #1 error for custom OpenFOAM development

### **How** (Detection & Prevention)

#### **Real OpenFOAM Error Messages**

```
--> FOAM FATAL ERROR:
Unknown turbulenceModel type kEpsilonMyModel

Valid turbulenceModel types:
  13 ( kEpsilon kOmega kOmegaSST ... )
```

```
request for fvPatchField<scalar> myFixedValue
    while constructing boundary foo
Unknown patch type myFixedValue
```

#### **Root Cause Detection**

```bash
# 1. Check if symbol exists in library
nm -D libmyCustomTurbulence.so | grep myModel

# 2. Verify RTS macro is present
grep -n "addToRunTimeSelectionTable" myModel.C

# 3. Check library linking
ldd ./mySolver | grep myCustom

# 4. Verify controlDict spelling
cat constant/turbulenceProperties | grep "type"
```

#### **Prevention Checklist**

- [ ] **Register with `addToRunTimeSelectionTable`** in `.C` file (not `.H`)
- [ ] **Spelling must match** dictionary type exactly
- [ ] **Link library in `Make/options`**: `-lmyCustomLib`
- [ ] **Library must be in `$FOAM_USER_LIBBIN`** or `$FOAM_LIBBIN`
- [ ] **Check `ldd` output** to verify runtime linking
- [ ] **Recompile after changes**: `wclean && wmake`

#### **Complete Implementation Pattern**

```cpp
// ========== myModel.H ==========
#ifndef myModel_H
#define myModel_H

#include "turbulenceModel.H"

namespace Foam
{
class myModel
:
    public turbulenceModel
{
public:
    TypeName("myModel");  // ✅ Must match dictionary type
    
    // Constructor
    myModel
    (
        const geometricSurfaceField& alpha,
        const surfaceField& rho,
        const surfaceField& U,
        const surfaceField& alphaRhoPhi,
        const surfaceField& phi,
        const transportModel& transport
    );
    
    // Destructor
    virtual ~myModel() = default;
    
    // Required interface
    virtual tmp<volSymmTensorField> R() const override;
    virtual tmp<volScalarField> k() const override;
    virtual tmp<volScalarField> epsilon() const override;
    virtual void correct() override;
};

} // End namespace Foam

#endif

// ========== myModel.C ==========
#include "myModel.H"

// ✅ RTS Registration (IN .C FILE, NOT .H!)
addToRunTimeSelectionTable
(
    turbulenceModel,
    myModel,
    dictionary
)

// Constructor
Foam::myModel::myModel
(
    const geometricSurfaceField& alpha,
    const surfaceField& rho,
    const surfaceField& U,
    const surfaceField& alphaRhoPhi,
    const surfaceField& phi,
    const transportModel& transport
)
:
    turbulenceModel(alpha, rho, U, alphaRhoPhi, phi, transport)
{}

// Implementation
void Foam::myModel::correct()
{
    // Your model implementation
}

// ========== Make/options ==========
EXE_INC = \
    -I$(LIB_SRC)/TurbulenceModels/turbulenceModels/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I../myModel

LIB_LIBS = \
    -lturbulenceModels \
    -lmyCustomLib  // ✅ Link your library

// ========== constant/turbulenceProperties ==========
simulationType  RAS;

RAS
{
    RASModel        myModel;  // ✅ Must match TypeName exactly
    
    myModelCoeffs
    {
        // Your coefficients
    }
}
```

#### **Debugging RTS Issues**

```bash
# 1. Check what's registered
./mySolver -listTurbulenceModels

# 2. Verbose library loading
export FOAM_ABORT=1
./mySolver 2>&1 | grep -i "myModel"

# 3. Examine library contents
nm -C libmyCustom.so | grep "myModel::"

# 4. Test instantiation manually
# In your code, before New():
Info << "Available types:" << nl;
wordListConstructorTable::iterator iter =
    wordListConstructorTablePtr_->begin();
for (; iter != wordListConstructorTablePtr_->end(); ++iter)
{
    Info << "  " << iter()->keyword << nl;
}
```

---

## 5. Calling Virtual Methods in Constructors

### **What** (Definition)

Calling a virtual method in a base class constructor invokes the base class version, not the derived override.

### **Why** (Impact)

- **Incorrect initialization**: Derived method never called
- **Confusing behavior**: Violates OOP expectations
- **Subtle bugs**: May appear to work until you override the method

### **How** (Detection & Prevention)

#### **Real OpenFOAM Pattern**

```cpp
// Base class in OpenFOAM often has this pattern
template<class Type>
class GeometricField
{
public:
    GeometricField(const IOobject& io)
    :
        IOobject(io)
    {
        // ⚠️ If this were virtual, derived version not called!
        readIfModified();  
    }
};
```

#### **Detection Strategies**

```cpp
// 1. Code review: check constructors for virtual calls
class Base
{
public:
    Base() { virtualMethod(); }  // ⚠️ Flag this
};

// 2. Runtime check
class Base
{
protected:
    bool constructed_ = false;
public:
    Base() 
    { 
        constructed_ = true;
        virtualMethod();  
    }
};

class Derived : public Base
{
    void virtualMethod() override
    {
        assert(constructed_ && "Called from constructor!");
    }
};

// 3. Use clang-tidy
// .clang-tidy: Checks: modernize-use-override
```

#### **Prevention Checklist**

- [ ] **Never call virtual methods** in constructors/destructors
- [ ] **Use two-phase initialization**: construct then `init()`
- [ ] **Mark constructors `final`** if inheritance not intended
- [ ] **Document initialization order** in header comments
- [ ] **Use `override` keyword** to catch signature mismatches

#### **Correct Implementation**

```cpp
// ❌ WRONG: Virtual in constructor
class Base
{
public:
    Base()
    {
        calculate();  // ⚠️ Calls Base::calculate, not Derived!
    }
    
    virtual void calculate()
    {
        // Default implementation
    }
};

class Derived : public Base
{
    double data_;
public:
    void calculate() override
    {
        data_ = 42.0;  // Never called!
    }
};

Derived d;  // data_ uninitialized!

// ✅ CORRECT: Two-phase initialization
class Base
{
public:
    Base() = default;
    
    virtual void calculate()
    {
        // Default
    }
    
    void initialize()
    {
        calculate();  // ✅ Calls correct version
    }
};

class Derived : public Base
{
    double data_ = 0.0;
public:
    void calculate() override
    {
        data_ = 42.0;  // ✅ Called!
    }
};

Derived d;
d.initialize();  // ✅ Proper two-phase init
```

#### **OpenFOAM Example: Boundary Condition Initialization**

```cpp
// ✅ OpenFOAM pattern: Separate construction from initialization
class myFixedValueFvPatchField
:
    public fvPatchField<vector>
{
private:
    scalar myParam_;
    
public:
    // Constructor - minimal initialization
    myFixedValueFvPatchField
    (
        const fvPatch& p,
        const DimensionedField<vector, volMesh>& iDF
    )
    :
        fvPatchField<vector>(p, iDF),
        myParam_(0.0)  // ✅ Initialize, don't call virtual methods
    {}
    
    // Virtual method called by OpenFOAM AFTER construction
    virtual void updateCoeffs() override
    {
        if (updated()) return;
        
        // ✅ Safe: object fully constructed now
        myParam_ = calculateParam();
        
        fvPatchField<vector>::operator==(this->patchInternalField());
    }
};
```

---

## 6. Covariant Return Type Confusion

### **What** (Definition)

C++ allows derived classes to override virtual functions with covariant return types (derived pointer instead of base pointer), but this has limitations.

### **Why** (Impact)

- **Inconsistent interface**: Sometimes returns Base*, sometimes Derived*
- **Unexpected slicing**: If used incorrectly
- **Template conflicts**: Doesn't work with smart pointers

### **How** (Detection & Prevention)

#### **Real OpenFOAM Example**

```cpp
// ✅ OpenFOAM uses covariant returns
class fvPatchField<Type>
{
public:
    virtual autoPtr<fvPatchField<Type>> clone() const;
};

class myFixedValueFvPatchField
:
    public fvPatchField<scalar>
{
public:
    // ✅ Covariant: returns derived type
    virtual autoPtr<myFixedValueFvPatchField> clone() const;
};
```

#### **Detection & Rules**

```cpp
// ✅ ALLOWED: Pointer covariancy
class Base { virtual Base* clone(); };
class Derived : public Base 
{ 
    virtual Derived* clone() override;  // ✅ OK
};

// ❌ NOT ALLOWED: Smart pointer covariancy
class Base { virtual autoPtr<Base> clone(); };
class Derived : public Base 
{ 
    virtual autoPtr<Derived> clone() override;  // ❌ Error
};

// ✅ OpenFOAM workaround
class Base { virtual tmp<Base> clone() const; };
// Uses tmp<T>, not autoPtr
```

#### **Prevention Checklist**

- [ ] **Covariant returns work with raw pointers only**
- [ ] **Does NOT work with smart pointers** (`autoPtr`, `unique_ptr`)
- [ ] **Return type must be derived-to-base** relationship
- [ ] **Consider using `auto`** in calling code
- [ ] **Prefer OpenFOAM `tmp<T>`** for covariant cloning

#### **Correct Implementation**

```cpp
// ✅ CORRECT: Raw pointer covariancy
class Patch
{
public:
    virtual Patch* clone() const = 0;
};

class MyPatch : public Patch
{
public:
    virtual MyPatch* clone() const override  // ✅ Covariant
    {
        return new MyPatch(*this);
    }
};

// Usage
Patch* base = new MyPatch();
Patch* cloned = base->clone();  // Returns MyPatch*, stored as Patch*

// ✅ CORRECT: OpenFOAM tmp<T> pattern
class fvPatchField<Type>
{
public:
    virtual tmp<fvPatchField<Type>> clone() const
    {
        return tmp<fvPatchField<Type>>
        (
            new fvPatchField<Type>(*this)
        );
    }
};

class myPatchField : public fvPatchField<scalar>
{
public:
    virtual tmp<fvPatchField<scalar>> clone() const override
    {
        return tmp<fvPatchField<scalar>>
        (
            new myPatchField(*this)  // ✅ Returns derived, typed as base
        );
    }
};

// ❌ WRONG: Smart pointer covariancy
class Base
{
public:
    virtual std::unique_ptr<Base> clone() const = 0;
};

class Derived : public Base
{
public:
    virtual std::unique_ptr<Derived> clone() const override  // ❌ Error!
    {
        return std::make_unique<Derived>(*this);
    }
};
```

---

## 7. Advanced Debugging Tools

### **What** (Available Tools)

OpenFOAM and Linux provide powerful debugging tools for template and inheritance issues.

### **GDB (GNU Debugger)**

#### **Basic Usage**

```bash
# Compile with debug symbols
export WM_COMPILE_OPTION=Debug
wclean && wmake

# Run with gdb
gdb --args ./mySolver -parallel

# Common GDB commands
(gdb) run                          # Start execution
(gdb) backtrace                    # Show call stack after crash
(gdb) frame 3                      # Jump to stack frame 3
(gdb) print variableName           # Show value
(gdb) print *this                  # Show current object
(gdb) call obj.virtualMethod()     # Test virtual dispatch
(gdb) info vtbl obj                # Show vtable layout
(gdb) break myClass::myMethod      # Set breakpoint
(gdb) continue                     # Continue to breakpoint
(gdb) step                         # Step into function
(gdb) next                         # Step over function
```

#### **GDB Example: Debugging Virtual Dispatch**

```bash
# 1. Start GDB
gdb ./mySolver

# 2. Set breakpoint on virtual method
(gdb) break turbulenceModel::correct

# 3. Run
(gdb) run

# 4. When stopped, examine vtable
(gdb) print *this
(gdb) info vtbl *this

# 5. See which function actually called
(gdb) backtrace
```

### **Valgrind (Memory Debugger)**

```bash
# Memory leak check
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --log-file=valgrind.log \
         ./mySolver

# Check for undefined behavior
valgrind --tool=memcheck \
         --undef-value-errors=yes \
         ./mySolver

# Cache profiling
valgrind --tool=cachegrind ./mySolver
cg_annotate cachegrind.out.<pid>
```

#### **Valgrind Output Analysis**

```
==12345== Invalid read of size 8
==12345==    at 0x123456: MyClass::virtualMethod() (myClass.C:42)
==12345==  Address 0x456789 is 8 bytes inside a block of size 16 free'd
==12345==    at 0x789ABC: operator delete(void*)

🔍 Analysis: Use-after-free - object deleted but still accessed
```

```
==12345== 16 bytes in 1 blocks are definitely lost
==12345==    loss record 1 of 5
==12345==    at 0xABCDEF: operator new(unsigned long)

🔍 Analysis: Memory leak - likely missing virtual destructor
```

### **Compiler Sanitizers (Faster than Valgrind)**

```bash
# Address Sanitizer (detects memory errors)
export CXXFLAGS="-fsanitize=address -fno-omit-frame-pointer -g"
export LDFLAGS="-fsanitize=address"
wclean && wmake

./mySolver  # Automatically runs ASan

# Undefined Behavior Sanitizer
export CXXFLAGS="-fsanitize=undefined -g"
wclean && wmake

# Thread Sanitizer (for parallel code)
export CXXFLAGS="-fsanitize=thread -g"
wclean && wmake
```

#### **Sanitizer Output**

```
mySolver: runtime error: member access within null pointer
#0 in MyClass::method() myClass.C:42

🔍 Analysis: Null pointer dereference
```

```
mySolver: runtime error: load of value 42, which is not a valid value
#0 in BaseClass::virtualMethod() baseClass.C:10

🔍 Analysis: Reading uninitialized memory
```

### **Compiler Warnings as Errors**

```bash
# Force all warnings to be errors
export WM_COMPILE_CONTROL="+Werror"

# Specific warning flags
export CXXFLAGS="-Wall -Wextra -Wold-style-cast -Woverloaded-virtual"

# Check for missing virtual destructors
export CXXFLAGS="-Wnon-virtual-dtor"

# Clang-specific checks (if using clang)
export CXXFLAGS="-Wclang-abi-compat"
```

### **Template Instantiation Debugging**

```bash
# 1. View instantiated templates
./mySolver -dry-run 2>&1 | grep "instantiating"

# 2. Force explicit instantiation
# In your .C file:
template class myClass<scalar>;
template class myClass<vector>;

# 3. Check symbol table
nm -C myLibrary.o | grep "myClass<"

# 4. Template backtrace (when compilation fails)
# Add to compiler flags:
export CXXFLAGS="-ftemplate-backtrace-limit=0"
```

---

## 🧠 Prevention Summary

### **Before You Code**

- [ ] **Plan inheritance hierarchy**: Identify abstract vs. concrete classes
- [ ] **Use `override` keyword**: On all virtual function overrides
- [ ] **Declare virtual destructors**: In all polymorphic base classes
- [ ] **Document interface contracts**: What must derived classes implement?

### **During Development**

- [ ] **Compile with warnings**: `-Wall -Wextra -Werror`
- [ ] **Use references not values**: For polymorphic parameters
- [ ] **Test with `-dry-run`**: Verify RTS registration
- [ ] **Run valgrind regularly**: Catch leaks early

### **Before Commit**

- [ ] **Run sanitizers**: ASan, UBSan
- [ ] **Check vtable completeness**: `nm -C` for undefined symbols
- [ ] **Verify linking**: `ldd ./mySolver`
- [ ] **Test boundary conditions**: Custom patches with different patch types

### **Runtime Monitoring**

- [ ] **Enable debug output**: `-debug` flag for verbose logging
- [ ] **Profile performance**: Use `Profiling` class
- [ ] **Monitor memory**: `/usr/bin/time -v ./mySolver`

---

## 🎯 Key Takeaways

### **Critical Patterns**

| Pattern | Rule | OpenFOAM Example |
|---------|------|------------------|
| **Pure Virtual** | Implement all in derived | `turbulenceModel::correct()` |
| **Destructor** | Always `virtual ~Base()` | `fvPatchField` base class |
| **Slicing** | Use `&` or `*`, never value | `for (auto& field : fields)` |
| **RTS** | Register in `.C`, link library | `addToRunTimeSelectionTable` |
| **Constructor** | No virtual calls | Two-phase: `ctor` then `init()` |
| **Covariant** | Raw pointers only | `clone()` returns `autoPtr<Base>` |

### **Debugging Workflow**

```
1. Compiler errors → Read template instantiation backtrace
2. Linker errors → Check vtable symbols with nm
3. Runtime crashes → Use gdb backtrace
4. Memory leaks → Run valgrind or ASan
5. RTS failures → Verify registration + linking
6. Wrong behavior → Check for slicing, virtual in ctor
```

### **Best Practices**

✅ **DO:**
- Always use `virtual ~Base()` in polymorphic classes
- Use `override` on all virtual function overrides
- Pass polymorphic types by `const&` or `*`
- Register RTS in `.C` file, link in `Make/options`
- Initialize in two phases if virtual methods needed
- Run with sanitizers in debug mode

❌ **DON'T:**
- Call virtual methods in constructors/destructors
- Pass derived objects by value to base parameters
- Forget to implement pure virtual functions
- Misspell dictionary types (must match `TypeName`)
- Use `autoPtr<Derived>` return with covariant override
- Ignore compiler warnings (they often catch these bugs!)

---

## 📚 Practice Exercise

### **Debug Challenge**

Given this broken OpenFOAM boundary condition:

```cpp
class myBrokenPatch
:
    public fvPatchField<scalar>
{
private:
    scalar* data_;
    
public:
    myBrokenPatch(const fvPatch& p, const DimensionedField<scalar, volMesh>& iDF)
    :
        fvPatchField<scalar>(p, iDF)
    {
        calculate();  // ⚠️ Virtual call in constructor
    }
    
    ~myBrokenPatch()
    {
        delete[] data_;  // ⚠️ Missing virtual destructor in base
    }
    
    void updateCoeffs()
    {
        // ⚠️ Missing override check
    }
    
    myBrokenPatch clone() const  // ⚠️ Wrong return type
    {
        return myBrokenPatch(*this);  // ⚠️ Slicing!
    }
};
```

**Tasks:**

1. **Identify** all 5 errors using the prevention checklist
2. **Fix** each error with correct OpenFOAM patterns
3. **Verify** with compiler warnings and valgrind
4. **Test** with `wmake` and runtime execution

<details>
<summary><b>🔍 Solution (Click to reveal)</b></summary>

```cpp
class myFixedPatch
:
    public fvPatchField<scalar>
{
private:
    scalarField data_;  // ✅ Use OpenFOAM field, not raw pointer
    
public:
    // ✅ Constructor: minimal initialization
    myFixedPatch(const fvPatch& p, const DimensionedField<scalar, volMesh>& iDF)
    :
        fvPatchField<scalar>(p, iDF),
        data_(this->size(), 0.0)  // ✅ Initialize, no virtual calls
    {}
    
    // ✅ Destructor: default (base has virtual destructor)
    virtual ~myFixedPatch() = default;
    
    // ✅ Override: correct keyword and signature
    virtual void updateCoeffs() override
    {
        if (updated()) return;
        
        // Your physics here
        fvPatchField<scalar>::operator==(data_);
    }
    
    // ✅ Clone: correct return type (autoPtr, not by value)
    virtual autoPtr<fvPatchField<scalar>> clone() const override
    {
        return autoPtr<fvPatchField<scalar>>
        (
            new myFixedPatch(*this)  // ✅ Heap allocation
        );
    }
};

// ✅ RTS registration in .C file
addToRunTimeSelectionTable
(
    fvPatchField<scalar>,
    myFixedPatch,
    patch
)
```

</details>

---

## 📖 Further Reading

### **OpenFOAM Documentation**

- **Base Classes:** `$FOAM_SRC/finiteVolume/fields/fvPatchFields`
- **RTS System:** Programmer's Guide, Chapter 3
- **Memory Management:** `$FOAM_SRC/OpenFOAM/memory`
- **Debugging:** User Guide, Section 4.5

### **Related Documentation**

- **📘 Interface Design:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md)
- **📗 Inheritance Hierarchies:** [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md)
- **📙 Run-Time Selection:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md)
- **📕 Design Patterns:** [05_Design_Patterns_in_Physics.md](05_Design_Patterns_in_Physics.md)
- **📔 Overview:** [00_Overview.md](00_Overview.md)
- **📓 Practical Exercise:** [07_Practical_Exercise.md](07_Practical_Exercise.md)

---

**Last Updated:** 2025-12-31  
**OpenFOAM Version:** v10+  
**Author:** OpenFOAM C++ Template Programming Curriculum