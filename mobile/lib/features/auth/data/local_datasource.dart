import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants/app_constants.dart';

class AuthLocalDatasource {
  final FlutterSecureStorage secureStorage;
  const AuthLocalDatasource({required this.secureStorage});

  Future<void> saveToken(String token) async {
    await secureStorage.write(key: AppConstants.keyAuthToken, value: token);
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.keyAuthToken, token);
    }
  }

  Future<void> saveUserId(String userId) async {
    await secureStorage.write(key: AppConstants.keyUserId, value: userId);
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.keyUserId, userId);
    }
  }

  Future<void> saveIdentifier(String identifier) async {
    await secureStorage.write(key: AppConstants.keyUserPhone, value: identifier);
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.keyUserPhone, identifier);
    }
  }

  Future<void> setLoggedOut(bool value) async {
    await secureStorage.write(
      key: AppConstants.keyHasBeenLoggedOut,
      value: value.toString(),
    );
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(AppConstants.keyHasBeenLoggedOut, value);
    }
  }

  Future<String?> getToken() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(AppConstants.keyAuthToken);
    }
    return secureStorage.read(key: AppConstants.keyAuthToken);
  }

  Future<String?> getSavedIdentifier() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(AppConstants.keyUserPhone);
    }
    return secureStorage.read(key: AppConstants.keyUserPhone);
  }

  Future<bool> hasBeenLoggedOut() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getBool(AppConstants.keyHasBeenLoggedOut) ?? false;
    }
    final val =
        await secureStorage.read(key: AppConstants.keyHasBeenLoggedOut);
    return val == 'true';
  }

  Future<void> clearAll() async {
    await secureStorage.deleteAll();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.prefUserProfile);
    if (kIsWeb) {
      await prefs.remove(AppConstants.keyAuthToken);
      await prefs.remove(AppConstants.keyUserId);
      await prefs.remove(AppConstants.keyUserPhone);
      await prefs.remove(AppConstants.keyHasBeenLoggedOut);
    }
  }
}
