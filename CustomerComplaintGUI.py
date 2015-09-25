from tkinter import *
from tkinter import ttk
import FetchData as FD
import Initialize
import os
import threading
import time
from tkinter import messagebox

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
        popupmsg("Invalid User/Password !!!")


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
    def FetchData(root, ImageFrame, ImageLabel, photo, MainPageFrame,FetchDataButton):
        #Start the Fetching Process


        InitialParameters = Initialize.getParam()
        LoadFileName = InitialParameters[15]

        #Disable the Button and destroy the Image
        FetchDataButton.config(state=DISABLED)
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

        #canvas to Implement Scroll Bar
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
        #View Button to Get Details ....Removed as not required
        #ViewButton = ttk.Button(BottopFetchFrame, text='View Log', width=20,command=lambda: DisplayLogContent(LogContentDisplay))
        #ViewButton.pack(side=LEFT)


        #Function to Fetch Log Details from Log File
        def DisplayLogContent():
            #global LogValue
            CurrentLogValue=''
            InitialParameters = Initialize.getParam()
            LogFileName = InitialParameters[14]
            try:
                LogFile = open(LogFileName, 'r')
            except Exception as e:
                print('Log File in Use : ',e)
                time.sleep(3)
                count=0
                while count!=3:
                    try:
                        LogFile = open(LogFileName, 'r')
                        count=3
                    except Exception as e2:
                        print('Log File in Use : ',2)
                        count+=1
                        CurrentLogValue='Unable to Display Log.Please Wait . . .'
                    else:
                        CurrentLogValue = LogFile.read()
            else:
                        CurrentLogValue = LogFile.read()
            LogContentDisplay.config(text=CurrentLogValue)
            LogContentDisplay.after(200,DisplayLogContent)

        DisplayLogContent()

        #Clear the Fetch Data Screen and revert to Default Main Page
        def DisplayLogClear(root, photo, ImageFrame, MainPageFrame):
            ImageFrame.destroy()
            MainPageFrame.destroy()
            MainPage(root, photo)

        #Button to Clear the Screen and revert back
        ClearButton = ttk.Button(BottopFetchFrame, text='Back', width=20,
                                 command=lambda: DisplayLogClear(root, photo, ImageFrame, MainPageFrame))
        ClearButton.pack(side=LEFT,padx=50)


        #Runthe Update Process using thread
        if os.path.isfile(LoadFileName) == True:
            popupmsg('Update Already in Progress !!!')
        else:
            Choice=messagebox.askquestion("Update", "Are You sure you want to update the Main DB Tables?", icon='warning')
            if Choice=='yes':
                FDThread=threading.Thread(target=FD.main)
                FDThread.start()
            else:
                DisplayLogClear(root, photo, ImageFrame, MainPageFrame)

    # Create Buttions to Perform Tasks
    FetchDataButton = ttk.Button(MainPageFrame, text='Fetch/Update Database', width=40,
                                 command=lambda: FetchData(root, ImageFrame, ImageLabel, photo, MainPageFrame,FetchDataButton))
    ViewLogButton = ttk.Button(MainPageFrame, text='View Log History', width=40)
    DataAnalystButton = ttk.Button(MainPageFrame, text='Data Analyst(Consumer Complaint)', width=40)
    MainExitButton = ttk.Button(MainPageFrame, text='Exit', width=40, command=root.quit)

    SpaceLabel0 = Label(MainPageFrame, text='', height=3)
    SpaceLabel1 = Label(MainPageFrame, text='', height=3)
    SpaceLabel2 = Label(MainPageFrame, text='', height=3)
    SpaceLabel3 = Label(MainPageFrame, text='', height=3)
    SpaceLabel4 = Label(MainPageFrame, text='', height=3)

    ###Clock
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



    # Status Bar
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

    status = Label(MainPageFrame, text='Consumer Complaint Analysis', bd=1, relief=SUNKEN, anchor=NE, height=4,
                   width=40)
    status.pack(side=BOTTOM, fill=X)

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
    # Image for SignUp Background
    photo = PhotoImage(file='ConsumerComplaint.png')
    #SignUpFrame(root,photo)
    MainPage(root, photo)
    root.mainloop()


main()
