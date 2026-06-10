import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/assets_constants.dart';
import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/formatters.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../dossiers/presentation/providers/dossiers_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user   = ref.watch(authProvider).user;
    final prenom = user != null
        ? AppFormatters.titleCase(user.nom.split(' ').first)
        : 'Bienvenue';

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      body: SafeArea(
        child: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [

            // ── Top bar ──────────────────────────────────────
            SliverToBoxAdapter(child: _TopBar(
              prenom: prenom,
              onNotifications: () => _showNotifications(context, ref),
            )),

            // ── Barre de recherche ───────────────────────────
            SliverToBoxAdapter(child: _SearchBar()),

            // ── Section : Services disponibles ──────────────
            SliverToBoxAdapter(child: _SectionHeader(
              title: 'Services disponibles',
              actionLabel: 'Mes dossiers',
              onAction: () => context.go(AppRoutes.dossiers),
            )),
            SliverToBoxAdapter(child: _QuickServices(context)),

            // ── Section : Bientôt disponibles ───────────────
            SliverToBoxAdapter(child: _SectionHeader(
              title: 'Bientôt disponibles',
              actionLabel: 'Voir tout',
              onAction: () {},
            )),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              sliver: SliverGrid(
                delegate: SliverChildListDelegate(
                  _comingSoonServices(context),
                ),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 1.55,
                ),
              ),
            ),

            // ── Délais de traitement ─────────────────────────
            SliverToBoxAdapter(child: _SectionHeader(
              title: 'Délais de traitement',
            )),
            SliverToBoxAdapter(child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 32),
              child: _DelaiBanner(),
            )),
          ],
        ),
      ),
    );
  }

  // ── Services rapides disponibles (scroll horizontal) ──────────
  Widget _QuickServices(BuildContext context) {
    final services = [
      _QuickService(
        icon: Icons.article_outlined,
        label: 'Naissance',
        color: const Color(0xFF3B82F6),
        onTap: () => context.push(AppRoutes.naissanceBeneficiary),
      ),
      _QuickService(
        icon: Icons.favorite_rounded,
        label: 'Mariage',
        color: const Color(0xFFEC4899),
        onTap: () => context.push(AppRoutes.mariageForm),
      ),
      _QuickService(
        icon: Icons.local_florist_outlined,
        label: 'Décès',
        color: const Color(0xFF6366F1),
        onTap: () => context.push(AppRoutes.decesForm),
      ),
      _QuickService(
        icon: Icons.folder_copy_outlined,
        label: 'Dossiers',
        color: const Color(0xFF1D9E75),
        onTap: () => context.go(AppRoutes.dossiers),
      ),
    ];

    return SizedBox(
      height: 100,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: services.length,
        separatorBuilder: (_, __) => const SizedBox(width: 16),
        itemBuilder: (_, i) => _QuickServiceTile(service: services[i]),
      ),
    );
  }

  // ── Services bientôt disponibles ─────────────────────────────
  List<Widget> _comingSoonServices(BuildContext context) => [
    _ComingSoonCard(
      icon: Icons.gavel_rounded,
      label: 'Casier judiciaire',
      color: const Color(0xFF8B5CF6),
    ),
    _ComingSoonCard(
      icon: Icons.public_rounded,
      label: 'Nationalité',
      color: const Color(0xFF0EA5E9),
    ),
    _ComingSoonCard(
      icon: Icons.badge_outlined,
      label: 'Demande NINEA',
      color: const Color(0xFFF59E0B),
    ),
    _ComingSoonCard(
      icon: Icons.store_rounded,
      label: 'Registre du Commerce',
      color: const Color(0xFF10B981),
    ),
  ];

  void _showNotifications(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => _NotificationSheet(ref: ref),
    );
  }
}

// ── Top Bar ───────────────────────────────────────────────────
class _TopBar extends StatelessWidget {
  final String prenom;
  final VoidCallback onNotifications;
  const _TopBar({required this.prenom, required this.onNotifications});

  static const _navy = Color(0xFF0A1F5C);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Row(
        children: [
          // Logo
          Image.asset(Assets.logoTeranga,
              width: 40, height: 40, fit: BoxFit.contain),
          const SizedBox(width: 10),
          // Titre + salut
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('TERANGA CIVIL',
                    style: TextStyle(
                      color: _navy,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      fontFamily: 'Poppins',
                      letterSpacing: 1,
                    )),
                Text(
                  'Bonjour, $prenom 👋',
                  style: const TextStyle(
                    color: Color(0xFF888888),
                    fontSize: 11,
                    fontFamily: 'Poppins',
                  ),
                ),
              ],
            ),
          ),
          // Cloche
          GestureDetector(
            onTap: onNotifications,
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: const Color(0xFFF0F4FF),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.notifications_outlined,
                  color: _navy, size: 20),
            ),
          ),
          const SizedBox(width: 8),
          // Paramètres
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFFF0F4FF),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.settings_outlined,
                color: _navy, size: 20),
          ),
        ],
      ),
    );
  }
}

