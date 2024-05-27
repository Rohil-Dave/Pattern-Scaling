#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and 
fabric efficiency metrics of the 100 scan Mendeley data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import math
from matplotlib import pyplot as plt
from matplotlib import ticker
#from sklearn.linear_model import LinearRegression
import ps_utils as psu

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
    raw_max = max(abdomen_circ, axilla_circ, chestbust_circ, hip_circ, seat_circ, stomach_circ,
        waist_circ)
    # Step 2: Round up to the nearest 0.5cm
    max_bodice_circ = math.ceil(raw_max * 2) / 2
    # Step 3: Calculate the pattern width with ease and seam allowance
    pattern_width = max_bodice_circ + 25 + 6 # add 25cm for ease (fixed for now) and 6cm for seam
    return max_bodice_circ, pattern_width

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

def bolt_width_based_calculations(result, bolt_width=150):
    '''
    Set the bolt width (default 150, but could be anything from 100:170:10)
    Based on the bolt width compute cut loss and efficiency values
    '''
    result['bolt_width_used'] = bolt_width

    if result['pattern_width'] <= result['bolt_width_used']:
        # pattern width fits the bolt
        result['cut_loss_width_used'] = result['bolt_width_used'] - result['pattern_width']
        result['cut_loss_area_used'] = result['cut_loss_width_used'] * result['pattern_height']
        result['efficiency_used'] = result['pattern_width'] / result['bolt_width_used']
    elif result['pattern_height'] <= result['bolt_width_used']:
        # pattern height fits the bolt
        result['cut_loss_width_used'] = result['bolt_width_used'] - result['pattern_height']
        result['cut_loss_area_used'] = result['cut_loss_width_used'] * result['pattern_width']
        result['efficiency_used'] = result['pattern_height'] / result['bolt_width_used']
    else:
        # leave this as -1 for now
        result['cut_loss_width_used'] = -1
        result['cut_loss_area_used'] = -1
        result['efficiency_used'] = -1

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
        result['max_circ'], result['pattern_width'] = calculate_pattern_width(row)
        result['pattern_height'] = calculate_pattern_height(row) # fixed now for testing purposes
        bolt_width_based_calculations(result, 150)

        psu.assign_ideal_values(result)
        analyses.append(result)
        # Sort by scan code in ascending order
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
    # Used vs Ideal Eff
    axs[0, 0].scatter(ids, efficiency_used, s=1, label='Efficiency - Used')
    axs[0, 0].scatter(ids, efficiency_ideal, s=1, label='Efficiency - Ideal')
    axs[0, 0].set_title('Efficiency values for Mendeley Participants', fontsize=14)
    axs[0, 0].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[0, 0].set_ylabel('Efficiencies', fontsize=12)
    axs[0, 0].legend()

    # Used vs Ideal Cut Loss Area
    axs[0, 1].scatter(ids, cut_loss_area_used, s=1, label='Cut Loss Area - Used')
    axs[0, 1].scatter(ids, cut_loss_area_ideal, s=1, label='Cut Loss Area - Ideal')
    axs[0, 1].set_title('Cut Loss Area for Mendeley Participants', fontsize=14)
    axs[0, 1].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[0, 1].set_ylabel('Cut Loss Area (cm$^2$)', fontsize=12)
    axs[0, 1].legend()

    # Used vs Ideal Cut Loss Width
    axs[1, 0].scatter(ids, cut_loss_width_used, s=1, label='Cut Loss Width - Used')
    axs[1, 0].scatter(ids, cut_loss_width_ideal, s=1, label='Cut Loss Width - Ideal')
    axs[1, 0].set_title('Cut Loss Width for Mendeley Participants', fontsize=14)
    axs[1, 0].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[1, 0].set_ylabel('Cut Loss Width (cm)', fontsize=12)
    axs[1, 0].legend()

    # Used vs Ideal Bolt Width
    axs[1, 1].scatter(ids, bolt_width_used, s=1, label='Bolt Width - Used')
    axs[1, 1].scatter(ids, bolt_width_ideal, s=1, label='Bolt Width - Ideal')
    axs[1, 1].set_title('Bolt Width for Mendeley Participants', fontsize=14)
    axs[1, 1].set_xlabel('Participant Scan Codes (IDs)', fontsize=12)
    axs[1, 1].set_ylabel('Bolt Width (cm)', fontsize=12)
    axs[1, 1].legend()

    # Add some space between the plots
    plt.tight_layout()
    plt.savefig('Mendeley_Plot.png')
    plt.close()

    # ----------------------------------------------------------------

    fig, axs = plt.subplots(3, 2, figsize=(15, 10))

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
    ax.scatter(height, efficiency_ideal, color='blue')
    ax.set_title('Efficiency vs Height for Mendeley Participants')
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
        for cur_bar, value in zip(bars, values):
            axs[axs_x, axs_y].text(cur_bar.get_x() + cur_bar.get_width() / 2, cur_bar.get_height(),
                 str(value), ha='center', va='bottom')
        counter += 1

    # Add some space between the plots
    plt.tight_layout()
    plt.savefig('Mendeley_Bar.png')
    plt.close()

# def regression_analysis(analyses):
#     '''
#     Run regression analysis to see what is the impact of various values on efficiency
#     '''
#     X = [[row['max_circ'], row['bolt_width_used']] for row in analyses]
#     y = [row['efficiency_used'] for row in analyses]
#     # Instantiate the linear regression model
#     model = LinearRegression()

#     # Fit the model to the data
#     model.fit(X, y)

#     # Print the coefficients and intercept
#     print("Coefficients:", model.coef_)
#     print("Intercept:", model.intercept_)

def main():
    '''
    the main routine to analyze 100 scan Mendeley data
    '''
    scan_data = psu.read_data('./mendeleyScansData.csv')
    analyses = analyze_data(scan_data)
    analyses = psu.add_pocket(analyses)
    generate_plots(analyses, scan_data)
    generate_bar_graphs(analyses)
    column_names = ['efficiency_ideal', 'cut_loss_width_ideal', 'cut_loss_area_ideal',
        'bolt_width_ideal', 'max_circ']
    psu.generate_box_plots(analyses, 'Mendeley', column_names)
    #regression_analysis(analyses)
    psu.write_analyses('mendeleyScansAnalysis.csv', analyses)

    # see if a choice of bolt widths fits this population better
    for bolt_width in range(110, 170, 5):
        print(f'\nFor bolt width {bolt_width}')
        for result in analyses:
            bolt_width_based_calculations(result, bolt_width)
            analyses = psu.add_pocket(analyses)
        column_names = ['efficiency_used', 'cut_loss_area_used']
        psu.generate_box_plots(analyses, f'Mendeley_{bolt_width}', column_names)

# Execute main function
if __name__ == "__main__":
    main()
