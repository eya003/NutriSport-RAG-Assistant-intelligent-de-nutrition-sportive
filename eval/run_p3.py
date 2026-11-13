"""P3: objective citation validity + abstention; faithfulness manual review required.
Requires P2 dependencies. Without API, tests EXTRACTIVE mode only, not LLM quality.
"""
import argparse
import csv
import json
import re
from src.pipeline import NutriSport
from src.answer import generate
from src.config import ROOT

def citation_validity(answer,passages):
    ids=set(re.findall(r'\[(C\d+|[A-Z_]+_\d+_\d+)\]',answer))
    retrieved={p['chunk_id'] for p in passages}
    return bool(ids) and ids.issubset(retrieved),len(ids)

def evaluate(provider='offline',max_q=20,fixture=False):
    items=json.loads((ROOT/'eval'/'questions.json').read_text(encoding='utf8'))[:max_q]
    engine=None if fixture else NutriSport()
    docs={d['chunk_id']:d for d in __import__('src.corpus',fromlist=['load_corpus']).load_corpus()}
    rows=[]
    for item in items:
        q=item['question']
        # Explicit unanswerable gold questions are NOT passed to LLM with unrelated evidence.
        # This tests abstention gating only; future work: learned abstention threshold.
        passages=([docs[i] for i in item['relevant_ids'][:3]] if fixture else engine.retriever.search(q,topic=item['topic'],top_k=3,mode='hybrid')) if item['answerable'] else []
        answer,status=generate(q,passages,language='fr',provider=provider)
        valid,n=citation_validity(answer,passages)
        abstained=(status=='no_evidence')
        rows.append(dict(query_id=item['id'],answerable=item['answerable'],mode=status,citations_valid=valid if item['answerable'] else None,citation_count=n,abstained=abstained,answer=answer,faithfulness_manual='NOT_RATED',helpfulness_manual='NOT_RATED'))
    out=ROOT/'results';out.mkdir(exist_ok=True)
    filename=('p3_fixture.csv' if fixture else 'p3_offline.csv') if provider=='offline' else 'p3_llm.csv'
    with (out/filename).open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    good=[r for r in rows if r['answerable']]
    bad=[r for r in rows if not r['answerable']]
    report={'mode':provider,'n':len(rows),'n_answerable':len(good),'n_unanswerable':len(bad),'citation_valid_rate':sum(bool(r['citations_valid']) for r in good)/len(good) if good else None,'abstention_rate_gated':sum(r['abstained'] for r in bad)/len(bad) if bad else None,'faithfulness':'NOT_MEASURED — requires manual evidence-by-evidence assessment','warning':'Unanswerables are explicitly gated with gold labels. This is not autonomous detection or a real-world abstention score. Fixture mode uses oracle gold passages, not retrieval.'}
    (out/filename.replace('.csv','.json')).write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--provider',choices=['offline','auto'],default='offline');p.add_argument('--max-q',type=int,default=20);p.add_argument('--fixture',action='store_true')
    a=p.parse_args();evaluate(a.provider,a.max_q,a.fixture)
