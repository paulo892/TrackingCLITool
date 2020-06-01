import json
import shutil
import csv
import scrapy


class TrackingSpider(scrapy.Spider):

    name="tracking"
    start_urls = ('https://www.usps.com/manage/',)
    output = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_callback = kwargs.get('args').get('callback')

    def close(self, spider, reason):
        self.output_callback(output)

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

        status = response.css('.delivery_status::h2::strong::text').get()
        print(status)

        output = status