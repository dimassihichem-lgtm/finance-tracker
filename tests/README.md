# Scripts de contrôle de l'application Patrimoine

Ces scripts ouvrent `index.html` dans un navigateur sans fenêtre, **hors réseau**, sur une **base fictive**,
et vérifient ce qu'une lecture du code ne montre pas. Ils servent avant chaque nouvelle version.

**Le dépôt est public.** Rien de personnel ne doit entrer ici : ni export, ni bulletin, ni nom, ni montant réel,
ni capture d'écran prise sur de vraies données. Pour contrôler une version sur de vraies données, passer un export
local avec `--base /chemin/export.json` et laisser les résultats hors du dépôt.

## Installation

    pip install playwright
    playwright install chromium     # inutile si Chrome est déjà installé (variable CHROME pour un autre chemin)

## Les contrôles

| Script | Ce qu'il vérifie |
|---|---|
| `autotests.py` | L'Autotest intégré à l'application (Plus → Autotest) passe en entier |
| `annulation.py` | L'Autotest ne touche ni la copie locale, ni le cloud, ni l'historique ; ↶ demande confirmation avant un état plus pauvre ; l'historique repart de zéro quand une version arrive du cloud |
| `cloture.py` | Clôture automatique : retenue si le cloud n'est pas lu, en cas de conflit ou si l'assistant est ouvert ; faite quand tout est en ordre |
| `dates.py` | Ouverture à plusieurs dates (mi-mois, 2 janvier, 1er septembre, 29 février) : rien n'est enregistré à l'ouverture, toutes les vues s'affichent, ce qui se crée tout seul est listé |
| `verrou.py` | Écran de code : attente après cinq codes faux, bon code refusé pendant l'attente, remise à zéro ensuite |
| `pdf.py` | Le module PDF n'est pas chargé à l'ouverture, se charge à la demande (contrôle d'intégrité compris) et fabrique un document. Demande une copie locale du module (voir l'en-tête du script) |
| `injection.py` | Des libellés contenant du HTML ou des apostrophes ne s'exécutent pas et ne cassent rien |
| `affichage.py` | Vue par vue : débordements, textes coupés, textes sous 11 px, tailles et polices, zones tactiles trop petites, contrastes sous 4,5:1, hauteur des pages. `--json` enregistre, `--ref` compare à une version précédente |
| `captures.py` | Captures d'écran de chaque vue, pour comparer deux versions à l'œil |
| `tout.py` | Lance tout à la suite |

`commun.py` contient la base fictive, l'ouverture hors réseau et la liste des vues.

## Comparer deux versions

    APP=/chemin/ancienne/index.html python3 affichage.py --json avant.json
    python3 affichage.py --ref avant.json --detail

Un autre fichier que `../index.html` se désigne par la variable `APP`.

## Modules externes pendant les contrôles

Le réseau est coupé : les graphiques et les autres modules chargés depuis Internet sont absents, sauf si on en fournit une copie locale :

    LOCAL='**/chart.umd.min.js=/chemin/chart.umd.js' python3 captures.py sortie

Le navigateur vérifie l'empreinte de chaque module : une copie qui n'est pas identique au fichier d'origine est refusée.

## Limites

- Le cloud est simulé : rien n'est jamais testé contre le vrai Firestore.
- Le navigateur est simulé : le rendu réel sur iPhone (zoom à la saisie, polices du système) ne se vérifie que sur l'appareil.
- Sous 700 px de large, l'écran est déclaré tactile, comme un téléphone. Une capture « pleine page » fait perdre ce réglage : `captures.py` agrandit la fenêtre à la place.
- Les graphiques sont dessinés dans des images : leurs textes ne sont pas mesurés par `affichage.py`.
