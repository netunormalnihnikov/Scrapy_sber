from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from Sber_pars import settings
from Sber_pars.spiders.sber import SberSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(SberSpider)

    process.start()
