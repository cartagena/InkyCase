// ============================================================================
//  FULL CASE  ·  Pimoroni Inky Impression 7.3"
//  OpenSCAD port of impression-73.py (the Fusion 360 script).
//
//  Builds the same four components as the Fusion script:
//    front_frame()   185.20 x 134.20 x 18.00, PCB pocket, display window,
//                    button pockets / slots / channel lips, screw pilots
//    button_levers() x4, the rev 4 compliant bell crank
//    back_cover()    2.00 plate, slot tongues, cable exit, screw holes,
//                    stand mounting bosses, PCB hold-down posts
//    stand()         one piece: two angled struts on a shared spine
//
//  ORIGIN AND ORIENTATION (same as the Fusion script / your sketch)
//    X, Y  origin at the bottom-left of the outer profile
//    Z     0 at the front outer face, +Z out the back
//    The frame leans BACK, resting on its bottom-rear edge plus the two feet.
//
//  Units are millimetres natively - no MM scale factor needed (that was only
//  because Fusion's API works in centimetres).
//
//  See CLAUDE.md for the three-coordinate-system reasoning (board / lever /
//  case datums) and the derivation rules. Nothing about that reasoning
//  changes here - only the CSG mechanics differ from Fusion's feature tree:
//    Fusion "cut"  -> subtracted from the second child of difference()
//    Fusion "join" -> unioned into the first child of difference()
//    Fusion "new"  -> a fresh module / union(), no participantBodies needed
//                     (CSG always merges touching solids; there is no
//                     Fusion-style "silent extra body" failure mode here)
// ============================================================================

$fn = 48;

// ---- which parts to draw in the assembly preview --------------------------
SHOW_FRAME  = true;
SHOW_COVER  = true;
SHOW_LEVERS = true;
SHOW_STAND  = true;

// ---------------------------------------------------------------------------
//  CASE SHELL  (from your sketch)
// ---------------------------------------------------------------------------
WALL_T      =   5.00;   // sides and bottom
WALL_T_TOP  =   5.00;   // raise this alone to even up the window's borders.
                        // CASE_D follows; the PCB pocket does NOT move, so the
                        // board, the buttons and the window all stay put.
BEZEL_LIP   =   1.50;   // front face to the PCB pocket floor
FRAME_H     =  18.00;   // front frame on its own
BACK_T      =   2.00;   // back cover thickness
// CASE_W and CASE_D are DERIVED further down, from the board plus the walls.
// The pocket locates the PCB, so it is sized from the board and never from
// the outer dimensions - otherwise widening the frame loosens the board.

// Display window is set by the borders on the board, NOT centred on the case.
// BOTTOM is the case's Y = 0 edge, i.e. the same edge your 28.50 mm button is
// measured from. If the wide border turns out to be at the other end, swap
// BORDER_BOTTOM and BORDER_TOP.
BORDER_SIDE   =  6.80;
BORDER_BOTTOM = 16.20;  // was 16.00 - PCB_REFERENCE.md confirms the real
                        // panel border is 16.50, which left zero crop margin
BORDER_TOP    = 10.40;  // was 10.00 - the real border is 10.70; at 10.00 the
                        // window would have exposed ~0.20 mm of dead panel
WINDOW_LAP    =  0.50;  // window undersized this much per side, so the bezel
                        // crops the active area instead of exposing a sliver
                        // of dead panel

// ---------------------------------------------------------------------------
//  BOARD AND SWITCH
// ---------------------------------------------------------------------------
BOARD_W     = 174.20;
BOARD_D     = 123.20;
BOARD_T     =   1.60;
BOARD_GAP   =   0.50;   // board edge -> pocket wall, per side
SW_ACROSS   =   3.40;   // switch body PERPENDICULAR to the board edge
SW_ALONG    =   4.20;
SW_INSET    =   2.60;   // board edge -> near edge of the switch body
SW_CAP_Z    =   2.60;   // actuator cap above the PCB rear face
BTN_Y       = [28.50, 52.50, 76.50, 100.50];   // from the BOARD's bottom edge
BUTTON_SIDE = "right";  // looking at the back of the case

