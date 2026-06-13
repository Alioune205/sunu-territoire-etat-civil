import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/providers/profile_state_provider.dart';

class ProfileCompletionScreen extends ConsumerStatefulWidget {
  const ProfileCompletionScreen({super.key});

  @override
  ConsumerState<ProfileCompletionScreen> createState() => _ProfileCompletionScreenState();
}

class _ProfileCompletionScreenState extends ConsumerState<ProfileCompletionScreen> {
  bool _rectoUploaded = false;
  bool _versoUploaded = false;
  bool _isUploadingRecto = false;
  bool _isUploadingVerso = false;
  bool _hasUnsavedChanges = false;

  void _simulateUpload(bool isRecto) {
    if (isRecto) {
      setState(() => _isUploadingRecto = true);
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          setState(() {
            _isUploadingRecto = false;
            _rectoUploaded = true;
            _hasUnsavedChanges = true;
          });
        }
      });
    } else {
      setState(() => _isUploadingVerso = true);
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          setState(() {
            _isUploadingVerso = false;
            _versoUploaded = true;
            _hasUnsavedChanges = true;
          });
        }
      });
    }
  }

  void _submit() {
    ref.read(cniUploadedProvider.notifier).state = true;
    setState(() => _hasUnsavedChanges = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Profil complété avec succès !'),
        backgroundColor: Color(0xFF059669),
      ),
    );
    context.pop();
  }

  Future<bool> _onWillPop() async {
    if (!_hasUnsavedChanges) return true;
    
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Modifications non enregistrées', style: TextStyle(fontFamily: 'Inter', fontWeight: FontWeight.bold)),
        content: const Text('Voulez-vous enregistrer vos modifications avant de quitter ?', style: TextStyle(fontFamily: 'Inter')),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Ne pas enregistrer', style: TextStyle(color: Colors.red)),
          ),
          ElevatedButton(
            onPressed: () {
              _submit(); // Save and pop is handled in submit
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0EA5E9),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Enregistrer', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  @override
  Widget build(BuildContext context) {
    final canSubmit = _rectoUploaded && _versoUploaded;

    return PopScope(
      canPop: !_hasUnsavedChanges,
      onPopInvoked: (didPop) async {
        if (didPop) return;
        final shouldPop = await _onWillPop();
        if (shouldPop && context.mounted) {
          context.pop();
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFFF8FAFC),
        appBar: AppBar(
          backgroundColor: Colors.white,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
            onPressed: () async {
              if (!_hasUnsavedChanges) {
                context.pop();
              } else {
                final shouldPop = await _onWillPop();
                if (shouldPop && context.mounted) {
                  context.pop();
                }
              }
            },
          ),
          title: const Text(
            'Compléter votre profil',
            style: TextStyle(
              color: Color(0xFF0F172A),
              fontSize: 16,
              fontWeight: FontWeight.w700,
              fontFamily: 'Inter',
            ),
          ),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Identité Nationale',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                  fontFamily: 'Inter',
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Afin de bénéficier de tous les services et d\'automatiser vos démarches, veuillez fournir une copie de votre pièce d\'identité.',
                style: TextStyle(
                  color: Color(0xFF475569),
                  fontSize: 14,
                  height: 1.5,
                  fontFamily: 'Inter',
                ),
              ),
              const SizedBox(height: 32),
              
              const Text(
                'Carte Nationale d\'Identité',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  fontFamily: 'Inter',
                ),
              ),
              const SizedBox(height: 16),
              
              _buildUploadCard(
                title: 'Recto de la CNI',
                subtitle: 'Photo côté face',
                isUploaded: _rectoUploaded,
                isUploading: _isUploadingRecto,
                onTap: () {
                  if (!_rectoUploaded && !_isUploadingRecto) {
                    _simulateUpload(true);
                  }
                },
              ),
              const SizedBox(height: 16),
              _buildUploadCard(
                title: 'Verso de la CNI',
                subtitle: 'Photo côté filiation',
                isUploaded: _versoUploaded,
                isUploading: _isUploadingVerso,
                onTap: () {
                  if (!_versoUploaded && !_isUploadingVerso) {
                    _simulateUpload(false);
                  }
                },
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
        bottomNavigationBar: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: canSubmit ? _submit : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: canSubmit ? const Color(0xFF0B285D) : const Color(0xFFE2E8F0),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 0,
                ),
                child: Text(
                  'Soumettre',
                  style: TextStyle(
                    color: canSubmit ? Colors.white : const Color(0xFF94A3B8),
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    fontFamily: 'Inter',
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildUploadCard({
    required String title,
    required String subtitle,
    required bool isUploaded,
    required bool isUploading,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: isUploaded ? const Color(0xFFF0FDF4) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isUploaded ? const Color(0xFF86EFAC) : const Color(0xFFE2E8F0),
            width: isUploaded ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.02),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUploaded ? const Color(0xFFDCFCE7) : const Color(0xFFF1F5F9),
                shape: BoxShape.circle,
              ),
              child: isUploading 
                  ? const SizedBox(
                      width: 24, height: 24,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0EA5E9)),
                    )
                  : Icon(
                      isUploaded ? Icons.check_circle_rounded : Icons.document_scanner_rounded,
                      color: isUploaded ? const Color(0xFF16A34A) : const Color(0xFF64748B),
                      size: 24,
                    ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: isUploaded ? const Color(0xFF166534) : const Color(0xFF0F172A),
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      fontFamily: 'Inter',
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isUploaded ? 'Document ajouté' : subtitle,
                    style: TextStyle(
                      color: isUploaded ? const Color(0xFF15803D) : const Color(0xFF64748B),
                      fontSize: 13,
                      fontFamily: 'Inter',
                    ),
                  ),
                ],
              ),
            ),
            if (!isUploaded && !isUploading)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(100),
                ),
                child: const Text(
                  'Ajouter',
                  style: TextStyle(
                    color: Color(0xFF2563EB),
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    fontFamily: 'Inter',
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
