import datetime
import urllib
import os.path
import logging
import re
import dbm
import time

class StaticMethods:

    @staticmethod
    def getMaster(year, month, day):
        """Retrieves the master index for a given date, strips crap from header, and saves it."""
        filePath='edgar/daily-index/'
        fileName='master.'+year+month+day+'.idx'
        urllib.urlretrieve('ftp://ftp.sec.gov/'+filePath+fileName, filePath+'temp.txt')

#Strip first 7 lines of crap so only data remains
#Code should locate beginning of data
        with open(filePath+'/temp.txt','r') as fin:
            data = fin.read().splitlines(True)
        with open(filePath+fileName, 'w') as fout:
            fout.writelines(data[7:])


    @staticmethod
    def getFormsFiledOnDay(formList, year, month, day):
        """
        Returns list containing all rows of an EDGAR master file for a given day
        if the form filed matches a type of form contained in formList.
        """
        rows=[]
        try:
            with open('edgar/daily-index/master.'+year+month+day+'.idx','r') as f:
                #this could be done in a one-line list comprehension
                for line in f.readlines():
                    temp=line.split('|')
                    if temp[2] in formList:
                        #Removes EOL character & appends
                        temp2=temp
                        temp2[-1]=temp[-1][:-1]
                        rows.append(temp2)

        except IOError: print 'IOError'

        return rows


    @staticmethod
    def getFormFromMaster(masterRecord):
        """
        Checks a record from a master file to see whether the filing exists locally and, if not, retrieves it.
        """
        fileName=masterRecord[-1]
        if os.path.isfile(fileName):
            logging.debug('Filename %s already exists' % fileName)
            print 'Filename %s already exists' % fileName
        else:
            filePath='/'.join(fileName.split('/')[:3]) #Should really slice through -2
            
            #Now check if path exists
            if os.path.exists(filePath):
                logging.debug('Path %s already exists' % filePath)
                print 'Path %s already exists' % filePath
            else:
                logging.info('Needed to create path %s.' % filePath)
                print 'Needed to create path %s.' % filePath
                os.makedirs(filePath)
            
            remotePath='ftp://ftp.sec.gov/'+fileName
            logging.info('Needed to download file from %s' % remotePath)
            print 'Needed to download file from %s' % remotePath
                
                #isError=True
                #            while isError:
            t0=time.time()
            try:
                #NEED TO HANDLE EXCEPTIONS WHEN THIS CANT FIND FILE, WAIT A COUPLE SECOND THEN TRY AGAIN
                urllib.urlretrieve(remotePath,fileName)
                t1=time.time()
                print 'Total time to download: ', t1-t0
                #        isError=False
                
            #This seems to be the wrong type of error to report, because the exception is getting
            #thrown even when the file is downloaded
            #Also, getting errors when trying to print e.code and e.read()
            except IOError as e:
                logging.error('File %s was not downloaded due to an IOERrror' % remotePath)

