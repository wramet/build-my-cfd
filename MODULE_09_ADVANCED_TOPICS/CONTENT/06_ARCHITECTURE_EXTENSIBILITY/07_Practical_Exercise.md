# Practical Exercise: Extensible Architecture Implementation

## Learning Objectives

By completing this practical exercise, you will be able to:

- Implement a complete Run-Time Selection (RTS) model with proper registration
- Create and register a custom Function Object for solver integration
- Build and compile dynamic libraries for OpenFOAM extensions
- Integrate extensible components into an existing solver
- Verify and validate your implementation through testing

---

## Prerequisites

- Completed study of Modules 01-05 in this section
- Basic understanding of C++ inheritance and polymorphism
- Access to OpenFOAM installation with wmake compilation tools
- Text editor and terminal for compilation and testing

---

## Exercise 1: Complete RTS Model Implementation

### Objective

Create a fully functional Run-Time Selection model that computes turbulence viscosity modifications. This exercise demonstrates the complete RTS pattern from base class to concrete implementation.

### Task Specification

Implement a custom turbulence model wrapper called `myViscosityModel` that modifies the effective viscosity based on a user-defined coefficient.

### Step 1: Base Class Definition

First, ensure you have a base class that defines the interface:

```cpp
// baseViscosityModel.H
#ifndef baseViscosityModel_H
#define baseViscosityModel_H

#include "fvMesh.H"
#include "dictionary.H"
#include "autoPtr.H"
#include "runTimeSelectionTables.H"

namespace Foam
{

class baseViscosityModel
{
protected:
    const fvMesh& mesh_;
    const dictionary& dict_;
    word name_;

public:
    TypeName("baseViscosityModel");

    declareRunTimeSelectionTable
    (
        autoPtr,
        baseViscosityModel,
        dictionary,
        (const fvMesh& mesh, const dictionary& dict),
        (mesh, dict)
    );

    // Constructor
    baseViscosityModel(const fvMesh& mesh, const dictionary& dict)
    : mesh_(mesh), dict_(dict), name_(dict.lookup("name"))
    {}

    // Destructor
    virtual ~baseViscosityModel() {}

    // Select factory method
    static autoPtr<baseViscosityModel> New
    (
        const fvMesh& mesh,
        const dictionary& dict
    );

    // Pure virtual compute method
    virtual tmp<volScalarField> computeEffViscosity() const = 0;

    // Optional info method
    virtual void writeInfo() const = 0;
};

} // End namespace Foam

#endif
```

### Step 2: Derived Model Implementation

Create the complete derived model:

```cpp
// myViscosityModel.H
#ifndef myViscosityModel_H
#define myViscosityModel_H

#include "baseViscosityModel.H"

namespace Foam
{

class myViscosityModel
:
    public baseViscosityModel
{
private:
    // Model coefficient
    scalar modificationFactor_;
    word baseModelName_;

public:
    TypeName("myViscosityModel");

    // Constructor
    myViscosityModel
    (
        const fvMesh& mesh,
        const dictionary& dict
    );

    // Destructor
    virtual ~myViscosityModel() {}

    // Compute effective viscosity
    virtual tmp<volScalarField> computeEffViscosity() const;

    // Write model info
    virtual void writeInfo() const;
};

} // End namespace Foam

#endif
```

### Step 3: Implementation File

```cpp
// myViscosityModel.C
#include "myViscosityModel.H"
#include "fvc.H"
#include "addToRunTimeSelectionTable.H"

// Register with RTS
namespace Foam
{
    defineTypeNameAndDebug(myViscosityModel, 0);
    addToRunTimeSelectionTable
    (
        baseViscosityModel,
        myViscosityModel,
        dictionary
    );
}

// Constructor implementation
Foam::myViscosityModel::myViscosityModel
(
    const fvMesh& mesh,
    const dictionary& dict
)
:
    baseViscosityModel(mesh, dict),
    modificationFactor_(dict.lookupOrDefault<scalar>("modificationFactor", 1.5)),
    baseModelName_(dict.lookupOrDefault<word>("baseModel", word::null))
{
    Info << "Creating myViscosityModel with factor: " 
         << modificationFactor_ << endl;
    
    if (modificationFactor_ <= 0)
    {
        FatalErrorInFunction
            << "modificationFactor must be positive, got: " 
            << modificationFactor_ << exit(FatalError);
    }
}

// Compute effective viscosity
Foam::tmp<Foam::volScalarField> 
Foam::myViscosityModel::computeEffViscosity() const
{
    // Get base turbulence viscosity from mesh object database
    const volScalarField& nut = 
        mesh_.objectRegistry::lookupObject<volScalarField>("nut");

    // Create modified field
    tmp<volScalarField> tnutEff
    (
        new volScalarField
        (
            IOobject
            (
                "nutEff",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            nut * modificationFactor_
        )
    );

    return tnutEff;
}

// Write model information
void Foam::myViscosityModel::writeInfo() const
{
    Info << "Model: " << type() << nl
         << "  Modification factor: " << modificationFactor_ << nl
         << "  Mesh cells: " << mesh_.nCells() << endl;
}
```

