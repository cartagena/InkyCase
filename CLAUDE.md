# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Handoff notes for continuing this design. This is a parametric CAD project, not
software in the usual sense — there is no build/lint/test suite, just two
scripts that both generate the same geometry (a Fusion 360 script and an
OpenSCAD port) plus a hardware-reference doc. This file has the *reasoning*
behind the numbers; that's the part that gets lost when only the code survives.

---

## Repository layout

Everything lives under `impression-7.3/`:

| File | What it is |
|---|---|
| `impression-7.3/fusion-script.py` | Fusion 360 script. The original source of the design; builds all four components. Requires Fusion 360 to run. |
| `impression-7.3/openscad-script.scad` | OpenSCAD port of the same design. Same parameter names, same derivations, so the two can be diffed line-by-line. Runs anywhere OpenSCAD does — no Fusion license needed — and can export STLs directly. |
| `impression-7.3/PCB_REFERENCE.md` | Standalone hardware reference for the Inky Impression 7.3" board (PIM773): board/module/active-area dimensions, mounting holes, button positions, headers, with a confidence rating (🟢🔵🟡🔴) per fact. This is the source of truth for anything board-related — check it before changing a board dimension in either script. |
| `impression-7.3/assets/` | Source photos and Pimoroni's dimensional drawing that `PCB_REFERENCE.md` was compiled from. |

**Keep the two scripts in sync.** They share parameter names and derivation
order on purpose. If you change a number in one (especially anything in
`PCB_REFERENCE.md`-derived territory — borders, PCB post positions), port the
same change to the other, or a future print will silently regress.

---

## Current state

Frame has been printed once. Cover has **not** fitted yet — the stand bosses fouled
the frame's bottom wall. That's fixed in the script but not verified on a print.
Nothing about the button mechanism has been physically tested.

---

## Commands

There's no build/test/lint tooling here — the equivalent workflows are:

**Validate the OpenSCAD script without opening a GUI** (fastest check — no
Fusion, no license, catches the same invariant violations the Fusion script
raises `RuntimeError` for, via `assert()`):

```bash
openscad -o /dev/null impression-7.3/openscad-script.scad
```

This renders the full assembly, prints `echo()` summaries of the key derived
numbers (case size, pocket size, display window, button Y positions, lever
ratio, stand strut X positions), and fails loudly if `POCKET_TOP` doesn't
reach the button slot or a stand screw doesn't clear its clipped boss.

**Export an individual part as an STL for printing** — toggle the relevant
`SHOW_*` boolean(s) at the top of `openscad-script.scad` to `false` for
everything except the part you want, then:

```bash
openscad -o frame.stl impression-7.3/openscad-script.scad
```

**Export all four parts as separate STLs in one go** — override the `SHOW_*`
booleans from the command line with `-D` instead of editing the file, once per
part:

```bash
openscad -D 'SHOW_FRAME=true;SHOW_COVER=false;SHOW_LEVERS=false;SHOW_STAND=false'  -o front.stl  impression-7.3/openscad-script.scad
openscad -D 'SHOW_FRAME=false;SHOW_COVER=true;SHOW_LEVERS=false;SHOW_STAND=false'  -o back.stl   impression-7.3/openscad-script.scad
openscad -D 'SHOW_FRAME=false;SHOW_COVER=false;SHOW_LEVERS=true;SHOW_STAND=false'  -o button.stl impression-7.3/openscad-script.scad
openscad -D 'SHOW_FRAME=false;SHOW_COVER=false;SHOW_LEVERS=false;SHOW_STAND=true'  -o stand.stl  impression-7.3/openscad-script.scad
```

Note `button.stl` this way contains all 4 levers already positioned at their
real `BUTTON_Y` locations (`button_levers()` loops over all of them) — unlike
the Fusion export below, which exports the single `Button lever` component
definition once, unpositioned duplicates included in the design as
occurrences rather than as separate geometry.

**Render the Fusion script**: Utilities → ADD-INS → Scripts and Add-Ins →
Scripts → "+" → Create → Python, replace the generated file with
`fusion-script.py`, select it, Run. Run it in an **empty** design — it builds
the frame from scratch rather than modifying an existing body. With
`EXPORT_STL = True` (the default, near the top of the script) it finishes by
asking for an output folder and writing `front.stl`, `back.stl`, `button.stl`
and `stand.stl` there — one file per component, mesh refinement Medium. Set
`EXPORT_STL = False` to skip that and just build the design.

