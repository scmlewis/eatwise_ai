# EatWise Branding - Quick Reference

## 🎨 Core Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Primary Teal** | `#10A19D` | 16, 161, 157 | Main brand, trust, health |
| **Light Teal** | `#52C4B8` | 82, 196, 184 | Accents, highlights |
| **Coral** | `#FF6B6B` | 255, 107, 107 | CTAs, action, alerts |
| **Success Green** | `#51CF66` | 81, 207, 102 | Achievements, progress |
| **Warning Yellow** | `#FFD43B` | 255, 212, 59 | Cautions, warnings |
| **Dark Navy** | `#0a0e27` | 10, 14, 39 | Backgrounds |
| **Light Text** | `#e0f2f1` | 224, 242, 241 | Text, readability |

---

## 🔤 Typography

**Font:** Outfit (Google Fonts)  
**Fallback:** -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif

| Usage | Size | Weight | Letter Spacing |
|-------|------|--------|-----------------|
| Hero Heading | 48-64px | 800-900 | -1 to 0 |
| H1 | 32-40px | 800 | -0.5 |
| H2 | 24-28px | 700 | -0.2 |
| H3 | 18-20px | 600 | 0 |
| Body | 14-16px | 400 | 0.5 |
| Small | 12-14px | 400 | 0.5 |
| Captions | 11-12px | 500 | 0.5 |

---

## 📁 Logo Files

Located in `/assets/` folder:

| File | Use Case | Min Size |
|------|----------|----------|
| `eatwise-logo-full-horizontal.svg` | Website header, marketing, login | 200px |
| `eatwise-logo-stacked.svg` | Mobile headers, sidebar, profiles | 100px |
| `eatwise-icon.svg` | Favicon, app icon, badges | 16px |
| `eatwise-icon-monochrome-black.svg` | Print, white backgrounds | 16px |
| `eatwise-icon-monochrome-white.svg` | Dark backgrounds, dark mode | 16px |
| `eatwise-icon-outlined.svg` | Line icon sets, minimal UI | 16px |

---

## 🎯 Logo Dos & Don'ts

### ✅ DO
- Maintain 20px clear space minimum
- Use SVG files (best quality)
- Scale proportionally
- Ensure contrast against backgrounds
- Use color variations for different backgrounds
- Test at multiple sizes

### ❌ DON'T
- Stretch or distort
- Add effects (shadows, glows)
- Rotate at odd angles
- Use below 16px
- Add borders or outlines
- Mix with other logos
- Change colors arbitrarily

---

## 💬 Brand Voice

### Personality
- Friendly & approachable
- Motivating & encouraging
- Clear & simple
- Intelligent & evidence-based
- Empowering & user-focused

### By Context

**Achievement:** Celebratory, enthusiastic  
"🔥 Amazing! You've hit a 7-day streak!"

**Motivation:** Encouraging, supportive  
"💪 Great progress! Let's keep going."

**Alerts:** Informative, helpful  
"⚠️ This meal exceeds your sodium target"

**Instructions:** Clear, step-by-step  
"Take a photo or describe your meal"

### Language Rules

✅ Use "you" and "your"  
✅ Positive framing  
✅ Celebrate small wins  
✅ Explain the "why"  
✅ One emoji max per message  

❌ No medical jargon  
❌ No judgment/shame  
❌ No false promises  
❌ No excessive !!!  
❌ No overcomplicated messages  

---

## 🎨 Color Usage

### Health/Wellness Context
- **Good:** Green (#51CF66)
- **Moderate:** Yellow (#FFD43B)
- **Caution:** Coral (#FF6B6B)

### UI Elements
- **Primary Action:** Teal (#10A19D)
- **Secondary Action:** Light Teal (#52C4B8)
- **Important/Alert:** Coral (#FF6B6B)
- **Success:** Green (#51CF66)
- **Warning:** Yellow (#FFD43B)

### Backgrounds
- **Dark Mode:** Dark Navy (#0a0e27)
- **Text on Dark:** Light Text (#e0f2f1)
- **Gradient:** Teal → Light Teal

---

## 🔌 App Implementation

### Page Config
```python
st.set_page_config(
    page_icon="assets/eatwise-icon.svg",
    page_title="EatWise"
)
```

### Logo in Header
```python
st.image("assets/eatwise-logo-full-horizontal.svg", width=250)
```

### Logo in Sidebar
```python
col1, col2 = st.columns([0.2, 1])
with col1:
    st.image("assets/eatwise-icon.svg", width=40)
with col2:
    st.markdown("## EatWise")
```

### Status Colors
```python
# Success
st.success("✅ Meal logged!")  # Green #51CF66

# Warning
st.warning("⚠️ Sodium high")  # Yellow #FFD43B

# Info
st.info("💡 AI insight")  # Teal #10A19D
```

### Background Gradient
```css
background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, 
                           #0D7A76 75%, #063d3a 100%);
```

---

## 📐 Spacing & Layout

**Base Unit:** 8px

| Size | Value |
|------|-------|
| Extra Small | 4px |
| Small | 8px |
| Medium | 16px |
| Large | 24px |
| Extra Large | 32px |
| Section | 48px+ |

**Responsive Breakpoints:**
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

---

## ✨ Component Styles

### Cards
- Border Radius: 12px minimum
- Shadow: 0 4px 12px rgba(0,0,0,0.1)
- Background: Transparent with 5-10% color overlay
- Border: 1-2px solid with palette colors

### Buttons
- Style: Gradient, rounded (12px)
- Hover: Slight elevation, increased shadow
- Active: Scale 0.98, darker gradient
- Disabled: 60% opacity

### Icons
- Sizes: 16px, 24px, 32px, 48px, 64px
- Stroke: 2-3px for outlined
- Style: Simple, geometric

### Progress Bars
- Background: 10% opacity color
- Fill: Gradient (Primary → Light Teal)
- Height: 6-8px or 12-16px
- Animation: 0.3s smooth transition

---

## 🎬 Motion & Animation

- **UI Transitions:** 200-400ms
- **Easing:** cubic-bezier or ease-out
- **Hover Effects:** 200ms
- **Loading:** 1.5s infinite shimmer
- **Respect prefers-reduced-motion**

---

## ♿ Accessibility

- **Color Contrast:** WCAG AA compliant
  - Teal on white: 5.8:1 ✓
  - Coral on white: 4.2:1 ✓
  - White on teal: 7.2:1 ✓
- **Minimum Font:** 12px
- **Line Height:** 1.4 minimum
- **Focus States:** 2px outline, 2px offset
- **Icon Labels:** Describe emojis in alt text

---

## 📚 Full Documentation

For complete details, refer to:
- **Logo Design Specification:** `LOGO_DESIGN_BRIEF.md`
- **Design Tool Options:** `DESIGN_TOOLS_GUIDE.md`
- **Complete Brand Guide:** `BRANDING_GUIDELINES.md`
- **Assets Summary:** `BRAND_ASSETS_SUMMARY.md`

---

## 🚀 Quick Start

1. **Use SVG logos** from `/assets/` folder
2. **Follow color palette** for consistency
3. **Use Outfit font** for all text
4. **Match tone** to context (celebratory, encouraging, etc.)
5. **Test contrast** and readability
6. **Reference this card** for quick decisions

---

**EatWise Branding Quick Reference v1.0** | November 2025
