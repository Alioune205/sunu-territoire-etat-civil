class NetworkException implements Exception {
  final String message;
  const NetworkException([this.message = 'Pas de connexion internet.']);
  @override String toString() => message;
}

class TimeoutException implements Exception {
  final String message;
  const TimeoutException([this.message = 'La requête a expiré.']);
  @override String toString() => message;
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? errorCode;
  const ApiException({required this.message, this.statusCode, this.errorCode});
  @override String toString() => message;
}

class UnauthorizedException implements Exception {
  final String message;
  const UnauthorizedException([this.message = 'Non autorisé.']);
  @override String toString() => message;
}

class ForbiddenException implements Exception {
  final String message;
  const ForbiddenException([this.message = 'Accès refusé.']);
  @override String toString() => message;
}

class NotFoundException implements Exception {
  final String message;
  const NotFoundException([this.message = 'Ressource introuvable.']);
  @override String toString() => message;
}

class ServerException implements Exception {
  final String message;
  const ServerException([this.message = 'Erreur serveur.']);
  @override String toString() => message;
}

class InvalidCredentialsException implements Exception {
  final String message;
  const InvalidCredentialsException([this.message = 'Identifiants incorrects.']);
  @override String toString() => message;
}

class InvalidOtpException implements Exception {
  final String message;
  const InvalidOtpException([this.message = 'Code OTP invalide.']);
  @override String toString() => message;
}

class PhoneAlreadyExistsException implements Exception {
  final String message;
  const PhoneAlreadyExistsException([this.message = 'Numéro déjà enregistré.']);
  @override String toString() => message;
}

class TooManyAttemptsException implements Exception {
  final String message;
  const TooManyAttemptsException([this.message = 'Trop de tentatives.']);
  @override String toString() => message;
}

class CacheException implements Exception {
  final String message;
  const CacheException([this.message = 'Erreur de cache local.']);
  @override String toString() => message;
}

class FileSizeExceededException implements Exception {
  final String message;
  const FileSizeExceededException([this.message = 'Fichier trop volumineux.']);
  @override String toString() => message;
}

class PaymentException implements Exception {
  final String message;
  const PaymentException([this.message = 'Erreur de paiement.']);
  @override String toString() => message;
}

class UnexpectedException implements Exception {
  final String message;
  const UnexpectedException([this.message = 'Erreur inattendue.']);
  @override String toString() => message;
}
