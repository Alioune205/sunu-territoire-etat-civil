# SUNU CIVIL - Plateforme GovTech (MVP Sénégal)

Ce dépôt contient le code source de **SUNU CIVIL**, une plateforme GovTech moderne destinée aux collectivités territoriales du Sénégal pour digitaliser et moderniser l'état civil et les démarches administratives.

---

## 🏗️ Structure Globale du Projet

```text
Hackathon/
├── backend/            # API REST Django (Cœur du Système)
├── frontend_react/     # Dashboard Administratif (React) - À venir
└── mobile_flutter/     # Application Mobile (Flutter) - À venir
```

---

## 🛠️ Guide d'Installation & Lancement (Backend)

Pour installer et exécuter le backend sur votre machine locale, suivez ces étapes :

### 1. Prérequis
- **Python 3.10+** installé.
- **PostgreSQL** installé et configuré (avec une base de données créée, ex: `sunu_civil_db`).

### 2. Cloner le Projet
```bash
git clone <URL_DU_DEPOT_GITHUB>
cd Hackathon/backend
```

### 3. Configurer l'Environnement Virtuel
Sous Windows :
```powershell
python -m venv venv
venv\Scripts\activate
```
Sous macOS/Linux :
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 5. Configurer les Variables d'Environnement
1. Dupliquez le fichier `.env.example` et renommez-le en `.env`.
2. Ouvrez `.env` et mettez à jour les accès PostgreSQL locaux :
   ```env
   DB_NAME=sunu_civil_db
   DB_USER=votre_utilisateur
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=127.0.0.1
   DB_PORT=5432
   ```

### 6. Appliquer les Migrations & Charger les Données de Test (Seed)
Créez la structure de la base de données et insérez les données initiales :
```bash
python manage.py migrate
python manage.py seed_data
```

### 7. Lancer le Serveur de Développement
```bash
python manage.py runserver
```
Le serveur sera disponible sur `http://127.0.0.1:8000/`.

---

## 🤝 Workflow de Collaboration & GitHub

### Rôles de l'Équipe
* **DEV 1A (Vous/Core)** : Architecture principale, authentification, rôles, dossiers, documents, audit.
* **DEV 2 (Backend Services)** : Compléter les modules stubs (`apps/notifications`, `apps/qr`, `apps/ai`, `apps/dashboard`).
* **DEV 3 & 4 (Frontend/Mobile)** : Consommer les API.

### Comment collaborer sur Git/GitHub ?

1. **Initialiser le dépôt (à faire une seule fois par DEV 1A)** :
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit with backend core architecture"
   git branch -M main
   git remote add origin <URL_VOTRE_DEPOT_GITHUB>
   git push -u origin main
   ```

2. **Bonnes Pratiques de Collaboration** :
   - **Ne jamais travailler directement sur `main`** : Créez toujours une branche pour vos modifications.
     ```bash
     git checkout -b feat/nom-de-votre-fonctionnalite
     ```
   - **Faire des Pull Requests (PR)** sur GitHub pour fusionner vos modifications dans `main`.
   - **Mettre à jour régulièrement votre code** local avec les changements des autres :
     ```bash
     git pull origin main
     ```

---

Voici une analyse claire des dépendances entre les développeurs des différentes équipes pour la réussite du projet :

---

### 🟢 1. Les développeurs indépendants (Créateurs de fondations)

* **DEV 1A (Lansana Coly - Tech Lead Backend)** : 
  * **Statut** : **100% Indépendant**. 
  * **Pourquoi** : Vous concevez les fondations (base de données, structure des dossiers, rôles, sécurité JWT). Vous ne dépendez de personne, mais **tous les autres développeurs dépendent de vous**.

---

### 🟡 2. Les développeurs à dépendance directe (Dépendent du Core Backend)

* **DEV 1B (Pathe Fall - Dossiers & Workflow)** :
  * **Statut** : **Dépendant de DEV 1A**.
  * **Pourquoi** : Il a besoin que votre modèle d'utilisateur (`User`), les `Communes` et vos décorateurs de permissions (`RBAC`) soient opérationnels pour coder la gestion des dossiers et la logique métier de validation.

* **DEV 1D (Ibrahima Khalilou Diallo - IA & OCR)** :
  * **Statut** : **Dépendant de DEV 1A & DEV 1B**.
  * **Pourquoi** : Pour faire de l'OCR sur les documents et de la détection de doublons, il a besoin que DEV 1B ait terminé l'implémentation du stockage des documents et que DEV 1A ait finalisé les profils citoyens (pour comparer les textes extraits aux informations réelles).

---

### 🔴 3. Les développeurs à forte dépendance (En fin de chaîne)

* **DEV 1C (Maimouna Sall - Notifications & Stats)** :
  * **Statut** : **Très dépendante de DEV 1A & DEV 1B**.
  * **Pourquoi** : Elle ne peut pas envoyer de notifications Firebase d'avancement de dossier si les dossiers (DEV 1B) et l'authentification (DEV 1A) ne sont pas stables. De même, ses statistiques dépendent des données des dossiers créés par DEV 1B.

* **Équipe DEV 2 (Pape Alioune Sene & El Hadji Massogui Diop - React Dashboard)** :
  * **Statut** : **Dépends entièrement de l'équipe DEV 1**.
  * **Pourquoi** : Ils construisent le Dashboard React. Ils dépendent de DEV 1A pour la connexion (JWT), de DEV 1B pour la gestion des dossiers à afficher, et de DEV 1C pour consommer les endpoints de statistiques (`/api/dashboard/stats/`).

* **Équipe DEV 3 & DEV 4 (Flutter & Mobile)** :
  * **Statut** : **Dépends entièrement de l'équipe DEV 1**.
  * **Pourquoi** : L'application mobile dépend de l'API REST Django complète pour l'inscription, la soumission des dossiers avec pièces jointes (DEV 1B) et la réception des notifications push (DEV 1C).

---

🛠️ Ce que vos collègues doivent faire sur leur machine :
Installer PostgreSQL localement.
Créer une base de données vide nommée sunucivil.
Créer leur propre fichier .env (qui est exclu de Git) et y écrire leurs propres identifiants PostgreSQL locaux :
env
DB_NAME=sunucivil
DB_USER=leur_nom_utilisateur_postgres  # ex: postgres
DB_PASSWORD=leur_mot_de_passe_postgres # ex: admin123
DB_HOST=localhost
DB_PORT=5432
Lancer ces deux commandes dans leur terminal pour cloner la structure et avoir les données de test :
bash
python manage.py migrate
python manage.py seed_data
Grâce à la commande seed_data que nous avons rendue robuste et identique pour tout le monde, en moins de 10 secondes ils auront exactement les mêmes utilisateurs et dossiers de test que vous sur leur ordinateur !

---

## 🔗 Documentation de l'API (Swagger & Redoc)

La documentation interactive de l'API est générée automatiquement et accessible aux développeurs Frontend et Mobile lorsque le serveur backend tourne :

- **Swagger UI** : `http://127.0.0.1:8000/api/docs/`
- **ReDoc** : `http://127.0.0.1:8000/api/docs/redoc/`
- **Schéma Schema JSON** : `http://127.0.0.1:8000/api/docs/schema/`
