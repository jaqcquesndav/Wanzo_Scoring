# 📊 ANALYSE TECHNIQUE & ÉCONOMIQUE - DÉPLOIEMENT AZURE VM
**Projet**: Wanzo Backend Microservices  
**Cible**: 3,000 - 10,000 Clients (PME/Institutions)  
**Date**: Décembre 2025  
**Région**: Canada Central

---

## 🎯 1. ARCHITECTURE BACKEND ACTUELLE

### 1.1 Stack Technique (Analyse du code source)

#### **Microservices Node.js/NestJS** (8 services)
```yaml
api-gateway:       Port 8000  | Point d'entrée unique, routage
admin-service:     Port 3001  | Gestion utilisateurs, Auth0, permissions
accounting-service: Port 3003 | Comptabilité, scoring crédit (XGBoost ML)
analytics-service:  Port 3002 | Analytics, métriques business
portfolio-institution: Port 3005 | Gestion portefeuilles institutionnels
gestion-commerciale: Port 3006 | CRM, prospection mobile
customer-service:   Port 3011 | Gestion clients, Stripe, OpenAI
payment-service:    Port 3007 | Paiements SerdiPay (RDC)
```

#### **Service Python/Django** (1 service IA)
```yaml
adha-ai-service:   Port 8002  | 
  - Django REST + Celery (tâches async)
  - OpenAI GPT-4o (chat, vision, embeddings)
  - ChromaDB (vector database)
  - Document processing (PDF, DOCX, images, OCR)
  - Kafka consumers
  - Pas de PyTorch (optimisé avec OpenAI API)
```

#### **Infrastructure**
```yaml
PostgreSQL 14:     Port 5432  | 8 bases données séparées
Kafka + Zookeeper: Ports 9092/29092, 2181 | Event streaming
Prometheus:        Port 9090  | Métriques
Grafana:           Port 4000  | Dashboards
```

### 1.2 Architecture Docker (Multi-stage optimisée)
- **Images de base partagées** : `wanzo-deps-base` + `wanzo-production-base`
- **Gain**: -75% temps build, -60% taille images (2.4GB vs 6GB)
- **Volumes persistants**: PostgreSQL, Kafka, logs séparés par service

---

## 💾 2. DIMENSIONNEMENT STOCKAGE

### 2.1 Estimation par charge (3K - 10K clients)

| Composant | 3K clients | 10K clients | Notes |
|-----------|-----------|-------------|-------|
| **PostgreSQL** | 50-80 GB | 150-250 GB | 8 DBs, croissance linéaire |
| **Kafka logs** | 20-30 GB | 50-80 GB | Rétention 7 jours |
| **Logs applicatifs** | 10-20 GB | 30-50 GB | Rotation quotidienne |
| **Adha-AI data** | 15-25 GB | 40-70 GB | Documents, embeddings |
| **Docker images** | 2.5 GB | 2.5 GB | Fixe (images optimisées) |
| **OS + système** | 15 GB | 15 GB | Ubuntu 22.04 LTS |
| **Buffer (20%)** | 25 GB | 135 GB | Croissance imprévue |
| **TOTAL** | **≈160 GB** | **≈630 GB** | |

**Recommandation stockage**:
- **3K clients**: 256 GB Premium SSD (P15)
- **10K clients**: 1 TB Premium SSD (P30)

### 2.2 Configuration disques optimale

```yaml
Disque 1 - OS:
  Type: Premium SSD (P10)
  Taille: 128 GB
  Mount: /
  Usage: Système, Docker engine, images

Disque 2 - Données:
  Type: Premium SSD (P20/P30)
  Taille: 512 GB ou 1 TB
  Mount: /data
  Sous-volumes:
    /data/postgres: PostgreSQL databases
    /data/kafka: Logs Kafka
    /data/docker-volumes: Volumes Docker
    /data/logs: Logs applicatifs
    /data/backups: Backups locaux temporaires
```

---

## 🖥️ 3. DIMENSIONNEMENT COMPUTE (VM)

### 3.1 Estimation charge CPU/RAM

