# 🏆 Rapport de Livraison - Hackathon SUNU CIVIL

**Développeur :** Ibrahima Khalilou Diallo (DEV 1D)
**Rôle :** IA & OCR, Audit Logs Avancés, Signaux et API Dashboard Core
**Date de Livraison :** Juin 2026

Ce rapport détaille l'ensemble des fonctionnalités implémentées sur la plateforme SUNU CIVIL (Backend Django) pour répondre aux exigences du MVP.

---

## 🤖 1. Module d'Intelligence Artificielle & OCR (`apps/ai`)

L'objectif de ce module est de réduire les fraudes et d'accélérer le traitement des demandes en automatisant la lecture et la validation des documents.

* **Moteur d'Extraction OCR (`ocr.py`) :** 
  Intégration de `pytesseract` pour lire et extraire le texte brut à partir d'images scannées (anciennes CNI, attestations).
* **Validation Intelligente (`validators.py`) :** 
  Algorithme de comparaison (`validate_citizen_document`) qui confronte les données extraites par l'OCR avec le profil citoyen enregistré en base de données (Numéro CNI, Date de naissance, Nom, Prénom) et génère un score de confiance.
* **Détection Anti-Fraude (Doublons) :** 
  Mise en place de `check_dossier_duplicate` pour empêcher la soumission de requêtes multiples identiques par un même utilisateur.
* **Assistant Virtuel FAQ (`faq.py`) :** 
  Agent basé sur des règles d'extraction de mots-clés (Regex) permettant d'assister les citoyens 24h/24 sur les procédures, délais et tarifs de l'état civil.

**Endpoints développés :**
* `POST /api/ai/ocr-validate/`
* `POST /api/ai/faq/`

---

## 📊 2. API Dashboard Core (`apps/dashboard`)

Développement du moteur de statistiques permettant d'alimenter les tableaux de bord (React) des agents municipaux et des maires.

* **Statistiques Globales :** Comptage en temps réel du nombre total de dossiers et calcul des taux d'approbation et de rejet.
* **Mesure de Performance (SLA) :** Calcul automatisé du temps moyen de traitement des dossiers (en jours).
* **Granularité des Données :** Extraction des performances détaillées **par agent** et **par commune**.
* **Activité Récente :** Agrégation des volumes d'activité journalière sur les 30 derniers jours.

**Endpoint développé :**
* `GET /api/dashboard/stats/`

---

## 🔒 3. Audit Logs & Sécurité (`apps/audit_logs`)

Système de traçabilité complète de l'application pour répondre aux exigences de sécurité gouvernementale.

* **Middleware d'Audit :** Interception automatique de toutes les requêtes API sensibles (`POST`, `PUT`, `PATCH`, `DELETE`). Enregistrement de l'auteur (via JWT), de l'action, et de l'adresse IP.
* **Signaux Django (Signals) :** Écouteurs d'événements (`post_save`, `post_delete`) pour tracer tout changement d'état sur les entités critiques (`User`, `Dossier`).
* **Logs Système Fichier :** Configuration du logger Django pour persister les erreurs critiques du système dans un fichier sécurisé (`logs/sunucivil_errors.log`).

**Endpoint développé :**
* `GET /api/audit-logs/` (Lecture de l'historique de sécurité)

---

## ✅ Tests et Validation

* La totalité du code a été validée avec `python manage.py check`.
* Les endpoints ont été documentés et testés avec succès via **Swagger UI** (`/api/docs/`).
* Les algorithmes de l'Assistant FAQ et du Dashboard Stats retournent des données fiables et exactes.
* Les dépendances (`pytesseract`, `Pillow`) ont été intégrées à `requirements.txt`.

**Livrable 100% complété.** Prêt pour l'intégration frontend et la présentation au jury ! 🚀
