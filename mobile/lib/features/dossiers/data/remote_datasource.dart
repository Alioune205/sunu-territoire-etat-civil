import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/mock/mock_config.dart';
import '../../../core/mock/mock_service.dart';
import 'models/dossier_model.dart';

class DossiersRemoteDatasource {
  final DioClient client;
  const DossiersRemoteDatasource({required this.client});

  Future<List<DossierModel>> getDossiers() async {
    final res = await client.get('/dossiers/');
    if (res.statusCode == 200 && res.data != null) {
      final list = res.data as List;
      return list
          .map((e) => DossierModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw const ApiException(message: 'Impossible de charger les dossiers');
  }

  Future<DossierModel> getDossierById(String id) async {
    final res = await client.get('/dossiers/$id/');
    if (res.statusCode == 200 && res.data != null) {
      return DossierModel.fromJson(res.data as Map<String, dynamic>);
    }
    throw const NotFoundException();
  }

  Future<String> submitCertificate(Map<String, dynamic> payload) async {
    final res = await client.post('/dossiers/', data: payload);
    if ((res.statusCode == 200 || res.statusCode == 201) && res.data != null) {
      final responseData = res.data as Map<String, dynamic>;
      if (responseData.containsKey('data') && responseData['data'] is Map) {
        return responseData['data']['id'] as String;
      }
      return responseData['id'] as String;
    }
    throw ApiException(
        message: 'Erreur lors de la soumission', statusCode: res.statusCode);
  }

  /// Télécharge le certificat PDF pour un dossier.
  /// Retourne le chemin local du fichier sauvegardé.
  Future<String> downloadCertificate(
    String dossierId, {
    void Function(int received, int total)? onProgress,
  }) async {
    if (kMockMode) {
      // Simulation en mode mock
      return MockService.downloadCertificate(dossierId);
    }
    final dir = await getApplicationDocumentsDirectory();
    final savePath = '${dir.path}/certificat_$dossierId.pdf';
    debugPrint('[DOWNLOAD] Téléchargement vers $savePath');
    await client.download(
      '/dossiers/$dossierId/download_pdf/',
      savePath,
      onReceiveProgress: onProgress,
    );
    return savePath;
  }
}
