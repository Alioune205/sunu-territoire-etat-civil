import 'models/user_model.dart';

abstract class AuthRepository {
  /// Connexion avec téléphone ou email + mot de passe
  Future<({String token, String userId, bool needsOtp})> login({
    required String identifier, // téléphone ou email
    required String password,
  });

  /// Inscription simplifiée
  Future<void> register({
    required String prenom,
    required String nom,
    required String password,
    String? phone,
    String? email,
  });

  /// Validation OTP (SMS ou email)
  Future<String> verifyOtp({
    required String identifier,
    required String code,
  });

  Future<void> resendOtp({required String identifier});

  Future<UserModel> getMe();

  // Stockage local
  Future<void> saveToken(String token);
  Future<void> saveUserId(String userId);
  Future<void> saveIdentifier(String identifier);
  Future<void> setLoggedOut(bool value);
  Future<String?> getToken();
  Future<String?> getSavedIdentifier();
  Future<bool> hasBeenLoggedOut();
  Future<void> logout();
}
