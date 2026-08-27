#Author-
#Description-Complete case for the Pimoroni Inky Impression 7.3 - frame, buttons, back cover, stand

# ============================================================================
#  FULL CASE  ·  Pimoroni Inky Impression 7.3"
#
#  BUILDS FOUR COMPONENTS
#    Front frame   185.20 x 134.20 x 18.00, PCB pocket, display window,
#                  button pockets / slots / channel lips, screw pilots
#    Button lever  x4, the rev 4 compliant bell crank
#    Back cover    2.00 plate, slot tongues, cable exit, screw holes,
#                  stand mounting bosses, PCB hold-down posts
#    Stand         one piece: two angled struts on a shared spine
#
#  ORIGIN AND ORIENTATION
#    X, Y  match your sketch: origin at the bottom-left of the outer profile
#    Z     0 at the front outer face, +Z out the back
#    The frame leans BACK, resting on its bottom-rear edge plus the two feet.
#
#  HOW TO RUN
#    Utilities -> ADD-INS -> Scripts and Add-Ins -> Scripts -> "+" -> Create
#    -> Python. Replace the generated .py with this file, select it, Run.
#    Run it in an EMPTY design - it builds the frame from scratch rather than
#    modifying an existing body.
#
#  Fusion's API works in centimetres. Everything below is millimetres.
# ============================================================================

import adsk.core
import adsk.fusion
import math
import traceback

MM = 0.1

# ---------------------------------------------------------------------------
#  CASE SHELL  (from your sketch)
# ---------------------------------------------------------------------------
WALL_T      =   5.00    # sides and bottom
WALL_T_TOP  =   5.00    # raise this alone to even up the window's borders.
                        # CASE_D follows; the PCB pocket does NOT move, so the
                        # board, the buttons and the window all stay put.
BEZEL_LIP   =   1.50    # front face to the PCB pocket floor
FRAME_H     =  18.00    # front frame on its own
BACK_T      =   2.00    # back cover thickness
# CASE_W and CASE_D are DERIVED further down, from the board plus the walls.
# The pocket locates the PCB, so it is sized from the board and never from the
# outer dimensions - otherwise widening the frame loosens the board.

# Display window is set by the borders on the board, NOT centred on the case.
# BOTTOM is the case's Y = 0 edge, i.e. the same edge your 28.50 mm button is
# measured from. If the wide border turns out to be at the other end, swap
# BORDER_BOTTOM and BORDER_TOP.
BORDER_SIDE   =  6.80
BORDER_BOTTOM = 16.20   # was 16.00 - PCB_REFERENCE.md confirms the real
                        # panel border is 16.50, which left zero crop margin
BORDER_TOP    = 10.40   # was 10.00 - the real border is 10.70; at 10.00 the
                        # window would have exposed ~0.20 mm of dead panel
WINDOW_LAP    =  0.50   # window undersized this much per side, so the bezel
                        # crops the active area instead of exposing a sliver
                        # of dead panel

# ---------------------------------------------------------------------------
#  BOARD AND SWITCH
# ---------------------------------------------------------------------------
BOARD_W     = 174.20
BOARD_D     = 123.20
BOARD_T     =   1.60
BOARD_GAP   =   0.50    # board edge -> pocket wall, per side
SW_ACROSS   =   3.40    # switch body PERPENDICULAR to the board edge
SW_ALONG    =   4.20
SW_INSET    =   2.60    # board edge -> near edge of the switch body
SW_CAP_Z    =   2.60    # actuator cap above the PCB rear face
BTN_Y       = [28.50, 52.50, 76.50, 100.50]   # from the BOARD's bottom edge
BUTTON_SIDE = 'right'   # looking at the back of the case

# ---------------------------------------------------------------------------
#  LEVER  (rev 4)
# ---------------------------------------------------------------------------
LEVER_W     = 10.00
PIVOT_Z     =  4.60
FLEX_LEN    =  2.00
FLEX_T      =  0.45
FLEX_W      =  6.00
FLARE       =  0.30
FLARE_LEN   =  0.40
POST_T      =  1.75
VARM_T      =  2.50
ARM_T       =  2.50
TIP_T       =  0.60
TIP_X0      =  1.00
NUB_W       =  3.00
REST_GAP    =  0.15
STOP_GAP    =  0.75
HEAD_T      =  1.60
HEAD_Z      =  8.00
SHAFT_Z     =  4.50
FOOT_Z0     =  0.00
POCKET_D    =  3.25     # into the wall's inner face
LIP_X       =  0.60
LIP_Y       =  0.90
CLR         =  0.20

# ---------------------------------------------------------------------------
#  FASTENERS  (M2.5 self-tappers - an M3 needs a 6 mm wall, you have 5)
# ---------------------------------------------------------------------------
PILOT_D     =  2.10
CLEAR_D     =  2.80
HEAD_D      =  5.20
SCREW_DEPTH =  8.00

