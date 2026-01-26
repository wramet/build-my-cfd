#include "TVDLimiter.H"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

using namespace Foam;

// Mock scalar/word if needed for standalone testing,
// but assuming we link against the project objects.

// Simple test harness
bool check(const std::string &name, scalar val, scalar expected,
           scalar tol = 1e-4) {
  if (std::abs(val - expected) < tol) {
    std::cout << "[PASS] " << name << ": " << val << std::endl;
    return true;
  } else {
    std::cout << "[FAIL] " << name << ": " << val << " Expected: " << expected
              << std::endl;
    return false;
  }
}

int main() {
  std::cout << "Testing TVD Limiters..." << std::endl;

  // Test points
  std::vector<scalar> r_values = {-1.0, 0.0, 0.5, 1.0, 2.0, 10.0};

  // 1. Minmod
  // max(0, min(1, r))
  TVDLimiter minmod("minmod");
  std::cout << "\n--- Minmod ---" << std::endl;
  check("Minmod(-1)", minmod(-1.0), 0.0);
  check("Minmod(0)", minmod(0.0), 0.0);
  check("Minmod(0.5)", minmod(0.5), 0.5);
  check("Minmod(1.0)", minmod(1.0), 1.0);
  check("Minmod(2.0)", minmod(2.0), 1.0);

  // 2. Van Leer
  // (r + |r|) / (1 + |r|)
  TVDLimiter vanLeer("vanLeer");
  std::cout << "\n--- Van Leer ---" << std::endl;
  check("VanLeer(-1)", vanLeer(-1.0), 0.0);
  check("VanLeer(0)", vanLeer(0.0), 0.0);
  check("VanLeer(0.5)", vanLeer(0.5), (0.5 + 0.5) / (1 + 0.5)); // 1/1.5 = 0.666
  check("VanLeer(1.0)", vanLeer(1.0), 1.0);
  check("VanLeer(2.0)", vanLeer(2.0), (2.0 + 2.0) / (1.0 + 2.0)); // 4/3 = 1.333

  // 3. SuperBee
  // max(0, max(min(2r, 1), min(r, 2)))
  TVDLimiter superBee("superBee");
  std::cout << "\n--- SuperBee ---" << std::endl;
  check("SuperBee(0)", superBee(0.0), 0.0);
  check("SuperBee(0.25)", superBee(0.25),
        0.5); // min(0.5, 1)=0.5, min(0.25, 2)=0.25 -> 0.5
  check("SuperBee(0.5)", superBee(0.5),
        1.0); // min(1,1)=1, min(0.5,2)=0.5 -> 1.0
  check("SuperBee(1.0)", superBee(1.0), 1.0);
  check("SuperBee(1.5)", superBee(1.5),
        1.5); // min(3,1)=1, min(1.5,2)=1.5 -> 1.5
  check("SuperBee(2.0)", superBee(2.0), 2.0); // min(4,1)=1, min(2,2)=2 -> 2.0
  check("SuperBee(2.5)", superBee(2.5), 2.0);

  // 4. PhaseChange
  // Same as SuperBee for now
  TVDLimiter phaseChange("phaseChange");
  std::cout << "\n--- PhaseChange ---" << std::endl;
  check("PhaseChange(1.5)", phaseChange(1.5), 1.5);

  return 0;
}
