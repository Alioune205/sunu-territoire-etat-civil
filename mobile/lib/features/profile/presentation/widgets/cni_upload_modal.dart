import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/profile_state_provider.dart';

void showCniUploadModal(BuildContext context, WidgetRef ref) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    useRootNavigator: true,
    backgroundColor: Colors.transparent,
    builder: (ctx) => const _CniUploadModal(),
  );
}

class _CniUploadModal extends ConsumerStatefulWidget {
  const _CniUploadModal();

  @override
  ConsumerState<_CniUploadModal> createState() => _CniUploadModalState();
}

class _CniUploadModalState extends ConsumerState<_CniUploadModal> {
  bool isRectoUploaded = false;
  bool isVersoUploaded = false;
  bool isSubmitting = false;

  void _simulateUpload(bool isRecto) {
    setState(() {
      if (isRecto) {
        isRectoUploaded = true;
      } else {
        isVersoUploaded = true;
      }
    });
  }

  void _submit() async {
    setState(() {
      isSubmitting = true;
    });

    await Future.delayed(const Duration(seconds: 1));
    
    if (mounted) {
      ref.read(cniUploadedProvider.notifier).state = true;
      Navigator.pop(context); // Close the bottom sheet
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Carte d'identité enregistrée avec succès !"),
          backgroundColor: Color(0xFF059669),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
        top: 24,
        left: 24,
        right: 24,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(32),
          topRight: Radius.circular(32),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFE2E8F0),
                borderRadius: BorderRadius.circular(10),
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Ajouter votre CNI',
            style: TextStyle(
              color: Color(0xFF0F172A),
              fontSize: 20,
              fontWeight: FontWeight.w800,
              fontFamily: 'Inter',
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            "Téléversez le recto et le verso de votre carte d'identité nationale pour valider votre compte.",
            style: TextStyle(
              color: Color(0xFF64748B),
              fontSize: 14,
              fontFamily: 'Inter',
              height: 1.4,
            ),
          ),
          const SizedBox(height: 24),
          
          // RECTO
          _UploadCard(
            title: 'Recto de la carte',
            isUploaded: isRectoUploaded,
            onTap: () => _simulateUpload(true),
          ),
          const SizedBox(height: 16),
          
          // VERSO
          _UploadCard(
            title: 'Verso de la carte',
            isUploaded: isVersoUploaded,
            onTap: () => _simulateUpload(false),
          ),
          const SizedBox(height: 32),
          
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: (isRectoUploaded && isVersoUploaded && !isSubmitting) ? _submit : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0EA5E9),
                disabledBackgroundColor: const Color(0xFFCBD5E1),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 0,
              ),
              child: isSubmitting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : const Text(
                      'Soumettre',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'Inter',
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

class _UploadCard extends StatelessWidget {
  final String title;
  final bool isUploaded;
  final VoidCallback onTap;

  const _UploadCard({required this.title, required this.isUploaded, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: isUploaded ? const Color(0xFFF0FDF4) : const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isUploaded ? const Color(0xFF86EFAC) : const Color(0xFFE2E8F0),
            width: 2,
            style: BorderStyle.solid,
          ),
        ),
        child: Column(
          children: [
            Icon(
              isUploaded ? Icons.check_circle_rounded : Icons.add_photo_alternate_rounded,
              color: isUploaded ? const Color(0xFF16A34A) : const Color(0xFF94A3B8),
              size: 32,
            ),
            const SizedBox(height: 12),
            Text(
              isUploaded ? '$title téléversé' : 'Appuyez pour uploader le $title',
              style: TextStyle(
                color: isUploaded ? const Color(0xFF16A34A) : const Color(0xFF64748B),
                fontSize: 14,
                fontWeight: FontWeight.w600,
                fontFamily: 'Inter',
              ),
            ),
          ],
        ),
      ),
    );
  }
}
