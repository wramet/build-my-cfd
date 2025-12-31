# Compilation Process

กระบวนการ Compile

---

## 🎯 Learning Objectives

**What will you learn?**
- Understand the wmake build system and its role in OpenFOAM development
- Configure directory structure and Make files for successful compilation
- Distinguish between compiling applications and shared libraries
- Apply different compilation modes (Debug vs. Optimized)
- Troubleshoot common compilation issues systematically

**Why is this important?**
- Compilation is the essential bridge between writing code and executing simulations
- Proper build configuration ensures efficient development workflow and reproducible results
- Understanding compilation mechanics enables effective debugging and optimization
- Mastering wmake is fundamental for OpenFOAM development and customization

**How will you apply this?**
- Set up correct directory structures for new OpenFOAM projects
- Configure Make/files and Make/options for specific compilation needs
- Execute appropriate build commands for different scenarios
- Switch between debug and optimized builds as needed
- Resolve compilation errors using systematic troubleshooting approaches

---

## 📋 Prerequisites

- Basic understanding of C++ compilation process
- Familiarity with command line interface
- Knowledge of OpenFOAM directory structure ([covered in Module 02](../../MODULE_02_OPENFOAM_FUNDAMENTALS/CONTENT/01_OPENFOAM_ARCHITECTURE/00_Overview.md))
- Understanding of Linux environment variables

---

## Overview

OpenFOAM uses the **wmake** build system, a specialized compilation framework designed for:
- **Complex dependency management**: Automatically handles header file dependencies
- **Cross-platform compilation**: Ensures consistency across different systems
- **Incremental builds**: Compiles only modified files for faster development
- **Library linking**: Simplifies linking against OpenFOAM and external libraries

---

## 1. Directory Structure

### What You Need

Every OpenFOAM compilation target requires a specific directory organization:

```
myProject/
├── Make/
│   ├── files      # Source files to compile
│   └── options    # Compiler flags and library links
├── myModel.H      # Header file
├── myModel.C      # Source implementation
└── myModelI.H     # Optional inline functions
```

### Why This Structure?

