import os
os.environ["PROJ_DATA"] = "/opt/miniconda3/envs/llms-course/share/proj"
os.environ["PROJ_LIB"] = "/opt/miniconda3/envs/llms-course/share/proj"

"""
ATLAS — Geography Quiz
Run: streamlit run geo_quiz.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import random
import io
import time
import json
import urllib.request
from shapely.geometry import shape, MultiPolygon
from shapely.affinity import rotate as shapely_rotate

st.set_page_config(page_title="ATLAS", page_icon="🌍", layout="centered",
                   initial_sidebar_state="collapsed")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Space+Grotesk:wght@400;600;700&display=swap');
.stApp { background: radial-gradient(ellipse at top, #14142b 0%, #0a0a0f 60%) fixed; }
html,body,[class*="css"],p,div { font-family:'Space Grotesk',sans-serif !important; color:#e8e8f0; }
.hero { font-family:'Syne',sans-serif; font-weight:800; font-size:4.5rem;
  background:linear-gradient(135deg,#4fc3f7,#7c4dff,#ff4081); background-size:250% 250%;
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  animation:gs 9s ease infinite; text-align:center; line-height:1; letter-spacing:-0.04em; }
@keyframes gs{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.sub { color:#6b7280; font-size:.9rem; font-weight:600; letter-spacing:.4em; text-transform:uppercase; text-align:center; margin-top:.4rem; }
.stButton>button { background:linear-gradient(135deg,#1a1a2e,#16213e); color:#e8e8f0;
  border:1.5px solid rgba(79,195,247,.25); border-radius:14px; padding:.8rem 1rem;
  font-weight:600; font-size:.95rem; transition:all .2s; width:100%; }
.stButton>button:hover { border-color:#4fc3f7; transform:translateY(-2px); box-shadow:0 8px 20px rgba(79,195,247,.2); }
div[data-testid="stButton"] button[kind="primary"] { background:linear-gradient(135deg,#4fc3f7,#7c4dff); border:none; color:#fff; font-weight:700; }
.pill { background:rgba(79,195,247,.06); border:1px solid rgba(79,195,247,.18); border-radius:16px; padding:.65rem .5rem; text-align:center; }
.pill-l { font-size:.6rem; color:#6b7280; text-transform:uppercase; letter-spacing:.15em; font-weight:700; }
.pill-v { font-size:1.35rem; font-weight:700; font-family:'Syne',sans-serif; }
.xp-track { background:rgba(255,255,255,.06); border-radius:12px; height:9px; overflow:hidden; }
.xp-fill { height:100%; background:linear-gradient(90deg,#4fc3f7,#7c4dff); border-radius:12px; box-shadow:0 0 12px rgba(79,195,247,.5); }
.badge { display:inline-block; background:linear-gradient(135deg,#4fc3f7,#7c4dff); padding:.35rem .9rem; border-radius:100px; color:#fff; font-weight:700; font-size:.75rem; letter-spacing:.08em; text-transform:uppercase; }
.q { font-family:'Syne',sans-serif; font-size:1.55rem; font-weight:700; text-align:center; margin:.5rem 0 1rem 0; color:#f4f4fa; }
.ok { background:linear-gradient(135deg,rgba(74,222,128,.15),rgba(34,197,94,.05)); border:1px solid rgba(74,222,128,.4); color:#86efac; padding:.8rem 1rem; border-radius:14px; text-align:center; font-weight:600; }
.no { background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(220,38,38,.05)); border:1px solid rgba(239,68,68,.4); color:#fca5a5; padding:.8rem 1rem; border-radius:14px; text-align:center; font-weight:600; }
.fact { background:linear-gradient(135deg,rgba(124,77,255,.1),rgba(79,195,247,.05)); border-left:3px solid #7c4dff; padding:.9rem 1.1rem; border-radius:0 14px 14px 0; margin:.8rem 0; color:#d4d4e0; }
.fact .fl { font-size:.65rem; color:#7c4dff; font-weight:700; letter-spacing:.15em; text-transform:uppercase; margin-bottom:.3rem; }
.xpf { display:inline-block; background:linear-gradient(135deg,#fbbf24,#f59e0b); padding:.2rem .65rem; border-radius:100px; color:#1a1a2e; font-weight:800; font-size:.9rem; }
.rstat { background:linear-gradient(135deg,rgba(79,195,247,.08),rgba(124,77,255,.05)); border:1px solid rgba(79,195,247,.2); border-radius:18px; padding:1.3rem; text-align:center; }
.rstat .rn { font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800; background:linear-gradient(135deg,#4fc3f7,#7c4dff); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; line-height:1; }
.rstat .rl { font-size:.7rem; color:#9ca3af; text-transform:uppercase; letter-spacing:.15em; font-weight:700; margin-top:.3rem; }
.timer-track { width:100%; height:5px; background:rgba(255,255,255,.06); border-radius:3px; overflow:hidden; margin:.6rem 0 1rem 0; }
.timer-bar { height:100%; animation:cd 15s linear forwards; background:linear-gradient(90deg,#4ade80 0%,#fbbf24 60%,#ef4444 100%); }
@keyframes cd{0%{width:100%}100%{width:0%}}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"]{background:#0e0e16;}
</style>
""", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────────────────────────
CAPITALS = {
    "Afghanistan":"Kabul","Albania":"Tirana","Algeria":"Alger","Angola":"Luanda",
    "Argentina":"Buenos Aires","Armenia":"Yerevan","Australia":"Canberra","Austria":"Wien",
    "Azerbaijan":"Baku","Bangladesh":"Dhaka","Belarus":"Minsk","Belgium":"Bruxelles",
    "Bolivia":"Sucre","Brazil":"Brasília","Bulgaria":"Sofia","Cambodia":"Phnom Penh",
    "Cameroon":"Yaoundé","Canada":"Ottawa","Chad":"N'Djamena","Chile":"Santiago",
    "China":"Beijing","Colombia":"Bogotá","Croatia":"Zagreb","Cuba":"Havana",
    "Cyprus":"Nicosia","Czechia":"Prag","Denmark":"København","Ecuador":"Quito",
    "Egypt":"Kairo","Estonia":"Tallinn","Ethiopia":"Addis Abeba","Finland":"Helsinki",
    "France":"Paris","Georgia":"Tbilisi","Germany":"Berlin","Ghana":"Accra",
    "Greece":"Athen","Hungary":"Budapest","Iceland":"Reykjavík","India":"New Delhi",
    "Indonesia":"Jakarta","Iran":"Teheran","Iraq":"Bagdad","Ireland":"Dublin",
    "Israel":"Jerusalem","Italy":"Rom","Japan":"Tokyo","Jordan":"Amman",
    "Kazakhstan":"Astana","Kenya":"Nairobi","Latvia":"Riga","Lebanon":"Beirut",
    "Libya":"Tripoli","Lithuania":"Vilnius","Madagascar":"Antananarivo",
    "Malaysia":"Kuala Lumpur","Mali":"Bamako","Mexico":"Mexico City",
    "Mongolia":"Ulaanbaatar","Morocco":"Rabat","Mozambique":"Maputo",
    "Myanmar":"Naypyidaw","Netherlands":"Amsterdam","New Zealand":"Wellington",
    "Nicaragua":"Managua","Niger":"Niamey","Nigeria":"Abuja","North Korea":"Pyongyang",
    "Norway":"Oslo","Oman":"Muscat","Pakistan":"Islamabad","Panama":"Panama City",
    "Paraguay":"Asunción","Peru":"Lima","Philippines":"Manila","Poland":"Warszawa",
    "Portugal":"Lissabon","Qatar":"Doha","Romania":"Bukarest","Russia":"Moskva",
    "Saudi Arabia":"Riyadh","Senegal":"Dakar","Serbia":"Beograd",
    "Slovakia":"Bratislava","Slovenia":"Ljubljana","Somalia":"Mogadishu",
    "South Africa":"Pretoria","South Korea":"Seoul","Spain":"Madrid",
    "Sri Lanka":"Colombo","Sudan":"Khartoum","Sweden":"Stockholm",
    "Switzerland":"Bern","Syria":"Damaskus","Tanzania":"Dodoma","Thailand":"Bangkok",
    "Tunisia":"Tunis","Turkey":"Ankara","Uganda":"Kampala","Ukraine":"Kyiv",
    "United Kingdom":"London","United States of America":"Washington D.C.",
    "Uruguay":"Montevideo","Uzbekistan":"Tashkent","Venezuela":"Caracas",
    "Vietnam":"Hanoi","Yemen":"Sanaa","Zambia":"Lusaka","Zimbabwe":"Harare",
}

