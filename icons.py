"""
SVG Icon System for EatWise
Professional SVG icons to replace emoji usage throughout the app.
Icons are from Heroicons and Lucide for consistency.
"""

from typing import Literal


# Icon size presets (in pixels)
ICON_SIZES = {
    "xs": 14,
    "sm": 18,
    "md": 24,
    "lg": 32,
    "xl": 48,
    "2xl": 64,
}

IconSize = Literal["xs", "sm", "md", "lg", "xl", "2xl"]


def _wrap_svg(path_d: str, size: int, color: str, view_box: str = "0 0 24 24", 
              fill: str = "none", stroke_width: str = "2", extra_attrs: str = "") -> str:
    """Wrap SVG path in proper SVG container with styling."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{view_box}" fill="{fill}" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle; flex-shrink: 0;" {extra_attrs}>{path_d}</svg>'''


def _filled_svg(path_d: str, size: int, color: str, view_box: str = "0 0 24 24") -> str:
    """Wrap SVG path for filled icons."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{view_box}" fill="{color}" style="display: inline-block; vertical-align: middle; flex-shrink: 0;">{path_d}</svg>'''


# ============== NUTRITION ICONS ==============

def icon_flame(size: IconSize = "md", color: str = "#FF6B35") -> str:
    """Fire/Flame icon for Calories - Heroicons solid"""
    s = ICON_SIZES.get(size, 24)
    path = '<path d="M12.356 2.082a.75.75 0 0 1 .416.672c0 1.754.394 3.204 1.068 4.456.635 1.18 1.476 2.164 2.318 3.148.167.196.335.392.501.59 1.482 1.77 2.841 3.6 2.841 6.302 0 3.726-2.965 6.75-6.625 6.75S6.25 20.976 6.25 17.25c0-2.702 1.36-4.532 2.841-6.301.166-.199.334-.395.501-.59.842-.985 1.683-1.97 2.318-3.149.674-1.252 1.068-2.702 1.068-4.456a.75.75 0 0 1 .416-.672.75.75 0 0 1 .962.318.75.75 0 0 1-.962.682c0 1.754-.394 3.204-1.068 4.456-.635 1.18-1.476 2.164-2.318 3.148-.167.196-.335.392-.501.59-1.482 1.77-2.841 3.6-2.841 6.302 0 2.9 2.282 5.25 5.125 5.25s5.125-2.35 5.125-5.25c0-2.702-1.36-4.532-2.841-6.301-.166-.199-.334-.395-.501-.59-.842-.985-1.683-1.97-2.318-3.149-.674-1.252-1.068-2.702-1.068-4.456z"/>'
    # Use simpler flame path
    path = '<path fill-rule="evenodd" d="M12.963 2.286a.75.75 0 0 0-1.071-.136 9.742 9.742 0 0 0-3.539 6.176 7.547 7.547 0 0 1-1.705-1.715.75.75 0 0 0-1.152-.082A9 9 0 1 0 15.68 4.534a7.46 7.46 0 0 1-2.717-2.248ZM15.75 14.25a3.75 3.75 0 1 1-7.313-1.172c.628.465 1.35.81 2.133 1a5.99 5.99 0 0 1 1.925-3.546 3.75 3.75 0 0 1 3.255 3.718Z" clip-rule="evenodd"/>'
    return _filled_svg(path, s, color)


def icon_protein(size: IconSize = "md", color: str = "#51CF66") -> str:
    """Muscle/Dumbbell icon for Protein - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="m6.5 6.5 11 11"/><path d="m21 21-1-1"/><path d="m3 3 1 1"/><path d="m18 22 4-4"/><path d="m2 6 4-4"/><path d="m3 10 7-7"/><path d="m14 21 7-7"/>'''
    return _wrap_svg(path, s, color)


def icon_wheat(size: IconSize = "md", color: str = "#845EF7") -> str:
    """Wheat/Grain icon for Carbs - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M2 22 16 8"/><path d="M3.47 12.53 5 11l1.53 1.53a3.5 3.5 0 0 1 0 4.94L5 19l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/><path d="M7.47 8.53 9 7l1.53 1.53a3.5 3.5 0 0 1 0 4.94L9 15l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/><path d="M11.47 4.53 13 3l1.53 1.53a3.5 3.5 0 0 1 0 4.94L13 11l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/><path d="M20 2h2v2a4 4 0 0 1-4 4h-2V6a4 4 0 0 1 4-4Z"/><path d="M11.47 17.47 13 19l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L5 19l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/><path d="M15.47 13.47 17 15l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L9 15l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/><path d="M19.47 9.47 21 11l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L13 11l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/>'''
    return _wrap_svg(path, s, color)


def icon_droplet(size: IconSize = "md", color: str = "#FFD43B") -> str:
    """Droplet icon for Fat/Oil - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>'
    return _wrap_svg(path, s, color, fill=color + "30")


