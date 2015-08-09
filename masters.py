import sqlite3
import pickle
import time
import urllib
import re
import os.path
import logging
import random
import ftplib
from StringIO import StringIO

def getTicker(inputText,cik):
    
    """
        Attempts to pull ticker from 8-Ks (it generally appears in exhibit 99.1)
    """

#    print inputText
    exchange=re.compile(r'([Nn][Yy][Ss][Ee]|[Nn][Aa][Ss][Dd][Aa][Qq])( GS)?:\W?([A-Z]{1,4})')
    result=exchange.search(inputText)

    if result!=None:
        toAdd=[cik,result.group(1),result.group(3)]
        print toAdd

        try:
            with open('data/cikExchangeTicker.pk','r') as input:
                cikExchangeTicker=pickle.load(input)
                cikExchangeTicker.append(toAdd)

        except IOError:
            print 'File probably doesn\'t exist.'
            cikExchangeTicker=[toAdd]
        finally:
            with open('data/cikExchangeTicker.pk','wb') as output:
                pickle.dump(cikExchangeTicker,output,pickle.HIGHEST_PROTOCOL)



def checkDaysFilings(masterReadlines):
    """
        Takes a master file as an argument and then spits out all the sketchy records associated with it. Should eventually break this out so that separate checks are run on 10-Ks and 8-Ks
    """
    
    with open('data/onExchange.pk', 'r') as input: onExchange=pickle.load(input)

    formsToCheck=['8-K']
    #Yields all records of publicly traded companies having certain specified forms
    linesToCheck=[line.split('|') for line in masterReadlines if line.split('|')[0].isdigit() and line.split('|')[2] in formsToCheck and line.split('|')[0] in onExchange]

    r=re.compile(r'[Mm]aterial(?:ly)? weak')
    cl=re.compile(r'continued listing')
    res=re.compile(r'resign')
    auditor=re.compile(r'Item 4[.]01')
    wells=re.compile(r'[Ww][Ee][Ll][Ll][Ss].(?![Ff][Aa][Rr][Gg][Oo])')
    wellsNotice=re.compile(r'[Ww][Ee][Ll][Ll][Ss] [Nn][Oo][Tt][Ii][Cc][Ee]|[Ww][Ee][Ll][Ll][Ss] [Ll][Ee][Tt][Tt][Ee][Rr]')
    investigation=re.compile(r'[Ss]ubpoena | [Oo][Ff] [Jj][Uu][Ss][Tt][Ii][Cc][Ee] | [Aa][Tt][Tt][Oo][Rr][Nn][Ee][Yy] [Gg][Ee][Nn][Ee][Rr][Aa][Ll]')

    regExes=[[r,'Material weakness'],[cl, 'Continued listing'],[res,'Resignation'],[wellsNotice, 'Wells Notice'],[investigation,'Poss investigation'],[auditor,'Auditor change']]


    j=len(linesToCheck)
    i=1

    output=[]

    for record in linesToCheck:
        #        print "Getting record %02d of %02d" % (i, j)

        i+=1

#######Replacing with code to just grab the file without writing to hard drive
#        getFormFromMaster(record)
#
#        with open(record[-1],'r') as f:
#            longText=f.readlines()
#
#####################################

        #This needs error-handling
        ftp=ftplib.FTP('ftp.sec.gov')
        ftp.login()
        
        j=0
        longText=getFormFromEDGAR(record,ftp)
        if longText!=None:
            
            #This should be handled with a StringIO object
            
            getTicker(longText,record[0])

            with open('temp/temp.txt','w') as shortText:
                for line in longText.split('\n'):
                    if j==2: break
                    elif line[0:10]=="<FILENAME>":
                        j+=1
                        shortText.write(line)
                    else: shortText.write(line)

            with open('temp/temp.txt','r') as shortText:
                fileText=shortText.read()

#These regexes should be handled by looping over each regex

            for line in regExes:
                ind=len(line[0].findall(fileText))
                if ind>0:
                    temp=record[:]
                    temp[0]='<a href=\"https://www.sec.gov/cgi-bin/browse-edgar?CIK='+temp[0]+'&Find=Search&owner=exclude&action=getcompany\">'+temp[0]+'</a>'
                    temp[4]='<a href=\"ftp://ftp.sec.gov/'+temp[4][:-1]+'\">Link</a>'
                    temp.extend([line[1],str(ind),'<br>'])
                    output.append(temp)
    
    
        else:
            print 'This should never appear: Skipping for record:', record
            print 'Sleeping'
            time.sleep(2)


    for line in output: print line, '\n'
    return output
    
    try:ftp.quit()
    except Exception as e:
        print e
        print e.args
        ftp.close()

