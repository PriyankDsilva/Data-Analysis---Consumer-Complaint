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
PRODUCT_ISSUE_COMPANY_FLG='NONE'
COMPANY_PRODUCT_FLG=False
COMPANY_SELECT_FLG=False
COMPANY_PRODUCT_VAL='NONE'
COMPARE_COMPANY_VAL='NONE'
COMPARE_COMPANY_FLG=False
COMPANY_PRODUCT_PLOT=False
COMPARE_SELECT_FLG=False
CompanyDF=pd.DataFrame()
CompanyProductDF=pd.DataFrame()
IssueDF=pd.DataFrame()
CompareCompanyDF=pd.DataFrame()

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
    YearDropDown = Listbox(YearFrame,listvariable=year,selectmode=MULTIPLE,height=3)
    YearDropDown.pack()
    ProductDropDown = Listbox(ProductFrame,listvariable=product,selectmode=MULTIPLE,height=3)
    ProductDropDown.pack()
    CompanyDropDown = Listbox(CompanyFrame,listvariable=company,selectmode=MULTIPLE,height=3)
    CompanyDropDown.pack()
    StateDropDown = Listbox(StateFrame,listvariable=state,selectmode=MULTIPLE,height=3)
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
    def ComplaintsOT(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton,CompanyButton):
        global REFRESH_COT_FLG
        REFRESH_COT_FLG=True
        ComplaintsOTButton.config(state=DISABLED)
        ProductIssueButton.config(state=DISABLED)
        CompanyButton.config(state=DISABLED)
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
    def ProductIssue(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton,CompanyButton):
        global REFRESH_COT_FLG,IssueDF
        IssueDF=FilteredDF
        REFRESH_COT_FLG=True
        ComplaintsOTButton.config(state=DISABLED)
        ProductIssueButton.config(state=DISABLED)
        CompanyButton.config(state=DISABLED)
        ImageLabel.destroy()

        OptionFrame=Frame(ImageFrame)
        OptionFrame.pack(side=TOP)

        var3=StringVar(value='Select Product')
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

        #function to display the cascading ISsue dropdown
        var4=StringVar(value='Select Issue')
        ProductICChoices=['Select Product First']

        def PICfunc(value):
            global PRODUCT_ISSUE_FLG,REFRESH_COT_FLG,PRODUCT_ISSUE_COMPANY_FLG,IssueDF
            InternalFlag=True
            if var4.get() in pd.unique(IssueDF.Issue):
                PRODUCT_ISSUE_COMPANY_FLG=var4.get()
            elif var4.get() =='None':
                PRODUCT_ISSUE_COMPANY_FLG='NONE'
            else:
                InternalFlag=False

            if InternalFlag is True:
                REFRESH_COT_FLG=True

        #Dropdown
        ProductIssueCompanyChoice=OptionMenu(OptionFrame,var4,*ProductICChoices)
        ProductIssueCompanyChoice.pack(side=LEFT)
        ProductIssueCompanyChoice.bind('<Configure>', PICfunc)



        #figure to plot
        f = plt.figure()

        #FUNCTION TO ANIMATE
        def PIAnimate(i):
            global REFRESH_COT_FLG
            try:
                if REFRESH_COT_FLG is True:

                    #var3.set('Select Product')
                    ProductIssueChoice['menu'].delete(0,END)
                    ProductIssueChoice['menu'].add_command(label='None', command=tk._setit(var3, 'None'))
                    for choice in pd.unique(FilteredDF.Product):
                        ProductIssueChoice['menu'].add_command(label=choice, command=tk._setit(var3, choice))

                    #CODE TO EMPTY THE iSSUE DROPdOWN
                    ProductIssueCompanyChoice['menu'].delete(0,END)
                    ProductIssueCompanyChoice['menu'].add_command(label='None', command=tk._setit(var4, 'Select Product First'))

                    ax1 = f.add_subplot(111)
                    ax1.clear()
                    #ax2 = f.add_subplot(211)
                    #ax3 = f.add_subplot(212)


                    #the the initial Product Pie chart
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
                    global PRODUCT_ISSUE_FLG,IssueDF,PRODUCT_ISSUE_COMPANY_FLG
                    if PRODUCT_ISSUE_FLG in pd.unique(FilteredDF.Product):



                        #Code for Issues
                        f.delaxes(ax1)
                        #GET FILTERED data after selecting the product
                        IssueStr='Product:'+PRODUCT_ISSUE_FLG+'\nIssues'
                        ax2 = f.add_subplot(111)
                        ax2.clear()
                        IssueFilterList=[]
                        IssueFilterList.append(PRODUCT_ISSUE_FLG)
                        IssueDF=FilteredDF[ (FilteredDF.Product.isin(IssueFilterList)) ]


                        #populate the dropdown
                        ProductIssueCompanyChoice['menu'].delete(0,END)
                        ProductIssueCompanyChoice['menu'].add_command(label='None', command=tk._setit(var4, 'None'))
                        for choice in pd.unique(IssueDF.Issue):
                            ProductIssueCompanyChoice['menu'].add_command(label=choice, command=tk._setit(var4, choice))

                        #PLOT THE iSSUES inside the product
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
                        #IssueDF.ComplaintId.groupby([IssueDF.Issue]).count().plot(kind='barh')

                        #code for Company
                        if PRODUCT_ISSUE_COMPANY_FLG in pd.unique(IssueDF.Issue):

                            f.delaxes(ax2)
                            #var3.set('Select Product')


                            ax3 = f.add_subplot(111)
                            ax3.clear()
                            #GET FILTERED DF FOR COMPANY
                            IssueFilterList=[]
                            IssueFilterList.append(PRODUCT_ISSUE_COMPANY_FLG)
                            IssueCompanyDF=IssueDF[ (IssueDF.Issue.isin(IssueFilterList)) ]

                            ExplodeListCompany=[]
                            for i in range(0,len(pd.unique(IssueCompanyDF.Company))):
                                if i%2==0:
                                    ExplodeListCompany.append(0.1)
                                else:
                                    ExplodeListCompany.append(0)

                            #plot Pie chart for Company
                            ax3.pie(IssueCompanyDF.ComplaintId.groupby([IssueCompanyDF.Company]).count(),
                                    explode=tuple(ExplodeListCompany),
                                    labels=pd.unique(IssueCompanyDF.Company),shadow=True,autopct='%1.1f%%',
                                    startangle=90)
                            CompanyStr='Product:'+PRODUCT_ISSUE_FLG+' Issues:'+PRODUCT_ISSUE_COMPANY_FLG+'\nCompanies'
                            ax3.set_title(CompanyStr)

                    else:
                        try:
                            f.delaxes(ax2)
                            f.delaxes(ax3)
                        except Exception as e:
                            print()

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

    #function for Company Analysis
