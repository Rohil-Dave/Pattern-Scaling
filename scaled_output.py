#import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.patches import Rectangle
#from matplotlib.patches import Arc

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
    main_body = plt.Rectangle((0, 0), width=pw, height=ph, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(main_body)

    # Draw collar areas; collar is split into 4 pieces
    collar_piece1 = plt.Rectangle((0, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece1)
    collar_piece2 = plt.Rectangle(((pw/2) - cw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece2)
    collar_piece3 = plt.Rectangle(((pw/2), ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)
    collar_piece3 = plt.Rectangle((pw - cw, ph - cl), width=cw, height=cl, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(collar_piece3)

   # ax.plot([cw, cw], [ph - cl, ph], linewidth=1, color='b')  


    ax.set_xlim(-10, 210)
    ax.set_ylim(-10, 120)
    ax.set_aspect('equal')
    ax.axis('on')
    
    plt.show()


draw_tee_pattern(pw=140, ph=90, cw=9.5, cl=25)



# # Function to draw a rectangle with the given width and height
# def draw_rectangle(width, height):
#     plt.figure(figsize=(5, 5 * height / width))
#     plt.gca().add_patch(plt.Rectangle((0, 0), width, height, edgecolor='black', facecolor='none'))
#     plt.xlim(0, width)
#     plt.ylim(0, height)
#     plt.gca().set_aspect('equal', adjustable='box')
#     plt.title(f"Rectangle {width}x{height}")
#     plt.axis('off')  # Hide axes
#     plt.show()

# draw_rectangle(200, 100)