#import prep
import StringIO
from lxml import etree
import re
import dbm
import sqlite3
import time
import urllib
import masters
import pickle
import ftplib


#with open('regexDoc.txt','r') as f:
#   toParse=f.read()

#print toParse

#This works nicely enough for a simple case
#p=re.compile(r'(?:&ldquo;)([A-Z]*)(?:&rdquo;)')
#This also works well
#q=re.compile(r'symbol[.\n](?:&ldquo;)?(?:&#14[5678];)?(?:&#822[01];)?([A-Z]{1,4})(?:&rdquo;)?(?:&#14[5678];)?(?:&#822[01];)?.*\n')
#r=re.compile(r'((?:OTC|NYSE|NASDAQ)?.*symbol[.\n](?:&ldquo;)?(?:&#14[5678];)?(?:&#822[01];)?([A-Z]{1,4})(?:&rdquo;)?(?:&#14[5678];)?(?:&#822[01];)?.*(?:OTC|NYSE|NASDAQ)?)')
#s=re.compile(r'(?:OTC|[Nn][Aa][Ss][Dd][Aa][Qq]).*symbol.*(?:")?([A-Z]{1,4}")')
#s=re.compile(r'((?:OTC|NYSE|[Nn][Aa][Ss][Dd][Aa][Qq])?.*symbol[.\n](?:&ldquo;)?(?:&#14[5678];)?(?:&#822[01];)?"?([A-Z]{1,4})(?:&rdquo;)?(?:&#14[5678];)?(?:&#822[01];)?"?.*(?:OTC|NYSE|NASDAQ)?)')

#print toParse
#print s.findall(toParse)
#print re.findall(r'[Mm]aterial(?:ly)? weak',"yo this shit is material weak")

#files=['73887/0000073887-15-000007.txt','859163/0000859163-15-000024.txt','919175/0001520138-15-000247.txt','1001463/0001185185-15-001386.txt','1001463/0001185185-15-001394.txt','1078075/0001628280-15-004363.txt']
#r=re.compile(r'(?:which registered.*([Nn][Aa][Ss][Dd][Aa][Qq]|OTC|[Oo][Vv][Ee][Rr] [Tt][Hh][Ee] [Cc][Oo][Uu][Nn][Tt][Ee][Rr]|[Nn][Ee][Ww] [Yy][Oo][Rr][Kk] [Ss][Tt][Oo][Cc][Kk] [Ee][Xx][Cc][Hh][Aa][Nn][Gg][Ee]|[Nn][Yy][Ss][Ee])[^<]*<)')
#for file in files:
#    with open('edgar/data/'+file,'r') as f:
#        m=r.search(f.read())
#        if m:
            #            print m.group(0)
            #            print m.group(1)
#        else: print "No matches for", file

#mydb=dbm.open('temp/testDbm','c')
#mydb={'1078075': '1078075','1207074': '1090872','1321741': '715957','1377936': '715957', '1409431': '1039399', '1439288': '1439288', '1439397': '37996', '1490949': '1039399'}

#print mydb['1078075']

#testing SQLITE
#conn=sqlite3.connect('temp/tempdb.db')
#c=conn.cursor()
#c.execute('''CREATE TABLE cikToTicker (cik text, ticker text) ''')

#for i,j in mydb.items():
#    c.execute("INSERT INTO cikToTicker VALUES ('23','44')")

#This is for trying to extract items from a 10-K, but I think the quickest way to do it (now) would be to just locate the end of the 10-K and start of exhibits and just save the former as its own file and run on that.
#exp=re.compile(r'Item&#160;[0-9]{1,3}')
#with open('edgar/data/20629/0000020629-15-000028.txt','r') as f:
#    g=f.read()
#print exp.findall(g)


#Testing relative speeds of downloading a file vs. reading it in memory.
#May be less necessary if can host on site with faster connection than my home connection
#with open('edgar/daily-index/master.20150601.idx','r') as f:
#    fileNames=[line.split("|")[-1][0:-1] for line in f.readlines()[0:10]]

#print fileNames

#t0=time.time()
#for file in fileNames:
#    urllib.urlretrieve('ftp://ftp.sec.gov/'+file,'temp/temp.txt')
#t1=time.time()
#print t1-t0

#t0=time.time()
#for file in fileNames:
#    temp1=urllib.open('ftp://ftp.sec.gov/'+file)
#    temp1.read()
#t1=time.time()
#print t1-t0

#conn=sqlite3.connect('temp/example.db')
#c=conn.cursor()

#c.execute('''CREATE TABLE watchlist
#             (cik text, form text)''')

#c.execute ('insert into watchlist values (?,?)', ('blah','Form4'))
#conn.commit()

#x='blah'
#c.execute('SELECT * FROM watchlist WHERE cik=?', (x,)   )
#print c.fetchone()

ftp=ftplib.FTP('ftp.sec.gov')
ftp.login()
#ftp.cwd('edgar/data/1000232/')
#r=StringIO.StringIO()
#ftp.retrbinary('RETR 0001000232-15-000007.txt',r.write)
#print r.getvalue()

s=StringIO.StringIO()
ftp.retrbinary('RETR edgar/data/1554225/0001604232-15-000091.txt', s.write)
print s.getvalue()

ftp.quit()