#### **Par service (production)**:
```
API Gateway:       0.5-1 vCPU, 1-2 GB RAM    | Routage, load faible
Admin Service:     0.5-1 vCPU, 1-1.5 GB RAM  | CRUD, auth
Accounting:        1-1.5 vCPU, 1.5-2 GB RAM  | ML scoring, calculs
Analytics:         0.75-1 vCPU, 1-1.5 GB RAM | Aggregations
Portfolio:         0.5-1 vCPU, 1-1.5 GB RAM  | CRUD
Commerce:          0.5-1 vCPU, 1-1.5 GB RAM  | CRM mobile
Customer:          0.75-1 vCPU, 1.5-2 GB RAM | OpenAI calls
Payment:           0.5-0.75 vCPU, 1 GB RAM   | API externe
Adha-AI:           1.5-2 vCPU, 3-4 GB RAM    | Python, Celery, OpenAI

PostgreSQL:        2-3 vCPU, 4-6 GB RAM      | 8 DBs, connexions
Kafka+Zookeeper:   1.5-2 vCPU, 2-3 GB RAM    | Event streaming
Monitoring:        0.5 vCPU, 1 GB RAM        | Prometheus+Grafana

TOTAL Minimum:     11-14 vCPUs, 20-28 GB RAM
Overhead Docker:   +20% → 14-17 vCPUs, 24-34 GB RAM
```

### 3.2 Options VM recommandées

#### **Option 1: Production 3K-5K clients** ✅ **RECOMMANDÉ**
```yaml
VM: Standard_D8ads_v5
Specs:
  - 8 vCPUs AMD EPYC (3.4 GHz)
  - 32 GB RAM
  - 300 GB SSD local temporaire (cache Docker)
  - Premium SSD support
  - Réseau accéléré (25 Gbps)

Coût: ~$360-400 CAD/mois
Performance: 
  - 8 vCPUs → peut gérer pics 150-200 req/s
  - 32GB RAM → confortable avec buffer 25%
  - Disque local → build Docker rapide
```

#### **Option 2: Production 7K-10K clients** 💪
```yaml
VM: Standard_E8ads_v5
Specs:
  - 8 vCPUs AMD EPYC
  - 64 GB RAM (ratio 8:1)
  - 300 GB SSD local
  - Premium SSD support
  - Réseau accéléré

Coût: ~$480-550 CAD/mois
Avantage: RAM doublée pour PostgreSQL cache, Redis futur
```

#### **Option 3: Démarrage/MVP** 💰
```yaml
VM: Standard_D4ads_v5
Specs:
  - 4 vCPUs AMD
  - 16 GB RAM
  - 150 GB SSD local
  - Premium SSD support

Coût: ~$180-220 CAD/mois
Limite: Max 2K-3K clients, risque saturation
```

---

## 🔧 4. CONFIGURATION VM AZURE

### 4.1 Création VM (Commande Azure CLI)

```bash
# Variables
RESOURCE_GROUP="wanzo-backend-prod"
VM_NAME="wanzo-backend-vm"
LOCATION="canadacentral"
VM_SIZE="Standard_D8ads_v5"
OS_IMAGE="Ubuntu2204"
ADMIN_USER="wanzoadmin"

# Créer groupe de ressources
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Créer VM
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image $OS_IMAGE \
  --size $VM_SIZE \
  --admin-username $ADMIN_USER \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --public-ip-address-allocation static \
  --accelerated-networking true \
  --os-disk-size-gb 128 \
  --os-disk-caching ReadWrite \
  --storage-sku Premium_LRS \
  --nsg-rule SSH \
  --priority Regular

# Ajouter disque de données
az vm disk attach \
  --resource-group $RESOURCE_GROUP \
  --vm-name $VM_NAME \
  --name "${VM_NAME}-data" \
  --new \
  --size-gb 512 \
  --sku Premium_LRS \
  --caching ReadWrite
```

### 4.2 Ouvrir ports requis

```bash
# NSG Rules
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "${VM_NAME}NSG" \
  --name Allow-HTTPS \
  --priority 1001 \
  --destination-port-ranges 443 \
  --protocol Tcp \
  --access Allow

az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "${VM_NAME}NSG" \
  --name Allow-HTTP \
  --priority 1002 \
  --destination-port-ranges 80 \
  --protocol Tcp \
  --access Allow

# API Gateway (temporaire, ensuite via reverse proxy)
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "${VM_NAME}NSG" \
  --name Allow-API-Gateway \
  --priority 1003 \
  --destination-port-ranges 8000 \
  --protocol Tcp \
  --access Allow
```

