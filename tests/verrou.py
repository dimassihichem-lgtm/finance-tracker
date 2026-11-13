"""Écran de code : après cinq codes faux, une attente s'impose (30 s, puis le double à chaque échec) ;
pendant l'attente même le bon code est refusé ; ensuite le bon code ouvre et remet le compteur à zéro.
Usage : python3 verrou.py"""
import sys
from commun import ouvrir, lancer, CODE

TAPE = "(c)=>{c.split('').forEach(k=>pp(k));return{ouvert:document.getElementById('app').style.display==='block',msg:document.getElementById('pin-msg').textContent,compteur:localStorage.getItem('hft7_pinfail')}}"


async def main():
    ok = True
    async with ouvrir(horloge='2026-11-14T10:00:00') as (pg, erreurs):
        # on reverrouille en rechargeant la page
        await pg.reload(); await pg.wait_for_timeout(700)
        for i in range(1, 6):
            r = await pg.evaluate(TAPE, '9999'); await pg.wait_for_timeout(600)
            print(f"code faux n°{i} → ouvert {r['ouvert']} · « {r['msg']} »")
            ok = ok and not r['ouvert']
        r = await pg.evaluate(TAPE, CODE); await pg.wait_for_timeout(300)
        print(f"bon code pendant l'attente → ouvert {r['ouvert']} · « {r['msg']} »"); ok = ok and not r['ouvert'] and 'Trop' in r['msg']
        await pg.reload(); await pg.wait_for_timeout(700)
        r = await pg.evaluate(TAPE, CODE); await pg.wait_for_timeout(300)
        print(f"après rechargement, toujours pendant l'attente → ouvert {r['ouvert']}"); ok = ok and not r['ouvert']
        await pg.clock.set_fixed_time('2026-11-14T10:00:31'); await pg.wait_for_timeout(1200)
        r = await pg.evaluate(TAPE, '9999'); await pg.wait_for_timeout(600)
        print(f"31 s plus tard, 6e code faux → « {r['msg']} »"); ok = ok and '1 min' in r['msg']
        await pg.clock.set_fixed_time('2026-11-14T10:01:32'); await pg.wait_for_timeout(1200)
        r = await pg.evaluate(TAPE, CODE); await pg.wait_for_timeout(500)
        print(f"61 s plus tard, bon code → ouvert {r['ouvert']} · compteur {r['compteur']}"); ok = ok and r['ouvert'] and r['compteur'] is None
        print('erreurs de page :', erreurs, '\nverdict :', 'OK' if ok and not erreurs else 'À REGARDER')
        sys.exit(0 if ok and not erreurs else 1)

lancer(main())