#print e.code
#                print e.read()
                print 'Failed to download file %s because of an error' % remotePath
                #time.sleep(5)
                t1=time.time()
                print 'Total time to suck: ', t1-t0
                return True
            except: raise
            else:
                #time.sleep(5)
                return False

        """
            avx-20150331x10k.htm
            sgmd-20140630_10k.htm
            brs10-k2015.htm
            acaciadiversified10k123113.htm
            ntct-2015331x10k.htm
            a2224790z10-k.htm Actual ticker is VIRT
            d927560d10k.htm Actual ticker is GAIN
        """

    @staticmethod
    def getAllFormsFromMaster(recordBlock):
        while len(recordBlock)>0:
            print "*********There are %02d records to retrieve*********" % len(recordBlock)
            #Using recordBlock[:] for some reason caused masterRecords variable to be overwritten.
            recordBlock=[line for line in recordBlock if StaticMethods.getFormFromMaster(line)]
            #Next line will only execute after the entire set of records has been iterated over
    
    @staticmethod
    def findTerms(masterRecords):
        """
        Searches each filing contained in a list of records from a master file for particular
        terms.
        """
        cikTicker=[]
        cikToTicker=dbm.open('data/cikToTicker','c')
        cikToExchange=dbm.open('data/cikToExchange','c')
        output=[]
        
        #First have to make sure all forms have been downloaded
        StaticMethods.getAllFormsFromMaster(masterRecords)

        for line in masterRecords:
            #NO IDEA WHY I CANT JUST CALL GETFORMFROMMASTER(LINE); IT WONT RUN LIKE THAT
            p=re.compile(r'under[^<]*the[^<]*symbol[^<]*(?:&ldquo;)*(?:&#14[5678];)*(?:&#822[01];)*([A-Z])+?((?:&rdquo;)*(?:&#14[5678];)*(?:&#822[01];)*)')
            #Issue here is that I cannot figure out how to match on or more " marks. "? does not work, nor does (?:")?
            s=re.compile(r'((?:OTC|NYSE|[Nn][Aa][Ss][Dd][Aa][Qq])?.*symbol[.\n](?:&ldquo;)?(?:&#14[5678];)?(?:&#822[01];)?([A-Z]{1,4})(?:&rdquo;)?(?:&#14[5678];)?(?:&#822[01];)?.*(?:OTC|NYSE|NASDAQ)?)')
            q=re.compile(r'[Mm]aterial(?:ly)? weak')
            #May want to use restatement, because in case of VRTU, turned up restated agreements; using a capital R will cause similar problems
            #Some 10-Ks may have exhibits that include prospectuses (or shareholder agreements) that address possibility of restatement. Should avoid reading these, which presumably means using an HTML parser.
            #Smaller reporting companies may also be worth focusing on, since less likely to be seen by other firms. Again, HTML might be necessary.
            #Item 9a in 10-K specifically speaks to internal controls. Certain words mentioned here should have higher value than mentioned elsewhere.
            #Item 4 (Controls and Procedures) in 10-Q is similar
            #Material weakness might show up in exhibits to 8-K, e.g., class action settlement notices
            
            r=re.compile(r'restatement')
            t=re.compile(r'(<FILENAME>([a-z]{1,4})[a-z0-9-_.]*htm)')
            
            i=0
            with open(line[-1],'r') as f:
                g=f.readlines()
            
            with open('temp/temp.txt','w') as h:
                for x in g:
                    if i==2: break
                    elif x[0:10]=="<FILENAME>":
                        i+=1
                        h.write(x)
                    else: h.write(x)
                
            with open('temp/temp.txt','r') as j:
                fileText=j.read()
                ind1=len(q.findall(fileText))
                ind2=len(r.findall(fileText))
                output.append([line,ind1,ind2])
                x=t.search(fileText)
                if x==None: print "no matches"
                else: cikTicker.append([line[0], x.group(2),"No"])
                os.remove('temp/temp.txt')
    
        #print cikTicker
        #This section works, but commented out for debugging purposes.
        #Now we check to see whether looking up the ticker gives us back the same cik
        #Best way would be to do this by parsing Form 4, which has the ticker in a much more obtainable format
        #        u=re.compile(r'action=getcompany&amp;CIK=([0-9]{10})&')
        #        for i in cikTicker:
        #            urlToOpen='https://www.sec.gov/cgi-bin/browse-edgar?CIK='+i[1]+'&Find=Search&owner=exclude&action=getcompany'
        #            f=urllib.urlopen(urlToOpen)
        #            print i[0],i[1]
            
            #This should be a real database, with multiple values per key

#            m=u.search(f.read())
#            if m==None: print "No matches"
#            elif i[0]==m.group(1).lstrip("0"): cikToTicker[i[0]]=i[1]
#            else: logging.debug("We pulled a string that was not the ticker symbol for %s %s" % (i[0],i[1]))

        for line in output:
            if line[1]>0 or line[2]>0: #This works for 8-K, but have higher cut-off for 10-Ks
                print str(line)+"\n"
#            else:  print str(line)+"\n"

#print re.findall(r'under[^<]*the[^<]*symbol[^<]*&ldquo;*[^<]*\n',fileText)
                #print re.findall(r'&ldquo;*',fileText)
                #print re.findall(r'(&#145;)*(&#146;)*',fileText)
#print re.findall(r'[Cc]ommon\s[Ss]tock.*symbol\s*()()',fileText)
#print fileText
#This takes forever. Also, because the files are in markup, the lines before and after are often
#just marked up and useless.
#                print re.findall(r'(.*\n)(.*[Mm]aterial\sweak.*\n)(.*\n)',fileText)
#                print re.findall(r'.*[Mm]aterial\sweak.*\n',fileText)

