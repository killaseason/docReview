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
import xml.etree.ElementTree as ET


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

#with open('masters/masterindex20150204','r') as f:
#   a=f.readlines()

#b=[line.split('|') for line in a if line[0][0].isdigit() and line.split('|')[1]=='ROYAL BANK OF CANADA']
#for line in b:
#    line[-1]='<a href=\"ftp://ftp.sec.gov/'+line[-1]+'\">link</a><br>'
#c=['|'.join(line) for line in b]

#print c
#toWrite='|'.join(b)

#with open('temp/temp.html','w') as f:
#    f.writelines(c)
#    for line in toWrite:
#        f.writelines(line)

#a=['B','I','L','L','Y']
#b='|'.join(a)
#print b

#for entry in fileList:
#    with open('edgar/data'+entry,'r') as f:text=f.read()
#    result=r.search(text)
#    toAdd=[result.group(1),result.group(2)]
#    print toAdd
#    try:
#        with open('data/cikExchangeTicker.pk','r') as input:
#            cikExchangeTicker=pickle.load(input)
#            cikExchangeTicker.append(toAdd)

#    except IOError:
#        print 'File probably doesn\'t exist.'
#        cikExchangeTicker=toAdd
#    finally:
#        with open('data/cikExchangeTicker.pk','wb') as output:
#            pickle.dump(cikExchangeTicker,output,pickle.HIGHEST_PROTOCOL)

#print cikExchangeTicker


#a=['1021270', 'FAMOUS DAVES OF AMERICA INC', '8-K', '20150807', 'edgar/data/1021270/0001193125-15-281337.txt\n']

#r=re.compile(r'good')
#with open('edgar/data/3545/0001104659-15-042557.txt','r') as f:g=f.read()
#s=r.findall(g)
#print str(s)


#with open('data/cikExchangeTicker.pk','r') as f: g=pickle.load(f)
#for rec in g: rec[1]=rec[1].upper()

#b=[]
#This removes exact duplicate entries in our mapping
#for rec in g:
#    if rec not in b: b.append(rec)

#This gets rid of probably erroneous
#c=[rec for rec in b if len(rec[2])>1]

#Creates set of unique CIKs in mapping
#x={rec[0] for rec in c}
#Takes only the CIKs from the mapping (includes duplicates)
#y=[rec[0] for rec in c]
#Creates set of CIKS that appear more than once in mapping
#z={rec for rec in y if y.count(rec)>1}

#print c
#print len(c)
#with open('data/cikExchangeTicker.pk','wb') as output:
#    pickle.dump(cikExchangeTicker,output,pickle.HIGHEST_PROTOCOL)


#print masters.getYahooData('1178253')

from masters import check8K
from masters import getHtmFile
r=re.compile(r'[Mm]aterial(?:ly)? weak')
cl=re.compile(r'continued listing')
res=re.compile(r'resign')
auditor=re.compile(r'Item 4[.]01')
wells=re.compile(r'[Ww][Ee][Ll][Ll][Ss].(?![Ff][Aa][Rr][Gg][Oo])')
wellsNotice=re.compile(r'[Ww][Ee][Ll][Ll][Ss] [Nn][Oo][Tt][Ii][Cc][Ee]|[Ww][Ee][Ll][Ll][Ss] [Ll][Ee][Tt][Tt][Ee][Rr]')
investigation=re.compile(r'[Ss]ubpoena | [Oo][Ff] [Jj][Uu][Ss][Tt][Ii][Cc][Ee] | [Aa][Tt][Tt][Oo][Rr][Nn][Ee][Yy] [Gg][Ee][Nn][Ee][Rr][Aa][Ll]')
t=re.compile(r'[Cc]ompany')
    
#regExes=[[r,'Material weakness'],[cl, 'Continued listing'],[res,'Resignation'],[wellsNotice, 'Wells Notice'],[investigation,'Poss investigation'],[auditor,'Auditor change'],[t,'bullshit']]

#b=['1000683','BLONDER TONGUE LABORATORIES INC','10-Q','20150814','edgar/data/1000683/0001144204-15-049290.txt\n']

