import scrapy
import re


class FundaSpider(scrapy.Spider):
	name = "funda"
	start_urls = [
	]

	def parse(self, response):
		houses = response.css('li.search-result')
		self.log('Found {} houses.'.format(len(houses)))

		for house in houses:
			if len(house.css('li.label-transactie-voorbehoud')):
				continue

			yield {
				'id'           : str(house.css('a::attr(data-search-result-item-anchor)').extract_first()),
				'link'         : response.urljoin(str(house.css('a[href*="koop"]::attr(href)').extract_first())),
				'street'       : str(house.css('h3.search-result-title::text').extract_first(default='').encode('ascii', 'ignore').strip()),
				'postal'       : str(house.css('small.search-result-subtitle::text').extract_first(default='').strip()),
				'thumbnail'    : str(house.css('img::attr(src)').extract_first()),
				'price'        : str(re.sub('[^0-9]','', str(house.css('span.search-result-price::text').extract_first(default='').encode('ascii', 'ignore')))),
				'living-area'  : str(re.sub('[^0-9]','', str(house.css('span[title="Woonoppervlakte"]::text').extract_first(default='').encode('ascii', 'ignore')))),
				'land-surface' : str(re.sub('[^0-9]','', str(house.css('span[title="Perceeloppervlakte"]::text').extract_first(default='').encode('ascii', 'ignore')))),
				'nr-rooms'     : str(re.sub('[^0-9]','', str(house.css('ul.search-result-kenmerken').css('li::text').extract()[-1]))),
			}

		next_page = response.css('a.pagination-next::attr(href)').extract_first()
		self.log("Next page : {}".format(next_page))

		if next_page is not None:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse)
