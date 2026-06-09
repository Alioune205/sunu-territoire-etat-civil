import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../../shared/widgets/status_badge.dart';
import '../../../../shared/widgets/recap_card.dart';
import '../../../../shared/widgets/skeleton_loader.dart';
import '../providers/dossiers_provider.dart';

/// S12A — Détail d'un dossier
class DossierDetailScreen extends ConsumerStatefulWidget {
  final String dossierId;
  const DossierDetailScreen({super.key, required this.dossierId});

  @override
  ConsumerState<DossierDetailScreen> createState() =>
      _DossierDetailScreenState();
}

class _DossierDetailScreenState extends ConsumerState<DossierDetailScreen> {
  bool _isDownloading = false;

  @override
  Widget build(BuildContext context) {
    final dossier = ref.watch(dossierDetailProvider(widget.dossierId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Détail du dossier'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
      ),
      body: Stack(
        children: [
          dossier.when(
        loading: () => const Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            children: [
              DossierCardSkeleton(),
              SizedBox(height: 16),
              DossierCardSkeleton(),
            ],
          ),
        ),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline,
                  size: 48, color: AppColors.error),
              const SizedBox(height: 12),
              Text('Dossier introuvable', style: AppTextStyles.headlineSmall),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => context.pop(),
                child: const Text('Retour'),
              ),
            ],
          ),
        ),
        data: (d) => SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── En-tête statut ──────────────────────────
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        AppFormatters.certTypeLabel(d.type),
                        style: AppTextStyles.headlineMedium,
                      ),
                    ),
                    StatusBadge(status: d.status),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Réf: ${d.id}',
                  style: AppTextStyles.caption,
                ),
                const SizedBox(height: 20),

                // ── Stepper progression ─────────────────────
                DossierProgressStepper(currentStatus: d.status),
                const SizedBox(height: 24),

                // ── Infos dossier ───────────────────────────
                RecapCard(
                  title: 'Informations',
                  fields: [
                    RecapField(
                      label: 'Type',
                      value: AppFormatters.certTypeLabel(d.type),
                      icon: Icons.article_outlined,
                    ),
                    RecapField(
                      label: 'Statut',
                      value: AppFormatters.statusLabel(d.status),
                      icon: Icons.info_outline,
                      valueColor: _statusColor(d.status),
                    ),
                    RecapField(
                      label: 'Date de demande',
                      value: AppFormatters.dateWithTime(d.createdAt),
                      icon: Icons.calendar_today_outlined,
                    ),
                    if (d.communeNom != null)
                      RecapField(
                        label: 'Commune',
                        value: d.communeNom!,
                        icon: Icons.location_on_outlined,
                      ),
                    if (d.beneficiaryNom != null)
                      RecapField(
                        label: 'Bénéficiaire',
                        value: d.beneficiaryNom!,
                        icon: Icons.person_outline,
                      ),
                    if (d.fraisFCFA != null)
                      RecapField(
                        label: 'Frais payés',
                        value: AppFormatters.amountFCFA(d.fraisFCFA!),
                        icon: Icons.receipt_outlined,
                        valueColor: AppColors.secondary,
                      ),
                  ],
                ),
                const SizedBox(height: 16),

                // ── Délai estimé si en cours ─────────────────
                if (d.status != 'pret' && d.status != 'rejete')
                  _DelayCard(type: d.type),

                // ── Bouton télécharger si prêt ───────────────
                if (d.status == 'pret') ...[
                  const SizedBox(height: 16),
                  PrimaryButton(
                    label: 'Télécharger le certificat',
                    leadingIcon: Icons.download_outlined,
                    onPressed: _isDownloading
                        ? null
                        : () => _download(context, d.id),
                  ),
                ],

                // ── Message rejet ────────────────────────────
                if (d.status == 'rejete')
                  Container(
                    margin: const EdgeInsets.only(top: 16),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppColors.statusRedLight,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                          color: AppColors.statusRed.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.cancel_outlined,
                            color: AppColors.statusRed, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Votre demande a été rejetée. '
                            'Contactez votre commune pour plus d\'informations.',
                            style: AppTextStyles.caption.copyWith(
                                color: AppColors.statusRed),
                          ),
                        ),
                      ],
                    ),
                  ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
          ),
          // ── Overlay de chargement pendant le téléchargement ──
          if (_isDownloading)
            Container(
              color: Colors.black26,
              child: const Center(
                child: Card(
                  elevation: 6,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.all(Radius.circular(16)),
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 32, vertical: 28),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(
                          color: AppColors.primary,
                          strokeWidth: 3,
                        ),
                        SizedBox(height: 16),
                        Text(
                          'Téléchargement en cours…',
                          style: TextStyle(
                            fontFamily: 'Poppins',
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'pret':
      case 'valide':
        return AppColors.statusGreen;
      case 'rejete':
        return AppColors.statusRed;
      case 'en_verification':
        return AppColors.statusAmber;
      default:
        return AppColors.statusBlue;
    }
  }

  Future<void> _download(BuildContext context, String id) async {
    setState(() => _isDownloading = true);
    try {
      final path =
          await ref.read(downloadCertificateProvider(id).future);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.check_circle_outline,
                  color: Colors.white, size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Certificat sauvegardé :\n$path',
                  style: const TextStyle(fontSize: 12),
                ),
              ),
            ],
          ),
          backgroundColor: AppColors.statusGreen,
          duration: const Duration(seconds: 5),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur : $e'),
          backgroundColor: AppColors.error,
        ),
      );
    } finally {
      if (mounted) setState(() => _isDownloading = false);
    }
  }
}

class _DelayCard extends StatelessWidget {
  final String type;
  const _DelayCard({required this.type});

  int get _days {
    switch (type) {
      case 'mariage': return 5;
      default: return 3;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.statusBlueLight,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
            color: AppColors.statusBlue.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.timer_outlined,
              color: AppColors.statusBlue, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'Délai estimé : $_days jours ouvrés',
              style: AppTextStyles.caption.copyWith(
                  color: AppColors.statusBlue),
            ),
          ),
        ],
      ),
    );
  }
}
