// Ticket 11 diagnostic hook -- see boundary_radius_override.h for why.
//
// A separate translation unit so the sweep hook is one removable file rather
// than a second copy of the same function. It only has to satisfy the extern
// declaration at the call site in edgeline_extraction_headless.cpp.
#include "boundary_radius_override.h"

extern double ticket11_boundary_radius_override_mm();
