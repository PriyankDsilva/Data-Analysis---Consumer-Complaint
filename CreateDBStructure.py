import fdb
import Initialize

InitialParameters=Initialize.getParam()
DBLocation=InitialParameters[1]
DBName=InitialParameters[6]
UserName=InitialParameters[7]
Password=InitialParameters[8]

DBPath=DBLocation+DBName
CreateComment="create database '"+str(DBPath)+"' user '"+str(UserName)+"' password '"+str(Password)+"'"

print('DatabasePath :',DBPath)
con = fdb.create_database(CreateComment)
print("Database (",DBName,") created Sucessfully .")
con = fdb.connect(database=DBPath, user=UserName, password=Password)
cur = con.cursor()
cur.execute("recreate table consumercomplaint (DateReceived date,Product varchar(100),SubProduct varchar(100),Issue varchar(100),SubIssue varchar(100),ConsumerComplaint varchar(5000),CompanyPublicResponse varchar(5000),Company varchar(100),State varchar(5),ZIPCode varchar(10),SubmittedVia varchar(20),DateSentCompany date,CompanyResponseConsumer varchar(100),TimelyResponseSts varchar(5),ConsumerDisputedSts varchar(5),ComplaintID int)")
con.commit()
print("Table ConsumerComplaint created Sucessfully .")
cur.execute("create unique index unique_ComplaintID on consumercomplaint(ComplaintID)")
con.commit()
print("Uniqie Index on ConsumerComplaint(ComplaintID)created Sucessfully .")
cur.execute("recreate table consumercomplaint_staging (DateReceived varchar(100),Product varchar(100),SubProduct varchar(100),Issue varchar(100),SubIssue varchar(100),ConsumerComplaint varchar(5000),CompanyPublicResponse varchar(5000),Company varchar(100),State varchar(50),ZIPCode varchar(100),SubmittedVia varchar(100),DateSentCompany varchar(100),CompanyResponseConsumer varchar(100),TimelyResponseSts varchar(10),ConsumerDisputedSts varchar(10),ComplaintID int)")
con.commit()
print("Table consumercomplaint_staging created Sucessfully .")
cur.execute("recreate view ConsumerComplaintView as select DateReceived,Product,SubProduct,Issue,SubIssue,ConsumerComplaint,CompanyPublicResponse,Company,State,ZIPCode,SubmittedVia,DateSentCompany,CompanyResponseConsumer,TimelyResponseSts,ConsumerDisputedSts,ComplaintID  from consumercomplaint")
con.commit()
print("View ConsumerComplaintView created Sucessfully .")
cur.execute("recreate table consumercomplaint_copy (DateReceived date,Product varchar(100),SubProduct varchar(100),Issue varchar(100),SubIssue varchar(100),ConsumerComplaint varchar(5000),CompanyPublicResponse varchar(5000),Company varchar(100),State varchar(5),ZIPCode varchar(10),SubmittedVia varchar(20),DateSentCompany date,CompanyResponseConsumer varchar(100),TimelyResponseSts varchar(5),ConsumerDisputedSts varchar(5),ComplaintID int)")
con.commit()
print("Table ConsumerComplaintCopy created Sucessfully .")

cur.execute("recreate table consumercomplaint_log (LoadIndex int,LoadOrder int,APICode varchar(20),FileName varchar(50), RecordCount int,LoadStartDTTM timestamp,LoadEndDTTM timestamp)")
con.commit()
print("Table consumercomplaint_Log created Sucessfully .")

cur.execute("recreate table consumercomplaint_mainlog (LoadIndex int,LoadOrder int,LoadStep varchar(20),StepName varchar(200),Status varchar(200), RecordCount int,LoadStartDTTM timestamp,LoadEndDTTM timestamp)")
con.commit()
print("Table consumercomplaint_Log created Sucessfully .")



#con.drop_database()
#print("Database Dropped.")