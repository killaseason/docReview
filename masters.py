import sqlite3
import pickle
import datetime
import time
import urllib
import re
import os.path
import logging
import random
import ftplib
from StringIO import StringIO
import xml.etree.ElementTree as ET


#Converts date in YYYYMMDD format to date object
def toDate(din):
    dout=datetime.date(int(din[:4]),int(din[4:6]),int(din[6:8]))
    return dout

def makeThreatIndex(warningSigns):

    index=0
    flags=''

    for sign in warningSigns:
        if flags=='': flags=sign[0]
        else: flags=flags+', '+sign[0]
        if sign[0]=='Resignation': index+=1
        elif sign[0]=='Poss investigation': index+=3
        elif sign[0]=='Continued listing': index+=1
        elif sign[0]=='Material weakness': index+=1
        elif sign[0]=='Wells Notice': index+=5
        elif sign[0]=='Auditor change': index+=2
        else: print 'Not handling ',sign[0]
    
    return flags, index


def updateWatchlist(outputBlock):

    """

    """

    inc = datetime.timedelta(days=180)
    print inc

    try:
        with open('data/watchlist.pk', 'r') as f: watchlist=pickle.load(f)
        for line in watchlist: print 'line[1]:', line[1]
        #Only keeping track of events for past 180 days.
        newWatchlist=[line for line in watchlist if line[1]+inc>datetime.date.today()]
        
        print watchlist

    except IOError as e:
        print e
        print e.args
        newWatchlist=[]

    toAdd=[[line[0],toDate(line[3]),makeThreatIndex(line[4])[0], makeThreatIndex(line[4])[1]] for line in outputBlock]

    if newWatchlist:    newWatchlist.extend(toAdd)
    else: newWatchlist=toAdd
    with open('data/watchlist.pk','wb') as output: pickle.dump(newWatchlist,output,pickle.HIGHEST_PROTOCOL)

    print toAdd
    print newWatchlist


    #the isdigit() code is a lazy way of checking that were getting records, as opposed to headers
    #    with open(fileName,'r') as f:
    #     g=[line.split('|') for line in f.readlines() if line.split('|')[0].isdigit() and line.split('|')[2] in warningSigns and line.split('|')[0] in onExchange]
    
#    print "These records are sketchy", g

#Attempts to open the watchlist and appends the data from the date just loaded
#if g: # evalutes to false if empty, presence of empty lists in watchlist would cause probs when iterating over watchlist
#   try:
#       with open('data/watchlist.pk', 'r') as input: temp=pickle.load(input)
        
        #This block of commented out stuff does not appear to work, at least in part because
        #removeLaterFiled does not return anything
        #First removes items from watchlist
        #            with open(fileName,'r') as f: #Gets records of 10-Ks etc for ciks that were already on watchlist
        #                laterFiling=f.readlines()
        #            temp=removeLaterFiled(temp,laterFiling)
        
        #            temp.extend(g)
        
        #       except IOError:
        #   print 'File probably doesn\'t exist'
    #            temp=g #Consider this part of block commented out above

#    finally:
#       pass
#Remove items from watchlist

#Outputs updated watchlist
#            with open('data/watchlist.pk', 'wb') as output:
#                pickle.dump(temp,output,pickle.HIGHEST_PROTOCOL) #Consider this part of block commented out above.
#else: pass

def writeOutput(outputBlock,opYear,opMonth,opDay):

    outputFile='output/output_TESTING'+opYear+opMonth+opDay+'.html'

    with open(outputFile,'w') as HTMLOutput:
        HTMLOutput.write('<table border=\"1\"><tr><th><b>CIK</b></th><th><b>Company Name</b></th><th><b>Form</b></th><th><b>Date Filed</b></th><th><b>Flag (#)</b></th><th>Matched Terms</th><th>Stock Price</th><th>1Day</th><th>50Day</th><th>200Day</th><th>Cap</th></tr>')
        for line in outputBlock:
            #Kind of janky, because last entry is just a key
            HTMLOutput.write(' '.join(line))
        HTMLOutput.write('</table>')


