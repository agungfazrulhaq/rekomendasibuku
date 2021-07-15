import pandas as pd
import numpy as np
import random

def sortedsimilar(bookgenres, genres) :
    bookgin = bookgenres
    ayye = [-1,'a_filter']
    t = 0
    for x in bookgenres.columns :
        if t > 1 :
            if x in genres :
                ayye.append(1)
            else :
                ayye.append(0)
        t += 1

    bookgin["distance"] = np.nan
    for index,row in bookgenres.iterrows() :
        book_ = row.values
        print(book_)
        book_s = ayye
        print(book_)
        print(book_s)
        print(len(book_), len(book_s))
        dissim = 0
        for i in range(2,len(bookgenres.columns)-1) :
            if book_[i] == 1 and book_s[i] == 1 :
                dissim += 1
        bookgin.loc[index,"distance"] = dissim
    
    bookgin = bookgenres.drop([len(bookgenres)-1])
    sortedbgn = bookgin.sort_values(by=["distance"], ascending=False)

    sorted = sortedbgn[["goodreads_book_id","title","distance"]]

    return sorted
