import pandas as pd
import numpy as np
import random

def sortedsimilar(book, bookgenres, books) :
    book = [-1,'a filter']
    zeros = []
    for i in range(len(bookgenres.columns)-2) :
        zeros.append(0)
    
    bookgenres.loc[len(bookgenres)] = book + zeros
    bookgenres["distance"] = np.nan
    for index,row in bookgenres.iterrows() :
        book_ = row.values
        book_s = bookgenres.loc[len(bookgenres)-1].values
        dissim = 0
        for i in range(2,len(bookgenres.column)-1) :
            dissim += abs(book[i]-book_s[i])
        row["distance"] = dissim
    
    bookgenres = bookgenres.drop([len(bookgenres)-1])
    sortedbgn = bookgenres.sort_values(by=["distance"], ascending=True)

    sorted = sortedbgn[["goodreads_book_id","title"]]

    return sorted
