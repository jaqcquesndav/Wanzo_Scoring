# Documentation du Modèle de Scoring — XGBoost-Boruta-GHM

## Vue d'ensemble

| Propriété | Valeur |
|---|---|
| **Modèle** | XGBoost-Boruta-GHM (Xia et al. 2024) |
| **Version** | v3.0-classique |
| **Cible** | Prédiction de défaut de paiement PME (RDC) |
| **Output** | Score de crédit 300–850 |
| **AUC-ROC** | 0.767 |
| **Accuracy** | 87.4% |
| **Fichier** | `model_classique_xgboost_bghm.pkl` (~857 KB) |

---

## 1. Variables à collecter

Le modèle utilise **13 features Boruta** calculées à partir de **20 variables brutes** organisées en 3 sources.

### Source 1 : ERP Wanzo — Données Financières (9 variables)

| Variable | Type | Plage | Description | Collecte |
|---|---|---|---|---|
| `chiffre_affaires` | float | 500K–500M CDF | Chiffre d'affaires annuel | Module comptabilité ERP |
| `charges_exploitation` | float | > 0 | Charges d'exploitation annuelles | Module comptabilité ERP |
| `marge_nette` | float | 0–1 | Résultat net / CA | **Calculable** = (CA - charges) / CA |
| `variabilite_ca` | float | 0–1 | Coefficient de variation du CA sur 12 mois | Écart-type(CA_mensuel) / Moyenne(CA_mensuel) |
| `ratio_endettement` | float | 0–8 | Dettes totales / Capitaux propres | Module comptabilité ERP |
| `couverture_dette` | float | -1–5 | Flux trésorerie / Service de la dette | Module trésorerie ERP |
| `nb_retards_paiement_12m` | int | 0–15 | Nombre de retards de paiement sur 12 mois | Historique paiements ERP |
| `jours_retard_moyen` | float | 0–90 | Moyenne des jours de retard | Historique paiements ERP |
| `nb_factures_impayees` | int | 0–20 | Factures en souffrance | Module facturation ERP |

### Source 2 : ERP Wanzo — Comportement Paiement (3 variables)

| Variable | Type | Plage | Description | Collecte |
|---|---|---|---|---|
| `taux_recouvrement_creances` | float | 0–1 | Créances recouvrées / Créances totales | Module créances ERP |
| `regularite_paiement_mobile` | float | 0–1 | % paiements mobile money à temps | Transactions mobile money ERP |
| `regularite_paiement_fournisseurs` | float | 0–1 | % paiements fournisseurs à temps | Module fournisseurs ERP |

### Source 3 : CET — Contexte Économique Territorial (7 variables)

| Variable | Type | Plage | Description | Collecte |
|---|---|---|---|---|
| `score_reseau_communautaire` | float | 0–1 | Force du réseau social/business local | Questionnaire terrain / Agent |
| `appartenance_association` | int | 0 ou 1 | Membre d'une association professionnelle | Questionnaire terrain |
| `pct_clients_recurrents` | float | 0–1 | % de clients qui reviennent | Données transactionnelles ERP |
| `score_reputation_terrain` | float | 0–1 | Réputation locale (agents/pairs) | Enquête terrain / Agent |
| `diversification_activites` | float | 0–1 | Diversification des sources de revenus | Questionnaire / ERP |
| `exposition_zones_instables` | float | 0–1 | Degré d'exposition à l'insécurité | Géolocalisation + base CET |
| `stock_securite_jours` | float | 0–90 | Jours de stock de sécurité | Inventaire ERP / Déclaratif |
| `anciennete_annees` | float | 0.5–30 | Ancienneté de l'entreprise (années) | Inscription ERP |

### Résumé des sources

| Source | Variables | % du modèle |
|---|---|---|
| ERP Financier | 9 | 45% |
| ERP Comportement | 3 | 15% |
| CET Territorial | 7 | 35% |
| Profil (ancienneté) | 1 | 5% |
| **Total** | **20** | **100%** |

---

