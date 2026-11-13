from .corpus import load_corpus
from .search import HybridRetriever
from .answer import generate

class NutriSport:
    def __init__(self, corpus_path=None, backend='faiss'):
        self.docs=load_corpus(corpus_path) if corpus_path else load_corpus()
        self.retriever=HybridRetriever(self.docs,backend=backend)
    def ask(self,question,topic='all',language='fr',mode='hybrid',top_k=3,provider='auto'):
        retrieved=self.retriever.search(question,mode=mode,top_k=top_k,topic=topic)
        response,status=generate(question,retrieved,language=language,provider=provider)
        return dict(answer=response,status=status,passages=retrieved)
