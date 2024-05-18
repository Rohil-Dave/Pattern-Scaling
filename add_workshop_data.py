'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics to the ZWS workshop data file
'''

import os
import csv

def calculate_ideal_bolt_width(width):
    '''Calculate the ideal bolt width for a given pattern width on boundaries of 5cm'''
    return width if width % 5 == 0 else width + 5 - width % 5

file_name = './ZWSworkshopData.csv'

with open(file_name, mode='r', newline='') as file:
    reader = csv.DictReader(file)
    source_data = [row for row in reader]  # Read all data into a list of dictionaries

print('person_id,', 'pattern_width,', 'pattern_height,', 'bolt_width_used,', 'cut_loss_width_used,', 'cut_loss_area_used,', 'cut_loss_width_ideal,', 'cut_loss_area_ideal,', 'efficiency_used,', 'efficiency_ideal')
for row in source_data:
    cut_loss_width_used = float(row['bolt_width']) - float(row['pattern_width'])
    cut_loss_area_used = cut_loss_width_used * float(row['pattern_height'])
    ideal_bolt_width = calculate_ideal_bolt_width(float(row['pattern_width']))
    cut_loss_width_ideal = ideal_bolt_width - float(row['pattern_width'])
    cut_loss_area_ideal = cut_loss_width_ideal * float(row['pattern_height'])
    efficiency_used = 1 - cut_loss_area_used / (float(row['bolt_width']) * float(row['pattern_height']))
    efficiency_ideal = 1 - cut_loss_area_ideal / (ideal_bolt_width * float(row['pattern_height']))
    print(row['person_id'] + ',' + row['pattern_width'] + ',' + row['pattern_height'] + ',' + row['bolt_width'] + ',' + str(cut_loss_width_used) + ',' + str(cut_loss_area_used) + ',' + str(cut_loss_width_ideal) + ',' + str(cut_loss_area_ideal) + ',' + str(efficiency_used) + ',' + str(efficiency_ideal))