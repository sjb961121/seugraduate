import xml.sax
from xml.sax.handler import ContentHandler
from xml.sax import parse
import pymysql


doc=open('author.txt','w',encoding='utf-8')

count1=0
count2=0
count3=0
count4=0
list_author=[]
class article( xml.sax.ContentHandler ):
   def __init__(self):
      self.CurrentData = ""
      self.author = ""
      self.title = ""
      self.year = ""
      self.journal = ""
      #self.ee=""
      
   # 元素开始事件处理
   def startElement(self, tag, attributes):
      self.CurrentData = tag
      global count1
      global count2
      global count3
      global count4
      if tag == "article":
         count1=0
         count2=0
         count3=0
         count4=0
         
   # 元素结束事件处理
   def endElement(self, tag):
      global list_author
      if tag=="author":
         list_author.append(self.author)
      if tag=="article":
         for item in list_author:
            print(item,file=doc)
         list_author.clear()
   # 内容事件处理
   def characters(self, content):
      global count1
      global count2
      global count3
      global count4
      if self.CurrentData == "author":
             self.author = content   
      '''elif self.CurrentData == "title":
         if count2==0:
             content=content.strip('.')
             self.title = content
             count2+=1
      elif self.CurrentData == "journal":
         if count3==0:
             content=content.strip('.')
             self.journal = content
             count3+=1
      elif self.CurrentData == "year":
         if count4==0:
             self.year = content
             count4+=1    '''
      '''elif self.CurrentData == "ee":
         self.ee = content''' 
if  __name__ == "__main__":  
   parser = xml.sax.make_parser()
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)
   parser.setContentHandler( article() )
   parser.parse('dblp.xml')
   
doc.close()

 

