import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress
import PySimpleGUI as sg
import PyInstaller

pd.options.mode.chained_assignment = None  # default='warn'

class concrete_specimen:
    def __init__(self, file_name, specimen_name, radius, kips_column, inch_column, unit_type, kips_or_strain):
        self.file_name = file_name
        self.specimen_name = specimen_name
        self.radius = radius
        self.ultimate_strength = 0
        self.youngs_modulus = 0
        self.data_table = 0
        self.kips_or_strain = kips_or_strain
        #self.fine_aggregate = fineaggpcnt * 0.453592
        #self.coarse_aggregate_percent = coarseaggpcnt * 0.453592
        #self.water_percent = waterpcnt * 0.453592
        #self.cement_percent = cementpcnt * 0.453592
        #self.blast_furnace_slag = blast_fer_slg * 0.453592
        #self.fly_ash = flyash * 0.453592
        #self.super_plastisizer = superplast * 0.453592
        #self.age = age
        self.predictive_data_table = 0
        self.kips_column = kips_column-1
        self.inch_column = inch_column-1

        #if unit_type == "Metric":
            #self.unit_conversion_imperial2metric()

    '''
    def unit_conversion_metric2imperial(self):
        self.fine_aggregate = fineaggpcnt * 0.00220462 #grams to lbs
        self.coarse_aggregate_percent = coarseaggpcnt * 0.00220462 #grams to lbs
        self.water_percent = waterpcnt * 0.00220462 #grams to lbs'
        self.cement_percent = cementpcnt * 0.00220462 #grams to lbs'
        self.blast_furnace_slag = blast_fer_slg * 0.00220462 #grams to lbs'
        self.fly_ash = flyash * 0.00220462 #grams to lbs
        self.super_plastisizer = superplast * 0.00220462 #grams to lbs'
        self.radius = radius * 39.3701 #meters to inches'

    def unit_conversion_imperial2metric(self):
        self.fine_aggregate = fineaggpcnt * 453.592 #lbs to grams'
        self.coarse_aggregate_percent = coarseaggpcnt * 453.592 #lbs to grams'
        self.water_percent = waterpcnt * 453.592 #lbs to grams'
        self.cement_percent = cementpcnt * 453.592 #lbs to grams'
        self.blast_furnace_slag = blast_fer_slg * 453.592 #lbs to grams'
        self.fly_ash = flyash * 453.592 #lbs to grams'
        self.super_plastisizer = superplast * 453.592 #lbs to grams'
        self.radius = radius * 0.0254 #inches 2 meter'
    '''

    def concreteAnalysis(self):
        ''' Takes an Excel file of inches vs kips and produces a graphical representation including
            a scatter plot, a rolling average, and a linear regression line. Also produces key metrics
            such as Young's Modulus and Ultimate Strength '''

        file_extension = self.file_name[-4:]
        if file_extension == "xlsx":
            concrete_df = pd.read_excel(self.file_name)
        elif file_extension == ".csv":
            concrete_df = pd.read_csv(self.file_name)


        if self.kips_or_strain == 'Kips':
            area = (self.radius ** 2) * np.pi  # opens CSV file
            concrete_df.rename(columns={concrete_df.columns[self.inch_column]: 'inch'}, inplace=True)
            concrete_df.rename(columns={concrete_df.columns[self.kips_column]: 'kips'}, inplace=True)
            concrete_dft = concrete_df[['kips', 'inch']]
            concrete_dftt = concrete_dft.drop([0, 1])
            concrete_dftt['kips'] = pd.to_numeric(concrete_dftt['kips'])
            concrete_dftt['inch'] = pd.to_numeric(concrete_dftt['inch'])


            concrete_dff = concrete_dftt[
                (concrete_dftt['kips'] >= 0.5) & (concrete_dftt['inch'] >= 0)]  # new df with all > 0 kips and inch values
            row_max = concrete_dff['kips'].idxmax()


            concrete_dff['corrected disp'] = concrete_dff['inch'] - concrete_dff.iloc[0]['inch']
            concrete_dff['strain'] = (concrete_dff['corrected disp'] / self.radius).truncate(after=row_max)
            concrete_dff['stress'] = ((concrete_dff['kips'] * 1000) / area).truncate(after=row_max)
            self.ultimate_strength = concrete_dff['stress'].max()





        elif self.kips_or_strain == 'Strain':
            self.ultimate_strength = concrete_df.iloc[0]['Stress at Break (psi):']
            if file_extension == "xlsx":
                concrete_dft = pd.read_excel(self.file_name, skiprows=2)
            elif file_extension == ".csv":
                concrete_dft = pd.read_csv(self.file_name, skiprows=2)
            #concrete_dff = pd.DataFrame((concrete_dft['Stress (psi)', 'Long. Strain']), columns=['Stress', 'Strain'])
            concrete_dff = concrete_dft.rename(columns={'Stress (psi)': 'stress', 'Long. Strain': 'strain'})

        reg_line_head = int(3/7*len(concrete_dff))


        concrete_dff['rolling'] = concrete_dff['stress'].rolling(50).mean()
        reg_line = linregress(concrete_dff['strain'].head(reg_line_head), concrete_dff['stress'].head(reg_line_head))
        self.youngs_modulus = reg_line.slope
        print(self.specimen_name + " Ultimate Strength: %f. Young's Modulus: %f" % (
        self.ultimate_strength, self.youngs_modulus))
        self.data_table = concrete_dff

        plt.figure()
        plt.plot(concrete_dff['strain'], concrete_dff['stress'],
                     label='Structural Analysis of %s' % self.specimen_name)
        plt.plot(concrete_dff['strain'], reg_line.intercept + self.youngs_modulus * concrete_dff['strain'],
                     label='Regression Line = %fx + %f with R^2 %f' % (
                     self.youngs_modulus, reg_line.intercept, reg_line.rvalue))
        plt.plot(concrete_dff['strain'], concrete_dff['rolling'], label='Rolling Average')
        plt.title(
                'Stress vs. Strain of %s with Ultimate Strength %f' % (self.specimen_name, self.ultimate_strength))
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

