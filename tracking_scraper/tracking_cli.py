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

# misc imports for styling
try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None


UPDATES_TRIGGERED_THIS_SESSION = 0


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

# asks user for tracking number for deletion
def askNumberDeletion():
	questions = [
		{
			'type': 'input',
			'name': 'tracking_number',
			'message': 'Please enter tracking number to be deleted.'
		}
	]

	answers = prompt(questions, style=style)
	return answers

# TODO
# determines company of tracking number
def companyToNumber(num):
	# presently just assumes USPS lmao
	return 'USPS'

# TODO
# updates statuses of tracked numbers
def updateStatuses():
	global UPDATES_TRIGGERED_THIS_SESSION

	# TODO - fix this bug
	# limits number of updates per session to one
	if UPDATES_TRIGGERED_THIS_SESSION >= 1:
		log('Please log out of the service to update again.', 'cyan')
		return

	# initializes crawling process
	process = CrawlerProcess({
                'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'LOG_LEVEL': 'WARNING',
            })
	process.crawl(TrackingSpider)
	process.start()
	process.stop()

	UPDATES_TRIGGERED_THIS_SESSION += 1
	

@click.command()
def main():

	log("Tracking CLI", color="cyan", figlet=True)
	log("Welcome to the Tracking CLI!", "cyan")
	log("Press Ctrl^C to exit.", "cyan")
	# TODO - extend to other services
	log("Presently limited to USPS tracking numbers.", "cyan")

	while (True):
		# take in request
		request = askRequest()

		# if request empty, returns with error
		if len(request) == 0:
			log("Goodbye :)", "cyan")
			exit(0)

		# if request is "see_all_entries"...
		if request['request_type'] == "see_all_entries":

			# loads the tracking file
			info = open("tracking_info.txt", "r")
			contents = info.read()
			info_dict = ast.literal_eval(contents)
			info.close()

			# prints all of the entries
			for k in info_dict:
				log(k + '(' + info_dict[k]['company'] + ') - ' + info_dict[k]['status'], 'cyan')

		# if request is "add_entry"...
		if request['request_type'] == 'add_entry':

			# loads the tracking file
			info = open("tracking_info.txt", "r")
			contents = info.read()
			info_dict = ast.literal_eval(contents)
			info.close()

			# asks user for tracking number
			number = askNumber()
			number = number['tracking_number']

			# if number in dict, informs user and continues
			if number in info_dict:
				log('Number already being tracked!', 'cyan')
				continue

			# determines which company number belongs to
			comp = companyToNumber(number)

			# updates the entry in the text file
			info_dict[number] = {'company': comp, 'status': 'Not yet requested'}

			# writes the updated dict to the file
			with open('tracking_info.txt', 'w') as file:
				file.write(json.dumps(info_dict))

			# logs the updated file
			for k in info_dict:
				log(k + '(' + info_dict[k]['company'] + ') - ' + info_dict[k]['status'], 'cyan')

		# if request is "delete_entry"
		if request['request_type'] == 'delete_entry':

			# loads the tracking file
			info = open("tracking_info.txt", "r")
			contents = info.read()
			info_dict = ast.literal_eval(contents)
			info.close()

			# asks user for tracking number
			number = askNumberDeletion()
			number = number['tracking_number']

			# if number not in dict, informs user and continues
			if number not in info_dict:
				log('Number not being tracked!', 'cyan')
				continue

			# deletes the key-value pair
			del info_dict[number]
			log(number + " successfully deleted!", 'cyan')

		# if request is "update_entries"
		if request['request_type'] == 'update_entries':

			updateStatuses()


if __name__ == '__main__':
	main()
