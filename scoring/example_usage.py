"""
Exemple d'utilisation du module scoring_engine.
"""
from scoring_engine import predict, REQUIRED_RAW_VARIABLES

# Exemple : une PME à Goma
pme_data = {
    # Profil
    "anciennete_annees": 5.0,
    # ERP Trésorerie
    "chiffre_affaires": 12_000_000,
    "charges_exploitation": 9_000_000,
    "marge_nette": 0.25,
    "variabilite_ca": 0.15,
    "ratio_endettement": 1.2,
    "couverture_dette": 1.8,
    # ERP Comportement Paiement
    "nb_retards_paiement_12m": 1,
    "jours_retard_moyen": 5.0,
    "nb_factures_impayees": 2,
    "taux_recouvrement_creances": 0.85,
    "regularite_paiement_mobile": 0.75,
    "regularite_paiement_fournisseurs": 0.80,
    # CET — Contexte Économique Territorial
    "score_reseau_communautaire": 0.65,
    "appartenance_association": 1,
    "pct_clients_recurrents": 0.70,
    "score_reputation_terrain": 0.80,
    "diversification_activites": 0.45,
    "exposition_zones_instables": 0.10,
    "stock_securite_jours": 20.0,
}

result = predict(pme_data)
print(f"Probabilité de défaut : {result['probability_default']:.2%}")
print(f"Score de crédit       : {result['credit_score']}")
print(f"Catégorie de risque   : {result['risk_category']}")
print(f"Version modèle        : {result['model_version']}")
