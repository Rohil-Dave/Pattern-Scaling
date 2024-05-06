#!/usr/bin/env python3
'''
This module is used for creating layered tailoring patterns in the dxf format
These are zero / low waste patterns based on a few body measurements. Tolerances 
are built in for hemming, sewing, etc. 
The output is suitable for being uploaded to Clo 3D

These are some rules and relationships:
- Smaller collar width means a thinner collar and wider sleeve holes
- cl (collar length) corresponds to the sleeve length
- Larger B5 width and height means a larger B5 piece, which takes away from the center front of bodice
- all measurements are in cms

Input variables key:
pattern width, pw
pattern height, ph
collar width, cw
collar length, cl
B5 width - neck hole cut width, bw
B5 height - neck hole cut height, bh
sleevehead depth, sd
sleevehead indent, sh
B5 straight line extent x-coordinate, bx
B5 straight line extent y-coordinate, by
armhole length (calculated from pattern width and collar width), al
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import ezdxf

# Fabric comes in industry defined widths (135, 140, 145, 150, 155 cms).
# Fabric width ranges mapped to max chest/bust and hip measurements
fabric_width_mapping = [
    (135, 96, 104),  # (Fabric width, max bust, max hip)
    (140, 101, 109),
    (145, 106, 114),
    (150, 111, 119),
    (155, 116, 124)
]

def draw_layered_pattern_dxf(p_measurements):
    '''
    Draw a layered pattern in the dxf format and save it in a file
    '''
    # Create a new DXF document
    doc = ezdxf.new('R2010')

    # Add new layers for different pattern pieces, you can define as many as you need
    doc.layers.new(name='B5', dxfattribs={'color': 2})  # color 2 is yellow
    doc.layers.new(name='Collar', dxfattribs={'color': 3})  # color 3 is green
    doc.layers.new(name='Sleeve', dxfattribs={'color': 4})  # color 4 is cyan
    doc.layers.new(name='Bodice', dxfattribs={'color': 6})  # color 6 is magenta
    doc.layers.new(name='Sew', dxfattribs={'color': 7})  # color 7 is white

    msp = doc.modelspace()

    pattern_width = p_measurements['pattern_width']
    pattern_height = p_measurements['pattern_height']
    collar_width = p_measurements['collar_width']
    collar_length = p_measurements['collar_length']
    b5_width = p_measurements['b5_width']
    b5_height = b5_width # this might be different later, in which case it will be in the p_measurements  dict
    b5_x = b5_y = b5_width * 0.5 # these might also be different
    sleeve_depth = p_measurements['sleeve_depth']
    sleeve_radius = p_measurements['sleeve_radius']
    #sleeve_indent = p_measurements['sleeve_indent'] # Dont need this anymore

    # COLLAR LAYER----------------------------------------------------------------
    collar_positions = [
        (0, pattern_height - collar_length), # left-most collar piece
        (0.5 * pattern_width - collar_width, pattern_height - collar_length), # left middle collar piece
        (0.5 * pattern_width, pattern_height - collar_length), # right middle collar piece
        (pattern_width - collar_width, pattern_height - collar_length) # right-most collar piece
    ]
    for x, y in collar_positions:
        msp.add_lwpolyline([(x, y), (x + collar_width, y), (x + collar_width, y + collar_length), (x, y + collar_length), (x, y)], close=True, dxfattribs={'layer': 'Collar'})

    # B5 LAYER--------------------------------------------------------------------
    # Draw B5 shapes, refered to as left and right respectively, adds straight lines and arcs
    # ONLY WORKS WHEN b5_x and b5_y ARE EQUAL!! AND ARE HALF OF b5_width and b5_height
    # Calculate common points
    left_horizontal_end = (b5_x, pattern_height - collar_length - b5_height)
    left_vertical_end = (b5_width, pattern_height - collar_length - b5_y)
    right_horizontal_end = (pattern_width - b5_x, pattern_height - collar_length - b5_height)
    right_vertical_end = (pattern_width - b5_width, pattern_height - collar_length - b5_y)

    # Draw straight lines
    msp.add_line((0, pattern_height - collar_length - b5_height), left_horizontal_end, dxfattribs={'layer': 'B5'})  # Left horizontal line
    msp.add_line(left_vertical_end, (b5_width, pattern_height - collar_length), dxfattribs={'layer': 'B5'})  # Left vertical line
    msp.add_line(right_horizontal_end, (pattern_width, pattern_height - collar_length - b5_height), dxfattribs={'layer': 'B5'})  # Right horizontal line
    msp.add_line((pattern_width - b5_width, pattern_height - collar_length), right_vertical_end, dxfattribs={'layer': 'B5'})  # Right vertical line

    msp.add_lwpolyline([(0, pattern_height - collar_length - b5_height), (0, pattern_height - collar_length), (b5_width, pattern_height - collar_length)], dxfattribs={'layer': 'B5'})
    msp.add_lwpolyline([(pattern_width, pattern_height - collar_length - b5_height), (pattern_width, pattern_height - collar_length), (pattern_width - b5_width, pattern_height - collar_length)], dxfattribs={'layer': 'B5'})

    # Calculate the radius, which is the distance from the corner to the curve start
    radius = b5_x  # or b5_y, assuming they are the same
    left_arc_center = (b5_x, pattern_height - collar_length - b5_y)
    right_arc_center = (pattern_width - b5_x, pattern_height - collar_length - b5_y)
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
        ((0.25 * pattern_width - sleeve_radius, pattern_height - collar_length), (0.25 * pattern_width, pattern_height - collar_length - sleeve_depth), (0.25 * pattern_width + sleeve_radius, pattern_height - collar_length)),
        ((0.75 * pattern_width - sleeve_radius, pattern_height - collar_length), (0.75 * pattern_width, pattern_height - collar_length - sleeve_depth), (0.75 * pattern_width + sleeve_radius, pattern_height - collar_length))
    ]
    for start, control, end in sleeve_data:
        msp.add_spline([start, control, end], dxfattribs={'layer': 'Sleeve'})

    # Draw lines connecting sleevehead lines to collar pieces
    msp.add_line((collar_width, pattern_height - collar_length), (0.25 * pattern_width - sleeve_radius, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # from leftmost collar to the right
    msp.add_line((0.25 * pattern_width + sleeve_radius, pattern_height - collar_length), (0.5 * pattern_width - collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # between left middle and center collar
    msp.add_line((0.5 * pattern_width + collar_width, pattern_height - collar_length), (0.75 * pattern_width - sleeve_radius, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # between center and right middle collar
    msp.add_line((0.75 * pattern_width + sleeve_radius, pattern_height - collar_length), (pattern_width - collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # from rightmost collar to the left

    # Draw vertical lines(edges) of sleeve pieces
    msp.add_line((collar_width, pattern_height), (collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((0.5 * pattern_width - collar_width, pattern_height), (0.5 * pattern_width - collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((0.5 * pattern_width + collar_width, pattern_height), (0.5 * pattern_width + collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((pattern_width - collar_width, pattern_height), (pattern_width - collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})

    # Draw top hortizontal lines(edges) of sleeve pieces
    msp.add_line((collar_width, pattern_height), (0.5 * pattern_width - collar_width, pattern_height), dxfattribs={'layer': 'Sleeve'})
    msp.add_line((0.5 * pattern_width + collar_width, pattern_height), (pattern_width - collar_width, pattern_height), dxfattribs={'layer': 'Sleeve'})

    # BODICE LAYER----------------------------------------------------------------
    # B5 border elements
    msp.add_line((0, pattern_height - collar_length - b5_height), left_horizontal_end, dxfattribs={'layer': 'Bodice'})  # Left horizontal line
    msp.add_line(left_vertical_end, (b5_width, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # Left vertical line
    msp.add_line(right_horizontal_end, (pattern_width, pattern_height - collar_length - b5_height), dxfattribs={'layer': 'Bodice'})  # Right horizontal line
    msp.add_line((pattern_width - b5_width, pattern_height - collar_length), right_vertical_end, dxfattribs={'layer': 'Bodice'})  # Right vertical line
    msp.add_arc(left_arc_center, radius, left_start_angle, left_end_angle, dxfattribs={'layer': 'Bodice'})
    msp.add_arc(right_arc_center, radius, right_start_angle, right_end_angle, dxfattribs={'layer': 'Bodice'})

    # Sleeve border elements
    for start, control, end in sleeve_data:
        msp.add_spline([start, control, end], dxfattribs={'layer': 'Bodice'})
    msp.add_line((b5_width, pattern_height - collar_length), (0.25 * pattern_width - sleeve_radius, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # middle connecting line thru center back
    msp.add_line((0.25 * pattern_width + sleeve_radius, pattern_height - collar_length), (0.75 * pattern_width - sleeve_radius, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # left connecting line thru center front
    msp.add_line((0.75 * pattern_width + sleeve_radius, pattern_height - collar_length), (pattern_width - b5_width, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # right connecting line thru center front

    # Side and bottom border
    msp.add_lwpolyline([(0, pattern_height - collar_length - b5_height), (0, 0), (pattern_width, 0), (pattern_width, pattern_height - collar_length - b5_height)], dxfattribs={'layer': 'Bodice'})

    # Draw armhole lines
    armhole_length = 0.5 * (0.5 * pattern_width - (2 * collar_width))  # Calculate armhole length
    msp.add_line((0.25 * pattern_width, pattern_height - collar_length - sleeve_depth), (0.25 * pattern_width, pattern_height - collar_length - sleeve_depth - armhole_length), dxfattribs={'layer': 'Bodice'})
    msp.add_line((0.75 * pattern_width, pattern_height - collar_length - sleeve_depth), (0.75 * pattern_width, pattern_height - collar_length - sleeve_depth - armhole_length), dxfattribs={'layer': 'Bodice'})

    # SEW AND HEM LINES, NOTCHES LAYER--------------------------------------------
    # CENTER FRONT-------
    # first notches 2.5cm from CF, second notches 3cm from first notches, third notches 3cm from second notches
    msp.add_line((2.5, pattern_height - collar_length - b5_height), (2.5, 0), dxfattribs={'layer': 'Sew'})
    msp.add_line((pattern_width - 2.5, pattern_height - collar_length - b5_height), (pattern_width - 2.5, 0), dxfattribs={'layer': 'Sew'})
    msp.add_line((2.5 + 3, pattern_height - collar_length - b5_height), (2.5 + 3, 0), dxfattribs={'layer': 'Sew'})
    msp.add_line((pattern_width - 2.5 - 3, pattern_height - collar_length - b5_height), (pattern_width - 2.5 - 3, 0), dxfattribs={'layer': 'Sew'})
    
    # CENTER BACK--------
    # notch at CB, first notches 9.5cm from CB, second notches 4.5cm from first notches
    msp.add_line((0.5 * pattern_width, pattern_height - collar_length), (0.5 * pattern_width, pattern_height - collar_length - 1), dxfattribs={'layer': 'Sew'})
    msp.add_line((0.5 * pattern_width - 9.5, pattern_height - collar_length), (0.5 * pattern_width - 9.5, pattern_height - collar_length - 14), dxfattribs={'layer': 'Sew'})
    msp.add_line((0.5 * pattern_width + 9.5, pattern_height - collar_length), (0.5 * pattern_width + 9.5, pattern_height - collar_length - 14), dxfattribs={'layer': 'Sew'})
    msp.add_line((0.5 * pattern_width - 9.5 - 4.5, pattern_height - collar_length), (0.5 * pattern_width - 9.5 - 4.5, pattern_height - collar_length - 1), dxfattribs={'layer': 'Sew'})
    msp.add_line((0.5 * pattern_width + 9.5 + 4.5, pattern_height - collar_length), (0.5 * pattern_width + 9.5 + 4.5, pattern_height - collar_length - 1), dxfattribs={'layer': 'Sew'})

    # SAVE DXF FILE---------------------------------------------------------------
    # Save the DXF file with the person id in the file name
    file_name = p_measurements['person_id'] + '_pattern.dxf'
    doc.saveas(file_name)

def get_fabric_width(user_measurements, p_measurements):
    '''
    Assigns fabric width based on bust/chest and hip measurements

    We need to choose the appropriate width based on body measurements, ease 
    and sewing tolerances
    The formula is the sum of larger body circumference + ease + tolerance
    If we are not choosing actual measure, then we need to closest bolt width
    size which is a ceiling on 5 cm boundaries, e.g 130cm, 135cm, 140cm, etc
    '''

    # Determine the larger of the chest or hip measurements
    largest_measurement = max(user_measurements['bust_circ'], user_measurements['hip_circ']) # should add waist_circ here?

    width = largest_measurement + p_measurements['ease'] + p_measurements['sew_tolerance']

    if user_measurements['actual_measure'] == '1':
        # return actual computed width
        return width

    # return the width of the closest bolt (we assume bolt widths are multiples of 5)
    return width if width % 5 == 0 else width + 5 - width % 5

def calculate_and_draw(user_measurments):
    '''
    calculate the dimensions and draw the pattern
    '''
    # Extract user measurements
    shirt_length = user_measurments['shirt_length']
    bust_circ = user_measurments['bust_circ']
    hip_circ = user_measurments['hip_circ']
    # arm_circ = user_measurments['arm_circ']
    actual_measure = user_measurments['actual_measure']

    # pattern measurements
    p_measurements = {}

    p_measurements['ease'] = 25 # currently fixed
    p_measurements['sew_tolerance'] = 6 # FIXED FOR ALL BODIES

    p_measurements['collar_width'] = 9.5 # FIXED FOR ALL BODIES
    p_measurements['collar_length'] = 25 # FIXED FOR ALL BODIES
    p_measurements['sleeve_depth'] = 3.5 # FIXED FOR ALL BODIES
    p_measurements['sleeve_radius'] = 14 # FIXED FOR ALL BODIES, should not be more than 16/17 ?
    p_measurements['b5_width'] = 14 # FIXED FOR ALL BODIES

    p_measurements['pattern_height'] = shirt_length + p_measurements['collar_length'] # do not add ease here, must account for hem
    p_measurements['pattern_width'] = get_fabric_width(user_measurments, p_measurements) # pattern_width based on bust, hip ranges
    #p_measurements['sleeve_indent'] = ((p_measurements['pattern_width'] - (4 * p_measurements['collar_length']) - (4 * p_measurements['sleeve_radius'])) / 4) # Dont need this anymore

    p_measurements['person_id'] = user_measurments['person_id']

    # Draw the pattern
    draw_layered_pattern_dxf(p_measurements)

def main():
    '''
    The main function. We get the user measurements and figure out the pattern
    During the measurement pattern_heightase we take a few readings (shirt length, bust, hip, 
    arm, neck, waist, shoulder width, and sleeve length). We may not use them all 
    for this particular pattern

    Shirt length and sleeve length are 'desired' quantities, the others are based on body size
    '''
    user_measurements = {}
    user_measurements['shirt_length'] = float(input("Enter your desired shirt length (cm): "))
    user_measurements['bust_circ'] = float(input("Enter your chest/bust circumference (cm): "))
    user_measurements['hip_circ'] = float(input("Enter your hip circumference (cm): "))
    user_measurements['waist_circ'] = float(input("Enter your waist circumference (cm): "))
    user_measurements['arm_circ'] = float(input("Enter your arm circumference (cm): "))
    user_measurements['neck_circ'] = float(input("Enter your neck circumference (cm): "))
    user_measurements['shoulder_width'] = float(input("Enter your shoulder width (cm): "))
    user_measurements['sleeve_length'] = float(input("Enter your desired sleeve length (cm): "))
    user_measurements['person_id'] = input('Enter the id of the person (str): ')
    user_measurements['actual_measure'] = int(input('Enter 1 for actual width fit   OR   0 for best bolt width fit: '))

    calculate_and_draw(user_measurements)

# Execute main function
if __name__ == "__main__":
    main()
