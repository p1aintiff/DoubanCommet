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


class CommentsSpider(scrapy.Spider):
    name = "comments"
    allowed_domains = ["movie.douban.com"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'doubanComment.pipelines.MovieInfoPipeLine': 400,
            'doubanComment.pipelines.Comment': 401,
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
            if doc.get("none")==0:
                task["none"]=url+"comments?percent_type=&start=0&limit=600&status=P&sort=new_score&comments_only=1"
            if doc.get("h")==0:
                task["h"]=url+"comments?percent_type=h&start=0&limit=600&status=P&sort=new_score&comments_only=1"
            if doc.get("m")==0:
                task["m"]=url+"comments?percent_type=m&start=0&limit=600&status=P&sort=new_score&comments_only=1"
            if doc.get("l")==0:
                task["l"]=url+"comments?percent_type=l&start=0&limit=600&status=P&sort=new_score&comments_only=1"
            

            task_list.append(task)
            
            


        print("get mongo task",len(task_list))
        



        tasks = task_list[START:URLS]
        print(len(tasks)," is in task!")
        for ontask in tasks:
                for key,value in ontask.items():
                    yield scrapy.Request(url=value, callback=self.parse_commets, headers=headers, meta={"type":key})
    
                
  


    def parse_commets(self, response):
        """
        解析评论
        """

        print('this comment url', response.url)
        
        item=DoubancommentItem()
        type = response.meta['type']
        if type:
            item['type'] = type
        print('tyhe type:   ', type)
        time.sleep(1)
        all = response.meta.get("all")
        if(all):
            item['all']=all

        commet = json.loads(response.text)

        # 解析html文本
        soup = BeautifulSoup(commet["html"], 'html.parser')

        # div.avatar>a title(name) href(person url)
        #  span.comment-vote > span (text, 有用数)
        # span.comment-time title （评论时间）
        # span.short (评论)

        # 提取评论信息
        comment_items = soup.find_all('div', class_='comment-item')

        for comment_item in comment_items:
            # 提取演员名字和个人主页链接
            name = comment_item.select_one('.avatar > a')['title']
            person_url = comment_item.select_one('.avatar > a')['href']

            # 提取有用数
            useful_count = comment_item.select_one('.votes.vote-count').text.strip()

            # 提取评论时间
            comment_time = comment_item.select_one('.comment-time')['title']

            # 提取评论内容
            comment_content = comment_item.select_one('.short').text.strip()


            # 提取评分信息
            rating_span = soup.find('span', class_=re.compile(r'allstar\d+ rating'))
            if rating_span:
                rating = int(re.search(r'\d+', rating_span['class'][0]).group())

            # 提取评论报告链接
            comment_report_div = soup.find('div', class_='comment-report')
            if comment_report_div:
                data_url = comment_report_div['data-url']

                subject_id_match = re.search(r'/subject/(\d+)/comments\?comment_id=(\d+)', data_url)
                if subject_id_match:
                    subject_id = subject_id_match.group(1)
                    comment_id = subject_id_match.group(2)
            
            movieUrl = "https://movie.douban.com/subject/"+subject_id+"/"
            commentUrl = movieUrl+"?comment_id="+comment_id


            commentInfo = {
                "person": name,
                "person_url": person_url,
                "useful_count":useful_count,
                "time":comment_time,
                "content":comment_content,
                "rating":rating,
                "movie_url":movieUrl,
                "url":commentUrl,
            }

            item['subject_url'] = movieUrl
            item['comment'] = commentInfo
            yield item

        print("css class count", len(comment_items))
        # print('url: ',response.meta['url'])