class cob_specimen:
    def __init__(self, file_name, specimen_name, radius, inch_column, kips_column):
        self.file_name = file_name
        self.specimen_name = specimen_name
        self.inch_column = inch_column-1
        self.kips_column = kips_column-1
        self.radius = radius


    def cobAnalysis(self):
        ''' Takes an Excel file of inches vs kips and produces a graphical representation including
            a scatter plot, a rolling average, and a linear regression line. Also produces key metrics
            such as Young's Modulus and Ultimate Strength '''
        area = (self.radius ** 2) * np.pi
        cob_df = pd.read_excel(self.file_name)  # opens CSV file
        cob_df.rename(columns={cob_df.columns[self.inch_column]: 'inch'}, inplace=True)
        cob_df.rename(columns={cob_df.columns[self.kips_column]: 'kips'}, inplace=True)
        cob_dft = cob_df[['kips', 'inch']]
        cob_dftt = cob_dft.drop([0, 1])
        cob_dftt['kips'] = pd.to_numeric(cob_dftt['kips'])
        cob_dftt['inch'] = pd.to_numeric(cob_dftt['inch'])

        cob_dff = cob_dftt[
            (cob_dftt['kips'] >= 0.15) & (cob_dftt['inch'] >= 0)]  # new df with all > 0 kips and inch values
        row_max = cob_dff['kips'].idxmax()

        cob_dff['corrected disp'] = cob_dff['inch'] - cob_dff.iloc[0]['inch']
        cob_dff['strain'] = (cob_dff['corrected disp'] / self.radius).truncate(after=row_max)
        cob_dff['stress'] = ((cob_dff['kips'] * 1000) / area).truncate(after=row_max)
        self.ultimate_strength = cob_dff['stress'].max()
        cob_dff['rolling'] = cob_dff['stress'].rolling(50).mean()
        reg_line = linregress(cob_dff['strain'].head(5000), cob_dff['stress'].head(5000))
        self.youngs_modulus = reg_line.slope
        print(self.specimen_name + " Ultimate Strength: %f. Young's Modulus: %f" % (
        self.ultimate_strength, self.youngs_modulus))
        self.data_table = cob_dff

        plt.figure()
        plt.plot(cob_dff['strain'], cob_dff['stress'],
                     label='Structural Analysis of %s' % self.specimen_name)
        plt.plot(cob_dff['strain'], reg_line.intercept + self.youngs_modulus * cob_dff['strain'],
                     label='Regression Line = %fx + %f with R^2 %f' % (
                     self.youngs_modulus, reg_line.intercept, reg_line.rvalue))
        plt.plot(cob_dff['strain'], cob_dff['rolling'], label='Rolling Average')
        plt.title(
                'Stress vs. Strain of %s with Ultimate Strength %f' % (self.specimen_name, self.ultimate_strength))
        plt.xlabel('Strain (in/in)')
        plt.ylabel('Stress (psi)')
        plt.ylim(0, self.ultimate_strength)
        plt.legend()
        plt.show()
        plt.savefig('%s plot.png' % self.specimen_name, dpi=500)

