# 📋 Plan de Répartition des Tâches - Équipe DEV 2 (Backend Services & Analytics)

Ce document détaille les missions et responsabilités spécifiques de l'équipe **DEV 2** sur le backend de **SUNU CIVIL**.

> [!IMPORTANT]
> **Rappel de Contexte** :
> L'équipe **DEV 2** travaille **SUR** l'architecture centrale mise en place par l'équipe **DEV 1 (DEV 1A Core Architect)**. 
> DEV 2 ne doit **PAS** modifier le cœur de l'architecture (Authentification, Modèles de base, RBAC principal), mais y greffer des services complémentaires, des statistiques, du monitoring et des optimisations de manière modulaire.

---

## 🏗️ Structure Globale de l'Équipe DEV 2

```text
DEV 2 (2 Développeurs Backend)
├── DEV 2A PAPE ALIOUNE SENE : Dashboard & Analytics Engineer
└── DEV 2B EL HADJI MASSOGUI DIOP : Services & System Integration Engineer
```

---

## 🧑‍💻 DEV 2A - PAPE ALIOUNE SENE : Dashboard & Analytics Engineer

**Objectif principal** : Construire toute la logique statistique, les analytics, le monitoring d'activité et les API nécessaires au fonctionnement du Dashboard Administratif (React).

### 📁 Applications & Fichiers cibles
* `backend/apps/dashboard/` (déjà existant en stub)
* `backend/apps/analytics/` (à initialiser si besoin)

### ⚙️ Missions et spécifications techniques

#### 1. Développement des APIs Statistiques et KPIs
Implémenter des endpoints performants sous `/api/dashboard/` pour renvoyer les données structurées suivantes :
* **`/api/dashboard/stats/`** : 
  * Total des dossiers dans le système.
  * Répartition des dossiers par statut (`draft`, `submitted`, `in_review`, `approved`, `rejected`, `completed`).
* **`/api/dashboard/kpis/`** :
  * Temps moyen de traitement des dossiers par commune (calculé via la différence entre `submitted_at` et `completed_at`).
  * Taux de rejet global et par commune.
  * Activité et productivité moyenne des agents de la commune.
* **`/api/dashboard/charts/`** :
  * Volume journalier/hebdomadaire des dépôts de dossiers pour les graphiques de tendances.
  * Pics d'activité horaires et saisonniers.
* **`/api/dashboard/activity/`** & **`/api/dashboard/recent-actions/`** :
  * Logs d'activité récents basés sur le modèle `AuditLog` (connexions, modifications sensibles).

#### 2. Recherche Avancée et Filtres
Créer des fonctionnalités de filtrage puissantes sur les dossiers et les utilisateurs :
* Filtrer les dossiers par commune, par statut, par type d'acte, par assignation d'agent et par plage de dates.
* Recherche textuelle indexée (sur le numéro de référence, le nom du citoyen, ou son numéro CNI).

#### 3. Optimisation de l'ORM et Performance SQL
Le dashboard agrégeant beaucoup de données, DEV 2A doit veiller à la rapidité des requêtes :
* Utiliser systématiquement `select_related` (pour les clés étrangères comme `commune`, `citizen`) et `prefetch_related`.
* Utiliser les fonctions d'agrégation de Django (`Count`, `Avg`, `Min`, `Max`, `Q` expressions) au niveau de la base de données plutôt que de faire des boucles en Python.
* Suggérer et implémenter des index PostgreSQL sur les champs fréquemment filtrés (`status`, `commune`, `created_at`).

---

## 🧑‍💻 DEV 2B - EL HADJI MASSOGUI DIOP : Services & System Integration Engineer

**Objectif principal** : Mettre en œuvre le système de notifications (Push/SMS/Emails), le monitoring des erreurs backend, les automatisations système et l'architecture d'intégration avec l'État.

### 📁 Applications & Fichiers cibles
* `backend/apps/notifications/` (déjà existant en stub)
* `backend/apps/services/`
* `backend/apps/system/` (à initialiser si besoin)

### ⚙️ Missions et spécifications techniques

#### 1. Système de Notifications (Firebase Cloud Messaging - FCM)
Créer un service de notification centralisé capable de gérer le temps réel :
* Gérer l'enregistrement et le stockage des tokens d'appareils mobiles (FCM Tokens) associés aux comptes utilisateurs.
* **Notifications requises pour les citoyens** :
  * "Dossier reçu et enregistré" (lors du passage à `submitted`).
  * "Action requise sur votre dossier" (lors d'un retour ou rejet temporaire).
  * "Votre acte d'état civil est disponible" (lors du passage à `completed`).
* **Notifications requises pour les agents** :
  * "Nouveau dossier soumis à traiter" (assignation ou file d'attente commune).
  * "Alerte de dossier urgent" (dossiers en attente depuis trop longtemps).

#### 2. Services Systèmes & Automatisations
* Mettre en œuvre des scripts automatiques ou des tâches planifiées (par exemple, des rappels de dossiers non traités, le nettoyage des fichiers temporaires).
* Implémenter les utilitaires système communs à l'application.

#### 3. Monitoring d'Erreurs & Journalisation (System Logs)
* Configurer le système de logs Django (`logging` dans `settings/base.py`) pour capturer et enregistrer toutes les exceptions non gérées dans des fichiers de log sécurisés.
* Créer l'endpoint **`/api/system/health/`** pour retourner l'état de santé du backend (statut de connexion à la base de données, espace disque disponible, latence d'API).

#### 4. Architecture pour Intégrations Futures (ANEC, APIs Gouvernementales)
* Le hackathon ne requiert pas d'intégrations réelles à des systèmes nationaux de production (souvent fermés).
* DEV 2B doit cependant concevoir une **architecture de modules d'intégration fictifs (Mock Services)** avec des interfaces extensibles et documentées dans `apps/integrations/` pour simuler le dialogue futur avec l'ANEC ou le registre national.

---

## 🚫 Règles d'Or et Interdictions pour DEV 2

* ❌ **Interdiction formelle** de modifier ou d'altérer le système d'authentification centralisé (`apps/authentication/`) sans validation préalable de l'architecte Core.
* ❌ **Interdiction** de contourner les permissions de sécurité et les rôles RBAC mis en place par DEV 1.
* ❌ **Interdiction** de dupliquer de la logique métier. Si une fonction existe dans `apps/shared/` ou dans un autre module, elle doit être importée et réutilisée.
* ⚠️ **Obligation** de s'assurer que chaque endpoint créé est documenté automatiquement dans Swagger (`/api/docs/`) à l'aide de décorateurs `drf-spectacular` si des paramètres complexes sont requis.
