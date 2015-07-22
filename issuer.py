from lxml import etree
import datetime
import urllib
import os.path
import logging
import pickle
import prep
import traderecord

class Issuer (object):
    #idea is to pass this the url of a form 4 from a daily index
    
    def __init__(self,cik):
        self.cik=cik
    
    def getAllFilings(self, weeksback):
    #Goes back through past X months of master files and build data set of all as pertain to the company
        periodend=datetime.date.today()
        delta=datetime.timedelta(weeks=24) # Check how regs calculates 6 mos
        periodstart=periodend-delta
    
        inc = datetime.timedelta(days=1)
    
        data3=[]

        while periodstart<=periodend:
            
            tempdate="%d%02d%02d" % ((periodstart.year), (periodstart.month), (periodstart.day))
            filename='ftp://ftp.sec.gov/edgar/daily-index/master.'+tempdate+'.idx'
            logging.debug("Attempting to open %s" % filename)
            #Once I figure out how to handle the read-in data, integrate this commented block into below block so the data can be retrieved from URL
                #try:
                #fin=urllib.urlopen(filename)
                
            myfile='masters/masterindex'+tempdate+'.txt'
            print myfile

            try:
                with open(myfile,"r") as fin:
                    data1=fin.read().splitlines(True)
                    data2=data1[7:] #Removes first 7 lines of master, which is generally junk
                    
                    #Only adds records containing the company CIK
                    for line in data2:
                        record=line.split("|")
                        if record[0]==self.cik:
                            record[-1]=record[-1].rstrip("\n")
                            data3.append(record)
                        else: pass
            

            except IOError:
                print "There was an IOError" #Make sure to diff btw file not there and cant connect

            periodstart+=inc

            with open("data/"+self.cik+".pk", "wb") as output:
                pickle.dump(data3,output,pickle.HIGHEST_PROTOCOL)
                    #with open("data/"+self.cik+".pk", "r") as input:
                    #               data4=pickle.load(input)
            print "printing data3", data3
    

    def checkForm4(self):
    
        with open("data/"+self.cik+".pk", "r") as input: temp=pickle.load(input)
    
        myblock=traderecord.TradeBlock()
        alltrades=[]
        traders=set() #Unique set of Cik of all individuals
    
        #Retrieve all Form 4s; then create data sets for each filer
        #print temp
        p=prep.Prep()
        for line in temp:
            if line[2]=="4": #Only getting form 4s
                p.getIfNecessary(line[-1])
                #XMLfile="XML/"+line[-1].split("/")[-1]
                XMLfile="XML/"+line[-1]
                logging.debug("Getting %s" % XMLfile)
                #print XMLfile
                rec=traderecord.TradeRecord(p.readXML(XMLfile))
                testrec=traderecord.XMLFiletoRecords(p.readXML(XMLfile))
                
                myblock.append(rec)
                alltrades.append(rec)
                traders.add(rec['ownerCik'])
            #print rec
            else: pass

        print traders
    
        testdict={}
        for person in traders:
            testdict.update({person:traderecord.TradeBlock()})


        for rec in alltrades:
#print rec
            testdict[rec['ownerCik']].append(rec)
        
        print alltrades
    
        myblock.getProfit()

#print myblock