// ---------------------------------------------------------------------------
//  LEVER  (rev 4)
// ---------------------------------------------------------------------------
LEVER_W     = 10.00;
PIVOT_Z     =  4.60;
FLEX_LEN    =  2.00;
FLEX_T      =  0.45;
FLEX_W      =  6.00;
FLARE       =  0.30;
FLARE_LEN   =  0.40;
POST_T      =  1.75;
VARM_T      =  2.50;
ARM_T       =  2.50;
TIP_T       =  0.60;
TIP_X0      =  1.00;
NUB_W       =  3.00;
REST_GAP    =  0.15;
STOP_GAP    =  0.75;
HEAD_T      =  1.60;
HEAD_Z      =  8.00;
SHAFT_Z     =  4.50;
FOOT_Z0     =  0.00;
POCKET_D    =  3.25;    // into the wall's inner face
LIP_X       =  0.60;
LIP_Y       =  0.90;
CLR         =  0.20;

// ---------------------------------------------------------------------------
//  FASTENERS  (M2.5 self-tappers - an M3 needs a 6 mm wall, you have 5)
// ---------------------------------------------------------------------------
PILOT_D     =  2.10;
CLEAR_D     =  2.80;
HEAD_D      =  5.20;
SCREW_DEPTH =  8.00;

// ---------------------------------------------------------------------------
//  CABLE EXIT  (stadium slot in the back cover)
// ---------------------------------------------------------------------------
CABLE_X_FRAC = 0.50;    // across the case width
CABLE_Y     = 30.00;
CABLE_L     = 16.00;
CABLE_W     =  9.00;

// ---------------------------------------------------------------------------
//  PCB HOLD-DOWN
//    Posts hanging off the cover's inner face that press the board's margin
//    onto the pocket floor. Their only job is stopping the board falling
//    away from the pocket floor (e.g. when the case is stood up on the
//    stand) - not clamping it hard - so 4 posts spread around the perimeter
//    is enough; see PCB_POSTS below for which 4 and why.
//    Positions are 8.00 mm inside the board's edge - confirmed clear of the
//    4 M2 mounting holes (3.00 mm inset, all corners - see
//    PCB_REFERENCE.md) by about 7 mm. Check them against your Pi Zero
//    before printing - the posts run the full depth of the cavity.
// ---------------------------------------------------------------------------
PCB_POST_W     =  5.50; // square section
PCB_POST_CLR   =  0.00; // gap left at the board's rear face - see notes
PCB_POST_IN    =  8.00; // inset from the board edge - was 4.00, which put
                        // the corner posts only ~1.4 mm from the M2
                        // mounting hole centres (see PCB_REFERENCE.md);
                        // 8.00 clears them with margin
PCB_POST_MID_Y = 70.00; // mid posts: centred in the gap between levers 2 and
                        // 3, not on the board's centreline

// ---------------------------------------------------------------------------
//  STAND
// ---------------------------------------------------------------------------
LEAN        = 18.0;     // degrees back from vertical
STAND_FRAC  = [0.28, 0.72];     // leg positions as a fraction of CASE_W
STRUT_W     = 12.00;    // leg width in X
PAD_T       =  5.00;    // pad thickness, standing off the back cover
PAD_Y0      =  4.00;    // pad, low end  - the ears run past the strut so the
PAD_Y1      = 41.00;    // pad, high end   screw heads are reachable
STRUT_Y0    = 13.00;    // where the strut actually springs from the pad
STRUT_Y1    = 32.00;
REACH       = 58.00;    // how far behind the cover the foot lands
FOOT_LEN    = 12.00;    // length of the flat that sits on the table
STAND_SCREW_Y = [8.50, 36.50];  // in the ears, clear of the strut
SPINE_Y0    =  4.00;    // spine tying the two struts into one printable part
SPINE_Y1    = 16.00;
BOSS_T      =  4.00;    // boss added inside the cover to take the leg screws
BOSS_CLR    =  0.40;    // anything on the cover's INNER face has to sit inside
                        // the frame's pocket footprint or the cover will not
                        // seat. This is the gap left to the pocket walls.
STAND_PILOT_DEPTH = 5.00;
CBORE_D     =  5.20;
CBORE_DEPTH =  2.00;