def formatOutput(outputBlock):
    """
        Adds HTML tags to output so that it will display nicely when written to file
    """
    
    formattedResults=[]
    
    for line in outputBlock:
        
        yahooData=getYahooData(line[0])
        yahooLink=getYahooLink(line[0])
        
        col0='<tr><td><a href=\"https://www.sec.gov/cgi-bin/browse-edgar?CIK='+line[0]+'&Find=Search&owner=exclude&action=getcompany\">'+line[0]+'</a></td>'
        col1='<td>'+line[1][0:20].title()+'</td>'
        col2=line[2] #Already formatted to have <td> tags
        col3='<td>'+line[3]+'</td>'
        col4a=[rec[0]+' ('+str(rec[2])+')' for rec in line[4]]
        col4b='<br>'.join(col4a)
        col4='<td>'+col4b+'</td>'
        col5a=[', '.join(rec[1]) for rec in line[5]]
        col5='<td>'+'<br>'.join(col5a)+'</td>'
        col6='<td>'+yahooLink+'</td>'
        col7='<td>'+yahooData[0]+'</td>'
        col8='<td>'+yahooData[1]+'</td>'
        col9='<td>'+yahooData[2]+'</td>'
        col10='<td>'+yahooData[3]+'</td></tr>'
        if yahooData==['Multiple tickers!','Multiple tickers!','Multiple tickers!','Multiple tickers!'] or yahooData==['No ticker!','No ticker!','No ticker!','No ticker!']:
            noData=1
        else: noData=0

        print '****yahoodata and nodata', yahooData,noData
        print [col0,col1,col2,col3,col4,col5,col6,col7,col8,col9,col10]
        formattedResults.append([col0,col1,col2,col3,col4,col5,col6,col7,col8,col9,col10,noData])
    
    formattedResults.sort(key=lambda l:[l[11],l[1]])
    print '******FORMATTED RESULTS**********', formattedResults
    returnVal=[line[0:11] for line in formattedResults]
    print returnVal
    return returnVal


def getHtmFile(record,toSearch):
    """
        Searches through text file and attempts to return the .htm file associated w filing
    """
    
    fileName=re.compile(r'<FILENAME>([A-Za-z0-9-_]*[.]htm)')
    htmResult=fileName.search(toSearch)

    if htmResult!=None:
        filePart1='/'.join(record[4].split('/')[0:3])
        fileStep1=record[4][:-5].split('/')[-1]
        filePart2=''.join(fileStep1.split('-'))
        htmLink=filePart1+'/'+filePart2+'/'+htmResult.group(1)
        return '<td><a href=\"https://www.sec.gov/Archives/'+htmLink+'\">'+record[2]+'</a></td>'

    else:
        return '<td><a href=\"ftp://ftp.sec.gov/'+record[4][:-1]+'\">'+record[2]+'</a></td>'


def stripExhibits(input):
    #    print 'running'
    temp=StringIO()

    j=0
    for line in input.split('\n'):
        if j==2:
            print 'encountered second filename'
            break
        elif line[0:10]=="<FILENAME>":
            print 'found one', line
            j+=1
            temp.write(line)
        else:
            #            'no prob here', line
            temp.write(line)
    return temp.getvalue()

#return '\n'.join(temp)

def check8K(record,input,regExes,year,month,day):
    """
        For some reason has already retrieved the full text file (input)
    """
    print 'Running check8K on', record

    htmFileName=getHtmFile(record,input)
            
    #Matches cik to ticker (should only really be run on 8-Ks before theyre trimmed
    getTicker(input,record[0])
    
    fileText=stripExhibits(input)

    warningSigns=[]

    #This section is completely fucked up and unmanageable.
    for line in regExes:
        hits=line[0].findall(fileText)
        uniqueHits=set()
        for hit in hits: uniqueHits.add(hit)
        ind=len(hits)
        
        #If there are one or more hits for a given regex, save for later display.
        if ind>0: warningSigns.append([line[1],uniqueHits,len(hits)])

    #This is the preferred way to test for non-empty list
    if warningSigns:
            
        temp=record[0:-1]
        print 'printing temp',temp

        cik=temp[0]

    #    yahooLink=getYahooLink(cik)
    #    yahooData=getYahooData(cik)
                    
        col0=cik
        col1=temp[1][0:20].title()
        col2=htmFileName
        col3=temp[3]
        col4=warningSigns
        col5=warningSigns

        return [col0,col1,col2,col3,col4,col5]

    else: return None

