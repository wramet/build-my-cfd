#include "SpatialDiscretizer.H"

namespace Foam {

// Constructors

SpatialDiscretizer::SpatialDiscretizer(const fvMesh &mesh) : mesh_(mesh) {}

// Member Functions

void SpatialDiscretizer::setScheme(const word &fieldName,
                                   const word &schemeName,
                                   const word &limiterName) {
  schemeRegistry_.insert(fieldName, schemeName);
  if (limiterName != "none") {
    limiterRegistry_.insert(fieldName, limiterName);
  }
}

} // End namespace Foam
