#include "TVDLimiter.H"
#include <algorithm> // For standard math if OF not available, but usually we use Foam::mag
#include <cmath>

namespace Foam {

// Constructors

TVDLimiter::TVDLimiter(const word &limiterName) {
  if (limiterName == "minmod")
    type_ = MINMOD;
  else if (limiterName == "vanLeer")
    type_ = VAN_LEER;
  else if (limiterName == "vanAlbada")
    type_ = VAN_ALBADA;
  else if (limiterName == "superBee")
    type_ = SUPER_BEE;
  else if (limiterName == "phaseChange")
    type_ = PHASE_CHANGE;
  else {
    // Default to vanLeer or warn (here default to vanLeer)
    type_ = VAN_LEER;
  }
}

TVDLimiter::TVDLimiter(const limiterType type) : type_(type) {}

// Member Functions

scalar TVDLimiter::operator()(const scalar r) const {
  switch (type_) {
  case MINMOD:
    return minmod(r);
  case VAN_LEER:
    return vanLeer(r);
  case VAN_ALBADA:
    return vanAlbada(r);
  case SUPER_BEE:
    return superBee(r);
  case PHASE_CHANGE:
    return phaseChange(r);
  default:
    return 0.0;
  }
}

scalar TVDLimiter::minmod(const scalar r) {
  // max(0, min(1, r))
  return std::max(0.0, std::min(1.0, r));
}

scalar TVDLimiter::vanLeer(const scalar r) {
  // (r + |r|) / (1 + |r|)
  return (r + std::abs(r)) / (1.0 + std::abs(r));
}

scalar TVDLimiter::vanAlbada(const scalar r) {
  // (r^2 + r) / (r^2 + 1)
  return (r * r + r) / (r * r + 1.0);
}

scalar TVDLimiter::superBee(const scalar r) {
  // max(0, max(min(2r, 1), min(r, 2)))
  // Simplified: max(0, min(2r, 1), min(r, 2)) if r>0
  // But generic form:
  if (r <= 0)
    return 0.0;
  return std::max(std::min(2.0 * r, 1.0), std::min(r, 2.0));
}

scalar TVDLimiter::phaseChange(const scalar r) {
  // Optimized for sharp interfaces: use SuperBee (compressive)
  return superBee(r);
}

} // End namespace Foam
