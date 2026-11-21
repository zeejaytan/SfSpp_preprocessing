// TICKET 09 unit test: write each surface point once.
//
// Exercises the same header the monolith calls (surface_dedupe.h):
//   U1  a tail whose rows the surface already holds appends nothing
//   U2  a mixed tail appends exactly its missing rows, in order
//   U3  a row at the same position whose normal is one float32 ulp off is SKIPPED, the destination
//       row (its normal included) is kept, and the de-duplication keeps that one row
//   U4  appending twice is idempotent and keeps the surface's order
//   U5  a cloud with an exact repeat, a same-position one-ulp-normal pair and a unique row yields
//       exactly two rows, in the same order whichever order the rows are offered in
//
// Built twice by CMake: SurfaceDedupeTest (shipped code, all five PASS) and
// SurfaceDedupeTestLegacy (-DSURFACE_DEDUPE_LEGACY=1, pre-ticket behaviour, red).
// Every case prints "CASE U<n> PASS|FAIL" on its own line, then "INFO U<n> ..." detail.

#include "surface_dedupe.h"

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

struct TestPoint
{
	float x, y, z;
	float normal_x, normal_y, normal_z;
};

typedef std::vector<TestPoint> RowVec;

static TestPoint pt(float x, float y, float z, float nx, float ny, float nz)
{
	TestPoint p;
	p.x = x; p.y = y; p.z = z;
	p.normal_x = nx; p.normal_y = ny; p.normal_z = nz;
	return p;
}

static int gPass = 0;
static int gFail = 0;

static void report(const char* id, bool ok, const std::string& detail)
{
	std::printf("CASE %s %s\n", id, ok ? "PASS" : "FAIL");
	std::printf("INFO %s %s\n", id, detail.c_str());
	if (ok) ++gPass; else ++gFail;
}

static bool sameRow(const TestPoint& a, const TestPoint& b)
{
	return surface_dedupe::samePoint6(a, b);
}

static bool sameRows(const RowVec& a, const RowVec& b)
{
	if (a.size() != b.size()) return false;
	for (std::size_t i = 0; i < a.size(); ++i)
		if (!sameRow(a[i], b[i])) return false;
	return true;
}

static std::string rowsBrief(const RowVec& rows)
{
	char buf[512];
	std::string s;
	for (std::size_t i = 0; i < rows.size() && i < 8; ++i)
	{
		std::snprintf(buf, sizeof(buf), "%s(%.1f,%.1f,%.1f|%.9g,%.1f,%.1f)",
			i ? " " : "", rows[i].x, rows[i].y, rows[i].z,
			static_cast<double>(rows[i].normal_x), rows[i].normal_y, rows[i].normal_z);
		s += buf;
	}
	return s;
}

// A surface of four rows; every coordinate in the cells below is one of them.
static RowVec surfaceA()
{
	RowVec a;
	a.push_back(pt(0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));
	a.push_back(pt(1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));
	a.push_back(pt(1.0f, 1.0f, 0.0f, 0.0f, 0.0f, 1.0f));
	a.push_back(pt(0.0f, 1.0f, 0.0f, 0.0f, 0.0f, 1.0f));
	return a;
}

// One float32 ulp at 1.0: the normal step the measured near-copies differ by.
static float ulpAtOne()
{
	return std::nextafter(1.0f, 2.0f) - 1.0f;
}

// U1: the second copy of a wall -- every offered row is already in the surface.
static void caseU1()
{
	RowVec dest = surfaceA();
	const RowVec before = dest;
	RowVec src;
	src.push_back(dest[0]);
	src.push_back(dest[1]);
	src.push_back(dest[2]);
	src.push_back(dest[3]);

	double nd = -1.0;
	const std::size_t skipped = surface_dedupe::appendNewPoints(dest, src, &nd);
	const bool ok = (dest.size() == 4) && (skipped == 4) && sameRows(dest, before);
	char buf[256];
	std::snprintf(buf, sizeof(buf),
		"offered=%zu appended=%zu skipped=%zu rows=%zu unchanged=%s normal_maxdiff=%.9g",
		src.size(), dest.size() - before.size(), skipped, dest.size(),
		sameRows(dest, before) ? "yes" : "no", nd);
	report("U1", ok, buf);
}

// U2: a mixed tail -- the two rows the surface lacks are appended, in the order offered.
static void caseU2()
{
	RowVec dest = surfaceA();
	const RowVec before = dest;
	RowVec src;
	src.push_back(pt(2.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));  // new
	src.push_back(dest[1]);                                  // held
	src.push_back(pt(2.0f, 1.0f, 0.0f, 0.0f, 0.0f, 1.0f));  // new
	src.push_back(dest[2]);                                  // held

	const std::size_t skipped = surface_dedupe::appendNewPoints(dest, src);
	RowVec want = before;
	want.push_back(src[0]);
	want.push_back(src[2]);
	const bool ok = (skipped == 2) && (dest.size() == 6) && sameRows(dest, want);
	char buf[320];
	std::snprintf(buf, sizeof(buf),
		"offered=%zu appended=%zu skipped=%zu rows=%zu order_kept=%s",
		src.size(), dest.size() - before.size(), skipped, dest.size(),
		sameRows(dest, want) ? "yes" : "no");
	report("U2", ok, buf);
}