### Step 4: Base Class Factory Implementation

```cpp
// baseViscosityModel.C
#include "baseViscosityModel.H"

Foam::autoPtr<Foam::baseViscosityModel> 
Foam::baseViscosityModel::New
(
    const fvMesh& mesh,
    const dictionary& dict
)
{
    word modelName = dict.lookup("type");

    Info << "Selecting viscosity model: " << modelName << endl;

    dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelName);

    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown viscosity model " << modelName 
            << nl << nl
            << "Valid models:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }

    return autoPtr<baseViscosityModel>
        (cstrIter()(mesh, dict));
}
```

### Step 5: Dictionary Configuration

```cpp
// constant/viscosityProperties
// -*- C++ -*-
 FoamFile
 {
     version     2.0;
     format      ascii;
     class       dictionary;
     location    "constant";
     object      viscosityProperties;
 }
 // * * * * * * * * * * * * * * * * * //

 viscosityModel
 {
     type myViscosityModel;
     modificationFactor 1.5;
 }

 // ************************************************************************* //
```

### Verification Steps

1. **Compile the model:**
```bash
cd $WM_PROJECT_USER_DIR/src/myViscosityModel
wmake libso
```

2. **Check successful compilation:**
```bash
ls $FOAM_USER_LIBBIN/libmyViscosityModel.so
```

3. **Verify RTS registration:**
```bash
# Test with a simple case
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/airfoil2D ~/testViscosityModel
cd ~/testViscosityModel
```

4. **Add to controlDict:**
```cpp
// system/controlDict
application     simpleFoam;

libs ("libmyViscosityModel.so");

functions
{
    viscosityInfo
    {
        type myViscosityModel;
        modificationFactor 1.5;
    }
}
```

5. **Run and verify:**
```bash
simpleFoam > log.simpleFoam 2>&1
grep "Selecting viscosity model" log.simpleFoam
```

### Expected Output

```
Selecting viscosity model: myViscosityModel
Creating myViscosityModel with factor: 1.5
Model: myViscosityModel
  Modification factor: 1.5
  Mesh cells: 12500
```

---

## Exercise 2: Function Object with Complete Implementation

### Objective

Create a production-ready Function Object that monitors and reports field statistics during simulation, demonstrating proper function object lifecycle management.

### Complete Function Object Header

```cpp
// fieldStatisticsFunctionObject.H
#ifndef fieldStatisticsFunctionObject_H
#define fieldStatisticsFunctionObject_H

#include "functionObject.H"
#include "fvMesh.H"
#include "HashSet.H"
#include "wordList.H"

namespace Foam
{

namespace functionObjects
{

class fieldStatistics
:
    public functionObject
{
    // Private Data
    const fvMesh& mesh_;
    wordList fieldNames_;
    scalar writeInterval_;
    label executionCounter_;
    fileName outputFile_;

    // Private Member Functions
    void writeFieldStats(const word& fieldName);
    scalar calculateMax(const volScalarField& field) const;
    scalar calculateMin(const volScalarField& field) const;
    scalar calculateAverage(const volScalarField& field) const;

public:
    TypeName("fieldStatistics");
    
    // Constructors
    fieldStatistics
    (
        const word& name,
        const Time& runTime,
        const dictionary& dict
    );

    //- Destructor
    virtual ~fieldStatistics();

    // Public Member Functions
    
    //- Read and set the function object
    virtual bool read(const dictionary& dict);

    //- Execute after calculation phase
    virtual bool execute();

    //- Execute at the final time loop
    virtual bool end();

    //- Write the function object results
    virtual bool write();
    
    //- Reset the function object
    virtual void updateMesh(const mapPolyMesh& mpm)
    {}

    //- Update for changes of mesh
    virtual void movePoints(const polyMesh& mesh)
    {}
};

} // End namespace functionObjects

} // End namespace Foam

#endif
```

