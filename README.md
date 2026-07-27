# L'Europe des castelets

Pré-étude cartographique de l'écosystème européen de la marionnette.

**Aucune valeur de ce dépôt n'est sourcée à ce stade.** Tout ce qui s'y trouve
a été produit de mémoire, sans recherche, pour servir d'hypothèse à confirmer ou
à infirmer pays par pays. C'est le but de l'exercice : disposer d'une
prévisualisation assez précise pour être réfutable.

## Ce que contient le dépôt

```
schema.json               définitions, dénominateurs, règles de collecte
data/<CC>.json            une fiche par pays, format long, 45 pays
geo/europe.json           tracés projetés (Natural Earth 1:50 M, domaine public)
templates/carte.html      gabarit de la carte, sans données
build.py                  valide les données et régénère dist/index.html
tools/seed_data.py        amorçage initial, ne plus exécuter
dist/index.html           carte générée, ne jamais éditer à la main
docs/                     note de méthode, protocole, tableau initial
```

## Utilisation

```bash
python3 build.py --check   # valide les données sans rien écrire
python3 build.py           # régénère dist/index.html
```

Aucune dépendance, Python 3 standard suffit. Ouvrir `dist/index.html` dans un
navigateur.

## Le format long, et pourquoi

Un tableau large mélange sur une même ligne du chiffre sourcé et du chiffre
inventé, sans moyen de les distinguer. Ici, chaque observation est un objet
autonome portant sa valeur, son année, sa source, son niveau de confiance, son
statut et le raisonnement qui l'a produite.

```json
{
  "indicateur": "dates",
  "valeur": 35,
  "annee": null,
  "source": null,
  "confiance": "estime",
  "statut": "conteste",
  "raisonnement": "..."
}
```

Le champ `raisonnement` est obligatoire et le build échoue s'il est vide. Ce
n'est pas une formalité : la première valeur de `dates` pour la France a été
réfutée en une phrase dès que le raisonnement a été explicité, parce qu'il
révélait un dénominateur amputé.

## Les trois niveaux de confiance

| Niveau | Sens | Citable |
|---|---|---|
| `estime` | Produit par raisonnement, sans source | Jamais, sous aucune forme |
| `declare` | Communiqué par un professionnel du pays, non publié | Avec mention explicite |
| `sourced` | Publié par une source identifiée et citable | Oui |

Le build refuse une observation `declare` ou `sourced` sans champ `source`
renseigné.

## L'arbitrage qui bloque tout le reste

Le dénominateur de l'indicateur `dates` n'est pas tranché. Trois options
incompatibles :

- toute personne se déclarant marionnettiste professionnel
- toute personne ayant joué au moins une date dans l'année
- tout interprète sous contrat permanent ou équivalent

Comparer des déclarés français à des permanents croates revient à comparer deux
populations différentes. Tant que ce choix n'est pas fait, les colonnes `dates`
et `part_sous_20` restent au statut `conteste`, et la carte les affiche comme
telles.

## Ce que la carte sait déjà faire

Dix mesures réparties en deux couches. La couche institutions recense des
contenants, la couche métier postule des volumes de travail. Dès qu'une mesure
métier est active, une trame diagonale couvre la carte et le bandeau bascule sur
« hypothèse à falsifier ». Les mesures à lecture inversée passent sur une rampe
froide.

## Prochaines étapes

1. Trancher le dénominateur de `dates`.
2. Afficher la confiance par cellule et non par couche : le payload transporte
   déjà `confiance[pays][indicateur]`, le gabarit ne l'exploite pas encore.
3. Remplacer une valeur estimée par une valeur sourcée, un pays à la fois, en
   commençant par ceux dont les structures publient un rapport annuel.
4. Ajouter les indicateurs listés dans `indicateurs_a_ajouter` du schéma, à
   commencer par la subvention publique par représentation jouée.