def checkForm4(record,input):
    """
        Cleans XML file, reads in into a block of data, appends to existing block associated with cik
        and then checks for profits.
    """
    print '****record', record
    #    print '****longtext', input
    
    #Should grab ticker and add to list of mappings.
    
    i=0
    lines=input.split('\n')
    for line in lines:
        i+=1
        if line[:5]=="<?xml":
            print '***found xml***'
            start=i
        elif line=="</ownershipDocument>":
            print '***found ownersh***'
            end=i
        else: pass

#Not sure why, but could not get code to work with StringIO, so had to use file
#    XMLFile=StringIO()
#    XMLFile.writelines(lines[start-1:end])
#    print '***XMLFile', XMLFile.getvalue()

    with open('temp/XML.xml','w') as XMLFile:
        XMLFile.writelines(lines[start-1:end])
    with open('temp/XML.xml','r') as XMLFile:
        tree=ET.parse(XMLFile)

    toAdd=[]

#Should really be testing to make sure the values we're getting are at least consistent in type with values we're expecting

    x=tree.find('issuer')
    issuerCik=x[0].text.lstrip('0')
    symbol=x[2].text
    addMapping([issuerCik,'DKDK',symbol],'999')

    y=tree.find('reportingOwner')
    z=y.find('reportingOwnerId')
    ownerCik=z[0].text.lstrip('0')

    aa=y.find('reportingOwnerRelationship')

    (isD,isO,is10P,isOther)=('0','0','0','0') #Defining these is risky
    for e in aa:
        if e.tag=='isDirector': isD=e.text
        elif e.tag=='isOfficer': isO=e.text
        elif e.tag=='isTenPercentOwner': is10P=e.text
        elif e.tag=='isOther': isOther=e.text
        else: print '***Unrecognized tag to describe owner***'


    for a in tree.findall('nonDerivativeTable'):
        for b in a.findall('nonDerivativeTransaction'): #does this for each of multiple transactions
            title=''
            transDate=None
            amount=None
            for c in b.iter(): #Each c should be a <nonDerivativeTransaction>, and constitutes its own record
                #Also not sure why using b.iter() as opposed to b
                if c.tag=='securityTitle': title=c[0].text
                elif c.tag=='transactionDate': transDate=''.join(c[0].text.split('-'))
                elif c.tag=='transactionCoding':
                    code=c[1].text
                    isSwap=c[2].text
                elif c.tag=='transactionAmounts':
                    shares=c[0][0].text
                    price=c[1][0].text
                    AD=c[2][0].text
                elif c.tag=='ownershipNature':
                    DI=c[0][0].text
                    try: nature=c[1][0].text
                    except IndexError: nature='' #Sometimes this element won't be in the XML file
                elif c.tag in (['postTransactionAmounts']): pass
                else: print '***Unrecognized tag', c.tag
            toAdd.append([issuerCik,ownerCik,isD,isO,is10P,isOther,title,transDate,code,isSwap,shares,price,AD,DI,nature])
            for c in b:
                print '***testing***'
                print c.tag
            print toAdd



def isNotOTC(cik):
    """
        Want to check if something is traded OTC. If not, we should review its forms.
    """

    with open('data/cikExchangeTicker.pk','r') as f: mappings=pickle.load(f)

    currentMapping=[line for line in mappings if line[0]==cik]

    if currentMapping==[]: return True
    else:
        if currentMapping[0][1]=='OTC': return False
        else: return True


def checkMappings():
    """
        Checks that for all cik-ticker mappings, looking up the ticker on EDGAR gets to page associated with the cik
    """

    with open('data/cikExchangeTicker.pk','r') as f: mappings=pickle.load(f)

    newMappings=[]

    for mapping in mappings:
        print 'Checking ticker symbol:',mapping[2]
        if checkMapping(mapping): newMappings.append(mapping)

    with open('data/cikExchangeTicker.pk','wb') as output:pickle.dump(newMappings,output,pickle.HIGHEST_PROTOCOL)

def checkMapping(input):
    """
        Takes a cik-exchange-ticker mapping and checks that an EDGAR search for the ticker returns the page for the mapping.
    """

    r=re.compile(r'(CIK=)([0-9]{10})')

    f=urllib.urlopen('https://www.sec.gov/cgi-bin/browse-edgar?CIK='+input[2]+'&Find=Search&owner=exclude&action=getcompany')

