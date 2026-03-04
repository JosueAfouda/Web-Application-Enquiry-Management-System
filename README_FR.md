# Enquiry Management System (EMS)

Une application web full-stack pour gérer les demandes clients de produits pharmaceutiques, depuis la première sollicitation jusqu’à la clôture de la livraison.

## 1. Vue d’ensemble du projet
EMS permet aux équipes d’export/trading de piloter un processus complexe, de la demande (enquiry) jusqu’à la commande, dans un seul système. Au lieu de suivre les dossiers via des feuilles Excel, des e-mails et des discussions dispersées, EMS centralise le workflow avec gestion des rôles, transitions de statuts contrôlées, révisions tarifaires, approbations, documents commerciaux, reporting et historique d’audit.

### Problèmes résolus
- Les demandes étaient difficiles à suivre entre équipes (BD, Admin, Super Admin, Supply Chain).
- L’historique des négociations de devis était fragmenté.
- Les étapes commerciales (PO, facture, paiement, livraison) manquaient de traçabilité.
- Les managers n’avaient pas de KPI homogènes.

### Public cible
- Équipes opérations d’export/trading pharmaceutique
- Équipes Sales / Business Development
- Équipes commerciales et Supply Chain
- Équipes techniques qui maintiennent des systèmes métiers internes

## 2. Contexte métier
Dans l’export pharmaceutique, une demande client peut passer par plusieurs cycles de pricing fabricant, d’approbation interne et d’exécution commerciale avant d’être clôturée. Les retards ou les informations manquantes impactent directement le chiffre d’affaires et la satisfaction client.

EMS standardise ce cycle :
- Saisir la demande
- Construire et réviser les devis
- Approuver les prix
- Exécuter PO / facturation / paiements / livraison
- Mesurer les résultats via des rapports

## 3. Concepts métier clés
- **Customer** : client acheteur qui demande des produits.
- **Manufacturer** : fournisseur qui propose les prix et exécute la fourniture.
- **Product** : article pharmaceutique géré dans les référentiels.
- **Enquiry** : demande client contenant une ou plusieurs lignes produit.
- **Quotation** : proposition commerciale liée à une enquiry.
- **Quotation Revision** : version tarifaire d’une quotation, utilisée pour la négociation.
- **Approval** : décision formelle sur une révision soumise.
- **Customer PO** : bon de commande reçu du client.
- **RTM PO** : PO interne / orienté fabricant pour l’exécution achat.
- **Invoice** : document de facturation lié au contexte enquiry/PO.
- **Payment** : encaissement rattaché à une facture, avec suivi du reste à payer.
- **Delivery Tracking** : suivi du cycle d’expédition et des événements logistiques.

## 4. Workflow de bout en bout
```text
Demande Client
   -> Création d'enquiry (BD/Admin)
   -> Revue de l'enquiry & suivi des statuts
   -> Création de quotation
   -> Révision(s): fret + marge + prix par ligne
   -> Soumission pour approbation
   -> Approbation/Rejet (Admin/SuperAdmin)
   -> Customer PO / RTM PO
   -> Création de facture
   -> Encaissement des paiements (partiel/complet)
   -> Livraison + événements de livraison
   -> KPI & exports Excel
```

## 5. Méthodologie de conception des fonctionnalités
### Authentication & Role-Based Access
- **Objectif** : limiter les actions selon le rôle.
- **Problème résolu** : modifications non autorisées et responsabilités floues.
- **Logique de conception** : authentification JWT + garde-fous RBAC côté API et navigation UI adaptée aux rôles.

### Master Data Management
- **Objectif** : garantir des données clients/fabricants/produits cohérentes.
- **Problème résolu** : doublons et incohérences de référentiel.
- **Logique de conception** : CRUD des référentiels avec validations et import Excel pour le volume.

### Enquiry Lifecycle
- **Objectif** : suivre la progression d’une enquiry avec responsabilité explicite.
- **Problème résolu** : perte de contexte et ambiguïté des statuts.
- **Logique de conception** : transitions de statuts contrôlées + historique (qui/quand/commentaire).

### Quotation Revision System
- **Objectif** : gérer la négociation sans perdre les prix antérieurs.
- **Problème résolu** : écrasement de l’historique de prix.
- **Logique de conception** : enregistrements de révision immuables avec calculs de totaux et traçabilité des versions.

### Approval Workflow
- **Objectif** : instaurer une gouvernance avant engagement commercial.
- **Problème résolu** : diffusion de prix non approuvés.
- **Logique de conception** : états submit/approve/reject, timeline d’approbation, remarques obligatoires pour approve/reject.

### Purchase Orders
- **Objectif** : transformer un prix approuvé en ordres exécutables.
- **Problème résolu** : ruptures de transmission entre équipes.
- **Logique de conception** : entités séparées Customer PO et RTM PO, liées à une révision approuvée.

### Invoice & Payment Tracking
- **Objectif** : piloter les créances et le recouvrement.
- **Problème résolu** : faible visibilité sur les montants restants.
- **Logique de conception** : statuts de facture (`UNPAID/PARTIAL/PAID`) dérivés des paiements, avec blocage du surpaiement.

### Reporting & Excel Export
- **Objectif** : fournir de la visibilité opérationnelle et managériale.
- **Problème résolu** : consolidation KPI manuelle.
- **Logique de conception** : API KPI + endpoints d’export (`enquiries/quotations/invoices/payments.xlsx`).

### Audit Trail
- **Objectif** : assurer responsabilité et traçabilité.
- **Problème résolu** : analyse post-incident difficile.
- **Logique de conception** : événements d’audit structurés sur les actions métier critiques (création/mise à jour/approbation/rejet).

