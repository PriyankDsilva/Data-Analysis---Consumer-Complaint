from tkinter import *
import tkinter as tk
from tkinter import ttk
import FetchData as FD
import Initialize
import os
import threading
import time
from tkinter import messagebox
import pandas as pd
import FirebirdDB
import datetime
import Initialize
#import DataAnalysis

# Global Variables
TIMER=''
UPDATE_FLAG=True
LOAD_STEP=''
# Fonts
NORM_FONT = ("Helvetica", 10)
CLOCK_FONT = ("Times", "15", "italic")

# Program Info
ABOUT_INFO = "In Progress !!!"

def SignUpFrame(root, photo):
    # Set Title for the Sign Up Frame
    root.title('Consumer Complaint Analysis - Login')

    # Menu Window for SignUp
    menu = Menu(root)
    root.config(menu=menu)
    subMenu = Menu(menu)
    menu.add_cascade(label='Menu', menu=subMenu)
    subMenu.add_command(label='About...', command=lambda: popupmsg(ABOUT_INFO))
    subMenu.add_separator()
    subMenu.add_command(label='Exit', command=root.quit)

    # BackGround Image for SignUp
    ImageLabel = Label(root, image=photo)
    ImageLabel.pack(fill=BOTH)

    # User and Password Frame
    UserPassFrame = Frame(root)
    UserPassFrame.pack()

    # Create Label and Entry
    UserLable = Label(UserPassFrame, text='User:')
    PassLabel = Label(UserPassFrame, text='Password:')
    UserEntry = Entry(UserPassFrame)
    PassEntry = Entry(UserPassFrame, show='*')

    # Display
    UserLable.grid(row=1, sticky=E)
    PassLabel.grid(row=2, sticky=E)
    UserEntry.grid(row=1, column=1)
    PassEntry.grid(row=2, column=1)

    # Login Button
    LoginButton = ttk.Button(UserPassFrame, text='Login',
                             command=lambda: Login(UserEntry.get(), PassEntry.get(), menu, UserPassFrame, ImageLabel,
                                                   status, root, photo))
    LoginButton.grid(row=4, column=1)

    # Status Bar
    status = Label(root, text='Consumer Complaint Analysis...', bd=1, relief=SUNKEN, anchor=E)
    status.pack(side=BOTTOM, fill=X)

# Authenticate User and Login
def Login(User, Password, menu, frame, image, lable, root, photo):
    if User == 'admin' and Password == 'admin':
        # Clear All Contents
        menu.destroy()
        frame.destroy()
        lable.destroy()
        image.destroy()
        MainPage(root, photo)
    else:
        messagebox.showinfo("Error !!!", 'Invalid User/Password !!!')

# Pop UP
def popupmsg(msg):
    popup = Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()

