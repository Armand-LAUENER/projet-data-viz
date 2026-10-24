# Projet Streamlit — Data Storytelling (EFREI, BIA)

## Sujet : les accidents de la route en France — quand un accident devient-il mortel ?

> **Dossier de cadrage et plan de réalisation complet**
> Projet individuel `#EFREIDataStories2026` — Enseignant : Mano Joseph Mathew
> Rédigé le 24/10/2026. Les points marqués **⚠️ À VÉRIFIER** n'ont pas pu être confirmés et doivent l'être avant de s'engager.

---

## Sommaire

1. [Ce qu'il faut rendre](#1-ce-quil-faut-rendre)
2. [Barème et ce qu'il implique](#2-barème-et-ce-quil-implique)
3. [Le dataset](#3-le-dataset)
4. [Cadrage : question, public, récit](#4-cadrage--question-public-récit)
5. [Storyboard détaillé](#5-storyboard-détaillé)
6. [Spécifications des données](#6-spécifications-des-données)
7. [Spécifications du dashboard](#7-spécifications-du-dashboard)
8. [Architecture technique](#8-architecture-technique)
9. [Qualité des données et validation](#9-qualité-des-données-et-validation)
10. [Éthique et vie privée](#10-éthique-et-vie-privée)
11. [Plan de réalisation par phases](#11-plan-de-réalisation-par-phases)
12. [Vidéo de démo](#12-vidéo-de-démo)
13. [README et packaging](#13-readme-et-packaging)
14. [Risques et pièges](#14-risques-et-pièges)
15. [Checklist finale (mapping barème)](#15-checklist-finale-mapping-barème)
16. [Questions ouvertes](#16-questions-ouvertes)
17. [Sources](#17-sources)

---

## 1. Ce qu'il faut rendre

| # | Livrable | Détail | Source |
|---|---|---|---|
| 1 | **App Streamlit déployée** | Récit cohérent + composants interactifs, URL publique (Streamlit Community Cloud ou équivalent) | Énoncé + PDF |
| 2 | **Vidéo de démo** | 2 à 4 minutes, parcours du récit et des interactions, fournie sous forme de lien | Énoncé + PDF |
| 3 | **Zip** `StApp26_<n°étudiant>_<NOM>_BIA.zip` | Lien/dataset, README, code Python | Énoncé |
| 4 | **Lien du repo** | Code + **rapport** | PDF uniquement |
| 5 | **Storyboard** | Lien à fournir | PDF uniquement |

**Inconnues (⚠️ À VÉRIFIER sur Moodle / auprès de l'enseignant) :**
- Date limite de rendu.
- Plateforme de dépôt.
- Forme attendue du « rapport » (README étoffé suffisant ? PDF séparé ?).
- Langue de l'app et de la vidéo (énoncé en anglais → probablement anglais).
- Acceptation d'un fond de carte externe et, éventuellement, de données de population INSEE (cf. §6.7).

---

## 2. Barème et ce qu'il implique

| Critère | Pts | Ce qui est réellement évalué | Où mettre l'effort |
|---|---|---|---|
| Narration & cadrage | **25** | Public clair, questions, takeaways, alignement avec le storyboard | Storyboard **avant** le code ; une phrase-insight par section |
| Travail sur les données | **25** | Sourcing, nettoyage, validation, feature engineering | Jointure des 4 tables, harmonisation, reproduction des chiffres ONISR |
| Visualisation & UX | **25** | Types de graphiques adaptés, annotations, légendes, couleurs, interactions | Peu de graphiques mais justes ; annotations ; pas de contrôle inutile |
| Qualité du code | **15** | Structure, cache, perf, reproductibilité, doc | Pipeline d'agrégation + `st.cache_data` + `requirements.txt` figé |
| Communication | **10** | Clarté du rapport, vidéo, transparence sur les limites | Section « limites » honnête (exposition, ruptures de série) ; vidéo scriptée |

**Conséquence :** 75 % des points portent sur le récit, les données et la visualisation. Ce dataset est **riche côté données** (4 tables à joindre, variables codées, ruptures de format) : c'est là que se gagnent les points, pas dans une architecture sophistiquée. **Pas de dbt, pas d'Airflow, pas de base de données** : pandas + Parquet suffisent largement.

---

## 3. Le dataset

### 3.1 Fiche d'identité

**« Bases de données annuelles des accidents corporels de la circulation routière — Années de 2005 à 2024 »**

| Attribut | Valeur |
|---|---|
| Portail | **data.gouv.fr** (portail autorisé ✅) |
| Producteur | ONISR (Observatoire national interministériel de la sécurité routière), ministère de l'Intérieur |
| Source | Fichier BAAC : fiches remplies par les forces de l'ordre pour chaque accident corporel |
| Identifiant data.gouv | `53698f4ca3a729239d2036df` |
| Couverture temporelle | 2005 → 2024 (dernière mise à jour du jeu : 29/12/2025) |
| Couverture géographique | France métropolitaine, DOM (Mayotte depuis 2012), autres territoires d'outre-mer depuis 2019 dans l'open data |
| Structure | **4 fichiers CSV par an** : Caractéristiques, Lieux, Véhicules, Usagers, reliés par l'identifiant d'accident `Num_Acc` |
| Granularité | Un enregistrement par accident / lieu / véhicule / usager |
| Volume | Plusieurs dizaines de milliers d'accidents par an, plus de 100 000 usagers par an (ordre de grandeur, à mesurer) |
| Qualité des métadonnées (data.gouv) | Jugée « bonne (100 %) » |
| Documentation | Guide de description des bases (ONISR, version d'octobre 2025, FR/EN/ES) + guide de codification BAAC |
| Licence | ⚠️ À VÉRIFIER sur la page data.gouv (probablement Licence Ouverte / Etalab 2.0) |

### 3.2 Définitions officielles à reprendre telles quelles

- **Accident corporel** : accident sur une voie ouverte à la circulation publique, impliquant au moins un véhicule et ayant fait au moins une victime ayant nécessité des soins.
- **Tué** : personne décédée sur le coup ou dans les **30 jours** qui suivent l'accident.
- **Blessé hospitalisé** : victime hospitalisée plus de 24 heures (⚠️ indicateur problématique, voir §3.4).

### 3.3 Pourquoi ce dataset

- **Coche toutes les cases de l'énoncé** : temps (année, mois, jour, heure), géographie (département, commune, coordonnées GPS), catégories (type d'usager, de véhicule, de route, conditions).
- **Travail sur les données substantiel et valorisable** : jointures entre 4 tables, décodage de variables, harmonisation entre années, construction de variables → c'est ce que mesurent les 25 points « data work ».
- **Sujet concret, non politique**, qui parle à tout le monde.
- **Chiffres officiels disponibles pour valider le pipeline** (bilans annuels ONISR).
- **Volet éthique naturel** (données sur des personnes) → l'énoncé demande d'agréger pour protéger la vie privée ; c'est un point facile à démontrer.

### 3.4 ⚠️ Avertissements officiels (à intégrer dans l'app)

Ces limites sont publiées par l'ONISR et data.gouv. **Les ignorer serait une erreur de méthode visible.**

1. **Blessés hospitalisés non comparables avant/après 2018** : changement du process de saisie des forces de l'ordre. L'indicateur « blessé hospitalisé » **n'est plus labellisé** par l'Autorité de la statistique publique depuis 2019.
   → **Ne pas faire de série temporelle sur les blessés hospitalisés à cheval sur 2018.** Travailler principalement sur les **tués**, indicateur fiable.
2. **Usagers en fuite ajoutés à partir de 2021** : informations manquantes sur eux (sexe, âge, voire gravité).
   → Les manquants sur l'âge et le sexe augmentent mécaniquement à partir de 2021 : à afficher dans la section qualité.
3. **Certaines données sont occultées** pour protéger la vie privée des personnes facilement identifiables.
4. **Tous les accidents ne sont pas géolocalisés précisément.**
   → Les cartes par point sont partielles ; l'agrégation par département est plus fiable.
5. **Le format de la base a évolué en 2019** (nouvelles variables et modalités).
   → Voir le choix de périmètre §6.1.

### 3.5 Calendrier de publication

- Le jeu 2005-2024 a été mis à jour le 29/12/2025.
- L'ONISR a publié le bilan 2025 en mai 2026 ; **la base open data 2025 pourrait donc être ajoutée pendant le projet** (probablement fin 2026).
- → **Figer un snapshot daté** dès le début et l'indiquer dans le README. Ne pas laisser le pipeline télécharger « la dernière version » à chaque exécution.

---

## 4. Cadrage : question, public, récit

### 4.1 Question centrale

> **Quand, où et pour qui un accident de la route devient-il mortel ?**

L'angle : **la fréquence et la gravité ne racontent pas la même histoire**. Là où il y a le plus d'accidents n'est pas forcément là où l'on meurt le plus. Ce contraste est le fil rouge du dashboard.

### 4.2 Sous-questions (une par section)

1. **Quand ?** À quelles heures, quels jours, quels mois les accidents sont-ils les plus fréquents… et les plus graves ?
2. **Où ?** Quels départements ont le plus d'accidents ? Lesquels ont les accidents les plus graves ? En ville ou hors agglomération ?
3. **Qui ?** Quels usagers (piétons, cyclistes, deux-roues motorisés, automobilistes) et quelles tranches d'âge sont les plus représentés parmi les tués ?
4. **Dans quelles conditions ?** *(approfondissement optionnel)* Luminosité, météo, type de route, vitesse maximale autorisée.

### 4.3 Public cible

**Grand public, en particulier les jeunes conducteurs et les usagers vulnérables** (piétons, cyclistes, deux-roues). Conséquences :
- vocabulaire simple, définitions en infobulle (`help=`) ;
- aucun code BAAC visible : uniquement des libellés en clair ;
- un message final actionnable (« ce que ces chiffres disent sur les situations à risque »), sans moraliser.

### 4.4 Hypothèses à tester (pas à démontrer)

| # | Hypothèse | Ce qui la confirme ou l'infirme |
|---|---|---|
| H1 | La majorité des accidents a lieu **en agglomération**, mais la majorité des tués **hors agglomération** | Comparer la part des accidents et la part des tués par milieu. L'ONISR indique qu'en 2024, 60 % des décès ont eu lieu hors agglomération (bilan provisoire) ; la part des accidents est à calculer |
| H2 | Les accidents **de nuit** sont moins nombreux mais **plus graves** | Indice de gravité par tranche horaire et par luminosité |
| H3 | Les **usagers vulnérables** pèsent plus parmi les tués que parmi l'ensemble des victimes | Part de chaque catégorie parmi les victimes vs parmi les tués |
| H4 | Les départements **ruraux** ont moins d'accidents mais un indice de gravité plus élevé | Carte nombre d'accidents vs carte indice de gravité |

Si les données contredisent une hypothèse, **le récit change**. Ne pas tordre les graphiques pour la confirmer.

### 4.5 Arc narratif (structure imposée par le PDF)

| Étape | Contenu | Exemple |
|---|---|---|
| **Hook** | Le chiffre qui accroche | « En 2024, 3 193 personnes sont mortes sur les routes de France métropolitaine, soit près de 9 par jour. » (ONISR, bilan définitif) |
| **Contexte** | Ce qu'est un accident corporel, d'où viennent les données, ce qu'elles ne disent pas | Définitions officielles + avertissements §3.4 |
| **Insights** | 3 constats démontrés par les données | Quand / où / qui — avec le contraste fréquence vs gravité |
| **Implications** | Ce que ça suggère et ce que ça ne permet pas de conclure | Les situations les plus meurtrières ne sont pas les plus fréquentes ; mais sans données d'exposition, on ne peut pas dire quel mode est « le plus dangereux » par kilomètre |

### 4.6 Ce que le dashboard ne prétend PAS faire

- **Aucun risque par kilomètre ou par trajet.** Le BAAC ne contient pas les distances parcourues par mode de transport. Dire « la moto est X fois plus dangereuse que la voiture » est **impossible avec ce dataset seul**. On compare des **répartitions** et des **taux de gravité**, pas des risques d'exposition.
- **Aucune causalité** (« la pluie cause les accidents mortels »). On décrit des co-occurrences.
- **Aucune évaluation de politique publique** (radars, limitations de vitesse) : hors sujet et contraire à l'objectif « non politique ».
- **Aucune donnée individuelle identifiable** affichée (cf. §10).

---

## 5. Storyboard détaillé

À produire **avant tout code** (papier, Figma, Excalidraw ou slides). Le rendu du storyboard est demandé et son alignement avec l'app est noté.

Les phrases-insights ci-dessous sont des **hypothèses de titres** : elles seront réécrites après l'exploration (phase 1) avec ce que montrent réellement les données.

| # | Section | Phrase-insight (titre provisoire) | Visuel | Interaction | Question |
|---|---|---|---|---|---|
| 0 | **Intro** | « Près de 9 morts par jour sur les routes de métropole. » | KPI header + texte d'accroche + encadré définitions | Filtres globaux | Pourquoi ça compte ? |
| 1 | **Quand ?** | « Les accidents culminent aux heures de pointe, mais les plus graves arrivent la nuit. » *(H2)* | **Heatmap heure × jour de la semaine** + **courbe mensuelle** | Bascule « nombre d'accidents » / « indice de gravité » | Quand le risque est-il le plus élevé ? |
| 2 | **Où ?** | « La carte s'inverse : les départements avec le plus d'accidents ne sont pas les plus meurtriers. » *(H4)* | **Carte choroplèthe par département** + **barres agglomération vs hors agglomération** | Bascule de métrique, sélection de région | Où les accidents sont-ils les plus graves ? |
| 3 | **Qui ?** | « Piétons, cyclistes et deux-roues pèsent bien plus parmi les tués que parmi les victimes. » *(H3)* | **Dumbbell / barres comparées** (part des victimes vs part des tués par catégorie) + **pyramide des âges des tués par sexe** | Sélection de catégorie d'usager | Qui paie le plus lourd tribut ? |
| 4 | **Dans quelles conditions ?** *(bonus)* | « Hors agglomération, sur route à 80-90 km/h, de nuit : la combinaison la plus meurtrière. » | **Small multiples** de l'indice de gravité par luminosité, météo, type de route, VMA | Choix de la dimension | Quelles conditions aggravent les accidents ? |
| 5 | **Évolution** | « Une baisse sur 20 ans, interrompue par 2020. » *(à confirmer)* | **Courbe des tués 2005-2024** annotée (Covid 2020, ruptures de série) | Plage d'années | La situation s'améliore-t-elle ? |
| 6 | **Qualité des données** | « Des données fiables sur les tués, fragiles sur les blessés hospitalisés. » | Tableau des contrôles + heatmap de complétude + écart avec les chiffres ONISR | Aucune | Peut-on faire confiance à ces chiffres ? |
| 7 | **Conclusions** | Synthèse des constats + limites + pistes | Texte + rappel des chiffres clés | Aucune | Que retenir ? Que ne sait-on pas ? |

**Règle :** chaque graphique répond à une question listée ici. Un graphique qui ne répond à rien est supprimé.

---

## 6. Spécifications des données

### 6.1 Choix du périmètre (décision structurante)

| Option | Périmètre | Avantages | Inconvénients |
|---|---|---|---|
| **A — recommandée** | Analyses détaillées sur **2019-2024** (format homogène), métropole | Un seul format à gérer, 6 années, données récentes | Pas de vision longue sur les détails |
| B | 2005-2024 complet | Vision longue | Harmonisation lourde entre formats, ruptures de série (2018, 2019, 2021) |
| C | A + **série longue des tués seulement** (2005-2024) | Le meilleur des deux : détails récents + tendance longue | Un peu plus de travail sur l'harmonisation des anciens fichiers |

**Recommandation : A pour le MVP, C en bonus.** La série longue (section 5 du storyboard) n'est ajoutée que si le MVP est terminé. Le nombre de tués (définition à 30 jours) est l'indicateur le plus comparable dans le temps.

**Métropole vs outre-mer :** analyser la **métropole** par défaut (comparabilité avec les bilans ONISR), avec l'outre-mer en option dans les filtres. Documenter ce choix.

### 6.2 Les 4 tables et la jointure

```
caracteristiques (1 ligne / accident)
   │  Num_Acc
   ├── lieux       (1 ligne / accident)
   ├── vehicules   (1 ligne / véhicule impliqué)
   │      │  Num_Acc + id_vehicule
   └── usagers     (1 ligne / personne impliquée)
```

**Points d'attention :**
- `usagers` est la table de référence pour compter les **victimes et les tués**.
- `caracteristiques` est la table de référence pour compter les **accidents**.
- Une jointure mal faite (`usagers` × `vehicules` sur `Num_Acc` seul) **duplique les lignes** et gonfle les comptes. Joindre usagers et véhicules sur la clé véhicule.
- Contrôler l'**intégrité référentielle** : usagers sans accident, accidents sans lieu (cf. §9).

### 6.3 Variables principales

⚠️ **À VÉRIFIER dans le guide de description ONISR** : la liste ci-dessous correspond au format 2019+ tel que connu, mais les noms exacts, les modalités et les codes de valeurs manquantes doivent être confirmés sur le guide officiel avant d'écrire le code.

| Table | Variables utiles | Usage |
|---|---|---|
| Caractéristiques | `Num_Acc`, `jour`, `mois`, `an`, `hrmn` (heure:minute), `lum` (luminosité), `dep`, `com`, `agg` (en/hors agglomération), `int` (type d'intersection), `atm` (conditions atmosphériques), `col` (type de collision), `lat`, `long` | Quand, où, conditions |
| Lieux | `catr` (catégorie de route), `surf` (état de la surface), `vma` (vitesse maximale autorisée), `situ`, `infra` | Conditions (bonus) |
| Véhicules | `id_vehicule`, `catv` (catégorie de véhicule), `obs`, `obsm`, `choc`, `manv` | Mode de déplacement |
| Usagers | `id_vehicule`, `catu` (conducteur / passager / piéton), `grav` (gravité), `sexe`, `an_nais`, `trajet`, `secu1-3` | Qui, gravité |

**Gravité (`grav`)** — codage à confirmer : indemne / tué / blessé hospitalisé / blessé léger.

### 6.4 Pièges de format connus ou probables

⚠️ À vérifier fichier par fichier lors de l'exploration :
- **Séparateurs et encodages hétérogènes** selon les années (point-virgule, virgule, tabulation ; UTF-8 vs Latin-1).
- **Nom de la clé d'accident** qui peut varier selon les années (ex. un fichier où la colonne s'appelle autrement que `Num_Acc`) → normaliser à la lecture.
- **Coordonnées avec virgule décimale** (`lat`, `long`) → conversion en float.
- **Codes département** : formats différents avant 2019 (codes à 3 caractères) et Corse (`2A` / `2B`) → table de correspondance.
- **Heure** : format `hh:mm` ou entier selon les années → normaliser.
- **Valeurs manquantes codées** (ex. `-1`, `0` ou cellule vide selon la variable) → convertir en `NaN` explicitement, variable par variable, d'après le guide.

### 6.5 Accès aux données

**Script `scripts/download_data.py` :**
1. Interroger l'API data.gouv (`https://www.data.gouv.fr/api/1/datasets/53698f4ca3a729239d2036df/`) pour lister les ressources.
2. Sélectionner les fichiers des années voulues (par titre de ressource — ⚠️ vérifier les conventions de nommage).
3. Télécharger dans `data/raw/` (non versionné, `.gitignore`).
4. Écrire un fichier `data/raw/MANIFEST.json` : URL, date de téléchargement, taille, hash de chaque fichier → reproductibilité.

**Script `scripts/build_tables.py` :** lecture, harmonisation, jointures, agrégation → tables Parquet légères dans `data/processed/` (versionnées).

L'app ne lit **que** `data/processed/`. Elle ne télécharge rien au lancement.

### 6.6 Feature engineering prévu

| Variable dérivée | Calcul | Pourquoi |
|---|---|---|
| `date`, `jour_semaine`, `weekend` | À partir de `an`, `mois`, `jour` | Heatmap temporelle |
| `heure`, `tranche_horaire` | À partir de `hrmn` | Heatmap, comparaison jour/nuit |
| `saison` | À partir du mois | Saisonnalité |
| `age`, `tranche_age` | `an - an_nais`, regroupée (0-13, 14-17, 18-24, 25-34, …, 75+) | Pyramide des âges |
| `mode_deplacement` | Regroupement de `catv` + `catu` : piéton, vélo, EDP motorisé, deux-roues motorisé, voiture, utilitaire, poids lourd, autre | Lisibilité de la section « Qui ? » |
| `est_tue`, `est_victime` | À partir de `grav` | Comptes |
| `accident_mortel` | Au moins un tué dans l'accident | Indice de gravité |
| **`indice_gravite`** | **Tués pour 100 accidents corporels** | **Métrique centrale du contraste fréquence vs gravité** — ne nécessite aucune donnée externe |
| `milieu` | `agg` en clair : agglomération / hors agglomération | H1 |
| `region` | Département → région (table de correspondance) | Filtre et agrégation |
| `metropole` | Booléen sur le département | Filtre par défaut |

**L'indice de gravité est la clé du projet** : il permet de comparer des départements, des heures et des catégories **sans dénominateur externe** (population, kilomètres), en restant dans une seule source de données.

### 6.7 Données externes (à limiter, à faire valider)

L'énoncé demande un dataset ou un lot cohérent **d'une seule source**. Deux besoins pourraient le dépasser :

| Besoin | Option dans la source | Option externe | Recommandation |
|---|---|---|---|
| **Fond de carte des départements** | Aucune (le BAAC contient des coordonnées mais pas de contours) | GeoJSON des départements dérivé de l'IGN (ex. dépôt `france-geojson`) | Nécessaire pour la choroplèthe ; c'est un fond de carte, pas une donnée d'analyse → ⚠️ **le mentionner à l'enseignant** |
| **Population par département / âge** (tués par habitant) | Aucune | INSEE sur data.gouv | **À éviter au départ.** L'indice de gravité suffit. Ajouter seulement si l'enseignant valide |

**Alternative sans fond de carte externe** : carte de densité (hexbin / density map Plotly) directement à partir des `lat`/`long` du BAAC. Agrégée, elle respecte aussi la vie privée. Moins lisible qu'une choroplèthe par département, mais 100 % mono-source.

---

## 7. Spécifications du dashboard

### 7.1 Sidebar (contrôles)

| Contrôle | Type | Valeur par défaut | Impacte |
|---|---|---|---|
| Années | `st.slider` (plage) | 2019 → 2024 | Tout |
| Territoire | `st.radio` | Métropole | Tout |
| Région | `st.multiselect` | Toutes | Carte, KPI, sections |
| Métrique | `st.radio` : Accidents / Tués / Indice de gravité | Indice de gravité | Heatmap, carte |
| Mode de déplacement | `st.multiselect` | Tous | Sections « Qui ? » et « Quand ? » |
| Milieu | `st.radio` : Tous / Agglomération / Hors agglomération | Tous | Tout |

**Règle du PDF :** chaque contrôle doit changer quelque chose d'utile au récit. Un contrôle qui ne change rien d'intéressant est supprimé.

### 7.2 KPI header (réagit aux filtres)

| KPI | Valeur | Delta |
|---|---|---|
| Accidents corporels | n | vs année précédente |
| Tués (30 jours) | n | vs année précédente |
| Indice de gravité | tués / 100 accidents | vs moyenne de la période |
| Part des tués hors agglomération | % | vs part des accidents hors agglomération |

### 7.3 Visuels (≥ 3 interactifs exigés — 7 prévus)

| # | Type | Bibliothèque | Annotations obligatoires |
|---|---|---|---|
| V1 | Heatmap heure × jour de la semaine | Plotly | Unité de la couleur ; pics annotés |
| V2 | Courbe mensuelle (accidents et tués) | Plotly | Saison estivale ; 2020 confinements |
| V3 | Carte choroplèthe par département | Plotly | Légende de la métrique ; note sur la géolocalisation |
| V4 | Barres agglomération vs hors agglomération (part des accidents vs part des tués) | Plotly | Libellés en % directement sur les barres |
| V5 | Dumbbell : part des victimes vs part des tués par mode | Plotly | Écart annoté pour les usagers vulnérables |
| V6 | Pyramide des âges des tués par sexe | Plotly | Unité (nombre de tués), tranche 18-24 mise en évidence si pertinent |
| V7 *(bonus)* | Small multiples de l'indice de gravité par condition | Plotly (`facet_col`) | Même échelle Y pour tous les panneaux |
| V8 *(bonus)* | Courbe longue des tués 2005-2024 | Plotly | Bandes : 2020 (Covid), ruptures de série |
| V9 *(qualité)* | Heatmap de complétude variable × année | Plotly | Légende explicite |

**Une seule bibliothèque principale (Plotly)** pour la cohérence visuelle, style centralisé dans `utils/viz.py`.

### 7.4 Accessibilité (critère explicite du PDF)

- **Palette colorblind-safe** : séquentielle (viridis / cividis) pour les cartes et heatmaps ; qualitative de type Okabe-Ito pour les modes.
- **Pas d'information encodée uniquement par la couleur** : libellés directs.
- **Tous les axes titrés avec unité** (« nombre de tués », « tués pour 100 accidents », « heure de la journée »).
- **Texte alternatif** : un `st.caption` sous chaque graphique, qui décrit en une phrase ce qu'il montre.
- **Ton sobre** : c'est un sujet qui touche des vies. Pas de couleurs criardes ni d'icônes humoristiques. Les titres de chargement restent neutres.
- Test en thème clair **et** sombre.

---

## 8. Architecture technique

### 8.1 Structure du repo (suit la recommandation du PDF)

```
streamlit-road-safety/
├── app.py                    # point d'entrée, config, sidebar, appel des sections
├── sections/
│   ├── intro.py              # hook, définitions, KPI
│   ├── when.py               # Quand ?
│   ├── where.py              # Où ?
│   ├── who.py                # Qui ?
│   ├── conditions.py         # Dans quelles conditions ? (bonus)
│   ├── quality.py            # Qualité des données
│   └── conclusions.py        # Insights, limites, pistes
├── utils/
│   ├── io.py                 # load_tables() depuis data/processed
│   ├── prep.py               # lecture, harmonisation, jointures, variables dérivées
│   ├── aggregate.py          # construction des tables agrégées
│   ├── viz.py                # fonctions de graphiques au style unifié
│   └── constants.py          # libellés des codes BAAC, regroupements, couleurs, dep → région
├── scripts/
│   ├── download_data.py      # data.gouv → data/raw + MANIFEST.json
│   └── build_tables.py       # data/raw → data/processed (Parquet agrégés)
├── data/
│   ├── raw/                  # ignoré par git
│   └── processed/            # tables agrégées versionnées (quelques Mo)
├── assets/
│   └── departements.geojson  # si fond de carte validé
├── tests/
│   └── test_prep.py
├── requirements.txt
├── Makefile                  # make data / make tables / make run / make test
└── README.md
```

### 8.2 Principe clé : l'app ne manipule que des agrégats

Le pipeline `build_tables.py` produit des tables **pré-agrégées** :

| Table | Grain |
|---|---|
| `by_dep_year_month` | département × année × mois × milieu → accidents, tués, victimes |
| `by_hour_dow` | heure × jour de semaine × année × milieu → accidents, tués |
| `by_mode` | mode × gravité × année × milieu → victimes |
| `by_age_sex` | tranche d'âge × sexe × année → tués, victimes |
| `by_condition` | dimension × modalité × année → accidents, tués |
| `quality_report` | contrôles calculés une fois |

**Trois bénéfices d'un coup :**
1. **Performance** : l'app charge quelques Mo au lieu de centaines de milliers de lignes.
2. **Vie privée** : aucune donnée individuelle n'est déployée (cf. §10).
3. **Déploiement** : aucun risque de dépasser les limites mémoire de Streamlit Community Cloud.

### 8.3 Bonnes pratiques Streamlit

- `@st.cache_data` sur le chargement des tables et sur les filtrages coûteux (paramètres de filtre en arguments).
- Pas de `st.cache_resource` (pas de modèle, pas de connexion).
- **Une page unique** qui se lit de haut en bas : elle sert mieux un récit linéaire que plusieurs pages.

### 8.4 Contraintes de déploiement (Streamlit Community Cloud)

- Mémoire : environ 690 Mo minimum, 2,7 Go maximum selon la documentation (limites susceptibles de changer). Avec des agrégats, **aucun risque**.
- Les apps **hibernent** après une période sans trafic → **réveiller l'app avant la démo et avant la correction**, et le mentionner dans le README.
- Repo GitHub **public** requis pour le déploiement gratuit standard.

### 8.5 Tests (proportionnés)

**4 à 6 tests ciblés**, sur ce qui fausserait le récit s'il cassait :
1. `Num_Acc` est unique dans `caracteristiques`.
2. Aucun usager orphelin après jointure (ou nombre connu et documenté).
3. La jointure usagers ↔ véhicules **ne duplique pas** de lignes (nombre de lignes avant = après).
4. Le nombre de tués métropole 2024 calculé est cohérent avec le chiffre ONISR (tolérance à définir, cf. §9.3).
5. Chaque code de `grav`, `catv`, `lum`, `agg` a un libellé dans `constants.py`.
6. La somme des agrégats par département = total national.

---

## 9. Qualité des données et validation

Section **obligatoire** du dashboard (« missingness, duplicates, validation checks ») et cœur des 25 points « data work ».

### 9.1 Contrôles à afficher dans l'app

| Contrôle | Méthode | Affichage |
|---|---|---|
| Valeurs manquantes | % de manquants par variable × année (après conversion des codes « non renseigné ») | Heatmap V9 |
| Doublons | Doublons sur `Num_Acc` (caractéristiques) et sur la clé usager | Nombre (attendu : 0) |
| Intégrité référentielle | Usagers / véhicules / lieux sans accident correspondant | Nombre d'orphelins |
| Coordonnées | `lat`/`long` manquantes ou hors du territoire | % et nombre |
| Âges aberrants | `an_nais` manquant ou âge > 110 / < 0 | Nombre |
| Effet « usagers en fuite » (2021+) | Hausse des manquants sur sexe / âge / gravité | Annotation sur la heatmap |
| Blessés hospitalisés | Rupture 2018 / non labellisé depuis 2019 | Encadré d'avertissement |
| Fraîcheur | Date du snapshot | Footer |

### 9.2 Ruptures et particularités à documenter

- **Rupture de série des blessés hospitalisés en 2018** (cf. §3.4).
- **Nouveau format en 2019** : nouvelles variables et modalités.
- **Usagers en fuite intégrés à partir de 2021.**
- **2020** : confinements → baisse du trafic, donc des accidents. Toute comparaison avec 2020 doit être annotée.
- **Géolocalisation incomplète** : certains accidents ne sont pas précisément localisés.
- **Données occultées** pour la vie privée.

### 9.3 Validation par reproduction des chiffres officiels

Le meilleur argument de rigueur : **montrer que ton pipeline retrouve les chiffres publiés par l'ONISR**.

| Chiffre de référence | Valeur publiée | Source |
|---|---|---|
| Tués en France métropolitaine, 2024 | **3 193** | ONISR, bilan définitif 2024 |
| Tués métropole + outre-mer, 2024 | **3 432** | ONISR, bilan définitif 2024 |
| Part des hommes parmi les tués (métropole), 2024 | **77 %** | ONISR, bilan 2024 |
| Tués par million d'habitants (métropole), 2024 | **48** | ONISR, bilan 2024 (nécessite la population → seulement pour information) |
| Part des tués hors agglomération, 2024 | **60 %** (1 928 tués) | ONISR, bilan **provisoire** 2024 — à comparer avec prudence |

**Si ton calcul diffère** (ce qui est possible : la base open data peut différer légèrement de la base de bilan, ou ton filtre « métropole » peut être différent) : chercher pourquoi et **l'afficher dans l'app**. Un écart expliqué vaut mieux qu'un écart caché.

**Attention aux blessés** : les chiffres de blessés publiés par l'ONISR (ex. 235 600 blessés en 2024) sont des **estimations** corrigées par une méthode ONISR-Université Gustave Eiffel. Ils ne sont **pas** reproductibles à partir des blessés comptés dans le BAAC. Ne pas chercher à les retrouver ; expliquer la différence.

---

## 10. Éthique et vie privée

Le PDF demande explicitement d'agréger les données sur les personnes et d'éviter tout risque de ré-identification. Ce dataset décrit des **victimes**, dont des personnes décédées : c'est le point éthique principal du projet.

**Mesures prévues :**
1. **Aucune donnée individuelle déployée** : l'app ne contient que des agrégats (§8.2).
2. **Pas de carte par point des accidents mortels** avec date, âge ou sexe : la combinaison lieu + date + profil peut identifier une victime dans une petite commune.
3. **Seuil minimal d'affichage** : masquer ou regrouper les cellules avec moins de N tués (ex. N = 5) dans les croisements fins (département × tranche d'âge × sexe). Documenter le seuil.
4. **Ton neutre** : pas de sensationnalisme, pas de stigmatisation d'une catégorie d'usagers ; rappeler que la répartition des tués dépend aussi de l'exposition, inconnue ici.
5. **Rappel dans l'app** que l'ONISR occulte déjà certaines données pour la vie privée.

Ces mesures sont à **expliquer dans l'app et dans le README** : elles valent des points en narration et en communication.

---

## 11. Plan de réalisation par phases

**Estimation totale : 32 à 40 heures.** La phase données est plus lourde que pour un dataset déjà agrégé. Appliquer la loi de Hofstadter : prévoir **+30 % de marge** par phase. Les phases sont **séquentielles** : pas de dashboard avant un storyboard validé et des tables propres.

### Phase 0 — Vérifications bloquantes (1 h)

- [ ] Date limite, plateforme de dépôt, format du rapport, langue.
- [ ] Licence exacte sur la page data.gouv.
- [ ] Question à l'enseignant : fond de carte externe accepté ? (et population INSEE, si envisagée).
- [ ] Télécharger le guide de description ONISR (version 2025) et le guide de codification.
- [ ] Créer le repo GitHub public + environnement virtuel.

**Critère de fin :** les inconnues de §1 sont levées ; le guide des variables est en main.

### Phase 1 — Exploration (4-5 h)

- [ ] Télécharger 2019-2024 (4 fichiers × 6 ans) dans un notebook.
- [ ] Vérifier séparateurs, encodages, noms de colonnes, codes manquants, fichier par fichier.
- [ ] Construire une jointure de test et vérifier l'absence de duplication.
- [ ] Calculer les tués métropole 2024 → comparer à 3 193.
- [ ] Tester rapidement H1 à H4 : lesquelles tiennent ?

**Critère de fin :** tu sais lire les 24 fichiers sans erreur, tu retrouves (à peu près) le chiffre ONISR, et tu connais les 3 insights réels.

### Phase 2 — Storyboard (2-3 h)

- [ ] Réécrire les phrases-insights à partir de ce que la phase 1 a montré.
- [ ] Croquis de chaque section (visuel + interaction + question).
- [ ] Faire relire par une personne non spécialiste : comprend-elle le fil ?

**Critère de fin :** storyboard exportable (PDF/image), rendu tel quel ; chaque graphique répond à une question.

### Phase 3 — Pipeline de données (6-8 h)

- [ ] `download_data.py` + `MANIFEST.json`.
- [ ] `utils/constants.py` : libellés de tous les codes utilisés, regroupements, départements → régions.
- [ ] `utils/prep.py` : lecture robuste, harmonisation, conversion des manquants, jointures, variables dérivées (§6.6).
- [ ] `utils/aggregate.py` + `build_tables.py` : tables agrégées (§8.2), seuil de confidentialité (§10).
- [ ] `tests/test_prep.py` : tests de §8.5.
- [ ] Documenter chaque choix (commentaires + section README).

**Critère de fin :** `make data && make tables && make test` passe depuis un clone propre.

### Phase 4 — Squelette de l'app + MVP (6-8 h)

- [ ] `app.py` + sidebar + KPI header branchés sur les filtres.
- [ ] V1 (heatmap), V3 (carte), V5 (dumbbell) — **3 visuels interactifs minimum, dont une carte**.
- [ ] Textes de chaque section repris du storyboard.

**Critère de fin (MVP) :** l'app remplit **toutes** les exigences techniques minimales de l'énoncé. Le projet est rendable à ce stade.

### Phase 5 — Approfondissements (5-6 h)

- [ ] V2, V4, V6.
- [ ] Section qualité des données (§9) avec V9.
- [ ] Section éthique (§10) et conclusions + limites.
- [ ] Annotations (2020, ruptures, fuyards).
- [ ] *Bonus si le temps le permet :* V7 (conditions), V8 (série longue 2005-2024).

**Critère de fin :** le récit complet se lit de haut en bas sans explication orale.

### Phase 6 — Finitions UX et accessibilité (2-3 h)

- [ ] Palette accessible, axes et unités partout, `st.caption` en texte alternatif.
- [ ] Infobulles de définition (`help=`).
- [ ] Test thème clair / sombre, test en fenêtre étroite.
- [ ] Supprimer tout contrôle ou graphique qui n'apporte rien.

### Phase 7 — Packaging et déploiement (2-3 h)

- [ ] `requirements.txt` figé (`pip freeze` dans un venv propre ; ne pas recopier des versions au hasard).
- [ ] Test **depuis un clone vierge** dans un nouvel environnement.
- [ ] Déploiement sur Streamlit Community Cloud ; vérification de l'URL en navigation privée.
- [ ] README complet (§13).

### Phase 8 — Vidéo et rendu (3-4 h)

- [ ] Script chronométré (§12), répétition, enregistrement, hébergement.
- [ ] Export du storyboard.
- [ ] Zip `StApp26_<n°>_<NOM>_BIA.zip`.
- [ ] Vérification de tous les liens depuis un autre appareil.
- [ ] Checklist finale (§15).

### Calendrier type

À ajuster dès que la date limite est connue. Exemple sur 3 semaines à ~12 h/semaine :

| Semaine | Phases | Jalon |
|---|---|---|
| S1 | 0, 1, 2 | Lecture des fichiers maîtrisée + storyboard terminé |
| S2 | 3, 4 | **MVP rendable** déployé |
| S3 | 5, 6, 7, 8 | Rendu complet, 2 jours de marge avant la deadline |

**Règle :** le MVP déployé doit exister **au plus tard à mi-parcours**. Tout le reste est de l'amélioration, pas une condition du rendu.

---

## 12. Vidéo de démo

### 12.1 Contraintes

- **2 à 4 minutes** (viser 3 min 30 pour garder une marge).
- Langue : ⚠️ à confirmer. Si anglais : **script écrit en phrases simples**, lu, pas improvisé.
- Hébergement : YouTube non répertorié ou Google Drive en lecture publique. Tester le lien en navigation privée.

### 12.2 Script type (≈ 3 min 30)

| Temps | Écran | Contenu |
|---|---|---|
| 0:00–0:20 | Intro + KPI | Hook : le chiffre clé, la question « quand un accident devient-il mortel ? » |
| 0:20–0:40 | Encadré définitions | Source BAAC, définition d'un tué, indice de gravité |
| 0:40–1:15 | Heatmap « Quand ? » | Insight 1 ; montrer la bascule accidents → gravité |
| 1:15–1:55 | Carte « Où ? » | Insight 2 ; montrer que la carte s'inverse |
| 1:55–2:35 | « Qui ? » | Insight 3 ; filtrer un mode de déplacement |
| 2:35–3:05 | Qualité + éthique | Contrôles, validation sur les chiffres ONISR, agrégation |
| 3:05–3:30 | Conclusions | Ce qu'on peut dire, ce qu'on ne peut pas dire (exposition) |

**Montrer les interactions en action**, pas seulement les décrire : c'est ce que la vidéo évalue.

---

## 13. README et packaging

### 13.1 Plan du README

1. **Titre + une phrase** de description + lien de l'app + lien de la vidéo.
2. **Question et public** (§4).
3. **Données** : nom, producteur (ONISR), URL data.gouv, licence, date du snapshot, années utilisées, citation.
4. **Méthode** : périmètre (2019-2024, métropole), jointures, variables dérivées, indice de gravité, seuil de confidentialité.
5. **Lancer le projet** :
   ```bash
   git clone <repo>
   cd streamlit-road-safety
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   make data      # télécharge les CSV bruts (optionnel : les tables agrégées sont versionnées)
   make tables    # reconstruit data/processed
   make run       # streamlit run app.py
   ```
6. **Structure du code** (§8.1).
7. **Qualité des données, limites et éthique** (§9, §10, §14).
8. **Pistes d'amélioration** (données d'exposition, population, série longue).
9. **Licences** : code (au choix, ex. MIT) **≠** données (licence data.gouv) — le PDF demande de distinguer les deux.

### 13.2 Citation des données

```
Source : ONISR — Bases de données annuelles des accidents corporels de la circulation
routière, années 2005 à 2024, data.gouv.fr, <licence>, consulté le JJ/MM/AAAA.
Données retraitées par l'auteur : harmonisation, jointures, agrégation.
```

### 13.3 Contenu du zip

```
StApp26_<n°>_<NOM>_BIA.zip
├── README.md
├── app.py, sections/, utils/, scripts/, tests/
├── requirements.txt, Makefile
├── data/processed/*.parquet          (agrégats légers)
├── DATA_LINK.txt                      (URL data.gouv + MANIFEST)
└── storyboard.pdf                     (si non fourni par lien seulement)
```

Les CSV bruts **ne vont pas dans le zip** (l'énoncé demande un script de téléchargement plutôt que de gros fichiers bruts).

---

## 14. Risques et pièges

| Risque | Probabilité | Impact | Parade |
|---|---|---|---|
| Deadline proche, inconnue | Élevée tant que non vérifiée | Élevé | Phase 0 immédiate |
| Formats hétérogènes entre fichiers | **Élevée** | Moyen (temps) | Périmètre 2019-2024 ; lecture fichier par fichier en phase 1 |
| Jointure qui duplique les lignes | Moyenne | **Élevé** (chiffres faux) | Test dédié ; validation sur le chiffre ONISR |
| Conclusion sur un « risque » sans données d'exposition | **Élevée** | Élevé (narration + communication) | Parler de répartition et de gravité, jamais de risque par km |
| Série sur les blessés hospitalisés à cheval sur 2018 | Moyenne | Moyen | Travailler sur les tués ; avertissement visible |
| Ré-identification via cartes ou croisements fins | Faible si agrégé | Élevé (éthique) | Agrégats uniquement, seuil de confidentialité |
| Sujet « classique » repris par d'autres étudiants | Élevée | Moyen | Angle différenciant : contraste fréquence vs gravité, indice de gravité |
| Snapshot modifié par la publication 2025 | Moyenne | Faible | Snapshot daté + MANIFEST |
| Sur-ingénierie (pipeline, tests, architecture) | **Élevée** vu ton profil | Moyen (temps perdu sur 15 pts) | Structure §8.1, rien de plus avant le MVP |
| Fond de carte externe refusé | Faible | Moyen | Alternative : carte de densité à partir des coordonnées du BAAC |
| App en hibernation lors de la correction | Moyenne | Moyen | La réveiller avant ; mention dans le README |
| Trop de contrôles / graphiques | Moyenne | Moyen (UX) | Règle : chaque élément répond à une question du storyboard |

---

## 15. Checklist finale (mapping barème)

### Narration & cadrage (25 pts)
- [ ] Public cible nommé explicitement dans l'app
- [ ] Hook → contexte → insights → implications, dans cet ordre
- [ ] Une phrase-insight en tête de chaque section
- [ ] Storyboard rendu et aligné avec l'app
- [ ] Le contraste fréquence vs gravité est le fil rouge visible

### Données (25 pts)
- [ ] Source, licence, date du snapshot et années utilisées cités
- [ ] Jointures des 4 tables documentées et testées
- [ ] Harmonisation des formats documentée
- [ ] Variables dérivées expliquées (dont l'indice de gravité)
- [ ] Section qualité : manquants, doublons, orphelins, aberrations
- [ ] Reproduction du nombre de tués ONISR 2024

### Visualisation & UX (25 pts)
- [ ] ≥ 3 visuels interactifs avec tooltips
- [ ] Au moins une carte
- [ ] KPI liés aux filtres
- [ ] Sidebar : période, territoire, région, métrique
- [ ] Annotations (2020, ruptures, fuyards)
- [ ] Axes et unités sur tous les graphiques
- [ ] Palette accessible + texte alternatif

### Code (15 pts)
- [ ] Structure modulaire `sections/` + `utils/` + `scripts/`
- [ ] `st.cache_data` utilisé
- [ ] App basée sur des agrégats pré-calculés
- [ ] `requirements.txt` figé
- [ ] Fonctionne depuis un clone propre
- [ ] Script de téléchargement + MANIFEST

### Communication (10 pts)
- [ ] Vidéo de 2 à 4 min, interactions montrées
- [ ] Limites exposées honnêtement (exposition, blessés hospitalisés, fuyards, géolocalisation)
- [ ] Section éthique
- [ ] README clair

### Rendu
- [ ] Zip correctement nommé
- [ ] Tous les liens testés en navigation privée
- [ ] App réveillée juste avant la date de correction

---

## 16. Questions ouvertes

| Question | Qui tranche | Bloquant ? |
|---|---|---|
| Date limite de rendu | Moodle / enseignant | **Oui** |
| Plateforme de dépôt | Moodle / enseignant | Oui (fin de projet) |
| Forme du « rapport » | Enseignant | Non (README par défaut) |
| Langue de l'app et de la vidéo | Enseignant | Non (anglais par défaut) |
| Fond de carte externe accepté ? | Enseignant | Non (alternative : carte de densité) |
| Données INSEE de population acceptées ? | Enseignant | Non (l'indice de gravité suffit) |
| Licence exacte du dataset | Toi (page data.gouv) | Oui pour le README |
| Quelles hypothèses H1-H4 tiennent ? | Les données (phase 1) | Non — oriente le récit |

---

## 17. Sources

**Dataset et documentation**
- data.gouv.fr — Bases de données annuelles des accidents corporels de la circulation routière, 2005 à 2024 — https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024
- ONISR — page Open Data (avertissements sur les blessés hospitalisés) — https://www.onisr.securite-routiere.gouv.fr/outils-statistiques/open-data
- ONISR — Description des bases de données annuelles 2005-2023 (FR, oct. 2024) — https://www.onisr.securite-routiere.gouv.fr/sites/default/files/2024-10/Description%20des%20bases%20de%20donn%C3%A9es%20annuelles.pdf
- ONISR — Description des bases de données annuelles 2005-2024 (EN, oct. 2025) — https://www.onisr.securite-routiere.gouv.fr/sites/default/files/2025-10/Description%20des%20bases%20de%20donn%C3%A9es%20annuelles%20en-EN.pdf
- ONISR — Indicateurs labellisés — https://www.onisr.securite-routiere.gouv.fr/outils-statistiques/indicateurs-labellises

**Chiffres de référence pour la validation**
- ONISR — Bilan 2024 de la sécurité routière — https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere
- ONISR — Accidentalité routière 2024, bilan provisoire (30/01/2025) — https://www.onisr.securite-routiere.gouv.fr/sites/default/files/2025-01/2025%2001%2030_ONISR_Accidentalit%C3%A9_Bilan_provisoire_2024_v8ter.pdf
- ONISR — Accidentalité routière 2025 (mai 2026) — https://www.onisr.securite-routiere.gouv.fr/sites/default/files/2026-05/20260529_Accidentalit%C3%A9_Routi%C3%A8re_2025.pdf

**Streamlit**
- Docs Streamlit — Manage your app (limites de ressources, hibernation) — https://docs.streamlit.io/streamlit-community-cloud/get-started/manage-your-app
- Docs Streamlit (général) — https://docs.streamlit.io/

**Storytelling et visualisation (référencés dans le PDF du projet)**
- FT Visual Vocabulary, Data Viz Society, *Evergreen Data*, Plotly (https://plotly.com/python/), Altair (https://altair-viz.github.io/)
