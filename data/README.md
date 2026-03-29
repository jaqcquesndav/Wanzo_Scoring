# Documentation des données — Scoring Crédit PME en RDC

## Vue d'ensemble

Ce jeu de données contient **5 000 PME synthétiques** opérant en République Démocratique du Congo, générées pour entraîner et valider un modèle de scoring crédit XGBoost-B-GHM (Boruta + Gradient Harmonizing Mechanism). Les données sont 100 % synthétiques (seed = 42) et calibrées sur les réalités économiques congolaises.

**Taux de défaut** : 13,2 % (660 défauts sur 5 000 entreprises)

## Formats disponibles

| Fichier | Format | Séparateur | Taille | Description |
|---------|--------|------------|--------|-------------|
| `pme_synthetiques.csv` | CSV | Virgule (`,`) | 2,1 Mo | Fichier plat, 5 000 lignes × 77 colonnes |
| `pme_synthetiques.json` | JSON | — | 12,8 Mo | Array de 5 000 objets (orient `records`) |
| `pme_synthetiques.xlsx` | Excel | — | 2,0 Mo | 3 feuilles : *Données complètes*, *Variables Boruta*, *Statistiques* |

### Feuilles Excel

- **Données complètes** : les 77 colonnes pour les 5 000 PME
- **Variables Boruta** : uniquement les 13 variables sélectionnées par Boruta (40 itérations)
- **Statistiques** : statistiques descriptives (count, mean, std, min, max, quartiles)

## Dimensions catégorielles

| Variable | Valeurs |
|----------|---------|
| `secteur` | Agriculture, Commerce, Construction, Manufacture, Mines, Services, TIC, Transport |
| `taille` | Micro, Petite, Moyenne |
| `localisation` | Bukavu, Goma, Kananga, Kinshasa, Kisangani, Lubumbashi, Mbuji-Mayi |

## Dictionnaire des variables (77 colonnes)

### 1. Identification de l'entreprise (3 variables)

| Variable | Type | Description |
|----------|------|-------------|
| `secteur` | str | Secteur d'activité de la PME |
| `taille` | str | Catégorie de taille (Micro / Petite / Moyenne) |
| `localisation` | str | Ville d'implantation en RDC |

### 2. Caractéristiques structurelles (4 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `anciennete_annees` | float | années | Âge de l'entreprise (0,5 – 30) |
| `nb_employes` | int | employés | Nombre d'employés (1 – 249) |
| `chiffre_affaires` | float | USD/mois | Chiffre d'affaires mensuel |
| `variabilite_ca` | float | ratio | Coefficient de variation du CA (0,05 – 0,60) |

### 3. Transactions et paiements (7 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `nb_transactions_mois` | int | transactions | Nombre mensuel de transactions (35 – 90) |
| `montant_moyen_transaction` | float | USD | Montant moyen par transaction |
| `pct_cash` | float | ratio | Part des paiements en cash |
| `pct_mobile_money` | float | ratio | Part des paiements en mobile money |
| `pct_banque` | float | ratio | Part des paiements bancaires |
| `diversification_paiement` | float | indice | Indice de diversification des moyens de paiement (entropie, 0–1) |
| `pct_transactions_usd` | float | ratio | Part des transactions en USD |

### 4. Rentabilité et exploitation (3 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `charges_exploitation` | float | USD/mois | Charges d'exploitation mensuelles |
| `resultat_net` | float | USD/mois | Résultat net mensuel |
| `marge_nette` | float | ratio | Marge nette (résultat net / CA), 0,05 – 0,50 |

### 5. Trésorerie (5 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `solde_caisse_moyen` | float | USD | Solde moyen en caisse |
| `entrees_tresorerie_mois` | float | USD/mois | Entrées de trésorerie mensuelles |
| `sorties_tresorerie_mois` | float | USD/mois | Sorties de trésorerie mensuelles |
| `flux_tresorerie_net` | float | USD/mois | Flux de trésorerie net (entrées – sorties) |
| `remboursements_dettes_mois` | float | USD/mois | Remboursements de dettes mensuels |

