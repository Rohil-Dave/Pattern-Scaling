#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics to the ZWS workshop data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import csv
from matplotlib import pyplot

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
        result['bolt_width_ideal'] = calculate_ideal_bolt_width(row['pattern_width'])
        result['cut_loss_width_ideal'] = result['bolt_width_ideal'] - row['pattern_width']
        result['cut_loss_area_ideal'] = result['cut_loss_width_ideal'] * row['pattern_height']
        result['efficiency_ideal'] = 1 - result['cut_loss_area_ideal'] \
            / (result['bolt_width_ideal'] * row['pattern_height'])
        
        
        analyses.append(result)

    return analyses

def generate_plots(analyses):
    '''
    generate some plots of workshop data analyses
    '''

    # make a list of the ids and values
    ids = [row['person_id'] for row in analyses]
    efficiency_used = [row['efficiency_used'] for row in analyses]
    efficiency_ideal = [row['efficiency_ideal'] for row in analyses]
    cut_loss_width_used = [row['cut_loss_width_used'] for row in analyses]
    cut_loss_area_used = [row['cut_loss_area_used'] for row in analyses]
    cut_loss_width_ideal = [row['cut_loss_width_ideal'] for row in analyses]
    cut_loss_area_ideal = [row['cut_loss_area_ideal'] for row in analyses]
    bolt_width_used = [row['bolt_width_used'] for row in analyses]
    bolt_width_ideal = [row['bolt_width_ideal'] for row in analyses]

    # Create a figure and a 2x2 grid of subplots
    fig, axs = pyplot.subplots(2, 2, figsize=(12, 10))

    # Plot on each subplot
    axs[0, 0].plot(ids, efficiency_used, label='Efficiency_Used')  # First subplot
    axs[0, 0].plot(ids, efficiency_ideal, label='Efficiency_Ideal')  
    axs[0, 0].set_title('Efficiency values for Workshop attendees')
    axs[0, 0].set_xlabel('Identifiers')
    axs[0, 0].set_ylabel('Efficiencies')
    axs[0, 0].legend()

    axs[0, 1].plot(ids, cut_loss_area_used, label='Cut_Loss_Area_Used')  # Second subplot
    axs[0, 1].plot(ids, cut_loss_area_ideal, label='Cut_Loss_Area_Ideal')  
    axs[0, 1].set_title('Cut Loss Area for Workshop attendees')
    axs[0, 1].set_xlabel('Identifiers')
    axs[0, 1].set_ylabel('Cut Loss Area')
    axs[0, 1].legend()

    axs[1, 0].plot(ids, cut_loss_width_used, label='Cut_Loss_Width_Used')  # Third subplot
    axs[1, 0].plot(ids, cut_loss_width_ideal, label='Cut_Loss_Width_Ideal')  
    axs[1, 0].set_title('Cut Loss Width for Workshop attendees')
    axs[1, 0].set_xlabel('Identifiers')
    axs[1, 0].set_ylabel('Cut Loss Width')
    axs[1, 0].legend()

    axs[1, 1].plot(ids, bolt_width_used, label='Bolt_Width_Used')  # Fourth subplot
    axs[1, 1].plot(ids, bolt_width_ideal, label='Bolt_Width_Ideal')  
    axs[1, 1].set_title('Bolt Width for Workshop attendees')
    axs[1, 1].set_xlabel('Identifiers')
    axs[1, 1].set_ylabel('Bolt Width')
    axs[1, 1].legend()

    '''pyplot.plot(ids, efficiency_used)
    pyplot.plot(ids, efficiency_ideal)
    pyplot.xlabel('Identifiers')
    pyplot.ylabel('Efficiency')
    pyplot.title('Efficiency values for Workshop attendees')
    pyplot.legend(['Used', 'Ideal'])'''
    # Add some space between the plots
    pyplot.tight_layout()
    pyplot.savefig('Workshop_Plot.png')


def main():
    '''
    the main routine to analyze workshop data
    '''

    workshop_data = read_workshop_data()
    analyses = analyze_data(workshop_data)
    generate_plots(analyses)

    output_file = 'ZWSworkshopAnalysis.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=analyses[0].keys())

        writer.writeheader()
        for row in analyses:
            writer.writerow(row)

# Execute main function
if __name__ == "__main__":
    main()