// ── Search Bar ────────────────────────────────────────────────
class _SearchBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 14),
      child: Container(
        height: 46,
        decoration: BoxDecoration(
          color: const Color(0xFFF5F7FA),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Row(
          children: [
            const SizedBox(width: 14),
            const Icon(Icons.search_rounded,
                color: Color(0xFF9CA3AF), size: 20),
            const SizedBox(width: 10),
            const Expanded(
              child: Text('Rechercher un service...',
                  style: TextStyle(
                    color: Color(0xFF9CA3AF),
                    fontSize: 13,
                    fontFamily: 'Poppins',
                  )),
            ),
            Container(
              margin: const EdgeInsets.all(6),
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                color: const Color(0xFF0A1F5C).withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.mic_outlined,
                  color: Color(0xFF0A1F5C), size: 18),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Section Header ────────────────────────────────────────────
class _SectionHeader extends StatelessWidget {
  final String title;
  final String? actionLabel;
  final VoidCallback? onAction;
  const _SectionHeader({required this.title, this.actionLabel, this.onAction});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 20, 16, 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title,
              style: const TextStyle(
                color: Color(0xFF0A1F5C),
                fontSize: 15,
                fontWeight: FontWeight.w700,
                fontFamily: 'Poppins',
              )),
          if (actionLabel != null)
            GestureDetector(
              onTap: onAction,
              child: Text(actionLabel!,
                  style: const TextStyle(
                    color: Color(0xFF1D9E75),
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    fontFamily: 'Poppins',
                  )),
            ),
        ],
      ),
    );
  }
}

// ── Quick Service data ────────────────────────────────────────
class _QuickService {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _QuickService({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });
}

// ── Quick Service Tile ────────────────────────────────────────
class _QuickServiceTile extends StatelessWidget {
  final _QuickService service;
  const _QuickServiceTile({required this.service});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: service.onTap,
      child: SizedBox(
        width: 72,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 58,
              height: 58,
              decoration: BoxDecoration(
                color: service.color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                    color: service.color.withValues(alpha: 0.2)),
              ),
              child: Icon(service.icon, color: service.color, size: 26),
            ),
            const SizedBox(height: 7),
            Text(
              service.label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Color(0xFF374151),
                fontSize: 11,
                fontWeight: FontWeight.w500,
                fontFamily: 'Poppins',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Coming Soon Card ──────────────────────────────────────────
class _ComingSoonCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  const _ComingSoonCard({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        child: Row(
          children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(label,
                      style: const TextStyle(
                        color: Color(0xFF1F2937),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        fontFamily: 'Poppins',
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 3),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF59E0B).withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text('Bientôt',
                        style: TextStyle(
                          color: Color(0xFFF59E0B),
                          fontSize: 9,
                          fontWeight: FontWeight.w700,
                          fontFamily: 'Poppins',
                        )),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Délai Banner ──────────────────────────────────────────────
class _DelaiBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final items = [
      _DelaiItem(icon: Icons.article_outlined,
          label: 'Certificat de naissance',
          delai: '3 jours ouvrés',
          color: const Color(0xFF3B82F6)),
      _DelaiItem(icon: Icons.favorite_rounded,
          label: 'Certificat de mariage',
          delai: '5 jours ouvrés',
          color: const Color(0xFFEC4899)),
      _DelaiItem(icon: Icons.local_florist_outlined,
          label: 'Certificat de décès',
          delai: '3 jours ouvrés',
          color: const Color(0xFF6366F1)),
    ];
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: List.generate(items.length, (i) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(
                  horizontal: 16, vertical: 12),
              child: Row(children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: items[i].color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(items[i].icon,
                      color: items[i].color, size: 18),
                ),
                const SizedBox(width: 12),
                Expanded(child: Text(items[i].label,
                    style: const TextStyle(
                      color: Color(0xFF374151),
                      fontSize: 12,
                      fontFamily: 'Poppins',
                    ))),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1D9E75).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(items[i].delai,
                      style: const TextStyle(
                        color: Color(0xFF1D9E75),
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'Poppins',
                      )),
                ),
              ]),
            ),
            if (i < items.length - 1)
              const Divider(height: 1, indent: 64),
          ],
        )),
      ),
    );
  }
}

