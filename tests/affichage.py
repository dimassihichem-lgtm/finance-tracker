"""Mesures d'affichage, vue par vue : débordements, textes coupés, textes sous 11 px,
nombre de tailles et de polices, zones tactiles trop petites, contrastes sous 4,5:1, hauteur des pages.

Usage :
  python3 affichage.py                         base fictive, 375 / 390 / 1440 px, thèmes sombre et clair
  python3 affichage.py --largeurs 390 --themes light --detail
  python3 affichage.py --base /chemin/export.json     sur un export local (ne jamais le copier ici)
  python3 affichage.py --json mesures.json            enregistre les mesures
  python3 affichage.py --ref mesures.json             compare à des mesures enregistrées
"""
import json, sys
from commun import ouvrir, lancer, option, VUES

MESURE = r"""
(sel)=>{const RAC=sel?document.querySelector(sel):document.body;const W=innerWidth,o={hauteur:sel?RAC.scrollHeight:document.documentElement.scrollHeight,defile:document.documentElement.scrollWidth>W+1,sort:[],coupe:[],coupeH:[],tronque:0,textes:0,petits:0,tailles:{},polices:{},cibles:0,c32:0,c44:0,ex32:{},contrasteBas:0,paires:{}};
const vis=e=>e.checkVisibility?e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}):!!e.offsetParent;
const nom=e=>{let s=e.tagName.toLowerCase();if(e.id)s+='#'+e.id;const c=(e.getAttribute('class')||'').trim().split(/\s+/).filter(Boolean).slice(0,2).join('.');if(c)s+='.'+c;return s};
const txt=e=>(e.textContent||'').replace(/\s+/g,' ').trim().slice(0,46);
const dansDefilant=e=>{for(let p=e.parentElement;p;p=p.parentElement){const s=getComputedStyle(p);if(/(auto|scroll)/.test(s.overflowX)&&p.scrollWidth>p.clientWidth+1)return true}return false};
const rgb=s=>{const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(/[,\s\/]+/).filter(Boolean).map(Number);return{r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}};
const sur=(h,b)=>({r:h.r*h.a+b.r*(1-h.a),g:h.g*h.a+b.g*(1-h.a),b:h.b*h.a+b.b*(1-h.a),a:1});
const lum=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)};
const fond=e=>{const pile=[];let grad=false;for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);if(s.backgroundImage&&s.backgroundImage!=='none')grad=true;const c=rgb(s.backgroundColor);if(c&&c.a>0){pile.push(c);if(c.a>=1)break}}
 let b={r:255,g:255,b:255,a:1};for(let i=pile.length-1;i>=0;i--)b=sur(pile[i],b);return{b,grad}};
const hex=c=>'#'+[c.r,c.g,c.b].map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
// textes
const tw=document.createTreeWalker(RAC,NodeFilter.SHOW_TEXT);const vus=new Set();
for(let n=tw.nextNode();n;n=tw.nextNode()){if(!n.nodeValue.trim())continue;const e=n.parentElement;if(!e||/^(SCRIPT|STYLE|OPTION|TEXTAREA)$/.test(e.tagName)||!vis(e))continue;const r=e.getBoundingClientRect();if(r.width<1||r.height<1)continue;
 const s=getComputedStyle(e);const fs=parseFloat(s.fontSize);o.textes++;if(fs<10.99)o.petits++;const k=String(Math.round(fs*10)/10);o.tailles[k]=(o.tailles[k]||0)+1;const pf=s.fontFamily.split(',')[0].replace(/['"]/g,'').trim();o.polices[pf]=(o.polices[pf]||0)+1;
 if(vus.has(e))continue;vus.add(e);
 const f=fond(e);if(!f.grad){let c=rgb(s.color);if(c){let op=1;for(let p=e;p;p=p.parentElement){op*=parseFloat(getComputedStyle(p).opacity)}c=sur({r:c.r,g:c.g,b:c.b,a:c.a*op},f.b);const l1=lum(c),l2=lum(f.b);const ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);const grand=fs>=24||(fs>=18.66&&parseInt(s.fontWeight)>=700);if(ratio<(grand?3:4.5)){o.contrasteBas++;const kk=hex(c)+' sur '+hex(f.b)+' ('+ratio.toFixed(1)+')';o.paires[kk]=(o.paires[kk]||0)+1}}}
 if(!dansDefilant(e)&&(r.right>W+1||r.left<-1)&&o.sort.length<40)o.sort.push(nom(e)+' « '+txt(e)+' » '+Math.round(r.left)+'→'+Math.round(r.right));
 if(e.scrollWidth>e.clientWidth+1&&/(hidden|clip)/.test(s.overflowX)){if(s.textOverflow==='ellipsis')o.tronque++;else if(o.coupe.length<40)o.coupe.push(nom(e)+' « '+txt(e)+' » '+e.clientWidth+'<'+e.scrollWidth)}
 if(e.scrollHeight>e.clientHeight+2&&/(hidden|clip)/.test(s.overflowY)&&e.clientHeight>0&&o.coupeH.length<40)o.coupeH.push(nom(e)+' « '+txt(e)+' » h'+e.clientHeight+'<'+e.scrollHeight)}
// zones tactiles
RAC.querySelectorAll('button,a[href],[onclick],input:not([type=hidden]),select,textarea,[role=button],summary').forEach(e=>{if(!vis(e))return;if(/^(checkbox|radio)$/.test(e.type||'')&&e.closest('label'))return;const r=e.getBoundingClientRect();if(r.width<1||r.height<1)return;o.cibles++;const m=Math.min(r.width,r.height);if(m<31.5){o.c32++;const k=nom(e).replace(/#[\w-]+/,'');o.ex32[k]=(o.ex32[k]||0)+1}else if(m<43.5)o.c44++});
return o}
"""
ALLER = "(c)=>{(0,eval)(c);return true}"
ASSISTANT = "(i)=>{if(i===0)wizStart();if(i>=WZ.steps.length){WZ.on=false;document.getElementById('wiz').classList.remove('on');return false}WZ.step=i;wizRender();return true}"


