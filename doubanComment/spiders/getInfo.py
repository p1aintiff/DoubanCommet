import re

import scrapy
import json

from bs4 import BeautifulSoup


class GetinfoSpider(scrapy.Spider):
    name = "getInfo"
    allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/chart"]

    def parse(self, response):
        span_text = response.css('div.aside > div > div.types > span>a::text').getall()
        span_href = response.css('div.aside > div > div.types > span>a::attr(href)').getall()
        with open('allcates.html', 'w') as f:
            f.write(response.text)
        category = dict(zip(span_text, span_href))
        # todo get id only
        with open("category.json", "w", encoding="utf-8") as f:
            json.dump(category, f, ensure_ascii=False, indent=1)

        # 每一个分类的数量
        amount = 1
        for i in range(1, 3):
            jsonUrl = f"https://movie.douban.com/j/chart/top_list?type={i}&interval_id=100%3A90&action=&start=20&limit={amount}"
            yield scrapy.Request(jsonUrl, callback=self.parse_all_movies)

    def parse_all_movies(self, response):
        context = json.loads(response.text.replace("\n", ""))
        print("context: ", context)
        allContext = []
        with open("allMovie.json", "r", encoding="utf-8") as fr:
            allContext = json.loads(fr.read())
        allContext.extend(context)
        print("all: ", allContext)
        with open("allMovie.json", "w", encoding="utf-8") as fw:
            fw.write(json.dumps(allContext, ensure_ascii=False, indent=1))
        for js in context:
            yield scrapy.Request(js["url"], callback=self.parse_one_movie)

    def parse_one_movie(self, response):
        path = "movieInfos"

        # print(response.text)
        with open(path + "/1.html", "w", encoding="utf-8") as fw:
            fw.write(response.text)

        # script type="application/ld+json"

        json_ld_script = response.xpath('/html//script[@type="application/ld+json"]').get()
        # 从script提出json - ld

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(json_ld_script, 'html.parser')

        # 提取包含 JSON-LD 数据的 <script> 标签的内容
        script_content = soup.find('script', {'type': 'application/ld+json'}).string

        # 解析 JSON-LD 数据为字典
        # todo success
        jsonld_data = json.loads(script_content)

        # 打印提取的字典数据
        # print()

        print("url", response.url)
        amount = 3
        past_url = f"comments?percent_type=&start=0&limit={amount}&status=P&sort=new_score&comments_only=1"
        yield scrapy.Request(response.url + past_url, callback=self.parse_commets)

    def parse_commets(self, response):
        # print(response.text)
        commet = json.loads(response.text)
        # print(commet["html"])
        with open("commet.html", "w", encoding='utf-8') as fw:
            fw.write(commet["html"])

        # 解析html文本
        soup = BeautifulSoup(commet["html"], 'html.parser')

        # div.avatar>a title(name) href(person url)

        #  span.comment-vote > span (text, 有用数)

        # span.comment-time title （评论时间）

        # span.short (评论)

        # 提取评论信息
        comment_item = soup.find('div', class_='comment-item')

        # 提取演员名字和个人主页链接
        name = comment_item.select_one('.avatar > a')['title']
        person_url = comment_item.select_one('.avatar > a')['href']

        # 提取有用数
        useful_count = comment_item.select_one('.votes.vote-count').text.strip()

        # 提取评论时间
        comment_time = comment_item.select_one('.comment-time')['title']

        # 提取评论内容
        comment_content = comment_item.select_one('.short').text.strip()

        # 打印提取的信息
        print(f"评论人名字: {name}")
        print(f"个人主页链接: {person_url}")
        print(f"有用数: {useful_count}")
        print(f"评论时间: {comment_time}")
        print(f"评论内容: {comment_content}")

        # 提取评分信息
        rating_span = soup.find('span', class_=re.compile(r'allstar\d+ rating'))
        if rating_span:
            rating = int(re.search(r'\d+', rating_span['class'][0]).group())
            print(f"评分: {rating}")
        else:
            print("未找到评分信息")

        # 提取评论报告链接
        comment_report_div = soup.find('div', class_='comment-report')
        if comment_report_div:
            data_url = comment_report_div['data-url']
            subject_id_match = re.search(r'/subject/(\d+)/comments\?comment_id=(\d+)', data_url)
            if subject_id_match:
                subject_id = subject_id_match.group(1)
                comment_id = subject_id_match.group(2)
                print(f"Subject ID: {subject_id}")
                print(f"Comment ID: {comment_id}")
            else:
                print("未找到匹配的Subject ID和Comment ID")
        else:
            print("未找到评论报告链接")
