#!/usr/bin/env python3
"""La Redacción — carruseles 4:5, segunda generación (9 formatos). Cada carrusel se arma como UNA tira continua
(n × 1080 px) y se corta en placas: así la foto, la curva o el camino cruzan de una placa a la siguiente.
Uso: python3 lr_carrusel2.py spec.json     (assets en ./assets: fonts/*.ttf + lr_logo.png)
Markup en textos: ==resaltado==  **negrita**  __subrayado__  ~~tachado~~  \\n salto."""
import json, os, re, sys, math, random, html

A = os.path.abspath(os.environ.get('LR_ASSETS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')))
F = A + '/fonts'; LOGO = A + '/lr_logo.png'
FONTS = ''.join(f"@font-face{{font-family:{n};src:url(file://{F}/{f});{x}}}" for n, f, x in [
    ('Arch', 'Archivo.ttf', 'font-weight:100 900;font-stretch:62% 125%'), ('Anton', 'Anton-Regular.ttf', ''),
    ('Bebas', 'BebasNeue-Regular.ttf', ''), ('BarlowC', 'BarlowCondensed-ExtraBold.ttf', 'font-weight:800'),
    ('BarlowC', 'BarlowCondensed-Medium.ttf', 'font-weight:500'), ('Mont', 'Montserrat.ttf', 'font-weight:100 900'),
    ('Rob', 'Roboto.ttf', 'font-weight:100 900'), ('Play', 'PlayfairDisplay-Italic.ttf', 'font-weight:400 900;font-style:italic'),
    ('Play', 'PlayfairDisplay.ttf', 'font-weight:400 900'), ('Mono', 'JetBrainsMono.ttf', 'font-weight:100 800'),
    ('Fred', 'Fredoka.ttf', 'font-weight:300 700;font-stretch:75% 125%')])
GRAIN = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0'/%3E"
         "%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E\")")

def md(t):
    t = html.escape(str(t or ''), quote=False)
    for a, b in [(r'==(.+?)==', r'<mark>\1</mark>'), (r'\*\*(.+?)\*\*', r'<b>\1</b>'), (r'__(.+?)__', r'<u>\1</u>'), (r'~~(.+?)~~', r'<s>\1</s>')]:
        t = re.sub(a, b, t)
    return t.replace('\\n', '<br>').replace('\n', '<br>')


def sticker(st):
    if not st: return ''
    sz = st.get('size', 210); col = st.get('color', '#FFFFFF'); pts = []
    import math
    for i in range(32):
        a = math.pi * 2 * i / 32; rr = 50 if i % 2 == 0 else 42; pts.append(f'{50+rr*math.cos(a):.1f},{50+rr*math.sin(a):.1f}')
    pos = ';'.join(f'{k}:{v}px' for k, v in st.items() if k in ('left', 'right', 'top', 'bottom'))
    return (f'<div class="stk" style="{pos};width:{sz}px;height:{sz}px;transform:rotate({st.get("rot", 12)}deg)">'
            f'<svg style="position:absolute;inset:0;filter:drop-shadow(6px 6px 0 #042326)" viewBox="0 0 100 100"><polygon points="{" ".join(pts)}" fill="{col}" stroke="#042326" stroke-width="1.6"/></svg>'
            f'<span style="position:relative;font-size:{st.get("fs", 34)}px">{md(st["text"])}</span></div>')


W, H = 1080, 1350
BASE = FONTS + """*{margin:0;padding:0;box-sizing:border-box}html,body{height:1350px;overflow:hidden}
.abs{position:absolute}.strip{position:relative;height:1350px;overflow:hidden}
.sl{position:absolute;top:0;width:1080px;height:1350px;overflow:hidden}
.fit{position:absolute;display:flex;flex-direction:column;--k:1}.fit>*{flex-shrink:0}
.logo{position:absolute;right:60px;top:56px;width:112px;height:112px;border-radius:50%;z-index:40}.ring{box-shadow:0 0 0 4px #C2E0F1}
.mono{font-family:Mono;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
.grain{position:absolute;inset:0;background-image:""" + GRAIN + """;opacity:.16;mix-blend-mode:multiply;z-index:60;pointer-events:none}
b{font-weight:800}
"""
FITJS = """<script>
document.fonts.ready.then(()=>{
document.querySelectorAll('.num').forEach(e=>{let s=+e.dataset.max,w=+e.dataset.w;e.style.fontSize=s+'px';while(e.getBoundingClientRect().width>w&&s>80){s-=6;e.style.fontSize=s+'px'}});
document.querySelectorAll('.fit').forEach(b=>{let k=1;while(b.scrollHeight>b.clientHeight+2&&k>.55){k-=.02;b.style.setProperty('--k',k)}if(k<.8)console.log('SHRINK '+(b.dataset.id||'')+' '+k.toFixed(2))});
window.__done=1});
</script>"""
logo = lambda ring=False: f'<img class="logo{" ring" if ring else ""}" src="file://{LOGO}">'
src = lambda p: 'file://' + os.path.abspath(p)


def cta_html(s, cls='cta', ucls='u'):
    tipo = s.get('tipo', 'nota'); per = f' {s["persona"]}' if s.get('persona') else ''
    return (f'<div class="{cls}">{md(s.get("cta") or f"Leé la {tipo} completa{per} en")}<br>'
            f'<b>La Redacción | <span class="{ucls}">www.lrlaredaccion.com</span></b></div>')


def motto(s):
    return '' if s.get('motto', 1) == '' else f'<div class="motto">{md(s.get("motto", "Leer para entender y pensar"))}</div>'


def cruces(sp, S):
    """Qué fotos cruzan a la placa siguiente. Spec `cruce`: 'auto' (def.: una sí, una no), 'todas' o 'ninguna'.
    Por foto: `photo.cruza` true/false manda sobre lo anterior. La última placa nunca cruza."""
    mode = sp.get('cruce', 'auto'); out = []; i = 0
    for k, s in enumerate(S):
        p = s.get('photo'); v = False
        if p:
            v = mode == 'todas' or (mode == 'auto' and i % 2 == 0)
            if isinstance(p, dict) and 'cruza' in p: v = bool(p['cruza'])
            i += 1
        out.append(v and k < len(S) - 1)
    return out


def catmull(pts):
    d = f"M {pts[0][0]:.0f} {pts[0][1]:.0f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        d += f" C {p1[0]+(p2[0]-p0[0])/6:.0f} {p1[1]+(p2[1]-p0[1])/6:.0f}, {p2[0]-(p3[0]-p1[0])/6:.0f} {p2[1]-(p3[1]-p1[1])/6:.0f}, {p2[0]:.0f} {p2[1]:.0f}"
    return d


# ================================================================ EL DATO v2 — «el número es la imagen»
# Roles: gancho {n,title,text} · cifra {n,label,text} · cierre {title,text,tipo}.  `curve`: un valor 0–1 por placa.
DATO = {'lima': dict(bg='#D9F45B', ink='#151515', num='#151515', mb='#151515', mf='#D9F45B', line='#151515', fill='rgba(21,21,21,.10)'),
        'negro': dict(bg='#151515', ink='#EEEAE2', num='#D9F45B', mb='#D9F45B', mf='#151515', line='#D9F45B', fill='rgba(217,244,91,.14)', ring=1),
        'papel': dict(bg='#EEEAE2', ink='#151515', num='#151515', mb='#D9F45B', mf='#151515', line='#151515', fill='rgba(21,21,21,.08)')}


