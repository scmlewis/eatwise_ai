"""
EatWise Design System
Defines consistent typography, spacing, colors, and component styles
for a production-grade UI.
"""

# ============================================================================
# TYPOGRAPHY SYSTEM
# ============================================================================
# Heading hierarchy for consistent visual hierarchy
TYPOGRAPHY = {
    "h1": {
        "size": "28px",
        "weight": "bold",
        "line_height": "1.3",
        "margin_bottom": "24px",
        "description": "Page titles, main headings"
    },
    "h2": {
        "size": "20px",
        "weight": "bold",
        "line_height": "1.4",
        "margin_bottom": "16px",
        "description": "Section headings"
    },
    "h3": {
        "size": "16px",
        "weight": "bold",
        "line_height": "1.4",
        "margin_bottom": "12px",
        "description": "Subsection headings"
    },
    "body": {
        "size": "14px",
        "weight": "normal",
        "line_height": "1.5",
        "description": "Body text, descriptions"
    },
    "caption": {
        "size": "12px",
        "weight": "normal",
        "line_height": "1.4",
        "color": "#a0a0a0",
        "description": "Small text, labels, metadata"
    },
    "label": {
        "size": "11px",
        "weight": "700",
        "line_height": "1.3",
        "letter_spacing": "0.5px",
        "text_transform": "uppercase",
        "color": "#a0a0a0",
        "description": "Form labels, badges"
    }
}

# ============================================================================
# SPACING SYSTEM (8px base unit)
# ============================================================================
SPACING = {
    "xs": "4px",      # Minimal spacing
    "sm": "8px",      # Small spacing between elements
    "md": "16px",     # Standard spacing between sections
    "lg": "24px",     # Large spacing between major sections
    "xl": "32px",     # Extra large spacing
    "2xl": "48px",    # Maximum spacing
}

# ============================================================================
# COLOR PALETTE
# ============================================================================
COLORS = {
    # Brand colors
    "primary": "#10A19D",      # Teal (main brand)
    "primary_light": "#52C4B8",  # Light teal
    "secondary": "#FFB84D",    # Orange/gold (accents)
    
    # Semantic colors
    "success": "#51CF66",      # Green for success
    "warning": "#FFD43B",      # Yellow for warning
    "error": "#FF6B6B",        # Red for errors
    "info": "#3B82F6",         # Blue for info
    
    # Neutral/Background
    "background": "#0a0e27",   # Dark background
    "surface": "#1a1f3a",      # Card/container background
    "border": "#2a3050",       # Border color
    "text_primary": "#e0f2f1",  # Primary text
    "text_secondary": "#a0a0a0", # Secondary text
    "text_disabled": "#5a6a8a", # Disabled text
    
    # Gradients (for cards)
    "gradient_primary": "linear-gradient(135deg, rgba(16, 161, 157, 0.15) 0%, rgba(82, 196, 184, 0.08) 100%)",
    "gradient_success": "linear-gradient(135deg, rgba(81, 207, 102, 0.15) 0%, rgba(128, 195, 66, 0.08) 100%)",
    "gradient_warning": "linear-gradient(135deg, rgba(255, 212, 59, 0.15) 0%, rgba(252, 196, 25, 0.08) 100%)",
    "gradient_error": "linear-gradient(135deg, rgba(255, 107, 107, 0.15) 0%, rgba(255, 138, 138, 0.08) 100%)",
}

# ============================================================================
# COMPONENT STYLES
# ============================================================================
COMPONENTS = {
    "card": {
        "border_radius": "12px",
        "padding": "16px",
        "shadow": "0 4px 12px rgba(0, 0, 0, 0.2)",
        "border": f"1px solid {COLORS['border']}",
        "background": COLORS["surface"],
        "hover_shadow": "0 8px 24px rgba(0, 0, 0, 0.3)",
        "transition": "all 0.2s ease",
    },
    "button": {
        "border_radius": "8px",
        "padding": "10px 20px",
        "min_height": "44px",  # WCAG AA accessible
        "font_weight": "600",
        "transition": "all 0.2s ease",
        "shadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
        "hover_shadow": "0 4px 12px rgba(0, 0, 0, 0.2)",
    },
    "input": {
        "border_radius": "8px",
        "padding": "12px",
        "border": f"1px solid {COLORS['border']}",
        "font_size": "14px",
        "min_height": "44px",  # WCAG AA accessible
    },
    "divider": {
        "height": "1px",
        "background": COLORS["border"],
        "margin_y": "24px",
    },
    "notification": {
        "border_radius": "8px",
        "padding": "12px 16px",
        "font_size": "14px",
        "shadow": "0 4px 12px rgba(0, 0, 0, 0.2)",
    },
}