#    with open('temp/EDGAR.txt','r') as f: g=f.read()
    g=f.read()
    result=r.search(g)
    if result==None:
        print '**ERROR** ticker ',input[2],' matches to no cik'
        return False
    else:
        returnedCik=result.group(2).lstrip('0')
        if input[0]==returnedCik:
            print 'Matched:', input[0],returnedCik
            return True
        else:
            print '**NO MATCH**:', input[0],returnedCik
            return False

#    print f.read()


def getYahooData(cik):
    """
        Returns a 4-element list, of data from a YQL query and/or error messages.
    """
    
    with open('data/cikExchangeTicker.pk','r') as f: g=pickle.load(f)
    links=[rec for rec in g if rec[0]==cik]
    print cik, links, len(links)
    
    if len(links)>1:
        return ['Multiple tickers!','Multiple tickers!','Multiple tickers!','Multiple tickers!']
    elif len(links)==0:
        return ['No ticker!','No ticker!','No ticker!','No ticker!']
    else:

        YQL='https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(%22'+links[0][2]+'%22)&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys'
    
        tree=ET.parse(urllib.urlopen(YQL))
        root=tree.getroot()
    
        #This is a truly terrible way to do this: there could be multiple nodes
        for node in root.iter('ChangeinPercent'):
            change1Day=node.text
            if change1Day==None: change1Day='N/A'
        for node in root.iter('MarketCapitalization'):
            marketCap=node.text
            if marketCap==None: marketCap='N/A'
        for node in root.iter('PercentChangeFromTwoHundreddayMovingAverage'):
            change200Days=node.text
            if change200Days==None: change200Days='N/A'
        for node in root.iter('PercentChangeFromFiftydayMovingAverage'):
            change50Days=node.text
            if change50Days==None: change50Days='N/A'
    
        print [change1Day,change50Days,change200Days,marketCap]
        return [change1Day,change50Days,change200Days,marketCap]

def getYahooLink(cik):

    """
        Returns a link to (hopefully) the Yahoo page with the company's financial info.
        
    """
    
    with open('data/cikExchangeTicker.pk','r') as f: g=pickle.load(f)
    links=[rec for rec in g if rec[0]==cik]
    print cik, links, len(links)

    if len(links)>1: myVal='Multiple tickers!'
    elif len(links)==0: myVal='No ticker!'
    else: myVal='<a href=\"http://finance.yahoo.com/q?s='+links[0][2]+'\">'+links[0][2]+'</a>'

    return myVal

def removeMapping(toRemove):

    with open('data/cikExchangeTicker.pk','r') as input: cikExchangeTicker=pickle.load(input)

    try:
        cikExchangeTicker.remove(toRemove)
        print 'Removed the following mapping: ', toRemove
        with open('data/cikExchangeTicker.pk','wb') as output:
            pickle.dump(cikExchangeTicker,output,pickle.HIGHEST_PROTOCOL)

    except ValueError: print 'Mapping not removed; not in database: ', toRemove


def addMapping(toAdd,flag):
    """
        Checks if proposed mapping of [cik, exchange, ticker] exists, then checks if its valid, then checks if cik mapped to s.t else
        if flag='m' (manual), we dont care if its a valid mapping
    """
    try:
        with open('data/cikExchangeTicker.pk','r') as input:
            cikExchangeTicker=pickle.load(input)
            if toAdd not in cikExchangeTicker:
                if checkMapping(toAdd) or flag=='m': #if valid mapping or manual override
                    uniques={company[0] for company in cikExchangeTicker}
                    if toAdd[0] not in uniques: #Making sure mapping for cik doesn't exist
                        cikExchangeTicker.append(toAdd)
                        print 'Added mapping', toAdd
                    else:
                        currentMapping=[entry for entry in cikExchangeTicker if entry[0]==toAdd[0]]
                        print 'Current mappings are:', currentMapping,'. Add:',toAdd,'?'
                elif not checkMapping(toAdd) and flag!='m':
                    print toAdd, ' is not a valid mapping; did not add.'
                else:
                    print 'This line should never print.'
                    raise
            else: print toAdd, 'already in mapping'
        
    except IOError:
        print 'File probably doesn\'t exist.'
        cikExchangeTicker=[toAdd]
    finally:
        with open('data/cikExchangeTicker.pk','wb') as output:
            pickle.dump(cikExchangeTicker,output,pickle.HIGHEST_PROTOCOL)