# ---------------------------------------------------------------------------
#  CABLE EXIT  (stadium slot in the back cover)
# ---------------------------------------------------------------------------
CABLE_X_FRAC = 0.50     # across the case width
CABLE_Y     = 30.00
CABLE_L     = 16.00
CABLE_W     =  9.00

# ---------------------------------------------------------------------------
#  PCB HOLD-DOWN
#    Posts hanging off the cover's inner face that press the board's margin
#    onto the pocket floor. Their only job is stopping the board falling
#    away from the pocket floor (e.g. when the case is stood up on the
#    stand) - not clamping it hard - so 4 posts spread around the perimeter
#    is enough; see PCB_POSTS below for which 4 and why.
#    Positions are 8.00 mm inside the board's edge - confirmed clear of the
#    4 M2 mounting holes (3.00 mm inset, all corners - see
#    PCB_REFERENCE.md) by about 7 mm. Check them against your Pi Zero before
#    printing - the posts run the full depth of the cavity.
# ---------------------------------------------------------------------------
PCB_POST_W   =  5.50    # square section
PCB_POST_CLR =  0.00    # gap left at the board's rear face - see notes
PCB_POST_IN  =  8.00    # inset from the board edge - was 4.00, which put
                        # the corner posts only ~1.4 mm from the M2 mounting
                        # hole centres (see PCB_REFERENCE.md); 8.00 clears
                        # them with margin regardless of the hole's exact
                        # diameter
PCB_POST_MID_Y = 70.00  # mid posts: centred in the gap between levers 2 and 3,
                        # not on the board's centreline

# ---------------------------------------------------------------------------
#  STAND
# ---------------------------------------------------------------------------
LEAN        = 18.0      # degrees back from vertical
STAND_FRAC  = [0.28, 0.72]      # leg positions as a fraction of CASE_W
STRUT_W     = 12.00     # leg width in X
PAD_T       =  5.00     # pad thickness, standing off the back cover
PAD_Y0      =  4.00     # pad, low end  - the ears run past the strut so the
PAD_Y1      = 41.00     # pad, high end   screw heads are reachable
STRUT_Y0    = 13.00     # where the strut actually springs from the pad
STRUT_Y1    = 32.00
REACH       = 58.00     # how far behind the cover the foot lands
FOOT_LEN    = 12.00     # length of the flat that sits on the table
STAND_SCREW_Y = [8.50, 36.50]   # in the ears, clear of the strut
SPINE_Y0    =  4.00     # spine tying the two struts into one printable part
SPINE_Y1    = 16.00
BOSS_T      =  4.00     # boss added inside the cover to take the leg screws
BOSS_CLR    =  0.40     # anything on the cover's INNER face has to sit inside
                        # the frame's pocket footprint or the cover will not
                        # seat. This is the gap left to the pocket walls.
STAND_PILOT_DEPTH = 5.00
CBORE_D     =  5.20
CBORE_DEPTH =  2.00

# ---------------------------------------------------------------------------
#  DERIVED
# ---------------------------------------------------------------------------
CASE_H      = FRAME_H + BACK_T                 # 20.00
POCKET_X0   = WALL_T                                  # 5.00
POCKET_X1   = POCKET_X0 + BOARD_W + 2 * BOARD_GAP     # 180.20
POCKET_Y0   = WALL_T                                  # 5.00
POCKET_Y1   = POCKET_Y0 + BOARD_D + 2 * BOARD_GAP     # 129.20
CASE_W      = POCKET_X1 + WALL_T                      # 185.20
CASE_D      = POCKET_Y1 + WALL_T_TOP                  # 134.20
CABLE_X     = CASE_W * CABLE_X_FRAC
POCKET_FLR  = BEZEL_LIP                        # 1.50
PCB_REAR_Z  = BEZEL_LIP + BOARD_T              # 3.10
DISP_X0     = POCKET_X0 + BOARD_GAP + BORDER_SIDE   + WINDOW_LAP
DISP_X1     = POCKET_X1 - BOARD_GAP - BORDER_SIDE   - WINDOW_LAP
DISP_Y0     = POCKET_Y0 + BOARD_GAP + BORDER_BOTTOM + WINDOW_LAP
DISP_Y1     = POCKET_Y1 - BOARD_GAP - BORDER_TOP    - WINDOW_LAP
DISP_W      = DISP_X1 - DISP_X0
DISP_D      = DISP_Y1 - DISP_Y0

BOARD_Y0    = POCKET_Y0 + BOARD_GAP            # 5.50
BUTTON_Y    = [BOARD_Y0 + y for y in BTN_Y]    # 34 58 82 106

