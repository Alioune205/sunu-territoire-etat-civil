class DossierModel {
  final String id;
  final String type;
  final String status;
  final DateTime createdAt;
  final String? communeNom;
  final String? beneficiaryNom;
  final int? fraisFCFA;

  const DossierModel({
    required this.id,
    required this.type,
    required this.status,
    required this.createdAt,
    this.communeNom,
    this.beneficiaryNom,
    this.fraisFCFA,
  });

  factory DossierModel.fromJson(Map<String, dynamic> json) => DossierModel(
        id: json['id'] as String? ?? '',
        type: json['type'] as String? ?? '',
        status: json['status'] as String? ?? 'soumis',
        createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
            DateTime.now(),
        communeNom: json['commune_nom'] as String?,
        beneficiaryNom: json['beneficiary_nom'] as String?,
        fraisFCFA: json['frais'] as int?,
      );
}
