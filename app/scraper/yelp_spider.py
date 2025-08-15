import scrapy

class YelpSpider(scrapy.Spider):
    name = "yelp_leads"
    allowed_domains = ["yelp.com"]
    start_urls = [
        # Example: US city + niche. Adjust carefully and respect robots/ToS.
        "https://www.yelp.com/search?find_desc=restaurants&find_loc=Austin%2C%20TX"
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        for biz in response.css("h3 a[href*='/biz/']::attr(href)").getall():
            yield response.follow(biz, self.parse_biz)

        next_page = response.css("a.next-link::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_biz(self, response):
        name = response.css("h1::text").get()
        website = response.css("a[href^='http'][data-analytics-label='biz-website']::attr(href)").get()
        # Email often not available; you'll enrich later.
        yield {
            "name": name,
            "website": website,
            "source": response.url,
            "city": response.css("p:contains('Address') + p::text").get(),
        }

# NOTE: Many directories prohibit scraping. Prefer official APIs or opt-in sources.
