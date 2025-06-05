# Guide de Déploiement HEXACO-PI-R

## Table des Matières
1. [Prérequis](#prerequis)
2. [Configuration de l'Environnement](#environnement)
3. [Déploiement Backend](#backend)
4. [Déploiement Frontend](#frontend)
5. [Configuration Base de Données](#database)
6. [Variables d'Environnement](#variables)
7. [Monitoring et Logs](#monitoring)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)

## Prérequis {#prerequis}

### Système
- **OS** : Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **RAM** : Minimum 4GB, Recommandé 8GB+
- **Stockage** : Minimum 20GB d'espace libre
- **CPU** : 2 cores minimum, 4+ recommandé

### Logiciels Requis
- **Python** : 3.9+
- **Node.js** : 18.0+
- **PostgreSQL** : 13+
- **Redis** : 6.0+ (optionnel, pour le cache)
- **Nginx** : 1.18+ (pour la production)

### Outils de Développement
```bash
# Installation des outils essentiels
sudo apt update
sudo apt install -y git curl wget build-essential

# Installation de Python et pip
sudo apt install -y python3.9 python3.9-pip python3.9-venv

# Installation de Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Installation de PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Installation de Redis (optionnel)
sudo apt install -y redis-server
```

## Configuration de l'Environnement {#environnement}

### Structure des Répertoires
```
/opt/orientor/
├── backend/
│   ├── app/
│   ├── data_n_notebook/data/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env.local
├── logs/
├── backups/
└── scripts/
```

### Création de l'Utilisateur Système
```bash
# Créer un utilisateur dédié
sudo useradd -m -s /bin/bash orientor
sudo usermod -aG sudo orientor

# Créer les répertoires
sudo mkdir -p /opt/orientor/{backend,frontend,logs,backups,scripts}
sudo chown -R orientor:orientor /opt/orientor
```

### Configuration des Permissions
```bash
# Permissions pour les logs
sudo mkdir -p /var/log/orientor
sudo chown orientor:orientor /var/log/orientor
sudo chmod 755 /var/log/orientor

# Permissions pour les données
sudo chown -R orientor:orientor /opt/orientor/backend/data_n_notebook
sudo chmod -R 644 /opt/orientor/backend/data_n_notebook/data/*.csv
```

## Déploiement Backend {#backend}

### Installation des Dépendances Python
```bash
cd /opt/orientor/backend

# Créer un environnement virtuel
python3.9 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Installer des dépendances supplémentaires pour la production
pip install gunicorn uvicorn[standard] psycopg2-binary redis
```

### Configuration de l'Application
```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer les variables d'environnement
nano .env
```

### Fichier de Configuration Backend (.env)
```bash
# Base de données
DATABASE_URL=postgresql://orientor_user:secure_password@localhost:5432/orientor_db

# Configuration HEXACO
HEXACO_DATA_PATH=/opt/orientor/backend/data_n_notebook/data
HEXACO_CONFIG_PATH=/opt/orientor/backend/app/config/hexaco_facet_mapping.json

# Cache Redis (optionnel)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/orientor/backend.log

# Sécurité
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

### Service Systemd pour le Backend
```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/orientor-backend.service
```

```ini
[Unit]
Description=Orientor Backend API
After=network.target postgresql.service

[Service]
Type=exec
User=orientor
Group=orientor
WorkingDirectory=/opt/orientor/backend
Environment=PATH=/opt/orientor/backend/venv/bin
ExecStart=/opt/orientor/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=orientor-backend

# Sécurité
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/orientor /var/log/orientor

[Install]
WantedBy=multi-user.target
```

### Démarrage du Service Backend
```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer et démarrer le service
sudo systemctl enable orientor-backend
sudo systemctl start orientor-backend

# Vérifier le statut
sudo systemctl status orientor-backend

# Voir les logs
sudo journalctl -u orientor-backend -f
```

## Déploiement Frontend {#frontend}

### Installation des Dépendances Node.js
```bash
cd /opt/orientor/frontend

# Installer les dépendances
npm ci --production

# Build pour la production
npm run build
```

### Configuration Frontend (.env.local)
```bash
# API Backend
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_API_TIMEOUT=30000

# Configuration HEXACO
NEXT_PUBLIC_HEXACO_VERSIONS=hexaco_60_fr,hexaco_100_fr,hexaco_60_en,hexaco_100_en

# Analytics (optionnel)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Environnement
NODE_ENV=production
```

### Service Systemd pour le Frontend
```bash
sudo nano /etc/systemd/system/orientor-frontend.service
```

```ini
[Unit]
Description=Orientor Frontend
After=network.target

[Service]
Type=exec
User=orientor
Group=orientor
WorkingDirectory=/opt/orientor/frontend
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=orientor-frontend

[Install]
WantedBy=multi-user.target
```

### Configuration Nginx
```bash
sudo nano /etc/nginx/sites-available/orientor
```

```nginx
# Configuration Nginx pour Orientor
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirection HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # Certificats SSL
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Configuration SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Headers de sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS Headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type";
        
        # Timeouts pour les tests longs
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # Fichiers statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Logs
    access_log /var/log/nginx/orientor_access.log;
    error_log /var/log/nginx/orientor_error.log;
}
```

### Activation de la Configuration Nginx
```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/orientor /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

## Configuration Base de Données {#database}

### Création de la Base de Données
```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

-- Créer l'utilisateur et la base de données
CREATE USER orientor_user WITH PASSWORD 'secure_password';
CREATE DATABASE orientor_db OWNER orientor_user;
GRANT ALL PRIVILEGES ON DATABASE orientor_db TO orientor_user;

-- Quitter psql
\q
```

### Schéma de Base de Données
```sql
-- Se connecter à la base de données
psql -U orientor_user -d orientor_db -h localhost

-- Créer les tables HEXACO
CREATE TABLE personality_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    assessment_type VARCHAR(50) NOT NULL DEFAULT 'hexaco',
    assessment_version VARCHAR(50) NOT NULL,
    session_id UUID UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'in_progress',
    total_items INTEGER NOT NULL,
    completed_items INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE personality_responses (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES personality_assessments(id) ON DELETE CASCADE,
    item_id VARCHAR(10) NOT NULL,
    item_type VARCHAR(20) DEFAULT 'likert',
    response_value JSONB NOT NULL,
    response_time_ms INTEGER,
    revision_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE personality_scores (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES personality_assessments(id) ON DELETE CASCADE,
    domain VARCHAR(50) NOT NULL,
    facet VARCHAR(50),
    raw_score DECIMAL(5,2),
    percentile_score INTEGER,
    score_type VARCHAR(20) DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les performances
CREATE INDEX idx_personality_assessments_user_id ON personality_assessments(user_id);
CREATE INDEX idx_personality_assessments_session_id ON personality_assessments(session_id);
CREATE INDEX idx_personality_responses_assessment_id ON personality_responses(assessment_id);
CREATE INDEX idx_personality_scores_assessment_id ON personality_scores(assessment_id);
CREATE INDEX idx_assessments_user_type_status ON personality_assessments(user_id, assessment_type, status);
```

### Configuration PostgreSQL pour la Production
```bash
# Éditer la configuration PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
```

```ini
# Paramètres de performance
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Sauvegarde Automatique
```bash
# Script de sauvegarde
sudo nano /opt/orientor/scripts/backup_db.sh
```

```bash
#!/bin/bash

# Configuration
DB_NAME="orientor_db"
DB_USER="orientor_user"
BACKUP_DIR="/opt/orientor/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/orientor_backup_$DATE.sql"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Effectuer la sauvegarde
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_FILE

# Compresser la sauvegarde
gzip $BACKUP_FILE

# Supprimer les sauvegardes de plus de 30 jours
find $BACKUP_DIR -name "orientor_backup_*.sql.gz" -mtime +30 -delete

echo "Sauvegarde terminée: $BACKUP_FILE.gz"
```

```bash
# Rendre le script exécutable
chmod +x /opt/orientor/scripts/backup_db.sh

# Ajouter au crontab
crontab -e
# Ajouter cette ligne pour une sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/orientor/scripts/backup_db.sh
```

## Variables d'Environnement {#variables}

### Variables Backend Complètes
```bash
# .env pour le backend
# Base de données
DATABASE_URL=postgresql://orientor_user:secure_password@localhost:5432/orientor_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Configuration HEXACO
HEXACO_DATA_PATH=/opt/orientor/backend/data_n_notebook/data
HEXACO_CONFIG_PATH=/opt/orientor/backend/app/config/hexaco_facet_mapping.json
HEXACO_CACHE_TTL=3600

# Cache Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=1800

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/orientor/backend.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# Sécurité
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=another-secret-key-for-jwt-tokens
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,api.your-domain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
TIMEOUT_KEEP_ALIVE=5
TIMEOUT_GRACEFUL_SHUTDOWN=30

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Email (pour les notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Variables Frontend Complètes
```bash
# .env.local pour le frontend
# API Configuration
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_API_RETRY_ATTEMPTS=3

# HEXACO Configuration
NEXT_PUBLIC_HEXACO_VERSIONS=hexaco_60_fr,hexaco_100_fr,hexaco_60_en,hexaco_100_en
NEXT_PUBLIC_DEFAULT_LANGUAGE=fr
NEXT_PUBLIC_DEFAULT_VERSION=hexaco_60_fr

# UI Configuration
NEXT_PUBLIC_THEME=light
NEXT_PUBLIC_ENABLE_DARK_MODE=true
NEXT_PUBLIC_CHART_ANIMATION=true

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_HOTJAR_ID=1234567

# Feature Flags
NEXT_PUBLIC_ENABLE_BETA_FEATURES=false
NEXT_PUBLIC_ENABLE_OFFLINE_MODE=true

# Performance
NEXT_PUBLIC_CACHE_DURATION=300000
NEXT_PUBLIC_IMAGE_OPTIMIZATION=true

# Environnement
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

## Monitoring et Logs {#monitoring}

### Configuration des Logs

#### Logrotate pour les Logs Applicatifs
```bash
sudo nano /etc/logrotate.d/orientor
```

```
/var/log/orientor/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 orientor orientor
    postrotate
        systemctl reload orientor-backend
        systemctl reload orientor-frontend
    endscript
}
```

#### Configuration de Journald
```bash
sudo nano /etc/systemd/journald.conf
```

```ini
[Journal]
Storage=persistent
Compress=yes
SplitMode=uid
RateLimitInterval=30s
RateLimitBurst=1000
SystemMaxUse=1G
SystemKeepFree=500M
SystemMaxFileSize=100M
MaxRetentionSec=2week
```

### Monitoring avec Prometheus (Optionnel)

#### Installation de Prometheus
```bash
# Créer un utilisateur pour Prometheus
sudo useradd --no-create-home --shell /bin/false prometheus

# Télécharger et installer Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz
sudo cp prometheus-2.40.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.40.0.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool

# Créer les répertoires
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

#### Configuration Prometheus
```bash
sudo nano /etc/prometheus/prometheus.yml
```

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"

scrape_configs:
  - job_name: 'orientor-backend'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    metrics_path: /metrics
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
      
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['localhost:9187']
```

### Alertes et Notifications

#### Script d'Alerte Simple
```bash
sudo nano /opt/orientor/scripts/health_check.sh
```

```bash
#!/bin/bash

# Configuration
BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"
EMAIL="admin@your-domain.com"
LOG_FILE="/var/log/orientor/health_check.log"

# Fonction de log
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Vérifier le backend
check_backend() {
    if curl -f -s $BACKEND_URL > /dev/null; then
        log_message "Backend OK"
        return 0
    else
        log_message "Backend DOWN"
        return 1
    fi
}

# Vérifier le frontend
check_frontend() {
    if curl -f -s $FRONTEND_URL > /dev/null; then
        log_message "Frontend OK"
        return 0
    else
        log_message "Frontend DOWN"
        return 1
    fi
}

# Vérifier la base de données
check_database() {
    if sudo -u orientor psql -U orientor_user -d orientor_db -c "SELECT 1;" > /dev/null 2>&1; then
        log_message "Database OK"
        return 0
    else
        log_message "Database DOWN"
        return 1
    fi
}

# Envoyer une alerte
send_alert() {
    local service=$1
    local message="ALERTE: $service est indisponible sur $(hostname)"
    
    # Envoyer par email (nécessite mailutils)
    echo "$message" | mail -s "Alerte Orientor - $service DOWN" $EMAIL
    
    log_message "Alerte envoyée pour $service"
}

# Vérifications principales
if ! check_backend; then
    send_alert "Backend API"
fi

if ! check_frontend; then
    send_alert "Frontend"
fi

if ! check_database; then
    send_alert "Database"
fi
```

```bash
# Rendre exécutable et ajouter au crontab
chmod +x /opt/orientor/scripts/health_check.sh

# Vérification toutes les 5 minutes
crontab -e
*/5 * * * * /opt/orientor/scripts/health_check.sh
```

## Maintenance {#maintenance}

### Tâches de Maintenance Régulières

#### Script de Maintenance Hebdomadaire
```bash
sudo nano /opt/orientor/scripts/weekly_maintenance.sh
```

```bash
#!/bin/bash

LOG_FILE="/var/log/orientor/maintenance.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_message "=== Début de la maintenance hebdomadaire ==="

# 1. Nettoyage des logs anciens
log_message "Nettoyage des logs..."
find /var/log/orientor -name "*.log" -mtime +30 -delete
find /var/log/nginx -name "*.log" -mtime +30 -delete

# 2. Nettoyage de la base de données
log_message "Nettoyage de la base de données..."
sudo -u orientor psql -U orientor_user -d orientor_db -c "
    DELETE FROM personality_responses 
    WHERE assessment_id IN (
        SELECT id FROM personality_assessments 
        WHERE status = 'abandoned' AND created_at < NOW() - INTERVAL '30 days'
    );
    
    DELETE FROM personality_assessments 
    WHERE status = 'abandoned' AND created_at < NOW() - INTERVAL '30 days';
    
    VACUUM ANALYZE;
"

# 3. Mise à jour des statistiques
log_message "Mise à jour des statistiques de la base de données..."
sudo -u orientor psql -U orientor_user -d orientor_db -c "ANALYZE;"

# 4. Vérification de l'espace disque
log_message "Vérification de l'espace disque..."
df -h | grep -E "(/$|/opt|/var)" >> $LOG_FILE

# 5. Redémarrage des services (si nécessaire)
if systemctl is-failed orientor-backend > /dev/null; then
    log_message "Redémarrage du backend..."
    sudo systemctl restart orientor-backend
fi

if systemctl is-failed orientor-frontend > /dev/null; then
    log_message "Redémarrage du frontend..."
    sudo systemctl restart orientor-frontend
fi

log_message "=== Fin de la maintenance hebdomadaire ==="
```

### Mise à Jour de l'Application

#### Script de Déploiement
```bash
sudo nano /opt/orientor/scripts/deploy.sh
```

```bash
#!/bin/bash

# Configuration
REPO_URL="https://github.com/your-org/orientor.git"
DEPLOY_DIR="/opt/orientor"
BACKUP_DIR="/opt/orientor/backups/deployments"
DATE=$(date +%Y%m%d_%H%M%S)

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Créer une sauvegarde avant déploiement
create_backup() {
    log_message "Création de la sauvegarde pré-déploiement..."
    mkdir -p $BACKUP_DIR
    
    # Sauvegarde de la base de données
    pg_dump -U orientor_user -h localhost orientor_db > $BACKUP_DIR/db_backup_$DATE.sql
    
    # Sauvegarde des fichiers
    tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz -C $DEPLOY_DIR backend frontend
    
    log_message "Sauvegarde créée: $BACKUP_DIR/*_$DATE.*"
}

# Déploiement du backend
deploy_backend() {
    log_message "Déploiement du backend..."
    
    cd $DEPLOY_DIR/backend
    
    # Arrêter le service
    sudo systemctl stop orientor-backend
    
    # Mettre à jour le code
    git pull origin main
    
    # Installer les dépendances
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Migrations de base de données (si nécessaire)
    # alembic upgrade head
    
    # Redémarrer le service
    sudo systemctl start orientor-backend
    
    # Vérifier le statut
    sleep 5
    if systemctl is-active orientor-backend > /dev/null; then
        log_message "Backend déployé avec succès"
    else
        log_message "ERREUR: Échec du déploiement backend"
        return 1
    fi
}

# Déploiement du frontend
deploy_frontend() {
    log_message "Déploiement du frontend..."
    
    cd $DEPLOY_DIR/frontend
    
    # Arrêter le service
    sudo systemctl stop orientor-frontend
    
    # Mettre à jour le code
    git pull origin main
    
    # Installer les dépendances et build
    npm ci --production
    npm run build
    
    # Redémarrer le service
    sudo systemctl start orientor-frontend
    
    # Vérifier le statut
    sleep 10
    if systemctl is-active orientor-frontend > /dev/null; then
        log_message "Frontend déployé avec succès"
    else
        log_message "ERREUR: Échec du déploiement frontend"
        return 1
    fi
}

# Exécution du déploiement
log_message "=== Début du déploiement ==="

create_backup

if deploy_backend && deploy_frontend; then
    log_message "=== Déploiement terminé avec succès ==="
else
    log_message "=== ERREUR: Échec du déploiement ==="
    exit 1
fi
```

## Troubleshooting {#troubleshooting}

### Problèmes Courants

#### Backend ne démarre pas
```bash
# Vérifier les logs
sudo journalctl -u orientor-backend -n 50

# Vérifier la configuration
cd /opt/orientor/backend
source venv/bin/activate
python -c "from app.main import app; print('Configuration OK')"

# Vérifier la base de données
psql -U orientor_user -d orientor_db -h localhost -c "SELECT 1;"

# Vérifier les permissions
ls -la /opt/orientor/backend/data_n_notebook/data/
```

#### Frontend ne se charge pas
```bash
# Vérifier les logs
sudo journalctl -u orientor-frontend -n 50

# Vérifier le build
cd /opt/orientor/frontend
npm run build

# Vérifier la configuration Nginx
sudo nginx -t
sudo systemctl status nginx
```

#### Problèmes de Performance
```bash
# Vérifier l'utilisation des ressources
htop
iotop
df -h

# Vérifier les connexions à la base de données
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Vérifier les logs de performance
grep "slow" /var/log/orientor/backend.log
```

#### Problèmes de Base de Données
```bash
# Vérifier les connexions
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname = 'orientor_db';"

# Vérifier l'espace disque
du -sh /var/lib/postgresql/

# Analyser les requêtes lentes
sudo -u postgres psql