**Check a parameter change against the arithmetic alone**, without rendering
anything (useful for quick "did this clash-check still hold" questions on the
Fusion script specifically — the OpenSCAD `echo()`/`assert()` approach above
is generally faster now, but this still works for the Python source):

```python
src = open('impression-7.3/fusion-script.py').read()
head = src.split('# 30-point lever profile')[0]
head = '\n'.join(l for l in head.splitlines() if not l.startswith('import'))
import math
ns = {'math': math}
exec(head, ns)
print(ns['CASE_W'], ns['DISP_W'], ns['BUTTON_Y'])
```

Worth keeping: clearance checks between the levers, PCB posts, stand bosses,
cable exit and screw positions all reduce to arithmetic on these values. Add
an assertion whenever a clash is found rather than just fixing the number —
both scripts already do this for the two invariants that have actually broken
in practice (wall-pocket-must-reach-slot, stand-screw-must-clear-clipped-boss).

---

## Three coordinate systems — read this before changing anything

Most of the bugs in this design came from mixing these up.

**1. Board datum** (from Pimoroni's drawing, cross-checked in `PCB_REFERENCE.md`).
Origin at the board's bottom-left in *rear* view. Buttons at Y = 28.50 / 52.50 /
76.50 / 100.50, switch body 2.60 in from the left edge.

**2. Lever datum** (local, one per button). `X = 0` at the board's edge with `+X`
pointing *inboard*; `Z = 0` at the PCB's rear face with `+Z` out the back;
`Y = 0` on the button's centreline. The whole 30-point `PROFILE` list is in this
frame.

**3. Case datum** (matches the user's sketch). Origin at the outer profile's
bottom-left, `Z = 0` at the front outer face.

Two functions bridge lever → case, present in both scripts:

```
gx(x) = BOARD_EDGE_X + XSIGN * x   # XSIGN = -1 on the right wall
gz(z) = PCB_REAR_Z + z             # 3.10
```

`gx` **mirrors as well as translating**, because `+X` meant inboard and inboard is
`−X` on the right-hand wall. Never translate the lever by hand to move it — flip
`BUTTON_SIDE` and let `gx` do it, or the flexure ends up on the wrong face.

The OpenSCAD port bakes `gx()`/`gz()` into the point list once
(`PROFILE_M = map_profile(PROFILE)`) rather than at every use site the way the
Fusion script's `pt_xz(sk, gx(x), gz(z))` does — same result, just computed
once instead of inline each time.

---

## Derivation rules that must not be inverted

These were all wrong at some point and caused real failures.

- **The pocket is sized from the board; `CASE_W`/`CASE_D` are derived from the
  pocket.** Not the other way round. Widening the frame must never loosen the
  board. `WALL_T_TOP` is the knob for changing the frame's proportions.
- **`POCKET_TOP` is derived from `SHAFT_Z0`,** not set independently. The wall
  pocket has to break *into* the button slot. When they were set separately they
  left a 0.05 mm web of wall and the lever's foot wouldn't pass.
- **`BUTTON_Z` is anchored to `WALL_TOP` (i.e. to `FRAME_H`, the case's own
  back edge), not to the PCB.** `PIVOT_Z`, by contrast, *is* anchored to the
  PCB (it's a fixed lever-local constant, gz()-mapped straight off
  `PCB_REAR_Z`). Because `gz(z) = PCB_REAR_Z + z` and
  `BUTTON_Z = WALL_TOP - HEAD_Z/2 = (FRAME_H - PCB_REAR_Z) - HEAD_Z/2`, the
  `PCB_REAR_Z` terms cancel inside `gz(BUTTON_Z...)` - the button head's
  *absolute* Z position never moves when `PCB_REAR_Z` changes. This is
  deliberate (the head has to reach flush to `FRAME_H` regardless of how
  thick the PCB stack is) but it means `LIN` (`BUTTON_Z - PIVOT_Z`, the
  pivot-to-button arm) is NOT a fixed lever geometry constant the way it
  looks - it silently shrinks or grows opposite to `PCB_REAR_Z`, changing the
  lever ratio. Don't change `PCB_REAR_Z` (or anything upstream of it, like
  `STACK_T`) without re-checking the lever ratio afterward - see the
  `STACK_T` open item below for the last time this bit.
- **Everything on the back cover's inner face must clip to the pocket footprint**
  (`POCKET_X0..POCKET_X1`, `POCKET_Y0..POCKET_Y1`, minus `BOSS_CLR`). The frame's
  walls occupy the outer 5 mm at *every* Z. This is what broke the printed cover.
- **The wall pocket and the foot channel are the same width** (`POCKET_W = 2 *
  CHAN_Y`). An earlier version had separate ribs 14.40 across inside a 13.00
  pocket, so 0.70 mm of each rib was buried in solid wall.
- **`PCB_POSTS` is 4 entries, not a post in every corner** — driven by real
  conflicts documented in `PCB_REFERENCE.md`, not by symmetry. The bottom-left
  corner is skipped because the board has a 10-pin debug header there with no
  confirmed footprint to design a clearance against; top-right is skipped as
  redundant once top-left and bottom-right are covered. Don't "complete" the
  set back to 4 corners without first measuring the header in
  `PCB_REFERENCE.md` §8.
- **`PCB_POST_IN` is 8.00, not 4.00** — at 4.00 the corner posts landed only
  ~1.4 mm from the M2 mounting hole centres (`PCB_REFERENCE.md` §5); 8.00
  clears them with margin regardless of the hole's exact diameter (also
  unconfirmed).
