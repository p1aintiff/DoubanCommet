from scrapy import cmdline

# 使用 cmdline 模块执行命令
cmdline.execute("scrapy crawl movieInfo".split())
cmdline.execute("scrapy crawl comments".split())
