from scrapy import cmdline

# 请替换为你的 Scrapy 项目和爬虫名称
project_name = "doubanComment"
spider_name = "getInfo"

# 构造启动爬虫的命令
cmd = f"scrapy crawl {spider_name}"

# 使用 cmdline 模块执行命令
cmdline.execute(cmd.split())
