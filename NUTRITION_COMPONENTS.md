# Nutrition Components Module

## Overview

The `nutrition_components.py` module provides reusable, modern UI components for displaying nutrition-related information in the EatWise application. This module was created to **modulize and modernize** the nutrition targets display functionality with enhanced styling and flexibility.

## 🎨 Design Philosophy

- **Modularity**: Reusable components that can be imported and used anywhere
- **Modern Styling**: Consistent gradient-based UI matching the overall EatWise design system
- **Flexibility**: Multiple visualization options for different use cases
- **Maintainability**: Centralized nutrition UI logic for easier updates

## 📦 Components

### 1. `display_nutrition_targets_progress(daily_nutrition, targets)`

**Description**: Main component that displays nutrition targets with visual progress bars.

**Features**:
- Clean, modern container with gradient border
- 6 nutrition metrics displayed in 2 columns
- Custom-styled progress bars with gradient colors
- Dynamic color coding based on progress percentage
- Percentage and value indicators

**Parameters**:
```python
daily_nutrition: dict
    {
        "calories": float,
        "protein": float,
        "carbs": float,
        "fat": float,
        "sodium": float,
        "sugar": float
    }

targets: dict
    {
        "calories": float,
        "protein": float,
        "carbs": float,
        "fat": float,
        "sodium": float,
        "sugar": float
    }
```

**Usage**:
```python
from nutrition_components import display_nutrition_targets_progress

daily_nutrition = {
    "calories": 1500,
    "protein": 45,
    "carbs": 200,
    "fat": 50,
    "sodium": 1800,
    "sugar": 35
}

targets = {
    "calories": 2000,
    "protein": 50,
    "carbs": 300,
    "fat": 65,
    "sodium": 2300,
    "sugar": 50
}

display_nutrition_targets_progress(daily_nutrition, targets)
```

