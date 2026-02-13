"""
Utilitaires pour la génération de contrats de travail
"""
import os
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.core.files.base import ContentFile
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docxtpl import DocxTemplate


def create_contract_template():
    """
    Crée un template de contrat de travail au format Word compatible avec docxtpl
    Cette fonction génère le template s'il n'existe pas encore
    """
    template_dir = os.path.join(settings.BASE_DIR, 'templates', 'word_templates')
    template_path = os.path.join(template_dir, 'contrat_travail_template.docx')
    
    # Si le template existe déjà, ne pas le recréer
    if os.path.exists(template_path):
        return template_path
    
    # Créer le dossier si nécessaire
    os.makedirs(template_dir, exist_ok=True)
    
    # Créer le document
    doc = Document()
    
    # Configuration des marges
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)
    
    # Titre
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('CONTRAT DE TRAVAIL')
    run.bold = True
    run.font.size = Pt(16)
    
    doc.add_paragraph()
    
    # Sous-titre avec variables Jinja2
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run('{{ contract_type_display }}')
    
    doc.add_paragraph()
    doc.add_paragraph('_' * 100)
    doc.add_paragraph()
    
    # ENTRE LES SOUSSIGNÉS
    doc.add_paragraph('ENTRE LES SOUSSIGNÉS :').runs[0].bold = True
    doc.add_paragraph()
    
    # Employeur
    p = doc.add_paragraph()
    p.add_run('L\'EMPLOYEUR\n').bold = True
    p.add_run('Nom de l\'entreprise : [Nom de votre entreprise]\n')
    p.add_run('Adresse : [Adresse de l\'entreprise]\n')
    p.add_run('SIRET : [Numéro SIRET]\n')
    p.add_run('Représentée par : [Nom du représentant légal]\n')
    
    doc.add_paragraph()
    doc.add_paragraph('D\'UNE PART,').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    # Salarié avec variables Jinja2
    p = doc.add_paragraph()
    p.add_run('ET LE SALARIÉ\n').bold = True
    p.add_run('Nom : {{ employee_last_name }}\n')
    p.add_run('Prénom : {{ employee_first_name }}\n')
    p.add_run('Date de naissance : {{ employee_birth_date }}\n')
    p.add_run('Lieu de naissance : {{ employee_birth_place }}\n')
    p.add_run('N° Sécurité sociale : {{ employee_social_security }}\n')
    p.add_run('Adresse : {{ employee_address }}\n')
    
    doc.add_paragraph()
    doc.add_paragraph('D\'AUTRE PART,').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_paragraph('_' * 100)
    doc.add_paragraph()
    
    # ARTICLE 1 - ENGAGEMENT
    doc.add_paragraph('ARTICLE 1 - ENGAGEMENT').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('Le salarié est engagé à compter du {{ start_date }} en qualité de {{ employee_profession }}.')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('Type de contrat : {{ contract_type_display }}')
    
    # Pour les CDD - utilisation de blocs Jinja2
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('{% if end_date %}Date de fin de contrat : {{ end_date }}{% endif %}')
    
    doc.add_paragraph()
    
    # ARTICLE 2 - PÉRIODE D'ESSAI
    doc.add_paragraph('ARTICLE 2 - PÉRIODE D\'ESSAI').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('{% if trial_end_date %}')
    p.add_run('Le contrat est conclu avec une période d\'essai qui prendra fin le {{ trial_end_date }}.')
    p.add_run('{% else %}')
    p.add_run('Le contrat est conclu sans période d\'essai.')
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    
    # ARTICLE 3 - DURÉE DU TRAVAIL
    doc.add_paragraph('ARTICLE 3 - DURÉE DU TRAVAIL').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('La durée hebdomadaire de travail est fixée à {{ working_hours_per_week }} heures par semaine.')
    
    doc.add_paragraph()
    
    # ARTICLE 4 - RÉMUNÉRATION
    doc.add_paragraph('ARTICLE 4 - RÉMUNÉRATION').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('{% if monthly_salary %}')
    p.add_run('Le salarié percevra une rémunération mensuelle brute de {{ monthly_salary }} euros.')
    p.add_run('{% endif %}')
    
    p = doc.add_paragraph()
    p.add_run('{% if hourly_rate %}')
    p.add_run('Taux horaire brut : {{ hourly_rate }} euros.')
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('La rémunération sera versée mensuellement.')
    
    doc.add_paragraph()
    
    # ARTICLE 5 - CONVENTION COLLECTIVE
    doc.add_paragraph('ARTICLE 5 - CONVENTION COLLECTIVE').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('Le présent contrat est soumis à la {{ collective_agreement }}.')
    
    doc.add_paragraph()
    
    # ARTICLE 6 - MÉDECINE DU TRAVAIL
    doc.add_paragraph('ARTICLE 6 - MÉDECINE DU TRAVAIL').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('{% if occupational_health_service %}')
    p.add_run('Service de médecine du travail : {{ occupational_health_service }}')
    p.add_run('{% else %}')
    p.add_run('Le salarié sera convoqué à une visite médicale d\'embauche conformément à la réglementation.')
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    doc.add_paragraph('_' * 100)
    doc.add_paragraph()
    
    # Signatures
    doc.add_paragraph('Fait en double exemplaire, le {{ signature_date }}')
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Table pour les signatures
    table = doc.add_table(rows=3, cols=2)
    table.autofit = False
    table.allow_autofit = False
    
    # En-têtes
    table.cell(0, 0).text = 'L\'EMPLOYEUR'
    table.cell(0, 1).text = 'LE SALARIÉ'
    
    # Lignes vides pour les signatures
    table.cell(1, 0).text = '\n\n\n'
    table.cell(1, 1).text = '\n\n\n'
    
    # Noms
    table.cell(2, 0).text = '[Nom et signature]'
    table.cell(2, 1).text = '{{ employee_first_name }} {{ employee_last_name }}\nSignature :'
    
    # Centrer le texte des signatures
    for row in table.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Sauvegarder
    doc.save(template_path)
    
    return template_path


