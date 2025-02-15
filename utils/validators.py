import re

def validate_phone_number(phone):
    """
    Validazione del formato del numero di telefono italiano.
    Formati validi:
    - +39 XXX XXXXXXX
    - 0039 XXX XXXXXXX
    - XXX XXXXXXX
    - XXXXXXXXXX
    Dove X è un numero, e la lunghezza totale dei numeri deve essere 10
    """
    # per prima cosa rimuovo tutti gli spazi
    cleaned_phone = phone.replace(" ", "")
    
    # controllo se il numero ha un prefisso internazionale
    if cleaned_phone.startswith("+39"):
        cleaned_phone = cleaned_phone[3:]
    elif cleaned_phone.startswith("0039"):
        cleaned_phone = cleaned_phone[4:]
    
    # controllo se il numero ha esattamente 10 cifre
    if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
        return False
    
    # controllo se il numero inizia con un prefisso valido (3XX) o (0)
    valid_mobile_prefixes = ["3"]  # i numeri italiani mobili iniziano con 3
    valid_landline_prefixes = ["0"]  # i numeri italiani fissi iniziano con 0
    
    first_digit = cleaned_phone[0]
    if first_digit not in valid_mobile_prefixes + valid_landline_prefixes:
        return False
        
    return True

def validate_email(email):
    """
    Valida l'email usando:
    - username può contenere lettere, numeri, punti, trattini, più e underscore
    - il dominio deve contenere lettere, numeri, punti e trattini
    - il TLD deve essere almeno 2 caratteri
    - non sono ammessi punti consecutivi
    - l'email non può iniziare o finire con un punto
    """
    email_regex = r"""(?x)
        ^(?!\.)                                  # email non può iniziare con un punto
        [a-zA-Z0-9_.+-]+                        # username
        @                                        # @ 
        [a-zA-Z0-9][a-zA-Z0-9-]*               # prima parte del dominio
        (?:\.[a-zA-Z0-9][a-zA-Z0-9-]*)*        # parti aggiuntive del dominio (es: unina.it)
        \.[a-zA-Z]{2,}$                         # TLD (almeno 2 caratteri)
    """
    
    if not re.match(email_regex, email, re.VERBOSE):
        return False
    
    # controlli aggiuntivi
    if '..' in email:  # non sono ammessi punti consecutivi
        return False
    if email.endswith('.'):  # l'email non può finire con un punto
        return False
    if len(email) > 254:  # limite RFC 5321
        return False
        
    return True 