### Complete Function Object Implementation

```cpp
// fieldStatisticsFunctionObject.C
#include "fieldStatisticsFunctionObject.H"
#include "volFields.H"
#include "fvMeshFunctionObject.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

namespace Foam
{
namespace functionObjects
{
    defineTypeNameAndDebug(fieldStatistics, 0);
    addToRunTimeSelectionTable
    (
        functionObject,
        fieldStatistics,
        dictionary
    );
}
}

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * //

Foam::functionObjects::fieldStatistics::fieldStatistics
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    functionObject(name, runTime),
    mesh_(runTime.lookupObject<fvMesh>(polyMesh::defaultRegion)),
    writeInterval_(dict.lookupOrDefault<scalar>("writeInterval", 1.0)),
    executionCounter_(0),
    outputFile_(dict.lookupOrDefault<fileName>("outputFile", "fieldStats.dat"))
{
    read(dict);
    Info << "Created " << type() << " for fields: " << fieldNames_ << endl;
}

// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * //

Foam::functionObjects::fieldStatistics::~fieldStatistics()
{}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * //

bool Foam::functionObjects::fieldStatistics::read(const dictionary& dict)
{
    dict.lookup("fields", fieldNames_);
    writeInterval_ = dict.lookupOrDefault<scalar>("writeInterval", 1.0);
    outputFile_ = dict.lookupOrDefault<fileName>("outputFile", "fieldStats.dat");
    
    // Validate field names exist
    forAll(fieldNames_, i)
    {
        if (!mesh_.objectRegistry::foundObject<volScalarField>(fieldNames_[i]))
        {
            WarningInFunction
                << "Field " << fieldNames_[i] 
                << " not found in mesh. Will check at runtime." << endl;
        }
    }
    
    return true;
}

bool Foam::functionObjects::fieldStatistics::execute()
{
    executionCounter_++;
    
    if (executionCounter_ % label(writeInterval_) == 0)
    {
        Info << "Field Statistics at time: " << time_.timeName() << endl;
        
        forAll(fieldNames_, i)
        {
            writeFieldStats(fieldNames_[i]);
        }
    }
    
    return true;
}

bool Foam::functionObjects::fieldStatistics::end()
{
    Info << "Final field statistics:" << endl;
    
    forAll(fieldNames_, i)
    {
        writeFieldStats(fieldNames_[i]);
    }
    
    return true;
}

bool Foam::functionObjects::fieldStatistics::write()
{
    // Write statistics to file
    OFstream os(time_.path() / outputFile_);
    
    os << "# Field statistics at time: " << time_.timeName() << nl;
    os << "# Field\tMax\tMin\tAverage" << nl;
    
    forAll(fieldNames_, i)
    {
        const word& fieldName = fieldNames_[i];
        
        if (mesh_.objectRegistry::foundObject<volScalarField>(fieldName))
        {
            const volScalarField& field = 
                mesh_.lookupObject<volScalarField>(fieldName);
            
            os << fieldName << "\t" 
               << calculateMax(field) << "\t"
               << calculateMin(field) << "\t"
               << calculateAverage(field) << nl;
        }
    }
    
    return true;
}

void Foam::functionObjects::fieldStatistics::writeFieldStats
(
    const word& fieldName
)
{
    if (!mesh_.objectRegistry::foundObject<volScalarField>(fieldName))
    {
        Warning << "Field " << fieldName << " not found. Skipping." << endl;
        return;
    }
    
    const volScalarField& field = mesh_.lookupObject<volScalarField>(fieldName);
    
    scalar fieldMax = calculateMax(field);
    scalar fieldMin = calculateMin(field);
    scalar fieldAvg = calculateAverage(field);
    
    Info << "  " << fieldName << ":" << nl
         << "    Max:     " << fieldMax << nl
         << "    Min:     " << fieldMin << nl
         << "    Average: " << fieldAvg << nl
         << endl;
}

Foam::scalar Foam::functionObjects::fieldStatistics::calculateMax
(
    const volScalarField& field
) const
{
    return max(field).value();
}

Foam::scalar Foam::functionObjects::fieldStatistics::calculateMin
(
    const volScalarField& field
) const
{
    return min(field).value();
}

Foam::scalar Foam::functionObjects::fieldStatistics::calculateAverage
(
    const volScalarField& field
) const
{
    return sum(field) / field.mesh().nCells();
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

### Dictionary Configuration

```cpp
// system/controlDict
functions
{
    fieldStatistics1
    {
        type            fieldStatistics;
        libs            ("libmyFunctionObjects.so");
        
        fields          (p U);
        writeInterval   10;
        outputFile      "postProcessing/fieldStats.dat";
        
        // Optional: write to log only
        writeToFile     yes;
        writeToLog      yes;
    }
}
```

### Verification Steps

1. **Compile the function object:**
```bash
cd $WM_PROJECT_USER_DIR/src/functionObjects/myFieldStats
wmake libso
```

2. **Verify library creation:**
```bash
ls -lh $FOAM_USER_LIBBIN/libmyFunctionObjects.so
```

3. **Create test case:**
```bash
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pipe ~/testFunctionObject
cd ~/testFunctionObject
```

4. **Add to controlDict:**
```cpp
// Add to system/controlDict under functions section
fieldStats
{
    type            fieldStatistics;
    libs            ("libmyFunctionObjects.so");
    fields          (p U k epsilon);
    writeInterval   5;
    outputFile      "postProcessing/fieldStatistics.dat";
}
```

5. **Run simulation:**
```bash
simpleFoam > log.simpleFoam 2>&1
```

6. **Check output:**
```bash
# Verify statistics in log
grep "Field Statistics" log.simpleFoam

