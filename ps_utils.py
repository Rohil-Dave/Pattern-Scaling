#!/usr/bin/env python3
'''
Utilities for pattern scaling module
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

import csv
import numpy as np
import matplotlib.pyplot as plt

IMG_DIR = './images/'

def calculate_ideal_bolt_width(width):
    '''
    Calculate the ideal bolt width for a given pattern width on boundaries of 5cm
    '''
    return width if width % 5 == 0 else width + 5 - width % 5

def read_data(file_name):
    '''
    Read the data from the saved file, cast all numeric values correctly
    '''

    file_data = []
    with open(file_name, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            for key, value in row.items():
                try:
                    row[key] = float(value)
                except ValueError:
                    row[key] = value
            file_data.append(row)
    return file_data

def write_analyses(file_name, analyses):
    '''
    write out the analyses as a csv file, given the analyses data
    '''
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=analyses[0].keys())

        writer.writeheader()
        for row in analyses:
            writer.writerow(row)

def assign_ideal_values(result):
    '''
    compute and assign ideal values for a given set of measurements
    '''
    result['bolt_width_ideal'] = calculate_ideal_bolt_width(result['pattern_width'])
    result['cut_loss_width_ideal'] = result['bolt_width_ideal'] - result['pattern_width']
    result['cut_loss_area_ideal'] = result['cut_loss_width_ideal'] * result['pattern_height']
    result['efficiency_ideal'] = result['pattern_width'] / result['bolt_width_ideal']

def add_pocket(analyses, bolt_width=150, append=False):
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
        if append:
            row[f'embellished_saved_{bolt_width}'] = row['embellished_saved']
    return analyses

def compute_stats(analyses, column_name):
    '''
    compute the distribution statistics for a particular column in our analyses data
    '''
    values = [row[column_name] for row in analyses if column_name in row]
    mean = np.mean(values)
    median = np.median(values)
    std_dev = np.std(values)
    print(column_name, "Mean:", mean)
    print(column_name, "Median:", median)
    print(column_name, "Standard Deviation:", std_dev)
    return values

def generate_box_plots(analyses, data_set, column_names):
    ''''
    generate box plots for a few given columns of the data set
    print stats as well
    '''

    for (column_name, unit_type) in column_names:
        values = compute_stats(analyses, column_name)
        cap_name = capitalize_underscore_text(column_name)

        # Boxplot
        plt.boxplot(values, showmeans=True)
        #plt.title(f"{data_set} {column_name}")
        plt.ylabel(f'{data_set} {cap_name} {unit_type}', fontsize=12)
        plt.xlabel(cap_name, fontsize=12)
        plt.savefig(f"{IMG_DIR}{data_set}_{column_name}_Boxplot.png", dpi=600)
        plt.close()

        plt.hist(values, bins=10, alpha=0.5)
        #plt.title(f"{data_set} {column_name}")
        plt.ylabel(f'{data_set} {cap_name} Distribution', fontsize=12)
        plt.xlabel(cap_name, fontsize=12)
        plt.savefig(f"{IMG_DIR}{data_set}_{column_name}_Hist.png", dpi=600)
        plt.close()

def randomize_mendeley(instances=10):
    '''
    creates randomized instances from mendeley data. we only care about the columns we use in our
    analysis
    '''
    column_names = ['Scan Code', 'Abdomen Circum Tape Measure', 'Chest / Bust Circum Tape Measure',
        'Axilla Chest Circumference Tape Measure', 'Hip Circum Tape Measure', 'Waist Height', 
        'Seat Circum Tape Measure', 'Stomach Max Circum Tape Measure', 'Waist Circum Tape Measure',
        'Half Back Center Tape Measure', 'Crotch Height']
    
    # read the original file
    original_data = read_data('./mendeleyScansData.csv')

    for i in range(instances):
        instance_data = []
        for index in range(len(original_data)):
            result = {}
            for column_name in column_names:
                rand_index = np.random.randint(0, len(original_data))
                result[column_name] = original_data[rand_index][column_name]
            instance_data.append(result)
        write_analyses(f'mendeley_{i}_of_{instances}.csv', instance_data)

def capitalize_underscore_text(text):
    # Step 1: Split the text by underscores
    words = text.split('_')
    
    # Step 2: Capitalize each word
    capitalized_words = [word.capitalize() for word in words]
    
    # Step 3: Join the words back together
    capitalized_text = ' '.join(capitalized_words)
    
    return capitalized_words[-1]
    return capitalized_text

def generate_combo_box_plots(analyses, plot_header, column_names, unit_type):
    '''
    generate group box plots for the given columns
    '''
    vals_list = []
    col_labels = []
    for column_name in column_names:
        values = [row[column_name] for row in analyses if column_name in row]
        vals_list.append(values)
        col_labels.append(capitalize_underscore_text(column_name))
    plt.boxplot(vals_list, showmeans=True)
    #plt.title(plot_header)
    plt.ylabel(f'{plot_header} {unit_type}', fontsize=12)
    x_ticks = [x + 1 for x in range(len(column_names))]
    plt.xticks(x_ticks, labels=col_labels, fontsize=12)
    plt.savefig(f"{IMG_DIR}{plot_header}_Boxplot.png", dpi=600)
    plt.close()

def main():
    '''
    write out mendeley randomized files
    '''
    randomize_mendeley(10)

if __name__ == '__main__':
    main()
