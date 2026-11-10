

### Bar 5 — renders, eye-checked

Three figures, one per mis-filed piece, in `artifacts/pota327/renders/` (script
`.scratch/pota-repro/t327/render327.py`, built only from the t66 exports and the GT axis — no ORIG or GT
geometry is drawn into the diagnostic itself, the key only defines the radial coordinate, same instrument as
bars 1 and 3):

- `artifacts/pota327/renders/juglet_piece_2_wall_side.png`
- `artifacts/pota327/renders/juglet_piece_6_wall_side.png`
- `artifacts/pota327/renders/juglet_piece_9_wall_side.png`

Each is four panels: top row is a 3D view about the GT axis, bottom row is the unrolled radial view
(x = height along the GT axis, y = radius from it) before (left) and after the copy-swap (right). Grey
`Surface_0`, blue `Surface_1`, red `Breakline_0`.

Eye check, piece by piece (the radial row is where a wall-side error is unambiguous):

- **Piece 2** — before, the grey sheet fills r 16.5-17.5 and every red dot sits on it; the blue sheet sits at
  14.3-15.5, ~2 mm in. After, the grey sheet is at 14.3-15.5 and the red line is on it. No red dot is left on
  the outer sheet. Radial range 14.0-17.7 mm, height −532 to −523.
- **Piece 6** — a tall curved patch, −282.5 to −262.5 mm high, inner sheet 13-15, outer 15-17.5; before the red
  line runs along the **top rim of the outer sheet**, after it runs along the top rim of the inner one (r 13.4-15.5).
  This is the piece whose exported normals are incoherent (|mean unit n| = 0.017 / 0.041), and the renders show
  why the vote had to fall back on face size: both faces are nearly edge-on to the radial direction.
- **Piece 9** — before, grey 16.6-17.1 with the red line exactly on it, blue 14.0-15.4. After, grey is the inner
  sheet and the red line rides it — but at both ends the red dots climb to 15.9-16.5 mm, i.e. the outer-fringed
  part that `.scratch/pota-repro/t327/blnormals327.py` counts as 17% of that walk (mean n·r̂ −0.680). That fringe
  is visible, not inferred, and it is the line that fails pair 1-9 after the swap.

So the wall side is visually confirmed on all three: the exported `Surface_0` is the exterior sheet and
`Breakline_0` is drawn on it, and flipping the filing on a copy puts both back on the interior sheet.
