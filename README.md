# Battery data parser
This software parses battery data from txt files and uploads them to a MySQL database. 
The software also provides an analisys of data by showing calculated values, summary data, and plots. 

Data description: [data.md](./data.md)
# Requirements
Install Python 3.x

[Install tkinter](https://tkdocs.com/tutorial/install.html) (starting with Python 3.7, the binary installers available at python.org come with tkinter pre-installed)

`pip3 install mysql-connector-python`

`pip3 install matplotlib`

# Quick start
Insert the connection parameters to use your MySQL database in *db.config*. Use *db.config.example* as a template.
## Run
`python3 batterydatamanager.py`
## Build executable
Use [pyinnstaller](https://www.pyinstaller.org/):

`pip3 install pyinstaller`

Pyinstaller has problems with current matplotlib version, so:

`pip3 install matplotlib==3.2.2`

## Windows

Install [Visual C++ Redistributable for Visual Studio 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145)

`python -m PyInstaller batterydatamanager.py --onefile --windowed --clean --add-data db.config;.`

## MacOS

`python3 -m PyInstaller batterydatamanager.py --onefile --windowed --clean --add-data db.config:. --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl'`