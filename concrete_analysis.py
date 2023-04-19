import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from scipy.stats import linregress
import PySimpleGUI as sg

pd.options.mode.chained_assignment = None  # default='warn'

class test_specimen:
    def __init__(self, file_name, specimen_name, fineaggpcnt, coarseaggpcnt, waterpcnt, cementpcnt, blast_fer_slg, flyash, superplast, age):
        self.file_name = file_name
        self.specimen_name = specimen_name
        self.radius = 2
        self.ultimate_strength = 0
        self.youngs_modulus = 0
        self.data_table = 0
        self.fine_aggregate = fineaggpcnt * 0.453592
        self.coarse_aggregate_percent = coarseaggpcnt * 0.453592
        self.water_percent = waterpcnt * 0.453592
        self.cement_percent = cementpcnt * 0.453592
        self.blast_furnace_slag = blast_fer_slg * 0.453592
        self.fly_ash = flyash * 0.453592
        self.super_plastisizer = superplast * 0.453592
        self.age = age
        self.predictive_data_table = 0

    def concreteAnalysis(self):
        ''' Takes an Excel file of inches vs kips and produces a graphical representation including
        a scatter plot, a rolling average, and a linear regression line. Also produces key metrics
        such as Young's Modulus and Ultimate Strength '''
        area = (self.radius ** 2) * np.pi

        concrete_df = pd.read_excel(self.file_name) #opens CSV file

        if 'inches' in concrete_df:
            concrete_df['inch'] = concrete_df['inches']


        concrete_dff = concrete_df[(concrete_df['kips'] >= 0.1) & (concrete_df['inch'] >= 0)] #new df with all > 0 kips and inch values
        row_max = concrete_dff['kips'].idxmax()

        concrete_dff['corrected disp'] = concrete_dff['inch'] - concrete_dff.iloc[0]['inch']
        concrete_dff['strain'] = (concrete_dff['corrected disp'] / self.radius).truncate(after=row_max)
        concrete_dff['stress'] = ((concrete_dff['kips'] * 1000) / area).truncate(after=row_max)
        print('Max is %f' %concrete_dff['stress'].max())
        self.ultimate_strength = concrete_dff['stress'].max()
        concrete_dff['rolling'] = concrete_dff['stress'].rolling(50).mean()
        reg_line = linregress(concrete_dff['strain'].head(5000), concrete_dff['stress'].head(5000))
        self.youngs_modulus = reg_line.slope
        print(self.specimen_name + " Ultimate Strength: %f. Young's Modulus: %f" % (self.ultimate_strength, self.youngs_modulus))
        self.data_table = concrete_dff

        fig = plt.figure()
        plt.plot(concrete_dff['strain'], concrete_dff['stress'], label='Structural Analysis of %s' % self.specimen_name)
        plt.plot(concrete_dff['strain'], reg_line.intercept + self.youngs_modulus * concrete_dff['strain'],
        label='Regression Line = %fx + %f with R^2 %f' % (self.youngs_modulus, reg_line.intercept, reg_line.rvalue))
        plt.plot(concrete_dff['strain'], concrete_dff['rolling'], label='Rolling Average')
        plt.title('Stress vs. Strain of %s with Ultimate Strength %f' % (self.specimen_name, self.ultimate_strength))
        plt.xlabel('Strain (in/in)')
        plt.ylabel('Stress (psi)')
        plt.ylim(0, self.ultimate_strength)
        plt.legend()
        plt.show()
        plt.savefig('%s plot.png' % self.specimen_name, dpi=500)

        #draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)

        def predictiveAnalysis(self):
            analysis_data = {'Cement': [self.cement_percent], 'Blast Furnace Slag': [self.blast_furnace_slag],
                             'Fly Ash': [self.fly_ash], 'Water': [self.water_percent],
                             'Superplasticizer': [self.super_plastisizer], 'Coarse Aggregate': [self.aggregate_percent],
                             'Fine Aggregate': [self.sand_percent], 'Age': [self.age], 'Concrete compressive strength': [self.ultimate_stength]}
            predictive_df = pd.DataFrame(data=analysis_data)
            self.predictive_data_table = predictive_df


#sg.theme('LightGrey') #sets theme of window
sg.set_options(font=('Arial Bold', 16))

material_choices = ['Concrete', 'Cob', 'Other']


