#!/usr/bin/env python3
"""
Generate all 8 article figures from saved data + model.
No retraining required: loads data_classique_seed.csv and model JSON.

Usage:
    python papers/extract_figures.py

Outputs -> papers/figures/fig1_..fig8_.png
"""
import os, sys, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (roc_curve, roc_auc_score, precision_recall_curve,
                             average_precision_score, confusion_matrix)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "papers", "figures")
os.makedirs(OUT, exist_ok=True)

# ── 1. Load raw data ────────────────────────────────────────────────────────
data = pd.read_csv(os.path.join(ROOT, "data", "data_classique_seed.csv"))
print(f"Data loaded: {data.shape}")

# ── 2. Feature engineering (mirrors NB1 exactly) ────────────────────────────
data["ca_par_employe"] = (data["chiffre_affaires"] / data["nb_employes"].clip(lower=1)).round(0)
data["charges_ratio"] = (data["charges_exploitation"] / data["chiffre_affaires"].clip(lower=1)).round(4)
data["flux_net_ratio"] = (data["flux_tresorerie_net"] / data["entrees_tresorerie_mois"].clip(lower=1)).round(4)
data["intensite_retards"] = data["nb_retards_paiement_12m"] * data["jours_retard_moyen"]
data["tresorerie_par_employe"] = (data["solde_caisse_moyen"] / data["nb_employes"].clip(lower=1)).round(0)
data["charge_remboursement_ratio"] = (
    data["remboursements_dettes_mois"] / data["entrees_tresorerie_mois"].clip(lower=1)
).round(4)
data["solde_caisse_ratio"] = (data["solde_caisse_moyen"] / data["chiffre_affaires"].clip(lower=1)).round(4)
data["score_comportement_transactionnel"] = (
    data["regularite_paiement_fournisseurs"] * 0.30 +
    data["regularite_paiement_mobile"] * 0.25 +
    data["taux_recouvrement_creances"] * 0.25 +
    (1 - data["nb_factures_impayees"] / data["nb_factures_impayees"].max()) * 0.20
).round(4)
data["score_reseau_reputation"] = (
    data["score_reseau_communautaire"] * 0.25 +
    data["appartenance_association"] * 0.25 +
    data["pct_clients_recurrents"] * 0.25 +
    data["score_reputation_terrain"] * 0.25
).round(4)
data["score_robustesse_contextuelle"] = (
    data["diversification_activites"] * 0.30 +
    (1 - data["exposition_zones_instables"]) * 0.30 +
    (data["stock_securite_jours"] / 90).clip(0, 1) * 0.20 +
    (1 - data["variabilite_ca"] / 0.6).clip(0, 1) * 0.20
).round(4)
data["creances_deviation_norme"] = (data["creances_sur_ca"] / 1.28).round(3)
data["score_psychometrie"] = (
    data["score_debrouillardise"] * 0.50 +
    data["usage_whatsapp_business"] * 0.20 +
    (data["anciennete_annees"] / 30).clip(0, 1) * 0.30
).round(4)
data["score_presence_digitale"] = (
    np.log1p(data["social_media_abonnes"]) * 0.3 +
    np.log1p(data["trafic_web_mensuel"]) * 0.3 +
    data["note_avis_moyenne"] / 5 * 0.2 +
    np.log1p(data["nb_avis_en_ligne"]) * 0.2
).round(4)
data["score_regularite_utilites"] = (
    data["regularite_paiement_energie"] * 0.35 +
    data["regularite_paiement_eau"] * 0.30 +
    data["regularite_paiement_loyer"] * 0.35
).round(4)
data["energie_par_employe"] = (data["conso_energie_kwh"] / data["nb_employes"].clip(lower=1)).round(2)
data["eau_par_employe"] = (data["conso_eau_m3"] / data["nb_employes"].clip(lower=1)).round(2)
data["anciennete_log"] = np.log1p(data["anciennete_annees"]).round(4)
data["employes_log"] = np.log1p(data["nb_employes"]).round(4)

# ── 3. Encode & split (mirrors NB1) ─────────────────────────────────────────
target = "default"
cat_vars = ["secteur", "taille", "localisation"]
X = data.drop(columns=[target])
y = data[target]

encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
cat_encoded = pd.DataFrame(
    encoder.fit_transform(X[cat_vars]),
    columns=encoder.get_feature_names_out(cat_vars),
    index=X.index,
)
X = pd.concat([X.drop(columns=cat_vars), cat_encoded], axis=1)
num_features = X.select_dtypes(include=np.number).columns.tolist()
scaler = StandardScaler()
X[num_features] = scaler.fit_transform(X[num_features])

