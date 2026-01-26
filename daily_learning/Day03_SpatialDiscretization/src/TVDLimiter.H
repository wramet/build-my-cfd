/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2026 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
Description
    Class to handle TVD limiters for spatial discretization.
    Supports standard limiters and custom phase change specific logic.

\*---------------------------------------------------------------------------*/

#ifndef TVDLimiter_H
#define TVDLimiter_H

#include "scalar.H"
#include "Enum.H"
#include "word.H"

namespace Foam {

/*---------------------------------------------------------------------------*\
                         Class TVDLimiter Declaration
\*---------------------------------------------------------------------------*/

class TVDLimiter {
public:
  //- Supported limiter types
  enum limiterType {
    MINMOD,
    VAN_LEER,
    VAN_ALBADA,
    SUPER_BEE,
    PHASE_CHANGE // Custom: Hybrid/Compressive for interface
  };

private:
  //- Current limiter type
  limiterType type_;

public:
  // Constructors

  //- Construct from limiter name
  TVDLimiter(const word &limiterName);

  //- Construct from enum
  TVDLimiter(const limiterType type);

  // Member Functions

  //- Calculate limiter value psi(r)
  scalar operator()(const scalar r) const;

  //- Static versions for direct access
  static scalar minmod(const scalar r);
  static scalar vanLeer(const scalar r);
  static scalar vanAlbada(const scalar r);
  static scalar superBee(const scalar r);

  //- Custom phase change limiter (compressive)
  static scalar phaseChange(const scalar r);
};

} // End namespace Foam

#endif