class UTM_analysis:
    def __init__(self, file_name, specimen_name):
        self.file_name = file_name
        self.specimen_name = specimen_name
        self.radius = 0

    def specimenAnalysis(self):
        self.file_extension = self.file_name[-4:]

        if self.file_extension == "xlsx":
            self.concrete_df = pd.read_excel(self.file_name)
        elif self.file_extension == ".csv":
            self.concrete_df = pd.read_csv(self.file_name)

        self.radius = self.concrete_df.iloc[0]['Diameter (in):']/2
        self.ultimate_strength = self.concrete_df.iloc[0]['Stress at Break (psi):']

        if self.file_extension == "xlsx":
            self.concrete_dft = pd.read_excel(self.file_name, skiprows=2)
        elif self.file_extension == ".csv":
            self.concrete_dft = pd.read_csv(self.file_name, skiprows=2)


        self.concrete_dft['Corrected Strain'] = -1*(self.concrete_dft['Ram Position (in)'] - self.concrete_dft.iloc[0]['Ram Position (in)'])

        self.concrete_dff = self.concrete_dft.rename(columns={'Stress (psi)': 'stress', 'Corrected Strain': 'strain'})


        self.reg_line_head = int(4/7*len(self.concrete_dff))


        self.concrete_dff['rolling'] = self.concrete_dff['stress'].rolling(50).mean()
        reg_line = linregress(self.concrete_dff['strain'].head(self.reg_line_head), self.concrete_dff['stress'].head(self.reg_line_head))
        self.youngs_modulus = reg_line.slope
        print(self.specimen_name + " Ultimate Strength: %f. Young's Modulus: %f" % (
        self.ultimate_strength, self.youngs_modulus))
        self.data_table = self.concrete_dff

        plt.figure()
        plt.plot(self.concrete_dff['strain'], self.concrete_dff['stress'],
                     label='Structural Analysis of %s' % self.specimen_name)
        plt.plot(self.concrete_dff['strain'], reg_line.intercept + self.youngs_modulus * self.concrete_dff['strain'],
                     label='Regression Line = %fx + %f with R^2 %f' % (
                     self.youngs_modulus, reg_line.intercept, reg_line.rvalue))
        plt.plot(self.concrete_dff['strain'], self.concrete_dff['rolling'], label='Rolling Average')
        plt.title(
                'Stress vs. Strain of %s with Ultimate Strength %f' % (self.specimen_name, self.ultimate_strength))
        plt.xlabel('Strain (in/in)')
        plt.ylabel('Stress (psi)')
        plt.ylim(0, self.ultimate_strength)
        plt.legend()
        plt.show()
        plt.savefig('%s plot.png' % self.specimen_name, dpi=500)




'''
BEGIN GUI CODE
'''


#sg.theme('LightGrey') #sets theme of window
sg.set_options(font=('Arial', 16))

material_choices = ['Concrete', 'Cob', 'Other']


setting_choices = [
    #[sg.Text('File Name'), sg.Input(enable_events=True, key='-IN-',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    #[sg.Text('Current Units'), sg.Radio("Imperial", "gen", key='imperial', default=True), sg.Radio("Metric", "gen", key='metric', default=False)],
    [sg.Text('Desired Units'), sg.Radio("Imperial", "gen", key='imperial', default=True), sg.Radio("Metric", "gen", key='metric', default=False)],
    [sg.Combo(material_choices, expand_x=True, default_value=material_choices[0], key='-COMBO-'), sg.Button('Confirm', key='-CONFIRM-')]
]


home_screen = [
    #[sg.Image(filename='mame logo.png', expand_x=True)],
    [sg.Button(button_text="Specimen Analysis from Kips/Inch File", key='Kip/Inch')],
    [sg.Button(button_text="Specimen Analysis from Stress/Strain File", key='Stress/Strain')],
    [sg.Button(button_text='UTM Analysis', key='UTM')],
    [sg.Button(button_text="Predict Performance from Ingredients", key='Predict')],
]

