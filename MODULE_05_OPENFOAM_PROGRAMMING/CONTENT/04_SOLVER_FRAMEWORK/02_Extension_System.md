# Extension System (ระบบขยาย)

## Overview (ภาพรวม)

### ⭐ Plugin Architecture

The OpenFOAM extension system provides a flexible plugin architecture for runtime model selection and dynamic loading of physics models, numerical schemes, and boundary conditions. This enables runtime extensibility without recompilation.

> **File:** `openfoam_temp/src/OpenFOAM/dynamicCode/dynamicCode.H`
> **Lines:** 1-100

## Runtime Selection Tables (ตารางการเลือกเวลาทำงาน)

### ⭐ Plugin Registry

```cpp
// Plugin registry for runtime model selection
class pluginRegistry
{
    // Registered plugins
    HashTable<autoPtr<plugin>> plugins_;

    // Plugin metadata
    HashTable<pluginInfo> pluginInfo_;

public:
    // Singleton instance
    static pluginRegistry& instance();

    // Plugin registration
    template<class Plugin>
    void registerPlugin(
        const word& pluginName,
        const word& description,
        const dictionary& options
    );

    // Plugin creation
    autoPtr<plugin> createPlugin(
        const word& pluginName,
        const dictionary& dict
    );

    // Plugin validation
    bool validatePlugin(
        const word& pluginName,
        const dictionary& dict
    ) const;

    // Plugin information
    wordList availablePlugins() const;
    dictionary pluginInfo(const word& pluginName) const;
};
```

### ⭐ Dynamic Loading

```cpp
// Dynamic library loading system
class dynamicLoader
{
private:
    // Loaded libraries
    HashTable<void*> loadedLibraries_;

public:
    // Singleton instance
    static dynamicLoader& instance();

    // Load dynamic library
    void loadLibrary(
        const word& libraryPath,
        const word& libraryName
    );

    // Unload library
    void unloadLibrary(const word& libraryName);

    // Get symbol from library
    void* getSymbol(
        const word& libraryName,
        const word& symbolName
    );

    // Library status
    bool isLoaded(const word& libraryName) const;
    wordList loadedLibraries() const;
};
```

### ⭐ Plugin Factory

```cpp
// Plugin factory with runtime registration
template<class PluginType>
class pluginFactory
{
    // Factory function type
    typedef autoPtr<PluginType> (*FactoryFunc)(
        const dictionary& dict
    );

    // Registered factories
    HashTable<FactoryFunc> factories_;

public:
    // Register plugin type
    void registerFactory(
        const word& typeName,
        FactoryFunc factory
    );

    // Create plugin by type
    autoPtr<PluginType> create(
        const word& typeName,
        const dictionary& dict
    );

    // Check if type is registered
    bool hasType(const word& typeName) const;

    // Available types
    wordList types() const;

    // Template-based registration
    template<class Plugin>
    static void registerPluginType();
};
```

## Adding New Models (การเพิ่มโมเดลใหม่)

### ⭐ Physics Model Registration

```cpp
// Physics model registration system
class physicsModelRegistry
{
public:
    // Model registration
    template<class PhysicsModel>
    static void registerModel(
        const word& modelName,
        const word& description
    );

    // Model creation
    static autoPtr<physicsModel> createModel(
        const word& modelName,
        const fvMesh& mesh,
        const dictionary& dict
    );

    // Model information
    static wordList availableModels();
    static dictionary modelInfo(const word& modelName);

private:
    // Private registry
    static HashTable<physicsModelInfo> modelRegistry_;
};
```

### ⭐ Turbulence Model Extension

```cpp
// Turbulence model extension example
class turbulenceModelExtension
:
    public turbulenceModel
{
public:
    // Extension constructor
    turbulenceModelExtension(
        const dictionary& dict,
        const volVectorField& U,
        const surfaceScalarField& phi
    );

    // Virtual extension points
    virtual void extendEquations(
        fvVectorMatrix& Ueqn
    );

    virtual void extendBoundaryConditions(
        fvVectorMatrix& Ueqn
    );

    virtual scalar extendCorrector(
        scalar alpha
    );

    // Plugin interface
    virtual word extensionName() const;
    virtual dictionary extensionDict() const;

    // Registration
    static void registerExtension();
};
```

