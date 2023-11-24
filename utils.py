from pymongo import MongoClient


class Task:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]
        self.col = self.db['task']

        self.task=[]
    


    def genTask(self):
        allUrl = self.db['apiJson'].distinct("url")
        print(len(allUrl))

        self.task = [{"url":url, "none":0, "h":0, "m":0, "l":0, "save":0, "all": 0} for url in allUrl]
    
    def updateTaskTable(self):
        # 查询数量，而不是默认0
        pass

    def loadTask(self):
        
        self.task = self.col.fond()
        print("load ", len(self.task),"条")

        
    def genTable(self):
        # 删除所有
        self.col.delete_many({})
        # 重新插入
        result=self.col.insert_many(self.task)
        print(result)
    

    def checkUrl(self, url):
        for t in self.task:
            if t.url == url and t.save<t.all:
                return t.save
            else:
                return -1
    
    def deleteComment(self):
        collection =self.db['movieComment']
        collection.delete_many({})
    
    def deleteMovieInfo(self):
        collection =self.db['movieInfo']
        collection.delete_many({})
    

if __name__ == "__main__":
    atask = Task()
    atask.genTask()
    atask.genTable()
    # atask.deleteComment()
    # atask.deleteMovieInfo()




