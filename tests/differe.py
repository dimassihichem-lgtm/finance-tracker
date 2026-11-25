"""Rémunération différée et MIP (v161), sur la base fictive : calcul, affichage sur la page Cap,
saisie d'une hypothèse, Cap inchangé, ajout et retrait du bloc. Usage : python3 differe.py"""
import sys
from commun import ouvrir, lancer

JS = r"""
async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));const out={};const txt=()=>document.getElementById('pg-more').innerText.replace(/[  ]/g,' ');
const cap0=JSON.stringify(capCalc());
// 1 · page Cap : le bloc, les trois cas, la mention « au-dessus du chemin »
go('more');await wait(120);SUB='cap';rMore();await wait(150);const T=txt();
out.page={bloc:/Rémunération différée et MIP/.test(T),chemin:/Au-dessus du chemin/.test(T),bas:/Bas\s+7 333 €/.test(T),central:/Central\s+8 000 €/.test(T),total_haut:/11 400 €/.test(T),mip:/1 200 €/.test(T)&&/1 000 £/.test(T),note:/Conditions fictives/.test(T)};
// 2 · une hypothèse modifiée dans la page : la valeur du point de la tranche A passe à 1 200 €
const inp=document.querySelector('#pg-more input[onchange*="remdiffSet(\'vpt\'"]');inp.value='1200';inp.dispatchEvent(new Event('change'));await wait(150);
const o=remdiffCalc();out.saisie={vpt:DB.params.remdiff.tr[0].vpt,haut_A:Math.round(o.T[0].haut),central:Math.round(o.C[1].d),page:/Central\s+8 800 €/.test(txt()),ouvert:!!document.querySelector('#pg-more details[open] input[onchange*="remdiffSet(\'vpt\'"]')};
// 3 · le Cap ne bouge pas
out.cap_inchange=JSON.stringify(capCalc())===cap0;
// 4 · retrait puis ajout du bloc
const uc=uiConfirm;uiConfirm=async()=>true;await remdiffDrop();await wait(120);out.retrait={absent:!DB.params.remdiff,bouton:/Ajouter/.test(txt())&&!/Au-dessus du chemin/.test(txt())};
remdiffInit();await wait(120);remdiffAdd();await wait(120);out.ajout={tranches:DB.params.remdiff.tr.length,vide:/Rien de saisi|Bas\s+0 €/.test(txt())};uiConfirm=uc;
out.verdict=(Object.values(out.page).every(Boolean)&&out.saisie.vpt===1200&&out.saisie.haut_A===7000&&out.saisie.central===8800&&out.saisie.page&&out.saisie.ouvert&&out.cap_inchange&&out.retrait.absent&&out.retrait.bouton&&out.ajout.tranches===1&&out.ajout.vide)?'OK':'À REGARDER';
return JSON.stringify(out,null,1)}
"""


async def main():
    async with ouvrir(horloge='2026-11-14T10:00:00', dernier=(2026, 11)) as (pg, erreurs):
        r = await pg.evaluate(JS)
        print(r); print('erreurs de page :', erreurs)
        sys.exit(0 if '"verdict": "OK"' in r and not erreurs else 1)

lancer(main())