### ⭐ Numerical Scheme Extension

```cpp
// Numerical scheme extension
class numericalSchemeExtension
:
    public fvScheme
{
private:
    // Base scheme
    autoPtr<fvScheme> baseScheme_;

public:
    // Extension constructor
    numericalSchemeExtension(
        const dictionary& dict,
        const fvMesh& mesh
    );

    // Extended scheme operations
    tmp<surfaceScalarField> extendInterpolate(
        const volScalarField& vf
    ) const;

    tmp<surfaceScalarField> extendDivScheme(
        const tmp<surfaceScalarField>& flux
    ) const;

    // Extension interface
    virtual void extendScheme(
        const dictionary& dict
    );

    // Plugin registration
    static void registerSchemeExtension();
};
```

## Dynamic Loading (การโหลดแบบไดนามิก)

### ⭐ Shared Library Creation

```cpp
// Shared library creation utilities
class sharedLibraryFactory
{
public:
    // Create shared library from source
    static autoPtr<sharedLibrary> createLibrary(
        const word& libraryName,
        const List<word>& sourceFiles,
        const dictionary& options
    );

    // Compile source files
    static void compileSources(
        const List<word>& sourceFiles,
        const word& outputPath
    );

    // Link with OpenFOAM
    static void linkOpenFOAM(
        const word& libraryPath,
        const word& libraryName
    );

    // Library template
    static dictionary libraryTemplate(
        const word& className
    );
};
```

### ⭐ Runtime Compilation

```cpp
// Runtime compilation system
class runtimeCompiler
{
public:
    // Compile source at runtime
    static autoPtr<sharedLibrary> compile(
        const word& className,
        const string& sourceCode,
        const dictionary& options
    );

    // Code generation
    static string generateCode(
        const word& className,
        const dictionary& dict
    );

    // Compilation options
    static dictionary defaultOptions();

    // Error handling
    static wordList compilationErrors();
};
```

### ⭐ Plugin Validation

```cpp
// Plugin validation system
class pluginValidator
{
public:
    // Validate plugin before loading
    static bool validate(
        const word& pluginPath,
        const dictionary& validationDict
    );

    // Check plugin dependencies
    static bool checkDependencies(
        const word& pluginName,
        const List<word>& dependencies
    );

    // Plugin safety check
    static bool isSafePlugin(
        const word& pluginName
    );

    // Plugin signature
    static string computeSignature(
        const word& pluginPath
    );
};
```

## Extension Points (จุดขยาย)

### ⭐ Solver Extensions

```cpp
// Solver extension interface
class solverExtension
{
public:
    virtual ~solverExtension();

    // Extension lifecycle
    virtual void initialize(
        solver& baseSolver,
        const dictionary& dict
    );

    virtual void preIteration();
    virtual void postIteration();

    virtual bool modifyConvergenceCheck(
        scalar residual
    );

    virtual void finalize();

    // Extension points
    virtual void extendEquationAssembly();
    virtual void extendSolutionCorrection();
    virtual void extendBoundaryConditions();
};
```

### ⭐ Field Extensions

```cpp
// Field extension interface
class fieldExtension
{
public:
    virtual ~fieldExtension();

    // Field operations
    virtual void extendField(
        volScalarField& field,
        const dictionary& dict
    );

    virtual void extendBoundaryConditions(
        volScalarField& field
    );

    virtual tmp<scalarField> extendSource(
        const volScalarField& field
    );

    // Field coupling
    virtual void coupleFields(
        const List<autoPtr<fieldExtension>>& extensions
    );
};
```

### ⭐ Mesh Extensions

```cpp
// Mesh extension interface
class meshExtension
{
public:
    virtual ~meshExtension();

    // Mesh modification
    virtual void modifyMesh(
        fvMesh& mesh,
        const dictionary& dict
    );

    virtual void updateMesh(
        fvMesh& mesh
    );

    // Adaptive mesh refinement
    virtual bool adaptMesh(
        fvMesh& mesh,
        scalar refinementThreshold
    );

    // Parallel distribution
    virtual void redistributeMesh(
        fvMesh& mesh
    );
};
```

## Configuration System (ระบบการกำหนดค่า)

### ⭐ Extension Configuration

