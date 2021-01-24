import pymysql
import re
import time
import nltk
from nltk.tokenize import word_tokenize

start_time = time.time()
lasttime = start_time       

# Open database connection
db = pymysql.connect("memorydb.cluster-c0usqt1uocaf.us-east-1.rds.amazonaws.com","admin","Alaska.01","Memory" )

# prepare cursor objects for Nexus and Nexus_Word tables
cursor = db.cursor()
cursorW = db.cursor()

selectsql = "SELECT NEXUS_ID, Category, Question, answer \
        FROM jeopardy "
#         LIMIT %d" % (207000)
        
insertsql = "INSERT INTO Nexus_Word (Nexus_ID, Nexus_Word) VALUES "

nid = 0     # the nexus ID we're starting with
ready = 1   # flag to say we're good to start the loop

try:
    cursor.execute("TRUNCATE TABLE Nexus_Word")
except:
    print ("Error: unable to Truncate the Nexus_Word table")
    ready = 0    
try:
    # Execute the select command
    cursor.execute(selectsql)
except:
   print ("Error: unable to fetch data")
   ready = 0
   
if ready:
    # Fetch all the rows in a list of lists.
    results = cursor.fetchall()
    for row in results:
        nid = row[0]
        allWords = re.sub(r'[\\\',;:?!|)(]', '', row[1] + " | " + row[2] + " | " + row[3]) 
        # changed to tokenized set from:  wordList = allWords.split()
        wordSet = set(word_tokenize(allWords.upper()))
        isql = insertsql
        valuecount = 0
      
        # print fetched result
        # print ("All Words=%s" % (allWords))
        for word in wordSet:
            valuecount += 1
            if valuecount > 1:
                isql  = isql + ", "  # comma between value sets
            isql  = isql + "(%d, upper('%s'))" % (nid, word)
            # print("NID: %d, %s" % (nid, word))
        
        try:
            cursorW.execute(isql)
            db.commit()
        
        except:
            print ("Error: unable to insert data")
            print (isql)
            db.rollback() 
            
        if (nid % 1000) == 0:
            print("%d --- %s seconds ---" % (nid, time.time() - lasttime))
            lasttime = time.time()
        
#  print (wordList)
print ("Complete: %d Nexus rows" % (nid))
    
# disconnect from server
db.close()
print("--- %s seconds, %s minutes ---" % (time.time() - start_time, (time.time() - start_time)/60))
