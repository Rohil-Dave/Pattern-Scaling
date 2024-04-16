import ezdxf

# Create a new DXF document
doc = ezdxf.new('R2010')

# Add new layers for different pattern pieces, you can define as many as you need
doc.layers.new(name='MainBody', dxfattribs={'color': 2})  # color 2 is yellow
doc.layers.new(name='Collar', dxfattribs={'color': 3})  # color 3 is green
doc.layers.new(name='Sleeve', dxfattribs={'color': 4})  # color 4 is cyan

msp = doc.modelspace()

# Example to add entities to the 'MainBody' layer
msp.add_lwpolyline([(0, 0), (100, 0), (100, 100), (0, 100)], close=True, dxfattribs={'layer': 'MainBody'})
msp.add_arc((50, 50), radius=25, start_angle=0, end_angle=180, dxfattribs={'layer': 'MainBody'})

# Example to add entities to the 'Collar' layer
msp.add_line((10, 100), (90, 100), dxfattribs={'layer': 'Collar'})
msp.add_lwpolyline([(0, 0), (100, 0), (100, 100), (0, 100)], close=True, dxfattribs={'layer': 'Sleeve'})

# Example to add entities to the 'Sleeve' layer
msp.add_lwpolyline([(0, 0), (100, 0), (100, 100), (0, 100)], close=True, dxfattribs={'layer': 'Sleeve'})

# Save the DXF file
doc.saveas("pattern_with_layers.dxf")