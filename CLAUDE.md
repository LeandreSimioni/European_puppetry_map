# Consignes de travail sur ce dépôt

## Nature du projet

Pré-étude cartographique sur l'écosystème européen de la marionnette. Les
valeurs actuelles sont des estimations produites sans source. L'objet du travail
est de les remplacer une à une par des valeurs vérifiées, pas de les défendre.

## Règles non négociables

1. **Une session, un pays.** Ne jamais modifier plusieurs fiches pays dans la
   même passe. La vérification de la Croatie ne doit pas toucher la ligne France.
2. **Jamais de valeur sans raisonnement.** Le champ `raisonnement` est
   obligatoire et le build échoue s'il est vide. Y écrire la méthode de calcul,
   pas une paraphrase de la valeur.
3. **Ne jamais inventer une source.** Si aucune source n'est trouvée, la valeur
   reste en `confiance: "estime"` avec `source: null`. Une source approximative
   ou reconstruite de mémoire est pire qu'une absence de source.
4. **Ne jamais éditer `dist/index.html`.** Il est écrasé à chaque build.
5. **Médiane, pas moyenne**, pour tout indicateur de métier. Les distributions
   sont bimodales et la moyenne ne décrit personne.
6. **Un cachet n'est pas une date jouée.** Répétitions, résidences, ateliers et
   actions culturelles produisent des cachets sans plateau. Toute valeur qui
   confond les deux est fausse.
7. **Un commit par valeur modifiée**, avec le raisonnement dans le message.

## Avant de modifier une valeur

Lire `schema.json`, en particulier le champ `denominateur` de l'indicateur
concerné et son `biais_connu`. Si le dénominateur porte la mention
`A TRANCHER`, ne pas produire de valeur : signaler l'arbitrage manquant.

## Après toute modification

```bash
python3 build.py --check   # doit sortir sans erreur
python3 build.py           # régénère la carte
```

## Ce qu'il ne faut pas faire

- Proposer des indicateurs qualitatifs ou catégoriels. Ils ont été écartés
  explicitement : régime de production, statut d'emploi, traditions, figures.
  Seul le quantifiable et comparable entre pays est retenu.
- Raisonner à partir du nombre de lieux ou d'écoles pour en déduire un volume
  d'activité. C'est le biais que ce dépôt existe pour corriger.
- Traiter une donnée institutionnelle comme un indicateur de vitalité.