### 4.3 Configuration post-déploiement

```bash
# SSH vers VM
ssh $ADMIN_USER@<VM_PUBLIC_IP>

# Monter disque de données
sudo mkfs.ext4 /dev/sdc
sudo mkdir /data
echo "/dev/sdc /data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mount -a

# Créer structure
sudo mkdir -p /data/{postgres,kafka,docker-volumes,logs,backups}
sudo chown -R $USER:$USER /data

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configurer Docker pour utiliser /data
sudo systemctl stop docker
sudo nano /etc/docker/daemon.json
```

```json
{
  "data-root": "/data/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "metrics-addr": "0.0.0.0:9323"
}
```

```bash
sudo systemctl start docker

# Optimisations système
sudo sysctl -w vm.max_map_count=262144
sudo sysctl -w fs.file-max=65536
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
echo "fs.file-max=65536" | sudo tee -a /etc/sysctl.conf
```

---

## 📦 5. BACKUP - STRATÉGIE COMPLÈTE

### 5.1 Backup Azure natif (Snapshots disques)

#### **Configuration**:
```bash
# Créer Recovery Services Vault
az backup vault create \
  --resource-group $RESOURCE_GROUP \
  --name wanzo-backup-vault \
  --location $LOCATION

# Activer backup pour VM
az backup protection enable-for-vm \
  --resource-group $RESOURCE_GROUP \
  --vault-name wanzo-backup-vault \
  --vm $VM_NAME \
  --policy-name DefaultPolicy
```

#### **Politique DefaultPolicy**:
- **Fréquence**: Quotidien 2h du matin (UTC)
- **Rétention**: 
  - Quotidien: 30 jours
  - Hebdomadaire: 12 semaines (Dimanche)
  - Mensuel: 12 mois (1er du mois)
  - Annuel: 5 ans (1er Janvier)
- **Coût**: ~$0.10/GB/mois stockage backup
  - 512GB → ~$51/mois
  - 1TB → ~$102/mois

### 5.2 Backup PostgreSQL (local + Azure Blob)

#### **Script backup automatique**:
```bash
#!/bin/bash
# /data/backups/backup-postgres.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/data/backups/postgres"
RETENTION_DAYS=7

# Créer backup de chaque DB
DATABASES="admin_service accounting_service analytics_service portfolio_institution_service gestion_commerciale_service adha_ai_service customer_service payment_service"

for DB in $DATABASES; do
  docker exec kiota-postgres pg_dump -U postgres $DB | gzip > "$BACKUP_DIR/${DB}_${DATE}.sql.gz"
done

# Nettoyer backups > 7 jours
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Upload vers Azure Blob (optionnel)
az storage blob upload-batch \
  --account-name wanzobackupstorage \
  --destination postgres-backups \
  --source $BACKUP_DIR \
  --pattern "*${DATE}*"

echo "Backup completed: $DATE"
```

#### **Configuration cron**:
```bash
# Backup quotidien 3h du matin
0 3 * * * /data/backups/backup-postgres.sh >> /data/logs/backup.log 2>&1
```

#### **Coût Azure Blob Storage (Cool tier)**:
- **Stockage**: $0.01/GB/mois
- **Exemple** (30 jours x 10GB/jour = 300GB): ~$3/mois
- **Transactions**: Négligeables pour backup quotidien

### 5.3 Backup configuration & code

```bash
#!/bin/bash
# Backup docker-compose, .env, configs
tar -czf /data/backups/config_$(date +%Y%m%d).tar.gz \
  /home/$USER/Wanzo_Backend/docker-compose.yml \
  /home/$USER/Wanzo_Backend/.env \
  /home/$USER/Wanzo_Backend/apps/*/.env \
  /etc/docker/daemon.json

# Upload vers Azure
az storage blob upload \
  --account-name wanzobackupstorage \
  --container-name config-backups \
  --file /data/backups/config_$(date +%Y%m%d).tar.gz
```

### 5.4 Stratégie de récupération (RTO/RPO)

| Type panne | RTO | RPO | Procédure |
|------------|-----|-----|-----------|
| **Container crash** | 2 min | 0 | `docker-compose restart` |
| **VM crash** | 15 min | 0 | Azure auto-restart + health checks |
| **Corruption disque** | 2h | 24h | Restore depuis snapshot Azure |
| **Perte totale région** | 4-6h | 24h | Redéployer VM + restore backups Blob |
| **Corruption DB** | 1h | 3h | Restore backup PostgreSQL local |

