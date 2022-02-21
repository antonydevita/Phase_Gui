# Introduction 
This project was focused on adding some more functionality to the phase analysis widget. I met and discussed some potential changes that could be made to the tool with some of its users. We found that adding the ability to import data directly from the API within the widget would be a significant improvement as it would make the tool much easier to use for large sets of data. 

# Getting Started
1.	Installation process
    - Simply download the files to the same directory and run phase_gui.py. From here it will launch the tool and you can use it. Zip files and their extracted components will also be downloaded to this directory.
2.	Software dependencies
    - Python and its libraries
3.	Latest releases
    - original version completed by Chris Ullmer with API functionality added by Antony Devita
4.	API references
    - reqFromAPI.py calls the public API to download burst data using the serial number and API key.

# Build and Test
This program was built entirely in python, and is relatively easy to read and make changes to. The GUI is done using tkinter, a standard python library, and numpy/matplotlib is responsible for much of the calculation done.



# Contribute
There are lots of features that the engineering teams have stated would be useful. One is the ability to flip the data 180 degrees by multiplying by -1. Shawn Davis has written code for that which I will include below.


# Shawn Davis' Flipdata code
from tkinter import Tk # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
import configparser
import pandas as pd
excel_path = filedialog.askopenfilename(title="Choose OG csv")

phase_stuff = pd.read_csv(excel_path)

flipdata = phase_stuff["Acceleration Time"][3:].astype(float)
flipdata = flipdata * -1
testy = phase_stuff
testy["Acceleration Time"][3:] = flipdata
filename = filedialog.askdirectory(title="Choose Save Location")
testy.to_csv(filename + "/testy.csv", index=False)