#************STUFF BELOW IS LEFTOVERS**************

    def gettransaction(self,filename):
        #Returns list comprising one transaction
        #Step 1, retrieve the data from the url and leave only the XML file portion
        #First block figures out where the XML portion begins/ends within the file
        #SHOULD THERE BE AN INITIAL BLOCK THAT DOWNLOADS THE DATA, OR WILL IT ALREADY RESIDE
        #ON COMPUTER?
        logging.info("Getting transaction based on file %s", filename)
        i=0
        j=0
        start=0
        end=0
    
        #Going to see if the file is already saved. If not, download it.
        if os.path.isfile(filename):
            logging.debug("Filename %s already exists", filename)
        else:
            try:
                temp=filename.split("/")
                mypath="/".join(temp[:3])
                #Now check if path exists
                if os.path.exists(mypath): pass
                else: os.makedirs(mypath)
                
                remotepath="ftp://ftp.sec.gov/"+filename
                logging.debug("Saving file %s as %s", remotepath, filename)
                urllib.urlretrieve(remotepath,filename)
            except IOError: logging.error("File %s was not downloaded due to an IOERrror",remotepath)
            except: raise
        
        with open(filename,"r") as fin:
            for line in fin:
                i+=1
                j+=1
                if line[:5]=="<?xml": start=i
                elif line=="</ownershipDocument>\n": end=j
                else: pass
        
        #Second block reads in the whole file and writes out only XML portion
        with open(filename,"r") as fin: data=fin.read().splitlines(True)
        #splitlines=True keeps the newline chars
        with open("XML/"+filename.split("/")[-1],"w") as fout: fout.writelines(data[start-1:end])

        #Step 2, get relevant fields from the XML file
        with open("XML/"+filename.split("/")[-1],"r") as f:
            parser=etree.XMLParser()
        
            #Parse function returns an ElementTree object
            tree=etree.parse(f,parser=parser)
            
            #Returns essentially a dictionary containing pertinent fields from a Form 4
            #This substitutes for the code below, which can probably be safely deleted now.
            rec=traderecord.TradeRecord(tree)
            
        return rec
                    
    def prevtransactions(self,transactiondate,weeksback):
        #Passes, in order, the integer version of the list elements of YYYY-MM-DD
        periodend=datetime.date(*map(int,transactiondate.split("-")))
        delta=datetime.timedelta(weeks=weeksback) # Check how regs calculates 6 mos
        periodstart=periodend-delta
        
        logging.info("Getting previous transactions between %s and %s" % (periodstart, periodend))
        
        inc = datetime.timedelta(days=1)

        rows=[]
        
        #This loop identifies prior issuer form 4s in masters
        #MAY BE BETTER TO READ FROM PREVIOUSLY-COMPILED LIST OF CIK FORM 4 FILINGS
        while periodstart<=periodend:
            year=str(periodstart.year)
            month = "%02d" % periodstart.month
            day = "%02d" % periodstart.day
        
            filename='masters/masterindex'+year+month+day+'.txt'
            logging.debug("Reading %s",filename)
        
            try:
                with open(filename) as f:
                    for line in f.readlines():
                        #print line
                        temp=line.split('|')
                        #Appending records in which issuer filed a form 4
                        if temp[0]==issuerCik and temp[2]=="4":
                        #Removes EOL character & appends
                            temp2=temp
                            temp2[-1]=temp[-1][:-1]
                            rows.append(temp2)
            #else: logging.debug("Did not add record: %s" % str(temp))
            except IOError: pass #print "IOError"
        
            periodstart+=inc
    
        temp=[]
        for row in rows:
            temp2=self.gettransaction(row[-1])
            temp.append(temp2)
        
        #Keeping only transactions in which the rptOwnerCik matches
        #THIS SHOULD OBVIOUSLY BE DONE ELSEWHERE TO AVOID ALL THIS WASTED EFFORT
        #returnval=[]
        returnval=traderecord.TradeBlock()
        for row in temp:
            if row["ownerCik"]==personCik: returnval.append(row)
            else: pass
        
        return returnval

    def getprofit(self,transactionfile):
        
        #First, get info about current transaction
        thistransaction=self.gettransaction(transactionfile)
        print "Current transaction: %s \n\n\n" % thistransaction
        #print thistransaction["periodOfReport"]
        #print thistransaction.gettype()
        
        #Second, get all transactions from previous six months for this filer
        prevtransactions=self.prevtransactions(thistransaction["ownerCik"],self.cik,thistransaction["transDate"],24)
        print "Previous transactions:", prevtransactions
        #for trans in prevtransactions:
#no longer necessary
#prevtransactions.compareRec(thistransaction)
#   print trans.values()

