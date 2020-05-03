from py2neo import Graph,Node,Relationship,authenticate
def recommand_article(data):
    graph=Graph()
    record=graph.run("MATCH (m:Article)<-[r:Read]-(u:User{name:'"+data+"'}) WITH m,u ORDER BY r.click DESC LIMIT 3\
                     MATCH (m:Article)-[:Written|:InYear|:Publish]->(t)<-[:Written|:InYear|:Publish]-(other:Article) \
                    WHERE NOT (other)-[:Read]-(u) AND NOT (other)-[:Dislike]-(u)\
                    WITH m, other, COUNT (t) AS intersection \
                    MATCH (m:Article)-[:Written|:InYear|:Publish]-(mt) \
                    WITH m,other, intersection, COLLECT (mt.name) AS s1 \
                    MATCH (other:Article)-[:Written|:InYear|:Publish]-(ot) \
                    WITH m,other,intersection, s1, COLLECT (ot.name) AS s2 \
                    WITH m,other,intersection,s1,s2 WITH m,other,intersection,s1+filter(x IN s2 WHERE NOT x IN s1) AS union, s1, s2 \
                    WITH m,other,intersection,union,s1,s2,((1.0*intersection)/SIZE(union)) AS jaccard WHERE jaccard<1 \
                    WITH other,sum(jaccard) as r\
                    RETURN other.name ORDER BY r DESC LIMIT 20")
    return record
def recommand_author_first(data):
    graph=Graph()
    list_article=[]
    record=graph.run("MATCH (m:User{name:'"+data+"'})-[:InJournal]-(t:Journal)-[:InJournal]-(other:User) WITH m, other, COUNT(t) AS intersection \
                        WHERE NOT other.name=m.name\
                        MATCH (m)-[:InJournal]-(mt)\
                        WITH m,other, intersection, COLLECT(mt.name) AS s1\
                        MATCH (other)-[:InJournal]-(ot)\
                        WITH m,other,intersection, s1, COLLECT(ot.name) AS s2\
                        WITH m,other,intersection,s1,s2\
                        WITH m,other,intersection,s1+filter(x IN s2 WHERE NOT x IN s1) AS union, s1, s2\
                        WITH m,other,intersection,union,s1,s2,((1.0*intersection)/SIZE(union)) AS jaccard WHERE jaccard<1\
                        RETURN other.name ORDER BY jaccard DESC LIMIT 10")
    doc=open(data+'-author.txt','w',encoding='utf-8')
    for item in record:
        print(item["other.name"],file=doc)
        '''author_record=graph.run("MATCH (u:User{name:'"+data+"'}) WITH u MATCH (m:User{name:'"+item["other.name"]+"'})-[:Written]-(a:Article) WHERE NOT (u)-[:Written|:Read|:Dislike]-(a) RETURN a.name LIMIT 4")
        for author_item in author_record:
            if len(list_article)<20:
                list_article.append(author_item["a.name"])
            else:
                break'''
    author_record=graph.run("MATCH (m:User{name:'"+data+"'})-[:InJournal]-(t:Journal)-[:InJournal]-(other:User) WITH m, other, COUNT(t) AS intersection \
                        WHERE NOT other.name=m.name\
                        MATCH (m)-[:InJournal]-(mt)\
                        WITH m,other, intersection, COLLECT(mt.name) AS s1\
                        MATCH (other)-[:InJournal]-(ot)\
                        WITH m,other,intersection, s1, COLLECT(ot.name) AS s2\
                        WITH m,other,intersection,s1,s2\
                        WITH m,other,intersection,s1+filter(x IN s2 WHERE NOT x IN s1) AS union, s1, s2\
                        WITH m,other,intersection,union,s1,s2,((1.0*intersection)/SIZE(union)) AS jaccard WHERE jaccard<1\
                        WITH m,other,jaccard ORDER BY jaccard DESC LIMIT 10\
                        MATCH (other)-[:Written]-(p:Article)\
                        WHERE NOT (m)-[:Read]-(p) AND NOT (m)-[:Dislike]-(p)\
                        with SUM(jaccard)as r,p\
                        RETURN p.name ORDER BY r DESC LIMIT 20")
    for author_item in author_record:
        list_article.append(author_item["p.name"])
    doc.close()
    return list_article


def recommand_author(data):
    graph=Graph()
    list_article=[]
    author_record=graph.run("MATCH (m:User{name:'"+data+"'})-[:InJournal]-(t:Journal)-[:InJournal]-(other:User) WITH m, other, COUNT(t) AS intersection \
                        WHERE NOT other.name=m.name\
                        MATCH (m)-[:InJournal]-(mt)\
                        WITH m,other, intersection, COLLECT(mt.name) AS s1\
                        MATCH (other)-[:InJournal]-(ot)\
                        WITH m,other,intersection, s1, COLLECT(ot.name) AS s2\
                        WITH m,other,intersection,s1,s2\
                        WITH m,other,intersection,s1+filter(x IN s2 WHERE NOT x IN s1) AS union, s1, s2\
                        WITH m,other,intersection,union,s1,s2,((1.0*intersection)/SIZE(union)) AS jaccard WHERE jaccard<1\
                        WITH m,other,jaccard ORDER BY jaccard DESC LIMIT 10\
                        MATCH (other)-[:Written]-(p:Article)\
                        WHERE NOT (m)-[:Read]-(p) AND NOT (m)-[:Dislike]-(p)\
                        with SUM(jaccard)as r,p\
                        RETURN p.name ORDER BY r DESC LIMIT 20")
    for author_item in author_record:
        list_article.append(author_item["p.name"])
    return list_article

