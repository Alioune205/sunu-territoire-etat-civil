import '../repository.dart';

class LoginUsecase {
  final AuthRepository repository;
  const LoginUsecase(this.repository);

  Future<({String token, String userId, bool needsOtp})> call({
    required String identifier,
    required String password,
  }) async {
    final result = await repository.login(
      identifier: identifier,
      password: password,
    );
    await repository.saveToken(result.token);
    await repository.saveUserId(result.userId);
    await repository.saveIdentifier(identifier);
    return result;
  }
}
