"""
Portion Estimation Disclaimer & Guidance Module
Provides clear reminders about how EatWise estimates portion sizes for vague inputs
"""

# Estimation criteria and confidence levels
ESTIMATION_CRITERIA = {
    "HIGH_CONFIDENCE": {
        "description": "Specific portion sizes provided",
        "examples": [
            "150g chicken breast",
            "2 cups of rice",
            "1 medium apple",
            "500ml juice",
            "2 slices of bread"
        ],
        "confidence_percent": 85,
        "notes": "Most accurate when specific weights/measures are provided"
    },
    "MEDIUM_CONFIDENCE": {
        "description": "General portion descriptions with context",
        "examples": [
            "A bowl of rice",
            "A plate of pasta",
            "A chicken sandwich",
            "A handful of nuts",
            "A glass of milk"
        ],
        "confidence_percent": 60,
        "notes": "Estimated based on typical serving sizes. Actual portions may vary ±20%"
    },
    "MEDIUM_LOW_CONFIDENCE": {
        "description": "Vague descriptions without clear portions",
        "examples": [
            "Some rice and chicken",
            "Salad with dressing",
            "A meal with vegetables",
            "Fried rice"
        ],
        "confidence_percent": 40,
        "notes": "Estimated using common portion assumptions. May vary significantly"
    },
    "LOW_CONFIDENCE": {
        "description": "Photo only, no text description of portions",
        "examples": [
            "Photo of a plate (without knowing portion sizes)",
            "Photo with unclear food items",
            "Photo from distance (hard to gauge size)"
        ],
        "confidence_percent": 30,
        "notes": "Portions estimated by visual reference. Actual portions may differ by ±40%"
    }
}

ESTIMATION_RULES = {
    "text_input": {
        "title": "Text Description Estimation Rules",
        "rules": [
            "If you specify weight (g, kg, oz) or volume (ml, L, cup, tbsp) → HIGH confidence",
            "If you mention 'a bowl', 'a plate', 'a serving' → MEDIUM confidence",
            "If you're vague ('some rice', 'vegetables') → MEDIUM-LOW confidence",
            "Sizes vary by person, so we estimate 'average' portions",
            "Added fats (oil, butter) are estimated if not specified",
            "Cooking method affects calories (fried vs baked) - specify if known"
        ]
    },
    "photo_input": {
        "title": "Photo Estimation Rules",
        "rules": [
            "We estimate portion by comparing to visible references (plate size, utensils)",
            "Photos from above may under-estimate depth and total volume",
            "Lighting affects visibility - clear, well-lit photos are more accurate",
            "Mixed dishes are harder to estimate - ~20-40% uncertainty expected",
            "If possible, add a text description of portion sizes for better accuracy",
            "For best results, photograph food before eating (with reference object)"
        ]
    }
}

def get_confidence_disclaimer(confidence_level: str, input_type: str = "text") -> dict:
    """
    Get appropriate disclaimer based on confidence level and input type.
    
    Args:
        confidence_level: One of HIGH_CONFIDENCE, MEDIUM_CONFIDENCE, MEDIUM_LOW_CONFIDENCE, LOW_CONFIDENCE
        input_type: Either "text" or "photo"
    
    Returns:
        Dictionary with disclaimer content
    """
    confidence_data = ESTIMATION_CRITERIA.get(confidence_level, {})
    
    return {
        "confidence_percent": confidence_data.get("confidence_percent", 50),
        "level_description": confidence_data.get("description", "Unknown"),
        "main_note": confidence_data.get("notes", ""),
        "input_type": input_type,
        "variation_warning": get_variation_warning(confidence_level)
    }


def get_variation_warning(confidence_level: str) -> str:
    """Get warning about potential variation based on confidence level."""
    warnings = {
        "HIGH_CONFIDENCE": "±15% expected variation",
        "MEDIUM_CONFIDENCE": "±20-25% expected variation",
        "MEDIUM_LOW_CONFIDENCE": "±30-35% expected variation",
        "LOW_CONFIDENCE": "±40-50% expected variation"
    }
    return warnings.get(confidence_level, "Variation may be significant")


