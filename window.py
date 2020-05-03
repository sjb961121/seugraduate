import tkinter as tk
from tkinter import ttk 
import py2neo 
from py2neo import Graph,Node,Relationship,authenticate
import tkinter.messagebox
import webbrowser
import os
import subprocess
from recommand import recommand_article
from recommand import reason
from recommand import recommand_like_dislike
from recommand import recommand_author
from recommand import recommand_author_first
import tkinter.font as tkFont


#authenticate
authenticate("localhost:7474", "neo4j", "neo4j")

#连接neo4j
graph= Graph()

#主界面
window=tk.Tk()
window.title('学术推荐系统')
window.geometry('800x450+280+150')
window.resizable(0,0)

style = ttk.Style()
style.configure("BW.TLabel", foreground="black", background="white")

#welcome
canvas=tk.Canvas(window,height=200,width=900)
image_file=tk.PhotoImage(file='welcome.gif')
image=canvas.create_image(400,100,anchor='center',image=image_file)
canvas.pack(side='top',fill='both')

#用户界面用户信息
ttk.Label(window,text='Username:').place(x=250,y=250)
ttk.Label(window,text='Password:').place(x=250,y=300)

var_usr_name=tk.StringVar()
var_usr_name.set('example')
entry_user_name=ttk.Entry(window,textvariable=var_usr_name)
entry_user_name.place(x=400,y=250)

var_usr_pwd=tk.StringVar()
entry_usr_pwd=ttk.Entry(window,textvariable=var_usr_pwd,show='*')
entry_usr_pwd.place(x=400,y=300)

#登录
def usr_login():
    usr_name=var_usr_name.get()
    usr_pwd=var_usr_pwd.get()
    userflag=False
    authorflag=False
    for record in graph.run("MATCH(a:User{name:'"+usr_name+"'}) RETURN a.name,a.password"):
        if record["a.name"]==usr_name:
            userflag=True
            if record["a.password"]==usr_pwd:
                if graph.run("MATCH (u:User{name:'"+usr_name+"'})-[:Written]-(p:Article) RETURN p.name LIMIT 1").evaluate()!=None:
                    authorflag=True
                #用户模块
                if (authorflag==True) and (os.path.exists(usr_name+'.txt')==False):
                    tk.messagebox.showinfo(title='Welcome',message='你好！'+usr_name+'\n由于您第一次使用本系统，将为您生成个性化推荐。\n请耐心等待1分钟！')
                else:
                    tk.messagebox.showinfo(title='Welcome',message='你好！'+usr_name)
                #隐藏用户窗口
                window.withdraw()
                
                #进入推荐界面
                '''if graph.run("MATCH (u:User{name:'"+usr_name+"'})-[:Written]-(p:Article) RETURN p.name LIMIT 1").evaluate()!=None:
                    authorflag=True'''
                recommand=tk.Toplevel(window)
                recommand.geometry('1000x550+220+120')
                recommand.title('推荐界面')
                recommand.resizable(0,0)
                def callback():
                    doc=open(usr_name+'.txt','w',encoding='utf-8')
                    data=recommand_lb.get(0,'end')
                    for item in data:
                        print(item,file=doc)
                    doc.close()
                    recommand.destroy()
                    window.deiconify()
                recommand.protocol("WM_DELETE_WINDOW", callback)

                #布局
                ft = tkFont.Font(family='Fixdsys', size=25, weight=tkFont.BOLD)
                top=tk.LabelFrame(recommand,height=50,bg='white')
                top.pack(side='top',fill='both')
                top_text=tk.Label(top,text='学术资源推荐系统',bg='white',fg='black',height=3,font=("黑体",25,"bold"))
                top_text.pack(side='left',fill=tk.Y)
                left=tk.LabelFrame(recommand,width=50,bg='white')
                left.pack(side='left',fill='both',ipady=5)
                mid=tk.LabelFrame(recommand,height=25,width=250,bg='white')
                mid.pack(side='left',fill='both')
                right=tk.LabelFrame(recommand,height=25,width=300,bg='white')
                right.pack(side='right',fill='both',expand='yes')
                
                search_word=tk.StringVar() 
                
                #查询框
                search=ttk.Entry(top,textvariable=search_word,width=20)
                #查询下拉框
                cmb=ttk.Combobox(top,width=5,state='readonly')
                cmb['value']=('按论文','按作者')
                cmb.current(0)

                
                '''#查询框
                search_word=tk.StringVar()
                search=ttk.Entry(recommand,textvariable=search_word,width=32)
                search.place(x=10,y=10)
                #查询下拉框
                cmb=ttk.Combobox(recommand,width=5,state='readonly')
                cmb['value']=('按论文','按作者')
                cmb.place(x=241,y=10)
                cmb.current(0)'''
                select=tk.StringVar()
                select.set(' 您没有正在阅读的论文，请在上方搜索框查询论文信息')
                select_title=tk.StringVar()
                select_title_name=''
                select_author_name=''
                select_year_name=''
                select_journal_name=''
                def recommand_reading():
                    #获取论文信息
                    select_title.set(recommand_lb.get(recommand_lb.curselection()))
                    select_title_name=''
                    select_author_name=''
                    select_year_name=''
                    select_journal_name=''
                    #subprocess.Popen("fillline.pyw",shell=True)
                    data=graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})-[:Written]->(a:Author) WITH p,a MATCH (p)-[:InYear]->(y:Year) \