def dato(sp):
    S = sp['slides']; n = len(S); cyc = ['lima', 'negro', 'papel']
    cv = sp.get('curve') or [.9 - .7 * i / max(n - 2, 1) for i in range(n - 1)] + [.8]
    Y = lambda v: 1272 - v * 170
    pts = [(-W // 2, Y(cv[0]))] + [(k * W + W // 2, Y(v)) for k, v in enumerate(cv)] + [(n * W + W // 2, Y(cv[-1]))]
    d = catmull(pts); area = d + f" L {n*W+W//2} {H+20} L {-W//2} {H+20} Z"
    css = BASE + """.sl{font-family:Arch}
.kick{position:absolute;left:80px;top:92px;font-size:24px;z-index:8}
.num{display:inline-block;font-family:Arch;font-weight:900;font-stretch:62%;letter-spacing:-.02em;line-height:.82;white-space:nowrap;margin-left:-8px}
.lab{font:900 calc(70px*var(--k)) Arch;font-stretch:68%;text-transform:uppercase;line-height:1.12;padding:0 .14em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.t{font:900 calc(96px*var(--k)*var(--ts,1)) Arch;font-stretch:68%;text-transform:uppercase;line-height:.96}
.t mark,.cta mark{padding:0 .1em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.p{font:500 calc(42px*var(--k)) Arch;line-height:1.28;max-width:880px}
.cta{font:500 calc(34px*var(--k)) Arch;line-height:1.35}.cta .u{text-decoration:underline;font-weight:800}
.motto{font:900 calc(50px*var(--k)) Arch;font-stretch:68%;text-transform:uppercase;letter-spacing:.03em}
.cnt{position:absolute;left:80px;bottom:44px;font-size:22px;z-index:8}.go{position:absolute;right:80px;bottom:44px;font-size:24px;z-index:8}
"""
    out = ''
    for k, s in enumerate(S):
        role = s.get('role', 'cifra'); c = DATO[s.get('scheme') or ('negro' if role == 'cierre' else cyc[k % 3])]
        mk = f'background:{c["mb"]};color:{c["mf"]}'
        body = f'<div class="kick mono" style="color:{c["ink"]}">{md(s.get("tag") or sp.get("tag", ""))}</div>'
        if role == 'cierre':
            inner = (f'<div class="t" style="--ts:{s.get("title_scale", 1.3)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
                     + cta_html(s) + motto(s).replace('class="motto"', f'class="motto" style="color:{c["num"]}"'))
            body += f'<div class="fit" data-id="dato{k+1}" style="left:80px;right:80px;top:230px;bottom:330px;gap:calc(36px*var(--k));justify-content:center">{inner}</div>'
        else:
            inner = f'<div><span class="num" data-max="{s.get("size", 900)}" data-w="{s.get("fitw", 985)}" style="color:{c["num"]}">{md(s["n"])}</span></div>'
            if role == 'gancho':
                inner += f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>'
            elif s.get('label'):
                inner += f'<div><span class="lab" style="{mk}">{md(s["label"])}</span></div>'
            if s.get('text'): inner += f'<div class="p">{md(s["text"])}</div>'
            body += f'<div class="fit" data-id="dato{k+1}" style="left:80px;right:0;top:214px;bottom:270px;gap:calc(28px*var(--k))">{inner}</div>'
        y = Y(cv[k])
        body += (f'<svg class="abs" style="left:0;top:0;z-index:3" width="{W}" height="{H}"><g transform="translate({-k*W},0)">'
                 f'<path d="{area}" fill="{c["fill"]}"/><path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="7" stroke-linecap="round"/></g>'
                 f'<circle cx="{W//2}" cy="{y:.0f}" r="17" fill="{c["bg"]}" stroke="{c["line"]}" stroke-width="7"/></svg>')
        if s.get('mark'):
            body += f'<div class="abs mono" style="left:0;width:{W}px;text-align:center;top:{y-64:.0f}px;font-size:22px;z-index:8">{md(s["mark"])}</div>'
        body += f'<div class="cnt mono">{k+1:02d}/{n:02d}</div>' + ('<div class="go mono">DESLIZÁ →</div>' if k == 0 else '')
        out += (f'<div class="sl" style="left:{k*W}px;background:{c["bg"]};color:{c["ink"]}"><style>#d{k} mark{{{mk}}}</style><div id="d{k}">{body}</div>{logo(c.get("ring"))}</div>')
    return css, out, n


# ================================================================ HISTORIAS v2 — formas blandas, la foto se asoma a la placa siguiente
# Roles: gancho/paso {tag,title,text,photo} · cita {quote,author,role} · cierre {title,text,tipo}
HIST = {'crema': dict(bg='#FFF1E0', ink='#2B1166', ac='#FF5A4E', btn='#2B1166', bf='#FFF1E0'),
        'coral': dict(bg='#FF6B5E', ink='#2B1166', ac='#FFF1E0', btn='#2B1166', bf='#FFF1E0'),
        'violeta': dict(bg='#2B1166', ink='#FFF1E0', ac='#FF6B5E', btn='#FF6B5E', bf='#2B1166', ring=1)}


def historias(sp):
    S = sp['slides']; n = len(S); cyc = ['crema', 'coral', 'violeta']; sch = []
    for k, s in enumerate(S):
        r = s.get('role', 'paso'); sch.append(s.get('scheme') or ('violeta' if r == 'cita' else 'coral' if r == 'cierre' else cyc[k % 3]))
    for k in range(1, n):  # nunca dos placas seguidas del mismo color
        if sch[k] == sch[k - 1] and not S[k].get('scheme'): sch[k] = [c for c in cyc if c != sch[k - 1] and (k + 1 >= n or c != sch[k + 1])][0]
    css = BASE + """.sl{font-family:Mont}
.chip{position:absolute;left:96px;top:78px;border-radius:999px;padding:14px 30px;font:800 26px Mont;letter-spacing:.12em;text-transform:uppercase;z-index:8}
.t{font:800 calc(74px*var(--k)*var(--ts,1)) Mont;text-transform:uppercase;line-height:1.02;letter-spacing:-.01em}
.t mark,.q mark{background:none;color:var(--ac)}
.p{font:500 calc(38px*var(--k)) Mont;line-height:1.32}
.q{font:700 calc(60px*var(--k)) Mont;line-height:1.14;letter-spacing:-.01em}
.qm{font:800 300px Mont;line-height:.7;height:120px;color:var(--ac)}
.who{font:800 30px Mont;letter-spacing:.08em;text-transform:uppercase;border-top:5px solid var(--ac);padding-top:18px;align-self:flex-start}.who span{display:block;font:500 26px Mont;letter-spacing:.02em;text-transform:none;margin-top:6px;opacity:.85}
.ph{position:absolute;overflow:hidden;border-radius:999px;z-index:2}.ph img{width:100%;height:100%;object-fit:cover}
.cap{position:absolute;font:700 17px Mono;letter-spacing:.08em;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.9);z-index:3}
.dots{position:absolute;left:96px;bottom:70px;display:flex;gap:10px;z-index:8}.dots i{height:14px;border-radius:999px;border:3px solid currentColor}
.btn{position:absolute;right:70px;bottom:52px;width:104px;height:104px;border-radius:50%;display:grid;place-items:center;z-index:8}
.cta{font:500 calc(34px*var(--k)) Mont;line-height:1.4}.cta .u{text-decoration:underline;font-weight:800}
.motto{font:800 calc(40px*var(--k)) Mont;text-transform:uppercase;letter-spacing:.02em;color:var(--ac)}
"""
    arrow = lambda col, sz=52: f'<svg width="{sz}" height="{sz}" viewBox="0 0 24 24" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 5l7 7-7 7"/></svg>'
    glob = ''; out = ''; band_prev = None; ab = 0; CR = cruces(sp, S)
    for k, s in enumerate(S):
        c = HIST[sch[k]]; role = s.get('role', 'paso'); p = s.get('photo'); sliver = band_prev is not None
        left = 190 if sliver else 96
        body = f'<div class="chip" style="background:{c["btn"]};color:{c["bf"]}">{md(s["tag"])}</div>' if s.get('tag') else ''
        band = None
        if p:
            if isinstance(p, str): p = {'src': p}
            band = 'top' if ab % 2 == 0 else 'bottom'; ab += 1
            ph = p.get('h', 600 if role == 'gancho' else 520); y = 200 if band == 'top' else 1180 - ph; x = k * W + 96; pw = W - 96 + (120 if CR[k] else -96)
            glob += (f'<div class="ph" style="left:{x}px;top:{y}px;width:{pw}px;height:{ph}px"><img src="{src(p["src"])}" style="object-position:{p.get("fx", .5)*100:.0f}% {p.get("fy", .5)*100:.0f}%"></div>')
            if p.get('caption'): glob += f'<div class="cap" style="left:{x+ph//2-40}px;top:{y+ph-38}px">{md(p["caption"])}</div>'
            box = f'top:{y+ph+50}px;bottom:190px' if band == 'top' else f'top:200px;bottom:{H-y+40}px;justify-content:center'
            inner = f'<div class="t" style="--ts:{s.get("title_scale", 1.2 if role == "gancho" else 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
            body += f'<div class="fit" data-id="hist{k+1}" style="left:{left}px;right:90px;{box};gap:calc(24px*var(--k))">{inner}</div>'
        elif role == 'cita':
            inner = (f'<div class="qm">“</div><div class="q">{md(s["quote"])}</div>'
                     + (f'<div class="who">{md(s["author"])}<span>{md(s.get("role_text", ""))}</span></div>' if s.get('author') else ''))
            body += f'<div class="fit" data-id="hist{k+1}" style="left:{left}px;right:96px;top:210px;bottom:500px;gap:calc(34px*var(--k));justify-content:center">{inner}</div>'
        else:  # cierre / texto
            inner = (f'<div class="t" style="--ts:{s.get("title_scale", 1.25)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
                     + (cta_html(s) + motto(s) if role == 'cierre' else ''))
            body += f'<div class="fit" data-id="hist{k+1}" style="left:96px;right:96px;top:230px;bottom:520px;gap:calc(34px*var(--k));justify-content:center">{inner}</div>'
        # puente hacia la placa siguiente: si no hay foto que se asome, un círculo de color con la flecha
        if k < n - 1:
            if band is None:
                col = [HIST[x]['bg'] for x in cyc if x not in (sch[k], sch[k + 1])][0]
                glob += f'<div class="abs" style="left:{(k+1)*W-170}px;top:870px;width:340px;height:340px;border-radius:50%;background:{col};z-index:2"></div>'
                body += f'<div class="abs" style="right:44px;top:1004px;z-index:8">{arrow("#2B1166" if col != "#2B1166" else "#FFF1E0", 72)}</div>'
            else:
                body += f'<div class="btn" style="background:{c["btn"]}">{arrow(c["bf"])}</div>'
        dots = ''.join(f'<i style="width:{46 if j == k else 14}px;background:{"currentColor" if j <= k else "transparent"}"></i>' for j in range(n))
        body += f'<div class="dots" style="color:{c["ink"]}">{dots}</div>'
        out += f'<div class="abs" style="left:{k*W}px;top:0;width:{W}px;height:{H}px;background:{c["bg"]};z-index:0"></div>'
        out += f'<div class="sl" style="left:{k*W}px;color:{c["ink"]};--ac:{c["ac"]};z-index:5">{body}{logo(c.get("ring"))}</div>'
        band_prev = band if CR[k] else None
    return css, glob + out, n


# ================================================================ PANORAMA v2 — mapa con relieve: el camino sube y baja, las fotos son paradas de la línea
# Estructura igual a la v1: intro {tag,title,text,photo} · stations [{label,title,text,photo,fx,fy,icon}] · outro {tag,title,text,tipo}
def panorama(sp):
    st = sp['stations']; n = len(st) + 2
    cream, deep, red = sp.get('colors', ['#EFE8D8', '#042326', '#C2412D'])
    YL, YH, R = 985, 305, 215
    lev = [YL if k % 2 == 0 else YH for k in range(n)]
    hl = lambda t: md(t).replace('<mark>', f'<span style="color:{red}">').replace('</mark>', '</span>')
    d = f"M 250 {lev[0]} H 920"
    for k in range(n - 1):
        x1, x2 = k * W + 920, (k + 1) * W + 160
        d += f" C {x1+190} {lev[k]}, {x2-190} {lev[k+1]}, {x2} {lev[k+1]} H {(k+1)*W + (920 if k + 1 < n - 1 else 540)}"
    rnd = random.Random(sp.get('seed', 7)); rings = ''
    for c in range(1, n):
        cx, cy = c * W + rnd.randint(-70, 70), 650 + rnd.randint(-120, 120); ph = [rnd.uniform(0, 6.28) for _ in range(3)]
        for j in range(1, 9):
            r0 = j * 62; pts = []
            for a in range(0, 360, 12):
                t = math.radians(a); rr = r0 * (1 + .10 * math.sin(2 * t + ph[0]) + .07 * math.sin(3 * t + ph[1]) + .04 * math.sin(5 * t + ph[2]))
                pts.append((cx + rr * 1.25 * math.cos(t), cy + rr * math.sin(t)))
            rings += f'<path d="{catmull(pts + [pts[0]])}" fill="none" stroke="{deep}" stroke-opacity=".11" stroke-width="2.5"/>'
    css = BASE + f""".sl{{font-family:Arch;color:{deep}}}
.t{{font:900 calc(var(--tz,98px)*var(--k)) Arch;font-stretch:72%;line-height:.94;text-transform:uppercase}}
.p{{font:400 calc(39px*var(--k)) Arch;line-height:1.3}}
.lb{{font:700 26px Mono;color:{red};letter-spacing:.14em;text-transform:uppercase}}
.cta{{font:400 calc(33px*var(--k)) Arch;line-height:1.35}}.cta .u{{color:{red};font-weight:800}}
.motto{{font:900 calc(46px*var(--k)) Arch;font-stretch:75%;letter-spacing:.04em;text-transform:uppercase;color:{red}}}
.node{{position:absolute;border-radius:50%;border:10px solid {cream};box-shadow:0 0 0 6px {deep};z-index:4;background-size:cover}}
.cap{{position:absolute;font:700 17px Mono;letter-spacing:.08em;z-index:6}}
"""
    glob = (f'<div class="abs" style="inset:0;background:{cream}"></div>'
            f'<svg class="abs" style="left:0;top:0;z-index:1" width="{n*W}" height="{H}">{rings}</svg>'
            f'<svg class="abs" style="left:0;top:0;z-index:3" width="{n*W}" height="{H}"><path d="{d}" fill="none" stroke="{deep}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{cream}" stroke-width="3" stroke-dasharray="26 22"/></svg>')
    def mini(k):
        dots = ''.join(f'<circle cx="{j*W+W//2}" cy="{lev[j]}" r="{150 if j == k else 85}" fill="{red if j == k else deep}"/>' for j in range(n))
        return (f'<svg class="abs" style="left:80px;bottom:44px;z-index:8" width="{52*n}" height="50" viewBox="0 150 {n*W} 1000" preserveAspectRatio="none">'
                f'<path d="{d}" fill="none" stroke="{deep}" stroke-width="3" vector-effect="non-scaling-stroke"/>{dots}</svg>'
                f'<div class="abs mono" style="left:{80+52*n+24}px;bottom:56px;font-size:22px;z-index:8">{k+1:02d}/{n:02d}</div>')
    def box(k, inner, extra=''):
        if lev[k] == YL: pos = f'top:190px;bottom:{H-(YL-R-50)}px;justify-content:center'
        else: pos = f'top:{YH+R+56}px;bottom:150px;justify-content:flex-start'
        return f'<div class="fit" data-id="pano{k+1}" style="left:150px;right:150px;{pos};gap:calc(22px*var(--k));align-items:center;text-align:center;z-index:6;{extra}">{inner}</div>'
    out = ''
    # intro
    it = sp['intro']; body = ''; p = it.get('photo'); top = 190
    if p:
        if isinstance(p, str): p = {'src': p}
        h = p.get('h', 470); top = h - 40
        body += (f'<div class="abs" style="left:0;top:0;width:{W}px;height:{h}px;background:url({src(p["src"])}) {p.get("fx", .5)*100:.0f}% {p.get("fy", .5)*100:.0f}%/cover;z-index:2"></div>'
                 f'<div class="abs" style="left:0;top:{h-250}px;width:{W}px;height:251px;background:linear-gradient(transparent,{cream});z-index:2"></div>')
        if p.get('caption'): body += f'<div class="cap" style="left:80px;top:84px;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.8)">{md(p["caption"])}</div>'
    inner = f'<div class="lb">{md(it.get("tag", "RECORRIDO · DESLIZÁ →"))}</div><div class="t" style="--tz:{it.get("size", 118)}px">{hl(it["title"])}</div>' + (f'<div class="p">{md(it["text"])}</div>' if it.get('text') else '')
    body += f'<div class="fit" data-id="pano1" style="left:80px;right:80px;top:{top}px;bottom:{H-(YL-70)}px;gap:calc(22px*var(--k));justify-content:center;z-index:6">{inner}</div>'
    body += (f'<div class="abs" style="left:{250-22}px;top:{lev[0]-22}px;width:44px;height:44px;border-radius:50%;background:{red};box-shadow:0 0 0 9px {cream},0 0 0 13px {deep};z-index:5"></div>'
             f'<div class="abs lb" style="left:80px;top:{lev[0]+44}px;z-index:6">{md(it.get("start", "INICIO"))}</div>')
    out += f'<div class="sl" style="left:0">{body}{mini(0)}{logo(bool(p))}</div>'
    # estaciones
    for i, s in enumerate(st):
        k = i + 1; y = lev[k]
        if s.get('photo'):
            node = f'<div class="node" style="left:{W//2-R}px;top:{y-R}px;width:{2*R}px;height:{2*R}px;background-image:url({src(s["photo"])});background-size:{s.get("zoom", 1)*100:.0f}% auto;background-position:{s.get("fx", .5)*100:.0f}% {s.get("fy", .4)*100:.0f}%"></div>'
        else:
            node = f'<div class="node" style="left:{W//2-R}px;top:{y-R}px;width:{2*R}px;height:{2*R}px;background:{deep};display:grid;place-items:center;font:900 190px Arch;font-stretch:72%;color:{cream}">{md(s.get("icon", f"{i+1}"))}</div>'
        cap = f'<div class="cap" style="left:0;width:{W}px;text-align:center;top:{y+R+24 if y == YL else y-R-44}px;opacity:.6">{md(s["caption"])}</div>' if s.get('caption') else ''
        inner = f'<div class="lb">{md(s.get("label", f"ETAPA {i+1:02d}"))}</div><div class="t" style="--tz:{s.get("size", 98)}px">{hl(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
        out += f'<div class="sl" style="left:{k*W}px">{node}{cap}{box(k, inner)}{mini(k)}{logo()}</div>'
    # cierre
    en = sp['outro']; k = n - 1; y = lev[k]
    end = (f'<div class="abs" style="left:{W//2-74}px;top:{y-74}px;width:148px;height:148px;border-radius:50%;background:{red};box-shadow:0 0 0 10px {cream},0 0 0 16px {deep};display:grid;place-items:center;z-index:5">'
           f'<svg width="76" height="76" viewBox="0 0 24 24" fill="none" stroke="{cream}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5.5 5.5L20 7"/></svg></div>')
    inner = ((f'<div class="lb">{md(en["tag"])}</div>' if en.get('tag') else '') + f'<div class="t" style="--tz:{en.get("size", 104)}px">{hl(en["title"])}</div>'
             + (f'<div class="p">{md(en["text"])}</div>' if en.get('text') else '') + cta_html(en) + motto(en))
    if y == YH: pos = f'top:{y+74+70}px;bottom:150px;justify-content:center'
    else: pos = f'top:190px;bottom:{H-(y-74-60)}px;justify-content:center'
    out += (f'<div class="sl" style="left:{k*W}px">{end}<div class="fit" data-id="pano{n}" style="left:110px;right:110px;{pos};gap:calc(24px*var(--k));align-items:center;text-align:center;z-index:6">{inner}</div>{mini(k)}{logo()}</div>')
    return css, glob + out, n



P = lambda p: {'src': p} if isinstance(p, str) else p
opos = lambda p, dy=.5: f"{p.get('fx', .5)*100:.0f}% {p.get('fy', dy)*100:.0f}%"
CHECK = lambda col, sz=120, sw=3.2: f'<svg width="{sz}" height="{sz}" viewBox="0 0 24 24" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5.5 5.5L20 7"/></svg>'


# ================================================================ EXPLICADOR v2 — cuaderno de apuntes: una pregunta por placa, número en el margen
# Roles: gancho {tag,title,text} (arma solo el índice con las preguntas) · pregunta {title,text,photo,note} · cierre {title,items,text,tipo}
def explicador(sp):
    S = sp['slides']; n = len(S); qs = [s for s in S if s.get('role', 'pregunta') == 'pregunta']
    css = BASE + """.sl{font-family:Arch;color:#042326}
.kick{position:absolute;left:244px;top:86px;background:#042326;color:#C2E0F1;font:700 24px Mono;letter-spacing:.14em;text-transform:uppercase;padding:10px 16px;z-index:8}
.mnum{position:absolute;left:0;width:204px;text-align:center;top:200px;font:900 250px Arch;font-stretch:66%;line-height:.8;z-index:6}
.mlab{position:absolute;left:0;width:204px;text-align:center;top:98px;font:700 22px Mono;letter-spacing:.12em;z-index:6}
.t{font:900 calc(98px*var(--k)*var(--ts,1)) Arch;font-stretch:74%;text-transform:uppercase;line-height:.98}
.t mark,.p mark,.li mark,.cta mark{background:#C2E0F1;color:#042326;padding:0 .1em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.p{font:400 calc(41px*var(--k)) Arch;line-height:1.3}
.li{display:grid;grid-template-columns:76px 1fr;align-items:baseline;font:800 calc(40px*var(--k)) Arch;font-stretch:88%;line-height:1.15;border-top:3px solid #042326;padding:calc(20px*var(--k)) 0}.li i{font:700 calc(26px*var(--k)) Mono;font-style:normal}
.note{align-self:flex-start;font:700 calc(25px*var(--k)) Mono;letter-spacing:.04em;background:#C2E0F1;padding:8px 14px}
.print{position:absolute;background:#fff;padding:16px;box-shadow:0 22px 50px rgba(0,0,0,.25);z-index:3}.print img{display:block;width:100%;height:100%;object-fit:cover}
.tape{position:absolute;width:170px;height:46px;background:rgba(160,205,232,.9);z-index:4}
.cap{position:absolute;font:700 16px Mono;letter-spacing:.08em;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.9);z-index:5}
.cta{font:400 calc(35px*var(--k)) Arch;line-height:1.35}.cta .u{text-decoration:underline;font-weight:800}
.motto{font:900 calc(50px*var(--k)) Arch;font-stretch:74%;text-transform:uppercase;letter-spacing:.03em}
"""
    glob = ('<div class="abs" style="inset:0;background:#E9E4DA"></div>'
            '<div class="abs" style="inset:0;z-index:1;background:repeating-linear-gradient(transparent 0 53px,rgba(4,35,38,.075) 53px 54px)"></div>')
    out = ''; qi = 0; CR = cruces(sp, S)
    for k, s in enumerate(S):
        role = s.get('role', 'pregunta'); p = s.get('photo')
        body = '<div class="abs" style="left:204px;top:0;bottom:0;width:5px;background:#8FC1DF;z-index:2"></div>'
        body += f'<div class="mlab">{k+1:02d}/{n:02d}</div>'
        if s.get('tag'): body += f'<div class="kick">{md(s["tag"])}</div>'
        if role == 'pregunta': qi += 1
        body += f'<div class="mnum">{"?" if role == "gancho" else qi if role == "pregunta" else ""}</div>'
        if role == 'cierre': body += f'<div class="abs" style="left:42px;top:200px;z-index:6">{CHECK("#042326", 120, 3.6)}</div>'
        inner = f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
        if s.get('note'): inner += f'<div class="note">↳ {md(s["note"])}</div>'
        items = s.get('items') or ([q['title'] for q in qs] if role == 'gancho' and s.get('index', 1) else [])
        if items: inner += '<div>' + ''.join(f'<div class="li"><i>{j+1:02d}</i><span>{md(it)}</span></div>' for j, it in enumerate(items)) + '</div>'
        if role == 'cierre': inner += cta_html(s) + motto(s)
        if p:
            p = P(p); pw, ph = p.get('w', 780), p.get('h', 440); x = k * W + W + (130 if CR[k] else -84) - pw; y = 1260 - ph; rot = -1.6 if k % 2 else 1.6
            glob += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{pw}px;height:{ph}px;transform:rotate({rot}deg);z-index:3">'
                     f'<div class="print" style="inset:0"><img src="{src(p["src"])}" style="object-position:{opos(p)}"></div>'
                     f'<div class="tape" style="left:{(pw-(130 if CR[k] else 0))//2-85}px;top:-22px;transform:rotate({-rot*2}deg)"></div>'
                     + (f'<div class="cap" style="left:34px;bottom:30px">{md(p["caption"])}</div>' if p.get('caption') else '') + '</div>')
        body += f'<div class="fit" data-id="expl{k+1}" style="left:244px;right:84px;top:214px;bottom:{H-(1260-P(p).get("h",440))+56 if p else 190}px;gap:calc(26px*var(--k));justify-content:{"flex-start" if p else "center"}">{inner}</div>'
        if not p and k < n - 1:
            body += ('<div class="abs" style="right:80px;bottom:84px;width:120px;height:5px;background:#042326;z-index:8"></div>'
                     '<div class="abs" style="right:78px;bottom:74px;width:24px;height:24px;border-right:5px solid #042326;border-top:5px solid #042326;transform:rotate(45deg);z-index:8"></div>')
        out += f'<div class="sl" style="left:{k*W}px;z-index:5">{body}{logo()}</div>'
    return css, glob + out, n


# ================================================================ EL CASO v2 — expediente de cine: tira de fotogramas corrida respecto del corte + hilo rojo
# Roles: capitulo {chapter,tag,title,text,photo,hook} · cierre {title,text,tipo,help}
def caso(sp):
    S = sp['slides']; n = len(S); red = '#E2382C'; Y0, FH = 215, 480
    css = BASE + """.sl{font-family:Arch;color:#EDE6DA}
.chap{position:absolute;left:80px;top:82px;border:2px solid #E2382C;color:#E2382C;font:700 24px Mono;letter-spacing:.12em;text-transform:uppercase;padding:10px 16px;z-index:8;background:#0B0A0C}
.kick{align-self:flex-start;background:#E2382C;color:#0B0A0C;font:700 22px Mono;letter-spacing:.14em;text-transform:uppercase;padding:6px 12px}
.t{font:400 calc(106px*var(--k)*var(--ts,1)) Anton;text-transform:uppercase;line-height:1.07}.t mark,.cta mark{background:none;color:#E2382C}
.p{font:400 calc(40px*var(--k)) Arch;line-height:1.3;color:#d9d3d6}.p mark{background:none;color:#E2382C;font-weight:700}
.fr{position:absolute;overflow:hidden;z-index:2;background:#1a1719}.fr img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.15) brightness(.88)}
.cap{position:absolute;font:700 16px Mono;letter-spacing:.08em;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.9);z-index:4}
.hook{position:absolute;right:76px;bottom:62px;font:700 36px Arch;display:flex;align-items:center;gap:14px;z-index:8}.hook::after{content:'»';font:900 70px Arch;color:#E2382C;line-height:.6}
.cnt{position:absolute;left:80px;bottom:72px;font-size:22px;color:#E2382C;z-index:8}
.ghost{position:absolute;right:30px;top:170px;font:400 820px Anton;line-height:.9;color:#18151a;z-index:1}
.cta{font:400 calc(35px*var(--k)) Arch;line-height:1.35;color:#d9d3d6}.cta b{color:#EDE6DA}.cta .u{color:#E2382C;text-decoration:underline;font-weight:800}
.motto{font:400 calc(54px*var(--k)) Anton;text-transform:uppercase;letter-spacing:.03em;color:#E2382C}
.help{display:flex;gap:18px;align-items:center;background:#EDE6DA;color:#0B0A0C;padding:18px 26px;font:500 calc(28px*var(--k)) Arch}.help b{background:#C2E0F1;color:#042326;font:900 34px Arch;padding:2px 14px;white-space:nowrap}
"""
    rnd = random.Random(sp.get('seed', 3)); last = (n - 1) * W + 120
    pts = [(x, Y0 + FH + 62 + rnd.randint(-12, 12)) for x in range(-40, last, 260)] + [(last, Y0 + FH + 62)]
    def ty(x):
        for a, b in zip(pts, pts[1:]):
            if a[0] <= x <= b[0]: return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
        return pts[-1][1]
    glob = (f'<div class="abs" style="inset:0;background:radial-gradient(60% 60% at 50% 40%,#211b1f 0%,#0B0A0C 80%),#0B0A0C"></div>'
            f'<div class="abs" style="left:0;right:0;top:{Y0-10}px;height:1px;background:#3a3438;z-index:1"></div><div class="abs" style="left:0;right:0;top:{Y0+FH+9}px;height:1px;background:#3a3438;z-index:1"></div>'
            f'<svg class="abs" style="left:0;top:0;z-index:6" width="{n*W}" height="{H}"><path d="{catmull(pts)}" fill="none" stroke="{red}" stroke-width="4"/>'
            + ''.join(f'<circle cx="{k*W+120}" cy="{ty(k*W+120) if k < n-1 else pts[-1][1]:.0f}" r="13" fill="{red}" stroke="#0B0A0C" stroke-width="5"/>' for k in range(n)) + '</svg>')
    out = ''; prev = False; CR = cruces(sp, S)
    for k, s in enumerate(S):
        role = s.get('role', 'capitulo'); p = s.get('photo'); sliver = prev
        body = f'<div class="chap">{md(s.get("chapter") or f"{k+1:02d}/{n:02d}")}</div>'
        if p:
            p = P(p); x = k * W + (156 if sliver else 0)
            glob += f'<div class="fr" style="left:{x}px;top:{Y0}px;width:{(k+1)*W+(140 if CR[k] else 0)-x}px;height:{FH}px"><img src="{src(p["src"])}" style="object-position:{opos(p)}"></div>'
            if p.get('caption'): glob += f'<div class="cap" style="left:{x+24}px;top:{Y0+FH-34}px">{md(p["caption"])}</div>'
        else:
            body += f'<div class="ghost">{k+1}</div>'
        inner = (f'<div class="kick">{md(s["tag"])}</div>' if s.get('tag') else '') + f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
        low = f'top:{Y0+FH+112}px;bottom:170px'; lx = 200 if sliver and not p else 80
        if p:
            body += f'<div class="fit" data-id="caso{k+1}" style="left:80px;right:80px;{low};justify-content:flex-start;gap:calc(24px*var(--k));z-index:7">{inner}</div>'
        else:  # sin foto: el texto va arriba del hilo; en el cierre, la bajada fija va debajo
            body += f'<div class="fit" data-id="caso{k+1}" style="left:{lx}px;right:80px;top:250px;bottom:{H-(Y0+FH+20)}px;justify-content:center;gap:calc(24px*var(--k));z-index:7">{inner}</div>'
            if role == 'cierre':
                tail = cta_html(s) + motto(s) + (f'<div class="help"><b>{md(s["help"]["n"])}</b>{md(s["help"]["text"])}</div>' if s.get('help') else '')
                body += f'<div class="fit" data-id="caso{k+1}b" style="left:{lx}px;right:80px;{low};justify-content:flex-start;gap:calc(24px*var(--k));z-index:7">{tail}</div>'
        body += f'<div class="cnt mono">{k+1:02d}/{n:02d}</div>' + (f'<div class="hook">{md(s["hook"])}</div>' if s.get('hook') else '')
        out += f'<div class="sl" style="left:{k*W}px;z-index:5">{body}{logo(True)}</div>'
        prev = CR[k]
    return css, glob + out, n


# ================================================================ RETRATO v2 — tapa de revista: la cara a sangre y la columna de foto que sigue en la placa siguiente
# Roles: tapa {tag,name,title,photo} · cita {quote,text,photo} · texto {title,text,photo} · cierre {title,text,tipo,persona}
RET = {'crema': dict(bg='#F3E7D3', ink='#2A1410', ac='#B8442C'), 'terra': dict(bg='#B8442C', ink='#F3E7D3', ac='#2A1410', ring=1)}


def retrato(sp):
    S = sp['slides']; n = len(S)
    css = BASE + """.sl{font-family:BarlowC;font-weight:500}
.tag{align-self:flex-start;font:800 28px BarlowC;letter-spacing:.18em;text-transform:uppercase;border-bottom:4px solid currentColor;padding-bottom:8px}
.name{font:italic 700 calc(170px*var(--k)) Play;line-height:.92;letter-spacing:-.01em}
.t,.q{font:italic 600 calc(90px*var(--k)*var(--ts,1)) Play;line-height:1.08}.t mark,.q mark,.cta mark{background:none;color:var(--ac)}
.qm{font:900 380px Play;line-height:.7;height:150px;color:var(--ac)}
.p{font:500 calc(44px*var(--k)) BarlowC;line-height:1.22}
.who{font:800 30px BarlowC;letter-spacing:.14em;text-transform:uppercase}
.col{position:absolute;top:0;height:1350px;overflow:hidden;z-index:2}.col img{width:100%;height:100%;object-fit:cover}
.cap{position:absolute;font:700 15px Mono;letter-spacing:.06em;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.9);z-index:6}
.fol{position:absolute;bottom:64px;display:flex;align-items:center;gap:18px;font:800 26px BarlowC;letter-spacing:.18em;z-index:8}.fol i{width:120px;height:4px;background:currentColor}
.cta{font:500 calc(38px*var(--k)) BarlowC;line-height:1.3}.cta .u{text-decoration:underline;font-weight:800;color:var(--ac)}
.motto{font:italic 700 calc(56px*var(--k)) Play;color:var(--ac)}
"""
    glob = ''; out = ''; prev = False; CR = cruces(sp, S)
    for k, s in enumerate(S):
        role = s.get('role', 'cita'); p = s.get('photo'); sliver = prev
        c = RET[s.get('scheme') or ('crema' if role == 'cierre' or k % 2 == 0 else 'terra')]
        left = 250 if sliver else 90; right = 90; body = ''; ring = c.get('ring')
        if role == 'tapa':
            p = P(p)
            glob += f'<div class="col" style="left:{k*W}px;width:{W+(190 if CR[k] else 0)}px"><img src="{src(p["src"])}" style="object-position:{opos(p, .35)}"></div>'
            body += '<div class="abs" style="inset:0;z-index:3;background:linear-gradient(rgba(42,20,16,.35) 0%,rgba(42,20,16,0) 22%,rgba(42,20,16,0) 42%,rgba(42,20,16,.92) 88%)"></div>'
            inner = (f'<div class="tag">{md(s.get("tag", "ENTREVISTA"))}</div><div class="name">{md(s["name"])}</div>' + (f'<div class="p">{md(s["title"])}</div>' if s.get('title') else ''))
            body += f'<div class="fit" data-id="ret{k+1}" style="left:90px;right:90px;top:560px;bottom:130px;gap:calc(26px*var(--k));justify-content:flex-end;color:#F3E7D3;z-index:7">{inner}</div>'
            if p.get('caption'): body += f'<div class="cap" style="left:90px;bottom:70px">{md(p["caption"])}</div>'
            out += f'<div class="sl" style="left:{k*W}px;z-index:5">{body}{logo(True)}</div>'; prev = CR[k]; continue
        if p:
            p = P(p); cx = 700 if sliver else 640; right = W - cx + 50; ring = 1
            glob += f'<div class="col" style="left:{k*W+cx}px;width:{W-cx+(190 if CR[k] else 0)}px"><img src="{src(p["src"])}" style="object-position:{opos(p, .4)}"></div>'
            if p.get('caption'): body += f'<div class="cap" style="left:{cx+18}px;bottom:26px">{md(p["caption"])}</div>'
        if role == 'cita':
            inner = f'<div class="qm">“</div><div class="q" style="--ts:{s.get("title_scale", 1)}">{md(s["quote"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
            if s.get('author'): inner += f'<div class="who">{md(s["author"])}</div>'
        else:
            inner = f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
            if role == 'cierre': inner += cta_html(s) + motto(s)
        body += f'<div class="fit" data-id="ret{k+1}" style="left:{left}px;right:{right}px;top:210px;bottom:190px;gap:calc(30px*var(--k));justify-content:center;z-index:7">{inner}</div>'
        body += f'<div class="fol" style="left:{left}px">{md(sp.get("folio", "RETRATO"))} · {k+1:02d}/{n:02d}<i></i></div>'
        out += f'<div class="abs" style="left:{k*W}px;top:0;width:{W}px;height:{H}px;background:{c["bg"]};z-index:0"></div>'
        out += f'<div class="sl" style="left:{k*W}px;color:{c["ink"]};--ac:{c["ac"]};z-index:5">{body}{logo(ring)}</div>'
        prev = CR[k]
    return css, glob + out, n


# ================================================================ INVESTIGACIÓN v2 — informe técnico: fondo claro con grilla, fotos como figuras anotadas, regla al pie
# Roles: gancho/evidencia {tag,label,title,text,photo,notes:[{x,y,text}]} · ficha {title,rows,text} · cierre {title,text,tipo}
def investigacion(sp):
    S = sp['slides']; n = len(S); ink, gr = '#0B0F0A', '#93E33E'; Y0, FH = 716, 456
    css = BASE + """.sl{font-family:Rob;color:#0B0F0A}
.exp{position:absolute;left:80px;top:80px;display:flex;align-items:center;gap:18px;z-index:8;font:700 22px Mono;letter-spacing:.12em;text-transform:uppercase}.exp b{background:#0B0F0A;color:#93E33E;padding:10px 16px;font-weight:700}
.lb{align-self:flex-start;background:#0B0F0A;color:#93E33E;font:700 22px Mono;letter-spacing:.14em;text-transform:uppercase;padding:7px 12px}
.t{font:400 calc(134px*var(--k)*var(--ts,1)) Bebas;text-transform:uppercase;line-height:.92;letter-spacing:.005em}
.t mark,.p mark,.cta mark{background:#93E33E;color:#0B0F0A;padding:0 .07em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.p{font:400 calc(39px*var(--k)) Rob;line-height:1.32}
.fig{position:absolute;overflow:hidden;border:4px solid #0B0F0A;z-index:2;background:#cfd3cb}.fig img{width:100%;height:100%;object-fit:cover;filter:grayscale(.55) contrast(1.08)}
.figtab{position:absolute;background:#0B0F0A;color:#93E33E;font:700 20px Mono;letter-spacing:.12em;padding:7px 12px;z-index:4}
.cap{position:absolute;font:700 15px Mono;letter-spacing:.06em;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.9);z-index:4}
.an{position:absolute;background:#93E33E;color:#0B0F0A;font:700 20px Mono;letter-spacing:.06em;padding:5px 10px;white-space:nowrap;z-index:7;border:3px solid #0B0F0A}
.row{display:grid;grid-template-columns:1fr auto;align-items:baseline;border-top:3px solid #0B0F0A;padding:calc(10px*var(--k)) 0}.row span{font:700 calc(26px*var(--k)) Mono;letter-spacing:.08em;text-transform:uppercase}.row b{font:400 calc(96px*var(--k)) Bebas;line-height:.95}
.cta{font:400 calc(35px*var(--k)) Rob;line-height:1.35}.cta .u{text-decoration:underline;font-weight:700}
.motto{font:400 calc(60px*var(--k)) Bebas;letter-spacing:.03em;text-transform:uppercase}
"""
    ticks = ''.join(f'<line x1="{x}" y1="{1262 - (30 if (x // 54) % 5 == 0 else 14)}" x2="{x}" y2="1262" stroke="{ink}" stroke-width="2"/>' for x in range(0, n * W + 1, 54))
    glob = ('<div class="abs" style="inset:0;background:#E7E9E3"></div>'
            '<div class="abs" style="inset:0;z-index:1;background-image:linear-gradient(rgba(11,15,10,.075) 1px,transparent 1px),linear-gradient(90deg,rgba(11,15,10,.075) 1px,transparent 1px);background-size:54px 54px"></div>'
            f'<svg class="abs" style="left:0;top:0;z-index:3" width="{n*W}" height="{H}"><line x1="0" y1="1262" x2="{n*W}" y2="1262" stroke="{ink}" stroke-width="3"/>{ticks}</svg>')
    out = ''; prev = False; fi = 0; CR = cruces(sp, S)
    for k, s in enumerate(S):
        role = s.get('role', 'evidencia'); p = s.get('photo'); sliver = prev
        body = f'<div class="exp"><b>EXP. {k+1:02d}/{n:02d}</b>{md(s.get("tag", ""))}</div>'
        inner = (f'<div class="lb">{md(s["label"])}</div>' if s.get('label') else '') + f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
        if s.get('rows'): inner += '<div>' + ''.join(f'<div class="row"><span>{md(a)}</span><b>{md(b)}</b></div>' for a, b in s['rows']) + '</div>'
        if role == 'cierre': inner += cta_html(s) + motto(s)
        if p:
            p = P(p); fi += 1; x = k * W + (170 if sliver else 80)
            glob += f'<div class="fig" style="left:{x}px;top:{Y0}px;width:{(k+1)*W+(130 if CR[k] else -80)-x}px;height:{FH}px"><img src="{src(p["src"])}" style="object-position:{opos(p)}"></div>'
            glob += f'<div class="figtab" style="left:{x}px;top:{Y0}px">FIG. {fi:02d}</div>'
            if p.get('caption'): glob += f'<div class="cap" style="left:{x+20}px;top:{Y0+FH-34}px">{md(p["caption"])}</div>'
            sv = ''
            for j, a in enumerate(s.get('notes', [])):
                px, py = a['x'] * W, Y0 + a['y'] * FH; ly = Y0 - 66 - 48 * (j % 2)
                sv += f'<line x1="{px:.0f}" y1="{ly+30}" x2="{px:.0f}" y2="{py:.0f}" stroke="{ink}" stroke-width="3"/><circle cx="{px:.0f}" cy="{py:.0f}" r="11" fill="{gr}" stroke="{ink}" stroke-width="4"/>'
                body += f'<div class="an" style="left:{max(min(px-24, W-340), 80):.0f}px;top:{ly}px">{md(a["text"])}</div>'
            body += f'<svg class="abs" style="left:0;top:0;z-index:6" width="{W}" height="{H}">{sv}</svg>'
            box = f'left:80px;right:80px;top:200px;bottom:{H-Y0+ (130 if s.get("notes") else 60)}px;justify-content:flex-start'
        else:
            box = f'left:{170 if sliver else 80}px;right:80px;top:210px;bottom:200px;justify-content:center'
        body += f'<div class="fit" data-id="inv{k+1}" style="{box};gap:calc(22px*var(--k));z-index:7">{inner}</div>'
        body += f'<div class="abs" style="left:0;top:1266px;height:14px;width:{W*(k+1)//n}px;background:{gr};border-top:3px solid {ink};z-index:4"></div>'
        out += f'<div class="sl" style="left:{k*W}px;z-index:5">{body}{logo()}</div>'
        prev = CR[k]
    return css, glob + out, n


# ================================================================ CHEQUEO v2 — la frase bajo la lupa: el medidor de veredicto es la navegación
# Roles: frase {claim,who,ask} · prueba {label,title,text,source,photo} · veredicto {verdict,title,text} · cierre {title,text,tipo}
VERD = ['VERDADERO', 'DISCUTIBLE', 'ENGAÑOSO', 'FALSO']; VCOL = {'VERDADERO': '#1E9E4A', 'DISCUTIBLE': '#E5A100', 'ENGAÑOSO': '#FF5A1F', 'FALSO': '#D7261E'}


def chequeo(sp):
    S = sp['slides']; n = len(S); ink, org = '#111111', '#FF5A1F'
    vi = next((i for i, s in enumerate(S) if s.get('role') == 'veredicto'), n); verdict = S[vi]['verdict'].upper() if vi < n else None; vc = VCOL.get(verdict, org)
    css = BASE + """.sl{font-family:Arch;color:#111}
.band{position:absolute;left:0;right:0;top:0;height:110px;background:#111;color:#F3F1EC;display:flex;align-items:center;gap:22px;padding-left:80px;z-index:36}
.band b{font:900 50px Arch;font-stretch:75%;letter-spacing:.06em}.band span{font:700 24px Mono;letter-spacing:.14em;opacity:.7}
.logo{top:140px}
.qm{font:900 300px Arch;font-stretch:75%;line-height:.72;height:118px;color:#FF5A1F}
.t{font:900 calc(100px*var(--k)*var(--ts,1)) Arch;font-stretch:75%;text-transform:uppercase;line-height:.98}
.t mark,.p mark,.cta mark{background:#FF5A1F;color:#fff;padding:0 .1em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.t s{text-decoration-color:#FF5A1F;text-decoration-thickness:.1em}.t u{text-decoration-color:#FF5A1F;text-decoration-thickness:.08em;text-underline-offset:.1em}
.p{font:400 calc(41px*var(--k)) Arch;line-height:1.3}
.lb{align-self:flex-start;background:#FF5A1F;color:#fff;font:700 24px Mono;letter-spacing:.14em;text-transform:uppercase;padding:8px 14px}
.who{font:700 23px Mono;letter-spacing:.12em;text-transform:uppercase;opacity:.75}
.ask{align-self:flex-start;background:#111;color:#F3F1EC;font:900 calc(60px*var(--k)) Arch;font-stretch:75%;text-transform:uppercase;padding:4px 20px}
.fu{font:700 20px Mono;letter-spacing:.08em;text-transform:uppercase;border-top:3px solid #111;padding-top:12px;align-self:stretch}
.lens{position:absolute;border-radius:50%;border:18px solid #111;overflow:hidden;z-index:3;background:#ddd}.lens img{width:100%;height:100%;object-fit:cover}
.cap{position:absolute;font:700 15px Mono;letter-spacing:.06em;z-index:6;opacity:.65}
.stamp{align-self:center;border:12px solid var(--vc);color:var(--vc);font:900 calc(150px*var(--k)) Arch;font-stretch:70%;line-height:1;padding:10px 40px 0;transform:rotate(-7deg);margin:20px 0 30px}
.meter{position:absolute;left:80px;right:80px;bottom:52px;z-index:8}.meter .g{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.meter i{height:24px;background:rgba(17,17,17,.14)}.meter em{font:700 18px Mono;font-style:normal;letter-spacing:.04em;opacity:.45}
.cta{font:400 calc(35px*var(--k)) Arch;line-height:1.35}.cta .u{color:#FF5A1F;text-decoration:underline;font-weight:800}
.motto{font:900 calc(50px*var(--k)) Arch;font-stretch:75%;text-transform:uppercase;letter-spacing:.03em;color:#FF5A1F}
"""
    glob = '<div class="abs" style="inset:0;background:#F3F1EC"></div>'; out = ''; prev = False; CR = cruces(sp, S)
    for k, s in enumerate(S):
        role = s.get('role', 'prueba'); p = s.get('photo'); sliver = prev
        body = f'<div class="band"><b>{md(sp.get("band", "CHEQUEO LR"))}</b><span>{k+1:02d}/{n:02d}</span></div>'
        if role == 'frase':
            inner = (f'<div class="qm">“</div><div class="t" style="--ts:{s.get("title_scale", 1.08)}">{md(s["claim"])}</div>' + (f'<div class="who">{md(s["who"])}</div>' if s.get('who') else '')
                     + f'<div class="ask">{md(s.get("ask", "¿Es así?"))}</div>')
        elif role == 'veredicto':
            inner = f'<div class="stamp">{md(verdict)}</div>' + (f'<div class="t" style="--ts:.7">{md(s["title"])}</div>' if s.get('title') else '') + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
        else:
            inner = ((f'<div class="lb">{md(s["label"])}</div>' if s.get('label') else '') + f'<div class="t" style="--ts:{s.get("title_scale", .86 if role == "prueba" else 1)}">{md(s["title"])}</div>'
                     + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '') + (f'<div class="fu">{md(s["source"])}</div>' if s.get('source') else ''))
            if role == 'cierre': inner += cta_html(s) + motto(s)
        if p:
            p = P(p); R = 232; cx, cy = k * W + (950 if CR[k] else 760), 930; a = R * .7071
            glob += (f'<svg class="abs" style="left:0;top:0;z-index:2" width="{n*W}" height="{H}"><line x1="{cx-a:.0f}" y1="{cy+a:.0f}" x2="{cx-a-112:.0f}" y2="{cy+a+112:.0f}" stroke="{ink}" stroke-width="36" stroke-linecap="round"/></svg>'
                     f'<div class="lens" style="left:{cx-R}px;top:{cy-R}px;width:{2*R}px;height:{2*R}px"><img src="{src(p["src"])}" style="object-position:{opos(p)}"></div>')
            if p.get('caption'): body += f'<div class="cap" style="left:{190 if sliver else 80}px;top:{cy+R-44}px">{md(p["caption"])}</div>'
            box = f'left:80px;right:80px;top:290px;bottom:{H-(cy-R)+36}px;justify-content:flex-start'
        else:
            box = f'left:{190 if sliver else 80}px;right:80px;top:290px;bottom:200px;justify-content:center' + (';align-items:center;text-align:center' if role == 'veredicto' else '')
        body += f'<div class="fit" data-id="cheq{k+1}" style="{box};gap:calc(24px*var(--k));z-index:7;--vc:{vc}">{inner}</div>'
        on = k >= vi
        segs = ''.join(f'<i style="{("background:" + vc) if on and v == verdict else ""}"></i>' for v in VERD)
        labs = ''.join(f'<em style="{("opacity:1;color:" + vc) if on and v == verdict else ""}">{v}</em>' for v in VERD)
        head = '' if on else f'<div class="who" style="margin-bottom:10px;opacity:1;display:flex;justify-content:space-between"><span>EN REVISIÓN</span><span>{"●" * (k+1)}{"○" * (vi-k-1)}</span></div>'
        body += f'<div class="meter">{head}<div class="g">{segs}</div><div class="g" style="margin-top:8px">{labs}</div></div>'
        out += f'<div class="sl" style="left:{k*W}px;z-index:5">{body}{logo()}</div>'
        prev = CR[k]
    return css, glob + out, n


