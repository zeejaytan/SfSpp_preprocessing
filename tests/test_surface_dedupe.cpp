// TICKET 09 unit test: write each surface point once.
//
// Compares the two behaviours the ticket changes, on the same header the monolith calls
// (surface_dedupe.h):
//   U1  a tail whose rows the surface already holds appends nothing
//   U2  a mixed tail appends exactly its missing rows, in order
//   U3  a row at the same position with a different normal is a different point
//   U4  appending twice is idempotent and keeps the surface's order
//   U5  the de-duplication compares all six values and keeps the last row
//
// Built twice by CMake: SurfaceDedupeTest (shipped code, all five PASS) and
// SurfaceDedupeTestLegacy (-DSURFACE_DEDUPE_LEGACY=1, the pre-ticket behaviour, red).
// Every case prints "CASE U<n> PASS|FAIL" on its own line, then "INFO U<n> ..." detail.

#include "surface_dedupe.h"

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
		std::snprintf(buf, sizeof(buf), "%s(%.1f,%.1f,%.1f|%.1f,%.1f,%.1f)",
			i ? " " : "", rows[i].x, rows[i].y, rows[i].z,
			rows[i].normal_x, rows[i].normal_y, rows[i].normal_z);
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

	const std::size_t skipped = surface_dedupe::appendNewPoints(dest, src);
	const bool ok = (dest.size() == 4) && (skipped == 4) && sameRows(dest, before);
	char buf[256];
	std::snprintf(buf, sizeof(buf),
		"offered=%zu appended=%zu skipped=%zu rows=%zu unchanged=%s",
		src.size(), dest.size() - before.size(), skipped, dest.size(),
		sameRows(dest, before) ? "yes" : "no");
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

// U3: same position, different normal -- a different point, both to the append and to the dedupe.
static void caseU3()
{
	RowVec dest = surfaceA();
	RowVec src;
	src.push_back(pt(0.0f, 0.0f, 0.0f, 0.0f, 0.0f, -1.0f)); // same xyz as dest[0], opposite normal
	const std::size_t skipped = surface_dedupe::appendNewPoints(dest, src);
	const bool appendOk = (skipped == 0) && (dest.size() == 5);

	// ... and the de-duplication must not fold them together either.
	RowVec rows;
	rows.push_back(pt(5.0f, 5.0f, 5.0f, 0.0f, 0.0f, 1.0f));
	rows.push_back(pt(5.0f, 5.0f, 5.0f, 0.0f, 0.0f, -1.0f));
	const RowVec kept = surface_dedupe::dedupeExact6(rows);
	const bool dedupeOk = (kept.size() == 2);

	const bool ok = appendOk && dedupeOk;
	char buf[256];
	std::snprintf(buf, sizeof(buf),
		"append_skipped=%zu append_rows=%zu dedupe_in=%zu dedupe_out=%zu (want 0,5 and 2,2)",
		skipped, dest.size(), rows.size(), kept.size());
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

// U5: the de-duplication of a full wall row set -- one exact 6-float repeat, one same-position
// different-normal pair, one unique row: exactly three rows survive, in a reproducible order.
// The old x/y/z-only rule returns two, which is the failure this test exists to catch.
static void caseU5()
{
	RowVec rows;
	rows.push_back(pt(10.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));   // a
	rows.push_back(pt(10.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));   // a, exact repeat
	rows.push_back(pt(10.0f, 0.0f, 0.0f, 0.0f, 0.0f, -1.0f));  // b, same xyz, different normal
	rows.push_back(pt(11.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f));   // c, unique

	const RowVec kept = surface_dedupe::dedupeExact6(rows);
	const RowVec keptAgain = surface_dedupe::dedupeExact6(rows);
	const bool countOk = (kept.size() == 3);
	const bool aOk = !kept.empty() && sameRow(kept[0], rows[0]);
	const bool normalKeptOk = kept.size() == 3 && sameRow(kept[1], rows[2]);
	const bool cOk = kept.size() == 3 && sameRow(kept[2], rows[3]);
	const bool deterministic = sameRows(kept, keptAgain);
	const bool ok = countOk && aOk && normalKeptOk && cOk && deterministic;
	char buf[384];
	std::snprintf(buf, sizeof(buf),
		"rows=%zu distinct=%zu want=3 a_kept=%s normal_pair_kept=%s unique_kept=%s deterministic=%s order=[%s]",
		rows.size(), kept.size(), aOk ? "yes" : "no", normalKeptOk ? "yes" : "no",
		cOk ? "yes" : "no", deterministic ? "yes" : "no", rowsBrief(kept).c_str());
	report("U5", ok, buf);
}

int main()
{
	std::printf("[SURFACE-DEDUPE-09] build=%s\n",
		surface_dedupe::legacy ? "SURFACE_DEDUPE_LEGACY=1 (old behaviour: append everything, compare x/y/z)"
		                       : "shipped (append only new rows, compare all six values)");
	caseU1();
	caseU2();
	caseU3();
	caseU4();
	caseU5();
	std::printf("[SURFACE-DEDUPE-09] cases=%d pass=%d fail=%d\n", gPass + gFail, gPass, gFail);
	return gFail == 0 ? 0 : 1;
}