**Styling**:
- Container: Gradient background with teal border (#10A19D)
- Progress bars: Dynamic gradient colors based on percentage
  - 🟢 Green (80-100%): Indicates good progress
  - 🟡 Yellow (<80%): Below target
  - 🔴 Red (>100%): Exceeded target

---

### 2. `render_nutrition_progress_bar(label, icon, current, target, unit, show_value)`

**Description**: Single nutrition progress bar component.

**Features**:
- Custom gradient progress bar with shadow effect
- Label and icon display
- Percentage calculation
- Optional value display
- Color-coded feedback

**Parameters**:
```python
label: str          # e.g., "Calories", "Protein"
icon: str           # e.g., "🔥", "💪"
current: float      # Current consumption value
target: float       # Target consumption value
unit: str           # e.g., "g", "mg", "" (optional)
show_value: bool    # Display exact value (default: True)
```

**Usage**:
```python
from nutrition_components import render_nutrition_progress_bar

render_nutrition_progress_bar(
    label="Protein",
    icon="💪",
    current=45,
    target=50,
    unit="g"
)
```

---

### 3. `display_nutrition_summary_cards(daily_nutrition, targets)`

**Description**: Alternative card-based visualization of nutrition metrics.

**Features**:
- Individual metric cards with gradient backgrounds
- Color-coded based on progress percentage
- Compact layout suitable for dashboards
- Hover effects for interactivity

**Parameters**:
Same as `display_nutrition_targets_progress`

**Usage**:
```python
from nutrition_components import display_nutrition_summary_cards

display_nutrition_summary_cards(daily_nutrition, targets)
```

**Card Layout**:
- 4 columns: Calories, Protein, Carbs, Fat
- Each card shows current value, target, and percentage
- Dynamic gradient colors based on progress

---

### 4. `display_nutrition_breakdown_table(daily_nutrition, targets)`

**Description**: Detailed table view of all nutrition metrics.

**Features**:
- Comprehensive table with 7 nutrients
- Current value, target, and percentage columns
- Color-coded percentage values
- Alternating row colors for readability
- Modern gradient header

**Parameters**:
Same as `display_nutrition_targets_progress`

**Usage**:
```python
from nutrition_components import display_nutrition_breakdown_table

display_nutrition_breakdown_table(daily_nutrition, targets)
```

**Nutrients Displayed**:
- 🔥 Calories
- 💪 Protein
- 🍚 Carbs
- 🫒 Fat
- 🧂 Sodium
- 🍬 Sugar
- 🌾 Fiber

---

### 5. `create_nutrition_status_badge(daily_nutrition, targets)`

**Description**: Overall nutrition health status indicator.

**Features**:
- Quick status overview
- Average percentage calculation
- Status indicators with icons
- Color-coded based on overall health

**Parameters**:
Same as `display_nutrition_targets_progress`

**Usage**:
```python
from nutrition_components import create_nutrition_status_badge

create_nutrition_status_badge(daily_nutrition, targets)
```

**Status Levels**:
- 📉 **Below Target** (<70%): Red warning
- ✅ **On Track** (70-110%): Green success
- 📈 **Exceeding Target** (>110%): Red notice

---

### 6. `get_nutrition_color(percentage)`

**Description**: Helper function to get gradient colors based on percentage.

**Returns**: Tuple of (primary_color, gradient_color)

**Parameters**:
```python
percentage: float   # Nutrition percentage of target
```

**Color Mapping**:
- **>100%**: Red gradient (#FF6B6B → #FF8A8A)
- **80-100%**: Green gradient (#51CF66 → #80C342)
- **<80%**: Yellow gradient (#FFD43B → #FFC94D)

**Usage**:
```python
from nutrition_components import get_nutrition_color

primary, gradient = get_nutrition_color(95)  # Returns green gradient
```

---

## 🎨 Color System

All components follow the EatWise color palette:

| State | Primary | Gradient | Usage |
|-------|---------|----------|-------|
| Good | #51CF66 | #80C342 | 80-100% progress |
| Low | #FFD43B | #FFC94D | <80% progress |
| Over | #FF6B6B | #FF8A8A | >100% progress |
| Container | #10A19D | #52C4B8 | Borders, headers |

---

## 🔄 Integration with Main App

The components are fully integrated into `app.py`:

### Before (Inline function):
```python
def display_nutrition_targets_progress(daily_nutrition, targets):
    # 45+ lines of inline code...
    pass
```

### After (Modulized):
```python
from nutrition_components import display_nutrition_targets_progress

# Same usage, cleaner codebase
display_nutrition_targets_progress(daily_nutrition, targets)
```

---

## 📊 Usage Examples

### Example 1: Dashboard View
```python
from nutrition_components import (
    display_nutrition_targets_progress,
    create_nutrition_status_badge
)

# Show status overview
create_nutrition_status_badge(daily_nutrition, targets)

# Show detailed progress
display_nutrition_targets_progress(daily_nutrition, targets)
```

### Example 2: Analytics View
```python
from nutrition_components import display_nutrition_breakdown_table

# Show detailed breakdown
display_nutrition_breakdown_table(daily_nutrition, targets)
```

### Example 3: Compact Card View
```python
from nutrition_components import display_nutrition_summary_cards

# Show compact cards
display_nutrition_summary_cards(daily_nutrition, targets)
```

### Example 4: Single Metric
```python
from nutrition_components import render_nutrition_progress_bar

render_nutrition_progress_bar(
    label="Daily Calories",
    icon="🔥",
    current=1500,
    target=2000,
    unit=""
)
```

---

## 🎯 Benefits

### ✅ Code Organization
- Separates nutrition UI logic into a dedicated module
- Reduces clutter in main `app.py`
- Improves code readability and maintainability

### ✅ Reusability
- Components can be imported anywhere in the application
- Use multiple visualization styles for different pages
- Share consistent styling across features

### ✅ Maintainability
- Single source of truth for nutrition styling
- Easy to update colors, styling globally
- Simpler to add new nutrition-related components

### ✅ Consistency
- All nutrition displays use the same design system
- Consistent color coding and visualization
- Professional, cohesive appearance

### ✅ Extensibility
- Easy to add new components (e.g., micro/macro breakdown)
- Can create specialized variants for specific use cases
- Foundation for future nutrition features

---

## 🚀 Future Enhancements

Potential additions to the module:

1. **Nutrient Breakdown Pie Chart**
   - Macronutrient composition visualization
   - Interactive Plotly chart

2. **Weekly Nutrition Comparison**
   - Compare this week vs. previous week
   - Trend visualization

3. **Goal Achievement Progress**
   - Multi-day/week progress tracking
   - Milestone indicators

4. **Recommendation Cards**
   - Show what to eat to meet targets
   - Food suggestions based on gaps

5. **Nutrition Export**
   - PDF/CSV report generation
   - Shareable nutrition summary

---

## 📝 Documentation

Each component includes:
- Comprehensive docstrings
- Parameter descriptions
- Usage examples
- Type hints for clarity

---

## ✨ Styling Updates

### Progress Bars
- Custom CSS with gradient fill
- Smooth animations
- Glow effect on overflow

### Cards
- Gradient backgrounds
- Border styling matching theme
- Hover effects (future enhancement)

### Tables
- Alternating row colors
- Gradient headers
- Color-coded percentage cells

---

## 🔗 Related Files

- **app.py**: Main application (uses components)
- **utils.py**: Contains `calculate_nutrition_percentage()` helper
- **config.py**: Defines nutrition targets
- **UI_MODERNIZATION.md**: Overall design system documentation

---

## 👨‍💻 Development Notes

### Adding a New Component

1. Create function with clear docstring
2. Add type hints for parameters
3. Use `st.markdown()` for custom HTML/CSS
4. Follow color system and styling conventions
5. Include usage example in docstring
6. Update this documentation

### Styling Best Practices

- Use CSS grid/flexbox in HTML for layout
- Apply gradients consistently
- Add subtle shadows for depth
- Use semi-transparent colors for layering
- Ensure dark mode compatibility

---

## 📞 Support

For questions or suggestions about nutrition components:
1. Check existing components for similar functionality
2. Review docstrings and examples
3. Refer to color system documentation
4. Check app.py for integration patterns

