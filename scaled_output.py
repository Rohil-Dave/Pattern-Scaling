#import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Arc

# Input variables key:
# pw: pattern width
# ph: pattern height
# cw: collar width
# cl: collar length

# Define the pattern drawing function
def draw_tee_pattern(pw, ph, cw, cl):
    # Create a figure and an axis
    fig, ax = plt.subplots(figsize=(10, 5))

    # Draw total area of pattern
    main_body = Rectangle((0, 0), width=pw, height=ph, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(main_body)


    # Draw collar areas; collar is split into 4 pieces
    collar_piece1 = Rectangle((0, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece1)
    collar_piece2 = Rectangle(((pw/2) - cw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece2)
    collar_piece3 = Rectangle(((pw/2), ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)
    collar_piece3 = Rectangle((pw - cw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)

    # Draw neckline
    ax.plot([0,pw], [ph - cl, ph - cl], linewidth=1, color='b')
    neckline_arc1 = Arc((20, 100), width=40, height=20, angle=0, theta1=0, theta2=180, linewidth=1, edgecolor='b')
    ax.add_patch(neckline_arc1)


    ax.set_xlim(-10, 160)
    ax.set_ylim(-10, 100)
    ax.set_aspect('equal')
    ax.axis('on')
    
    plt.show()


draw_tee_pattern(pw=140, ph=90, cw=9.5, cl=25)
