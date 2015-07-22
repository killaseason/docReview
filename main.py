import datetime
import time
import csv
import urllib
from lxml import etree
import StringIO
#import prep
#import person
import issuer
import os, errno
import logging
import staticmethods
import masters
#import traderecord


#Without filemode arg would just append
logging.basicConfig(filename="log.txt",filemode="w",level=logging.DEBUG)

#Need method either here or in prep that makes sure masters are up to date

def getfilers(date,form):
    """
        Rreturns unique list of cik, filer from master file for all filers of specified form on given day
    """

    filename='masters/masterindex'+date+'.txt'

   #Save each row as an array
    rows = []
    with open(filename,'r') as f:
        for line in f.readlines():
            temp=line.split('|')
            if temp[2]==form:
                #rows.append(temp)
                temp2=[temp[0],temp[1]]
                if temp2 not in rows: rows.append(temp2)
   
    return rows



def findtransactions(cik,weeksback):
    """
        Search for a specific filers previous filings
        Returns records in which filer filed a form 4
        Might be preferable to use the map method to iterate over this date range
        
    """
    
    periodend=datetime.date.today()
    delta=datetime.timedelta(weeks=weeksback) # Check how regs calculates 6 mos
    periodstart=periodend-delta

    inc = datetime.timedelta(days=1)

    rows=[]

    while periodstart<periodend:
        year=str(periodstart.year)
        month=str(periodstart.month)
        day=str(periodstart.day)

        if len(month)==1: month='0'+month
        if len(day)==1: day='0'+day

        filename='masters/masterindex'+year+month+day+'.txt'

        try:
            with open(filename) as f:
                for line in f.readlines():
                    temp=line.split('|')
                    if temp[0]==cik and temp[2]=="4":
                        #Removes EOL character & appends
                        temp2=temp
                        temp2[-1]=temp[-1][:-1]
                        rows.append(temp2)
        except IOError: print "IOError"

        periodstart+=inc

    return rows

def savepasttrades(filerstoday):
    """
        #Uses records from master with filers of a particular form and finds previous filings
        #Saves all such filings in files
    """
    for i in filerstoday:
        cik=i[0]
        #IN FORM 4 USE CASE SHOULD ONLY GET PAST SIX MONTHS
        filer=findtransactions(cik,24)
        print filer
        filename="form4filers/cik"+cik+".txt"
        with open(filename,"wb") as f:
            #spamwriter=csv.writer(f, delimiter="|", quoting=csv.QUOTE_NONNUMERIC)
            spamwriter=csv.writer(f, delimiter="|", quoting=csv.QUOTE_NONE)
            #Only writes first row
            #spamwriter.writerow(filer[0])
            for row in filer:
                #ISSUE WITH EOL CHARACTERS
                spamwriter.writerow(row)

#Want this to read in piped lines of data showing previous trades
#Then convert text dates to actual dates
#Then keep only dates within past six months of passed date
#Then calculate so-called profit
def matchtrades(cik,d):
    mydate=todate(d)
    inc = datetime.timedelta(weeks=24)

    rows=[]
    filename="form4filers/cik"+cik+".txt"
    with open(filename,"r") as fin:
        for line in fin:
            temp=line.split("|")
            temp[3]=todate(temp[3])
            #Only appends if record occurred in past 6 mos.
            #Right now only records we have are from past 6.
            if temp[3]>mydate-inc:
                temp[-1]=temp[-1][:-2]
                rows.append(temp)
            else: pass

#Now get the "profit"


#Converts date in YYYYMMDD format to date object
def todate(din):
    dout=datetime.date(int(din[:4]),int(din[4:6]),int(din[6:8]))
    return dout


#The action starts here

#a=issuer.Issuer("1616707")
#a.checkForm4()
#b.getAllFilings(24)

#a=issuer.Issuer("1616707")

#Downloads master for day in question; identifies all 10ks etc filed that day; looks for specified terms in those forms.
#Takes forever. Can be about 30-60 second to download a file. Upwards of 300 files.
#staticmethods.StaticMethods.getMaster("2015","06","02")
#masterRecords=staticmethods.StaticMethods.getFormsFiledOnDay(['10-K','10-Q','8-K'],'2015','06','02')
#staticmethods.StaticMethods.findTerms(masterRecords)


masters.updateWatchlist('2015','02','02')
masters.updateWatchlist('2015','02','03')
masters.updateWatchlist('2015','02','04')
masters.updateWatchlist('2015','02','05')
masters.updateWatchlist('2015','02','06')

masters.updateWatchlist('2015','02','09')
masters.updateWatchlist('2015','02','10')
masters.updateWatchlist('2015','02','11')
masters.updateWatchlist('2015','02','12')
masters.updateWatchlist('2015','02','13')

#masters.updateWatchlist('2015','02','16') Presidents day
masters.updateWatchlist('2015','02','17')
masters.updateWatchlist('2015','02','18')
masters.updateWatchlist('2015','02','19')
masters.updateWatchlist('2015','02','20')

masters.updateWatchlist('2015','02','23')
masters.updateWatchlist('2015','02','24')
masters.updateWatchlist('2015','02','25')
masters.updateWatchlist('2015','02','26')
masters.updateWatchlist('2015','02','27')

masters.updateWatchlist('2015','03','02')
masters.updateWatchlist('2015','03','03')
masters.updateWatchlist('2015','03','04')
masters.updateWatchlist('2015','03','05')
masters.updateWatchlist('2015','03','06')

masters.updateWatchlist('2015','03','09')
masters.updateWatchlist('2015','03','10')
masters.updateWatchlist('2015','03','11')
masters.updateWatchlist('2015','03','12')
masters.updateWatchlist('2015','03','13')

masters.updateWatchlist('2015','03','16')
masters.updateWatchlist('2015','03','17')
masters.updateWatchlist('2015','03','18')
masters.updateWatchlist('2015','03','19')
masters.updateWatchlist('2015','03','20')

masters.updateWatchlist('2015','03','23')
masters.updateWatchlist('2015','03','24')
masters.updateWatchlist('2015','03','25')
masters.updateWatchlist('2015','03','26')
masters.updateWatchlist('2015','03','27')

masters.updateWatchlist('2015','03','30')
masters.updateWatchlist('2015','03','31')


masters.filedDelayedReport()