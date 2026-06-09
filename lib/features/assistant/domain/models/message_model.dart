/// Modèle d'un message dans la conversation avec l'assistant IA
class MessageModel {
  final String id;
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final String language; // 'fr' ou 'wo'

  const MessageModel({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.language = 'fr',
  });

  factory MessageModel.user(String content, {String language = 'fr'}) =>
      MessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: content,
        isUser: true,
        timestamp: DateTime.now(),
        language: language,
      );

  factory MessageModel.assistant(String content, {String language = 'fr'}) =>
      MessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: content,
        isUser: false,
        timestamp: DateTime.now(),
        language: language,
      );
}
