# 📋 Plan de Répartition des Tâches - Équipe DEV 1 (Backend Core, IA & Services)

Ce document détaille la répartition précise des tâches de l'équipe **DEV 1** pour le backend de **SUNU CIVIL**. L'équipe DEV 1 a la responsabilité entière du cœur du backend Django, des services associés (Notifications, Statistiques, QR Codes) et de la partie intelligence artificielle (OCR, détection de doublons, etc.).

---

## 🧑‍💻 DEV 1A - LANSANA COLY : Tech Lead / Architecture Core

**Mission principale** : Garantir la robustesse de l'architecture, la sécurité, le bon fonctionnement de la base de données, la documentation globale et la cohérence technique.

### ⚙️ Spécifications techniques & Tâches
1. **Architecture & Base de données** :
   * Maintenance de la structure Django, gestion des environnements (`base.py`, `development.py`, `production.py`).
   * Administration de la base de données PostgreSQL.
2. **Sécurité & Authentification** :
   * Gestion du système d'authentification JWT (durées de vie des tokens, rotation, blacklist).
   * Gestion du contrôle d'accès basé sur les rôles (RBAC) et permissions personnalisées.
3. **Qualité & Supervision** :
   * Revue de code (Code Review) de l'ensemble de l'équipe backend.
   * Coordination technique avec les autres équipes (DEV 2, DEV 3, DEV 4).
   * Documentation globale (Swagger/Postman).

---

## 🧑‍💻 DEV 1B - PATHE FALL : Dossiers & Workflow

**Mission principale** : Prendre en charge toute la gestion des demandes administratives, le cycle de validation, les pièces jointes, la génération d'actes en PDF et l'intégration des QR Codes.

### 📁 Applications associées
* `apps/dossiers/`
* `apps/documents/`
* `apps/qr/` (en collaboration avec la génération)

### ⚙️ Spécifications techniques & Tâches
1. **CRUD Dossiers & Workflow** :
   * Créer et valider la machine à états pour la transition des statuts (`draft` -> `submitted` -> `in_review` -> `approved`/`rejected` -> `completed`).
   * Génération automatique de la référence de dossier unique (ex: `SNCV-2026-XXXXX`).
   * Actions d'attribution des dossiers aux agents municipaux.
2. **Upload sécurisé des Documents** :
   * Implémenter le validateur d'uploads (limite stricte à 10 Mo, filtrage par type MIME et validation par magic bytes pour bloquer les scripts malveillants).
3. **Génération PDF & Intégration QR Code** :
   * Concevoir un service pour générer automatiquement l'acte officiel au format PDF dès que le dossier passe au statut `completed`.
   * Générer un code QR sécurisé contenant l'URL de vérification de l'acte et l'apposer automatiquement sur le document PDF généré.

---

## 🧑‍💻 DEV 1C - MAIMOUNA SALL : Notifications & Services Dashboard

**Mission principale** : Prendre en charge le système de notifications en temps réel pour l'ensemble des utilisateurs, le monitoring système et les endpoints statistiques du Dashboard.

### 📁 Applications associées
* `apps/notifications/`
* `apps/dashboard/`
* `apps/audit_logs/`

### ⚙️ Spécifications techniques & Tâches
1. **Notifications Cloud (FCM)** :
   * Configurer Firebase Cloud Messaging (FCM) côté backend pour stocker les tokens d'appareils et envoyer des notifications push en temps réel aux citoyens (avancement de dossier, validation, rejet) et aux agents (nouveau dossier reçu).
2. **Statistiques & Endpoints Dashboard** :
   * Créer les API pour alimenter le dashboard d'administration React :
     * Statistiques globales (nombre de dossiers, taux d'approbation et de rejet).
     * Calcul de performance (temps moyen de traitement des dossiers par commune/agent).
     * Volumes journaliers et graphiques d'activité pour l'interface frontend.
3. **Historique & Traçabilité (Audit Logs)** :
   * Mettre en œuvre le middleware d'audit pour enregistrer chaque action sensible en base de données.
   * Configurer le système de logs système pour enregistrer les erreurs graves dans des fichiers dédiés.

---

## 🧑‍💻 DEV 1D - IBRAHIMA KHALILOU DIALLO : IA & OCR

**Mission principale** : Implémenter l'intelligence artificielle au service de l'état civil, comprenant la lecture automatique de documents, la détection de fraudes et l'aide aux citoyens.

### 📁 Applications associées
* `apps/ai/`

### ⚙️ Spécifications techniques & Tâches
1. **OCR Tesseract (Lecture de documents)** :
   * Intégrer PyTesseract (ou une API OCR) pour extraire automatiquement le texte des scans de documents téléversés par le citoyen (ex: anciennes cartes d'identité, attestations).
2. **Validation Intelligente & Détection de Doublons** :
   * Concevoir l'algorithme comparant les textes extraits par OCR avec les informations saisies par le citoyen (nom, date de naissance, CNI) pour signaler automatiquement toute incohérence aux agents de vérification.
   * Implémenter un système de détection des demandes doublons (ex: vérifier si un citoyen a déjà fait une demande similaire en cours de traitement).
3. **Assistant FAQ Intelligent** :
   * Créer un endpoint d'assistance / agent FAQ (basé sur des règles d'IA ou une API LLM simplifiée) pour aider le citoyen dans ses démarches (répondre à ses questions sur la constitution de son dossier).
