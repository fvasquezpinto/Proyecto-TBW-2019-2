# -*- coding: utf-8 -*-

from datetime import date
import re


class TbwImdbPipeline(object):
    def process_item(self, item, spider):

        user_review = item["review"]
        text = ";".join([item["rate"], re.sub("\n", "", user_review)])
        text = "".join([text, "\n"])

        filename = "_".join(["IMDb_reviews", date.today().strftime("%d_%m_%Y")])
        filename = ".".join([filename, "txt"])
        with open(filename, 'a', encoding='utf8') as f:
            f.write(text)


class TbwFilmAffinityPipeline(object):
    def process_item(self, item, spider):

        user_review = item["review"]
        text = ";".join([item["rate"], re.sub("\n", "", user_review)])
        text = "".join([text, "\n"])

        filename = "_".join(["filmaffinity_reviews", date.today().strftime("%d_%m_%Y")])
        filename = ".".join([filename, "txt"])
        with open(filename, 'a', encoding='utf8') as f:
            f.write(text)
