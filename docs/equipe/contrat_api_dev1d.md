# Guide d'Intégration API : Validations Métier (DEV 1D)

*Ce document est rédigé par Ibrahima Khalilou Diallo (DEV 1D) à l'attention de toutes les équipes interagissant avec la création et la lecture des dossiers d'état civil (Résidence, Décès, Mariage).*

---

## 📌 Architecture de l'API (Le champ `metadata`)

Pour permettre des formulaires dynamiques sans modifier la structure de la base de données à chaque nouveau type d'acte, un champ **`metadata`** (JSON) a été ajouté à l'entité `Dossier`.
C'est ce champ qui contient toutes les informations spécifiques d'un acte et les références (ID) des pièces jointes. L'API est stricte et rejettera toute requête ne respectant pas les règles ci-dessous.

---

## 📱 1. Pour l'Équipe Mobile (Flutter) & Pathé (DEV 1B - Guichet Rapide)
**Votre mission vis-à-vis de mon travail :** Formater correctement la requête de création de dossier.

Lors de l'appel à `POST /api/dossiers/`, vous devez injecter un objet `metadata` contenant **obligatoirement** les clés suivantes selon le type d'acte :

### 📄 Certificat de Résidence (`type: "residence_certificate"`)
```json
"metadata": {
  "cni_recto": "id_ou_url_du_document",
  "attestation_delegue": "id_ou_url_du_document"
}
```

### 💍 Acte de Mariage (`type: "marriage_certificate"`)
```json
"metadata": {
  "cni_epoux": "id_ou_url_du_document",
  "cni_epouse": "id_ou_url_du_document",
  "cni_temoins": "id_ou_url_du_document"
}
```

### 🕊️ Acte de Décès (`type: "death_certificate"`)
```json
"metadata": {
  "constat_medecin": "id_ou_url_du_document",
  "cni_defunt": "id_ou_url_du_document",
  "date_deces": "YYYY-MM-DD"
}
```
⚠️ **RÈGLE STRICTE (Délai de décès)** : Si la `date_deces` que vous envoyez est supérieure à 1 an (365 jours) par rapport à la date du jour, mon API vous renverra une erreur HTTP 400. **Vous devez gérer cette erreur dans votre interface et afficher un message clair au citoyen.**

---

## 👁️ 2. Pour Maimouna (DEV 1C - Viewer Documentaire)
**Ta mission vis-à-vis de mon travail :** Afficher les justificatifs à l'écran.

Lorsque tu fais un `GET /api/dossiers/{id}/` pour afficher le détail d'un dossier aux agents, tu n'as pas besoin de chercher les images dans une table complexe. 
Il te suffit d'accéder au dictionnaire `metadata`.
Exemple pour un décès : `dossier.metadata.constat_medecin` te donnera l'information nécessaire pour afficher le fichier dans ton Viewer.

---

## 🖨️ 3. Pour Pape Alioune Sene (DEV 2A - Générateur PDF)
**Ta mission vis-à-vis de mon travail :** Consommer les données validées pour dessiner tes PDF.

Je m'assure qu'aucun dossier ne passe si les données sont incomplètes. Tu n'as donc pas besoin de faire de validations complexes dans ton code de génération PDF. 
Tu peux lire en toute confiance `dossier.metadata.get('date_deces')` sachant que j'ai déjà vérifié sa validité.

🔄 **S'il te manque un champ pour le PDF** (ex: `lieu_deces` ou `nom_temoin`), **ne modifie pas la base de données**. Viens me voir (DEV 1D) et je rajouterai ce champ comme obligatoire dans mon validateur `DossierCreateSerializer`.

---

## 🧪 4. Pour El Hadji Massogui Diop (DEV 2B - Tests Unitaires QA)
**Ta mission vis-à-vis de mon travail :** Éprouver la sécurité de l'API.

Dans tes scripts de tests (TDD/QA), tu dois écrire des tests spécifiques ciblant mes validateurs :
1. Tente de soumettre un dossier de mariage sans la clé `cni_temoins`. Assure-toi que l'API renvoie bien une 400.
2. Tente de soumettre un acte de décès avec une `date_deces` d'il y a 3 ans. Assure-toi que la requête est bloquée.
3. Tente d'envoyer un format de date invalide (ex: `14-10-2025`).

Si tu trouves une faille, ouvre un ticket et je patcherai mon code dans `serializers.py`.
