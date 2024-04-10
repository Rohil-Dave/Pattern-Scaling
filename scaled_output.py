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


# Define the pattern drawing function
def draw_tee_pattern(pw, ph, cw, cl, sd, sh, bw, bh):


    # Create a figure and an axis
    fig, ax = plt.subplots(figsize=(10, 5))

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
    b5_piece1 = Rectangle((0, ph - cl - bh), width=bw, height=bh, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(b5_piece1)
    b5_piece2 = Rectangle((pw - bw, ph - cl - bh), width=bw, height=bh, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(b5_piece2)

    # Draw sleevehead lines
    start_point1 = (cw + sh, ph - cl)
    control_midpoint1 = (0.25*pw, ph - cl - 2*sd)   # sd is doubled show sleevehead connection to armhole, may need to adjust
    end_point1 = (0.5*pw - cw - sh, ph - cl)

    start_point2 = (0.5*pw + cw + sh, ph - cl)
    control_midpoint2 = (0.75*pw, ph - cl - 2*sd)   # sd is doubled show sleevehead connection to armhole, may need to adjust
    end_point2 = (pw - cw - sh, ph - cl)

    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    vertices1 = [start_point1, control_midpoint1, end_point1]
    vertices2 = [start_point2, control_midpoint2, end_point2]
    sleeveheadpath1 = Path(vertices1, codes)
    sleeveheadpath2 = Path(vertices2, codes)

    sleeveline1 = PathPatch(sleeveheadpath1, fc="none", lw=1, edgecolor='b')
    ax.add_patch(sleeveline1)
    sleeveline2 = PathPatch(sleeveheadpath2, fc="none", lw=1, edgecolor='b')
    ax.add_patch(sleeveline2)

    # Draw lines connecting sleevehead lines to collar pieces, on pattern from left to right
    # Sample: ax.plot([x1, x2], [y1, y2], color='r')
    ax.plot([cw, cw + sh], [ph - cl, ph - cl], color='r', lw=1)
    ax.plot([0.5*pw - cw - sh, 0.5*pw - cw], [ph - cl, ph - cl], color='r', lw=1)
    ax.plot([0.5*pw + cw, 0.5*pw + cw + sh], [ph - cl, ph - cl], color='r', lw=1)
    ax.plot([pw - cw, pw - cw - sh], [ph - cl, ph - cl], color='r', lw=1)

    # Draw armhole lines
    al = 0.5*(0.5*pw - 2*cw)
    ax.plot([0.25*pw, 0.25*pw], [ph - cl - sd, ph - cl - sd - al], color='g', lw=1)
    ax.plot([0.75*pw, 0.75*pw], [ph - cl - sd, ph - cl - sd - al], color='g', lw=1)

    # Setting limits
    ax.set_xlim(-10, 160)
    ax.set_ylim(-10, 100)
    ax.set_aspect('equal')
    ax.axis('on')  # Change to off to hide axis
    
    plt.show()


draw_tee_pattern(pw=140, ph=90, cw=9.5, cl=25, sd=3, sh=8, bw=14, bh=14)
