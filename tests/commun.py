"""Outils communs aux scripts de contrôle de l'application Patrimoine.

Le dépôt est public : tout ce qui se trouve dans ce dossier est fictif.
Ne jamais y copier un export, un bulletin, un nom ou un montant réel.
"""
import os, sys, json, asyncio
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(os.environ.get('APP') or os.path.join(ICI, '..', 'index.html'))
CODE = '0000'  # code d'accès de la base fictive


def chrome():
    """Chemin du navigateur : variable CHROME, sinon Chrome installé, sinon celui de Playwright."""
    c = os.environ.get('CHROME')
    if c:
        return c
    for p in ('/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'):
        if os.path.exists(p):
            return p
    return None


def option(nom, defaut=None):
    """Lit « --nom valeur » sur la ligne de commande."""
    a = sys.argv
    return a[a.index(nom) + 1] if nom in a and a.index(nom) + 1 < len(a) else defaut


# Base fictive : d'avril 2026 au mois o.last ; tous les mois clos sauf le dernier
# (ouvert, relevé partiel, pas de soldes). Libellés longs exprès, pour les contrôles d'affichage.
SEED = r"""
(o)=>{
DB=defDB();ensure();DB.params.v2From='2026-04';DB.params.cibleprecaution=10000;
DB.params.cap={label:'Test',to:'2046-02',cibles:[{l:'Cible',v:900000}]};
DB.params.proj.salaire=5000;DB.params.proj.aides=[{l:'Allocations familiales',v:150,from:'2026-01',to:''}];
DB.params.proj.ponctuels=[{l:'Participation et intéressement',mois:8,v:9000}];
DB.params.proj.depPonctuels=[{l:'Vacances été',v:3000,mois:8,an:2026,rec:true,id:'pvac'},{l:'Noël',v:800,mois:12,an:2026,rec:true,id:'pnoel'}];
const S=(a,b)=>[{n:'PEA',v:a,det:[]},{n:'PEE Fonds',v:b,det:[]}];DB.bm=[];DB.im=[];
const CH=()=>[{l:'Loyer',v:1000,fixe:true},{l:'Assurance habitation et responsabilité civile',v:38.5,fixe:true},{l:'Courses',v:2000}];
const mkImp=(y,m,full)=>({done:true,at:(full?dayKeyOf(new Date(y,m,2)):ym(y,m)+'-13')+'T10:00:00.000Z',t:{fixe:1000,variable:2000,invest:200,salaire:5000,entree:0,foyerOut:0,foyerIn:0},bySub:{fixe:{},variable:{},entree:{},transfertFoyer:{}},byGrp:{},unmatched:[],salaireCount:1,internesOut:0,livretOut:0,livretIn:0,entrees:[],
 lines:[{d:ym(y,m)+'-05',l:'CB MAGASIN DU CENTRE COMMERCIAL REGIONAL',v:-2000,t:'variable',s:'Courses'},{d:ym(y,m)+(full?'-28':'-12'),l:'PRLV LOYER',v:-1000,t:'fixe',s:'Loyer'}],ccEndDate:ym(y,m)+(full?'-28':'-12'),consoCsv:3000});
let y=2026,m=3,cc=6000,i=0;const end=o.last[0]*12+o.last[1];
DB.bm.push(Object.assign(defBM(2026,3),{ch:CH(),cash:{cc:6000,la:2000,ldds:0},cashFin:8000,cl:true}));DB.im.push({y:2026,m:3,supports:S(20000,10000),contribs:[{l:'PEA mensuel',v:200}],cl:true});
while(true){m++;if(m>12){m=1;y++}if(y*12+m>end)break;i++;const last=y*12+m===end;cc+=1800;
 const b=Object.assign(defBM(y,m),{ch:CH(),entrees:[{cat:'salaire',v:5000,l:'SALAIRE'}]});
 b.imp=mkImp(y,m,!last);if(!last){b.cash={cc,la:2000,ldds:0};b.cashFin=cc+2000;b.cl=true;b.closedAt=ym(y,m)+'-28'}
 DB.bm.push(b);DB.im.push({y,m,supports:last?S(0,0):S(20000+i*300,10000+i*100),contribs:[{l:'PEA mensuel',v:200}],cl:!last})}
if(o.code)pinSet(o.code);
DB._marque='BASE FICTIVE';localStorage.setItem('hft7',JSON.stringify(DB));return DB.bm.length+' mois'}
"""

