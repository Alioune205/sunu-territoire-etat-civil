import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:go_router/go_router.dart';
import '../../../../../core/constants/app_constants.dart';
import '../../../../../core/router/app_router.dart';
import '../../../../../core/theme/app_colors.dart';
import '../../../../../core/theme/app_text_styles.dart';
import '../../../../../core/utils/validators.dart';
import '../../../../../core/network/dio_client.dart';
import '../../../../../shared/widgets/primary_button.dart';
import '../../../../../shared/widgets/app_text_field.dart';
import '../../../../../shared/widgets/region_commune_select.dart';
import '../../../../../shared/widgets/upload_document_card.dart';
import '../../../../../shared/widgets/certificate_step_indicator.dart';
import '../../../../../shared/models/commune_model.dart';
import '../../../../auth/presentation/providers/auth_provider.dart';
import '../../data/remote_datasource.dart';

/// S08A — Formulaire "Pour moi"
/// Deux options : upload de l'extrait (OCR) OU saisie manuelle
class RecapSelfScreen extends ConsumerStatefulWidget {
  const RecapSelfScreen({super.key});

  @override
  ConsumerState<RecapSelfScreen> createState() => _RecapSelfScreenState();
}

class _RecapSelfScreenState extends ConsumerState<RecapSelfScreen> {
  final _formKey = GlobalKey<FormState>();
  final _registreCtr = TextEditingController();
  DateTime? _dateNaissance;
  CommuneModel? _commune;
  RegionModel? _region;
  bool _communeError = false;

  // Upload extrait (optionnel)
  String? _extraitNaissance;
  bool _ocrLoading = false;
  String? _ocrMessage;
  bool _ocrSuccess = false;
  bool _imageTooSmall = false;
  String? _ocrRegionId;
  String? _ocrCommuneId;

  static const _kRegistre = 'draft_naissance_self_registre';
  static const _kDate = 'draft_naissance_self_date';

  @override
  void initState() {
    super.initState();
    _loadDraft();
    _ensureUser();
  }

  /// Si l'état auth n'a pas de user (hot-restart, token expiré…),
  /// on le recharge depuis l'API — ou on renvoie vers login.
  Future<void> _ensureUser() async {
    if (ref.read(authProvider).user != null) return;
    try {
      final repo = ref.read(authRepositoryProvider);
      final user = await repo.getMe();
      if (mounted) ref.read(authProvider.notifier).setUser(user);
    } catch (_) {
      if (mounted) context.go(AppRoutes.login);
    }
  }