def icon_salt(size: IconSize = "md", color: str = "#94A3B8") -> str:
    """Salt shaker icon for Sodium - Custom"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M8 2h8l1 4H7l1-4Z"/><rect x="7" y="6" width="10" height="14" rx="1"/><circle cx="9" cy="10" r="0.5" fill="currentColor"/><circle cx="12" cy="12" r="0.5" fill="currentColor"/><circle cx="15" cy="10" r="0.5" fill="currentColor"/><circle cx="10" cy="14" r="0.5" fill="currentColor"/><circle cx="14" cy="14" r="0.5" fill="currentColor"/><circle cx="12" cy="16" r="0.5" fill="currentColor"/>'''
    return _wrap_svg(path, s, color)


def icon_candy(size: IconSize = "md", color: str = "#F472B6") -> str:
    """Candy icon for Sugar - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="m9.5 7.5-2 2a4.95 4.95 0 1 0 7 7l2-2a4.95 4.95 0 1 0-7-7Z"/><path d="M14 6.5v10"/><path d="M10 7.5v10"/><path d="m16 7 1-5 1.37.68A3 3 0 0 0 19.7 3H21v1.3c0 .46.1.92.32 1.33L22 7l-5 1"/><path d="m8 17-1 5-1.37-.68A3 3 0 0 0 4.3 21H3v-1.3a3 3 0 0 0-.32-1.33L2 17l5-1"/>'''
    return _wrap_svg(path, s, color)


def icon_leaf(size: IconSize = "md", color: str = "#22C55E") -> str:
    """Leaf icon for Fiber - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>'''
    return _wrap_svg(path, s, color)


# ============== WATER/HYDRATION ICONS ==============

def icon_water(size: IconSize = "md", color: str = "#3B82F6") -> str:
    """Water glass icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M5.116 4.104A1 1 0 0 1 6.11 3h11.78a1 1 0 0 1 .994 1.105l-1.6 16a1 1 0 0 1-.994.895H7.71a1 1 0 0 1-.994-.895l-1.6-16Z"/><path d="M6 12h12"/>'''
    return _wrap_svg(path, s, color)


def icon_droplets(size: IconSize = "md", color: str = "#60A5FA") -> str:
    """Multiple droplets for hydration - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/><path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/>'''
    return _wrap_svg(path, s, color)


# ============== MEAL TYPE ICONS ==============

def icon_sunrise(size: IconSize = "md", color: str = "#FBBF24") -> str:
    """Sunrise icon for Breakfast - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M12 2v8"/><path d="m4.93 10.93 1.41 1.41"/><path d="M2 18h2"/><path d="M20 18h2"/><path d="m19.07 10.93-1.41 1.41"/><path d="M22 22H2"/><path d="m8 6 4-4 4 4"/><path d="M16 18a4 4 0 0 0-8 0"/>'''
    return _wrap_svg(path, s, color)


