import PySimpleGUI as sg

sg.theme('LightGrey') #sets theme of window
sg.set_options(font=('Arial Bold', 16))

sand_inputs = [
    #[sg.Image('flickr logo.png'), ],
    [sg.Text('Specimen Name '), sg.Input()],
    [sg.Text('Sand (lbs)'), sg.Input()],
    [sg.Text('Aggregate (lbs) '), sg.Input()],
    [sg.Text('Cement (lbs) '), sg.Input()],
    [sg.Text('Water (lbs) '), sg.Input()],
    [sg.OK(), sg.Cancel()]
          ]

layout = [
    [sg.Column(sand_inputs),]
    ]

window = sg.Window('Concrete Machine', layout) #creates a window based on the layout above with title and size
#shown
while True:
    event, values = window.read()
    filename = sg.popup_get_file('filename to open', no_window=True, file_types=(("CSV Files", "*.csv"),))
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    mix_name = values[0]
    sand_lbs = float(values[1])
    aggregate_lbs = float(values[2])
    cement_lbs = float(values[3])
    water_lbs = float(values[4])

    total_weight = sand_lbs + aggregate_lbs + cement_lbs + water_lbs

    sand_pcnt = sand_lbs/total_weight
    aggregate_pcnt = aggregate_lbs/total_weight
    cement_pcnt = cement_lbs/total_weight
    water_pcnt = water_lbs/total_weight

    print('You entered ', mix_name)
    print('Your mix has a total weight of ', total_weight)
    print(filename)



window.close()