FACTS = {
    "Denmark":"København er Nordens ældste hovedstad — grundlagt før år 1000.",
    "France":"Frankrig modtager flere turister end nogen anden nation i verden.",
    "Japan":"Japan består af over 14.000 øer.",
    "Russia":"Rusland strækker sig over 11 tidszoner.",
    "China":"Den Kinesiske Mur er over 21.000 km lang.",
    "Brazil":"Brasilien rummer ca. 60% af Amazonas regnskov.",
    "Australia":"Australien er det eneste land der er et helt kontinent.",
    "Egypt":"Pyramiderne i Giza er over 4.500 år gamle.",
    "Italy":"Italien har flere UNESCO verdensarvssteder end noget andet land.",
    "United States of America":"USA har 50 stater og 5 beboede territorier.",
    "United Kingdom":"Storbritannien har et konstitutionelt monarki med over 1.000 års historie.",
    "Germany":"Tyskland har over 1.500 forskellige slags pølser.",
    "India":"Indien har 22 officielle sprog.",
    "Canada":"Canada har den længste kystlinje i verden.",
    "Norway":"Norge har over 1.000 fjorde.",
    "Sweden":"Sverige har omkring 100.000 søer.",
    "Iceland":"Island har ingen myg.",
    "Finland":"Finland har 188.000 søer.",
    "Mexico":"Mexico City er bygget oven på aztekerhovedstaden Tenochtitlan.",
    "Greece":"Grækenland har over 6.000 øer, kun ca. 200 er beboede.",
    "Spain":"Spanien er verdens største producent af olivenolie.",
    "Netherlands":"Ca. 26% af Holland ligger under havets overflade.",
    "Switzerland":"Schweiz har fire officielle sprog.",
    "South Africa":"Sydafrika har tre hovedstæder.",
    "Argentina":"Argentina var hjemsted for verdens største dinosaurer.",
    "Indonesia":"Indonesien består af over 17.000 øer.",
    "Turkey":"Istanbul er den eneste by der ligger på to kontinenter.",
    "New Zealand":"New Zealand har flere får end mennesker — ca. 5 til 1.",
    "Mongolia":"Mongoliet er verdens mindst tæt befolkede land.",
    "Portugal":"Portugals grænser har været uændrede siden 1297.",
}