def create_entity_template(entity_name):
    """
    Crée un template de contrat personnalisé pour une entité spécifique
    
    Args:
        entity_name: 'nantes_urgences' ou 'ambulances_sansoucy'
        
    Returns:
        str: Chemin du template créé
    """
    template_dir = os.path.join(settings.BASE_DIR, 'templates', 'word_templates')
    template_path = os.path.join(template_dir, f'contrat_{entity_name}_template.docx')
    
    # Si le template existe déjà, ne pas le recréer
    if os.path.exists(template_path):
        return template_path
    
    # Créer le dossier si nécessaire
    os.makedirs(template_dir, exist_ok=True)
    
    # Informations spécifiques à chaque entité
    entity_info = {
        'nantes_urgences': {
            'name': 'NANTES URGENCES SANSOUCY',
            'legal_form': 'SARL',
            'address': '12 Rue de la Chapelle\n44000 NANTES',
            'siret': '123 456 789 00012',
            'representative': 'M. Jean SANSOUCY, Gérant',
            'medical_service': 'Service de Santé au Travail de Loire-Atlantique',
        },
        'ambulances_sansoucy': {
            'name': 'AMBULANCES SANSOUCY',
            'legal_form': 'SAS',
            'address': '25 Avenue des Ambulances\n44300 NANTES',
            'siret': '987 654 321 00019',
            'representative': 'Mme. Marie SANSOUCY, Présidente',
            'medical_service': 'ASTIA - Service de Santé au Travail',
        }
    }
    
    info = entity_info.get(entity_name, entity_info['nantes_urgences'])
    
    # Créer le document
    doc = Document()
    
    # Configuration des marges
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)
    
    # Titre
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('CONTRAT DE TRAVAIL')
    run.bold = True
    run.font.size = Pt(16)
    
    doc.add_paragraph()
    
    # Sous-titre avec variables Jinja2
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run('{{ contract_type_display }}')
    
    doc.add_paragraph()
    doc.add_paragraph('_' * 100)
    doc.add_paragraph()
    
    # ENTRE LES SOUSSIGNÉS
    doc.add_paragraph('ENTRE LES SOUSSIGNÉS :').runs[0].bold = True
    doc.add_paragraph()
    
    # Employeur avec informations spécifiques
    p = doc.add_paragraph()
    p.add_run('L\'EMPLOYEUR\n').bold = True
    p.add_run(f'{info["name"]}\n')
    p.add_run(f'{info["legal_form"]}\n')
    p.add_run(f'{info["address"]}\n')
    p.add_run(f'SIRET : {info["siret"]}\n')
    p.add_run(f'Représentée par : {info["representative"]}\n')
    
    doc.add_paragraph()
    doc.add_paragraph('D\'UNE PART,').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    # Salarié avec variables Jinja2
    p = doc.add_paragraph()
    p.add_run('ET LE SALARIÉ\n').bold = True
    p.add_run('Nom : {{ employee_last_name }}\n')
    p.add_run('Prénom : {{ employee_first_name }}\n')
    p.add_run('Date de naissance : {{ employee_birth_date }}\n')
    p.add_run('Lieu de naissance : {{ employee_birth_place }}\n')
    p.add_run('N° Sécurité sociale : {{ employee_social_security }}\n')
    p.add_run('Adresse : {{ employee_address }}\n')
    
    doc.add_paragraph()
    doc.add_paragraph('D\'AUTRE PART,').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_paragraph('_' * 100)
    doc.add_paragraph()
    
    # ARTICLE 1 - ENGAGEMENT
    doc.add_paragraph('ARTICLE 1 - ENGAGEMENT').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('Le salarié est engagé à compter du {{ start_date }} en qualité de {{ employee_profession }}.')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('Type de contrat : {{ contract_type_display }}')
    
    # Conditions pour CDD
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('{% if end_date %}')
    p = doc.add_paragraph()
    p.add_run('Date de fin du contrat : {{ end_date }}')
    p = doc.add_paragraph()
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    
    # ARTICLE 2 - PÉRIODE D'ESSAI
    doc.add_paragraph('ARTICLE 2 - PÉRIODE D\'ESSAI').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('{% if trial_end_date %}')
    p = doc.add_paragraph()
    p.add_run('Une période d\'essai est prévue jusqu\'au {{ trial_end_date }}.')
    p = doc.add_paragraph()
    p.add_run('{% else %}')
    p = doc.add_paragraph()
    p.add_run('Aucune période d\'essai n\'est prévue.')
    p = doc.add_paragraph()
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    
    # ARTICLE 3 - DURÉE DU TRAVAIL
    doc.add_paragraph('ARTICLE 3 - DURÉE DU TRAVAIL').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run(f'La durée hebdomadaire de travail est fixée à {{{{ working_hours_per_week }}}} heures.')
    
    doc.add_paragraph()
    
    # ARTICLE 4 - RÉMUNÉRATION
    doc.add_paragraph('ARTICLE 4 - RÉMUNÉRATION').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('{% if monthly_salary %}')
    p = doc.add_paragraph()
    p.add_run('Le salaire mensuel brut s\'élève à {{ monthly_salary }} euros.')
    p = doc.add_paragraph()
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('{% if hourly_rate %}')
    p = doc.add_paragraph()
    p.add_run('Le taux horaire brut s\'élève à {{ hourly_rate }} euros.')
    p = doc.add_paragraph()
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    
    # ARTICLE 5 - CONVENTION COLLECTIVE
    doc.add_paragraph('ARTICLE 5 - CONVENTION COLLECTIVE').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('Le présent contrat est soumis à la {{ collective_agreement }}.')
    
    doc.add_paragraph()
    
    # ARTICLE 6 - MÉDECINE DU TRAVAIL
    doc.add_paragraph('ARTICLE 6 - MÉDECINE DU TRAVAIL').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run(f'Le salarié relève du service de médecine du travail : {info["medical_service"]}')
    p = doc.add_paragraph()
    p.add_run('{% if occupational_health_service %}')
    p = doc.add_paragraph()
    p.add_run(' - {{ occupational_health_service }}')
    p = doc.add_paragraph()
    p.add_run('{% endif %}')
    
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph('Fait à {{ signature_place }}, le {{ signature_date }}')
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Tableau de signatures
    table = doc.add_table(rows=2, cols=2)
    table.style = 'Table Grid'
    
    # En-têtes
    header_cells = table.rows[0].cells
    header_cells[0].text = 'L\'Employeur'
    header_cells[1].text = 'Le Salarié'
    
    # Espaces pour signatures
    for cell in header_cells:
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Lignes de signature
    signature_cells = table.rows[1].cells
    for cell in signature_cells:
        cell.text = '\n\n\n'
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Sauvegarder
    doc.save(template_path)
    
    return template_path


