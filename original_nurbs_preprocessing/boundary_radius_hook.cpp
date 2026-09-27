// Ticket 11 diagnostic hook -- see boundary_radius_override.cpp for why.
#include "boundary_radius_override.h"

namespace ticket11 {

double ticket11_boundary_radius_override_mm()
{
    return boundary_radius_override_mm();
}

}  // namespace ticket11
