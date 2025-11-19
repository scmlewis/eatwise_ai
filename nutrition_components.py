"""
Nutrition UI Components Module
Reusable, modern nutrition-related UI components for the EatWise application
"""

import streamlit as st
from utils import calculate_nutrition_percentage


def get_nutrition_color(percentage: float) -> tuple[str, str]:
    """
    Get gradient color based on nutrition percentage.
    
    Args:
        percentage: Nutrition percentage of target
        
    Returns:
        Tuple of (primary_color, gradient_color)
    """
    if percentage > 100:
        return ("#FF6B6B", "#FF8A8A")  # Red - Over target
    elif percentage >= 80:
        return ("#51CF66", "#80C342")  # Green - Good
    else:
        return ("#FFD43B", "#FFC94D")  # Yellow - Below target


def render_nutrition_progress_bar(
    label: str,
    icon: str,
    current: float,
    target: float,
    unit: str = "",
    show_value: bool = True
) -> None:
    """
    Render a single nutrition progress bar with modern styling.
    
    Args:
        label: Nutrition name (e.g., "Calories", "Protein")
        icon: Emoji icon for the nutrient
        current: Current consumption value
        target: Target consumption value
        unit: Unit of measurement (e.g., "g", "mg")
        show_value: Whether to show the exact value
    """
    percentage = calculate_nutrition_percentage(current, target)
    primary_color, gradient_color = get_nutrition_color(percentage)
    
    # Determine if this is a "limit" nutrient (should not exceed)
    limit_nutrients = ["sodium", "sugar", "fat"]
    is_limit_nutrient = any(lim.lower() in label.lower() for lim in limit_nutrients)
    
    # Cap bar at 100% visually but show actual percentage in text
    bar_width = min(percentage, 100)
    
    # Display percentage and value text
    if show_value:
        value_text = f"{current:.1f}{unit}" if unit else f"{current:.0f}"
        target_text = f"{target:.1f}{unit}" if unit else f"{target:.0f}"
        percentage_text = f"↑ {percentage:.0f}% • {value_text} of {target_text}"
    else:
        percentage_text = f"↑ {percentage:.0f}%"
    
    # Extract RGB values from hex color for glow effect
    rgb_str = f"{int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}"
    
    # Build warning section if needed
    warning_html = ""
    if is_limit_nutrient and percentage > 100:
        excess_amount = current - target
        warning_html = f"""
        <div style="color: #FF6B6B; font-size: 12px; font-weight: 600; margin-bottom: 6px;">
            ⚠️ Exceeded by {excess_amount:.1f}{unit}
        </div>
        """
    
    # Create complete progress bar with label, bar, and text in one HTML block
    progress_html = f"""
    <div style="width: 100%; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="color: #e0f2f1; font-size: 13px; font-weight: 500;">{icon} {label}</span>
        </div>
        {warning_html}
        <div style="
            width: 100%;
            background: #2a2a3e;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 6px;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
            box-sizing: border-box;
        ">
            <div style="
                background: linear-gradient(90deg, {primary_color} 0%, {gradient_color} 100%);
                height: 100%;
                width: {bar_width}%;
                border-radius: 4px;
                transition: width 0.3s ease;
                box-shadow: 0 0 10px rgba({rgb_str}, 0.5);
            "></div>
        </div>
        <div style="color: #a0a0a0; font-size: 11px; text-align: left;">
            {percentage_text}
        </div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)


def display_nutrition_targets_progress(daily_nutrition: dict, targets: dict) -> None:
    """
    Display nutrition targets progress in a modern, styled container.
    
    This is a modulized component that displays all nutrition targets
    with visual progress bars and modern gradient styling.
    
    Args:
        daily_nutrition: Dictionary with current nutrition values
                        (calories, protein, carbs, fat, sodium, sugar)
        targets: Dictionary with target nutrition values
    
    Example:
        >>> daily_nutrition = {
        ...     "calories": 1500,
        ...     "protein": 45,
        ...     "carbs": 200,
        ...     "fat": 50,
        ...     "sodium": 1800,
        ...     "sugar": 35
        ... }
        >>> targets = {
        ...     "calories": 2000,
        ...     "protein": 50,
        ...     "carbs": 300,
        ...     "fat": 65,
        ...     "sodium": 2300,
        ...     "sugar": 50
        ... }
        >>> display_nutrition_targets_progress(daily_nutrition, targets)
    """
    # Display title outside container
    st.markdown("""
    <h2 style="color: white; margin: 0 0 20px 0; display: flex; align-items: center; gap: 8px; font-size: 1.5em; font-weight: 600;">
        📊 Nutrition Targets Progress
    </h2>
    """, unsafe_allow_html=True)
    
    # Create two columns for nutrition targets
    col1, col2 = st.columns(2)
    
    nutrition_items = [
        {
            "col": col1,
            "label": "Calories",
            "icon": "🔥",
            "key": "calories",
            "unit": ""
        },
        {
            "col": col1,
            "label": "Protein",
            "icon": "💪",
            "key": "protein",
            "unit": "g"
        },
        {
            "col": col1,
            "label": "Carbs",
            "icon": "🍚",
            "key": "carbs",
            "unit": "g"
        },
        {
            "col": col2,
            "label": "Fat",
            "icon": "🫒",
            "key": "fat",
            "unit": "g"
        },
        {
            "col": col2,
            "label": "Sodium",
            "icon": "🧂",
            "key": "sodium",
            "unit": "mg"
        },
        {
            "col": col2,
            "label": "Sugar",
            "icon": "🍬",
            "key": "sugar",
            "unit": "g"
        }
    ]
    
    # Render each nutrition item
    for item in nutrition_items:
        with item["col"]:
            render_nutrition_progress_bar(
                label=item["label"],
                icon=item["icon"],
                current=daily_nutrition.get(item["key"], 0),
                target=targets.get(item["key"], 0),
                unit=item["unit"]
            )


def display_nutrition_summary_cards(daily_nutrition: dict, targets: dict) -> None:
    """
    Display nutrition summary as modern metric cards.
    
    Alternative visualization for nutrition targets as individual cards
    rather than progress bars. Useful for different layout contexts.
    
    Args:
        daily_nutrition: Dictionary with current nutrition values
        targets: Dictionary with target nutrition values
    """
    st.markdown("""
    <h3 style="color: #52C4B8; margin: 0 0 20px 0; display: flex; align-items: center; gap: 8px;">
        📊 Nutrition Summary
    </h3>
    """, unsafe_allow_html=True)
    
    nutrition_items = [
        {
            "icon": "🔥",
            "label": "Calories",
            "key": "calories",
            "unit": "",
            "color": "#FF6B16"
        },
        {
            "icon": "💪",
            "label": "Protein",
            "key": "protein",
            "unit": "g",
            "color": "#51CF66"
        },
        {
            "icon": "🍚",
            "label": "Carbs",
            "key": "carbs",
            "unit": "g",
            "color": "#845EF7"
        },
        {
            "icon": "🫒",
            "label": "Fat",
            "key": "fat",
            "unit": "g",
            "color": "#FFD43B"
        }
    ]
    
    cols = st.columns(len(nutrition_items), gap="small")
    
    for idx, item in enumerate(nutrition_items):
        with cols[idx]:
            current = daily_nutrition.get(item["key"], 0)
            target = targets.get(item["key"], 0)
            percentage = calculate_nutrition_percentage(current, target)
            
            # Determine color based on percentage
            if percentage > 100:
                color = "#FF6B6B"
                gradient_color = "#FF8A8A"
            elif percentage >= 80:
                color = "#51CF66"
                gradient_color = "#80C342"
            else:
                color = "#FFD43B"
                gradient_color = "#FFC94D"
            
            value_text = f"{current:.1f}{item['unit']}" if item['unit'] else f"{current:.0f}"
            target_text = f"{target:.1f}{item['unit']}" if item['unit'] else f"{target:.0f}"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}20 0%, {gradient_color}40 100%);
                border: 2px solid {color};
                border-radius: 10px;
                padding: 12px;
                text-align: center;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 6px;
                box-shadow: 0 4px 12px rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            ">
                <div style="font-size: 28px;">{item['icon']}</div>
                <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{item['label']}</div>
                <div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{value_text}</div>
                <div style="font-size: 9px; color: {color}; font-weight: 600;">↑ {percentage:.0f}% of {target_text}</div>
            </div>
            """, unsafe_allow_html=True)