if BUTTON_SIDE == 'right':
    BOARD_EDGE_X = POCKET_X1 - BOARD_GAP       # 179.70
    XSIGN = -1.0
else:
    BOARD_EDGE_X = POCKET_X0 + BOARD_GAP
    XSIGN = 1.0

# Lever datum: X = 0 at the board edge, +X inboard; Z = 0 at the PCB rear face
WALL_IN     = -BOARD_GAP
WALL_OUT    = -BOARD_GAP - WALL_T
POCKET_X    = WALL_IN - POCKET_D
SW_CX       = SW_INSET + SW_ACROSS / 2.0
WALL_TOP    = FRAME_H - PCB_REAR_Z             # 14.90

FLEX_X0     = POCKET_X + POST_T
FLEX_X1     = FLEX_X0 + FLEX_LEN
PIVOT_X     = FLEX_X0 + FLEX_LEN / 2.0
FLEX_Z0     = PIVOT_Z - FLEX_T / 2.0
FLEX_Z1     = PIVOT_Z + FLEX_T / 2.0

BUTTON_Z    = WALL_TOP - HEAD_Z / 2.0
LOUT        = SW_CX - PIVOT_X
LIN         = BUTTON_Z - PIVOT_Z
RATIO       = LIN / LOUT

ARM_Z0      = PIVOT_Z - ARM_T / 2.0
ARM_Z1      = PIVOT_Z + ARM_T / 2.0
TIP_Z1      = ARM_Z0 + TIP_T
NUB_Z       = SW_CAP_Z + REST_GAP
NUB_X0      = SW_CX - NUB_W / 2.0
NUB_X1      = SW_CX + NUB_W / 2.0
VARM_X1     = NUB_X0 + VARM_T

SHAFT_Z0    = BUTTON_Z - SHAFT_Z / 2.0
SHAFT_Z1    = BUTTON_Z + SHAFT_Z / 2.0
HEAD_X1     = WALL_OUT - STOP_GAP
HEAD_X0     = HEAD_X1 - HEAD_T
HEAD_Z0     = BUTTON_Z - HEAD_Z / 2.0
HEAD_Z1     = BUTTON_Z + HEAD_Z / 2.0
POST_TOP    = SHAFT_Z0 - 0.75

POCKET_LAP  = 0.50      # the pocket must break INTO the button slot, or a
                        # sliver of wall is left between them and the lever's
                        # foot cannot pass. Derived from the slot, not guessed.
POCKET_TOP  = SHAFT_Z0 - CLR + POCKET_LAP

CHAN_D      = POST_T + CLR
CHAN_Y      = LEVER_W / 2.0 + CLR
POCKET_W    = 2 * CHAN_Y                       # 10.40, the pocket IS the channel
SLOT_W      = LEVER_W + 2 * CLR

STAND_X     = [CASE_W * f for f in STAND_FRAC]
TAN_L       = math.tan(math.radians(LEAN))
SIN_L       = math.sin(math.radians(LEAN))
COS_L       = math.cos(math.radians(LEAN))

BOARD_X0    = POCKET_X0 + BOARD_GAP            # 5.50
BOARD_X1    = POCKET_X1 - BOARD_GAP            # 179.70
BOARD_Y1    = POCKET_Y1 - BOARD_GAP            # 128.70

# Only 4 posts: the job is stopping the board falling away from the pocket
# floor, not clamping it, so a diagonal pair of corners (top-left,
# bottom-right) plus the two mid-edge posts is enough - no need for a post
# in all 4 corners.
#
# Bottom-left and top-right corners are skipped on purpose:
#   bottom-left  - the board has a 10-pin header (3V3/SDA/SCL/.../5V)
#                  mounted on the rear face right in that corner (confirmed
#                  against Pimoroni's dimensional drawing - it shows at
#                  bottom-right there, but that drawing is mirrored
#                  left-right relative to the physical board). No reliable
#                  footprint measurement for it, so rather than guess a
#                  clearance, the corner is left unsupported. If you measure
#                  the header's exact extent off the real board, a post can
#                  be added at (BOARD_X0 + PCB_POST_IN, BOARD_Y0 + PCB_POST_IN)
#                  with a verified offset.
#   top-right    - redundant once top-left and bottom-right are both
#                  present; dropped to keep the post count minimal.
PCB_POSTS = [
    (BOARD_X0 + PCB_POST_IN, BOARD_Y1 - PCB_POST_IN),   # top-left
    (BOARD_X1 - PCB_POST_IN, BOARD_Y0 + PCB_POST_IN),   # bottom-right
    (BOARD_X0 + PCB_POST_IN, PCB_POST_MID_Y),           # mid-left
    (BOARD_X1 - PCB_POST_IN, PCB_POST_MID_Y),           # mid-right
]

