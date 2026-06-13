import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../../core/network/dio_client.dart';
import '../../../../dossiers/data/remote_datasource.dart';

class NaissanceState {
  final bool isLoading;
  final String? error;
  final String? dossierId;

  const NaissanceState({
    this.isLoading = false,
    this.error,
    this.dossierId,
  });

  NaissanceState copyWith({
    bool? isLoading, String? error, String? dossierId, bool clearError = false,
  }) => NaissanceState(
        isLoading: isLoading ?? this.isLoading,
        error: clearError ? null : error ?? this.error,
        dossierId: dossierId ?? this.dossierId,
      );
}

class NaissanceNotifier extends StateNotifier<NaissanceState> {
  final DossiersRemoteDatasource _ds;
  NaissanceNotifier(this._ds) : super(const NaissanceState());

  Future<String> submit({
    required String communeId,
    required String nom,
    required DateTime dateNaissance,
    required String registre,
    bool forSelf = false,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final id = await _ds.submitCertificate({
        'type': 'birth_certificate',
        'commune': communeId,
        'metadata': {
          'nom': nom,
          'date_naissance': dateNaissance.toIso8601String().split('T').first,
          'registre': registre,
        },
        'is_for_third_party': !forSelf,
      });
      state = state.copyWith(isLoading: false, dossierId: id);
      return id;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }
}

final naissanceProvider =
    StateNotifierProvider<NaissanceNotifier, NaissanceState>((ref) =>
        NaissanceNotifier(
            DossiersRemoteDatasource(client: ref.read(dioClientProvider))));
