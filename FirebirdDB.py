import fdb,time
import Initialize
import pandas as pd


InitialParameters=Initialize.getParam()
DBLocation=InitialParameters[1]
StagingPath=InitialParameters[2]
DBName=InitialParameters[6]
UserName=InitialParameters[7]
Password=InitialParameters[8]
RejectFileName=InitialParameters[9]
MainLogTable = InitialParameters[18]
LogTableName=InitialParameters[13]

DBPath=DBLocation+DBName

#Insert Data into Table from File and Create a Reject file for the Rejected Records
def InsertData(TableName,FileName):

    global DBPath,UserName,Password,StagingPath,RejectFileName
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    #create Insert Statement
    SQLComment="insert into "+TableName+" (DateReceived,Product,SubProduct,Issue,SubIssue,ConsumerComplaint,CompanyPublicResponse,Company,State,ZIPCode,SubmittedVia,DateSentCompany,CompanyResponseConsumer,TimelyResponseSts,ConsumerDisputedSts,ComplaintID) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    fbIns = cur.prep(SQLComment)

    CSVFileName=StagingPath+FileName+'.csv'
    RejectFile=StagingPath+RejectFileName
    RejectedRecords=pd.DataFrame()

    try:
        RejectedRecords=pd.read_csv(RejectFile)
    except Exception as e:
        print("Zero Rejects Found !!!")

    DataFrame=pd.read_csv(CSVFileName,low_memory=False)

    try:
        cur.executemany(fbIns,DataFrame.values.tolist())
    except:
        print('Rejects found in the File !!!')
        for i in range(0,len(DataFrame)):
            try:
                cur.execute(fbIns, (DataFrame.iloc[i,0],DataFrame.iloc[i,1],DataFrame.iloc[i,2],DataFrame.iloc[i,3],DataFrame.iloc[i,4],DataFrame.iloc[i,5],DataFrame.iloc[i,6],DataFrame.iloc[i,7],DataFrame.iloc[i,8],DataFrame.iloc[i,9],DataFrame.iloc[i,10],DataFrame.iloc[i,11],DataFrame.iloc[i,12],DataFrame.iloc[i,13],DataFrame.iloc[i,14],DataFrame.iloc[i,15]))
            except:
                RejectedRecords=RejectedRecords.append( {'Datereceived':DataFrame.iloc[i,0],'Product':DataFrame.iloc[i,1],'Subproduct':DataFrame.iloc[i,2],'Issue':DataFrame.iloc[i,3],'Subissue':DataFrame.iloc[i,4],'Consumercomplaintnarrative':DataFrame.iloc[i,5],'Companypublicresponse':DataFrame.iloc[i,6],'Company':DataFrame.iloc[i,7],'State':DataFrame.iloc[i,8],'ZIPcode':DataFrame.iloc[i,9],'Submittedvia':DataFrame.iloc[i,10],'Datesenttocompany':DataFrame.iloc[i,11],'Companyresponsetoconsumer':DataFrame.iloc[i,12],'Timelyresponse':DataFrame.iloc[i,13],'Consumerdisputed':DataFrame.iloc[i,14],'ComplaintID':DataFrame.iloc[i,15]}, ignore_index=True)

    con.commit()
    RejectedRecords.to_csv(RejectFile,index=False)

#Function to Delete all Records from Table
def DeleteData(TableName):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="delete from "+TableName
    fbDel = cur.prep(SQLComment)
    cur.execute(fbDel)
    con.commit()

def UpdateCopyTable(MainTable,CopyTable):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="INSERT INTO "+CopyTable+" SELECT * FROM "+MainTable
    fbInsCopy = cur.prep(SQLComment)
    cur.execute(fbInsCopy)
    con.commit()

