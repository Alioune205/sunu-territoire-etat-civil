import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
import '../../data/remote_datasource.dart';

/// S08B — Formulaire "Pour une autre personne"
/// L'utilisateur peut : uploader l'extrait (OCR auto) OU saisir manuellement
class OtherPersonScreen extends ConsumerStatefulWidget {
  const OtherPersonScreen({super.key});

  @override
  ConsumerState<OtherPersonScreen> createState() => _OtherPersonScreenState();
}

class _OtherPersonScreenState extends ConsumerState<OtherPersonScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nomCtr = TextEditingController();
  final _registreCtr = TextEditingController();
  String? _lienParente;
  DateTime? _dateNaissance;
  CommuneModel? _commune;
  RegionModel? _region;
  bool _communeError = false;

  // Documents
  String? _cniRecto;
  String? _cniVerso;
  String? _extraitNaissance;

  // OCR state
  bool _ocrLoading = false;
  String? _ocrMessage;
  bool _ocrSuccess = false;
  bool _imageTooSmall = false;
  String? _ocrRegionId;
  String? _ocrCommuneId;

  static const _kNom = 'draft_naissance_other_nom';
  static const _kRegistre = 'draft_naissance_other_registre';
  static const _kLien = 'draft_naissance_other_lien';
  static const _kDate = 'draft_naissance_other_date';

  @override
  void initState() {
    super.initState();
    _loadDraft();
  }

  Future<void> _loadDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final nom = prefs.getString(_kNom) ?? '';
    final registre = prefs.getString(_kRegistre) ?? '';
    final lien = prefs.getString(_kLien);
    final dateStr = prefs.getString(_kDate);
    if (!mounted) return;
    setState(() {
      if (nom.isNotEmpty) _nomCtr.text = nom;
      if (registre.isNotEmpty) _registreCtr.text = registre;
      if (lien != null) _lienParente = lien;
      if (dateStr != null) _dateNaissance = DateTime.tryParse(dateStr);
    });
    if (nom.isNotEmpty || registre.isNotEmpty) {
      if (mounted) {
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
  }

  Future<void> _saveDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_kNom, _nomCtr.text.trim());
    await prefs.setString(_kRegistre, _registreCtr.text.trim());
    if (_lienParente != null) await prefs.setString(_kLien, _lienParente!);
    if (_dateNaissance != null) {
      await prefs.setString(_kDate, _dateNaissance!.toIso8601String());
    }
  }

  Future<void> _clearDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_kNom);
    await prefs.remove(_kRegistre);
    await prefs.remove(_kLien);
    await prefs.remove(_kDate);
  }

  @override
  void dispose() {
    _nomCtr.dispose();
    _registreCtr.dispose();
    super.dispose();
  }

  bool get _isValid =>
      _nomCtr.text.trim().isNotEmpty &&
      _registreCtr.text.trim().isNotEmpty &&
      _dateNaissance != null &&
      _commune != null &&
      _lienParente != null &&
      _cniRecto != null &&
      _cniVerso != null;

  // ── Upload documents ────────────────────────────────────
  Future<void> _pickDocument(String type) async {
    final path = await DocumentUploadHelper.pick(context);
    if (path == null) return;
    setState(() {
      switch (type) {
        case 'recto':   _cniRecto = path; break;
        case 'verso':   _cniVerso = path; break;
        case 'extrait':
          _extraitNaissance = path;
          _imageTooSmall = false;
          break;
      }
    });
    if (type == 'extrait') {
      // Vérification qualité
      try {
        final size = await File(path).length();
        if (size < 40000 && mounted) setState(() => _imageTooSmall = true);
      } catch (_) {}
      await _runOcr(path);
    }
  }

  // ── OCR automatique ────────────────────────────────────
  Future<void> _runOcr(String imagePath) async {
    setState(() {
      _ocrLoading = true;
      _ocrMessage = null;
      _ocrSuccess = false;
    });
    try {
      final ds = NaissanceRemoteDatasource(
          client: ref.read(dioClientProvider));
      final data = await ds.extractOcr(imagePath);
      if (!mounted) return;
      setState(() {
        _ocrLoading = false;
        _ocrSuccess = true;
        if ((data['nom'] as String? ?? '').isNotEmpty) {
          _nomCtr.text = data['nom'] as String;
        }
        final reg = data['registre'] as String? ?? '';
        if (reg.isNotEmpty) {
          _registreCtr.text =
              reg.length > 5 ? reg.substring(0, 5) : reg;
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
        _ocrMessage =
            'Extraction automatique échouée. Remplissez manuellement.';
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
      _nomCtr.clear();
      _registreCtr.clear();
      _dateNaissance = null;
      _ocrRegionId = null;
      _ocrCommuneId = null;
      _commune = null;
      _region = null;
    });
  }

  void _showTooltipRegistre(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.info_outline, color: AppColors.primary, size: 20),
            SizedBox(width: 8),
            Text('Numéro de registre'),
          ],
        ),
        content: const Text(
          'Le numéro de registre (aussi appelé numéro d\'acte) figure sur l\'extrait '
          'de naissance, en haut à droite du document, sous la forme d\'un nombre '
          'à 1–5 chiffres.\n\n'
          'Exemple : si vous voyez "Acte n° 42 du …", entrez 42.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Compris'),
          ),
        ],
      ),
    );
  }

  void _goToRecap() {
    if (_commune == null) {
      setState(() => _communeError = true);
      return;
    }
    if (!_formKey.currentState!.validate()) return;
    if (_cniRecto == null || _cniVerso == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Veuillez ajouter les deux faces de la CNI.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }
    _clearDraft();
    context.push(AppRoutes.naissanceRecapOther, extra: {
      'nom': _nomCtr.text.trim(),
      'registre': _registreCtr.text.trim(),
      'date_naissance': _dateNaissance!.toIso8601String(),
      'commune_id': _commune!.id,
      'commune_nom': _commune!.nom,
      'region_nom': _region?.nom ?? '',
      'lien_parente': _lienParente ?? '',
      'cni_recto': _cniRecto,
      'cni_verso': _cniVerso,
      'extrait_naissance': _extraitNaissance,
      'for_self': false,
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Pour une autre personne'),
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
                      // SECTION 1 : Extrait (optionnel / OCR)
                      // ══════════════════════════════════════
                      _SectionHeader(
                        title: 'Extrait de naissance existant',
                        badge: 'Optionnel',
                        badgeColor: AppColors.statusBlue,
                        badgeBg: AppColors.statusBlueLight,
                      ),
                      const SizedBox(height: 8),
                      // Explication claire des deux options
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
                              '📎 Uploader un extrait → les champs se remplissent automatiquement\n'
                              '✏️  Remplir manuellement → ignorez cette section',
                              style: AppTextStyles.caption
                                  .copyWith(color: AppColors.statusBlue),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      UploadDocumentCard(
                        title: 'Extrait de naissance',
                        subtitle: _ocrLoading
                            ? 'Extraction en cours...'
                            : 'Photo ou galerie — pré-remplissage automatique',
                        icon: Icons.description_outlined,
                        filePath: _extraitNaissance,
                        isRequired: false,
                        isLoading: _ocrLoading,
                        onTap: _ocrLoading ? () {} : () => _pickDocument('extrait'),
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
                            width: 16, height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(AppColors.secondary),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text('Analyse de l\'extrait en cours...',
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
                      // SECTION 2 : Formulaire bénéficiaire
                      // ══════════════════════════════════════
                      Text('Informations du bénéficiaire',
                          style: AppTextStyles.headlineMedium),
                      const SizedBox(height: 4),
                      Text(
                        _ocrSuccess
                            ? 'Données extraites — vérifiez et corrigez si nécessaire'
                            : 'Remplissez les informations manuellement',
                        style: AppTextStyles.bodySmall,
                      ),
                      const SizedBox(height: 20),

                      // ── Lien de parenté ──────────────────────
                      _LienParenteField(
                        value: _lienParente,
                        onChanged: (v) {
                          setState(() => _lienParente = v);
                          _saveDraft();
                        },
                      ),
                      const SizedBox(height: 16),

                      // Nom complet
                      AppTextField(
                        label: 'Nom complet',
                        hint: 'Ex: Fatou Sow',
                        controller: _nomCtr,
                        validator: Validators.fullName,
                        textInputAction: TextInputAction.next,
                        prefixIcon: const Icon(Icons.person_outline,
                            color: AppColors.textSecondary, size: 20),
                      ),
                      const SizedBox(height: 16),

                      // Registre (max 5 chiffres)
                      AppTextField(
                        label: 'Numéro de registre (max 5 chiffres)',
                        hint: 'Ex: 12345',
                        suffixIcon: GestureDetector(
                          onTap: () => _showTooltipRegistre(context),
                          child: const Padding(
                            padding: EdgeInsets.all(12),
                            child: Icon(Icons.info_outline,
                                size: 18, color: AppColors.textSecondary),
                          ),
                        ),
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
                        _ocrSuccess && _ocrMessage!.contains('suggérée')
                            ? 'Commune suggérée par l\'OCR — sélectionnez dans la liste'
                            : 'Choisissez la région puis la commune',
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
                      const SizedBox(height: 32),

                      // ══════════════════════════════════════
                      // SECTION 3 : CNI obligatoire
                      // ══════════════════════════════════════
                      _SectionHeader(
                        title: 'Pièce d\'identité (CNI)',
                        badge: 'Obligatoire',
                        badgeColor: AppColors.statusRed,
                        badgeBg: AppColors.statusRedLight,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Les deux faces de la CNI sont requises pour valider la demande.',
                        style: AppTextStyles.bodySmall,
                      ),
                      const SizedBox(height: 14),
                      UploadDocumentCard(
                        title: 'CNI — Recto',
                        subtitle: 'Face avant de la carte d\'identité',
                        icon: Icons.credit_card_outlined,
                        filePath: _cniRecto,
                        isRequired: true,
                        onTap: () => _pickDocument('recto'),
                        onRemove: _cniRecto != null
                            ? () => setState(() => _cniRecto = null)
                            : null,
                      ),
                      const SizedBox(height: 12),
                      UploadDocumentCard(
                        title: 'CNI — Verso',
                        subtitle: 'Face arrière de la carte d\'identité',
                        icon: Icons.credit_card_outlined,
                        filePath: _cniVerso,
                        isRequired: true,
                        onTap: () => _pickDocument('verso'),
                        onRemove: _cniVerso != null
                            ? () => setState(() => _cniVerso = null)
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

// ── Lien de parenté ──────────────────────────────────────────
class _LienParenteField extends StatelessWidget {
  final String? value;
  final void Function(String?) onChanged;

  static const _options = [
    'Père / Mère',
    'Enfant',
    'Frère / Sœur',
    'Grand-parent',
    'Époux / Épouse',
    'Représentant légal',
    'Autre',
  ];

  const _LienParenteField({required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Text('Lien de parenté', style: AppTextStyles.inputLabel),
          const SizedBox(width: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: AppColors.statusRedLight,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text('Requis',
                style: AppTextStyles.caption.copyWith(
                    color: AppColors.statusRed,
                    fontSize: 10,
                    fontWeight: FontWeight.w600)),
          ),
        ]),
        const SizedBox(height: 6),
        DropdownButtonFormField<String>(
          value: value,
          isExpanded: true,
          hint: Text('Votre lien avec le bénéficiaire',
              style: AppTextStyles.inputHint),
          icon: const Icon(Icons.keyboard_arrow_down_rounded,
              color: AppColors.textSecondary),
          style: AppTextStyles.inputText,
          dropdownColor: AppColors.surface,
          decoration: InputDecoration(
            filled: true,
            fillColor: AppColors.surface,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            prefixIcon: const Icon(Icons.people_outline,
                color: AppColors.textSecondary, size: 20),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide:
                  const BorderSide(color: AppColors.primary, width: 1.5),
            ),
          ),
          items: _options
              .map((o) => DropdownMenuItem(
                    value: o,
                    child: Text(o, style: AppTextStyles.inputText),
                  ))
              .toList(),
          onChanged: onChanged,
          validator: (v) =>
              v == null ? 'Veuillez indiquer votre lien de parenté.' : null,
        ),
      ],
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final String badge;
  final Color badgeColor;
  final Color badgeBg;

  const _SectionHeader({
    required this.title,
    required this.badge,
    required this.badgeColor,
    required this.badgeBg,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: AppTextStyles.headlineSmall),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: badgeBg,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            badge,
            style: AppTextStyles.caption.copyWith(
                color: badgeColor, fontWeight: FontWeight.w600),
          ),
        ),
      ],
    );
  }
}