def display_nutrition_breakdown_table(daily_nutrition: dict, targets: dict) -> None:
    """
    Display nutrition information in a detailed table format.
    
    Provides a comprehensive view of all nutrition metrics with
    current values, targets, and percentage of goal.
    
    Args:
        daily_nutrition: Dictionary with current nutrition values
        targets: Dictionary with target nutrition values
    """
    st.markdown("""
    <h3 style="color: #52C4B8; margin: 0 0 20px 0; display: flex; align-items: center; gap: 8px;">
        📋 Detailed Nutrition Breakdown
    </h3>
    """, unsafe_allow_html=True)
    
    nutrition_items = [
        {"label": "Calories", "key": "calories", "unit": "", "icon": "🔥"},
        {"label": "Protein", "key": "protein", "unit": "g", "icon": "💪"},
        {"label": "Carbs", "key": "carbs", "unit": "g", "icon": "🍚"},
        {"label": "Fat", "key": "fat", "unit": "g", "icon": "🫒"},
        {"label": "Sodium", "key": "sodium", "unit": "mg", "icon": "🧂"},
        {"label": "Sugar", "key": "sugar", "unit": "g", "icon": "🍬"},
        {"label": "Fiber", "key": "fiber", "unit": "g", "icon": "🌾"},
    ]
    
    # Create table rows
    table_html = """
    <div style="
        border: 2px solid #10A19D40;
        border-radius: 10px;
        overflow: hidden;
        background: linear-gradient(135deg, #1a3a3820 0%, #2a4a4a25 100%);
    ">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%); color: white;">
                    <th style="padding: 12px; text-align: left; font-weight: 600;">Nutrient</th>
                    <th style="padding: 12px; text-align: center; font-weight: 600;">Current</th>
                    <th style="padding: 12px; text-align: center; font-weight: 600;">Target</th>
                    <th style="padding: 12px; text-align: center; font-weight: 600;">% Progress</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for idx, item in enumerate(nutrition_items):
        current = daily_nutrition.get(item["key"], 0)
        target = targets.get(item["key"], 0)
        percentage = calculate_nutrition_percentage(current, target)
        
        # Alternate row colors
        row_bg = "#1a3a3825" if idx % 2 == 0 else "#0a1a1810"
        
        # Color code based on percentage
        if percentage > 100:
            pct_color = "#FF6B6B"
        elif percentage >= 80:
            pct_color = "#51CF66"
        else:
            pct_color = "#FFD43B"
        
        current_text = f"{current:.1f}{item['unit']}" if item['unit'] else f"{current:.0f}"
        target_text = f"{target:.1f}{item['unit']}" if item['unit'] else f"{target:.0f}"
        
        table_html += f"""
                <tr style="background: {row_bg}; border-bottom: 1px solid #10A19D20;">
                    <td style="padding: 12px; color: #e0f2f1; font-weight: 500;">{item['icon']} {item['label']}</td>
                    <td style="padding: 12px; text-align: center; color: #a0a0a0;">{current_text}</td>
                    <td style="padding: 12px; text-align: center; color: #a0a0a0;">{target_text}</td>
                    <td style="padding: 12px; text-align: center; color: {pct_color}; font-weight: 600;">{percentage:.0f}%</td>
                </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)


