// Ticket 11: allow the boundary-detection radius to be overridden.
//
// WHY AN ENV VAR AND NOT A CONSTANT
// The radius is not a constant. It is computed per sherd as
//   boundary_radius_mm = clamp(estimated_spacing_mm * 6.0, 1, 15) mm
// from the cloud's own density, so editing a literal would not sweep
// anything -- it would only change the multiplier. To find out whether our
// ~1.2 mm outward bias tracks the radius, the radius has to be settable to
// an absolute value and the adaptive path bypassed.
//
// This is a DIAGNOSTIC HOOK, not a fix. It returns -1.0 when the variable is
// absent, and the caller leaves the adaptive value alone in that case, so
// default behaviour is unchanged. The sweep sets it; if the sweep identifies
// the radius as the cause, the fix is a decision about the multiplier or the
// clamp, made in review -- not this hook left enabled.
//
// Env var: SFSPP_BOUNDARY_RADIUS_MM. Absent, empty, or non-positive => inert.
#pragma once

#include <cstdlib>

inline double ticket11_boundary_radius_override_mm()
{
    const char* v = std::getenv("SFSPP_BOUNDARY_RADIUS_MM");
    if (v == nullptr || *v == '\0') return -1.0;
    const double parsed = std::atof(v);
    return parsed > 0.0 ? parsed : -1.0;
}
