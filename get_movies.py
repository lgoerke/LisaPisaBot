from lxml import etree
import requests
import re
import csv
import sys

movie_titles = []

with open('movies.csv','r') as csvfile:
	reader = csv.reader(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
	for row in reader:
		movie_titles.append(row[0])

with open('movie_db.csv', 'w', newline='') as csvfile:
	writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
	writer.writerow(["question","answer","second_answer"])
	for i,movie_title in enumerate(movie_titles):
		if (i%10==0):
			sys.stdout.write('.')
			sys.stdout.flush()
		splitted = str.split(movie_title)
		movie_plus = '+'.join(splitted)
		page = requests.get("http://www.omdbapi.com/?t="+ movie_plus +"&plot=full&r=xml")
		root = etree.fromstring(page.content)
		doc = etree.tostring(root)

		doc = doc.decode("utf-8") 

		movie_name = re.compile('movie title="(.*)" year')
		match = re.findall(movie_name,doc)
		if match:
			title = match[0].lower()

		movie_plot = re.compile('plot="(.*)" language')
		match = re.findall(movie_plot,doc)
		if match:
			plot_long = match[0]

		page = requests.get("http://www.omdbapi.com/?t="+ movie_plus +"&r=xml")

		root = etree.fromstring(page.content)
		doc = etree.tostring(root)

		doc = doc.decode("utf-8") 
		movie_plot = re.compile('plot="(.*)" language')
		match = re.findall(movie_plot,doc)
		if match:
			plot_short = match[0]

		writer.writerow([title, plot_long, plot_short])