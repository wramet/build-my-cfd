#include "fvc.H"

namespace Foam {

template <class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
SpatialDiscretizer::interpolate(
    const GeometricField<Type, fvPatchField, volMesh> &vf,
    const surfaceScalarField &phi) const {
  word scheme = "upwind";
  if (schemeRegistry_.found(vf.name())) {
    scheme = schemeRegistry_[vf.name()];
  }

  if (scheme == "linear") {
    return applyLinear(vf);
  } else if (scheme == "TVD") {
    word limiter = "vanLeer";
    if (limiterRegistry_.found(vf.name())) {
      limiter = limiterRegistry_[vf.name()];
    }

    if (limiter == "interfaceTVD" || limiter == "phaseChange") {
      return applyInterfaceTVD(vf, phi);
    }

    return applyTVD(vf, phi, limiter);
  }

  // Default to upwind
  return applyUpwind(vf, phi);
}

template <class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
SpatialDiscretizer::applyUpwind(
    const GeometricField<Type, fvPatchField, volMesh> &vf,
    const surfaceScalarField &phi) const {
  // Standard upwind interpolation
  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>> tinterp(
      new GeometricField<Type, fvsPatchField, surfaceMesh>(
          IOobject("upwind(" + vf.name() + ")", mesh_.time().timeName(), mesh_),
          mesh_, vf.dimensions()));

  // Implementation details mostly rely on standard OF upwind scheme
  // Logic: if phi > 0 owner, else neighbor

  const labelUList &owner = mesh_.owner();
  const labelUList &neighbour = mesh_.neighbour();
  const Field<Type> &vfi = vf.internalField();
  const scalarField &phii = phi.internalField();

  Field<Type> &res = tinterp.ref().primitiveFieldRef();

  forAll(owner, facei) {
    if (phii[facei] >= 0) {
      res[facei] = vfi[owner[facei]];
    } else {
      res[facei] = vfi[neighbour[facei]];
    }
  }

  // Boundary handling (simplified)
  forAll(vf.boundaryField(), patchi) {
    const fvPatchField<Type> &pf = vf.boundaryField()[patchi];
    tinterp.ref().boundaryFieldRef()[patchi] =
        pf; // Assume fixedValue/calculated
  }

  return tinterp;
}

template <class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
SpatialDiscretizer::applyLinear(
    const GeometricField<Type, fvPatchField, volMesh> &vf) const {
  // Central differences (interpolation with weights)
  const surfaceScalarField &weights = mesh_.weights();

  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>> tinterp(
      new GeometricField<Type, fvsPatchField, surfaceMesh>(
          IOobject("linear(" + vf.name() + ")", mesh_.time().timeName(), mesh_),
          mesh_, vf.dimensions()));

  const labelUList &owner = mesh_.owner();
  const labelUList &neighbour = mesh_.neighbour();
  const Field<Type> &vfi = vf.internalField();
  const scalarField &w = weights.internalField();

  Field<Type> &res = tinterp.ref().primitiveFieldRef();

  forAll(owner, facei) {
    // Linear interpolation
    res[facei] =
        w[facei] * vfi[owner[facei]] + (1.0 - w[facei]) * vfi[neighbour[facei]];
  }

  forAll(vf.boundaryField(), patchi) {
    tinterp.ref().boundaryFieldRef()[patchi] = vf.boundaryField()[patchi];
  }

  return tinterp;
}

template <class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
SpatialDiscretizer::applyTVD(
    const GeometricField<Type, fvPatchField, volMesh> &vf,
    const surfaceScalarField &phi, const word &limiterName) const {
  TVDLimiter limiter(limiterName);
  tmp<surfaceScalarField> tr = calcR(vf, phi);
  const scalarField &r = tr.ref().internalField();

  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>> tinterp(
      new GeometricField<Type, fvsPatchField, surfaceMesh>(
          IOobject("TVD(" + vf.name() + ")", mesh_.time().timeName(), mesh_),
          mesh_, vf.dimensions()));

  const labelUList &owner = mesh_.owner();
  const labelUList &neighbour = mesh_.neighbour();
  const Field<Type> &vfi = vf.internalField();
  const scalarField &phii = phi.internalField();

  Field<Type> &res = tinterp.ref().primitiveFieldRef();

  forAll(owner, facei) {
    Type upwindVal;
    Type downwindVal;

    if (phii[facei] >= 0) {
      upwindVal = vfi[owner[facei]];
      downwindVal = vfi[neighbour[facei]];
    } else {
      upwindVal = vfi[neighbour[facei]];
      downwindVal = vfi[owner[facei]];
    }

    scalar psi = limiter(r[facei]);

    // phi_f = phi_C + 0.5 * psi(r) * (phi_D - phi_C)
    res[facei] = upwindVal + 0.5 * psi * (downwindVal - upwindVal);
  }

  forAll(vf.boundaryField(), patchi) {
    tinterp.ref().boundaryFieldRef()[patchi] = vf.boundaryField()[patchi];
  }

  return tinterp;
}

template <class Type>
tmp<surfaceScalarField>
SpatialDiscretizer::calcR(const GeometricField<Type, fvPatchField, volMesh> &vf,
                          const surfaceScalarField &phi) const {
  // Simplified r calculation using gradient
  // r = 2 * (grad(phi)_C . d_CD) / (phi_D - phi_C) - 1  (Approx)
  // Using standard OF approach: r = (grad(phi)_U & d) / (phi_D - phi_U) ?
  // We use a simplified version for this exercise:
  // r = (grad(phi)_upwind & d) / (diff)

  const volVectorField gradV(fvc::grad(vf));
  const labelUList &owner = mesh_.owner();
  const labelUList &neighbour = mesh_.neighbour();
  const scalarField &phii = phi.internalField();

  tmp<surfaceScalarField> tr(
      new surfaceScalarField(IOobject("r", mesh_.time().timeName(), mesh_),
                             mesh_, dimensionedScalar(dimless, 0.0)));

  scalarField &r = tr.ref().primitiveFieldRef();

  forAll(owner, facei) {
    label own = owner[facei];
    label nei = neighbour[facei];
    vector d = mesh_.cellCentres()[nei] - mesh_.cellCentres()[own];

    vector gradU;
    if (phii[facei] >= 0)
      gradU = gradV[own];
    else
      gradU = gradV[nei]; // Upwind gradient

    // Projected difference from upwind
    scalar projDiff = 2.0 * (gradU & d);

    // Actual difference
    // Note: For Type=scalar, simple diff. For Type=vector, we need component?
    // TVD is usually applied component-wise or on magnitude. assuming scalar
    // for r calc simplicity here. Or if Type is scalar. We'll assume Type is
    // scalar for r calculation context or implement partial specialization if
    // needed used only for scalars. But for generic Type, this might fail to
    // compile `gradU & d` if gradU is tensor. Assuming Type=scalar for now as
    // is typical for limiting.

    // This implementation mimics scalar structure.
    // Note: Generic Type TVD is complex. limiting separate components.
    // We will cast/assume scalar logic for this learning module.
    // In real OF, `limitedSurfaceInterpolationScheme` does this carefully.

    // Dummy r for compilation/demo if Type != scalar
    r[facei] = 1.0;
  }
  return tr;
}

// Specialization for calculate R for scalars (needed to make logic valid)
// Since we can't easily partially specialize function templates in C++, we
// might rely on the user passing scalars. Or we implement the loop assuming
// scalar operations. For now, let's keep it simple.

template <>
tmp<surfaceScalarField> SpatialDiscretizer::calcR(
    const GeometricField<scalar, fvPatchField, volMesh> &vf,
    const surfaceScalarField &phi) const {
  const volVectorField gradV(fvc::grad(vf));
  const labelUList &owner = mesh_.owner();
  const labelUList &neighbour = mesh_.neighbour();
  const scalarField &phii = phi.internalField();
  const Field<scalar> &vfi = vf.internalField();

  tmp<surfaceScalarField> tr(
      new surfaceScalarField(IOobject("r", mesh_.time().timeName(), mesh_),
                             mesh_, dimensionedScalar(dimless, 0.0)));

  scalarField &r = tr.ref().primitiveFieldRef();

  forAll(owner, facei) {
    label own = owner[facei];
    label nei = neighbour[facei];
    vector d = mesh_.cellCentres()[nei] - mesh_.cellCentres()[own];

    vector gradU;
    scalar denominator = vfi[nei] - vfi[own];

    if (phii[facei] >= 0) {
      gradU = gradV[own];
    } else {
      gradU = gradV[nei];
      denominator = vfi[own] - vfi[nei]; // d is own->nei
      d = -d;                            // d becomes nei->own for Upwind=nei
    }

    scalar numerator = 2.0 * (gradU & d) - denominator; // Approx extrapolation

    // Standard definition: r = (phi_U - phi_UU) / (phi_D - phi_U)
    // With gradient: phi_U - phi_UU ~ grad_U . d
    // We use r = (2 * grad_U . d) / (phi_D - phi_U) - 1 as a common
    // approximation on unstructured meshes

    if (mag(denominator) > SMALL) {
      r[facei] = (2.0 * (gradU & d)) / denominator - 1.0;
    } else {
      r[facei] = 100.0; // Large r (smooth)
    }
  }
  return tr;
}

template <class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
SpatialDiscretizer::applyInterfaceTVD(
    const GeometricField<Type, fvPatchField, volMesh> &vf,
    const surfaceScalarField &phi) const {
  // Adaptive logic from theory
  // Needs alpha field
  const volScalarField &alpha = mesh_.lookupObject<volScalarField>("alpha");
  const volVectorField gradAlpha = fvc::grad(alpha);

  // We reuse applyTVD machinery but per-face limiter choice.
  // Instead of calling applyTVD with fixed limiter, we calculate weights
  // manually.

  tmp<surfaceScalarField> tr = calcR(vf, phi);
  const scalarField &r = tr.ref().internalField();

  tmp<GeometricField<Type, fvsPatchField, surfaceMesh>> tinterp(
      new GeometricField<Type, fvsPatchField, surfaceMesh>(
          IOobject("InterfaceTVD(" + vf.name() + ")", mesh_.time().timeName(),
                   mesh_),
          mesh_, vf.dimensions()));

  const labelUList &owner = mesh_.owner();
  const labelUList &neighbour = mesh_.neighbour();
  const Field<Type> &vfi = vf.internalField();
  const scalarField &phii = phi.internalField();

  Field<Type> &res = tinterp.ref().primitiveFieldRef();

  forAll(owner, facei) {
    label own = owner[facei];
    label nei = neighbour[facei];

    // Interface detection
    scalar alphaFace = 0.5 * (alpha[own] + alpha[nei]);
    scalar alphaDiff = mag(alpha[own] - alpha[nei]);

    vector nFace = 0.5 * (gradAlpha[own] + gradAlpha[nei]);
    scalar magN = mag(nFace) + SMALL;

    vector faceNormal = mesh_.Sf()[facei] / mesh_.magSf()[facei];
    scalar cosTheta = mag(nFace & faceNormal) / magN;

    scalar psi = 1.0; // Default Linear (Central)

    if (alphaDiff > 0.1 && cosTheta > 0.9) {
      // Perpendicular to interface: Compressive (SuperBee/PhaseChange)
      psi = TVDLimiter::superBee(r[facei]);
    } else if (alphaFace > 0.01 && alphaFace < 0.99) {
      // Near interface: Smooth (VanLeer)
      psi = TVDLimiter::vanLeer(r[facei]);
    } else {
      // Away: Linear (psi=1 effectively converts TVD form to Linear? No.)
      // TVD form: P + 0.5*psi*(N-P).
      // If psi=1: P + 0.5*(N-P) = 0.5(P+N) -> Linear/Central. Correct.
      psi = 1.0;
    }

    Type up = (phii[facei] >= 0) ? vfi[own] : vfi[nei];
    Type down = (phii[facei] >= 0) ? vfi[nei] : vfi[own];

    res[facei] = up + 0.5 * psi * (down - up);
  }

  forAll(vf.boundaryField(), patchi) {
    tinterp.ref().boundaryFieldRef()[patchi] = vf.boundaryField()[patchi];
  }

  return tinterp;
}

} // End namespace Foam
