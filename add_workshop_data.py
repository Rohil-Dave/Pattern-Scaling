#!/usr/bin/env python3
'''
This module is used to add the fabric cut loss metrics and
fabric efficiency metrics to the ZWS workshop data file
'''
__author__ = 'Rohil J Dave'
__email__ = 'rohil.dave20@imperial.ac.uk'

from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import ps_utils as psu

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
        psu.assign_ideal_values(result)

        # # Calculate and assign theoretical ease values for the garment based on the pattern
        # # Bodice: Straight "boxy" fit around torso means the theoretical ease for bodice circs equal to
        # # subtracting the body measurement and sew tolerance from the pattern width (driven by largest circ)
        # result['T_bust_ease']= row['pattern_width'] - row['sew_tolerance'] - row['bust_circ']
        # result['T_waist_ease'] = row['pattern_width'] - row['sew_tolerance'] - row['waist_circ']
        # # No theoretical hip ease if the shirt length is above the hip
        # if row['shirt_above_hip'] == 1:
        #     result['T_hip_ease'] = None
        # else:
        #     result['T_hip_ease'] = row['pattern_width'] - row['sew_tolerance'] - row['hip_circ']
        # # Arm: Multiply calculated pattern armhole_length by two to get sleeve circumference and
        # # subtract sew tolerance (2x 1cm), then subtract arm circ to get ease
        # result['T_arm_ease'] = ((2 * row['armhole_length']) - 2) - row['arm_circ']
        # # Shoulders: Take 2 halfs of the sleevehead curve approximated by straight line distance
        # # between the minimum point of the curve and where the curve meets the horizontal. Add twice
        # # the shoulder horizontal from the pattern and subtract the body shoulder width to get ease
        # result['T_shoulder_ease'] = (2 * math.dist([0,0], [row['sleevehead_radius'], row['sleevehead_depth']])) + (2 * ((row['pattern_width'] - (4 * row['collar_width']) - (4 * row['sleevehead_radius'])) / 4))


        # Calculate the ease for the finished garment, only for participants who finished
        if row['garment_finished'] == 1:
            result['FG_bust_ease'] = row['FG_bust_circ'] - row['bust_circ']
            result['FG_waist_ease'] = row['FG_waist_circ'] - row['waist_circ']
            result['FG_hip_ease'] = row['FG_hip_circ'] - row['hip_circ']
            result['FG_arm_ease'] = row['FG_arm_circ'] - row['arm_circ']
            result['FG_neck_ease'] = row['FG_neckline'] - row['neck_circ']
            result['FG_shoulder_ease'] = row['FG_shoulder_width'] - row['shoulder_width']

            result['fit_bust'] = row['likert_fit_bust']
            result['comfort_bust'] = row['likert_comfort_bust']
            result['fit_waist'] = row['likert_fit_waist']
            result['comfort_waist'] = row['likert_comfort_waist']
            result['fit_hip'] = row['likert_fit_hips']
            result['comfort_hip'] = row['likert_comfort_hips']
            result['fit_arm'] = row['likert_fit_arms']
            result['comfort_arm'] = row['likert_comfort_arms']
            result['fit_neck'] = row['likert_fit_neck']
            result['comfort_neck'] = row['likert_comfort_neck']
            result['fit_shoulder'] = row['likert_fit_shoulders']
            result['comfort_shoulder'] = row['likert_comfort_shoulders']
        else:
            result['FG_bust_ease'] = None
            result['FG_waist_ease'] = None
            result['FG_hip_ease'] = None
            result['FG_arm_ease'] = None
            result['FG_neck_ease'] = None
            result['FG_shoulder_ease'] = None
            # Not doing armhole ease because measurements were not consistently correctly taken

            result['fit_bust'] = None
            result['comfort_bust'] = None
            result['fit_waist'] = None
            result['comfort_waist'] = None
            result['fit_hip'] = None
            result['comfort_hip'] = None
            result['fit_arm'] = None
            result['comfort_arm'] = None
            result['fit_neck'] = None
            result['comfort_neck'] = None
            result['fit_shoulder'] = None
            result['comfort_shoulder'] = None
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

    # Bar width
    bar_width = 0.35

    # X positions
    r1 = np.arange(len(ids))
    r2 = [x + bar_width for x in r1]

    # Plot on each subplot
    axs[0, 0].bar(r1, efficiency_used, width=bar_width, edgecolor='grey', label='Efficiency - Used') # Used vs Ideal Eff
    axs[0, 0].bar(r2, efficiency_ideal, width=bar_width, edgecolor='grey', label='Efficiency - Ideal')
    axs[0, 0].set_title('Efficiency values for Workshop attendees', fontsize=14)
    axs[0, 0].set_xlabel('Identifiers', fontsize=12)
    axs[0, 0].set_ylabel('Efficiencies', fontsize=12)
    axs[0, 0].set_xticks([r + bar_width / 2 for r in range(len(ids))])
    axs[0, 0].set_xticklabels(ids)
    axs[0, 0].set_ylim(0.7, 1.03)
    axs[0, 0].legend(loc='upper right')

    axs[0, 1].scatter(ids, bolt_width_used, label='Bolt Width - Used')  # Used vs Ideal Bolt Width
    axs[0, 1].scatter(ids, bolt_width_ideal, label='Bolt Width - Ideal')
    # Adding vertical lines for the difference between used and ideal bolt width
    for i in range(len(ids)):
        axs[0, 1].plot([ids[i], ids[i]], [bolt_width_used[i], bolt_width_ideal[i]], color='gray', linestyle='--')
        difference = int(abs(bolt_width_used[i] - bolt_width_ideal[i]))
        axs[0, 1].annotate(f'Diff: {difference}', (ids[i], bolt_width_ideal[i]), textcoords="offset points", xytext=(0, -15), ha='center')
    axs[0, 1].set_title('Bolt Width for Workshop attendees', fontsize=14)
    axs[0, 1].set_xlabel('Identifiers', fontsize=12)
    axs[0, 1].set_ylabel('Bolt Width (cm)', fontsize=12)
    axs[0, 1].set_ylim(116, 152)
    axs[0, 1].legend(loc='lower right')

    axs[1, 0].bar(r1, cut_loss_width_used, width=bar_width, edgecolor='grey', label='Cut Loss Width - Used')  # Used vs Ideal Cut Loss Width
    axs[1, 0].bar(r2, cut_loss_width_ideal, width=bar_width, edgecolor='grey', label='Cut Loss Width - Ideal')
    axs[1, 0].set_title('Cut Loss Width for Workshop attendees', fontsize=14)
    axs[1, 0].set_xlabel('Identifiers', fontsize=12)
    axs[1, 0].set_ylabel('Cut Loss Width (cm)', fontsize=12)
    axs[1, 0].set_xticks([r + bar_width / 2 for r in range(len(ids))])
    axs[1, 0].set_xticklabels(ids)
    axs[1, 0].legend(loc='upper right')

    axs[1, 1].bar(r1, cut_loss_area_used, width=bar_width, edgecolor='grey', label='Cut Loss Area - Used')  # Used vs Ideal Cut Loss Area
    axs[1, 1].bar(r2, cut_loss_area_ideal, width=bar_width, edgecolor='grey', label='Cut Loss Area - Ideal')
    axs[1, 1].set_title('Cut Loss Area for Workshop attendees', fontsize=14)
    axs[1, 1].set_xlabel('Identifiers', fontsize=12)
    axs[1, 1].set_ylabel('Cut Loss Area (cm$^2$)', fontsize=12)
    axs[1, 1].set_xticks([r + bar_width / 2 for r in range(len(ids))])
    axs[1, 1].set_xticklabels(ids)
    axs[1, 1].legend(loc='upper right')

    # Add some space between the plots
    plt.tight_layout()
    plt.savefig('Workshop_Plot.png')
    plt.close()

    # ----------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(12, 10))

    # Function to mask and plot data, removes None values for unfinished participants
    def plot_with_mask(ax, x, y, label):
        mask = [val is not None for val in y]
        ax.scatter([x[i] for i in range(len(x)) if mask[i]],
                [y[i] for i in range(len(y)) if mask[i]],
                label=label, s=50)

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
    plt.close()

    # ----------------------------------------------------------------

    df = pd.DataFrame(analyses)

    # Filter out rows where garments were not finished
    df_finished = df.dropna(subset=['FG_bust_ease'])

    # Create subplots for fit ratings
    fig, axs = plt.subplots(3, 2, figsize=(15, 15))
    for i, area in enumerate(['bust', 'waist', 'hip', 'arm', 'neck', 'shoulder']):
        sns.regplot(x=f'FG_{area}_ease', y=f'fit_{area}', data=df_finished, ax=axs[i // 2, i % 2])
        axs[i // 2, i % 2].set_title(f'{area.capitalize()} Ease vs. Fit Rating')
        axs[i // 2, i % 2].set_xlabel(f'{area.capitalize()} Ease')
        axs[i // 2, i % 2].set_ylabel(f'{area.capitalize()} Fit Rating')
    plt.tight_layout()
    plt.savefig('fit_ratings.png')
    plt.close()

    # Create subplots for comfort ratings
    fig, axs = plt.subplots(3, 2, figsize=(15, 15))
    for i, area in enumerate(['bust', 'waist', 'hip', 'arm', 'neck', 'shoulder']):
        sns.regplot(x=f'FG_{area}_ease', y=f'comfort_{area}', data=df_finished, ax=axs[i // 2, i % 2])
        axs[i // 2, i % 2].set_title(f'{area.capitalize()} Ease vs. Comfort Rating')
        axs[i // 2, i % 2].set_xlabel(f'{area.capitalize()} Ease')
        axs[i // 2, i % 2].set_ylabel(f'{area.capitalize()} Comfort Rating')
    plt.tight_layout()
    plt.savefig('comfort_ratings.png')
    plt.close()

    # Correlation heatmap for fit ratings
    fit_columns = [f'fit_{area}' for area in ['bust', 'waist', 'hip', 'arm', 'neck', 'shoulder']]
    ease_columns = [f'FG_{area}_ease' for area in ['bust', 'waist', 'hip', 'arm', 'neck', 'shoulder']]
    fit_corr_matrix = df_finished[ease_columns + fit_columns].corr()

    plt.figure(figsize=(12, 8))
    sns.heatmap(fit_corr_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap between Ease and Fit Ratings')
    plt.savefig('corr_heat_ease_fit.png')
    plt.close()

    # Correlation heatmap for comfort ratings
    comfort_columns = [f'comfort_{area}' for area in ['bust', 'waist', 'hip', 'arm', 'neck', 'shoulder']]
    comfort_corr_matrix = df_finished[ease_columns + comfort_columns].corr()

    plt.figure(figsize=(12, 8))
    sns.heatmap(comfort_corr_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap between Ease and Comfort Ratings')
    plt.savefig('corr_heat_ease_comfort.png')
    plt.close()

def main():
    '''
    the main routine to analyze workshop data
    '''

    workshop_data = psu.read_data('./ZWSworkshopData.csv')
    analyses = analyze_data(workshop_data)
    analyses = psu.add_pocket(analyses)
    generate_plots(analyses)
    column_names = ['efficiency_used', 'efficiency_ideal', 'cut_loss_width_used',
        'cut_loss_area_used', 'cut_loss_width_ideal', 'cut_loss_area_ideal',
        'bolt_width_ideal', 'embellished_saved']
    psu.generate_box_plots(analyses, 'Workshop', column_names)

    psu.write_analyses('ZWSworkshopAnalysis.csv', analyses)

# Execute main function
if __name__ == "__main__":
    main()
