import '../repository.dart';

class ResendOtpUsecase {
  final AuthRepository repository;
  const ResendOtpUsecase(this.repository);

  Future<void> call({required String identifier}) =>
      repository.resendOtp(identifier: identifier);
}
