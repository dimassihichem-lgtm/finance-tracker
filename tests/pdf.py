"""Module PDF à la demande : il n'est pas chargé à l'ouverture, se charge au premier appel
(contrôle d'intégrité du navigateur compris) et sait fabriquer un document.
Le réseau étant coupé, le module est servi depuis une copie locale :
    npm install jspdf@2.5.1        puis        JSPDF=node_modules/jspdf/dist/jspdf.umd.min.js python3 pdf.py
Avec --base export.json, la fiche de paie du mois en cours est fabriquée pour de bon (rien n'est conservé)."""
import os, sys
from commun import ouvrir, lancer, option


async def main():
    local = os.environ.get('JSPDF')
    if not local or not os.path.exists(local):
        print('Copie locale du module introuvable : définir JSPDF (voir en tête du script).'); sys.exit(2)
    corps = open(local, 'rb').read()
    async with ouvrir(horloge='2026-11-14T10:00:00', base=option('--base')) as (pg, erreurs):
        appels = []
        async def servir(route):
            appels.append(route.request.url)
            await route.fulfill(status=200, content_type='application/javascript', body=corps, headers={'access-control-allow-origin': '*'})
        await pg.route('**/jspdf.umd.min.js', servir)
        avant = await pg.evaluate("()=>!!(window.jspdf||window.jsPDF)")
        r = await pg.evaluate("async()=>{try{const J=await jspdfLoad();const d=new J({unit:'mm',format:'a4'});d.text('essai',10,10);const J2=await jspdfLoad();return{ok:true,pages:d.internal.getNumberOfPages(),meme:J===J2}}catch(e){return{ok:false,err:String(e&&e.message||e)}}}")
        print(f"chargé à l'ouverture : {avant} · chargement à la demande : {r} · requêtes : {len(appels)}")
        ok = (not avant) and r.get('ok') and r.get('meme') and len(appels) == 1
        if option('--base'):
            await pg.evaluate("()=>{go('garde')}"); await pg.wait_for_timeout(300)
            try:
                async with pg.expect_download(timeout=8000) as dl:
                    await pg.evaluate("()=>{const n=new Date();FY=n.getFullYear();FM=n.getMonth()+1;return downloadPdf()}")
                d = await dl.value
                print('fiche fabriquée :', bool(d.suggested_filename), '· taille du nom', len(d.suggested_filename))
            except Exception as e:
                print('fiche non fabriquée :', str(e)[:160]); ok = False
        print('erreurs de page :', erreurs, '\nverdict :', 'OK' if ok and not erreurs else 'À REGARDER')
        sys.exit(0 if ok and not erreurs else 1)

lancer(main())