WITH p,a,y MATCH (p)-[:Publish]->(j:Journal) RETURN a.name,y.name,j.name")
                    for item in data:
                            select_author_name=select_author_name+item["a.name"]+'\t'
                            select_year_name='发表年份:\n\n'+item["y.name"]+'\n\n'
                            select_journal_name='发表期刊\n\n'+item["j.name"]+'\n\n'
                    select_author_name='作者:\n\n'+select_author_name+'\n\n'
                    if select_year_name=='':
                            select_year_name='发表年份:\n\n\n\n'
                    if select_journal_name=='':
                            select_journal_name='发表期刊\n\n\n\n'
                    select_title_name='您好！您现在正在查看的论文为:\n\n'+select_title.get()+'\n\n'
                    #创建用户和论文之间关系
                    userread=graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})<-[r:Read]-(u:User{name:'"+usr_name+"'}) return r")
                    if userread.evaluate()==None:
                        graph.run("MATCH (p:Article{name:'"+select_title.get()+"'}),(u:User{name:'"+usr_name+"'}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)")
                    else:
                        graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})<-[r:Read]-(u:User{name:'"+usr_name+"'}) SET r.click=r.click+1,r.time=timestamp()")
                    #论文信息窗口添加信息(article)
                    select.set(select_title_name+select_author_name+select_year_name+select_journal_name)
                    
                    def dislike():
                            like_dislike=recommand_like_dislike(select_title.get(),usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                    recommand_dislike=ttk.Button(article,text='喜欢/不喜欢',command=dislike)
                    recommand_dislike.place(x=60,y=390)
                    doi=ttk.Button(article,text='阅读论文',command=web_open).place(x=200,y=390)
                #recommand_reading函数结束
                        
                #进入论文网站(包括推荐算法)
                def web_open():
                        org=graph.run("MATCH (a:Article{name:'"+select_title.get()+"'}) RETURN a.doi").evaluate()
                        webbrowser.open(org)
                    
                        #推荐模块
                        data=usr_name
                        if authorflag==False:
                            data_back=recommand_article(data)
                            recommand_lb.delete(0,'end')
                            for item in data_back:
                                recommand_lb.insert('end',item["other.name"])
                        else:
                            data_author=recommand_author(data)
                            recommand_lb.delete(0,'end')
                            for item_author in data_author:
                                recommand_lb.insert('end',item_author)
                        
                        def recommand_reason():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            data_reason=reason(selected,usr_name,authorflag)
                            if authorflag==False:
                                tk.messagebox.showinfo(title='Reason',message='根据您所读的论文: '+data_reason.evaluate()+' 向您推荐！')
                            else:
                                tk.messagebox.showinfo(title='Reason',message='根据与您相似的作者: '+data_reason.evaluate()+' 向您推荐他的论文！')
                        def dislike():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            like_dislike=recommand_like_dislike(selected,usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                        recommand_dislike=ttk.Button(recommand_module,text='喜欢/不喜欢',command=dislike)
                        recommand_dislike.place(x=50,y=390)
                        recommand_reason=ttk.Button(recommand_module,text='推荐理由',command=recommand_reason)
                        recommand_reason.place(x=220,y=390)
                        recommand_read=ttk.Button(recommand_module,text='查看论文',command=recommand_reading)
                        recommand_read.place(x=390,y=390)
                        #推荐模块结束
                #web_open函数结束

                def search_title_further(keyword,state):
                    vague_search=tk.Toplevel(recommand)
                    vague_search.geometry('800x425+300+200')
                    vague_search.title('查询论文')
                    vague_search.resizable(0,0)
                    search_lb=tk.Listbox(vague_search,width=120,height=20)
                    search_lb.pack()
                    xscrollbar = ttk.Scrollbar(vague_search,orient='horizontal')
                    xscrollbar.pack(fill=tk.X)
                    search_lb['xscrollcommand'] = xscrollbar.set
                    xscrollbar.config(command=search_lb.xview)
                    if state==False:
                        for record in graph.run("MATCH (p:Article) where p.name =~'(?i).*"+keyword+".*' return p.name LIMIT 20"):
                            search_lb.insert('end',record["p.name"])
                    else:
                        for record in graph.run("MATCH (a:Author{name:'"+keyword+"'})-[:Written]-(p:Article) return p.name LIMIT 20"):
                            search_lb.insert('end',record["p.name"])
                                
                    def search_reading():
                        
                        #获取论文信息
                        select_title.set(search_lb.get(search_lb.curselection()))
                        select_title_name=''
                        select_author_name=''
                        select_year_name=''
                        select_journal_name=''
                        #subprocess.Popen("fillline.pyw",shell=True)
                        data=graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})-[:Written]->(a:Author) WITH p,a MATCH (p)-[:InYear]->(y:Year) \