// ---------------------------------------------------------------------------
//  DERIVED
// ---------------------------------------------------------------------------
CASE_H      = FRAME_H + BACK_T;                        // 20.00
POCKET_X0   = WALL_T;                                  // 5.00
POCKET_X1   = POCKET_X0 + BOARD_W + 2 * BOARD_GAP;     // 180.20
POCKET_Y0   = WALL_T;                                  // 5.00
POCKET_Y1   = POCKET_Y0 + BOARD_D + 2 * BOARD_GAP;     // 129.20
CASE_W      = POCKET_X1 + WALL_T;                      // 185.20
CASE_D      = POCKET_Y1 + WALL_T_TOP;                  // 134.20
CABLE_X     = CASE_W * CABLE_X_FRAC;
POCKET_FLR  = BEZEL_LIP;                               // 1.50
PCB_REAR_Z  = BEZEL_LIP + BOARD_T;                     // 3.10
DISP_X0     = POCKET_X0 + BOARD_GAP + BORDER_SIDE   + WINDOW_LAP;
DISP_X1     = POCKET_X1 - BOARD_GAP - BORDER_SIDE   - WINDOW_LAP;
DISP_Y0     = POCKET_Y0 + BOARD_GAP + BORDER_BOTTOM + WINDOW_LAP;
DISP_Y1     = POCKET_Y1 - BOARD_GAP - BORDER_TOP    - WINDOW_LAP;
DISP_W      = DISP_X1 - DISP_X0;
DISP_D      = DISP_Y1 - DISP_Y0;

BOARD_Y0    = POCKET_Y0 + BOARD_GAP;                   // 5.50
BUTTON_Y    = [for (y = BTN_Y) BOARD_Y0 + y];          // 34 58 82 106

BOARD_EDGE_X = (BUTTON_SIDE == "right") ? POCKET_X1 - BOARD_GAP   // 179.70
                                         : POCKET_X0 + BOARD_GAP;
XSIGN        = (BUTTON_SIDE == "right") ? -1.0 : 1.0;

// Lever datum: X = 0 at the board edge, +X inboard; Z = 0 at the PCB rear face
WALL_IN     = -BOARD_GAP;
WALL_OUT    = -BOARD_GAP - WALL_T;
POCKET_X    = WALL_IN - POCKET_D;
SW_CX       = SW_INSET + SW_ACROSS / 2.0;
WALL_TOP    = FRAME_H - PCB_REAR_Z;                    // 14.90

FLEX_X0     = POCKET_X + POST_T;
FLEX_X1     = FLEX_X0 + FLEX_LEN;
PIVOT_X     = FLEX_X0 + FLEX_LEN / 2.0;
FLEX_Z0     = PIVOT_Z - FLEX_T / 2.0;
FLEX_Z1     = PIVOT_Z + FLEX_T / 2.0;

BUTTON_Z    = WALL_TOP - HEAD_Z / 2.0;
LOUT        = SW_CX - PIVOT_X;
LIN         = BUTTON_Z - PIVOT_Z;
RATIO       = LIN / LOUT;

ARM_Z0      = PIVOT_Z - ARM_T / 2.0;
ARM_Z1      = PIVOT_Z + ARM_T / 2.0;
TIP_Z1      = ARM_Z0 + TIP_T;
NUB_Z       = SW_CAP_Z + REST_GAP;
NUB_X0      = SW_CX - NUB_W / 2.0;
NUB_X1      = SW_CX + NUB_W / 2.0;
VARM_X1     = NUB_X0 + VARM_T;

SHAFT_Z0    = BUTTON_Z - SHAFT_Z / 2.0;
SHAFT_Z1    = BUTTON_Z + SHAFT_Z / 2.0;
HEAD_X1     = WALL_OUT - STOP_GAP;
HEAD_X0     = HEAD_X1 - HEAD_T;
HEAD_Z0     = BUTTON_Z - HEAD_Z / 2.0;
HEAD_Z1     = BUTTON_Z + HEAD_Z / 2.0;
POST_TOP    = SHAFT_Z0 - 0.75;

POCKET_LAP  = 0.50;     // the pocket must break INTO the button slot, or a
                        // sliver of wall is left between them and the
                        // lever's foot cannot pass. Derived, not guessed.
