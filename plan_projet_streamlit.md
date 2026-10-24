lis # Projet Streamlit — Data Storytelling (EFREI, BIA)

> **Dossier de cadrage et plan de réalisation complet**
> Projet individuel `#EFREIDataStories2026` — Enseignant : Mano Joseph Mathew
> Rédigé le 24/10/2026. Les points marqués **⚠️ À VÉRIFIER** n'ont pas pu être confirmés et doivent l'être avant de s'engager.

---

## Sommaire

1. [Ce qu'il faut rendre](#1-ce-quil-faut-rendre)
2. [Barème et ce qu'il implique](#2-barème-et-ce-quil-implique)
3. [Choix du dataset](#3-choix-du-dataset)
4. [Cadrage : question, public, récit](#4-cadrage--question-public-récit)
5. [Storyboard détaillé](#5-storyboard-détaillé)
6. [Spécifications des données](#6-spécifications-des-données)
7. [Spécifications du dashboard](#7-spécifications-du-dashboard)
8. [Architecture technique](#8-architecture-technique)
9. [Qualité des données et validation](#9-qualité-des-données-et-validation)
10. [Plan de réalisation par phases](#10-plan-de-réalisation-par-phases)
11. [Vidéo de démo](#11-vidéo-de-démo)
12. [README et packaging](#12-readme-et-packaging)
13. [Risques et pièges](#13-risques-et-pièges)
14. [Checklist finale (mapping barème)](#14-checklist-finale-mapping-barème)
15. [Questions ouvertes](#15-questions-ouvertes)
16. [Sources](#16-sources)

---

## 1. Ce qu'il faut rendre

| # | Livrable | Détail | Source |
|---|---|---|---|
| 1 | **App Streamlit déployée** | Récit cohérent + composants interactifs, URL publique (Streamlit Community Cloud ou équivalent) | Énoncé + PDF |
| 2 | **Vidéo de démo** | 2 à 4 minutes, parcours du récit et des interactions, à fournir sous forme de lien | Énoncé + PDF |
| 3 | **Zip** `StApp26_<n°étudiant>_<NOM>_BIA.zip` | Lien/dataset, README, code Python | Énoncé |
| 4 | **Lien du repo** | Code + **rapport** | PDF uniquement |
| 5 | **Storyboard** | Lien à fournir | PDF uniquement |

**Inconnues (⚠️ À VÉRIFIER sur Moodle / auprès de l'enseignant) :**
- Date limite de rendu.
- Plateforme de dépôt.
- Forme attendue du « rapport » (README étoffé suffisant ? PDF séparé ?).
- Langue de la vidéo et de l'app (l'énoncé est en anglais → probablement anglais).

---

## 2. Barème et ce qu'il implique

| Critère | Pts | Ce qui est réellement évalué | Où mettre l'effort |
|---|---|---|---|
| Narration & cadrage | **25** | Public clair, questions, takeaways, alignement avec le storyboard | Storyboard **avant** le code ; une phrase-insight par section |
| Travail sur les données | **25** | Sourcing, nettoyage, validation, feature engineering | Documenter chaque transformation ; reproduire un chiffre officiel |
| Visualisation & UX | **25** | Types de graphiques adaptés, annotations, légendes, couleurs, interactions | Peu de graphiques mais justes ; annotations ; pas de contrôle inutile |
| Qualité du code | **15** | Structure, cache, perf, reproductibilité, doc | Structure simple + `st.cache_data` + `requirements.txt` figé |
| Communication | **10** | Clarté du rapport, vidéo, transparence sur les limites | Section « limites » honnête ; vidéo scriptée |

**Conséquence :** 75 % des points portent sur le récit, les données et la visualisation. Le code ne vaut que 15 points. **Pas de dbt, pas d'Airflow, pas de tests exhaustifs** : un pipeline pandas propre et caché suffit. C'est un livrable académique cadré, pas un produit.

---

## 3. Choix du dataset

### 3.1 Dataset retenu : Eurostat `gov_10a_taxag`

**« Main national accounts tax aggregates »**

| Attribut | Valeur |
|---|---|
| Producteur | Eurostat |
| Code / DOI | `gov_10a_taxag` — DOI `10.2908/gov_10a_taxag` |
| Contenu | Recettes fiscales et cotisations sociales détaillées, par type d'impôt et par sous-secteur des administrations publiques (table 0900 du programme de transmission SEC 2010) |
| Unités | Euros, monnaie nationale, **% du PIB**, % du total |
| Couverture géographique | UE, zone euro, États membres, Islande, Norvège, Suisse |
| Couverture temporelle | 1995 → 2025 (dernière mise à jour vue : 21/07/2026) |
| Prix | Prix courants |
| Granularité | Annuelle × pays × type d'impôt (93 indicateurs) × sous-secteur (7) |
| Volume | ~83 000 séries — mais quelques Mo une fois filtré sur `% PIB` |
| Licence | **CC BY 4.0** (politique de réutilisation Eurostat) — citer la source, signaler les modifications |
| Calendrier de publication | Publication annuelle complète **fin octobre** |

### 3.2 Pourquoi ce dataset

- **Coche toutes les cases de l'énoncé** : dimension temporelle (30 ans), dimension géographique (≈30 pays → carte), dimension catégorielle (types d'impôts → small multiples / barres empilées).
- **Taille raisonnable**, schéma propre, métadonnées documentées (fichier ESMS).
- **Sujet qui intéresse un public large** et sur lequel circulent beaucoup d'affirmations approximatives → bon matériau de storytelling.
- **Données agrégées** : pas de risque de ré-identification (point « ethics » du PDF réglé d'office).
- **Possibilité de valider** : Eurostat et l'INSEE publient des chiffres de référence qu'on peut reproduire → preuve de rigueur pour la partie « data work ».
- Cohérent avec ton intérêt pour l'analyse fiscale France/Europe.

### 3.3 Alternatives écartées

| Candidat | Raison de l'écart |
|---|---|
| OCDE Revenue Statistics (`REV`) | Très riche mais **pas sur un portail autorisé** |
| INSEE — taux de prélèvements obligatoires | Bon, mais centré France ; comparaison européenne moins détaillée |
| EEA — intensité CO₂ de l'électricité | Les tables trouvées datent de 2020, données anciennes |
| Thèmes « exemples » du PDF (qualité de l'air, mix électrique…) | Viables, mais sujets très repris par les autres étudiants → moins différenciant |

### 3.4 ⚠️ À VÉRIFIER avant de s'engager

1. **Référencement sur data.europa.eu** : je n'ai pas pu confirmer la fiche. Les données Eurostat y sont en principe moissonnées, mais il faut le vérifier : rechercher `gov_10a_taxag` sur https://data.europa.eu, noter l'URL de la fiche, la licence affichée et le lien de téléchargement. **Si la fiche n'existe pas, demander à l'enseignant si un téléchargement direct via l'API Eurostat est accepté.**
2. **Nouvelle publication fin octobre 2026** : Eurostat publie la mise à jour complète fin octobre. Si le snapshot est pris avant, l'année 2025 risque d'être incomplète. **Recommandation : figer le snapshot après la publication de fin octobre**, et le dater dans le README.

---

## 4. Cadrage : question, public, récit

### 4.1 Question centrale

> **La France est-elle vraiment une exception fiscale en Europe — et de quoi est fait l'écart ?**

### 4.2 Sous-questions (une par section du dashboard)

1. Quel est le niveau des prélèvements en France, comparé à l'UE et aux autres pays ? *(classement)*
2. Comment cet écart a-t-il évolué depuis 1995 ? *(avant/après dans le temps)*
3. Où se situe l'écart : impôts sur la consommation, sur le revenu, cotisations sociales ? *(composition)*
4. Qui collecte : État central, collectivités, sécurité sociale ? *(répartition par sous-secteur — optionnel)*

### 4.3 Public cible

**Un citoyen ou étudiant curieux, non spécialiste**, qui a entendu « la France est championne d'Europe des impôts » et veut savoir ce que ça veut dire réellement. Conséquence : vocabulaire simple, définitions en infobulle (`help=`), pas de jargon SEC 2010 visible sans explication.

### 4.4 Hypothèse à tester (et non à démontrer)

> L'écart de la France avec la moyenne européenne viendrait surtout du **financement de la protection sociale** (cotisations sociales), plus que d'un niveau d'impôt uniformément élevé.

C'est une hypothèse. **Les données décideront.** Si elles disent autre chose, le récit change. Ne pas tordre les graphiques pour la confirmer.

### 4.5 Arc narratif (structure imposée par le PDF)

| Étape | Contenu | Exemple de phrase |
|---|---|---|
| **Hook** | Le chiffre qui accroche | « En 2024, les prélèvements représentent 45,3 % du PIB en France, contre 40,4 % dans l'UE. » (INSEE, d'après Eurostat) |
| **Contexte** | Définition + trajectoire | Ce qu'est le « taux de prélèvements », comment il se calcule, comment il a évolué |
| **Insights** | 2 à 3 constats démontrés | Rang, évolution de l'écart, composition de l'écart |
| **Implications** | Ce que ça permet de dire… et pas | Un taux élevé ≠ « trop d'impôts » : il reflète des choix de financement (public vs privé) ; les données ne disent rien de l'efficacité de la dépense |

### 4.6 Ce que le dashboard ne prétend PAS faire

- **Aucune affirmation causale** (« les impôts causent X »). L'énoncé demande explicitement d'éviter de surinterpréter la causalité. Les données agrégées par pays ne le permettent pas.
- **Aucun jugement politique** (« trop » / « pas assez » d'impôts). On décrit et on compare.
- Pas de conclusion sur le pouvoir d'achat individuel : le taux en % du PIB ne dit rien de la charge supportée par un ménage donné.

---

## 5. Storyboard détaillé

À produire **avant tout code** (papier, Figma, Excalidraw ou slides). Le rendu du storyboard est demandé et son alignement avec l'app est noté.

| # | Section | Phrase-insight (titre) | Visuel | Interaction | Question à laquelle il répond |
|---|---|---|---|---|---|
| 0 | **Intro** | « La France prélève près de 5 points de PIB de plus que la moyenne européenne. » *(à confirmer par les données)* | KPI header + texte d'accroche | Aucune | Pourquoi ça compte ? |
| 1 | **Où en est-on ?** | « La France est dans le trio de tête européen. » | **Carte choroplèthe** de l'Europe + **classement en barres** | Curseur d'année | Quel est le niveau relatif de chaque pays ? |
| 2 | **Comment en est-on arrivé là ?** | « L'écart avec l'UE est stable / s'est creusé / s'est réduit depuis 1995. » *(selon données)* | **Courbes** France vs UE vs pays choisis + **courbe de l'écart** | Sélection de pays, période | L'écart est-il structurel ou récent ? |
| 3 | **De quoi est fait l'écart ?** | « L'essentiel de l'écart vient de [catégorie]. » | **Barres empilées** par catégorie (FR vs UE) + **small multiples** par catégorie dans le temps | Choix des pays comparés | Quelle composante explique l'écart ? |
| 4 | **Qui collecte ?** *(bonus)* | « La sécurité sociale collecte X % du total en France contre Y % en moyenne. » | Barres 100 % par sous-secteur | Choix de pays | Qui perçoit l'argent ? |
| 5 | **Qualité des données** | « Les données sont complètes à X % ; les écarts de définition existent. » | Heatmap de complétude pays × année + tableau de contrôles | Aucune | Peut-on faire confiance à ces chiffres ? |
| 6 | **Conclusions** | Synthèse des 3 constats + limites + pistes | Texte + rappel des chiffres clés | Aucune | Que retenir ? Qu'est-ce qu'on ne sait pas ? |

**Règle :** chaque graphique doit répondre à une question listée ici. Un graphique qui ne répond à rien est supprimé.

---

## 6. Spécifications des données

### 6.1 Dimensions du dataset

| Dimension | Code | Valeurs utiles |
|---|---|---|
| Fréquence | `freq` | `A` (annuel) |
| Unité | `unit` | `PC_GDP` (% du PIB) — principal ; `MIO_EUR` pour les montants ; `PC_TOT` pour la structure |
| Secteur | `sector` | `S13_S212` (APU + institutions UE) ou `S13` (APU) — voir 6.3 ; `S1311`, `S1313`, `S1314` pour la section « qui collecte » |
| Indicateur | `na_item` | voir 6.2 |
| Pays | `geo` | 27 pays UE + agrégats + IS, NO, CH |

### 6.2 Indicateurs (`na_item`) à utiliser

| Code | Libellé | Usage |
|---|---|---|
| `D2_D5_D91_D61_M_D995` | Total des recettes d'impôts et cotisations sociales (y c. cotisations imputées), net des montants non recouvrables | **Indicateur principal** (taux de prélèvements) |
| `D2_D5_D91` | Total des recettes fiscales (hors cotisations) | Comparaison « impôts seuls » |
| `D2` | Impôts sur la production et les importations | Catégorie « consommation / production » |
| `D211` | TVA | Détail optionnel |
| `D5` | Impôts courants sur le revenu, le patrimoine, etc. | Catégorie « revenu et patrimoine » |
| `D91` | Impôts en capital | Catégorie « capital » (faible, à regrouper éventuellement) |
| `D61` | Cotisations sociales nettes | Catégorie « cotisations sociales » |
| `D995` | Montants évalués mais non recouvrables | À soustraire, pour la cohérence des sommes |

⚠️ **À VÉRIFIER** : lister les codes réellement présents (`df['na_item'].unique()`) avant d'écrire le code de regroupement. La liste ci-dessus vient de la documentation et de DBnomics, pas d'un téléchargement effectif.

### 6.3 Choix de définition (décision à documenter)

Les chiffres de « taux de prélèvements » **divergent selon la source** :
- Pour 2022, l'INSEE publie 45,4 % pour la France, Eurostat environ 48 %, à cause de différences de périmètre (cotisations imputées, crédits d'impôt, etc.).

**Décision recommandée :**
- Utiliser **uniquement Eurostat**, avec un indicateur et un secteur fixes, pour tous les pays.
- Expliquer la définition dans l'app (encadré « Définition » dans l'intro).
- **Ne jamais mélanger** un chiffre INSEE et un chiffre Eurostat dans un même graphique.
- Valider le choix du secteur (`S13` vs `S13_S212`) en vérifiant lequel reproduit le chiffre UE officiel (40,4 % en 2024, cf. §9.3).

### 6.4 Accès aux données

**Option A — Package Python `eurostat` (recommandé, le plus simple)**

```python
import eurostat

df = eurostat.get_data_df(
    "gov_10a_taxag",
    filter_pars={
        "unit": ["PC_GDP", "MIO_EUR"],
        "sector": ["S13", "S13_S212", "S1311", "S1313", "S1314"],
        "startPeriod": "1995",
    },
)
```

**Option B — API Eurostat directe**
- Base : `https://ec.europa.eu/eurostat/api/dissemination`
- Endpoint « Statistics » : JSON-stat 2.0, filtres en paramètres d'URL.
- Endpoint SDMX 2.1 : TSV, SDMX-CSV ou JSON-stat.
- ⚠️ À VÉRIFIER : syntaxe exacte des requêtes dans la doc officielle (lien en §16).

**Option C — Téléchargement manuel** depuis le databrowser Eurostat ou la fiche data.europa.eu, fichier CSV commité dans `data/raw/` avec la date.

**Dans tous les cas :**
- Script de téléchargement `scripts/download_data.py` qui écrit un **snapshot daté** en Parquet dans `data/`.
- L'app lit **le snapshot local**, pas l'API à chaque lancement (sinon : dépendance réseau, lenteur, et chiffres qui changent entre ta démo et la correction).
- Le snapshot filtré pèse quelques Mo : il peut être commité dans le repo et mis dans le zip (l'énoncé demande d'éviter les gros fichiers bruts, pas un petit fichier filtré).

### 6.5 Fond de carte

**Recommandé : Plotly `choropleth` avec codes ISO-3**, sans GeoPandas.
- `locationmode="ISO-3"` + `scope="europe"` → aucune géométrie à télécharger.
- Nécessite un mapping des codes Eurostat (ISO-2) vers ISO-3, avec **une exception connue : Eurostat utilise `EL` pour la Grèce** (ISO = `GR` / `GRC`).
- Avantage : zéro dépendance géo, déploiement plus léger.

**Alternative : géométries GISCO** (Eurostat) au format GeoJSON, via le dépôt `Nuts2json` (niveau NUTS 0 = pays), schéma d'URL `/<ANNÉE>/<PROJECTION>/<ÉCHELLE>/<TYPE>_<NIVEAU>.json`. Plus joli (projection européenne), mais une dépendance de plus. **À garder pour plus tard si le temps le permet.**

### 6.6 Feature engineering prévu

| Variable dérivée | Calcul | Pourquoi |
|---|---|---|
| `gap_vs_eu` | taux pays − taux UE27, en points | Mesure directe de « l'exception » |
| `rank` | Rang du pays dans l'UE27 pour une année | KPI et classement |
| `category` | Regroupement des `na_item` en 4 catégories (production/consommation, revenu/patrimoine, capital, cotisations sociales) | Lisibilité pour un non-spécialiste |
| `gap_contribution` | Écart FR − UE par catégorie | Répond à « de quoi est fait l'écart » |
| `share_of_total` | Part de chaque catégorie dans le total | Comparer les structures indépendamment du niveau |
| `is_provisional` | Flag issu des métadonnées (`p`) | Transparence sur les dernières années |
| `region_group` *(optionnel)* | Nordiques / Ouest / Sud / Est | Small multiples par groupe de pays |

---

## 7. Spécifications du dashboard

### 7.1 Sidebar (contrôles)

| Contrôle | Type | Valeur par défaut | Impacte |
|---|---|---|---|
| Période | `st.slider` (plage d'années) | 1995 → dernière année complète | Courbes, KPI |
| Année de référence | `st.select_slider` | Dernière année complète | Carte, classement, composition, KPI |
| Pays comparés | `st.multiselect` | France, Allemagne, Italie, Espagne, Suède | Courbes, composition |
| Pays focal | `st.selectbox` | France | KPI, écart |
| Catégorie d'impôt | `st.radio` | Total | Carte, classement |
| Inclure hors UE (IS, NO, CH) | `st.toggle` | Non | Carte, classement |

**Règle du PDF :** chaque contrôle doit changer quelque chose d'utile au récit. Si un contrôle ne change rien d'intéressant → supprimé.

### 7.2 KPI header (réagit aux filtres)

| KPI | Valeur | Delta |
|---|---|---|
| Taux du pays focal | X % du PIB | vs année précédente |
| Taux UE27 | Y % du PIB | vs année précédente |
| Écart pays − UE | +Z pts | vs début de période |
| Rang dans l'UE27 | n/27 | vs début de période |

### 7.3 Visuels (≥ 3 interactifs exigés — 6 prévus)

| # | Type | Bibliothèque | Annotations obligatoires |
|---|---|---|---|
| V1 | Carte choroplèthe Europe | Plotly | Légende en % du PIB, source en bas |
| V2 | Barres horizontales classées | Plotly | Ligne de référence = moyenne UE ; pays focal mis en couleur |
| V3 | Courbes multi-pays | Plotly | Bandes / marqueurs crise 2008-2009 et Covid 2020 |
| V4 | Courbe de l'écart pays − UE | Plotly | Ligne zéro ; valeur min/max annotée |
| V5 | Barres empilées par catégorie | Plotly | Libellés de catégories en clair, pas les codes SEC |
| V6 | Small multiples par catégorie | Plotly (`facet_col`) ou Altair | Axes Y comparables (même échelle) |
| V7 *(qualité)* | Heatmap de complétude pays × année | Plotly | Légende explicite |

**Choisir une seule bibliothèque principale (Plotly) pour la cohérence visuelle**, et centraliser le style dans `utils/viz.py`.

### 7.4 Accessibilité (critère explicite du PDF)

- **Palette colorblind-safe** (ex. viridis / cividis pour la carte ; palette qualitative type Okabe-Ito pour les pays).
- Ne jamais encoder l'information **uniquement par la couleur** : libellés directs sur les courbes.
- **Tous les axes titrés avec unité** (« % du PIB », « points de % »).
- **Texte alternatif** : un `st.caption` sous chaque graphique, qui décrit en une phrase ce qu'il montre.
- Contraste suffisant en thème clair **et** sombre (tester les deux).

### 7.5 Bonus optionnel : « what-if »

Un curseur : *« Si la France avait la structure fiscale moyenne de l'UE pour [catégorie], son taux serait de… »*. C'est un simple recalcul arithmétique, à **hypothèses documentées**. **Uniquement si le MVP est fini.** Ne pas présenter comme une prévision.

---

## 8. Architecture technique

### 8.1 Structure du repo (suit la recommandation du PDF)

```
streamlit-tax-europe/
├── app.py                    # point d'entrée, config, sidebar, appel des sections
├── sections/
│   ├── intro.py              # hook, définition, KPI
│   ├── overview.py           # carte + classement
│   ├── deep_dives.py         # évolution, composition, sous-secteurs
│   ├── quality.py            # qualité des données
│   └── conclusions.py        # insights, limites, pistes
├── utils/
│   ├── io.py                 # load_data() depuis le snapshot local
│   ├── prep.py               # nettoyage, regroupements, variables dérivées
│   ├── viz.py                # fonctions de graphiques au style unifié
│   └── constants.py          # codes na_item, mapping catégories, ISO2→ISO3, couleurs
├── scripts/
│   └── download_data.py      # téléchargement API → snapshot daté
├── data/
│   └── gov_10a_taxag_2026-11-XX.parquet
├── assets/
├── tests/
│   └── test_prep.py          # 3-5 tests sur les transformations critiques
├── requirements.txt
├── Makefile                  # make data / make run / make test
└── README.md
```

### 8.2 Bonnes pratiques Streamlit

- `@st.cache_data` sur le chargement **et** sur les agrégations coûteuses (avec les paramètres de filtre en arguments).
- **Pré-agréger** dans `prep.py` : l'app ne manipule que des tables déjà prêtes (format long, filtré `PC_GDP`).
- Pas de `st.cache_resource` nécessaire (pas de modèle, pas de connexion BDD).
- Navigation : une seule page avec sections et ancres, ou `st.navigation` / pages multiples. **Une page unique qui se lit de haut en bas sert mieux un récit linéaire.**

### 8.3 Contraintes de déploiement (Streamlit Community Cloud)

- Mémoire : environ 690 Mo minimum, 2,7 Go maximum selon la doc (limites susceptibles de changer). Avec quelques Mo de données, **aucun risque**.
- Les apps **hibernent** après une période sans trafic → **réveiller l'app avant la démo et avant la correction**, et le mentionner dans le README.
- Repo GitHub **public** requis pour le déploiement gratuit standard.

### 8.4 Tests (proportionnés)

Pas de suite exhaustive. **3 à 5 tests ciblés** sur ce qui, s'il casse, fausse le récit :
1. La somme des catégories ≈ le total (à une tolérance près).
2. Le taux UE27 calculé pour l'année de référence reproduit le chiffre officiel Eurostat.
3. Aucun doublon (pays, année, indicateur).
4. Le mapping ISO-2 → ISO-3 couvre tous les pays affichés (dont `EL` → `GRC`).

---

## 9. Qualité des données et validation

Section **obligatoire** du dashboard (« missingness, duplicates, validation checks ») et cœur des 25 points « data work ».

### 9.1 Contrôles automatiques à afficher dans l'app

| Contrôle | Méthode | Affichage |
|---|---|---|
| Valeurs manquantes | % de NaN par pays × année × catégorie | Heatmap + tableau des trous |
| Doublons | `df.duplicated(['geo','time','na_item','sector','unit'])` | Nombre (attendu : 0) |
| Cohérence des sommes | Σ catégories vs total | Écart max affiché |
| Valeurs aberrantes | Variations annuelles > X pts | Liste des cas, avec explication si connue |
| Données provisoires | Flags `p` d'Eurostat | Marqueur visuel sur les dernières années |
| Fraîcheur | Date du snapshot | Affichée dans le footer |

### 9.2 Ruptures et particularités à documenter

- **Changements de composition des agrégats** : UE à 27 depuis 2020 (Royaume-Uni sorti) → utiliser `EU27_2020` sur toute la période.
- **Zone euro** : le code évolue avec les adhésions (ex. EA20 ; ⚠️ vérifier le code en vigueur après l'adhésion de la Bulgarie en 2026).
- **Code Grèce** : `EL` chez Eurostat, `GR` / `GRC` en ISO.
- **Prix courants** : les montants en euros ne sont pas corrigés de l'inflation → privilégier les % du PIB pour les comparaisons dans le temps.
- **Effet dénominateur** : un taux en % du PIB peut monter parce que le PIB baisse (2009, 2020), sans hausse d'impôt. À annoter explicitement.
- **Révisions** : les données sont révisables à tout moment → snapshot daté.

### 9.3 Validation par reproduction de chiffres officiels

Le meilleur argument de rigueur : **montrer que ton pipeline retrouve les chiffres publiés**.

| Chiffre de référence | Valeur publiée | Source |
|---|---|---|
| Taux UE, 2024 | 40,4 % du PIB | Eurostat, Statistics Explained |
| Taux UE, 2023 | 39,9 % du PIB | Eurostat, Statistics Explained |
| Taux France, 2024 | 45,3 % du PIB | INSEE, d'après Eurostat (extraction du 12/02/2026) |
| Pays les plus élevés en 2024 | Danemark, France, Belgique | Eurostat news, 31/10/2025 |

Si ton calcul diffère : chercher pourquoi (secteur, indicateur, révision), et **le dire dans l'app**. Un écart expliqué vaut mieux qu'un écart caché.

---

## 10. Plan de réalisation par phases

**Estimation totale : 28 à 35 heures.** Appliquer la loi de Hofstadter : prévoir **+30 % de marge** sur chaque phase. Les phases sont **séquentielles** : ne pas commencer le dashboard avant d'avoir un storyboard validé et des données propres.

### Phase 0 — Vérifications bloquantes (1 h)

- [ ] Date limite, plateforme de dépôt, format du rapport, langue de la vidéo.
- [ ] Fiche du dataset sur data.europa.eu (URL + licence) — ou accord de l'enseignant pour l'API Eurostat.
- [ ] Créer le repo GitHub public + environnement virtuel.

**Critère de fin :** les 4 inconnues de §1 sont levées ; la source est confirmée.

### Phase 1 — Exploration rapide des données (3 h)

- [ ] Télécharger le dataset complet une fois, en notebook.
- [ ] Lister les codes `na_item`, `sector`, `geo` réellement présents.
- [ ] Vérifier la complétude par pays et par année.
- [ ] Tester la reproduction du chiffre UE 2024 (40,4 %) → choisir le secteur.
- [ ] Regarder grossièrement la composition FR vs UE → **l'hypothèse tient-elle ?**

**Critère de fin :** tu sais quel indicateur et quel secteur utiliser, et tu as une première idée des 2-3 insights réels.

### Phase 2 — Storyboard (2-3 h)

- [ ] Formuler la phrase-insight de chaque section **à partir de ce que la phase 1 a montré**.
- [ ] Croquis de chaque section (visuel + interaction + question).
- [ ] Faire relire à une personne non spécialiste : comprend-elle le fil ?

**Critère de fin :** storyboard exportable (PDF/image) qui sera rendu tel quel ; chaque graphique répond à une question.

### Phase 3 — Pipeline de données (4-5 h)

- [ ] `scripts/download_data.py` → snapshot Parquet daté.
- [ ] `utils/constants.py` : codes, mapping catégories, ISO-2 → ISO-3.
- [ ] `utils/prep.py` : format long, filtres, regroupements, variables dérivées (§6.6).
- [ ] `tests/test_prep.py` : les 4 tests de §8.4.
- [ ] Documenter chaque choix (commentaires + section README).

**Critère de fin :** `make data && make test` passe depuis un clone propre ; les tables prêtes pour l'app existent.

### Phase 4 — Squelette de l'app + MVP (6-8 h)

- [ ] `app.py` + sidebar + KPI header branchés sur les filtres.
- [ ] V1 (carte), V2 (classement), V3 (courbes) — **les 3 visuels minimum exigés**.
- [ ] Textes de chaque section repris du storyboard.

**Critère de fin (MVP) :** l'app remplit **toutes** les exigences techniques minimales de l'énoncé. À ce stade, le projet est rendable.

### Phase 5 — Approfondissements (4-5 h)

- [ ] V4 (écart), V5 (composition), V6 (small multiples).
- [ ] Annotations (crises, effet dénominateur, provisoires).
- [ ] Section qualité des données (§9) avec V7.
- [ ] Section conclusions + limites.

**Critère de fin :** le récit complet se lit de haut en bas sans explication orale.

### Phase 6 — Finitions UX et accessibilité (2-3 h)

- [ ] Palette accessible, libellés d'axes et unités partout, `st.caption` alt text.
- [ ] Infobulles de définition (`help=`).
- [ ] Test thème clair / sombre, test largeur réduite.
- [ ] Supprimer tout contrôle ou graphique qui n'apporte rien.

### Phase 7 — Packaging et déploiement (2-3 h)

- [ ] `requirements.txt` figé (`pip freeze` dans un venv propre — ne pas recopier des versions au hasard).
- [ ] Test **depuis un clone vierge** dans un nouvel environnement.
- [ ] Déploiement Streamlit Community Cloud ; vérifier que l'URL fonctionne en navigation privée.
- [ ] README complet (§12).

### Phase 8 — Vidéo et rendu (3-4 h)

- [ ] Script chronométré (§11), répétition, enregistrement, hébergement.
- [ ] Export du storyboard.
- [ ] Zip `StApp26_<n°>_<NOM>_BIA.zip` : README + code + snapshot/lien du dataset.
- [ ] Vérifier tous les liens (app, repo, vidéo, storyboard) depuis un autre appareil.
- [ ] Checklist finale (§14).

### Calendrier type

À ajuster dès que la date limite est connue. Exemple sur 3 semaines à ~10-12 h/semaine :

| Semaine | Phases | Jalon |
|---|---|---|
| S1 | 0, 1, 2 | Source validée + storyboard terminé |
| S2 | 3, 4 | **MVP rendable** déployé |
| S3 | 5, 6, 7, 8 | Rendu complet, 2 jours de marge avant la deadline |

**Règle :** le MVP déployé doit exister **au plus tard à mi-parcours**. Tout ce qui suit est de l'amélioration, pas une condition du rendu.

---

## 11. Vidéo de démo

### 11.1 Contraintes

- **2 à 4 minutes** (viser 3 min 30 pour garder une marge).
- Langue : ⚠️ à confirmer. Si anglais : **script écrit en phrases simples**, lu, pas improvisé.
- Hébergement : YouTube non répertorié ou Google Drive en lecture publique. Tester le lien en navigation privée.

### 11.2 Script type (≈ 3 min 30)

| Temps | Écran | Contenu |
|---|---|---|
| 0:00–0:20 | Intro + KPI | Hook : le chiffre clé, la question |
| 0:20–0:40 | Encadré définition | Ce que mesure le taux, d'où viennent les données |
| 0:40–1:20 | Carte + classement | Insight 1 ; montrer le curseur d'année |
| 1:20–2:00 | Courbes + écart | Insight 2 ; ajouter/retirer un pays |
| 2:00–2:45 | Composition | Insight 3 ; changer de pays comparé |
| 2:45–3:10 | Qualité des données | Les contrôles, ce qui manque, la validation sur les chiffres officiels |
| 3:10–3:30 | Conclusions | Ce qu'on peut dire, ce qu'on ne peut pas dire |

**Montrer les interactions en action**, ne pas seulement les décrire : c'est ce que la vidéo évalue.

---

## 12. README et packaging

### 12.1 Plan du README

1. **Titre + une phrase** de description + lien de l'app déployée + lien vidéo.
2. **Question et public** (§4).
3. **Données** : nom, producteur, DOI, URL data.europa.eu, licence CC BY 4.0, date du snapshot, citation.
4. **Méthode** : indicateur et secteur retenus et pourquoi, regroupements, variables dérivées.
5. **Lancer le projet** :
   ```bash
   git clone <repo>
   cd streamlit-tax-europe
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   make data      # optionnel : retélécharge le snapshot
   make run       # streamlit run app.py
   ```
6. **Structure du code** (§8.1).
7. **Qualité des données et limites** (§9 et §13).
8. **Pistes d'amélioration**.
9. **Licences** : code (au choix, ex. MIT) **≠** données (CC BY 4.0) — le PDF demande explicitement de distinguer les deux.

### 12.2 Citation des données (format Eurostat)

```
Source : Eurostat, Main national accounts tax aggregates (gov_10a_taxag),
DOI 10.2908/gov_10a_taxag, consulté le JJ/MM/AAAA.
Données modifiées : filtrage, regroupement des catégories et calculs dérivés par l'auteur.
```

### 12.3 Contenu du zip

```
StApp26_<n°>_<NOM>_BIA.zip
├── README.md
├── app.py, sections/, utils/, scripts/, tests/
├── requirements.txt, Makefile
├── data/gov_10a_taxag_<date>.parquet   (ou DATA_LINK.txt)
└── storyboard.pdf                       (si non fourni par lien seulement)
```

---

## 13. Risques et pièges

| Risque | Probabilité | Impact | Parade |
|---|---|---|---|
| Dataset non référencé sur data.europa.eu | Moyenne | **Bloquant** | Vérifier en phase 0 ; sinon demander validation ou changer de dataset |
| Deadline proche, inconnue | Élevée tant que non vérifiée | Élevé | Phase 0 immédiate |
| Snapshot pris avant la publication de fin octobre | Moyenne | Moyen | Figer après la mise à jour ; dater |
| Confusion de définitions (INSEE vs Eurostat) | Élevée | Moyen | Une seule source, définition affichée |
| Glissement vers une conclusion causale | Élevée (vu ton intérêt initial) | Élevé (narration + communication) | Formulations descriptives ; section « ce qu'on ne peut pas dire » |
| Sur-ingénierie (pipeline, tests, archi) | **Élevée** vu ton profil | Moyen (temps perdu sur 15 pts) | Structure §8.1, rien de plus avant le MVP |
| Effet dénominateur mal interprété (2009, 2020) | Élevée | Moyen | Annotation explicite sur les graphiques |
| Hypothèse « cotisations sociales » infirmée | Possible | Faible si anticipée | Le récit suit les données, pas l'inverse |
| App en hibernation lors de la correction | Moyenne | Moyen | Réveiller avant ; mention dans le README |
| Trop de contrôles / graphiques | Moyenne | Moyen (UX) | Règle : chaque élément répond à une question du storyboard |

---

## 14. Checklist finale (mapping barème)

### Narration & cadrage (25 pts)
- [ ] Public cible nommé explicitement dans l'app
- [ ] Hook → contexte → insights → implications présents et dans cet ordre
- [ ] Une phrase-insight en tête de chaque section
- [ ] Storyboard rendu et aligné avec l'app

### Données (25 pts)
- [ ] Source, licence, DOI, date du snapshot cités
- [ ] Chaque transformation documentée
- [ ] Variables dérivées expliquées
- [ ] Section qualité : manquants, doublons, contrôles de cohérence
- [ ] Reproduction d'au moins un chiffre officiel

### Visualisation & UX (25 pts)
- [ ] ≥ 3 visuels interactifs avec tooltips
- [ ] Au moins une carte
- [ ] KPI liés aux filtres
- [ ] Sidebar : période, pays, variable
- [ ] Annotations / lignes de référence
- [ ] Axes et unités sur tous les graphiques
- [ ] Palette accessible + alt text

### Code (15 pts)
- [ ] Structure modulaire `sections/` + `utils/`
- [ ] `st.cache_data` utilisé
- [ ] `requirements.txt` figé
- [ ] Fonctionne depuis un clone propre
- [ ] Script de téléchargement des données

### Communication (10 pts)
- [ ] Vidéo 2-4 min, interactions montrées
- [ ] Limites et incertitudes exposées honnêtement
- [ ] README clair

### Rendu
- [ ] Zip correctement nommé
- [ ] Tous les liens testés en navigation privée
- [ ] App réveillée juste avant la date de correction

---

## 15. Questions ouvertes

| Question | Qui tranche | Bloquant ? |
|---|---|---|
| Date limite de rendu | Moodle / enseignant | **Oui** |
| Plateforme de dépôt | Moodle / enseignant | Oui (fin de projet) |
| Forme du « rapport » | Enseignant | Non (README par défaut) |
| Langue de l'app et de la vidéo | Enseignant | Non (anglais par défaut) |
| Le dataset est-il sur data.europa.eu ? | Toi (vérification) | **Oui** |
| API Eurostat acceptée comme mode d'accès ? | Enseignant | Seulement si la fiche data.europa.eu n'existe pas |
| L'hypothèse « cotisations sociales » tient-elle ? | Les données (phase 1) | Non — oriente le récit |

---

## 16. Sources

**Dataset et documentation Eurostat**
- Databrowser `gov_10a_taxag` (couverture, DOI, date de mise à jour) — https://ec.europa.eu/eurostat/databrowser/view/GOV_10A_TAXAG__custom_5767115/default/table?lang=en
- Métadonnées ESMS `gov_10a_taxag` (base légale, couverture, calendrier) — https://ec.europa.eu/eurostat/cache/metadata/en/gov_10a_taxag_esms.htm
- Statistics Explained, *Tax revenue statistics* — https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Tax_revenue_statistics
- Eurostat news, *EU and euro area tax-to-GDP ratio up in 2024* (31/10/2025) — https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251031-2
- Liste des dimensions et codes (DBnomics) — https://db.nomics.world/Eurostat/gov_10a_taxag

**Licence et citation**
- Eurostat, Copyright notice (CC BY 4.0, conditions de réutilisation) — https://ec.europa.eu/eurostat/en/help/copyright-notice
- Eurostat, Copyright notice (FR, formats de citation) — https://ec.europa.eu/eurostat/fr/help/copyright-notice

**Accès aux données**
- Eurostat, API — Introduction — https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction
- Package Python `eurostat` (PyPI) — https://pypi.org/project/eurostat/
- GISCO, unités territoriales NUTS — https://ec.europa.eu/eurostat/web/gisco/geodata//statistical-units/territorial-units-statistics
- Nuts2json (GeoJSON / TopoJSON des NUTS) — https://github.com/jgaffuri/Nuts2json

**Chiffres de référence et définitions**
- INSEE, *Taux de prélèvements obligatoires au sein de l'UE* — https://www.insee.fr/fr/statistiques/2381410
- IFRAP, *45,2 ou 48 % ? Quel est le vrai niveau des prélèvements obligatoires en 2022 ?* — https://www.ifrap.org/budget-et-fiscalite/452-ou-48-quel-est-le-vrai-niveau-des-prelevements-obligatoires-en-2022

**Streamlit**
- Docs Streamlit — Manage your app (limites de ressources, hibernation) — https://docs.streamlit.io/streamlit-community-cloud/get-started/manage-your-app
- Docs Streamlit (général) — https://docs.streamlit.io/

**Storytelling et visualisation (référencées dans le PDF du projet)**
- FT Visual Vocabulary, Data Viz Society, *Evergreen Data*, Plotly (https://plotly.com/python/), Altair (https://altair-viz.github.io/)
