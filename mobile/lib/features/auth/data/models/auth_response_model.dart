import '../../domain/models/user_model.dart';

class LoginResponseModel {
  final String token;
  final String userId;
  final bool needsOtp;

  const LoginResponseModel({
    required this.token,
    required this.userId,
    required this.needsOtp,
  });

  factory LoginResponseModel.fromJson(Map<String, dynamic> json) {
    if (json.containsKey('data') && json['data'] is Map<String, dynamic>) {
      final data = json['data'] as Map<String, dynamic>;
      final user = data['user'] as Map<String, dynamic>?;
      return LoginResponseModel(
        token: data['access'] as String? ?? data['token'] as String? ?? '',
        userId: user != null ? user['id'] as String? ?? '' : data['user_id'] as String? ?? '',
        needsOtp: data['needs_otp'] as bool? ?? false,
      );
    }
    return LoginResponseModel(
      token: json['token'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      needsOtp: json['needs_otp'] as bool? ?? false,
    );
  }
}

class UserResponseModel {
  final String id;
  final String prenom;
  final String nom;
  final String? phone;
  final String? email;
  final bool isVerified;
  final String? communeId;
  final String? communeNom;
  final String? registre;
  final String? dateNaissance;

  const UserResponseModel({
    required this.id,
    required this.prenom,
    required this.nom,
    this.phone,
    this.email,
    this.isVerified = false,
    this.communeId,
    this.communeNom,
    this.registre,
    this.dateNaissance,
  });

  factory UserResponseModel.fromJson(Map<String, dynamic> json) {
    final Map<String, dynamic> source = (json.containsKey('data') && json['data'] is Map<String, dynamic>)
        ? json['data'] as Map<String, dynamic>
        : json;
    
    final prenom = source['prenom'] as String? ?? source['first_name'] as String? ?? '';
    final nom = source['nom'] as String? ?? source['last_name'] as String? ?? '';

    return UserResponseModel(
      id: source['id'] as String? ?? '',
      prenom: prenom,
      nom: nom,
      phone: source['phone'] as String?,
      email: source['email'] as String?,
      isVerified: source['is_verified'] as bool? ?? false,
      communeId: source['commune_id'] as String?,
      communeNom: source['commune_nom'] as String?,
      registre: source['registre'] as String?,
      dateNaissance: source['date_naissance'] as String?,
    );
  }

  UserModel toDomain() => UserModel(
        id: id,
        prenom: prenom,
        nom: nom,
        phone: phone,
        email: email,
        isVerified: isVerified,
        communeId: communeId,
        communeNom: communeNom,
        registre: registre,
        dateNaissance: dateNaissance != null
            ? DateTime.tryParse(dateNaissance!)
            : null,
      );
}
