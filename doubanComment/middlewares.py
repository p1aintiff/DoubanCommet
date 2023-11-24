# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import pymongo
from time import sleep
import requests
from scrapy.exceptions import IgnoreRequest


class DoubancommentSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DoubancommentDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)





class MongoMiddleware:
    def __init__(self):
        self.url = "mongodb://localhost:27017"
        self.client = None
        print("dowloadMidel init")


    def process_request(self, request, spider):
        sleep(0.2)
        # 检查请求的 URL 是否在 MongoDB 中
        print("检验", request.url[:42])

        theT =self.url_in_mongo(request.url[:42])
        if theT:
            return None  # 如果存在，继续请求
        else:
            # 如果不存在，阻止请求
            raise IgnoreRequest(f"URL {request.url} not found in MongoDB")
            return 

    def process_response(self, request, response, spider):
        # 检查响应的 URL 是否在 MongoDB 中
        # theT = self.url_in_mongo(request.url)
        # if theT:
        #     save,all = theT
        #     save = save+1
        #     if save==all:
        #         # 删除任务
        #         self.collection.delete_one("url",response.url)
        #     else:
        #         # 更新任务
        #         self.collection.update({"url":response.url},{"url":response.url,"save":save,"all":all})
        return response

    def url_in_mongo(self, url):
        # 连接 MongoDB
        if not self.client:
            self.client = pymongo.MongoClient(self.url)

        # 获取指定的集合
        self.collection = self.client["douban"]["task"]

        # 查询 URL 是否存在
        result = self.collection.find_one({'url': url})
        if result:
            return (result['save'],result['all'])
        else:
            return None

    def spider_closed(self, spider):
        # 关闭 MongoDB 连接
        if self.client:
            self.client.close()
        
        print("close mid")



class proxy:

    def __init__(self):
            self.url = "mongodb://localhost:27017"
            self.client = None
    
    def process_request(self, request, spider):
        proxy = get_proxy().get("proxy")
        # proxy = get_dok_proxy()
        print(proxy)
        request.meta['proxy'] = "http://"+proxy

        return None


def get_dok_proxy():
    return requests.get("https://api2.docip.net/v1/get_proxy_status?api_key=shGomj9vDfaTyCD6WYtRUF4M655f61db&tunnel=1").json()[0] 

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# your spider code

def getHtml():
    # ....
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            html = requests.get('http://www.example.com', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    return None

if __name__ == '__main__':
    # m = MongoMiddleware()
    # m.url_in_mongo("https://movie.douban.com/subject/10432911/")
    proxy = get_dok_proxy()
    print(proxy[0])

