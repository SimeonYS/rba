import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import RbaItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class RbaSpider(scrapy.Spider):
	name = 'rba'
	start_urls = ['https://www.rba.hr/press/vijesti/2021']

	def parse(self, response):
		post_links = response.xpath('//div[@class="column gridModule x6 y12 z4"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="control next "]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)
		else:
			years = response.xpath('//div[@class="gridModule x4 y12 z4 subModule"]//ul/li/a[contains(text(),"Vijesti iz")]/@href').getall()
			for year in years:
				yield response.follow(year, self.parse)

	def parse_post(self, response):

		date = response.xpath('//div[@class="welcome gridModule x7 y12 z4"]/h4/text()').get()
		title = response.xpath('//div[@class="welcome gridModule x7 y12 z4"]/h1/text()').get()
		content = response.xpath('//div[@class="text gridModule x6 y12 z4"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=RbaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
