from urllib import request
import Initialize
import FirebirdDB
import os
import datetime
import shutil
import time
import threading
from tkinter import messagebox

#Global Variable
FAIL_FLAG=False
STEP_COUNT=1

#Function to Check if the Update Process is Initiated or not if not then Initiate it else exit if process is running.
def DataUpdateFlag():
    # check if the file is present if not then create
    InitialParameters = Initialize.getParam()
    LoadFileName = InitialParameters[15]
    LogFileName = InitialParameters[14]
    MainLogTable = InitialParameters[18]

    if os.path.isfile(LoadFileName) == True:
        print('Update Already in Progress  !!!')
        exit()
    else:
        LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
        LoadFile = open(LoadFileName, 'w')
        LoadFile.close()
        LogFile = open(LogFileName, 'w')
        LogFile.close()
        WriteToLog('Update Process Initiated . . .   '+time.strftime('%d %b %Y %X'))
        LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
        LoadIndex+=1
        LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
        global STEP_COUNT
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Pre-Pre',LogFileName.split('\\')[-1],'Created Log File to Capture Update Progress Status',0,LoadStartDTTM,LoadEndDTTM)
        STEP_COUNT+=1
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Pre-Pre',LoadFileName.split('\\')[-1],'Created Trig File to Indicate \'Update in Progress\'',0,LoadStartDTTM,LoadEndDTTM)
        STEP_COUNT+=1

#function to append a message in Log file
def WriteToLog(msg):
    InitialParameters = Initialize.getParam()
    LogFileName = InitialParameters[14]
    LogFile = open(LogFileName, 'a')
    LogFile.write(msg+'\n')
    LogFile.close()
    print(msg)

#Pre Tasks to Clone and Swap Main Table and View
def PreLoadTasks():
    InitialParameters = Initialize.getParam()
    LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
    TableName = InitialParameters[10]
    CloneTableName=InitialParameters[12]
    ViewName=InitialParameters[16]
    MainLogTable = InitialParameters[18]
    global STEP_COUNT

    # Clone Main Table
    try:
        LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
        FirebirdDB.CloneTable(TableName,CloneTableName)
        TableCount=FirebirdDB.GetTableCount(CloneTableName)
        LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
    except Exception as e:
        FailureRevert(1,e)
    else:
        WriteToLog('\nClone Table ('+CloneTableName.upper()+') Created.')
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Pre-Pre',CloneTableName,'Clone Table Created',TableCount,LoadStartDTTM,LoadEndDTTM)
        STEP_COUNT+=1
    #Swap Views
    try:
        FirebirdDB.ViewSwap(CloneTableName,ViewName)
        ViewCount=FirebirdDB.GetTableCount(ViewName)
        LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
    except Exception as e2:
        FailureRevert(2,e2)
    else:
        WriteToLog('View Swap ('+ViewName.upper()+' --> '+CloneTableName.upper()+') Completed.')
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Pre-Pre',ViewName,'Swap Main view to Clone Table',ViewCount,LoadStartDTTM,LoadEndDTTM)
        STEP_COUNT+=1



#Function to Get Data from API into CSV file
def GetData():
    try:
        InitialParameters = Initialize.getParam()
        StagingPath = InitialParameters[2]
        APIView = InitialParameters[3].split(',')
        APICategory = InitialParameters[4].split(',')
        BaseURl = InitialParameters[5].replace("'", "")

        type_param = 'csv'
        row_param = 'rows'
        RequestURLList = []

        WriteToLog('\nFetching Files form http://data.consumerfinance.gov using API')
        WriteToLog('------------------------------------------------------------------------------------------------------------------')

        for i in range(0, len(APIView)):
            # print(APICategory[i].replace("'",""),'\t\t',APIView[i].replace("'",""))
            RequestURLList.append(BaseURl + APIView[i].replace("'", "") + '/' + row_param + '.' + type_param)
            #print(RequestURLList[i])
            URLData = request.urlopen(RequestURLList[i])
            CSVRaw = URLData.read()
            CSVData = str(CSVRaw).strip("b'")
            lines = CSVData.split("\\n")

            CSVFileName = StagingPath + APICategory[i].replace("'", "") + '.' + type_param
            CSVFile = open(CSVFileName, 'w')
            WriteToLog('Loading : '+APICategory[i].replace("'", "") + '.' + type_param+' <-- '+ RequestURLList[i])
            #print(CSVFileName)

            for line in lines:
                CSVFile.write(line + "\n")
            CSVFile.close()
        WriteToLog('------------------------------------------------------------------------------------------------------------------')
    except Exception as e:
        FailureRevert(3,e)

