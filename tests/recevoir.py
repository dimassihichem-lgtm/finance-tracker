"""« À recevoir » : la liste des remboursements attendus, sur la base fictive.
Du calcul à l'accueil, la déclaration d'une dépense, les exclusions, puis le ré-import du relevé
(les étiquettes posées sur les lignes doivent y survivre). Usage : python3 recevoir.py"""
import sys
from commun import ouvrir, lancer

JS = r"""
async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));const out={};const txt=()=>document.getElementById('pg-more').innerText;
// 1 · départ : 8 box à 40 €, 6 remboursées, octobre en retard, novembre en attente, une note de frais sans dépense en face
const E=recvCalc().payers[0];out.depart={du:E.du,recu:E.recu,reste:E.reste,retard:E.late.length,sans_depense:E.extraAmt};
// 2 · accueil, menu Plus, page
go('home');await wait(150);out.accueil=/Remboursement en retard · Employeur fictif/.test(document.getElementById('pg-home').innerText);
go('more');await wait(150);out.menu=/Remboursements[\s\S]{0,80}1 en retard/.test(txt());
SUB='recv';rMore();await wait(150);out.page={reste:/80 €/.test(txt()),retard:/1 remboursement en retard de plus de 30 jours : 40 € à réclamer/.test(txt()),sans:/Reçu sans dépense en face/.test(txt())};
// 3 · déclarer une dépense : on la choisit dans le relevé (recherche), puis 12,50 € attendus
document.querySelector('#pg-more button[onclick="recvPickOpen()"]').click();await wait(120);const M=()=>document.getElementById('recv-modal');
out.choix={liste:M().querySelectorAll('#rv-list button').length,box_suivie:/↩ 40 €/.test(M().innerText)};
const q=document.getElementById('rv-q');q.value='centre commercial';q.dispatchEvent(new Event('input'));await wait(80);out.choix.recherche=[...M().querySelectorAll('#rv-list button')].every(x=>/CENTRE COMMERCI/.test(x.innerText))&&M().querySelectorAll('#rv-list button').length===8;
const b=gBM(2026,11);const i=b.imp.lines.findIndex(l=>/CENTRE COMMERCIAL/.test(l.l));M().querySelector('#rv-list button[onclick^="recvAsk(2026,11,"]').click();await wait(80);
out.feuille=/CB MAGASIN/.test(M().innerText)&&/Employeur fictif/.test(M().innerText)&&/Retour/.test(M().innerText);
document.getElementById('rv-amt').value='12.5';recvSave();await wait(150);
out.declaration={etiquette:JSON.stringify(b.imp.lines[i].recv),du:recvCalc().payers[0].du,feuille_fermee:!M().innerHTML,page:/CB MAGASIN/.test(txt())};
// 4 · rien à recevoir sur la box de novembre, puis virement de la note de frais ignoré
const j=b.imp.lines.findIndex(l=>/FOURNISSEUR BOX/.test(l.l));recvAsk(2026,11,j);await wait(80);recvNone();await wait(80);
const a=gBM(2026,4);const k=a.imp.lines.findIndex(l=>/NOTE DE FRAIS/.test(l.l));SUB='recv';rMore();await wait(80);
document.querySelector('#pg-more div[onclick^="recvExtra(2026,4,"]').click();await wait(80);out.virement={feuille:/ne correspond à aucune dépense suivie/.test(M().innerText),sans_reste:!/Laisser ce reste de côté/.test(M().innerText)};
M().querySelector('button[onclick^="recvSkip(2026,4,"]').click();await wait(80);
const R2=recvCalc().payers[0];out.exclusions={du:R2.du,reste:R2.reste,sans_depense:R2.extraAmt,ecartes:R2.aside.length,marque:a.imp.lines[k].recvSkip,visible:/Virements écartés \(1\)/.test(txt())};
// 4 bis · solder une dépense en gardant ce qui est reçu : la box d'octobre, 0 € reçu → rien à recevoir ; puis on la remet
const io=gBM(2026,10).imp.lines.findIndex(l=>/FOURNISSEUR BOX/.test(l.l));recvAsk(2026,10,io,false,0);await wait(60);recvNone();await wait(60);out.solde={reste:recvCalc().payers[0].reste};
recvAsk(2026,10,io);await wait(60);document.getElementById('rv-amt').value='40';recvSave();await wait(60);out.solde.remise=recvCalc().payers[0].reste;
// 4 ter · avoir à confirmer (v156) : proposé, puis refusé
SUB='recv';rMore();await wait(80);out.avoir={carte:/Avoirs à confirmer \(1\)/.test(txt()),todo:todoList().some(x=>/1 avoir à confirmer/.test(x.t))};
document.querySelector('#pg-more button[onclick="rapNo(0)"]').click();await wait(80);out.avoir.non=/Propositions refusées \(1\)/.test(txt())&&!/Avoirs à confirmer \(1\)/.test(txt());
// 5 · ré-import du relevé de novembre : les étiquettes survivent
const ua=uiAlert,uc=uiConfirm;uiAlert=async()=>{};uiConfirm=async()=>true;
IMP_STATE={byM:{'2026-11':b.imp.lines.map(l=>({d:l.d,l:l.l,v:l.v}))},unRes:{},months:['2026-11'],res:{}};
await impValidate('2026-11');await wait(500);uiAlert=ua;uiConfirm=uc;
const L=gBM(2026,11).imp.lines;const AV=L.find(l=>/^AVOIR/.test(l.l));out.reimport={refus:!!(AV&&AV.rapNo===1),type_avoir:AV&&AV.t,lignes:L.length,declaration:JSON.stringify((L.find(l=>/CENTRE COMMERCIAL/.test(l.l))||{}).recv),exclusion:JSON.stringify((L.find(l=>/FOURNISSEUR BOX/.test(l.l))||{}).recv),reste:recvCalc().payers[0].reste};
// 5 bis · la proposition remise, puis acceptée : l'avoir et l'achat passent en transit
SUB='recv';rMore();await wait(80);document.querySelector('#pg-more button[onclick^="rapUndo("]').click();await wait(80);document.querySelector('#pg-more button[onclick="rapYes(0)"]').click();await wait(80);
out.avoir.oui=gBM(2026,11).imp.lines.filter(l=>/JOUETS/.test(l.l)&&l.transit).length===2&&!document.querySelector('#pg-more button[onclick^="rapYes("]');
// 6 · réglages : un mot-clé de virement qui ne correspond plus à rien, et tout redevient dû
SUB='recv';rMore();await wait(100);recvSet('payers','emp','pat','AUTRE NOM');await wait(100);const R3=recvCalc().payers[0];out.reglages={recu:R3.recu,virements:R3.recN};recvSet('payers','emp','pat','EMPLOYEUR FICTIF');
const D=out.depart,P=out.page,X=out.declaration,Y=out.exclusions,Z=out.reimport;
out.verdict=(D.du===320&&D.recu===240&&D.reste===80&&D.retard===1&&D.sans_depense===120&&out.accueil&&out.menu&&P.reste&&P.retard&&P.sans&&out.choix.liste===10&&out.choix.box_suivie&&out.choix.recherche&&out.feuille
 &&X.etiquette==='{"p":"emp","a":12.5}'&&X.page&&X.du===332.5&&X.feuille_fermee&&Y.du===292.5&&Y.reste===52.5&&Y.sans_depense===0&&Y.ecartes===1&&Y.marque===2&&Y.visible&&out.virement.feuille&&out.virement.sans_reste&&out.solde.reste===12.5&&out.solde.remise===52.5
 &&out.avoir.carte&&out.avoir.todo&&out.avoir.non&&out.avoir.oui&&Z.refus&&Z.declaration==='{"p":"emp","a":12.5}'&&Z.exclusion==='{"p":"emp","a":0}'&&Z.reste===52.5&&out.reglages.recu===0&&out.reglages.virements===0)?'OK':'À REGARDER';
return JSON.stringify(out,null,1)}
"""


async def main():
    async with ouvrir(horloge='2026-11-14T10:00:00', dernier=(2026, 11)) as (pg, erreurs):
        r = await pg.evaluate(JS)
        print(r); print('erreurs de page :', erreurs)
        sys.exit(0 if '"verdict": "OK"' in r and not erreurs else 1)

lancer(main())
