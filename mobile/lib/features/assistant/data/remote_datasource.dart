import '../../../core/network/dio_client.dart';
import '../../../core/errors/exceptions.dart';

class AssistantRemoteDatasource {
  final DioClient client;
  const AssistantRemoteDatasource({required this.client});

  Future<String> sendMessage({
    required String message,
    required String language,
    List<Map<String, dynamic>>? history,
  }) async {
    final res = await client.post('/ai/ndiogoye/chat/', data: {
      'message': message,
      'language': language,
      'chat_history': history ?? [],
    });
    if ((res.statusCode == 200) && res.data != null) {
      return (res.data as Map<String, dynamic>)['reply'] as String;
    }
    throw const ApiException(message: 'Réponse invalide du serveur');
  }
}
