import os,configparser

def getParam():

    WorkingDirectory=os.getcwd()
    ConfigFilePath=WorkingDirectory+"\\config.ini"
    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(ConfigFilePath)
    DatabasePath=WorkingDirectory+settings.get('General', 'DatabasePath')
    StagingPath=WorkingDirectory+settings.get('General', 'StagingPath')
    APIView=settings.get('General', 'APIView')
    APICategory=settings.get('General', 'APICategory')
    BaseURl=settings.get('General', 'BaseURl')
    DBName=settings.get('General', 'DBName')
    UserName=settings.get('General', 'UserName')
    Password=settings.get('General', 'Password')
    RejectFileName=settings.get('General', 'RejectFileName')
    TableName=settings.get('General', 'TableName')
    StagTableName=settings.get('General', 'StagTableName')
    CloneTableName=settings.get('General', 'CloneTableName')
    LogTableName=settings.get('General', 'LogTableName')
    LogFileName=DatabasePath+settings.get('General', 'LogFileName')
    LogFileTrig=DatabasePath+settings.get('General', 'LogFileTrig')
    ViewName=settings.get('General', 'ViewName')
    FilterValue=settings.get('General', 'FilterValue')
    MainLogTableName=settings.get('General', 'MainLogTableName')
    LogPath=WorkingDirectory+settings.get('General', 'LogPath')

    ReturnList=[WorkingDirectory,DatabasePath,StagingPath,APIView,APICategory,BaseURl,
                DBName,UserName,Password,RejectFileName,TableName,
                StagTableName,CloneTableName,LogTableName,LogFileName,LogFileTrig,
                ViewName,FilterValue,MainLogTableName,LogPath]
    return(ReturnList)