CONT_MAP = {
    "Afghanistan":"Asia","Albania":"Europe","Algeria":"Africa","Angola":"Africa",
    "Argentina":"South America","Armenia":"Asia","Australia":"Oceania","Austria":"Europe",
    "Azerbaijan":"Asia","Bangladesh":"Asia","Belarus":"Europe","Belgium":"Europe",
    "Bolivia":"South America","Brazil":"South America","Bulgaria":"Europe",
    "Cambodia":"Asia","Cameroon":"Africa","Canada":"North America","Chad":"Africa",
    "Chile":"South America","China":"Asia","Colombia":"South America","Croatia":"Europe",
    "Cuba":"North America","Cyprus":"Europe","Czechia":"Europe","Denmark":"Europe",
    "Ecuador":"South America","Egypt":"Africa","Estonia":"Europe","Ethiopia":"Africa",
    "Finland":"Europe","France":"Europe","Georgia":"Asia","Germany":"Europe",
    "Ghana":"Africa","Greece":"Europe","Hungary":"Europe","Iceland":"Europe",
    "India":"Asia","Indonesia":"Asia","Iran":"Asia","Iraq":"Asia","Ireland":"Europe",
    "Israel":"Asia","Italy":"Europe","Japan":"Asia","Jordan":"Asia",
    "Kazakhstan":"Asia","Kenya":"Africa","Latvia":"Europe","Lebanon":"Asia",
    "Libya":"Africa","Lithuania":"Europe","Madagascar":"Africa","Malaysia":"Asia",
    "Mali":"Africa","Mexico":"North America","Mongolia":"Asia","Morocco":"Africa",
    "Mozambique":"Africa","Myanmar":"Asia","Netherlands":"Europe",
    "New Zealand":"Oceania","Nicaragua":"North America","Niger":"Africa",
    "Nigeria":"Africa","North Korea":"Asia","Norway":"Europe","Oman":"Asia",
    "Pakistan":"Asia","Panama":"North America","Paraguay":"South America",
    "Peru":"South America","Philippines":"Asia","Poland":"Europe","Portugal":"Europe",
    "Qatar":"Asia","Romania":"Europe","Russia":"Europe","Saudi Arabia":"Asia",
    "Senegal":"Africa","Serbia":"Europe","Slovakia":"Europe","Slovenia":"Europe",
    "Somalia":"Africa","South Africa":"Africa","South Korea":"Asia","Spain":"Europe",
    "Sri Lanka":"Asia","Sudan":"Africa","Sweden":"Europe","Switzerland":"Europe",
    "Syria":"Asia","Tanzania":"Africa","Thailand":"Asia","Tunisia":"Africa",
    "Turkey":"Asia","Uganda":"Africa","Ukraine":"Europe","United Kingdom":"Europe",
    "United States of America":"North America","Uruguay":"South America",
    "Uzbekistan":"Asia","Venezuela":"South America","Vietnam":"Asia",
    "Yemen":"Asia","Zambia":"Africa","Zimbabwe":"Africa",
}

