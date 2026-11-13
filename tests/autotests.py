"""Lance l'Autotest intégré à l'application (Plus → Autotest) et affiche les échecs.
Usage : python3 autotests.py [-v]"""
import sys
from commun import ouvrir, lancer


async def main():
    async with ouvrir(semer=False) as (pg, erreurs):
        await pg.wait_for_timeout(800)
        res = await pg.evaluate('typeof runSelfTests==="function"?runSelfTests():null')
        if res is None:
            print('Autotest introuvable'); sys.exit(1)
        ko = [r for r in res if not r['ok']]
        print(f"{len(res) - len(ko)}/{len(res)} tests réussis · erreurs de page : {erreurs[:5]}")
        for r in res:
            if not r['ok'] or '-v' in sys.argv:
                print(('OK ' if r['ok'] else 'KO ') + r['n'] + ' | ' + r['d'])
        sys.exit(1 if ko or erreurs else 0)

lancer(main())