specimen_type_concrete = [
    #[sg.Text('Kips Column #'), sg.Input(key='-KIPS COLUMN-'), sg.Text('Inch Column #'), sg.Input(key='-INCH COLUMN-')],
    [sg.Text('Specimen Name*        ', justification='left'), sg.Input(key='Specimen Name')],
    [sg.Text('Specimen Radius* (in) ', justification='left'), sg.Input(default_text='2', key='Rad')],
    #[sg.Text('Fine Aggregate (lbs)       ', justification='left'), sg.Input(key='Fine Agg')],
    #[sg.Text('Course Aggregate (lbs) ', justification='left'), sg.Input(key='Course Agg')],
    #[sg.Text('Cement (lbs)                 ', justification='left'), sg.Input(key='Cement')],
    #[sg.Text('Water (lbs)                     ', justification='left'), sg.Input(key='Water')],
    #[sg.Text('Fly Ash (lbs)                   ', justification='left'), sg.Input(default_text='0', key='Fly Ash')],
    #[sg.Text('Super Plasticizer (lbs)    ', justification='left'), sg.Input(default_text='0', key='Super')],
    #[sg.Text('Blast Furnace Slag (lbs) ', justification='left'), sg.Input(default_text='0', key='Blast Slag')],
    #[sg.Text('Curing Time (days)            ', justification='left'), sg.Input(default_text='28', key='Age')],
          ]


choices = [
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
]

specimen_type_cob = [
    [sg.Combo(material_choices, expand_x=True, default_value=material_choices[0], key='-COMBO-'), sg.Button('Confirm', key='-CONFIRM-')],
    [sg.Text('Specimen Name*     ', justification='left'), sg.Input(key='Specimen Name')],
    [sg.Text('Radius* (in)              ', justification='left'), sg.Input(key='Cob Radius', default_text='3')],
    #[sg.Text('Soil (lbs)   '), sg.Input(expand_x=True, key='Soil')],
    #[sg.Text('Sand (lbs)   '), sg.Input(expand_x=True, key='Sand')],
    #[sg.Text('Water (lbs)  '), sg.Input(expand_x=True, key='Water')],
    #[sg.Text('Straw (lbs)  '), sg.Input(expand_x=True, key='Straw')],
    [sg.Text('')]
]


specimen_type = specimen_type_concrete


concrete_layout = [
    #[sg.Image(filename='mame logo.png', expand_x=True)],
    [setting_choices],
    [specimen_type_concrete],
    [sg.Text('File Options', expand_x='true', justification='center', font=('Arial Bold', 16))],
    [sg.Text('File Name*'), sg.Input(key='-FILEBROWSE-',font=('Arial Bold', 12),expand_x=True, ), sg.FileBrowse()],
    [sg.Text('Kips Column #*         '), sg.Input(key='-KIPS COLUMN-', expand_x=True)],
    [sg.Text('Inch Column #*         '), sg.Input(key='-INCH COLUMN-', expand_x=True)],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
    ]