# Déverrouillage par le clavier de l'écran de code (base fictive).
UNLOCK = "(c)=>{c.split('').forEach(k=>pp(k));return document.getElementById('app').style.display}"
# Ouverture sans code (export local dont on ne connaît pas le code).
OUVRIR_SANS_CODE = "()=>{document.getElementById('lock').style.display='none';document.getElementById('app').style.display='block';APP_INIT=true;initApp();return true}"

# Toutes les vues de l'application, dans l'ordre. Chaque entrée : [nom, code qui l'affiche].
VUES = [
    ['accueil', "go('home')"], ['budget', "go('budget')"], ['invest', "go('invest')"], ['garde', "go('garde')"],
] + [['plus/' + s, "PG='more';go('more');SUB='%s';rMore()" % s] for s in
     ['hub', 'fiscal', 'proj', 'cap', 'recur', 'decis', 'analyses', 'notes', 'gouv', 'rules', 'perso', 'donnees', 'config', 'guide', 'import', 'poches']]


def _servir(corps, genre):
    async def f(route):
        await route.fulfill(status=200, content_type=genre, body=corps, headers={'access-control-allow-origin': '*'})
    return f


@asynccontextmanager
async def ouvrir(largeur=430, hauteur=900, horloge=None, dernier=(2026, 11), base=None, echelle=1, theme=None, accent=None, semer=True):
    """Ouvre l'application hors réseau sur la base fictive (ou sur un export local : base=chemin).

    Rend (page, erreurs). Le réseau est coupé : seuls les fichiers locaux sont lus.
    """
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome(), args=['--no-sandbox'])
        mobile = largeur < 700  # téléphone : écran tactile, comme sur l'appareil
        ctx = await b.new_context(viewport={'width': largeur, 'height': hauteur}, device_scale_factor=echelle, has_touch=mobile, is_mobile=mobile)
        pg = await ctx.new_page()
        erreurs = []
        pg.on('pageerror', lambda e: erreurs.append(str(e)[:300]))
        await pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
        # Modules externes servis depuis des copies locales, si on en fournit :
        #   LOCAL='**/chart.umd.min.js=/chemin/chart.umd.js;**/css2*=/chemin/polices.css'
        for regle in filter(None, (os.environ.get('LOCAL') or '').split(';')):
            motif, chemin = regle.split('=', 1)
            corps = open(chemin, 'rb').read()
            genre = 'text/css' if chemin.endswith('.css') else 'application/javascript'
            await pg.route(motif, _servir(corps, genre))
        if horloge:
            await pg.clock.set_fixed_time(horloge)
        await pg.goto('file://' + APP)
        await pg.wait_for_timeout(500)
        if semer:
            if base:
                brut = open(base, encoding='utf-8').read()
                await pg.evaluate("(raw)=>{localStorage.setItem('hft7',raw)}", brut)
            else:
                await pg.evaluate(SEED, {'last': list(dernier), 'code': CODE})
            if theme or accent:
                await pg.evaluate("(o)=>{if(o.t)localStorage.setItem('hft7_theme',o.t);if(o.a)localStorage.setItem('hft7_accent',o.a)}", {'t': theme, 'a': accent})
            await pg.reload()
            await pg.wait_for_timeout(900)
            if base:
                await pg.evaluate(OUVRIR_SANS_CODE)
            else:
                await pg.evaluate(UNLOCK, CODE)
            await pg.wait_for_timeout(700)
        try:
            yield pg, erreurs
        finally:
            await b.close()


def lancer(coro):
    asyncio.run(coro)


def dire(titre, objet):
    print(titre, json.dumps(objet, ensure_ascii=False, indent=1) if not isinstance(objet, str) else objet)