POCKET_TOP  = SHAFT_Z0 - CLR + POCKET_LAP;

assert(POCKET_TOP > SHAFT_Z0 - CLR, str(
    "Wall pocket top (", POCKET_TOP, ") does not reach the button slot ",
    "bottom (", SHAFT_Z0 - CLR, "). Raise POCKET_LAP."));

CHAN_D      = POST_T + CLR;
CHAN_Y      = LEVER_W / 2.0 + CLR;
POCKET_W    = 2 * CHAN_Y;                              // 10.40, the pocket
                                                        // IS the channel
SLOT_W      = LEVER_W + 2 * CLR;

STAND_X     = [for (f = STAND_FRAC) CASE_W * f];
TAN_L       = tan(LEAN);
SIN_L       = sin(LEAN);
COS_L       = cos(LEAN);

BOARD_X0    = POCKET_X0 + BOARD_GAP;                   // 5.50
BOARD_X1    = POCKET_X1 - BOARD_GAP;                   // 179.70
BOARD_Y1    = POCKET_Y1 - BOARD_GAP;                   // 128.70

// Only 4 posts: the job is stopping the board falling away from the pocket
// floor, not clamping it, so a diagonal pair of corners (top-left,
// bottom-right) plus the two mid-edge posts is enough - no need for a post
// in all 4 corners.
//
// Bottom-left and top-right corners are skipped on purpose:
//   bottom-left  - the board has a 10-pin header (3V3/SDA/SCL/.../5V)
//                  mounted on the rear face right in that corner (confirmed
//                  against Pimoroni's dimensional drawing - it shows at
//                  bottom-right there, but that drawing is mirrored
//                  left-right relative to the physical board). No reliable
//                  footprint measurement for it, so rather than guess a
//                  clearance, the corner is left unsupported. If you
//                  measure the header's exact extent off the real board, a
//                  post can be added at
//                  [BOARD_X0 + PCB_POST_IN, BOARD_Y0 + PCB_POST_IN] with a
//                  verified offset.
//   top-right    - redundant once top-left and bottom-right are both
//                  present; dropped to keep the post count minimal.
PCB_POSTS = [
    [BOARD_X0 + PCB_POST_IN, BOARD_Y1 - PCB_POST_IN],   // top-left
    [BOARD_X1 - PCB_POST_IN, BOARD_Y0 + PCB_POST_IN],   // bottom-right
    [BOARD_X0 + PCB_POST_IN, PCB_POST_MID_Y],           // mid-left
    [BOARD_X1 - PCB_POST_IN, PCB_POST_MID_Y],           // mid-right
];

SCREW_POS = [
    [WALL_T / 2.0,           WALL_T / 2.0],
    [CASE_W - WALL_T / 2.0,  WALL_T / 2.0],
    [WALL_T / 2.0,           CASE_D - WALL_T_TOP / 2.0],
    [CASE_W - WALL_T / 2.0,  CASE_D - WALL_T_TOP / 2.0],
    [CASE_W / 2.0,           WALL_T / 2.0],
    [CASE_W / 2.0,           CASE_D - WALL_T_TOP / 2.0],
    // side mid-screws pinned to the pocket centre, not the case centre, so
    // they stay in the gap between levers 2 and 3 whatever WALL_T_TOP is
    [WALL_T / 2.0,           (POCKET_Y0 + POCKET_Y1) / 2.0],
    [CASE_W - WALL_T / 2.0,  (POCKET_Y0 + POCKET_Y1) / 2.0],
];