EASY = {"Italy","France","Spain","United Kingdom","Germany","Norway","Sweden",
        "Finland","Denmark","Greece","United States of America","Brazil","Canada",
        "Mexico","Australia","Japan","India","China","Russia","South Africa",
        "Argentina","Chile","Egypt","Saudi Arabia","Turkey","Iran","South Korea",
        "Indonesia","Madagascar","Iceland","Netherlands","Portugal","New Zealand"}

CONTINENT_GROUPS = {
    "All":None,"Europe":["Europe"],"Africa":["Africa"],"Asia":["Asia"],
    "Americas":["North America","South America"],"Oceania":["Oceania"],
}

# ── LEVEL ──────────────────────────────────────────────────────────────────────
def get_level(xp):
    if xp>=1500: return("Grand Master","👑",1500,None)
    if xp>=700:  return("Cartographer","🧭",700,1500)
    if xp>=300:  return("Geographer","🗺️",300,700)
    if xp>=100:  return("Explorer","🧗",100,300)
    return("Rookie","🌱",0,100)

def calc_xp(elapsed, streak):
    base=10; speed=10 if elapsed<3 else(5 if elapsed<5 else 0)
    mult=4 if streak>=10 else(3 if streak>=6 else(2 if streak>=3 else 1))
    return(base+speed)*mult

def fire(s):
    return "🔥🔥🔥" if s>=10 else("🔥🔥" if s>=6 else("🔥" if s>=3 else ""))

# ── LOAD WORLD (pure shapely — no PROJ) ───────────────────────────────────────
@st.cache_data(show_spinner="Indlæser verdenskort...")
def load_world():
    try:
        url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            gj = json.loads(r.read())

        features = {}
        for feat in gj["features"]:
            name = feat["properties"].get("ADMIN") or feat["properties"].get("name","")
            geom = shape(feat["geometry"])
            features[name] = geom
        return features, None
    except Exception as e:
        return None, str(e)

