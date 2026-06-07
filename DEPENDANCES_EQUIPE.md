# TERANGA CIVIL — Dépendances Inter-Développeurs

> Document de coordination d'équipe. Mis à jour après l'audit QA de la branche `Developpe`.
>
> **Légende :**
> - 🟢 **Peut démarrer maintenant** — aucune dépendance bloquante
> - 🟡 **Partiellement bloqué** — peut commencer certaines tâches, mais pas toutes
> - 🔴 **Bloqué** — dépend d'une livraison non encore faite
> - ✅ **Déjà livré** — disponible dans la branche `Developpe`

---

## Vue d'ensemble des dépendances (graphe simplifié)

```
DEV 1A (Backend Core)
    │
    ├──────────────────────────────────────┐
    │                                      │
    ▼                                      ▼
DEV 1B (PDF/Timbres)            DEV 1C (Notifications/Dashboard)
    │                                      │
    │              DEV 1D (IA/OCR) ────────┤
    │                   │                  │
    ▼                   ▼                  ▼
DEV 2B (React Citoyen) ◄──── DEV 2A (React Admin Dashboard)
DEV 4 (Flutter Dossiers) ◄───── DEV 3 (Flutter Auth)
```

---

## DEV 1A — Lansana Coly (Backend Core + Co-IA)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Système OTP (modèle `OTPCode`, endpoints `/api/auth/otp/`) | Indépendant, extension de l'auth existante ✅ |
| Login par téléphone (`phone` OU `email`) | Extension du serializer existant |
| Throttling anti brute-force sur `/api/auth/login/` | Config Django uniquement |
| Historique des connexions (`LoginHistory` modèle + endpoint) | Extension des signaux existants |
| Demande pour une tierce personne (champs Dossier + endpoint verify-register) | Modèle Dossier déjà existant ✅ |

### 🟡 Partiellement bloqué (partage avec DEV 1D)

| Tâche | Dépend de |
|-------|-----------|
| Refonte assistant Ndiogoye (intentions + contexte) | ⚠️ À coordonner avec DEV 1D — développement conjoint |

### Ce que DEV 1A livre aux autres

| Livraison | Débloque |
|-----------|----------|
| Endpoints OTP terminés | DEV 3 (Flutter Auth) peut finaliser l'écran OTP |
| Login téléphone actif | DEV 3 et DEV 2B peuvent adapter leurs formulaires |
| Endpoint `verify-register` (tierce personne) | DEV 2B et DEV 4 peuvent construire ce formulaire |
| Ndiogoye IA structurée | DEV 2B et DEV 4 peuvent construire l'interface chat |

---

## DEV 1B — (PDF Officiels + Timbres + Signatures)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Générateur PDF `reportlab` (structure de base) | `reportlab` déjà dans `requirements.txt` ✅ |
| Modèle `Timbre` (numéro unique, montant, hash cryptographique) | Indépendant du reste |
| Structure de `CivilActPDFGenerator` pour les 3 types d'actes | Architecture pure Python |
| Endpoint `/api/documents/{id}/appliquer-timbre/` | Modèle Document déjà existant ✅ |

### 🟡 Partiellement bloqué

| Tâche | Dépend de |
|-------|-----------|
| Intégration QR Code dans le PDF | DEV 1B doit d'abord avoir le générateur PDF fonctionnel (auto-dépendance) |
| Endpoint de signature `/api/dossiers/{id}/signer/` | Le workflow de dossier est ✅ mais il faut définir le modèle `OfficierSignature` |

### ⚠️ N'attend PERSONNE mais TOUT LE MONDE attend DEV 1B

| Livraison | Débloque |
|-----------|----------|
| PDF généré pour un dossier complet | DEV 2A (bouton "Générer PDF" dans la liste des dossiers) |
| PDF généré pour un dossier complet | DEV 2B (page de suivi — bouton "Télécharger mon acte") |
| PDF généré pour un dossier complet | DEV 4 (écran de détail dossier Flutter — bouton télécharger) |
| Timbre numérique implémenté | DEV 2A (affichage du timbre dans le dashboard admin) |