SCREW_POS = [
    (WALL_T / 2.0,           WALL_T / 2.0),
    (CASE_W - WALL_T / 2.0,  WALL_T / 2.0),
    (WALL_T / 2.0,           CASE_D - WALL_T_TOP / 2.0),
    (CASE_W - WALL_T / 2.0,  CASE_D - WALL_T_TOP / 2.0),
    (CASE_W / 2.0,           WALL_T / 2.0),
    (CASE_W / 2.0,           CASE_D - WALL_T_TOP / 2.0),
    # side mid-screws pinned to the pocket centre, not the case centre, so they
    # stay in the gap between levers 2 and 3 whatever WALL_T_TOP is
    (WALL_T / 2.0,           (POCKET_Y0 + POCKET_Y1) / 2.0),
    (CASE_W - WALL_T / 2.0,  (POCKET_Y0 + POCKET_Y1) / 2.0),
]

# 30-point lever profile in the lever datum. 2/27 and 5/24 are the flexure
# corners; the divider lines between them fence it off for the narrower extrude.
PROFILE = [
    (POCKET_X,            FOOT_Z0),
    (FLEX_X0,             FOOT_Z0),
    (FLEX_X0,             FLEX_Z0 - FLARE),
    (FLEX_X0 + FLARE_LEN, FLEX_Z0),
    (FLEX_X1 - FLARE_LEN, FLEX_Z0),
    (FLEX_X1,             FLEX_Z0 - FLARE),
    (FLEX_X1,             ARM_Z0),
    (NUB_X0,              ARM_Z0),
    (NUB_X0,              NUB_Z),
    (NUB_X1,              NUB_Z),
    (NUB_X1,              TIP_Z1 + 0.60),
    (VARM_X1,             TIP_Z1 + 0.60),
    (VARM_X1,             SHAFT_Z1),
    (HEAD_X1,             SHAFT_Z1),
    (HEAD_X1,             HEAD_Z1),
    (HEAD_X0,             HEAD_Z1),
    (HEAD_X0,             HEAD_Z0),
    (HEAD_X1,             HEAD_Z0),
    (HEAD_X1,             SHAFT_Z0),
    (NUB_X0,              SHAFT_Z0),
    (NUB_X0,              TIP_Z1),
    (TIP_X0,              TIP_Z1),
    (TIP_X0,              ARM_Z1),
    (FLEX_X1,             ARM_Z1),
    (FLEX_X1,             FLEX_Z1 + FLARE),
    (FLEX_X1 - FLARE_LEN, FLEX_Z1),
    (FLEX_X0 + FLARE_LEN, FLEX_Z1),
    (FLEX_X0,             FLEX_Z1 + FLARE),
    (FLEX_X0,             POST_TOP),
    (POCKET_X,            POST_TOP),
]
FLEX_DIVIDERS = [(2, 27), (5, 24)]

NEW  = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT  = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation


# ---------------------------------------------------------------------------
#  Lever datum -> case coordinates
# ---------------------------------------------------------------------------

def gx(x):
    """+X pointed inboard; on the right-hand wall inboard is -X, so this
    mirrors the whole lever as well as translating it."""
    return BOARD_EDGE_X + XSIGN * x


def gz(z):
    return PCB_REAR_Z + z


# ---------------------------------------------------------------------------
#  Sketch helpers.  Points go through modelToSketchSpace so we never have to
#  assume which way round Fusion orients a construction plane.
# ---------------------------------------------------------------------------

def pt_xy(sk, x, y):
    return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y * MM, 0.0))


def pt_xz(sk, x, z):
    return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, 0.0, z * MM))


def pt_on_yz(sk, x, y, z):
    """Point on a YZ plane that may be offset in X."""
    return sk.modelToSketchSpace(
        adsk.core.Point3D.create(x * MM, y * MM, z * MM))


def closed_polyline(sk, pts):
    lines = sk.sketchCurves.sketchLines
    made = [lines.addByTwoPoints(pts[0], pts[1])]
    for i in range(1, len(pts) - 1):
        made.append(lines.addByTwoPoints(made[-1].endSketchPoint, pts[i + 1]))
    made.append(lines.addByTwoPoints(made[-1].endSketchPoint,
                                     made[0].startSketchPoint))
    return made


def _extrude_z(comp, prof, z0, z1, op, name, participants):
    exts = comp.features.extrudeFeatures
    inp = exts.createInput(prof, op)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(
        adsk.core.ValueInput.createByReal(z0 * MM))
    inp.setDistanceExtent(False,
                          adsk.core.ValueInput.createByReal((z1 - z0) * MM))
    if participants:
        inp.participantBodies = participants
    feat = exts.add(inp)
    feat.name = name
    return feat


