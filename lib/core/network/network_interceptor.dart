import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';
import '../errors/exceptions.dart';

/// Intercepteur réseau TERANGA CIVIL.
/// Responsabilités :
///   1. Injecter le JWT Bearer dans chaque requête
///   2. Détecter les 401 et nettoyer la session
///   3. Mapper les erreurs HTTP en exceptions typées
///   4. Détecter l'absence de réseau
class NetworkInterceptor extends Interceptor {
  final FlutterSecureStorage storage;
  final Dio dio;

  NetworkInterceptor({required this.storage, required this.dio});

  // ── 1. Requête sortante — injecter le token ───────────────
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    try {
      final token = await storage.read(key: AppConstants.keyAuthToken);
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    } catch (e) {
      debugPrint('[NetworkInterceptor] Erreur lecture token: $e');
    }
    handler.next(options);
  }

  // ── 2. Réponse reçue — mapper les erreurs HTTP ────────────
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final status = response.statusCode ?? 0;

    // 401 : session expirée → nettoyer et forcer reconnexion
    if (status == 401) {
      _clearSession();
      handler.reject(
        DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: const UnauthorizedException(),
        ),
        true,
      );
      return;
    }

    // 403 : accès refusé
    if (status == 403) {
      handler.reject(
        DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: const ForbiddenException(),
        ),
        true,
      );
      return;
    }

    // 404 : ressource introuvable
    if (status == 404) {
      handler.reject(
        DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: const NotFoundException(),
        ),
        true,
      );
      return;
    }

    // 4xx autres : erreur métier avec message du backend
    if (status >= 400 && status < 500) {
      final data = response.data;
      final message = _extractMessage(data) ?? 'Erreur de requête.';
      final code = _extractCode(data);
      handler.reject(
        DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: ApiException(
            message: message,
            statusCode: status,
            errorCode: code,
          ),
        ),
        true,
      );
      return;
    }

    handler.next(response);
  }

  // ── 3. Erreur réseau ─────────────────────────────────────
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            type: err.type,
            error: const TimeoutException(),
          ),
        );
        return;

      case DioExceptionType.connectionError:
        handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            type: err.type,
            error: const NetworkException(),
          ),
        );
        return;

      case DioExceptionType.badResponse:
        // Déjà traité dans onResponse si status < 500
        // Ici : 5xx serveur
        if (err.response?.statusCode != null &&
            err.response!.statusCode! >= 500) {
          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              response: err.response,
              type: err.type,
              error: const ServerException(),
            ),
          );
          return;
        }
        handler.next(err);
        return;

      default:
        handler.next(err);
    }
  }

  // ── Utilitaires privés ────────────────────────────────────

  Future<void> _clearSession() async {
    try {
      await storage.delete(key: AppConstants.keyAuthToken);
      await storage.write(
        key: AppConstants.keyHasBeenLoggedOut,
        value: 'true',
      );
    } catch (e) {
      debugPrint('[NetworkInterceptor] Erreur nettoyage session: $e');
    }
  }

  String? _extractMessage(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data['message'] as String? ??
          data['error'] as String? ??
          data['detail'] as String?;
    }
    return null;
  }

  String? _extractCode(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data['code'] as String? ?? data['error_code'] as String?;
    }
    return null;
  }
}