#Function to Load Data into the Staging Table
def LoadDataStaging():
    InitialParameters = Initialize.getParam()
    MainLogTable = InitialParameters[18]
    MainLoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
    APIView = InitialParameters[3].split(',')
    APICategory = InitialParameters[4].split(',')
    FilterValue = InitialParameters[17].split(',')
    type_param = 'csv'

    StagTableName = InitialParameters[11]
    TableName = InitialParameters[10]
    RejectFileName = InitialParameters[9]
    StagingPath = InitialParameters[2]
    RejectFile = StagingPath + RejectFileName
    LogTableName=InitialParameters[13]

    # create a Reject List
    try:
        LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
        RFile = open(RejectFile, 'w')
        #RejectComment = "Datereceived,Product,Subproduct,Issue,Subissue,Consumercomplaintnarrative,Companypublicresponse,Company,State,ZIPcode,Submittedvia,Datesenttocompany,Companyresponsetoconsumer,Timelyresponse,Consumerdisputed,ComplaintID"
        RejectComment = "Company,Companypublicresponse,Companyresponsetoconsumer,ComplaintID,Consumercomplaintnarrative,Consumerdisputed,Datereceived,Datesenttocompany,Issue,Product,State,Subissue,Submittedvia,Subproduct,Timelyresponse,ZIPcode"
        RFile.write(RejectComment)
        RFile.close
    except Exception as e:
        FailureRevert(4,e)
    else:
        WriteToLog('\nReject File ('+RejectFileName+') Created.')

        #Update the Main Log
        LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
        LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
        global STEP_COUNT
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Pre-Pre',RejectFileName,'Created Reject File to Capture Rejects',0,LoadStartDTTM,LoadEndDTTM)
        STEP_COUNT+=1

    try:
        # Truncate staging db
        FirebirdDB.DeleteData(StagTableName)
    except Exception as e:
        FailureRevert(5,e)
    else :
        WriteToLog('Staging Table '+StagTableName.upper()+' Truncated. \n')

    try:
        #Get Load Index
        LoadIndex=FirebirdDB.GetLoadIndex(LogTableName)

        WriteToLog('Staging Table '+StagTableName.upper()+' Loading Initiated . . . ')
        WriteToLog('------------------------------------------------------------------------------------------------------------------')
        # load data from files
        for i in range(0, len(APICategory)):
            LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
            #print('InsertData(',StagTableName,',',APICategory[i].replace("'", ""))
            FirebirdDB.InsertData(StagTableName, APICategory[i].replace("'", ""))
            LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
            RowCount=FirebirdDB.GetRecordCount(StagTableName,FilterValue[i].replace("'", ""))
            WriteToLog('Loading : '+StagTableName.upper()+' <-- '+ APICategory[i].replace("'", "")+'   [Count('+str(RowCount)+')]')
            FirebirdDB.UpdateLog(LogTableName,(LoadIndex+1),(i+1),APIView[i].replace("'", ""),APICategory[i].replace("'", ""),RowCount,LoadStartDTTM,LoadEndDTTM)
        WriteToLog('------------------------------------------------------------------------------------------------------------------')
    except Exception as e:
        FailureRevert(6,e)
    else:
        #Update the Main Log
        LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
        TableCount=FirebirdDB.GetTableCount(StagTableName)
        MainLoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Data-Load',StagTableName,'Staging Table Loaded',TableCount,MainLoadStartDTTM,MainLoadEndDTTM)
        STEP_COUNT+=1

