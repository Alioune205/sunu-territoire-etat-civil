class DocumentField {
  final String id;
  final String label;
  final String type; // 'text', 'number', 'file', 'select'
  final bool isRequired;
  final String? helperText;

  const DocumentField({
    required this.id,
    required this.label,
    this.type = 'text',
    this.isRequired = true,
    this.helperText,
  });
}

class DocumentConfig {
  final String id;
  final String title;
  final String description;
  final List<DocumentField> fields;

  const DocumentConfig({
    required this.id,
    required this.title,
    required this.description,
    required this.fields,
  });
}

final Map<String, DocumentConfig> documentConfigs = {
  // ── NAISSANCE ──
  'cert_naissance': DocumentConfig(
    id: 'cert_naissance',
    title: 'Certificat de naissance ou d\'accouchement',
    description: 'Délai : 48h.',
    fields: [
      DocumentField(id: 'certificat_accouchement', label: 'Certificat de naissance ou d\'accouchement', type: 'file', helperText: 'Délivré par l\'hôpital ou la sage-femme'),
      DocumentField(id: 'cni_parents', label: 'Pièces d\'identité des parents', type: 'file', helperText: 'Cartes nationales d\'identité (recto/verso)'),
    ],
  ),
  'extrait_naissance': DocumentConfig(
    id: 'extrait_naissance',
    title: 'Extrait / Copie littérale de naissance',
    description: 'Validité : 3 mois.',
    fields: [
      DocumentField(id: 'nom_requerant', label: 'Prénom et nom du requérant', type: 'text'),
      DocumentField(id: 'num_acte', label: 'Numéro de l\'acte dans le registre', type: 'number'),
      DocumentField(id: 'annee_declaration', label: 'Année de déclaration', type: 'number'),
    ],
  ),
  'non_inscription_naissance': DocumentConfig(
    id: 'non_inscription_naissance',
    title: 'Certificat de non-inscription de naissance',
    description: 'Au-delà d\'un an à compter de la naissance.',
    fields: [
      DocumentField(id: 'certificat_accouchement', label: 'Certificat de naissance ou d\'accouchement', type: 'file'),
      DocumentField(id: 'cni_declarant', label: 'Pièce d\'identité du déclarant', type: 'file'),
      DocumentField(id: 'cni_temoins', label: 'Pièces d\'identité de 2 témoins', type: 'file'),
    ],
  ),

  // ── MARIAGE ──
  'cert_mariage': DocumentConfig(
    id: 'cert_mariage',
    title: 'Certificat de mariage',
    description: 'Preuve officielle d\'union.',
    fields: [
      DocumentField(id: 'cni_epoux', label: 'Pièces d\'identité des époux', type: 'file'),
      DocumentField(id: 'num_acte', label: 'Numéro de l\'acte de mariage', type: 'number'),
    ],
  ),
  'cert_celibat': DocumentConfig(
    id: 'cert_celibat',
    title: 'Certificat de célibat',
    description: 'Attestation de non-mariage.',
    fields: [
      DocumentField(id: 'cni_requerant', label: 'Pièce d\'identité du requérant', type: 'file'),
      DocumentField(id: 'extrait_naissance', label: 'Extrait de naissance (- de 3 mois)', type: 'file'),
      DocumentField(id: 'cni_temoins', label: 'Pièces d\'identité de 2 témoins', type: 'file'),
    ],
  ),
  'cert_non_divorce': DocumentConfig(
    id: 'cert_non_divorce',
    title: 'Certificat de non-divorce',
    description: 'Prouver que le mariage est toujours valide.',
    fields: [
      DocumentField(id: 'cni_epoux', label: 'Pièces d\'identité des époux', type: 'file'),
      DocumentField(id: 'extrait_mariage', label: 'Extrait de mariage', type: 'file'),
    ],
  ),
  'cert_non_remariage': DocumentConfig(
    id: 'cert_non_remariage',
    title: 'Certificat de non-remariage',
    description: 'Pour veufs ou divorcés.',
    fields: [
      DocumentField(id: 'cni_requerant', label: 'Pièce d\'identité du requérant', type: 'file'),
      DocumentField(id: 'extrait_naissance', label: 'Extrait de naissance', type: 'file'),
      DocumentField(id: 'jugement_divorce', label: 'Jugement de divorce OU Certificat de décès du conjoint', type: 'file'),
    ],
  ),
  'cert_veuvage': DocumentConfig(
    id: 'cert_veuvage',
    title: 'Certificat de veuvage',
    description: 'Attestation du statut de veuf/veuve.',
    fields: [
      DocumentField(id: 'cni_requerant', label: 'Pièce d\'identité du requérant', type: 'file'),
      DocumentField(id: 'extrait_mariage', label: 'Extrait de mariage', type: 'file'),
      DocumentField(id: 'extrait_deces', label: 'Extrait de décès du conjoint', type: 'file'),
    ],
  ),

  // ── DECES ──
  'cert_deces': DocumentConfig(
    id: 'cert_deces',
    title: 'Certificat de décès',
    description: 'Acte de décès officiel.',
    fields: [
      DocumentField(id: 'certificat_genre_mort', label: 'Certificat de genre de mort', type: 'file', helperText: 'Délivré par le médecin'),
      DocumentField(id: 'cni_defunt', label: 'Pièce d\'identité du défunt', type: 'file'),
      DocumentField(id: 'cni_declarant', label: 'Pièce d\'identité du déclarant', type: 'file'),
    ],
  ),
  'permis_inhumer': DocumentConfig(
    id: 'permis_inhumer',
    title: 'Permis d\'inhumer / transfert',
    description: 'Autorisation pour inhumation.',
    fields: [
      DocumentField(id: 'certificat_deces', label: 'Certificat de décès', type: 'file'),
    ],
  ),
  'non_inscription_deces': DocumentConfig(
    id: 'non_inscription_deces',
    title: 'Certificat de non-inscription de décès',
    description: 'Pour décès non enregistrés à temps.',
    fields: [
      DocumentField(id: 'certificat_genre_mort', label: 'Certificat de genre de mort', type: 'file'),
      DocumentField(id: 'cni_declarant', label: 'Pièce d\'identité du déclarant', type: 'file'),
      DocumentField(id: 'cni_temoins', label: 'Pièces d\'identité de 2 témoins', type: 'file'),
    ],
  ),

  // ── URBANISME ──
  'autorisation_construire': DocumentConfig(
    id: 'autorisation_construire',
    title: 'Autorisation de construire',
    description: 'Permis de bâtir.',
    fields: [
      DocumentField(id: 'demande', label: 'Demande manuscrite', type: 'file', helperText: 'Adressée au Maire'),
      DocumentField(id: 'titre_propriete', label: 'Titre de propriété', type: 'file', helperText: 'Bail, Titre foncier, Permis d\'occuper...'),
      DocumentField(id: 'plan_archi', label: 'Plan architectural', type: 'file', helperText: 'Signé par un architecte agréé'),
      DocumentField(id: 'devis', label: 'Devis estimatif des travaux', type: 'file'),
      DocumentField(id: 'attestation', label: 'Attestation de conformité', type: 'file'),
    ],
  ),
  'permis_occuper': DocumentConfig(
    id: 'permis_occuper',
    title: 'Permis d\'occuper',
    description: 'Autorisation d\'occupation de l\'espace.',
    fields: [
      DocumentField(id: 'demande', label: 'Demande manuscrite', type: 'file', helperText: 'Adressée au Maire'),
      DocumentField(id: 'cni_demandeur', label: 'Copie CNI du demandeur', type: 'file'),
      DocumentField(id: 'plan_situation', label: 'Plan de situation du terrain', type: 'file'),
      DocumentField(id: 'quittance', label: 'Quittance de paiement', type: 'file', helperText: 'Paiement des frais de bornage'),
    ],
  ),

  // ── MORALITE ──
  'bonne_vie_moeurs': DocumentConfig(
    id: 'bonne_vie_moeurs',
    title: 'Certificat de bonne vie et mœurs',
    description: 'Attestation de moralité.',
    fields: [
      DocumentField(id: 'casier_judiciaire', label: 'Extrait de casier judiciaire', type: 'file', helperText: 'Moins de 3 mois'),
      DocumentField(id: 'extrait_naissance', label: 'Extrait de naissance', type: 'file'),
      DocumentField(id: 'cni_demandeur', label: 'Copie CNI', type: 'file'),
    ],
  ),
  'vie_entretien': DocumentConfig(
    id: 'vie_entretien',
    title: 'Certificat de vie et d\'entretien',
    description: 'Pour allocations familiales.',
    fields: [
      DocumentField(id: 'cni_declarant', label: 'Copie CNI du déclarant', type: 'file'),
      DocumentField(id: 'extraits_enfants', label: 'Extraits de naissance des enfants', type: 'file'),
    ],
  ),
  'indigence': DocumentConfig(
    id: 'indigence',
    title: 'Certificat d\'indigence',
    description: 'Attestation de faibles revenus.',
    fields: [
      DocumentField(id: 'demande', label: 'Demande adressée au Maire', type: 'file'),
      DocumentField(id: 'cni_demandeur', label: 'Copie CNI', type: 'file'),
      DocumentField(id: 'enquete', label: 'Rapport d\'enquête sociale ou Témoignage chef quartier', type: 'file'),
    ],
  ),
  'cert_residence': DocumentConfig(
    id: 'cert_residence',
    title: 'Certificat de résidence',
    description: 'Preuve de domicile.',
    fields: [
      DocumentField(id: 'cni', label: 'Copie de la CNI', type: 'file'),
      DocumentField(id: 'facture', label: 'Facture (Eau, Électricité) ou Certificat chef de quartier', type: 'file'),
    ],
  ),
  'legalisation': DocumentConfig(
    id: 'legalisation',
    title: 'Légalisation de documents',
    description: 'Authentification de copies conformes.',
    fields: [
      DocumentField(id: 'document_original', label: 'Document original scanné', type: 'file'),
      DocumentField(id: 'document_copie', label: 'Copie à légaliser', type: 'file'),
    ],
  ),
};
