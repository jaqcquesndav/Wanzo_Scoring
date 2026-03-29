# Wanzo Scoring — Credit Scoring XGBoost pour PME en RDC

**Modèle de prédiction de défauts de paiement des PME** en République Démocratique du Congo, basé sur l'algorithme **XGBoost-Boruta-GHM** (Xia et al., 2024) intégrant le **Contexte Économique Territorial (CET)** via l'ERP Wanzo.

## Pipeline

```
Données synthétiques → Feature Engineering → Boruta → XGBoost-B-GHM → Scoring 300-850
```

Deux méthodes de génération de données sont comparées :
- **Classique** (Notebook 1) : distributions paramétriques indépendantes, calibrées par expertise
- **CTGAN** (Notebook 2) : GAN conditionnel apprenant la distribution jointe (Xu et al., 2019)

## Structure du projet

```
├── 01_xgboost_generation_classique.ipynb   # Notebook 1 — Génération paramétrique
├── 02_xgboost_generation_ctgan.ipynb       # Notebook 2 — Génération CTGAN
├── data/
│   ├── data_classique_seed.csv             # 5000 PME synthétiques (seed)
│   ├── metrics_classique.pkl               # Métriques Notebook 1
│   ├── metrics_ctgan.pkl                   # Métriques Notebook 2
│   ├── arbre_{0,1,2}_{classique,ctgan}.png # Visualisations des arbres
│   └── comparaison_classique_vs_ctgan.png  # Graphique comparatif
├── models/
│   ├── model_classique_xgboost_bghm.json   # Modèle XGBoost (Classique)
│   ├── model_classique_xgboost_bghm.pkl    # Artefacts complets (Classique)
│   ├── model_ctgan_xgboost_bghm.json       # Modèle XGBoost (CTGAN)
│   └── model_ctgan_xgboost_bghm.pkl        # Artefacts complets (CTGAN + modèle CTGAN)
├── papers/
│   ├── article_scoring_pme_rdc.md          # Article scientifique (Markdown)
│   ├── article_scoring_pme_rdc.tex         # Article scientifique (LaTeX)
│   ├── extract_data.py                     # Extraction données depuis notebooks
│   ├── extract_figures.py                  # Extraction figures depuis notebooks
│   └── figures/                            # Figures pour l'article
│       ├── arbre_{0,1,2}_{classique,ctgan}.png
│       └── comparaison_classique_vs_ctgan.png
└── README.md
```

## Résultats (Notebook 1 — Classique)

| Métrique | Valeur |
|----------|--------|
| AUC-ROC | 0.786 |
| Accuracy | 0.878 |
| Precision | 0.667 |
| Recall | 0.152 |
| Brier Score | 0.099 |
| Variables Boruta | 13 (3 ERP-Trés, 3 ERP-Comp, 4 CET, 1 Profil, 2 Alt) |

## Variables clés

Le modèle repose sur 3 sources de données :
- **ERP Wanzo** : transactions, trésorerie, comportement de paiement
- **CET** : réseau/réputation, robustesse contextuelle, psychométrie adaptée
- **Données alternatives** : médias sociaux, utilités, empreinte numérique

Les variables CET représentent **31 % des features retenues par Boruta**, confirmant que le contexte territorial est un signal significatif pour le scoring en RDC.

## Scoring

Échelle 300–850, 5 catégories : Excellent → Très risqué  
Taux de défaut monotone : 5.2 % (Excellent) → 100 % (Très risqué)

## Prérequis

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost joblib Boruta shap ctgan graphviz
```

## Références

- Xia et al. (2024) — XGBoost-B-GHM, *MDPI Systems*
- Xu et al. (2019) — CTGAN, *NeurIPS*
- Nguyen & Sagara (2020) — Credit Risk Database for SMEs, *ADBI*
- Guérin (2015) — *La Microfinance et ses Dérives*, Demopolis/IRD