# Use same 13 features as the saved model
BORUTA_FEATURES = [
    "marge_nette", "variabilite_ca", "ratio_endettement",
    "nb_retards_paiement_12m", "intensite_retards",
    "score_comportement_transactionnel", "anciennete_annees",
    "couverture_dette", "jours_retard_moyen",
    "taux_recouvrement_creances", "charges_ratio",
    "score_reseau_reputation", "score_robustesse_contextuelle",
]
X = X[BORUTA_FEATURES]
scaler2 = StandardScaler()
X[BORUTA_FEATURES] = scaler2.fit_transform(X[BORUTA_FEATURES])

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
X_valid, X_test, y_valid, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# ── 4. Load saved model ─────────────────────────────────────────────────────
model = xgb.XGBClassifier()
model.load_model(os.path.join(ROOT, "models", "model_classique_xgboost_bghm.json"))
booster = model.get_booster()
booster.feature_names = BORUTA_FEATURES
n_trees = booster.num_boosted_rounds()
print(f"Model loaded: {n_trees} trees, {len(BORUTA_FEATURES)} features")

y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred = (y_pred_proba >= 0.5).astype(int)

print(f"Test AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11,
    "figure.dpi": 150, "savefig.dpi": 150,
})


# ═══════════════════════════════════════════════════════════════════════════
# FIG 1 — Distribution des defauts
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

counts = data["default"].value_counts().sort_index()
bars = axes[0].bar(["Sain (0)", "Défaut (1)"], counts.values,
                   color=["#2ecc71", "#e74c3c"], edgecolor="white")
for b, c in zip(bars, counts.values):
    axes[0].text(b.get_x() + b.get_width()/2, c + 30,
                 f"{c}\n({c/len(data)*100:.1f}%)", ha="center", fontsize=10)
axes[0].set_ylabel("Nombre de PME")
axes[0].set_title("Distribution des classes")
axes[0].grid(True, alpha=0.3, axis="y")

sector_default = data.groupby("secteur")["default"].mean().sort_values() * 100
sector_default.plot(kind="barh", ax=axes[1], color="#3498db", edgecolor="white")
axes[1].set_xlabel("Taux de défaut (%)")
axes[1].set_title("Taux de défaut par secteur")
axes[1].grid(True, alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig1_distribution_defauts.png"))
plt.close()
print("fig1 OK")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 2 — Correlations
# ═══════════════════════════════════════════════════════════════════════════
num_data = data.select_dtypes(include=np.number)
corr_with_default = num_data.corr()["default"].drop("default").sort_values()
top15 = corr_with_default.abs().nlargest(15).index.tolist()

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

colors_corr = ["#e74c3c" if v > 0 else "#3498db" for v in corr_with_default[top15]]
corr_with_default[top15].plot(kind="barh", ax=axes[0], color=colors_corr, edgecolor="white")
axes[0].set_xlabel("Corrélation de Pearson avec le défaut")
axes[0].set_title("Top 15 corrélations avec le défaut")
axes[0].grid(True, alpha=0.3, axis="x")

corr_matrix = num_data[top15].corr()
mask_tri = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, mask=mask_tri, cmap="RdBu_r", center=0, vmin=-1, vmax=1,
            ax=axes[1], square=True, linewidths=0.5,
            xticklabels=True, yticklabels=True, cbar_kws={"shrink": 0.8})