def assess_input_confidence(text_description: str = None, has_photo: bool = False) -> str:
    """
    Assess confidence level based on input characteristics.
    
    Args:
        text_description: Text description of meal (if provided)
        has_photo: Whether a photo was provided
    
    Returns:
        Confidence level string
    """
    if not text_description and has_photo:
        return "LOW_CONFIDENCE"
    
    if not text_description:
        return "LOW_CONFIDENCE"
    
    text_lower = text_description.lower()
    
    # Check for specific quantities/weights
    specific_amount_keywords = [
        r'\d+\s*(g|kg|oz|lb|ml|l|cup|tbsp|tsp|slice|piece|bowl|plate)',
        r'medium\s+(apple|orange|banana|egg)',
        r'large\s+(apple|orange|banana)',
        r'small\s+(apple|orange|banana)'
    ]
    
    import re
    for pattern in specific_amount_keywords:
        if re.search(pattern, text_lower):
            return "HIGH_CONFIDENCE"
    
    # Check for general portion descriptions
    general_keywords = ['a bowl', 'a plate', 'a serving', 'a cup', 'a handful', 'a slice', 'some']
    if any(keyword in text_lower for keyword in general_keywords):
        return "MEDIUM_CONFIDENCE"
    
    # Check for vague descriptions
    if len(text_description.strip()) < 20:
        return "MEDIUM_LOW_CONFIDENCE"
    
    # Default to medium
    return "MEDIUM_CONFIDENCE"


def format_disclaimer_for_display(confidence_level: str, input_type: str = "text") -> str:
    """
    Format disclaimer text for Streamlit display.
    
    Args:
        confidence_level: Confidence level string
        input_type: "text" or "photo"
    
    Returns:
        Formatted markdown string for display
    """
    disclaimer = get_confidence_disclaimer(confidence_level, input_type)
    
    variation = disclaimer["variation_warning"]
    confidence_pct = disclaimer["confidence_percent"]
    main_note = disclaimer["main_note"]
    
    markdown = f"""
### Portion Estimation Confidence

**Confidence Level:** {confidence_level.replace('_', ' ')} ({confidence_pct}%)

**Variation Range:** {variation}

**Note:** {main_note}

**What this means:**
- Your nutrition values may differ from actual values by the variation range above
- For most accurate tracking, specify exact portions when possible
- Recurring patterns over time are more reliable than individual meal estimates
"""
    
    return markdown


def get_estimation_tips_for_input(input_type: str = "text") -> str:
    """Get tips for improving estimation accuracy based on input type."""
    
    if input_type == "photo":
        tips = """
### Tips for Accurate Photo Meal Logging

1. **Include a reference object** - Place a coin, credit card, or hand in photo for scale
2. **Good lighting** - Natural light works best to clearly see all food items
3. **Top-down view** - Photograph from above at 45° angle to capture all ingredients
4. **Add text description** - Include portion sizes or ingredients in the notes for better accuracy
5. **High quality photo** - Use camera instead of blurry phone snapshots
6. **Before eating** - Log the meal before consuming so nothing is missing

**Example:** "Chicken (150g), Brown rice (1 cup cooked), Broccoli (1 cup)"
"""
    else:
        tips = """
### Tips for Accurate Text Meal Logging

1. **Be specific with amounts** - Use grams, milliliters, cups, or standard measures
   - ✓ Good: "150g grilled chicken breast, 200g brown rice"
   - ✗ Vague: "Some chicken and rice"

2. **Mention cooking method** - It affects calories
   - ✓ "Grilled chicken" vs ✗ "Fried chicken"

3. **Include condiments** - Oils, sauces, dressings add significant calories
   - ✓ "Salad with 2 tbsp olive oil dressing"
   - ✗ "Salad with dressing"

4. **Specify portion context** - Use familiar references
   - ✓ "Medium apple" or "1 cup of rice"
   - ✗ "An apple" or "Some rice"

5. **List each component** - Don't summarize as one item
   - ✓ "Chicken breast, rice, broccoli, olive oil"
   - ✗ "Stir fry"

**Example:** "2 eggs scrambled in 1 tbsp butter, 2 slices whole wheat toast, 1 medium apple, 1 cup orange juice"
"""
    
    return tips


# Display helper functions for Streamlit integration
def show_estimation_disclaimer(st, confidence_level: str, input_type: str = "text"):
    """Display disclaimer in Streamlit."""
    disclaimer_text = format_disclaimer_for_display(confidence_level, input_type)
    st.warning(disclaimer_text)


def show_estimation_tips(st, input_type: str = "text"):
    """Display tips in Streamlit."""
    tips_text = get_estimation_tips_for_input(input_type)
    st.info(tips_text)