#Function to Update the Main Table with New Records
def MainTableAppend():
    try:
        InitialParameters = Initialize.getParam()
        MainLogTable = InitialParameters[18]
        MainLoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
        StagTableName = InitialParameters[11]
        TableName = InitialParameters[10]
        WriteToLog('\nAdding new Records to Main Table ('+TableName.upper()+')')
        WriteToLog('----------------------------------------------------------------------------------------------------------')
        MainRowCount=FirebirdDB.GetMainRecordCount(TableName,StagTableName)
        FirebirdDB.UpdateMainTable(TableName,StagTableName)
        WriteToLog('Loading : '+TableName.upper()+'<-- '+StagTableName.upper()+'   [Count('+str(MainRowCount)+')]')
        WriteToLog('----------------------------------------------------------------------------------------------------------')

        #Update the Main Log
        LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
        TableCount=FirebirdDB.GetTableCount(TableName)
        MainLoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
    except Exception as e:
        FailureRevert(7,e)
    else:
        global STEP_COUNT
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Data-Load',TableName,'Main Table Loaded',TableCount,MainLoadStartDTTM,MainLoadEndDTTM)
        STEP_COUNT+=1

#function to do post tasks like swapping views,reject file log ang Trig file related activities
#added failure mechanizm
def PostLoadTasks(*RevertList):

    if len(RevertList) == 0 :
        RevertList=['S','T','L','R']

    InitialParameters = Initialize.getParam()
    MainLogTable = InitialParameters[18]
    TableName = InitialParameters[10]
    ViewName=InitialParameters[16]
    LogPath=InitialParameters[19]
    LoadFileName = InitialParameters[15]
    LogFileName = InitialParameters[14]
    LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
    LogTime=time.strftime("%d%b%Y_%X")
    global STEP_COUNT,FAIL_FLAG

    if 'S' in RevertList:
        try:
            LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]

            #Swap View
            FirebirdDB.ViewSwap(TableName,ViewName)
            ViewCount=FirebirdDB.GetTableCount(ViewName)
            LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

            FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Post-Post',ViewName,'View Swap back to Main Table',ViewCount,LoadStartDTTM,LoadEndDTTM)
            STEP_COUNT+=1

        except Exception as e:
            FailureRevert(8,e)
        else :
            WriteToLog('\nView Swap ('+ViewName.upper()+' --> '+TableName.upper()+') Completed.')

    if 'R' in RevertList:
        try:
            #Checkif the Rejects Exists if so then move then to log dir
            LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
            RejectFileName = InitialParameters[9]
            StagingPath = InitialParameters[2]
            RejectFile = StagingPath + RejectFileName
            if sum(1 for line in open(RejectFile))==1:
                WriteToLog('Zero Reject Records Found !!! ')
                RejectStatus='No Rejects Found'
                TotalRejectCount=0
                os.remove(RejectFile)
            else:
                TotalRejectCount=sum(1 for line in open(RejectFile))-1
                WriteToLog('Rejects Records Captured in - '+RejectFileName+' Count: '+str(TotalRejectCount))
                ArchiveReject=LogPath+'RejectFile_'+LogTime.replace(':','')+'.csv'
                RejectStatus='Rejects Found...Archiving the Reject File as '+ ArchiveReject.split('\\')[-1]
                shutil.move(RejectFile,ArchiveReject)
                WriteToLog('Reject File ('+RejectFileName+') Sucessfully Archived.')
        except Exception as e:
            FailureRevert(9,e)
        else:
            LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
            FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Post-Post',RejectFileName,RejectStatus,TotalRejectCount,LoadStartDTTM,LoadEndDTTM)
            STEP_COUNT+=1

    if 'T' in RevertList:
        try:
            #Delete Trig File
            LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
            #remove the file
            os.remove(LoadFileName)
            LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

            if 'F' in RevertList:
                TrigStatus='Trig File deleted .Process Terminated due to Error !!!'
                FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Post-Post',LoadFileName.split('\\')[-1],TrigStatus,0,LoadStartDTTM,LoadEndDTTM)
                STEP_COUNT+=1
                WriteToLog('\nTrig File Deleted -- Process Terminated.')
            else:
                TrigStatus='Trig File deleted to indicate Data Load Status as Completed'
                FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Post-Post',LoadFileName.split('\\')[-1],TrigStatus,0,LoadStartDTTM,LoadEndDTTM)
                STEP_COUNT+=1
                WriteToLog('\nTrig File Deleted to Indicate Data Load Complete.')

        except Exception as e:
            FailureRevert(10,e)



    if 'L' in RevertList:
        try:
            ##Move log file
            LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]

            ArchiveLog=LogPath+'DataUpdateLog_'+LogTime.replace(':','')+'.log'

            WriteToLog('Log File ('+LogFileName.split('\\')[-1]+') Archived.')
            if 'F' in RevertList:
                WriteToLog('\nUpdate Process Terminated due to Error !!!   '+time.strftime('%d %b %Y %X'))
            else:
                WriteToLog('\nUpdate Process Sucessfully Completed. . .   '+time.strftime('%d %b %Y %X'))
            WriteToLog('\n\n\n*Note-Display will be cleared in 10 seconds.')

            time.sleep(10)
            shutil.move(LogFileName,ArchiveLog)
            LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
            FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Post-Post',LogFileName.split('\\')[-1],'Log File Archived as '+ArchiveLog.split('\\')[-1],0,LoadStartDTTM,LoadEndDTTM)
            STEP_COUNT+=1
            WriteToLog('--  Log File Cleared/Archived !!!  ---')

        except Exception as e:
            FailureRevert(11,e)

        FAIL_FLAG=True

