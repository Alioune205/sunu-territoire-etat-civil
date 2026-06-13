import 'package:flutter_riverpod/flutter_riverpod.dart';

class Draft {
  final String id;
  final String documentId;
  final String documentName;
  final Map<String, dynamic> formData;
  final DateTime updatedAt;

  Draft({
    required this.id,
    required this.documentId,
    required this.documentName,
    required this.formData,
    required this.updatedAt,
  });

  Draft copyWith({
    String? id,
    String? documentId,
    String? documentName,
    Map<String, dynamic>? formData,
    DateTime? updatedAt,
  }) {
    return Draft(
      id: id ?? this.id,
      documentId: documentId ?? this.documentId,
      documentName: documentName ?? this.documentName,
      formData: formData ?? this.formData,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class DraftsNotifier extends StateNotifier<List<Draft>> {
  DraftsNotifier() : super([]);

  void saveDraft(String documentId, String documentName, Map<String, dynamic> formData) {
    // Si toutes les données sont vides, on ne sauvegarde pas
    bool isEmpty = formData.values.every((v) => v == null || v.toString().trim().isEmpty);
    if (isEmpty) return;

    final existingIndex = state.indexWhere((d) => d.documentId == documentId);
    if (existingIndex >= 0) {
      final updated = [...state];
      updated[existingIndex] = updated[existingIndex].copyWith(
        formData: formData,
        updatedAt: DateTime.now(),
      );
      state = updated;
    } else {
      state = [
        ...state,
        Draft(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          documentId: documentId,
          documentName: documentName,
          formData: formData,
          updatedAt: DateTime.now(),
        )
      ];
    }
  }

  void removeDraft(String documentId) {
    state = state.where((d) => d.documentId != documentId).toList();
  }

  Draft? getDraft(String documentId) {
    try {
      return state.firstWhere((d) => d.documentId == documentId);
    } catch (_) {
      return null;
    }
  }
}

final draftsProvider = StateNotifierProvider<DraftsNotifier, List<Draft>>((ref) {
  return DraftsNotifier();
});