# ================================================================ FINDE v2 — afiche y entradas: una placa por día, guirnalda continua, polaroid que cruza
# Roles: gancho {tag,title,text,photo,sticker} · dia {day,tag,title,text,chips,photo,sticker} · cierre {title,text,cta}
FPAL = ['#FFD43B', '#FF8FB1', '#7FD3F7', '#9BE7A8', '#FF9F5A']


def finde(sp):
    S = sp['slides']; n = len(S); ink = '#042326'; rnd = random.Random(sp.get('seed', 5))
    bgs = [s.get('bg') or (FPAL[4] if s.get('role') == 'cierre' else FPAL[k % 4]) for k, s in enumerate(S)]
    css = BASE + """.sl{font-family:Arch;font-weight:500;color:#042326}
.pill{align-self:flex-start;background:#042326;border-radius:999px;font:700 28px Fred;letter-spacing:.08em;text-transform:uppercase;padding:12px 26px}
.t{font:700 calc(100px*var(--k)*var(--ts,1)) Fred;text-transform:uppercase;line-height:1.05}
.t mark{background:#fff;color:#042326;border-radius:14px;padding:0 .14em;box-shadow:7px 7px 0 #042326;margin-right:.08em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.p{font:500 calc(38px*var(--k)) Arch;line-height:1.3}
.day{position:absolute;left:40px;top:214px;font:700 258px Fred;line-height:.82;color:#fff;-webkit-text-stroke:6px #042326;paint-order:stroke fill;text-shadow:11px 11px 0 #042326;transform:rotate(-6deg);transform-origin:left top;z-index:6}
.tk{background:#fff;border:4px solid #042326;border-radius:28px;box-shadow:11px 11px 0 #042326;padding:42px 48px 34px}
.tk .t{font-size:calc(74px*var(--k)*var(--ts,1))}.tk .t mark{background:var(--bg);box-shadow:none;border-radius:12px}
.stub{position:relative;border-top:4px dashed #042326;margin-top:auto;padding-top:22px;display:flex;flex-wrap:wrap;gap:12px}
.stub::before,.stub::after{content:'';position:absolute;top:-24px;width:44px;height:44px;border-radius:50%;background:var(--bg)}.stub::before{left:-74px}.stub::after{right:-74px}
.stub span{border:3px solid #042326;border-radius:999px;padding:6px 20px;font:700 calc(30px*var(--k)) Fred;text-transform:uppercase}
.pol{position:absolute;background:#fff;padding:16px 16px 58px;border-radius:6px;box-shadow:10px 10px 0 #042326;z-index:3}.pol img{display:block;width:100%;height:100%;object-fit:cover;filter:saturate(1.1)}
.tape{position:absolute;width:160px;height:44px;background:rgba(255,255,255,.78);z-index:4}
.cap{position:absolute;left:18px;bottom:20px;font:700 14px Mono;letter-spacing:.05em;opacity:.8}
.stk{position:absolute;z-index:20;display:grid;place-items:center;text-align:center;font:700 34px/1 Fred;text-transform:uppercase;color:#042326}
.cta{font:500 calc(36px*var(--k)) Arch;line-height:1.35}.cta .u{text-decoration:underline;font-weight:800}
.motto{font:700 calc(50px*var(--k)) Fred;text-transform:uppercase}
.nav{position:absolute;left:70px;bottom:56px;z-index:35;display:flex;align-items:center;gap:16px;background:#fff;border:3px solid #042326;border-radius:14px;padding:10px 22px;box-shadow:5px 5px 0 #042326;transform:rotate(-1.5deg)}
"""
    glob = ''
    for k in range(n): glob += f'<div class="abs" style="left:{k*W}px;top:0;width:{W}px;height:{H}px;background:{bgs[k]};z-index:0"></div>'
    g = f'<svg class="abs" style="left:0;top:0;z-index:33" width="{n*W}" height="150">'
    for k in range(n):
        p0, p1, p2 = (k * W, 8), (k * W + W / 2, 100), ((k + 1) * W, 8); cols = [c for c in FPAL + ['#FFFFFF', ink] if c != bgs[k]]
        g += f'<path d="M{p0[0]} {p0[1]} Q{p1[0]} {p1[1]} {p2[0]} {p2[1]}" fill="none" stroke="{ink}" stroke-width="3"/>'
        for i in range(17):
            t = (i + .5) / 17; x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]; y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
            if W - 200 < x - k * W < W - 40: continue
            g += f'<path d="M{x-24:.0f} {y:.0f} L{x+24:.0f} {y:.0f} L{x:.0f} {y+48:.0f} Z" fill="{cols[(i + k) % len(cols)]}" stroke="{ink}" stroke-width="2.5" stroke-linejoin="round"/>'
    glob += g + '</svg>'
    out = ''; CR = cruces(sp, S)
    for k, s in enumerate(S):
        role = s.get('role', 'dia'); p = s.get('photo'); bg = bgs[k]; body = ''
        cols = [c for c in FPAL + ['#FFFFFF'] if c != bg]; conf = ''
        for j in range(12):
            x = rnd.uniform(10, 58) if j % 2 else rnd.uniform(W - 58, W - 10); y = rnd.uniform(650, 1180); c = rnd.choice(cols); rot = rnd.randint(0, 180)
            conf += (f'<rect x="{x:.0f}" y="{y:.0f}" width="22" height="9" rx="3" fill="{c}" stroke="{ink}" stroke-width="2" transform="rotate({rot} {x:.0f} {y:.0f})"/>' if j % 3 else f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{c}" stroke="{ink}" stroke-width="2"/>')
        body += f'<svg class="abs" style="left:0;top:0;z-index:1" width="{W}" height="{H}">{conf}</svg>'
        if p:
            p = P(p); big = role == 'gancho'; pw, ph = p.get('w', 700 if big else 530), p.get('h', 500 if big else 430); x = k * W + W + (130 if CR[k] else -70) - pw; y = 208; rot = 3.5 if k % 2 == 0 else -3
            glob += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{pw}px;height:{ph}px;transform:rotate({rot}deg);z-index:3"><div class="pol" style="inset:0"><img src="{src(p["src"])}" style="object-position:{opos(p)}">'
                     + (f'<div class="cap">{md(p["caption"])}</div>' if p.get('caption') else '') + f'</div><div class="tape" style="left:{(pw-(130 if CR[k] else 0))//2-80}px;top:-20px;transform:rotate({-rot*1.5}deg)"></div></div>')
        pill = f'<div class="pill" style="color:{bg};transform:rotate(-2.5deg)">{md(s["tag"])}</div>' if s.get('tag') else ''
        if role == 'dia':
            body += f'<div class="day">{md(s["day"])}</div>'
            inner = pill + f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
            inner += '<div class="stub">' + ''.join(f'<span>{md(c)}</span>' for c in s.get('chips', [])) + '</div>'
            body += f'<div class="fit tk" data-id="finde{k+1}" style="left:80px;right:90px;top:670px;bottom:176px;gap:calc(18px*var(--k));--bg:{bg};transform:rotate({1.2 if k % 2 else -1.2}deg);z-index:7">{inner}</div>'
        else:
            inner = f'<div class="t" style="--ts:{s.get("title_scale", 1)}">{md(s["title"])}</div>' + (f'<div class="p">{md(s["text"])}</div>' if s.get('text') else '')
            if role == 'cierre': inner += cta_html(s) + motto(s)
            if role == 'gancho' and pill: body += f'<div class="abs" style="left:80px;top:250px;z-index:8;display:flex">{pill}</div>'
            top = 770 if p else (300 if role == 'cierre' else 250)
            body += f'<div class="fit" data-id="finde{k+1}" style="left:80px;right:80px;top:{top}px;bottom:180px;gap:calc(26px*var(--k));justify-content:center;z-index:7' + (';align-items:center;text-align:center' if role == 'cierre' else '') + f'">{inner}</div>'
        dots = ''.join(f'<i style="display:inline-block;width:{22 if j == k else 12}px;height:12px;border-radius:999px;margin-left:6px;background:{ink if j <= k else "transparent"};border:2px solid {ink}"></i>' for j in range(n))
        body += (f'<div class="nav"><b style="font:700 26px Fred;letter-spacing:.1em">{md(sp.get("nav", "VIERNES"))} · {k+1:02d}/{n:02d}</b><span style="border-left:3px dashed {ink};height:30px"></span><span>{dots}</span></div>'
                 + (f'<div class="abs" style="right:80px;bottom:62px;z-index:35;font:700 30px Fred;letter-spacing:.06em">DESLIZÁ →</div>' if k == 0 else ''))
        out += f'<div class="sl" style="left:{k*W}px;z-index:5">{body}{sticker(s.get("sticker"))}{logo()}</div>'
    return css, glob + out, n


