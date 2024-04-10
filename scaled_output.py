import numpy as np
import matplotlib.pyplot as plt

# Function to draw a rectangle with the given width and height
def draw_rectangle(width, height):
    plt.figure(figsize=(5, 5 * height / width))
    plt.gca().add_patch(plt.Rectangle((0, 0), width, height, edgecolor='black', facecolor='none'))
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(f"Rectangle {width}x{height}")
    plt.axis('off')  # Hide axes
    plt.show()

draw_rectangle(200, 100)