# ============================================================================
# BREAKPOINTS (for responsive design)
# ============================================================================
BREAKPOINTS = {
    "mobile": "375px",     # Small phones
    "tablet": "768px",     # Tablets
    "desktop": "1024px",   # Desktop
    "wide": "1440px",      # Wide desktop
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_card_style(bg_color: str = "surface", border_color: str = "primary", 
                   hover: bool = False, custom_padding: str = None) -> str:
    """
    Generate consistent card styling CSS.
    
    Args:
        bg_color: Background color name from COLORS dict
        border_color: Border color name from COLORS dict
        hover: Whether to include hover effects
        custom_padding: Custom padding (overrides default)
    
    Returns:
        CSS style string
    """
    bg = COLORS.get(bg_color, bg_color)
    border = COLORS.get(border_color, border_color)
    padding = custom_padding or COMPONENTS["card"]["padding"]
    
    style = f"""
    background: {bg};
    border: 1px solid {border};
    border-radius: {COMPONENTS['card']['border_radius']};
    padding: {padding};
    box-shadow: {COMPONENTS['card']['shadow']};
    transition: {COMPONENTS['card']['transition']};
    """
    
    if hover:
        style += f"cursor: pointer; "
    
    return style


def get_heading_style(level: int = 1) -> str:
    """
    Generate consistent heading styling CSS.
    
    Args:
        level: Heading level (1=h1, 2=h2, 3=h3)
    
    Returns:
        CSS style string
    """
    key = f"h{level}"
    h = TYPOGRAPHY[key]
    
    return f"""
    font-size: {h['size']};
    font-weight: {h['weight']};
    line-height: {h['line_height']};
    margin-bottom: {h['margin_bottom']};
    color: {COLORS['text_primary']};
    """


def get_spacing_style(margin_top: str = None, margin_bottom: str = None,
                     padding: str = None) -> str:
    """
    Generate spacing CSS using spacing scale.
    
    Args:
        margin_top: Spacing key (xs, sm, md, lg, xl, 2xl)
        margin_bottom: Spacing key
        padding: Spacing key
    
    Returns:
        CSS style string
    """
    style = ""
    if margin_top:
        style += f"margin-top: {SPACING.get(margin_top, margin_top)}; "
    if margin_bottom:
        style += f"margin-bottom: {SPACING.get(margin_bottom, margin_bottom)}; "
    if padding:
        style += f"padding: {SPACING.get(padding, padding)}; "
    
    return style


# ============================================================================
# DESIGN SYSTEM REFERENCE (for documentation)
# ============================================================================
DESIGN_REFERENCE = """
EatWise Design System Reference
================================

TYPOGRAPHY HIERARCHY:
- H1 (28px, bold): Page titles - "Dashboard", "Log Meal"
- H2 (20px, bold): Major sections - "📊 Statistics", "💧 Water Intake"
- H3 (16px, bold): Subsections - card titles
- Body (14px): Regular text content
- Caption (12px): Small text, helpers, labels
- Label (11px, uppercase): Form labels, badges

SPACING SCALE (8px base):
- xs (4px): Minimal spacing
- sm (8px): Element spacing
- md (16px): Section spacing
- lg (24px): Major section spacing
- xl (32px): Large spacing
- 2xl (48px): Maximum spacing

COLORS:
- Primary: #10A19D (Teal) - Main brand color
- Success: #51CF66 (Green) - Positive actions
- Warning: #FFD43B (Yellow) - Caution
- Error: #FF6B6B (Red) - Errors/Destructive
- Info: #3B82F6 (Blue) - Information

COMPONENTS:
- Card: 12px radius, 16px padding, subtle shadow, hover effect
- Button: 8px radius, 44px min height (accessible), hover shadow
- Input: 8px radius, 44px min height, clear border
- Divider: 1px solid border with md margin (16px)

CONSISTENCY RULES:
1. Always use SPACING scale - don't use arbitrary values
2. All headings must follow typography hierarchy
3. Cards should use get_card_style() helper
4. Buttons must be ≥44px tall for accessibility
5. Use semantic colors (success/warning/error/info consistently)
6. Text contrast must meet WCAG AA (4.5:1 for normal text)
7. Hover states should use shadow and transition effects
"""

if __name__ == "__main__":
    print(DESIGN_REFERENCE)
