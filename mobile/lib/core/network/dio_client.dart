import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';
import '../mock/mock_config.dart';
import 'network_interceptor.dart';
import 'mock_interceptor.dart';

class AppErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    String message = 'Une erreur réseau est survenue.';
    if (err.response?.data != null && err.response?.data is Map) {
      final data = err.response!.data as Map;
      
      if (data.containsKey('errors') && data['errors'] != null) {
        final errors = data['errors'];
        if (errors is Map && errors.isNotEmpty) {
          final firstValue = errors.values.first;
          if (firstValue is List && firstValue.isNotEmpty) {
            message = firstValue.first.toString();
          } else {
            message = firstValue.toString();
          }
        } else if (errors is List && errors.isNotEmpty) {
          message = errors.first.toString();
        } else if (errors is String && errors.isNotEmpty) {
          message = errors;
        }
      } else if (data.containsKey('message') && data['message'] != null && data['message'].toString().isNotEmpty) {
        message = data['message'].toString();
      } else if (data.containsKey('detail')) {
        message = data['detail'].toString();
      } else if (data.containsKey('error')) {
        message = data['error'].toString();
      } else if (data.containsKey('non_field_errors')) {
        message = (data['non_field_errors'] as List).first.toString();
      } else if (data.isNotEmpty) {
        // Exclude the 'success' boolean key if it is the first value in the map
        final filteredKeys = data.keys.where((k) => k != 'success');
        if (filteredKeys.isNotEmpty) {
          final firstValue = data[filteredKeys.first];
          if (firstValue is List && firstValue.isNotEmpty) {
            message = firstValue.first.toString();
          } else {
            message = firstValue.toString();
          }
        }
      }
    } else if (err.type == DioExceptionType.connectionTimeout || err.type == DioExceptionType.receiveTimeout) {
      message = 'La connexion au serveur a expiré.';
    } else if (err.type == DioExceptionType.connectionError) {
      message = 'Impossible de contacter le serveur (Vérifiez que Django tourne).';
    }
    
    final newErr = err.copyWith(message: message);
    handler.next(newErr);
  }
}

final dioClientProvider = Provider<DioClient>((ref) {
  const storage = FlutterSecureStorage();
  return DioClient(storage: storage);
});

class DioClient {
  late final Dio _dio;
  final FlutterSecureStorage storage;

  DioClient({required this.storage}) {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.apiBaseUrl,
        connectTimeout: AppConstants.apiConnectTimeout,
        receiveTimeout: AppConstants.apiReceiveTimeout,
        sendTimeout: AppConstants.apiSendTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-App-Version': AppConstants.appVersion,
          'X-Platform': 'mobile',
        },
        responseType: ResponseType.json,
        validateStatus: (status) => status != null && status >= 200 && status < 300,
      ),
    );

    if (kMockMode) {
      // En mode mock : intercepteur qui retourne des données locales
      _dio.interceptors.add(MockInterceptor());
      debugPrint('[MOCK] Mode mock activé — aucun serveur requis');
    } else {
      // En mode production : vrai intercepteur JWT
      _dio.interceptors.add(NetworkInterceptor(storage: storage, dio: _dio));
    }
    // Intercepteur global d'erreurs (pour le backend Django)
    _dio.interceptors.add(AppErrorInterceptor());
  }

  Dio get dio => _dio;

  Future<Response<T>> get<T>(String path,
      {Map<String, dynamic>? queryParameters,
      Options? options,
      CancelToken? cancelToken}) =>
      _dio.get<T>(path,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken);

  Future<Response<T>> post<T>(String path,
      {dynamic data,
      Map<String, dynamic>? queryParameters,
      Options? options,
      CancelToken? cancelToken}) =>
      _dio.post<T>(path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken);

  Future<Response<T>> put<T>(String path,
      {dynamic data,
      Map<String, dynamic>? queryParameters,
      Options? options,
      CancelToken? cancelToken}) =>
      _dio.put<T>(path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken);

  Future<Response<T>> patch<T>(String path,
      {dynamic data,
      Map<String, dynamic>? queryParameters,
      Options? options,
      CancelToken? cancelToken}) =>
      _dio.patch<T>(path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken);

  Future<Response<T>> delete<T>(String path,
      {dynamic data,
      Options? options,
      CancelToken? cancelToken}) =>
      _dio.delete<T>(path,
          data: data,
          options: options,
          cancelToken: cancelToken);

  Future<Response> download(String path, String savePath,
      {ProgressCallback? onReceiveProgress, CancelToken? cancelToken}) =>
      _dio.download(path, savePath,
          onReceiveProgress: onReceiveProgress,
          cancelToken: cancelToken,
          options: Options(responseType: ResponseType.bytes));
}