---

## DEV 1C — (Notifications + Dashboard amélioré + Export CSV)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Notifications asynchrones (threading) | Modification de `signals.py` uniquement |
| Endpoint `GET /api/notifications/` + `mark-read` | Modèle Notification déjà existant ✅ |
| Dashboard enrichi (`dossiers_par_type`, `dossiers_par_commune`, top agents) | Requêtes ORM sur données existantes ✅ |
| Export CSV des dossiers `GET /api/dashboard/export/` | Python natif `csv`, aucune lib externe |

### 🟡 Partiellement bloqué

| Tâche | Dépend de |
|-------|-----------|
| Notifier à la signature du document | DEV 1B (endpoint signature) doit exister |

### Ce que DEV 1C livre aux autres

| Livraison | Débloque |
|-----------|----------|
| Dashboard enrichi | DEV 2A peut afficher tous les graphiques (types, communes, agents) |
| Export CSV | DEV 2A peut implémenter le bouton d'export |
| Notifications mark-read | DEV 2B et DEV 4 peuvent construire le centre de notifications |

---

## DEV 1D — (IA & OCR avancé, Co-Ndiogoye avec DEV 1A)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Extraction structurée CNI (Nom, Prénom, N° doc, Dates) depuis OCR brut | Amélioration de `ocr.py` existant ✅ |
| Pré-traitement image avant OCR (niveaux de gris, binarisation) | `Pillow` déjà installé ✅ |
| Endpoint de confirmation OCR `/api/ai/ocr/confirm/` (l'utilisateur valide avant enregistrement) | Extension de `views.py` IA existant ✅ |
| Amélioration de la détection de doublons (hash SHA-256 du fichier document) | Extension de `validators.py` ✅ |

### 🟡 Partiellement bloqué (partage avec DEV 1A)

| Tâche | Dépend de |
|-------|-----------|
| Assistant Ndiogoye conversationnel (intentions, contexte) | ⚠️ À faire EN BINÔME avec DEV 1A — ne pas développer en silo |

### Ce que DEV 1D livre aux autres

| Livraison | Débloque |
|-----------|----------|
| Extraction CNI structurée | DEV 2B peut pré-remplir les formulaires automatiquement |
| Extraction CNI structurée | DEV 4 (Flutter) peut pré-remplir les champs après scan photo |
| Endpoint `/api/ai/ocr/confirm/` | DEV 2B et DEV 4 peuvent afficher "Confirmez-vous ces informations ?" |
| Ndiogoye IA conversationnel | DEV 2B et DEV 4 peuvent construire l'interface chat complète |

---

## DEV 2A — (Dashboard React Admin)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Architecture React + Routing complet | Pur frontend, indépendant |
| Pages statiques (Login, Layout, Sidebar, Navbar) | Pur frontend |
| Intercepteur Axios (JWT inject + refresh auto + redirect 401) | Auth API déjà ✅ sur `Developpe` |
| Authentification admin (Login + Logout + Refresh) | Endpoints `POST /api/auth/login/` et `/logout/` ✅ |
| CRUD Communes (`GET/POST/PUT/DELETE /api/communes/`) | Disponible ✅ |
| CRUD Agents/Utilisateurs (`GET/POST /api/users/`) | Disponible ✅ |
| Liste des dossiers avec filtres (`GET /api/dossiers/`) | Disponible ✅ |
| Détail dossier + changement de statut | Disponible ✅ |
| Liste des logs d'audit (`GET /api/audit-logs/`) | Disponible ✅ |
| Cards KPI de base (total dossiers, en attente, traités) | `GET /api/dashboard/stats/` ✅ |

### 🟡 Bloqué partiellement — attend ces livraisons

| Tâche bloquée | Attend | Développeur |
|---------------|--------|-------------|
| Graphiques enrichis (par type, par commune, top agents) | `GET /api/dashboard/stats/` enrichi | DEV 1C |
| Bouton "Générer PDF" fonctionnel | Endpoint génération PDF | DEV 1B |
| Bouton "Export CSV" | `GET /api/dashboard/export/` | DEV 1C |
| Affichage timbres numériques | Modèle Timbre + endpoint | DEV 1B |

### Ce que DEV 2A attend en priorité

```
CRITIQUE   → DEV 1C (dashboard enrichi) : graphiques incomplets sans ça
IMPORTANT  → DEV 1B (PDF) : bouton générer PDF
SECONDAIRE → DEV 1C (export CSV) : confort utilisateur admin
```

---

## DEV 2B — (React Frontend Citoyen)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Landing page publique | Pur frontend |
| Architecture React + Routing citoyen | Pur frontend |
| Intercepteur Axios (JWT) | Même pattern que DEV 2A |
| Page Login citoyen (`POST /api/auth/login/`) | Disponible ✅ |
| Page Inscription (`POST /api/auth/register/`) | Disponible ✅ |
| Page "Mes dossiers" (`GET /api/dossiers/`) | Disponible ✅ |
| Page détail dossier + suivi statut | Disponible ✅ |
| Upload de documents (`POST /api/documents/upload/`) | Disponible ✅ |
| Vérification publique QR Code (`GET /api/qr/verify/{ref}/`) | Disponible ✅ |
| Composant `DocumentUpload` (drag&drop, prévisualisation, progression) | Pur frontend |
| Timeline de progression du dossier (UI) | Les statuts sont définis ✅ |

### 🟡 Bloqué partiellement — attend ces livraisons

| Tâche bloquée | Attend | Développeur |
|---------------|--------|-------------|
| Page inscription avec OTP | Endpoint `/api/auth/otp/send/` et `/verify/` | DEV 1A |
| Login par numéro de téléphone | Adaptation du serializer login | DEV 1A |
| Bouton "Télécharger mon acte" | Endpoint génération PDF | DEV 1B |
| Formulaire "demande pour quelqu'un d'autre" | Endpoint `/api/dossiers/verify-register/` | DEV 1A |
| Pré-remplissage auto via OCR | Endpoint `/api/ai/ocr/confirm/` | DEV 1D |
| Interface chat Ndiogoye | `POST /api/ai/ndiogoye/chat/` | DEV 1A + DEV 1D |

### Ce que DEV 2B peut faire en attendant les livraisons bloquantes

> Construire **le formulaire OTP en UI** (champ 6 chiffres, minuterie 60s) sans le brancher — il suffira de connecter l'endpoint quand DEV 1A livre.
> Construire **l'interface chat Ndiogoye en UI** avec des réponses mockées — il suffira de remplacer le mock par l'appel API.

---

## DEV 3 — Flutter (Auth + Onboarding)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Onboarding (3 slides) + SharedPreferences | Pur Flutter, aucune API |
| SplashScreen + logique de redirection (token en SecureStorage) | Architecture locale |
| Écran Login (UI + appel `POST /api/auth/login/`) | Auth API disponible ✅ |
| Écran Register (UI + appel `POST /api/auth/register/`) | Auth API disponible ✅ |
| Page d'accueil (résumé des dossiers actifs) | `GET /api/dossiers/` disponible ✅ |
| Intercepteur Dio (JWT inject + refresh auto) | Auth API disponible ✅ |
| Gestion du token `flutter_secure_storage` | Pur Flutter |

### 🟡 Bloqué partiellement — attend ces livraisons

| Tâche bloquée | Attend | Développeur |
|---------------|--------|-------------|
| Écran OTP (saisie + renvoi + validation) | Endpoints OTP | DEV 1A |
| Login par numéro de téléphone | Adaptation backend login | DEV 1A |

### Ce que DEV 3 livre aux autres

| Livraison | Débloque |
|-----------|----------|
| Auth Flow Flutter complet (Login/Register/OTP/Token) | DEV 4 peut démarrer en s'appuyant sur le module auth |

---

## DEV 4 — Flutter (Dossiers + Ndiogoye)

### 🟢 Peut faire MAINTENANT sans attendre personne

| Tâche | Raison |
|-------|--------|
| Liste des dossiers (`GET /api/dossiers/`) avec pull-to-refresh | API disponible ✅ |
| Détail dossier (timeline, statut, dates) | API disponible ✅ |
| Upload de documents depuis le mobile (`image_picker` + `POST /api/documents/upload/`) | API disponible ✅ |
| Stepper "Nouvelle demande" (étapes 1 à 3, UI) | Formulaires définis dans le CDC |
| Interface Chat Ndiogoye (UI avec réponses mockées) | Peut mocker en attendant l'API IA |
| Configuration Firebase Messaging (token FCM + envoi vers `/api/notifications/register-device/`) | API disponible ✅ |

### 🟡 Bloqué partiellement — attend ces livraisons

| Tâche bloquée | Attend | Développeur |
|---------------|--------|-------------|
| Auth flow complet (Login/Register/OTP) | Module Auth Flutter | DEV 3 |
| Bouton "Télécharger mon acte" (PDF) | Endpoint génération PDF | DEV 1B |
| Pré-remplissage formulaire via scan CNI | Endpoint OCR structuré | DEV 1D |
| Chat Ndiogoye branché sur l'API réelle | `POST /api/ai/ndiogoye/chat/` | DEV 1A + DEV 1D |

### Conseil pratique pour DEV 4

> ⚡ **Ne pas attendre DEV 3 pour tout** : DEV 4 peut builder les screens Dossiers/Ndiogoye avec un `userId` hardcodé ou un mock d'auth en local. Dès que DEV 3 livre le module auth, il suffira de le plugger.

---

## Tableau de criticité globale

| Développeur | Bloque | Critique pour la démo |
|-------------|--------|----------------------|
| **DEV 1A** | DEV 3, DEV 2B, DEV 4 (OTP), DEV 1D (Ndiogoye) | ⚠️ OUI — OTP requis pour la démo inscription |
| **DEV 1B** | DEV 2A, DEV 2B, DEV 4 (PDF final) | ⚠️ OUI — Le jury veut voir un acte généré |
| **DEV 1C** | DEV 2A (graphiques enrichis) | 🟡 MOYEN — Dashboard de base fonctionne déjà |
| **DEV 1D** | DEV 2B, DEV 4 (OCR auto-fill + Ndiogoye) | ⚠️ OUI — L'IA est un argument de vente pour le jury |
| **DEV 3**  | DEV 4 (module auth Flutter) | 🟡 MOYEN — DEV 4 peut mocker en attendant |
| **DEV 2A** | Personne | 🟢 NON — Consommateur final |
| **DEV 2B** | Personne | 🟢 NON — Consommateur final |
| **DEV 4**  | Personne | 🟢 NON — Consommateur final |

---

## Ordre de livraison recommandé pour la démo

```
SPRINT IMMÉDIAT (J+0 → J+1)
├── DEV 1A  : OTP + Login téléphone + Throttling
├── DEV 1B  : Générateur PDF (au moins l'acte de naissance)
├── DEV 1C  : Notifications async + Dashboard enrichi
├── DEV 1D  : OCR structuré (extraction CNI)
├── DEV 2A  : Auth + Liste dossiers + Cards KPI
├── DEV 2B  : Auth + Formulaires + Upload
├── DEV 3   : Onboarding + Login + Register
└── DEV 4   : Liste dossiers + Upload + Chat UI mock

SPRINT DÉMO (J+2 → J+3)
├── DEV 1A + DEV 1D : Ndiogoye IA conversationnel
├── DEV 1B  : Signature officier + Timbre cryptographique
├── DEV 2A  : Graphiques enrichis + Génération PDF
├── DEV 2B  : OTP + Ndiogoye branché + Télécharger acte
├── DEV 3   : OTP Flutter + Polissage UX
└── DEV 4   : Ndiogoye branché + Télécharger PDF + Notifications push
```

---

*Dernière mise à jour : 2026-06-07 — Architecte DEV 1A (Lansana Coly)*
