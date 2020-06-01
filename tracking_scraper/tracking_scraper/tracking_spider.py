import json
import shutil
import csv
import scrapy


class TrackingSpider(scrapy.Spider):

    name="tracking"
    start_urls = ('https://www.usps.com/manage/',)

    def parse(self,response):
        # extracts company from request
        company = getattr(self,'company','')

        # extracts tracking number from request
        num = getattr(self, 'num', '')

        # if company is usps...
        if company == 'USPS':

            data = {'track-package--input': num}

            # creates form request
            res = yield scrapy.FormRequest(url=start_urls[0], dont_filter=True, formdata=data, callback=self.parse_result)

    def parse_result(self, response):

        return response.css('.delivery_status::h2::strong::text').get()
        # TODO write the result to text file