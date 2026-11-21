// TICKET 09: write each surface point once.
//
// finishImprovedSurface built the surface it exports in two steps that both wrote points which
// were already there: it appended every row of the segmented cloud to the surface it had just
// fitted, and TICKET-27's de-duplication compared x/y/z only, so a row at the same position with a
// different normal also survived. Ticket 08 measured the result on the exported walls: 288 of 296
// own walls carry a unique prefix followed by a second copy of part of themselves, and 45.8-48.1 %
// of their rows are exact 6-float repeats, while the Authors' 282 walls carry none.
//
// The two operations live here, templated over the point container, so the unit test in
// tests/test_surface_dedupe.cpp exercises the same code the monolith calls -- without PCL.

#ifndef SURFACE_DEDUPE_H
#define SURFACE_DEDUPE_H

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <unordered_set>
#include <vector>

namespace surface_dedupe
{

// SURFACE_DEDUPE_LEGACY=1 puts the pre-ticket behaviour back (append everything, compare x/y/z).
// It exists only so the unit test can be shown RED on the old code; no shipped target defines it.
#ifdef SURFACE_DEDUPE_LEGACY
constexpr bool legacy = true;
#else
constexpr bool legacy = false;
#endif

static_assert(sizeof(float) == 4, "the 6-float key assumes 32-bit floats");

// The six values that make a surface point, as raw bits. Compared by bits, not by value: the rows
// the append is offered are copies of rows the surface already holds, so bit equality is exactly
// what identifies them, and it does not call -0.0 and +0.0 the same row. A tolerance is not an
// option either -- these walls are dense (median nearest neighbour 0.26-0.31 mm on the ticket-09
// cells), so an epsilon would delete real points.
struct Key6
{
	std::uint32_t v[6];

	bool operator==(const Key6& o) const
	{
		return v[0] == o.v[0] && v[1] == o.v[1] && v[2] == o.v[2]
			&& v[3] == o.v[3] && v[4] == o.v[4] && v[5] == o.v[5];
	}
};

struct Key6Hash
{
	std::size_t operator()(const Key6& k) const
	{
		// 64-bit FNV-1a over the 24 bytes, folded to size_t.
		std::uint64_t h = 1469598103934665603ULL;
		for (int i = 0; i < 6; ++i)
		{
			h ^= static_cast<std::uint64_t>(k.v[i]);
			h *= 1099511628211ULL;
		}
		return static_cast<std::size_t>(h ^ (h >> 32));
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

// The pre-ticket test: x/y/z only, normal ignored.
template <class P>
inline bool samePosition3(const P& a, const P& b)
{
	const Key6 ka = key6(a);
	const Key6 kb = key6(b);
	return ka.v[0] == kb.v[0] && ka.v[1] == kb.v[1] && ka.v[2] == kb.v[2];
}

// A strict total order on the whole point, by the bits of the six values. Bit order puts bit-equal
// rows next to each other (which is what the de-duplication needs) and stays a strict weak ordering
// for every float, including NaN -- the old x/y/z-only comparator was neither. On positive floats
// it coincides with the numeric order; the sign bit only moves negatives, and no exported row order
// depends on it while SFS_DEDUPE is off.
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

// Append the rows of "src" that "dest" does not already hold, keeping the order in which they are
// offered; returns how many rows were skipped because the surface already held them.
// Precondition: "src" is not "dest".
template <class Container>
inline std::size_t appendNewPoints(Container& dest, const Container& src)
{
	typedef typename Container::value_type PointT;

	if (legacy)
	{
		for (const PointT& p : src) dest.push_back(p);
		return 0;
	}
	if (static_cast<const void*>(&dest) == static_cast<const void*>(&src)) return 0;

	std::unordered_set<Key6, Key6Hash> have;
	have.reserve(dest.size() + src.size() + 16);
	for (const PointT& p : dest) have.insert(key6(p));

	std::size_t skipped = 0;
	for (const PointT& p : src)
	{
		if (!have.insert(key6(p)).second)
		{
			++skipped;
			continue;
		}
		dest.push_back(p);
	}
	return skipped;
}

// The de-duplicated rows in a deterministic order: one row per distinct 6-value point, sorted by
// the bits of the six values. The last sorted row has no successor to differ from and is always
// kept (TICKET 27 fixed the loop that used to drop it).
template <class Container>
inline Container dedupeExact6(const Container& rows)
{
	typedef typename Container::value_type PointT;

	Container out;
	if (rows.empty()) return out;

	Container sorted(rows);
	std::sort(sorted.begin(), sorted.end(),
		[](const PointT& a, const PointT& b) { return lessPoint6(a, b); });

	out.reserve(sorted.size());
	for (std::size_t i = 0; i + 1 < sorted.size(); ++i)
	{
		const bool dup = legacy ? samePosition3(sorted[i], sorted[i + 1])
		                        : samePoint6(sorted[i], sorted[i + 1]);
		if (!dup) out.push_back(sorted[i]);
	}
	out.push_back(sorted.back());
	return out;
}

} // namespace surface_dedupe

#endif // SURFACE_DEDUPE_H