// U3: same position, normal one ulp off -- skipped, the surface's row (its normal included) kept,
// and the de-duplication keeps exactly one row for that position, with the surface's six values.
static void caseU3()
{
	const float ulp = ulpAtOne();

	RowVec dest = surfaceA();
	const RowVec before = dest;
	RowVec src;
	src.push_back(pt(0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f + ulp)); // dest[0]'s xyz, normal one ulp off

	double nd = -1.0;
	const std::size_t skipped = surface_dedupe::appendNewPoints(dest, src, &nd);
	const bool appendOk = (skipped == 1) && (dest.size() == 4) && sameRows(dest, before)
		&& (nd == static_cast<double>(ulp));

	RowVec rows;
	rows.push_back(before[0]);
	rows.push_back(src[0]);
	const RowVec kept = surface_dedupe::dedupePositions(rows);
	const bool dedupeOk = (kept.size() == 1) && sameRow(kept[0], before[0]);

	const bool ok = appendOk && dedupeOk;
	char buf[320];
	std::snprintf(buf, sizeof(buf),
		"append_skipped=%zu append_rows=%zu unchanged=%s normal_maxdiff=%.9g ulp=%.9g dedupe_in=%zu dedupe_out=%zu kept_surface_row=%s (want 1,4,yes,ulp,2,1,yes)",
		skipped, dest.size(), sameRows(dest, before) ? "yes" : "no", nd,
		static_cast<double>(ulp), rows.size(), kept.size(),
		(kept.size() == 1 && sameRow(kept[0], before[0])) ? "yes" : "no");
	report("U3", ok, buf);
}

// U4: idempotent -- a second append of the same tail adds nothing, and the order is the surface's
// own order followed by the missing rows in the order they were offered.
static void caseU4()
{
	RowVec dest = surfaceA();
	RowVec src;
	src.push_back(pt(3.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));
	src.push_back(dest[0]);
	src.push_back(pt(3.0f, 1.0f, 0.0f, 0.0f, 0.0f, 1.0f));

	surface_dedupe::appendNewPoints(dest, src);
	const RowVec once = dest;
	const std::size_t skipped2 = surface_dedupe::appendNewPoints(dest, src);

	RowVec want = surfaceA();
	want.push_back(src[0]);
	want.push_back(src[2]);
	const bool ok = (skipped2 == 3) && (dest.size() == once.size()) && sameRows(dest, once)
		&& sameRows(dest, want);
	char buf[288];
	std::snprintf(buf, sizeof(buf),
		"second_skipped=%zu rows=%zu unchanged=%s prefix_then_offered=%s",
		skipped2, dest.size(), sameRows(dest, once) ? "yes" : "no",
		sameRows(dest, want) ? "yes" : "no");
	report("U4", ok, buf);
}

// U5: a cloud with an exact repeat, a same-position one-ulp-normal pair and a unique row: exactly
// two rows survive, and the reduction does not depend on the order the rows are offered in. The
// pre-ticket path (append everything, no de-duplication) keeps all four, which is the red case.
static void caseU5()
{
	const float ulp = ulpAtOne();

	TestPoint a = pt(10.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f);
	TestPoint aRepeat = a;                                            // exact repeat of a
	TestPoint b = pt(10.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f + ulp);      // same position, one ulp off
	TestPoint q = pt(11.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f);            // unique position

	RowVec offer1;
	offer1.push_back(a); offer1.push_back(aRepeat); offer1.push_back(b); offer1.push_back(q);
	RowVec offer2;
	offer2.push_back(b); offer2.push_back(q); offer2.push_back(a); offer2.push_back(aRepeat);
	RowVec offer3;
	offer3.push_back(q); offer3.push_back(aRepeat); offer3.push_back(b); offer3.push_back(a);

	const RowVec k1 = surface_dedupe::dedupePositions(offer1);
	const RowVec k2 = surface_dedupe::dedupePositions(offer2);
	const RowVec k3 = surface_dedupe::dedupePositions(offer3);

	const bool countOk = (k1.size() == 2);
	const bool aKeptOk = (k1.size() == 2) && sameRow(k1[0], a);
	const bool uniqueKeptOk = (k1.size() == 2) && sameRow(k1[1], q);
	const bool orderIndependent = countOk && sameRows(k1, k2) && sameRows(k1, k3);
	const bool ok = countOk && aKeptOk && uniqueKeptOk && orderIndependent;
	char buf[384];
	std::snprintf(buf, sizeof(buf),
		"rows=%zu distinct=%zu want=2 a_kept=%s unique_kept=%s order_independent=%s order=[%s]",
		offer1.size(), k1.size(), aKeptOk ? "yes" : "no", uniqueKeptOk ? "yes" : "no",
		orderIndependent ? "yes" : "no", rowsBrief(k1).c_str());
	report("U5", ok, buf);
}

int main()
{
	std::printf("[SURFACE-DEDUPE-09] build=%s\n",
		surface_dedupe::legacy
			? "SURFACE_DEDUPE_LEGACY=1 (old behaviour: append everything, no de-duplication)"
			: "shipped (append only new positions, keep one row per position, deterministic)");
	caseU1();
	caseU2();
	caseU3();
	caseU4();
	caseU5();
	std::printf("[SURFACE-DEDUPE-09] cases=%d pass=%d fail=%d\n", gPass + gFail, gPass, gFail);
	return gFail == 0 ? 0 : 1;
}
