// Ticket 11: allow the boundary-detection radius to be overridden.
//
// WHY AN ENV VAR AND NOT A CONSTANT
// The radius is not a constant. Line 874 computes it adaptively as
//   boundary_radius_mm = clamp(estimated_spacing_mm * 6.0, 1, 15)
// from the cloud's own density, so editing the "4" would not sweep anything
// -- it would only change the multiplier. To find out whether our ~1.2 mm
// outward bias tracks the radius, the radius has to be settable to an
// absolute value and the adaptive path has to be bypassed.
//
// This is a DIAGNOSTIC HOOK, not a fix. It defaults to off, so with the
// variable unset the behaviour is byte-identical to before: the adaptive
// value is computed and used exactly as it was. The sweep sets it; if the
// sweep identifies the radius as the cause, the fix is a decision about the
// multiplier or the clamp, made in review -- not this hook left enabled.
//
// Env var: SFSPP_BOUNDARY_RADIUS_MM. Absent or empty => unchanged behaviour.

#include <cstdlib>
#include <string>

namespace ticket11 {

double boundary_radius_override_mm()
{
    const char* v = std::getenv("SFSPP_BOUNDARY_RADIUS_MM");
    if (v == nullptr || *v == '\0') return -1.0;
    const double parsed = std::atof(v);
    return parsed > 0.0 ? parsed : -1.0;
}

}  // namespace ticket11
