"""Libellés piégés : des libellés contenant du HTML et des apostrophes ne doivent ni s'exécuter
ni casser l'affichage. Usage : python3 injection.py"""
import sys
from commun import ouvrir, lancer, VUES

PIEGE = r"""
()=>{const P='<img src=x onerror="window.__inj=(window.__inj||0)+1">\'"><b id=__inj_b>x</b>';let n=0;
const walk=(o,d)=>{if(!o||d>6)return;if(Array.isArray(o)){o.forEach(x=>walk(x,d+1));return}if(typeof o!=='object')return;
 for(const k of Object.keys(o)){const v=o[k];if(typeof v==='string'&&/^(l|n|label|nom|lib|titre|note|motif|env|t|s|name|pattern)$/.test(k)&&!/^\d{4}-\d{2}/.test(v)){o[k]=P+' '+v.slice(0,12);n++}else walk(v,d+1)}};
walk(DB.bm,0);walk(DB.im,0);walk(DB.params,0);walk(DB.rules,0);walk(DB.decisions,0);walk(DB.fiscal,0);GM_CACHE={};return n}
"""
RENDU = "(vues)=>{const e=[];vues.forEach(([n,c])=>{try{(0,eval)(c)}catch(x){e.push(n+' : '+(x&&x.message||x))}if(document.getElementById('__inj_b')||document.querySelector('img[src=x]'))e.push(n+' : libellé interprété comme du HTML')});return e}"


async def main():
    async with ouvrir(horloge='2026-11-14T10:00:00') as (pg, erreurs):
        n = await pg.evaluate(PIEGE)
        pb = await pg.evaluate(RENDU, VUES)
        await pg.wait_for_timeout(600)
        ex = await pg.evaluate('window.__inj||0')
        print(f"{n} libellés piégés · exécutions : {ex} · vues en défaut : {pb} · erreurs de page : {erreurs[:5]}")
        print('verdict :', 'OK' if not ex and not pb and not erreurs else 'À REGARDER')
        sys.exit(0 if not ex and not pb and not erreurs else 1)

lancer(main())
