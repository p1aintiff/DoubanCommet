# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging


class ApiInfoPipeline:
    """
    储存api的电影信息
    """

    def __init__(self):
        pass

    def open_spider(self, spider):
        # 在爬虫启动时打开数据库连接
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]

    def close_spider(self, spider):
        # 在爬虫结束时关闭数据库连接
        if self.client:
            self.client.close()

    def process_item(self, item, spider):

        # 保存api的json
        api_jsons = item["api_jsons"]
        if api_jsons:
            apiJsonCol = self.db["apiJson"]
            for api_json in api_jsons:
                apiJsonCol.insert_one(api_json)


class MovieInfoPipeLine:
    """
    电影的详细信息
    """

    def __init__(self):
        pass

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
    """
    电影评论
    """

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
        if item.get("comment"):
            collection = self.db["movieComment"]
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
        all_count = item.get('all')
        the_task = None
        if url:
            the_task = collection.find_one({"url": url})
            # 更新任务
            if the_task:
                save = the_task.get("save")
                all = the_task.get("all")
                save = save + 1
                none = the_task.get('none')
                h = the_task.get('h')
                m = the_task.get('m')
                l = the_task.get('l')
                if item.get('type'):
                    type = item['type']
                    if (type == "none"):
                        none += 1
                    elif type == "h":
                        h += 1
                    elif type == "m":
                        m += 1
                    elif type == "l":
                        l += 1

                # 更新总数
                if all_count and all == 0:
                    collection.update({"url": url},
                                      {"url": url, "save": save, "all": all_count, 'none': none, "h": h, "m": m,
                                       "l": l})

        return item