# Check output file
cat postProcessing/fieldStatistics.dat
```

### Expected Output Format

```
Field Statistics at time: 0.1
  p:
    Max:     101325.0
    Min:     100000.0
    Average: 100650.5

  U:
    Max:     10.5
    Min:     0.0
    Average: 5.2
```

---

## Exercise 3: Dynamic Library Loading - Complete Implementation

### Objective

Create a complete dynamic library with multiple models, proper Make files, and demonstrate various loading mechanisms.

### Step 1: Create Library Directory Structure

```bash
cd $WM_PROJECT_USER_DIR
mkdir -p src/customModels/{Make,Models}
cd src/customModels
```

### Step 2: Create Main Header File

```cpp
// customModels.H
#ifndef customModels_H
#define customModels_H

#include "fvOptions.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

//- Model that adds momentum source
template<class RhoFieldType>
class customMomentumSource
:
    public fv::option
{
    // Private Data
    const RhoFieldType& rho_;
    vector sourceDirection_;
    scalar sourceMagnitude_;

public:
    TypeName("customMomentumSource");

    customMomentumSource
    (
        const word& name,
        const word& modelType,
        const fvMesh& mesh,
        const dictionary& dict
    );

    virtual ~customMomentumSource()
    {}

    // Evaluation
    virtual void addSup
    (
        fvMatrix<vector>& eqn,
        const label fieldI
    );

    virtual void addSup
    (
        const volScalarField& rho,
        fvMatrix<vector>& eqn,
        const label fieldI
    );

    // IO
    virtual bool read(const dictionary& dict);
    
    virtual void writeData(Ostream& os) const;
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif
```

### Step 3: Implementation File

```cpp
// customModels.C
#include "customModels.H"
#include "fvm.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

namespace Foam
{
template<class RhoFieldType>
typeName(Foam::customMomentumSource<RhoFieldType>);

template<class RhoFieldType>
addToRunTimeSelectionTable
(
    fv::option,
    customMomentumSource<RhoFieldType>,
    dictionary
);
}

// * * * * * * * * * * * * * * * * Constructors * * * * * * * * * * * * * * //

template<class RhoFieldType>
Foam::customMomentumSource<RhoFieldType>::customMomentumSource
(
    const word& name,
    const word& modelType,
    const fvMesh& mesh,
    const dictionary& dict
)
:
    fv::option(name, modelType, mesh, dict),
    rho_
    (
        mesh.lookupObject<RhoFieldType>
        (
            dict.lookupOrDefault<word>("rho", "rho")
        )
    ),
    sourceDirection_(dict.lookup("direction")),
    sourceMagnitude_(dict.lookup<scalar>("magnitude"))
{
    Info << "Created " << type() << " named " << name 
         << " with direction: " << sourceDirection_ 
         << " and magnitude: " << sourceMagnitude_ << endl;
}

// * * * * * * * * * * * * * * * Member Functions * * * * * * * * * * * * * //

template<class RhoFieldType>
void Foam::customMomentumSource<RhoFieldType>::addSup
(
    fvMatrix<vector>& eqn,
    const label fieldI
)
{
    DimensionedField<vector, volMesh> source
    (
        IOobject
        (
            name_ + ":source",
            mesh_.time().timeName(),
            mesh_,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh_,
        dimensionedVector
        (
            "zero",
            eqn.dimensions()/dimVolume,
            Zero
        )
    );

    vector uniformSource = sourceDirection_ * sourceMagnitude_;
    source = uniformSource;

    eqn += source;
}

template<class RhoFieldType>
void Foam::customMomentumSource<RhoFieldType>::addSup
(
    const volScalarField& rho,
    fvMatrix<vector>& eqn,
    const label fieldI
)
{
    DimensionedField<vector, volMesh> source
    (
        IOobject
        (
            name_ + ":source",
            mesh_.time().timeName(),
            mesh_,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh_,
        dimensionedVector
        (
            "zero",
            eqn.dimensions()/dimVolume,
            Zero
        )
    );

    vector uniformSource = sourceDirection_ * sourceMagnitude_;
    source = uniformSource;

    eqn += source;
}

template<class RhoFieldType>
bool Foam::customMomentumSource<RhoFieldType>::read(const dictionary& dict)
{
    fv::option::read(dict);
    
    dict.lookup("direction", sourceDirection_);
    sourceMagnitude_ = dict.lookup<scalar>("magnitude");
    
    return true;
}

template<class RhoFieldType>
void Foam::customMomentumSource<RhoFieldType>::writeData(Ostream& os) const
{
    fv::option::writeData(os);
    
    os << indent << "direction " << sourceDirection_ << token::END_STATEMENT << nl
       << indent << "magnitude " << sourceMagnitude_ << token::END_STATEMENT << nl;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Explicit template instantiation
template class Foam::customMomentumSource<Foam::volScalarField>;
template class Foam::customMomentumSource<Foam::volScalarField::Internal>;

// ************************************************************************* //
```

### Step 4: Make/files

```bash
# Make/files
customModels.C

LIB = $(FOAM_USER_LIBBIN)/libcustomModels
```

### Step 5: Make/options

```bash
# Make/options
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/sampling/lnInclude

LIB_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

### Step 6: Compile Library

```bash
cd $WM_PROJECT_USER_DIR/src/customModels
wmake libso
```

### Loading Methods

**Method 1: controlDict (automatic at startup)**
```cpp
// system/controlDict
libs
(
    "libcustomModels.so"
);
```

**Method 2: Code-based loading (dynamic)**
```cpp
// In your solver code
#include "dlLibraryTable.H"

// Load library dynamically
dlLibraryTable& libTable = const_cast<Time&>(mesh.time()).libs();
bool loaded = libTable.open("libcustomModels.so");

if (loaded)
{
    Info << "Successfully loaded libcustomModels.so" << endl;
}
else
{
    Warning << "Failed to load libcustomModels.so" << endl;
}
```

**Method 3: fvOptions dictionary**
```cpp
// constant/fvOptions
momentumSource1
{
    type            customMomentumSource;
    active          yes;
    
    rho             rho;
    direction       (1 0 0);
    magnitude       10.0;
    
    selectionMode   all;
}
```

### Verification Steps

1. **Check library exists:**
```bash
ls -lh $FOAM_USER_LIBBIN/libcustomModels.so
```

2. **List symbols in library:**
```bash
nm -D $FOAM_USER_LIBBIN/libcustomModels.so | grep custom
```

3. **Test loading:**
```bash
# Create test case
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/airfoil2D ~/testLibrary
cd ~/testLibrary

# Add library to controlDict
echo 'libs ("libcustomModels.so");' >> system/controlDict

# Create fvOptions file
cat > constant/fvOptions << EOF
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvOptions;
}

momentumSource1
{
    type            customMomentumSource;
    active          yes;
    rho             rho;
    direction       (0.1 0 0);
    magnitude       5.0;
    selectionMode   all;
}
EOF

# Run solver
simpleFoam > log.simpleFoam 2>&1

# Check for successful loading
grep "customMomentumSource" log.simpleFoam
```

### Expected Output

```
--> FOAM Warning : 
    From function dlLibraryTable::open
    in file db/dynamicLibrary/dlLibraryTable/dlLibraryTable.C at line 123
    can not open "libcustomModels.so"
    
Successfully loaded libcustomModels.so
Created customMomentumSource named momentumSource1 with direction: (0.1 0 0) and magnitude: 5.0
```

---

## Exercise 4: Integration in Solver - Complete Example

### Objective

Integrate all extensible components into a modified solver, demonstrating the complete workflow from model creation to solver integration.

### Complete Modified Solver

Create a custom solver `mySimpleFoam` that uses the extensible architecture:

```cpp
// mySimpleFoam.C
#include "fvCFD.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"
#include "pisoControl.H"
#include "baseViscosityModel.H"
#include "fvOptions.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    
    Info << nl << "Starting mySimpleFoam solver" << nl << endl;

    // Load custom viscosity model if specified
    autoPtr<baseViscosityModel> viscosityModel;
    
    if (mesh.objectRegistry::foundObject<dictionary>("viscosityProperties"))
    {
        const dictionary& viscosityDict = 
            mesh.lookupObject<dictionary>("viscosityProperties");
        
        const dictionary& modelDict = viscosityDict.subDict("viscosityModel");
        
        viscosityModel = baseViscosityModel::New(mesh, modelDict);
        viscosityModel->writeInfo();
    }
    else
    {
        Info << "No custom viscosity model found. Using standard turbulence model." 
             << endl;
    }

    turbulence->validate();

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    
    while (simple.loop())
    {
        Info << "Time = " << runTime.timeName() << nl << endl;

        // --- Pressure-velocity SIMPLE corrector
        {
            #include "UEqn.H"

            // Pressure equation
            while (simple.correctNonOrthogonal())
            {
                tmp<fvScalarMatrix> pEqn
                (
                    fvm::laplacian turbulence->nuEff()(), p
                 ==
                    fvc::div(phi)
                );

                pEqn.setReference(pRefCell, pRefValue);
                pEqn.solve();

                if (simple.finalNonOrthogonalIter())
                {
                    phi -= pEqn.flux();
                }
            }

            #include "continuityErrs.H"
        }

        // Apply custom viscosity model if active
        if (viscosityModel.valid())
        {
            tmp<volScalarField> nutEff = 
                viscosityModel->computeEffViscosity();
            
            nutEff().write();
            
            Info << "Applied custom viscosity modification" << endl;
        }

        turbulence->correct();

        #include "write.H"

        Info << "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
             << "  ClockTime = " << runTime.elapsedClockTime() << " s"
             << nl << endl;
    }

    Info << "End\n" << endl;

    return 0;
}

// ************************************************************************* //
```

### Complete UEqn.H

```cpp
// UEqn.H
// Solve the Momentum equation

tmp<fvVectorMatrix> UEqn
(
    fvm::div(phi, U)
  + turbulence->divDevReff(U)
  + fvOptions(U)
);

UEqn.relax();

fvOptions.constrain(UEqn);

if (simple.momentumPredictor())
{
    solve(UEqn == -fvc::grad(p));

    fvOptions.correct(U);
}
```

### Complete createFields.H

```cpp
// createFields.H
Info << "Reading field p\n" << endl;
volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info << "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

#include "createPhi.H"

label pRefCell = 0;
scalar pRefValue = 0.0;
setRefCell(p, mesh.solutionDict().subDict("SIMPLE"), pRefCell, pRefValue);

singlePhaseTransportModel laminarTransport(U, phi);

autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New(U, phi, laminarTransport)
);

// Initialize fvOptions
IOdictionary fvOptionsDict
(
    IOobject
    (
        "fvOptions",
        runTime.constant(),
        mesh,
        IOobject::MUST_READ,
        IOobject::NO_WRITE
    )
);
```

### Make/files for Solver

```bash
mySimpleFoam.C

EXE = $(FOAM_USER_APPBIN)/mySimpleFoam
```

### Make/options for Solver

```bash
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/transportModels/incompressible/singlePhaseTransportModel \
    -I$(LIB_SRC)/turbulenceModels \
    -I$(LIB_SRC)/turbulenceModels/incompressible/turbulenceModel \
    -I$(LIB_SRC)/fvOptions/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I../customModels

EXE_LIBS = \
    -lfiniteVolume \
    -lincompressibleTransportModels \
    -lincompressibleTurbulenceModels \
    -lfvOptions \
    -lmeshTools \
    -lcustomModels
```

### Complete Test Case Setup

**constant/polymesh/blockMeshDict:**
```cpp
// Create simple 2D channel mesh
convertToMeters 1;

vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 1 0.1)
    (0 1 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 50 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }
    walls
    {
        type wall;
        faces
        (
            (0 1 5 4)
            (3 7 6 2)
        );
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (0 1 2 3)
            (4 5 6 7)
        );
    }
);
```

**0/p:**
```cpp
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    
    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    
    walls
    {
        type            zeroGradient;
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

**0/U:**
```cpp
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            noSlip;
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

**system/controlDict:**
```cpp
application     mySimpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

writeControl    timeStep;

writeInterval   100;

purgeWrite      0;

libs
(
    "libcustomModels.so"
);

functions
{
    fieldStats
    {
        type            fieldStatistics;
        libs            ("libmyFunctionObjects.so");
        
        fields          (p U);
        writeInterval   50;
        outputFile      "postProcessing/fieldStats.dat";
    }
}
```

**system/fvSchemes:**
```cpp
ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwindV grad(U);
    div(phi,k)      bounded Gauss upwind;
    div(phi,epsilon) bounded Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

**system/fvSolution:**
```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
}

potentialFlow
{
    nNonOrthogonalCorrectors 0;
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
    }
}
```

**constant/transportProperties:**
```cpp
transportModel  Newtonian;

nu              [0 2 -1 0 0 0 0]  0.01;
```

**constant/turbulenceProperties:**
```cpp
simulationType  RAS;

RAS
{
    RASModel        kEpsilon;

    turbulence      on;

    printCoeffs     on;
}
```

### Complete Verification Steps

**Step 1: Compile all components**
```bash
# Compile custom models library
cd $WM_PROJECT_USER_DIR/src/customModels
wmake libso

# Compile function objects
cd $WM_PROJECT_USER_DIR/src/functionObjects/myFieldStats
wmake libso

# Compile solver
cd $WM_PROJECT_USER_DIR/applications/solvers/mySimpleFoam
wmake
```

**Step 2: Verify all binaries exist**
```bash
ls -lh $FOAM_USER_LIBBIN/libcustomModels.so
ls -lh $FOAM_USER_LIBBIN/libmyFunctionObjects.so
ls -lh $FOAM_USER_APPBIN/mySimpleFoam

which mySimpleFoam
```

**Step 3: Prepare and run test case**
```bash
# Create test directory
mkdir -p ~/mySimpleFoamTest
cd ~/mySimpleFoamTest

# Copy all configuration files (create as shown above)
# [Create all files from the examples above]

# Generate mesh
blockMesh

# Check mesh
checkMesh

# Run solver
mySimpleFoam > log.mySimpleFoam 2>&1
```

**Step 4: Verify results**
```bash
# Check for successful model creation
grep "customMomentumSource" log.mySimpleFoam

# Check for viscosity model loading
grep "Selecting viscosity model" log.mySimpleFoam

# Check field statistics
grep "Field Statistics" log.mySimpleFoam

# Verify output files written
ls -lh postProcessing/

# Check convergence
tail -50 log.mySimpleFoam | grep "solution"

# Visualize results (optional)
paraFoam
```

### Expected Complete Output

```
Starting mySimpleFoam solver

No custom viscosity model found. Using standard turbulence model.
Selecting turbulence model: kEpsilon

Created customMomentumSource named momentumSource1 with direction: (0.1 0 0) and magnitude: 5.0

Time = 0
fieldStatistics1: Created fieldStatistics for fields: 2(p U)

Starting time loop

Time = 1
Field Statistics at time: 1
  p:
    Max:     101325.0
    Min:     100000.0
    Average: 100650.5
  U:
    Max:     1.2
    Min:     0.0
    Average: 0.8

ExecutionTime = 12.5 s  ClockTime = 13.2 s

[... continues ...]

Time = 1000
Field Statistics at time: 1000
  p:
    Max:     101350.0
    Min:     99950.0
    Average: 100675.3
  U:
    Max:     1.25
    Min:     0.0
    Average: 0.85

Final field statistics:
  p:
    Max:     101350.0
    Min:     99950.0
    Average: 100675.3
  U:
    Max:     1.25
    Min:     0.0
    Average: 0.85

End
```

---

## Quick Reference Tables

### RTS Registration Macros

| Purpose | Macro | Usage Location |
|---------|-------|----------------|
| Declare type | `TypeName("name")` | Class header |
| Define type | `defineTypeNameAndDebug` | Implementation file |
| Add to table | `addToRunTimeSelectionTable` | Implementation file |
| Declare table | `declareRunTimeSelectionTable` | Base class header |

### Function Object Lifecycle

| Method | When Called | Purpose |
|--------|-------------|---------|
| Constructor | Object creation | Initialize from dictionary |
| read() | Dictionary re-read | Update parameters |
| execute() | Every time step | Perform computations |
| write() | Write time | Output results |
| end() | Simulation end | Finalize and cleanup |

### Library Loading Methods

| Method | Syntax | When Used |
|--------|--------|-----------|
| controlDict | `libs ("libname.so");` | Startup |
| Code API | `dlLibraryTable::open()` | Dynamic |
| fvOptions | Automatic | Model loading |

### Common Make Files

**Library:**
```makefile
FILES = source.C
LIB = $(FOAM_USER_LIBBIN)/libname
```

**Application:**
```makefile
FILES = main.C
EXE = $(FOAM_USER_APPBIN)/appName
```

---

## Key Takeaways

### Architecture Design
- **RTS enables extensibility** through compile-time registration and runtime selection
- **Base classes define interfaces** that derived classes must implement
- **Factory methods** (New) decouple implementation from usage
- **Dynamic libraries** allow adding functionality without recompiling solvers

### Implementation Patterns
- **Always implement complete classes** with proper constructors, destructors, and required methods
- **Register with RTS macros** in implementation files, never in headers
- **Validate input parameters** in constructors with appropriate error handling
- **Follow OpenFOAM conventions** for naming, file organization, and dictionary structure

### Testing and Verification
- **Always verify compilation** produces expected library/executable
- **Test with simple cases** before complex simulations
- **Check log output** for successful model creation and execution
- **Validate results** against analytical solutions or experimental data

### Integration Best Practices
- **Use proper Make files** with correct include paths and library dependencies
- **Load libraries explicitly** in controlDict or through code
- **Configure models** through dictionary files, not hard-coded values
- **Implement error handling** for missing fields, invalid parameters, and failed operations

### Common Pitfalls
- **Missing RTS registration** causes models to be invisible to factory methods
- **Incorrect library paths** prevent dynamic loading at runtime
- **Incomplete method implementations** lead to linker errors or runtime failures
- **Forgotten virtual keywords** break polymorphism and override behavior

---

## Concept Check

<details>
<summary><b>1. What are the three required components for RTS implementation?</b></summary>

**Answer:**
1. `TypeName("name")` - declares the type name in class header
2. `addToRunTimeSelectionTable` - registers class with factory in implementation file
3. Proper constructor matching the base class signature
</details>

<details>
<summary><b>2. Which methods must a Function Object implement?</b></summary>

**Answer:**
- `execute()` - called every time step for computations
- `write()` - called at write times for output
- Optional: `read()`, `end()`, `updateMesh()`, `movePoints()`
</details>

<details>
<summary><b>3. How do you load a custom library in OpenFOAM?</b></summary>

**Answer:**
- **Static loading**: Add to `system/controlDict` with `libs ("libname.so");`
- **Dynamic loading**: Use `dlLibraryTable::open("libname.so")` in code
- **Automatic**: Through model selection when dictionary specifies type
</details>

<details>
<summary><b>4. What is the purpose of the factory method pattern in RTS?</b></summary>

**Answer:**
The factory method (`New()`) provides:
- **Decoupling**: Client code doesn't need to know concrete implementation
- **Extensibility**: New types can be added without modifying existing code
- **Centralized creation**: All object creation goes through one point
- **Error handling**: Validates type names and provides informative errors
</details>

<details>
<summary><b>5. Why do we use `autoPtr` for RTS-created objects?</b></summary>

**Answer:**
`autoPtr` provides:
- **Automatic memory management**: Ensures proper cleanup
- **Ownership transfer**: Clear semantics about who owns the object
- **RAII principles**: Exception-safe resource management
- **OpenFOAM convention**: Consistent with framework practices
</details>

---

## Related Documentation

- **Architecture Overview**: [00_Overview.md](00_Overview.md)
- **RTS Tables**: [02_Runtime_Selection_Tables.md](02_Runtime_Selection_Tables.md)
- **Dynamic Libraries**: [03_Dynamic_Library_Loading.md](03_Dynamic_Library_Loading.md)
- **Function Objects**: [04_FunctionObject_Integration.md](04_FunctionObject_Integration.md)
- **Design Patterns**: [05_Design_Patterns.md](05_Design_Patterns.md)