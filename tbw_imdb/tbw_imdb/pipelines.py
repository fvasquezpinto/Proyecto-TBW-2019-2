# -*- coding: utf-8 -*-

from datetime import date


class TbwImdbPipeline(object):
    def process_item(self, item, spider):

        text = "\n".join([item["rate"], item["review"]])
        text = "".join([text, "\n\n"])

        filename = "_".join(["IMDb_reviews", date.today().strftime("%d_%m_%Y")])
        filename = ".".join([filename, "txt"])
        with open(filename, 'a') as f:
            f.write(text)
