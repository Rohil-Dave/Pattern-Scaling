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


def draw_layered_pattern_dxf(pw, ph, cw, cl):

    # Create a new DXF document
    doc = ezdxf.new('R2010')

    # Add new layers for different pattern pieces, you can define as many as you need
    doc.layers.new(name='B5', dxfattribs={'color': 2})  # color 2 is yellow
    doc.layers.new(name='Collar', dxfattribs={'color': 3})  # color 3 is green
    doc.layers.new(name='Sleeve', dxfattribs={'color': 4})  # color 4 is cyan

    msp = doc.modelspace()

    # Draw the collar pieces
    collar_positions = [
        (0, ph - cl), # left-most collar piece
        (0.5 * pw - cw, ph - cl), # left middle collar piece
        (0.5 * pw, ph - cl), # right middle collar piece
        (pw - cw, ph - cl) # right-most collar piece
    ]
    for x, y in collar_positions:
        msp.add_lwpolyline([(x, y), (x + cw, y), (x + cw, y + cl), (x, y + cl), (x, y)], close=True, dxfattribs={'layer': 'Collar'})

    

    # Save the DXF file
    doc.saveas("pattern_with_layers.dxf")

# Execute the function
draw_layered_pattern_dxf(pw=140, ph=100, cw=9.5, cl=25)

# bh=14, bw=14, sd=3, sh=15, bx=7, by=7