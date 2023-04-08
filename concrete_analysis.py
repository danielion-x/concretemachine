import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress
import PySimpleGUI as sg

pd.options.mode.chained_assignment = None  # default='warn'

class test_specimen:
    def __init__(self,file_name, specimen_name, radius, sandpcnt, aggpcnt, waterpcnt, cementpcnt):
        self.file_name = file_name
        self.specimen_name = specimen_name
        self.radius = radius
        self.ultimate_strength = 0
        self.youngs_modulus = 0
        self.data_table = 0

    def concreteAnalysis(self):
        ''' Takes an Excel file of inches vs kips and produces a graphical representation including
        a scatter plot, a rolling average, and a linear regression line. Also produces key metrics
        such as Young's Modulus and Ultimate Strength '''
        area = (self.radius ** 2) * np.pi
        concrete_df = pd.read_csv(self.file_name) #opens CSV file
        concrete_dff = concrete_df[(concrete_df['kips'] >= 1) & (concrete_df['inch'] >= 0)] #new df with all > 0 kips and inch values
        row_max = concrete_dff['kips'].idxmax()

        concrete_dff['corrected disp'] = concrete_dff['inch'] - concrete_dff.iloc[0]['inch']
        concrete_dff['strain'] = (concrete_dff['corrected disp'] / self.radius).truncate(after=row_max)
        concrete_dff['stress'] = ((concrete_dff['kips'] * 1000) / area).truncate(after=row_max)
        self.ultimate_strength = concrete_dff['stress'].max()
        rounded_val_max = self.ultimate_strength.round(3)
        concrete_dff['rolling'] = concrete_dff['stress'].rolling(50).mean()
        reg_line = linregress(concrete_dff['strain'].head(5000), concrete_dff['stress'].head(5000))
        self.youngs_modulus = reg_line.slope
        print(self.specimen_name + " Ultimate Strength: %f. Young's Modulus: %f" % (self.ultimate_strength, self.youngs_modulus))
        self.data_table = concrete_dff

        plt.figure(dpi=300)
        plt.plot(concrete_dff['strain'], concrete_dff['stress'], label='Structural Analysis of %s' % self.specimen_name)
        plt.plot(concrete_dff['strain'], reg_line.intercept + self.youngs_modulus * concrete_dff['strain'],
             label='Regression Line = %fx + %f with R^2 %f' % (self.youngs_modulus, reg_line.intercept, reg_line.rvalue))
        plt.plot(concrete_dff['strain'], concrete_dff['rolling'], label='Rolling Average')
        plt.title('Stress vs. Strain of %s with Ultimate Strength %f' % (self.specimen_name, self.ultimate_strength))
        plt.xlabel('Strain (in/in)')
        plt.ylabel('Stress (psi)')
        plt.ylim(0, self.ultimate_strength)
        plt.legend()
        plt.savefig('%s plot.png' % self.specimen_name, dpi=500)


sg.theme('LightGrey') #sets theme of window
sg.set_options(font=('Arial Bold', 16))

setting_names = [
    [sg.Text('Units ')],
]

setting_choices = [
    [sg.Radio("Imperial", "gen", key='imperial', default=True), sg.Radio("Metric", "gen", key='metric', default=True)],
]

specimen_names = [
    #[sg.Image('flickr logo.png'), ],
    [sg.Text('Specimen Name ')],
    [sg.Text('Fine Aggregate (lbs)')],
    [sg.Text('Course Aggregate (lbs)')],
    [sg.Text('Cement (lbs) ')],
    [sg.Text('Water (lbs) ')],
    [sg.Text('Specimen Radius (in) ')],
    [sg.Text('Curing Time (days)')],
    [sg.OK(), sg.Cancel()]
          ]

value_inputs = [
    [sg.Input()],
    [sg.Input()],
    [sg.Input()],
    [sg.Input()],
    [sg.Input()],
    [sg.Input()],
    [sg.Input()],
    [sg.Text('')],
    [sg.Text('')],
]

layout = [
    [sg.Column(setting_names), sg.Column(setting_choices)],
    [sg.Column(specimen_names), sg.Column(value_inputs)],
    ]

window = sg.Window('Concrete Machine', layout) #creates a window based on the layout above with title and size
#shown
while True:
    event, values = window.read()
    filename = sg.popup_get_file('filename to open', no_window=True, file_types=(("CSV Files", "*.csv"),))

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    mix_name = values[0]
    fineagg_lbs = float(values[1])
    courseagg_lbs = float(values[2])
    cement_lbs = float(values[3])
    water_lbs = float(values[4])
    radius = float(values[5])
    curing_time =  float(values[6])

    total_weight = fineagg_lbs + courseagg_lbs + cement_lbs + water_lbs

    fineagg_pcnt = fineagg_lbs/total_weight
    courseagg_pcnt = courseagg_lbs/total_weight
    cement_pcnt = cement_lbs/total_weight
    water_pcnt = water_lbs/total_weight

    print('You entered ', mix_name)
    print('Your mix has a total weight of ', total_weight)
    print(filename)

    mix_name = test_specimen(filename, mix_name, radius, fineagg_pcnt, courseagg_pcnt, cement_pcnt, water_pcnt)
    mix_name.concreteAnalysis()


    
    window.close()






