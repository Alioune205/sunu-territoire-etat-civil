import 'package:flutter/material.dart';

/// Palette de couleurs officielle TERANGA CIVIL.
/// À utiliser PARTOUT dans l'application — jamais de couleur codée en dur ailleurs.
abstract class AppColors {
  AppColors._();

  // ── Couleurs principales ─────────────────────────────────────────────────
  static const Color primary      = Color(0xFF1B2A6B); // Navy blue (logo exact)
  static const Color primaryLight = Color(0xFF2D3E8F); // Navy clair pour dégradés
  static const Color primaryDark  = Color(0xFF111D50); // Navy profond
  static const Color secondary    = Color(0xFF4CAF82); // Mint green (logo exact)
  static const Color secondaryDark = Color(0xFF3A9A6E); // Mint foncé

  // ── Or sénégalais (baobab) ───────────────────────────────────────────────
  static const Color gold      = Color(0xFFD4A853);
  static const Color goldLight = Color(0xFFFFF8E7);

  // ── Fond & surfaces ──────────────────────────────────────────────────────
  static const Color background = Color(0xFFF0F4FF); // Bleu perle très léger
  static const Color surface    = Color(0xFFFFFFFF);
  static const Color surfaceElevated = Color(0xFFF8FAFF); // Cartes légèrement bleutées

  // ── Textes ───────────────────────────────────────────────────────────────
  static const Color textPrimary   = Color(0xFF1B2A6B);
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color textHint      = Color(0xFF9CA3AF);
  static const Color textOnPrimary = Color(0xFFFFFFFF);

  // ── Statuts dossiers ─────────────────────────────────────────────────────
  static const Color statusAmber = Color(0xFFF59E0B);
  static const Color statusRed   = Color(0xFFEF4444);
  static const Color statusGreen = Color(0xFF4CAF82);
  static const Color statusBlue  = Color(0xFF3B82F6);

  // ── Backgrounds statuts (version claire) ─────────────────────────────────
  static const Color statusAmberLight = Color(0xFFFEF3C7);
  static const Color statusRedLight   = Color(0xFFFEE2E2);
  static const Color statusGreenLight = Color(0xFFD1FAE5);
  static const Color statusBlueLight  = Color(0xFFDBEAFE);

  // ── Bordures & séparateurs ───────────────────────────────────────────────
  static const Color border      = Color(0xFFE2E8F0);
  static const Color borderFocus = Color(0xFF1B2A6B);
  static const Color divider     = Color(0xFFF1F5F9);

  // ── États boutons ────────────────────────────────────────────────────────
  static const Color buttonDisabledBg   = Color(0xFFD1D5DB);
  static const Color buttonDisabledText = Color(0xFF9CA3AF);

  // ── Erreur / validation inline ───────────────────────────────────────────
  static const Color error      = Color(0xFFEF4444);
  static const Color errorLight = Color(0xFFFEE2E2);

  // ── Succès ───────────────────────────────────────────────────────────────
  static const Color success      = Color(0xFF4CAF82);
  static const Color successLight = Color(0xFFD1FAE5);

  // ── Overlay & ombres ─────────────────────────────────────────────────────
  static const Color overlay = Color(0x801B2A6B);
  static const Color shadow  = Color(0x1A1B2A6B);
  static const Color shadowStrong = Color(0x291B2A6B);

  // ── Transparent ──────────────────────────────────────────────────────────
  static const Color transparent = Colors.transparent;

  // ── Dégradés ─────────────────────────────────────────────────────────────
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF1B2A6B), Color(0xFF2D3E8F)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient primaryGradientVertical = LinearGradient(
    colors: [Color(0xFF1B2A6B), Color(0xFF243480)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient secondaryGradient = LinearGradient(
    colors: [Color(0xFF4CAF82), Color(0xFF3A9A6E)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFD4A853), Color(0xFFE8C070)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient headerGradient = LinearGradient(
    colors: [Color(0xFF1B2A6B), Color(0xFF1E3080), Color(0xFF243585)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    stops: [0.0, 0.5, 1.0],
  );
}
