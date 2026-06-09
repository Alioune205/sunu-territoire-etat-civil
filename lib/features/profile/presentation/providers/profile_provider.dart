import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/remote_datasource.dart';
import '../../../auth/domain/models/user_model.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

class ProfileState {
  final bool isLoading;
  final String? error;
  final bool updateSuccess;

  const ProfileState({
    this.isLoading = false,
    this.error,
    this.updateSuccess = false,
  });

  ProfileState copyWith({
    bool? isLoading,
    String? error,
    bool? updateSuccess,
    bool clearError = false,
  }) =>
      ProfileState(
        isLoading: isLoading ?? this.isLoading,
        error: clearError ? null : error ?? this.error,
        updateSuccess: updateSuccess ?? this.updateSuccess,
      );
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfileRemoteDatasource _ds;
  final Ref _ref;

  ProfileNotifier(this._ds, this._ref) : super(const ProfileState());

  Future<UserModel?> loadProfile() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final res = await _ds.getProfile();
      final user = res.toDomain();
      state = state.copyWith(isLoading: false);
      return user;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return null;
    }
  }

  Future<void> updateProfile({String? nom, String? communeId}) async {
    state = state.copyWith(isLoading: true, clearError: true, updateSuccess: false);
    try {
      final data = <String, dynamic>{
        if (nom != null) 'nom': nom,
        if (communeId != null) 'commune_id': communeId,
      };
      await _ds.updateProfile(data);
      state = state.copyWith(isLoading: false, updateSuccess: true);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }

  Future<void> changePin({
    required String oldPin,
    required String newPin,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final oldHash = sha256.convert(utf8.encode(oldPin)).toString();
      await _ds.changePin(oldPinHash: oldHash, newPin: newPin);
      state = state.copyWith(isLoading: false, updateSuccess: true);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }

  Future<void> logout() async {
    await _ref.read(authProvider.notifier).logout();
  }
}

final profileProvider =
    StateNotifierProvider<ProfileNotifier, ProfileState>((ref) =>
        ProfileNotifier(
          ProfileRemoteDatasource(client: ref.read(dioClientProvider)),
          ref,
        ));
