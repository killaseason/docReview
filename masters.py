import sqlite3
import pickle
import time

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


def updateWatchlist(year,month,day):
    """
    Adds records from a given day's list of master records to watchlist.
    Can save for SQL code, but going to try to accomplish this with lists and pickling in near term
    """
        
        #CHECK IF MASTER EXISTS AND DOWNLOAD IF NOT
        
    fileName='masters/masterindex'+year+month+day
    warningSigns=['NT 10-K','NT 10-Q']
    requiredFilings=['10-K','10-Q']

    #the isdigit() code is a lazy way of checking that were getting records, as opposed to headers
    with open(fileName,'r') as f:
        g=[line.split('|') for line in f.readlines() if line.split('|')[0].isdigit() and line.split('|')[2] in warningSigns]

    #Attempts to open the watchlist and appends the data from the date just loaded
    if g: # evalutes to false if empty, presence of empty lists in watchlist would cause probs when iterating over watchlist
        try:
            with open('data/watchlist.pk', 'r') as input: temp=pickle.load(input)

            #First removes items from watchlist
            with open(fileName,'r') as f: #Gets records of 10-Ks etc for ciks that were already on watchlist
                laterFiling=f.readlines()
            temp=removeLaterFiled(temp,laterFiling)
            
            
            


            temp.extend(g)

        except IOError:
            print 'File probably doesn\'t exist'
            temp=g

        finally:
            #Remove items from watchlist
            
            #Outputs updated watchlist
            with open('data/watchlist.pk', 'wb') as output:
                pickle.dump(temp,output,pickle.HIGHEST_PROTOCOL)
                    
    else: pass

def removeLaterFiled(myWatchlist,fileAsList):
    """
        Once the watchlist exists, this program is run prior to incorporating a new days master data into the watchlist.
        Function takes watchlist and a file (containing latest master data) read in as list. It first identifies which CIKs can be found in the watchlist.
        It then checks whether those CIKs are in the latest master data and are associated with corrective filings (currently defined as 10-ks and 10-qs but should
        eventually be determined based on initial filing)
        It then updates the watchlist it took as an argument
    """
    
#    with open('data/watchlist.pk', 'r') as input: watchlist=pickle.load(input)
    #print watchlist
    #want to define list comprehension that iterates over watchlist and adds only those items for which a corrective filing was not made within the appropriate amount of time
    uniques=getUniqueCiks(myWatchlist)
    #Creates list comprehension from more recent filing where cik matches that of one already on watchlist--ie a corrective filing was made
    correctiveFilings=[line.split('|') for line in fileAsList if line.split('|')[0] in uniques and line.split('|')[2] in requiredFilings]
    print 'Records that represent corrective filings', h

    correctiveUniques=getUniqueCiks(correctiveFilings)

def filedCorrective(myWatchlist):



def getUniqueCiks(myWatchlist):

    uniqueCiks=[]
    for line in myWatchlist:

        if line[0] not in uniqueCiks: uniqueCiks.append(line[0])
        else: pass

    return uniqueCiks



