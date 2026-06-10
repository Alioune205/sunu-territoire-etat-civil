import '../../../core/network/dio_client.dart';
import '../../../core/errors/exceptions.dart';
import '../../auth/data/models/auth_response_model.dart';

class ProfileRemoteDatasource {
  final DioClient client;
  const ProfileRemoteDatasource({required this.client});

  Future<UserResponseModel> getProfile() async {
    final res = await client.get('/users/me/');
    if (res.statusCode == 200 && res.data != null) {
      return UserResponseModel.fromJson(res.data as Map<String, dynamic>);
    }
    throw const UnauthorizedException();
  }

  Future<UserResponseModel> updateProfile(Map<String, dynamic> data) async {
    final res = await client.patch('/profiles/me/', data: data);
    if (res.statusCode == 200 && res.data != null) {
      return UserResponseModel.fromJson(res.data as Map<String, dynamic>);
    }
    throw ApiException(
        message: 'Mise à jour échouée', statusCode: res.statusCode);
  }

  Future<void> changePin({
    required String oldPinHash,
    required String newPin,
  }) async {
    final res = await client.post('/profiles/change-pin/', data: {
      'old_pin_hash': oldPinHash,
      'new_pin': newPin,
    });
    if (res.statusCode != 200) {
      throw ApiException(
          message: 'Changement de PIN échoué', statusCode: res.statusCode);
    }
  }
}
