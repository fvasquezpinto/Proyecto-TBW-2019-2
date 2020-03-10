from datetime import date
import w3lib
import scrapy

from tbw_imdb.items import TbwImdbItem as Item


class ImdbSpider(scrapy.Spider):

    name = "imdb"
    base_url = "https://www.imdb.com/"

    # Clear today's file when scraper runs, so remember to save it before run
    filename = "_".join(["IMDb_reviews", date.today().strftime("%d_%m_%Y")])
    filename = ".".join([filename, "txt"])
    file = open(filename, "w", encoding='utf8')
    file.close()

    custom_settings = {
        "ITEM_PIPELINES": {"tbw_imdb.pipelines.TbwImdbPipeline": 0},
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": None,
        },
        "DOWNLOAD_DELAY": 1,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4
    }

    LOAD_MORE_REVIEWS_QUERY_URL = "https://www.imdb.com/title/tt6751668/reviews/_ajax?ref_=undefined&paginationKey="

    def start_requests(self):

        urls = [
            "https://www.imdb.com/"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        yield response.follow(
            url="https://www.imdb.com/feature/genre/?ref_=nv_ch_gr",
            callback=self.parse_genre_catalog
        )

    def parse_genre_catalog(self, response):

        movie_and_tvshow_genres_urls = response.xpath(
            "//div[@class='image'] /a /@href"
        ).getall()
        for movie_and_tvshow_genre_url in movie_and_tvshow_genres_urls:
            yield response.follow(
                url=movie_and_tvshow_genre_url,
                callback=self.parse_genre
            )

    def parse_genre(self, response):

        titles_url = response.xpath(
            "//h3[@class='lister-item-header'] /a /@href"
        ).getall()
        for title_url in titles_url:
            yield response.follow(
                url=title_url,
                callback=self.parse_title
            )

        next_page_url = response.xpath(
            "//div[@class='desc'] /a[contains(text(), 'Next')] /@href"
        ).get()
        yield response.follow(url=next_page_url, callback=self.parse_genre)

    def parse_title(self, response):

        user_reviews_url = response.xpath(
            "//a[contains(text(), 'USER REVIEWS')] /@href"
        ).get()

        yield response.follow(
                url=user_reviews_url,
                callback=self.parse_user_reviews
        )

    def parse_user_reviews(self, response):

        reviews_selectors = response.xpath("//div[@class='lister-item-content']")
        for review_selector in reviews_selectors:

            rate_scale = review_selector.xpath(
                "./div /span /span[@class='point-scale'] /text()"
            ).get()
            user_rate = None
            if rate_scale == "/10":
                user_rate = review_selector.xpath("./div /span /span /text()").get()

            user_review = review_selector.xpath(
                "./div /div[contains(@class, 'text show')]"
            ).get()
            user_review = w3lib.html.remove_tags(user_review)

            if user_review and user_rate:

                item = Item()
                item["review"] = user_review
                item["rate"] = user_rate

                yield item

        load_more_reviews_query_key = response.xpath(
            "//div[@class='load-more-data'] /@data-key"
        ).get()

        if load_more_reviews_query_key:
            load_more_reviews_url = "{}{}".format(
                self.LOAD_MORE_REVIEWS_QUERY_URL,
                load_more_reviews_query_key
            )
            yield response.follow(
                url=load_more_reviews_url,
                callback=self.parse_user_reviews
            )