---

## 💰 6. ANALYSE ÉCONOMIQUE DÉTAILLÉE

### 6.1 Coûts mensuels (Production Standard_D8ads_v5)

| Composant | 3K clients | 10K clients | Notes |
|-----------|-----------|-------------|-------|
| **VM Compute** | $360 | $360 | Fixe (720h/mois) |
| **Disque OS (128GB P10)** | $25 | $25 | Premium SSD |
| **Disque Data (512GB P20)** | $97 | - | Pour 3K-5K clients |
| **Disque Data (1TB P30)** | - | $193 | Pour 7K-10K clients |
| **IP publique statique** | $4 | $4 | IPv4 |
| **Bande passante sortante** | $15-25 | $40-60 | 150GB - 500GB/mois |
| **Azure Backup** | $51 | $102 | Snapshots disques |
| **Blob Storage (backups)** | $3 | $8 | PostgreSQL + configs |
| **Azure Key Vault** | $2 | $2 | Secrets management |
| **TOTAL/mois** | **~$557-567** | **~$734-754** | |
| **TOTAL/an** | **~$6,684** | **~$8,808** | |

### 6.2 Services externes (hors Azure)

```yaml
Auth0:              $23-240/mois   | 7,000 MAU gratuits, puis $0.05/MAU
OpenAI API:         $100-500/mois  | GPT-4o, embeddings (dépend usage)
SerdiPay:           % transactions  | Frais paiement mobile RDC
Cloudinary:         $0-89/mois     | Upload images mobile
Monitoring (opt):   $0-100/mois    | Sentry, Datadog si besoin

Estimation: +$150-900/mois selon trafic IA
```

### 6.3 Économies potentielles

#### **Reserved Instances (1-3 ans)**:
```
Économie 1 an:  -20 à -30%  → $252-288/mois compute au lieu de $360
Économie 3 ans: -40 à -60%  → $144-216/mois compute
```

**ROI si engagement 3 ans**:
- Économie annuelle: ~$1,728 - $2,592
- Économie sur 3 ans: ~$5,184 - $7,776

#### **Spot VM** (NON recommandé production):
- Économie: -90%
- Risque: Interruption avec préavis 30s
- **Usage**: Dev/Test uniquement

### 6.4 Scalabilité verticale vs horizontale

#### **Scalabilité verticale** (augmenter VM):
```
Phase 1 (0-3K):   D4ads_v5  → $220/mois
Phase 2 (3-7K):   D8ads_v5  → $400/mois  ✅ Recommandé démarrage
Phase 3 (7-15K):  E8ads_v5  → $550/mois
Phase 4 (15K+):   E16ads_v5 → $1,100/mois
```

#### **Scalabilité horizontale** (multi-VM + Load Balancer):
```
2x D8ads_v5:      $720/mois compute
Load Balancer:    $23/mois
Total:            $743/mois
Avantage:         Haute disponibilité, 0 downtime updates
Complexité:       Orchestration, sync sessions, coût x2
```

**Recommandation**: Vertical scaling jusqu'à 15K clients, puis horizontal.

---

## 🚀 7. PLAN DE DÉPLOIEMENT

### Phase 1: Setup infrastructure (Jour 1-2)
```bash
1. Créer VM Azure (Standard_D8ads_v5)
2. Configurer disques (OS 128GB + Data 512GB)
3. Installer Docker + Docker Compose
4. Configurer NSG (ports 22, 80, 443, 8000)
5. Monter disque /data et créer structure
```

### Phase 2: Déploiement application (Jour 2-3)
```bash
6. Clone repo Wanzo_Backend
7. Configurer variables d'environnement (.env)
8. Pull/Build images Docker
9. Démarrer stack: docker-compose --profile prod up -d
10. Vérifier health checks tous services
```

### Phase 3: Configuration backup (Jour 3)
```bash
11. Activer Azure Backup (VM snapshots)
12. Configurer backup PostgreSQL automatique
13. Setup Azure Blob Storage pour backups
14. Créer cron jobs backup quotidien
15. Tester restoration depuis backup
```