################################################## BEGIN ###############################################################
    def Company(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton,CompanyButton):
        global REFRESH_COT_FLG,COMPANY_PRODUCT_FLG,COMPANY_SELECT_FLG
        REFRESH_COT_FLG=True
        COMPANY_SELECT_FLG=False
        COMPANY_PRODUCT_FLG=False
        COMPARE_COMPANY_FLG=False
        ComplaintsOTButton.config(state=DISABLED)
        ProductIssueButton.config(state=DISABLED)
        CompanyButton.config(state=DISABLED)
        ImageLabel.destroy()

        OptionFrame=Frame(ImageFrame)
        OptionFrame.pack(side=TOP)

        CompareFrame=Frame(ImageFrame)
        CompareFrame.pack(side=BOTTOM)


        var=StringVar(value='Select Company')
        CompanyOptions=pd.unique(FilteredDF.Company)
        global CompanyDF,CompanyProductDF,CompareCompanyDF
        CompanyDF=FilteredDF
        CompanyProductDF=FilteredDF


        #function to select te recieved or sent lines
        def Companyfunc(value):
            global REFRESH_COT_FLG,CompanyDF,COMPANY_SELECT_FLG,COMPANY_PRODUCT_PLOT
            #print('Companyfunc')
            CompanyList=[]
            CompanyList.append(value)
            CompanyDF=FilteredDF[FilteredDF.Company.isin(CompanyList)]
            COMPANY_SELECT_FLG=True
            REFRESH_COT_FLG=True
            COMPANY_PRODUCT_PLOT=False
            COMPARE_COMPANY_FLG=False


        #Drop down buttons
        CompanyChoice=OptionMenu(OptionFrame,var,*CompanyOptions,command=Companyfunc)
        CompanyChoice.pack(side=LEFT)

        #function to get the products related to company
        var2=StringVar(value='Please Select Company First')
        CompanyProductOptions=['None']


        def CompanyProductfunc(value):
            global REFRESH_COT_FLG,CompanyProductDF,CompanyDF,COMPANY_PRODUCT_FLG,COMPANY_PRODUCT_VAL,COMPARE_SELECT_FLG
            #print('CompanyProductfunc')
            InternalFlag=True
            if var2.get() in pd.unique(CompanyDF.Product):
                COMPANY_PRODUCT_VAL=var2.get()
            elif var2.get() =='None':
                COMPANY_PRODUCT_VAL='NONE'
            else:
                InternalFlag=False

            if InternalFlag is True:
                REFRESH_COT_FLG=True
                COMPANY_PRODUCT_FLG=True
                COMPARE_SELECT_FLG=True
                COMPARE_COMPANY_FLG=False
                #print('COMPANY_PRODUCT_VAL :',COMPANY_PRODUCT_VAL)

        CompanyProductChoice=OptionMenu(OptionFrame,var2,*CompanyProductOptions)
        CompanyProductChoice.pack(side=RIGHT)
        CompanyProductChoice.bind('<Configure>', CompanyProductfunc)



        #Code for Comparison Drop Down

        var3=StringVar(value='Please Select Company/Product First')
        CompareCompanyOptions=['None']
        CompareCompanyDF=FilteredDF

        def CompareCompanyfunc(value):
            global REFRESH_COT_FLG,CompareCompanyDF,COMPANY_PRODUCT_FLG,COMPARE_COMPANY_FLG,COMPARE_COMPANY_VAL
            print('CompanyComparefunc')
            InternalFlag=True
            if var3.get() in pd.unique(CompareCompanyDF.Company):
                COMPARE_COMPANY_VAL=var3.get()
            elif var3.get() =='None':
                COMPARE_COMPANY_VAL='NONE'
            else:
                InternalFlag=False

            if InternalFlag is True:
                print('reset done')
                REFRESH_COT_FLG=True
                COMPARE_COMPANY_FLG=True


        CompareCompanyChoice=OptionMenu(CompareFrame,var3,*CompareCompanyOptions)
        CompareCompanyChoice.pack(side=RIGHT)
        CompareCompanyChoice.bind('<Configure>', CompareCompanyfunc)



        f = plt.figure()

        #animate function for company
        def CompanyAnimate(i):
            global REFRESH_COT_FLG,CompanyDF,CompareCompanyDF,COMPANY_SELECT_FLG,COMPARE_COMPANY_VAL,COMPARE_COMPANY_FLG
            global COMPANY_PRODUCT_FLG,CompanyProductDF,COMPANY_PRODUCT_VAL,COMPANY_PRODUCT_PLOT,COMPARE_SELECT_FLG
            try:
                if REFRESH_COT_FLG is True:

                    ax1 = f.add_subplot(221)
                    ax1.clear()
                    #plot basic chart for all products or the company specific products if selected
                    ExplodeListProduct=[]
                    for i in range(0,len(pd.unique(CompanyDF.Product))):
                        if i%2==0:
                            ExplodeListProduct.append(0.1)
                        else:
                            ExplodeListProduct.append(0)
                    #plot Pie chart for Products
                    ax1.pie(CompanyDF.ComplaintId.groupby([CompanyDF.Product]).count(),
                            explode=tuple(ExplodeListProduct),
                            labels=pd.unique(CompanyDF.Product),shadow=True,autopct='%1.1f%%',
                            startangle=90)
                    CompanyName=''
                    if len(pd.unique(CompanyDF.Company)) == 1:
                        CompanyName=str(pd.unique(CompanyDF.Company)[0])+' Products'
                    else:
                        CompanyName='All Company Products'
                    ax1.set_title(CompanyName)



                    if COMPANY_SELECT_FLG is True:

                        var2.set('Select Product')
                        CompanyProductChoice['menu'].delete(0,END)
                        CompanyProductChoice['menu'].add_command(label='None', command=tk._setit(var2, 'None'))
                        for choice in pd.unique(CompanyDF.Product):
                            CompanyProductChoice['menu'].add_command(label=choice, command=tk._setit(var2, choice))
                        COMPANY_SELECT_FLG=False

                    if COMPARE_SELECT_FLG is True:
                        #create a dataframe
                        print('set for compare company')
                        CompareList=[]
                        CompareList.append(var2.get())
                        print(CompareList)
                        CompareCompanyDF=FilteredDF[FilteredDF.Product.isin(CompareList)]

                        var3.set('Select Company')
                        CompareCompanyChoice['menu'].delete(0,END)
                        CompareCompanyChoice['menu'].add_command(label='None', command=tk._setit(var3, 'None'))
                        for choice in pd.unique(CompareCompanyDF.Company):
                            CompareCompanyChoice['menu'].add_command(label=choice, command=tk._setit(var3, choice))
                        COMPARE_SELECT_FLG=False


                    #code to display the product issues is company Product is selected
                    ax2=f.add_subplot(222)
                    if COMPANY_PRODUCT_FLG is True:

                        ax2.clear()

                        CompanyProductList=[]
                        CompanyProductList.append(COMPANY_PRODUCT_VAL)
                        CompanyProductDF=CompanyDF[ (CompanyDF.Product.isin(CompanyProductList)) ]

                        ExplodeListCompanyProductIssue=[]
                        for i in range(0,len(pd.unique(CompanyProductDF.Issue))):
                            if i%2==0:
                                ExplodeListCompanyProductIssue.append(0.1)
                            else:
                                ExplodeListCompanyProductIssue.append(0)


                        #plot Pie chart for Products
                        ax2.pie(CompanyProductDF.ComplaintId.groupby([CompanyProductDF.Issue]).count(),
                                explode=tuple(ExplodeListCompanyProductIssue),
                                labels=pd.unique(CompanyProductDF.Issue),shadow=True,autopct='%1.1f%%',
                                startangle=90)
                        CompanyName=''
                        if len(pd.unique(CompanyProductDF.Product)) == 1:
                            CompanyName=str(pd.unique(CompanyProductDF.Product)[0])+' Issues'
                        else:
                            CompanyName='Product Not Specified'
                        ax2.set_title(CompanyName)

                        COMPANY_PRODUCT_PLOT=True
                        COMPANY_PRODUCT_FLG=False
                    else:
                        if COMPANY_PRODUCT_PLOT is False:
                            f.delaxes(ax2)

                        #code to add compare Company
                    if COMPARE_COMPANY_FLG is True:
                        ax3=f.add_subplot(223)
                        ax3.clear()


                        #Plot issues of the compare company
                        CompareList=[]
                        CompareList.append(COMPARE_COMPANY_VAL)
                        CompareDF=CompareCompanyDF[ (CompareCompanyDF.Company.isin(CompareList)) ]


                        ExplodeListCompareIssue=[]
                        for i in range(0,len(pd.unique(CompareDF.Issue))):
                            if i%2==0:
                                ExplodeListCompareIssue.append(0.1)
                            else:
                                ExplodeListCompareIssue.append(0)

                        ax3.pie(CompareDF.ComplaintId.groupby([CompareDF.Issue]).count(),
                                    explode=tuple(ExplodeListCompareIssue),
                                    labels=pd.unique(CompareDF.Issue),shadow=True,autopct='%1.1f%%',
                                    startangle=90)
                        CompareName='Company :'+COMPARE_COMPANY_VAL
                        ax3.set_title(CompareName)

                        #Plot compare of the compare company
                        Company1=var.get()
                        Company2=var3.get()

                        CompanyLists=[]
                        CompanyLists.append(Company1)
                        CompanyLists.append(Company2)
                        print(CompanyLists)
                        ax4=f.add_subplot(224)
                        ax4.clear()

                        PlotDF=CompareCompanyDF[CompareCompanyDF.Company.isin(CompanyLists)]

                        ExplodeCompare=[]
                        for i in range(0,len(pd.unique(PlotDF.Company))):
                            if i%2==0:
                                ExplodeCompare.append(0.1)
                            else:
                                ExplodeCompare.append(0)


                        #PlotDF.Issue.groupby([PlotDF.Company,PlotDF.Issue]).count().plot(kind='bar')
                        ax4.pie(PlotDF.Issue.groupby([PlotDF.Company]).count(),
                                    explode=tuple(ExplodeCompare),
                                    labels=pd.unique(PlotDF.Company),shadow=True,autopct='%1.1f%%',
                                    startangle=90)


                        ax4.set_title('Comparison')

                        COMPARE_COMPANY_FLG=False





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
        ani=animation.FuncAnimation(f,CompanyAnimate,1000)

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
                                    command=lambda: ComplaintsOT(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton,CompanyButton),
                                    width=40,padding=10)
    ComplaintsOTButton.pack()
    SpaceLabel0.pack()#Space Label

    ProductIssueButton = ttk.Button(MainPageFrame, text='Product Analysis',
                                    command=lambda: ProductIssue(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton,CompanyButton),
                               width=40,padding=10)
    ProductIssueButton.pack()
    SpaceLabel1.pack()#Space Label

    CompanyButton = ttk.Button(MainPageFrame, text='Company Analysis',
                                    command=lambda: Company(ImageFrame, ImageLabel, ComplaintsOTButton,ProductIssueButton,CompanyButton),
                               width=40,padding=10)
    CompanyButton.pack()
    SpaceLabel2.pack()#Space Label

    #####
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
