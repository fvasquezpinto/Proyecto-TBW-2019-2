# -*- coding: utf-8 -*-

import scrapy


class TbwImdbItem(scrapy.Item):

    review = scrapy.Field()
    rate = scrapy.Field()


class TbwFilmAffinityItem(scrapy.Item):

    review = scrapy.Field()
    rate = scrapy.Field()