axes[1].set_title("Matrice de corrélation (15 var.)")
axes[1].tick_params(axis="both", labelsize=7)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig2_correlations.png"))
plt.close()
print("fig2 OK")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 3 — Distributions cles (KDE)
# ═══════════════════════════════════════════════════════════════════════════
kde_vars = [
    "marge_nette", "ratio_endettement", "nb_retards_paiement_12m",
    "score_comportement_transactionnel", "taux_recouvrement_creances",
    "score_reseau_reputation", "score_robustesse_contextuelle",
    "pct_mobile_money", "variabilite_ca",
]
fig, axes = plt.subplots(3, 3, figsize=(16, 12))
for i, col in enumerate(kde_vars):
    ax = axes.flatten()[i]
    for label, color in [(0, "#2ecc71"), (1, "#e74c3c")]:
        subset = data.loc[data["default"] == label, col].dropna()
        if len(subset) > 1:
            subset.plot.kde(ax=ax, color=color, lw=2,
                            label="Sain" if label == 0 else "Défaut")
    ax.set_title(col, fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle("Distributions KDE stratifiées par statut de défaut", fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig3_distributions_cles.png"))
plt.close()
print("fig3 OK")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 4 — Learning curve (evaluate saved model at each tree count)
# ═══════════════════════════════════════════════════════════════════════════
dmat_train = xgb.DMatrix(X_train, label=y_train, feature_names=BORUTA_FEATURES)
dmat_valid = xgb.DMatrix(X_valid, label=y_valid, feature_names=BORUTA_FEATURES)

step = max(1, n_trees // 100)  # sample ~100 points
tree_counts = list(range(step, n_trees + 1, step))
if tree_counts[-1] != n_trees:
    tree_counts.append(n_trees)

train_aucs, valid_aucs = [], []
for n in tree_counts:
    p_tr = booster.predict(dmat_train, iteration_range=(0, n))
    p_va = booster.predict(dmat_valid, iteration_range=(0, n))
    train_aucs.append(roc_auc_score(y_train, p_tr))
    valid_aucs.append(roc_auc_score(y_valid, p_va))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(tree_counts, train_aucs, label="Train", color="#3498db", lw=2)
ax.plot(tree_counts, valid_aucs, label="Validation", color="#e74c3c", lw=2)
ax.set_xlabel("Nombre d'itérations (arbres)")
ax.set_ylabel("AUC")
ax.set_title("Courbe d'apprentissage, Génération Classique (AUC)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig4_learning_curve.png"))
plt.close()
print(f"fig4 OK  (Train AUC final={train_aucs[-1]:.4f}, Val={valid_aucs[-1]:.4f})")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 5 — ROC, Precision-Recall, Confusion Matrix
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
auc_val = roc_auc_score(y_test, y_pred_proba)
axes[0].plot(fpr, tpr, color="#e74c3c", lw=2, label=f"AUC = {auc_val:.3f}")
axes[0].plot([0, 1], [0, 1], "k--", lw=1)
axes[0].fill_between(fpr, tpr, alpha=0.1, color="#e74c3c")
axes[0].set_xlabel("FPR"); axes[0].set_ylabel("TPR")
axes[0].set_title("Courbe ROC, Génération Classique")
axes[0].legend(); axes[0].grid(True, alpha=0.3)

prec, rec, _ = precision_recall_curve(y_test, y_pred_proba)
ap_val = average_precision_score(y_test, y_pred_proba)
axes[1].plot(rec, prec, color="#3498db", lw=2, label=f"AP = {ap_val:.3f}")
axes[1].fill_between(rec, prec, alpha=0.1, color="#3498db")
axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
axes[1].set_title("Precision-Recall, Génération Classique")
axes[1].legend(); axes[1].grid(True, alpha=0.3)

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[2],
            xticklabels=["Sain", "Défaut"], yticklabels=["Sain", "Défaut"])
axes[2].set_xlabel("Prédiction"); axes[2].set_ylabel("Réalité")
axes[2].set_title("Matrice de Confusion")

plt.suptitle("Évaluation, Génération Classique (Paramétrique)", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig5_roc_pr_confusion.png"))
plt.close()
print(f"fig5 OK  (CM: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]})")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 6 — Feature Importance (top 13 by gain)
# ═══════════════════════════════════════════════════════════════════════════
importance = booster.get_score(importance_type="gain")
fi = pd.DataFrame({"feature": list(importance.keys()),
                    "gain": list(importance.values())})
fi = fi.sort_values("gain", ascending=True)

CATEGORY_MAP = {
    "marge_nette": ("ERP, Trésorerie", "#3498db"),
    "variabilite_ca": ("ERP, Transactionnel", "#2ecc71"),
    "ratio_endettement": ("ERP, Trésorerie", "#3498db"),
    "nb_retards_paiement_12m": ("ERP, Comportement paiement", "#9b59b6"),
    "intensite_retards": ("ERP, Comportement paiement", "#9b59b6"),
    "score_comportement_transactionnel": ("ERP, Comportement paiement", "#9b59b6"),
    "anciennete_annees": ("Profil entreprise", "#95a5a6"),
    "couverture_dette": ("ERP, Trésorerie", "#3498db"),
    "jours_retard_moyen": ("ERP, Comportement paiement", "#9b59b6"),
    "taux_recouvrement_creances": ("ERP, Comportement paiement", "#9b59b6"),
    "charges_ratio": ("ERP, Trésorerie", "#3498db"),
    "score_reseau_reputation": ("CET, Contexte territorial", "#e74c3c"),
    "score_robustesse_contextuelle": ("CET, Contexte territorial", "#e74c3c"),
}
colors_fi = [CATEGORY_MAP.get(f, ("Autre", "#95a5a6"))[1] for f in fi["feature"]]

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(fi["feature"], fi["gain"], color=colors_fi, edgecolor="white")
ax.set_xlabel("Gain")
ax.set_title(f"Importance des {len(fi)} variables (XGBoost-B-GHM, Génération Classique)")
ax.grid(True, alpha=0.3, axis="x")

from matplotlib.patches import Patch
seen = {}
for f in fi["feature"]:
    cat, col = CATEGORY_MAP.get(f, ("Autre", "#95a5a6"))
    seen[cat] = col
legend_elements = [Patch(facecolor=c, label=l) for l, c in seen.items()]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig6_feature_importance.png"))
plt.close()
print(f"fig6 OK  (top feature: {fi.iloc[-1]['feature']})")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 7 — SHAP analysis (bar + beeswarm)
# ═══════════════════════════════════════════════════════════════════════════
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

fig, axes = plt.subplots(1, 2, figsize=(20, 8))

plt.sca(axes[0])
shap.summary_plot(shap_values, X_test, plot_type="bar", max_display=13, show=False)
axes[0].set_title("SHAP, Importance globale")

plt.sca(axes[1])
shap.summary_plot(shap_values, X_test, max_display=13, show=False)
axes[1].set_title("SHAP, Impact directionnel (Beeswarm)")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig7_shap_analysis.png"))
plt.close()
print("fig7 OK")


# ═══════════════════════════════════════════════════════════════════════════
# FIG 8 — Credit scores & risk categories
# ═══════════════════════════════════════════════════════════════════════════
scores = ((1 - y_pred_proba) * 550 + 300).round(0).astype(int)

def risk_cat(s):
    if s >= 750: return "Excellent"
    if s >= 650: return "Bon"
    if s >= 550: return "Acceptable"
    if s >= 450: return "Risqué"
    return "Très risqué"

risk_categories = pd.Series(scores).apply(risk_cat)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(scores[y_test.values == 0], bins=30, alpha=0.6, color="#2ecc71",
             label="Sain", density=True)
axes[0].hist(scores[y_test.values == 1], bins=30, alpha=0.6, color="#e74c3c",
             label="Défaut", density=True)
axes[0].axvline(550, color="#e67e22", ls="--", lw=2, label="Seuil (550)")
axes[0].set_xlabel("Score de crédit"); axes[0].set_ylabel("Densité")
axes[0].set_title("Distribution des scores, Génération Classique")
axes[0].legend(); axes[0].grid(True, alpha=0.3)

cat_order = ["Excellent", "Bon", "Acceptable", "Risqué", "Très risqué"]
cat_counts = risk_categories.value_counts().reindex(cat_order)
colors_cat = ["#2ecc71", "#27ae60", "#f39c12", "#e67e22", "#e74c3c"]
cat_counts.plot(kind="bar", ax=axes[1], color=colors_cat, edgecolor="white")
axes[1].set_title("Catégories de risque, Génération Classique")
axes[1].set_ylabel("Nombre de PME")
axes[1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig8_scores_categories.png"))
plt.close()
print("fig8 OK")


# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("All 8 figures generated in", OUT)
for f in sorted(os.listdir(OUT)):
    if f.startswith("fig"):
        sz = os.path.getsize(os.path.join(OUT, f))
        print(f"  {f}  ({sz:,} bytes)")
print("=" * 60)

# Print metrics for article update reference
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, brier_score_loss
print("\nMetrics for article (Classique):")
print(f"  Accuracy    : {accuracy_score(y_test, y_pred):.3f}")
print(f"  Precision   : {precision_score(y_test, y_pred, zero_division=0):.3f}")
print(f"  Recall      : {recall_score(y_test, y_pred):.3f}")
print(f"  F1-Score    : {f1_score(y_test, y_pred):.3f}")
print(f"  AUC-ROC     : {roc_auc_score(y_test, y_pred_proba):.3f}")
print(f"  AUC-PR      : {average_precision_score(y_test, y_pred_proba):.3f}")
print(f"  Brier Score : {brier_score_loss(y_test, y_pred_proba):.3f}")
print(f"  CM: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")


if __name__ == "__main__":
    pass
