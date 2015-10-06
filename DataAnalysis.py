import FirebirdDB
import Initialize
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import tkinter as tk
import FirebirdDB
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.finance import quotes_historical_yahoo_ochl
import datetime
import numpy as np
import matplotlib.dates as mdates
import  matplotlib.animation  as animation
from matplotlib import style
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter,DayLocator

matplotlib.use("TKAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
style.use('ggplot')


#Global Variables
REFRESH_COT_FLG=True
COT_RECEIVED_FLG=True
COT_SEND_FLG=True
COT_FILTER_TYPE='DAY'
PRODUCT_ISSUE_FLG='NONE'


#Function to get initial Data Frame from the System
def LoadDF():
    #DataFrame = FirebirdDB.GetViewData()
    #DataFrame = FirebirdDB.GetViewDataCustom()
    DataFrame = pd.read_csv('TempRecords.csv')
    #DataFrame = pd.read_csv('TempRecordsTotal.csv',low_memory=False)
    #DataFrame.to_csv('TempRecordsTotal.csv',index=False)
    DataFrame.DateReceived = pd.to_datetime(DataFrame.DateReceived)
    DataFrame.DateSentCompany = pd.to_datetime(DataFrame.DateSentCompany)

    return DataFrame

#MAin Analyst Page
def Analyst(root, photo, DataFrame):
    # Main Page Frame
    OuterMainPageFrame = Frame(root, width=500, height=800)
    MainPageFrame = Frame(OuterMainPageFrame, relief=GROOVE, borderwidth=2)
    Label(OuterMainPageFrame, text='CATEGORIES').pack(side=TOP,anchor=NW)
    MainPageFrame.pack(side=BOTTOM)

    # Filter Frame
    FilterFrame = Frame(root,relief=GROOVE, borderwidth=2)
    FilterFrame.pack(side=TOP)
    OuterMainPageFrame.pack(side=LEFT)

    #Seperate Filter Frame for Year, Product,Company and State
    YearFrame=Frame(FilterFrame)
    YearFrame.pack(side=LEFT)
    ProductFrame=Frame(FilterFrame)
    ProductFrame.pack(side=LEFT)
    CompanyFrame=Frame(FilterFrame)
    CompanyFrame.pack(side=LEFT)
    StateFrame=Frame(FilterFrame)
    StateFrame.pack(side=LEFT)
    ResetFrame=Frame(FilterFrame)
    ResetFrame.pack(side=LEFT)

    #Labels for Filters
    YearLabel=Label(YearFrame,text='Year Filter')
    ProductLabel=Label(ProductFrame,text='Product Filter')
    CompanyLabel=Label(CompanyFrame,text='Company Filter')
    StateLabel=Label(StateFrame,text='State Filter')
    YearLabel.pack(side=TOP)
    ProductLabel.pack(side=TOP)
    CompanyLabel.pack(side=TOP)
    StateLabel.pack(side=TOP)


    # Image Frame to display basic Image and Plot Graphs
    ImageFrame = Frame(root,relief=GROOVE, borderwidth=2)
    ImageFrame.pack(side=RIGHT)
    ImageLabel = Label(ImageFrame, image=photo)
    ImageLabel.pack(side=BOTTOM)

    #Filters Code
    year=StringVar(value=tuple(pd.unique(DataFrame.DateReceived.dt.year)))
    product=StringVar(value=tuple(pd.unique(DataFrame.Product)))
    company=StringVar(value=tuple(pd.unique(DataFrame.Company)))
    state=StringVar(value=tuple(pd.unique(DataFrame.State)))

    #Create a Filtered DF
    global FilteredDF
    FilteredDF=DataFrame

    #Function to Refresh the DataFrame
    def RefreshDF(DF):
        YearList = pd.unique(DF.DateReceived.dt.year)
        ProductList = pd.unique(DF.Product)
        CompanyList = pd.unique(DF.Company)
        StateList = pd.unique(DF.State)

        year.set(tuple(YearList))
        product.set(tuple(ProductList))
        company.set(tuple(CompanyList))
        state.set(tuple(StateList))
        global FilteredDF
        FilteredDF=DF

        #Set COT Flag
        global REFRESH_COT_FLG,PRODUCT_ISSUE_FLG
        REFRESH_COT_FLG=True
        #PRODUCT_ISSUE_FLG='NONE'



    #Filter Buttons
    YearDropDown = Listbox(YearFrame,listvariable=year,selectmode=MULTIPLE,height=5)
    YearDropDown.pack()
    ProductDropDown = Listbox(ProductFrame,listvariable=product,selectmode=MULTIPLE,height=5)
    ProductDropDown.pack()
    CompanyDropDown = Listbox(CompanyFrame,listvariable=company,selectmode=MULTIPLE,height=5)
    CompanyDropDown.pack()
    StateDropDown = Listbox(StateFrame,listvariable=state,selectmode=MULTIPLE,height=5)
    StateDropDown.pack()

    #Functions for Filters Year
    def YearFunc():
        NewYearList=[]
        for i in YearDropDown.curselection():
            NewYearList.append(YearDropDown.get(i))
        if not NewYearList:
            messagebox.showinfo("Error !!!", 'Value not Selected')
        else:
            CurrentProduct=list(ProductDropDown.get(0,END))
            CurrentCompany=list(CompanyDropDown.get(0,END))
            CurrentState=list(StateDropDown.get(0,END))

            RefreshDF(DataFrame[ (DataFrame.DateReceived.dt.year.isin(list(map(int, NewYearList)))) &
                                  (DataFrame.Product.isin(CurrentProduct)) &
                                  (DataFrame.Company.isin(CurrentCompany)) &
                                  (DataFrame.State.isin(CurrentState)) ])


    #Functions for Filters Product
    def ProductFunc():
        NewProductList=[]
        for i in ProductDropDown.curselection():
            NewProductList.append(ProductDropDown.get(i))
        if not NewProductList:
            messagebox.showinfo("Error !!!", 'Value not Selected')
        else:
            CurrentYear=list(YearDropDown.get(0,END))
            CurrentCompany=list(CompanyDropDown.get(0,END))
            CurrentState=list(StateDropDown.get(0,END))

            RefreshDF(DataFrame[ (DataFrame.DateReceived.dt.year.isin(list(map(int, CurrentYear)))) &
                                  (DataFrame.Product.isin(NewProductList)) &
                                  (DataFrame.Company.isin(CurrentCompany)) &
                                  (DataFrame.State.isin(CurrentState)) ])


    #Functions for Filters Company
    def CompanyFunc():
        NewCompanyList=[]
        for i in CompanyDropDown.curselection():
            NewCompanyList.append(CompanyDropDown.get(i))
        if not NewCompanyList:
            messagebox.showinfo("Error !!!", 'Value not Selected')
        else:
            CurrentYear=list(YearDropDown.get(0,END))
            CurrentProduct=list(ProductDropDown.get(0,END))
            CurrentState=list(StateDropDown.get(0,END))

            RefreshDF(DataFrame[ (DataFrame.DateReceived.dt.year.isin(list(map(int, CurrentYear)))) &
                                  (DataFrame.Product.isin(CurrentProduct)) &
                                  (DataFrame.Company.isin(NewCompanyList)) &
                                  (DataFrame.State.isin(CurrentState)) ])

    #Functions for Filters State
    def StateFunc():
        NewStateList=[]
        for i in StateDropDown.curselection():
            NewStateList.append(StateDropDown.get(i))
        if not NewStateList:
            messagebox.showinfo("Error !!!", 'Value not Selected')
        else:
            CurrentYear=list(YearDropDown.get(0,END))
            CurrentProduct=list(ProductDropDown.get(0,END))
            CurrentCompany=list(CompanyDropDown.get(0,END))

            RefreshDF(DataFrame[ (DataFrame.DateReceived.dt.year.isin(list(map(int, CurrentYear)))) &
                                  (DataFrame.Product.isin(CurrentProduct)) &
                                  (DataFrame.Company.isin(CurrentCompany)) &
                                  (DataFrame.State.isin(NewStateList)) ])


    #Apply Buttons
    YearButton=ttk.Button(YearFrame,text='Apply',command=YearFunc)
    ProductButton=ttk.Button(ProductFrame,text='Apply',command=ProductFunc)
    CompanyButton=ttk.Button(CompanyFrame,text='Apply',command=CompanyFunc)
    StateButton=ttk.Button(StateFrame,text='Apply',command=StateFunc)
    ResetButton=ttk.Button(ResetFrame,text='Reset',command=lambda:RefreshDF(DataFrame))
    YearButton.pack(side=BOTTOM)
    ProductButton.pack(side=BOTTOM)
    CompanyButton.pack(side=BOTTOM)
    StateButton.pack(side=BOTTOM)
    ResetButton.pack(side=BOTTOM)

    #Function to Plot Graph for Complaints over Time
################################################## BEGIN ###############################################################
    def ComplaintsOT(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton):
        global REFRESH_COT_FLG
        REFRESH_COT_FLG=True
        ComplaintsOTButton.config(state=DISABLED)
        ProductIssueButton.config(state=DISABLED)
        ImageLabel.destroy()

        #frame to select options
        OptionFrame=Frame(ImageFrame)
        OptionFrame.pack(side=TOP)

        var=StringVar(value='Both')
        COTChoices=['Complaints Received Over Time','Complaints Sent Over Time','Both']

        #function to select te recieved or sent lines
        def COTfunc(value):
            global COT_RECEIVED_FLG,COT_SEND_FLG,REFRESH_COT_FLG
            if value=='Complaints Sent Over Time':
                COT_RECEIVED_FLG=True
                COT_SEND_FLG=False
            elif value=='Complaints Received Over Time':
                COT_RECEIVED_FLG=False
                COT_SEND_FLG=True
            else:
                COT_RECEIVED_FLG=True
                COT_SEND_FLG=True
            REFRESH_COT_FLG=True

        #Drop down buttons
        COTReciveSentChoice=OptionMenu(OptionFrame,var,*COTChoices,command=COTfunc)
        COTReciveSentChoice.pack(side=LEFT)

        #Space label
        SpaceLabel5=Label(OptionFrame,text=':Select Legend         Select Filter Type:')
        SpaceLabel5.pack(side=LEFT)

        #function to select the formats like day ,month and year
        def COTFilterfunc(value):
            global COT_FILTER_TYPE,REFRESH_COT_FLG
            if value=='Day':
                COT_FILTER_TYPE='DAY'
            elif value=='Month':
                COT_FILTER_TYPE='MONTH'
            elif value=='Year':
                COT_FILTER_TYPE='YEAR'
            REFRESH_COT_FLG=True

        #Drop down button
        var2=StringVar(value='Day')
        COTFilterChoices=['Day','Month','Year']
        COTReciveSentChoice=OptionMenu(OptionFrame,var2,*COTFilterChoices,command=COTFilterfunc)
        COTReciveSentChoice.pack(side=RIGHT)

        #Figure and SubPlot
        #f = Figure(figsize=(5, 5), dpi=100)
        f = Figure()
        ax1 = f.add_subplot(111)

        #Function to Refresh Values
        def COTAnimate(i):
            global REFRESH_COT_FLG
            if REFRESH_COT_FLG is True:

                global FilteredDF
                ax1.clear()

                global COT_FILTER_TYPE
                #code for date format
                if COT_FILTER_TYPE=='DAY':
                    DF_1=FilteredDF.ComplaintId.groupby([FilteredDF.DateReceived]).count()
                    DF_2=FilteredDF.ComplaintId.groupby([FilteredDF.DateSentCompany]).count()

                    PlotDate1=DF_1.index.values
                    PlotData1=DF_1
                    PlotDate2=DF_2.index.values
                    PlotData2=DF_2
                #code for month format
                if COT_FILTER_TYPE=='MONTH':
                    DF_1=FilteredDF.ComplaintId.groupby([FilteredDF.DateReceived.dt.year,FilteredDF.DateReceived.dt.month]).count()
                    DF_2=FilteredDF.ComplaintId.groupby([FilteredDF.DateSentCompany.dt.year,FilteredDF.DateSentCompany.dt.month]).count()
                    DF1Date=[]
                    DF2Date=[]

                    for MonthYear in DF_1.index.values:
                        Date1=datetime.datetime.strptime(str(list(MonthYear)[0])+'-'+str(list(MonthYear)[1]).rjust(2,'0')+'-01','%Y-%m-%d')
                        DF1Date.append(Date1)
                    for MonthYear in DF_2.index.values:
                        Date2=datetime.datetime.strptime(str(list(MonthYear)[0])+'-'+str(list(MonthYear)[1]).rjust(2,'0')+'-01','%Y-%m-%d')
                        DF2Date.append(Date2)

                    DF1Date=pd.DataFrame(DF1Date,columns=['DateGroup'])
                    DF2Date=pd.DataFrame(DF2Date,columns=['DateGroup'])

                    PlotDate1=DF1Date
                    PlotData1=DF_1
                    PlotDate2=DF2Date
                    PlotData2=DF_2
                #code for year format
                if COT_FILTER_TYPE=='YEAR':
                    DF_1=FilteredDF.ComplaintId.groupby([FilteredDF.DateReceived.dt.year]).count()
                    DF_2=FilteredDF.ComplaintId.groupby([FilteredDF.DateSentCompany.dt.year]).count()
                    DF1Date=[]
                    DF2Date=[]

                    for Yr in np.nditer(DF_1.index.values):
                        Date1=datetime.datetime.strptime(str(Yr)+'-01-01','%Y-%m-%d')
                        DF1Date.append(Date1)

                    for Yr in np.nditer(DF_2.index.values):
                        Date2=datetime.datetime.strptime(str(Yr)+'-01-01','%Y-%m-%d')
                        DF2Date.append(Date2)

                    DF1Date=pd.DataFrame(DF1Date,columns=['DateGroup'])
                    DF2Date=pd.DataFrame(DF2Date,columns=['DateGroup'])

                    PlotDate1=DF1Date
                    PlotData1=DF_1
                    PlotDate2=DF2Date
                    PlotData2=DF_2

                #Display the relative plots only
                global COT_RECEIVED_FLG,COT_SEND_FLG
                if COT_RECEIVED_FLG is True:
                    ax1.plot_date(PlotDate1,PlotData1,'#183A54',label='Complaints Received Over Time')
                if COT_SEND_FLG is True:
                    ax1.plot_date(PlotDate2,PlotData2,'#00A3E0',label='Complaints Sent to Company')

                #axis properties
                ax1.legend(borderaxespad=0)
                ax1.xaxis.set_major_locator(MonthLocator())
                ax1.xaxis.set_major_formatter(DateFormatter("%b '%y"))
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Total Number of Complaints')
                ax1.set_title('Consumer Complains Over Time')
                ax1.autoscale_view()
                ax1.grid(True)
                f.autofmt_xdate()

                REFRESH_COT_FLG=False

        #code to Display Plot using Canvas
        canvas = FigureCanvasTkAgg(f, ImageFrame)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        #Toolbar for the Plots
        toolbar=NavigationToolbar2TkAgg(canvas,ImageFrame)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP,fill=BOTH,expand=True)

        #Animation Function to Display filter values
        ani=animation.FuncAnimation(f,COTAnimate,1000)

