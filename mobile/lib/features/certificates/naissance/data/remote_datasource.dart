import 'package:dio/dio.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/errors/exceptions.dart';

class NaissanceRemoteDatasource {
  final DioClient client;
  const NaissanceRemoteDatasource({required this.client});

  /// Envoie l'image de l'extrait au backend pour extraction OCR.
  /// Retourne les données extraites : nom, registre, date, commune...
  /// TODO prod : utiliser MultipartFile pour envoyer la vraie image
  Future<Map<String, dynamic>> extractOcr(String imagePath) async {
    try {
      // En production, envoyer l'image en multipart :
      // final formData = FormData.fromMap({
      //   'image': await MultipartFile.fromFile(imagePath, filename: 'extrait.jpg'),
      // });
      // final res = await client.post('/ai/ocr/extract/', data: formData);

      // En mode mock : simple POST sans fichier
      final res = await client.post('/ai/ocr/extract/', data: {
        'image_path': imagePath,
      });

      if (res.statusCode == 200 && res.data != null) {
        final data = res.data as Map<String, dynamic>;
        if (data['success'] == true) {
          return data['data'] as Map<String, dynamic>;
        }
      }
      throw const ApiException(message: 'Extraction OCR échouée');
    } on DioException {
      throw const ApiException(message: 'Erreur lors de l\'extraction OCR');
    }
  }
}
