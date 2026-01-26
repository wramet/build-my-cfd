/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2026 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
Description
    Class to handle spatial discretization schemes.
    Manages selection and application of Upwind, Linear, and TVD schemes.

\*---------------------------------------------------------------------------*/

#ifndef SpatialDiscretizer_H
#define SpatialDiscretizer_H

#include "fvMesh.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "TVDLimiter.H"
#include "HashTable.H"

namespace Foam {

/*---------------------------------------------------------------------------*\
                         Class SpatialDiscretizer Declaration
\*---------------------------------------------------------------------------*/

class SpatialDiscretizer {
  // Private Data

  //- Reference to mesh
  const fvMesh &mesh_;

  //- Registry of selected schemes for fields
  //  Key: fieldName, Value: schemeName
  HashTable<word> schemeRegistry_;

  //- Registry of limiters for TVD schemes
  //  Key: fieldName, Value: limiterName
  HashTable<word> limiterRegistry_;

  // Private Member Functions

  //- Calculate gradient ratio r for TVD
  template <class Type>
  tmp<surfaceScalarField>
  calcR(const GeometricField<Type, fvPatchField, volMesh> &vf,
        const surfaceScalarField &phi) const;

  //- Apply Upwind scheme
  template <class Type>
  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
  applyUpwind(const GeometricField<Type, fvPatchField, volMesh> &vf,
              const surfaceScalarField &phi) const;

  //- Apply Linear (Central) scheme
  template <class Type>
  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
  applyLinear(const GeometricField<Type, fvPatchField, volMesh> &vf) const;

  //- Apply TVD scheme
  template <class Type>
  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
  applyTVD(const GeometricField<Type, fvPatchField, volMesh> &vf,
           const surfaceScalarField &phi, const word &limiterName) const;

  //- Apply Adaptive Interface TVD scheme
  template <class Type>
  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
  applyInterfaceTVD(const GeometricField<Type, fvPatchField, volMesh> &vf,
                    const surfaceScalarField &phi) const;

public:
  // Constructors

  //- Construct from mesh
  SpatialDiscretizer(const fvMesh &mesh);

  // Member Functions

  //- Set scheme for a field
  void setScheme(const word &fieldName, const word &schemeName,
                 const word &limiterName = "none");

  //- Interpolate field to faces using configured scheme
  template <class Type>
  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
  interpolate(const GeometricField<Type, fvPatchField, volMesh> &vf,
              const surfaceScalarField &phi) const;
};

// Template implementations
#include "SpatialDiscretizerTemplates.C"

} // End namespace Foam

#endif
