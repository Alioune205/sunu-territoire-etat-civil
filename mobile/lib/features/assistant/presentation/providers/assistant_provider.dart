import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/remote_datasource.dart';
import '../../domain/models/message_model.dart';

class AssistantState {
  final List<MessageModel> messages;
  final bool isLoading;
  final String? error;
  final String language;

  const AssistantState({
    this.messages = const [],
    this.isLoading = false,
    this.error,
    this.language = 'fr',
  });

  AssistantState copyWith({
    List<MessageModel>? messages,
    bool? isLoading,
    String? error,
    String? language,
    bool clearError = false,
  }) =>
      AssistantState(
        messages: messages ?? this.messages,
        isLoading: isLoading ?? this.isLoading,
        error: clearError ? null : error ?? this.error,
        language: language ?? this.language,
      );
}

class AssistantNotifier extends StateNotifier<AssistantState> {
  final AssistantRemoteDatasource _ds;

  AssistantNotifier(this._ds) : super(const AssistantState());

  void setLanguage(String lang) {
    state = state.copyWith(language: lang);
  }

  void clearHistory() {
    state = state.copyWith(messages: []);
  }

  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty) return;

    // Ajouter le message utilisateur immédiatement
    final userMsg = MessageModel.user(content, language: state.language);
    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isLoading: true,
      clearError: true,
    );

    try {
      final history = state.messages
          .take(state.messages.length - 1) // exclure le dernier (vient d'être ajouté)
          .map((m) => {
                'role': m.isUser ? 'user' : 'assistant',
                'content': m.content,
              })
          .toList();

      final response = await _ds.sendMessage(
        message: content,
        language: state.language,
        history: history,
      );

      final assistantMsg = MessageModel.assistant(
        response,
        language: state.language,
      );

      state = state.copyWith(
        messages: [...state.messages, assistantMsg],
        isLoading: false,
      );
    } catch (e) {
      // Message d'erreur dans la conversation
      final errMsg = MessageModel.assistant(
        state.language == 'fr'
            ? 'Désolé, je ne suis pas disponible pour le moment. Réessayez dans quelques instants.'
            : 'Baal ma, maa ngi ci kanam. Jéfandiku ko ëllëk bi.',
        language: state.language,
      );
      state = state.copyWith(
        messages: [...state.messages, errMsg],
        isLoading: false,
        error: e.toString(),
      );
    }
  }
}

final assistantProvider =
    StateNotifierProvider<AssistantNotifier, AssistantState>((ref) =>
        AssistantNotifier(
          AssistantRemoteDatasource(client: ref.read(dioClientProvider)),
        ));
