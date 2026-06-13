import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Provider pour simuler le téléversement de la CNI
final cniUploadedProvider = StateProvider<bool>((ref) => false);

/// Provider pour simuler les informations personnelles de l'utilisateur
final personalInfoProvider = StateProvider<Map<String, dynamic>>((ref) {
  return {
    'nom': 'Fall',
    'prenom': 'Pathé',
    'phone': '+221 771234567',
    'nin': '1234567890123', // Utilisé uniquement si CNI est uploadée
    'region': null,
    'commune': null,
  };
});
