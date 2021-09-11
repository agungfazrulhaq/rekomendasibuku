import pandas as pd
import numpy as np
import random
import time
import recommenderfilter as rf
import method as mt
from flask import Flask, render_template, url_for, request, redirect
import numba
from numba import vectorize, jit, cuda, njit
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning, NumbaWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaWarning)


app = Flask(__name__)

b = pd.read_csv("data/books500.csv")
book_df = b[['book_id','goodreads_book_id','original_title','authors','image_url','original_publication_year']]
bookgenres = pd.read_csv("data/500bookgenres.csv")
dataclusterwid = pd.read_csv('data/500Fuzzy25ClusterMembershipValue.csv')
bookids = pd.read_csv("data/book500ids.csv")
ratings = pd.read_csv("data/rtest.csv")
genre_content = []
ex20 = book_df.head(5)
item_per_page = 25
total_pages = 0
ratings_given = pd.DataFrame(columns=['user_id','book_id','rating'])

randomed_ids = random.randint(0,200000)
while randomed_ids in ratings['user_id'].unique() :
    randomed_ids = random.randint(0,200000)


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
                    ratings_given.loc[len(ratings_given)] = [randomed_ids, arr_txt[1],arr_txt[0]]
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
            similar = rf.sortedsimilar(bookgenres,genre_content)
            ex20 = pd.merge(similar, book_df, how='left', on='goodreads_book_id').head(250)

    
    total_pages = (len(ex20) // item_per_page) + 1
    
    if page > len(ex20) // item_per_page :
        books = ex20.iloc[item_per_page*(page-1):]
    else :
        books = ex20.iloc[item_per_page*(page-1):item_per_page*page]
    
    return render_template("book-list.html", ratings_given = ratings_given , books = books, total_pages = total_pages, page = page, genre_content = genre_content)

@app.route('/search', methods=['POST'])
def search() :
    global ex20
    if request.method == 'POST' :
        keyword_ = request.form.get('search')
        print(keyword_)
        array_of_titles = []
        arr_tit = book_df['original_title'].unique()
        for x in range(len(arr_tit)) :
            if keyword_ in str(arr_tit[x]) :
                array_of_titles.append(str(arr_tit[x]))
        ex20 = book_df[book_df['original_title'].isin(array_of_titles)]
    
    return redirect('/step2')

@app.route('/recommendation')

@numba.jit
def recommendation() :
    # print("----")
    # print("Clustering Data")
    # print('----')
    # print('')
    start = time.time()
    # datacluster = mt.fuzzykmodes(3, bookgenres, threshold=0.4)
    # print(datacluster.head(5))
    k_cluster = 25
    clusters_fuzzy = []
    for i in range(k_cluster) :
        clusters_fuzzy.append([])
        
    threshold=1/k_cluster
    for det in range(len(dataclusterwid)) :
        for dt in range(k_cluster) :
            if dataclusterwid.iloc[det]['membership'+str(dt)] > threshold :
                clusters_fuzzy[dt].append(int(dataclusterwid.iloc[det]['book_id']))
    
    book500feature = pd.merge(bookids,bookgenres, on='goodreads_book_id')
    ratings['book_id'] = ratings['book_id'].astype('int')
    ratings_given['book_id'] = ratings_given['book_id'].astype('int')
    ratings_given['rating'] = ratings_given['rating'].astype('int')
    print(ratings_given)
    concatted = [ratings, ratings_given]
    new_rating = pd.concat(concatted)
    rating_matrix = new_rating.pivot(index = 'user_id', columns ='book_id', values = 'rating')
    rating_matrix0 = rating_matrix.fillna(0)
    new_cluster_ = []
    for cl in clusters_fuzzy :
        cls = np.array(cl)
        clusters__ = []
        for x in cls :
            if x in rating_matrix0.columns :
                clusters__.append(x)
                
        new_cluster_.append(clusters__)
    
    matrix_rating_arr_c = []

    for cluster in new_cluster_ :
        matrix_rating_arr_c.append(rating_matrix0[cluster])
    
    prediction_result_arr = []
    for i in range(len(matrix_rating_arr_c)) :
        prediction_result_arr.append(mt.recommending(randomed_ids,matrix_rating_arr_c[i],matrix_rating_arr_c,book500feature))
        print("---")

    prediction_result = pd.DataFrame(columns = ['book_id','rating_prediction'])
    for index,row in book500feature.iterrows() :
        arr_of_val = []
        for i in range(len(prediction_result_arr)) :
            if row['book_id'] in prediction_result_arr[i]['indexincl'].unique() :
                arr_of_val.append(prediction_result_arr[i].loc[prediction_result_arr[i]['indexincl'] == row['book_id']]['ratingprediksi'].values[0])
        rate = 0
        if len(arr_of_val) != 0 :
            sumall = 0
            for xj in arr_of_val :
                sumall += xj
            rate = sumall/len(arr_of_val)
        else :
            rate = 0
        prediction_result.loc[len(prediction_result)] = [str(int(row['book_id'])),rate]

    prediction_result['book_id'] = prediction_result['book_id'].astype('int')
    ratings_given['book_id'] = ratings_given['book_id'].astype('int')
    book_df['book_id'] = book_df['book_id'].astype('int')

    recom = prediction_result.sort_values('rating_prediction',ascending=False)
    book_recommendation = pd.merge(recom,book_df, how='left', on='book_id')

    for i in range(k_cluster) :
        book_recommendation = book_recommendation[~book_recommendation['book_id'].isin(mt.rated_by_user(randomed_ids, matrix_rating_arr_c[i]))]

    book_recommendation = book_recommendation.head(20)

    maedf = pd.merge(prediction_result, ratings_given, how='right', on='book_id')
    maesum = 0
    for index,row in maedf.iterrows() :
        maesum += abs(row['rating_prediction']-int(row['rating']))

    maescore = maesum/len(maedf)
    end = time.time()
    print('Recommendation Given')
    print('-----')
    print('Running Time : ', abs(start-end))
    print('MAE Score : ', maescore)
    print('-----')
    print('book_recommendation : ', recom.head(20))
    return render_template('Recommendation.html', book_recommendation = book_recommendation, maescore = maescore)

@app.route('/', methods=['POST','GET'])
def index() :
    global genre_content
    global ratings_given

    genre_content = []
    ratings_given = pd.DataFrame(columns=['user_id','book_id','rating'])
    return render_template("index.html")

if __name__ == "__main__" :
    app.run(debug=True, use_reloader=False)