def create_nutrition_status_badge(daily_nutrition: dict, targets: dict) -> None:
    """
    Create a status badge showing overall nutrition health.
    
    Displays a quick overview of whether the user is meeting their
    nutrition targets in a visually appealing format.
    
    Args:
        daily_nutrition: Dictionary with current nutrition values
        targets: Dictionary with target nutrition values
    """
    # Calculate average percentage across key nutrients
    key_nutrients = ["calories", "protein", "carbs", "fat", "sodium", "sugar"]
    percentages = [
        calculate_nutrition_percentage(
            daily_nutrition.get(nutrient, 0),
            targets.get(nutrient, 0)
        )
        for nutrient in key_nutrients
    ]
    
    avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    
    # Determine status
    if avg_percentage < 70:
        status = "Below Target"
        status_icon = "📉"
        color = "#FFD43B"
    elif avg_percentage <= 110:
        status = "On Track"
        status_icon = "✅"
        color = "#51CF66"
    else:
        status = "Exceeding Target"
        status_icon = "📈"
        color = "#FF6B6B"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}20 0%, {color}40 100%);
        border: 2px solid {color};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2);
    ">
        <div style="font-size: 24px; margin-bottom: 8px;">{status_icon}</div>
        <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 4px;">Nutrition Status</div>
        <div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{status}</div>
        <div style="font-size: 12px; color: {color}; font-weight: 600; margin-top: 6px;">Average: {avg_percentage:.0f}% of target</div>
    </div>
    """, unsafe_allow_html=True)
