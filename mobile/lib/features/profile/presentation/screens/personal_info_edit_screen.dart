import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/providers/profile_state_provider.dart';

final Map<String, List<String>> _regionsEtCommunes = {
  'Dakar': ['Dakar Plateau', 'Médina', 'Fass-Colobane', 'Gueule Tapée', 'Point E', 'Yoff', 'Ngor', 'Ouakam', 'Grand Dakar'],
  'Thiès': ['Thiès Nord', 'Thiès Sud', 'Thiès Ouest', 'Mbour', 'Tivaouane'],
  'Diourbel': ['Diourbel', 'Bambey', 'Mbacké', 'Touba'],
  'Saint-Louis': ['Saint-Louis', 'Richard-Toll', 'Dagana', 'Podor'],
  'Ziguinchor': ['Ziguinchor', 'Bignona', 'Oussouye'],
  'Kaolack': ['Kaolack', 'Nioro du Rip', 'Guinguinéo'],
  'Kolda': ['Kolda', 'Vélingara', 'Médina Yoro Foulah'],
  'Tambacounda': ['Tambacounda', 'Koumpentoum', 'Goudiry', 'Bakel'],
  'Fatick': ['Fatick', 'Foundiougne', 'Gossas'],
  'Kaffrine': ['Kaffrine', 'Birkelane', 'Koungheul', 'Malem Hodar'],
  'Kédougou': ['Kédougou', 'Salémata', 'Saraya'],
  'Matam': ['Matam', 'Kanel', 'Ranérou'],
  'Louga': ['Louga', 'Kébémer', 'Linguère'],
  'Sédhiou': ['Sédhiou', 'Bounkiling', 'Goudomp'],
};

class PersonalInfoEditScreen extends ConsumerStatefulWidget {
  const PersonalInfoEditScreen({super.key});

  @override
  ConsumerState<PersonalInfoEditScreen> createState() => _PersonalInfoEditScreenState();
}

class _PersonalInfoEditScreenState extends ConsumerState<PersonalInfoEditScreen> {
  late TextEditingController _nomCtr;
  late TextEditingController _prenomCtr;
  late TextEditingController _phoneCtr;
  
  String? _selectedRegion;
  String? _selectedCommune;

  bool _hasUnsavedChanges = false;

  @override
  void initState() {
    super.initState();
    final personalInfo = ref.read(personalInfoProvider);
    _nomCtr = TextEditingController(text: personalInfo['nom']);
    _prenomCtr = TextEditingController(text: personalInfo['prenom']);
    _phoneCtr = TextEditingController(text: personalInfo['phone']);
    _selectedRegion = personalInfo['region'];
    _selectedCommune = personalInfo['commune'];

    _nomCtr.addListener(_onChange);
    _prenomCtr.addListener(_onChange);
    _phoneCtr.addListener(_onChange);
  }

  void _onChange() {
    if (!_hasUnsavedChanges) {
      setState(() => _hasUnsavedChanges = true);
    }
  }