# ── RENDER OUTLINE (pure matplotlib — no geopandas plot) ──────────────────────
def geom_to_patches(geom, ax, fc, ec, lw, alpha=1.0):
    from shapely.geometry import Polygon
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    for poly in polys:
        if poly.is_empty: continue
        xs, ys = poly.exterior.xy
        verts = list(zip(xs, ys))
        codes = [Path.MOVETO] + [Path.LINETO]*(len(verts)-2) + [Path.CLOSEPOLY]
        path = Path(verts, codes)
        ax.add_patch(PathPatch(path, facecolor=fc, edgecolor=ec,
                               linewidth=lw, alpha=alpha))

def render_outline(geom, hard_mode=False):
    if isinstance(geom, MultiPolygon):
        geom = max(geom.geoms, key=lambda g: g.area)
    if hard_mode:
        geom = shapely_rotate(geom, random.choice([-90,-45,45,90,180]))

    fig, ax = plt.subplots(figsize=(7,5), facecolor='#0a0a0f')
    ax.set_facecolor('#0a0a0f')

    # glow layers
    for alpha, lw in [(0.08,14),(0.15,9),(0.25,5)]:
        geom_to_patches(geom, ax, 'none', '#4fc3f7', lw, alpha)
    geom_to_patches(geom, ax, '#162033', '#4fc3f7', 2.0)

    bx = geom.bounds
    pad = max(bx[2]-bx[0], bx[3]-bx[1]) * 0.2
    ax.set_xlim(bx[0]-pad, bx[2]+pad)
    ax.set_ylim(bx[1]-pad, bx[3]+pad)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout(pad=0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='#0a0a0f', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return buf

# ── STATE ──────────────────────────────────────────────────────────────────────
def init():
    defs = {
        'screen':'menu','mode':None,'xp':0,'streak':0,'best_streak':0,
        'q_total':0,'q_correct':0,'s_count':0,'s_xp':0,
        's_ol_c':0,'s_ol_t':0,'s_ca_c':0,'s_ca_t':0,'s_qs':[],
        'q':None,'q_t0':None,'answered':False,'selected':None,'last_xp':0,
        'ss_used':False,'use_ss':False,'lb':{},'name':'',
        'timer':True,'cont_filter':'All','diff':'Normal',
    }
    for k,v in defs.items(): st.session_state.setdefault(k,v)

def reset_s():
    for k in ['s_count','s_xp','s_ol_c','s_ol_t','s_ca_c','s_ca_t','streak','last_xp']:
        st.session_state[k]=0
    st.session_state.s_qs=[]
    st.session_state.ss_used=False
    st.session_state.q=None
    st.session_state.answered=False

# ── QUESTION ───────────────────────────────────────────────────────────────────
def gen_q(world, mode, pool):
    actual = random.choice(["outline","capital"]) if mode=="blended" else mode
    correct = random.choice(pool)
    cont = CONT_MAP.get(correct,"")
    same = [c for c in pool if c!=correct and CONT_MAP.get(c)==cont]
    wrong = random.sample(same,3) if len(same)>=3 else random.sample([c for c in pool if c!=correct],3)

    if actual=="outline":
        if correct not in world: return None
        opts=[correct]+wrong; random.shuffle(opts)
        return {'mode':'outline','correct':correct,'options':opts,
                'geom':world[correct],'q':"Hvilket land er dette?"}
    else:
        cap=CAPITALS[correct]
        opts=[cap]+[CAPITALS[c] for c in wrong]; random.shuffle(opts)
        return {'mode':'capital','correct':cap,'country':correct,
                'options':opts,'q':f"Hvad er hovedstaden i {correct}?"}

# ── ANSWER ─────────────────────────────────────────────────────────────────────
def handle(sel, q):
    elapsed = time.time()-st.session_state.q_t0
    ok = sel==q['correct'] and not(st.session_state.timer and elapsed>15)
    st.session_state.selected=sel
    st.session_state.answered=True
    st.session_state.s_count+=1
    st.session_state.q_total+=1
    lbl = q.get('country') or q['correct']
    st.session_state.s_qs.append((lbl, elapsed, ok))
    if q['mode']=='outline': st.session_state.s_ol_t+=1
    else: st.session_state.s_ca_t+=1
    if ok:
        xp=calc_xp(elapsed, st.session_state.streak+1)
        st.session_state.last_xp=xp
        st.session_state.xp+=xp; st.session_state.s_xp+=xp
        st.session_state.q_correct+=1; st.session_state.streak+=1
        st.session_state.best_streak=max(st.session_state.best_streak,st.session_state.streak)
        if q['mode']=='outline': st.session_state.s_ol_c+=1
        else: st.session_state.s_ca_c+=1
    else:
        st.session_state.last_xp=0
        if st.session_state.use_ss and not st.session_state.ss_used and st.session_state.streak>0:
            st.session_state.ss_used=True; st.session_state.use_ss=False
            st.toast("🛡️ Streak reddet!")
        else:
            st.session_state.streak=0

# ── XP BAR ─────────────────────────────────────────────────────────────────────
def xp_bar():
    lv,ic,lo,hi=get_level(st.session_state.xp)
    pct=max(0,min(100,(st.session_state.xp-lo)/(hi-lo)*100)) if hi else 100
    lbl=f"{st.session_state.xp}/{hi} XP" if hi else f"{st.session_state.xp} XP"
    st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem;">'
                f'<span class="badge">{ic} {lv}</span>'
                f'<span style="color:#6b7280;font-size:.82rem;font-weight:600;">{lbl}</span></div>'
                f'<div class="xp-track"><div class="xp-fill" style="width:{pct}%;"></div></div>',
                unsafe_allow_html=True)

