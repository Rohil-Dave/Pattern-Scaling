#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics to the ZWS workshop data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import csv

def calculate_ideal_bolt_width(width):
    '''
    Calculate the ideal bolt width for a given pattern width on boundaries of 5cm
    '''
    return width if width % 5 == 0 else width + 5 - width % 5

def read_workshop_data():
    '''
    Read the data from the workshop, cast all numeric values correctly
    '''
    file_name = './ZWSworkshopData.csv'

    workshop_data = []
    with open(file_name, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            for key, value in row.items():
                try:
                    row[key] = float(value)
                except ValueError:
                    row[key] = value
            workshop_data.append(row)
    return workshop_data

def analyze_data(workshop_data):
    '''
    we are going to compute the cut loss width, area, and efficiency for an
    ideal bolt width (within 5cm) and a bolt that we have (150cm). We will
    also indicate whether the off cuts can be used as embellishments, etc.

    we can do more here like indicate what kinds of embellishments we can 
    suggest given the off cut. If we define 'belt' and pocket geometry, we
    can recoup and increase the efficiency for given bolt width.
    '''

    analyses = []
    for row in workshop_data:
        result = {}
        result['person_id'] = row['person_id']
        result['pattern_width'] = row['pattern_width']
        result['pattern_height'] = row['pattern_height']
        result['bolt_width_used'] = row['bolt_width']
        result['cut_loss_width_used'] = row['bolt_width'] - row['pattern_width']
        result['cut_loss_area_used'] = result['cut_loss_width_used'] * row['pattern_height']
        result['efficiency_used'] = 1 - result['cut_loss_area_used'] / (row['bolt_width'] *
            row['pattern_height'])
        result['ideal_bolt_width'] = calculate_ideal_bolt_width(row['pattern_width'])
        result['cut_loss_width_ideal'] = result['ideal_bolt_width'] - row['pattern_width']
        result['cut_loss_area_ideal'] = result['cut_loss_width_ideal'] * row['pattern_height']
        result['efficiency_ideal'] = 1 - result['cut_loss_area_ideal'] \
            / (result['ideal_bolt_width'] * row['pattern_height'])
        analyses.append(result)

    return analyses

def main():
    '''
    the main routine to analyze workshop data
    '''

    workshop_data = read_workshop_data()
    analyses = analyze_data(workshop_data)

    output_file = 'ZWSworkshopAnalysis.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=analyses[0].keys())

        writer.writeheader()
        for row in analyses:
            writer.writerow(row)

# Execute main function
if __name__ == "__main__":
    main()