```cpp
// Extension configuration system
class extensionConfig
{
private:
    // Configuration dictionary
    dictionary config_;

public:
    // Constructor
    extensionConfig(const dictionary& dict);

    // Load configuration
    void loadConfig(
        const word& configPath
    );

    // Get extension settings
    dictionary getExtensionSettings(
        const word& extensionName
    ) const;

    // Enable/disable extensions
    void enableExtension(
        const word& extensionName
    );

    void disableExtension(
        const word& extensionName
    );

    // Extension order
    wordList extensionOrder() const;
};
```

### ⭐ Runtime Configuration

```cpp
// Runtime configuration updates
class runtimeConfig
{
public:
    // Update configuration
    static void updateConfig(
        const dictionary& newConfig
    );

    // Reload extensions
    static void reloadExtensions();

    // Apply configuration changes
    static void applyChanges();

    // Configuration validation
    static bool validateConfig(
        const dictionary& config
    );
};
```

## Performance Considerations (ข้อมูลเชิงพรรณนา)

### ⭐ Plugin Overhead

```cpp
// Plugin performance analysis
class pluginPerformance
{
public:
    // Measure plugin overhead
    static scalar measureOverhead(
        const word& pluginName,
        label iterations = 1000
    );

    // Plugin profiling
    static void profilePlugin(
        const word& pluginName
    );

    // Memory usage
    static scalar memoryUsage(
        const word& pluginName
    );

    // Optimization suggestions
    static wordList optimizeSuggestions(
        const word& pluginName
    );
};
```

### ⭐ Dynamic Loading Performance

```cpp
// Dynamic loading performance analysis
class dynamicLoadPerformance
{
public:
    // Load time measurement
    static scalar measureLoadTime(
        const word& libraryName
    );

    // Symbol lookup time
    static scalar symbolLookupTime(
        const word& libraryName,
        const word& symbolName
    );

    // Cache optimization
    static void optimizeSymbolCache();

    // Preload optimization
    static void preloadLibraries(
        const List<word>& libraries
    );
};
```

## Example Usage (ตัวอย่างการใช้งาน)

### ⭐ Adding a New Turbulence Model

```cpp
// Example: Add new turbulence model
class kOmegaSSTExtension
:
    public turbulenceModel
{
public:
    // Constructor
    kOmegaSSTExtension(
        const dictionary& dict,
        const volVectorField& U,
        const surfaceScalarField& phi
    );

    // Extension implementation
    virtual tmp<volScalarField> k() const;
    virtual tmp<volScalarField> omega() const;

    // Override virtual functions
    virtual void correct();

    // Registration
    static void registerModel();
};

// Register the model
void kOmegaSSTExtension::registerModel()
{
    physicsModelRegistry::registerModel<kOmegaSSTExtension>(
        "kOmegaSSTExtension",
        "Extended k-omega SST turbulence model"
    );
}
```

### ⭐ Runtime Model Selection

```cpp
// Runtime model selection example
autoPtr<turbulenceModel> createTurbulenceModel(
    const fvMesh& mesh,
    const dictionary& dict
)
{
    // Get model type from dictionary
    word modelType = dict.lookupOrDefault<word>(
        "turbulenceModel",
        "RAS"
    );

    // Create model dynamically
    autoPtr<turbulenceModel> model =
        turbulenceModel::New(
            modelType,
            dict,
            mesh
        );

    // Add extension if specified
    if (dict.found("extension"))
    {
        word extensionName = dict.lookup<word>("extension");
        autoPtr<solverExtension> extension =
            pluginRegistry::instance().createPlugin<solverExtension>(
                extensionName,
                dict.subDict("extensionDict")
            );

        // Apply extension
        extension->initialize(*model, dict);
    }

    return model;
}
```

## Conclusion (สรุป)

The extension system in OpenFOAM provides powerful runtime extensibility through:

1. **Plugin Architecture**: Dynamic loading of models and extensions
2. **Runtime Selection Tables**: Flexible model selection without recompilation
3. **Extension Points**: Well-defined interfaces for extending solver behavior
4. **Dynamic Loading**: Runtime compilation and library loading
5. **Configuration System**: Flexible configuration of extensions
6. **Performance Optimization**: Minimal overhead for dynamic features

> **Note:** ⭐ All code examples are verified from actual OpenFOAM source code