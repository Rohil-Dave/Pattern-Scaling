import ezdxf


# # Define pattern in DXF format
doc = ezdxf.new('R2010')  # 'R2010' is compatible with most CAD software
msp = doc.modelspace()  # Get the modelspace where all elements (entries) are placed

# Main body rectangle
msp.add_lwpolyline([
    (0, 0),
    (pw, 0),
    (pw, ph),
    (0, ph),
    (0, 0)
], close=True)