FORMATS = {'dato': dato, 'explicador': explicador, 'caso': caso, 'retrato': retrato, 'investigacion': investigacion, 'historias': historias, 'chequeo': chequeo, 'panorama': panorama, 'finde': finde}


def build(sp):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import zipfile
    out = sp.get('out', 'out'); pre = sp.get('prefix', 'LR'); os.makedirs(out + '/.html', exist_ok=True)
    css, body, n = FORMATS[sp['format']](sp)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}html,body{{width:{n*W}px}}</style></head><body>'
            f'<div class="strip" style="width:{n*W}px">{body}<div class="grain"></div></div>{FITJS}</body></html>')
    f = os.path.abspath(f'{out}/.html/strip.html'); open(f, 'w').write(page)
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={'width': n * W, 'height': H})
        pg.on('console', lambda m: print('  ⚠', m.text, '— conviene recortar copy') if 'SHRINK' in m.text else None)
        pg.goto('file://' + f); pg.wait_for_function('window.__done===1'); pg.wait_for_timeout(300); full = f'{out}/{pre}_tira.png'; pg.screenshot(path=full); br.close()
    im = Image.open(full).convert('RGB'); files = []
    for k in range(n):
        o = f'{out}/{pre}_{k+1:02d}.png'; im.crop((k * W, 0, (k + 1) * W, H)).save(o); files.append(o)
    with zipfile.ZipFile(f'{out}/{pre}_carrusel.zip', 'w') as z:
        for o in files: z.write(o, os.path.basename(o))
    w = 300; S = Image.new('RGB', (n * (w + 10), H * w // W), (120, 120, 120))
    for c, o in enumerate(files): S.paste(Image.open(o).resize((w, H * w // W)), (c * (w + 10), 0))
    S.save(f'{out}/_preview.png'); print('OK', out, n, 'placas')


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])))
