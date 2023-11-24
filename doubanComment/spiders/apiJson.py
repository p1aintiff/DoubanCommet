import re
import scrapy
import json
from doubanComment.items import DoubancommentItem;

from bs4 import BeautifulSoup


class GetinfoSpider(scrapy.Spider):
    name = "apiJson"
    allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/chart"]







    def parse(self, response):
        span_text = response.css('div.aside > div > div.types > span>a::text').getall()
        span_href = response.css('div.aside > div > div.types > span>a::attr(href)').getall()
        category = dict(zip(span_text, span_href))
        
        item = DoubancommentItem()
        type_id_values = {}

        for genre, href in category.items():
            match = re.search(r'type=(\d+)', href)
            if match:
                type_id_value = match.group(1)
                type_id_values[genre] = int(type_id_value)

        # item["typeId"] = type_id_values
        # yield item
        # 每一个分类的电影数量，可以设为2000，确保能获取全部
        amount = 2000
        for i in range(1, 32):
            jsonUrl = f"https://movie.douban.com/j/chart/top_list?type={i}&interval_id=100%3A90&action=&start=20&limit={amount}"
            yield scrapy.Request(jsonUrl, callback=self.parse_all_movies)



    

    def parse_all_movies(self, response):
        """
        解析出各种电影的url
        """
        context = json.loads(response.text.replace("\n", ""))
        # print("context: ", context)
        item = DoubancommentItem()
        for aMovie in context:
            item['apiJson'] = aMovie
            yield item
            # yield scrapy.Request(aMovie["url"], callback=self.parse_one_movie)