class _DelaiItem {
  final IconData icon;
  final String label;
  final String delai;
  final Color color;
  const _DelaiItem({
    required this.icon,
    required this.label,
    required this.delai,
    required this.color,
  });
}

// ── Notification Sheet ────────────────────────────────────────
class _NotifItem {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  const _NotifItem({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
  });
}

class _NotificationSheet extends ConsumerWidget {
  final WidgetRef ref;
  const _NotificationSheet({required this.ref});

  @override
  Widget build(BuildContext context, WidgetRef _) {
    final dossiers = ref.watch(dossiersListProvider);

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.55,
      maxChildSize: 0.85,
      minChildSize: 0.35,
      builder: (ctx, scrollController) => Column(
        children: [
          const SizedBox(height: 12),
          Container(
            width: 40, height: 4,
            decoration: BoxDecoration(
              color: AppColors.border,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Notifications', style: AppTextStyles.headlineSmall),
                dossiers.when(
                  data: (list) => list.isNotEmpty
                      ? Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            gradient: AppColors.primaryGradient,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text('${list.length}',
                              style: AppTextStyles.labelSmall
                                  .copyWith(color: Colors.white)),
                        )
                      : const SizedBox.shrink(),
                  loading: () => const SizedBox.shrink(),
                  error: (_, __) => const SizedBox.shrink(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          const Divider(height: 1),
          Expanded(
            child: dossiers.when(
              loading: () => const Center(
                  child: CircularProgressIndicator(
                      color: AppColors.primary)),
              error: (_, __) => Center(
                child: Text('Impossible de charger les notifications.',
                    style: AppTextStyles.bodySmall),
              ),
              data: (list) {
                final items = list.map((d) {
                  final typeLabel =
                      AppFormatters.certTypeLabel(d.type).toLowerCase();
                  String title;
                  String subtitle;
                  IconData icon;
                  Color color;
                  switch (d.status) {
                    case 'pret':
                      title = 'Certificat prêt à télécharger';
                      subtitle = 'Votre $typeLabel (${d.id}) est disponible.';
                      icon = Icons.check_circle_outline;
                      color = AppColors.statusGreen;
                      break;
                    case 'valide':
                      title = 'Dossier validé';
                      subtitle = 'Votre $typeLabel (${d.id}) a été validé.';
                      icon = Icons.verified_outlined;
                      color = AppColors.statusGreen;
                      break;
                    case 'en_verification':
                      title = 'Dossier en vérification';
                      subtitle = 'Votre $typeLabel (${d.id}) est en cours.';
                      icon = Icons.hourglass_top_outlined;
                      color = AppColors.statusAmber;
                      break;
                    case 'rejete':
                      title = 'Dossier rejeté';
                      subtitle = 'Votre $typeLabel (${d.id}) a été rejeté.';
                      icon = Icons.cancel_outlined;
                      color = AppColors.statusRed;
                      break;
                    default:
                      title = 'Dossier reçu';
                      subtitle = 'Votre $typeLabel (${d.id}) a été soumis.';
                      icon = Icons.inbox_outlined;
                      color = AppColors.statusBlue;
                  }
                  return _NotifItem(
                      icon: icon, iconColor: color,
                      title: title, subtitle: subtitle);
                }).toList();

                if (items.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 72, height: 72,
                          decoration: BoxDecoration(
                            color: AppColors.background,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                              Icons.notifications_none_outlined,
                              size: 36, color: AppColors.textHint),
                        ),
                        const SizedBox(height: 16),
                        Text('Aucune notification',
                            style: AppTextStyles.labelMedium),
                        const SizedBox(height: 4),
                        Text('Vos dossiers s\'afficheront ici',
                            style: AppTextStyles.bodySmall),
                      ],
                    ),
                  );
                }

                return ListView.separated(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: items.length,
                  separatorBuilder: (_, __) =>
                      const Divider(height: 1, indent: 68),
                  itemBuilder: (_, i) {
                    final n = items[i];
                    return ListTile(
                      leading: Container(
                        width: 44, height: 44,
                        decoration: BoxDecoration(
                          color: n.iconColor.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(n.icon, color: n.iconColor, size: 22),
                      ),
                      title: Text(n.title, style: AppTextStyles.labelMedium),
                      subtitle: Text(n.subtitle,
                          style: AppTextStyles.caption,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis),
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 6),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
