#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics to the ZWS workshop data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import csv
from matplotlib import pyplot as plt
import numpy as np

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

    analyses = [] # List of dictionaries to store the results of the analysis

    # For each workshop participant, calculate the cut loss and efficiencies
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
        
        # Calculate the ease for the finished garment, only for participants who finished
        if row['garment_finished'] == 1:
            result['FG_bust_ease'] = row['FG_bust_circ'] - row['bust_circ']
            result['FG_waist_ease'] = row['FG_waist_circ'] - row['waist_circ']
            result['FG_hip_ease'] = row['FG_hip_circ'] - row['hip_circ']
            result['FG_arm_ease'] = row['FG_arm_circ'] - row['arm_circ']
            result['FG_neck_ease'] = row['FG_neckline'] - row['neck_circ']
            result['FG_shoulder_ease'] = row['FG_shoulder_width'] - row['shoulder_width']
        else:
            result['FG_bust_ease'] = None
            result['FG_waist_ease'] = None
            result['FG_hip_ease'] = None
            result['FG_arm_ease'] = None
            result['FG_neck_ease'] = None
            result['FG_shoulder_ease'] = None
            # Not doing armhole ease because measurements were not consistently correctly taken
        # Apend values to the analyses list
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
    FG_bust_ease = [row['FG_bust_ease'] for row in analyses]
    FG_waist_ease = [row['FG_waist_ease'] for row in analyses]
    FG_hip_ease = [row['FG_hip_ease'] for row in analyses]
    FG_arm_ease = [row['FG_arm_ease'] for row in analyses]
    FG_neck_ease = [row['FG_neck_ease'] for row in analyses]
    FG_shoulder_ease = [row['FG_shoulder_ease'] for row in analyses]

    # Create a figure and a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Plot on each subplot
    axs[0, 0].plot(ids, efficiency_used, label='Efficiency - Used')  # Used vs Ideal Eff
    axs[0, 0].plot(ids, efficiency_ideal, label='Efficiency - Ideal')  
    axs[0, 0].set_title('Efficiency values for Workshop attendees', fontsize=14)
    axs[0, 0].set_xlabel('Identifiers', fontsize=12)
    axs[0, 0].set_ylabel('Efficiencies', fontsize=12)
    axs[0, 0].legend()

    axs[0, 1].plot(ids, cut_loss_area_used, label='Cut Loss Area - Used')  # Used vs Ideal Cut Loss Area
    axs[0, 1].plot(ids, cut_loss_area_ideal, label='Cut Loss Area - Ideal')  
    axs[0, 1].set_title('Cut Loss Area for Workshop attendees', fontsize=14)
    axs[0, 1].set_xlabel('Identifiers', fontsize=12)
    axs[0, 1].set_ylabel('Cut Loss Area (cm$^2$)', fontsize=12)
    axs[0, 1].legend()

    axs[1, 0].plot(ids, cut_loss_width_used, label='Cut Loss Width - Used')  # Used vs Ideal Cut Loss Width
    axs[1, 0].plot(ids, cut_loss_width_ideal, label='Cut Loss Width - Ideal')  
    axs[1, 0].set_title('Cut Loss Width for Workshop attendees', fontsize=14)
    axs[1, 0].set_xlabel('Identifiers', fontsize=12)
    axs[1, 0].set_ylabel('Cut Loss Width (cm)', fontsize=12)
    axs[1, 0].legend()

    axs[1, 1].plot(ids, bolt_width_used, label='Bolt Width - Used')  # Used vs Ideal Bolt Width
    axs[1, 1].plot(ids, bolt_width_ideal, label='Bolt Width - Ideal')  
    axs[1, 1].set_title('Bolt Width for Workshop attendees', fontsize=14)
    axs[1, 1].set_xlabel('Identifiers', fontsize=12)
    axs[1, 1].set_ylabel('Bolt Width (cm)', fontsize=12)
    axs[1, 1].legend()

    '''pyplot.plot(ids, efficiency_used)
    pyplot.plot(ids, efficiency_ideal)
    pyplot.xlabel('Identifiers')
    pyplot.ylabel('Efficiency')
    pyplot.title('Efficiency values for Workshop attendees')
    pyplot.legend(['Used', 'Ideal'])'''
    # Add some space between the plots
    plt.tight_layout()
    plt.savefig('Workshop_Plot.png')
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 10))

    # Function to mask and plot data, removes None values for unfinished participants
    def plot_with_mask(ax, x, y, label):
        mask = [val is not None for val in y]
        ax.plot([x[i] for i in range(len(x)) if mask[i]], 
                [y[i] for i in range(len(y)) if mask[i]],
                label=label, marker='o', ms=10)

    # Plot each line with masking
    plot_with_mask(ax, ids, FG_bust_ease, 'Bust Ease')
    plot_with_mask(ax, ids, FG_waist_ease, 'Waist Ease')
    plot_with_mask(ax, ids, FG_hip_ease, 'Hip Ease')
    plot_with_mask(ax, ids, FG_arm_ease, 'Arm Ease')
    plot_with_mask(ax, ids, FG_neck_ease, 'Neck Ease')
    plot_with_mask(ax, ids, FG_shoulder_ease, 'Shoulder Ease')
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
    ax.set_title('Finished Garment Ease for Workshop finishers', fontsize=18)
    ax.set_xlabel('Identifiers', fontsize=16)
    ax.set_ylabel('Ease', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.legend()

    plt.savefig('FG_Ease_Plot.png')

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