- **`BORDER_BOTTOM`/`BORDER_TOP` are 16.20/10.40, not 16.00/10.00** — the real
  panel borders per `PCB_REFERENCE.md` §4 are 16.50/10.70; at the old values
  the display window had zero (bottom) or ~0.20 mm negative (top) crop margin,
  meaning the bezel could expose a sliver of dead panel instead of cropping
  live active area. See `WINDOW_LAP` below for why some crop margin is wanted
  at all.

---

## Design decisions worth not undoing

**The lever is a single 2D profile extruded 10 mm in Y.** This is why it prints
on its side with zero supports, and why the 0.45 mm flexure survives — the tensile
stress runs along the extrusion strands instead of across layer bonds. The only
departure is the flexure's width neck to 6.00 mm, which is an in-layer bridge and
prints fine. Don't add features that break the constant cross-section.

In the OpenSCAD port this profile is split into three fixed index ranges
(`ANCHOR_IDX` / `FLEXURE_IDX` / `BODY_IDX`) instead of Fusion's runtime
"sketch it, add divider lines, sort the resulting profiles by area" dance —
same three regions, extruded at `LEVER_W` (anchor + body) and `FLEX_W`
(flexure) respectively. If the profile shape changes, these index lists have
to move with it; there's no automatic re-detection like Fusion's area sort.

**The flexure is necked to 6.00 mm so it clears the channel lips at ±4.30** while
the lever slides down into the pocket during assembly. Widening it back to 10 mm
makes the lever un-insertable.

**The button slot is open at the top and closed by a tongue on the back cover.**
That's what allows the one-piece lever to drop in from the rear. The tongue is
load-bearing: without it the button head only bears on the slot's lower edge and
the button tilts when pressed.

**Peak load on the switch is bounded near 6 N** by two features working together:
the head bottoms on the wall after 0.75 mm, and the 0.60 mm thinned arm tip
absorbs whatever overtravel the tolerance stack leaves. Pimoroni moved these
buttons from side- to rear-mounted because the side ones were getting knocked off
in transit, so the pads are weak. Don't remove either feature.

**The flexure is 0.45 × 2.00, deliberately short and thin.** With only 0.50 mm of
side clearance the output arm is 5.30 mm, so the hinge rotates ~4.3° instead of
~2.6°. A ligament can't be soft in rotation and stiff in the direction the switch
pushes back — those are locked together by its length. Thickening it kills the
tactile click; the ~0.06 mm of vertical sag is already in the travel budget.

**`build_stand` / `stand()` creates the spine first.** The two struts don't touch
each other, so in Fusion, if the first strut were the new body the second would
have nothing to join to and Fusion would silently make a *second body* — which
then misses every cut that follows. There's an assertion for this in the Fusion
script. The OpenSCAD port doesn't need the assertion (CSG `union()` always
merges regardless of build order), but the spine-first ordering is kept anyway
for the two scripts to read the same way.

**PCB posts are 4, sized to stop the board falling away from the pocket floor,
not to clamp it.** See the derivation rule above for which 4 and why.

---

## Verified numbers