def cumul(tot, m):
    for k in ('textes', 'petits', 'cibles', 'c32', 'c44', 'contrasteBas', 'tronque', 'hauteur'):
        tot[k] = tot.get(k, 0) + m[k]
    for k in ('tailles', 'polices', 'paires', 'ex32'):
        d = tot.setdefault(k, {})
        for a, b in m[k].items():
            d[a] = d.get(a, 0) + b
    for k in ('sort', 'coupe', 'coupeH'):
        tot[k] = tot.get(k, 0) + len(m[k])
    tot['defile'] = tot.get('defile', 0) + (1 if m['defile'] else 0)


async def passe(largeur, theme, base, detail):
    mobile = largeur < 700
    res = {}
    async with ouvrir(largeur=largeur, hauteur=844 if mobile else 900, horloge='2026-11-14T10:00:00', base=base, theme=theme) as (pg, erreurs):
        for nom, code in VUES:
            await pg.evaluate(ALLER, code); await pg.wait_for_timeout(250)
            res[nom] = await pg.evaluate(MESURE, None)
        i = 0
        while await pg.evaluate(ASSISTANT, i):
            await pg.wait_for_timeout(150)
            res['assistant/%d' % i] = await pg.evaluate(MESURE, '#wiz'); i += 1
        res['_erreurs'] = erreurs
    return res


def resume(cle, res, detail, ref=None):
    tot = {}
    for nom, m in res.items():
        if nom != '_erreurs':
            cumul(tot, m)
    t = tot
    print(f"\n===== {cle} · {len(res) - 1} vues · erreurs de page : {res['_erreurs'][:3]}")
    print(f"  textes {t['textes']} · sous 11 px {t['petits']} ({100 * t['petits'] / max(1, t['textes']):.0f} %) · tailles {len(t['tailles'])} · polices {dict(sorted(t['polices'].items(), key=lambda x: -x[1]))}")
    print(f"  zones tactiles {t['cibles']} · sous 32 px {t['c32']} · de 32 à 44 px {t['c44']}")
    print(f"  contraste insuffisant {t['contrasteBas']} · défilement horizontal {t['defile']} vue(s) · éléments qui sortent {t['sort']} · textes coupés {t['coupe']} (hauteur {t['coupeH']}) · textes abrégés « … » {t['tronque']}")
    print(f"  hauteur cumulée des pages {t['hauteur']} px")
    if ref and cle in ref:
        r = {}
        for nom, m in ref[cle].items():
            if nom != '_erreurs':
                cumul(r, m)
        print(f"  par rapport à la référence : hauteur {100 * (t['hauteur'] - r['hauteur']) / max(1, r['hauteur']):+.1f} % · sous 11 px {r['petits']} → {t['petits']} · sous 32 px {r['c32']} → {t['c32']} · contraste {r['contrasteBas']} → {t['contrasteBas']} · qui sortent {r['sort']} → {t['sort']} · coupés {r['coupe']} → {t['coupe']} · coupés en hauteur {r['coupeH']} → {t['coupeH']} · abrégés {r['tronque']} → {t['tronque']}")
        for nom, m in res.items():
            if nom == '_erreurs' or nom not in ref[cle]:
                continue
            a = ref[cle][nom]
            neufs = [x for k in ('sort', 'coupe', 'coupeH') for x in m[k] if x.split(' « ')[0] not in {y.split(' « ')[0] for y in a[k]}]
            if neufs or (m['defile'] and not a['defile']):
                print(f"   NOUVEAU dans {nom} : défilement {m['defile']} ·", neufs[:6])
    if detail:
        print('  tailles :', dict(sorted(t['tailles'].items(), key=lambda x: float(x[0]))))
        print('  contrastes les plus fréquents :', sorted(t['paires'].items(), key=lambda x: -x[1])[:12])
        print('  petites zones tactiles :', sorted(t['ex32'].items(), key=lambda x: -x[1])[:25])
        for nom, m in res.items():
            if nom == '_erreurs':
                continue
            if m['defile'] or m['sort'] or m['coupe'] or m['coupeH']:
                print(f"  — {nom} : défilement {m['defile']}")
                for k in ('sort', 'coupe', 'coupeH'):
                    for x in m[k][:8]:
                        print(f"       {k} : {x}")


async def main():
    largeurs = [int(x) for x in option('--largeurs', '375,390,1440').split(',')]
    themes = option('--themes', 'dark,light').split(',')
    base = option('--base'); detail = '--detail' in sys.argv
    ref = json.load(open(option('--ref'), encoding='utf-8')) if option('--ref') else None
    tout = {}
    for th in themes:
        for w in largeurs:
            cle = f"{w} px · {th}"
            tout[cle] = await passe(w, th, base, detail)
            resume(cle, tout[cle], detail, ref)
    if option('--json'):
        json.dump(tout, open(option('--json'), 'w', encoding='utf-8'), ensure_ascii=False)

lancer(main())
