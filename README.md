# Data-Analysis---Consumer-Complaint
Analyse consumer complaint data from https://data.consumerfinance.gov using python. Also use of tkinter libs to have a GUI front End for the program.  This solution will help vendors and customers to generate adhoc customized reports  as per their requirement. Reports will have various categories depending on data  requested and will be have target end users as both business and customers


Username and Password for the GUI is admin/admin

Requirement:
Python 3.4/Anaconda with python 3.4

FireBird:
Install Firebird Database and its python Library(fdb)
Create an account to be used for database operations using below command:
goto the installed dir using dos(cmd prmt):
gsec -user sysdba -pass masterkey -add <User Name> -pw <Password>

Additional Python Libraries used are as follows:
fdb
pandas
os
configparser
urllib
datetime
shutil
time
tkinter
pandastable
matplotlib
numpy
threading


Issue encountered with python Libraries:
As we were using tkinter ,we were unable to plot graphs using GUI because of some erroe due to matplotlib.
Solution - uninstalled matplotlib and pillow libraries and reinstall the core libraries from sourceforge
*Note-the .whl files for these libraries are uploaded in Download folder.
to install them just write pip install .whl file

Modules:
CreateDBStructure.py - The python code will create initial DB Structure required for the Project (one time run)
(make sure to create the username and password for Firebird DB and update the config.ini file)

ConsumerComplaintIcon.ico- Icon image for GUI

ConsumerComplaint.png - Image to display in GUI

config.ini - store the General Variable values in her.so that the main code dosent impact if anything need to be changed.

Initialize.py - Loads the Variables with initial value and store it in a List to be accesed from anywhere.

FirebirdDB.py - This python file has the functions associated with the DB operation for Firebird.

FetchData.py - The Python code will fetch data from the online API and load it into Main tables while maintaining the log of the entire process.

CustomerComplaintGUI.py - python code to Built GUI for Customer Complaint project.Currently has Login page(admin/admin) and Fetch/Update Data page which loads data from online API to main tables.other pages(View Log/Data Analisis) in Progress.

DataAnalyst.py-python code to provide a GUI and Data Analysis for the Data Fetched from the Consumer Complaint site.

Database - This Folder have working Log ,Trig file(to indicate that update is in progress),Firebird Database and Staging folder for Staging Activities

Database\Staging -This folder will be used to store downloaded csv files and reject file. 

Logs - This folder will be used to archive log and Reject Files if any
