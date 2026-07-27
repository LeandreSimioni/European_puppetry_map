# Protocole de vérification, pays par pays

## Ordre de traitement suggéré

Commencer par les pays où la donnée existe déjà quelque part, pour calibrer la
méthode avant d'attaquer les cas difficiles.

1. **Pologne, Tchéquie, Roumanie, Croatie, Hongrie.** Les théâtres d'État y sont
   comptables d'un volume et publient un rapport annuel avec nombre de
   représentations et de spectateurs. C'est la source la plus directe.
2. **Allemagne.** Les théâtres municipaux publient des bilans, et il existe des
   statistiques sectorielles agrégées du spectacle vivant.
3. **France.** Paradoxalement le cas le plus difficile : l'information est
   éclatée et hétérogène. Passer par le côté organisateur ou par les données de
   paie du spectacle vivant, qui donnent des jours travaillés déclarés.
4. **Italie, Espagne, Royaume-Uni.** Peu d'agrégation, beaucoup de compagnies.
   Probablement enquête déclarative.
5. **Le reste**, par contact professionnel direct.

## Pour chaque pays, dans l'ordre

1. Lire `data/<CC>.json` et la liste `a_verifier`.
2. Identifier une structure ou un organisme qui publie un volume d'activité.
3. Remplir d'abord les indicateurs institutionnels, plus faciles, qui servent de
   test de fiabilité de la source.
4. Ne passer aux indicateurs de métier que si le dénominateur a été tranché.
5. Mettre à jour `confiance`, `statut`, `source`, `annee` et `raisonnement`.
6. `python3 build.py --check`, puis commit.

## Modèle de raisonnement acceptable

> Rapport annuel 2024 de la structure X : 312 représentations, troupe de 19
> interprètes permanents, distributions de 3 à 5 selon les titres. En retenant
> une distribution moyenne de 4, on obtient environ 66 dates par interprète.
> Dénominateur : interprètes sous contrat permanent. Ne vaut que pour les
> théâtres d'État, pas pour le secteur indépendant du même pays.

## Modèle de raisonnement inacceptable

> Environ 100 dates, ce qui correspond à ce qu'on observe dans les pays à
> troupes permanentes.

La différence : le premier se réfute, le second se croit.

## Le piège à surveiller en permanence

Une valeur estimée qui reste en place assez longtemps finit par être citée comme
une donnée. C'est la raison d'être du champ `confiance` et de la trame visuelle
sur la carte. Si une valeur estimée sort du dépôt, elle revient sous forme de
chiffre officieux et devient impossible à corriger.
