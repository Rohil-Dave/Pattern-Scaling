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
    Read the data from the workshop, cast all numeric values correctly.
    The first column of the CSV is used as keys, and the rest of the columns are values.
    '''
    file_name = './myScanData.csv'

    myscan_data = {}
    with open(file_name, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Read the header row

        for row in csv_reader:
            key = row[0]
            values = row[1:]
            # Cast numeric values correctly
            casted_values = []
            for value in values:
                try:
                    casted_values.append(float(value))
                except ValueError:
                    casted_values.append(value)
            myscan_data[key] = casted_values
    return myscan_data

def calculate_pattern_width(myscan_data):
    '''
    Calculate the pattern width from my scan data, taking the maximum of
    several bodice circumference TM measurements

    Use Index 1 to access processed median values from the 5 total scans
    Example) median_value = myscan_data['measurement name'][1]

    Use Index 0 to access PRE processed median values from the 5 total scans
    Example) pre_median_value = myscan_data['measurement name'][0]
    '''
    chestbust_circ = myscan_data['B01c_ChestBust_Circ_TM_072c'][1]
    stomach_circ = myscan_data['S20c_Stomach_Circ_TM_083c'][1]
    abdomen_circ = myscan_data['A01c_Abdomen_Circ_TM_084c'][1]
    seat_circ = myscan_data['S01c_Seat_CircTM_086c'][1]
    hip_circ = myscan_data['H01c_Hip_CircTM_085c'][1]
    waist_circ = myscan_data['W01c_Waist_SoB_2_Circ_TM_105c'][1]

    # Step 1: Find the largest circumference measurement
    raw_max = max(chestbust_circ, stomach_circ, abdomen_circ, seat_circ, hip_circ, waist_circ)
    # Step 2: Round up to the nearest 0.5cm
    max_bodice_circ = math.ceil(raw_max * 2) / 2
    # Step 3: Calculate the pattern width with ease and seam allowance
    pattern_width = max_bodice_circ + 25 + 6 # add 25cm for ease (fixed for now) and 6cm for hem
    return pattern_width

def calculate_pattern_height(myscan_data):
    '''
    Calculate the pattern height from my scan data, deriving shirt length from
    center back neck height and crotch height

    Use Index 1 to access processed median values from the 5 total scans
    Example) median_value = myscan_data['measurement name'][1]

    Use Index 0 to access PRE processed median values from the 5 total scans
    Example) pre_median_value = myscan_data['measurement name'][0]
    '''
    cbn_height = myscan_data['N10hb_Neck_Base_Circ_CB_Height_001hb'][1]
    crotch_height = myscan_data['C10h_Crotch_Height_036h'][1]

    # Step 1: Calculate shirt length
    raw_shirt_length = cbn_height - crotch_height
    # Step 2: Round up to the nearest 0.5cm
    shirt_length = math.ceil(raw_shirt_length * 2) / 2
    # Step 3: Calculate pattern height with collar piece length and hem allowance
    pattern_height = shirt_length + 25 + 2.5 # add 6cm for hem and 2cm for collar piece
    return pattern_height
    
def main():
    '''
    the main routine to analyze my scan data
    '''

    myscan_data = read_myscan_data()
    calculate_pattern_width(myscan_data)
    calculate_pattern_height(myscan_data)

# Execute main function
if __name__ == "__main__":
    main()


