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


def get_gender_agreements(gender):
    """
    Retourne les accords grammaticaux selon le genre
    
    Args:
        gender: 'M' (masculin) ou 'F' (féminin)
        
    Returns:
        dict: Dictionnaire avec les variantes grammaticales
    """
    if gender == 'F':
        return {
            'salarie': 'La salariée',
            'salarie_art': 'la salariée',
            'engage': 'engagée',
            'ne': 'née',
            'il_elle': 'elle',
            'son_sa': 'sa',
            'lui': 'elle',
        }
    else:
        return {
            'salarie': 'Le salarié',
            'salarie_art': 'le salarié',
            'engage': 'engagé',
            'ne': 'né',
            'il_elle': 'il',
            'son_sa': 'son',
            'lui': 'lui',
        }


def create_specific_template(entity_name, contract_type, gender):
    """
    Crée un template de contrat personnalisé pour une entité, type de contrat et genre spécifiques
    
    Args:
        entity_name: 'nantes_urgences' ou 'ambulances_sansoucy'
        contract_type: 'cdi' ou 'cdd'
        gender: 'M' (masculin) ou 'F' (féminin)
        
    Returns:
        str: Chemin du template créé
    """
    template_dir = os.path.join(settings.BASE_DIR, 'templates', 'word_templates')
    gender_suffix = 'homme' if gender == 'M' else 'femme'
    template_path = os.path.join(template_dir, f'contrat_{entity_name}_{contract_type}_{gender_suffix}.docx')
    
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
    agreements = get_gender_agreements(gender)
    
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
    
    # Sous-titre avec type de contrat
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contract_type_label = 'CDI - Contrat à Durée Indéterminée' if contract_type == 'cdi' else 'CDD - Contrat à Durée Déterminée'
    subtitle.add_run(contract_type_label)
    
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
    
    # Salarié avec variables Jinja2 et accords de genre
    p = doc.add_paragraph()
    p.add_run(f'ET {agreements["salarie"].upper()}\n').bold = True
    p.add_run('Nom : {{ employee_last_name }}\n')
    p.add_run('Prénom : {{ employee_first_name }}\n')
    p.add_run(f'Date de naissance : {{{{ employee_birth_date }}}} - {agreements["ne"]} à {{{{ employee_birth_place }}}}\n')
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
    p.add_run(f'{agreements["salarie"]} est {agreements["engage"]}')
    
    if contract_type == 'cdd':
        p.add_run(' à compter du {{ start_date }} jusqu\'au {{ end_date }} en qualité de {{ employee_profession }}.')
    else:
        p.add_run(' à compter du {{ start_date }} en qualité de {{ employee_profession }}.')
    
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
    p.add_run(f'{agreements["salarie"]} exercera {agreements["son_sa"]} activité à raison de {{{{ working_hours_per_week }}}} heures par semaine.')
    
    doc.add_paragraph()
    
    # ARTICLE 4 - RÉMUNÉRATION
    doc.add_paragraph('ARTICLE 4 - RÉMUNÉRATION').runs[0].bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('{% if monthly_salary %}')
    p = doc.add_paragraph()
    p.add_run(f'{agreements["salarie"]} percevra une rémunération mensuelle brute de {{{{ monthly_salary }}}} euros.')
    p = doc.add_paragraph()
    p.add_run('{% endif %}')
    
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
    p.add_run(f'{agreements["salarie"]} relève du service de médecine du travail : {info["medical_service"]}')
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
    header_cells[1].text = f'{agreements["salarie"]}'
    
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
    Génère un document Word de contrat réaliste à partir d'un objet Contract
    Génère directement avec python-docx sans passer par des templates
    
    Args:
        contract: Instance du modèle Contract
        
    Returns:
        tuple: (filename, file_content) pour sauvegarde dans FileField
    """
    from io import BytesIO
    import os
    
    # Importer la fonction de génération depuis cdd_templates_generator
    # mais générer avec les vraies données au lieu de placeholders
    from contracts.cdd_templates_generator import get_gender_agreements, set_cell_background
    
    # Récupérer les informations
    employee = contract.employee
    user = employee.user
    
    # Déterminer l'entité
    entity_name = contract.entity_template if contract.entity_template else 'nantes_urgences'
    
    # Déterminer le type de contrat (cdi ou cdd)
    contract_type = 'cdi' if contract.contract_type == 'cdi' else 'cdd'
    
    # Déterminer le genre
    gender = employee.gender if hasattr(employee, 'gender') and employee.gender else 'M'
    agreements = get_gender_agreements(gender)
    
    # Formater les données
    def format_date_french_long(date_obj):
        """Formate une date en texte français long (ex: 02 mars 2026)"""
        if not date_obj:
            return '[Date]'
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        return f"{date_obj.day:02d} {months[date_obj.month - 1]} {date_obj.year}"
    
    def format_date_french_short(date_obj):
        """Formate une date en format court (JJ/MM/AAAA)"""
        if not date_obj:
            return '[Date]'
        return date_obj.strftime('%d/%m/%Y')
    
    def safe_format_currency(value):
        """Convertit une valeur en montant formaté (format français)"""
        if not value:
            return '0,00'
        try:
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            return f"{float(value):.2f}".replace('.', ',')
        except (ValueError, TypeError):
            return '0,00'
    
    # Préparer les données
    monthly_hours = 152
    if contract.working_hours_per_week:
        try:
            weekly_hours = float(contract.working_hours_per_week)
            monthly_hours = int((weekly_hours * 52) / 12)
        except (ValueError, TypeError):
            monthly_hours = 152
    
    trial_period_days = ''
    if contract.trial_end_date and contract.start_date:
        delta = contract.trial_end_date - contract.start_date
        trial_period_days = f"{delta.days} jours"
    
    birth_place_code = ''
    if employee.birth_place:
        import re
        match = re.search(r'\b\d{5}\b', employee.birth_place)
        if match:
            birth_place_code = match.group()
        elif employee.social_security_number and len(employee.social_security_number) >= 7:
            dept_code = employee.social_security_number[5:7]
            birth_place_code = dept_code
    
    city_postalcode = f"{employee.postal_code} {employee.city}" if hasattr(employee, 'postal_code') and hasattr(employee, 'city') else ''
    
    cdd_reason = "Remplacement d'un salarié absent" if contract.contract_type == 'cdd' else ''
    if contract.notes and 'motif' in contract.notes.lower():
        cdd_reason = contract.notes
    
    # Créer le document en important directement la bonne fonction de génération
    if entity_name == 'ambulances_sansoucy':
        from contracts.cdd_templates_generator import create_ambulances_sansoucy_cdd_template
        # On ne peut pas utiliser directement car elle crée des templates, pas des documents remplis
    
    # Plutôt que d'utiliser les fonctions de template, on va générer directement
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    
    doc = Document()
    
    #Marges
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(0.79)
        section.right_margin = Inches(0.79)
    
    # EN-TÊTE selon l'entité
    if entity_name == 'nantes_urgences':
        company_name = 'SARL NANTES URGENCES SANSOUCY'
        address = '8 Rue de Remouleur, 44800 SAINT-HERBLAIN'
        siret = '48805076600028'
        urssaf = 'URSSAF NANTES 627201905366'
        representative = 'Monsieur Patrice BORÉ, Direction'
        city_signature = 'St-Herblain'
    else:  # ambulances_sansoucy
        company_name = 'SARL AMBULANCES SANSOUCY'
        address = '2 avenue de la Véra Cruz, 44600 SAINT NAZAIRE'
        siret = '38026793000036'
        urssaf = 'URSSAF NANTES 527201905363'
        representative = 'Monsieur Bruno SANSOUCY, Gérant'
        city_signature = 'St-Nazaire'
    
    # Header
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(company_name)
    run.bold = True
    run.font.size = Pt(14)
    
    p = doc.add_paragraph(address)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(11)
    
    p = doc.add_paragraph(f'SIRET: {siret}')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(11)
    
    p = doc.add_paragraph(urssaf)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(11)
    
    doc.add_paragraph()
    
    # TITRE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title = 'CONTRAT À DURÉE INDÉTERMINÉE' if contract_type == 'cdi' else 'CONTRAT À DURÉE DÉTERMINÉE'
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(12)
    
    doc.add_paragraph()
    
    # ENTRE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('ENTRE:')
    run.bold = True
    run.font.size = Pt(11)
    
    doc.add_paragraph(company_name)
    doc.add_paragraph(address)
    doc.add_paragraph(f'Représentée par {representative}')
    
    doc.add_paragraph()
    doc.add_paragraph('ET')
    doc.add_paragraph()
    
    # EMPLOYÉ
    doc.add_paragraph(f'{agreements["civility"]} {user.first_name} {user.last_name.upper()}')
    doc.add_paragraph(employee.address if hasattr(employee, 'address') else '[Adresse]')
    doc.add_paragraph(city_postalcode)
    doc.add_paragraph(f'{agreements["ne"]} le: {format_date_french_short(employee.birth_date)} à {employee.birth_place if hasattr(employee, "birth_place") else "[Lieu]"} ({birth_place_code})')
    doc.add_paragraph(f'Immatriculé: {employee.social_security_number}')
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # RAPPEL
    p = doc.add_paragraph()
    run = p.add_run('IL A ÉTÉ RAPPELÉ CE QUI SUIT')
    run.bold = True
    run.font.size = Pt(11)
    
    doc.add_paragraph()
    
    # ARTICLE 1
    p = doc.add_paragraph()
    run = p.add_run('ARTICLE 1: ATTRIBUTION ET EMPLOI')
    run.bold = True
    run.font.size = Pt(11)
    
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run(f'{agreements["civility"]} {user.first_name} {user.last_name.upper()} ').font.bold = True
    p.add_run(f'{agreements["est_was"]} {agreements["engage"]} en qualité d\'ambulancier.')
    
    doc.add_paragraph()
    
    # ARTICLE 2: SALAIRE
    p = doc.add_paragraph()
    run = p.add_run('ARTICLE 2: SALAIRE')
    run.bold = True
    run.font.size = Pt(11)
    
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run('Le salaire de ').font.size = Pt(11)
    p.add_run(f'{agreements["civility"]} {user.first_name} {user.last_name.upper()}').font.bold = True
    p.add_run(' se décompose comme suit:').font.size = Pt(11)
    
    doc.add_paragraph()
    
    # Tableau salaire
    table = doc.add_table(rows=2, cols=3)
    table.style = 'Light Grid Accent 1'
    
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Emploi'
    header_cells[1].text = 'Taux'
    header_cells[2].text = f'À compter du 1er janvier 2025 (base {monthly_hours}h / mois)'
    
    for cell in header_cells:
        set_cell_background(cell, 'D9D9D9')
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
    
    data_cells = table.rows[1].cells
    data_cells[0].text = 'AA'
    data_cells[1].text = f'{safe_format_currency(contract.hourly_rate)}€'
    data_cells[2].text = f'{safe_format_currency(contract.monthly_salary)}€'
    
    doc.add_paragraph()
    
    # CDD spécifique
    if contract_type == 'cdd':
        p = doc.add_paragraph()
        run = p.add_run('ARTICLE 3: DURÉE ET CAUSE DU CONTRAT')
        run.bold = True
        run.font.size = Pt(11)
        
        doc.add_paragraph()
        
        p = doc.add_paragraph()
        p.add_run(f'{agreements["civility"]} {user.first_name} {user.last_name.upper()} ').font.bold = True
        p.add_run(f'est engagé à titre précaire du {format_date_french_long(contract.start_date)} au {format_date_french_long(contract.end_date) if contract.end_date else "[Date de fin]"}, avec période d\'essai de {trial_period_days if trial_period_days else "[Durée]"}.')
        
        p = doc.add_paragraph()
        p.add_run(f'Motif du recours au CDD: {cdd_reason}')
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # SIGNATURE
    p = doc.add_paragraph()
    p.add_run(f'Fait à {city_signature}, le {format_date_french_long(datetime.now().date())}')
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Tableau signature
    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.style = 'Table Grid'
    
    emp_cells = sig_table.rows[0].cells
    emp_cells[0].text = f'{agreements["civility"]} {user.first_name} {user.last_name.upper()}:'
    emp_cells[0].paragraphs[0].runs[0].font.bold = True
    emp_cells[0].add_paragraph('Bon pour accord, lu et approuvé')
    
    comp_cells = sig_table.rows[0].cells
    comp_cells[1].text = company_name
    comp_cells[1].paragraphs[0].runs[0].font.bold = True
    comp_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    comp_cells[1].add_paragraph(representative).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # Générer le nom du fichier
    filename = f"Contrat_{contract.contract_number}_{user.last_name}_{user.first_name}.docx"
    filename = filename.replace(' ', '_').replace('\'', '')
    
    # Sauvegarder dans un buffer
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return filename, file_stream.read()
