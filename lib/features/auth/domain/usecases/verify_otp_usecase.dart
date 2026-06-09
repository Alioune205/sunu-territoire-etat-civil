import '../repository.dart';

class VerifyOtpUsecase {
  final AuthRepository repository;
  const VerifyOtpUsecase(this.repository);

  Future<void> call({
    required String identifier,
    required String code,
  }) async {
    final token = await repository.verifyOtp(
        identifier: identifier, code: code);
    await repository.saveToken(token);
  }
}