# Main Page of GUI
def MainPage(root, photo):
    root.title('Consumer Complaint Analysis - Main Page')
    MainPageFrame = Frame(root)
    MainPageFrame.pack(side=LEFT)

    # Side Image for MainPage
    ImageFrame = Frame(root)
    ImageFrame.pack(side=RIGHT)
    ImageLabel = Label(ImageFrame, image=photo)
    ImageLabel.pack(side=TOP)

    # Functions
    # Fetch/Update Data Button Function
    ###################################Fetch Data Starts####################################################
    def FetchData(root, ImageFrame, ImageLabel, photo, MainPageFrame,FetchDataButton,ViewLogButton):
        #Start the Fetching Process
        InitialParameters = Initialize.getParam()
        LoadFileName = InitialParameters[15]

        #Disable the Button and destroy the Image
        FetchDataButton.config(state=DISABLED)
        ViewLogButton.config(state=DISABLED)
        ImageLabel.destroy()

        #Create Top and Bottom Frame
        TopFetchFrame=Frame(ImageFrame)
        TopFetchFrame.pack(side=TOP)
        BottopFetchFrame=Frame(ImageFrame)
        BottopFetchFrame.pack(side=BOTTOM)
        #Label to Display Log with Scroll Bar

        #Function for Scroll Bar
        def ScrollLogFunc(event):
            FetchCanvas.configure(scrollregion=FetchCanvas.bbox("all"),height=370,width=700)

        #canvas to Implement Scroll Bar for Log
        FetchCanvas=Canvas(TopFetchFrame)
        CanvasFrame=Frame(FetchCanvas)
        ScrollLogY=Scrollbar(TopFetchFrame, orient="vertical",command=FetchCanvas.yview)
        FetchCanvas.configure(yscrollcommand=ScrollLogY.set)
        FetchCanvas.pack(side=LEFT)
        ScrollLogY.pack(side=RIGHT,fill=Y)
        FetchCanvas.create_window((0,0),window=CanvasFrame,anchor=NW)

        #Label to display the Log Details
        LogContentDisplay=Label(CanvasFrame,text='Loading Log Details . . ..',anchor=NW,justify=LEFT,wraplength=650)
        CanvasFrame.bind("<Configure>",ScrollLogFunc)
        LogContentDisplay.pack()

        #Function to Fetch Log Details from Log File - continuesly
        def DisplayLogContent():
            #global LogValue
            CurrentLogValue=''
            InitialParameters = Initialize.getParam()
            LogFileName = InitialParameters[14]
            try:
                LogFile = open(LogFileName, 'r')
            except Exception as e:
                #print('Log File Error : ',e)
                CurrentLogValue='Unable to Display Log.Please Wait . . .'
            else:
                CurrentLogValue = LogFile.read()
            LogContentDisplay.config(text=CurrentLogValue)
            LogContentDisplay.after(200,DisplayLogContent)
        #run the Fetch Log function
        DisplayLogContent()

        #Clear the Fetch Data Screen and revert to Default Main Page
        def DisplayLogClear(root, photo, ImageFrame, MainPageFrame):
            ImageFrame.destroy()
            MainPageFrame.destroy()
            MainPage(root, photo)

        #Button to Clear the Screen and revert back
        BackButton = ttk.Button(BottopFetchFrame, text='Back', width=20,
                                 command=lambda: DisplayLogClear(root, photo, ImageFrame, MainPageFrame))
        BackButton.pack(side=LEFT,padx=50)

        #Runthe Update Process using thread

        if os.path.isfile(LoadFileName) == True:
            popupmsg('Update Already in Progress !!!')
        else:
            Choice=messagebox.askquestion("Update", "Are You sure you want to update the Main DB Tables?", icon='warning')
            if Choice=='yes':
                threading.Thread(target=FD.main).start()
            else:
                DisplayLogClear(root, photo, ImageFrame, MainPageFrame)

    ###################################Fetch Data Ended####################################################

    ###################################View Log Starts####################################################
    def ViewLog(root, ImageFrame, ImageLabel, photo, MainPageFrame,ViewLogButton,FetchDataButton):
        #Disable the Button and destroy the Image
        ViewLogButton.config(state=DISABLED)
        FetchDataButton.config(state=DISABLED)
        ImageLabel.destroy()

        #Create Top and Bottom Frame
        TopViewFrame=Frame(ImageFrame)
        TopViewFrame.pack(side=TOP)
        BottopViewFrame=Frame(ImageFrame)
        BottopViewFrame.pack(side=BOTTOM)
        #Label to Display Log with Scroll Bar

        #Function for Scroll Bar
        def ScrollLogFunc(event):
            ViewCanvas.configure(scrollregion=ViewCanvas.bbox("all"),height=370,width=800)

        #canvas to Implement Scroll Bar for Log
        ViewCanvas=Canvas(TopViewFrame)
        CanvasFrame=Frame(ViewCanvas)
        ScrollLogY=Scrollbar(TopViewFrame, orient="vertical",command=ViewCanvas.yview)
        ViewCanvas.configure(yscrollcommand=ScrollLogY.set)
        ViewCanvas.pack(side=LEFT)
        ScrollLogY.pack(side=RIGHT,fill=Y)
        ViewCanvas.create_window((0,0),window=CanvasFrame,anchor=NW)

        #Label to display the Log Details
        ViewLogDisplay=Label(CanvasFrame,text='Please Select a Log Category.',anchor=NW,justify=LEFT,wraplength=700)
        CanvasFrame.bind("<Configure>",ScrollLogFunc)
        ViewLogDisplay.pack(side=BOTTOM)

        #DropDown Button For Archive Log
        var = StringVar()
        var.set('')
        InitialParameters=Initialize.getParam()
        LogPath=InitialParameters[19]
        #LogPath=r'C:\Users\Priyank\Desktop\MIS\Scripting Languages\DataAnalyst-Project(Python)\Coding\Logs'
        LogList=[]
        for filename in os.listdir(LogPath):
            #if filename.split('.')[-1]=='log' and filename.split('_')[0]=='DataUpdateLog':
            LogList.append(filename)
        def func(value):
            LogFile=LogPath +'\\' + str(value)
            Log = open(LogFile, 'r')
            LogValue = Log.read()
            ViewLogDisplay.config(text=LogValue)
            ChoiceLabel.config(text='Archived Process Logs -')

        ChoiceLabel=Label(CanvasFrame,text='LOGS !!!')
        ChoiceLabel.pack(side=LEFT)
        ChoiceDropDown = OptionMenu(CanvasFrame, var, *LogList, command=func)
        ChoiceDropDown.pack(side=RIGHT)

        #Function to Display the Logs based on selection
        #APi and Source file info from Log table
        def APILog(ChoiceLabel):
            ChoiceLabel.config(text='Source File and API Logs -')
            var.set('')
            APLDataFrame=FirebirdDB.DisplayAPILog()
            APLDataFrame['FileLen']=APLDataFrame.FileName.map(len)
            MaxLength=0
            for i in range(0,len(APLDataFrame)):
                if APLDataFrame.loc[i,'FileLen'] >MaxLength:
                    MaxLength=APLDataFrame.loc[i,'FileLen']

            for i in range(0,len(APLDataFrame)):
                APLDataFrame.loc[i,'FileName']=str(APLDataFrame.loc[i,'FileName']).ljust(MaxLength,'_')
                m,s=divmod(APLDataFrame.loc[i,'Duration'],60)
                h,m=divmod(m,60)
                DurationTime=str(int(h)).rjust(2,'0')+':'+str(int(m)).rjust(2,'0')+':'+str(int(s)).rjust(2,'0')
                APLDataFrame.loc[i,'Duration']=DurationTime
                #print(APLDataFrame.loc[i,'LoadStartDTTM'])
                APLDataFrame.loc[i,'LoadStartDTTM']=datetime.datetime.strptime(APLDataFrame.loc[i,'LoadStartDTTM'], "%Y-%m-%d %H:%M:%S.%f").strftime("%d %b %y %H:%M:%S")
                APLDataFrame.loc[i,'LoadStartDTTM']=str(APLDataFrame.loc[i,'LoadStartDTTM']).ljust(30,' ').upper()
                #print(datetime.datetime.strptime(APLDataFrame.loc[i,'LoadStartDTTM']),"%d/%m/%Y").strftime("%d%b%y"))
                APLDataFrame.loc[i,'LoadIndex']=str(int(APLDataFrame.loc[i,'LoadIndex']))
                APLDataFrame.loc[i,'LoadOrder']=str(int(APLDataFrame.loc[i,'LoadOrder']))
                APLDataFrame.loc[i,'RecordCount']=str(int(APLDataFrame.loc[i,'RecordCount']))

            ViewLogDisplay.config(text='--------------------------------------------------------------------------------'
                                       '-----------------------------------------------\n'
                                       'Index\tOrder\t'+
                                       'FileName'.ljust(MaxLength,'_')
                                       +'\tCount\tStartTime\t\tDuration\n'+
                                        '--------------------------------------------------------------------------------'
                                        '-----------------------------------------------\n'+
                                       APLDataFrame.to_csv(sep='\t',index=False,header=False,
                          columns=['LoadIndex','LoadOrder','FileName','RecordCount','LoadStartDTTM','Duration'])
                                  +'--------------------------------------------------------------------------------'
                                  '-----------------------------------------------')

        #Load Step info from Main Log
        def LoadStep(ChoiceLabel):
            ChoiceLabel.config(text='Load Step Logs -')
            var.set('')
            LoadStepDataFrame=FirebirdDB.DisplayLoadStepLog()
            LoadStepDataFrame['StatusLen']=LoadStepDataFrame.Status.map(len)
            MaxStatus=0

            for i in range(0,len(LoadStepDataFrame)):
                if LoadStepDataFrame.loc[i,'StatusLen'] > MaxStatus:
                    MaxStatus=LoadStepDataFrame.loc[i,'StatusLen']

            for i in range(0,len(LoadStepDataFrame)):
                LoadStepDataFrame.loc[i,'Status']=str(LoadStepDataFrame.loc[i,'Status']).ljust(MaxStatus,'_')
                LoadStepDataFrame.loc[i,'LoadIndex']=str(int(LoadStepDataFrame.loc[i,'LoadIndex']))
                LoadStepDataFrame.loc[i,'LoadOrder']=str(int(LoadStepDataFrame.loc[i,'LoadOrder']))
                LoadStepDataFrame.loc[i,'RecordCount']=str(int(LoadStepDataFrame.loc[i,'RecordCount']))
                LoadStepDataFrame.loc[i,'LoadStartDTTM']=datetime.datetime.strptime(LoadStepDataFrame.loc[i,'LoadStartDTTM'], "%Y-%m-%d %H:%M:%S.%f").strftime("%d %b %y %H:%M:%S")
                LoadStepDataFrame.loc[i,'LoadStartDTTM']=str(LoadStepDataFrame.loc[i,'LoadStartDTTM']).ljust(30,' ').upper()
                m,s=divmod(LoadStepDataFrame.loc[i,'Duration'],60)
                h,m=divmod(m,60)
                DurationTime=str(int(h)).rjust(2,'0')+':'+str(int(m)).rjust(2,'0')+':'+str(int(s)).rjust(2,'0')
                LoadStepDataFrame.loc[i,'Duration']=DurationTime

            ViewLogDisplay.config(text='--------------------------------------------------------------------------------'
                                       '----------------------------------------------------------\n'
                                       'Index\tOrder\t'+'Status'.ljust(MaxStatus,'_')+'\tCount\tStartTime\t\tDuration\n'+
                                        '--------------------------------------------------------------------------------'
                                        '----------------------------------------------------------\n'+
                                       LoadStepDataFrame.to_csv(sep='\t',index=False,header=False,
                          columns=['LoadIndex','LoadOrder','Status','RecordCount','LoadStartDTTM','Duration'])
                                  +'--------------------------------------------------------------------------------'
                                  '----------------------------------------------------------')

        #Display Log details from Archived files/Rejects
        def ProcessLog():
            ChoiceLabel.config(text='Archived Process Logs -')
            ViewLogDisplay.config(text='Please Select an Archive File !!!')
            var.set('')

        #Clear the View Log Screen and revert to Default Main Page
        def DisplayLogClear(root, photo, ImageFrame, MainPageFrame):
            ImageFrame.destroy()
            MainPageFrame.destroy()
            MainPage(root, photo)


        #Buttions to choose log type
        APILogButton = ttk.Button(BottopViewFrame, text='API Logs', width=20,
                                 command=lambda:APILog(ChoiceLabel))
        LoadStepButton = ttk.Button(BottopViewFrame, text='Load Step Logs', width=20,
                                 command=lambda:LoadStep(ChoiceLabel))
        ProcessLogButton = ttk.Button(BottopViewFrame, text='Process Logs/Rejects', width=20,
                                 command=ProcessLog)
        BackButton = ttk.Button(BottopViewFrame, text='Back', width=20,
                                 command=lambda: DisplayLogClear(root, photo, ImageFrame, MainPageFrame))

        #pack Buttons
        APILogButton.pack(side=LEFT,padx=20)
        LoadStepButton.pack(side=LEFT,padx=20)
        ProcessLogButton.pack(side=LEFT,padx=20)
        BackButton.pack(side=LEFT,padx=20)


    ###################################View Log Ended####################################################

    # Create Buttions to Perform Tasks
    FetchDataButton = ttk.Button(MainPageFrame, text='Fetch/Update Database', width=40,
                                 command=lambda: FetchData(root, ImageFrame, ImageLabel, photo, MainPageFrame,FetchDataButton,ViewLogButton))
    ViewLogButton = ttk.Button(MainPageFrame, text='View Log History', width=40,
                               command=lambda: ViewLog(root, ImageFrame, ImageLabel, photo, MainPageFrame,ViewLogButton,FetchDataButton))
    DataAnalystButton = ttk.Button(MainPageFrame, text='Data Analyst(Consumer Complaint)',
                                    #command=DataAnalysis.main,
                                    width=40)
    MainExitButton = ttk.Button(MainPageFrame, text='Exit', width=40, command=root.quit)

    SpaceLabel0 = Label(MainPageFrame, text='', height=3)
    SpaceLabel1 = Label(MainPageFrame, text='', height=3)
    SpaceLabel2 = Label(MainPageFrame, text='', height=3)
    SpaceLabel3 = Label(MainPageFrame, text='', height=3)
    SpaceLabel4 = Label(MainPageFrame, text='', height=3)

    #Clock
    clock = Label(MainPageFrame, font=CLOCK_FONT,anchor=W)
    clock.pack(side=TOP,fill=BOTH,expand=1)

    def tick():
        global TIMER
        #CurrTime = time.strftime('%H:%M:%S')
        CurrTime = time.strftime('%d %b %Y %X')
        if CurrTime != TIMER:
            Timer = CurrTime
            clock.config(text=CurrTime)
        clock.after(200, tick)
    #run Clock
    tick()

    # Display the Buttons on Main Page
    SpaceLabel0.pack()
    FetchDataButton.pack()
    SpaceLabel1.pack()
    ViewLogButton.pack()
    SpaceLabel2.pack()
    DataAnalystButton.pack()
    SpaceLabel3.pack()
    MainExitButton.pack()
    SpaceLabel4.pack()

    # Status Bar Functions
    def NormStatus(event):
        status.config(text='Consumer Complaint Analysis', anchor=NE)

    def FetchStatus(event):
        status.config(
            text='Fetch Consumer Complaint Data from http://data.consumerfinance.gov/ site and Update the Database Tables.'
            , anchor=NW, justify=LEFT, wraplength=280)

    def ViewLogStatus(event):
        status.config(
            text='View Log History of all the All Database updates from http://data.consumerfinance.gov/ site.'
            , anchor=NW, justify=LEFT, wraplength=280)

    def DataAnalystStatus(event):
        status.config(text='Click to Analyse in Detail the Comsumer Complaint Data ,fetch Reports and Visualize Data.'
                      , anchor=NW, justify=LEFT, wraplength=280)

    def ExitStatus(event):
        status.config(text='Exit the Consumer Complaint Analyst Program'
                      , anchor=NW, justify=LEFT, wraplength=280)

    #status Bar Bottom
    status = Label(MainPageFrame, text='Consumer Complaint Analysis', bd=1, relief=SUNKEN, anchor=NE, height=4,
                   width=40)
    status.pack(side=BOTTOM, fill=X)

    #Binding Status Functions
    FetchDataButton.bind('<Enter>', FetchStatus)
    FetchDataButton.bind('<Leave>', NormStatus)
    ViewLogButton.bind('<Enter>', ViewLogStatus)
    ViewLogButton.bind('<Leave>', NormStatus)
    DataAnalystButton.bind('<Enter>', DataAnalystStatus)
    DataAnalystButton.bind('<Leave>', NormStatus)
    MainExitButton.bind('<Enter>', ExitStatus)
    MainExitButton.bind('<Leave>', NormStatus)

def main():
    root = Tk()
    root.iconbitmap(default='ConsumerComplaintIcon.ico')
    # Image for Consumer Complaint
    photo = PhotoImage(file='ConsumerComplaint.png')
    SignUpFrame(root,photo)
    #MainPage(root, photo)
    root.mainloop()

main()