WITH p,a,y MATCH (p)-[:Publish]->(j:Journal) RETURN a.name,y.name,j.name")
                        for item in data:
                            select_author_name=select_author_name+item["a.name"]+'\t'
                            select_year_name='发表年份:\n\n'+item["y.name"]+'\n\n'
                            select_journal_name='发表期刊\n\n'+item["j.name"]+'\n\n'
                        select_author_name='作者:\n\n'+select_author_name+'\n\n'
                        if select_year_name=='':
                            select_year_name='发表年份:\n\n\n\n'
                        if select_journal_name=='':
                            select_journal_name='发表期刊\n\n\n\n'
                        select_title_name='您好！您现在正在查看的论文为:\n\n'+select_title.get()+'\n\n'
                        vague_search.destroy()
                        
                        #创建用户和论文之间关系
                        userread=graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})<-[r:Read]-(u:User{name:'"+usr_name+"'}) return r")
                        if userread.evaluate()==None:
                            graph.run("MATCH (p:Article{name:'"+select_title.get()+"'}),(u:User{name:'"+usr_name+"'}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)")
                        else:
                            graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})<-[r:Read]-(u:User{name:'"+usr_name+"'}) SET r.click=r.click+1,r.time=timestamp()")
                            
                        #论文信息窗口添加信息(article)
                        select.set(select_title_name+select_author_name+select_year_name+select_journal_name)
                        
                        def dislike():
                            like_dislike=recommand_like_dislike(select_title.get(),usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                        recommand_dislike=ttk.Button(article,text='喜欢/不喜欢',command=dislike)
                        recommand_dislike.place(x=60,y=390)    
                        doi=ttk.Button(article,text='阅读论文',command=web_open).place(x=200,y=390)

                        
                    
                    #查询窗口按钮(查看论文)    
                    search_read=ttk.Button(vague_search,text='查看论文',command=search_reading)
                    search_read.pack()
                
                def search_title():
                    keyword=search_word.get()
                    keykind=cmb.get()
                    state=False
                    #查询窗口
                    if keykind=='按作者':
                        state=True
                        author_search=tk.Toplevel(recommand)
                        author_search.geometry('800x425+300+200')
                        author_search.title('查询作者')
                        author_search.resizable(0,0)
                        author_lb=tk.Listbox(author_search,width=120,height=20)
                        author_lb.pack()
                        xscrollbar = tk.Scrollbar(author_search,orient='horizontal')
                        xscrollbar.pack(fill=tk.X)
                        author_lb['xscrollcommand'] = xscrollbar.set
                        xscrollbar.config(command=author_lb.xview)
                        for record in graph.run("MATCH (p:Author) where p.name =~'(?i).*"+keyword+".*' return p.name LIMIT 20"):
                            author_lb.insert('end',record["p.name"])
                        def author_reading():
                            keyword=author_lb.get(author_lb.curselection())
                            author_search.destroy()
                            search_title_further(keyword,state)
                        author_read=ttk.Button(author_search,text='查看作者',command=author_reading)
                        author_read.pack()
                    else:
                        search_title_further(keyword,state)
                   
                    #search_title函数结束
                
                #主窗口的查询按钮    
                #search_button=ttk.Button(recommand,text='查询',command=search_title).place(x=300,y=10)
                search_button=ttk.Button(top,text='查询',width=4,command=search_title)
                search_button.pack(side='right',padx=5)
                cmb.pack(side='right')
                search.pack(side='right')
                
                #显示论文信息
                article=tk.Label(mid,height=25,width=45,bg='white',textvariable=select,wraplength=300,justify='left',anchor='nw',pady=45)
                article.pack(side='left',fill=tk.Y)       
                #article=tk.Label(recommand,width=45,height=20,bg='white',textvariable=select,wraplength=300,justify='left',anchor='nw',pady=45)
                #article.place(x=10,y=90)

                #小图片
                '''global small_image_file
                small_image_file=tk.PhotoImage(file='recommend.gif')
                small_image=tk.Label(recommand,width=400,height=70,image=small_image_file)
                small_image.place(x=400,y=5)'''
                global small_image_file
                small_image_file=tk.PhotoImage(file='neu.gif')
                small_image=tk.Label(left,image=small_image_file)
                small_image.pack(side='bottom',pady=10)
                
                #推荐窗口
                recommand_module=tk.Label(right,width=45,height=25,bg='white')
                recommand_module.pack(side='left',fill=tk.Y)
                recommand_lb=tk.Listbox(recommand_module,width=80,height=20)
                recommand_lb.pack(side='top')
                xscrollbar = ttk.Scrollbar(recommand_module,orient='horizontal')
                xscrollbar.pack(fill=tk.X)
                recommand_lb['xscrollcommand'] = xscrollbar.set
                xscrollbar.config(command=recommand_lb.xview)
                '''recommand_module=tk.Label(recommand,width=45,height=25,bg='white')
                recommand_module.place(x=450,y=90)
                recommand_lb=tk.Listbox(recommand_module,width=45,height=20)
                recommand_lb.place(x=0,y=0)'''
                
                #初始推荐（冷启动）
                
                if (graph.run("MATCH (u:User{name:'"+usr_name+"'})-[r:Read]->(p:Article) RETURN r").evaluate()==None) and (authorflag==False):
                    initial_data=graph.run("MATCH (p:Article)<-[r:Read]-(:User) WITH p,SUM(r.click) AS a RETURN p.name ORDER BY a DESC LIMIT 20")
                    recommand_lb.delete(0,'end')
                    for initial_item in initial_data:
                        recommand_lb.insert('end',initial_item["p.name"])
                    
                    def recommand_reason():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            data_reason=reason(selected,usr_name,authorflag)
                            if authorflag==False:
                                tk.messagebox.showinfo(title='Reason',message='根据您所读的论文: '+data_reason.evaluate()+' 向您推荐！')
                            else:
                                tk.messagebox.showinfo(title='Reason',message='根据与您相似的作者: '+data_reason.evaluate()+' 向您推荐他的论文！')
                    def dislike():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            like_dislike=recommand_like_dislike(selected,usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                    recommand_dislike=ttk.Button(recommand_module,text='喜欢/不喜欢',command=dislike)
                    recommand_dislike.place(x=50,y=390)
                    recommand_reason=ttk.Button(recommand_module,text='推荐理由',command=recommand_reason)
                    recommand_reason.place(x=220,y=390)
                    recommand_read=ttk.Button(recommand_module,text='查看论文',command=recommand_reading)
                    recommand_read.place(x=390,y=390)
                
                elif (authorflag==True) and (os.path.exists(usr_name+'.txt')==False):
                    #subprocess.Popen("welcome.pyw",shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    #tk.messagebox.showinfo(title='Wait',message='由于您是新用户，系统正为您生成个性化推荐，请耐心等待30秒')
                    data_author=recommand_author_first(usr_name)
                    recommand_lb.delete(0,'end')
                    for item_author in data_author:
                        recommand_lb.insert('end',item_author)
                    
                    def recommand_reason():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            data_reason=reason(selected,usr_name,authorflag)
                            if authorflag==False:
                                tk.messagebox.showinfo(title='Reason',message='根据您所读的论文: '+data_reason.evaluate()+' 向您推荐！')
                            else:
                                tk.messagebox.showinfo(title='Reason',message='根据与您相似的作者: '+data_reason.evaluate()+' 向您推荐他的论文！')
                    def dislike():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            like_dislike=recommand_like_dislike(selected,usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                    recommand_dislike=ttk.Button(recommand_module,text='喜欢/不喜欢',command=dislike)
                    recommand_dislike.place(x=50,y=390)
                    recommand_reason=ttk.Button(recommand_module,text='推荐理由',command=recommand_reason)
                    recommand_reason.place(x=220,y=390)
                    recommand_read=ttk.Button(recommand_module,text='查看论文',command=recommand_reading)
                    recommand_read.place(x=390,y=390)
                    
                else:
                    #subprocess.Popen("welcome.pyw",shell=True)
                    f=open(usr_name+'.txt','r',encoding='utf-8')
                    data_initial=f.readlines()
                    recommand_lb.delete(0,'end')
                    for initial_item in data_initial:
                        initial_item=initial_item.strip()
                        recommand_lb.insert('end',initial_item)
                    f.close()
                    
                    def recommand_reason():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            data_reason=reason(selected,usr_name,authorflag)
                            if authorflag==False:
                                tk.messagebox.showinfo(title='Reason',message='根据您所读的论文: '+data_reason.evaluate()+' 向您推荐！')
                            else:
                                tk.messagebox.showinfo(title='Reason',message='根据与您相似的作者: '+data_reason.evaluate()+' 向您推荐他的论文！')
                    def dislike():
                            selected=recommand_lb.get(recommand_lb.curselection())
                            like_dislike=recommand_like_dislike(selected,usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                    recommand_dislike=ttk.Button(recommand_module,text='喜欢/不喜欢',command=dislike)
                    recommand_dislike.place(x=50,y=390)
                    recommand_reason=ttk.Button(recommand_module,text='推荐理由',command=recommand_reason)
                    recommand_reason.place(x=220,y=390)
                    recommand_read=ttk.Button(recommand_module,text='查看论文',command=recommand_reading)
                    recommand_read.place(x=390,y=390)

                #知识图谱
                def open_KG():
                    graph.open_browser()
                KG=ttk.Button(left,text='知识图谱',command=open_KG,width=20)
                KG.pack(side='top',fill=tk.X)
                #KG.place(x=50,y=550)

                #浏览历史
                def recommand_histroy(histroy_write):
                    if histroy_write==True:
                        histroy=graph.run("MATCH (:User{name:'"+usr_name+"'})-[r:Read]-(p:Article) RETURN p.name ORDER BY r.time DESC LIMIT 20")
                    else:
                        histroy=graph.run("MATCH (:User{name:'"+usr_name+"'})-[r:Written]-(p:Article) RETURN p.name LIMIT 20")
                    histroy_recommand=tk.Toplevel(recommand)
                    histroy_recommand.geometry('800x425+300+200')
                    if histroy_write==True:
                        histroy_recommand.title('浏览历史')
                    else:
                        histroy_recommand.title('写作信息')
                    histroy_recommand.resizable(0,0)
                    histroy_lb=tk.Listbox(histroy_recommand,width=120,height=20)
                    histroy_lb.pack()
                    for histroy_item in histroy:
                        histroy_lb.insert('end',histroy_item["p.name"])
                    xscrollbar = ttk.Scrollbar(histroy_recommand,orient='horizontal')
                    xscrollbar.pack(fill=tk.X)
                    histroy_lb['xscrollcommand'] = xscrollbar.set
                    xscrollbar.config(command=histroy_lb.xview)
                    def histroy_reading():
                        select_title.set(histroy_lb.get(histroy_lb.curselection()))
                        select_title_name=''
                        select_author_name=''
                        select_year_name=''
                        select_journal_name=''
                        #subprocess.Popen("fillline.pyw",shell=True)
                        data=graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})-[:Written]->(a:Author) WITH p,a MATCH (p)-[:InYear]->(y:Year) \
WITH p,a,y MATCH (p)-[:Publish]->(j:Journal) RETURN a.name,y.name,j.name")
                        for item in data:
                            select_author_name=select_author_name+item["a.name"]+'\t'
                            select_year_name='发表年份:\n\n'+item["y.name"]+'\n\n'
                            select_journal_name='发表期刊\n\n'+item["j.name"]+'\n\n'
                        select_author_name='作者:\n\n'+select_author_name+'\n\n'
                        if select_year_name=='':
                            select_year_name='发表年份:\n\n\n\n'
                        if select_journal_name=='':
                            select_journal_name='发表期刊\n\n\n\n'
                        select_title_name='您好！您现在正在查看的论文为:\n\n'+select_title.get()+'\n\n'
                        histroy_recommand.destroy()
                        #创建用户和论文之间关系
                        userread=graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})<-[r:Read]-(u:User{name:'"+usr_name+"'}) return r")
                        if userread.evaluate()==None:
                            graph.run("MATCH (p:Article{name:'"+select_title.get()+"'}),(u:User{name:'"+usr_name+"'}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)")
                        else:
                            graph.run("MATCH (p:Article{name:'"+select_title.get()+"'})<-[r:Read]-(u:User{name:'"+usr_name+"'}) SET r.click=r.click+1,r.time=timestamp()")
                        #论文信息窗口添加信息(article)
                        select.set(select_title_name+select_author_name+select_year_name+select_journal_name)
                        def dislike():
                            like_dislike=recommand_like_dislike(select_title.get(),usr_name)
                            if like_dislike==True:
                                tk.messagebox.showinfo(title='Like',message='将增加相似论文推荐！')
                            else:
                                tk.messagebox.showinfo(title='Dislike',message='将减少相似论文推荐！')
                        recommand_dislike=ttk.Button(article,text='喜欢/不喜欢',command=dislike)
                        recommand_dislike.place(x=60,y=390)
                        doi=ttk.Button(article,text='阅读论文',command=web_open).place(x=200,y=390)
                        
                    histroy_read=ttk.Button(histroy_recommand,text='查看论文',command=histroy_reading)
                    histroy_read.pack()
                #recommand_histroy函数结束
                def recommand_histroy_before():
                    recommand_histroy(True)
                HISTROY=ttk.Button(left,text='浏览历史',command=recommand_histroy_before,width=20)
                #HISTROY.place(x=200,y=550)
                HISTROY.pack(side='top',fill=tk.X)

                #写作信息
                if authorflag==True:
                    def write():
                        recommand_histroy(False)
                    Write=ttk.Button(left,text='写作信息',command=write,width=20)
                    Write.pack(side='top',fill=tk.X)
                #修改密码
                def recommand_password():
                    change_password=tk.Toplevel(recommand)
                    change_password.geometry('350x200+500+300')
                    change_password.title('修改密码')
                    change_password.resizable(0,0)

                    #修改密码信息
                    old_password=tk.StringVar()
                    ttk.Label(change_password,text='Old Password').place(x=10,y=10)
                    entry_old_password=ttk.Entry(change_password,textvariable=old_password,show='*')
                    entry_old_password.place(x=150,y=10)

                    new_pwd=tk.StringVar()
                    ttk.Label(change_password,text='New Password:').place(x=10,y=50)
                    entry_new_pwd=ttk.Entry(change_password,textvariable=new_pwd,show='*')
                    entry_new_pwd.place(x=150,y=50)

                    new_pwd_confirm=tk.StringVar()
                    ttk.Label(change_password,text='Confirm password:').place(x=10,y=90)
                    entry_new_pwd_confirm=ttk.Entry(change_password,textvariable=new_pwd_confirm,show='*')
                    entry_new_pwd_confirm.place(x=150,y=90)

                    def change_password_confirm():
                        old=old_password.get()
                        new=new_pwd.get()
                        confirm=new_pwd_confirm.get()
                        if graph.run("MATCH (u:User{name:'"+usr_name+"'}) RETURN u.password").evaluate()==old:
                            if new!=confirm:
                                tk.messagebox.showerror('Error','密码和确认密码必须相同！')
                            else:
                                graph.run("MATCH (u:User{name:'"+usr_name+"'}) SET u.password='"+new+"'")
                                tk.messagebox.showinfo('OK','你已修改成功！')
                                change_password.destroy() 
                        else:
                            tk.messagebox.showerror('Error','原密码错误!')
                    #修改密码按钮
                    confirm_change_password=ttk.Button(change_password,text='确认修改',command=change_password_confirm)
                    confirm_change_password.place(x=120,y=130)
                change_password=ttk.Button(left,text='修改密码',command=recommand_password,width=20)
                change_password.pack(side='top',fill=tk.X)

                #帮助
                def help_recommand():
                    HELP=tk.Toplevel(recommand)
                    HELP.geometry('800x120+300+300')
                    HELP.title('帮助')
                    HELP.resizable(0,0)
                    infor=tk.Label(HELP,text='本系统包括四个部分。\n 左侧栏包括六大功能：知识图谱、浏览历史、写作信息（如您是作者将有此功能）、修改密码、帮助和退出。\n上侧栏为对论文和作者的搜索框。\n\
中间界面为论文信息的查看，并包含喜欢/不喜欢和阅读论文两个功能键。\n右侧界面为论文推荐界面，界面上方显示20篇推荐论文，下方包含三个功能键喜欢/不喜欢、推荐理由和查看功能，\n选择界面上方的某篇论文后再点击功能键\
即可实现相应功能。\n')
                    infor.pack()
                Help=ttk.Button(left,text='帮助',command=help_recommand,width=20)
                Help.pack(side='top',fill=tk.X)
                
                #退出
                def quit_recommand():
                    doc=open(usr_name+'.txt','w',encoding='utf-8')
                    data=recommand_lb.get(0,'end')
                    for item in data:
                        print(item,file=doc)
                    doc.close()
                    recommand.destroy()
                    window.deiconify()
                QUIT=ttk.Button(left,text='退出',command=quit_recommand,width=20)
                QUIT.pack(side='top',fill=tk.X)

               
                #用户界面结束
            else:
                tk.messagebox.showerror(message='密码错误！请重试')
            break
    if userflag==False:
        
        is_sign_up=tk.messagebox.askyesno('Welcome','你还未注册，是否注册？')
        if is_sign_up:
            usr_sign_up()

