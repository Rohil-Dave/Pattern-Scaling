#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics of the 100 scan Mendeley data file
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

def read_mendeley_data():
    '''
    Read the data from the workshop, cast all numeric values correctly
    '''
    file_name = './mendeleyScansData.csv'

    scan_data = []
    with open(file_name, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            for key, value in row.items():
                try:
                    row[key] = float(value)
                except ValueError:
                    row[key] = value
            scan_data.append(row)

    # # COMMENT OUT THE FOLLOWING LINE IF USING OPTION 1 FOR PATTERN HEIGHT
    # # Remove entries where 'Scan Code' is 66, if using OPTION 2 for pattern height
    # scan_data = [row for row in scan_data if row['Scan Code'] != 66]      

    return scan_data

def calculate_pattern_width(row):
    '''
    Calculate the pattern width for a given scan, taking the maximum of 
    several bodice circumference TM measurements
    '''
    abdomen_circ = row['Abdomen Circum Tape Measure']
    axilla_circ = row['Axilla Chest Circumference Tape Measure']
    chestbust_circ = row['Chest / Bust Circum Tape Measure']
    hip_circ = row['Hip Circum Tape Measure']
    seat_circ = row['Seat Circum Tape Measure']
    stomach_circ = row['Stomach Max Circum Tape Measure']
    waist_circ = row['Waist Circum Tape Measure']
    
    # Step 1: Find the largest circumference measurement
    raw_max = max(abdomen_circ, axilla_circ, chestbust_circ, hip_circ, seat_circ, stomach_circ, waist_circ)
    # Step 2: Round up to the nearest 0.5cm
    max_bodice_circ = math.ceil(raw_max * 2) / 2
    # Step 3: Calculate the pattern width with ease and seam allowance
    pattern_width = max_bodice_circ + 25 + 6 # add 25cm for ease (fixed for now) and 6cm for hem

    return pattern_width
    
def calculate_pattern_height(row):
    '''
    Calculate the pattern height for a given scan, deriving shirt length from
    OPTION 1 OR OPTION 2
    '''
    # OPTION 1: Use the half back center tape measure, waist height, crotch height
    half_cb_tm = row['Half Back Center Tape Measure']
    waist_height = row['Waist Height']
    crotch_height = row['Crotch Height']
    
    # Step 1: Calculate shirt length
    raw_shirt_length = half_cb_tm + waist_height - crotch_height
    # Step 2: Round up to the nearest 0.5cm
    shirt_length = math.ceil(raw_shirt_length * 2) / 2
    # Step 3: Calculate pattern height with collar piece length and hem allowance
    pattern_height = shirt_length + 25 + 2.5 # add 6cm for hem and 2cm for collar piece

    # return pattern_height

    # # OPTION 2: Use the mid shoulder heights, chin height, crotch height
    # # Must remove entry in scan_data 'Scan Code' is 66 because user does have mid shoulder height left
    # mid_shoulder_height_L = float(row['Mid Shoulder Height Left'])
    # mid_shoulder_height_R = float(row['Mid Shoulder Height Right'])
    # chin_height = float(row['Chin Height'])
    # crotch_height = float(row['Crotch Height'])
    
    # # Step 1: Compute the average mid-shoulder height, 
    # # Justification: Central tendency gives a better overall fit than the extremes in fitting
    # mid_shoulder_height = (mid_shoulder_height_L + mid_shoulder_height_R) / 2
    # # Step 2: Determine the center back neck height (CBN Height)
    # cbn_height = mid_shoulder_height + 5  # Center back neck is no more than 5 cm up
    # # Step 3: Validate the chin height constraint
    # # Ensure the chin height is within 10 cm of the center back neck height
    # if abs(chin_height - cbn_height) > 10:
    #     raise ValueError("Chin height difference with center back neck height exceeds 10 cm")
    # # Step 4: Calculate the shirt length
    # raw_shirt_length = cbn_height - crotch_height
    # # Step 5: Round up to the nearest 0.5cm
    # shirt_length = math.ceil(raw_shirt_length * 2) / 2
    # # Step 6: Calculate pattern height with collar piece length and hem allowance
    # pattern_height = shirt_length + 25 + 2.5 # add 6cm for hem and 2cm for collar piece

    # return pattern_height

def analyze_data(scan_data):
    '''
    we are going to compute the cut loss width, area, and efficiency for an
    ideal bolt width (within 5cm) and a bolt that we have (150cm). We will
    also indicate whether the off cuts can be used as embellishments, etc.

    we can do more here like indicate what kinds of embellishments we can 
    suggest given the off cut. If we define 'belt' and pocket geometry, we
    can recoup and increase the efficiency for given bolt width.
    '''

    analyses = []
    for row in scan_data:
        result = {}
        result['person_id'] = row['Scan Code'] # use scan code as unqiue identifier
        result['pattern_width'] = calculate_pattern_width(row)
        result['pattern_height'] = calculate_pattern_height(row) # fixed now for testing purposes
        result['bolt_width_used'] = 150 # fixed now for testing purposes

        if result['pattern_width'] > result['bolt_width_used']: # setting these to -1 for now
            result['cut_loss_width_used'] = -1
            result['cut_loss_area_used'] = -1
            result['efficiency_used'] = -1
        else:
            result['cut_loss_width_used'] = result['bolt_width_used'] - result['pattern_width']
            result['cut_loss_area_used'] = result['cut_loss_width_used'] * result['pattern_height']
            result['efficiency_used'] = 1 - result['cut_loss_area_used'] / (result['bolt_width_used'] * result['pattern_height'])

        result['ideal_bolt_width'] = calculate_ideal_bolt_width(result['pattern_width'])
        result['cut_loss_width_ideal'] = result['ideal_bolt_width'] - result['pattern_width']
        result['cut_loss_area_ideal'] = result['cut_loss_width_ideal'] * result['pattern_height']
        result['efficiency_ideal'] = 1 - result['cut_loss_area_ideal'] \
            / (result['ideal_bolt_width'] * result['pattern_height'])
        analyses.append(result)

    return analyses

def main():
    '''
    the main routine to analyze 100 scan Mendeley data
    '''

    scan_data = read_mendeley_data()
    analyses = analyze_data(scan_data)

    output_file = 'test.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=analyses[0].keys())

        writer.writeheader()
        for row in analyses:
            writer.writerow(row)

# Execute main function
if __name__ == "__main__":
    main()