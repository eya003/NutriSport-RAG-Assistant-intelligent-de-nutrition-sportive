"""Pure presentation styles for the NutriSport user-facing Streamlit UI."""
import base64
from pathlib import Path


def stylesheet(hero_path: Path) -> str:
    photo = base64.b64encode(hero_path.read_bytes()).decode('ascii')
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*='css'], .stApp, input, button { font-family: 'DM Sans', 'Segoe UI', sans-serif; }
.stApp { background: radial-gradient(ellipse at 91% 2%,rgba(38,107,64,.17),transparent 38%), #081713; color:#eef9f3; }
[data-testid='stHeader'] { background:transparent !important; }
[data-testid='stMainBlockContainer'] { max-width:1310px !important; padding:1.6rem 3.1rem 5rem !important; }
[data-testid='stSidebar'] { background:linear-gradient(165deg,#0d231e 0%,#0a1917 70%,#103529 100%); border-right:1px solid rgba(152,213,180,.12); }
[data-testid='stSidebar'] [data-testid='stVerticalBlock'] { gap:.8rem; }
[data-testid='stSidebar'] [data-testid='stSidebarContent'] { padding-top:1.8rem; }
.ns-logo { font-size:1.33rem; font-weight:800; letter-spacing:-.04em; padding:.35rem 0 .8rem; color:#fff; }
.ns-logo span { font-size:1.6rem; vertical-align:middle; margin-right:.42rem; }
.ns-brand-caption { color:#85bba0; font-size:.78rem; letter-spacing:.11em; text-transform:uppercase; margin-top:-.7rem; margin-bottom:1.1rem; }
.ns-side-label { font-size:.7rem;color:#81ac9a;font-weight:800; letter-spacing:.13em; margin:1.2rem 0 .35rem; }
.ns-hero { position:relative; overflow:hidden; isolation:isolate; border:1px solid rgba(115,189,144,.21);
  background:linear-gradient(90deg,#103329 0%,#11352d 35%,rgba(14,40,32,.92) 51%,rgba(5,32,22,.19) 100%),
  url('data:image/webp;base64,""" + photo + """') right center / auto 100% no-repeat,#123d30;
  border-radius:28px; min-height:248px; padding:2.25rem 2.35rem; box-shadow:0 22px 52px rgba(0,0,0,.20);
  animation:ns-rise .65s ease both; }
.ns-hero::before { content:''; z-index:-1; position:absolute; right:15%; top:-72%; width:280px; height:280px; border-radius:100%;
  border:1px solid rgba(134,255,161,.10); box-shadow:0 0 0 38px rgba(134,255,161,.035),0 0 0 75px rgba(134,255,161,.02);
  animation:ns-glow 5s ease-in-out infinite alternate; }
.ns-kicker { display:inline-flex;align-items:center;gap:.55rem; border:1px solid rgba(108,226,151,.30);border-radius:99px;
  background:rgba(20,75,54,.73); color:#b0f5bb; padding:.36rem .8rem; font-size:.7rem;font-weight:800;letter-spacing:.13em;}
.ns-kicker::before { content:''; width:7px;height:7px;background:#83ff99;border-radius:99px; box-shadow:0 0 12px rgba(116,245,138,.75); }
.ns-hero h1 { max-width:650px; color:#fff;font-size:clamp(2.05rem,3.35vw,3.25rem); letter-spacing:-.052em;
  line-height:1.1; margin:.95rem 0 .85rem; font-weight:800; }
.ns-hero p { color:#c5e5d6;font-size:1rem;line-height:1.65;max-width:510px;margin:0; }
.ns-hero-note {color:#a6ffb0; font-size:.82rem; margin-top:1.32rem;letter-spacing:.015em;}
.ns-section-title { font-weight:800;letter-spacing:-.025em;font-size:1.33rem;color:#effdf3;margin:1.7rem 0 .2rem; }
.ns-section-description { color:#91b6a6;font-size:.86rem;margin:.05rem 0 1rem; }
.ns-panel {border:1px solid rgba(128,194,159,.16);border-radius:20px; background:linear-gradient(135deg,rgba(18,52,42,.95),rgba(13,34,29,.95)); padding:1.2rem 1.3rem; box-shadow:0 8px 20px rgba(0,0,0,.10); }
.ns-empty {text-align:center; min-height:260px; display:flex; flex-direction:column; align-items:center;justify-content:center;padding:1.7rem; }
.ns-empty-icon {font-size:2.1rem;background:rgba(68,181,122,.14);border-radius:18px;width:68px;height:68px;display:flex;align-items:center;justify-content:center;margin:0 auto .8rem;}
.ns-empty h3 {font-size:1.17rem;color:#e9faef;margin:.5rem 0 .6rem;}
.ns-empty p {max-width:420px;color:#98b8a7;font-size:.89rem;line-height:1.65;}
.ns-tip {position:relative;overflow:hidden;border:1px solid rgba(107,216,135,.21);min-height:250px;border-radius:22px;
  background:linear-gradient(140deg,rgba(24,80,49,.95),rgba(16,54,39,.96));padding:1.2rem 1.4rem;}
.ns-tip::after {content:'✦';color:rgba(178,252,162,.13);position:absolute;font-size:8.8rem;right:-16px;bottom:-69px;transform:rotate(-12deg);}
.ns-tip-label {font-size:.8rem;font-weight:700;letter-spacing:.025em;color:#a8e9b1;}
.ns-tip h3 {font-size:1.16rem;color:#f0fff3;font-weight:800;margin:.85rem 0 .5rem;line-height:1.35;}
.ns-tip p {color:#cbe5d2;font-size:.9rem;line-height:1.58;max-width:300px;}
.ns-source-small {font-size:.73rem;color:#88d5a4; margin-top:.85rem;}
.ns-source-small a {color:#a9f4b7;text-decoration:underline;text-underline-offset:3px;}
.ns-goal-icon {font-size:1.45rem;padding:0 0 .4rem;}
.ns-goal-name {font-size:1rem;font-weight:800;color:#f5fff9;}
.ns-goal-detail {font-size:.78rem;color:#90bca4;min-height:2.6rem;margin-top:.3rem;line-height:1.45;}
.ns-footer {font-size:.76rem;color:#7fa490;text-align:center;margin:2.7rem auto 0;max-width:800px;line-height:1.6;}
.ns-meta {font-size:.76rem;color:#84a99a;margin:.65rem 0;}
.ns-response-head {font-size:.88rem;font-weight:800;color:#9af0ae;padding:0 0 .35rem;}
.ns-hint {font-size:.75rem;color:#88b49e;margin:.25rem 0 .3rem;}
@keyframes ns-rise {from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes ns-glow {from{transform:scale(.96)}to{transform:scale(1.05)}}
[data-testid='stButton'] button {border-radius:14px !important;background:rgba(25,58,48,.70) !important;border:1px solid rgba(149,208,171,.20) !important;
 color:#ecfff3 !important;font-weight:700;min-height:2.9rem;transition:all .18s ease!important;}
[data-testid='stButton'] button:hover {background:rgba(33,88,66,.85) !important;border-color:#6add8e!important;transform:translateY(-1px);}
[data-testid='stButton'] button[kind='primary'] {background:linear-gradient(108deg,#6cfa83,#90f061)!important;border-color:#75ee8d!important;color:#062112!important; font-weight:800;box-shadow:0 6px 25px rgba(74,237,103,.15);}
[data-testid='stButton'] button[kind='primary']:hover {background:#adff9e!important;}
[data-testid='stChatInput'] {border:1px solid rgba(140,230,176,.34)!important;border-radius:17px!important;background:#102b23!important;box-shadow:0 0 0 5px rgba(97,189,119,.05);}
[data-testid='stChatInput'] textarea {color:#eafff2!important;}
[data-testid='stChatInput'] button {background:#80ee83!important;border-radius:9px!important;}
[data-testid='stChatMessage'] {border-radius:18px!important;border:1px solid rgba(134,208,156,.15);padding:1.05rem!important;background:#112a22!important;margin:.6rem 0;}
[data-testid='stChatMessage'] [data-testid='stMarkdownContainer'] p {line-height:1.66;}
[data-testid='stExpander'] {border:1px solid rgba(149,220,164,.15)!important;border-radius:13px!important;background:rgba(13,41,32,.48)!important;}
[data-testid='stSelectbox'] [data-baseweb='select'] >div {background:#17382d!important;border-color:#34624c!important;color:white!important;border-radius:12px!important;}
[data-testid='stCaptionContainer'] {color:#91b5a3!important;}
[data-testid='stAlert'] {border-radius:13px!important;}
a, a:visited {color:#a4f2b4;}
a:hover {color:#d3ffd9;}
@media (max-width:1000px) { [data-testid='stMainBlockContainer'] {padding:1.2rem 1rem 3rem!important;} .ns-hero {min-height:240px;padding:1.6rem;background-size:auto 100%;} .ns-hero h1 {font-size:2rem;} }
@media (max-width:680px) { .ns-hero {padding:1.35rem;background-image:linear-gradient(90deg,rgba(10,38,28,.96),rgba(10,38,28,.80)),url('data:image/webp;base64,""" + photo + """');} .ns-hero h1 {font-size:1.7rem;} .ns-hero p {font-size:.9rem;} }
</style>"""
