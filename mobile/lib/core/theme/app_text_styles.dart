import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// Styles typographiques TERANGA CIVIL — Poppins uniquement.
abstract class AppTextStyles {
  AppTextStyles._();

  static TextStyle get displayLarge => GoogleFonts.poppins(
        fontSize: 32, fontWeight: FontWeight.w700,
        color: AppColors.textPrimary, height: 1.2);

  static TextStyle get displayMedium => GoogleFonts.poppins(
        fontSize: 28, fontWeight: FontWeight.w700,
        color: AppColors.textPrimary, height: 1.25);

  static TextStyle get headlineLarge => GoogleFonts.poppins(
        fontSize: 24, fontWeight: FontWeight.w700,
        color: AppColors.textPrimary, height: 1.3);

  static TextStyle get headlineMedium => GoogleFonts.poppins(
        fontSize: 20, fontWeight: FontWeight.w600,
        color: AppColors.textPrimary, height: 1.35);

  static TextStyle get headlineSmall => GoogleFonts.poppins(
        fontSize: 18, fontWeight: FontWeight.w600,
        color: AppColors.textPrimary, height: 1.4);

  static TextStyle get appBarTitle => GoogleFonts.poppins(
        fontSize: 18, fontWeight: FontWeight.w600,
        color: AppColors.textOnPrimary, height: 1.4);

  static TextStyle get bodyLarge => GoogleFonts.poppins(
        fontSize: 16, fontWeight: FontWeight.w400,
        color: AppColors.textPrimary, height: 1.5);

  static TextStyle get bodyMedium => GoogleFonts.poppins(
        fontSize: 14, fontWeight: FontWeight.w400,
        color: AppColors.textPrimary, height: 1.5);

  static TextStyle get bodySmall => GoogleFonts.poppins(
        fontSize: 12, fontWeight: FontWeight.w400,
        color: AppColors.textSecondary, height: 1.5);

  static TextStyle get labelLarge => GoogleFonts.poppins(
        fontSize: 14, fontWeight: FontWeight.w600,
        color: AppColors.textPrimary, height: 1.4);

  static TextStyle get labelMedium => GoogleFonts.poppins(
        fontSize: 12, fontWeight: FontWeight.w500,
        color: AppColors.textSecondary, height: 1.4);

  static TextStyle get labelSmall => GoogleFonts.poppins(
        fontSize: 11, fontWeight: FontWeight.w500,
        color: AppColors.textSecondary, height: 1.4);

  static TextStyle get buttonPrimary => GoogleFonts.poppins(
        fontSize: 16, fontWeight: FontWeight.w600,
        color: AppColors.textOnPrimary, height: 1.4, letterSpacing: 0.3);

  static TextStyle get buttonDisabled => GoogleFonts.poppins(
        fontSize: 16, fontWeight: FontWeight.w600,
        color: AppColors.buttonDisabledText, height: 1.4, letterSpacing: 0.3);

  static TextStyle get inputText => GoogleFonts.poppins(
        fontSize: 14, fontWeight: FontWeight.w400,
        color: AppColors.textPrimary, height: 1.5);

  static TextStyle get inputLabel => GoogleFonts.poppins(
        fontSize: 13, fontWeight: FontWeight.w500,
        color: AppColors.textSecondary, height: 1.4);

  static TextStyle get inputHint => GoogleFonts.poppins(
        fontSize: 14, fontWeight: FontWeight.w400,
        color: AppColors.textHint, height: 1.5);

  static TextStyle get inputError => GoogleFonts.poppins(
        fontSize: 12, fontWeight: FontWeight.w400,
        color: AppColors.error, height: 1.4);

  static TextStyle get link => GoogleFonts.poppins(
        fontSize: 14, fontWeight: FontWeight.w500,
        color: AppColors.secondary, height: 1.5,
        decoration: TextDecoration.underline,
        decorationColor: AppColors.secondary);

  static TextStyle get linkPrimary => GoogleFonts.poppins(
        fontSize: 14, fontWeight: FontWeight.w500,
        color: AppColors.primary, height: 1.5,
        decoration: TextDecoration.underline,
        decorationColor: AppColors.primary);

  static TextStyle get badgeText => GoogleFonts.poppins(
        fontSize: 11, fontWeight: FontWeight.w600,
        height: 1.2, letterSpacing: 0.3);

  static TextStyle get caption => GoogleFonts.poppins(
        fontSize: 11, fontWeight: FontWeight.w400,
        color: AppColors.textSecondary, height: 1.5);

  static TextStyle get tagline => GoogleFonts.poppins(
        fontSize: 13, fontWeight: FontWeight.w400,
        color: AppColors.secondary, height: 1.5, letterSpacing: 0.5);

  static TextStyle get navLabel => GoogleFonts.poppins(
        fontSize: 10, fontWeight: FontWeight.w500, height: 1.2);

  static TextStyle get otpDigit => GoogleFonts.poppins(
        fontSize: 22, fontWeight: FontWeight.w700,
        color: AppColors.textPrimary, height: 1.2);

  static TextStyle get amount => GoogleFonts.poppins(
        fontSize: 20, fontWeight: FontWeight.w700,
        color: AppColors.primary, height: 1.2);

  static TextStyle get appNameBold => GoogleFonts.poppins(
        fontSize: 22, fontWeight: FontWeight.w700,
        color: AppColors.primary, height: 1.2, letterSpacing: 2);

  static TextStyle get appNameRegular => GoogleFonts.poppins(
        fontSize: 22, fontWeight: FontWeight.w400,
        color: AppColors.primary, height: 1.2, letterSpacing: 2);

  static TextStyle withColor(TextStyle base, Color color) =>
      base.copyWith(color: color);
}
