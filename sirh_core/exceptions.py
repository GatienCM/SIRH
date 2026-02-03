"""
Exception handlers personnalisés pour DRF avec traductions en français
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Handler personnalisé pour traduire les erreurs DRF en français
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Traduction des messages d'erreur courants
        translations = {
            "Invalid username or password": "Nom d'utilisateur ou mot de passe invalide",
            "Authentication credentials were not provided": "Les identifiants d'authentification n'ont pas été fournis",
            "You do not have permission to perform this action": "Vous n'avez pas la permission d'effectuer cette action",
            "Not found": "Non trouvé",
            "Method not allowed": "Méthode non autorisée",
            "This field may not be blank": "Ce champ ne peut pas être vide",
            "This field is required": "Ce champ est obligatoire",
            "Ensure this field has no more than": "Assurez-vous que ce champ n'a pas plus de",
            "Ensure this field has at least": "Assurez-vous que ce champ a au moins",
            "Ensure this value is less than or equal to": "Assurez-vous que cette valeur est inférieure ou égale à",
            "Ensure this value is greater than or equal to": "Assurez-vous que cette valeur est supérieure ou égale à",
            "Not a valid string": "Pas une chaîne valide",
            "Not a valid integer": "Pas un entier valide",
            "Not a valid boolean": "Pas un booléen valide",
            "Not a valid date": "Pas une date valide",
            "Not a valid time": "Pas une heure valide",
            "Not a valid datetime": "Pas une date-heure valide",
        }
        
        # Traduire les erreurs dans la réponse
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    translated = []
                    for msg in value:
                        msg_str = str(msg)
                        translated_msg = translations.get(msg_str, msg_str)
                        translated.append(translated_msg)
                    response.data[key] = translated
                elif isinstance(value, str):
                    response.data[key] = translations.get(str(value), str(value))
        elif isinstance(response.data, list):
            translated = []
            for msg in response.data:
                msg_str = str(msg)
                translated_msg = translations.get(msg_str, msg_str)
                translated.append(translated_msg)
            response.data = translated
    
    return response
