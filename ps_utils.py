#!/usr/bin/env python3
'''
Utilities for pattern scaling module
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import numpy as np
import matplotlib.pyplot as plt

def add_pocket(analyses):
    '''
    Checks if there is enough cut loss to add a pocket. Determines pocket size based 
    on cut loss width. 
    
    Only considers pocket if pattern width is scaled to actual
    body measurements and not to the ideal bolt width i.e. actual_measure == 1

    We will set a constant finished pocket size of 10cm by 10cm for all users.
    For this, seam allowances of 0.5cm are added to the side and bottom edges of the pocket,
    and heam allowance of 2cm is added to the top edge of the pocket.
    The pocket pattern piece then has dimensions of 11cm by 12.5cm. So area of 2 pockets is 275
    '''
    for row in analyses:
        if row['cut_loss_width_used'] >= 11:
            row['pocket_possible'] = True
            row['embellished_saved'] = 275.0 / row['cut_loss_area_used']
        else:
            row['pocket_possible'] = False
            row['embellished_saved'] = 0.0
    return analyses

def compute_stats(analyses, column_name):
    '''
    compute the distribution statistics for a particular column in our analyses data
    '''
    values = [row[column_name] for row in analyses if column_name in row]
    mean = np.mean(values)
    median = np.median(values)
    std_dev = np.std(values)
    return mean, median, std_dev, values

def generate_box_plots(analyses, data_set, column_names):
    ''''
    generate box plots for a few given columns of the data set
    print stats as well
    '''

    for column_name in column_names:
        mean, median, std_dev, values = compute_stats(analyses, column_name)
        print(column_name, "Mean:", mean)
        print(column_name, "Median:", median)
        print(column_name, "Standard Deviation:", std_dev)

        # Boxplot
        plt.boxplot(values)
        plt.title(f"Boxplot of '{data_set}' data '{column_name}' column")
        plt.ylabel("Values")
        plt.xlabel(column_name)
        plt.savefig(f"{data_set}_{column_name}_Boxplot.png")
        plt.close()