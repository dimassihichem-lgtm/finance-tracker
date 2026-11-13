"""Autotest et annulation (↶ ↷) :
- l'Autotest ne touche ni la copie locale, ni le cloud, ni l'historique ;
- ↶ demande confirmation si l'état visé contient moins de données ;
- l'historique repart de zéro quand une version arrive du cloud.
Usage : python3 annulation.py"""
from commun import ouvrir, lancer

JS = r"""
async()=>{const out={};const wait=ms=>new Promise(r=>setTimeout(r,ms));
DB=defDB();ensure();DB.im=[{y:2026,m:10,supports:[{n:'PEA',v:64000,det:[]}],contribs:[]}];DB.bm=[Object.assign(defBM(2026,10),{cashFin:8000,cl:true})];DB._marque='BASE DE DÉPART';
localStorage.setItem('hft7',JSON.stringify(DB));postLoad();
let acces=0;const fdb0=fdb;fdb=new Proxy({},{get(){acces++;return()=>{throw new Error('cloud touché')}}});CLOUD_READ=true;
const copie=localStorage.getItem('hft7');const res=runSelfTests();await wait(3000);
out.autotests=res.filter(r=>r.ok).length+'/'+res.length;out.acces_cloud_pendant_autotest=acces;out.copie_locale_intacte=localStorage.getItem('hft7')===copie;fdb=fdb0;CLOUD_READ=false;
DB.gn='a';save();DB.gn='b';save();await undo();out.annuler=DB.gn==='a'&&DB._marque==='BASE DE DÉPART';await redo();out.retablir=DB.gn==='b';
const pauvre=JSON.parse(JSON.stringify(DB));pauvre.im=[];pauvre._marque='PAUVRE';HIST.push(JSON.stringify(pauvre));
let n=0,rep=false;const uc=uiConfirm;uiConfirm=async(t,o)=>{n++;return rep};
await undo();out.refus_garde_la_base=DB._marque==='BASE DE DÉPART'&&n===1&&HIST.length>0;
rep=true;await undo();out.accord_applique=DB._marque==='PAUVRE'&&n===2;await redo();out.retour_par_retablir=DB._marque==='BASE DE DÉPART';uiConfirm=uc;
DB.gn='c';save();const h=HIST.length;const c=JSON.parse(JSON.stringify(DB));c._rev=99;c.gn='cloud';applyCloud(c,'essai');out.historique_avant_cloud=h;out.historique_apres_cloud=HIST.length;
out.verdict=(out.acces_cloud_pendant_autotest===0&&out.copie_locale_intacte&&out.annuler&&out.retablir&&out.refus_garde_la_base&&out.accord_applique&&out.retour_par_retablir&&out.historique_apres_cloud===0)?'OK':'À REGARDER';
return JSON.stringify(out,null,1)}
"""


async def main():
    async with ouvrir(semer=False) as (pg, erreurs):
        await pg.wait_for_timeout(800)
        print(await pg.evaluate(JS)); print('erreurs de page :', erreurs)

lancer(main())