#     This section works--takes 1/30th the time to read as to download
#        remoteFile='ftp://ftp.sec.gov/'+record[-1][:-1]

#        fileText=urllib.urlopen(remoteFile).read()
#        ind=len(r.findall(fileText))
#        print ind

#        print myFile

def getFormFromEDGAR(masterRecord,connection):
    
    #This is to be used when doing it the urllib way, not the ftplib way
    #    remoteFile='ftp://ftp.sec.gov/'+masterRecord[-1]
    remoteFile=masterRecord[-1]
    #print connection.getwelcome()

    gotRecord=False
    while gotRecord==False:

        t0=time.time()
        
        s=StringIO()

        try:
            #            temp=urllib.urlopen(remoteFile)
            connection.retrbinary('RETR '+remoteFile,s.write)
            #            print 'Read %s' % remoteFile
            gotRecord=True
        except IOError as e:
            print 'IOError opening %s' % remoteFile
            print e
            print e.args
        except Exception as f:
            print 'There was some other kind of error.'
            print f
            print f.args
        finally:
            delay=random.randrange(1,3,1)
#            time.sleep(delay)

#    outputText=s.getvalue().split('\n')
    outputText=s.getvalue()
    t1=time.time()
    print 'Total time:',t1-t0

    return outputText




def getFormFromMaster(masterRecord):
    """
        Checks a record from a master file to see whether the filing exists locally and, if not, retrieves it.
    """
    
    fileName=masterRecord[-1]
    
    if os.path.isfile(fileName):
        logging.debug('Filename %s already exists' % fileName)
    #        print 'Filename %s already exists' % fileName
    else:
        filePath='/'.join(fileName.split('/')[:3]) #Should really slice through -2
    
        #Now check if path exists

        if os.path.exists(filePath):
            logging.debug('Path %s already exists' % filePath)
        #            print 'Path %s already exists' % filePath

        else:
            logging.info('Needed to create path %s.' % filePath)
            #            print 'Needed to create path %s.' % filePath
            os.makedirs(filePath)

        remotePath='ftp://ftp.sec.gov/'+fileName
        logging.info('Needed to download file from %s' % remotePath)
#        print 'Needed to download file from %s' % remotePath
                                                                            
        t0=time.time()
        try: #NEED TO HANDLE EXCEPTIONS WHEN THIS CANT FIND FILE, WAIT A COUPLE SECOND THEN TRY AGAIN
            urllib.urlretrieve(remotePath,fileName)
            t1=time.time()
            print 'Total time to download: ', t1-t0

        #This seems to be the wrong type of error to report, because the exception is getting
        #thrown even when the file is downloaded
        #Also, getting errors when trying to print e.code and e.read()
        except IOError as e:
            logging.error('File %s was not downloaded due to an IOERrror' % remotePath)
            print 'Failed to download file %s because of an error' % remotePath
            t1=time.time()
            print 'Total time to suck: ', t1-t0

        except: raise

def updateWatchlistSQL(year,month,day):
    """
    Adds records from a given day's list of master records to watchlist.
    Can save for SQL code, but going to try t accomplish this with lists and pickling in near term

    """
        
#CHECK IF MASTER EXISTS AND DOWNLOAD IF NOT

    fileName='masters/masterindex'+year+month+day
    warningSigns=['NT 10-K','NT 10-Q']
    
    with open(fileName,'r') as f:
        g=[line.split('|') for line in f.readlines() if line.split('|')[0].isdigit() and line.split('|')[2] in warningSigns]

    conn=sqlite3.connect('data/watchlist.db')
    c=conn.cursor()

    try:
        c.execute('CREATE TABLE watchlist (cik TEXT, company TEXT, form TEXT, formDate TEXT)')
    except sqlite3.OperationalError as e:
        print 'Table probably already exists'

    for line in g:
        c.execute('INSERT INTO watchlist VALUES (?,?,?,?)', (line[0], line[1], line[2], line[3]))

    conn.commit()
#    c.execute('SELECT * FROM watchlist')
#    print c.fetchall()