def stats_row():
    acc=int(st.session_state.q_correct/st.session_state.q_total*100) if st.session_state.q_total else 0
    for col,(l,v) in zip(st.columns(4),[
        ("Streak",f"{st.session_state.streak} {fire(st.session_state.streak)}"),
        ("Bedste",st.session_state.best_streak),("Accuracy",f"{acc}%"),
        ("Spillet",st.session_state.q_total)]):
        with col:
            st.markdown(f'<div class="pill"><div class="pill-l">{l}</div>'
                        f'<div class="pill-v">{v}</div></div>',unsafe_allow_html=True)

def sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Indstillinger")
        st.session_state.timer=st.toggle("Timer 15s",value=st.session_state.timer)
        st.session_state.cont_filter=st.selectbox("Kontinent",list(CONTINENT_GROUPS.keys()),
            index=list(CONTINENT_GROUPS.keys()).index(st.session_state.cont_filter))
        st.session_state.diff=st.select_slider("Sværhedsgrad",
            options=["Easy","Normal","Hard"],value=st.session_state.diff)
        st.divider()
        st.markdown("### 🛡️ Power-ups")
        if not st.session_state.ss_used and st.session_state.streak>0:
            st.session_state.use_ss=st.toggle("Streak save (1×)",value=st.session_state.use_ss)
        else:
            st.caption("Streak save brugt / ingen streak")
        if st.session_state.lb:
            st.divider(); st.markdown("### 🏆 Leaderboard")
            for i,(n,x) in enumerate(sorted(st.session_state.lb.items(),key=lambda x:-x[1])[:5],1):
                m=["🥇","🥈","🥉","  ","  "][i-1]
                st.markdown(f"{m} **{n}** · {x} XP")

