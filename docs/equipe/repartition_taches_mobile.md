# Répartition des Tâches : Équipe Mobile Flutter (Certificats Résidence & Décès)

L'équipe Mobile (composée de 3 développeurs) est chargée d'intégrer les nouveaux formulaires de demandes depuis l'application citoyen. Les défis majeurs résident dans la gestion des uploads de fichiers (pièces justificatives) et la logique conditionnelle.

## 📱 DEV MOBILE 1
**Rôle** : Lead UI / UX & Formulaires
- **Tâche 1** : Créer l'écran `residence_form_screen.dart`. Y intégrer les champs requis et les boutons d'ajout pour : Pièce d'identité, Attestation délégué de quartier, et Copie CNI. Ajouter une note d'information visible : *"Ce certificat aura une validité de 3 mois"*.
- **Tâche 2** : Créer l'écran `deces_form_screen.dart` (Permis d'inhumation).
- **Tâche 3** : Implémenter la logique réactive de l'interface : Si l'utilisateur coche la case "Décès intervenu à domicile", faire apparaître dynamiquement deux nouveaux champs de téléversement obligatoires pour les CNIs de "Témoin 1" et "Témoin 2".

## 📱 DEV MOBILE 2
**Rôle** : Lead API, Riverpod & Uploads Multi-part
- **Tâche 4** : Créer et configurer les providers (`residence_provider.dart`, `deces_provider.dart`).
- **Tâche 5** : Gérer la soumission des données à l'API Django. Comme il y a des fichiers (images/PDFs), implémenter la logique d'envoi en `Multipart/form-data` via le client Dio.
- **Tâche 6** : Gérer la réception des erreurs spécifiques du backend (ex: Afficher une modale "Erreur : Le délai d'un an est dépassé" si le backend renvoie un code 400 pour la date de décès).

## 📱 DEV MOBILE 3
**Rôle** : Intégration Native & Optimisation Fichiers
- **Tâche 7** : Développer le module de capture de documents. Intégrer les plugins `image_picker` ou `file_picker` pour permettre au citoyen de scanner ses pièces avec l'appareil photo ou la galerie.
- **Tâche 8** : Implémenter un système de compression d'images côté client avant envoi. Les scans de CNIs ou d'attestations ne doivent pas dépasser un certain poids (ex: 2 Mo maximum par fichier) pour éviter de saturer la bande passante et le serveur.
- **Tâche 9** : Gérer les permissions natives (demande d'accès à la caméra et au stockage sur iOS et Android).
