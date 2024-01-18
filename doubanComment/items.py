# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanCommentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    typeId = scrapy.Field()
    apiJsons = scrapy.Field()

    movieInfo = scrapy.Field()

    comment = scrapy.Field()
    all = scrapy.Field()

    subject_url = scrapy.Field()

    type = scrapy.Field()
    typeNum = scrapy.Field()
