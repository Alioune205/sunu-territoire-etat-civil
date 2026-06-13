import 'package:flutter/material.dart';

class UploadItemWidget extends StatefulWidget {
  final String title;
  
  const UploadItemWidget({super.key, required this.title});

  @override
  State<UploadItemWidget> createState() => _UploadItemWidgetState();
}

class _UploadItemWidgetState extends State<UploadItemWidget> {
  bool _isUploading = false;
  bool _isUploaded = false;

  void _simulateUpload() {
    if (_isUploaded || _isUploading) return;
    
    setState(() {
      _isUploading = true;
    });
    
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isUploading = false;
          _isUploaded = true;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _isUploaded ? const Color(0xFFF0FDF4) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _isUploaded ? const Color(0xFF86EFAC) : const Color(0xFFE2E8F0),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: _isUploaded ? const Color(0xFFDCFCE7) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(10),
            ),
            child: _isUploading
                ? const SizedBox(
                    width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0EA5E9)),
                  )
                : Icon(
                    _isUploaded ? Icons.check_circle_outline_rounded : Icons.description_outlined, 
                    color: _isUploaded ? const Color(0xFF16A34A) : const Color(0xFF64748B), 
                    size: 18,
                  ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              widget.title,
              style: TextStyle(
                color: _isUploaded ? const Color(0xFF166534) : const Color(0xFF1E293B),
                fontSize: 13,
                fontWeight: FontWeight.w600,
                fontFamily: 'Inter',
              ),
            ),
          ),
          const SizedBox(width: 12),
          if (!_isUploaded && !_isUploading)
            GestureDetector(
              onTap: _simulateUpload,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
                    Icon(Icons.upload_rounded, color: Colors.white, size: 14),
                    SizedBox(width: 4),
                    Text(
                      'Upload',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'Inter',
                      ),
                    ),
                  ],
                ),
              ),
            ),
          if (_isUploaded)
            const Text(
              'Ajouté',
              style: TextStyle(
                color: Color(0xFF16A34A),
                fontSize: 12,
                fontWeight: FontWeight.w600,
                fontFamily: 'Inter',
              ),
            ),
        ],
      ),
    );
  }
}