setting_choices = [
    #[sg.Text('File Name'), sg.Input(enable_events=True, key='-IN-',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    [sg.Text('Current Units'), sg.Radio("Imperial", "gen", key='imperial', default=True), sg.Radio("Metric", "gen", key='metric', default=False)],
    [sg.Text('Desired Units'), sg.Radio("Imperial", "gen", key='imperial', default=True), sg.Radio("Metric", "gen", key='metric', default=False)],
    [sg.Combo(material_choices, expand_x=True, default_value=material_choices[0], key='-COMBO-'), sg.Button('Confirm', key='-CONFIRM-')]
]


specimen_type_concrete = [
    [sg.Text('Specimen Name     ', justification='left'), sg.Input(key='Specimen Name')],
    [sg.Text('Fine Aggregate       ', justification='left'), sg.Input(key='Fine Agg')],
    [sg.Text('Course Aggregate  ', justification='left'), sg.Input(key='Course Agg')],
    [sg.Text('Cement                    ', justification='left'), sg.Input(key='Cement')],
    [sg.Text('Water                       ', justification='left'), sg.Input(key='Water')],
    [sg.Text('Fly Ash                    ', justification='left'), sg.Input(default_text='0', key='Fly Ash')],
    [sg.Text('Super Plasticizer    ', justification='left'), sg.Input(default_text='0', key='Super')],
    [sg.Text('Blast Furnace Slag ', justification='left'), sg.Input(default_text='0', key='Blast Slag')],
    [sg.Text('Specimen Radius   ', justification='left'), sg.Input(default_text='2', key='Rad')],
    [sg.Text('Curing Time            ', justification='left'), sg.Input(default_text='28', key='Age')],
          ]

choices = [
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
]

specimen_type_cob = [
    [sg.Combo(material_choices, expand_x=True, default_value=material_choices[0], key='-COMBO-'), sg.Button('Confirm', key='-CONFIRM-')],
    [sg.Text('Soil   '), sg.Input(expand_x=True, key='Dirt')],
    [sg.Text('Sand   '), sg.Input(expand_x=True, key='Sand')],
    [sg.Text('Water  '), sg.Input(expand_x=True, key='Water')],
    [sg.Text('Straw  '), sg.Input(expand_x=True, key='Straw')],
]


specimen_type = specimen_type_concrete


concrete_layout = [
    [sg.Image(filename='mame logo.png', expand_x=True)],
    [setting_choices],
    [specimen_type_concrete],
    [sg.Text('File Name'), sg.Input(key='_FILEBROWSE_',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
    ]

cob_layout = [
    [sg.Image(filename='mame logo.png', expand_x=True)],
    [specimen_type_cob],
    [sg.Text('File Name'), sg.Input(key='_FILEBROWSE_',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
    ]


window = sg.Window('Concrete Machine', concrete_layout, finalize=False) #creates a window based on the layout above with title and size
#shown

while True:
    event, values = window.read()

    if event == '-CONFIRM-':
        if values['-COMBO-'] == 'Cob':
            window.close()
            window = sg.Window('Cob Machine', cob_layout)

    elif event == '-OK-':
        specimen_name = values['Specimen Name']
        fineagg_lbs = int((values['Fine Agg']))
        courseagg_lbs = int((values['Course Agg']))
        cement_lbs = int((values['Cement']))
        water_lbs = int((values['Water']))
        flyash_lbs = int((values['Fly Ash']))
        superplasticizer_lbs = int((values['Super']))
        blast_fer_slg_lbs = int((values['Blast Slag']))
        radius = int(values['Rad'])
        age = int((values['Age']))
        filename = values['_FILEBROWSE_']

        total_weight = fineagg_lbs + courseagg_lbs + cement_lbs + water_lbs

        fineaggpcnt = fineagg_lbs/total_weight
        coarseaggpcnt = courseagg_lbs/total_weight
        cementpcnt = cement_lbs/total_weight
        waterpcnt = water_lbs/total_weight
        blast_fer_slg = blast_fer_slg_lbs/total_weight
        flyash = flyash_lbs/total_weight
        superplast = superplasticizer_lbs/total_weight

        mix_name = test_specimen(filename, specimen_name, fineaggpcnt, coarseaggpcnt, waterpcnt, cementpcnt, blast_fer_slg, flyash, superplast, age)
        mix_name_data = mix_name.concreteAnalysis()


    elif event == sg.WIN_CLOSED: # if user closes window or clicks cancel
        break




