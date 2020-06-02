import json
import shutil
import csv
import scrapy
import os
import ast
import six
from scrapy import signals
from pyfiglet import figlet_format
import logging

try:
    from termcolor import colored
except ImportError:
    colored = None

# logs data to the command line
def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(
                string, font=font), color))
    else:
        six.print_(string)


class TrackingSpider(scrapy.Spider):

    name="tracking"
    start_urls = ['https://tools.usps.com/go/TrackConfirmAction',]

    # opens the number list
    info = open("tracking_info.txt", "r")
    contents = info.read()
    info_dict = ast.literal_eval(contents)
    info.close()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TrackingSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # writes the updated dict to the file
        with open('tracking_info.txt', 'w') as file:
            file.write(json.dumps(self.info_dict))

        for k in self.info_dict:
            log(k + '(' + self.info_dict[k]['company'] + ') - ' + self.info_dict[k]['status'], 'cyan')

    def parse(self,response):

        # for each number...
        for num in self.info_dict:
            company = self.info_dict[num]['company']

            if company == 'USPS':
                data = {'tLabels': num}
                res = yield scrapy.FormRequest(url=self.start_urls[0], dont_filter=True, formdata=data, callback=self.parse_result, meta={'num': num},)


    def parse_result(self, response):

        # gets the delivery description
        desc_list = response.css('.status_feed p::text').getall()
        desc = "; ".join(desc_list)

        # writes the delivery status to the dictionary
        self.info_dict[response.meta['num']]['status'] = desc