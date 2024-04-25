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
# eh: encapulation rectangle height
# al: armhole length (calculated from pattern width and collar width)



def draw_layered_pattern_dxf(pw, ph, cw, cl, bw, bh, bx, by, sd, sh, eh):

    # Create a new DXF document
    doc = ezdxf.new('R2010')

    # Add new layers for different pattern pieces, you can define as many as you need
    doc.layers.new(name='B5', dxfattribs={'color': 2})  # color 2 is yellow
    doc.layers.new(name='Collar', dxfattribs={'color': 3})  # color 3 is green
    doc.layers.new(name='Sleeve', dxfattribs={'color': 4})  # color 4 is cyan
    #doc.layers.new(name='Test', dxfattribs={'color': 5})  # color 5 is indigo
    doc.layers.new(name='Bodice', dxfattribs={'color': 6})  # color 6 is magenta
    doc.layers.new(name='Encap', dxfattribs={'color': 1})  # color 1 is red

    msp = doc.modelspace()

    # COLLAR LAYER----------------------------------------------------------------
    collar_positions = [
        (0, ph - cl), # left-most collar piece
        (0.5 * pw - cw, ph - cl), # left middle collar piece
        (0.5 * pw, ph - cl), # right middle collar piece
        (pw - cw, ph - cl) # right-most collar piece
    ]
    for x, y in collar_positions:
        msp.add_lwpolyline([(x, y), (x + cw, y), (x + cw, y + cl), (x, y + cl), (x, y)], close=True, dxfattribs={'layer': 'Collar'})

    # B5 LAYER--------------------------------------------------------------------
    # Draw B5 shapes, refered to as left and right respectively, adds straight lines and arcs
    # ONLY WORKS WHEN bx and by ARE EQUAL!! AND ARE HALF OF bw and bh
    # Calculate common points
    left_horizontal_end = (bx, ph - cl - bh)
    left_vertical_end = (bw, ph - cl - by)
    right_horizontal_end = (pw - bx, ph - cl - bh)
    right_vertical_end = (pw - bw, ph - cl - by)
    
    # Draw straight lines
    msp.add_line((0, ph - cl - bh), left_horizontal_end, dxfattribs={'layer': 'B5'})  # Left horizontal line
    msp.add_line(left_vertical_end, (bw, ph - cl), dxfattribs={'layer': 'B5'})  # Left vertical line
    msp.add_line(right_horizontal_end, (pw, ph - cl - bh), dxfattribs={'layer': 'B5'})  # Right horizontal line
    msp.add_line((pw - bw, ph - cl), right_vertical_end, dxfattribs={'layer': 'B5'})  # Right vertical line

    msp.add_lwpolyline([(0, ph - cl - bh), (0, ph - cl), (bw, ph - cl)], dxfattribs={'layer': 'B5'})
    msp.add_lwpolyline([(pw, ph - cl - bh), (pw, ph - cl), (pw - bw, ph - cl)], dxfattribs={'layer': 'B5'})

    # Calculate the radius, which is the distance from the corner to the curve start
    radius = bx  # or by, assuming they are the same
    left_arc_center = (bx, ph - cl - by)
    right_arc_center = (pw - bx, ph - cl - by)
    # The start and end angles depend on the orientation of the lines
    # For the left side:
    left_start_angle = 270  # Starting from the bottom, going counter-clockwise
    left_end_angle = 360  # Ending to the right
    # For the right side, it would be mirrored
    right_start_angle = 180  # Starting from the left, going counter-clockwise
    right_end_angle = 270  # Ending to the bottom

    # Draw arcs for the rounded corners
    msp.add_arc(left_arc_center, radius, left_start_angle, left_end_angle, dxfattribs={'layer': 'B5'})
    msp.add_arc(right_arc_center, radius, right_start_angle, right_end_angle, dxfattribs={'layer': 'B5'})

    # SLEEVE LAYER-----------------------------------------------------------------
    # Draw sleevehead curves
    sleeve_data = [
        ((cw + sh, ph - cl), (0.25 * pw, ph - cl - sd), (0.5 * pw - cw - sh, ph - cl)),
        ((0.5 * pw + cw + sh, ph - cl), (0.75 * pw, ph - cl - sd), (pw - cw - sh, ph - cl))
    ]
    for start, control, end in sleeve_data:
        msp.add_spline([start, control, end], dxfattribs={'layer': 'Sleeve'})

    # Draw lines connecting sleevehead lines to collar pieces
    msp.add_line((cw, ph - cl), (cw + sh, ph - cl), dxfattribs={'layer': 'Sleeve'})  # from leftmost collar to the right
    msp.add_line((0.5 * pw - cw - sh, ph - cl), (0.5 * pw - cw, ph - cl), dxfattribs={'layer': 'Sleeve'})  # between left middle and center collar
    msp.add_line((0.5 * pw + cw, ph - cl), (0.5 * pw + cw + sh, ph - cl), dxfattribs={'layer': 'Sleeve'})  # between center and right middle collar
    msp.add_line((pw - cw, ph - cl), (pw - cw - sh, ph - cl), dxfattribs={'layer': 'Sleeve'})  # from rightmost collar to the left

    # Draw vertical lines(edges) of sleeve pieces
    msp.add_line((cw, ph), (cw, ph - cl), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((0.5 * pw - cw, ph), (0.5 * pw - cw, ph - cl), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((0.5 * pw + cw, ph), (0.5 * pw + cw, ph - cl), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((pw - cw, ph), (pw - cw, ph - cl), dxfattribs={'layer': 'Sleeve'})

    # Draw top hortizontal lines(edges) of sleeve pieces
    msp.add_line((cw, ph), (0.5 * pw - cw, ph), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((0.5 * pw + cw, ph), (pw - cw, ph), dxfattribs={'layer': 'Sleeve'})

    # BODICE LAYER----------------------------------------------------------------
    # B5 border elements
    msp.add_line((0, ph - cl - bh), left_horizontal_end, dxfattribs={'layer': 'Bodice'})  # Left horizontal line
    msp.add_line(left_vertical_end, (bw, ph - cl), dxfattribs={'layer': 'Bodice'})  # Left vertical line
    msp.add_line(right_horizontal_end, (pw, ph - cl - bh), dxfattribs={'layer': 'Bodice'})  # Right horizontal line
    msp.add_line((pw - bw, ph - cl), right_vertical_end, dxfattribs={'layer': 'Bodice'})  # Right vertical line
    msp.add_arc(left_arc_center, radius, left_start_angle, left_end_angle, dxfattribs={'layer': 'Bodice'})
    msp.add_arc(right_arc_center, radius, right_start_angle, right_end_angle, dxfattribs={'layer': 'Bodice'})

    # Sleeve border elements
    for start, control, end in sleeve_data:
        msp.add_spline([start, control, end], dxfattribs={'layer': 'Bodice'})
    msp.add_line((0.5 * pw - cw - sh, ph - cl), (0.5 * pw + cw + sh, ph - cl), dxfattribs={'layer': 'Bodice'})  # middle connecting line thru center back
    msp.add_line((bw, ph - cl), (cw + sh, ph - cl), dxfattribs={'layer': 'Bodice'})  # left connecting line thru center front
    msp.add_line((pw - bw, ph - cl), (pw - cw - sh, ph - cl), dxfattribs={'layer': 'Bodice'})  # right connecting line thru center front

    # Side and bottom border
    msp.add_lwpolyline([(0, ph - cl - bh), (0, 0), (pw, 0), (pw, ph - cl - bh)], dxfattribs={'layer': 'Bodice'})

    # Draw armhole lines
    al = 0.5 * (0.5 * pw - (2 * cw))  # Calculate armhole length
    msp.add_line((0.25 * pw, ph - cl - sd), (0.25 * pw, ph - cl - sd - al), dxfattribs={'layer': 'Bodice'})
    msp.add_line((0.75 * pw, ph - cl - sd), (0.75 * pw, ph - cl - sd - al), dxfattribs={'layer': 'Bodice'})


    # ENCAPSULATION LAYER----------------------------------------------------------
    # Bottom rectangle for sensor and circuit encapsulation
    msp.add_lwpolyline([(0, 0), (0, -eh), (pw, -eh), (pw, 0), (0, 0)], close=True, dxfattribs={'layer': 'Encap'})

    # # TEST LAYER------------------------------------------------------------------
    # fit_points = [
    #     (0, 0),  # Starting point
    #     (50, 0),  # Mid-point on a straight line
    #     (100, 50),  # Arc peak or control point for a curve
    #     (150, 0),  # End of arc or curve
    #     (200, 0),  # Another straight segment
    #     (0, 0)   # Closing back to the start
    # ]
    # # Create a spline that fits all these points
    # spline = msp.add_spline(dxfattribs={'layer': 'Test'})
    # spline.fit_points = fit_points

    # SAVE DXF FILE---------------------------------------------------------------
    # Save the DXF file
    doc.saveas("main_func_test.dxf")

'''Assigns fabric width based on bust/chest and hip measurements'''
def get_fabric_width(bust, hip):
    # Fabric width ranges mapped to max chest/bust and hip measurements
    fabric_width_mapping = [
        (135, 96, 104),  # (Fabric width, max bust, max hip)
        (140, 101, 109),
        (145, 106, 114),
        (150, 111, 119),
        (155, 116, 124),
    ]
    
    # Determine the larger of the chest or hip measurements
    largest_measurement = max(bust, hip)
    
    # Find the smallest fabric width that fits the largest measurement
    for fabric_width, max_chest, max_hip in fabric_width_mapping:
        if largest_measurement <= max(max_chest, max_hip):
            return fabric_width  # Return the matching fabric width
    
    # If the measurement is larger than all available sizes, return the largest fabric width
    return fabric_width_mapping[-1][0]



def calculate_and_draw(user_measurments):
    # Extract user measurements
    shirt_length = user_measurments['shirt_length']
    bust_circ = user_measurments['bust_circ']
    hip_circ = user_measurments['hip_circ']
    arm_circ = user_measurments['arm_circ']

    # Calculate pattern dimensions
    ease = 5 # Fixed ease

    # Also kept fixed for all by BH of ZWP book
    cw = 9.5 # Fixed for now
    sd = 3 # Fixed for now
    sh = 15 # Fixed for now
    bw = bh = 14 # Fixed for now
    bx = by = 0.5 * bw

    cl = arm_circ + ease
    ph = shirt_length + cl + ease
    #pw = bust_circ + 35 + ease  # pw based on constant and ease from bust only

    pw = get_fabric_width(bust_circ, hip_circ)  # pw based on ranges for bust and hip

    eh = 2.5 # Encapsulation depth
    
    # Draw the pattern
    draw_layered_pattern_dxf(pw, ph, cw, cl, bw, bh, bx, by, sd, sh, eh)
    return pw, ph, cw, cl, bw, bh, bx, by, sd, sh, eh


def main():
    user_measurements = {}
    user_measurements['shirt_length'] = float(input("Enter your shirt length (cm): "))
    user_measurements['bust_circ'] = float(input("Enter your chest/bust circumference (cm): "))
    user_measurements['hip_circ'] = float(input("Enter your hip circumference (cm): "))
    user_measurements['arm_circ'] = float(input("Enter your arm circumference (cm): "))

    calculate_and_draw(user_measurements)

# Execute main function
if __name__ == "__main__":
    main()

# Execute the function
# draw_layered_pattern_dxf(pw=140, ph=100, cw=9.5, cl=25, bh=14, bw=14, bx=7, by=7, sd=3, sh=15)



# Rules and relationships:
# - Smaller collar width means a thinner collar and longer sleeves
# - Larger collar length means wider sleeve holes
# - Larger B5 width and height means a larger B5 piece, which takes away from the center front of bodice
# - 
 