// 30-point lever profile in the LEVER datum (not yet mapped to case coords).
// In the Fusion script, points 2/27 and 5/24 are fenced off by divider lines
// so the sketch yields 3 separate profiles (anchor / flexure / body) that
// get extruded at two different widths. OpenSCAD has no sketch-profile step,
// so instead of splitting one polygon we slice this same point list into the
// three closed loops directly (see ANCHOR_IDX / FLEXURE_IDX / BODY_IDX below)
// - same geometry, no "expected 3 profiles" check needed.
PROFILE = [
    [POCKET_X,            FOOT_Z0],                //  0
    [FLEX_X0,             FOOT_Z0],                //  1
    [FLEX_X0,             FLEX_Z0 - FLARE],        //  2  flexure corner
    [FLEX_X0 + FLARE_LEN, FLEX_Z0],                //  3
    [FLEX_X1 - FLARE_LEN, FLEX_Z0],                //  4
    [FLEX_X1,             FLEX_Z0 - FLARE],        //  5  flexure corner
    [FLEX_X1,             ARM_Z0],                 //  6
    [NUB_X0,              ARM_Z0],                 //  7
    [NUB_X0,              NUB_Z],                  //  8
    [NUB_X1,              NUB_Z],                  //  9
    [NUB_X1,              TIP_Z1 + 0.60],          // 10
    [VARM_X1,             TIP_Z1 + 0.60],          // 11
    [VARM_X1,             SHAFT_Z1],               // 12
    [HEAD_X1,             SHAFT_Z1],               // 13
    [HEAD_X1,             HEAD_Z1],                // 14
    [HEAD_X0,             HEAD_Z1],                // 15
    [HEAD_X0,             HEAD_Z0],                // 16
    [HEAD_X1,             HEAD_Z0],                // 17
    [HEAD_X1,             SHAFT_Z0],               // 18
    [NUB_X0,              SHAFT_Z0],               // 19
    [NUB_X0,              TIP_Z1],                 // 20
    [TIP_X0,              TIP_Z1],                 // 21
    [TIP_X0,              ARM_Z1],                 // 22
    [FLEX_X1,             ARM_Z1],                 // 23
    [FLEX_X1,             FLEX_Z1 + FLARE],        // 24  flexure corner
    [FLEX_X1 - FLARE_LEN, FLEX_Z1],                // 25
    [FLEX_X0 + FLARE_LEN, FLEX_Z1],                // 26
    [FLEX_X0,             FLEX_Z1 + FLARE],        // 27  flexure corner
    [FLEX_X0,             POST_TOP],               // 28
    [POCKET_X,            POST_TOP],               // 29
];

// The three closed loops the Fusion dividers (2-27) and (5-24) cut the
// 30-point outline into. Each list is a valid winding on its own because the
// two chords are shared edges between adjacent loops.
ANCHOR_IDX  = [29, 0, 1, 2, 27, 28];
FLEXURE_IDX = [2, 3, 4, 5, 24, 25, 26, 27];
BODY_IDX    = [for (i = [5:24]) i];

// ---------------------------------------------------------------------------
//  Lever datum -> case coordinates
// ---------------------------------------------------------------------------

// +X pointed inboard; on the right-hand wall inboard is -X, so this mirrors
// the whole lever as well as translating it.
function gx(x) = BOARD_EDGE_X + XSIGN * x;
function gz(z) = PCB_REAR_Z + z;

function map_profile(pts) = [for (p = pts) [gx(p[0]), gz(p[1])]];
PROFILE_M = map_profile(PROFILE);
function pick(idx) = [for (i = idx) PROFILE_M[i]];

// ---------------------------------------------------------------------------
//  Sketch helpers.  rect_z/cyl_z take either corner order, same as Fusion's
//  addTwoPointRectangle - this matters because gx() mirrors on the right wall.
// ---------------------------------------------------------------------------