- **Make/**: Standard directory recognized by wmake
- **files**: Lists all source files requiring compilation
- **options**: Specifies include paths and library dependencies
- **.H/.C separation**: Follows C++ convention for declaration vs. implementation

### How to Organize

1. Create project directory: `mkdir myProject && cd myProject`
2. Create Make subdirectory: `mkdir Make`
3. Place source files in project root
4. Create files and options in Make/ directory

---

## 2. Make/files Configuration

### What Is This File?

The `Make/files` file specifies:
- **Source files**: Which `.C` files to compile
- **Target type**: Library (LIB) or executable (EXE)
- **Output location**: Where to place the compiled binary

### Example Configuration

```make
# Source files to compile
myModel.C
anotherClass.C

# Target specification (choose ONE)

# For library:
LIB = $(FOAM_USER_LIBBIN)/libmyModel

# For application:
EXE = $(FOAM_USER_APPBIN)/mySolver
```

### Why Different Targets?

| Target Type | Use Case | Output Location |
|-------------|----------|-----------------|
| **LIB** | Reusable code components | `$FOAM_USER_LIBBIN/libmyModel.so` |
| **EXE** | Standalone solver/utility | `$FOAM_USER_APPBIN/mySolver` |

### How to Choose?

- **Use LIB** when:
  - Creating functionality for multiple solvers
  - Developing boundary conditions, turbulence models
  - Building utility libraries
- **Use EXE** when:
  - Creating standalone solvers
  - Developing utilities with main() function
  - Building end-user applications

---

## 3. Make/options Configuration

### What Is This File?

The `Make/options` file defines:
- **EXE_INC**: Include paths for header files
- **EXE_LIBS**: Libraries to link against
- **Compilation flags**: Optimization, debugging options

### Example Configuration

```make
# Include paths (where to find .H files)
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/basic/lnInclude

# Libraries to link (what .so files to use)
EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lthermophysicalModels
```

### Why Include Both?

- **EXE_INC**: Compiler needs to find declarations during compilation
- **EXE_LIBS**: Linker needs to find implementations during linking
- Missing either causes compilation or linking errors

### How to Determine Dependencies?

1. Check which classes you use in your code
2. Find their location: `find $FOAM_SRC -name className.H`
3. Add include path to EXE_INC
4. Add library link to EXE_LIBS (usually same name as directory)

---

## 4. How wmake Works Internally

### What Happens During Compilation?

```
┌─────────────────────────────────────────────────────────────┐
│                    wmake Execution Process                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Parse Make/files                                         │
│     ├─ Identify source files (.C)                           │
│     ├─ Determine target type (LIB/EXE)                      │
│     └─ Set output directory                                 │
│           ↓                                                 │
│  2. Parse Make/options                                       │
│     ├─ Collect include paths (EXE_INC)                      │
│     ├─ Collect library links (EXE_LIBS)                     │
│     └─ Apply compiler flags                                 │
│           ↓                                                 │
│  3. Generate Dependencies                                     │
│     ├─ Scan #include directives                             │
│     ├─ Build dependency tree                                │
│     └─ Create .dep files                                    │
│           ↓                                                 │
│  4. Compilation Phase                                        │
│     ├─ Compile each .C → .o (object file)                   │
│     ├─ Use dependency information                           │
│     └─ Compile only modified files (incremental)            │
│           ↓                                                 │
│  5. Linking Phase                                            │
│     ├─ LIB: Create .so (shared library)                     │
│     ├─ EXE: Create executable with main()                   │
│     └─ Link against EXE_LIBS                                │
│           ↓                                                 │
│  6. Output                                                   │
│     └─ Binary placed in target directory                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Why This Multi-Stage Process?

1. **Dependency management**: Ensures correct compilation order
2. **Incremental builds**: Saves time by recompiling only changed files
3. **Modularity**: Separates compilation and linking concerns
4. **Flexibility**: Allows mixing of libraries and executables

### How Dependency Tracking Works

```bash
# wmake creates .dep files alongside source files
myModel.C    → myModel.dep (tracks header dependencies)
myModel.C    → myModel.o   (compiled object file)
```

When a header file changes:
- wmake reads corresponding .dep file
- Identifies which source files depend on changed header
- Recompiles only affected source files

---

## 5. Build Commands

### Common Compilation Scenarios

| Scenario | Command | Output |
|----------|---------|--------|
| **Standard build** | `wmake` | Executable in `$FOAM_USER_APPBIN` |
| **Shared library** | `wmake libso` | Library in `$FOAM_USER_LIBBIN` |
| **Clean build** | `wclean` | Removes all compiled files |
| **Force rebuild** | `wclean && wmake` | Complete recompilation |
| **Parallel build** | `wmake -j 4` | Uses 4 CPU cores |
| **Verbose output** | `wmake | tee build.log` | Saves compilation log |

### Why Use Different Commands?

- **wmake**: Default for executables, reads EXE from Make/files
- **wmake libso**: Explicitly builds shared library
- **wclean**: Removes object files and dependencies before rebuild
- **Parallel builds**: Significantly reduces compilation time on multi-core systems

### How to Use Effectively?

```bash
# First time compilation
wmake

# After modifying source files
wmake  # Incremental build (fast)

# After modifying headers
wmake  # Automatic dependency tracking

# Complete rebuild (troubleshooting)
wclean && wmake

# Production build (use all cores)
wmake -j
```

---

## 6. Debug vs Optimized Compilation

### What's the Difference?

| Feature | Debug Mode | Optimized Mode |
|---------|------------|----------------|
| **Compilation flags** | `-g -O0 -fdef-population` | `-O3 -DNDEBUG` |
| **Symbol information** | Full debugging symbols | Minimal symbols |
| **Optimization** | Disabled (fast compilation) | Maximum optimization |
| **Assertions** | Enabled | Disabled |
| **Use case** | Development, debugging | Production simulations |
| **Performance** | Slow execution | Fast execution |
| **File size** | Larger | Smaller |

### Why Switch Modes?

- **Debug mode**:
  - Essential during development
  - Enables use of debuggers (gdb, valgrind)
  - Preserves line number information for error tracking
  - Includes runtime assertions for error detection
  
- **Optimized mode**:
  - Critical for production runs
  - Significantly faster execution (2-10x speedup)
  - Smaller memory footprint
  - Suitable for parameter studies and large simulations

### How to Switch Modes?

```bash
# Check current mode
echo $WM_COMPILE_OPTION

# Switch to Debug mode
export WM_COMPILE_OPTION=Debug
wclean && wmake

# Switch to Optimized mode
export WM_COMPILE_OPTION=Opt
wclean && wmake

# Permanent setting (add to ~/.bashrc)
echo "export WM_COMPILE_OPTION=Debug" >> ~/.bashrc
source ~/.bashrc
```

---

## 7. Troubleshooting Compilation Issues

### Common Error Types and Solutions

#### A. Header File Not Found

**Error:**
```
fatal error: fvMesh.H: No such file or directory
```

**Solution:**
1. Identify missing header location:
   ```bash
   find $FOAM_SRC -name "fvMesh.H"
   ```
2. Add include path to Make/options:
   ```make
   EXE_INC = -I$(LIB_SRC)/finiteVolume/lnInclude
   ```

#### B. Undefined Reference

**Error:**
```
undefined reference to `Foam::fvMesh::fvMesh()`
```

**Solution:**
1. Add missing library to Make/options:
   ```make
   EXE_LIBS = -lfiniteVolume
   ```

#### C. Wrong Target Type

**Error:**
```
wmake error: target must be specified as LIB or EXE
```

**Solution:**
- Ensure Make/files contains exactly ONE of:
  - `LIB = $(FOAM_USER_LIBBIN)/libName` for libraries
  - `EXE = $(FOAM_USER_APPBIN)/exeName` for executables

### Troubleshooting Flowchart

```
                    Compilation Error?
                          │
                          ▼
                ┌─────────────────────┐
                │ Check error message  │
                └─────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Header   │    │ Linking  │    │ Syntax   │
    │ not found│    │ error    │    │ error    │
    └──────────┘    └──────────┘    └──────────┘
          │               │               │
          ▼               ▼               ▼
    Add include     Add library    Fix syntax in
    path to         link to        source file
    EXE_INC         EXE_LIBS
          │               │               │
          └───────────────┴───────────────┘
                          │
                          ▼
                  Run `wclean && wmake`
                          │
                    ┌─────┴─────┐
                    │           │
                  Success?    Still fails?
                    │           │
                    ▼           ▼
                  Done     Check log file
                          `wmake > log 2>&1`
                          Search specific error
```

### How to Get Detailed Error Information?

```bash
# Capture full compilation output
wmake 2>&1 | tee compilation.log

# Search for specific errors
grep "error:" compilation.log

# Show wmake dependency information
wmake -h  # Display help and environment

# Check environment variables
wmake -show-compile-c
wmake -show-link-c
```

---

## 8. Best Practices

### Development Workflow

1. **Initial Setup**:
   ```bash
   export WM_COMPILE_OPTION=Debug
   ```

2. **During Development**:
   ```bash
   wmake  # Incremental builds
   ```

3. **Testing Phase**:
   ```bash
   wclean && wmake  # Clean build
   ```

4. **Production**:
   ```bash
   export WM_COMPILE_OPTION=Opt
   wclean && wmake
   ```

### Organization Tips

- **Separate concerns**: One target per directory
- **Clear naming**: Use descriptive library/executable names
- **Document dependencies**: Comment complex Make/options entries
- **Version control**: Commit Make/ directory along with source

---

## 📚 Quick Reference

### Essential Commands

| Task | Command | Notes |
|------|---------|-------|
| **Build executable** | `wmake` | Reads EXE from Make/files |
| **Build library** | `wmake libso` | Creates .so file |
| **Clean build** | `wclean` | Removes compiled files |
| **Force rebuild** | `wclean && wmake` | Complete recompilation |
| **Parallel build** | `wmake -j N` | Use N CPU cores |
| **Debug mode** | `export WM_COMPILE_OPTION=Debug` | Add symbols, no optimization |
| **Optimized mode** | `export WM_COMPILE_OPTION=Opt` | Full optimization |

### Make/files Structure

```make
# Source files (one per line)
file1.C
file2.C

# Target (EXACTLY ONE required)
LIB = $(FOAM_USER_LIBBIN)/libName    # For libraries
EXE = $(FOAM_USER_APPBIN)/exeName    # For executables
```

### Make/options Structure

```make
EXE_INC = \
    -I/path/to/includes1 \
    -I/path/to/includes2

EXE_LIBS = \
    -llibrary1 \
    -llibrary2
```

---

## 🎯 Key Takeaways

- **wmake is the heart of OpenFOAM compilation**: It handles dependencies, compilation, and linking in an integrated system
- **Make/ directory is essential**: Both `files` and `options` files are required for successful compilation
- **Target type matters**: LIB for reusable libraries, EXE for standalone applications
- **Include paths enable compilation**: EXE_INC tells compiler where to find header declarations
- **Library links enable linking**: EXE_LIBS tells linker where to find implementations
- **Debug mode for development**: Use Debug when developing and testing code
- **Optimized mode for production**: Use Opt for actual simulations requiring performance
- **Clean before switching modes**: Always run `wclean` when changing compilation options
- **Parallel builds save time**: Use `wmake -j` on multi-core systems
- **Dependency tracking is automatic**: wmake handles incremental builds intelligently
- **Error messages guide fixes**: Read compilation errors carefully to identify missing includes or libraries
- **Environment variables control behavior**: `WM_COMPILE_OPTION` affects all OpenFOAM compilations

---

## 🧠 Concept Check

<details>
<summary><b>1. What goes in Make/files?</b><br>Make/files ใส่อะไร?</summary>

**Answer:** Source files (.C files) and target specification (LIB or EXE)
<br><br>
**คำตอบ:** ไฟล์ซอร์สโค้ด (.C) และการระบุเป้าหมาย (LIB หรือ EXE)
</details>

<details>
<summary><b>2. What goes in Make/options?</b><br>Make/options ใส่อะไร?</summary>

**Answer:** Include paths (EXE_INC) for headers and library links (EXE_LIBS)
<br><br>
**คำตอบ:** เส้นทางการค้นหาไฟล์ header (EXE_INC) และการเชื่อมโยงไลบรารี (EXE_LIBS)
</details>

<details>
<summary><b>3. How does wmake libso differ from wmake?</b><br>wmake libso ต่างจาก wmake อย่างไร?</summary>

**Answer:** wmake libso builds a shared library (.so file), while wmake builds an executable
<br><br>
**คำตอบ:** wmake libso สร้าง shared library (.so) ส่วน wmake สร้าง executable
</details>

<details>
<summary><b>4. Why use Debug mode during development?</b><br>ทำไมต้องใช้ Debug mode ขณะพัฒนาโปรแกรม?</summary>

**Answer:** Debug mode includes debugging symbols and disables optimization, making errors easier to trace with tools like gdb
<br><br>
**คำตอบ:** Debug mode มีสัญลักษณ์ดีบักและปิดการ优化 ทำให้ตรวจสอบข้อผิดพลาดได้ง่ายด้วย gdb หรือเครื่องมืออื่นๆ
</details>

<details>
<summary><b>5. What is the purpose of wclean?</b><br>wclean มีไว้เพื่ออะไร?</summary>

**Answer:** wclean removes all compiled object files and dependencies, forcing a complete rebuild on next wmake
<br><br>
**คำตอบ:** wclean ลบไฟล์ object และ dependencies ทั้งหมด เพื่อบังคับให้คอมไพล์ใหม่ทั้งหมดเมื่อรัน wmake ครั้งถัดไป
</details>

---

## 📖 Related Documentation

### Within This Module

- **Overview:** [00_Overview.md](00_Overview.md) - Module structure and learning path
- **Project Setup:** [01_Project_Overview.md](01_Project_Overview.md) - Practical project organization
- **Code Structure:** [02_Code_Structure.md](02_Code_Structure.md) - Header and source file organization
- **Runtime Selection:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md) - How compiled models are loaded
- **Common Errors:** [07_Common_Errors_and_Debugging.md](07_Common_Errors_and_Debugging.md) - Detailed troubleshooting guide

### Cross-Module References

- **OpenFOAM Architecture:** [Module 02 - OpenFOAM Fundamentals](../../MODULE_02_OPENFOAM_FUNDAMENTALS/CONTENT/01_OPENFOAM_ARCHITECTURE/00_Overview.md) - Directory structure and environment
- **C++ Compilation:** [Module 02 - Programming Fundamentals](../../MODULE_02_OPENFOAM_FUNDAMENTALS/CONTENT/02_PROGRAMMING_FUNDAMENTALS/00_Overview.md) - Basic compilation concepts
- **Debugging Tools:** [Module 08 - Testing and Validation](../../MODULE_08_TESTING_VALIDATION/CONTENT/03_TEST_FRAMEWORK_CODING/03_Automation_Scripts.md) - Testing compiled code

---

## 🔗 External Resources

- **OpenFOAM Source Code:** [GitHub Repository](https://github.com/OpenFOAM/OpenFOAM-dev) - Study existing wmake implementations
- **wmake Documentation:** [OpenFOAM User Guide](https://cfd.direct/openfoam/user-guide/) - Official compilation guidelines
- **C++ Compilation:** [GCC Documentation](https://gcc.gnu.org/onlinedocs/) - Compiler flag reference