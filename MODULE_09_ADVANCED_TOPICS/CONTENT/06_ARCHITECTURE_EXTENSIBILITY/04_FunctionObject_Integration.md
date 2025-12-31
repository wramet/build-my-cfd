# Function Object Integration

**Complete Integration of Custom Function Objects into OpenFOAM Solvers**

---

## 🎯 Learning Objectives

By the end of this section, you will be able to:

- **Design and implement** custom function objects that integrate seamlessly with OpenFOAM solver loops
- **Configure** solver execution control through `execute()` and `write()` methods appropriately
- **Access and process** mesh fields and database objects during runtime
- **Register and load** custom function objects through dynamic libraries
- **Leverage built-in function objects** for common post-processing tasks
- **Debug and verify** function object behavior in practical solver scenarios

---

## 1. Introduction: Why Function Objects?

### 1.1 Motivation and Benefits

**Function Objects** provide a powerful mechanism for extending solver functionality without modifying core solver code. They serve as **post-processing hooks** that execute at specific points during the solver loop, enabling:

- **Non-intrusive Analysis**: Add monitoring, visualization, and data extraction without recompiling solvers
- **Runtime Configurability**: Enable/disable features through dictionary controls without code changes
- **Modular Design**: Package analysis capabilities as reusable, loadable components
- **Performance Efficiency**: Execute calculations only when needed (time step vs. write time)

### 1.2 When to Use Each Mechanism

| Mechanism | Best Use Case | Execution Frequency |
|-----------|---------------|---------------------|
| **execute()** | Per-time-step calculations, real-time monitoring, convergence tracking | Every solver iteration |
| **write()** | Output file generation, visualization data export, checkpointing | At scheduled write times |
| **read()** | Initialization, parameter validation, field lookup | During construction/reconstruction |
| **end()** | Final statistics, report generation, resource cleanup | At solver termination |

### 1.3 Architecture Overview

Function objects operate within OpenFOAM's **object registry** system:

```
┌─────────────────────────────────────────────────────────────┐
│                    SOLVER LOOP                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Time Loop Iteration                                 │    │
│  │                                                      │    │
│  │  ┌──────────────┐      ┌──────────────┐            │    │
│  │  │  UEqn.solve()│      │  pEqn.solve()│            │    │
│  │  └──────────────┘      └──────────────┘            │    │
│  │         │                      │                     │    │
│  │         └──────────┬───────────┘                     │    │
│  │                    ▼                                │    │
│  │         ┌──────────────────────┐                    │    │
│  │         │  functionObject::    │                    │    │
│  │         │  execute()           │◄─── executeControl │    │
│  │         └──────────────────────┘                    │    │
│  │                    │                                │    │
│  │                    ▼ (at writeTime)                 │    │
│  │         ┌──────────────────────┐                    │    │
│  │         │  functionObject::    │                    │    │
│  │         │  write()             │◄─── writeControl   │    │
│  │         └──────────────────────┘                    │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Object Registry: U, p, T, mesh, customFields...            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Basic Structure and Implementation

### 2.1 Class Definition

```cpp
#ifndef myFunctionObject_H
#define myFunctionObject_H

#include "functionObject.H"
#include "fvMesh.H"

