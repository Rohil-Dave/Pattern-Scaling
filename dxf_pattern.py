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


def draw_tee_pattern_dxf(pw, ph, cw, cl, bw, bh, sd, sh):
    
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

    # Draw B5 boxes
    b5_positions = [
        (0, ph - cl - bh),  # position for the left B5 piece
        (pw - bw, ph - cl - bh)  # position for the right B5 piece
    ]
    for x, y in b5_positions:
        msp.add_lwpolyline([(x, y), (x + bw, y), (x + bw, y + bh), (x, y + bh), (x, y)], close=True)

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
draw_tee_pattern_dxf(pw=140, ph=100, cw=9.5, cl=25, bh=14, bw=14, sd=3, sh=15)
