import ezdxf

# # Input variables key:
# # pw: pattern width
# # ph: pattern height
# cw: collar width
# cl: collar length


import ezdxf

def draw_tee_pattern_dxf(pw, ph, cw, cl):
    # Create a new DXF document.
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    # Draw the main rectangle body of the pattern
    msp.add_lwpolyline([(0, 0), (pw, 0), (pw, ph), (0, ph), (0, 0)], close=True)

    # Draw the collar pieces
    collar_positions = [
        (0, ph - cl), 
        (0.5 * pw - cw, ph - cl),
        (0.5 * pw, ph - cl),
        (pw - cw, ph - cl)
    ]
    for x, y in collar_positions:
        msp.add_lwpolyline([(x, y), (x + cw, y), (x + cw, y + cl), (x, y + cl), (x, y)], close=True)

    

    # # Save the drawing as 'test.dxf' in the current directory
    doc.saveas("test.dxf")

# Test the function with the same parameters as before
draw_tee_pattern_dxf(pw=140, ph=100, cw=9.5, cl=25)