module rect_z(xa, ya, xb, yb, za, zb) {
    x0 = min(xa, xb); x1 = max(xa, xb);
    y0 = min(ya, yb); y1 = max(ya, yb);
    z0 = min(za, zb); z1 = max(za, zb);
    translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

module cyl_z(cx, cy, d, z0, z1) {
    translate([cx, cy, z0]) cylinder(h = z1 - z0, d = d);
}

// Rounded slot: a rectangle plus a circle at each end. hull() of the two end
// circles gives exactly that union (the straight sides are the common
// tangents), so it is used directly instead of building rect + 2 circles.
module stadium_z(cx, cy, length, width, z0, z1) {
    r = width / 2.0;
    a = max(length / 2.0 - r, 0.01);
    translate([0, 0, z0])
        linear_extrude(height = z1 - z0)
            hull() {
                translate([cx - a, cy]) circle(r = r);
                translate([cx + a, cy]) circle(r = r);
            }
}

// Extrude a profile given as [x,z] pairs symmetrically along Y by `width`.
// (rotate([90,0,0]) turns the extrude axis into Y while keeping X and Z fixed
// - see the comment above button_lever_at() for the derivation.)
module extrude_xz_sym_y(pts, width) {
    rotate([90, 0, 0])
        linear_extrude(height = width, center = true)
            polygon(points = pts);
}

// Extrude a profile given as [y,z] pairs symmetrically along X by `width`,
// then place it at X = cx. (Mirrors Fusion sketching on a YZ plane offset to
// X = sx and extruding symmetrically - see build_stand() below.)
module extrude_yz_sym_x(cx, pts_yz, width) {
    translate([cx, 0, 0])
        rotate([0, -90, 0])
            linear_extrude(height = width, center = true)
                polygon(points = [for (p = pts_yz) [p[1], p[0]]]);
}

// ---------------------------------------------------------------------------
//  1. FRONT FRAME
// ---------------------------------------------------------------------------

module front_frame() {
    difference() {
        union() {
            // Frame blank
            rect_z(0, 0, CASE_W, CASE_D, 0, FRAME_H);

            // Retaining lips: two ledges on each pocket's own side walls that
            // turn it into a T-channel. They clear the necked flexure by
            // 1.30 a side.
            for (by = BUTTON_Y) {
                for (s = [1, -1]) {
                    rect_z(
                        gx(POCKET_X + CHAN_D),
                        by + s * (POCKET_W / 2.0 - LIP_Y),
                        gx(POCKET_X + CHAN_D + LIP_X),
                        by + s * (POCKET_W / 2.0),
                        gz(FOOT_Z0), gz(POST_TOP));
                }
            }
        }
        union() {
            // PCB pocket, open to the rear
            rect_z(POCKET_X0, POCKET_Y0, POCKET_X1, POCKET_Y1,
                   POCKET_FLR, FRAME_H + 1);

            // Display window through the bezel lip
            rect_z(DISP_X0, DISP_Y0, DISP_X1, DISP_Y1,
                   -1.0, POCKET_FLR + 0.001);

            for (by = BUTTON_Y) {
                // Wall pocket. This IS the foot channel - same width, so
                // nothing ends up floating inside solid wall. Cut from the
                // PCB rear face up, so the bezel below stays full thickness.
                rect_z(gx(POCKET_X), by - POCKET_W / 2.0,
                       gx(WALL_IN + 0.5), by + POCKET_W / 2.0,
                       gz(FOOT_Z0), gz(POCKET_TOP));

                // Button slot, open at the top so the lever drops in
                rect_z(gx(WALL_OUT - 1.0), by - SLOT_W / 2.0,
                       gx(WALL_IN + 1.0), by + SLOT_W / 2.0,
                       gz(SHAFT_Z0 - CLR), FRAME_H + 2.0);
            }

            for (p = SCREW_POS) {
                cyl_z(p[0], p[1], PILOT_D, FRAME_H - SCREW_DEPTH, FRAME_H + 1);
            }
        }
    }
}

// ---------------------------------------------------------------------------
//  2. BUTTON LEVER
//
//  The lever is a single 2D profile extruded 10 mm in Y - this is why it
//  prints on its side with zero supports, and why the 0.45 mm flexure
//  survives. The flexure alone is necked to FLEX_W (6 mm) so it clears the
//  channel lips while sliding into the pocket. Don't widen it back to
//  LEVER_W or the lever becomes un-insertable.
// ---------------------------------------------------------------------------

module button_lever_at(by) {
    translate([0, by, 0])
        union() {
            extrude_xz_sym_y(pick(ANCHOR_IDX), LEVER_W);
            extrude_xz_sym_y(pick(BODY_IDX),   LEVER_W);
            extrude_xz_sym_y(pick(FLEXURE_IDX), FLEX_W);
        }
}

module button_levers() {
    for (by = BUTTON_Y) button_lever_at(by);
}

// ---------------------------------------------------------------------------
//  3. BACK COVER
// ---------------------------------------------------------------------------

module back_cover() {
    difference() {
        union() {
            // Cover blank
            rect_z(0, 0, CASE_W, CASE_D, FRAME_H, CASE_H);

            // Tongues that fill the top of each button slot flush with the
            // wall's OUTER face. Without these the button head only bears on
            // the slot's lower edge and the button tilts when pressed.
            for (by = BUTTON_Y) {
                rect_z(gx(WALL_OUT), by - (SLOT_W / 2.0 - 0.15),
                       gx(WALL_IN),  by + (SLOT_W / 2.0 - 0.15),
                       gz(SHAFT_Z1) + CLR, FRAME_H);
            }

            // Bosses that give the stand screws something to bite into -
            // the cover on its own is only 2 mm thick. Clipped to the pocket
            // footprint: the frame's bottom wall owns Y = 0 to 5.00 at every
            // Z, so an unclipped boss fouls it and the cover sits proud.
            for (sx = STAND_X) {
                bx0 = max(sx - STRUT_W / 2.0 - 3.0, POCKET_X0 + BOSS_CLR);
                bx1 = min(sx + STRUT_W / 2.0 + 3.0, POCKET_X1 - BOSS_CLR);
                by0 = max(PAD_Y0 - 1.0,             POCKET_Y0 + BOSS_CLR);
                by1 = min(PAD_Y1 + 1.0,             POCKET_Y1 - BOSS_CLR);

                for (sy = STAND_SCREW_Y) {
                    assert(sy >= by0 + PILOT_D && sy <= by1 - PILOT_D, str(
                        "Stand screw at Y=", sy, " has too little boss ",
                        "around it once clipped to the pocket (", by0,
                        " to ", by1, "). Move STAND_SCREW_Y or PAD_Y0."));
                }

                rect_z(bx0, by0, bx1, by1, FRAME_H - BOSS_T, FRAME_H);
            }

            // PCB hold-downs. Square columns down to the board's rear face.
            // A hard stop, not a spring - see the tuning note at the bottom.
            for (p = PCB_POSTS) {
                rect_z(p[0] - PCB_POST_W / 2.0, p[1] - PCB_POST_W / 2.0,
                       p[0] + PCB_POST_W / 2.0, p[1] + PCB_POST_W / 2.0,
                       PCB_REAR_Z + PCB_POST_CLR, FRAME_H);
            }
        }
        union() {
            stadium_z(CABLE_X, CABLE_Y, CABLE_L, CABLE_W,
                      FRAME_H - 1.0, CASE_H + 1.0);

            for (p = SCREW_POS) {
                cyl_z(p[0], p[1], CLEAR_D, FRAME_H - 1.0, CASE_H + 1.0);
            }

            for (sx = STAND_X) {
                for (sy = STAND_SCREW_Y) {
                    cyl_z(sx, sy, PILOT_D,
                          CASE_H - STAND_PILOT_DEPTH, CASE_H + 1.0);
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
//  4. STAND LEG
//
//  With the frame leaning back by LEAN, the table plane in frame coordinates
//  is Y = (Z - CASE_H) * tan(LEAN), passing through the case's bottom-rear
//  edge. The foot is trimmed on that line so it sits flat.
//
//  Fusion sketches each strut on a YZ plane offset to X = sx and extrudes it
//  symmetrically - i.e. the "width" direction is X, not Y. extrude_yz_sym_x()
//  reproduces that by extruding along Z as usual and then rotating the
//  extrude axis onto X (see its comment above).
// ---------------------------------------------------------------------------

FOOT_FAR  = [REACH * TAN_L, CASE_H + REACH];
FOOT_NEAR = [REACH * TAN_L - FOOT_LEN * SIN_L,
             CASE_H + REACH - FOOT_LEN * COS_L];

PTS_YZ = [
    [PAD_Y1,   CASE_H],           // top of the pad, against the cover
    [PAD_Y1,   CASE_H + PAD_T],   // top ear, rear face - nothing behind it
    [STRUT_Y1, CASE_H + PAD_T],   // step in to where the strut starts
    FOOT_FAR,                     // strut's upper edge, down to the table
    FOOT_NEAR,                    // the flat that sits on the table
    [STRUT_Y0, CASE_H + PAD_T],   // back up the strut's lower edge
    [PAD_Y0,   CASE_H + PAD_T],   // bottom ear, rear face
    [PAD_Y0,   CASE_H],           // bottom of the pad, against the cover
];

module stand() {
    difference() {
        union() {
            // Spine ties the two struts into one printable part.
            rect_z(STAND_X[0] - STRUT_W / 2.0, SPINE_Y0,
                   STAND_X[1] + STRUT_W / 2.0, SPINE_Y1,
                   CASE_H, CASE_H + PAD_T);

            for (sx = STAND_X) extrude_yz_sym_x(sx, PTS_YZ, STRUT_W);
        }
        union() {
            for (sx = STAND_X) {
                for (sy = STAND_SCREW_Y) {
                    cyl_z(sx, sy, CLEAR_D,
                          CASE_H - 1.0, CASE_H + PAD_T + 1.0);
                    cyl_z(sx, sy, CBORE_D,
                          CASE_H + PAD_T - CBORE_DEPTH, CASE_H + PAD_T + 1.0);
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
//  Assembly
// ---------------------------------------------------------------------------

module full_case() {
    if (SHOW_FRAME)  color("SlateGray", 0.9)        front_frame();
    if (SHOW_COVER)  color("DarkSlateGray", 0.9)    back_cover();
    if (SHOW_LEVERS) color("OrangeRed")             button_levers();
    if (SHOW_STAND)  color("DimGray", 0.9)          stand();
}

echo(str("CASE outer            ", CASE_W, " x ", CASE_D, " x ", CASE_H));
echo(str("PCB pocket            ", POCKET_X1 - POCKET_X0, " x ",
         POCKET_Y1 - POCKET_Y0, ", floor Z=", POCKET_FLR));
echo(str("Display window        ", DISP_W, " x ", DISP_D, " at (",
         DISP_X0, ", ", DISP_Y0, ")"));
echo(str("PCB rear face Z       ", PCB_REAR_Z));
echo(str("Button Y (", BUTTON_SIDE, " wall)   ", BUTTON_Y,
         ", switch X=", gx(SW_CX)));
echo(str("Lever ratio           ", RATIO, " : 1, travel ", STOP_GAP, " mm"));
echo(str("Stand struts at X =   ", STAND_X, ", leans ", LEAN, " deg"));

full_case();

// ============================================================================
//  ASSEMBLY (same as the Fusion script)
//    1. Drop the four levers into the frame from the rear: head down the
//       outside of the wall, shaft down the slot, foot down the channel
//       until it bottoms on the pocket floor.
//    2. Drop the PCB into the pocket, display first. Nothing clamps it until
//       the cover goes on - the six posts do that.
//    3. Fit the Pi.
//    4. Close with the back cover, 8 x M2.5 x 10 into the wall's rear edge.
//    5. Screw the stand onto the two bosses from OUTSIDE, 4 x M2.5 x 10.
//
//  PRINTING
//    Frame        as modelled, front face (Z=0) on the bed. No supports.
//    Levers       ON THEIR SIDE - the profile plane flat on the bed. PETG,
//                 0.15 mm layers, 4 perimeters, 100% infill. This is the only
//                 orientation in which a 0.45 mm flexure survives; rotate the
//                 STL 90 deg about X (or Y, depending on slicer) before
//                 slicing rather than changing this model.
//    Back cover   flat, tongues and bosses upward (as modelled, Z=FRAME_H
//                 face down).
//    Stand        pads down on the bed, as modelled with CASE_H toward the
//                 bed - the struts then grow upward at under 14 deg from
//                 vertical, so no supports.
//
//  THINGS THIS FILE DELIBERATELY LEAVES TO YOU (same list as the Fusion
//  script - fillets/chamfers are still meant to be added post-hoc, in a
//  slicer or by hand, not modelled parametrically here):
//    R0.4 at the lever arm's thickness step, 0.3 around the nub's bottom
//    face, 1 mm on the frame's outer edges, and a 0.4 mm relief groove around
//    the bottom of each wall pocket (this last one directly sets the
//    0.15 mm REST_GAP - the nozzle's inside-corner fillet would otherwise
//    hold the lever's foot proud).
//
//  PCB POSTS - the one number you will probably have to tune. See
//  CLAUDE.md / the Fusion script header for the PCB_POST_CLR tuning notes;
//  they apply unchanged here.
// ============================================================================