### Observability
- **Objectif** : rendre le comportement runtime diagnostiable.
- **Problème résolu** : débogage lent et manque de visibilité sur les erreurs.
- **Logique de conception** : endpoint `/health`, logs structurés, propagation d’un request ID, schéma d’erreur normalisé.

## 6. Architecture système
### Vue globale
```text
[React + Nginx (web)]  --->  [FastAPI (api)]  --->  [PostgreSQL (db)]
         |                        |
         |                        +--> Migrations Alembic
         |
         +--> UI orientée rôles, formulaires, actions de workflow
```

### Composants
- **Frontend** : SPA React + TypeScript (build Vite), servie par Nginx.
- **Backend** : service FastAPI exposant les APIs REST et les règles métier.
- **Base de données** : PostgreSQL avec historique de migrations Alembic.
- **Contrat API** : OpenAPI disponible via `/docs` et `/openapi.json`.
- **Plateforme conteneurs** : Docker Compose pour l’orchestration locale.
- **Production** : Blueprint Render (`render.yaml`) pour API + frontend statique + Postgres managé.

## 7. Stack technologique
- **Backend** : Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic.
- **Database** : PostgreSQL 16.
- **Frontend** : React 19, TypeScript, Vite, Tailwind CSS, React Query, React Hook Form + Zod.
- **Auth/Security** : modèle JWT access/refresh, hash de mots de passe, RBAC.
- **Reporting** : Pandas/OpenPyXL/XlsxWriter pour les exports Excel.
- **Infra** : Docker, Docker Compose, Render.

Pourquoi cette stack :
- Open source et compatible avec un budget nul
- Itérations API rapides avec typage fort et validation
- Parcours de déploiement fiable du local vers le cloud

## 8. Structure du projet
```text
backend/
  app/
    api/            # endpoints HTTP
    services/       # logique métier
    models/         # entités SQLAlchemy
    schemas/        # contrats requête/réponse
    db/migrations/  # révisions Alembic
  tests/            # tests backend

frontend/
  src/
    pages/          # écrans par route
    components/     # composants UI et layout
    context/        # états auth/workflow
    lib/            # client API, helpers, formatage

scripts/
  smoke_local.sh
  smoke_frontend.sh

render.yaml         # blueprint production
docker-compose.yml  # orchestration locale
```

## 9. Exécution locale
### Prérequis
- Docker + Docker Compose

### 1) Configurer l’environnement
```bash
cp .env.example .env
```

### 2) Démarrer tous les services
```bash
docker compose up -d --build
```

### 3) Appliquer les migrations base de données
```bash
docker compose exec -T api alembic -c alembic.ini upgrade head
```

### 4) Accéder au système
- Frontend : http://localhost:3000
- Documentation API : http://localhost:8000/docs
- Santé API : http://localhost:8000/health

### 5) Compte par défaut (local/dev)
- Username : `admin`
- Password : `admin`

### Variables d’environnement importantes
- `APP_ENV`, `APP_NAME`, `APP_VERSION`
- `SECRET_KEY`, `JWT_ALGORITHM`, durées d’expiration des tokens
- `DB_*` ou `DATABASE_URL`
- `CORS_ORIGINS`
- `DELIVERY_START_REQUIRED_STEP`
- `VITE_API_URL` (cible API au build du frontend)

## 10. Smoke Testing
Lancer les vérifications de base :
```bash
bash scripts/smoke_local.sh
bash scripts/smoke_frontend.sh
```

Ce que ces scripts valident :
- Endpoint de santé API
- Flux d’authentification (`/auth/login`, `/auth/me`)
- Disponibilité du frontend et routage SPA

## 11. Déploiement (Render)
La production est définie dans `render.yaml` :
- `ems-api` (service web Python)
- `ems-web` (service web statique)
- `ems-postgres` (Postgres managé)

Flux de déploiement :
1. Render construit l’API via `build.sh`.
2. La commande de démarrage API attend la base (`wait-for-postgres.py`).
3. Les migrations Alembic sont exécutées au démarrage.
4. Uvicorn expose FastAPI.
5. Le frontend est buildé sur Render puis publié en statique.
6. `VITE_API_URL` est alimenté depuis l’URL du service API.

## 12. Modèle de sécurité
- Authentification JWT (tokens d’accès + refresh).
- RBAC appliqué côté backend et reflété dans la navigation frontend.
- Schéma d’erreur standardisé avec identifiant de requête.
- Événements d’audit enregistrés sur les actions métier critiques.
- Liste d’origines CORS pilotée par variables d’environnement.

## 13. Observabilité
- **Health checks** :
  - API : `/health`
  - Healthchecks de conteneurs dans Docker Compose
- **Traçabilité des requêtes** :
  - `X-Request-ID` généré/conservé par requête
  - renvoyé dans les réponses et erreurs
- **Logs** :
  - logs structurés avec méthode, route, statut, durée
- **Comportement opérationnel** :
  - le frontend surveille la disponibilité API et propose une action de retry

## 14. Améliorations futures
- Extensions BRD avancées (workflow plus large et champs métier additionnels)
- Administration de l’approbation des utilisateurs et reset de mot de passe
- Gestion de pièces jointes pour quotations/factures
- Notifications e-mail (rappels, digest quotidien)
- Rapports supplémentaires (ageing, performance, revenu détaillé, export PDF)
- Portails self-service optionnels pour customers/manufacturers

---
Pour un parcours de validation guidé via l’interface, consultez `FRONTEND_USER_GUIDE.md`.
