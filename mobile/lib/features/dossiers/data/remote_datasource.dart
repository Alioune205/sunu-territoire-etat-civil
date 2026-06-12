import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/mock/mock_config.dart';
import '../../../core/mock/mock_service.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:dio/dio.dart';
import 'downloader.dart';
import 'models/dossier_model.dart';

class DossiersRemoteDatasource {
  final DioClient client;
  const DossiersRemoteDatasource({required this.client});

  Future<List<DossierModel>> getDossiers() async {
    final res = await client.get('/dossiers/');
    if (res.statusCode == 200 && res.data != null) {
      final responseData = res.data as Map<String, dynamic>;
      List<dynamic> list = [];
      if (responseData.containsKey('data')) {
        final data = responseData['data'];
        if (data is Map && data.containsKey('results')) {
          list = data['results'] as List;
        } else if (data is List) {
          list = data;
        }
      } else if (responseData.containsKey('results')) {
        list = responseData['results'] as List;
      }
      return list
          .map((e) => DossierModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw const ApiException(message: 'Impossible de charger les dossiers');
  }

  Future<DossierModel> getDossierById(String id) async {
    final res = await client.get('/dossiers/$id/');
    if (res.statusCode == 200 && res.data != null) {
      final responseData = res.data as Map<String, dynamic>;
      final dossierData = responseData.containsKey('data') 
          ? responseData['data'] as Map<String, dynamic> 
          : responseData;
      return DossierModel.fromJson(dossierData);
    }
    throw const NotFoundException();
  }

  Future<String> submitCertificate(Map<String, dynamic> payload) async {
    final res = await client.post('/dossiers/', data: payload);
    if ((res.statusCode == 200 || res.statusCode == 201) && res.data != null) {
      final responseData = res.data as Map<String, dynamic>;
      final dossierData = responseData.containsKey('data') 
          ? responseData['data'] as Map<String, dynamic> 
          : responseData;
      return dossierData['id'] as String? ?? '';
    }
    throw const ApiException(message: 'Échec de la soumission du dossier');
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
    
    if (kIsWeb) {
      // Web : Fetch using Dio (so we include our auth tokens) and trigger download
      debugPrint('[DOWNLOAD] Fetching PDF data for web download');
      final response = await client.dio.get(
        '/dossiers/$dossierId/download-pdf/',
        options: Options(responseType: ResponseType.bytes),
        onReceiveProgress: onProgress,
      );
      final bytes = response.data as List<int>;
      downloadWeb(bytes, 'certificat_$dossierId.pdf');
      return 'Téléchargement réussi';
    } else {
      final dir = await getApplicationDocumentsDirectory();
      final savePath = '${dir.path}/certificat_$dossierId.pdf';
      debugPrint('[DOWNLOAD] Téléchargement vers $savePath');
      await client.download(
        '/dossiers/$dossierId/download-pdf/',
        savePath,
        onReceiveProgress: onProgress,
      );
      return savePath;
    }
  }
}
