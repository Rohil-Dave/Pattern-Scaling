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
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.path import Path
from matplotlib.patches import PathPatch

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

def draw_pdf_with_dimensions(p_measurements):
    '''
    Creates the pattern in pdf format using matplotlib and adds dimensions
    needed for user to draw the pattern onto their fabric
    '''
    # Create a figure and an axis
    fig, ax = plt.subplots(figsize=(20, 10))

    pattern_width = p_measurements['pattern_width']
    pattern_height = p_measurements['pattern_height']
    collar_width = p_measurements['collar_width']
    collar_length = p_measurements['collar_length']
    b5_width = p_measurements['b5_width']
    b5_height = b5_width 
    b5_x = b5_y = b5_width * 0.5
    sleeve_depth = p_measurements['sleeve_depth']
    sleeve_radius = p_measurements['sleeve_radius']
    armhole_length = 0.5 * (0.5 * pattern_width - (2 * collar_width))  # Calculated armhole length

    # Draw total area of pattern
    main_body = Rectangle((0, 0), width=pattern_width, height=pattern_height, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(main_body)

    # Draw collar areas; collar is split into 4 pieces
    collar_piece1 = Rectangle((0, pattern_height - collar_length), width=collar_width, height=collar_length, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece1)
    collar_piece2 = Rectangle((0.5 * pattern_width - collar_width, pattern_height - collar_length), width=collar_width, height=collar_length, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece2)
    collar_piece3 = Rectangle((0.5 * pattern_width, pattern_height - collar_length), width=collar_width, height=collar_length, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)
    collar_piece4 = Rectangle((pattern_width - collar_width, pattern_height - collar_length), width=collar_width, height=collar_length, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece4)

    # Draw B5 areas, for necklines, and for usage as back neck facing or pockets, etc.
    # Construct B5 straight lines in x direction (width)
    ax.plot([0, b5_x], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height], color='b', lw=1)
    ax.plot([pattern_width - b5_x, pattern_width], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height], color='b', lw=1)
    # Construct B5 straight lines in y direction (length/height)
    ax.plot([b5_width, b5_width], [pattern_height - collar_length, pattern_height - collar_length - b5_y], color='b', lw=1)
    ax.plot([pattern_width - b5_width, pattern_width - b5_width], [pattern_height - collar_length, pattern_height - collar_length - b5_y], color='b', lw=1)
    # Construct B5 curves
    B5_left_start = (b5_x, pattern_height - collar_length - b5_height)
    B5_left_control = (b5_width, pattern_height - collar_length - b5_height)
    B5_left_end = (b5_width, pattern_height - collar_length - b5_y)
    B5_left_vertices = [B5_left_start, B5_left_control, B5_left_end]
    B5_right_start = (pattern_width - b5_x, pattern_height - collar_length - b5_height)
    B5_right_control = (pattern_width - b5_width, pattern_height - collar_length - b5_height)
    B5_right_end = (pattern_width - b5_width, pattern_height - collar_length - b5_y)
    B5_right_vertices = [B5_right_start, B5_right_control, B5_right_end]
    B5headcodes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    B5_left_path = Path(B5_left_vertices, B5headcodes)
    B5_right_path = Path(B5_right_vertices, B5headcodes)
    B5_left_curve = PathPatch(B5_left_path, fc="none", lw=1, edgecolor='b')
    ax.add_patch(B5_left_curve)
    B5_right_curve = PathPatch(B5_right_path, fc="none", lw=1, edgecolor='b')
    ax.add_patch(B5_right_curve)

    # Draw sleevehead curves
    sleeve1_control = (0.25 * pattern_width, pattern_height - collar_length - 2*sleeve_depth) #multiplied by 2 in plt construction
    sleeve1_start = (0.25 * pattern_width - sleeve_radius, pattern_height - collar_length)
    sleeve1_end = (0.25 * pattern_width + sleeve_radius, pattern_height - collar_length)
    sleeve2_control = (0.75 * pattern_width, pattern_height - collar_length - 2*sleeve_depth) #multiplied by 2 in plt construction
    sleeve2_start = (0.75 * pattern_width - sleeve_radius, pattern_height - collar_length)
    sleeve2_end = (0.75 * pattern_width + sleeve_radius, pattern_height - collar_length)
    sleeve1_vertices = [sleeve1_start, sleeve1_control, sleeve1_end]
    sleeve2_vertices = [sleeve2_start, sleeve2_control, sleeve2_end]
    sleeveheadcodes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    sleeve1_path = Path(sleeve1_vertices, sleeveheadcodes)
    sleeve2_path = Path(sleeve2_vertices, sleeveheadcodes)
    sleeve1_curve = PathPatch(sleeve1_path, fc="none", lw=1, edgecolor='b')
    sleeve2_curve = PathPatch(sleeve2_path, fc="none", lw=1, edgecolor='b')
    ax.add_patch(sleeve1_curve)
    ax.add_patch(sleeve2_curve)
    # Draw sleevehead lines
    ax.plot([collar_width, 0.25 * pattern_width - sleeve_radius], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)
    ax.plot([0.25 * pattern_width + sleeve_radius, 0.5 * pattern_width - collar_width], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)
    ax.plot([0.5 * pattern_width + collar_width, 0.75 * pattern_width - sleeve_radius], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)
    ax.plot([0.75 * pattern_width + sleeve_radius, pattern_width - collar_width], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)

    # Draw armhole lines
    ax.plot([0.25 * pattern_width, 0.25 * pattern_width], [pattern_height - collar_length - sleeve_depth, pattern_height - collar_length - sleeve_depth - armhole_length], color='b', lw=1)
    ax.plot([0.75 * pattern_width, 0.75 * pattern_width], [pattern_height - collar_length - sleeve_depth, pattern_height - collar_length - sleeve_depth - armhole_length], color='b', lw=1)

    # Draw dimensions
    # Annotations for dimensions at specific positions
    ax.annotate(f'{pattern_width} cm', xy=(pattern_width + 0.2, -5),
                xytext=(-5.9, -5),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'))
    ax.annotate(f'{pattern_height} cm', xy=(pattern_width + 5, 0),
                xytext=(pattern_width + 5, pattern_height + 5),
                textcoords="data", va="center", ha="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)
    ax.annotate(f'{collar_width} cm', xy=(0, pattern_height + 5),
                xytext=(collar_width + 4.6, pattern_height + 5),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'))
    ax.annotate(f'{collar_length} cm', xy=(-5, pattern_height),
                xytext=(-5, pattern_height - collar_length - 4.6),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)
    ax.annotate(f'{armhole_length:.2f} cm', xy=(0.25 * pattern_width + 5, pattern_height - collar_length - sleeve_depth),
                xytext=(0.25 * pattern_width + 5, pattern_height - collar_length - sleeve_depth - armhole_length - 6.5),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)

    # Setting limits
    ax.set_xlim(-15, pattern_width + 10)
    ax.set_ylim(-10, pattern_height + 15)
    ax.set_aspect('equal')
    ax.axis('off')  # Change to off to hide axis

    file_name = p_measurements['person_id'] + '_pattern_dimensions.pdf'
    plt.savefig(file_name, bbox_inches='tight', dpi=300)
    plt.show()

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

    # Draw the pattern in dxf
    draw_layered_pattern_dxf(p_measurements)
    
    # Draw the pattern with dimensions in pdf
    draw_pdf_with_dimensions(p_measurements)

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
