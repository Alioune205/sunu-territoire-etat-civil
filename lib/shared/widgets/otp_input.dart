import 'package:flutter/material.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';

/// Widget OTP 6 cases — utilisé sur S02B, S05
class OtpInput extends StatelessWidget {
  final TextEditingController controller;
  final void Function(String) onChanged;
  final void Function(String)? onCompleted;
  final bool hasError;

  const OtpInput({
    super.key,
    required this.controller,
    required this.onChanged,
    this.onCompleted,
    this.hasError = false,
  });

  @override
  Widget build(BuildContext context) {
    return PinCodeTextField(
      appContext: context,
      length: 6,
      controller: controller,
      keyboardType: TextInputType.number,
      animationType: AnimationType.fade,
      autoFocus: true,
      enableActiveFill: true,
      obscureText: false,
      pinTheme: PinTheme(
        shape: PinCodeFieldShape.box,
        borderRadius: BorderRadius.circular(10),
        fieldHeight: 52,
        fieldWidth: 46,
        // État normal
        inactiveColor: AppColors.border,
        inactiveFillColor: AppColors.surface,
        // Focus
        selectedColor: AppColors.primary,
        selectedFillColor: AppColors.surface,
        // Rempli
        activeColor: hasError ? AppColors.error : AppColors.secondary,
        activeFillColor: hasError ? AppColors.errorLight : AppColors.successLight,
        // Erreur globale
        errorBorderColor: AppColors.error,
      ),
      textStyle: AppTextStyles.otpDigit,
      cursorColor: AppColors.primary,
      onChanged: onChanged,
      onCompleted: onCompleted,
      // Pas de message d'erreur intégré — géré par le parent
      errorAnimationController: null,
    );
  }
}

/// Ligne "Renvoyer le code" avec countdown 60s
class OtpResendRow extends StatefulWidget {
  final VoidCallback onResend;
  final int cooldownSeconds;

  const OtpResendRow({
    super.key,
    required this.onResend,
    this.cooldownSeconds = 60,
  });

  @override
  State<OtpResendRow> createState() => _OtpResendRowState();
}

class _OtpResendRowState extends State<OtpResendRow> {
  late int _remaining;
  bool _canResend = false;

  @override
  void initState() {
    super.initState();
    _remaining = widget.cooldownSeconds;
    _startCountdown();
  }

  void _startCountdown() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (!mounted) return false;
      setState(() {
        _remaining--;
        if (_remaining <= 0) {
          _remaining = 0;
          _canResend = true;
        }
      });
      return _remaining > 0;
    });
  }

  void _handleResend() {
    setState(() {
      _remaining = widget.cooldownSeconds;
      _canResend = false;
    });
    _startCountdown();
    widget.onResend();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Vous n\'avez pas reçu le code ? ',
          style: AppTextStyles.bodySmall,
        ),
        if (_canResend)
          GestureDetector(
            onTap: _handleResend,
            child: Text(
              'Renvoyer',
              style: AppTextStyles.link,
            ),
          )
        else
          Text(
            'Renvoyer (${_remaining}s)',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textHint,
            ),
          ),
      ],
    );
  }
}
