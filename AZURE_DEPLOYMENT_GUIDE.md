# 🚀 GUIDE COMPLET : DÉPLOIEMENT AZURE - WANZO BACKEND

## 📋 TABLE DES MATIÈRES
1. [Architecture de déploiement](#architecture)
2. [Prérequis](#prerequis)
3. [Configuration Azure](#configuration-azure)
4. [Configuration GitHub](#configuration-github)
5. [Déploiement CI/CD](#deploiement-cicd)
6. [Frontends (Flutter & React)](#frontends)
7. [Monitoring & Maintenance](#monitoring)
8. [**Leçons Apprises - Déploiement VM Azure**](#leçons-apprises---déploiement-vm-azure-janvier-2026)
9. [**🛡️ Backup & Disaster Recovery**](#-backup--disaster-recovery-janvier-2026)

---

## 🏗️ ARCHITECTURE DE DÉPLOIEMENT

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB REPOSITORY                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐         │
│  │  Backend │  │ Flutter  │  │  React Vite Apps │         │
│  │   /apps  │  │   App    │  │   (Web Portals)  │         │
│  └────┬─────┘  └────┬─────┘  └─────────┬────────┘         │
└───────┼─────────────┼──────────────────┼──────────────────┘
        │             │                   │
        │             │                   │
   [GitHub Actions]   │                   │
        │             │                   │
        ▼             ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│              AZURE CLOUD SERVICES                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Container Registry (ACR)                     │   │
│  │  - wanzo-deps-base:latest                           │   │
│  │  - wanzo-production-base:latest                     │   │
│  │  - accounting-service:v1.2.3                        │   │
│  │  - admin-service, analytics-service, etc...         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Container Apps Environment                   │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │ API Gateway  │  │ Admin Service│                │   │
│  │  │  :8000       │  │    :3001     │                │   │
│  │  │  (external)  │  │  (internal)  │                │   │
│  │  └──────┬───────┘  └──────────────┘                │   │
│  │         │                                           │   │
│  │  ┌──────┴──────────────────────────────────┐       │   │
│  │  │    Internal Microservices Network       │       │   │
│  │  │  - accounting-service:3001              │       │   │
│  │  │  - analytics-service:3002               │       │   │
│  │  │  - customer-service:3011                │       │   │
│  │  │  - gestion_commerciale_service:3006     │       │   │
│  │  │  - portfolio-institution-service:3005   │       │   │
│  │  │  - payment-service:3007                 │       │   │
│  │  │  - adha-ai-service:8002                 │       │   │
│  │  └─────────────────────────────────────────┘       │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Database for PostgreSQL Flexible Server     │   │
│  │  - admin_service                                    │   │
│  │  - accounting_service                               │   │
│  │  - analytics_service                                │   │
│  │  - customer_service                                 │   │
│  │  - gestion_commerciale_service                      │   │
│  │  - portfolio_institution_service                    │   │
│  │  - payment_service                                  │   │
│  │  - adha_ai_service                                  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Event Hubs (remplace Kafka)                 │   │
│  │  - user-events (4 partitions)                      │   │
│  │  - transaction-events                               │   │
│  │  - accounting-events                                │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Key Vault (Secrets Management)              │   │
│  │  - DB_PASSWORD                                      │   │
│  │  - AUTH0_CLIENT_SECRET                              │   │
│  │  - ENCRYPTION_SECRET_KEY                            │   │
│  │  - OPENAI_API_KEY                                   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Monitor + Application Insights               │   │
│  │  - Logs, Metrics, Traces                           │   │
│  │  - Alertes automatiques                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure Static Web Apps                              │   │
│  │  - React Admin Portal                               │   │
│  │  - React Customer Portal                            │   │
│  │  - React Institution Portal                         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Azure App Center                                   │   │
│  │  - Flutter Mobile App (iOS/Android)                │   │
│  │  - Distribution, Analytics, Crashes                │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   UTILISATEURS FINAUX                       │
│  📱 Mobile App  →  API Gateway (external)                   │
│  🌐 Web Portals →  Static Web Apps → API Gateway           │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ PRÉREQUIS

### Comptes & Accès
- ✅ Compte Azure (avec Subscription ID)
- ✅ Compte GitHub (avec admin access sur le repo)
- ✅ Azure CLI installé localement
- ✅ Docker Desktop (pour tests locaux)
- ✅ Node.js 20+ & Yarn (déjà installé)

### Coûts estimés Azure (par mois)
- Container Apps (8 services) : ~$150-300
- PostgreSQL Flexible Server : ~$50-100
- Event Hubs Standard : ~$50
- Container Registry : ~$10
- Key Vault : ~$5
- Static Web Apps (3 portails) : $0 (Free tier)
- **TOTAL : ~$265-465/mois**

---

## 🔧 PHASE 1 : CONFIGURATION AZURE

### 1.1 Installer Azure CLI

```powershell
# Windows (déjà fait si Azure CLI disponible)
winget install -e --id Microsoft.AzureCLI

# Connexion
az login

# Vérifier subscription
az account show
az account list --output table

# Définir subscription active (si plusieurs)
az account set --subscription "VOTRE_SUBSCRIPTION_ID"
```

### 1.2 Créer les ressources de base

```powershell
# Variables (à personnaliser)
$RESOURCE_GROUP="wanzo-prod-rg"
$LOCATION="westeurope"
$ACR_NAME="wanzoregistry"
$POSTGRES_SERVER="wanzo-postgres-prod"
$POSTGRES_ADMIN="wanzoadmin"
$POSTGRES_PASSWORD="VotreMotDePasseSecurisé123!"  # CHANGEZ ÇA!
$KEYVAULT_NAME="wanzo-keyvault-prod"
$CONTAINER_ENV="wanzo-prod-env"

# 1. Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Azure Container Registry (ACR)
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $ACR_NAME `
  --sku Standard `
  --location $LOCATION

az acr update --name $ACR_NAME --admin-enabled true

# Récupérer credentials ACR (pour GitHub Secrets)
az acr credential show --name $ACR_NAME
# ⚠️ SAUVEGARDER username et password pour GitHub Secrets

# 3. PostgreSQL Flexible Server
az postgres flexible-server create `
  --resource-group $RESOURCE_GROUP `
  --name $POSTGRES_SERVER `
  --location $LOCATION `
  --admin-user $POSTGRES_ADMIN `
  --admin-password $POSTGRES_PASSWORD `
  --sku-name Standard_B2s `
  --tier Burstable `
  --version 14 `
  --storage-size 32 `
  --public-access 0.0.0.0 `
  --backup-retention 7

# Créer les bases de données
$databases = @(
    "admin_service",
    "accounting_service",
    "analytics_service",
    "customer_service",
    "gestion_commerciale_service",
    "portfolio_institution_service",
    "payment_service",
    "adha_ai_service"
)

foreach ($db in $databases) {
    az postgres flexible-server db create `
        --resource-group $RESOURCE_GROUP `
        --server-name $POSTGRES_SERVER `
        --database-name $db
    Write-Host "✅ Created database: $db"
}

# 4a. OPTION 1 : GARDER KAFKA AUTO-HÉBERGÉ (RECOMMANDÉ) ✅

# Créer VM pour Kafka + Zookeeper
az vm create `
  --resource-group $RESOURCE_GROUP `
  --name wanzo-kafka-vm `
  --image Ubuntu2204 `
  --size Standard_B2s `
  --admin-username azureuser `
  --generate-ssh-keys `
  --public-ip-address-allocation Static `
  --nsg-rule SSH

# Ouvrir ports Kafka
az vm open-port --resource-group $RESOURCE_GROUP --name wanzo-kafka-vm --port 9092 --priority 1001
az vm open-port --resource-group $RESOURCE_GROUP --name wanzo-kafka-vm --port 2181 --priority 1002

# SSH dans la VM et installer Kafka
# ssh azureuser@<IP_VM>
# Ensuite exécuter :
# sudo apt-get update
# sudo apt-get install -y docker.io docker-compose
# sudo systemctl start docker
# sudo systemctl enable docker
# 
# Créer docker-compose.yml avec Kafka + Zookeeper (voir ci-dessous)

Write-Host "✅ VM Kafka créée. IP: " (az vm show -d -g $RESOURCE_GROUP -n wanzo-kafka-vm --query publicIps -o tsv)
Write-Host "⚠️ IMPORTANT: Connectez-vous en SSH et déployez Kafka avec Docker Compose"

# 4b. OPTION 2 : AZURE EVENT HUBS (Alternative managée)
# Si vous voulez un service managé (plus cher ~$50/mois mais aucun serveur à gérer)

# az eventhubs namespace create `
#   --name wanzo-eventhub-prod `
#   --resource-group $RESOURCE_GROUP `
#   --location $LOCATION `
#   --sku Standard `
#   --capacity 1

# az eventhubs eventhub create `
#   --resource-group $RESOURCE_GROUP `
#   --namespace-name wanzo-eventhub-prod `
#   --name user-events `
#   --partition-count 4 `
#   --message-retention 7

# Récupérer connection string (pour GitHub Secrets)
# az eventhubs namespace authorization-rule keys list `
#   --resource-group $RESOURCE_GROUP `
#   --namespace-name wanzo-eventhub-prod `
#   --name RootManageSharedAccessKey `
#   --query primaryConnectionString -o tsv

# 5. Azure Key Vault
az keyvault create `
  --name $KEYVAULT_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --enable-rbac-authorization false

# Ajouter secrets
az keyvault secret set --vault-name $KEYVAULT_NAME `
  --name "DB-PASSWORD" --value $POSTGRES_PASSWORD

az keyvault secret set --vault-name $KEYVAULT_NAME `
  --name "AUTH0-CLIENT-SECRET" --value "votre_auth0_secret"

az keyvault secret set --vault-name $KEYVAULT_NAME `
  --name "ENCRYPTION-SECRET-KEY" --value "6FketZDIaxXjbissbTwN9mTpeXRjDLLvflbUBnHDqPU="

az keyvault secret set --vault-name $KEYVAULT_NAME `
  --name "OPENAI-API-KEY" --value "votre_openai_key"

# 6. Container Apps Environment
az containerapp env create `
  --name $CONTAINER_ENV `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION

# Lier Key Vault à Container Apps Environment
$KEYVAULT_ID=$(az keyvault show --name $KEYVAULT_NAME --query id -o tsv)

az containerapp env update `
  --name $CONTAINER_ENV `
  --resource-group $RESOURCE_GROUP `
  --mi-system-assigned

# Donner accès Key Vault au Managed Identity
$ENV_IDENTITY=$(az containerapp env show `
  --name $CONTAINER_ENV `
  --resource-group $RESOURCE_GROUP `
  --query identity.principalId -o tsv)

az keyvault set-policy `
  --name $KEYVAULT_NAME `
  --object-id $ENV_IDENTITY `
  --secret-permissions get list
```

### 1.3 Créer Service Principal pour GitHub Actions

```powershell
# Créer Service Principal
$SP_NAME="github-actions-wanzo"
$SUBSCRIPTION_ID=$(az account show --query id -o tsv)

az ad sp create-for-rbac `
  --name $SP_NAME `
  --role Contributor `
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP `
  --sdk-auth

# ⚠️ SAUVEGARDER TOUT LE JSON RETOURNÉ pour GitHub Secret: AZURE_CREDENTIALS
```

---

## 🔐 PHASE 2 : CONFIGURATION GITHUB

### 2.1 Ajouter GitHub Secrets

Aller sur votre repo GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Ajouter ces secrets :

| Secret Name | Valeur | Source |
|-------------|--------|--------|
| `AZURE_CREDENTIALS` | JSON du Service Principal | Sortie de `az ad sp create-for-rbac` |
| `ACR_USERNAME` | Username ACR | `az acr credential show --name wanzoregistry` |
| `ACR_PASSWORD` | Password ACR | `az acr credential show --name wanzoregistry` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | Variable `$POSTGRES_PASSWORD` |
| `EVENTHUB_CONNECTION_STRING` | Connection string Event Hubs | `az eventhubs namespace authorization-rule keys list` |
| `AUTH0_CLIENT_SECRET` | Secret Auth0 | Tableau de bord Auth0 |
| `OPENAI_API_KEY` | Clé OpenAI | OpenAI Dashboard |
| `ENCRYPTION_SECRET_KEY` | Clé de chiffrement | `6FketZDIaxXjbissbTwN9mTpeXRjDLLvflbUBnHDqPU=` |

### 2.2 Workflow GitHub Actions déjà créé

Le fichier `.github/workflows/azure-deploy.yml` a été créé et contient :
- ✅ Build des images de base (wanzo-deps-base, wanzo-production-base)
- ✅ Build parallèle des 8 microservices
- ✅ Push vers Azure Container Registry
- ✅ Déploiement automatique vers Azure Container Apps
- ✅ Health checks post-déploiement

---

## 🚀 PHASE 3 : PREMIER DÉPLOIEMENT

### 3.1 Test local avant push

```powershell
# Build et test local
docker-compose --profile prod build
docker-compose --profile prod up -d

# Vérifier que tous les services démarrent
docker-compose ps

# Test API Gateway
curl http://localhost:8000/health

# Arrêter
docker-compose down
```

### 3.2 Push vers GitHub pour déclencher CI/CD

```powershell
git add .
git commit -m "feat: Configure Azure deployment with GitHub Actions CI/CD"
git push origin dev-payment
```

🎉 **GitHub Actions va automatiquement** :
1. Builder les images Docker
2. Pusher vers Azure Container Registry
3. Déployer vers Azure Container Apps
4. Exécuter les health checks

### 3.3 Surveiller le déploiement

- GitHub Actions : `https://github.com/jaqcquesndav/Wanzo_Backend/actions`
- Azure Portal : Aller dans **Resource Group** → **wanzo-prod-rg**

---

## 📱 PHASE 4 : DÉPLOIEMENT FRONTENDS

### 4.1 Flutter Mobile App → Azure App Center

```powershell
# Installer App Center CLI
npm install -g appcenter-cli

# Login
appcenter login

# Créer app iOS
appcenter apps create -d "Wanzo Mobile iOS" -o iOS -p React-Native

# Créer app Android
appcenter apps create -d "Wanzo Mobile Android" -o Android -p React-Native

# Configuration dans votre projet Flutter
# Ajouter dans pubspec.yaml:
# dependencies:
#   appcenter: ^4.0.0
#   appcenter_analytics: ^4.0.0
#   appcenter_crashes: ^4.0.0
```

**GitHub Actions pour Flutter** : Créer `.github/workflows/flutter-deploy.yml`

```yaml
name: Flutter Mobile App Deployment

on:
  push:
    branches:
      - main
    paths:
      - 'mobile-app/**'

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v3
        with:
          distribution: 'zulu'
          java-version: '11'
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      
      - name: Install dependencies
        working-directory: ./mobile-app
        run: flutter pub get

      - name: Build APK
        working-directory: ./mobile-app
        run: flutter build apk --release

      - name: Upload to App Center
        run: |
          appcenter distribute release \
            --app jaqcques/Wanzo-Android \
            --file mobile-app/build/app/outputs/flutter-apk/app-release.apk \
            --group Collaborators
        env:
          APPCENTER_API_TOKEN: ${{ secrets.APPCENTER_API_TOKEN }}

  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      
      - name: Install dependencies
        working-directory: ./mobile-app
        run: flutter pub get

      - name: Build iOS
        working-directory: ./mobile-app
        run: flutter build ios --release --no-codesign

      - name: Upload to App Center
        run: |
          appcenter distribute release \
            --app jaqcques/Wanzo-iOS \
            --file mobile-app/build/ios/ipa/Runner.ipa \
            --group Collaborators
        env:
          APPCENTER_API_TOKEN: ${{ secrets.APPCENTER_API_TOKEN }}
```

### 4.2 React Web Apps → Azure Static Web Apps

```powershell
# Pour chaque app React (admin-portal, customer-portal, institution-portal)

# 1. Créer Static Web App via Azure CLI
az staticwebapp create `
  --name wanzo-admin-portal `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --source https://github.com/jaqcquesndav/Wanzo_Frontend `
  --branch main `
  --app-location "/admin-portal" `
  --output-location "dist" `
  --sku Free

# 2. Récupérer deployment token
az staticwebapp secrets list `
  --name wanzo-admin-portal `
  --resource-group $RESOURCE_GROUP `
  --query "properties.apiKey" -o tsv
# ⚠️ Ajouter dans GitHub Secret: AZURE_STATIC_WEB_APPS_API_TOKEN_ADMIN

# Répéter pour customer-portal et institution-portal
```

**GitHub Actions pour React** : `.github/workflows/react-deploy.yml`

```yaml
name: React Web Apps Deployment

on:
  push:
    branches:
      - main
    paths:
      - 'admin-portal/**'
      - 'customer-portal/**'
      - 'institution-portal/**'

jobs:
  deploy-admin-portal:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: ./admin-portal
        run: npm ci

      - name: Build
        working-directory: ./admin-portal
        run: npm run build
        env:
          VITE_API_URL: https://wanzo-api-gateway.azurecontainerapps.io

      - name: Deploy to Azure Static Web Apps
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN_ADMIN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/admin-portal"
          output_location: "dist"

  # Répéter pour customer-portal et institution-portal
```

---

## 📊 PHASE 5 : MONITORING & MAINTENANCE

### 5.1 Configurer Azure Monitor

```powershell
# Activer Application Insights
az monitor app-insights component create `
  --app wanzo-app-insights `
  --location $LOCATION `
  --resource-group $RESOURCE_GROUP `
  --application-type web

# Récupérer Instrumentation Key
$INSTRUMENTATION_KEY=$(az monitor app-insights component show `
  --app wanzo-app-insights `
  --resource-group $RESOURCE_GROUP `
  --query instrumentationKey -o tsv)

# Ajouter dans Key Vault
az keyvault secret set --vault-name $KEYVAULT_NAME `
  --name "APPINSIGHTS-INSTRUMENTATION-KEY" --value $INSTRUMENTATION_KEY
```

### 5.2 Configurer Alertes

```powershell
# Créer Action Group (email)
az monitor action-group create `
  --name wanzo-alerts `
  --resource-group $RESOURCE_GROUP `
  --short-name wanzo `
  --email-receiver name=admin email=votre-email@example.com

# Alerte: Service Down
az monitor metrics alert create `
  --name "API Gateway Down" `
  --resource-group $RESOURCE_GROUP `
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/wanzo-api-gateway" `
  --condition "avg Percentage CPU > 90" `
  --window-size 5m `
  --evaluation-frequency 1m `
  --action wanzo-alerts
```

### 5.3 Accéder aux logs

```powershell
# Logs en temps réel
az containerapp logs show `
  --name wanzo-api-gateway `
  --resource-group $RESOURCE_GROUP `
  --follow

# Logs Application Insights
az monitor app-insights query `
  --app wanzo-app-insights `
  --analytics-query "requests | where timestamp > ago(1h) | limit 100"
```

---

## 🔄 WORKFLOW COMPLET CI/CD

```
1. DÉVELOPPEMENT LOCAL
   └─> git add . && git commit -m "..." && git push origin dev-payment

2. GITHUB ACTIONS (Automatique)
   ├─> Build base images (wanzo-deps-base, wanzo-production-base)
   ├─> Build 8 microservices en parallèle
   ├─> Push vers Azure Container Registry
   ├─> Deploy vers Azure Container Apps
   └─> Health checks

3. AZURE CONTAINER APPS
   ├─> Pull images depuis ACR
   ├─> Deploy new revisions
   ├─> Blue-green deployment (zero downtime)
   └─> Activate new version

4. FRONTENDS (Séparément)
   ├─> Flutter App → Azure App Center (iOS/Android)
   └─> React Apps → Azure Static Web Apps

5. MONITORING
   └─> Azure Monitor + Application Insights + Alertes
```

---

## 📝 CHECKLIST FINALE

### Avant le premier déploiement :
- [ ] ✅ Resource Group créé
- [ ] ✅ Azure Container Registry configuré
- [ ] ✅ PostgreSQL avec 8 databases créées
- [ ] ✅ Azure Event Hubs créé
- [ ] ✅ Azure Key Vault avec tous les secrets
- [ ] ✅ Container Apps Environment créé
- [ ] ✅ Service Principal créé
- [ ] ✅ GitHub Secrets configurés (10 secrets minimum)
- [ ] ✅ Workflow `.github/workflows/azure-deploy.yml` présent
- [ ] ✅ Code backend poussé sur GitHub

### Après le premier déploiement :
- [ ] ✅ Vérifier GitHub Actions (tous les jobs verts)
- [ ] ✅ Tester API Gateway : `curl https://wanzo-api-gateway.azurecontainerapps.io/health`
- [ ] ✅ Vérifier logs dans Azure Portal
- [ ] ✅ Configurer Application Insights
- [ ] ✅ Configurer alertes email
- [ ] ✅ Déployer frontends (Flutter + React)
- [ ] ✅ Tester end-to-end

---

## 🆘 TROUBLESHOOTING

### Problème : Build échoue sur GitHub Actions
```powershell
# Solution : Vérifier les secrets GitHub
# Aller sur : Settings → Secrets → Actions
# Vérifier que AZURE_CREDENTIALS, ACR_USERNAME, ACR_PASSWORD sont présents
```

### Problème : Container App ne démarre pas
```powershell
# Voir les logs
az containerapp logs show `
  --name wanzo-api-gateway `
  --resource-group wanzo-prod-rg `
  --follow

# Vérifier les variables d'environnement
az containerapp show `
  --name wanzo-api-gateway `
  --resource-group wanzo-prod-rg `
  --query properties.template.containers[0].env
```

### Problème : Database connection failed
```powershell
# Vérifier firewall PostgreSQL
az postgres flexible-server firewall-rule create `
  --resource-group wanzo-prod-rg `
  --name wanzo-postgres-prod `
  --rule-name AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0
```

---

## 🎯 RÉSUMÉ - COÛTS & TIMELINES

### Coûts mensuels estimés :
- **Production** : ~$265-465/mois
- **Staging/Dev** : ~$150-200/mois (optionnel)

### Temps de mise en place :
- Configuration Azure : **2-3 heures**
- Configuration GitHub CI/CD : **1 heure**
- Premier déploiement : **30-45 minutes**
- Configuration frontends : **2-3 heures**
- **TOTAL : 1 journée de travail**

### Bénéfices :
- ✅ Déploiement continu automatique (push → production en 15min)
- ✅ Zéro downtime avec blue-green deployments
- ✅ Monitoring et alertes automatiques
- ✅ Scalabilité automatique (Azure Container Apps)
- ✅ Sécurité : Secrets dans Key Vault, pas de credentials en dur
- ✅ Multi-environnement (dev, staging, prod)

---

## 🎓 LEÇONS APPRISES - DÉPLOIEMENT VM AZURE (Janvier 2026)

### Architecture VM actuelle
```
VM Azure: 4.205.236.59
├── User: wanzoadmin
├── App Path: /data/app/Wanzo_Backend
├── Docker Compose: 8 microservices
└── Containers: kiota-* naming convention
```

### Services déployés sur VM
| Service | Container | Port | Technologie |
|---------|-----------|------|-------------|
| accounting-service | kiota-accounting-service | 3003 | NestJS |
| adha-ai-service | kiota-adha-ai-service | 8002 | Django/Python |
| gestion-commerciale-service | kiota-gestion-commerciale-service | 3006 | NestJS |
| admin-service | kiota-admin-service | 3001 | NestJS |
| customer-service | kiota-customer-service | 3011 | NestJS |
| analytics-service | kiota-analytics-service | 3002 | NestJS |
| api-gateway | kiota-api-gateway | 8000 | NestJS |
| portfolio-institution-service | kiota-portfolio-institution-service | 3005 | NestJS |

---

### ⚠️ ERREURS CRITIQUES À ÉVITER

#### 1. NE JAMAIS utiliser Compress-Archive de PowerShell pour les projets Node.js
```powershell
# ❌ MAUVAIS - Échoue avec les chemins longs de node_modules
Compress-Archive -Path "apps\accounting-service" -DestinationPath "deploy.zip"
# Erreur: Impossible de trouver une partie du chemin d'accès 
# (node_modules/@opentelemetry/... chemins trop longs)

# ✅ BON - Utiliser tar avec exclusions
tar -cvf deploy-services.tar `
  --exclude="node_modules" `
  --exclude="dist" `
  --exclude="__pycache__" `
  --exclude=".venv" `
  --exclude="*.pyc" `
  apps/accounting-service apps/Adha-ai-service apps/gestion_commerciale_service
```

#### 2. Toujours nettoyer Docker avant de reconstruire
```bash
# Sur la VM, AVANT de reconstruire:
# 1. Arrêter les containers concernés
docker-compose stop adha-ai-service kiota-accounting-service gestion-commerciale-service

# 2. Supprimer les containers
docker-compose rm -f adha-ai-service kiota-accounting-service gestion-commerciale-service

# 3. Supprimer les anciennes images
docker rmi wanzo_backend-adha-ai-service wanzo_backend-kiota-accounting-service wanzo_backend-gestion-commerciale-service

# 4. Nettoyer le cache de build Docker
docker builder prune -f
```

#### 3. Ne jamais mélanger les fichiers de différents services dans une archive
```powershell
# ❌ MAUVAIS - Archive avec structure plate qui mélange les fichiers
# Cela corrompt les services car app.module.ts d'un service écrase l'autre

# ✅ BON - Conserver la structure de dossiers
tar -cvf deploy-services.tar apps/accounting-service apps/Adha-ai-service
# Cela préserve apps/accounting-service/src/... et apps/Adha-ai-service/...
```

---

### ✅ PROCÉDURE DE DÉPLOIEMENT RAPIDE (TESTÉE ET VALIDÉE)

#### Étape 1: Préparer l'archive localement
```powershell
cd C:\Users\JACQUES\Documents\DevSpace\Wanzo_Backend

# Créer archive tar (sans node_modules/dist/__pycache__)
tar -cvf deploy-services.tar `
  --exclude="node_modules" `
  --exclude="dist" `
  --exclude="__pycache__" `
  --exclude=".venv" `
  --exclude="*.pyc" `
  apps/accounting-service apps/Adha-ai-service apps/gestion_commerciale_service
```

#### Étape 2: Envoyer l'archive à la VM
```powershell
scp deploy-services.tar wanzoadmin@4.205.236.59:/data/app/
```

#### Étape 3: Déployer sur la VM
```bash
# Connexion SSH
ssh wanzoadmin@4.205.236.59

# Aller dans le répertoire de l'app
cd /data/app/Wanzo_Backend

# Supprimer les anciens dossiers et extraire l'archive
rm -rf apps/accounting-service apps/Adha-ai-service apps/gestion_commerciale_service
cd /data/app
tar -xvf deploy-services.tar -C Wanzo_Backend/
```

#### Étape 4: Reconstruire et démarrer les services
```bash
cd /data/app/Wanzo_Backend

# Reconstruire les 3 services (en parallèle)
docker-compose build --no-cache adha-ai-service kiota-accounting-service gestion-commerciale-service

# Démarrer les services
docker-compose up -d adha-ai-service kiota-accounting-service gestion-commerciale-service
```

#### Étape 5: Vérifier l'état de santé
```bash
# Attendre 30 secondes puis vérifier
sleep 30
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'adha|accounting|gestion'

# Résultat attendu:
# kiota-gestion-commerciale-service     Up X minutes (healthy)
# kiota-adha-ai-service                 Up X minutes (healthy)
# kiota-accounting-service              Up X minutes (healthy)
```

---

### 🔧 COMMANDES SSH UTILES

```bash
# Connexion
ssh wanzoadmin@4.205.236.59

# Voir tous les containers
docker ps -a

# Voir les logs d'un service
docker logs -f kiota-accounting-service --tail 100

# Redémarrer un service
docker-compose restart kiota-accounting-service

# Voir l'utilisation des ressources
docker stats --no-stream

# Vérifier l'espace disque
df -h

# Nettoyer Docker (images/containers non utilisés)
docker system prune -af
```

---

### 📊 PROBLÈMES RÉSOLUS (Janvier 2026)

#### Problème 1: WriteMode reste bloqué à `true`
- **Symptôme**: Après désactivation du mode écriture, il reste actif
- **Cause**: Opérateur `||` dans JS traite `false` comme falsy
- **Solution**: Modifier `chat.controller.ts`:
```typescript
// ❌ Ancien code (bug)
const writeMode = chat.context?.writeMode || chatRequestDto.writeMode || false;

// ✅ Nouveau code (fix)
const writeMode = chatRequestDto.writeMode !== undefined 
  ? chatRequestDto.writeMode 
  : (chat.context?.writeMode || false);
```
- **Fichiers modifiés**: 
  - `apps/accounting-service/src/modules/chat/controllers/chat.controller.ts`
  - `apps/accounting-service/src/modules/chat/services/chat.service.ts` (ajout `updateContext()`)

#### Problème 2: Outils de calcul ADHA AI trop restrictifs
- **Symptôme**: `requires_user_input: True` bloque la génération d'écritures
- **Cause**: `_check_required_data()` trop strict sur les formats
- **Solution**: Modifier `llm_tool_system.py`:
  - Ajouter `_try_enrich_arguments()` pour mapper les noms de champs alternatifs
  - Modifier `_create_llm_fallback_response()` pour retourner des valeurs estimées
  - Mettre `requires_user_input: False` avec fallback gracieux
- **Fichier modifié**: `apps/Adha-ai-service/agents/utils/llm_tool_system.py`

#### Problème 3: Incompatibilité format journal entries
- **Symptôme**: Erreurs de validation entre ADHA AI et accounting-service
- **Cause**: Formats de champs différents (snake_case vs camelCase)
- **Solution**: 
  - Normaliser le producteur Kafka: `apps/Adha-ai-service/api/kafka/producer_accounting.py`
  - Améliorer le consumer: `apps/accounting-service/src/modules/events/consumers/adha-accounting.consumer.ts`

---

### 🔄 WORKFLOW GIT RECOMMANDÉ

```powershell
# 1. Développer et tester localement
yarn workspace @kiota-suit/accounting-service build
# ou pour Python:
python -m py_compile apps/Adha-ai-service/agents/utils/llm_tool_system.py

# 2. Commit et push
git add .
git commit -m "fix: description du fix"
git push origin main

# 3. Déployer sur VM (voir procédure ci-dessus)

# 4. Vérifier les logs sur VM
ssh wanzoadmin@4.205.236.59 "docker logs -f kiota-accounting-service --tail 50"
```

---

### 📁 STRUCTURE DES BACKUPS SUR VM

```
/data/app/
├── Wanzo_Backend/              # Code actif
├── Wanzo_Backend_backup/       # Backup (ancien)
├── Wanzo_Backend_backup_/      # Backup avec .git (décembre 2025)
├── Wanzo_Backend_old/          # Ancienne version
├── deploy-services.tar         # Dernière archive de déploiement
└── *.zip                       # Archives de déploiement précédentes
```

---

### ⚡ TEMPS DE DÉPLOIEMENT TYPIQUES

| Étape | Temps |
|-------|-------|
| Création archive tar | 5-10 sec |
| SCP vers VM (~75MB) | 2-3 min |
| Extraction tar | 5 sec |
| Docker build (3 services) | 3-5 min |
| Docker up + health check | 30-60 sec |
| **TOTAL** | **~8-10 min** |

---

## 🛡️ BACKUP & DISASTER RECOVERY (Janvier 2026)

### Architecture de Sauvegarde

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         STRATÉGIE DE BACKUP WANZO                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                          VM AZURE (4.205.236.59)                          │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    POSTGRESQL (kiota-postgres)                     │  │  │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │  │  │
│  │  │  │admin_service │ │accounting_   │ │analytics_    │               │  │  │
│  │  │  │              │ │service       │ │service       │               │  │  │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘               │  │  │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │  │  │
│  │  │  │customer_     │ │gestion_      │ │portfolio_    │               │  │  │
│  │  │  │service       │ │commerciale   │ │institution   │               │  │  │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘               │  │  │
│  │  │  ┌──────────────┐ ┌──────────────┐                                │  │  │
│  │  │  │payment_      │ │adha_ai_      │                                │  │  │
│  │  │  │service       │ │service       │                                │  │  │
│  │  │  └──────────────┘ └──────────────┘                                │  │  │
│  │  └────────────────────────────┬───────────────────────────────────────┘  │  │
│  │                               │                                           │  │
│  │                       CRON: 3h00 UTC                                      │  │
│  │                               │                                           │  │
│  │                               ▼                                           │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                     SCRIPT: backup-postgres.sh                     │  │  │
│  │  │  1. pg_dump chaque base → .sql.gz                                  │  │  │
│  │  │  2. Stockage local /data/backups/postgres/ (7 jours)               │  │  │
│  │  │  3. Upload vers Azure Blob Storage (30 jours)                      │  │  │
│  │  └────────────────────────────┬───────────────────────────────────────┘  │  │
│  │                               │                                           │  │
│  └───────────────────────────────┼───────────────────────────────────────────┘  │
│                                  │                                              │
│  ┌───────────────────────────────┼───────────────────────────────────────────┐  │
│  │     STOCKAGE LOCAL            │         STOCKAGE CLOUD (OFF-SITE)         │  │
│  │  ┌────────────────────┐       │       ┌────────────────────────────────┐  │  │
│  │  │ /data/backups/     │       │       │   AZURE BLOB STORAGE            │  │  │
│  │  │   postgres/        │───────┼──────▶│   wanzobackupstorage            │  │  │
│  │  │                    │       │       │   Container: postgres-backups   │  │  │
│  │  │ Rétention: 7 jours │       │       │   Tier: Cool (économique)       │  │  │
│  │  │ ~500 KB/jour       │       │       │   Rétention: 30 jours           │  │  │
│  │  └────────────────────┘       │       │   Structure: YYYY/MM/DD/*.gz    │  │  │
│  │                               │       └────────────────────────────────┘  │  │
│  └───────────────────────────────┴───────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                           CODE SOURCE                                     │  │
│  │  ┌──────────────────┐                     ┌──────────────────────────┐   │  │
│  │  │   GITHUB REPO    │◀───── git pull ─────│  VM: /data/app/          │   │  │
│  │  │ jaqcquesndav/    │                     │     Wanzo_Backend        │   │  │
│  │  │ Wanzo_Backend    │                     │                          │   │  │
│  │  │ Branch: main     │                     │  Images Docker:          │   │  │
│  │  │                  │                     │  Reconstruites à la      │   │  │
│  │  │ (Backup infini)  │                     │  volée depuis le code    │   │  │
│  │  └──────────────────┘                     └──────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 📦 Configuration du Backup Azure Blob Storage

#### Ressources Azure créées

| Ressource | Valeur | Description |
|-----------|--------|-------------|
| **Storage Account** | `wanzobackupstorage` | Compte de stockage dédié aux backups |
| **Container** | `postgres-backups` | Conteneur pour les dumps PostgreSQL |
| **Région** | Canada Central | Même région que la VM |
| **Tier** | Cool | Optimisé coûts pour archivage (accès peu fréquent) |
| **Redondance** | LRS | Locally Redundant Storage (3 copies dans la région) |

#### Fichiers de configuration sur la VM

```
/etc/azure-backup-config.sh (permissions: 600, owner: root)
├── AZURE_STORAGE_ACCOUNT='wanzobackupstorage'
├── AZURE_STORAGE_KEY='<clé secrète>'
└── AZURE_CONTAINER_NAME='postgres-backups'

/data/backups/backup-postgres.sh (permissions: 755)
├── Script de backup automatisé
├── Exécuté par cron à 3h00 UTC
└── Logs: /data/logs/backup.log
```

#### Cron configuré

```bash
# Voir la configuration cron actuelle
crontab -l
# Résultat:
# 0 3 * * * /data/backups/backup-postgres.sh
```

---

### 📊 Détails du Script de Backup

```bash
#!/bin/bash
# /data/backups/backup-postgres.sh
# ============================================
# Script de backup PostgreSQL avec Azure Blob
# ============================================

# CONFIGURATION
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/data/backups/postgres"
LOG_FILE="/data/logs/backup.log"
RETENTION_DAYS=7          # Rétention locale
AZURE_RETENTION_DAYS=30   # Rétention Azure

# BASES DE DONNÉES SAUVEGARDÉES
DATABASES="
  admin_service
  accounting_service
  analytics_service
  portfolio_institution_service
  gestion_commerciale_service
  adha_ai_service
  customer_service
  payment_service
"

# PROCESSUS POUR CHAQUE BASE
for DB in $DATABASES; do
    # 1. Dump PostgreSQL compressé
    docker exec kiota-postgres pg_dump -U postgres $DB | gzip > "$BACKUP_DIR/${DB}_${DATE}.sql.gz"
    
    # 2. Upload vers Azure Blob Storage
    az storage blob upload \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --account-key "$AZURE_STORAGE_KEY" \
        --container-name "$AZURE_CONTAINER_NAME" \
        --name "$(date +%Y/%m/%d)/${DB}_${DATE}.sql.gz" \
        --file "$BACKUP_DIR/${DB}_${DATE}.sql.gz" \
        --tier Cool
done

# NETTOYAGE AUTOMATIQUE
# - Local: supprime fichiers > 7 jours
# - Azure: supprime blobs > 30 jours
```

---

### 📈 Structure des Backups dans Azure

```
wanzobackupstorage / postgres-backups /
│
├── 2026/
│   └── 01/
│       ├── 23/
│       │   ├── accounting_service_20260123_030001.sql.gz
│       │   ├── admin_service_20260123_030001.sql.gz
│       │   ├── adha_ai_service_20260123_030001.sql.gz
│       │   ├── analytics_service_20260123_030001.sql.gz
│       │   ├── customer_service_20260123_030001.sql.gz
│       │   ├── gestion_commerciale_service_20260123_030001.sql.gz
│       │   ├── payment_service_20260123_030001.sql.gz
│       │   └── portfolio_institution_service_20260123_030001.sql.gz
│       │
│       ├── 24/
│       │   └── ... (8 fichiers)
│       │
│       ├── ...
│       │
│       └── 30/
│           ├── accounting_service_20260130_030001.sql.gz    (56 KB)
│           ├── admin_service_20260130_030001.sql.gz         (16 KB)
│           ├── adha_ai_service_20260130_030001.sql.gz       (90 KB)
│           ├── analytics_service_20260130_030001.sql.gz     (4 KB)
│           ├── customer_service_20260130_030001.sql.gz      (44 KB)
│           ├── gestion_commerciale_service_20260130_030001.sql.gz (52 KB)
│           ├── payment_service_20260130_030001.sql.gz       (2 KB)
│           └── portfolio_institution_service_20260130_030001.sql.gz (20 KB)
│
└── ... (30 jours de rétention)
```

---

### 🔍 Vérifier l'État des Backups

#### Sur la VM (backups locaux)

```bash
# Connexion SSH
ssh wanzoadmin@4.205.236.59

# Voir les derniers backups
ls -lah /data/backups/postgres/ | tail -20

# Voir les logs du dernier backup
tail -50 /data/logs/backup.log

# Vérifier le cron
crontab -l

# Espace disque utilisé par les backups
du -sh /data/backups/postgres/
```

#### Sur Azure (backups cloud)

```powershell
# Depuis votre machine locale (avec Azure CLI)

# Lister tous les backups
az storage blob list \
  --account-name wanzobackupstorage \
  --container-name postgres-backups \
  --auth-mode key \
  --output table

# Lister backups d'une date spécifique
az storage blob list \
  --account-name wanzobackupstorage \
  --container-name postgres-backups \
  --prefix "2026/01/30/" \
  --auth-mode key \
  --output table

# Taille totale des backups
az storage blob list \
  --account-name wanzobackupstorage \
  --container-name postgres-backups \
  --auth-mode key \
  --query "[].properties.contentLength" \
  --output tsv | awk '{sum+=$1} END {print sum/1024/1024 " MB"}'
```

---

### 🚨 PROCÉDURE DE DISASTER RECOVERY

#### Scénario: La VM Azure crash complètement (perte totale)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      PROCESSUS DE DISASTER RECOVERY                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ÉTAPE 1: CRÉER NOUVELLE VM                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  az vm create --name wanzo-vm-new --image Ubuntu2204 --size Standard_D4s_v3│ │
│  │  + Configurer réseau, IP publique, disque /data                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ÉTAPE 2: INSTALLER DÉPENDANCES                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  - Docker + Docker Compose                                                 │ │
│  │  - Azure CLI                                                               │ │
│  │  - Git                                                                     │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ÉTAPE 3: RÉCUPÉRER LE CODE                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  git clone https://github.com/jaqcquesndav/Wanzo_Backend.git              │ │
│  │  cd Wanzo_Backend                                                          │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ÉTAPE 4: TÉLÉCHARGER BACKUPS DEPUIS AZURE                                      │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  az storage blob download-batch                                            │ │
│  │    --source postgres-backups                                               │ │
│  │    --destination /data/restore/                                            │ │
│  │    --pattern "2026/01/30/*"  # Dernier backup disponible                   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ÉTAPE 5: DÉMARRER POSTGRESQL                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  docker-compose up -d postgres                                             │ │
│  │  # Attendre que PostgreSQL soit prêt                                       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ÉTAPE 6: RESTAURER CHAQUE BASE DE DONNÉES                                      │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  for db in admin_service accounting_service ...; do                        │ │
│  │    gunzip -c /data/restore/${db}_*.sql.gz | \                              │ │
│  │      docker exec -i kiota-postgres psql -U postgres -d $db                 │ │
│  │  done                                                                      │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ÉTAPE 7: DÉMARRER TOUS LES SERVICES                                            │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  docker-compose up -d                                                      │ │
│  │  # Vérifier la santé: docker ps --format 'table {{.Names}}\t{{.Status}}'   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                      │
│                                          ▼                                      │
│  ✅ SYSTÈME RESTAURÉ !                                                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 📋 GUIDE DÉTAILLÉ: Restauration après crash VM

#### Étape 1: Créer une nouvelle VM Azure

```powershell
# Depuis votre machine locale avec Azure CLI

# Variables
$RESOURCE_GROUP="wanzo-backend-prod"
$VM_NAME="wanzo-vm-recovery"
$LOCATION="canadacentral"

# Créer la VM
az vm create `
  --resource-group $RESOURCE_GROUP `
  --name $VM_NAME `
  --image Ubuntu2204 `
  --size Standard_D4s_v3 `
  --admin-username wanzoadmin `
  --generate-ssh-keys `
  --public-ip-address-allocation Static `
  --os-disk-size-gb 128

# Attacher un disque de données pour /data
az vm disk attach `
  --resource-group $RESOURCE_GROUP `
  --vm-name $VM_NAME `
  --name wanzo-data-disk `
  --size-gb 512 `
  --sku Premium_LRS `
  --new

# Ouvrir les ports nécessaires
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 80 --priority 1001
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 443 --priority 1002
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 8000 --priority 1003

# Récupérer l'IP publique
$NEW_IP = az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv
Write-Host "Nouvelle IP: $NEW_IP"
```

#### Étape 2: Configurer la nouvelle VM

```bash
# Connexion SSH (depuis PowerShell ou terminal)
ssh wanzoadmin@<NOUVELLE_IP>

# Mettre à jour le système
sudo apt-get update && sudo apt-get upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Installer Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Monter le disque de données
sudo mkfs.ext4 /dev/sdc
sudo mkdir -p /data
sudo mount /dev/sdc /data
echo "UUID=$(sudo blkid -s UUID -o value /dev/sdc) /data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab

# Créer structure de répertoires
sudo mkdir -p /data/app /data/backups /data/logs /data/restore
sudo chown -R wanzoadmin:wanzoadmin /data

# Déconnexion et reconnexion pour appliquer groupe docker
exit
```

#### Étape 3: Récupérer le code source

```bash
# Reconnexion SSH
ssh wanzoadmin@<NOUVELLE_IP>

# Cloner le repository
cd /data/app
git clone https://github.com/jaqcquesndav/Wanzo_Backend.git
cd Wanzo_Backend

# Copier le fichier .env depuis un backup ou recréer
cat > .env << 'EOF'
# Variables d'environnement (à adapter)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<votre_mot_de_passe>
POSTGRES_HOST=kiota-postgres
AUTH0_DOMAIN=<votre_domaine_auth0>
AUTH0_CLIENT_ID=<votre_client_id>
AUTH0_CLIENT_SECRET=<votre_client_secret>
OPENAI_API_KEY=<votre_clé_openai>
ENCRYPTION_SECRET_KEY=<votre_clé_encryption>
# ... autres variables
EOF
```

#### Étape 4: Télécharger les backups depuis Azure

```bash
# Se connecter à Azure (interactif)
az login

# OU utiliser la clé de stockage directement
export AZURE_STORAGE_ACCOUNT="wanzobackupstorage"
export AZURE_STORAGE_KEY="<votre_clé_de_stockage>"

# Créer répertoire de restauration
mkdir -p /data/restore

# Lister les backups disponibles (trouver la date la plus récente)
az storage blob list \
  --account-name $AZURE_STORAGE_ACCOUNT \
  --account-key $AZURE_STORAGE_KEY \
  --container-name postgres-backups \
  --output table | tail -20

# Télécharger les backups de la date souhaitée (ex: 30 janvier 2026)
az storage blob download-batch \
  --account-name $AZURE_STORAGE_ACCOUNT \
  --account-key $AZURE_STORAGE_KEY \
  --source postgres-backups \
  --destination /data/restore/ \
  --pattern "2026/01/30/*"

# Vérifier les fichiers téléchargés
ls -la /data/restore/2026/01/30/
```

#### Étape 5: Démarrer PostgreSQL et restaurer les données

```bash
cd /data/app/Wanzo_Backend

# Démarrer uniquement PostgreSQL d'abord
docker-compose up -d postgres

# Attendre que PostgreSQL soit prêt (30 secondes)
sleep 30

# Vérifier que PostgreSQL répond
docker exec kiota-postgres pg_isready -U postgres

# Créer les bases de données (si elles n'existent pas)
DATABASES="admin_service accounting_service analytics_service portfolio_institution_service gestion_commerciale_service adha_ai_service customer_service payment_service"

for db in $DATABASES; do
    echo "Creating database: $db"
    docker exec kiota-postgres psql -U postgres -c "CREATE DATABASE $db;" 2>/dev/null || echo "Database $db already exists"
done

# Restaurer chaque base de données depuis les backups
BACKUP_DATE="2026/01/30"  # Adapter selon la date du backup

for db in $DATABASES; do
    echo "🔄 Restoring $db..."
    BACKUP_FILE=$(ls /data/restore/$BACKUP_DATE/${db}_*.sql.gz 2>/dev/null | head -1)
    
    if [ -f "$BACKUP_FILE" ]; then
        gunzip -c "$BACKUP_FILE" | docker exec -i kiota-postgres psql -U postgres -d $db
        echo "✅ $db restored successfully"
    else
        echo "⚠️  No backup found for $db"
    fi
done

echo "🎉 Database restoration complete!"
```

#### Étape 6: Démarrer tous les services

```bash
# Démarrer tous les services
docker-compose up -d

# Attendre le démarrage (60 secondes)
sleep 60

# Vérifier l'état de tous les containers
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Vérifier les logs en cas de problème
docker-compose logs --tail 50 kiota-api-gateway
docker-compose logs --tail 50 kiota-accounting-service
```

#### Étape 7: Reconfigurer le backup automatique

```bash
# Recréer le fichier de config Azure
sudo cat > /etc/azure-backup-config.sh << 'EOF'
#!/bin/bash
export AZURE_STORAGE_ACCOUNT='wanzobackupstorage'
export AZURE_STORAGE_KEY='<votre_clé_de_stockage>'
export AZURE_CONTAINER_NAME='postgres-backups'
EOF

sudo chmod 600 /etc/azure-backup-config.sh
sudo chown root:root /etc/azure-backup-config.sh

# Le script de backup est déjà dans le repo Git
chmod +x /data/app/Wanzo_Backend/scripts/backup-postgres-azure.sh
cp /data/app/Wanzo_Backend/scripts/backup-postgres-azure.sh /data/backups/backup-postgres.sh

# Reconfigurer le cron
(crontab -l 2>/dev/null; echo "0 3 * * * /data/backups/backup-postgres.sh") | crontab -

# Vérifier le cron
crontab -l
```

#### Étape 8: Mettre à jour le DNS (si applicable)

```powershell
# Si vous utilisez un nom de domaine, mettez à jour l'enregistrement DNS
# vers la nouvelle IP publique de la VM

# Exemple avec Azure DNS
az network dns record-set a update `
  --resource-group wanzo-dns-rg `
  --zone-name wanzo.com `
  --name api `
  --set "aRecords[0].ipv4Address=<NOUVELLE_IP>"
```

---

### ⏱️ Temps de Récupération Estimés

| Étape | Temps estimé | Notes |
|-------|--------------|-------|
| Création VM Azure | 5-10 min | Dépend de la région |
| Installation Docker/Azure CLI | 5-10 min | Automatisable |
| Clone du repo Git | 2-3 min | ~75 MB |
| Téléchargement backups Azure | 5-10 min | ~300 KB total |
| Restauration PostgreSQL | 2-5 min | 8 bases de données |
| Démarrage services Docker | 3-5 min | Build des images |
| Tests de vérification | 5-10 min | Health checks |
| **TOTAL RTO** | **~30-60 min** | Recovery Time Objective |

---

### 📊 Métriques de Backup

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **RPO** | 24 heures max | Recovery Point Objective (perte de données max) |
| **RTO** | ~1 heure | Recovery Time Objective (temps de restauration) |
| **Fréquence** | Quotidienne à 3h00 UTC | Via cron |
| **Rétention locale** | 7 jours | Sur disque VM /data |
| **Rétention Azure** | 30 jours | Sur Blob Storage |
| **Taille backup/jour** | ~300 KB | Compressé gzip |
| **Coût stockage Azure** | ~$0.01/mois | Tier Cool, très économique |

---

### 🔐 Sécurité des Backups

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SÉCURITÉ DES BACKUPS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ACCÈS AU STORAGE ACCOUNT                                                │
│     ┌─────────────────────────────────────────────────────────────────────┐│
│     │ • Clé d'accès stockée dans /etc/azure-backup-config.sh             ││
│     │ • Permissions: 600 (lecture seule par root)                        ││
│     │ • Pas d'accès public au container                                  ││
│     │ • Accès uniquement via clé ou Azure AD                             ││
│     └─────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  2. CHIFFREMENT                                                             │
│     ┌─────────────────────────────────────────────────────────────────────┐│
│     │ • Azure Storage: chiffrement au repos (AES-256) par défaut         ││
│     │ • Transport: HTTPS obligatoire                                     ││
│     │ • Données PostgreSQL: chiffrées via colonnes sensibles (app-level) ││
│     └─────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  3. REDONDANCE                                                              │
│     ┌─────────────────────────────────────────────────────────────────────┐│
│     │ • LRS (Locally Redundant Storage): 3 copies dans la région         ││
│     │ • Option: Upgrade vers GRS pour copie géo-redondante               ││
│     └─────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  4. ROTATION DES CLÉS (Recommandé)                                          │
│     ┌─────────────────────────────────────────────────────────────────────┐│
│     │ # Régénérer les clés périodiquement                                ││
│     │ az storage account keys renew --account-name wanzobackupstorage    ││
│     │ # Puis mettre à jour /etc/azure-backup-config.sh sur la VM         ││
│     └─────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🧪 Test de Restauration (Recommandé mensuellement)

```bash
# Script de test de restauration (à exécuter sur VM de test)
#!/bin/bash

echo "🧪 TEST DE RESTAURATION - $(date)"

# 1. Télécharger le dernier backup
LATEST_DATE=$(az storage blob list \
  --account-name wanzobackupstorage \
  --account-key "$AZURE_STORAGE_KEY" \
  --container-name postgres-backups \
  --query "[].name" -o tsv | grep -oP '^\d{4}/\d{2}/\d{2}' | sort -u | tail -1)

echo "📅 Dernier backup: $LATEST_DATE"

# 2. Télécharger un fichier de test
TEST_DB="accounting_service"
az storage blob download \
  --account-name wanzobackupstorage \
  --account-key "$AZURE_STORAGE_KEY" \
  --container-name postgres-backups \
  --name "$LATEST_DATE/${TEST_DB}_*.sql.gz" \
  --file /tmp/test_restore.sql.gz

# 3. Créer base de données de test
docker exec kiota-postgres psql -U postgres -c "CREATE DATABASE test_restore;"

# 4. Restaurer
gunzip -c /tmp/test_restore.sql.gz | docker exec -i kiota-postgres psql -U postgres -d test_restore

# 5. Vérifier le contenu
TABLES=$(docker exec kiota-postgres psql -U postgres -d test_restore -c "\dt" | wc -l)
echo "✅ Tables restaurées: $TABLES"

# 6. Nettoyer
docker exec kiota-postgres psql -U postgres -c "DROP DATABASE test_restore;"
rm /tmp/test_restore.sql.gz

echo "🎉 Test de restauration réussi!"
```

---

### 📞 Contacts d'Urgence

| Situation | Action | Contact |
|-----------|--------|---------|
| VM inaccessible | Vérifier Azure Portal | Azure Support |
| Backup échoué | Vérifier logs `/data/logs/backup.log` | DevOps team |
| Données corrompues | Restaurer depuis Azure Blob | DBA |
| Clé Azure expirée | Régénérer via Azure Portal | Admin Azure |

---

### ✅ Checklist Backup Quotidienne (Automatique)

- [x] Cron exécuté à 3h00 UTC
- [x] 8 bases de données sauvegardées
- [x] Fichiers uploadés vers Azure Blob Storage
- [x] Anciens backups locaux nettoyés (>7 jours)
- [x] Anciens backups Azure nettoyés (>30 jours)
- [x] Logs écrits dans `/data/logs/backup.log`

### ✅ Checklist Disaster Recovery (Manuelle)

- [ ] Créer nouvelle VM Azure
- [ ] Installer Docker, Docker Compose, Azure CLI
- [ ] Cloner repo GitHub
- [ ] Configurer fichier .env
- [ ] Télécharger backups depuis Azure Blob
- [ ] Démarrer PostgreSQL
- [ ] Restaurer les 8 bases de données
- [ ] Démarrer tous les services
- [ ] Vérifier health checks
- [ ] Reconfigurer cron backup
- [ ] Mettre à jour DNS si nécessaire
- [ ] Tester l'application end-to-end

---

**🎉 Votre backend Wanzo sera prêt pour la production avec CI/CD complet !**
