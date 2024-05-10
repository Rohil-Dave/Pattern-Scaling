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
sleevehead radius, sr
B5 straight line extent x-coordinate, bx
B5 straight line extent y-coordinate, by
armhole length (calculated from pattern width and collar width), al
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import os
import csv
import ezdxf
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.path import Path
from matplotlib.patches import PathPatch

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
    b5_height = b5_width # this might be different later, in which case it will be in the p_measurements dict
    b5_x = b5_y = b5_width * 0.5 # these might also be different
    sleevehead_depth = p_measurements['sleevehead_depth']
    sleevehead_radius = p_measurements['sleevehead_radius']
   

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
        ((0.25 * pattern_width - sleevehead_radius, pattern_height - collar_length), (0.25 * pattern_width, pattern_height - collar_length - sleevehead_depth), (0.25 * pattern_width + sleevehead_radius, pattern_height - collar_length)),
        ((0.75 * pattern_width - sleevehead_radius, pattern_height - collar_length), (0.75 * pattern_width, pattern_height - collar_length - sleevehead_depth), (0.75 * pattern_width + sleevehead_radius, pattern_height - collar_length))
    ]
    for start, control, end in sleeve_data:
        msp.add_spline([start, control, end], dxfattribs={'layer': 'Sleeve'})

    # Draw lines connecting sleevehead lines to collar pieces
    msp.add_line((collar_width, pattern_height - collar_length), (0.25 * pattern_width - sleevehead_radius, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # from leftmost collar to the right
    msp.add_line((0.25 * pattern_width + sleevehead_radius, pattern_height - collar_length), (0.5 * pattern_width - collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # between left middle and center collar
    msp.add_line((0.5 * pattern_width + collar_width, pattern_height - collar_length), (0.75 * pattern_width - sleevehead_radius, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # between center and right middle collar
    msp.add_line((0.75 * pattern_width + sleevehead_radius, pattern_height - collar_length), (pattern_width - collar_width, pattern_height - collar_length), dxfattribs={'layer': 'Sleeve'})  # from rightmost collar to the left

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
    msp.add_line((b5_width, pattern_height - collar_length), (0.25 * pattern_width - sleevehead_radius, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # middle connecting line thru center back
    msp.add_line((0.25 * pattern_width + sleevehead_radius, pattern_height - collar_length), (0.75 * pattern_width - sleevehead_radius, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # left connecting line thru center front
    msp.add_line((0.75 * pattern_width + sleevehead_radius, pattern_height - collar_length), (pattern_width - b5_width, pattern_height - collar_length), dxfattribs={'layer': 'Bodice'})  # right connecting line thru center front

    # Side and bottom border
    msp.add_lwpolyline([(0, pattern_height - collar_length - b5_height), (0, 0), (pattern_width, 0), (pattern_width, pattern_height - collar_length - b5_height)], dxfattribs={'layer': 'Bodice'})

    # Draw armhole lines
    armhole_length = 0.5 * (0.5 * pattern_width - (2 * collar_width))  # Calculate armhole length
    p_measurements['armhole_length'] = armhole_length # Add to value p_measurements dict
    msp.add_line((0.25 * pattern_width, pattern_height - collar_length - sleevehead_depth), (0.25 * pattern_width, pattern_height - collar_length - sleevehead_depth - armhole_length), dxfattribs={'layer': 'Bodice'})
    msp.add_line((0.75 * pattern_width, pattern_height - collar_length - sleevehead_depth), (0.75 * pattern_width, pattern_height - collar_length - sleevehead_depth - armhole_length), dxfattribs={'layer': 'Bodice'})

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
    sleevehead_depth = p_measurements['sleevehead_depth']
    sleevehead_radius = p_measurements['sleevehead_radius']
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
    sleeve1_control = (0.25 * pattern_width, pattern_height - collar_length - 2*sleevehead_depth) #multiplied by 2 in plt construction
    sleeve1_start = (0.25 * pattern_width - sleevehead_radius, pattern_height - collar_length)
    sleeve1_end = (0.25 * pattern_width + sleevehead_radius, pattern_height - collar_length)
    sleeve2_control = (0.75 * pattern_width, pattern_height - collar_length - 2*sleevehead_depth) #multiplied by 2 in plt construction
    sleeve2_start = (0.75 * pattern_width - sleevehead_radius, pattern_height - collar_length)
    sleeve2_end = (0.75 * pattern_width + sleevehead_radius, pattern_height - collar_length)
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
    ax.plot([collar_width, 0.25 * pattern_width - sleevehead_radius], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)
    ax.plot([0.25 * pattern_width + sleevehead_radius, 0.5 * pattern_width - collar_width], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)
    ax.plot([0.5 * pattern_width + collar_width, 0.75 * pattern_width - sleevehead_radius], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)
    ax.plot([0.75 * pattern_width + sleevehead_radius, pattern_width - collar_width], [pattern_height - collar_length, pattern_height - collar_length], color='b', lw=1)

    # Draw armhole lines
    ax.plot([0.25 * pattern_width, 0.25 * pattern_width], [pattern_height - collar_length - sleevehead_depth, pattern_height - collar_length - sleevehead_depth - armhole_length], color='b', lw=1)
    ax.plot([0.75 * pattern_width, 0.75 * pattern_width], [pattern_height - collar_length - sleevehead_depth, pattern_height - collar_length - sleevehead_depth - armhole_length], color='b', lw=1)

    # Draw hem and sew lines
    # Center Front hem lines
    ax.plot([2.5, 2.5], [pattern_height - collar_length - b5_height, 0], color='k', lw=0.5, linestyle='dashdot')
    ax.plot([pattern_width - 2.5, pattern_width - 2.5], [pattern_height - collar_length - b5_height, 0], color='k', lw=0.5, linestyle='dashdot')
    ax.plot([2.5 + 3, 2.5 + 3], [pattern_height - collar_length - b5_height, 0], color='k', lw=0.5, linestyle='dashdot')
    ax.plot([pattern_width - 2.5 - 3, pattern_width - 2.5 - 3], [pattern_height - collar_length - b5_height, 0], color='k', lw=0.5, linestyle='dashdot')
    # Center Front notches
    ax.plot([2.5, 2.5], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([pattern_width - 2.5, pattern_width - 2.5], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([2.5 + 3, 2.5 + 3], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([pattern_width - 2.5 - 3, pattern_width - 2.5 - 3], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([2.5 + 3 + 3, 2.5 + 3 + 3], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([pattern_width - 2.5 - 3 - 3, pattern_width - 2.5 - 3 - 3], [pattern_height - collar_length - b5_height, pattern_height - collar_length - b5_height - 1], color='k', lw=1.5, linestyle='solid')
    # Center Back pleat sew lines
    ax.plot([0.5 * pattern_width - 9.5, 0.5 * pattern_width - 9.5], [pattern_height - collar_length, pattern_height - collar_length - 14], color='k', lw=0.5, linestyle='dashdot')
    ax.plot([0.5 * pattern_width + 9.5, 0.5 * pattern_width + 9.5], [pattern_height - collar_length, pattern_height - collar_length - 14], color='k', lw=0.5, linestyle='dashdot')
    # Center Back notches
    ax.plot([0.5 * pattern_width, 0.5 * pattern_width], [pattern_height - collar_length, pattern_height - collar_length - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([0.5 * pattern_width - 9.5, 0.5 * pattern_width - 9.5], [pattern_height - collar_length, pattern_height - collar_length - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([0.5 * pattern_width + 9.5, 0.5 * pattern_width + 9.5], [pattern_height - collar_length, pattern_height - collar_length - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([0.5 * pattern_width - 9.5 - 4.5, 0.5 * pattern_width - 9.5 - 4.5], [pattern_height - collar_length, pattern_height - collar_length - 1], color='k', lw=1.5, linestyle='solid')
    ax.plot([0.5 * pattern_width + 9.5 + 4.5, 0.5 * pattern_width + 9.5 + 4.5], [pattern_height - collar_length, pattern_height - collar_length - 1], color='k', lw=1.5, linestyle='solid')

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
    ax.annotate(f'{collar_length} cm', xy=(-5, pattern_height - collar_length),
                xytext=(-5, pattern_height + 4.6),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)
    ax.annotate(f'{armhole_length:.2f} cm', xy=(0.25 * pattern_width + 5, pattern_height - collar_length - sleevehead_depth),
                xytext=(0.25 * pattern_width + 5, pattern_height - collar_length - sleevehead_depth - armhole_length - 6.5),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)
    ax.annotate(f'{b5_width} cm', xy=(-5, pattern_height - collar_length),
                xytext=(-5, pattern_height - collar_length - b5_height - 4.6),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)
    ax.annotate(f'{sleevehead_depth} cm', xy=(0.25 * pattern_width, pattern_height - collar_length - sleevehead_depth),
                xytext=(0.25 * pattern_width, pattern_height - collar_length + 4.6),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'),
                rotation=90)
    ax.annotate(f'{sleevehead_radius} cm', xy=(0.75* pattern_width - sleevehead_radius, pattern_height - collar_length),
                xytext=(0.75 * pattern_width + 4.4, pattern_height - collar_length),
                textcoords="data", ha="center", va="center",
                arrowprops=dict(arrowstyle="|-|", lw=1, color='red'))
    

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
    Assigns fabric width based on bust/chest, waist, and hip measurements

    We need to choose the appropriate width based on body measurements, ease 
    and sewing tolerances
    The formula is the sum of larger body circumference + ease + tolerance
    If we are not choosing actual fit width, then we need to closest bolt width
    size which is a ceiling on 5 cm boundaries, e.g 130cm, 135cm, 140cm, etc
    '''

    # Determine the larger of the chest, waist, (and hip measurements if shirt below hip)
    if user_measurements['shirt_above_hip'] == 1: 
        largest_measurement = max(user_measurements['bust_circ'], user_measurements['waist_circ'])
    else:
        largest_measurement = max(user_measurements['bust_circ'], user_measurements['waist_circ'], user_measurements['hip_circ'])

    width = largest_measurement + p_measurements['ease'] + p_measurements['sew_tolerance']

    if user_measurements['actual_measure'] == 1:
        # return actual computed width
        return width

    # return the width of the closest bolt (we assume bolt widths are multiples of 5)
    return width if width % 5 == 0 else width + 5 - width % 5

def assign_template_size(user_measurements, param):
    '''
    Assigns the template size for the neck facing (B5) pieces and sleeve head curves 
    based on the user's body measurements

    We need to choose the appropriate template sizes when the pattern width is scaled up
    or down based on the largest bodice circumference (between bust, waist, and hip)

    The ideal range of largest bodice circumference for the base pattern is 95—125 cm
    '''

    # Determine the larger of the chest, waist, (and hip measurements if shirt below hip)
    if user_measurements['shirt_below_hip'] == 1: 
        largest_measurement = max(user_measurements['bust_circ'], user_measurements['waist_circ'], user_measurements['hip_circ'])
    else:
        largest_measurement = max(user_measurements['bust_circ'], user_measurements['waist_circ'])

    if param == 'b5_width' or param == 'sleevehead_radius':
        if largest_measurement < 95:  # smaller than ideal range
            return 12
        if largest_measurement > 125: # larger than ideal range
            return 16
        return 14 # within ideal range
    if param == 'sleevehead_depth':
        if largest_measurement < 95:
            return 3.0
        if largest_measurement > 125:
            return 4.0
        return 3.5

def update_db(user_measurements, p_measurements):
    '''
    Writes out the values to a csv file
    '''
    file_name = './ZWSworkshopData.csv'

    file_exists = os.path.exists(file_name)
    data_to_append = {**user_measurements, **p_measurements}
    fieldnames = data_to_append.keys()

    # Open the CSV file in append mode
    with open(file_name, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header if the file doesn't exist
        if not file_exists:
            writer.writeheader()
        
        # Write data to the file
        writer.writerow(data_to_append)

def compute_efficiency(user_measurements, p_measurements):
    '''
    Compute the efficiency of the pattern
    We know the 'ideal' pattern width, need to see if it fits the given bolt width
    If the bolt width is too small, see if we can tip the pattern 90 degrees and 
    fit the pattern width

    The basic computation is simple: bolt width - patter dimension / bolt width

    We should record whether we used pattern width (option 1), pattern height (option 2)
    or something more complex. For example if bolt width is smaller than we might need
    to add a panel or cut the pattern into quads. All of this is lumped as (option 3)
    and the efficiency is listed as -1
    '''
    if p_measurements['pattern_width'] < user_measurements['bolt_width']:
        p_measurements['Eff_Option'] = 1
        p_measurements['Efficiency'] = 1 - (user_measurements['bolt_width'] - p_measurements['pattern_width']) / user_measurements['bolt_width']
    elif p_measurements['pattern_height'] < user_measurements['bolt_width']:
        p_measurements['Eff_Option'] = 2
        p_measurements['Efficiency'] = 1 - (user_measurements['bolt_width'] - p_measurements['pattern_height']) / user_measurements['bolt_width']
    else:
        p_measurements['Eff_Option'] = 3
        p_measurements['Efficiency'] = -1.0

def calculate_and_draw(user_measurements):
    '''
    Calculates the dimensions and draw the pattern
    '''
    # Extract user measurements
    shirt_length = user_measurements['desired_shirt_length']

    # Append pattern measurements, both fixed and variable
    p_measurements = {}
    p_measurements['person_id'] = user_measurements['person_id']
    p_measurements['ease'] = 25 # currently fixed
    p_measurements['sew_tolerance'] = 6 # FIXED FOR ALL BODIES

    p_measurements['collar_width'] = 9.5 # FIXED FOR ALL BODIES
    p_measurements['collar_length'] = 25 # FIXED FOR ALL BODIES
    
    p_measurements['sleevehead_depth'] = assign_template_size(user_measurements, 'sleevehead_depth') # Assigns based on largest body circumference
    p_measurements['sleevehead_radius'] = assign_template_size(user_measurements, 'sleevehead_radius') # Assigns based on largest body circumference
    p_measurements['b5_width'] = assign_template_size(user_measurements, 'b5_width') # Assigns based on largest body circumference

    p_measurements['pattern_height'] = shirt_length + p_measurements['collar_length'] + 2.5 # must account for hem of 2.5
    p_measurements['pattern_width'] = get_fabric_width(user_measurements, p_measurements) # pattern_width based on bust, hip ranges

    # Draw the pattern in dxf
    draw_layered_pattern_dxf(p_measurements)
    # Draw the pattern with dimensions in pdf
    draw_pdf_with_dimensions(p_measurements)
    # See how well it fits the given bolt
    compute_efficiency(user_measurements, p_measurements)
    # Update the database
    update_db(user_measurements, p_measurements)

def main():
    '''
    The main function. We get the user measurements and figure out the pattern
    During the measurement pattern_heightase we take a few readings (shirt length, bust, hip, 
    arm, neck, waist, shoulder width, and sleeve length). We may not use them all 
    for this particular pattern

    Shirt length and sleeve length are 'desired' quantities, the others are based on body size
    '''
    user_measurements = {}
    user_measurements['person_id'] = input('Enter the id of the person (str): ')
    user_measurements['desired_shirt_length'] = float(input('Enter your desired shirt length (cm): '))
    user_measurements['shirt_above_hip'] = int(input('Enter 1 if shirt length ends above hip OR 0 if shirt length ends below hip: '))
    user_measurements['bust_circ'] = float(input('Enter your chest/bust circumference (cm): '))
    user_measurements['waist_circ'] = float(input('Enter your waist circumference (cm): '))
    user_measurements['hip_circ'] = float(input('Enter your hip circumference (cm): '))
    user_measurements['arm_circ'] = float(input('Enter your arm circumference (cm): '))
    user_measurements['neck_circ'] = float(input('Enter your neck circumference (cm): '))
    user_measurements['shoulder_width'] = float(input('Enter your shoulder width (cm): '))
    user_measurements['desired_sleeve_length'] = float(input('Enter your desired sleeve length (cm): '))
    user_measurements['actual_measure'] = int(input('Enter 1 for actual fit width OR 0 for best bolt width: '))
    user_measurements['bolt_width'] = float(input('Enter the width of the bolt you want to use (cm): '))

    # Generate the customised pattern
    calculate_and_draw(user_measurements)

# Execute main function
if __name__ == "__main__":
    main()
