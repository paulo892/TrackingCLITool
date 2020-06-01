import os
import re
import ast
import click
import signal
import sendgrid
import six
import json
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from tracking_scraper.spiders.tracking_spider import TrackingSpider
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict)
from pyfiglet import figlet_format

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None


# styles for CLI
style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})

class CustomCrawler:
	def __init__(self):
		self.output = None
		self.process = CrawlerProcess(settings={'LOG_ENABLED': False})

	def yield_output(self, data):
		self.output = data

	def crawl(self, cls):
		self.process.crawl(cls, args={'callback': self.yield_output})
		self.process.start()

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

# asks user for request type
def askRequest():
	questions = [
		{
			'type': 'input',
			'name': 'request_type',
			'message': 'What would you like to do? (\'add_entry\' - add new tracking entry, \'see_all_entries\' - see all tracking entries, \'update_entries\' - update tracking entries, \'delete_entry\' - delete tracking entry)',
		}
	]

	answers = prompt(questions, style=style)
	return answers

# asks user for tracking number
def askNumber():
	questions = [
		{
			'type': 'input',
			'name': 'tracking_number',
			'message': 'Please enter your tracking number.'
		}
	]

	answers = prompt(questions, style=style)
	return answers

# TODO
# determines company of tracking number
def companyToNumber(num):
	# presently just assumes USPS lmao
	return 'USPS'


# gets status of delivery by number
def getStatus(num, comp):

	# initializes crawling process
	crawler = CustomCrawler()
	crawler.crawl(TrackingSpider, args={'company': comp, 'num': num})

	# TODO read result from the text file, maybe
	

@click.command()
def main():
	# loads the JSON file with tracking information
	info = open("tracking_info.txt", "r")
	contents = info.read()
	info_dict = ast.literal_eval(contents)
	info.close()

	log("Tracking CLI", color="cyan", figlet=True)
	log("Welcome to the Tracking CLI", "cyan")
	log("Press Ctrl^C to exit.", "cyan")

	while (True):
		# take in request
		request = askRequest()

		# if request empty, returns with error
		if len(request) == 0:
			log("Goodbye :)", "green")
			exit(0)

		# if request is "see_all_entries"...
		if request['request_type'] == "see_all_entries":
			# prints all of the entries
			for k in info_dict:
				print(k + '(' + info_dict[k]['company'] + ') - ' + info_dict[k]['status'])

		# if request is "add_entry"...
		if request['request_type'] == 'add_entry':

			# asks user for tracking number
			number = askNumber()
			number = number['tracking_number']

			# if number in dict, informs user and continues
			if number in info_dict:
				log()

			# determines which company number belongs to
			comp = companyToNumber(number)

			# updates the entry in the text file
			print(number)
			info_dict[number] = {'company': comp, 'status': 'Not yet requested'}

			# writes the updated dict to the file
			with open('tracking_info.txt', 'w') as file:
				file.write(json.dumps(info_dict))

			# gets the status of the delivery
			#status = getStatus(number, comp)







if __name__ == '__main__':
	main()
