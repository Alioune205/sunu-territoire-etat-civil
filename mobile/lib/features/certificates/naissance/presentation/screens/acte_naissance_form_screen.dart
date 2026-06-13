import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../../core/theme/app_colors.dart';
import '../../../../../core/theme/app_text_styles.dart';

class ActeNaissanceFormScreen extends ConsumerStatefulWidget {
  const ActeNaissanceFormScreen({super.key});

  @override
  ConsumerState<ActeNaissanceFormScreen> createState() => _ActeNaissanceFormScreenState();
}

class _ActeNaissanceFormScreenState extends ConsumerState<ActeNaissanceFormScreen> {
  final TextEditingController _nomController = TextEditingController(text: 'Pathé Fall');
  String? _lienParente;
  
  bool _certificatUploaded = false;
  bool _cniPereUploaded = false;
  bool _cniMereUploaded = false;

  bool get _isFormValid =>
      _nomController.text.isNotEmpty &&
      _lienParente != null &&
      _certificatUploaded &&
      _cniPereUploaded &&
      _cniMereUploaded;

  @override
  void dispose() {
    _nomController.dispose();
    super.dispose();
  }

  void _simulateUpload(String docType) {
    setState(() {
      if (docType == 'certificat') _certificatUploaded = true;
      if (docType == 'cni_pere') _cniPereUploaded = true;
      if (docType == 'cni_mere') _cniMereUploaded = true;
    });
  }

  void _submitForm() {
    if (!_isFormValid) return;
    
    // Simulate submission to recap or directly to payment. 
    // Since this is a new document form, let's just push to a success/payment screen.
    // The user mentioned just having a form and a "Soumettre la demande" button.
    context.push('/payment', extra: {
      'documentId': 'cert_naissance',
      'documentName': 'Acte de naissance',
      'formData': {
        'nom': _nomController.text,
        'lienParente': _lienParente,
      },
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Acte de naissance'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Demande d\'acte de naissance', style: AppTextStyles.headlineLarge),
              const SizedBox(height: 8),
              Text(
                'Délai : 48h',
                style: AppTextStyles.bodySmall.copyWith(color: AppColors.primary),
              ),
              const SizedBox(height: 32),

              Text('Informations du demandeur', style: AppTextStyles.labelLarge),
              const SizedBox(height: 16),
              
              // Prénom et Nom (Pré-rempli)
              TextField(
                controller: _nomController,
                readOnly: true, // Pré-rempli par l'utilisateur
                decoration: InputDecoration(
                  labelText: 'Prénom et nom du demandeur',
                  filled: true,
                  fillColor: AppColors.surface,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: AppColors.border),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: AppColors.border),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Lien de parenté
              DropdownButtonFormField<String>(
                value: _lienParente,
                hint: const Text('Lien de parenté avec l\'enfant'),
                decoration: InputDecoration(
                  filled: true,
                  fillColor: AppColors.surface,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: AppColors.border),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: AppColors.border),
                  ),
                ),
                items: const [
                  DropdownMenuItem(value: 'Pere', child: Text('Père')),
                  DropdownMenuItem(value: 'Mere', child: Text('Mère')),
                ],
                onChanged: (value) {
                  setState(() {
                    _lienParente = value;
                  });
                },
              ),
              
              const SizedBox(height: 32),

              // Note d'alerte clarté
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFFECACA)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline_rounded, color: Color(0xFFDC2626), size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Assurez-vous que toutes les pièces jointes sont claires et lisibles pour éviter tout rejet de votre dossier.',
                        style: TextStyle(
                          color: Colors.red.shade900,
                          fontSize: 12,
                          height: 1.4,
                          fontFamily: 'Inter',
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              Text('Pièces justificatives', style: AppTextStyles.labelLarge),
              const SizedBox(height: 16),

              _buildUploadItem('Certificat d\'accouchement', _certificatUploaded, () => _simulateUpload('certificat')),
              const SizedBox(height: 12),
              _buildUploadItem('Carte d\'identité du père', _cniPereUploaded, () => _simulateUpload('cni_pere')),
              const SizedBox(height: 12),
              _buildUploadItem('Carte d\'identité de la mère', _cniMereUploaded, () => _simulateUpload('cni_mere')),

              const SizedBox(height: 40),

              // Bouton Soumettre
              SizedBox(
                width: double.infinity,
                child: GestureDetector(
                  onTap: _submitForm,
                  child: Container(
                    alignment: Alignment.center,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      gradient: _isFormValid ? const LinearGradient(
                        colors: [Color(0xFF0B285D), Color(0xFF1B4A9C)],
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                      ) : null,
                      color: _isFormValid ? null : const Color(0xFFE2E8F0),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Soumettre la demande',
                          style: TextStyle(
                            color: _isFormValid ? Colors.white : const Color(0xFF94A3B8),
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            fontFamily: 'Inter',
                          ),
                        ),
                        if (_isFormValid) ...[
                          const SizedBox(height: 4),
                          Text(
                            'Vos données sont cryptées et sécurisées',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.7),
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                              fontFamily: 'Inter',
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUploadItem(String title, bool isUploaded, VoidCallback onUpload) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isUploaded ? const Color(0xFFF0FDF4) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: isUploaded ? const Color(0xFF86EFAC) : const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: isUploaded ? const Color(0xFFDCFCE7) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              isUploaded ? Icons.check_circle_rounded : Icons.description_outlined,
              color: isUploaded ? const Color(0xFF16A34A) : const Color(0xFF64748B),
              size: 20,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              title,
              style: TextStyle(
                color: isUploaded ? const Color(0xFF166534) : const Color(0xFF1E293B),
                fontSize: 14,
                fontWeight: FontWeight.w600,
                fontFamily: 'Inter',
              ),
            ),
          ),
          const SizedBox(width: 16),
          if (!isUploaded)
            GestureDetector(
              onTap: onUpload,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0B285D), Color(0xFF1B4A9C)],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.upload_rounded, color: Colors.white, size: 16),
                    SizedBox(width: 4),
                    Text(
                      'Upload',
                      style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700, fontFamily: 'Inter'),
                    ),
                  ],
                ),
              ),
            )
          else
            const Text(
              'Ajouté',
              style: TextStyle(color: Color(0xFF16A34A), fontSize: 13, fontWeight: FontWeight.w700, fontFamily: 'Inter'),
            ),
        ],
      ),
    );
  }
}
