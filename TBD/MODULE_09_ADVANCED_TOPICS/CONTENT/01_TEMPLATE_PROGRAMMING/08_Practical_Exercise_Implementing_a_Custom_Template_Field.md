# แบบฝึกปฏิบัติ: การImplement Custom Template Field

แบบฝึกปฏิบัติที่ครอบคลุมนี้สาธิตวิธีการขยายสถาปัตยกรรม template ที่ทรงพลังของ OpenFOAM โดยการสร้างคลาส `StatisticalField` แบบ custom ที่ติดตามคุณสมบัติทางสถิติโดยอัตโนมัติควบคู่ไปกับค่าของ field นี้แสดงให้เห็นถึงปรัชญาการออกแบบของ OpenFOAM ที่ผสมผสาน C++ template metaprogramming กับ inheritance hierarchies

## ภาพรวมสถาปัตยกรรม

`StatisticalField` ขยายคลาส template `GeometricField` ของ OpenFOAM ซึ่งเป็นพื้นฐานสำหรับ field types ทั้งหมดใน OpenFOAM (volume fields, surface fields, point fields, เป็นต้น) โดยการสืบทอดจาก `GeometricField<Type, fvPatchField, volMesh>` ค่า field แบบ custom ของเราจะได้รับความเข้ากันได้เต็มรูปแบบกับโครงสร้างพื้นฐานที่มีอยู่ของ OpenFOAM ในขณะที่เพิ่มความสามารถในการติดตามสถิติ

## Core Implementation

### Base Template Class Structure

```cpp
template<class Type>
class StatisticalField : public GeometricField<Type, fvPatchField, volMesh>
{
private:
    // Statistical tracking variables
    Type runningMean_;         // Online running mean
    Type runningVariance_;     // Online running variance
    label count_;              // Number of samples
    
    // Internal calculation variables
    Type sum_;                 // Running sum for mean calculation
    Type sumOfSquares_;        // Running sum of squared differences

public:
    // Type definitions for consistency with OpenFOAM conventions
    typedef GeometricField<Type, fvPatchField, volMesh> GeomField;
    
    // Constructors
    StatisticalField(const IOobject& io, const fvMesh& mesh);
    StatisticalField(const IOobject& io, const fvMesh& mesh, const Type& defaultValue);
    StatisticalField(const GeometricField<Type, fvPatchField, volMesh>& field);
    
    // Statistical calculation methods
    void updateStatistics();
    void resetStatistics();
    
    // Access methods
    Type mean() const;
    Type variance() const;
    Type standardDeviation() const;
    Type min() const;
    Type max() const;
    
    // Advanced statistics
    Type coefficientOfVariation() const;
    Type relativeStandardDeviation() const;
    
    // Time integration for statistics
    void timeIntegrateStatistics(const scalar deltaT);
};
```

### Constructor Implementation

```cpp
template<class Type>
StatisticalField<Type>::StatisticalField(const IOobject& io, const fvMesh& mesh)
    : GeomField(io, mesh),
      runningMean_(pTraits<Type>::zero),
      runningVariance_(pTraits<Type>::zero),
      sum_(pTraits<Type>::zero),
      sumOfSquares_(pTraits<Type>::zero),
      count_(0)
{}

template<class Type>
StatisticalField<Type>::StatisticalField(
    const IOobject& io, 
    const fvMesh& mesh, 
    const Type& defaultValue
)
    : GeomField(io, mesh, dimensioned<Type>("zero", dimless, defaultValue)),
      runningMean_(defaultValue),
      runningVariance_(pTraits<Type>::zero),
      sum_(defaultValue * this->size()),
      sumOfSquares_(pTraits<Type>::zero),
      count_(1)
{}
```

## Statistical Algorithm Implementation

### Welford's Algorithm for Numerical Stability

การ implement ใช้ Welford's online algorithm ซึ่งให้เสถียรภาพทางตัวเลขที่ยอดเยี่ยมสำหรับการคำนวณค่าเฉลี่ยและความแปรปรวนในครั้งเดียว:

```cpp
template<class Type>
void StatisticalField<Type>::updateStatistics()
{
    // Reset counters
    count_ = 0;
    runningMean_ = pTraits<Type>::zero;
    runningVariance_ = pTraits<Type>::zero;
    sum_ = pTraits<Type>::zero;
    sumOfSquares_ = pTraits<Type>::zero;
    
    // Calculate statistics over all internal field cells
    forAll(this->internalField(), celli)
    {
        Type value = this->internalField()[celli];
        
        // Update count
        count_++;
        
        // Calculate new mean using Welford's algorithm
        Type delta = value - runningMean_;
        runningMean_ += delta / count_;
        
        // Calculate new variance
        Type delta2 = value - runningMean_;
        runningVariance_ += delta * delta2;
        
        // Maintain running sums for additional calculations
        sum_ += value;
        sumOfSquares_ += value * value;
    }
}
```

