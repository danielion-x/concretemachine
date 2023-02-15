import PySimpleGUI as sg
import os.path

sg.theme('LightGrey') #sets theme of window
sg.set_options(font=('Arial Bold', 16))

file_opener = [
    [sg.Text("Excel File"),
     sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
     sg.FolderBrowse(),],
    [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")],
]

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
    [sg.Column(sand_inputs),
    sg.VSeperator(),
    sg.Column(file_opener)],
    ]

window = sg.Window('Concrete Machine', layout) #creates a window based on the layout above with title and size
#shown
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    sand = values[1]
    aggregate = values[2]
    cement = values[3]
    water = values[4]
    print('You entered ', values[0])


window.close()
