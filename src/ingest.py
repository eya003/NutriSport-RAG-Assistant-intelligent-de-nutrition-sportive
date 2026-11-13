"""Optional ingestion of complete official pages when Internet is available.
Never executes automatically; the curated, cited summaries ship offline.
"""
import argparse
import json
import re
import requests
from bs4 import BeautifulSoup
from .config import DATA
from .corpus import clean_text, split_words

def extract_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script','style','nav','footer','header','aside','form','svg']):
        tag.decompose()
    article = soup.find('article') or soup.find('main') or soup
    elements = article.find_all(['h1','h2','h3','p','li'])
    lines=[]
    for el in elements:
        if el.find_parent(['li','p']) and el.name not in ('li','p'):
            continue
        t=clean_text(el.get_text(' ',strip=True))
        if len(t) >= 45 and not re.search(r'^(references|bibliography|cookie|subscribe|newsletter)$',t,re.I):
            lines.append((el.name,t))
    # remove duplicate navigational paragraph strings
    seen=set(); filtered=[]
    for tag,t in lines:
        if t not in seen:
            filtered.append((tag,t)); seen.add(t)
    return filtered

def fetch_sources(timeout=20):
    sources=json.loads((DATA/'sources.json').read_text(encoding='utf8'))
    out=[]
    session=requests.Session();session.headers['User-Agent']='NutriSportRAG/1.0 (student research project)'
    for s in sources:
        try:
            res=session.get(s['url'],timeout=timeout);res.raise_for_status()
            lines=extract_html(res.text)
            heading='Document overview';blocks=[]
            for tag,line in lines:
                if tag.startswith('h'):
                    if blocks:
                        blocks.append(('__SECTION_END__',''))
                    heading=line
                else:blocks.append((heading,line))
            sections={}
            for h,t in blocks:
                if h=='__SECTION_END__':continue
                sections.setdefault(h,[]).append(t)
            for n,(section,paras) in enumerate(sections.items()):
                for j,chunk in enumerate(split_words(' '.join(paras))):
                    if len(chunk.split())<35:continue
                    out.append(dict(chunk_id=f"{s['source_id']}_{n:03}_{j:03}",source_id=s['source_id'],source_title=s['title'],source_url=s['url'],section=section,topic=s['topic'],text=chunk,language='en',provenance='downloaded_html'))
            print(f"{s['source_id']}: {len(lines)} blocks")
        except Exception as e:
            print(f"SKIPPED {s['source_id']}: {e}")
    if not out:raise RuntimeError('No source fetched; check Internet. Curated offline corpus still usable.')
    target=DATA/'full_text';target.mkdir(exist_ok=True)
    dst=target/'downloaded_chunks.json'
    dst.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print('Wrote',dst,len(out),'chunks')
    print('NOTICE: review extraction for reference lists/footnotes before selecting this corpus.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--timeout',type=int,default=20)
    args=parser.parse_args();fetch_sources(args.timeout)
