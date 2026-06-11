import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../../core/network/dio_client.dart';
import '../../../../dossiers/data/remote_datasource.dart';

class DecesState {
  final bool isLoading;
  final String? error;
  final String? dossierId;
  const DecesState({this.isLoading = false, this.error, this.dossierId});
  DecesState copyWith({bool? isLoading, String? error, String? dossierId,
      bool clearError = false}) =>
      DecesState(
        isLoading: isLoading ?? this.isLoading,
        error: clearError ? null : error ?? this.error,
        dossierId: dossierId ?? this.dossierId,
      );
}

class DecesNotifier extends StateNotifier<DecesState> {
  final DossiersRemoteDatasource _ds;
  DecesNotifier(this._ds) : super(const DecesState());

  Future<String> submit({
    required String communeId,
    required String nomDefunt,
    required String registre,
    required DateTime dateDeces,
    String nomDeclarant = '',
    String lienParente = '',
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final id = await _ds.submitCertificate({
        'type': 'death_certificate',
        'commune': communeId,
        'is_for_third_party': true,
        'third_party_relation': lienParente,
        'metadata': {
          'nom_defunt': nomDefunt,
          'registre': registre,
          'date_deces': dateDeces.toIso8601String().split('T').first,
          'nom_declarant': nomDeclarant,
          'lien_parente': lienParente,
        },
      });
      state = state.copyWith(isLoading: false, dossierId: id);
      return id;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }
}

final decesProvider =
    StateNotifierProvider<DecesNotifier, DecesState>((ref) =>
        DecesNotifier(
            DossiersRemoteDatasource(client: ref.read(dioClientProvider))));
