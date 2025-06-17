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

def validate_text(text):
    """
    valida il testo per assicurarsi che non contenga caratteri problematici
    che potrebbero causare problemi con n8n o json
    
    restituisce:
    - true se il testo è valido
    - false se il testo contiene caratteri problematici
    """
    if not isinstance(text, str):
        return True
        
    # controlla caratteri problematici
    problematic_chars = ['"', '\\', '{', '}', '[', ']', '<', '>', '&', '#']
    for char in problematic_chars:
        if char in text:
            return False
            
    # controlla caratteri di controllo
    if re.search(r'[\x00-\x1F\x7F]', text):
        return False
        
    return True

def get_invalid_chars(text):
    """
    identifica i caratteri problematici nel testo
    
    restituisce:
    - una stringa vuota se non ci sono caratteri problematici
    - una stringa con i caratteri problematici trovati
    """
    if not isinstance(text, str):
        return ""
        
    problematic_chars = ['"', '\\', '{', '}', '[', ']', '<', '>', '&', '#']
    found_chars = []
    
    for char in problematic_chars:
        if char in text:
            found_chars.append(char)
            
    # aggiungi eventuali caratteri di controllo trovati
    control_chars = re.findall(r'[\x00-\x1F\x7F]', text)
    if control_chars:
        found_chars.extend(['caratteri di controllo'])
        
    return ", ".join(found_chars) if found_chars else "" 

def clean_text(text):
        """
        pulisce il testo da caratteri che potrebbero causare problem
        """
        if isinstance(text, str):
            # replace backslashes
            text = text.replace('\\', '')
            # replace quotes with single quotes
            text = text.replace('"', "'")
            # replace newlines and carriage returns with spaces
            text = text.replace('\n', ' ').replace('\r', ' ')
            # remove control characters
            text = re.sub(r'[\x00-\x1F\x7F]', '', text)
            # replace other potentially problematic characters
            text = text.replace('{', '(').replace('}', ')')
            text = text.replace('[', '(').replace(']', ')')
            # remove any HTML/XML tags that might be present
            text = re.sub(r'<[^>]*>', '', text)
            # normalize whitespace (replace multiple spaces with a single space)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        return text