def getTicker(inputText,cik):
    
    """
        Attempts to pull ticker from 8-Ks (it generally appears in exhibit 99.1)
    """

#    print inputText
#    exchange=re.compile(r'([Nn][Yy][Ss][Ee]|[Nn][Aa][Ss][Dd][Aa][Qq]|OTC)( GS)?:\W?([A-Z]{1,4})')
    exchange=re.compile(r'([Nn][Yy][Ss][Ee]|[Nn][Aa][Ss][Dd][Aa][Qq]|OTC)( GS)?:\W?([A-Z]{1,4})')
    result=exchange.search(inputText)

    if result!=None:
        #Adds [CIK, Exchange, Ticker]
        toAdd=[cik,result.group(1).upper(),result.group(3)]
        #        print toAdd

        try:
            with open('data/cikExchangeTicker.pk','r') as input:
                cikExchangeTicker=pickle.load(input)
                if toAdd not in cikExchangeTicker:
                    if checkMapping(toAdd):
                        uniques={company[0] for company in cikExchangeTicker}
                        if toAdd[0] not in uniques:
                            cikExchangeTicker.append(toAdd)
                            print 'Added mapping', toAdd
                        else:
                            currentMapping=[entry for entry in cikExchangeTicker if entry[0]==toAdd[0]]
                            print 'Current mappings are:', currentMapping,'. Add:',toAdd,'?'
                    else: print toAdd, ' is not a valid mapping; did not add.'
                else: print toAdd, 'already in mapping'

        except IOError:
            print 'File probably doesn\'t exist.'
            cikExchangeTicker=[toAdd]
        finally:
            with open('data/cikExchangeTicker.pk','wb') as output:
                pickle.dump(cikExchangeTicker,output,pickle.HIGHEST_PROTOCOL)
    else: print 'Could not find a ticker.'



def checkDaysFilings(masterReadlines,year,month,day):
    """
        Takes a master file as an argument and then spits out all the sketchy records associated with it. Should eventually break this out so that separate checks are run on 10-Ks and 8-Ks
    """
    
    with open('data/onExchange.pk', 'r') as input: onExchange=pickle.load(input)

    formsToCheck=['8-K','6-K','20-F','10-Q','10-K','NT 10-Q','10-K/A','10-Q/A','NT 20-F']
