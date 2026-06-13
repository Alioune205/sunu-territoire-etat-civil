import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/drafts_provider.dart';
import '../../../../core/router/app_router.dart';

class DocumentsScreen extends ConsumerWidget {
  const DocumentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final drafts = ref.watch(draftsProvider);

    final List<Map<String, dynamic>> categories = [
      {
        'id': 'etat_civil',
        'name': 'État civil',
        'icon': Icons.child_care_rounded,
        'color': const Color(0xFF2563EB), // Bleu
        'desc': 'Naissances, identité',
      },
      {
        'id': 'mariage',
        'name': 'Mariage',
        'icon': Icons.favorite_border_rounded,
        'color': const Color(0xFFDC2626), // Rouge
        'desc': 'Certificats de mariage, célibat',
      },
      {
        'id': 'deces',
        'name': 'Décès',
        'icon': Icons.church_outlined,
        'color': const Color(0xFF475569), // Ardoise
        'desc': 'Certificats et permis',
      },
      {
        'id': 'urbanisme',
        'name': 'Urbanisme',
        'icon': Icons.home_work_outlined,
        'color': const Color(0xFFC026D3), // Fuchsia
        'desc': 'Permis et autorisations',
      },
      {
        'id': 'moralite',
        'name': 'Moralité',
        'icon': Icons.verified_user_outlined,
        'color': const Color(0xFF059669), // Vert
        'desc': 'Résidence, légalisation',
      },
    ];

    final Map<String, List<Map<String, dynamic>>> documentsByCategory = {
      'etat_civil': [
        {'id': 'cert_naissance', 'name': 'Acte de naissance', 'desc': 'Pour les naissances de moins d\'un an', 'badges': ['PAYANT'], 'price': '500 FCFA', 'delay': '48h', 'categoryName': 'État civil'},
        {'id': 'extrait_naissance', 'name': 'Extrait de naissance', 'desc': 'Copie de l\'acte dans le registre', 'badges': [], 'price': 'Gratuit', 'delay': '48h', 'categoryName': 'État civil'},
        {'id': 'copie_litterale', 'name': 'Copie littérale', 'desc': 'Copie intégrale de l\'acte', 'badges': ['PAYANT'], 'price': '500 FCFA', 'delay': '48h', 'categoryName': 'État civil'},
      ],
      'mariage': [
        {'id': 'cert_mariage', 'name': 'Certificat de mariage', 'desc': 'Preuve officielle d\'union', 'badges': ['PAYANT'], 'price': '500 FCFA', 'delay': '48h', 'categoryName': 'Mariage'},
        {'id': 'cert_celibat', 'name': 'Certificat de célibat', 'desc': 'Attestation de non-mariage', 'badges': ['PRÉSENTIEL'], 'price': 'Gratuit', 'delay': 'Sur place', 'categoryName': 'Mariage'},
        {'id': 'cert_non_divorce', 'name': 'Certificat de non-divorce', 'desc': 'Prouver que le mariage est valide', 'badges': [], 'price': 'Gratuit', 'delay': '48h', 'categoryName': 'Mariage'},
      ],
      'deces': [
        {'id': 'cert_deces', 'name': 'Certificat de décès', 'desc': 'Acte de décès officiel', 'badges': [], 'price': 'Gratuit', 'delay': '48h', 'categoryName': 'Décès'},
        {'id': 'permis_inhumer', 'name': 'Permis d\'inhumer', 'desc': 'Autorisation pour inhumation', 'badges': ['PRÉSENTIEL', 'COMPLEXE'], 'price': 'Gratuit', 'delay': 'Immédiat', 'categoryName': 'Décès'},
      ],
      'urbanisme': [
        {'id': 'autorisation_construire', 'name': 'Autorisation de construire', 'desc': 'Permis de bâtir', 'badges': ['PAYANT', 'COMPLEXE'], 'price': 'Variable', 'delay': '1 mois', 'categoryName': 'Urbanisme'},
        {'id': 'permis_occuper', 'name': 'Permis d\'occuper', 'desc': 'Espace public/privé', 'badges': ['PAYANT'], 'price': 'Variable', 'delay': '15 jours', 'categoryName': 'Urbanisme'},
      ],
      'moralite': [
        {'id': 'bonne_vie_moeurs', 'name': 'Bonne vie et mœurs', 'desc': 'Attestation de moralité', 'badges': ['PRÉSENTIEL'], 'price': 'Gratuit', 'delay': 'Sur place', 'categoryName': 'Moralité'},
        {'id': 'cert_residence', 'name': 'Certificat de résidence', 'desc': 'Preuve de domicile', 'badges': [], 'price': 'Gratuit', 'delay': '24h', 'categoryName': 'Moralité'},
        {'id': 'legalisation', 'name': 'Légalisation', 'desc': 'Copies conformes', 'badges': ['PAYANT', 'PRÉSENTIEL'], 'price': '200 FCFA', 'delay': 'Immédiat', 'categoryName': 'Moralité'},
      ],
    };

