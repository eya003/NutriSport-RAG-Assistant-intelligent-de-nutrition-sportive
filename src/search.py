"""P2: multilingual dense embeddings + FAISS, lexical BM25, RRF fusion.
All returned scores are ranks / RRF values, NOT probabilities.
"""
import re
import unicodedata
import numpy as np
from .config import EMBEDDING_MODEL, RRF_CONSTANT

def tokenize(text):
    # Keeps Arabic Unicode characters; no stemming, so Arabic lexical matching is limited.
    text=unicodedata.normalize('NFKC',text).casefold()
    return re.findall(r'[^\W_]+', text, flags=re.UNICODE)

def rrf(rankings, constant=RRF_CONSTANT):
    out={}
    for ranking in rankings:
        for rank,idx in enumerate(ranking,1):
            out[idx]=out.get(idx,0.0)+1.0/(constant+rank)
    return sorted(out,key=lambda i:(-out[i],i)),out

class HybridRetriever:
    def __init__(self, corpus, model_name=EMBEDDING_MODEL, backend='faiss'):
        self.corpus=corpus
        self.model_name=model_name
        self.backend=backend
        self.texts=[r['text'] for r in corpus]
        self.lex_tokens=[tokenize(x) for x in self.texts]
        try:
            from rank_bm25 import BM25Okapi
        except ImportError as e:
            raise RuntimeError('Install dependencies: pip install -r requirements.txt') from e
        self.bm25=BM25Okapi(self.lex_tokens)
        from sentence_transformers import SentenceTransformer
        self.encoder=SentenceTransformer(model_name)
        vectors=np.asarray(self.encoder.encode(self.texts,normalize_embeddings=True,show_progress_bar=False),dtype='float32')
        self.index=None
        if backend=='faiss':
            import faiss
            self.index=faiss.IndexFlatIP(vectors.shape[1]);self.index.add(vectors)
        elif backend=='numpy':
            self.vectors=vectors
        else:raise ValueError('backend must be faiss or numpy')

    def _rank_dense(self,query,ids):
        q=np.asarray(self.encoder.encode([query],normalize_embeddings=True),dtype='float32')
        if self.index is not None and len(ids)==len(self.corpus):
            scores,indices=self.index.search(q,len(self.corpus))
            return [int(i) for i in indices[0] if i>=0]
        vals=(self.vectors if self.index is None else self.index.reconstruct_n(0,len(self.corpus)))@q[0]
        return sorted(ids,key=lambda i:(-float(vals[i]),i))

    def search(self,query,mode='hybrid',top_k=3,topic='all',pool=20):
        ids=[i for i,r in enumerate(self.corpus) if topic=='all' or r['topic'] in (topic,'general')]
        if not ids:return []
        dense=self._rank_dense(query,ids)
        lexical_scores=self.bm25.get_scores(tokenize(query))
        sparse=sorted(ids,key=lambda i:(-float(lexical_scores[i]),i))
        # Do not fuse full rankings: use fixed retrieval candidate pools.
        candidate_n=min(pool,len(ids))
        dense_pool=dense[:candidate_n]
        sparse_pool=sparse[:candidate_n]
        if mode=='dense': ranked=dense_pool; score={i:1/(1+j) for j,i in enumerate(ranked)}
        elif mode=='bm25':ranked=sparse_pool;score={i:1/(1+j) for j,i in enumerate(ranked)}
        elif mode=='hybrid':ranked,score=rrf([dense_pool,sparse_pool])
        else:raise ValueError('mode must be dense, bm25 or hybrid')
        return [dict(self.corpus[i],score=round(float(score[i]),6),rank=j+1) for j,i in enumerate(ranked[:top_k])]
