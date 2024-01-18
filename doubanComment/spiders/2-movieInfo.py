import scrapy
from bs4 import BeautifulSoup
import json
import re
from doubanComment.items import DoubanCommentItem
import html
import pymongo

# 每次运行考虑的前n个
START = 0
COUNTS = 1


class MovieinfoSpider(scrapy.Spider):
    name = "movieInfo"
    allowed_domains = ["movie.douban.com"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'doubanComment.pipelines.MovieInfoPipeLine': 400,
        },
        "DOWNLOADER_MIDDLEWARES": {
            'doubanComment.middlewares.MongoMiddleware': 543,  # 检查请求url是否在数据库中
            'doubanComment.middlewares.proxy': 544,  # 设置代理
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
        # todo
        query = {"all": 0}

        # 执行查询
        cursor = collection.find(query)
        # 提取所有文档的 URL 列表
        task_list = []

        for doc in cursor:
            task = {
            }
            url = doc.get("url")
            if doc.get("all"):
                task_list.append(url)

        print("获取到任务列表" + str(len(task_list)))

        # 选取一定数量的任务
        tasks = task_list[START:START + COUNTS]
        print(len(tasks), "个任务被选中")
        for one_task in tasks:
            yield scrapy.Request(url=one_task, callback=self.parse_one_movie, headers=headers)

    def parse_one_movie(self, response):
        """
        请求一个电影，获取详细信息,获取评论链接
        """
        item = DoubanCommentItem()

        # script type="application/ld+json"
        json_ld_script = response.xpath('/html//script[@type="application/ld+json"]').get()

        # 从script提出json - ld
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(json_ld_script, 'html.parser')

        # 提取包含 JSON-LD 数据的 <script> 标签的内容
        script_content = soup.find('script', {'type': 'application/ld+json'}).string
        script_content = html.unescape(script_content)
        # 解析 JSON-LD 数据为字典
        jsonld_data = json.loads(script_content.replace("\n", ""))

        ###################################

        comment_count_element = response.css('#comments-section > div.mod-hd > h2 > span > a::text').get()

        # 使用正则表达式提取数字
        comment_count = 0
        if comment_count_element:
            # 提取数字部分
            match = re.search(r'\d+', comment_count_element)
            if match:
                comment_count = int(match.group())
                jsonld_data['commentCount'] = comment_count

        # 电影信息
        item['movieInfo'] = jsonld_data
        # 评论数量
        item['all'] = comment_count
        # 电影链接
        item['subject_url'] = response.url
        yield item
