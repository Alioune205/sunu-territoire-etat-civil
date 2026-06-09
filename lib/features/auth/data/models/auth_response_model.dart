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

  factory LoginResponseModel.fromJson(Map<String, dynamic> json) =>
      LoginResponseModel(
        token: json['token'] as String? ?? '',
        userId: json['user_id'] as String? ?? '',
        needsOtp: json['needs_otp'] as bool? ?? false,
      );
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

  factory UserResponseModel.fromJson(Map<String, dynamic> json) =>
      UserResponseModel(
        id: json['id'] as String? ?? '',
        prenom: json['prenom'] as String? ?? '',
        nom: json['nom'] as String? ?? '',
        phone: json['phone'] as String?,
        email: json['email'] as String?,
        isVerified: json['is_verified'] as bool? ?? false,
        communeId: json['commune_id'] as String?,
        communeNom: json['commune_nom'] as String?,
        registre: json['registre'] as String?,
        dateNaissance: json['date_naissance'] as String?,
      );

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
