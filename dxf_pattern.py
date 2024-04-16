import ezdxf

# Input variables key:
# pw: pattern width
# ph: pattern height
# cw: collar width
# cl: collar length
# bw: B5 width
# bh: B5 height
# sd: sleevehead depth
# sh: sleevehead indent
# bx: B5 straight line extent x-coordinate
# by: B5 straight line extent y-coordinate
# al: armhole length (calculated from pattern width and collar width)


def draw_tee_pattern_dxf(pw, ph, cw, cl, bw, bh, sd, sh, bx, by):
    
    doc = ezdxf.new(dxfversion='R2010') # Create a new DXF document
    msp = doc.modelspace() # Create a new modelspace in the DXF document

    # Draw the main rectangle body of the pattern
    msp.add_lwpolyline([(0, 0), (pw, 0), (pw, ph), (0, ph), (0, 0)], close=True)

    # Draw the collar pieces
    collar_positions = [
        (0, ph - cl), # left-most collar piece
        (0.5 * pw - cw, ph - cl), # left middle collar piece
        (0.5 * pw, ph - cl), # right middle collar piece
        (pw - cw, ph - cl) # right-most collar piece
    ]
    for x, y in collar_positions:
        msp.add_lwpolyline([(x, y), (x + cw, y), (x + cw, y + cl), (x, y + cl), (x, y)], close=True)

    # Draw B5 shapes, refered to as left and right respectively, adds straight lines and arcs
    # ONLY WORKS WHEN bx and by ARE EQUAL!!
    # Calculate common points
    left_horizontal_end = (bx, ph - cl - bh)
    left_vertical_end = (bw, ph - cl - by)
    right_horizontal_end = (pw - bx, ph - cl - bh)
    right_vertical_end = (pw - bw, ph - cl - by)
    # Calculate the radius, which is the distance from the corner to the curve start
    radius = bx  # or by, assuming they are the same
    # Assuming that bx and by are the same and the radius for the curve,
    # the center of the arc would be offset from the ends of the lines by the radius
    left_arc_center = (bx, ph - cl - by)
    right_arc_center = (pw - bx, ph - cl - by)
    # The start and end angles depend on the orientation of the lines
    # For the left side:
    left_start_angle = 270  # Starting from the bottom, going counter-clockwise
    left_end_angle = 360  # Ending to the right
    # For the right side, it would be mirrored
    right_start_angle = 180  # Starting from the left, going counter-clockwise
    right_end_angle = 270  # Ending to the bottom
    # Draw straight lines
    msp.add_line((0, ph - cl - bh), left_horizontal_end)  # Left horizontal line
    msp.add_line(left_vertical_end, (bw, ph - cl))  # Left vertical line
    msp.add_line(right_horizontal_end, (pw, ph - cl - bh))  # Right horizontal line
    msp.add_line((pw - bw, ph - cl), right_vertical_end)  # Right vertical line
    # Draw arcs for the rounded corners
    msp.add_arc(left_arc_center, radius, left_start_angle, left_end_angle)
    msp.add_arc(right_arc_center, radius, right_start_angle, right_end_angle)

    # Draw sleevehead curves
    sleeve_data = [
        ((cw + sh, ph - cl), (0.25 * pw, ph - cl - sd), (0.5 * pw - cw - sh, ph - cl)),
        ((0.5 * pw + cw + sh, ph - cl), (0.75 * pw, ph - cl - sd), (pw - cw - sh, ph - cl))
    ]
    for start, control, end in sleeve_data:
        msp.add_spline([start, control, end])

    # Draw lines connecting sleevehead lines to collar pieces
    msp.add_line((cw, ph - cl), (cw + sh, ph - cl))  # from leftmost collar to the right
    msp.add_line((0.5 * pw - cw - sh, ph - cl), (0.5 * pw - cw, ph - cl))  # between left middle and center collar
    msp.add_line((0.5 * pw + cw, ph - cl), (0.5 * pw + cw + sh, ph - cl))  # between center and right middle collar
    msp.add_line((pw - cw, ph - cl), (pw - cw - sh, ph - cl))  # from rightmost collar to the left
    
    # Draw armhole lines
    al = 0.5 * (0.5 * pw - 2 * cw)  # Calculate armhole length
    msp.add_line((0.25 * pw, ph - cl - sd), (0.25 * pw, ph - cl - sd - al))
    msp.add_line((0.75 * pw, ph - cl - sd), (0.75 * pw, ph - cl - sd - al))

    # Save the drawing as 'test.dxf' in the current directory
    doc.saveas("test.dxf")

# Execute the function
draw_tee_pattern_dxf(pw=140, ph=100, cw=9.5, cl=25, bh=14, bw=14, sd=3, sh=15, bx=7, by=7)
