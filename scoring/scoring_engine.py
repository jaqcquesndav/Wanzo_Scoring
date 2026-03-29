"""
Module de scoring crédit PME — XGBoost-Boruta-GHM
Wanzo ERP — République Démocratique du Congo

Ce module charge le modèle XGBoost pré-entraîné et expose une fonction
d'inférence complète : données brutes → score de crédit (300-850).

Fichiers requis dans le même répertoire :
  - model_classique_xgboost_bghm.pkl  (artifacts complets)
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GHM loss (nécessaire pour désérialiser le modèle XGBClassifier)
# ---------------------------------------------------------------------------

def ghm_loss(y_true, y_pred, bins=7, beta=0.65):
    sigmoid_pred = 1.0 / (1.0 + np.exp(-y_pred))
    g = np.abs(y_true - sigmoid_pred)
    edges = np.linspace(0, 1, bins + 1)
    weights = np.ones_like(g)
    for i in range(bins):
        mask = (g >= edges[i]) & (g < edges[i + 1])
        count = mask.sum()
        if count > 0:
            density = count / (edges[i + 1] - edges[i])
            weights[mask] = len(g) / (density * bins)
    weights = beta * weights + (1 - beta) * 1.0
    grad = weights * (sigmoid_pred - y_true)
    hess = weights * sigmoid_pred * (1 - sigmoid_pred)
    return grad, hess


# ---------------------------------------------------------------------------
# Chargement singleton du modèle
# ---------------------------------------------------------------------------

_model_artifacts = None
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "model_classique_xgboost_bghm.pkl")


def _load_model():
    global _model_artifacts
    if _model_artifacts is None:
        # ghm_loss doit être dans __main__ pour le unpickling du XGBClassifier
        import __main__
        if not hasattr(__main__, "ghm_loss"):
            __main__.ghm_loss = ghm_loss
        logger.info("Chargement du modèle XGBoost-B-GHM depuis %s", MODEL_PATH)
        _model_artifacts = joblib.load(MODEL_PATH)
        logger.info(
            "Modèle chargé — version=%s, features=%d",
            _model_artifacts["metadata"]["version"],
            len(_model_artifacts["feature_names"]),
        )
    return _model_artifacts


# ---------------------------------------------------------------------------
# Feature engineering (identique à l'entraînement)
# ---------------------------------------------------------------------------

# Variables brutes nécessaires au calcul des 13 features Boruta
REQUIRED_RAW_VARIABLES = [
    # Profil
    "anciennete_annees",
    # ERP Trésorerie
    "chiffre_affaires",
    "charges_exploitation",
    "marge_nette",
    "variabilite_ca",
    "ratio_endettement",
    "couverture_dette",
    # ERP Comportement Paiement
    "nb_retards_paiement_12m",
    "jours_retard_moyen",
    "nb_factures_impayees",
    "taux_recouvrement_creances",
    "regularite_paiement_mobile",
    "regularite_paiement_fournisseurs",
    # CET — Contexte Économique Territorial
    "score_reseau_communautaire",
    "appartenance_association",
    "pct_clients_recurrents",
    "score_reputation_terrain",
    "diversification_activites",
    "exposition_zones_instables",
    "stock_securite_jours",
]


def compute_features(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les 13 features Boruta à partir des variables brutes.

    Parameters
    ----------
    raw : pd.DataFrame
        DataFrame avec au minimum les colonnes listées dans
        REQUIRED_RAW_VARIABLES.

    Returns
    -------
    pd.DataFrame avec exactement les 13 colonnes attendues par le modèle.
    """
    df = raw.copy()

    # --- Ratios ERP ---
    df["charges_ratio"] = (
        df["charges_exploitation"] / df["chiffre_affaires"].clip(lower=1)
    ).round(4)

    df["intensite_retards"] = (
        df["nb_retards_paiement_12m"] * df["jours_retard_moyen"]
    )

    # --- Score comportement transactionnel ---
    max_factures = df["nb_factures_impayees"].max()
    if max_factures == 0:
        max_factures = 1  # éviter division par zéro
    df["score_comportement_transactionnel"] = (
        df["regularite_paiement_fournisseurs"] * 0.30
        + df["regularite_paiement_mobile"] * 0.25
        + df["taux_recouvrement_creances"] * 0.25
        + (1 - df["nb_factures_impayees"] / max_factures) * 0.20
    ).round(4)

    # --- Scores CET composites ---
    df["score_reseau_reputation"] = (
        df["score_reseau_communautaire"] * 0.25
        + df["appartenance_association"] * 0.25
        + df["pct_clients_recurrents"] * 0.25
        + df["score_reputation_terrain"] * 0.25
    ).round(4)

    df["score_robustesse_contextuelle"] = (
        df["diversification_activites"] * 0.30
        + (1 - df["exposition_zones_instables"]) * 0.30
        + (df["stock_securite_jours"] / 90).clip(0, 1) * 0.20
        + (1 - df["variabilite_ca"] / 0.6).clip(0, 1) * 0.20
    ).round(4)

    # --- Sélectionner les 13 features dans l'ordre du modèle ---
    artifacts = _load_model()
    feature_names = artifacts["feature_names"]

    # Les features brutes directes + calculées
    return df[feature_names]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

RISK_CATEGORIES = [
    (750, "Excellent"),
    (650, "Bon"),
    (550, "Acceptable"),
    (450, "Risqué"),
    (0, "Très risqué"),
]


def get_risk_category(score: int) -> str:
    for threshold, label in RISK_CATEGORIES:
        if score >= threshold:
            return label
    return "Très risqué"


def predict(raw_data: dict | pd.DataFrame) -> dict:
    """
    Scoring complet : données brutes → score de crédit.

    Parameters
    ----------
    raw_data : dict ou pd.DataFrame
        Variables brutes d'une PME (voir REQUIRED_RAW_VARIABLES).
        Si dict, sera converti en DataFrame 1 ligne.

    Returns
    -------
    dict avec :
        - probability_default : float (0-1)
        - credit_score : int (300-850)
        - risk_category : str
        - model_version : str
    """
    artifacts = _load_model()
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    feature_names = artifacts["feature_names"]

    # Convertir dict → DataFrame
    if isinstance(raw_data, dict):
        df = pd.DataFrame([raw_data])
    else:
        df = raw_data.copy()

    # Valider les variables requises
    missing = [v for v in REQUIRED_RAW_VARIABLES if v not in df.columns]
    if missing:
        raise ValueError(f"Variables manquantes : {missing}")

    # Feature engineering
    X = compute_features(df)

    # Standardisation (scaler fitté à l'entraînement)
    X[feature_names] = scaler.transform(X[feature_names])

    # Prédiction
    prob_default = model.predict_proba(X)[:, 1]

    # Conversion score de crédit (300-850)
    credit_scores = ((1 - prob_default) * 550 + 300).round(0).astype(int)

    results = []
    for i in range(len(df)):
        results.append(
            {
                "probability_default": round(float(prob_default[i]), 4),
                "credit_score": int(credit_scores[i]),
                "risk_category": get_risk_category(int(credit_scores[i])),
                "model_version": artifacts["metadata"]["version"],
            }
        )

    return results[0] if len(results) == 1 else results
