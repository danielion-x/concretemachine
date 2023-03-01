import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress

pd.options.mode.chained_assignment = None  # default='warn'

class test_specimen:
    def __init__(self,file_name, specimen_name, radius):
        self.file_name = file_name
        self.specimen_name = specimen_name
        self.radius = radius
    def concreteAnalysis(self):
        ''' Takes an Excel file of inches vs kips and produces a graphical representation including
        a scatter plot, a rolling average, and a linear regression line. Also produces key metrics
        such as Young's Modulus and Ultimate Strength '''
        area = (self.radius ** 2) * np.pi
        concrete_df = pd.read_csv(self.file_name) #opens excel file
        concrete_dff = concrete_df[(concrete_df['kips'] >= 1) & (concrete_df['inch'] >= 0)] #new df with all > 0 kips and inch values
        row_max = concrete_dff['kips'].idxmax()

        concrete_dff['corrected disp'] = concrete_dff['inch'] - concrete_dff.iloc[0]['inch']
        concrete_dff['strain'] = (concrete_dff['corrected disp'] / self.radius).truncate(after=row_max)
        concrete_dff['stress'] = ((concrete_dff['kips'] * 1000) / area).truncate(after=row_max)
        val_max = concrete_dff['stress'].max()
        rounded_val_max = val_max.round(3)
        concrete_dff['rolling'] = concrete_dff['stress'].rolling(50).mean()
        reg_line = linregress(concrete_dff['strain'].head(5000), concrete_dff['stress'].head(5000))
        print(self.specimen_name + " Ultimate Strength: %f. Young's Modulus: %f" % (val_max, reg_line.slope))

        plt.figure(dpi=300)
        plt.plot(concrete_dff['strain'], concrete_dff['stress'], label='Structural Analysis of %s' % self.specimen_name)
        plt.plot(concrete_dff['strain'], reg_line.intercept + reg_line.slope * concrete_dff['strain'],
             label='Regression Line = %fx + %f with R^2 %f' % (reg_line.slope, reg_line.intercept, reg_line.rvalue))
        plt.plot(concrete_dff['strain'], concrete_dff['rolling'], label='Rolling Average')
        plt.title('Stress vs. Strain of %s with Ultimate Strength %f' % (self.specimen_name, rounded_val_max))
        plt.xlabel('Stress (in/in)')
        plt.ylabel('Strain (psi)')
        plt.ylim(0, val_max)
        plt.legend()
        plt.savefig('%s plot.png' % self.specimen_name, dpi=500)

Concrete =test_specimen('conc_mix_test.csv', 'Conc Test', 2)
Cob =test_specimen('cob_mix_test.csv', 'Cob Test', 3)

Concrete.concreteAnalysis()
Cob.concreteAnalysis()


