import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../../core/router/app_router.dart';
import '../../../../../core/theme/app_colors.dart';
import '../../../../../core/theme/app_text_styles.dart';

/// S08 — Choix bénéficiaire
class BeneficiaryChoiceScreen extends StatelessWidget {
  const BeneficiaryChoiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
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
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 8),
              Text('Pour qui ?', style: AppTextStyles.headlineLarge),
              const SizedBox(height: 4),
              Text(
                'Sélectionnez le bénéficiaire du certificat',
                style: AppTextStyles.bodySmall,
              ),
              const SizedBox(height: 32),
              _ChoiceCard(
                icon: Icons.person_outlined,
                title: 'Pour moi',
                subtitle: 'Utiliser mon nom d\'inscription\net choisir ma commune',
                onTap: () => context.push(AppRoutes.naissanceRecapSelf),
              ),
              const SizedBox(height: 12),
              _ChoiceCard(
                icon: Icons.group_outlined,
                title: 'Pour une autre personne',
                subtitle: 'Remplir les informations manuellement\n+ CNI obligatoire',
                onTap: () => context.push(AppRoutes.naissanceOtherPerson),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.statusGreenLight,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.security_outlined,
                        color: AppColors.secondary, size: 18),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Vos données sont protégées et chiffrées.',
                        style: AppTextStyles.caption
                            .copyWith(color: AppColors.secondary),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ChoiceCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ChoiceCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.border),
          boxShadow: [
            BoxShadow(
                color: AppColors.shadow,
                blurRadius: 6,
                offset: const Offset(0, 2)),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: AppColors.primary, size: 26),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: AppTextStyles.labelLarge),
                  const SizedBox(height: 3),
                  Text(subtitle, style: AppTextStyles.bodySmall),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios,
                color: AppColors.textHint, size: 16),
          ],
        ),
      ),
    );
  }
}
