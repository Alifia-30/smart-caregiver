import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// CareTrack Design System — Warm Minimalism
/// Based on Stitch design tokens (Plus Jakarta Sans + Zinc palette + Amber accent)
class AppColors {
  AppColors._();

  // ── Surface / Background ──────────────────────────────
  static const Color background = Color(0xFFFDF8F8);
  static const Color surfaceLowest = Color(0xFFFFFFFF);
  static const Color surfaceLow = Color(0xFFF7F3F2);
  static const Color surface = Color(0xFFF1EDED);
  static const Color surfaceHigh = Color(0xFFEBE7E7);
  static const Color surfaceHighest = Color(0xFFE5E2E1);
  static const Color surfaceDim = Color(0xFFDDD9D9);

  // ── Content ───────────────────────────────────────────
  static const Color onBackground = Color(0xFF1C1B1C);
  static const Color onSurface = Color(0xFF1C1B1C);
  static const Color onSurfaceVariant = Color(0xFF47464B);
  static const Color outline = Color(0xFF77767B);
  static const Color outlineVariant = Color(0xFFC8C5CB);

  // ── Primary ───────────────────────────────────────────
  static const Color primary = Color(0xFF18181B);       // Zinc-900
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFF1B1B1E);
  static const Color primaryFixed = Color(0xFFE4E1E6);

  // ── Secondary ─────────────────────────────────────────
  static const Color secondary = Color(0xFF71717A);     // Zinc-500
  static const Color secondaryContainer = Color(0xFFE3E1EC);
  static const Color onSecondaryContainer = Color(0xFF63646C);

  // ── Accent (Amber) ────────────────────────────────────
  static const Color accent = Color(0xFFFBBF24);        // Amber-400
  static const Color accentDark = Color(0xFFF59E0B);

  // ── Error ─────────────────────────────────────────────
  static const Color error = Color(0xFFBA1A1A);
  static const Color errorContainer = Color(0xFFFFDAD6);
  static const Color onError = Color(0xFFFFFFFF);

  // ── Status ────────────────────────────────────────────
  static const Color statusGood = Color(0xFF16A34A);
  static const Color statusWarning = Color(0xFFF59E0B);
  static const Color statusDanger = Color(0xFFDC2626);
  static const Color statusInfo = Color(0xFF2563EB);
}

class AppTextStyles {
  AppTextStyles._();

  static TextStyle get display => GoogleFonts.plusJakartaSans(
    fontSize: 30,
    fontWeight: FontWeight.w700,
    letterSpacing: -0.6,
    color: AppColors.onBackground,
    height: 38 / 30,
  );

  static TextStyle get headlineLg => GoogleFonts.plusJakartaSans(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.24,
    color: AppColors.onBackground,
    height: 32 / 24,
  );

  static TextStyle get headlineMd => GoogleFonts.plusJakartaSans(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: AppColors.onBackground,
    height: 28 / 20,
  );

  static TextStyle get bodyLg => GoogleFonts.plusJakartaSans(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    color: AppColors.onSurface,
    height: 28 / 18,
  );

  static TextStyle get bodyMd => GoogleFonts.plusJakartaSans(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: AppColors.onSurface,
    height: 24 / 16,
  );

  static TextStyle get labelMd => GoogleFonts.plusJakartaSans(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.14,
    color: AppColors.onSurface,
    height: 20 / 14,
  );

  static TextStyle get labelSm => GoogleFonts.plusJakartaSans(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: AppColors.onSurfaceVariant,
    height: 16 / 12,
  );
}

class AppTheme {
  AppTheme._();

  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      textTheme: GoogleFonts.plusJakartaSansTextTheme(),
      scaffoldBackgroundColor: AppColors.background,
      colorScheme: const ColorScheme.light(
        primary: AppColors.primary,
        onPrimary: AppColors.onPrimary,
        primaryContainer: AppColors.primaryFixed,
        secondary: AppColors.secondary,
        secondaryContainer: AppColors.secondaryContainer,
        surface: AppColors.surfaceLowest,
        onSurface: AppColors.onSurface,
        error: AppColors.error,
        onError: AppColors.onError,
        outline: AppColors.outline,
        outlineVariant: AppColors.outlineVariant,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.background,
        elevation: 0,
        scrolledUnderElevation: 0,
        iconTheme: const IconThemeData(color: AppColors.onBackground),
        titleTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: AppColors.onBackground,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: AppColors.onPrimary,
          minimumSize: const Size.fromHeight(52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 0,
          textStyle: AppTextStyles.labelMd.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          minimumSize: const Size.fromHeight(52),
          side: const BorderSide(color: AppColors.outlineVariant),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: AppTextStyles.labelMd.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surfaceLow,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.outlineVariant),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.outlineVariant),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.error),
        ),
        labelStyle: AppTextStyles.labelMd.copyWith(
          color: AppColors.onSurfaceVariant,
        ),
        hintStyle: AppTextStyles.bodyMd.copyWith(
          color: AppColors.outline,
        ),
      ),
      cardTheme: CardThemeData(
        color: AppColors.surfaceLowest,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        margin: EdgeInsets.zero,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.surfaceLowest,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.outline,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.outlineVariant,
        thickness: 1,
        space: 0,
      ),
    );
  }
}