#with open ('edgar/data/16732/0000016732-15-000013.txt','r') as a:f=a.read()
#print check8K(b,f,regExes)
#print getHtmFile(b,f)

#q=['a','b']

#with open('data/fuck.pk','wb') as x: pickle.dump(q,x,pickle.HIGHEST_PROTOCOL)

a=[['1012493', 'Ferrellgas Partners ', '<td><a href="https://www.sec.gov/Archives/edgar/data/1012493/000110465915042483/a15-13180_58k.htm">8-K</a></td>', '20150601', [['Material weakness', set(['material weak']), 7]], [['Material weakness', set(['material weak']), 7]]], ['1013606', 'Endologix Inc /De/', '<td><a href="https://www.sec.gov/Archives/edgar/data/1013606/000101360615000109/form8-kmay282015annualshar.htm">8-K</a></td>', '20150601', [['Resignation', set(['resign']), 1]], [['Resignation', set(['resign']), 1]]], ['1021635', 'Oge Energy Corp.', '<td><a href="https://www.sec.gov/Archives/edgar/data/1021635/000102163515000078/ogeenergycorpform8-kx6x1x15.htm">8-K</a></td>', '20150601', [['Resignation', set(['resign']), 1]], [['Resignation', set(['resign']), 1]]], ['1022837', 'Sumitomo Mitsui Fina', '<td><a href="https://www.sec.gov/Archives/edgar/data/1022837/000119312515207559/d931112d6k.htm">6-K</a></td>', '20150601', [['Resignation', set(['resign']), 2]], [['Resignation', set(['resign']), 2]]], ['1022837', 'Sumitomo Mitsui Fina', '<td><a href="https://www.sec.gov/Archives/edgar/data/1022837/000119312515207584/d931100d6k.htm">6-K</a></td>', '20150601', [['Resignation', set(['resign']), 4]], [['Resignation', set(['resign']), 4]]], ['1034563', 'Icahn Enterprises Ho', '<td><a href="https://www.sec.gov/Archives/edgar/data/1034563/000114420415034805/v411215_8k.htm">8-K</a></td>', '20150601', [['Resignation', set(['resign']), 1]], [['Resignation', set(['resign']), 1]]]]

#masters.updateWatchlist(a)

#masters.addMapping(['1020646', 'OTC', 'ERFB'],'m')
#a.sort(key=lambda x:x[4][0][2])
#b=['<tr><td><a href="https://www.sec.gov/cgi-bin/browse-edgar?CIK=1072248&Find=Search&owner=exclude&action=getcompany">1072248</a></td>', '<td>M Line Holdings Inc</td>', '<td><a href="https://www.sec.gov/Archives/edgar/data/1072248/000161577415002335/s101709_10q.htm">10-Q</a></td>', '<td>20150819</td>', '<td>Material weakness (3)</td>', '<td>material weak</td>', '<td>No ticker!</td>', '<td>No ticker!</td>', '<td>No ticker!</td>', '<td>No ticker!</td>', '<td>No ticker!</td></tr>']

mytext='im on that OTC BB: XXYZ, as well as that '
exchange=re.compile(r'([Nn][Yy][Ss][Ee]|[Nn][Aa][Ss][Dd][Aa][Qq]|OTC(( Pink)?|( QB)?|( BB)?))( GS)?:\W?([A-Z]{1,4})')
#for i in range(0,10): print exchange.search(mytext).group(i)


#toRemove=[['1017043', 'DKDK', 'GLPW'],['1018094', 'DKDK', 'PULB'],['1013272', 'DKDK', 'NWFL'],['1013005', 'DKDK', 'KRO'],['1011060', 'DKDK', 'ASNB'],['1009976', 'DKDK', 'CMOH'],['1009106', 'DKDK', 'TFX'],['1008463', 'DKDK', 'CDNS'],['1008023', 'DKDK', 'BAS'],['1007190', 'DKDK', 'CBZ'],['1006830', 'DKDK', 'CBKM.OB'],['1003201', 'DKDK', 'MMAC'],['1000697', 'DKDK', 'WAT']]

#for b in toRemove: masters.removeMapping(b)

masters.addMapping(['1006830', 'OTC', 'CBKM'],'xxx')
