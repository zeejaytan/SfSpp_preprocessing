// TICKET 09: write each surface point once.
//
// finishImprovedSurface built the surface it exports in two steps that both wrote points which
// were already there: it appended every row of the segmented cloud to the surface it had just
// fitted, and the TICKET-27 de-duplication kept one row per position only when SFS_DEDUPE was on.
// Ticket 08 measured the result on the exported walls: 288 of 296 own walls carry a unique prefix
// followed by a second copy of part of themselves, and 45.8-48.1 % of their rows are exact 6-float
// repeats, while the Authors' 282 walls carry none.
//
// The rule is POSITION, not the six values: the same position reaches a surface twice with a
// normal that differs in one float32 ulp (measured, ticket 09 section 7.14), and the exporter
// prints eight significant digits, so at the precision of the only artefact anyone reads those
// two rows are the same row written twice. The append therefore keeps the destination row (its
// normal included) and reports the largest normal difference among the skipped pairs, so no
// material normal can be dropped silently.
//
// The two operations live here, templated over the point container, so the unit test in
// tests/test_surface_dedupe.cpp exercises the same code the monolith calls -- without PCL.

#ifndef SURFACE_DEDUPE_H
#define SURFACE_DEDUPE_H

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <unordered_map>
#include <vector>

namespace surface_dedupe
{

// SURFACE_DEDUPE_LEGACY=1 puts the pre-ticket behaviour back: append every row and apply no
// de-duplication at all (the old TICKET-27 block assigned its result only with SFS_DEDUPE=on, and
// the switch ships off, so the exported cloud was the cloud the append built). It exists only so
// the unit test can be shown RED on the old code; no shipped target defines it.
#ifdef SURFACE_DEDUPE_LEGACY
constexpr bool legacy = true;
#else
constexpr bool legacy = false;
#endif

static_assert(sizeof(float) == 4, "the position key assumes 32-bit floats");

// A position, as raw bits. Compared by bits, not by value: the rows the append is offered are
// copies of rows the surface already holds, so bit equality is exactly what identifies them, and
// it does not call -0.0 and +0.0 the same row. A tolerance is not an option either -- these walls
// are dense (median nearest neighbour 0.26-0.31 mm on the ticket-09 cells), so an epsilon would
// delete real points.
struct Key3
{
	std::uint32_t v[3];

	bool operator==(const Key3& o) const
	{
		return v[0] == o.v[0] && v[1] == o.v[1] && v[2] == o.v[2];
	}
};

struct Key3Hash
{
	std::size_t operator()(const Key3& k) const
	{
		// 64-bit FNV-1a over the 12 bytes, folded to size_t.
		std::uint64_t h = 1469598103934665603ULL;
		for (int i = 0; i < 3; ++i)
		{
			h ^= static_cast<std::uint64_t>(k.v[i]);
			h *= 1099511628211ULL;
		}
		return static_cast<std::size_t>(h ^ (h >> 32));
	}
};

template <class P>
inline Key3 key3(const P& p)
{
	Key3 k;
	const float f[3] = { p.x, p.y, p.z };
	std::memcpy(k.v, f, sizeof(f));
	return k;
}

template <class P>
inline bool samePosition3(const P& a, const P& b)
{
	return key3(a) == key3(b);
}

// The six values that make a surface point, as raw bits. Used only by the deterministic ordering
// of the de-duplication (and by the test's row comparison), never as the duplicate test.
struct Key6
{
	std::uint32_t v[6];