def rect_z(comp, x0, y0, x1, y1, z0, z1, op, name, participants=None):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = name
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt_xy(sk, x0, y0),
                                                     pt_xy(sk, x1, y1))
    return _extrude_z(comp, sk.profiles.item(0), z0, z1, op, name, participants)


def cyl_z(comp, cx, cy, d, z0, z1, op, name, participants=None):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = name
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt_xy(sk, cx, cy),
                                                    d / 2.0 * MM)
    return _extrude_z(comp, sk.profiles.item(0), z0, z1, op, name, participants)


def stadium_z(comp, cx, cy, length, width, z0, z1, op, name, participants=None):
    """Rounded slot: a rectangle plus a circle at each end, all profiles cut
    together so the result is their union."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = name
    r = width / 2.0
    a = max(length / 2.0 - r, 0.01)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt_xy(sk, cx - a, cy - r),
                                                     pt_xy(sk, cx + a, cy + r))
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt_xy(sk, cx - a, cy), r * MM)
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt_xy(sk, cx + a, cy), r * MM)
    coll = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        coll.add(sk.profiles.item(i))
    return _extrude_z(comp, coll, z0, z1, op, name, participants)


def extrude_sym_y(comp, prof, width, op, name, participants=None):
    exts = comp.features.extrudeFeatures
    inp = exts.createInput(prof, op)
    inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(width * MM), True)
    if participants:
        inp.participantBodies = participants
    feat = exts.add(inp)
    feat.name = name
    return feat


# ---------------------------------------------------------------------------
#  1. FRONT FRAME
# ---------------------------------------------------------------------------

def build_front_frame(comp):
    body = rect_z(comp, 0, 0, CASE_W, CASE_D, 0, FRAME_H,
                  NEW, 'Frame blank').bodies.item(0)
    body.name = 'Front frame'
    P = [body]

    # PCB pocket, open to the rear
    rect_z(comp, POCKET_X0, POCKET_Y0, POCKET_X1, POCKET_Y1,
           POCKET_FLR, FRAME_H + 1, CUT, 'PCB pocket', P)

    # Display window through the bezel lip
    rect_z(comp, DISP_X0, DISP_Y0, DISP_X1, DISP_Y1,
           -1.0, POCKET_FLR + 0.001, CUT, 'Display window', P)

    if POCKET_TOP <= SHAFT_Z0 - CLR:
        raise RuntimeError(
            'Wall pocket top ({:.2f}) does not reach the button slot bottom '
            '({:.2f}). Raise POCKET_LAP.'.format(POCKET_TOP, SHAFT_Z0 - CLR))

    for i, by in enumerate(BUTTON_Y):
        tag = str(i + 1)

        # Wall pocket. This IS the foot channel - same width, so nothing
        # ends up floating inside solid wall. Cut from the PCB rear face up,
        # so the bezel below stays full thickness.
        rect_z(comp, gx(POCKET_X), by - POCKET_W / 2.0,
               gx(WALL_IN + 0.5), by + POCKET_W / 2.0,
               gz(FOOT_Z0), gz(POCKET_TOP), CUT, 'Wall pocket ' + tag, P)

        # Button slot, open at the top so the lever drops in
        rect_z(comp, gx(WALL_OUT - 1.0), by - SLOT_W / 2.0,
               gx(WALL_IN + 1.0), by + SLOT_W / 2.0,
               gz(SHAFT_Z0 - CLR), FRAME_H + 2.0, CUT, 'Button slot ' + tag, P)

        # Retaining lips: two ledges on the pocket's own side walls that turn
        # it into a T-channel. They clear the necked flexure by 1.30 a side.
        for s in (1.0, -1.0):
            rect_z(comp, gx(POCKET_X + CHAN_D),
                   by + s * (POCKET_W / 2.0 - LIP_Y),
                   gx(POCKET_X + CHAN_D + LIP_X),
                   by + s * (POCKET_W / 2.0),
                   gz(FOOT_Z0), gz(POST_TOP), JOIN,
                   'Channel lip {}{}'.format(tag, '+' if s > 0 else '-'), P)

    for j, (sx, sy) in enumerate(SCREW_POS):
        cyl_z(comp, sx, sy, PILOT_D, FRAME_H - SCREW_DEPTH, FRAME_H + 1,
              CUT, 'Screw pilot {}'.format(j + 1), P)

    return body


# ---------------------------------------------------------------------------
#  2. BUTTON LEVER
# ---------------------------------------------------------------------------

def build_lever(comp):
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = 'Lever profile'
    sk.isComputeDeferred = True

    pts = [pt_xz(sk, gx(x), gz(z)) for (x, z) in PROFILE]
    lines = closed_polyline(sk, pts)
    for a, b in FLEX_DIVIDERS:
        sk.sketchCurves.sketchLines.addByTwoPoints(
            lines[a].startSketchPoint, lines[b].startSketchPoint)

    sk.isComputeDeferred = False

    acc = adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
    profs = sorted([sk.profiles.item(i) for i in range(sk.profiles.count)],
                   key=lambda p: p.areaProperties(acc).area)
    if len(profs) != 3:
        raise RuntimeError(
            'Expected 3 lever profiles (anchor, flexure, body), got {}.'
            .format(len(profs)))

    coll = adsk.core.ObjectCollection.create()
    for p in profs[1:]:
        coll.add(p)
    main = extrude_sym_y(comp, coll, LEVER_W, NEW, 'Lever body')
    bodies = [main.bodies.item(i) for i in range(main.bodies.count)]

    extrude_sym_y(comp, profs[0], FLEX_W, JOIN, 'Flexure', bodies)

    for i in range(comp.bRepBodies.count):
        comp.bRepBodies.item(i).name = 'Button lever'


# ---------------------------------------------------------------------------
#  3. BACK COVER
# ---------------------------------------------------------------------------

def build_back_cover(comp):
    body = rect_z(comp, 0, 0, CASE_W, CASE_D, FRAME_H, CASE_H,
                  NEW, 'Cover blank').bodies.item(0)
    body.name = 'Back cover'
    P = [body]

    # Tongues that fill the top of each button slot flush with the wall's
    # OUTER face. Without these the button head only bears on the slot's lower
    # edge and the button tilts when you press it.
    for i, by in enumerate(BUTTON_Y):
        rect_z(comp, gx(WALL_OUT), by - (SLOT_W / 2.0 - 0.15),
               gx(WALL_IN), by + (SLOT_W / 2.0 - 0.15),
               gz(SHAFT_Z1) + CLR, FRAME_H, JOIN,
               'Slot tongue {}'.format(i + 1), P)

    # Bosses that give the stand screws something to bite into - the cover on
    # its own is only 2 mm thick. Clipped to the pocket footprint: the leg's
    # pad runs down to Y = 4.00, but the frame's bottom wall owns Y = 0 to
    # 5.00 at every Z, so an unclipped boss fouls it and the cover sits proud.
    for i, sx in enumerate(STAND_X):
        bx0 = max(sx - STRUT_W / 2.0 - 3.0, POCKET_X0 + BOSS_CLR)
        bx1 = min(sx + STRUT_W / 2.0 + 3.0, POCKET_X1 - BOSS_CLR)
        by0 = max(PAD_Y0 - 1.0,             POCKET_Y0 + BOSS_CLR)
        by1 = min(PAD_Y1 + 1.0,             POCKET_Y1 - BOSS_CLR)

        for sy in STAND_SCREW_Y:
            if not (by0 + PILOT_D <= sy <= by1 - PILOT_D):
                raise RuntimeError(
                    'Stand screw at Y {:.2f} has too little boss around it '
                    'once clipped to the pocket ({:.2f} to {:.2f}). Move '
                    'STAND_SCREW_Y or PAD_Y0.'.format(sy, by0, by1))

        rect_z(comp, bx0, by0, bx1, by1, FRAME_H - BOSS_T, FRAME_H, JOIN,
               'Stand boss {}'.format(i + 1), P)

    # PCB hold-downs. Square columns down to the board's rear face. These are
    # a hard stop, not a spring - see the tuning note at the bottom.
    for i, (px, py) in enumerate(PCB_POSTS):
        rect_z(comp, px - PCB_POST_W / 2.0, py - PCB_POST_W / 2.0,
               px + PCB_POST_W / 2.0, py + PCB_POST_W / 2.0,
               PCB_REAR_Z + PCB_POST_CLR, FRAME_H, JOIN,
               'PCB post {}'.format(i + 1), P)

    stadium_z(comp, CABLE_X, CABLE_Y, CABLE_L, CABLE_W,
              FRAME_H - 1.0, CASE_H + 1.0, CUT, 'Cable exit', P)

    for j, (sx, sy) in enumerate(SCREW_POS):
        cyl_z(comp, sx, sy, CLEAR_D, FRAME_H - 1.0, CASE_H + 1.0,
              CUT, 'Case screw hole {}'.format(j + 1), P)

    for i, sx in enumerate(STAND_X):
        for k, sy in enumerate(STAND_SCREW_Y):
            cyl_z(comp, sx, sy, PILOT_D, CASE_H - STAND_PILOT_DEPTH,
                  CASE_H + 1.0, CUT,
                  'Stand pilot {}{}'.format(i + 1, k + 1), P)

    return body


# ---------------------------------------------------------------------------
#  4. STAND LEG
#
#  With the frame leaning back by LEAN, the table plane in frame coordinates
#  is Y = (Z - CASE_H) * tan(LEAN), passing through the case's bottom-rear
#  edge. The foot is trimmed on that line so it sits flat.
# ---------------------------------------------------------------------------

def build_stand(comp):
    foot_far  = (REACH * TAN_L, CASE_H + REACH)
    foot_near = (REACH * TAN_L - FOOT_LEN * SIN_L,
                 CASE_H + REACH - FOOT_LEN * COS_L)

    pts_yz = [
        (PAD_Y1,   CASE_H),           # top of the pad, against the cover
        (PAD_Y1,   CASE_H + PAD_T),   # top ear, rear face - nothing behind it
        (STRUT_Y1, CASE_H + PAD_T),   # step in to where the strut starts
        foot_far,                     # strut's upper edge, down to the table
        foot_near,                    # the flat that sits on the table
        (STRUT_Y0, CASE_H + PAD_T),   # back up the strut's lower edge
        (PAD_Y0,   CASE_H + PAD_T),   # bottom ear, rear face
        (PAD_Y0,   CASE_H),           # bottom of the pad, against the cover
    ]

    # Spine FIRST. The two struts do not touch each other, so if the first one
    # is the new body the second has nothing to join to and Fusion quietly
    # makes a separate body - which then misses every cut that follows.
    # Building the spine first gives both struts a common parent.
    body = rect_z(comp, STAND_X[0] - STRUT_W / 2.0, SPINE_Y0,
                  STAND_X[1] + STRUT_W / 2.0, SPINE_Y1,
                  CASE_H, CASE_H + PAD_T, NEW, 'Spine').bodies.item(0)
    body.name = 'Stand'
    P = [body]

    for i, sx in enumerate(STAND_X):
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.yZConstructionPlane,
                        adsk.core.ValueInput.createByReal(sx * MM))
        plane = planes.add(pin)
        plane.name = 'Strut {} plane'.format(i + 1)

        sk = comp.sketches.add(plane)
        sk.name = 'Strut {} profile'.format(i + 1)
        sk.isComputeDeferred = True
        closed_polyline(sk, [pt_on_yz(sk, sx, y, z) for (y, z) in pts_yz])
        sk.isComputeDeferred = False

        extrude_sym_y(comp, sk.profiles.item(0), STRUT_W, JOIN,
                      'Strut {}'.format(i + 1), P)

    if comp.bRepBodies.count != 1:
        raise RuntimeError(
            'Stand came out as {} bodies instead of 1. The spine must overlap '
            'both strut pads in X and Y for the joins to merge.'
            .format(comp.bRepBodies.count))

    for i, sx in enumerate(STAND_X):
        for k, sy in enumerate(STAND_SCREW_Y):
            cyl_z(comp, sx, sy, CLEAR_D, CASE_H - 1.0, CASE_H + PAD_T + 1.0,
                  CUT, 'Stand screw {}{}'.format(i + 1, k + 1), P)
            cyl_z(comp, sx, sy, CBORE_D,
                  CASE_H + PAD_T - CBORE_DEPTH, CASE_H + PAD_T + 1.0,
                  CUT, 'Stand counterbore {}{}'.format(i + 1, k + 1), P)

    return body


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Switch to the Design workspace and try again.')
            return
        root = design.rootComponent

        def new_comp(name, tx=0.0, ty=0.0, tz=0.0):
            m = adsk.core.Matrix3D.create()
            m.translation = adsk.core.Vector3D.create(tx * MM, ty * MM, tz * MM)
            occ = root.occurrences.addNewComponent(m)
            occ.component.name = name
            return occ.component

        build_front_frame(new_comp('Front frame'))
        build_back_cover(new_comp('Back cover'))

        lever = new_comp('Button lever', 0.0, BUTTON_Y[0], 0.0)
        build_lever(lever)
        for by in BUTTON_Y[1:]:
            m = adsk.core.Matrix3D.create()
            m.translation = adsk.core.Vector3D.create(0, by * MM, 0)
            root.occurrences.addExistingComponent(lever, m)

        build_stand(new_comp('Stand'))

        ui.messageBox(
            'Built the full case.\n\n'
            'FRAME\n'
            '  outer            {:.2f} x {:.2f} x {:.2f}\n'
            '  walls            {:.2f} sides and bottom, {:.2f} top\n'
            '  PCB pocket       {:.2f} x {:.2f}, floor at Z = {:.2f}\n'
            '  display window   {:.2f} x {:.2f}, corner at ({:.2f}, {:.2f})\n'
            '  borders           {:.1f} sides, {:.1f} bottom, {:.1f} top\n'
            '  PCB rear face    Z = {:.2f}\n\n'
            'BUTTONS on the {} wall\n'
            '  centrelines      Y = {}\n'
            '  switch centre    X = {:.2f}\n'
            '  head sticks out  to X = {:.2f}\n'
            '  ratio {:.3f} : 1, travel {:.2f} mm, about 210 gf\n\n'
            'BACK COVER\n'
            '  {:.2f} thick, cable exit {:.0f} x {:.0f} at ({:.1f}, {:.1f})\n'
            '  {} case screws, M2.5 x 10 self-tapping\n'
            '  {} PCB posts, {:.1f} sq, tips at Z = {:.2f}\n\n'
            'STAND\n'
            '  leans {:.0f} deg, feet {:.0f} mm behind the cover\n'
            '  one piece, struts at X = {:.1f} and {:.1f}\n'
            '  4 x M2.5 x 10 from outside'
            .format(CASE_W, CASE_D, CASE_H, WALL_T, WALL_T_TOP,
                    POCKET_X1 - POCKET_X0, POCKET_Y1 - POCKET_Y0, POCKET_FLR,
                    DISP_W, DISP_D, DISP_X0, DISP_Y0,
                    BORDER_SIDE, BORDER_BOTTOM, BORDER_TOP, PCB_REAR_Z,
                    BUTTON_SIDE,
                    ' / '.join('{:.0f}'.format(y) for y in BUTTON_Y),
                    gx(SW_CX), gx(HEAD_X0), RATIO, STOP_GAP,
                    BACK_T, CABLE_L, CABLE_W, CABLE_X, CABLE_Y,
                    len(SCREW_POS), len(PCB_POSTS), PCB_POST_W,
                    PCB_REAR_Z + PCB_POST_CLR,
                    LEAN, REACH, STAND_X[0], STAND_X[1]),
            'Inky Impression 7.3 case')

    except Exception:
        if ui:
            ui.messageBox('Script failed:\n\n{}'.format(traceback.format_exc()))


# ============================================================================
#  ASSEMBLY
#    1. Drop the four levers into the frame from the rear: head down the
#       outside of the wall, shaft down the slot, foot down the channel until
#       it bottoms on the pocket floor.
#    2. Drop the PCB into the pocket, display first. Nothing clamps it until
#       the cover goes on - the six posts do that.
#    3. Fit the Pi.
#    4. Close with the back cover, 8 x M2.5 x 10 into the wall's rear edge.
#    5. Screw the stand onto the two bosses from OUTSIDE, 4 x M2.5 x 10. The
#       heads land in counterbores in the pad's ears, which stick out past the
#       strut at both ends so a driver can reach them.
#
#  PRINTING
#    Frame        face down, no supports. 0.2 mm layers.
#    Levers       ON THEIR SIDE, profile flat on the bed, 10 mm build height.
#                 PETG, 0.15 mm layers, 4 perimeters, 100% infill. This is the
#                 only orientation in which a 0.45 mm flexure survives.
#    Back cover   flat, tongues and bosses upward.
#    Stand        PADS DOWN on the bed. The struts then grow upward at
#                 under 14 degrees from vertical, so no supports. Printing it
#                 on its side instead would leave the spine as an island.
#
#  THINGS THIS SCRIPT DELIBERATELY LEAVES TO YOU
#    Fillets and chamfers. Edge selection by index breaks the moment a
#    dimension changes, so it is safer to add them by hand: R0.4 at the lever
#    arm's thickness step, 0.3 around the nub's bottom face, 1 mm on the
#    frame's outer edges, and a 0.4 mm relief groove around the bottom of each
#    wall pocket so the nozzle's inside-corner fillet cannot hold the lever's
#    foot proud. That last one directly sets the 0.15 mm rest gap.
#
#    Pi mounting. The cavity behind the PCB is only 14.90 mm deep, which fits
#    a Zero on the GPIO header and nothing larger. Standoffs are not modelled
#    because their positions depend on how you stack it.
#
#  PCB POSTS - the one number you will probably have to tune
#    The posts bottom out on the board's rear face at Z = 3.10. That is a hard
#    stop built from a stack of printed tolerances, so on the first assembly
#    one of three things happens:
#      cover will not seat        -> raise PCB_POST_CLR to 0.10 and reprint
#      board rattles              -> lower PCB_POST_CLR to -0.10
#      it just works              -> leave it
#    The cheap fix for either direction is a 0.5 mm adhesive foam pad on each
#    post tip and PCB_POST_CLR = 0.40. Foam takes up the whole stack-up, holds
#    the board without a preload spike, and costs nothing.
#
#    Check the four positions against your Pi Zero before you print. They sit
#    8 mm inside the board's edge and run the full 14.9 mm depth of the cavity,
#    so anything overhanging the board's perimeter will foul them.
#
#  CHECK BEFORE PRINTING 10 HOURS OF FRAME
#    Print one lever plus a 40 mm section of the button wall first. Verify the
#    click, then tune REST_GAP and STOP_GAP. Everything else in this case is
#    forgiving; the button is not.
# ============================================================================