### Phase 4: Monitoring & sécurité (Jour 4)
```bash
16. Configurer Azure Key Vault (secrets)
17. Activer Managed Identity VM
18. Setup reverse proxy Nginx/Caddy pour SSL
19. Configurer Let's Encrypt (SSL gratuit)
20. Valider alertes Prometheus/Grafana
```

### Phase 5: Tests & validation (Jour 5)
```bash
21. Load testing (JMeter/k6) - simuler 3K users
22. Stress test PostgreSQL connexions
23. Valider backup/restore complet
24. Tests failover (kill containers)
25. Documentation runbook opérations
```

---

## 📋 8. COMMANDES AZURE CLI ESSENTIELLES

### Gestion VM
```bash
# Démarrer VM
az vm start --resource-group wanzo-backend-prod --name wanzo-backend-vm

# Arrêter VM (économise compute, pas stockage)
az vm stop --resource-group wanzo-backend-prod --name wanzo-backend-vm

# Deallocate VM (libère compute complètement)
az vm deallocate --resource-group wanzo-backend-prod --name wanzo-backend-vm

# Redémarrer VM
az vm restart --resource-group wanzo-backend-prod --name wanzo-backend-vm

# Voir statut
az vm get-instance-view --resource-group wanzo-backend-prod --name wanzo-backend-vm --query instanceView.statuses[1]

# Resize VM (scale up)
az vm resize --resource-group wanzo-backend-prod --name wanzo-backend-vm --size Standard_E8ads_v5
```

### Gestion disques
```bash
# Lister disques attachés
az vm show --resource-group wanzo-backend-prod --name wanzo-backend-vm --query storageProfile.dataDisks

# Augmenter taille disque (ATTENTION: pas de réduction possible)
az disk update --resource-group wanzo-backend-prod --name wanzo-backend-vm-data --size-gb 1024

# Créer snapshot manuel
az snapshot create --resource-group wanzo-backend-prod --name snapshot-$(date +%Y%m%d) --source wanzo-backend-vm-data
```

### Monitoring
```bash
# Métriques CPU/RAM
az vm monitor metrics list --resource wanzo-backend-vm --resource-group wanzo-backend-prod --metric "Percentage CPU"

# Logs diagnostics
az vm boot-diagnostics get-boot-log --resource-group wanzo-backend-prod --name wanzo-backend-vm
```

---

## ✅ 9. CHECKLIST PRODUCTION

### Avant go-live
- [ ] VM créée avec specs recommandées
- [ ] Disques configurés et montés (/data)
- [ ] Docker + Compose installés et testés
- [ ] Stack déployée (docker-compose --profile prod)
- [ ] PostgreSQL: 8 databases créées et migrées
- [ ] Kafka topics créés et testés
- [ ] Secrets migrés vers Azure Key Vault
- [ ] SSL/TLS configuré (Let's Encrypt)
- [ ] NSG configuré (ports minimaux ouverts)
- [ ] Backup automatique activé et testé
- [ ] Monitoring Prometheus + Grafana opérationnel
- [ ] Alertes configurées (email/SMS)
- [ ] Load testing validé (3K users simulés)
- [ ] Runbook opérations documenté
- [ ] DNS pointé vers IP publique VM

### Post go-live (suivi)
- [ ] Monitoring quotidien métriques
- [ ] Backup verification hebdomadaire
- [ ] Mise à jour sécurité système mensuelle
- [ ] Review coûts Azure mensuel
- [ ] Plan scale-up si croissance >80% capacité
- [ ] Tests disaster recovery trimestriel

---

## 🎯 RECOMMANDATION FINALE

**Pour démarrage production (0-5K clients)**:
```yaml
VM:              Standard_D8ads_v5 (8 vCPUs, 32GB RAM)
Disque OS:       128 GB Premium SSD
Disque Data:     512 GB Premium SSD
Backup:          Azure Backup + PostgreSQL local
Région:          Canada Central
Coût total:      ~$560/mois CAD (~$6,720/an)
Réserver 1 an:   ~$430/mois CAD (économie $130/mois)
```

**Cette configuration supporte**:
- 3,000-5,000 clients actifs
- 100-150 requêtes/seconde en pointe
- Croissance 50-100 clients/mois
- 99.5% uptime (estimation)

**Quand scaler**: CPU >75% sustained ou RAM >80%