### Specialized Access Methods

```cpp
template<class Type>
Type StatisticalField<Type>::mean() const
{
    return count_ > 0 ? runningMean_ : pTraits<Type>::zero;
}

template<class Type>
Type StatisticalField<Type>::variance() const
{
    return count_ > 1 ? runningVariance_ / (count_ - 1) : pTraits<Type>::zero;
}

template<class Type>
Type StatisticalField<Type>::standardDeviation() const
{
    Type var = variance();
    return sqrt(var);
}

template<class Type>
Type StatisticalField<Type>::coefficientOfVariation() const
{
    Type meanVal = mean();
    Type stdDev = standardDeviation();
    
    Type result = pTraits<Type>::zero;
    for (direction comp = 0; comp < pTraits<Type>::nComponents; comp++)
    {
        if (component(meanVal, comp) > VSMALL)
        {
            setComponent(result, comp, component(stdDev, comp) / component(meanVal, comp));
        }
    }
    
    return result;
}
```

## Specialization for Scalar Fields

สเปเชียลไลเซชันสำหรับ scalar field ให้ฟังก์ชันสถิติเพิ่มเติมที่ใช้กันทั่วไปในการวิเคราะห์ CFD:

```cpp
template<>
class StatisticalField<scalar> : public StatisticalField<scalar>
{
private:
    scalar runningSum3_;      // For skewness calculation
    scalar runningSum4_;      // For kurtosis calculation
    
public:
    // Constructors inherit from base class
    StatisticalField(const IOobject& io, const fvMesh& mesh)
        : StatisticalField<scalar>(io, mesh),
          runningSum3_(0.0),
          runningSum4_(0.0) {}
    
    // Additional statistical moments
    scalar skewness() const;
    scalar kurtosis() const;
    scalar excessKurtosis() const;
    
    // Percentile calculations
    scalar percentile(const scalar p) const;
    scalar median() const { return percentile(0.5); }
    scalar firstQuartile() const { return percentile(0.25); }
    scalar thirdQuartile() const { return percentile(0.75); }
    
    // Range statistics
    scalar range() const;
    scalar interquartileRange() const;
    
    // Distribution analysis
    scalar RMS() const;
    scalar RMSE(const StatisticalField<scalar>& reference) const;
};
```

### Advanced Statistical Implementations

```cpp
scalar StatisticalField<scalar>::skewness() const
{
    if (count_ < 3) return 0.0;
    
    scalar meanVal = mean();
    scalar stdDev = standardDeviation();
    
    if (stdDev < VSMALL) return 0.0;
    
    // Calculate third central moment
    scalar thirdMoment = 0.0;
    forAll(this->internalField(), celli)
    {
        scalar value = this->internalField()[celli];
        scalar deviation = value - meanVal;
        thirdMoment += pow(deviation, 3);
    }
    thirdMoment /= count_;
    
    // Skewness = third moment / standard deviation^3
    return thirdMoment / pow(stdDev, 3);
}

scalar StatisticalField<scalar>::kurtosis() const
{
    if (count_ < 4) return 0.0;
    
    scalar meanVal = mean();
    scalar stdDev = standardDeviation();
    
    if (stdDev < VSMALL) return 0.0;
    
    // Calculate fourth central moment
    scalar fourthMoment = 0.0;
    forAll(this->internalField(), celli)
    {
        scalar value = this->internalField()[celli];
        scalar deviation = value - meanVal;
        fourthMoment += pow(deviation, 4);
    }
    fourthMoment /= count_;
    
    // Kurtosis = fourth moment / standard deviation^4
    return fourthMoment / pow(stdDev, 4);
}

scalar StatisticalField<scalar>::percentile(const scalar p) const
{
    if (p < 0.0 || p > 1.0) return 0.0;
    if (count_ == 0) return 0.0;
    
    // Create sorted copy of field values
    List<scalar> sortedValues(this->size());
    forAll(this->internalField(), celli)
    {
        sortedValues[celli] = this->internalField()[celli];
    }
    std::sort(sortedValues.begin(), sortedValues.end());
    
    // Calculate percentile using linear interpolation
    scalar index = p * (count_ - 1);
    label lowerIndex = std::floor(index);
    label upperIndex = std::ceil(index);
    
    if (lowerIndex == upperIndex)
    {
        return sortedValues[lowerIndex];
    }
    
    scalar fraction = index - lowerIndex;
    return sortedValues[lowerIndex] * (1.0 - fraction) + 
           sortedValues[upperIndex] * fraction;
}
```

