import pandas as pd
import numpy as np
import random
import recommenderfilter as rf
from flask import Flask, render_template, url_for, request

app = Flask(__name__)

b = pd.read_csv("data/books.csv")
book_df = b[['book_id','goodreads_book_id','original_title','authors','image_url','original_publication_year']]
bookgenres = pd.read_csv("data/500bookgenres.csv")
bookids = pd.read_csv("data/book500ids.csv")
genre_content = []
ex20 = book_df.head(5)
item_per_page = 25
total_pages = 0
books = book_df.head(5)

@app.route('/step2', methods=['POST','GET'])
def step2() :
    page = request.args.get('page', 1 , type=int)
    global genre_content
    global ex20
    global total_pages
    global books
    if request.method == 'POST' :
        if len(genre_content) == 0 :
            genre_content = request.form.getlist('genre')
        ex20 = book_df.head(215)
        total_pages = (len(ex20) // item_per_page) + 1
    
    if page > len(ex20) // item_per_page :
        books = ex20.iloc[item_per_page*(page-1):]
    else :
        books = ex20.iloc[item_per_page*(page-1):item_per_page*page]
    
    return render_template("book-list.html", books = books, total_pages = total_pages, page = page, genre_content = genre_content)

@app.route('/', methods=['POST','GET'])
def index() :
    return render_template("index.html")

if __name__ == "__main__" :
    app.run(debug=True)