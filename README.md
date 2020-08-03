# Battery data parser
This software parses battery data from txt files and uploads them to a MySQL database. 
The software also provides an analisys of data by showing calculated values, summary data, and plots. 
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
Use [pyinnstaller](https://www.pyinstaller.org/)