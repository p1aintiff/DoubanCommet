import re
import scrapy
import json
from doubanComment.items import DoubanCommentItem;

"""
起始步骤：
遍历分类id 1-31, 通过api获取每个分类的所有电影信息
"""


class GetinfoSpider(scrapy.Spider):
    name = "apiJson"
    allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/chart"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'doubanComment.pipelines.ApiInfoPipeline': 400,
        },
        "DOWNLOADER_MIDDLEWARES": {
            'doubanComment.middlewares.MongoMiddleware': 543,  # 检查请求url是否在数据库中
            'doubanComment.middlewares.proxy': 544,  # 设置代理
        },
    }

    def parse(self, response):
        """
        分类及其 对应id
        """
        span_text = response.css('div.aside > div > div.types > span>a::text').getall()
        span_href = response.css('div.aside > div > div.types > span>a::attr(href)').getall()
        category = dict(zip(span_text, span_href))

        type_id_values = {}

        for genre, href in category.items():
            match = re.search(r'type=(\d+)', href)
            if match:
                type_id_value = match.group(1)
                type_id_values[genre] = int(type_id_value)

        # 如果分类有变化，使用这个
        # for type, id in type_id_values.items():
        #     json_url = f"https://movie.douban.com/j/chart/top_list?type={id}&interval_id=100%3A90&action=&start=20&limit=2000"
        #     yield scrapy.Request(json_url, callback=self.parse_all_movies)

        # 每一个分类的电影数量，可以设为2000，确保能获取全部
        amount = 2000
        # 当前分类id是1-31
        for i in range(1, 32):
            json_url = f"https://movie.douban.com/j/chart/top_list?type={i}&interval_id=100%3A90&action=&start=20&limit={amount}"
            yield scrapy.Request(json_url, callback=self.parse_all_movies)

    def parse_all_movies(self, response):
        """
        解析出各种电影的url
        """
        context = json.loads(response.text.replace("\n", ""))
        # print("context: ", context)
        item = DoubanCommentItem()
        item['apiJsons'] = context
