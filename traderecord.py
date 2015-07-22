from lxml import etree
import logging

class TradeRecord(dict):
    #This inherits from dict, which is apparently a no-no. Supposedly should use
    #Abstract Base Classes
    def __init__(self,tree):
        root=tree.getroot()
        
        #Iterates over tree that was passed and throws certain text into array
        #Does not deal with possibility that given field may appear twice
        #In fact multiple transactions may be reported on single Form 4
        output={}
        for a in root.iter():
            if a.tag=="issuerCik": self["issuerCik"]=a.text.lstrip("0")
            elif a.tag=="rptOwnerCik": self["ownerCik"]=a.text.lstrip("0")
            elif a.tag=="rptOwnerName": self["ownerName"]=a.text
            elif a.tag=="periodOfReport": self["repDate"]=a.text
            elif a.tag=="securityTitle": self["secType"]=a[0].text
            elif a.tag=="transactionDate": self["transDate"]=a[0].text
            #P=open market purchase; S=open market sale
            #Transaction codes defined here: https://www.sec.gov/about/forms/form4data.pdf
            elif a.tag=="transactionCode": self["transCode"]=a.text
            elif a.tag=="transactionShares": self["shares"]=a[0].text
            elif a.tag=="transactionPricePerShare": self["pricePerShare"]=a[0].text
            elif a.tag=="transactionAcquiredDisposedCode": self["boughtSold"]=a[0].text

#Creating variables using SEC explanations about Form 4

class XMLFiletoRecords(dict):
    #This inherits from dict, which is apparently a no-no. Supposedly should use
    #Abstract Base Classes
    def __init__(self,tree):

        r=tree.xpath("/ownershipDocument/issuer")
        
        self["issuerCik"]=r[0][0].text.lstrip("0")
        
        ownerInfo={}

        #Getting owner info
        r=tree.xpath("/ownershipDocument/reportingOwner/reportingOwnerId")
        for sub in r[0]:
            if sub.tag=="rptOwnerCik": ownerInfo['ownerCik']=sub.text.lstrip("0")
            elif sub.tag=="rptOwnerName": ownerInfo['ownerName']=sub.text
        self["ownerCik"]=r[0][0].text.lstrip("0")
        self["ownerName"]=r[0][1].text

        r=tree.xpath("/ownershipDocument/reportingOwner/reportingOwnerRelationship")
        for sub in r[0]:
            if sub.tag=="isDirector": ownerInfo['isDirector']=sub.text
            elif sub.tag=="isOfficer": ownerInfo['isOfficer']=sub.text
            elif sub.tag=="isTenPercentOwner": ownerInfo['is10P']=sub.text
                #print ownerInfo.values()
        
        tradeInfo={}
        r=tree.xpath("/ownershipDocument/nonDerivativeTable/nonDerivativeTransaction")
        trades=[]
        i=0
        while i<len(r):
            temp={}
            for trade in r[i-1]:
                print i, trade.tag, trade.text
                if trade.tag=="securityTitle": temp["secType"]=trade[0].text
                elif trade.tag=="transactionData": temp["transDate"]=trade[0].text
                elif trade.tag=="transactionCoding": temp["transCode"]=trade[1].text
                #Footnote needs to be dealt with differently, becuase involves an attribute
                #elif trade.tag=="fn": temp["fn"]=trade[3].text
                elif trade.tag=="transactionAmounts":
                    temp["shares"]=trade[0][0].text
                    temp["pps"]=trade[1][0].text
                    temp["boughtSold"]=trade[2][0].text
                elif trade.tag=="ownershipNature": temp["directOrIndirect"]=trade[0][0].text

#print temp
            trades.append(temp)
            
            
            i+=1
        print trades



class TradeBlock(list):
    
    def __init__(self):
        pass
    #self.ownerCik=ownerCik
    
    def getProfit(self):
        #Need to break into groups of securities
        classA=[]
        classB=[]
        for rec in self:
            if rec["secType"]=="Class B Common Stock":
                classB.append(rec)
            elif rec["secType"]=="Class A Common Stock":
                classA.append(rec)
            else: logging.debug("%s security type trades not compiled" % rec["secType"])

#Need to identify the sale at the highest price
        highVal=max(classA,key=lambda x:x['pricePerShare'])
        lowVal=min(classA,key=lambda x:x['pricePerShare'])
        print highVal
        print lowVal

    

        print classB