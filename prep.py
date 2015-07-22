import datetime
import csv
import urllib
from lxml import etree
import StringIO
import traderecord
import logging
import os.path


#Download today's data
#NB THIS IS HARD-CODED; NEED TO CHANGE
def gettodays():
    urllib.urlretrieve('ftp://ftp.sec.gov/edgar/daily-index/master.20150424.idx', 'masterindex')
    
    #Strip first 7 lines of crap so only data remains
    #Code should locate beginning of data
    with open('masterindex','r') as fin:
        data = fin.read().splitlines(True)
    with open('masterclean.txt', 'w') as fout:
        fout.writelines(data[7:])

def cleanmaster(filename):
    with open(filename,'r') as fin:
        data = fin.read().splitlines(True)
    #Outputs from line 7 on, because the first 6 are just header crap
    #IMPROVE WITH CODE FROM makeXML
    with open(filename+'.txt', 'w') as fout:
        fout.writelines(data[7:])

def getIfNecessary(self,filename):
    #Seems like this should be a private method or located elsewhere
    #(No need for it to be called by an Issuer.)
    logging.info("Getting transaction based on file %s", filename)
    i=0
    start=0
    end=0

    #Going to see if the file is already saved. If not, download it.
    if os.path.isfile(filename):
        logging.debug("Filename %s already exists", filename)
            #print filename.split("/")[-2:]
            #XMLfile="XML/"+filename.split("/")[-2]
        XMLfile="XML/"+filename
        if os.path.isfile(XMLfile): logging.debug("Filename %s already exists", XMLfile)
        else: self.makeXML(filename)

    else:
        try:
            mypath="/".join(filename.split("/")[:3])
        
            #Now check if path exists
            if os.path.exists(mypath): logging.debug("Path %s exists" % mypath)
            else:
                logging.info("Needed to create path %s." % mypath)
                os.makedirs(mypath)
        
            remotepath="ftp://ftp.sec.gov/"+filename
            logging.info("Needed to download file from %s" % remotepath)
        
            urllib.urlretrieve(remotepath,filename)
        
            self.makeXML("XML/"+filename)
            
            #This seems to be the wrong type of error to report, because the exception is getting
            #thrown even when the file is downloaded
        except IOError: logging.error("File %s was not downloaded due to an IOERrror",remotepath)
        except: raise

#Removes bullshit at the top and bottom of file
def makeXML(self,filename):
        #Check if path exists and make if necessary
    temp=filename.split("/")
    mypath="XML/"+"/".join(temp[:3])
    if os.path.exists(mypath):logging.debug("The path %s already exists" % mypath)
    else:
        logging.info("Creating path %s" % mypath)
        os.makedirs(mypath)
        
    (i,start,end)=(0,0,0)
    with open(filename,"r") as fin:
        for line in fin:
            i+=1
            if line[:5]=="<?xml": start=i
            elif line=="</ownershipDocument>\n": end=i
            else: pass
    
    #Second block reads in the whole file and writes out only XML portion
    with open(filename,"r") as fin: data=fin.read().splitlines(True)
    #splitlines=True keeps the newline chars
    logging.debug("Outputting %s as an XML file" % filename)
#        with open("XML/"+filename.split("/")[-1],"w") as fout: fout.writelines(data[start-1:end])
    with open("XML/"+filename,"w") as fout: fout.writelines(data[start-1:end])
def readXML(self,filename):
    parser=etree.XMLParser()
    
    #Parse function returns an ElementTree object
    with open(filename,"r") as f:
        tree=etree.parse(f,parser=parser)
    return tree