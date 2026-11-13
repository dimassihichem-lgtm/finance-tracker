"""Clôture automatique des mois : vérifie les conditions qui la retiennent
(cloud pas encore lu, conflit, assistant ouvert) puis la clôture normale et la protection de ↶.
Le cloud est simulé : rien ne sort de la machine.
Usage : python3 cloture.py"""
from commun import ouvrir, lancer

JS = r"""
async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));const out={};
let n=0;const mk=()=>new Proxy(function(){},{get(t,k){if(k==='then')return undefined;n++;return mk()},apply(){return mk()}});
const fdb0=fdb;fdb=mk();CLOUD_READ=true;
DB.bm=DB.bm.filter(b=>!(b.y===2026&&b.m===12));DB.im=DB.im.filter(b=>!(b.y===2026&&b.m===12));n=0;autoTick();await wait(300);
out.creation_silencieuse={decembre_recree:!!gBM(2026,12)&&!!gIM(2026,12),acces_cloud:n};
CLOUD_READ=false;const b=gBM(2026,11);b.imp.at='2026-12-01T09:00:00.000Z';b.imp.ccEndDate='2026-11-28';b.imp.lines[1].d='2026-11-28';b.cash={cc:20400,la:2000,ldds:0};b.cashFin=22400;const im=gIM(2026,11);im.supports[0].v=22500;im.supports[1].v=10900;GM_CACHE={};
autoTick();out.cloud_non_lu={clos:!!b.cl,pret:autoCloseCheck(2026,11).ok};
CLOUD_READ=true;SYNC_CONFLICT={_rev:99};autoTick();out.conflit_en_cours={clos:!!b.cl};SYNC_CONFLICT=null;
WZ.on=true;autoTick();out.assistant_ouvert={clos:!!b.cl};WZ.on=false;
autoTick();out.tout_en_ordre={clos:!!b.cl,automatique:!!b.closedAuto};
let q='';const uc=uiConfirm;uiConfirm=async(t,o)=>{q=o.desc;return false};await undo();uiConfirm=uc;out.annulation={question_posee:q.length>0,reste_clos:!!b.cl};
fdb=fdb0;
out.verdict=(out.creation_silencieuse.decembre_recree&&out.creation_silencieuse.acces_cloud===0&&!out.cloud_non_lu.clos&&out.cloud_non_lu.pret&&!out.conflit_en_cours.clos&&!out.assistant_ouvert.clos&&out.tout_en_ordre.clos&&out.annulation.question_posee&&out.annulation.reste_clos)?'OK':'À REGARDER';
return JSON.stringify(out,null,1)}
"""


async def main():
    async with ouvrir(horloge='2026-11-14T10:00:00', dernier=(2026, 11)) as (pg, erreurs):
        await pg.clock.set_fixed_time('2026-12-01T10:00:00')
        await pg.reload(); await pg.wait_for_timeout(800)
        await pg.evaluate("(c)=>c.split('').forEach(k=>pp(k))", '0000'); await pg.wait_for_timeout(4000)
        print(await pg.evaluate(JS)); print('erreurs de page :', erreurs)

lancer(main())
