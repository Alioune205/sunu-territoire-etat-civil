import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/layout/main_scaffold.dart';

// ── Auth screens
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/welcome_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/otp_verification_screen.dart';
import '../../features/auth/presentation/screens/register_step1_screen.dart';
import '../../features/auth/presentation/screens/register_step2_screen.dart';
import '../../features/auth/presentation/screens/register_step3_screen.dart';
import '../../features/auth/presentation/screens/register_step4_screen.dart';

// ── Home
import '../../features/home/presentation/screens/home_screen.dart';

// ── Certificates — Naissance
import '../../features/certificates/naissance/presentation/screens/beneficiary_choice_screen.dart';
import '../../features/certificates/naissance/presentation/screens/recap_self_screen.dart';
import '../../features/certificates/naissance/presentation/screens/other_person_screen.dart';
import '../../features/certificates/naissance/presentation/screens/recap_other_screen.dart';

// ── Certificates — Décès
import '../../features/certificates/deces/presentation/screens/deces_form_screen.dart';
import '../../features/certificates/deces/presentation/screens/deces_recap_screen.dart';

// ── Certificates — Mariage
import '../../features/certificates/mariage/presentation/screens/mariage_form_screen.dart';
import '../../features/certificates/mariage/presentation/screens/mariage_recap_screen.dart';

// ── Payment
import '../../features/payment/presentation/screens/payment_screen.dart';
import '../../features/payment/presentation/screens/payment_success_screen.dart';

// ── Dossiers
import '../../features/dossiers/presentation/screens/dossiers_list_screen.dart';
import '../../features/dossiers/presentation/screens/dossier_detail_screen.dart';

// ── Profile
import '../../features/profile/presentation/screens/profile_screen.dart';

/// Noms de routes — utiliser ces constantes partout (jamais de chaînes en dur)
abstract class AppRoutes {
  // Auth
  static const splash = '/';
  static const welcome = '/welcome';
  static const login = '/login';
  static const otpVerification = '/otp-verification';
  static const registerStep1 = '/register/step1';
  static const registerStep2 = '/register/step2';
  static const registerStep3 = '/register/step3';
  static const registerStep4 = '/register/step4';

  // Shell (bottom nav)
  static const home = '/home';
  static const dossiers = '/dossiers';
  static const profile = '/profile';

  // Naissance
  static const naissanceBeneficiary = '/certificates/naissance/beneficiary';
  static const naissanceRecapSelf = '/certificates/naissance/recap-self';
  static const naissanceOtherPerson = '/certificates/naissance/other-person';
  static const naissanceRecapOther = '/certificates/naissance/recap-other';

  // Décès
  static const decesForm = '/certificates/deces/form';
  static const decesRecap = '/certificates/deces/recap';

  // Mariage
  static const mariageForm = '/certificates/mariage/form';
  static const mariageRecap = '/certificates/mariage/recap';

  // Paiement
  static const payment = '/payment';
  static const paymentSuccess = '/payment/success';

  // Dossier détail
  static const dossierDetail = '/dossiers/:id';
  static String dossierDetailPath(String id) => '/dossiers/$id';
}