########################################################################################################################

    #function to plot the Products and Issue Pie Chart
################################################## BEGIN ###############################################################
    def ProductIssue(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton):
        global REFRESH_COT_FLG
        REFRESH_COT_FLG=True
        ComplaintsOTButton.config(state=DISABLED)
        ProductIssueButton.config(state=DISABLED)
        ImageLabel.destroy()

        OptionFrame=Frame(ImageFrame)
        OptionFrame.pack(side=TOP)

        var3=StringVar('')
        ProductIssueChoices=['Select Product']

        #function to display the relative Issues
        def PIfunc(value):
            global PRODUCT_ISSUE_FLG,REFRESH_COT_FLG
            InternalFlag=True
            if var3.get() in pd.unique(FilteredDF.Product):
                PRODUCT_ISSUE_FLG=var3.get()
            elif var3.get() =='None':
                PRODUCT_ISSUE_FLG='NONE'
            else:
                InternalFlag=False

            if InternalFlag is True:
                REFRESH_COT_FLG=True

        #Dropdown
        ProductIssueChoice=OptionMenu(OptionFrame,var3,*ProductIssueChoices)
        ProductIssueChoice.pack(side=LEFT)
        ProductIssueChoice.bind('<Configure>', PIfunc)

        #figure to plot
        f = Figure()

        #FUNCTION TO ANIMATE
        def PIAnimate(i):
            global REFRESH_COT_FLG
            try:
                if REFRESH_COT_FLG is True:

                    var3.set('Select Product')
                    ProductIssueChoice['menu'].delete(0,END)
                    ProductIssueChoice['menu'].add_command(label='None', command=tk._setit(var3, 'None'))
                    for choice in pd.unique(FilteredDF.Product):
                        ProductIssueChoice['menu'].add_command(label=choice, command=tk._setit(var3, choice))

                    ax1 = f.add_subplot(221)
                    ax1.clear()
                    ax2 = f.add_subplot(222)
                    ax3 = f.add_subplot(223)

                    ExplodeListProduct=[]
                    for i in range(0,len(pd.unique(FilteredDF.Product))):
                        if i%2==0:
                            ExplodeListProduct.append(0.1)
                        else:
                            ExplodeListProduct.append(0)
                    #plot Pie chart for Products
                    ax1.pie(FilteredDF.ComplaintId.groupby([FilteredDF.Product]).count(),
                            explode=tuple(ExplodeListProduct),
                            labels=pd.unique(FilteredDF.Product),shadow=True,autopct='%1.1f%%',
                            startangle=90)
                    ax1.set_title('Products')

                    #code for Sub Plots
                    global PRODUCT_ISSUE_FLG
                    if PRODUCT_ISSUE_FLG in pd.unique(FilteredDF.Product):
                        #Code for Issues
                        f.delaxes(ax1)

                        IssueStr='Product:'+PRODUCT_ISSUE_FLG+'\nIssues'

                        ax2.clear()
                        IssueFilterList=[]
                        IssueFilterList.append(PRODUCT_ISSUE_FLG)
                        IssueDF=FilteredDF[ (FilteredDF.Product.isin(IssueFilterList)) ]

                        ExplodeListIssue=[]
                        for i in range(0,len(pd.unique(IssueDF.Issue))):
                            if i%2==0:
                                ExplodeListIssue.append(0.1)
                            else:
                                ExplodeListIssue.append(0)

                        #plot Pie chart for Issues
                        ax2.pie(IssueDF.ComplaintId.groupby([IssueDF.Issue]).count(),
                                explode=tuple(ExplodeListIssue),
                                labels=pd.unique(IssueDF.Issue),shadow=True,autopct='%1.1f%%',
                                startangle=90)
                        ax2.set_title(IssueStr)

                        #code for Company
                        ax3.clear()
                        ExplodeListCompany=[]
                        for i in range(0,len(pd.unique(IssueDF.Company))):
                            if i%2==0:
                                ExplodeListCompany.append(0.1)
                            else:
                                ExplodeListCompany.append(0)

                        #plot Pie chart for Company
                        ax3.pie(IssueDF.ComplaintId.groupby([IssueDF.Company]).count(),
                                explode=tuple(ExplodeListCompany),
                                labels=pd.unique(IssueDF.Company),shadow=True,autopct='%1.1f%%',
                                startangle=90)
                        ax3.set_title('Companies')

                    else:
                        f.delaxes(ax2)
                        f.delaxes(ax3)

                    REFRESH_COT_FLG=False
            except Exception as e:
                print(e)



        #canvas to Display
        canvas = FigureCanvasTkAgg(f, ImageFrame)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        #Toolbar for the Plots
        toolbar=NavigationToolbar2TkAgg(canvas,ImageFrame)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP,fill=BOTH,expand=True)

        #Animation Function to Display filter values
        ani=animation.FuncAnimation(f,PIAnimate,1000)

