import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/router/app_router.dart';
import 'document_config.dart';

class DocumentRequestScreen extends StatefulWidget {
  final String documentId;
  const DocumentRequestScreen({super.key, required this.documentId});

  @override
  State<DocumentRequestScreen> createState() => _DocumentRequestScreenState();
}

class _DocumentRequestScreenState extends State<DocumentRequestScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));
    
    if (!mounted) return;
    setState(() => _isLoading = false);
    
    // Pass to success screen
    context.go(AppRoutes.paymentSuccess, extra: 'DOC-${DateTime.now().millisecondsSinceEpoch.toString().substring(5)}');
  }

  @override
  Widget build(BuildContext context) {
    final config = documentConfigs[widget.documentId];

    if (config == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Erreur')),
        body: const Center(child: Text('Document non trouvé')),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Color(0xFF0B285D), size: 20),
          onPressed: () => context.pop(),
        ),
        title: Text(
          config.title,
          style: const TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 18,
            fontWeight: FontWeight.w700,
            fontFamily: 'Inter',
            letterSpacing: -0.5,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Pièces à fournir',
                style: const TextStyle(
                  color: Color(0xFF1E293B),
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                  fontFamily: 'Inter',
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                config.description,
                style: const TextStyle(
                  color: Color(0xFF64748B),
                  fontSize: 14,
                  fontFamily: 'Inter',
                ),
              ),
              const SizedBox(height: 24),

              ...config.fields.map((field) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 20),
                  child: _buildField(field),
                );
              }).toList(),

              const SizedBox(height: 40),
              
              // SUBMIT BUTTON
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1B4A9C),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    elevation: 0,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                        )
                      : const Text(
                          'Soumettre la demande',
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
        ),
      ),
    );
  }

  Widget _buildField(DocumentField field) {
    if (field.type == 'file') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                field.label,
                style: const TextStyle(
                  color: Color(0xFF1E293B),
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  fontFamily: 'Inter',
                ),
              ),
              if (field.isRequired)
                const Text(' *', style: TextStyle(color: Color(0xFFEF4444))),
            ],
          ),
          if (field.helperText != null) ...[
            const SizedBox(height: 4),
            Text(
              field.helperText!,
              style: const TextStyle(
                color: Color(0xFF94A3B8),
                fontSize: 12,
                fontFamily: 'Inter',
              ),
            ),
          ],
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              children: [
                const Icon(Icons.cloud_upload_outlined, color: Color(0xFF3B82F6), size: 32),
                const SizedBox(height: 12),
                const Text(
                  'Appuyez pour uploader le fichier',
                  style: TextStyle(
                    color: Color(0xFF64748B),
                    fontSize: 13,
                    fontFamily: 'Inter',
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'PDF, JPG ou PNG (max 5 MB)',
                  style: TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                    fontFamily: 'Inter',
                  ),
                ),
              ],
            ),
          ),
        ],
      );
    }

    // Text or Number input
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              field.label,
              style: const TextStyle(
                color: Color(0xFF1E293B),
                fontSize: 14,
                fontWeight: FontWeight.w600,
                fontFamily: 'Inter',
              ),
            ),
            if (field.isRequired)
              const Text(' *', style: TextStyle(color: Color(0xFFEF4444))),
          ],
        ),
        if (field.helperText != null) ...[
          const SizedBox(height: 4),
          Text(
            field.helperText!,
            style: const TextStyle(
              color: Color(0xFF94A3B8),
              fontSize: 12,
              fontFamily: 'Inter',
            ),
          ),
        ],
        const SizedBox(height: 8),
        TextFormField(
          keyboardType: field.type == 'number' ? TextInputType.number : TextInputType.text,
          validator: (value) {
            if (field.isRequired && (value == null || value.isEmpty)) {
              return 'Ce champ est requis';
            }
            return null;
          },
          decoration: InputDecoration(
            hintText: 'Entrez ${field.label.toLowerCase()}',
            hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 14, fontFamily: 'Inter'),
            filled: true,
            fillColor: Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 1.5),
            ),
          ),
        ),
      ],
    );
  }
}