stressstrain_specimen =  [
    #[sg.Image(filename='mame logo.png', expand_x=True)],
    [sg.Text('Specimen Name*'), sg.Input(key='Specimen Name', default_text='New Mix')],
    [sg.Text('Radius*'), sg.Input(key='Radius')],
    [sg.Text('File Name*'), sg.Input(key='-FILEBROWSE-',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
]

cob_layout = [
    #[sg.Image(filename='mame logo.png', expand_x=True)],
    [specimen_type_cob],
    [sg.Text('File Name*'), sg.Input(key='-FILEBROWSE-',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    [sg.Text('Kips Column #*             '), sg.Input(key='-KIPS COLUMN-', expand_x=False)],
    [sg.Text('Inch Column #*             '), sg.Input(key='-INCH COLUMN-', expand_x=False)],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
    ]

utm_layout = [
    #[sg.Image(filename='mame logo.png', expand_x=True)],
    [sg.Text('Specimen Name*'), sg.Input(key='Specimen Name', default_text='New Mix')],
    [sg.Text('File Name*'), sg.Input(key='-FILEBROWSE-',font=('Arial Bold', 12),expand_x=True), sg.FileBrowse()],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
]

current_layout = home_screen

window = sg.Window('Concrete Machine', layout=current_layout, finalize=False) #creates a window based on the layout above with title and size
#shown



while True:
    event, values = window.read()

    if event == 'Kip/Inch':
        window.close()
        window = sg.Window('Concrete Machine', concrete_layout)
        current_layout = concrete_layout

    if event == 'Stress/Strain':
        window.close()
        window = sg.Window('Stress Strain Machine', stressstrain_specimen)
        current_layout = stressstrain_specimen

    if event == '-CONFIRM-':
        if values['-COMBO-'] == 'Cob':
            window.close()
            window = sg.Window('Cob Machine', cob_layout)
            current_layout = cob_layout

    if event == 'Predict':
        sg.popup_auto_close("Feature Coming Soon", title="Coming Soon")

    if event == 'UTM':
        window.close()
        window = sg.Window('UTM Data Analysis', utm_layout)
        current_layout = utm_layout

    elif event == '-OK-':
        if current_layout == concrete_layout:
            required_vals = ['Specimen Name', 'Rad', '-INCH COLUMN-', '-FILEBROWSE-', '-KIPS COLUMN-']

            error = 0

            for i in required_vals:
                if values[i] == '':
                    error += 1

            if error > 0:
                sg.popup_auto_close("Please Enter All Required Fields", title='Error')

            kips_col = int((values['-KIPS COLUMN-']))
            inch_col = int((values['-INCH COLUMN-']))
            filename = values['-FILEBROWSE-']
            specimen_name = values['Specimen Name']
            radius = int(values['Rad'])

            '''
            if error == 0:

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
                filename = values['-FILEBROWSE-']

                total_weight = fineagg_lbs + courseagg_lbs + cement_lbs + water_lbs


                if total_weight > 0:
                    fineaggpcnt = fineagg_lbs/total_weight
                    coarseaggpcnt = courseagg_lbs/total_weight
                    cementpcnt = cement_lbs/total_weight
                    waterpcnt = water_lbs/total_weight
                    blast_fer_slg = blast_fer_slg_lbs/total_weight
                    flyash = flyash_lbs/total_weight
                    superplast = superplasticizer_lbs/total_weight

                else:
                    fineaggpcnt = 0
                    coarseaggpcnt = 0
                    cementpcnt = 0
                    waterpcnt = 0
                    blast_fer_slg = 0
                    flyash = 0
                    superplast = 0
                '''
            if values['imperial'] == True:
                units = "Imperial"
            else:
                units = "Metric"

            mix_name = concrete_specimen(filename, specimen_name, radius, kips_col, inch_col, units, "Kips")

            mix_name_data = mix_name.concreteAnalysis()

            if event == sg.WIN_CLOSED:
                break

        elif current_layout == cob_layout:
            required_vals = ['Specimen Name', 'Cob Radius', '-INCH COLUMN-', '-FILEBROWSE-', '-KIPS COLUMN-']

            error = 0

            for i in required_vals:
                if values[i] == '':
                    error += 1

            if error > 0:
                sg.popup_auto_close("Please Enter All Required Fields", title='Error')

            if error == 0:
                specimen_name = values['Specimen Name']
                #soil = int(values['Soil'])
                #sand = int(values['Sand'])
                #straw = int(values['Straw'])
                #water = int(values['Water'])
                radius = int(values['Cob Radius'])
                inch_column = int(values['-INCH COLUMN-'])
                filename = values['-FILEBROWSE-']
                kips_column = int(values['-KIPS COLUMN-'])

                mix_name = cob_specimen(filename, specimen_name, radius, inch_column, kips_column)
                mix_name_data = mix_name.cobAnalysis()

            if event == sg.WIN_CLOSED:
                break

        elif current_layout == stressstrain_specimen:
            required_vals = ['Specimen Name', '-FILEBROWSE-']

            error = 0

            for i in required_vals:
                if values[i] == '':
                    error += 1

            if error > 0:
                sg.popup_auto_close("Please Enter All Required Fields", title='Error')

            if error == 0:
                specimen_name = values['Specimen Name']
                radius = 0
                inch_column = 0
                filename = values['-FILEBROWSE-']
                kips_column = 0

                units = "Imperial"

                mix_name = concrete_specimen(filename, specimen_name, radius, inch_column, kips_column, units, "Strain")
                mix_name_data = mix_name.concreteAnalysis()

            if event == sg.WIN_CLOSED:
                break

        elif current_layout == utm_layout:
            required_vals = ['Specimen Name', '-FILEBROWSE-']

            error = 0

            for i in required_vals:
                if values[i] == '':
                    error += 1

            if error > 0:
                sg.popup_auto_close("Please Enter All Required Fields", title='Error')

            if error == 0:
                specimen_name = values['Specimen Name']
                filename = values['-FILEBROWSE-']

                mix_name = UTM_analysis(filename, specimen_name)
                mix_name_data = mix_name.specimenAnalysis()

    elif event == sg.WIN_CLOSED: # if user closes window or clicks cancel
        break


