#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics of the 100 scan Mendeley data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import csv
import math
from matplotlib import pyplot as plt
from matplotlib import ticker

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
    pattern_width = max_bodice_circ + 25 + 6 # add 25cm for ease (fixed for now) and 6cm for seam
    return pattern_width

def calculate_pattern_height(row):
    '''
    Calculate the pattern height for a given scan, deriving center back neck height from
    half back center tape measure and waist height, substracting crotch height to get shirt length
    '''
    # Use the half back center tape measure, waist height, crotch height
    half_cb_tm = row['Half Back Center Tape Measure']
    waist_height = row['Waist Height']
    crotch_height = row['Crotch Height']
    # Step 1: Calculate shirt length
    raw_shirt_length = half_cb_tm + waist_height - crotch_height
    # Step 2: Round up to the nearest 0.5cm
    shirt_length = math.ceil(raw_shirt_length * 2) / 2
    # Step 3: Calculate pattern height with collar piece length and hem allowance
    pattern_height = shirt_length + 25 + 2.5 # add 6cm for hem and 2cm for collar piece
    return pattern_height

def analyze_data(scan_data):
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

        result['bolt_width_ideal'] = calculate_ideal_bolt_width(result['pattern_width'])
        result['cut_loss_width_ideal'] = result['bolt_width_ideal'] - result['pattern_width']
        result['cut_loss_area_ideal'] = result['cut_loss_width_ideal'] * result['pattern_height']
        result['efficiency_ideal'] = 1 - result['cut_loss_area_ideal'] \
            / (result['bolt_width_ideal'] * result['pattern_height'])
        analyses.append(result)

        analyses = sorted(analyses, key=lambda x : x['person_id'])

    return analyses

