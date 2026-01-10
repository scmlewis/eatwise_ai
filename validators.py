"""
Input Validation Module for EatWise

Provides centralized validation functions for all user inputs.
Each validator returns a tuple of (is_valid: bool, result_or_error: str).
"""
import re
import html
import logging
from typing import Tuple, Optional, List, Any, Union

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Result Type
# ============================================================================

class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool, value: Any = None, error: str = None):
        self.is_valid = is_valid
        self.value = value  # Sanitized/normalized value if valid
        self.error = error  # Error message if invalid
    
    def __bool__(self):
        return self.is_valid
    
    def __repr__(self):
        if self.is_valid:
            return f"ValidationResult(valid=True, value={self.value!r})"
        return f"ValidationResult(valid=False, error={self.error!r})"


# ============================================================================
# Email Validation
# ============================================================================

# RFC 5322 compliant email regex (simplified)
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        ValidationResult with normalized email or error message
    """
    if not email:
        return ValidationResult(False, error="Email is required")
    
    email = email.strip().lower()
    
    if len(email) > 254:  # RFC 5321 limit
        return ValidationResult(False, error="Email address is too long")
    
    if not EMAIL_PATTERN.match(email):
        return ValidationResult(False, error="Please enter a valid email address")
    
    # Check for common typos
    common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    domain = email.split('@')[1] if '@' in email else ''
    
    # Suggest corrections for obvious typos
    typo_suggestions = {
        'gmial.com': 'gmail.com',
        'gmai.com': 'gmail.com',
        'gmail.co': 'gmail.com',
        'yaho.com': 'yahoo.com',
        'hotmal.com': 'hotmail.com',
        'outloo.com': 'outlook.com',
    }
    
    if domain in typo_suggestions:
        suggested = email.replace(domain, typo_suggestions[domain])
        return ValidationResult(
            False, 
            error=f"Did you mean {suggested}?"
        )
    
    return ValidationResult(True, value=email)


# ============================================================================
# Password Validation
# ============================================================================

def validate_password(
    password: str, 
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = False
) -> ValidationResult:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum required length
        require_uppercase: Require at least one uppercase letter
        require_lowercase: Require at least one lowercase letter
        require_digit: Require at least one digit
        require_special: Require at least one special character
        
    Returns:
        ValidationResult with password or error message
    """
    if not password:
        return ValidationResult(False, error="Password is required")
    
    errors = []
    
    if len(password) < min_length:
        errors.append(f"at least {min_length} characters")
    
    if require_uppercase and not re.search(r'[A-Z]', password):
        errors.append("one uppercase letter")
    
    if require_lowercase and not re.search(r'[a-z]', password):
        errors.append("one lowercase letter")
    
    if require_digit and not re.search(r'\d', password):
        errors.append("one number")
    
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("one special character")
    
    if errors:
        error_msg = "Password must contain " + ", ".join(errors)
        return ValidationResult(False, error=error_msg)
    
    return ValidationResult(True, value=password)


def validate_password_match(password: str, confirm_password: str) -> ValidationResult:
    """
    Validate that password and confirmation match.
    
    Args:
        password: Original password
        confirm_password: Password confirmation
        
    Returns:
        ValidationResult
    """
    if password != confirm_password:
        return ValidationResult(False, error="Passwords do not match")
    
    return ValidationResult(True, value=password)


# ============================================================================
# Name/Text Validation
# ============================================================================

def validate_name(
    name: str, 
    field_name: str = "Name",
    min_length: int = 1,
    max_length: int = 100,
    allow_special: bool = False
) -> ValidationResult:
    """
    Validate a name field (user name, meal name, etc.).
    
    Args:
        name: Name to validate
        field_name: Name of the field for error messages
        min_length: Minimum required length
        max_length: Maximum allowed length
        allow_special: Allow special characters beyond letters/spaces
        
    Returns:
        ValidationResult with sanitized name or error message
    """
    if not name:
        return ValidationResult(False, error=f"{field_name} is required")
    
    # Strip whitespace
    name = name.strip()
    
    # Remove excessive internal whitespace
    name = ' '.join(name.split())
    
    if len(name) < min_length:
        return ValidationResult(
            False, 
            error=f"{field_name} must be at least {min_length} character(s)"
        )
    
    if len(name) > max_length:
        return ValidationResult(
            False, 
            error=f"{field_name} must be {max_length} characters or less"
        )
    
    # Check for potentially dangerous characters
    dangerous_chars = ['<', '>', '{', '}', '\\', '\x00']
    if any(char in name for char in dangerous_chars):
        return ValidationResult(
            False, 
            error=f"{field_name} contains invalid characters"
        )
    
    # HTML escape for safety
    sanitized = html.escape(name)
    
    return ValidationResult(True, value=sanitized)


