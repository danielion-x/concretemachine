import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress

pd.options.mode.chained_assignment = None  # default='warn'

def concreteAnalysis(filename, spec_name, rad=2):
    ''' Takes an Excel file of inches vs kips and produces a graphical representation including
    a scatter plot, a rolling average, and a linear regression line. Also produces key metrics
    such as Young's Modulus and Ultimate Strength '''
    area = (rad ** 2) * np.pi
    concrete_df = pd.read_excel(filename)
    concrete_dff = concrete_df[(concrete_df['kips'] >= 0) & (concrete_df['inch'] >= 0)]
    row_max = concrete_dff['kips'].idxmax()

    concrete_dff['corrected disp'] = concrete_dff['inch'] - concrete_dff.iloc[0]['inch']
    concrete_dff['strain'] = (concrete_dff['corrected disp'] / rad).truncate(after=row_max)
    concrete_dff['stress'] = ((concrete_dff['kips'] * 1000) / area).truncate(after=row_max)
    val_max = concrete_dff['stress'].max()
    concrete_dff['rolling'] = concrete_dff['stress'].rolling(50).mean()
    reg_line = linregress(concrete_dff['strain'].head(10000), concrete_dff['stress'].head(10000))
    print(spec_name + " Ultimate Strength: %f. Young's Modulus: %f" % (val_max, reg_line.slope))

    plt.figure(dpi=300)
    plt.plot(concrete_dff['strain'], concrete_dff['stress'], label='Structural Analysis of %s' % spec_name)
    plt.plot(concrete_dff['strain'], reg_line.intercept + reg_line.slope * concrete_dff['strain'],
             label='Regression Line = %fx + %f with R^2 %f' % (reg_line.slope, reg_line.intercept, reg_line.rvalue))
    plt.plot(concrete_dff['strain'], concrete_dff['rolling'], label='Rolling Average')
    plt.title('Stress vs. Strain of %s' % spec_name)
    plt.xlabel('Stress (in/in)')
    plt.ylabel('Strain (psi)')
    plt.ylim(0, val_max)
    plt.legend()
    plt.savefig('%s plot.png' % spec_name, dpi=500)


concreteAnalysis("001 Mix1 KingBob.xlsx", 'Bob - Mix1')
concreteAnalysis("000 Mix1 Chrys.xlsx", 'Chrys - Mix1')
concreteAnalysis('002 Mix2 Benito.xlsx', 'Benito - Mix2')
concreteAnalysis('003 Mix2 Malo.xlsx', 'Malo - Mix2')
concreteAnalysis('004 Mix3 Chiffon.xlsx', 'Chiffon - Mix3')
concreteAnalysis('005 Mix3 LilSteela.xlsx', 'LilSteela - Mix3')
concreteAnalysis('006 Mix4 Girl.xlsx', 'Girl - Mix4')
concreteAnalysis('007 Mix4 Boy.xlsx', 'Boy - Mix4')