#Function to Update Main table from Stag Table or to copy main table content to Copy table
def UpdateMainTable(MainTable,StagingTable):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="INSERT INTO "+MainTable+"(DATERECEIVED,PRODUCT,SUBPRODUCT,ISSUE,SUBISSUE,CONSUMERCOMPLAINT,COMPANYPUBLICRESPONSE,"
    SQLComment +="COMPANY,STATE,ZIPCODE,SUBMITTEDVIA,DATESENTCOMPANY,COMPANYRESPONSECONSUMER,TIMELYRESPONSESTS,CONSUMERDISPUTEDSTS,COMPLAINTID)"
    SQLComment +=' SELECT '
    SQLComment +='CASE a.DATERECEIVED WHEN \'nan\' THEN NULL ELSE CAST(a.DATERECEIVED AS DATE) END DATERECEIVED,'
    SQLComment +='CASE a.PRODUCT WHEN \'nan\' THEN NULL ELSE a.PRODUCT END PRODUCT,'
    SQLComment +='CASE a.SUBPRODUCT WHEN \'nan\' THEN NULL ELSE a.SUBPRODUCT END SUBPRODUCT, '
    SQLComment +='CASE a.ISSUE WHEN \'nan\' THEN NULL ELSE a.ISSUE END ISSUE,'
    SQLComment +='CASE a.SUBISSUE WHEN \'nan\' THEN NULL ELSE a.SUBISSUE END SUBISSUE,'
    SQLComment +='CASE a.CONSUMERCOMPLAINT WHEN \'nan\' THEN NULL ELSE a.CONSUMERCOMPLAINT END CONSUMERCOMPLAINT,'
    SQLComment +='CASE a.COMPANYPUBLICRESPONSE WHEN \'nan\' THEN NULL ELSE a.COMPANYPUBLICRESPONSE END COMPANYPUBLICRESPONSE,'
    SQLComment +='CASE a.COMPANY WHEN \'nan\' THEN NULL ELSE a.COMPANY END COMPANY,'
    SQLComment +='CASE a.STATE WHEN \'nan\' THEN NULL ELSE a.STATE END STATE,'
    SQLComment +='CASE a.ZIPCODE WHEN \'nan\' THEN NULL ELSE a.ZIPCODE END ZIPCODE,'
    SQLComment +='CASE a.SUBMITTEDVIA WHEN \'nan\' THEN NULL ELSE a.SUBMITTEDVIA END SUBMITTEDVIA,'
    SQLComment +='CASE a.DATESENTCOMPANY WHEN \'nan\' THEN NULL ELSE CAST(a.DATESENTCOMPANY AS DATE) END DATESENTCOMPANY,'
    SQLComment +='CASE a.COMPANYRESPONSECONSUMER WHEN \'nan\' THEN NULL ELSE a.COMPANYRESPONSECONSUMER END COMPANYRESPONSECONSUMER,'
    SQLComment +='CASE a.TIMELYRESPONSESTS WHEN \'nan\' THEN NULL ELSE a.TIMELYRESPONSESTS END TIMELYRESPONSESTS,'
    SQLComment +='CASE a.CONSUMERDISPUTEDSTS WHEN \'nan\' THEN NULL ELSE a.CONSUMERDISPUTEDSTS END CONSUMERDISPUTEDSTS,'
    SQLComment +='a.COMPLAINTID '
    SQLComment +='FROM '+ StagingTable+" a "
    SQLComment +="WHERE a.COMPLAINTID NOT IN (SELECT COMPLAINTID FROM "+MainTable+")"
    fbInsMain = cur.prep(SQLComment)
    cur.execute(fbInsMain)
    con.commit()

#Function to Swap View
def ViewSwap(TableName,ViewName):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="recreate view " + ViewName + " as select DateReceived,Product,SubProduct,Issue,SubIssue,ConsumerComplaint,CompanyPublicResponse,Company,State,ZIPCode,SubmittedVia,DateSentCompany,CompanyResponseConsumer,TimelyResponseSts,ConsumerDisputedSts,ComplaintID  from "+TableName
    fbSwap=cur.prep(SQLComment)
    try:
        cur.execute(fbSwap)
    except Exception as e:
        con.commit()
        raise Exception(e)
    con.commit()

#Function to Create copy table and Swap Views
def CloneTable(MainTable,CloneTable):
    DeleteData(CloneTable)
    UpdateCopyTable(MainTable,CloneTable)

#Function to Get Load Index
def GetLoadIndex(LogTable):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    IdSelComment="SELECT COALESCE(max(LoadIndex),0) FROM "+LogTable
    idcur=con.cursor()
    idcur.execute(IdSelComment)
    for LoadIndex in idcur:
        LoadIndexMax=LoadIndex[0]
    return LoadIndexMax

#function to get Record Count
def GetRecordCount(TableName,FilterValue):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    RowCntComment="SELECT COUNT(*) FROM "+TableName+" a WHERE a.PRODUCT =\'"+FilterValue+"\'"
    rowcur=con.cursor()
    rowcur.execute(RowCntComment)
    for count in rowcur:
        RowCount=count[0]
    return RowCount

#function to get Record Count of Main Table
def GetMainRecordCount(TableName,StageTableName):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    RowCntComment="SELECT COUNT(*) FROM "+StageTableName+" a WHERE a.COMPLAINTID NOT IN (SELECT COMPLAINTID FROM "+TableName+")"
    rowcur=con.cursor()
    rowcur.execute(RowCntComment)
    for count in rowcur:
        RowCount=count[0]
    return RowCount