def updateWatchlist(UWyear,UWmonth,UWday):
    """
    Adds records from a given day's list of master records to watchlist.
    Can save for SQL code, but going to try to accomplish this with lists and pickling in near term
    Given that this gets called from loopOverDates, might make sense to pass it a file obj.
    """
        
    fileName='masters/masterindex'+UWyear+UWmonth+UWday
    warningSigns=['NT 10-K','NT 10-Q']
    requiredFilings=['10-K','10-Q']

    with open('data/onExchange.pk', 'r') as input: onExchange=pickle.load(input)

    #the isdigit() code is a lazy way of checking that were getting records, as opposed to headers
    with open(fileName,'r') as f:
        g=[line.split('|') for line in f.readlines() if line.split('|')[0].isdigit() and line.split('|')[2] in warningSigns and line.split('|')[0] in onExchange]

    print "These records are sketchy", g

    #Attempts to open the watchlist and appends the data from the date just loaded
    if g: # evalutes to false if empty, presence of empty lists in watchlist would cause probs when iterating over watchlist
        try:
            with open('data/watchlist.pk', 'r') as input: temp=pickle.load(input)

#This block of commented out stuff does not appear to work, at least in part because
#removeLaterFiled does not return anything
            #First removes items from watchlist
            #            with open(fileName,'r') as f: #Gets records of 10-Ks etc for ciks that were already on watchlist
            #                laterFiling=f.readlines()
            #            temp=removeLaterFiled(temp,laterFiling)

#            temp.extend(g)

        except IOError:
            print 'File probably doesn\'t exist'
            #            temp=g #Consider this part of block commented out above

        finally:
            pass
            #Remove items from watchlist
            
            #Outputs updated watchlist
            #            with open('data/watchlist.pk', 'wb') as output:
                #                pickle.dump(temp,output,pickle.HIGHEST_PROTOCOL) #Consider this part of block commented out above.
    else: pass

def removeLaterFiled(myWatchlist,fileAsList):
    """
        Once the watchlist exists, this program is run prior to incorporating a new days master data into the watchlist.
        Function takes watchlist and a file (containing latest master data) read in as list. It first identifies which CIKs can be found in the watchlist.
        It then checks whether those CIKs are in the latest master data and are associated with corrective filings (currently defined as 10-ks and 10-qs but should
        eventually be determined based on initial filing)
        It then updates the watchlist it took as an argument
    """
    requiredFilings=['10-K','10-Q']

#    with open('data/watchlist.pk', 'r') as input: watchlist=pickle.load(input)
    #print watchlist
    #want to define list comprehension that iterates over watchlist and adds only those items for which a corrective filing was not made within the appropriate amount of time
    uniques=getUniqueCiks(myWatchlist)
    #Creates list comprehension from more recent filing where cik matches that of one already on watchlist--ie a corrective filing was made
    correctiveFilings=[line.split('|') for line in fileAsList if line.split('|')[0] in uniques and line.split('|')[2] in requiredFilings]
    print 'Records that represent corrective filings', correctiveFilings

    correctiveUniques=getUniqueCiks(correctiveFilings)

def filedCorrective(myWatchlist):
    pass


def getUniqueCiks(myWatchlist):

    uniqueCiks=[]
    for line in myWatchlist:

        if line[0] not in uniqueCiks: uniqueCiks.append(line[0])
        else: pass

    return uniqueCiks

def onExchange(f):
    """
        Goes through master file (f) and identifies which CIKs are associated with proxy-related filings.
        The fact of a companys filing one of these is taken to mean its traded on exchange.
    """

    #These are the flinings I believe to be associated with being publicly traded
    #Filings that should not be included: PREM14A & DEFM14A (concern mergers)
    #DEF 14A can be associated with consent solicitations, other proposals and have no references to exchanges
    #DEFA14A was assocaited with a company traded on foreign exchange (Acucela).
    #Additional materials filings seem not to contain useful information.
    #If/when we ultimately look through these filings, will want to check for New York Stock Exchange in addition
    #to NYSE, since, e.g., Joy Global refers to it as such in its 14A
    #Text searches may yield false positives since D&Os qualifications may include their service on NASDAQ/NYSE
    #listed companies
    #'DEFA14A','PRER14A' seem not to contain actual info re NASDAQ/NSYE
    keyFilings=['DEF 14A','PRE 14A']

    #Creates set of ciks
    a={line.split('|')[0] for line in f.readlines() if line.split('|')[0].isdigit() and line.split('|')[2] in keyFilings}

    #Attempts to open list of ciks that are traded and appends the data from the date just loaded

    try:
        with open('data/onExchange.pk', 'r') as input: temp=pickle.load(input)
#        temp.add(a)
        for element in a:
            temp.add(element)
        
    except IOError:
        print 'File probably doesn\'t exist'
        temp=a

    #Outputs updated list
    with open('data/onExchange.pk', 'wb') as output: pickle.dump(temp,output,pickle.HIGHEST_PROTOCOL)

#    print temp
#    print len(temp)
#    print '\n'