#    formsToCheck=['10-Q','10-K','NT 10-Q','10-K/A','10-Q/A']
#    formsToCheck=['10-K','NT 10-Q','10-K/A','10-Q/A']
#    formsToCheck=['10-Q']
#    formsToCheck=['10-Q','8-K','6-K']
#    formsToCheck=['6-K','20-F']
#    formsToCheck=['20-F','10-Q','10-K','NT 10-Q','10-K/A','10-Q/A','NT 20-F']
#    formsToCheck=['4']

    linesToCheck=[line.split('|') for line in masterReadlines if line.split('|')[0].isdigit() and line.split('|')[2] in formsToCheck and isNotOTC(line.split('|')[0])]
 
    print 'We have %02d lines to check' % len(linesToCheck)

    r=re.compile(r'[Mm]aterial(?:ly)? weak')
    cl=re.compile(r'continued listing')
    res=re.compile(r'resign')
    auditor=re.compile(r'Item 4[.]01')
    wells=re.compile(r'[Ww][Ee][Ll][Ll][Ss].(?![Ff][Aa][Rr][Gg][Oo])')
    wellsNotice=re.compile(r'[Ww][Ee][Ll][Ll][Ss] [Nn][Oo][Tt][Ii][Cc][Ee]|[Ww][Ee][Ll][Ll][Ss] [Ll][Ee][Tt][Tt][Ee][Rr]')
    investigation=re.compile(r'[Ss]ubpoena | [Oo][Ff] [Jj][Uu][Ss][Tt][Ii][Cc][Ee] | [Aa][Tt][Tt][Oo][Rr][Nn][Ee][Yy] [Gg][Ee][Nn][Ee][Rr][Aa][Ll]')
    misstatement=re.compile(r'[Mm][Aa][Tt][Ee][Rr][Ii][Aa][Ll] [Mm][Ii][Ss][Ss][Tt][Aa][Tt][Ee]')
    impairment=re.compile(r'[Ii][Mm][Pp][Aa][Ii][Rr][Mm][Ee][Nn][Tt]')

    regExes=[[r,'Material weakness'],[cl, 'Continued listing'],[res,'Resignation'],[wellsNotice, 'Wells Notice'],[investigation,'Poss investigation'],[auditor,'Auditor change'],[misstatement,'Mat. misstatement'],[impairment,'Impairment']]


    newOutput=[]

    j=len(linesToCheck)
    i=1

    output=[]

    for record in linesToCheck:
        print "Getting record %02d of %02d" % (i, j)

        i+=1

        #This needs error-handling
        ftp=ftplib.FTP('ftp.sec.gov')
        ftp.login()
        
        j=0
        longText=getFormFromEDGAR(record,ftp)
        if longText!=None:
            
            if record[2] in ['8-K','6-K','20-F','10-Q','10-K','NT 10-Q','10-K/A','10-Q/A','NT 20-F']:
                tempResult=check8K(record,longText,regExes,year,month,day)
                if tempResult!=None:
                    newOutput.append(tempResult)
        
            elif record[2] in ['4']:
                checkForm4(record,longText)

            else:
                fileName=re.compile(r'<FILENAME>([A-Za-z0-9-_]*[.]htm)')
                htmResult=fileName.search(longText)
                if htmResult!=None:
                    htmFile=htmResult.group(1)
            #                print htmFile
                else: print 'No matching .htm file'


            #Matches cik to ticker (should only really be run on 8-Ks before theyre trimmed
                getTicker(longText,record[0])

            #This segment should be handled with a StringIO object

                with open('temp/temp.txt','w') as shortText:
                    for line in longText.split('\n'):
                        if j==2: break
                        elif line[0:10]=="<FILENAME>":
                            j+=1
                            shortText.write(line)
                        else: shortText.write(line)

                with open('temp/temp.txt','r') as shortText:
                    fileText=shortText.read()

#This section is completely fucked up and unmanageable.
                for line in regExes:
                    hits=line[0].findall(fileText)
                    uniqueHits=set()
                    for hit in hits: uniqueHits.add(hit)
                    ind=len(hits)
                    if ind>0:
                        temp=record[0:-1]
                    #                    print temp
                        yahooLink=getYahooLink(temp[0])
                        yahooData=getYahooData(temp[0])

                        temp[0]='<tr><td><a href=\"https://www.sec.gov/cgi-bin/browse-edgar?CIK='+temp[0]+'&Find=Search&owner=exclude&action=getcompany\">'+temp[0]+'</a></td>'
                        temp[1]='<td>'+temp[1][0:20].title()+'</td>'
                    #                    temp[2]='<td>'+temp[2]+'</td>'
                        if htmResult!=None:
                            filePart1='/'.join(record[4].split('/')[0:3])
                            fileStep1=record[4][:-5].split('/')[-1]
                            filePart2=''.join(fileStep1.split('-'))
                            htmLink=filePart1+'/'+filePart2+'/'+htmFile
                            temp[2]='<td><a href=\"https://www.sec.gov/Archives/'+htmLink+'\">'+temp[2]+'</a></td>'
                        else: temp[2]='<td><a href=\"ftp://ftp.sec.gov/'+record[4][:-1]+'\">'+temp[2]+'</a></td>'
                        temp[3]='<td>'+temp[3]+'</td>'
                    #                    print someText
                    


                        temp.extend(['<td>'+line[1]+'</td>','<td>'+', '.join(uniqueHits)+'</td>','<td>'+str(ind)+'</td><td>'+yahooLink+'</td><td>'+yahooData[0]+'</td><td>'+yahooData[1]+'</td><td>'+yahooData[2]+'</td><td>'+yahooData[3]+'</td></tr>'])
                        output.append(temp)
    
    
        else:
            print 'This should never appear: Skipping for record:', record
            print 'Sleeping'
            time.sleep(2)


#    for line in output: print line, '\n'

    try:ftp.quit()
    except Exception as e:
        print e
        print e.args
        ftp.close()
    
    updateWatchlist(newOutput)
    writeOutput(formatOutput(newOutput),year,month,day)
    with open('temp/output.pk','wb') as dest: pickle.dump(newOutput,dest,pickle.HIGHEST_PROTOCOL)


    return output


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
