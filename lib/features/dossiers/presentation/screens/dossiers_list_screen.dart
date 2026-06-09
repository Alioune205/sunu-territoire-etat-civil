import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../shared/widgets/status_badge.dart';
import '../../../../shared/widgets/skeleton_loader.dart';
import '../../data/models/dossier_model.dart';
import '../providers/dossiers_provider.dart';

/// S12 — Liste des dossiers
class DossiersListScreen extends ConsumerWidget {
  const DossiersListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dossiers = ref.watch(dossiersListProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Mes dossiers'),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            onPressed: () => ref.invalidate(dossiersListProvider),
          ),
        ],
      ),
      body: dossiers.when(
        loading: () => const Padding(
          padding: EdgeInsets.all(24),
          child: DossierListSkeleton(),
        ),
        error: (err, _) => _ErrorView(
          onRetry: () => ref.invalidate(dossiersListProvider),
        ),
        data: (list) => list.isEmpty
            ? const _EmptyView()
            : RefreshIndicator(
                color: AppColors.secondary,
                onRefresh: () async =>
                    ref.invalidate(dossiersListProvider),
                child: ListView.separated(
                  padding: const EdgeInsets.all(24),
                  itemCount: list.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (_, i) => _DossierCard(dossier: list[i]),
                ),
              ),
      ),
    );
  }
}

class _DossierCard extends StatelessWidget {
  final DossierModel dossier;
  const _DossierCard({required this.dossier});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push(
          AppRoutes.dossierDetailPath(dossier.id)),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadow,
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        AppFormatters.certTypeLabel(dossier.type),
                        style: AppTextStyles.labelLarge,
                      ),
                      if (dossier.beneficiaryNom != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          dossier.beneficiaryNom!,
                          style: AppTextStyles.bodySmall,
                        ),
                      ],
                    ],
                  ),
                ),
                StatusBadge(status: dossier.status),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.calendar_today_outlined,
                    size: 13, color: AppColors.textSecondary),
                const SizedBox(width: 4),
                Text(
                  AppFormatters.dateShort(dossier.createdAt),
                  style: AppTextStyles.caption,
                ),
                if (dossier.communeNom != null) ...[
                  const SizedBox(width: 12),
                  const Icon(Icons.location_on_outlined,
                      size: 13, color: AppColors.textSecondary),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      dossier.communeNom!,
                      style: AppTextStyles.caption,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 12),
            DossierProgressStepper(currentStatus: dossier.status),
          ],
        ),
      ),
    );
  }
}

class _EmptyView extends StatelessWidget {
  const _EmptyView();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.folder_open_outlined,
                size: 72, color: AppColors.border),
            const SizedBox(height: 16),
            Text('Aucun dossier', style: AppTextStyles.headlineSmall),
            const SizedBox(height: 8),
            Text(
              'Vos demandes de certificats apparaîtront ici.',
              style: AppTextStyles.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final VoidCallback onRetry;
  const _ErrorView({required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.wifi_off_outlined,
                size: 64, color: AppColors.textSecondary),
            const SizedBox(height: 16),
            Text('Impossible de charger', style: AppTextStyles.headlineSmall),
            const SizedBox(height: 8),
            Text(
              'Vérifiez votre connexion et réessayez.',
              style: AppTextStyles.bodySmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Réessayer'),
            ),
          ],
        ),
      ),
    );
  }
}
