import scrapy
from bs4 import BeautifulSoup
import json
import re
from doubanComment.items import DoubancommentItem
import html
import pymongo
import time


# 每次运行考虑的前n个
START = 0
URLS = 500

# # 前n个中最多爬取的数量
# ONETASK = 1
# # 每个电影的 每次评论请求数量
# COMMENT_STEP = 1000


class MovieinfoSpider(scrapy.Spider):
    name = "movieInfo"
    allowed_domains = ["movie.douban.com"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'doubanComment.pipelines.MovieInfoPipeLine': 400,
            # 'doubanComment.pipelines.Comment': 401,
            'doubanComment.pipelines.TaskManage': 403,
        },
        "DOWNLOADER_MIDDLEWARES":{
            'doubanComment.middlewares.MongoMiddleware': 543,  # 调整优先级
            'doubanComment.middlewares.proxy': 544,  # 调整优先级
        },
    }

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        }

        # 使用mongodb启动
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client["douban"]
        collection = self.db["task"]
        query = {
            "$or": [
                {"none": 0},
                {"h": 0},
                {"m": 0},
                {"l": 0},
            ]
        }




        # 执行查询
        cursor = collection.find(query)
        # 提取所有文档的 URL 列表
        task_list = []
        task = {
            "movie":"",
            "none": "",
            "h":"",
            "m":"",
            "l":""
        }

        for doc in cursor:
            task = {
            }
            url=doc.get("url")
            if doc.get("save"):
                task_list.append(url)
            
            


        print("get mongo task",len(task_list))
        



        tasks = task_list[START:URLS]
        print(len(tasks)," is in task!")
        for ontask in tasks:
    
            yield scrapy.Request(url=ontask, callback=self.parse_one_movie, headers=headers)
        


    
    def parse_one_movie(self, response):
        """
        请求一个电影，获取详细信息,获取评论链接
        """
        item = DoubancommentItem()

        # script type="application/ld+json"

        json_ld_script = response.xpath('/html//script[@type="application/ld+json"]').get()
        # 从script提出json - ld

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(json_ld_script, 'html.parser')

        # 提取包含 JSON-LD 数据的 <script> 标签的内容
        script_content = soup.find('script', {'type': 'application/ld+json'}).string
        script_content = html.unescape(script_content)
        # 解析 JSON-LD 数据为字典
        jsonld_data = json.loads(script_content.replace("\n",""))
        item['movieInfo'] = jsonld_data
        
        
        ###################################

        comment_count_element = response.css('#comments-section > div.mod-hd > h2 > span > a::text').get()

        # 使用正则表达式提取数字
        if comment_count_element:
            # 提取数字部分
            match = re.search(r'\d+', comment_count_element)
            if match:
                comment_count = int(match.group())
                
        
        jsonld_data['commentCount'] = comment_count



        # print("url", response.url)
        item['all'] = comment_count
        item['subject_url'] = response.url
        yield item