| | |
|---|---|
| Case outer | 185.20 × 134.20 × 20.00 |
| Walls | 5.00, bezel lip 1.50, frame 18.00, cover 2.00 |
| PCB pocket | 175.20 × 124.20, floor at Z = 1.50, PCB rear face Z = 4.40 |
| Display window | 159.60 × 95.60 at (12.80, 22.20) |
| Borders (board-relative) | `BORDER_SIDE` 6.80, `BORDER_BOTTOM` 16.20, `BORDER_TOP` 10.40 |
| Borders (case-edge-relative) | 12.80 sides, 22.20 bottom, 16.40 top |
| Buttons | Y = 34 / 58 / 82 / 106, right wall, switch centreline X = 175.40 |
| Lever | ratio 0.943 : 1, travel 0.75 mm — **changed from the tuned 1.189 : 1, ≈210 gf; unresolved**, see `STACK_T` open item below |
| Cavity behind PCB | 13.60 mm (`WALL_TOP` = `FRAME_H` − `PCB_REAR_Z`) — Pi Zero only |
| PCB posts | 4, `PCB_POST_IN` = 8.00 mm from the board edge |
| Screws | 8 × M2.5 × 10 (cover→frame), 4 × M2.5 × 8 (stand→cover), Ø2.10 pilots |

---

## Open items

- **Cover fit** — reprint and confirm it seats now the bosses are clipped. Also
  check the tongues: 10.10 mm in a 10.40 slot is only 0.15/side, and elephant's
  foot on the frame would bind them with the same symptom.
