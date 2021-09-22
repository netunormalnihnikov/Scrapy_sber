from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import datetime
from Sber_pars import settings
from Sber_pars.spiders.sber import SberSpider

if __name__ == '__main__':
    time_format = "%Y-%m-%d %H:%M:%S"
    print(f"Время начала: {datetime.datetime.now(): {time_format}}")
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(SberSpider)

    process.start()
    print(f"Время окончания: {datetime.datetime.now(): {time_format}}")
