import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/errors/exceptions.dart';
import 'models/auth_response_model.dart';

class AuthRemoteDatasource {
  final DioClient client;
  const AuthRemoteDatasource({required this.client});

  Future<LoginResponseModel> login({
    required String identifier,
    required String password,
  }) async {
    Response? res;
    try {
      res = await client.post('/auth/login', data: {
        'identifier': identifier,
        'password': password,
      });
      if (res.statusCode == 401) throw const InvalidCredentialsException();
      if (res.statusCode == 200 && res.data != null) {
        return LoginResponseModel.fromJson(res.data as Map<String, dynamic>);
      }
      throw ApiException(
          message: 'Réponse invalide', statusCode: res.statusCode);
    } on DioException catch (e) {
      if (e.error is UnauthorizedException || res?.statusCode == 401) {
        throw const InvalidCredentialsException();
      }
      rethrow;
    }
  }

  Future<void> register({
    required String prenom,
    required String nom,
    required String password,
    String? phone,
    String? email,
  }) async {
    final res = await client.post('/auth/register', data: {
      'prenom': prenom,
      'nom': nom,
      'password': password,
      if (phone != null) 'phone': phone,
      if (email != null) 'email': email,
    });
    if (res.statusCode != 200 && res.statusCode != 201) {
      final data = res.data;
      final msg = data is Map<String, dynamic>
          ? data['message'] as String? ?? 'Erreur inscription'
          : 'Erreur inscription';
      throw ApiException(message: msg, statusCode: res.statusCode);
    }
  }

  Future<String> verifyOtp({
    required String identifier,
    required String code,
  }) async {
    final res = await client.post('/auth/verify-otp', data: {
      'identifier': identifier,
      'code': code,
    });
    if (res.statusCode == 200 && res.data != null) {
      return (res.data as Map<String, dynamic>)['token'] as String? ?? '';
    }
    throw const InvalidOtpException();
  }

  Future<void> resendOtp({required String identifier}) async {
    await client.post('/auth/resend-otp', data: {'identifier': identifier});
  }

  Future<UserResponseModel> getMe() async {
    final res = await client.get('/auth/me');
    if (res.statusCode == 200 && res.data != null) {
      return UserResponseModel.fromJson(res.data as Map<String, dynamic>);
    }
    throw const UnauthorizedException();
  }
}