#revert in case of failure
def FailureRevert(Step,Error):
    global FAIL_FLAG,STEP_COUNT
    ErrorString={1:'Creating Clone Table',
                 2:'Swapping View to Clone Table',
                 3:'Fetching Data from Online API',
                 4:'Creating Reject File',
                 5:'Truncating Staging Table',
                 6:'Loading Data into Staging Table',
                 7:'Appending Data to Main Table',
                 8:'Swapping View to Main Table',
                 9:'Archiving Reject File',
                 10:'Deleting Trig File',
                 11:'Archiving Log File'}
    WriteToLog('Error During : '+str(ErrorString.get(Step)))
    WriteToLog('Description :'+str(Error))

    InitialParameters = Initialize.getParam()
    MainLogTable = InitialParameters[18]
    TableName = InitialParameters[10]
    CloneTableName=InitialParameters[12]
    LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
    LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
    LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,STEP_COUNT,'Error',str(ErrorString.get(Step)),str(Error),0,LoadStartDTTM,LoadEndDTTM)
    STEP_COUNT+=1

    #Revert Tasks if needed
    if Step==1:
        RevertList=['T','L','F']
    elif Step in (3,4,5,6):
        RevertList=['S','T','L','F']
    elif Step == 7:
        FirebirdDB.CloneTable(CloneTableName,TableName)
        RevertList=['S','T','L','F']
    else:
        messagebox.showinfo("Alert !!!", "Error in Swapping View.Please check Logs!!!\n\n\nTerminating Upload Process.")
        exit()
    #fun the post function
    PostLoadTasks(*RevertList)

def main():
    global FAIL_FLAG
    if FAIL_FLAG==False:
        DataUpdateFlag()
    if FAIL_FLAG==False:
        PreLoadTasks()
    if FAIL_FLAG==False:
        GetData()
    if FAIL_FLAG==False:
        LoadDataStaging()
    if FAIL_FLAG==False:
        MainTableAppend()
    if FAIL_FLAG==False:
        PostLoadTasks()
