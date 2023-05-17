import scrapy
import json
import logging
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import difflib

class JsonExportPipeline:

    def open_spider(self, spider):
        self.file = open('results.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class VGSpider(scrapy.Spider):
    name = "game_spider"

    def __init__(self, game_name=None, *args, **kwargs):
        super(VGSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.vgchartz.com/games/games.php?name={game_name}']

    custom_settings = {
        'LOG_LEVEL': logging.ERROR,
        'ITEM_PIPELINES': {'__main__.JsonExportPipeline': 1},
    }


    def parse(self, response):
        GAME_SELECTOR = '//*[@id="generalBody"]/table[1]/tr'

        for row in response.xpath(GAME_SELECTOR):
            game_data = {
                'title': row.xpath('.//td[3]/a/text()').get(),
                'total_shipped': row.xpath('.//td[9]/text()').get(),
            }

            if game_data['title']:
                print(f"Scraped data: {game_data}")
                yield game_data

def scrape_game_data(game_name):
    process = CrawlerProcess(get_project_settings())
    process.crawl(VGSpider, game_name=game_name)
    process.start(stop_after_crawl=True)

if __name__ == "__main__":
    game_name = sys.argv[1]
    scrape_game_data(game_name)