# ============================================================================
# Meal Input Validation
# ============================================================================

def validate_meal_input(
    meal_description: str,
    max_length: int = 1000
) -> ValidationResult:
    """
    Validate meal description input for AI analysis.
    
    Args:
        meal_description: Meal description to validate
        max_length: Maximum allowed length
        
    Returns:
        ValidationResult with sanitized description or error message
    """
    if not meal_description:
        return ValidationResult(False, error="Please describe your meal")
    
    # Strip whitespace
    description = meal_description.strip()
    
    if len(description) < 3:
        return ValidationResult(
            False, 
            error="Please provide more detail about your meal"
        )
    
    if len(description) > max_length:
        return ValidationResult(
            False, 
            error=f"Description is too long (max {max_length} characters)"
        )
    
    # Remove potential injection patterns
    # Remove script tags
    description = re.sub(r'<script[^>]*>.*?</script>', '', description, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove HTML tags
    description = re.sub(r'<[^>]+>', '', description)
    
    # Remove null bytes and control characters (except newlines/tabs)
    description = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', description)
    
    # Collapse excessive whitespace but preserve intentional line breaks
    lines = description.split('\n')
    lines = [' '.join(line.split()) for line in lines]
    description = '\n'.join(line for line in lines if line)
    
    # HTML escape
    sanitized = html.escape(description)
    
    return ValidationResult(True, value=sanitized)


def validate_portion_description(portion: str) -> ValidationResult:
    """
    Validate portion size description.
    
    Args:
        portion: Portion description (e.g., "1 cup", "200g", "medium bowl")
        
    Returns:
        ValidationResult with sanitized portion or error message
    """
    if not portion:
        # Portion is optional
        return ValidationResult(True, value="")
    
    portion = portion.strip()
    
    if len(portion) > 200:
        return ValidationResult(
            False,
            error="Portion description is too long"
        )
    
    # Remove dangerous characters
    sanitized = re.sub(r'[<>{}\[\]\\]', '', portion)
    sanitized = html.escape(sanitized)
    
    return ValidationResult(True, value=sanitized)


# ============================================================================
# Numeric Validation
# ============================================================================

def validate_numeric(
    value: Any,
    field_name: str = "Value",
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_zero: bool = True,
    allow_negative: bool = False,
    as_int: bool = False
) -> ValidationResult:
    """
    Validate a numeric value.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_zero: Allow zero as a valid value
        allow_negative: Allow negative values
        as_int: Convert to integer
        
    Returns:
        ValidationResult with numeric value or error message
    """
    if value is None or value == "":
        return ValidationResult(False, error=f"{field_name} is required")
    
    try:
        if as_int:
            num_value = int(float(value))
        else:
            num_value = float(value)
    except (ValueError, TypeError):
        return ValidationResult(
            False, 
            error=f"{field_name} must be a valid number"
        )
    
    if not allow_negative and num_value < 0:
        return ValidationResult(
            False, 
            error=f"{field_name} cannot be negative"
        )
    
    if not allow_zero and num_value == 0:
        return ValidationResult(
            False, 
            error=f"{field_name} cannot be zero"
        )
    
    if min_value is not None and num_value < min_value:
        return ValidationResult(
            False, 
            error=f"{field_name} must be at least {min_value}"
        )
    
    if max_value is not None and num_value > max_value:
        return ValidationResult(
            False, 
            error=f"{field_name} must be at most {max_value}"
        )
    
    return ValidationResult(True, value=num_value)


def validate_calories(value: Any) -> ValidationResult:
    """Validate calorie input (0-10000 kcal)"""
    return validate_numeric(
        value, 
        field_name="Calories",
        min_value=0,
        max_value=10000,
        as_int=True
    )


def validate_macros(value: Any, macro_name: str) -> ValidationResult:
    """Validate macro nutrient input (protein, carbs, fat in grams)"""
    return validate_numeric(
        value,
        field_name=macro_name,
        min_value=0,
        max_value=1000  # Reasonable max for a single meal
    )


def validate_height(value: Any) -> ValidationResult:
    """Validate height in cm (50-250 cm)"""
    return validate_numeric(
        value,
        field_name="Height",
        min_value=50,
        max_value=250,
        as_int=True
    )


def validate_weight(value: Any) -> ValidationResult:
    """Validate weight in kg (20-500 kg)"""
    return validate_numeric(
        value,
        field_name="Weight",
        min_value=20,
        max_value=500
    )


def validate_water_glasses(value: Any) -> ValidationResult:
    """Validate water goal in glasses (1-20)"""
    return validate_numeric(
        value,
        field_name="Water goal",
        min_value=1,
        max_value=20,
        as_int=True
    )


# ============================================================================
# Menu/Restaurant Validation
# ============================================================================

def validate_menu_text(menu_text: str, max_length: int = 5000) -> ValidationResult:
    """
    Validate restaurant menu text input.
    
    Args:
        menu_text: Menu text to validate
        max_length: Maximum allowed length
        
    Returns:
        ValidationResult with sanitized menu text or error message
    """
    if not menu_text:
        return ValidationResult(False, error="Please enter the menu items")
    
    text = menu_text.strip()
    
    if len(text) < 10:
        return ValidationResult(
            False,
            error="Please provide more menu details"
        )
    
    if len(text) > max_length:
        return ValidationResult(
            False,
            error=f"Menu text is too long (max {max_length} characters)"
        )
    
    # Remove potential script/HTML injections
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # HTML escape
    sanitized = html.escape(text)
    
    return ValidationResult(True, value=sanitized)


# ============================================================================
# Chat/Coaching Input Validation
# ============================================================================

def validate_chat_input(message: str, max_length: int = 2000) -> ValidationResult:
    """
    Validate chat/coaching message input.
    
    Args:
        message: User message to validate
        max_length: Maximum allowed length
        
    Returns:
        ValidationResult with sanitized message or error message
    """
    if not message:
        return ValidationResult(False, error="Please enter a message")
    
    message = message.strip()
    
    if len(message) < 2:
        return ValidationResult(
            False,
            error="Message is too short"
        )
    
    if len(message) > max_length:
        return ValidationResult(
            False,
            error=f"Message is too long (max {max_length} characters)"
        )
    
    # Remove potential injections
    message = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
    message = re.sub(r'<[^>]+>', '', message)
    message = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', message)
    
    sanitized = html.escape(message)
    
    return ValidationResult(True, value=sanitized)


# ============================================================================
# Batch Validation Helper
# ============================================================================

def validate_all(*validations: ValidationResult) -> Tuple[bool, List[str]]:
    """
    Check multiple validations and collect all errors.
    
    Args:
        *validations: ValidationResult objects to check
        
    Returns:
        Tuple of (all_valid, list_of_errors)
    """
    errors = []
    all_valid = True
    
    for validation in validations:
        if not validation.is_valid:
            all_valid = False
            if validation.error:
                errors.append(validation.error)
    
    return all_valid, errors


# ============================================================================
# Convenience Functions for Streamlit
# ============================================================================

def show_validation_error(validation: ValidationResult, container=None) -> bool:
    """
    Display validation error in Streamlit if validation failed.
    
    Args:
        validation: ValidationResult to check
        container: Optional Streamlit container to display in
        
    Returns:
        True if valid, False if error was shown
    """
    if validation.is_valid:
        return True
    
    import streamlit as st
    
    if container:
        container.error(f"❌ {validation.error}")
    else:
        st.error(f"❌ {validation.error}")
    
    return False
