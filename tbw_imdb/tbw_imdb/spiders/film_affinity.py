from datetime import date
import urllib
import w3lib
import scrapy
import re

from tbw_imdb.items import TbwFilmAffinityItem as Item


class ImdbSpider(scrapy.Spider):

    name = "film_affinity"
    base_url = "https://www.filmaffinity.com"

    # Clear today's file when scraper runs, so remember to save it before run
    filename = "_".join(["filmaffinity_reviews", date.today().strftime("%d_%m_%Y")])
    filename = ".".join([filename, "txt"])
    file = open(filename, "w", encoding='utf8')
    file.close()

    custom_settings = {
        "ITEM_PIPELINES": {"tbw_imdb.pipelines.TbwFilmAffinityPipeline": 0},
        "USER_AGENT": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "DOWNLOAD_DELAY": 4,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4
    }

    def start_requests(self):

        urls = [
            urllib.parse.urljoin(self.base_url, "cl/main.html")
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        movies_by_theme_url = response.xpath("//a[contains(text(), 'Películas por temas')] /@href").get()
        yield response.follow(
            url=movies_by_theme_url,
            callback=self.parse_theme_catalog
        )

    def parse_theme_catalog(self, response):

        movie_theme_urls = response.xpath(
            "//a[contains(@class, 'topic')] /@href"
        ).getall()
        for movie_theme_url in movie_theme_urls:
            yield response.follow(
                url=movie_theme_url,
                callback=self.parse_theme_movie_list
            )

    def parse_theme_movie_list(self, response):

        movie_theme_list_url = response.xpath(
            "//li[contains(@class, 'active')] /a /@href"
        ).get()

        yield response.follow(
            url=movie_theme_list_url,
            callback=self.parse_theme
        )

    def parse_theme(self, response):

        titles_url = response.xpath(
            "//div[contains(@class, 'mc-title')] /a /@href"
        ).getall()

        for title_url in titles_url:
            yield response.follow(
                url=title_url,
                callback=self.parse_title
            )

        next_page_url = response.xpath(
            "//div[contains(@class, 'pager')] /a[contains(text(), '>>')] /@href"
        ).get()
        if next_page_url:

            yield response.follow(url=next_page_url, callback=self.parse_theme)

    def parse_title(self, response):

        user_reviews_url = response.xpath(
            "//li /a[contains(text(), 'Críticas')] /@href"
        ).get()

        if user_reviews_url:

            yield response.follow(
                    url=user_reviews_url,
                    callback=self.parse_user_reviews
            )

    def parse_user_reviews(self, response):

        reviews_selectors = response.xpath("//div[contains(@class, 'rw-item')]")

        for review_selector in reviews_selectors:

            user_rate = review_selector.xpath(
                "./div[contains(@class, 'mr-user-info-wrapper sn')] /div[contains(@class, 'user-reviews-movie-rating')] /text()"
            ).get()

            user_review = review_selector.xpath(
                "./div[contains(@class, 'review-text1')]"
            ).get()

            user_rate = user_rate.strip()

            user_review = w3lib.html.remove_tags(user_review).replace(";", "").strip()
            user_review = re.sub("(\n|\r){1,}", " ", user_review)

            if user_review and user_rate:

                item = Item()
                item["review"] = user_review
                item["rate"] = user_rate

                yield item

        next_page_url = response.xpath(
            "//div[contains(@class, 'pager')] /a[contains(text(), '>>')] /@href"
        ).get()

        if next_page_url:

            yield response.follow(
                url=next_page_url,
                callback=self.parse_user_reviews
            )
