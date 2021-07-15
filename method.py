import pandas as pd
import numpy as np
import random
import math

def random_sum_to(n, num_terms = None):
    num_terms = (num_terms or random.randint(2, n)) - 1
    a = random.sample(range(1, n), num_terms) + [0, n]
    list.sort(a)
    return [a[i+1] - a[i] for i in range(len(a) - 1)]

def funcobj(w,z,alph,bookgenres) :
    fwz = 0
    for it in range(len(bookgenres)) :
        for ctr in range(len(z)) :
            centerarr = z[ctr]
            rowarr = bookgenres.iloc[it].values
            diss = 0
            for b in range(2,len(centerarr)) :
                if rowarr[b] == centerarr[b] :
                    diss += 0
                else :
                    diss += 1
            
            fwz = fwz + ((w[it][ctr]**alph)*diss)
    
    return fwz

def membershipdataframe(k,w,bookgenres) :
    
    newdf = bookgenres[['goodreads_book_id']]
    for x in range(k) :
        column = 'membership'+str(x)
        mem = []
        for j in range(len(w)) :
            mem.append(w[j][x])
            
        newdf[column] = mem
    
    return newdf

def newCentroid(k,mem,bookgenres,threshold) :
    clusters = []
    for j in range(k) :
        clusters.append([])
    
    threshold=threshold
    for det in range(len(mem)) :
        for dt in range(k) :
            if mem.iloc[det]['membership'+str(dt)] >= threshold :
                clusters[dt].append(det)
                
    new_centroid = []
    for jp in range(k) :
        centroid = [jp, "a centroid"]
        for p in range(2, len(bookgenres.iloc[0].values)) :
            num_0 = 0
            num_1 = 0
            for m in range(len(clusters[jp])) :
                if (bookgenres.iloc[clusters[jp][m]].values[p] == 0) :
                    num_0 += 1
                else :
                    num_1 += 1
            if num_0 >= num_1 :
                centroid.append(0)
            else :
                centroid.append(1)
        new_centroid.append(centroid)
        
    return new_centroid

def newMembershipVal(k,centroids,bookgenres,alph) :
    theWn = []
    for index,row in bookgenres.iterrows() :
        wli = []
        for i in range(k) :
            centerarr = centroids[i]
            rowarr = row.values
            diss = 0
            for b in range(2,len(centerarr)) :
                if rowarr[b] == centerarr[b] :
                    diss += 0
                else :
                    diss += 1
            if diss == 0 :
                wli.append(1)
                for lp in range(0,len(wli)-1) :
                    wli[lp] = 0
                for lop in range(len(wli),k) :
                    wli.append(0)
                break
            else :
                sumwli = 0
                for kl in range(k) :
                    centerarr = centroids[kl]
                    diss1 = 0
                    for b in range(2,len(centerarr)) :
                        if rowarr[b] == centerarr[b] :
                            diss1 += 0
                        else :
                            diss1 += 1
                        
                    if(diss1 == 0) :
                        sumwli += 0
                    else :
                        sumwli += ((diss/diss1)**(1/(alph-1)))
                wli.append(1/sumwli)
        theWn.append(wli)
    return theWn

def fuzzykmodes(k, bookgenres, alph=1.2, threshold=0.2) :
    center = []
    for i in range(k) :
        randomed = random.randint(0,len(bookgenres))
        while randomed in center :
            randomed = random.randint(0,len(bookgenres))
        center.append(randomed)
        
    z0 = []
    for x in center :
        z0.append(bookgenres.iloc[x])
        
    w0 = []
    
    for index,row in bookgenres.iterrows() :
        wli = random_sum_to(100,k)
        for er in range(len(wli)) :
            wli[er] = wli[er]/100
        w0.append(wli)
    
    alph = alph
    
    fwz = funcobj(w0,z0,alph,bookgenres)
    
    memberdf = membershipdataframe(k,w0,bookgenres)
    
    maxiter = 10
    for t in range(maxiter) :
        z1 = newCentroid(k,memberdf,bookgenres,threshold)
        
        fwz1 = funcobj(w0,z1,alph,bookgenres)
        
        if fwz == fwz1 :
            break
        else :
            w1 = newMembershipVal(k,z1,bookgenres,alph)
            
            fw1z1 = funcobj(w1,z1,alph,bookgenres)
            
            if fwz1 == fw1z1 :
                break
            else :
                w0 = w1
                memberdf = membershipdataframe(k,w0,bookgenres)
                
                z0 = z1
                fwz = funcobj(w0,z0,alph,bookgenres)
    return memberdf
    
def pearsonSim(i,j,bookset) :
    ri_sum = []
    rj_sum = []
    ubr = []
    
    index_in = 0
    for index,row in bookset.iterrows() :
        if row[i] != 0 :
            ri_sum.append(row[i])
        if row[j] != 0 :
            rj_sum.append(row[j])
        if row[i] != 0 and row[j] != 0 :
            ubr.append(index_in)
        index_in += 1
    
    ri_mean = np.mean(np.array(ri_sum))
    rj_mean = np.mean(np.array(rj_sum))
    
    sim = 0
    simri_sqr = 0
    simrj_sqr = 0
    for x in ubr :
        ri = bookset.iloc[x][i] - ri_mean
        rj = bookset.iloc[x][j] - rj_mean
        
        simri_sqr += ri**2
        simrj_sqr += rj**2
        sim += ri * rj
    
    if (math.sqrt(simri_sqr))*(math.sqrt(simrj_sqr)) == 0 :
       return 0
       
    pearson_sim = (sim)/((math.sqrt(simri_sqr))*(math.sqrt(simrj_sqr)))
    
    return pearson_sim

def featsim(i,j,arrgenres) :
    sumfeat = 0
    for x in range(3,len(arrgenres.loc[arrgenres.book_id == i].values[0])) :
        xi = arrgenres.loc[arrgenres.book_id == i].values[0][x]
        xj = arrgenres.loc[arrgenres.book_id == j].values[0][x]
        sumfeat+= abs(xi-xj)
    
    return 1-(sumfeat/(len(arrgenres.loc[arrgenres.book_id == i].values[0])-3))

def mixedsim(i,j,arrgenres,bookset, c=0.4) :
    return (c*pearsonSim(i,j,bookset)) + ((1-c)*featsim(i,j,arrgenres))

def rated_by_user(user_id,bookset) :
    book_ids = []
    for j in bookset.columns :
        if bookset.loc[bookset.index == user_id][j].values[0] != 0.0 :
            book_ids.append(j)

    return book_ids

def recommending(user_id,cluster,clusters,book_feat) :
    rated_by_u = rated_by_user(user_id,cluster)
    indexbuku = []
    predictionrating = []
    
    for it in cluster.columns :
        sumup = 0
        sumdown = 0
        for rated in rated_by_u :
            similar = mixedsim(rated,it,book_feat,cluster,c=0.8)
            sumup += cluster.loc[cluster.index == user_id][rated].values[0] * similar
            sumdown += abs(similar)
        if(sumdown != 0) :
            prediction = sumup/sumdown
        else :
            prediction = 0
                
        predictionrating.append(prediction)
        indexbuku.append(it)
    
    predictionresult = pd.DataFrame({'indexincl' : indexbuku, 'ratingprediksi' : predictionrating})
    
    return predictionresult