# ── SCREENS ────────────────────────────────────────────────────────────────────
def screen_menu(world, pool):
    st.markdown('<h1 class="hero">ATLAS</h1><p class="sub">a geography quiz</p>',
                unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    if not st.session_state.name:
        n=st.text_input("",placeholder="Indtast dit navn",label_visibility="collapsed")
        if st.button("Start →",type="primary",use_container_width=True):
            if n.strip(): st.session_state.name=n.strip(); st.rerun()
            else: st.warning("Indtast et navn")
        return

    if st.session_state.q_total>0:
        xp_bar(); st.markdown("<br>",unsafe_allow_html=True)
        stats_row(); st.markdown("<br>",unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center;color:#9ca3af;'>Hej "
                f"<b style='color:#4fc3f7;'>{st.session_state.name}</b> — vælg en mode</p>",
                unsafe_allow_html=True)

    for col,(ic,ti,de,mo) in zip(st.columns(3),[
        ("🗺️","Outline","Gæt landet fra silhuet","outline"),
        ("🏙️","Hovedstad","Gæt landets hovedstad","capital"),
        ("⚡","Blandet","Begge modes blandet","blended")]):
        with col:
            st.markdown(f'<div style="background:linear-gradient(135deg,rgba(79,195,247,.06),rgba(124,77,255,.06));'
                        f'border:1px solid rgba(79,195,247,.18);border-radius:22px;padding:1.4rem 1rem;'
                        f'text-align:center;height:185px;display:flex;flex-direction:column;justify-content:center;">'
                        f'<div style="font-size:2.5rem;">{ic}</div>'
                        f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:1.2rem;margin:.5rem 0 .2rem;">{ti}</div>'
                        f'<div style="color:#9ca3af;font-size:.78rem;">{de}</div></div>',
                        unsafe_allow_html=True)
            if st.button(f"Spil {ti.lower()}",key=f"m_{mo}",use_container_width=True):
                reset_s(); st.session_state.mode=mo; st.session_state.screen='quiz'; st.rerun()

    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Reset profil"):
        for k in ['xp','streak','best_streak','q_total','q_correct']:
            st.session_state[k]=0
        st.session_state.lb={}; st.session_state.name=''; st.rerun()


def screen_quiz(world, pool):
    xp_bar(); st.markdown("<br>",unsafe_allow_html=True)
    stats_row(); st.markdown("<br>",unsafe_allow_html=True)

    cl,cr=st.columns([3,1])
    cl.markdown(f"<p style='color:#6b7280;font-weight:600;'>Spørgsmål "
                f"{st.session_state.s_count+1} af 10</p>",unsafe_allow_html=True)
    if cr.button("← Menu"): st.session_state.screen='menu'; st.rerun()

    if st.session_state.q is None:
        st.session_state.q=gen_q(world, st.session_state.mode, pool)
        st.session_state.q_t0=time.time()
        st.session_state.answered=False; st.session_state.selected=None

    q=st.session_state.q
    if not q: st.error("Kunne ikke generere spørgsmål."); return

    if st.session_state.timer and not st.session_state.answered:
        st.markdown('<div class="timer-track"><div class="timer-bar"></div></div>',
                    unsafe_allow_html=True)

    st.markdown(f'<div class="q">{q["q"]}</div>',unsafe_allow_html=True)

    if q['mode']=='outline':
        st.image(render_outline(q['geom'], st.session_state.diff=="Hard"),
                 use_column_width=True)

    for i,opt in enumerate(q['options']):
        with st.columns(2)[i%2]:
            key=f"o{i}_{st.session_state.s_count}"
            if st.session_state.answered:
                if opt==q['correct']:
                    st.markdown(f'<div class="ok">✓ {opt}</div>',unsafe_allow_html=True)
                elif opt==st.session_state.selected:
                    st.markdown(f'<div class="no">✗ {opt}</div>',unsafe_allow_html=True)
                else:
                    st.button(opt,key=key,disabled=True,use_container_width=True)
            else:
                if st.button(f"{i+1}. {opt}",key=key,use_container_width=True):
                    handle(opt,q); st.rerun()

    if st.session_state.answered:
        elapsed=time.time()-st.session_state.q_t0
        if st.session_state.selected==q['correct']:
            sp=" · ⚡ lyn!" if elapsed<3 else(" · ⚡ hurtig!" if elapsed<5 else "")
            st.markdown(f'<div style="text-align:center;margin-top:.8rem;">'
                        f'<span class="xpf">+{st.session_state.last_xp} XP</span>'
                        f'<span style="color:#86efac;margin-left:.5rem;">Korrekt!{sp}</span></div>',
                        unsafe_allow_html=True)
        else:
            lbl=q.get('country') or q['correct']
            st.markdown(f'<div style="text-align:center;margin-top:.8rem;color:#fca5a5;">'
                        f'Forkert — svaret var <b>{q["correct"]}</b></div>',unsafe_allow_html=True)

        fk=q.get('country') or q['correct']
        if fk in FACTS:
            st.markdown(f'<div class="fact"><div class="fl">Did you know</div>{FACTS[fk]}</div>',
                        unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        if st.session_state.s_count>=10:
            if st.button("Se resultater →",type="primary",use_container_width=True):
                st.session_state.screen='results'; st.rerun()
        else:
            if st.button("Næste →",type="primary",use_container_width=True):
                st.session_state.q=None; st.rerun()


def screen_results():
    st.markdown('<h1 class="hero" style="font-size:3.2rem;">RESULTAT</h1>'
                f'<p class="sub">{st.session_state.name}</p>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    c=st.session_state.s_ol_c+st.session_state.s_ca_c
    t=st.session_state.s_ol_t+st.session_state.s_ca_t
    acc=int(c/t*100) if t else 0

    for col,(n,l) in zip(st.columns(3),[
        (f"{c}/{t}","Rigtige"),(f"{acc}%","Accuracy"),(f"+{st.session_state.s_xp}","XP tjent")]):
        with col:
            st.markdown(f'<div class="rstat"><div class="rn">{n}</div>'
                        f'<div class="rl">{l}</div></div>',unsafe_allow_html=True)

    if st.session_state.s_ol_t>0:
        ot,oc=st.session_state.s_ol_t,st.session_state.s_ol_c
        st.markdown(f"**🗺️ Outline:** {oc}/{ot} ({int(oc/ot*100)}%)")
    if st.session_state.s_ca_t>0:
        ct,cc=st.session_state.s_ca_t,st.session_state.s_ca_c
        st.markdown(f"**🏙️ Hovedstad:** {cc}/{ct} ({int(cc/ct*100)}%)")

    if st.session_state.s_qs:
        h=max(st.session_state.s_qs,key=lambda x:x[1])
        st.markdown(f'<div class="fact"><div class="fl">Sværeste</div>'
                    f'<b>{h[0]}</b> — {h[1]:.1f} sek ({"✓" if h[2] else "✗"})</div>',
                    unsafe_allow_html=True)

    if st.session_state.name:
        st.session_state.lb[st.session_state.name]=max(
            st.session_state.lb.get(st.session_state.name,0), st.session_state.xp)

    if acc>=80: st.balloons(); st.success("🎉 Over 80% — imponerende!")
    elif acc>=50: st.info("💪 Solid runde.")
    else: st.warning("📚 Tid til at slå atlasset op.")

    c1,c2=st.columns(2)
    if c1.button("Spil igen",type="primary",use_container_width=True):
        reset_s(); st.session_state.screen='quiz'; st.rerun()
    if c2.button("Menu",use_container_width=True):
        st.session_state.screen='menu'; st.rerun()


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    init()
    sidebar()

    world, err = load_world()
    if world is None:
        st.error(f"❌ Kunne ikke indlæse kortdata: {err}")
        return

    pool = [c for c in CAPITALS if c in world]

    cf=CONTINENT_GROUPS.get(st.session_state.cont_filter)
    if cf:
        pool=[c for c in pool if CONT_MAP.get(c) in cf]

    if st.session_state.diff=="Easy":
        easy=[c for c in pool if c in EASY]
        if len(easy)>=4: pool=easy

    if len(pool)<4:
        st.error("Ikke nok lande — skift filter."); return

    if   st.session_state.screen=='menu':    screen_menu(world, pool)
    elif st.session_state.screen=='quiz':    screen_quiz(world, pool)
    elif st.session_state.screen=='results': screen_results()

if __name__=="__main__":
    main()