### 6. Ratios financiers (3 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `ratio_liquidite` | float | ratio | Ratio de liquidité générale (0,34 – 7,59) |
| `ratio_endettement` | float | ratio | Ratio d'endettement total (0,10 – 19,90) |
| `couverture_dette` | float | ratio | Ratio de couverture de la dette (−2,85 – 6,01) |

### 7. Historique de paiement (8 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `nb_retards_paiement_12m` | int | retards | Nombre de retards sur 12 mois (0 – 8) |
| `jours_retard_moyen` | float | jours | Durée moyenne des retards de paiement |
| `nb_factures_impayees` | int | factures | Nombre de factures impayées |
| `taux_recouvrement_creances` | float | ratio | Taux de recouvrement des créances |
| `delai_paiement_fournisseurs` | float | jours | Délai moyen de paiement aux fournisseurs |
| `delai_recouvrement_jours` | float | jours | Délai de recouvrement des créances clients |
| `creances_sur_ca` | float | ratio | Ratio créances / chiffre d'affaires |
| `regularite_paiement_mobile` | float | score | Score de régularité des paiements mobile (0–1) |

### 8. Contexte socio-économique congolais (8 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `regularite_paiement_fournisseurs` | float | score | Régularité des paiements fournisseurs (0–1) |
| `pct_activite_informelle` | float | ratio | Part d'activité dans le secteur informel |
| `ecart_taux_change` | float | % | Écart de taux de change USD/CDF subi |
| `appartenance_association` | int | binaire | Membre d'une association professionnelle (0/1) |
| `score_reseau_communautaire` | float | score | Intégration dans le réseau communautaire (0–1) |
| `pct_clients_recurrents` | float | ratio | Part de clients récurrents |
| `score_reputation_terrain` | float | score | Réputation de l'entreprise sur le terrain (0–1) |
| `part_credit_informel` | float | ratio | Part de financement par crédit informel |

### 9. Résilience et adaptabilité (4 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `exposition_zones_instables` | float | score | Exposition aux zones d'instabilité (0–1) |
| `diversification_activites` | float | score | Diversification des sources de revenus (0–1) |
| `stock_securite_jours` | float | jours | Stock de sécurité en jours |
| `score_debrouillardise` | float | score | Capacité d'adaptation / débrouillardise (0–1) |

### 10. Présence digitale et réputation en ligne (5 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `usage_whatsapp_business` | int | binaire | Utilisation de WhatsApp Business (0/1) |
| `social_media_abonnes` | int | abonnés | Nombre d'abonnés réseaux sociaux |
| `social_media_sentiment` | float | score | Score de sentiment sur les réseaux sociaux (0–1) |
| `social_media_freq_publication` | int | posts/mois | Fréquence de publication |
| `trafic_web_mensuel` | int | visites | Trafic web mensuel |

### 11. Avis clients (2 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `nb_avis_en_ligne` | int | avis | Nombre d'avis en ligne |
| `note_avis_moyenne` | float | note/5 | Note moyenne des avis clients (1–5) |

### 12. Consommation d'utilités (5 variables)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `conso_energie_kwh` | float | kWh/mois | Consommation électrique mensuelle |
| `tendance_energie` | float | ratio | Tendance de la consommation énergétique |
| `conso_eau_m3` | float | m³/mois | Consommation d'eau mensuelle |
| `regularite_paiement_energie` | float | score | Régularité des paiements d'énergie (0–1) |
| `regularite_paiement_eau` | float | score | Régularité des paiements d'eau (0–1) |

### 13. Régularité locative (1 variable)

| Variable | Type | Unité | Description |
|----------|------|-------|-------------|
| `regularite_paiement_loyer` | float | score | Régularité des paiements de loyer (0–1) |

### 14. Variable cible (1 variable)

| Variable | Type | Valeurs | Description |
|----------|------|---------|-------------|
| `default` | int | 0 / 1 | **Défaut de paiement** — 0 = sain (4 340), 1 = défaut (660) |

### 15. Variables d'ingénierie (feature engineering) — 18 variables dérivées

