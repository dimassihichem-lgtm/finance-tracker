"""Captures d'écran des vues, pour comparer deux versions à l'œil.
Usage : python3 captures.py dossier_de_sortie [--largeurs 390,1440] [--themes light,dark] [--vues accueil,budget,plus/fiscal] [--base export.json]
Avec --base, les images contiennent des données réelles : ne pas les ranger dans le dépôt."""
import os, sys
from commun import ouvrir, lancer, option, VUES


async def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'captures'
    os.makedirs(sortie, exist_ok=True)
    largeurs = [int(x) for x in option('--largeurs', '390,1440').split(',')]
    themes = option('--themes', 'light').split(',')
    choix = option('--vues'); base = option('--base'); accent = option('--accent')
    vues = [v for v in VUES if not choix or v[0] in choix.split(',')]
    for th in themes:
        for w in largeurs:
            async with ouvrir(largeur=w, hauteur=844 if w < 700 else 900, horloge='2026-11-14T10:00:00', base=base, theme=th, accent=accent, echelle=2 if w < 700 else 1) as (pg, erreurs):
                for nom, code in vues:
                    await pg.evaluate("(c)=>{(0,eval)(c);window.scrollTo(0,0)}", code); await pg.wait_for_timeout(500)
                    f = os.path.join(sortie, f"{nom.replace('/', '_')}_{w}_{th}.png")
                    # Pas de capture « pleine page » : elle fait perdre au navigateur son écran tactile simulé,
                    # et l'image ne montrerait pas les réglages propres au téléphone. On agrandit la fenêtre à la place.
                    h = await pg.evaluate("()=>document.documentElement.scrollHeight")
                    await pg.set_viewport_size({'width': w, 'height': max(600, min(h, 15000))}); await pg.wait_for_timeout(250)
                    await pg.screenshot(path=f, full_page=False)
                    await pg.set_viewport_size({'width': w, 'height': 844 if w < 700 else 900})
                print(f"{w} px · {th} : {len(vues)} captures dans {sortie} · erreurs de page : {erreurs[:3]}")

lancer(main())