namespace Foam
{

class myFunctionObject
:
    public functionObject
{
    // Private Data
        
        //- Reference to the mesh
        const fvMesh& mesh_;
        
        //- Dictionary parameters
        dictionary dict_;
        
        //- Output file name
        fileName outputFile_;
        
        //- Calculation frequency
        label writeInterval_;


public:

    //- Runtime type information
    TypeName("myFunctionObject");

    // Constructors

        //- Construct from components
        myFunctionObject
        (
            const word& name,
            const Time& runTime,
            const dictionary& dict
        );

    //- Destructor
    virtual ~myFunctionObject() = default;


    // Member Functions

        //- Read the dictionary
        virtual bool read(const dictionary& dict);

        //- Execute called at each time step (based on executeControl)
        virtual bool execute();

        //- Execute called at write time (based on writeControl)
        virtual bool write();

        //- Called at the end of the run
        virtual bool end();
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

#endif
```

### 2.2 Constructor and Initialization

```cpp
#include "myFunctionObject.H"
#include "Time.H"
#include "fvMesh.H"
#include "volFields.H"

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

defineTypeNameAndDebug(myFunctionObject, 0);
addToRunTimeSelectionTable(functionObject, myFunctionObject, dictionary);

// * * * * * * * * * * * * * Private Member Functions  * * * * * * * * * * * //


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

Foam::myFunctionObject::myFunctionObject
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    functionObject(name, runTime),
    mesh_(runTime.lookupObject<fvMesh>(polyMesh::defaultRegion)),
    dict_(dict),
    outputFile_(dict.getOrDefault<fileName>("outputFile", "functionObjectOutput.dat")),
    writeInterval_(dict.getOrDefault<label>("writeInterval", 1))
{
    Info << nl << "Creating " << name << " function object" << nl
         << "  Output file: " << outputFile_ << nl
         << "  Write interval: " << writeInterval_ << nl
         << endl;
        
    // Validate required fields exist
    if (!mesh_.foundObject<volVectorField>("U"))
    {
        WarningInFunction
            << "Velocity field U not found in mesh database" << endl;
    }
}
```

### 2.3 Execute Method Implementation

The `execute()` method is called **every time step** (or per `executeControl` settings):

```cpp
bool Foam::myFunctionObject::execute()
{
    // Access velocity field
    if (!mesh_.foundObject<volVectorField>("U"))
    {
        return false;
    }
    
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    
    // Calculate per-time-step quantities
    scalar maxU = max(mag(U)).value();
    scalar avgU = average(mag(U)).value();
    
    // Get current time
    scalar currentTime = time_.timeOutputValue();
    
    // Real-time monitoring output
    Info << type() << " output:" << nl
         << "  Time = " << currentTime << nl
         << "  Max |U| = " << maxU << nl
         << "  Avg |U| = " << avgU << nl
         << endl;
    
    // Store intermediate results for write() method
    maxUMemory_.append(maxU);
    avgUMemory_.append(avgU);
    
    return true;
}
```

### 2.4 Write Method Implementation

The `write()` method is called **at write times** (based on `writeControl`):

```cpp
bool Foam::myFunctionObject::write()
{
    // Create output file path
    fileName outputPath = time_.globalPath()/outputFile_;
    
    // Open file in append mode
    OFstream os(outputPath);
    
    if (!os.good())
    {
        WarningInFunction
            << "Cannot open file " << outputPath << " for writing" << endl;
        return false;
    }
    
    // Write header if new file
    if (time_.timeIndex() == 1)
    {
        os << "# Time maxU avgU CourantNumber" << nl;
    }
    
    // Access fields for current time statistics
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    scalar maxU = max(mag(U)).value();
    scalar avgU = average(mag(U)).value();
    
    // Calculate Courant number
    surfaceScalarField phi = fvc::flux(U);
    scalar CoNum = max(mag(phi)/mesh_.magSf()/mesh_.deltaCoeffs()).value()
                 *time_.deltaTValue();
    
    // Write data line
    os << time_.timeOutputValue() << tab
       << maxU << tab
       << avgU << tab
       << CoNum << nl;
    
    Info << type() << " written data to " << outputPath << endl;
    
    return true;
}
```

### 2.5 Read Method Implementation

```cpp
bool Foam::myFunctionObject::read(const dictionary& dict)
{
    // Update internal parameters from dictionary
    if (dict.found("outputFile"))
    {
        dict.readEntry("outputFile", outputFile_);
    }
    
    if (dict.found("writeInterval"))
    {
        dict.readEntry("writeInterval", writeInterval_);
    }
    
    Info << "Reconfigured " << type() << " with:" << nl
         << "  outputFile = " << outputFile_ << nl
         << "  writeInterval = " << writeInterval_ << nl;
    
    return true;
}
```

---

## 3. Registration and Loading

### 3.1 Runtime Selection Table Registration

```cpp
// At top of source file after includes
#include "myFunctionObject.H"

// Define type name and debug switch
defineTypeNameAndDebug(myFunctionObject, 0);

// Add to runtime selection table for dictionary-based construction
addToRunTimeSelectionTable
(
    functionObject,
    myFunctionObject,
    dictionary
);
```

### 3.2 Compilation Options File

**Make/options**:
```bash
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/sampling/lnInclude

LIB_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

### 3.3 Compilation and Linking

```bash
# Compile the function object library
wmake

# Or compile with debug symbols
wmake libso
```

---

## 4. Control Dictionary Configuration

### 4.1 Basic Configuration

```cpp
functions
{
    myVelocityMonitor
    {
        type            myFunctionObject;
        libs            ("libmyFunctionObjects.so");
        
        // Execution control
        executeControl  timeStep;        // Options: timeStep, writeTime, outputTime
        executeInterval 1;               // Execute every N time steps
        
        // Output control
        writeControl    writeTime;       // Options: timeStep, writeTime, outputTime, adjustableRunTime
        writeInterval   1;
        
        // Custom parameters
        outputFile      "velocityMonitoring.dat";
        writeInterval   10;              // Custom parameter read by function object
        
        // Enable/disable
        enabled         yes;
    }
}
```

### 4.2 Advanced Execution Control

```cpp
functions
{
    // Execute every 0.01 seconds of simulation time
    highFreqMonitor
    {
        type            myFunctionObject;
        libs            ("libmyFunctionObjects.so");
        executeControl  adjustableRunTime;
        executeInterval 0.01;
    }
    
    // Execute when Courant number exceeds threshold
    conditionalMonitor
    {
        type            myFunctionObject;
        libs            ("libmyFunctionObjects.so");
        executeControl  writeTime;       // Only at write times
    }
}
```

### 4.3 Multiple Function Objects

```cpp
functions
{
    // Velocity statistics
    velocityStats
    {
        type            myFunctionObject;
        libs            ("libmyFunctionObjects.so");
        executeControl  timeStep;
        writeControl    writeTime;
        outputFile      "U_stats.dat";
    }
    
    // Pressure monitoring
    pressureMonitor
    {
        type            myFunctionObject;
        libs            ("libmyFunctionObjects.so");
        executeControl  timeStep;
        writeControl    writeTime;
        outputFile      "p_stats.dat";
    }
    
    // Convergence tracking
    convergenceCheck
    {
        type            convergenceFunctionObject;
        libs            ("libmyFunctionObjects.so");
        executeControl  timeStep;
        tolerance       1e-6;
    }
}
```

---

## 5. Accessing Fields and Database Objects

### 5.1 Field Lookup and Access

```cpp
bool myAdvancedFunctionObject::execute()
{
    // Method 1: Lookup with error checking
    if (mesh_.foundObject<volVectorField>("U"))
    {
        const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
        
        // Process velocity field
        vector Umean = average(U).value();
        Info << "Mean velocity: " << Umean << endl;
    }
    
    // Method 2: Direct lookup (throws error if not found)
    const volScalarField& p = mesh_.lookupObject<volScalarField>("p");
    
    // Method 3: Lookup from Time object registry
    const surfaceScalarField& phi = 
        time_.lookupObject<surfaceScalarField>("phi");
    
    return true;
}
```

### 5.2 Creating Temporary Fields

```cpp
bool myFunctionObject::execute()
{
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    
    // Create derived field
    volScalarField magU
    (
        IOobject
        (
            "magU",
            time_.timeName(),
            mesh_,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mag(U)
    );
    
    // Calculate statistics
    scalar maxMagU = max(magU).value();
    scalar minMagU = min(magU).value();
    
    // Write derived field for visualization
    magU.write();
    
    return true;
}
```

### 5.3 Accessing Boundary Data

```cpp
bool myFunctionObject::execute()
{
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    
    // Access boundary patches
    const volVectorField::Boundary& Ubf = U.boundaryFieldRef();
    
    forAll(Ubf, patchi)
    {
        const fvPatchVectorField& patchU = Ubf[patchi];
        const word& patchName = patchU.patch().name();
        
        // Calculate patch-averaged values
        vector avgU = gAverage(patchU);
        
        Info << "Patch " << patchName << " average U: " << avgU << endl;
        
        // Specific patch analysis
        if (patchName == "inlet")
        {
            vector inletU = avgU;
            // Process inlet velocity
        }
    }
    
    return true;
}
```

### 5.4 Accessing Mesh Geometry

```cpp
bool myFunctionObject::execute()
{
    // Cell centers
    const vectorField& C = mesh_.C().internalField();
    
    // Cell volumes
    const scalarField& V = mesh_.V().field();
    
    // Face areas
    const surfaceVectorField& Sf = mesh_.Sf();
    
    // Calculate total domain volume
    scalar totalVolume = gSum(V);
    
    Info << "Domain volume: " << totalVolume << " m³" << endl;
    
    return true;
}
```

---

## 6. Built-in Function Objects

### 6.1 Common Built-in Function Objects

| Function Object | Purpose | Typical Use Case |
|-----------------|---------|------------------|
| **fieldAverage** | Time averaging of fields | Statistical convergence, mean flow profiles |
| **probes** | Point sampling | Time series at specific locations |
| **surfaces** | Surface sampling | Data along lines/planes |
| **sets** | Sample on cell sets | Zone-specific monitoring |
| **forces** | Force/moment calculation | Aerodynamic forces, lift/drag |
| **forceCoeffs** | Force coefficients | Nondimensional coefficients (Cl, Cd) |
| **yPlus** | Wall y+ calculation | Turbulence model validation |
| **courantNo** | Courant number monitoring | Time step stability |
| **execFlowFunctionObjects** | Multi-function execution | Batch operations |
| **nearWallFields** | Wall-adjacent cell values | Boundary layer analysis |

### 6.2 Field Average Example

```cpp
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        libs            ("libfieldFunctionObjects.so");
        
        writeControl    writeTime;
        
        fields
        (
            U
            {
                mean            on;
                prime2Mean      on;   // <U'U'> = <U²> - <U>²
                base            time; // Options: time, iteration
            }
            
            p
            {
                mean            on;
                prime2Mean      off;
                base            time;
            }
        );
    }
}
```

### 6.3 Probes Example

```cpp
functions
{
    probes
    {
        type            probes;
        libs            ("libsampling.so");
        
        writeControl    timeStep;
        writeInterval   10;
        
        probeLocations
        (
            (0.01 0.01 0.01)
            (0.01 0.05 0.01)
            (0.05 0.05 0.05)
        );
        
        fields          (p U);
    }
}
```

### 6.4 Forces Example

```cpp
functions
{
    forces
    {
        type            forces;
        libs            ("libforces.so");
        
        writeControl    timeStep;
        writeInterval   1;
        
        patches         ("wall");
        
        // Density field for compressible
        rho             rhoInf;
        rhoInf          1.225;  // kg/m³
        
        // Center of rotation for moments
        CofR            (0 0 0);
        
        // Write component breakdown
        writeFields     yes;
    }
    
    forceCoeffs
    {
        type            forceCoeffs;
        libs            ("libforces.so");
        
        patches         ("wall");
        rhoInf          1.225;
        
        // Reference values for coefficients
        lRef            0.1;     // Reference length
        Aref            0.01;    // Reference area
        
        // Lift and drag direction
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        
        // MagU∞ and p∞
        magUInf         10.0;
        pInf            0.0;
        
        writeFields     yes;
    }
}
```

---

## 7. Complete Practical Exercise

### 7.1 Exercise: Convergence Monitoring Function Object

**Objective**: Create a complete function object that monitors solution convergence by tracking field residuals and mass conservation.

### 7.2 Implementation

**File: `convergenceMonitor.H`**
```cpp
#ifndef convergenceMonitor_H
#define convergenceMonitor_H

#include "functionObject.H"
#include "fvMesh.H"
#include "volFields.H"

namespace Foam
{

class convergenceMonitor
:
    public functionObject
{
    // Private Data
        
        //- Reference to mesh
        const fvMesh& mesh_;
        
        //- Convergence tolerance
        scalar tolerance_;
        
        //- Maximum iterations before warning
        label maxIterations_;
        
        //- Previous time values for residual calculation
        scalar previousUMax_;
        scalar previousPMax_;
        
        //- Converged flag
        bool converged_;


public:

    //- Runtime type information
    TypeName("convergenceMonitor");

    // Constructors

        convergenceMonitor
        (
            const word& name,
            const Time& runTime,
            const dictionary& dict
        );

    //- Destructor
    virtual ~convergenceMonitor() = default;


    // Member Functions

        virtual bool read(const dictionary&);
        virtual bool execute();
        virtual bool write();
        virtual bool end();
        
        //- Check if converged
        bool converged() const { return converged_; }
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

#endif
```

**File: `convergenceMonitor.C`**
```cpp
#include "convergenceMonitor.H"
#include "fvc.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

defineTypeNameAndDebug(convergenceMonitor, 0);
addToRunTimeSelectionTable(functionObject, convergenceMonitor, dictionary);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

Foam::convergenceMonitor::convergenceMonitor
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    functionObject(name, runTime),
    mesh_(runTime.lookupObject<fvMesh>(polyMesh::defaultRegion)),
    tolerance_(dict.getOrDefault<scalar>("tolerance", 1e-6)),
    maxIterations_(dict.getOrDefault<label>("maxIterations", 1000)),
    previousUMax_(GREAT),
    previousPMax_(GREAT),
    converged_(false)
{
    Info << nl << "Convergence Monitor:" << nl
         << "  Tolerance: " << tolerance_ << nl
         << "  Max iterations: " << maxIterations_ << nl
         << endl;
}


bool Foam::convergenceMonitor::read(const dictionary& dict)
{
    dict.readIfPresent("tolerance", tolerance_);
    dict.readIfPresent("maxIterations", maxIterations_);
    return true;
}


bool Foam::convergenceMonitor::execute()
{
    // Check required fields
    if (!mesh_.foundObject<volVectorField>("U") || 
        !mesh_.foundObject<volScalarField>("p"))
    {
        return false;
    }
    
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    const volScalarField& p = mesh_.lookupObject<volScalarField>("p");
    
    // Calculate current maximum magnitudes
    scalar currentUMax = max(mag(U)).value();
    scalar currentPMax = max(mag(p)).value();
    
    // Calculate residuals (relative change)
    scalar residualU = GREAT;
    scalar residualP = GREAT;
    
    if (previousUMax_ < GREAT && previousPMax_ < GREAT)
    {
        residualU = mag(currentUMax - previousUMax_) / 
                   (previousUMax_ + SMALL);
        residualP = mag(currentPMax - previousPMax_) / 
                   (previousPMax_ + SMALL);
    }
    
    // Update previous values
    previousUMax_ = currentUMax;
    previousPMax_ = currentPMax;
    
    // Check mass conservation (continuity)
    surfaceScalarField phi = fvc::flux(U);
    scalar maxContinuityError = max(mag(fvc::div(phi))).value();
    
    // Output convergence information
    Info << "Convergence Monitor:" << nl
         << "  Time = " << time_.timeOutputValue() << nl
         << "  |U|_max = " << currentUMax << nl
         << "  |p|_max = " << currentPMax << nl
         << "  Residual U = " << residualU << nl
         << "  Residual p = " << residualP << nl
         << "  Continuity error = " << maxContinuityError << nl
         << "  Converged = " << (converged_ ? "YES" : "NO") << nl
         << endl;
    
    // Check convergence criteria
    if (residualU < tolerance_ && residualP < tolerance_ && 
        maxContinuityError < tolerance_)
    {
        if (!converged_)
        {
            Info << nl << ">>> SOLUTION CONVERGED <<<" << nl << nl;
            converged_ = true;
        }
    }
    else
    {
        converged_ = false;
    }
    
    // Check iteration limit
    if (time_.timeIndex() > maxIterations_ && !converged_)
    {
        WarningInFunction
            << "Maximum iterations (" << maxIterations_ 
            << ") exceeded without convergence" << endl;
    }
    
    return true;
}


bool Foam::convergenceMonitor::write()
{
    // Write convergence history to file
    OFstream os(time_.globalPath()/"convergenceHistory.dat");
    
    if (time_.timeIndex() == 1)
    {
        os << "# Time  U_max  p_max  Residual_U  Residual_p  Continuity  Converged" << nl;
    }
    
    const volVectorField& U = mesh_.lookupObject<volVectorField>("U");
    const volScalarField& p = mesh_.lookupObject<volScalarField>("p");
    
    scalar currentUMax = max(mag(U)).value();
    scalar currentPMax = max(mag(p)).value();
    
    scalar residualU = mag(currentUMax - previousUMax_) / (previousUMax_ + SMALL);
    scalar residualP = mag(currentPMax - previousPMax_) / (previousPMax_ + SMALL);
    
    surfaceScalarField phi = fvc::flux(U);
    scalar maxContinuityError = max(mag(fvc::div(phi))).value();
    
    os << time_.timeOutputValue() << tab
       << currentUMax << tab
       << currentPMax << tab
       << residualU << tab
       << residualP << tab
       << maxContinuityError << tab
       << (converged_ ? 1 : 0) << nl;
    
    Info << "Convergence history written" << endl;
    
    return true;
}


bool Foam::convergenceMonitor::end()
{
    Info << nl << "Final Convergence Status:" << nl;
    
    if (converged_)
    {
        Info << "  ✓ Solution converged successfully" << nl;
    }
    else
    {
        Info << "  ✗ Solution did NOT converge" << nl;
    }
    
    Info << "  Final time: " << time_.timeOutputValue() << nl
         << "  Total iterations: " << time_.timeIndex() << nl
         << endl;
    
    return true;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam
```

### 7.3 Configuration

**File: `system/controlDict`**
```cpp
application     simpleFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          0.01;

writeControl    timeStep;
writeInterval   100;

functions
{
    convergenceMonitor
    {
        type            convergenceMonitor;
        libs            ("libcustomFunctionObjects.so");
        
        executeControl  timeStep;
        writeControl    writeTime;
        
        tolerance       1e-6;
        maxIterations   10000;
    }
    
    // Additional built-in function objects
    fieldAverage1
    {
        type            fieldAverage;
        libs            ("libfieldFunctionObjects.so");
        writeControl    writeTime;
        
        fields
        (
            U
            {
                mean        on;
                prime2Mean  on;
                base        time;
            }
            p
            {
                mean        on;
                prime2Mean  off;
                base        time;
            }
        );
    }
}
```

### 7.4 Compilation and Verification

**Make/files**:
```bash
convergenceMonitor.C

LIB = $(FOAM_USER_LIBBIN)/libcustomFunctionObjects
```

**Make/options**:
```bash
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/sampling/lnInclude

LIB_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

**Compile**:
```bash
cd convergenceMonitor
wmake libso
```

**Verification Test**:
```bash
# Run simpleFoam with the function object
cd ~/OpenFOAM/user-${WM_PROJECT_VERSION}/run/tutorials/incompressible/simpleFoam/airfoil2D

# Modify system/controlDict to include the function object configuration

# Run solver
simpleFoam

# Expected output in log:
# Convergence Monitor:
#   Time = 0.01
#   |U|_max = 2.5
#   |p|_max = 1250
#   Residual U = 0.05
#   Residual p = 0.02
#   Continuity error = 1e-5
#   Converged = NO
#
# ...
#
# >>> SOLUTION CONVERGED <<<

# Verify convergence history file was created
ls convergenceHistory.dat
cat convergenceHistory.dat

# Should see tab-separated data showing convergence progression
```

---

## 8. Debugging and Best Practices

### 8.1 Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| **cannot open file include** | Incorrect path in options file | Verify `-I` paths include required libraries |
| **undefined symbol** | Missing registration macro | Add `defineTypeNameAndDebug` and `addToRunTimeSelectionTable` |
| **lookup failed** | Field not in database | Use `foundObject()` before `lookupObject()` |
| **segmentation fault** | Null pointer access | Always check object existence before access |
| **library not loaded** | Incorrect `libs` path | Use absolute path or ensure library in `$FOAM_USER_LIBBIN` |

### 8.2 Debugging Techniques

```cpp
// Enable debug output in constructor
defineTypeNameAndDebug(myFunctionObject, 1);  // Set debug = 1

// In execute()
if (debug)
{
    Info << "DEBUG: " << type() << " executing at time " 
         << time_.timeName() << endl;
}

// Print object registry contents (for debugging)
const objectRegistry& obr = mesh_.thisDb();
Info << "Objects in registry:" << nl;
wordList objectNames = obr.sortedNames();
forAll(objectNames, i)
{
    Info << "  " << objectNames[i] << endl;
}
```

### 8.3 Performance Considerations

- **Minimize file I/O**: Buffer data and write less frequently
- **Avoid field recalculation**: Store derived quantities as member variables
- **Use selective lookup**: Only access required fields
- **Profile execution**: Use `cpuTime` class to measure execution time

```cpp
bool myFunctionObject::execute()
{
    cpuTime executionTimer;
    
    // ... function object logic ...
    
    if (debug)
    {
        Info << "Execution time: " << executionTimer.cpuTimeIncrement() 
             << " s" << endl;
    }
    
    return true;
}
```

### 8.4 Best Practices Summary

✅ **DO**:
- Always check field existence with `foundObject()` before `lookupObject()`
- Use `const` references for field access to avoid unnecessary copying
- Write informative output with `Info` for monitoring
- Validate dictionary parameters in constructor
- Handle edge cases (empty fields, zero division, etc.)
- Document function object purpose and usage in header comments

❌ **DON'T**:
- Don't modify solver fields unless absolutely necessary
- Don't perform expensive calculations every time step if not needed
- Don't ignore warnings from failed object lookups
- Don't hardcode file paths (use `time_.globalPath()`)
- Don't forget to clean up resources in destructor if needed

---

## 📋 Key Takeaways

### Architecture and Integration

- **Function objects** provide non-intrusive extensibility through the object registry system
- **execute() method**: Called every time step (per `executeControl`) for real-time monitoring
- **write() method**: Called at write times (per `writeControl`) for data export and file output
- **Runtime selection tables** enable dynamic loading through `.so` libraries specified in `libs`

### Field Access and Processing

- **`mesh_.lookupObject<FieldType>(fieldName)`**: Primary method for accessing registered fields
- **`foundObject()` check**: Essential safety practice before field access to prevent runtime errors
- **Derived fields**: Create temporary fields with `NO_READ/NO_WRITE` for intermediate calculations
- **Boundary access**: Use `.boundaryFieldRef()` for patch-specific analysis

### Practical Implementation

- **Registration**: Always include `defineTypeNameAndDebug` and `addToRunTimeSelectionTable` macros
- **Error handling**: Validate dictionary parameters and field existence in constructor
- **Output control**: Use `executeControl` and `writeControl` strategically for performance
- **Built-in objects**: Leverage existing function objects (`fieldAverage`, `probes`, `forces`) before creating custom ones
- **Debugging**: Enable debug output and use `foundObject()` checks for robust field access

### Common Pitfalls to Avoid

- **Missing library path**: Ensure `libs` entry points to valid `.so` file location
- **Incorrect execution timing**: Understand difference between `executeControl` (per-step) and `writeControl` (output)
- **Null pointer access**: Never assume field exists without checking first
- **Performance issues**: Avoid expensive calculations every time step when less frequent execution suffices
- **Incomplete verification**: Always test function object with real solver runs, not just compilation

---

## 📖 Related Documentation

- **Overview**: [00_Overview.md](00_Overview.md) - Extensibility architecture overview
- **Patterns**: [03_Design_Patterns.md](../03_DESIGN_PATTERNS/00_Overview.md) - Factory and strategy patterns
- **Runtime Selection**: [02_Inheritance_Polymorphism.md](../02_INHERITANCE_POLYMORPHISM/04_Run_Time_Selection_System.md) - Runtime selection mechanism
- **Built-in Objects**: OpenFOAM User Guide - Function Objects reference