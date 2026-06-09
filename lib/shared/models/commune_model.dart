// Modèles de données pour le select cascadé Région → Département → Commune.
// Chargés depuis assets/data/senegal_communes.json

class CommuneModel {
  final String id;
  final String nom;

  const CommuneModel({required this.id, required this.nom});

  factory CommuneModel.fromJson(Map<String, dynamic> json) =>
      CommuneModel(id: json['id'] as String, nom: json['nom'] as String);

  @override
  String toString() => nom;
}

class DepartementModel {
  final String id;
  final String nom;
  final List<CommuneModel> communes;

  const DepartementModel({
    required this.id,
    required this.nom,
    required this.communes,
  });

  factory DepartementModel.fromJson(Map<String, dynamic> json) =>
      DepartementModel(
        id: json['id'] as String,
        nom: json['nom'] as String,
        communes: (json['communes'] as List)
            .map((c) => CommuneModel.fromJson(c as Map<String, dynamic>))
            .toList(),
      );
}

class RegionModel {
  final String id;
  final String nom;
  final List<DepartementModel> departements;

  const RegionModel({
    required this.id,
    required this.nom,
    required this.departements,
  });

  factory RegionModel.fromJson(Map<String, dynamic> json) => RegionModel(
        id: json['id'] as String,
        nom: json['nom'] as String,
        departements: (json['departements'] as List)
            .map((d) => DepartementModel.fromJson(d as Map<String, dynamic>))
            .toList(),
      );
}