#Get Table Count
def GetTableCount(TableName):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    RowCntComment="SELECT COUNT(*) FROM "+TableName
    rowcur=con.cursor()
    rowcur.execute(RowCntComment)
    for count in rowcur:
        RowCount=count[0]
    return RowCount

#Function to Update Log Table
def UpdateLog(LogTable,LoadIndex,LoadOrder,APICode,FileName,RecordCount,LoadStartDTTM,LoadEndDTTM):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="insert into "+LogTable+" (LoadIndex,LoadOrder,APICode,FileName,RecordCount,LoadStartDTTM,LoadEndDTTM) values (?,?,?,?,?,?,?)"
    fbLog=cur.prep(SQLComment)
    cur.execute(fbLog, (LoadIndex,LoadOrder,APICode,FileName,RecordCount,LoadStartDTTM,LoadEndDTTM))
    con.commit()

#Function to Update Main Log
def UpdateMainLog(LogTable,LoadIndex,LoadOrder,LoadStep,StepName,Status,RecordCount,LoadStartDTTM,LoadEndDTTM):
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="insert into "+LogTable+" (LoadIndex,LoadOrder,LoadStep,StepName,Status,RecordCount,LoadStartDTTM,LoadEndDTTM) values (?,?,?,?,?,?,?,?)"
    fbLog=cur.prep(SQLComment)
    cur.execute(fbLog, (LoadIndex,LoadOrder,LoadStep,StepName,Status,RecordCount,LoadStartDTTM,LoadEndDTTM))
    con.commit()


def DisplayAPILog():
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="SELECT LOADINDEX,LOADORDER,APICODE,FILENAME,RECORDCOUNT,CAST(LOADSTARTDTTM AS CHAR(24)) LOADSTARTDTTM,LOADENDDTTM,"\
               + "DATEDIFF(SECOND FROM LOADSTARTDTTM TO LOADENDDTTM) AS DURATION FROM "+LogTableName
    APILog=cur.prep(SQLComment)
    cur.execute(APILog)
    df=pd.DataFrame()
    list=[]
    for LOADINDEX,LOADORDER,APICODE,FILENAME,RECORDCOUNT,LOADSTARTDTTM,LOADENDDTTM,DURATION in cur:
        df=df.append({'LoadIndex':LOADINDEX,
                      'LoadOrder':LOADORDER,
                      'APICode':APICODE,
                      'FileName':FILENAME,
                      'RecordCount':RECORDCOUNT,
                      'LoadStartDTTM':LOADSTARTDTTM,
                      'LoadEndDTTM':LOADENDDTTM,
                      'Duration':DURATION
                      },ignore_index=True)
    con.commit()
    return df[['LoadIndex','LoadOrder','APICode','FileName','RecordCount','LoadStartDTTM','LoadEndDTTM','Duration']]

def DisplayLoadStepLog():
    global DBPath,UserName,Password
    con = fdb.connect(database=DBPath, user=UserName, password=Password)
    cur = con.cursor()
    SQLComment="SELECT LOADINDEX,LOADORDER,LOADSTEP,STEPNAME,STATUS,RECORDCOUNT,CAST(LOADSTARTDTTM AS CHAR(24)) LOADSTARTDTTM,LOADENDDTTM,"\
                +"DATEDIFF(SECOND FROM LOADSTARTDTTM TO LOADENDDTTM) AS DURATION FROM "+MainLogTable
    APILog=cur.prep(SQLComment)
    cur.execute(APILog)
    df=pd.DataFrame()
    list=[]
    for LOADINDEX,LOADORDER,LOADSTEP,STEPNAME,STATUS,RECORDCOUNT,LOADSTARTDTTM,LOADENDDTTM,DURATION in cur:
        df=df.append({'LoadIndex':LOADINDEX,
                      'LoadOrder':LOADORDER,
                      'LoadStep':LOADSTEP,
                      'StepName':STEPNAME,
                      'Status':STATUS,
                      'RecordCount':RECORDCOUNT,
                      'LoadStartDTTM':LOADSTARTDTTM,
                      'LoadEndDTTM':LOADENDDTTM,
                      'Duration':DURATION
                      },ignore_index=True)
    con.commit()
    return df[['LoadIndex','LoadOrder','LoadStep','StepName','Status','RecordCount','LoadStartDTTM','LoadEndDTTM','Duration']]