"""P2 objective retrieval metrics. Default actual embedding/FAISS; --proxy is OFFLINE TF-IDF, NOT FAISS."""
import argparse
import csv
import json
from pathlib import Path
from src.corpus import load_corpus
from src.search import rrf, tokenize
from src.config import ROOT

def metrics(retrieved, relevant, k):
    # Each test defines a set of relevant IDs; no question is in index.
    predicted=retrieved[:k]
    intersection=set(predicted)&set(relevant)
    return dict(hit=int(bool(intersection)),recall=(len(intersection)/len(relevant) if relevant else None),precision=(len(intersection)/k if relevant else None),mrr=(next((1/(i+1) for i,c in enumerate(predicted) if c in relevant),0) if relevant else None))

def evaluate(proxy=False):
    docs=load_corpus();questions=json.loads((ROOT/'eval'/'questions.json').read_text(encoding='utf8'))
    texts=[d['text'] for d in docs]
    if proxy:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        tfidf=TfidfVectorizer(tokenizer=tokenize,token_pattern=None,lowercase=False,ngram_range=(1,2),sublinear_tf=True)
        vectors=tfidf.fit_transform(texts)
        def ranks(q,ids):
            dense_scores=cosine_similarity(tfidf.transform([q]),vectors)[0]
            dense=sorted(ids,key=lambda i:(-dense_scores[i],i))
            # BM25 from scratch for isolated, reproducible proxy without rank-bm25 dependency.
            import math
            corpus=[tokenize(s) for s in texts]
            avg=sum(map(len,corpus))/len(corpus)
            t=tokenize(q)
            dfs={word:sum(word in set(doc) for doc in corpus) for word in set(t)}
            def score(i):
                return sum(math.log(1+(len(corpus)-dfs[w]+0.5)/(dfs[w]+0.5))*(doc.count(w)*2.2/(doc.count(w)+1.2*(0.25+0.75*len(doc)/avg))) for w in set(t) if (doc:=corpus[i]) and doc.count(w))
            sparse=sorted(ids,key=lambda i:(-score(i),i))
            return dense,sparse
    else:
        from src.search import HybridRetriever
        engine=HybridRetriever(docs)
        def ranks(q,ids):
            d=engine._rank_dense(q,ids)
            lex=engine.bm25.get_scores(tokenize(q))
            s=sorted(ids,key=lambda i:(-float(lex[i]),i))
            return d,s
    rows=[]
    for q in questions:
        ids=[i for i,r in enumerate(docs) if q['topic']=='all' or r['topic'] in (q['topic'],'general')]
        dense,sparse=ranks(q['question'],ids)
        pool=min(20,len(ids))
        hybrid,_=rrf([dense[:pool],sparse[:pool]])
        rel=q['relevant_ids']
        for method,r in [('dense',dense),('bm25',sparse),('hybrid',hybrid)]:
            labels=[docs[i]['chunk_id'] for i in r]
            for k in (3,5):
                values=metrics(labels,rel,k)
                rows.append(dict(query_id=q['id'],method=method,k=k,answerable=q['answerable'],retrieved='|'.join(labels[:k]),**values))
    output=ROOT/'results';output.mkdir(exist_ok=True)
    name='p2_proxy_tfidf' if proxy else 'p2_actual_faiss'
    with (output/(name+'.csv')).open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report=[]
    for method in ('dense','bm25','hybrid'):
        for k in (3,5):
            valid=[r for r in rows if r['method']==method and r['k']==k and r['answerable']]
            report.append({'method':method,'k':k,'n_answerable':len(valid),'hit_at_k':round(sum(r['hit'] for r in valid)/len(valid),4),'recall_at_k':round(sum(r['recall'] for r in valid)/len(valid),4),'mrr_at_k':round(sum(r['mrr'] for r in valid)/len(valid),4)})
    (output/(name+'.json')).write_text(json.dumps({'run_type':'TF-IDF proxy, NO FAISS/embeddings' if proxy else 'REAL multilingual SentenceTransformer + FAISS', 'n_questions':len(questions),'gold_manual':True,'note':'Unanswerable questions excluded from retrieval recall: retrieval ranking cannot decide answerability alone.', 'metrics':report},indent=2),encoding='utf8')
    print(json.dumps(report,indent=2));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--proxy',action='store_true');a=p.parse_args();evaluate(a.proxy)