def icon_utensils(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Fork and knife for Lunch/Dinner - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>'''
    return _wrap_svg(path, s, color)


def icon_moon(size: IconSize = "md", color: str = "#8B5CF6") -> str:
    """Moon icon for Dinner - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'
    return _wrap_svg(path, s, color)


def icon_apple(size: IconSize = "md", color: str = "#EF4444") -> str:
    """Apple icon for Snack - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.9 4.9 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z"/><path d="M10 2c1 .5 2 2 2 5"/>'''
    return _wrap_svg(path, s, color)


def icon_coffee(size: IconSize = "md", color: str = "#A78BFA") -> str:
    """Coffee cup for Beverage - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/>'''
    return _wrap_svg(path, s, color)


# ============== GAMIFICATION ICONS ==============

def icon_trophy(size: IconSize = "md", color: str = "#FFD43B") -> str:
    """Trophy icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>'''
    return _wrap_svg(path, s, color)


def icon_medal(size: IconSize = "md", color: str = "#F59E0B") -> str:
    """Medal icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M7.21 15 2.66 7.14a2 2 0 0 1 .13-2.2L4.4 2.8A2 2 0 0 1 6 2h12a2 2 0 0 1 1.6.8l1.6 2.14a2 2 0 0 1 .14 2.2L16.79 15"/><path d="M11 12 5.12 2.2"/><path d="m13 12 5.88-9.8"/><path d="M8 7h8"/><circle cx="12" cy="17" r="5"/><path d="M12 18v-2h-.5"/>'''
    return _wrap_svg(path, s, color)


def icon_zap(size: IconSize = "md", color: str = "#FBBF24") -> str:
    """Lightning bolt for XP/Energy - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>'
    return _wrap_svg(path, s, color, fill=color)


def icon_fire(size: IconSize = "md", color: str = "#FF6B35") -> str:
    """Fire icon for Streaks - Lucide (outline)"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>'''
    return _wrap_svg(path, s, color, fill=color + "30")


def icon_target(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Target/Goal icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'''
    return _wrap_svg(path, s, color)


def icon_star(size: IconSize = "md", color: str = "#FBBF24", filled: bool = False) -> str:
    """Star icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>'
    if filled:
        return _filled_svg(path, s, color)
    return _wrap_svg(path, s, color, fill="none")


def icon_crown(size: IconSize = "md", color: str = "#FFD43B") -> str:
    """Crown for achievements - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z"/><path d="M5 21h14"/>'''
    return _wrap_svg(path, s, color, fill=color + "30")


# ============== STATUS/FEEDBACK ICONS ==============

def icon_check_circle(size: IconSize = "md", color: str = "#22C55E") -> str:
    """Checkmark circle for success - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>'''
    return _wrap_svg(path, s, color)


def icon_alert_triangle(size: IconSize = "md", color: str = "#F59E0B") -> str:
    """Warning triangle - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>'''
    return _wrap_svg(path, s, color)


def icon_x_circle(size: IconSize = "md", color: str = "#EF4444") -> str:
    """X circle for error/danger - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>'''
    return _wrap_svg(path, s, color)


def icon_info(size: IconSize = "md", color: str = "#3B82F6") -> str:
    """Info icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>'''
    return _wrap_svg(path, s, color)


def icon_trending_up(size: IconSize = "md", color: str = "#22C55E") -> str:
    """Trending up arrow - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'''
    return _wrap_svg(path, s, color)


def icon_trending_down(size: IconSize = "md", color: str = "#EF4444") -> str:
    """Trending down arrow - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>'''
    return _wrap_svg(path, s, color)


# ============== NAVIGATION/ACTION ICONS ==============

def icon_plus(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Plus icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M5 12h14"/><path d="M12 5v14"/>'''
    return _wrap_svg(path, s, color)


def icon_minus(size: IconSize = "md", color: str = "#94A3B8") -> str:
    """Minus icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '<path d="M5 12h14"/>'
    return _wrap_svg(path, s, color)


def icon_chart(size: IconSize = "md", color: str = "#8B5CF6") -> str:
    """Bar chart icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/>'''
    return _wrap_svg(path, s, color)


def icon_calendar(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Calendar icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>'''
    return _wrap_svg(path, s, color)


def icon_clock(size: IconSize = "md", color: str = "#94A3B8") -> str:
    """Clock icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'''
    return _wrap_svg(path, s, color)


def icon_user(size: IconSize = "md", color: str = "#10A19D") -> str:
    """User profile icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'''
    return _wrap_svg(path, s, color)


def icon_settings(size: IconSize = "md", color: str = "#94A3B8") -> str:
    """Settings gear icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>'''
    return _wrap_svg(path, s, color)


def icon_camera(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Camera icon for photo logging - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>'''
    return _wrap_svg(path, s, color)


def icon_sparkles(size: IconSize = "md", color: str = "#A78BFA") -> str:
    """Sparkles/AI magic icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>'''
    return _wrap_svg(path, s, color)


def icon_message(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Message/Chat icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>'''
    return _wrap_svg(path, s, color)


def icon_restaurant(size: IconSize = "md", color: str = "#F59E0B") -> str:
    """Restaurant/Menu icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>'''
    return _wrap_svg(path, s, color)


def icon_help_circle(size: IconSize = "md", color: str = "#10A19D") -> str:
    """Help/Question circle icon - Lucide"""
    s = ICON_SIZES.get(size, 24)
    path = '''<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>'''
    return _wrap_svg(path, s, color)


# ============== HELPER FUNCTIONS ==============

def get_nutrition_icon(nutrient: str, size: IconSize = "md") -> str:
    """Get the appropriate icon for a nutrition type."""
    icons = {
        "calories": icon_flame,
        "protein": icon_protein,
        "carbs": icon_wheat,
        "fat": icon_droplet,
        "sodium": icon_salt,
        "sugar": icon_candy,
        "fiber": icon_leaf,
        "water": icon_water,
    }
    icon_func = icons.get(nutrient.lower(), icon_flame)
    return icon_func(size=size)


def get_meal_type_icon(meal_type: str, size: IconSize = "md") -> str:
    """Get the appropriate icon for a meal type."""
    icons = {
        "breakfast": icon_sunrise,
        "lunch": icon_utensils,
        "dinner": icon_moon,
        "snack": icon_apple,
        "beverage": icon_coffee,
    }
    icon_func = icons.get(meal_type.lower(), icon_utensils)
    return icon_func(size=size)


# ============== RADIAL PROGRESS COMPONENT ==============

def radial_progress(
    percentage: float,
    size: int = 120,
    stroke_width: int = 10,
    color: str = "#10A19D",
    bg_color: str = "rgba(255,255,255,0.1)",
    label: str = "",
    value_text: str = "",
    show_percentage: bool = True
) -> str:
    """
    Generate a radial/circular progress indicator.
    
    Args:
        percentage: Progress percentage (0-100)
        size: Diameter of the circle in pixels
        stroke_width: Width of the progress stroke
        color: Color of the progress arc
        bg_color: Background circle color
        label: Label text below the value
        value_text: Custom value text (overrides percentage display)
        show_percentage: Whether to show percentage number
    
    Returns:
        HTML string for the radial progress component
    """
    # Calculate circle properties
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius
    
    # Clamp percentage between 0 and 100
    pct = max(0, min(100, percentage))
    stroke_offset = circumference - (pct / 100) * circumference
    
    # Determine display text
    if value_text:
        display_text = value_text
    elif show_percentage:
        display_text = f"{pct:.0f}%"
    else:
        display_text = ""
    
    # Extract RGB for glow effect
    if color.startswith("#"):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        glow_color = f"rgba({r}, {g}, {b}, 0.3)"
    else:
        glow_color = "rgba(16, 161, 157, 0.3)"
    
    return f'''
    <div style="position: relative; width: {size}px; height: {size}px; display: inline-flex; align-items: center; justify-content: center;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <!-- Background circle -->
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="{bg_color}"
                stroke-width="{stroke_width}"
            />
            <!-- Progress circle -->
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="{color}"
                stroke-width="{stroke_width}"
                stroke-linecap="round"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{stroke_offset}"
                style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1); filter: drop-shadow(0 0 6px {glow_color});"
            />
        </svg>
        <div style="position: absolute; text-align: center;">
            <div style="font-size: {size/4}px; font-weight: 700; color: {color};">{display_text}</div>
            {f'<div style="font-size: {size/8}px; color: #94A3B8; margin-top: 2px;">{label}</div>' if label else ''}
        </div>
    </div>
    '''


def radial_nutrition_card(
    nutrient: str,
    current: float,
    target: float,
    unit: str = "",
    size: int = 100
) -> str:
    """
    Generate a complete radial nutrition card with icon and labels.
    
    Args:
        nutrient: Nutrient name (calories, protein, carbs, fat, sodium, sugar, fiber)
        current: Current consumption value
        target: Target value
        unit: Unit of measurement
        size: Size of the radial progress
    
    Returns:
        HTML string for the complete card
    """
    percentage = (current / target * 100) if target > 0 else 0
    
    # Color mapping
    colors = {
        "calories": "#FF6B35",
        "protein": "#51CF66",
        "carbs": "#845EF7",
        "fat": "#FFD43B",
        "sodium": "#94A3B8",
        "sugar": "#F472B6",
        "fiber": "#22C55E",
    }
    color = colors.get(nutrient.lower(), "#10A19D")
    
    # Determine color based on percentage
    if percentage > 100:
        progress_color = "#FF6B6B"  # Over target - red
    elif percentage >= 80:
        progress_color = "#51CF66"  # Good - green
    else:
        progress_color = color  # Use nutrient color
    
    icon = get_nutrition_icon(nutrient, size="md")
    value_text = f"{current:.0f}" if not unit else f"{current:.0f}"
    
    return f'''
    <div style="
        background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
    ">
        <div style="margin-bottom: 4px;">{icon}</div>
        {radial_progress(percentage, size=size, color=progress_color, value_text=value_text, label=unit or "")}
        <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-top: 4px;">
            {nutrient.title()}
        </div>
        <div style="font-size: 10px; color: {progress_color}; font-weight: 600;">
            {percentage:.0f}% of {target:.0f}{unit}
        </div>
    </div>
    '''