def generate_plots(analyses, scan_data):
    '''
    generate some plots of mendeley data analyses
    '''

    # make a list of the ids and calculated values
    ids = [row['person_id'] for row in analyses]
    efficiency_used = [row['efficiency_used'] for row in analyses]
    efficiency_ideal = [row['efficiency_ideal'] for row in analyses]
    cut_loss_width_used = [row['cut_loss_width_used'] for row in analyses]
    cut_loss_area_used = [row['cut_loss_area_used'] for row in analyses]
    cut_loss_width_ideal = [row['cut_loss_width_ideal'] for row in analyses]
    cut_loss_area_ideal = [row['cut_loss_area_ideal'] for row in analyses]
    bolt_width_used = [row['bolt_width_used'] for row in analyses]
    bolt_width_ideal = [row['bolt_width_ideal'] for row in analyses]

    # make list of the needed scan data
    abdomen_circ = [row['Abdomen Circum Tape Measure'] for row in scan_data]
    chestbust_circ = [row['Chest / Bust Circum Tape Measure'] for row in scan_data]
    hip_circ = [row['Hip Circum Tape Measure'] for row in scan_data]
    seat_circ = [row['Seat Circum Tape Measure'] for row in scan_data]
    stomach_circ = [row['Stomach Max Circum Tape Measure'] for row in scan_data]
    waist_circ = [row['Waist Circum Tape Measure'] for row in scan_data]
    height = [row['Height cm'] for row in scan_data]

    # Create a figure and a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Plot on each subplot
    axs[0, 0].plot(ids, efficiency_used, label='Efficiency - Used')  # Used vs Ideal Eff
    axs[0, 0].plot(ids, efficiency_ideal, label='Efficiency - Ideal')
    axs[0, 0].set_title('Efficiency values for Mendeley Participants', fontsize=14)
    axs[0, 0].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[0, 0].set_ylabel('Efficiencies', fontsize=12)
    axs[0, 0].legend()

    axs[0, 1].plot(ids, cut_loss_area_used, label='Cut Loss Area - Used')  # Used vs Ideal Cut Loss Area
    axs[0, 1].plot(ids, cut_loss_area_ideal, label='Cut Loss Area - Ideal')
    axs[0, 1].set_title('Cut Loss Area for Mendeley Participants', fontsize=14)
    axs[0, 1].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[0, 1].set_ylabel('Cut Loss Area (cm$^2$)', fontsize=12)
    axs[0, 1].legend()

    axs[1, 0].plot(ids, cut_loss_width_used, label='Cut Loss Width - Used')  # Used vs Ideal Cut Loss Width
    axs[1, 0].plot(ids, cut_loss_width_ideal, label='Cut Loss Width - Ideal')
    axs[1, 0].set_title('Cut Loss Width for Mendeley Participants', fontsize=14)
    axs[1, 0].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[1, 0].set_ylabel('Cut Loss Width (cm)', fontsize=12)
    axs[1, 0].legend()

    axs[1, 1].plot(ids, bolt_width_used, label='Bolt Width - Used')  # Used vs Ideal Bolt Width
    axs[1, 1].plot(ids, bolt_width_ideal, label='Bolt Width - Ideal')
    axs[1, 1].set_title('Bolt Width for Mendeley Participants', fontsize=14)
    axs[1, 1].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[1, 1].set_ylabel('Bolt Width (cm)', fontsize=12)
    axs[1, 1].legend()

    # Add some space between the plots
    plt.tight_layout()
    plt.savefig('Mendeley_Plot.png')
    plt.close()

   # ----------------------------------------------------------------

    fig, axs = plt.subplots(3, 2, figsize=(12, 10))

    axs[0, 0].scatter(abdomen_circ, efficiency_used) # Used Eff vs Ab Circ
    axs[0, 0].set_title('Efficiency(Used) vs Abdomen Circumference for Mendeley Participants') 
    axs[0, 0].set_xlabel('Abdomen Circumference (cm)')
    axs[0, 0].set_ylabel('Efficiencies')
    axs[0, 0].set_ylim([0.70, 1])
    #axs[0, 0].legend()

    axs[0, 1].scatter(chestbust_circ, efficiency_used) # Used Eff vs Chest/Bust Circ
    axs[0, 1].set_title('Efficiency(Used) vs Chest/Bust Circumference for Mendeley Participants') 
    axs[0, 1].set_xlabel('Chest/Bust Circumference (cm)')
    axs[0, 1].set_ylabel('Efficiencies')
    axs[0, 1].set_ylim([0.70, 1])
    #axs[0, 1].legend()

    axs[1, 0].scatter(hip_circ, efficiency_used) # Used Eff vs Hip Circ
    axs[1, 0].set_title('Efficiency(Used) vs Hip Circumference for Mendeley Participants')
    axs[1, 0].set_xlabel('Hip Circumference (cm)')
    axs[1, 0].set_ylabel('Efficiencies')
    axs[1, 0].set_ylim([0.70, 1])
    #axs[1, 0].legend()

    axs[1, 1].scatter(seat_circ, efficiency_used) # Used Eff vs Seat Circ
    axs[1, 1].set_title('Efficiency(Used) vs Seat Circumference for Mendeley Participants')
    axs[1, 1].set_xlabel('Seat Circumference (cm)')
    axs[1, 1].set_ylabel('Efficiencies')
    axs[1, 1].set_ylim([0.70, 1])
    #axs[1, 1].legend()

    axs[2, 0].scatter(stomach_circ, efficiency_used) # Used Eff vs Stomach Circ
    axs[2, 0].set_title('Efficiency(Used) vs Stomach Circumference for Mendeley Participants')
    axs[2, 0].set_xlabel('Stomach Circumference (cm)')
    axs[2, 0].set_ylabel('Efficiencies')
    axs[2, 0].set_ylim([0.70, 1])
    #axs[2, 0].legend()

    axs[2, 1].scatter(waist_circ, efficiency_used) # Used Eff vs Waist Circ
    axs[2, 1].set_title('Efficiency(Used) vs Waist Circumference for Mendeley Participants')
    axs[2, 1].set_xlabel('Waist Circumference (cm)')
    axs[2, 1].set_ylabel('Efficiencies')
    axs[2, 1].set_ylim([0.70, 1])
    #axs[2, 1].legend()

    plt.tight_layout()
    plt.savefig('Bodice_Circ_Comparison.png')
    plt.close()

    # ----------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(12, 10))

    ax.scatter(height, efficiency_used, color='red')
    ax.set_title('Efficiency(Used) vs Height for Mendeley Participants')
    ax.set_xlabel('Height (cm)')
    ax.set_ylabel('Efficiencies')
    ax.set_ylim([0.70, 1])
    #ax.legend()

    plt.tight_layout()
    plt.savefig('Height_Comparison.png')
    plt.close()

