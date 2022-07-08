from flask import Blueprint, jsonify

from .extensions import mongo

import json

from bson.json_util import dumps

from datetime import datetime

from collections import defaultdict

main = Blueprint('main', __name__)


# books collection
books = mongo['library']['books']
transactions = mongo['library']['transactions']

@main.route('/')
def index():
	return jsonify(message="This is library API")


@main.route('/search/<name>')
def booklist(name):

	ans = []
	name = name.lower()

	for book in books.find():

		if name in book['name'].lower():
			ans.append(book)

	return jsonify(json.loads(dumps(ans)))


@main.route('/search/range/<price_range>')
def books_in_price_range(price_range):
	ans = []
	price_range = list(map(int, price_range.split('-')))

	for book in books.find():
		if book['rent per day'] >= price_range[0] and int(book['rent per day']) <= price_range[1]:
			ans.append(book)

	return jsonify(json.loads(dumps(ans)))



@main.route('/search/<category>/<name>')
def books_in_category(category,name):
	ans = []

	category = category.lower()
	name = name.lower()

	for book in books.find():
		if book['category'].lower()==category:
			if name in book['name'].lower():
				ans.append(book)

	return jsonify(json.loads(dumps(ans)))


@main.route('/book-issue/<book>+<person>+<issue_date>')
def issue_book(book, person, issue_date):

	book,person=book.lower(),person.lower()

	result=transactions.insert_one({
		'book': book, 
		'person': person,
		'issue_date':datetime.strptime(issue_date, '%Y-%m-%d'),
		'return_date': '',
		'rent_generated': 0
	})

	return jsonify(json.loads(dumps(result.inserted_id)))



@main.route('/book-return/<book>+<person>+<return_date>')
def return_book(book, person, return_date):

	book,person=book.lower(),person.lower()

	return_date = datetime.strptime(return_date, '%Y-%m-%d')

	delta = None
	for transaction in transactions.find():

		if transaction['book'].lower()==book:

			if transaction['person'].lower()==person:

				delta = return_date - transaction['issue_date']

	
	rate = 0
	for item in books.find():

		if book in item['name'].lower():
			rate = item['rent per day']



	rent_generated = delta.days*rate


	query = {'book':book, 'person':person}
	update_value={'$set':{'return_date':return_date, 'rent_generated': rent_generated}}

	transactions.update_one(query, update_value)


	return jsonify(rent_generated=rent_generated)



@main.route('/list/people/<book>')
def list_people(book):

	book=book.lower()

	people_book_issued_to = []

	people_currently_have_book = []

	for transaction in transactions.find():
		if transaction['book'] == book:
			people_book_issued_to.append(transaction['person'])

			if transaction['return_date']=='':
				people_currently_have_book.append(transaction['person'])

	return jsonify({
		'people_book_issued_to': people_book_issued_to,
		'people_currently_have_book': people_currently_have_book
	})


@main.route('/list/books/<person>')
def list_books(person):

	person = person.lower()

	books_issued = []

	for transaction in transactions.find():
		if transaction['person'] == person:
			books_issued.append(transaction['book'])
	

	return jsonify({'books_issued': books_issued})




@main.route('/total-rent-generated/<book>')
def total_rent_generated(book):

	book = book.lower()

	total_rent = 0

	for transaction in transactions.find():
		if transaction['book'] == book:
			total_rent += transaction['rent_generated']
	

	return jsonify({'total_rent_generated': total_rent})



@main.route('/list/books-issued/date-range/<begin_date>/<end_date>')
def books_issued_in_date_range(begin_date, end_date):

	begin_date,end_date=(datetime.strptime(begin_date, '%Y-%m-%d'),
							datetime.strptime(end_date, '%Y-%m-%d'))

	books = []

	for transaction in transactions.find():
		if transaction['issue_date'] >= begin_date and transaction['issue_date'] <= end_date:
			books.append({'person':transaction['person'],'book':transaction['book']})



	return jsonify(books=books)