from urllib import request
import Initialize
import FirebirdDB
import os
import datetime
import shutil
import time

#Function to Check if the Update Process is Initiated or not if not then Initiate it else exit if process is running.
def DataUpdateFlag():
    # check if the file is present if not then create
    InitialParameters = Initialize.getParam()
    LoadFileName = InitialParameters[15]
    LogFileName = InitialParameters[14]
    MainLogTable = InitialParameters[18]

    if os.path.isfile(LoadFileName) == True:
        print('Update Already in Progress !!!')
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

        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'1','Pre-Pre',LogFileName.split('\\')[-1],'Created Log File to Capture Update Progress Status',0,LoadStartDTTM,LoadEndDTTM)
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'2','Pre-Pre',LoadFileName.split('\\')[-1],'Created Trig File to Indicate \'Update in Progress\'',0,LoadStartDTTM,LoadEndDTTM)

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

    # Clone Main Table and Swap Views
    #print(TableName,CloneTableName,ViewName)
    WriteToLog('\nClone Table ('+CloneTableName.upper()+') Created.')
    WriteToLog('View Swap ('+ViewName.upper()+' --> '+CloneTableName.upper()+') Completed.')
    FirebirdDB.CloneTable(TableName,CloneTableName,ViewName)

    LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
    TableCount=FirebirdDB.GetTableCount(CloneTableName)
    ViewCount=FirebirdDB.GetTableCount(ViewName)
    LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'3','Pre-Pre',CloneTableName,'Clone Table Created',TableCount,LoadStartDTTM,LoadEndDTTM)
    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'4','Pre-Pre',ViewName,'Swap Main view to Clone Table',ViewCount,LoadStartDTTM,LoadEndDTTM)

#Function to Get Data from API into CSV file
def GetData():
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
    LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
    RFile = open(RejectFile, 'w')
    #RejectComment = "Datereceived,Product,Subproduct,Issue,Subissue,Consumercomplaintnarrative,Companypublicresponse,Company,State,ZIPcode,Submittedvia,Datesenttocompany,Companyresponsetoconsumer,Timelyresponse,Consumerdisputed,ComplaintID"
    RejectComment = "Company,Companypublicresponse,Companyresponsetoconsumer,ComplaintID,Consumercomplaintnarrative,Consumerdisputed,Datereceived,Datesenttocompany,Issue,Product,State,Subissue,Submittedvia,Subproduct,Timelyresponse,ZIPcode"
    RFile.write(RejectComment)
    RFile.close

    WriteToLog('\nReject File ('+RejectFileName+') Created.')
    #Update the Main Log
    LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
    LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'5','Pre-Pre',RejectFileName,'Created Reject File to Capture Rejects',0,LoadStartDTTM,LoadEndDTTM)



    # Truncate staging db
    FirebirdDB.DeleteData(StagTableName)
    WriteToLog('Staging Table '+StagTableName.upper()+' Truncated. \n')

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

    #Update the Main Log

    LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
    TableCount=FirebirdDB.GetTableCount(StagTableName)
    MainLoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'6','Data-Load',StagTableName,'Staging Table Loaded',TableCount,MainLoadStartDTTM,MainLoadEndDTTM)





#Function to Update the Main Table with New Records
def MainTableAppend():
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

    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'7','Data-Load',TableName,'Main Table Loaded',TableCount,MainLoadStartDTTM,MainLoadEndDTTM)

def PostLoadTasks():
    InitialParameters = Initialize.getParam()
    MainLogTable = InitialParameters[18]
    TableName = InitialParameters[10]
    ViewName=InitialParameters[16]
    LogPath=InitialParameters[19]
    LoadFileName = InitialParameters[15]
    LogFileName = InitialParameters[14]

    LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
    LoadIndex=FirebirdDB.GetLoadIndex(MainLogTable)
    #Swap View
    FirebirdDB.ViewSwap(TableName,ViewName)
    ViewCount=FirebirdDB.GetTableCount(ViewName)
    LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]

    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'8','Post-Post',ViewName,'View Swap back to Main Table',ViewCount,LoadStartDTTM,LoadEndDTTM)
    WriteToLog('\nView Swap ('+ViewName.upper()+' --> '+TableName.upper()+') Completed.')

    #Checkif the Rejects Exists if so then move then to log dir
    LogTime=time.strftime("%d%b%Y_%X")
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


    LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'9','Post-Post',RejectFileName,RejectStatus,TotalRejectCount,LoadStartDTTM,LoadEndDTTM)



    #Delete Trig File
    LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]
    #remove the file
    os.remove(LoadFileName)
    LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
    FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'10','Post-Post',LoadFileName.split('\\')[-1],'Trig File deleted to indicate Data Load Status as Completed',0,LoadStartDTTM,LoadEndDTTM)
    WriteToLog('\nTrig File Deleted to Indicate Data Load Complete.')

    ##Move log file
    LoadStartDTTM=str(datetime.datetime.now()).split('.')[0]

    ArchiveLog=LogPath+'DataUpdateLog_'+LogTime.replace(':','')+'.log'

    WriteToLog('Log File ('+LogFileName.split('\\')[-1]+') Archived.')
    WriteToLog('\nUpdate Process Sucessfully Completed. . .   '+time.strftime('%d %b %Y %X'))
    WriteToLog('\n\n\n*Note-Display will be cleared in 30 seconds.')
    time.sleep(30)
    try:
        shutil.move(LogFileName,ArchiveLog)
    except Exception as e:
        print(e)
    else:
        LoadEndDTTM=str(datetime.datetime.now()).split('.')[0]
        FirebirdDB.UpdateMainLog(MainLogTable,LoadIndex,'11','Post-Post',LogFileName.split('\\')[-1],'Log File Archived as '+ArchiveLog.split('\\')[-1],0,LoadStartDTTM,LoadEndDTTM)
    WriteToLog('--  Log File Cleared/Archived !!!  ---')




def main():
    DataUpdateFlag()
    PreLoadTasks()
    GetData()
    LoadDataStaging()
    MainTableAppend()
    PostLoadTasks()
