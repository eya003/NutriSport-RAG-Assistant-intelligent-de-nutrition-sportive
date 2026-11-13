import pytest
from src.corpus import clean_text, split_words,load_corpus
from src.search import tokenize,rrf
from src.answer import generate,make_messages,needs_caution
from eval.run_p2 import metrics

def test_corpus_unique():
    docs=load_corpus()
    assert len(docs)>=20 and len(set(d['chunk_id'] for d in docs))==len(docs)
    assert all(d['source_url'].startswith('https://') for d in docs)

def test_chunking_overlap():
    text=' '.join(str(i) for i in range(22))
    chunks=split_words(text,10,3)
    assert chunks[0].split()[-3:]==chunks[1].split()[:3]

def test_clean():
    assert clean_text('abc   [12]   def')=='abc def'

def test_arabic():
    assert 'بروتين' in tokenize('ما هي فوائد بروتين العضلات؟')

def test_rrf():
    ids,scores=rrf([[1,2,3],[2,1,3]])
    assert abs(scores[1]-scores[2])<1e-9 and ids[0]==1

def test_metrics():
    r=metrics(['a','b','c'],['b','c'],3)
    assert r['recall']==1 and r['mrr']==0.5

def test_evidence_only():
    docs=load_corpus()
    answer,mode=generate('protein',docs[:1],provider='offline')
    assert '[C001]' in answer and mode=='offline_extracts'

def test_empty_evidence_abstains():
    answer,mode=generate('unknown',[],provider='offline')
    assert mode=='no_evidence'

def test_prompt_sources():
    prompt=make_messages('protein',load_corpus()[:1])[1]['content']
    assert '[C001]' in prompt

def test_caution():
    assert needs_caution('prescribe a diet')


def test_grok_api_request_uses_xai_endpoint(monkeypatch):
    import json
    import urllib.request

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, *args):
            return json.dumps({'choices':[{'message':{'content':'Protein recommendation [C001].'}}]}).encode()

    captured={}
    def fake_urlopen(request, timeout=45):
        captured['url']=request.full_url
        captured['body']=json.loads(request.data.decode('utf8'))
        assert request.get_header('Authorization') == 'Bearer test-key'
        return FakeResponse()

    monkeypatch.setenv('XAI_API_KEY','test-key')
    monkeypatch.setenv('XAI_BASE_URL','https://api.x.ai/v1')
    monkeypatch.setenv('XAI_MODEL','grok-4.3')
    monkeypatch.setattr(urllib.request,'urlopen',fake_urlopen)
    answer,mode=generate('How does protein help?',load_corpus()[:1],provider='auto')
    assert mode=='grok_api'
    assert '[C001]' in answer
    assert captured['url']=='https://api.x.ai/v1/chat/completions'
    assert captured['body']['model']=='grok-4.3'
    assert captured['body']['reasoning_effort']=='none'
    assert captured['body']['messages'][0]['role']=='system'

def test_missing_xai_key_is_explicit(monkeypatch):
    monkeypatch.delenv('XAI_API_KEY', raising=False)
    with pytest.raises(RuntimeError,match='XAI_API_KEY missing'):
        generate('protein',load_corpus()[:1],provider='auto_explicit')