## 2. Feature Engineering — Transformations appliquées

Le module calcule automatiquement les 13 features finales. Voici leur formule pour référence :

### Features directes (8/13) — aucun calcul, lues directement

```
marge_nette              → tel quel
variabilite_ca           → tel quel
ratio_endettement        → tel quel
nb_retards_paiement_12m  → tel quel
couverture_dette         → tel quel
jours_retard_moyen       → tel quel
taux_recouvrement_creances → tel quel
anciennete_annees        → tel quel
```

### Features calculées (5/13) — formules exactes

```python
# 1. Ratio charges (ERP)
charges_ratio = charges_exploitation / max(chiffre_affaires, 1)

# 2. Intensité des retards (ERP)
intensite_retards = nb_retards_paiement_12m × jours_retard_moyen

# 3. Score comportement transactionnel (ERP + pondérations)
score_comportement_transactionnel =
    regularite_paiement_fournisseurs × 0.30
  + regularite_paiement_mobile × 0.25
  + taux_recouvrement_creances × 0.25
  + (1 - nb_factures_impayees / max_factures) × 0.20

# 4. Score réseau + réputation (CET)
score_reseau_reputation =
    score_reseau_communautaire × 0.25
  + appartenance_association × 0.25
  + pct_clients_recurrents × 0.25
  + score_reputation_terrain × 0.25

# 5. Score robustesse contextuelle (CET)
score_robustesse_contextuelle =
    diversification_activites × 0.30
  + (1 - exposition_zones_instables) × 0.30
  + min(stock_securite_jours / 90, 1) × 0.20
  + min(1 - variabilite_ca / 0.6, 1) × 0.20
```

---

## 3. Les 13 Features Boruta (entrée du modèle)

Après feature engineering et standardisation (μ=0, σ=1), le modèle reçoit exactement :

| # | Feature | Type | Source |
|---|---|---|---|
| 1 | `marge_nette` | float | ERP directe |
| 2 | `variabilite_ca` | float | ERP directe |
| 3 | `ratio_endettement` | float | ERP directe |
| 4 | `nb_retards_paiement_12m` | int | ERP directe |
| 5 | `intensite_retards` | float | **Calculée** |
| 6 | `score_comportement_transactionnel` | float | **Calculée** |
| 7 | `anciennete_annees` | float | Profil directe |
| 8 | `couverture_dette` | float | ERP directe |
| 9 | `jours_retard_moyen` | float | ERP directe |
| 10 | `taux_recouvrement_creances` | float | ERP directe |
| 11 | `charges_ratio` | float | **Calculée** |
| 12 | `score_reseau_reputation` | float | **Calculée** |
| 13 | `score_robustesse_contextuelle` | float | **Calculée** |

---

## 4. Sortie du modèle

### Score de crédit (300–850)

```
credit_score = (1 - probabilité_défaut) × 550 + 300
```

### Catégories de risque

| Score | Catégorie | Interprétation |
|---|---|---|
| ≥ 750 | **Excellent** | Risque très faible, crédit recommandé |
| 650–749 | **Bon** | Risque faible, crédit avec conditions standard |
| 550–649 | **Acceptable** | Risque modéré, crédit avec garanties |
| 450–549 | **Risqué** | Risque élevé, crédit partiel ou refusé |
| < 450 | **Très risqué** | Risque très élevé, crédit refusé |

### Format de réponse API

```json
{
  "probability_default": 0.3379,
  "credit_score": 664,
  "risk_category": "Bon",
  "model_version": "v3.0-classique"
}
```

---

## 5. Ce qu'il faut copier dans adha-ai-service

### Structure dans le service

```
apps/Adha-ai-service/
├── scoring/                          ← NOUVEAU DOSSIER
│   ├── __init__.py
│   ├── scoring_engine.py             ← Module d'inférence
│   ├── model_classique_xgboost_bghm.pkl  ← Artefact modèle (~857 KB)
│   └── requirements.txt              ← Dépendances pip
└── ...
```

### Fichiers à copier

