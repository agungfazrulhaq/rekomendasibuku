import pandas as pd
import numpy as np
import random
import recommenderfilter as rf
from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)

b = pd.read_csv("data/books.csv")
book_df = b[['book_id','goodreads_book_id','original_title','authors','image_url','original_publication_year']]
bookgenres = pd.read_csv("data/500bookgenres.csv")
bookids = pd.read_csv("data/book500ids.csv")
genre_content = []
ex20 = book_df.head(5)
item_per_page = 25
total_pages = 0
ratings_given = pd.DataFrame(columns=['book_id','rating'])

@app.route('/giveratings', methods=['POST'])
def give_rating() :
    global ratings_given
    paged = int(request.form.get('page'))
    values = []
    if request.method == 'POST' :
        for i in range(item_per_page) :
            if request.form.get('rating['+str(i)+']') != None :
                value = request.form.get('rating['+str(i)+']')
                values.append(value)
        # values=request.form.getlist('rating[]')
        # for index,row in books.iterrows() :
        #     if request.form.get('rating-'+str(row['book_id'])) :
                text = request.form.get('rating['+str(i)+']')
                arr_txt = text.split("-")
                if arr_txt[1] not in ratings_given['book_id'].unique() :
                    ratings_given.loc[len(ratings_given)] = [arr_txt[1],arr_txt[0]]
                else :
                    ratings_given.loc[ratings_given['book_id'] == arr_txt[1],'rating'] = arr_txt[0]

    return redirect('/step2?page='+str(paged))
    # return render_template('test_inputrating.html', values=values)

@app.route('/step2', methods=['POST','GET'])
def step2() :
    page = request.args.get('page', 1 , type=int)
    global genre_content
    global ex20
    global total_pages
    global ratings_given
    if request.method == 'POST' :
        if len(genre_content) == 0 :
            genre_content = request.form.getlist('genre')

        ex20 = book_df.head(215)
        total_pages = (len(ex20) // item_per_page) + 1
    
    if page > len(ex20) // item_per_page :
        books = ex20.iloc[item_per_page*(page-1):]
    else :
        books = ex20.iloc[item_per_page*(page-1):item_per_page*page]
    
    return render_template("book-list.html", ratings_given = ratings_given , books = books, total_pages = total_pages, page = page, genre_content = genre_content)

@app.route('/', methods=['POST','GET'])
def index() :
    return render_template("index.html")

if __name__ == "__main__" :
    app.run(debug=True)