## Integration with OpenFOAM Ecosystem

### File I/O Operations

```cpp
template<class Type>
void StatisticalField<Type>::writeStats(Ostream& os) const
{
    os << "StatisticalField Statistics:" << nl
       << "  Count: " << count_ << nl
       << "  Mean: " << mean() << nl
       << "  Variance: " << variance() << nl
       << "  Standard Deviation: " << standardDeviation() << nl
       << "  Min: " << min() << nl
       << "  Max: " << max() << nl
       << "  Range: " << (max() - min()) << nl;
}

template<>
void StatisticalField<scalar>::writeStats(Ostream& os) const
{
    StatisticalField<scalar>::writeStats(os);
    os << "  Skewness: " << skewness() << nl
       << "  Kurtosis: " << kurtosis() << nl
       << "  Median: " << median() << nl
       << "  Interquartile Range: " << interquartileRange() << nl;
}
```

### Time Integration Support

```cpp
template<class Type>
void StatisticalField<Type>::timeIntegrateStatistics(const scalar deltaT)
{
    if (deltaT <= 0.0) return;
    
    // Create time-weighted statistics
    Type timeWeightedMean = runningMean_ * deltaT;
    Type timeWeightedVariance = runningVariance_ * deltaT;
    
    // Store for temporal analysis
    if (!timeHistory_.found(this->time().timeName()))
    {
        timeHistory_.insert(this->time().timeName(), List<Type>(3));
    }
    
    List<Type>& historyEntry = timeHistory_[this->time().timeName()];
    historyEntry[0] = timeWeightedMean;
    historyEntry[1] = timeWeightedVariance;
    historyEntry[2] = runningMean_; // Store instantaneous mean
}
```

## Usage Examples

### Creating and Using Statistical Fields

```cpp
// Create a statistical velocity field
volVectorField U(IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);
StatisticalField<vector> statU(IOobject("statU", runTime.timeName(), mesh, IOobject::NO_READ), mesh);
statU = U;  // Copy current velocity field

// Update statistics
statU.updateStatistics();

// Access statistical information
vector meanVelocity = statU.mean();
vector velocityStdDev = statU.standardDeviation();
Info << "Mean velocity: " << meanVelocity << nl;
Info << "Velocity std dev: " << velocityStdDev << nl;

// For scalar fields with additional statistics
volScalarField p(IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ), mesh);
StatisticalField<scalar> statP(IOobject("statP", runTime.timeName(), mesh, IOobject::NO_READ), mesh);
statP = p;
statP.updateStatistics();

Info << "Pressure statistics:" << nl;
Info << "  Mean: " << statP.mean() << nl;
Info << "  Variance: " << statP.variance() << nl;
Info << "  Skewness: " << statP.skewness() << nl;
Info << "  Kurtosis: " << statP.kurtosis() << nl;
```

### Integration in Solver Workflow

```cpp
// Inside a time loop of a solver
while (runTime.loop())
{
    // Solve equations...
    solve(UEqn == -fvc::grad(p));
    
    // Update statistical tracking
    statU.updateStatistics();
    
    // Write statistics for analysis
    if (runTime.outputTime())
    {
        statU.writeStats(Info);
        
        // Write statistical field for post-processing
        statU.write();
    }
}
```

## Compile-Time Integration

### Make/files Configuration

```
StatisticalField.C
StatisticalFieldTemplates.C

EXE = $(FOAM_USER_APPBIN)/statisticalFieldTest
```

### Make/options Configuration

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/OpenFOAM/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lOpenFOAM \
    -lmeshTools
```

แบบฝึกปฏิบัตินี้สาธิตวิธีการที่สถาปัตยกรรม template ของ OpenFOAM ช่วยให้ **domain-specific extensions** ในขณะที่ยังคงความเข้ากันได้เต็มรูปแบบกับโครงสร้างพื้นฐานที่มีอยู่ statistical field สามารถใช้ได้ทุกที่ที่ OpenFOAM field ทั่วไปสามารถใช้ได้ รวมถึง boundary conditions, interpolation schemes, และ solver equations ในขณะที่ให้ความสามารถในการวิเคราะห์เพิ่มเติมสำหรับการวิจัยและการตรวจสอบ CFD