  @override
  void dispose() {
    _nomCtr.dispose();
    _prenomCtr.dispose();
    _phoneCtr.dispose();
    super.dispose();
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
            onPressed: () => Navigator.pop(ctx, true), // Ne pas enregistrer (pop dialog, return true to pop screen)
            child: const Text('Ne pas enregistrer', style: TextStyle(color: Colors.red)),
          ),
          ElevatedButton(
            onPressed: () {
              _save();
              Navigator.pop(ctx, true); // Enregistrer et quitter (pop dialog, return true to pop screen)
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

  void _save() {
    final personalInfo = ref.read(personalInfoProvider);
    ref.read(personalInfoProvider.notifier).state = {
      ...personalInfo,
      'nom': _nomCtr.text,
      'prenom': _prenomCtr.text,
      'phone': _phoneCtr.text,
      'region': _selectedRegion,
      'commune': _selectedCommune,
    };
    setState(() => _hasUnsavedChanges = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Modifications enregistrées'), backgroundColor: Color(0xFF059669)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cniUploaded = ref.watch(cniUploadedProvider);
    final personalInfo = ref.watch(personalInfoProvider);
    final nin = personalInfo['nin'] as String;
    final registre = nin.length >= 3 ? nin.substring(nin.length - 3) : nin;

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
            'Informations personnelles',
            style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.w700, fontFamily: 'Inter'),
          ),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildTextField('Prénom', _prenomCtr),
              const SizedBox(height: 16),
              _buildTextField('Nom', _nomCtr),
              const SizedBox(height: 16),
              _buildTextField('Téléphone', _phoneCtr, keyboardType: TextInputType.phone),
              const SizedBox(height: 16),
              
              if (cniUploaded) ...[
                _buildDisabledField('NIN', nin),
                const SizedBox(height: 16),
                _buildDisabledField('Numéro de registre', registre),
                const SizedBox(height: 16),
              ],

              const Text('Région', style: TextStyle(color: Color(0xFF0F172A), fontSize: 14, fontWeight: FontWeight.w600, fontFamily: 'Inter')),
              const SizedBox(height: 8),
              _buildRegionDropdown(),
              const SizedBox(height: 16),
              
              const Text('Commune', style: TextStyle(color: Color(0xFF0F172A), fontSize: 14, fontWeight: FontWeight.w600, fontFamily: 'Inter')),
              const SizedBox(height: 8),
              _buildCommuneDropdown(),
              const SizedBox(height: 40),
            ],
          ),
        ),
        bottomNavigationBar: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: ElevatedButton(
              onPressed: () {
                _save();
                context.pop();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0EA5E9),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 0,
              ),
              child: const Text('Enregistrer les modifications', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w700, fontFamily: 'Inter')),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, {TextInputType keyboardType = TextInputType.text}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Color(0xFF0F172A), fontSize: 14, fontWeight: FontWeight.w600, fontFamily: 'Inter')),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          keyboardType: keyboardType,
          style: const TextStyle(fontFamily: 'Inter'),
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF0EA5E9), width: 2)),
          ),
        ),
      ],
    );
  }

  Widget _buildDisabledField(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Color(0xFF0F172A), fontSize: 14, fontWeight: FontWeight.w600, fontFamily: 'Inter')),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          decoration: BoxDecoration(
            color: const Color(0xFFF1F5F9),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Row(
            children: [
              Expanded(child: Text(value, style: const TextStyle(color: Color(0xFF64748B), fontSize: 16, fontFamily: 'Inter', fontWeight: FontWeight.w500))),
              const Icon(Icons.lock_rounded, color: Color(0xFF94A3B8), size: 18),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRegionDropdown() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          isExpanded: true,
          value: _selectedRegion,
          hint: const Text('Sélectionnez une région', style: TextStyle(color: Color(0xFF94A3B8), fontFamily: 'Inter')),
          icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Color(0xFF64748B)),
          items: _regionsEtCommunes.keys.map((String region) {
            return DropdownMenuItem<String>(
              value: region,
              child: Text(region, style: const TextStyle(color: Color(0xFF1E293B), fontFamily: 'Inter')),
            );
          }).toList(),
          onChanged: (newValue) {
            setState(() {
              _selectedRegion = newValue;
              _selectedCommune = null; // reset commune when region changes
              _hasUnsavedChanges = true;
            });
          },
        ),
      ),
    );
  }

  Widget _buildCommuneDropdown() {
    List<String> communes = _selectedRegion != null ? _regionsEtCommunes[_selectedRegion!]! : [];
    
    return Container(
      decoration: BoxDecoration(
        color: _selectedRegion == null ? const Color(0xFFF1F5F9) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          isExpanded: true,
          value: _selectedCommune,
          hint: Text(
            _selectedRegion == null ? "Choisissez d'abord une région" : 'Sélectionnez une commune', 
            style: const TextStyle(color: Color(0xFF94A3B8), fontFamily: 'Inter'),
          ),
          icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Color(0xFF64748B)),
          items: communes.map((String commune) {
            return DropdownMenuItem<String>(
              value: commune,
              child: Text(commune, style: const TextStyle(color: Color(0xFF1E293B), fontFamily: 'Inter')),
            );
          }).toList(),
          onChanged: _selectedRegion == null ? null : (newValue) {
            setState(() {
              _selectedCommune = newValue;
              _hasUnsavedChanges = true;
            });
          },
        ),
      ),
    );
  }
}