| Variable | Type | Formule / Description |
|----------|------|----------------------|
| `ca_par_employe` | float | `chiffre_affaires / nb_employes` — Productivité par employé |
| `charges_ratio` | float | `charges_exploitation / chiffre_affaires` — Part des charges dans le CA |
| `flux_net_ratio` | float | `flux_tresorerie_net / entrees_tresorerie_mois` — Efficacité de trésorerie |
| `intensite_retards` | float | `nb_retards_paiement_12m × jours_retard_moyen` — Gravité cumulée des retards |
| `tresorerie_par_employe` | float | `solde_caisse_moyen / nb_employes` — Liquidité par tête |
| `charge_remboursement_ratio` | float | `remboursements_dettes_mois / chiffre_affaires` — Poids du remboursement |
| `solde_caisse_ratio` | float | `solde_caisse_moyen / chiffre_affaires` — Coussin de trésorerie |
| `score_comportement_transactionnel` | float | Composite : diversification paiement + régularité mobile + clients récurrents |
| `score_reseau_reputation` | float | Composite : réseau communautaire + réputation terrain + association |
| `score_robustesse_contextuelle` | float | Composite : stock sécurité + diversification activités − exposition instabilité |
| `creances_deviation_norme` | float | Écart normalisé des créances par rapport à la norme sectorielle |
| `score_psychometrie` | float | Score psychométrique composite (débrouillardise ajustée) |
| `score_presence_digitale` | float | Composite : WhatsApp Business + sentiment réseaux + fréquence publication |
| `score_regularite_utilites` | float | Moyenne pondérée : régularité énergie, eau, loyer |
| `energie_par_employe` | float | `conso_energie_kwh / nb_employes` — Intensité énergétique |
| `eau_par_employe` | float | `conso_eau_m3 / nb_employes` — Consommation d'eau par employé |
| `anciennete_log` | float | `log(anciennete_annees + 1)` — Ancienneté log-transformée |
| `employes_log` | float | `log(nb_employes + 1)` — Taille log-transformée |

## Variables sélectionnées par Boruta (13 features)

Ces 13 variables ont été confirmées comme significatives par l'algorithme Boruta (40 itérations, α = 0,05) et alimentent le modèle XGBoost-B-GHM final :

1. **`marge_nette`** — Marge nette
2. **`ratio_endettement`** — Ratio d'endettement
3. **`charges_ratio`** — Part des charges dans le CA
4. **`score_comportement_transactionnel`** — Score comportemental transactionnel
5. **`intensite_retards`** — Intensité cumulée des retards
6. **`jours_retard_moyen`** — Durée moyenne des retards
7. **`score_reseau_reputation`** — Score réseau et réputation
8. **`score_robustesse_contextuelle`** — Score de robustesse contextuelle
9. **`score_psychometrie`** — Score psychométrique
10. **`usage_whatsapp_business`** — Utilisation de WhatsApp Business
11. **`anciennete_annees`** — Ancienneté de l'entreprise
12. **`social_media_sentiment`** — Sentiment sur les réseaux sociaux
13. **`note_avis_moyenne`** — Note moyenne des avis clients

## Génération des données

- **Méthode** : génération synthétique paramétrique avec corrélations réalistes
- **Graine aléatoire** : `np.random.seed(42)` pour reproductibilité
- **Calibration** : distributions inspirées des rapports FPM 2024, enquêtes FOGEC sur les PME congolaises et Persona Wanzo (profils CET — Caractéristiques, Environnement, Transactions)
- **Déséquilibre** : taux de défaut de 13,2 %, traité par la perte GHM (Gradient Harmonizing Mechanism) lors de l'entraînement

## Utilisation

```python
import pandas as pd

# CSV
df = pd.read_csv("data/pme_synthetiques.csv")

# JSON
df = pd.read_json("data/pme_synthetiques.json", orient="records")

# Excel — feuille complète
df = pd.read_excel("data/pme_synthetiques.xlsx", sheet_name="Données complètes")

# Excel — variables Boruta uniquement
df_boruta = pd.read_excel("data/pme_synthetiques.xlsx", sheet_name="Variables Boruta")
```

## Licence et avertissement

Ces données sont **100 % synthétiques** et ne représentent aucune entreprise réelle. Elles sont fournies à des fins de recherche et de démonstration du modèle de scoring crédit XGBoost-B-GHM pour les PME en RDC.