def generate_bar_graphs(analyses):
    '''
    generate bar graphs for pattern fit for various bolt widths. we will try
    6 different widths ranging from 110-160:10. for each width we will sort
    how many participants could get the clothing pattern fit the bolt, either
    regularly, or flipped. of the ones that do fit, see if there's enough for
    embellishment
    '''

    categories = ['Regular Layout', 'Flipped Layout', 'Embellished']
    colors = ['lightblue', 'teal', 'maroon']

    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    counter = 0
    for bolt_width in range(110, 170, 10):
        regular_fit = 0
        flipped_fit = 0
        embellished = 0
        for row in analyses:
            if row['pattern_width'] <= bolt_width:
                regular_fit += 1
                if bolt_width - row['pattern_width'] >= 11:
                    embellished += 1
            elif row['pattern_height'] <= bolt_width:
                flipped_fit += 1
                if bolt_width - row['pattern_height'] >= 11:
                    embellished += 1
        values = [regular_fit, flipped_fit, embellished]
        axs_x = counter % 3
        axs_y = int(counter / 3)
        axs[axs_x, axs_y].bar(categories, values, width=0.25, color=colors)
        axs[axs_x, axs_y].set_title('Distribution for Bolt Width: ' + str(bolt_width), fontsize=16)
        axs[axs_x, axs_y].set_xlabel('Categories', fontsize=14)
        axs[axs_x, axs_y].set_ylabel('Count', fontsize=14)
        axs[axs_x, axs_y].set_ylim([0,105])
        axs[axs_x, axs_y].yaxis.set_major_locator(ticker.MultipleLocator(10))
        # Remove y-axis tick labels
        axs[axs_x, axs_y].set_yticklabels([])
        
        # Create the bars and store them in the 'bars' variable
        bars = axs[axs_x, axs_y].bar(categories, values, width=0.25, color=colors)
        # Add counts on top of each bar
        for bar, value in zip(bars, values):
            axs[axs_x, axs_y].text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value), 
                                   ha='center', va='bottom')
        counter += 1

    # Add some space between the plots
    plt.tight_layout()
    plt.savefig('Mendeley_Bar.png')
    plt.close()

def add_pocket(analyses):
    '''
    Checks if there is enough cut loss to add a pocket. Determines pocket size based 
    on cut loss width. 
    
    Only considers pocket if pattern width is scaled to actual
    body measurements and not to the ideal bolt width i.e. actual_measure == 1

    We will set a constant finished pocket size of 10cm by 10cm for all users.
    For this, seam allowances of 0.5cm are added to the side and bottom edges of the pocket,
    and heam allowance of 2cm is added to the top edge of the pocket.
    The pocket pattern piece then has dimensions of 11cm by 12.5cm.
    '''
    for row in analyses:
        if row['cut_loss_width_used'] >= 11:
            row['pocket_possible'] = 'Yes'
        else:
            row['pocket_possible'] = 'No'
    return analyses

def main():
    '''
    the main routine to analyze 100 scan Mendeley data
    '''

    scan_data = read_mendeley_data()
    analyses = analyze_data(scan_data)
    analyses = add_pocket(analyses)
    generate_plots(analyses, scan_data)
    generate_bar_graphs(analyses)

    output_file = 'mendeleyScansAnalysis.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=analyses[0].keys())

        writer.writeheader()
        for row in analyses:
            writer.writerow(row)

# Execute main function
if __name__ == "__main__":
    main()