- **Button feel — tested, found broken with the cover on, partially fixed,
  not re-verified.** Printed and tested: the lever worked fine with the cover
  off but jammed completely (didn't move at all) with the cover on. Root
  cause: `HEAD_Z1` (top of the button head) lands at exactly `FRAME_H` in
  absolute case coordinates, flush with where the cover's slot tongue
  starts — the tongue was only cleared against the lever's REST-position
  footprint (`CLR`, 0.20 mm), not the arc the head actually sweeps through
  when pressed. Added `TONGUE_SWEEP_CLR` (0.50 mm, on top of `CLR`) recessing
  the tongue further back to give the sweep room — a moderate first guess,
  not a measured fix. **Needs a reprint and retest of just the cover to
  confirm.** If it's still jammed, that's evidence the tongue isn't the only
  interference (or `TONGUE_SWEEP_CLR` needs to go higher than 0.50, up
  against the tongue's ~1.55 mm total available span) — don't assume more of
  the same fix will keep working. Once it moves, still need to tune
  `REST_GAP` then `STOP_GAP` for feel, per the original plan below.
- **PCB post length** — hard stop at Z = 4.40 (was 3.10, see the `STACK_T`
  note above) made of stacked tolerances. Expect to adjust `PCB_POST_CLR`, or
  use 0.5 mm foam pads with `PCB_POST_CLR = 0.40`.
- **`STACK_T` correction changed the lever ratio to 0.943:1 (was 1.189:1) —
  unresolved. Do NOT compensate via `PIVOT_Z`, that was tried and it breaks
  the lever sketch.** `PCB_REAR_Z` was wrongly derived from `BOARD_T` (1.60,
  bare PCB only); the real board + epaper glass module stack measures
  2.90 mm (`STACK_T`). Fixing this shifted `PCB_REAR_Z` from 3.10 to 4.40 and
  `WALL_TOP` (cavity behind the board) from 14.90 down to 13.60. Because
  `BUTTON_Z` is deliberately anchored to `WALL_TOP` (i.e. to `FRAME_H`, not
  to the PCB — see the derivation rule above), its *absolute* Z position
  didn't move, but `PIVOT_Z` *is* anchored to the PCB, so the pivot-to-button
  arm (`LIN`) got physically shorter and the lever ratio dropped — a real
  mechanical change, not a rendering artifact.
  **`PIVOT_Z` compensation was tried and reverted.** Moving `PIVOT_Z` from
  4.60 to 3.30 does restore `gz(PIVOT_Z)` and the exact 1.189:1 ratio on
  paper, but it broke the lever's 30-point `PROFILE` outline: `ARM_Z0`
  (tied to `PIVOT_Z`) and `NUB_Z` (tied to `SW_CAP_Z`) are BOTH already
  PCB-anchored via `gz()`, and their relative spacing (`ARM_Z0` above
  `NUB_Z`) was already correct and untouched by the `STACK_T` fix - it never
  needed compensating. Shifting `PIVOT_Z` alone pushed `ARM_Z0` below
  `NUB_Z`, flipping an edge in the outline and making it self-intersect.
  OpenSCAD rendered this "successfully" with no warning at all (no
  equivalent to Fusion's profile-count check); Fusion's
  `build_lever()` caught it immediately with `RuntimeError: Expected 3 lever
  profiles ... got 4`. **Lesson: a clean OpenSCAD render is not sufficient
  evidence that a `PIVOT_Z`-adjacent change is safe — check it against a
  Fusion build too**, since OpenSCAD has no equivalent to the lever
  sketch's self-intersection check.
  `PIVOT_Z` is back to 4.60 and the ratio is back to 0.943:1. **The real fix
  still needs to happen on the `BUTTON_Z`/`HEAD_Z` side** (the side that's
  actually FRAME_H-anchored and changed relative to the PCB-anchored group,
  not the PCB-anchored group itself) - not yet attempted. Whatever the fix
  turns out to be, re-verify against a Fusion build (3 lever profiles), not
  only an OpenSCAD render, before trusting it.
- **Bottom-left PCB post** — currently omitted because the debug header's
  footprint isn't confirmed (`PCB_REFERENCE.md` §8, §11). If you measure it off
  the real board, a post can go at
  `(BOARD_X0 + PCB_POST_IN, BOARD_Y0 + PCB_POST_IN)` with a verified clearance.
- **Switch body footprint** (`SW_ACROSS`/`SW_ALONG`) — not confirmed by any
  labelled dimension (`PCB_REFERENCE.md` §6, §11); `SW_ACROSS = 3.40` is an
  assumption. If it's actually 4.20, the switch centreline moves to 4.70 and
  every downstream number improves slightly.
- **Stand lean** — 18° is a guess, never sat on a desk.
- **Pi Zero standoffs** — not modelled. Positions depend on the stack.
- **Fillets and chamfers** — modelled in both scripts on both the frame and
  the cover, plus a 1.5 mm equal-distance chamfer (`CHAMFER_WINDOW`) around
  the window's front rim. All reverse-derived from `front.stl`/`back.stl`
  exports (Fusion's own fillet/chamfer features, applied by hand at some
  point, then ported back into the scripts) and selected by face/loop/edge
  geometry in Fusion (`add_box_edge_fillet()`, shared by
  `build_front_frame()`'s own call and `add_back_cover_finishing()`) rather
  than edge index, and in OpenSCAD by `rounded_box_bottom_cap()` /
  `rounded_box_top_cap()` plus the same `chamfered_window()` hull taper — see
  `impression-7.3/openscad-script.scad` for the derivation comments.
  Each part's 4 vertical corners are rounded for its FULL height/thickness —
  `FILLET_OUTER` (2 mm) for the frame, `FILLET_COVER_FACE` (1 mm) for the
  cover — and ONLY that part's exterior-facing flat face gets an additional
  fillet blending into it, the same radius: the frame's front (Z=0), the
  cover's back (Z=CASE_H). The hidden mating face between them — the frame's
  back (Z=FRAME_H) and the cover's front (Z=FRAME_H) — is left sharp and
  flush on both parts, not filleted at all. Three earlier passes in this
  file got this wrong: a uniform fillet on *every* edge of both parts
  (bulged the cover's corner out to 2 mm at mid-thickness); then a mixed
  radius on the cover (1 mm face, 2 mm vertical, same bulge); then a uniform
  1 mm on *every* edge of the cover including the mating face. All three
  were rejected on sight against the real part — a second fillet on the
  hidden face reads as a separate bead, not the continuous rounded column
  the real part has. Don't reintroduce any of them; each part gets exactly
  one face filleted, matched to its own exterior side.
  Still left to hand-finishing or a slicer, same reasoning as before (no
  clean parametric selector for these, and they don't affect fit): R0.4 at
  the lever arm's thickness step, 0.3 around the nub's bottom face, and a
  0.4 mm relief groove around the bottom of each wall pocket. That last one
  matters — the nozzle's inside-corner fillet will hold the lever's foot proud
  and change the rest gap.
- **`front.stl`/`back.stl` predate the border fix** — the copies inspected to
  reverse the fillet/chamfer numbers above have a display window inset using
  the *old* `BORDER_BOTTOM`/`BORDER_TOP` (16.00/10.00), not the corrected
  16.20/10.40 documented above. Their window Y-position (22.0–118.2 at the
  pocket floor) is therefore ~0.2–0.4 mm off from what the current scripts
  produce (22.2–117.8). Don't use either file as a dimensional reference
  without re-exporting from a script run with current parameters — only the
  fillet/chamfer *shape* was pulled from them, not window position.

---

## Fusion API gotchas hit so far (`fusion-script.py` only)

- **Units are centimetres.** Everything in the script is mm, scaled by `MM = 0.1`
  at the point of use. (The OpenSCAD port has no equivalent — OpenSCAD is
  natively mm, no scale factor.)
- **Points go through `modelToSketchSpace`** so plane orientation is never
  assumed. Fusion's XZ/YZ plane handedness is the classic way these scripts come
  out mirrored.
- **A Join extrude with `participantBodies` only merges into bodies it physically
  touches.** Otherwise you get a silent extra body.
- **`closed_polyline` chains through shared `SketchPoint`s.** Passing bare
  `Point3D`s leaves the loop open and no profile forms.
- **The lever sketch must yield exactly 3 profiles** (anchor, flexure, body) —
  two divider lines fence the flexure off so it can extrude narrower. There's a
  check; if it fires, a dimension edit has made the outline self-intersect.
- **A fillet feature given more than one of {vertical edges, front loop, back
  loop} in a box's edge set can fail** with `ASM_BL_CAP_COMPLEX - The
  fillet/chamfer could not be created at the requested size`, even when
  every individual radius is well within the part's dimensions, and even
  when the two loops are 18 mm apart and share no edges. It first broke as
  one feature for all 12 edges; splitting into two (verticals, then both
  loops together) broke the exact same way on the second feature. Only three
  fully independent `filletFeatures.add()` calls — verticals, then the front
  loop, then the back loop, each its own feature — actually computes; that's
  what `add_box_edge_fillet()` does. Don't collapse any of these three back
  together to "clean it up" — that's the exact shape that broke, twice.
- **Even three separate fillet features isn't enough if the loop being
  filleted has already been notched by another cut.** The frame's back-face
  outer loop (Z=FRAME_H) still failed the same `ASM_BL_CAP_COMPLEX` error
  even alone, because the button slot cut (`gz(SHAFT_Z0 - CLR)` to
  `FRAME_H + 2.0` in Z, past `gx(WALL_OUT - 1.0)` in X — deliberately past
  both `FRAME_H` and `CASE_W` so the slot reaches flush to the real
  boundary) breaks through the back face and the right wall's exterior at
  each of the 4 button positions before the fillet ever runs, leaving 4
  notches in what should be a plain rectangle. **Fix: fillet the outer edges
  of the raw blank immediately after creating it, before any other
  cut/join**, so the solver only ever sees a plain rectangle; every
  subsequent feature (button slots, PCB pocket, screw pilots, tongues,
  bosses, cable exit, etc.) then just cuts or joins into an already-rounded
  solid, a plain boolean with no fillet math involved. `build_front_frame()`
  and `build_back_cover()` both call `add_box_edge_fillet()` /
  `add_back_cover_finishing()` right after `rect_z(...NEW...)` creates the
  blank, before anything else. (The current design sidesteps this specific
  failure a second way too, now that only one face per part gets a face
  fillet at all — see the "Fillets and chamfers" bullet above; the frame's
  back loop, Z=FRAME_H, is never filleted, notched or not. Keep both fixes
  in mind if a future change re-adds a fillet on that face.) The window
  chamfer is the one exception that has to run *last* (`add_window_chamfer()`)
  since the window loop it
  chamfers doesn't exist until the window is cut. If you add a new outer-loop
  fillet anywhere in this file, put it first, not last, or expect this same
  failure back.

## OpenSCAD gotchas (`openscad-script.scad` only)

- **Extruding a profile along an axis other than Z needs a rotation, and the
  rotation flips a sign that has to be cancelled in the point data.**
  `extrude_xz_sym_y()` (lever profiles, extruded along Y) and
  `extrude_yz_sym_x()` (strut profiles, extruded along X) both do
  `linear_extrude()` (which always extrudes along local Z) then `rotate()` the
  result onto the axis actually wanted. The rotation's sign convention forces
  one coordinate of the input points to be pre-negated (or swapped) so the
  final geometry lands right-way-round instead of mirrored. If you inline a
  `linear_extrude()` somewhere else for a profile that isn't already in the
  XY-plane-extruded-along-Z shape, work through the same rotation math —
  don't assume `rotate([90,0,0])` alone does the right thing.
- **`rect_z`/`cyl_z` take corner points in either order**, same as Fusion's
  `addTwoPointRectangle` — this matters because `gx()` mirrors on the right
  wall, so `x0` is often numerically *greater* than `x1` at the call site.
- **`assert()` inside a `for` loop works fine** at module scope in current
  OpenSCAD — used for the same two invariant checks the Fusion script raises
  `RuntimeError` for (wall-pocket-reaches-slot, stand-screw-clears-boss).