#登录函数结束

#用户界面登录按钮
login=ttk.Button(window,text='Login',command=usr_login)
login.place(x=300,y=350)

#注册窗口
def usr_sign_up():
    def sign_up_confirm():
        nn=new_name.get()
        np=new_pwd.get()
        npc=new_pwd_confirm.get()
        userflag=False
        if np!=npc:
            tk.messagebox.showerror('Error','密码和确认密码必须相同！')
        elif graph.run("MATCH(a:User{name:'"+nn+"'}) RETURN a.name").evaluate()!=None:
            userflag=True
            tk.messagebox.showerror('Error','用户名已被注册!')
        else:
            p=Node("User", name=nn,password=np)
            graph.create(p)
            tk.messagebox.showinfo('Welcome','你已注册成功！')
            window_sign_up.destroy()
            
    window_sign_up=tk.Toplevel(window)
    window_sign_up.geometry('350x200+500+300')
    window_sign_up.title('注册窗口')
    window_sign_up.resizable(0,0)

    #注册用户信息
    new_name=tk.StringVar()
    new_name.set('example')
    ttk.Label(window_sign_up,text='Username:').place(x=10,y=10)
    entry_new_name=ttk.Entry(window_sign_up,textvariable=new_name)
    entry_new_name.place(x=150,y=10)

    new_pwd=tk.StringVar()
    ttk.Label(window_sign_up,text='Password:').place(x=10,y=50)
    entry_new_pwd=ttk.Entry(window_sign_up,textvariable=new_pwd,show='*')
    entry_new_pwd.place(x=150,y=50)

    new_pwd_confirm=tk.StringVar()
    ttk.Label(window_sign_up,text='Confirm password:').place(x=10,y=90)
    entry_new_pwd_confirm=ttk.Entry(window_sign_up,textvariable=new_pwd_confirm,show='*')
    entry_new_pwd_confirm.place(x=150,y=90)

    #注册窗口按钮
    confirm_sign_up=ttk.Button(window_sign_up,text='Sign up',command=sign_up_confirm)
    confirm_sign_up.place(x=120,y=130)
#注册函数结束

#用户界面注册按钮
sign_up=ttk.Button(window,text='Sign up',command=usr_sign_up)
sign_up.place(x=450,y=350)

window.mainloop()

