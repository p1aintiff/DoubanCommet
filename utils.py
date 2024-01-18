from pymongo import MongoClient


class Task:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]
        self.col = self.db['task']

        self.task = []

    def gen_task(self):
        all_url = self.db['apiJson'].distinct("url")
        print("评论任务总数" + str(len(all_url)))
        self.task = [{"url": url, "none": 0, "h": 0, "m": 0, "l": 0, "save": 0, "all": 0} for url in all_url]

    def save_task(self):
        # 删除所有
        self.col.delete_many({})
        # 重新插入
        result = self.col.insert_many(self.task)
        print(result)

    def checkUrl(self, url):
        for t in self.task:
            if t.url == url and t.save < t.all:
                return t.save
            else:
                return -1


if __name__ == "__main__":
    atask = Task()
    atask.gen_task()
    atask.save_task()
