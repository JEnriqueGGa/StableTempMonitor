StableTempMonitor - Versión 2.0

Description
StableTempMonitor is an interactive tool developed in Python to monitor and analyze temperature data over time. In this version, new functionalities have been added and several features have been improved to make the program easier to use and flexible.

Improvements in Version 2.0
Manual Data Entry: You can now manually enter data directly from the graphical interface, eliminating the need for external .txt files.
CSV File Support: Added the ability to process up to five CSV files, extracting and combining temperature data.
Greater Flexibility: The restriction that the first column of the .txt file had to be the time column was removed. Now, any column can represent any type of data.
Customizing Dashed Lines: You can configure the values ​​of the dashed lines on the graph, which represent temperature limits.
Improved Zoom and Move: The zoom and move functionalities on the graph have been improved to make it easier to explore the data.
Changing Column Names: Ability to change column names from the interface and save these changes in a JSON file.

Instructions for Use
Data Upload:

You can upload a .txt or CSV file to view temperature data.
Or, enter the data manually using the new data entry section in the interface.

Visualization and Personalization:

View data in an interactive graph with configurable zoom, pan, and dashed line options.
Change the column names as necessary and save the graph to an image (.png) file.
Save Settings:

Saves column names to a JSON file to reuse custom settings in the future.

Requirements
Python 3.x
Libraries: Tkinter, ttkbootstrap, Numpy, Matplotlib, Pandas (if you use CSV files).


Facility

Clone the repository
git clone https://github.com/tu_usuario/tu_repositorio.git

Install the dependencies:
pip install -r requirements.txt

Run the program
python StableTempMonitor.py
