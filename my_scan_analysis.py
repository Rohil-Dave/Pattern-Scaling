#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics of my scan data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import csv
import math

def calculate_ideal_bolt_width(width):
    '''
    Calculate the ideal bolt width for a given pattern width on boundaries of 5cm
    '''
    return width if width % 5 == 0 else width + 5 - width % 5

def read_myscan_data():
    '''
    Read the data from the workshop, cast all numeric values correctly
    '''
    file_name = './myScanData.csv'

    myscan_data = []
    with open(file_name, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            for key, value in row.items():
                try:
                    row[key] = float(value)
                except ValueError:
                    row[key] = value
            myscan_data.append(row)
    print(myscan_data)