| Fichier | Source | Destination dans adha-ai |
|---|---|---|
| `scoring/scoring_engine.py` | Ce repo | `apps/Adha-ai-service/scoring/scoring_engine.py` |
| `models/model_classique_xgboost_bghm.pkl` | Ce repo | `apps/Adha-ai-service/scoring/model_classique_xgboost_bghm.pkl` |
| `scoring/requirements.txt` | Ce repo | Ajouter au `requirements.txt` global |

### Dépendances à ajouter au pip install du service

```
xgboost>=1.7.0
scikit-learn>=1.0
```

(`pandas`, `numpy`, `joblib` sont déjà dans Django)

### Intégration Django — Endpoint REST

Créer dans `apps/Adha-ai-service/api/views/` :

```python
# scoring_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from scoring.scoring_engine import predict, REQUIRED_RAW_VARIABLES


class CreditScoringView(APIView):
    def post(self, request):
        data = request.data
        missing = [v for v in REQUIRED_RAW_VARIABLES if v not in data]
        if missing:
            return Response(
                {"error": f"Variables manquantes: {missing}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = predict(data)
        return Response(result, status=status.HTTP_200_OK)

    def get(self, request):
        return Response({
            "required_variables": REQUIRED_RAW_VARIABLES,
            "description": "POST les variables brutes pour obtenir un score de crédit",
        })
```

### Ajouter la route URL

Dans `apps/Adha-ai-service/api/urls.py` :

```python
from api.views.scoring_views import CreditScoringView

urlpatterns += [
    path('api/scoring/predict', CreditScoringView.as_view(), name='credit-scoring'),
]
```

### Route API Gateway

Dans la config de l'API Gateway NestJS, ajouter le proxy :

```typescript
// Route scoring → adha-ai-service
{ path: '/scoring/*', target: 'http://adha-ai-service:8002' }
```

---

## 6. Test rapide (appel API)

```bash
curl -X POST http://localhost:8002/api/scoring/predict \
  -H "Content-Type: application/json" \
  -d '{
    "anciennete_annees": 5.0,
    "chiffre_affaires": 12000000,
    "charges_exploitation": 9000000,
    "marge_nette": 0.25,
    "variabilite_ca": 0.15,
    "ratio_endettement": 1.2,
    "couverture_dette": 1.8,
    "nb_retards_paiement_12m": 1,
    "jours_retard_moyen": 5.0,
    "nb_factures_impayees": 2,
    "taux_recouvrement_creances": 0.85,
    "regularite_paiement_mobile": 0.75,
    "regularite_paiement_fournisseurs": 0.80,
    "score_reseau_communautaire": 0.65,
    "appartenance_association": 1,
    "pct_clients_recurrents": 0.70,
    "score_reputation_terrain": 0.80,
    "diversification_activites": 0.45,
    "exposition_zones_instables": 0.10,
    "stock_securite_jours": 20.0
  }'
```

Réponse attendue :
```json
{
  "probability_default": 0.3379,
  "credit_score": 664,
  "risk_category": "Bon",
  "model_version": "v3.0-classique"
}
```

---

## 7. Flux de données dans l'architecture Wanzo

```
┌──────────────────┐     POST /scoring/predict     ┌───────────────────────┐
│  accounting-     │ ──────────────────────────────►│  adha-ai-service      │
│  service         │     (via API Gateway ou        │                       │
│  (NestJS:3003)   │      Kafka event)              │  scoring_engine.py    │
│                  │◄──────────────────────────────  │  ├── compute_features │
│  → Demande score │     JSON réponse               │  ├── standardize      │
│  → Reçoit résult │                                │  └── predict_proba    │
└──────────────────┘                                └───────────────────────┘
         │                                                     │
         │                                          ┌──────────┴──────────┐
         │                                          │ model_classique_    │
         ▼                                          │ xgboost_bghm.pkl   │
  Stocke le score                                   │ (857 KB, en RAM)    │
  dans PostgreSQL                                   └─────────────────────┘
```
