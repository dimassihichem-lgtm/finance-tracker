"""Ouvre l'application à plusieurs dates (horloge réglée) et vérifie que :
- rien n'est enregistré à la simple ouverture ;
- toutes les vues et l'assistant s'affichent sans erreur ;
- on voit ce qui se crée tout seul (nouveau mois, reconduction des dépenses ponctuelles).
Usage : python3 dates.py"""
import json
from commun import ouvrir, lancer, VUES

ETAT = r"""
()=>{const st=JSON.parse(localStorage.getItem('hft7'));const k=d=>(d.bm||[]).map(b=>b.y+'-'+String(b.m).padStart(2,'0')+(b.cl?'✓':'')).join(' ');
return {enregistre:k(st).split(' ').slice(-3).join(' '),en_memoire:k(DB).split(' ').slice(-3).join(' '),historique:HIST.length,
 a_faire:todoList().filter(x=>/Compl|clôtur|Reclô/i.test(x.t)).map(x=>x.t+' — '+x.s)}}
"""
CREE = r"""
()=>{const st=JSON.parse(localStorage.getItem('hft7'));const out=[];const mois=d=>new Set((d.bm||[]).map(b=>b.y+'-'+b.m));const a=mois(st),b=mois(DB);[...b].filter(x=>!a.has(x)).forEach(x=>out.push('mois de budget créé : '+x));
const ia=new Set((st.im||[]).map(b=>b.y+'-'+b.m));(DB.im||[]).map(b=>b.y+'-'+b.m).filter(x=>!ia.has(x)).forEach(x=>out.push('mois de placements créé : '+x));
const pa=JSON.stringify(st.params.proj.depPonctuels),pb=JSON.stringify(DB.params.proj.depPonctuels);if(pa!==pb)out.push('dépenses ponctuelles : '+DB.params.proj.depPonctuels.map(d=>d.l+' '+d.an+(d.rec?' (reconduite)':'')).join(' · '));
return out}
"""
RENDU = "(vues)=>{const e=[];vues.forEach(([n,c])=>{try{(0,eval)(c)}catch(x){e.push(n+' : '+(x&&x.message||x))}});try{wizStart();for(let i=0;i<WZ.steps.length;i++){WZ.step=i;wizRender()}WZ.on=false;document.getElementById('wiz').classList.remove('on')}catch(x){e.push('assistant : '+(x&&x.message||x))}go('home');return e}"


async def scenario(nom, horloge, dernier):
    async with ouvrir(horloge=horloge, dernier=dernier) as (pg, erreurs):
        avant = await pg.evaluate("()=>localStorage.getItem('hft7')")
        await pg.wait_for_timeout(4500)
        apres = await pg.evaluate("()=>localStorage.getItem('hft7')")
        print('\n=====', nom, '· horloge', horloge)
        print('copie enregistrée inchangée après ouverture :', avant == apres)
        print(json.dumps(await pg.evaluate(ETAT), ensure_ascii=False, indent=1))
        print('créé tout seul (en mémoire) :', json.dumps(await pg.evaluate(CREE), ensure_ascii=False))
        print('erreurs de rendu :', await pg.evaluate(RENDU, VUES), '| erreurs de page :', erreurs)


async def main():
    await scenario('Milieu de mois', '2026-11-14T10:00:00', (2026, 11))
    await scenario('Passage de janvier', '2027-01-02T10:00:00', (2026, 12))
    await scenario('Passage de septembre (nouvelle année de suivi)', '2027-09-01T10:00:00', (2027, 8))
    await scenario('29 février', '2028-02-29T23:30:00', (2028, 2))

lancer(main())
