import '../repository.dart';

class RegisterUsecase {
  final AuthRepository repository;
  const RegisterUsecase(this.repository);

  Future<void> call({
    required String prenom,
    required String nom,
    required String password,
    String? phone,
    String? email,
  }) =>
      repository.register(
        prenom: prenom,
        nom: nom,
        password: password,
        phone: phone,
        email: email,
      );
}