  Future<void> _loadDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final registre = prefs.getString(_kRegistre) ?? '';
    final dateStr = prefs.getString(_kDate);
    if (!mounted) return;
    setState(() {
      if (registre.isNotEmpty) _registreCtr.text = registre;
      if (dateStr != null) _dateNaissance = DateTime.tryParse(dateStr);
    });
    if (registre.isNotEmpty && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(children: [
            Icon(Icons.restore_outlined, color: Colors.white, size: 16),
            SizedBox(width: 8),
            Text('Brouillon restauré'),
          ]),
          backgroundColor: AppColors.statusBlue,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
          action: SnackBarAction(
            label: 'Effacer',
            textColor: Colors.white,
            onPressed: _clearDraft,
          ),
        ),
      );
    }
  }

  Future<void> _saveDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_kRegistre, _registreCtr.text.trim());
    if (_dateNaissance != null) {
      await prefs.setString(_kDate, _dateNaissance!.toIso8601String());
    }
  }

  Future<void> _clearDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_kRegistre);
    await prefs.remove(_kDate);
  }

  @override
  void dispose() {
    _registreCtr.dispose();
    super.dispose();
  }

  bool get _isValid =>
      _registreCtr.text.trim().isNotEmpty &&
      _registreCtr.text.trim().length <= 5 &&
      _dateNaissance != null &&
      _commune != null;

  // ── Upload & OCR ───────────────────────────────────────────
  Future<void> _pickExtrait() async {
    final path = await DocumentUploadHelper.pick(context);
    if (path == null) return;
    setState(() {
      _extraitNaissance = path;
      _imageTooSmall = false;
    });
    // Vérification qualité : fichier trop petit → image floue probable
    try {
      final size = await File(path).length();
      if (size < 40000 && mounted) setState(() => _imageTooSmall = true);
    } catch (_) {}
    await _runOcr(path);
  }

  Future<void> _runOcr(String imagePath) async {
    setState(() {
      _ocrLoading = true;
      _ocrMessage = null;
      _ocrSuccess = false;
    });
    try {
      final ds = NaissanceRemoteDatasource(client: ref.read(dioClientProvider));
      final data = await ds.extractOcr(imagePath);
      if (!mounted) return;
      setState(() {
        _ocrLoading = false;
        _ocrSuccess = true;
        final reg = data['registre'] as String? ?? '';
        if (reg.isNotEmpty) {
          _registreCtr.text = reg.length > 5 ? reg.substring(0, 5) : reg;
        }
        if (data['date_naissance'] != null) {
          _dateNaissance =
              DateTime.tryParse(data['date_naissance'] as String);
        }
        // Pré-sélection région + commune
        _ocrRegionId = data['region_id'] as String? ?? '';
        _ocrCommuneId = data['commune_id'] as String? ?? '';
        final communeNom = data['commune_nom'] as String? ?? '';
        _ocrMessage = communeNom.isNotEmpty
            ? 'Données extraites. Région et commune pré-sélectionnées ($communeNom).'
            : 'Données extraites automatiquement. Vérifiez et corrigez si besoin.';
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _ocrLoading = false;
        _ocrSuccess = false;
        _ocrMessage = 'Extraction automatique échouée. Remplissez manuellement.';
      });
    }
  }

  void _clearExtrait() {
    setState(() {
      _extraitNaissance = null;
      _ocrMessage = null;
      _ocrSuccess = false;
      _imageTooSmall = false;
      // Vider les champs pré-remplis par l'OCR
      _registreCtr.clear();
      _dateNaissance = null;
      _ocrRegionId = null;
      _ocrCommuneId = null;
      _commune = null;
      _region = null;
    });
  }

  // ── Navigation vers récap ──────────────────────────────────
  void _goToRecap() {
    if (_commune == null) {
      setState(() => _communeError = true);
      return;
    }
    if (!_formKey.currentState!.validate()) return;

    final user = ref.read(authProvider).user!;
    _clearDraft();
    context.push(
      AppRoutes.naissanceRecapSelf + '/recap',
      extra: {
        'nom': user.nomComplet,
        'registre': _registreCtr.text.trim(),
        'date_naissance': _dateNaissance!.toIso8601String(),
        'commune_id': _commune!.id,
        'commune_nom': _commune!.nom,
        'region_nom': _region?.nom ?? '',
        'extrait_naissance': _extraitNaissance,
        'for_self': true,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).user;
    if (user == null) {
      return Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          title: const Text('Certificat de naissance'),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new),
            onPressed: () => context.pop(),
          ),
        ),
        body: const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation(AppColors.secondary),
              ),
              SizedBox(height: 16),
              Text('Chargement du profil…'),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Certificat de naissance'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ── Stepper progression ──────────────────────
            const CertificateStepIndicator(currentStep: CertStep.formulaire),
            const SizedBox(height: 8),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Form(
                  key: _formKey,
                  onChanged: () {
                    setState(() {});
                    _saveDraft();
                  },
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [

                      // ══════════════════════════════════════
                      // SECTION 1 : Upload extrait (optionnel)
                      // ══════════════════════════════════════
                      Row(children: [
                        Text('Extrait de naissance existant',
                            style: AppTextStyles.headlineSmall),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: AppColors.statusBlueLight,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text('Optionnel',
                              style: AppTextStyles.caption.copyWith(
                                  color: AppColors.statusBlue,
                                  fontWeight: FontWeight.w600)),
                        ),
                      ]),
                      const SizedBox(height: 8),

                      // Info box
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.statusBlueLight,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                              color: AppColors.statusBlue.withValues(alpha: 0.3)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(children: [
                              const Icon(Icons.info_outline,
                                  color: AppColors.statusBlue, size: 16),
                              const SizedBox(width: 8),
                              Text('Deux options disponibles :',
                                  style: AppTextStyles.labelMedium
                                      .copyWith(color: AppColors.statusBlue)),
                            ]),
                            const SizedBox(height: 6),
                            Text(
                              '📎 Uploader mon extrait → les champs se remplissent automatiquement\n'
                              '✏️  Remplir manuellement → ignorez cette section',
                              style: AppTextStyles.caption
                                  .copyWith(color: AppColors.statusBlue),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      UploadDocumentCard(
                        title: 'Mon extrait de naissance',
                        subtitle: _ocrLoading
                            ? 'Extraction en cours...'
                            : 'Photo ou galerie — pré-remplissage automatique',
                        icon: Icons.description_outlined,
                        filePath: _extraitNaissance,
                        isRequired: false,
                        isLoading: _ocrLoading,
                        onTap: _ocrLoading ? () {} : _pickExtrait,
                        onRemove: (_extraitNaissance != null && !_ocrLoading)
                            ? _clearExtrait
                            : null,
                      ),

                      // ── Avertissement qualité ──────────────
                      if (_imageTooSmall && !_ocrLoading) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppColors.statusAmberLight,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                              color: AppColors.statusAmber.withValues(alpha: 0.4)),
                          ),
                          child: Row(children: [
                            const Icon(Icons.photo_size_select_large_outlined,
                                color: AppColors.statusAmber, size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Image de faible résolution — résultats OCR potentiellement imprécis. '
                                'Prenez une photo nette et bien éclairée.',
                                style: AppTextStyles.caption
                                    .copyWith(color: AppColors.statusAmber),
                              ),
                            ),
                          ]),
                        ),
                      ],

                      // ── Feedback OCR ────────────────────────
                      if (_ocrLoading) ...[
                        const SizedBox(height: 10),
                        Row(children: [
                          const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(
                                  AppColors.secondary),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                                'Analyse de l\'extrait en cours...',
                                style: AppTextStyles.caption
                                    .copyWith(color: AppColors.secondary)),
                          ),
                        ]),
                      ],
                      if (_ocrMessage != null && !_ocrLoading) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: _ocrSuccess
                                ? AppColors.statusGreenLight
                                : AppColors.statusAmberLight,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                              color: (_ocrSuccess
                                      ? AppColors.secondary
                                      : AppColors.statusAmber)
                                  .withValues(alpha: 0.4),
                            ),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Icon(
                                _ocrSuccess
                                    ? Icons.check_circle_outline
                                    : Icons.warning_amber_outlined,
                                size: 16,
                                color: _ocrSuccess
                                    ? AppColors.secondary
                                    : AppColors.statusAmber,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(_ocrMessage!,
                                    style: AppTextStyles.caption.copyWith(
                                      color: _ocrSuccess
                                          ? AppColors.secondary
                                          : AppColors.statusAmber,
                                    )),
                              ),
                            ],
                          ),
                        ),
                        // ── Bouton Réessayer (échec OCR) ────────
                        if (!_ocrSuccess && _extraitNaissance != null) ...[
                          const SizedBox(height: 8),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: GestureDetector(
                              onTap: () => _runOcr(_extraitNaissance!),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 14, vertical: 9),
                                decoration: BoxDecoration(
                                  color: AppColors.primary,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.refresh,
                                        color: Colors.white, size: 16),
                                    const SizedBox(width: 6),
                                    Text('Réessayer l\'extraction',
                                        style: AppTextStyles.caption.copyWith(
                                            color: Colors.white,
                                            fontWeight: FontWeight.w600)),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ],
                      const SizedBox(height: 32),

                      // ══════════════════════════════════════
                      // SECTION 2 : Informations
                      // ══════════════════════════════════════
                      Row(children: [
                        Text('Vos informations',
                            style: AppTextStyles.headlineMedium),
                        if (_ocrSuccess) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: AppColors.statusGreenLight,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.auto_fix_high,
                                    size: 12, color: AppColors.secondary),
                                const SizedBox(width: 4),
                                Text('Pré-rempli',
                                    style: AppTextStyles.caption.copyWith(
                                        color: AppColors.secondary,
                                        fontWeight: FontWeight.w600)),
                              ],
                            ),
                          ),
                        ],
                      ]),
                      const SizedBox(height: 4),
                      Text(
                        _ocrSuccess
                            ? 'Données extraites — vérifiez et corrigez si nécessaire'
                            : 'Complétez les informations pour votre certificat',
                        style: AppTextStyles.bodySmall,
                      ),
                      const SizedBox(height: 20),

                      // Nom verrouillé
                      _LockedField(
                        label: 'Nom complet',
                        value: user.nomComplet,
                        hint: 'Récupéré depuis votre inscription',
                      ),
                      const SizedBox(height: 16),

                      // Numéro de registre
                      AppTextField(
                        label: 'Numéro de registre',
                        hint: 'Ex: 12345 (5 chiffres max)',
                        controller: _registreCtr,
                        keyboardType: TextInputType.number,
                        textInputAction: TextInputAction.next,
                        maxLength: 5,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly,
                          LengthLimitingTextInputFormatter(5),
                        ],
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) {
                            return 'Le numéro de registre est requis.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      // Date de naissance
                      DateTextField(
                        label: 'Date de naissance',
                        selectedDate: _dateNaissance,
                        validator: (_) =>
                            Validators.dateNaissance(_dateNaissance),
                        onDateSelected: (d) {
                          setState(() => _dateNaissance = d);
                          _saveDraft();
                        },
                      ),
                      const SizedBox(height: 24),

                      // Région → Commune
                      Text('Commune déclarée',
                          style: AppTextStyles.headlineSmall),
                      const SizedBox(height: 4),
                      Text(
                        _ocrSuccess && (_ocrMessage?.contains('suggérée') ?? false)
                            ? 'Commune suggérée par l\'OCR — sélectionnez dans la liste'
                            : 'Choisissez votre région puis votre commune',
                        style: AppTextStyles.bodySmall,
                      ),
                      const SizedBox(height: 16),
                      RegionCommuneSelect(
                        initialRegionId: _ocrRegionId,
                        initialCommuneId: _ocrCommuneId,
                        onChanged: (r, c) => setState(() {
                          _region = r;
                          _commune = c;
                          if (c != null) _communeError = false;
                        }),
                        errorText: _communeError
                            ? 'Veuillez sélectionner une commune.'
                            : null,
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
              child: PrimaryButton(
                label: 'Voir le récapitulatif →',
                onPressed: _goToRecap,
                isEnabled: _isValid,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Champ verrouillé visuellement ──────────────────────────────
class _LockedField extends StatelessWidget {
  final String label;
  final String value;
  final String hint;

  const _LockedField({
    required this.label,
    required this.value,
    required this.hint,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.inputLabel),
        const SizedBox(height: 6),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: AppColors.background,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppColors.divider),
          ),
          child: Row(
            children: [
              const Icon(Icons.person_outline,
                  color: AppColors.textSecondary, size: 18),
              const SizedBox(width: 10),
              Expanded(
                child: Text(value,
                    style: AppTextStyles.inputText.copyWith(
                      color: AppColors.textSecondary,
                    )),
              ),
              const Icon(Icons.lock_outline,
                  color: AppColors.textHint, size: 16),
            ],
          ),
        ),
        const SizedBox(height: 4),
        Text(hint,
            style: AppTextStyles.caption
                .copyWith(color: AppColors.textHint)),
      ],
    );
  }
}