	bool operator==(const Key6& o) const
	{
		return v[0] == o.v[0] && v[1] == o.v[1] && v[2] == o.v[2]
			&& v[3] == o.v[3] && v[4] == o.v[4] && v[5] == o.v[5];
	}
};

template <class P>
inline Key6 key6(const P& p)
{
	Key6 k;
	const float f[6] = { p.x, p.y, p.z, p.normal_x, p.normal_y, p.normal_z };
	std::memcpy(k.v, f, sizeof(f));
	return k;
}

template <class P>
inline bool samePoint6(const P& a, const P& b)
{
	return key6(a) == key6(b);
}

// A strict total order on the whole point, by the bits of the six values: x, y, z first, the three
// normal words as the tie-break. Bit order stays a strict weak ordering for every float, including
// NaN -- the old x/y/z-only comparator was neither -- and it makes the de-duplication independent
// of the order the cloud arrives in, which is what W3 asks for.
template <class P>
inline bool lessPoint6(const P& a, const P& b)
{
	const Key6 ka = key6(a);
	const Key6 kb = key6(b);
	for (int i = 0; i < 6; ++i)
	{
		if (ka.v[i] != kb.v[i]) return ka.v[i] < kb.v[i];
	}
	return false;
}

// The largest absolute difference in any normal component between two rows at the same position.
// Computed in double so a one-ulp difference is reported exactly, not rounded away.
template <class P>
inline double normalComponentMaxDiff(const P& a, const P& b)
{
	double d = std::fabs(static_cast<double>(a.normal_x) - static_cast<double>(b.normal_x));
	const double dy = std::fabs(static_cast<double>(a.normal_y) - static_cast<double>(b.normal_y));
	const double dz = std::fabs(static_cast<double>(a.normal_z) - static_cast<double>(b.normal_z));
	if (dy > d) d = dy;
	if (dz > d) d = dz;
	return d;
}

// Append the rows of "src" whose position "dest" does not already hold, keeping the order in which
// they are offered; returns how many rows were skipped because the surface already held their
// position. When "normalMaxDiffOut" is given it receives the largest normal-component difference
// over the skipped pairs (zero when nothing was skipped), which is the guard that the skipped row's
// normal is the same normal to within a float32 ulp.
// Precondition: "src" is not "dest".
template <class Container>
inline std::size_t appendNewPoints(Container& dest, const Container& src,
	double* normalMaxDiffOut = NULL)
{
	typedef typename Container::value_type PointT;

	if (normalMaxDiffOut) *normalMaxDiffOut = 0.0;

	if (legacy)
	{
		for (const PointT& p : src) dest.push_back(p);
		return 0;
	}
	if (static_cast<const void*>(&dest) == static_cast<const void*>(&src)) return 0;

	std::unordered_map<Key3, std::size_t, Key3Hash> have;
	have.reserve(dest.size() + src.size() + 16);
	for (std::size_t i = 0; i < dest.size(); ++i) have.emplace(key3(dest[i]), i);

	std::size_t skipped = 0;
	double worst = 0.0;
	for (const PointT& p : src)
	{
		const std::unordered_map<Key3, std::size_t, Key3Hash>::const_iterator it = have.find(key3(p));
		if (it != have.end())
		{
			++skipped;
			const double d = normalComponentMaxDiff(p, dest[it->second]);
			if (d > worst) worst = d;
			continue;
		}
		have.emplace(key3(p), dest.size());
		dest.push_back(p);
	}
	if (normalMaxDiffOut) *normalMaxDiffOut = worst;
	return skipped;
}

// One row per position, in a deterministic order: sorted by x, y, z with the three normal words as
// the tie-break, and of a run of rows at the same position the first of the sorted run survives
// (the one with the smallest normal words). Neither the choice nor the order depends on the order
// the rows arrive in. The legacy build applies no de-duplication at all, so it returns the rows
// unchanged.
template <class Container>
inline Container dedupePositions(const Container& rows)
{
	typedef typename Container::value_type PointT;

	Container out;
	if (rows.empty()) return out;
	if (legacy) return Container(rows);

	Container sorted(rows);
	std::sort(sorted.begin(), sorted.end(),
		[](const PointT& a, const PointT& b) { return lessPoint6(a, b); });

	out.reserve(sorted.size());
	for (std::size_t i = 0; i < sorted.size(); ++i)
	{
		if (i == 0 || !samePosition3(sorted[i - 1], sorted[i])) out.push_back(sorted[i]);
	}
	return out;
}

} // namespace surface_dedupe

#endif // SURFACE_DEDUPE_H
