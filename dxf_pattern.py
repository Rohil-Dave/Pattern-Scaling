import ezdxf

# Input variables key:
# pw: pattern width
# ph: pattern height
# cw: collar width
# cl: collar length


def draw_tee_pattern_dxf(pw, ph, cw, cl):
    # Create a new DXF document.
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

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

    

    # # Save the drawing as 'test.dxf' in the current directory
    doc.saveas("test.dxf")

# Execute the function
draw_tee_pattern_dxf(pw=140, ph=100, cw=9.5, cl=25)
