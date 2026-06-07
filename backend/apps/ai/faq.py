import re

FAQ_KNOWLEDGE_BASE = {
    r'\b(naissance|extrait|acte.*naissance)\b': "Pour obtenir un acte de naissance, vous devez fournir un certificat médical d'accouchement et une pièce d'identité des parents.",
    r'\b(mariage|acte.*mariage)\b': "Pour un acte de mariage, veuillez vous munir des copies des pièces d'identité des époux et des témoins, ainsi que du certificat de célébration.",
    r'\b(décès|deces|acte.*décès)\b': "L'acte de décès nécessite le certificat médical de constatation du décès et le livret de famille ou la pièce d'identité du défunt.",
    r'\b(residence|résidence|domicile)\b': "Pour le certificat de résidence, un justificatif de domicile (facture SENELEC/SEN'EAU) récent est requis.",
    r'\b(délai|delai|temps|combien.*temps)\b': "Le délai de traitement habituel des dossiers est de 48 à 72 heures ouvrables.",
    r'\b(prix|coût|cout|payer|tarif)\b': "Les démarches d'état civil de base sont généralement gratuites, à l'exception des timbres fiscaux nécessaires pour certains actes.",
    r'\b(erreur|modifier|changement)\b': "En cas d'erreur sur un acte, il faut entamer une procédure de jugement d'hérédité ou de rectification au niveau du tribunal d'instance.",
    r'\b(bonjour|salut)\b': "Bonjour ! Je suis l'assistant de l'état civil SUNU CIVIL. Posez-moi votre question concernant vos démarches."
}

def get_faq_answer(question):
    """
    Analyse la question avec des expressions régulières pour trouver la réponse la plus pertinente.
    """
    question_lower = question.lower()
    
    for pattern, answer in FAQ_KNOWLEDGE_BASE.items():
        if re.search(pattern, question_lower):
            return answer
            
    return "Je suis désolé, je ne trouve pas la réponse à votre question spécifique. Veuillez reformuler ou contacter l'état civil de votre commune."