########################################################################################################################

    #Function to Clear the Screen Reset
################################################## BEGIN ###############################################################
    def ClearFigure(root, photo, DataFrame, ImageFrame, OuterMainPageFrame, FilterFrame):
        ImageFrame.destroy()
        OuterMainPageFrame.destroy()
        FilterFrame.destroy()
        Analyst(root, photo, DataFrame)
########################################################################################################################

    # Buttons on MAin Frame
    #Sample Lables
    SpaceLabel0 = Label(MainPageFrame, text='', height=3)
    SpaceLabel00 = Label(MainPageFrame, text='', height=3)
    SpaceLabel1 = Label(MainPageFrame, text='', height=3)
    SpaceLabel2 = Label(MainPageFrame, text='', height=3)
    SpaceLabel3 = Label(MainPageFrame, text='', height=3)
    SpaceLabel4 = Label(MainPageFrame, text='', height=3)


    def Working():
        messagebox.showinfo("ALERT !!!", 'In Progress !!!')

    SpaceLabel00.pack()#Space Label
    ComplaintsOTButton = ttk.Button(MainPageFrame, text='Complaints Over Time',
                                    command=lambda: ComplaintsOT(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton),
                                    width=40,padding=10)
    ComplaintsOTButton.pack()
    SpaceLabel0.pack()#Space Label

    ProductIssueButton = ttk.Button(MainPageFrame, text='Product/Issue Analysis',
                                    command=lambda: ProductIssue(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton),
                               width=40,padding=10)
    ProductIssueButton.pack()
    SpaceLabel1.pack()#Space Label



    #####
    SampleButton2 = ttk.Button(MainPageFrame, text='In Progress. . .',
                                    command=Working,
                               width=40,padding=10)
    SampleButton2.pack()
    SpaceLabel2.pack()#Space Label

    SampleButton3 = ttk.Button(MainPageFrame, text='In Progress. . .',
                                    command=Working,
                               width=40,padding=10)
    SampleButton3.pack()
    SpaceLabel3.pack()#Space Label
    #####

    ClearButton = ttk.Button(MainPageFrame, text='Clear',
                             command=lambda: ClearFigure(root, photo, DataFrame, ImageFrame, OuterMainPageFrame,
                                                         FilterFrame),width=20,padding=10)
    ClearButton.pack(side=RIGHT)

    ExitButton = ttk.Button(MainPageFrame, text='Exit',command=root.quit,width=20,padding=10)
    ExitButton.pack(side=RIGHT)
    SpaceLabel4.pack()#Space Label

#Main Function
def main():
    root = Tk()
    root.iconbitmap(default='ConsumerComplaintIcon.ico')
    root.title('Consumer Complaint Analysis')
    #root.geometry('1250x700')
    # Image for Consumer Complaint
    photo = PhotoImage(file='ConsumerComplaint.png')
    DataFrame = LoadDF()
    Analyst(root, photo, DataFrame)
    root.mainloop()


main()
