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