    final mostRequested = [
      documentsByCategory['etat_civil']![1], // Extrait de naissance
      documentsByCategory['moralite']![1], // Certificat de résidence
      documentsByCategory['mariage']![1], // Certificat de célibat
      documentsByCategory['etat_civil']![0], // Acte de naissance
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // HEADER BLEU
            Container(
              decoration: const BoxDecoration(
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(32),
                  bottomRight: Radius.circular(32),
                ),
                gradient: LinearGradient(
                  colors: [Color(0xFF0B285D), Color(0xFF1B4A9C)],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
              padding: const EdgeInsets.fromLTRB(20, 56, 20, 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Documents',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                          fontFamily: 'Inter',
                          letterSpacing: -0.5,
                        ),
                      ),
                      GestureDetector(
                        onTap: () => context.push('/drafts'),
                        child: Stack(
                          clipBehavior: Clip.none,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.1),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.edit_document, color: Colors.white, size: 24),
                            ),
                            if (drafts.isNotEmpty)
                              Positioned(
                                top: -2,
                                right: -2,
                                child: Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(
                                    color: Colors.redAccent,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Text(
                                    '${drafts.length}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 10,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  // SEARCH BAR
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(100),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.05),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: TextField(
                      style: const TextStyle(color: Color(0xFF0F172A), fontSize: 14, fontFamily: 'Inter'),
                      decoration: InputDecoration(
                        hintText: 'Rechercher une démarche...',
                        hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13, fontFamily: 'Inter'),
                        prefixIcon: const Icon(Icons.search, color: Color(0xFF94A3B8), size: 18),
                        suffixIcon: Container(
                          margin: const EdgeInsets.all(6),
                          decoration: const BoxDecoration(
                            color: Color(0xFFF1F5F9),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.mic_none, color: Color(0xFF64748B), size: 16),
                        ),
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // LES PLUS DEMANDÉS
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.0),
              child: Text(
                'Les plus demandés',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  fontFamily: 'Inter',
                ),
              ),
            ),
            const SizedBox(height: 12),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 20),
              itemCount: mostRequested.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final doc = mostRequested[index];
                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.03),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                    border: Border.all(color: const Color(0xFFF1F5F9)),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              doc['name'] as String,
                              style: const TextStyle(
                                color: Color(0xFF0F172A),
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                fontFamily: 'Inter',
                              ),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                _MiniBadge(icon: Icons.folder_open, text: doc['categoryName'] as String, color: const Color(0xFF64748B)),
                                const SizedBox(width: 8),
                                _MiniBadge(icon: Icons.timer_outlined, text: doc['delay'] as String, color: const Color(0xFF10B981)),
                                const SizedBox(width: 8),
                                _MiniBadge(icon: Icons.payments_outlined, text: doc['price'] as String, color: const Color(0xFF0EA5E9)),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      GestureDetector(
                          onTap: () {
                            navigateToDocument(context, doc);
                          },
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(100),
                            gradient: const LinearGradient(
                              colors: [Color(0xFF0B285D), Color(0xFF1B4A9C)],
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                            ),
                          ),
                          child: const Text(
                            'Demander',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              fontFamily: 'Inter',
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),

            const SizedBox(height: 32),

            // CATÉGORIES
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.0),
              child: Text(
                'Catégories',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  fontFamily: 'Inter',
                ),
              ),
            ),
            const SizedBox(height: 12),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 100), // padding bottom avoids hiding content behind nav
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 1.1,
              ),
              itemCount: categories.length,
              itemBuilder: (context, index) {
                final cat = categories[index];
                return GestureDetector(
                  onTap: () {
                    context.push('/category_detail', extra: {
                      'category': cat,
                      'documents': documentsByCategory[cat['id']] ?? [],
                    });
                  },
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.03),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                      border: Border.all(color: const Color(0xFFF1F5F9)),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: (cat['color'] as Color).withValues(alpha: 0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(cat['icon'] as IconData, color: cat['color'] as Color, size: 28),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          cat['name'] as String,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Color(0xFF0F172A),
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            fontFamily: 'Inter',
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          cat['desc'] as String,
                          textAlign: TextAlign.center,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: Color(0xFF64748B),
                            fontSize: 11,
                            fontFamily: 'Inter',
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _MiniBadge extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color color;

  const _MiniBadge({required this.icon, required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: color, size: 12),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(
            color: color,
            fontSize: 10,
            fontWeight: FontWeight.w600,
            fontFamily: 'Inter',
          ),
        ),
      ],
    );
  }
}
