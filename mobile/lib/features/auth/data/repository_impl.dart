import '../../../core/errors/exceptions.dart';
import '../../../core/errors/failures.dart';
import '../domain/models/user_model.dart';
import '../domain/repository.dart';
import 'local_datasource.dart';
import 'remote_datasource.dart';
import 'package:dio/dio.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDatasource remote;
  final AuthLocalDatasource local;
  const AuthRepositoryImpl({required this.remote, required this.local});

  @override
  Future<({String token, String userId, bool needsOtp})> login({
    required String identifier,
    required String password,
  }) async {
    try {
      final res =
          await remote.login(identifier: identifier, password: password);
      return (token: res.token, userId: res.userId, needsOtp: res.needsOtp);
    } on InvalidCredentialsException {
      throw const InvalidCredentialsFailure();
    } on TooManyAttemptsException {
      throw const TooManyAttemptsFailure();
    } on NetworkException {
      throw const NetworkFailure();
    } on DioException catch (e) {
      throw ApiFailure(message: e.message ?? 'Erreur inattendue');
    } on ApiException catch (e) {
      throw ApiFailure(message: e.message);
    } catch (_) {
      throw const UnexpectedFailure();
    }
  }

  @override
  Future<void> register({
    required String prenom,
    required String nom,
    required String password,
    String? phone,
    String? email,
  }) async {
    try {
      await remote.register(
        prenom: prenom,
        nom: nom,
        password: password,
        phone: phone,
        email: email,
      );
    } on PhoneAlreadyExistsException {
      throw const PhoneAlreadyExistsFailure();
    } on NetworkException {
      throw const NetworkFailure();
    } on DioException catch (e) {
      throw ApiFailure(message: e.message ?? 'Erreur inattendue');
    } on ApiException catch (e) {
      throw ApiFailure(message: e.message);
    } catch (_) {
      throw const UnexpectedFailure();
    }
  }

  @override
  Future<String> verifyOtp({
    required String identifier,
    required String code,
  }) async {
    try {
      return await remote.verifyOtp(identifier: identifier, code: code);
    } on InvalidOtpException {
      throw const InvalidOtpFailure();
    } on NetworkException {
      throw const NetworkFailure();
    } on DioException catch (e) {
      throw ApiFailure(message: e.message ?? 'Erreur inattendue');
    } on ApiException catch (e) {
      throw ApiFailure(message: e.message);
    } catch (_) {
      throw const UnexpectedFailure();
    }
  }

  @override
  Future<void> resendOtp({required String identifier}) async {
    try {
      await remote.resendOtp(identifier: identifier);
    } on NetworkException {
      throw const NetworkFailure();
    } on DioException catch (e) {
      throw ApiFailure(message: e.message ?? 'Erreur inattendue');
    } on ApiException catch (e) {
      throw ApiFailure(message: e.message);
    } catch (_) {
      throw const UnexpectedFailure();
    }
  }

  @override
  Future<UserModel> getMe() async {
    try {
      final res = await remote.getMe();
      return res.toDomain();
    } on UnauthorizedException {
      throw const UnauthorizedFailure();
    } on DioException catch (e) {
      throw ApiFailure(message: e.message ?? 'Erreur inattendue');
    } on ApiException catch (e) {
      throw ApiFailure(message: e.message);
    } catch (_) {
      throw const UnexpectedFailure();
    }
  }

  @override Future<void> saveToken(String t) => local.saveToken(t);
  @override Future<void> saveUserId(String id) => local.saveUserId(id);
  @override Future<void> saveIdentifier(String i) => local.saveIdentifier(i);
  @override Future<void> setLoggedOut(bool v) => local.setLoggedOut(v);
  @override Future<String?> getToken() => local.getToken();
  @override Future<String?> getSavedIdentifier() => local.getSavedIdentifier();
  @override Future<bool> hasBeenLoggedOut() => local.hasBeenLoggedOut();
  @override Future<void> logout() => local.clearAll();
}
