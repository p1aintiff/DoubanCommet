# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging


class DoubancommentPipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        # 在爬虫启动时打开数据库连接
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]

    def close_spider(self, spider):
        # 在爬虫结束时关闭数据库连接
        if self.client:
            self.client.close()



    def process_item(self, item, spider):
        # 分类与id
        # typeId = item["typeId"]
        # if(typeId):    
        #     movieTypeCol = self.db["movieType"]
        #     result = movieTypeCol.insert_one(typeId)
        #     self.logger.info("save a typeid")
        
        # apiJson 获取阶段
        apiJson = item["apiJson"]
        if(apiJson):
            apiJsonCol = self.db["apiJson"]
            apiJsonCol.insert_one(apiJson)
            self.logger.info("insert a apiJson")



class MovieInfoPipeLine:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        # 在爬虫启动时打开数据库连接
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]

    def close_spider(self, spider):
        # 在爬虫结束时关闭数据库连接
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        collection = self.db["movieInfo"]
        if item.get('movieInfo'):
            collection.insert_one(item['movieInfo'])
        
        return item
    


class Comment:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        # 在爬虫启动时打开数据库连接
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]

    def close_spider(self, spider):
        # 在爬虫结束时关闭数据库连接
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        collection = self.db["movieComment"]
        if item.get("comment"):
            collection.insert_one(item['comment'])
        return item


class TaskManage:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        # 在爬虫启动时打开数据库连接
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]
    
    def close_spider(self, spider):
        # 在爬虫结束时关闭数据库连接
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        collection = self.db["task"]
        url = item.get('subject_url')
        allCount = item.get('all')
        theT = None
        # 只在电影评论生效？
        if(url):
            theT=collection.find_one({"url":url})
            print("get url", url)
        
            # 更新任务
            if theT:
                save = theT.get("save")
                all = theT.get("all")
                save = save+1
                none = theT.get('none')
                h = theT.get('h')
                m = theT.get('m')
                l = theT.get('l')
                if(item.get('type')):
                    type = item['type']
                    if(type == "none"):
                        none+=1
                    elif type =="h":
                        h+=1
                    elif type=="m":
                        m+=1
                    elif type == "l":
                        l+=1

                # 更新总数
                if allCount and all==0:
                    collection.update({"url":url},{"url":url,"save":save,"all":allCount, 'none':none, "h":h, "m":m,"l":l})
                    all=allCount

                if (save==all and all != 0) or save >= 3000:
                    # 删除任务
                    # collection.delete_one({"url":url})
                    pass
                else:
                    # 更新任务
                    collection.update({"url":url},{"url":url,"save":save,"all":all, 'none':none, "h":h, "m":m,"l":l})
    
        return item