def reason(data,name,flag):
    graph=Graph()
    list_author=[]
    if flag==False:
        read=graph.run("MATCH (other:Article)-[:Read]-(:User{name:'"+name+"'}) \
                    WITH other \
                    MATCH (m:Article {name:'"+data+"'})-[:Written|:InYear|:Publish]-(t)<-[:Written|:InYear|:Publish]-(other:Article)\
                    WITH m, other, COUNT(t) AS intersection \
                    MATCH (m)-[:Written|:InYear|:Publish]-(mt)\
                    WITH m,other, intersection, COLLECT(mt.name) AS s1\
                    MATCH (other)-[:Written|:InYear|:Publish]-(ot)\
                    WITH m,other,intersection, s1, COLLECT(ot.name) AS s2\
                    WITH m,other,intersection,s1,s2\
                    WITH m,other,intersection,s1+filter(x IN s2 WHERE NOT x IN s1) AS union, s1, s2\
                    WITH m,other,intersection,union,s1,s2,((1.0*intersection)/SIZE(union)) AS jaccard WHERE jaccard<1\
                    RETURN other.name ORDER BY jaccard DESC  LIMIT 1")
    else:
        f=open(name+'-author.txt','r',encoding='utf-8')
        data_initial=f.readlines()
        read=graph.run("MATCH (p:Article{name:'"+data+"'})-[:Written]-(u:User) RETURN u.name")
        for item in read:
            list_author.append(item["u.name"])
        for initial_item in data_initial:
                initial_item=initial_item.strip()
                '''read=graph.run("MATCH (other:User{name:'"+initial_item+"'})-[:Written]-(p:Article{name:'"+data+"'}) RETURN other.name")
                if read.evaluate()!=None:'''
                if initial_item in list_author:
                    read=graph.run("MATCH (other:User{name:'"+initial_item+"'})-[:Written]-(p:Article{name:'"+data+"'}) RETURN other.name")
                    break
        f.close()
    return read

def recommand_like_dislike(data,name):
    graph=Graph()
    '''#相似论文
    record=graph.run('MATCH (m:Article {name: "'+data+'"})-[:Written|:InYear|:Publish]-(t)<-[:Written|:InYear|:Publish]-(other:Article) \
                      WITH m, other, COUNT(t) AS intersection \
                      MATCH (m)-[:Written|:InYear|:Publish]-(mt)\
                      WITH m,other, intersection, COLLECT(mt.name) AS s1\
                      MATCH (other)-[:Written|:InYear|:Publish]-(ot)\
                      WITH m,other,intersection, s1, COLLECT(ot.name) AS s2\
                      WITH m,other,intersection,s1,s2\
                      WITH m,other,intersection,s1+filter(x IN s2 WHERE NOT x IN s1) AS union, s1, s2\
                      WITH m,other,intersection,union,s1,s2,((1.0*intersection)/SIZE(union)) AS jaccard\
                      RETURN other.name ORDER BY jaccard DESC LIMIT 5')
    for item in record:
        if graph.run('MATCH (:User{name:"'+name+'"})-[r:Read]-(:Article{name:"'+item["other.name"]+'"}) RETURN r').evaluate()==None:
            if graph.run('MATCH (:User{name:"'+name+'"})-[r:Dislike]-(:Article{name:"'+item["other.name"]+'"}) RETURN r').evaluate()==None:
                graph.run('MATCH (u:User{name:"'+name+'"}),(p:Article{name:"'+item["other.name"]+'"}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)')
            else:
                graph.run('MATCH (:User{name:"'+name+'"})-[r:Dislike]-(:Article{name:"'+item["other.name"]+'"}) DELETE r')
                graph.run('MATCH (u:User{name:"'+name+'"}),(p:Article{name:"'+item["other.name"]+'"}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)')
        else:
            graph.run('MATCH (:User{name:"'+name+'"})-[r:Read]-(:Article{name:"'+item["other.name"]+'"}) DELETE r')
            graph.run('MATCH (u:User{name:"'+name+'"}),(p:Article{name:"'+item["other.name"]+'"}) CREATE (u)-[:Dislike]->(p)')'''

    #该论文
    if graph.run('MATCH (:User{name:"'+name+'"})-[r:Read]-(:Article{name:"'+data+'"}) RETURN r').evaluate()==None:
        if graph.run('MATCH (:User{name:"'+name+'"})-[r:Dislike]-(:Article{name:"'+data+'"}) RETURN r').evaluate()==None:
            graph.run('MATCH (u:User{name:"'+name+'"}),(p:Article{name:"'+data+'"}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)')
            return True
        else:
            graph.run('MATCH (:User{name:"'+name+'"})-[r:Dislike]-(:Article{name:"'+data+'"}) DELETE r')
            graph.run('MATCH (u:User{name:"'+name+'"}),(p:Article{name:"'+data+'"}) CREATE (u)-[:Read{click:1,time:timestamp()}]->(p)')
            return True
    else:
        graph.run('MATCH (:User{name:"'+name+'"})-[r:Read]-(:Article{name:"'+data+'"}) DELETE r')
        graph.run('MATCH (u:User{name:"'+name+'"}),(p:Article{name:"'+data+'"}) CREATE (u)-[:Dislike]->(p)')
        return False

