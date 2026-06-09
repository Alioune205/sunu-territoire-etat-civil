import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../../core/network/dio_client.dart';
import '../../../../dossiers/data/remote_datasource.dart';

class MariageState {
  final bool isLoading;
  final String? error;
  final String? dossierId;
  const MariageState({this.isLoading = false, this.error, this.dossierId});
  MariageState copyWith({bool? isLoading, String? error, String? dossierId,
      bool clearError = false}) =>
      MariageState(
        isLoading: isLoading ?? this.isLoading,
        error: clearError ? null : error ?? this.error,
        dossierId: dossierId ?? this.dossierId,
      );
}

class MariageNotifier extends StateNotifier<MariageState> {
  final DossiersRemoteDatasource _ds;
  MariageNotifier(this._ds) : super(const MariageState());

  Future<String> submit({
    required String communeId,
    required String registreMarriage,
    required int anneeMarriage,
    required String nomEpoux,
    required String nomEpouse,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final id = await _ds.submitCertificate({
        'type': 'mariage',
        'commune_id': communeId,
        'beneficiary': {
          'registre_marriage': registreMarriage,
          'annee_marriage': anneeMarriage,
          'nom_epoux': nomEpoux,
          'nom_epouse': nomEpouse,
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

final mariageProvider =
    StateNotifierProvider<MariageNotifier, MariageState>((ref) =>
        MariageNotifier(
            DossiersRemoteDatasource(client: ref.read(dioClientProvider))));