/// Provider du router — consommé dans MaterialApp.router
final appRouterProvider = Provider.family<GoRouter, String>((ref, initialRoute) {
  return GoRouter(
    initialLocation: initialRoute,
    debugLogDiagnostics: true,
    redirect: _globalRedirect,
    errorBuilder: (context, state) => _ErrorScreen(error: state.error),
    routes: [
      // ── Splash ─────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.splash,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const SplashScreen(),
        ),
      ),

      // ── Welcome ────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.welcome,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const WelcomeScreen(),
        ),
      ),

      // ── Auth ────────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.login,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const LoginScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.otpVerification,
        pageBuilder: (context, state) {
          final phone = state.extra as String? ?? '';
          return _slidePage(
            state: state,
            child: OtpVerificationScreen(phone: phone),
          );
        },
      ),
      GoRoute(
        path: AppRoutes.registerStep1,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const RegisterStep1Screen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.registerStep2,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: RegisterStep2Screen(registrationData: data),
          );
        },
      ),
      GoRoute(
        path: AppRoutes.registerStep3,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: RegisterStep3Screen(registrationData: data),
          );
        },
      ),
      GoRoute(
        path: AppRoutes.registerStep4,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: RegisterStep4Screen(registrationData: data),
          );
        },
      ),

      // ── Shell (Bottom Nav) ──────────────────────────────────
      ShellRoute(
        builder: (context, state, child) {
          final index = _shellIndex(state.matchedLocation);
          return MainScaffold(currentIndex: index, child: child);
        },
        routes: [
          GoRoute(
            path: AppRoutes.home,
            pageBuilder: (context, state) => _noTransitionPage(
              state: state,
              child: const HomeScreen(),
            ),
          ),
          GoRoute(
            path: AppRoutes.dossiers,
            pageBuilder: (context, state) => _noTransitionPage(
              state: state,
              child: const DossiersListScreen(),
            ),
            routes: [
              GoRoute(
                path: ':id',
                pageBuilder: (context, state) {
                  final id = state.pathParameters['id']!;
                  return _slidePage(
                    state: state,
                    child: DossierDetailScreen(dossierId: id),
                  );
                },
              ),
            ],
          ),
          GoRoute(
            path: AppRoutes.profile,
            pageBuilder: (context, state) => _noTransitionPage(
              state: state,
              child: const ProfileScreen(),
            ),
          ),
        ],
      ),

      // ── Certificat de naissance ─────────────────────────────
      GoRoute(
        path: AppRoutes.naissanceBeneficiary,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const BeneficiaryChoiceScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.naissanceRecapSelf,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const RecapSelfScreen(),
        ),
        routes: [
          GoRoute(
            path: 'recap',
            pageBuilder: (context, state) {
              final data = state.extra as Map<String, dynamic>? ?? {};
              return _slidePage(
                state: state,
                child: RecapOtherScreen(formData: data),
              );
            },
          ),
        ],
      ),
      GoRoute(
        path: AppRoutes.naissanceOtherPerson,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const OtherPersonScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.naissanceRecapOther,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: RecapOtherScreen(formData: data),
          );
        },
      ),

      // ── Certificat de décès ─────────────────────────────────
      GoRoute(
        path: AppRoutes.decesForm,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const DecesFormScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.decesRecap,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: DecesRecapScreen(formData: data),
          );
        },
      ),

      // ── Certificat de mariage ───────────────────────────────
      GoRoute(
        path: AppRoutes.mariageForm,
        pageBuilder: (context, state) => _slidePage(
          state: state,
          child: const MariageFormScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.mariageRecap,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: MariageRecapScreen(formData: data),
          );
        },
      ),

      // ── Paiement ────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.payment,
        pageBuilder: (context, state) {
          final data = state.extra as Map<String, dynamic>? ?? {};
          return _slidePage(
            state: state,
            child: PaymentScreen(paymentData: data),
          );
        },
      ),
      GoRoute(
        path: AppRoutes.paymentSuccess,
        pageBuilder: (context, state) {
          final dossierId = state.extra as String? ?? '';
          return _slidePage(
            state: state,
            child: PaymentSuccessScreen(dossierId: dossierId),
          );
        },
      ),
    ],
  );
});

// ── Redirect global ────────────────────────────────────────────────────────────
// Pas de vérification async ici (lente) — la navigation auth est gérée
// par SplashScreen (token local) et par chaque écran protégé.
Future<String?> _globalRedirect(BuildContext context, GoRouterState state) async {
  return null;
}

// ── Index shell selon la route active ─────────────────────────────────────────
int _shellIndex(String location) {
  if (location.startsWith('/dossiers')) return 1;
  if (location.startsWith('/profile')) return 2;
  return 0; // /home par défaut
}

// ── Builders de pages ──────────────────────────────────────────────────────────

/// Page avec transition slide horizontal (standard TERANGA)
CustomTransitionPage<void> _slidePage({
  required GoRouterState state,
  required Widget child,
}) {
  return CustomTransitionPage<void>(
    key: state.pageKey,
    child: child,
    transitionDuration: const Duration(milliseconds: 300),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      const begin = Offset(1.0, 0.0);
      const end = Offset.zero;
      const curve = Curves.easeInOut;
      final tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
      return SlideTransition(
        position: animation.drive(tween),
        child: child,
      );
    },
  );
}

/// Page sans transition (tabs bottom nav)
NoTransitionPage<void> _noTransitionPage({
  required GoRouterState state,
  required Widget child,
}) {
  return NoTransitionPage<void>(key: state.pageKey, child: child);
}

// ── Écran d'erreur ─────────────────────────────────────────────────────────────
class _ErrorScreen extends StatelessWidget {
  final Exception? error;
  const _ErrorScreen({this.error});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Color(0xFFEF4444)),
              const SizedBox(height: 16),
              const Text(
                'Page introuvable',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B2A6B),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                error?.toString() ?? 'Une erreur est survenue.',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Color(0xFF6B7280)),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => context.go(AppRoutes.home),
                child: const Text('Retour à l\'accueil'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
