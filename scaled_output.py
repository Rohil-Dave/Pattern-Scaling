#import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
#from matplotlib.patches import Arc
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# Input variables key:
# pw: pattern width
# ph: pattern height
# cw: collar width
# cl: collar length
# sd: sleevehead depth
# sh: sleevehead indent
# bw: B5 width
# bh: B5 height
# al: armhole length (calculated from pattern width and collar width)
# bx: B5 straight line extent x-coordinate
# by: B5 straight line extent y-coordinate


# Define the pattern drawing function
def draw_tee_pattern(pw, ph, cw, cl, sd, sh, bw, bh, bx, by):


    # Create a figure and an axis
    fig, ax = plt.subplots(figsize=(20, 10))

    # Draw total area of pattern
    main_body = Rectangle((0, 0), width=pw, height=ph, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(main_body)

    # Draw collar areas; collar is split into 4 pieces
    collar_piece1 = Rectangle((0, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece1)
    collar_piece2 = Rectangle((0.5*pw - cw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece2)
    collar_piece3 = Rectangle((0.5*pw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)
    collar_piece3 = Rectangle((pw - cw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)



    # Draw B5 areas, for necklines, and for usage as back neck facing or pockets, etc.
    # Construct B5 straight lines in x direction (width)
    ax.plot([0, bx], [ph - cl - bh, ph - cl - bh], color='b', lw=1)
    ax.plot([pw - bx, pw], [ph - cl - bh, ph - cl - bh], color='b', lw=1)
    # Construct B5 straight lines in y direction (length/height)
    ax.plot([bw, bw], [ph - cl, ph - cl - by], color='b', lw=1)
    ax.plot([pw - bw, pw - bw], [ph - cl, ph - cl - by], color='b', lw=1)

    B5_left_start = (bx, ph - cl - bh)
    B5_left_control = (bw, ph - cl - bh)   
    B5_left_end = (bw, ph - cl - by)
    B5_left_vertices = [B5_left_start, B5_left_control, B5_left_end]
    B5_right_start = (pw - bx, ph - cl - bh)
    B5_right_control = (pw - bw, ph - cl - bh)
    B5_right_end = (pw - bw, ph - cl - by)
    B5_right_vertices = [B5_right_start, B5_right_control, B5_right_end]
    B5headcodes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]

    B5_left_path = Path(B5_left_vertices, B5headcodes)
    B5_right_path = Path(B5_right_vertices, B5headcodes)

    B5_left_curve = PathPatch(B5_left_path, fc="none", lw=1, edgecolor='r')
    ax.add_patch(B5_left_curve)
    B5_right_curve = PathPatch(B5_right_path, fc="none", lw=1, edgecolor='r')
    ax.add_patch(B5_right_curve)

    # Simple box B5 pieces
    # b5_piece1 = Rectangle((0, ph - cl - bh), width=bw, height=bh, linewidth=1, edgecolor='b', facecolor='none')
    # ax.add_patch(b5_piece1)
    # b5_piece2 = Rectangle((pw - bw, ph - cl - bh), width=bw, height=bh, linewidth=1, edgecolor='b', facecolor='none')
    # ax.add_patch(b5_piece2)



    # Draw sleevehead lines
    sleeve1_start = (cw + sh, ph - cl)
    control_midpoint1 = (0.25*pw, ph - cl - 2*sd)   # sd is doubled show sleevehead connection to armhole, may need to adjust
    sleeve1_end = (0.5*pw - cw - sh, ph - cl)
    sleeve1_vertices = [sleeve1_start, control_midpoint1, sleeve1_end]
    sleeve2_start = (0.5*pw + cw + sh, ph - cl)
    control_midpoint2 = (0.75*pw, ph - cl - 2*sd)   # sd is doubled show sleevehead connection to armhole, may need to adjust
    sleeve2_end = (pw - cw - sh, ph - cl)
    sleeve2_vertices = [sleeve2_start, control_midpoint2, sleeve2_end]
    sleeveheadcodes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    
    sleeveheadpath1 = Path(sleeve1_vertices, sleeveheadcodes)
    sleeveheadpath2 = Path(sleeve2_vertices, sleeveheadcodes)

    sleeveline1 = PathPatch(sleeveheadpath1, fc="none", lw=1, edgecolor='r')
    ax.add_patch(sleeveline1)
    sleeveline2 = PathPatch(sleeveheadpath2, fc="none", lw=1, edgecolor='r')
    ax.add_patch(sleeveline2)



    # Draw lines connecting sleevehead lines to collar pieces, on pattern from left to right
    # Sample: ax.plot([x1, x2], [y1, y2], color='r')
    ax.plot([cw, cw + sh], [ph - cl, ph - cl], color='b', lw=1)
    ax.plot([0.5*pw - cw - sh, 0.5*pw - cw], [ph - cl, ph - cl], color='b', lw=1)
    ax.plot([0.5*pw + cw, 0.5*pw + cw + sh], [ph - cl, ph - cl], color='b', lw=1)
    ax.plot([pw - cw, pw - cw - sh], [ph - cl, ph - cl], color='b', lw=1)

    # Draw dashed lines to show sleevehead area
    ax.plot([cw + sh, 0.5*pw - cw - sh], [ph - cl, ph - cl], color='b', lw=1, linestyle='dashed')
    ax.plot([0.5*pw + cw + sh, pw - cw - sh], [ph - cl, ph - cl], color='b', lw=1, linestyle='dashed')


    # Draw armhole lines
    al = 0.5*(0.5*pw - 2*cw)
    ax.plot([0.25*pw, 0.25*pw], [ph - cl - sd, ph - cl - sd - al], color='b', lw=1)
    ax.plot([0.75*pw, 0.75*pw], [ph - cl - sd, ph - cl - sd - al], color='b', lw=1)


    # Draw


    # Setting limits
    ax.set_xlim(-10, 150)
    ax.set_ylim(-10, 110)
    ax.set_aspect('equal')
    ax.axis('on')  # Change to off to hide axis
    
    plt.show()


draw_tee_pattern(pw=140, ph=90, cw=9.5, cl=25, sd=3, sh=15, bw=14, bh=14, bx=6, by=6)