def generate_contract_document(contract):
    """
    Génère un document Word de contrat à partir d'un objet Contract
    
    Args:
        contract: Instance du modèle Contract
        
    Returns:
        tuple: (filename, file_content) pour sauvegarde dans FileField
    """
    from docxtpl import DocxTemplate
    
    # Choisir le template en fonction de l'entité
    if hasattr(contract, 'entity_template') and contract.entity_template:
        template_path = create_entity_template(contract.entity_template)
    else:
        # Utiliser le template générique par défaut
        template_path = create_contract_template()
    
    # Charger le template
    doc = DocxTemplate(template_path)
    
    # Préparer le contexte pour le publipostage
    employee = contract.employee
    user = employee.user
    
    # Formater les dates
    start_date_fr = contract.start_date.strftime('%d/%m/%Y') if contract.start_date else ''
    end_date_fr = contract.end_date.strftime('%d/%m/%Y') if contract.end_date else ''
    trial_end_date_fr = contract.trial_end_date.strftime('%d/%m/%Y') if contract.trial_end_date else ''
    birth_date_fr = employee.birth_date.strftime('%d/%m/%Y') if employee.birth_date else ''
    
    # Formater les montants - convertir en Decimal/float d'abord
    def safe_format_currency(value):
        """Convertit une valeur en montant formaté (format français)"""
        if not value:
            return ''
        try:
            # Convertir en float si c'est une string
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            formatted = f"{float(value):,.2f}"
            return formatted.replace(',', ' ').replace('.', ',')
        except (ValueError, TypeError):
            return ''
    
    monthly_salary_str = safe_format_currency(contract.monthly_salary)
    hourly_rate_str = safe_format_currency(contract.hourly_rate)
    
    # Formater working_hours - convertir en float
    working_hours_str = str(contract.working_hours_per_week).replace('.', ',')
    try:
        if isinstance(contract.working_hours_per_week, str):
            working_hours_str = str(float(contract.working_hours_per_week)).replace('.', ',')
    except (ValueError, TypeError):
        working_hours_str = '35'
    
    context = {
        # Informations sur le contrat
        'contract_number': contract.contract_number,
        'contract_type': contract.contract_type,
        'contract_type_display': contract.get_contract_type_display(),
        'start_date': start_date_fr,
        'end_date': end_date_fr if contract.end_date else None,
        'trial_end_date': trial_end_date_fr if contract.trial_end_date else None,
        
        # Informations sur l'employé
        'employee_first_name': user.first_name,
        'employee_last_name': user.last_name,
        'employee_birth_date': birth_date_fr,
        'employee_birth_place': employee.birth_place if hasattr(employee, 'birth_place') else '',
        'employee_social_security': employee.social_security_number,
        'employee_address': employee.address if hasattr(employee, 'address') else '',
        'employee_profession': employee.profession.label if employee.profession else '',
        
        # Conditions de travail
        'working_hours_per_week': working_hours_str,
        'monthly_salary': monthly_salary_str if contract.monthly_salary else None,
        'hourly_rate': hourly_rate_str if contract.hourly_rate else None,
        
        # Convention collective
        'collective_agreement': contract.collective_agreement,
        
        # Médecine du travail
        'occupational_health_service': contract.occupational_health_service if contract.occupational_health_service else None,
        
        # Signature
        'signature_place': '[Ville]',
        'signature_date': datetime.now().strftime('%d/%m/%Y'),
    }
    
    # Remplir le template
    doc.render(context)
    
    # Générer le nom du fichier
    filename = f"Contrat_{contract.contract_number}_{user.last_name}_{user.first_name}.docx"
    filename = filename.replace(' ', '_')
    
    # Sauvegarder dans un buffer
    from io import BytesIO
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return filename, file_stream.read()
