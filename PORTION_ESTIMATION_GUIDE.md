# Portion Estimation Guide for EatWise AI

## Overview

EatWise uses AI to analyze your meals and estimate their nutritional content. However, **the accuracy of our estimates depends on how clearly you describe or photograph your food**. This guide explains our estimation methodology and how to get the most accurate results.

---

## Confidence Levels

### Level 1: HIGH CONFIDENCE (85% accuracy) ✓
**When:** You provide specific portion sizes with exact measurements

**Examples:**
- "150g grilled chicken breast, 200g brown rice, 100g steamed broccoli"
- "2 eggs scrambled, 2 slices whole wheat bread, 15ml olive oil"
- "500ml orange juice, 1 medium apple, 200g yogurt"
- "1 cup pasta, 100g ground beef, 200ml marinara sauce"

**Variation Range:** ±15%

**Why this is most accurate:**
- Specific grams/ml/cups eliminate guessing
- Cooking method is specified
- All ingredients and condiments are listed
- No assumptions needed

**Tips for HIGH CONFIDENCE:**
- Use kitchen scales if possible (most affordable scales cost $10-30)
- Use measuring cups or spoons for liquids and grains
- Be explicit about cooking method (grilled, fried, baked, boiled)
- Include ALL ingredients: protein, carbs, fats, condiments, sauces

---

### Level 2: MEDIUM CONFIDENCE (60% accuracy)
**When:** You provide general portion descriptions with context

**Examples:**
- "A bowl of rice with grilled chicken"
- "A plate of pasta with tomato sauce"
- "A medium apple with a handful of almonds"
- "A glass of milk with cereal"

**Variation Range:** ±20-25%

**Why this has moderate accuracy:**
- We know the food types but not exact portions
- We estimate portions based on "typical" serving sizes
- Actual portions vary significantly by person and region

**Tips for MEDIUM CONFIDENCE:**
- Say "a bowl" instead of just "rice" (tells us approximate amount)
- Use familiar reference objects: "small apple", "large banana", "regular glass"
- Mention if portions are smaller or larger than usual
- Group ingredients clearly: "chicken and broccoli" vs "broccoli"

---

### Level 3: MEDIUM-LOW CONFIDENCE (40% accuracy)
**When:** Vague descriptions without clear portion indicators

**Examples:**
- "Some rice and chicken"
- "Salad with dressing"
- "A meal with vegetables"
- "Fried rice"

**Variation Range:** ±30-35%

**Why accuracy decreases:**
- We make assumptions about portion sizes
- Unknown how much oil/sauce was used
- Cooking method unclear (affects calories significantly)
- Can't distinguish ingredients from description

**Tips for MEDIUM-LOW CONFIDENCE:**
- Add ANY size reference: "small portion", "large helping", "a plate full"
- Specify if something is fried, grilled, or steamed
- List each ingredient separately
- Estimate total: "about 400g total" helps even if individual amounts unknown

---

### Level 4: LOW CONFIDENCE (30% accuracy) ⚠️
**When:** Photo only, without text description of portions

**Examples:**
- Photos of mixed dishes without portion context
- Blurry or distant photos
- Photos taken after eating (can't see total amount)
- Unidentifiable food items

**Variation Range:** ±40-50%

**Why this is least accurate:**
- We estimate size from plate/utensil comparisons
- Cannot see all ingredients clearly
- Hard to judge depth and actual quantity
- Mixed dishes hard to separate

**Tips to improve photo accuracy:**
- Add a size reference: coin, credit card, or hand in photo
- Take photo from 45° angle to see depth
- Use good lighting (natural light best)
- Photograph before eating, when all food is visible
- Add text description: "150g chicken, 1 cup rice" helps enormously

**IMPORTANT:** If you're uploading a photo, please consider adding a text description of approximate portion sizes. This dramatically improves accuracy!

---

## Estimation Criteria & Rules

### Text Input Estimation

We estimate portions based on these rules:

#### 1. **Measurement Keywords** (HIGH confidence if present)
- **Weight:** "150g", "400g", "2 oz", "1 lb"
- **Volume:** "1 cup", "200ml", "2 tbsp", "1 L"
- **Count:** "2 eggs", "3 slices", "1 piece"
- **Size descriptor + food:** "medium apple", "large banana"

#### 2. **Portion Descriptors** (MEDIUM confidence)
- "a bowl of" → estimate ~250-350g cooked food
- "a plate of" → estimate ~300-400g
- "a serving of" → standard USDA serving
- "a handful of" → estimate ~50-100g
- "a slice of" → food-dependent (bread = 30g, pizza = 100g)

#### 3. **Cooking Methods** (CRITICAL for accuracy)
| Method | Calorie Impact | How to mention |
|--------|-----------------|----------------|
| Grilled/Baked | Baseline | "grilled chicken" |
| Boiled/Steamed | -10% | "steamed vegetables" |
| Pan-fried | +20% | "pan-fried in 1 tbsp oil" |
| Deep-fried | +50-100% | "fried chicken" |
| With oil/butter | +100+ cal | "sautéed in 2 tbsp olive oil" |

#### 4. **Sauce & Condiments** (Often forgotten, big impact)
- "with dressing" - ambiguous (could be 1 tbsp or ¼ cup!)
- **BETTER:** "2 tbsp olive oil dressing", "1 tbsp mayo"
- Sauces add 50-200 calories - mention them!

#### 5. **Component Listing** (How we parse)
- ✓ **Good:** "Grilled 150g chicken, 200g brown rice, 100g broccoli, 1 tbsp olive oil"
- ✗ **Bad:** "Chicken and rice stir fry"

We process each component separately for accuracy.

---

### Photo Estimation Methodology

For photos, we use visual clues:

1. **Size References**
   - Plate diameter: ~25cm (standard plate), ~20cm (smaller), ~30cm (larger)
   - Utensils: fork/spoon typical size ~17cm
   - Coin: quarters/10 cent pieces ~17-20mm
   - Hand: adult hand ~8-10cm wide

2. **Food Density Estimation**
   - Rice/grains: ~150g per cup
   - Vegetables: ~100-150g per cup (depends on type)
   - Meat: ~150-200g per standard serving
   - Pasta: ~200g cooked per cup

3. **Camera Angles & Accuracy**
   - Top-down (90°): Can see area, harder to judge depth → under-estimate
   - 45° angle: Best angle for accurate estimation
   - Side view: Can judge depth but not area → over-estimate
   - Distance photos: Harder to judge absolute size

4. **Lighting Effects**
   - Bright lighting: Clearer visibility of ingredients
   - Shadows: Makes portion estimation harder
   - Backlighting: Can obscure ingredient amounts

5. **Mixed Dish Challenges**
   - Identifying all ingredients difficult
   - Portion of each ingredient unclear
   - Order of ingredients affects visibility
   - Usually results in wider variation range

---

## Tips to Improve Accuracy

### Text Input Best Practices

**DO:**
✓ Use specific measurements (grams, milliliters, cups, tablespoons)
✓ List each ingredient separately
✓ Specify cooking method
✓ Include sauces, oils, condiments
✓ Mention if portions are unusually small or large
✓ Use standard food sizes: "1 medium apple", "2 large eggs"

**DON'T:**
✗ Use vague terms like "some" or "a bit of"
✗ Describe mixed dishes without listing components
✗ Forget about cooking fats and oils
✗ Assume we know portion size from food name alone
✗ Use regional/personal portion descriptions

**Example of BAD input:**
"I had a healthy salad and chicken for lunch"

**Same meal, GOOD input:**
"Spinach salad (200g) with 2 tbsp olive oil vinaigrette, 150g grilled chicken breast, 50g grated cheese"

---

### Photo Best Practices

**DO:**
✓ Include reference object for scale (coin, utensil, hand)
✓ Photograph from 45° angle
✓ Use good lighting (natural light preferred)
✓ Photograph all food before eating
✓ Take sharp, in-focus photo
✓ Add text description of portions if possible

**DON'T:**
✗ Photograph from directly above (hard to judge volume)
✗ Use poor lighting or high contrast shadows
✗ Include only part of the meal
✗ Photograph after partially eating
✗ Use blurry or low-resolution photos
✗ Skip text description entirely

**Photo Quality Checklist:**
- [ ] All food items visible in frame
- [ ] Reference object included (coin/utensil/hand)
- [ ] Natural or even lighting
- [ ] Sharp focus on food
- [ ] 45° angle (or moderate side angle)
- [ ] High resolution/quality

---

## Expected Variation Ranges

These variation ranges reflect typical differences between estimated and actual nutrition:

| Confidence Level | Variation | Reliability |
|------------------|-----------|-------------|
| HIGH | ±15% | Very Good |
| MEDIUM | ±20-25% | Good |
| MEDIUM-LOW | ±30-35% | Fair |
| LOW | ±40-50% | Poor |

**Example:** If HIGH confidence estimate shows 500 calories, actual range could be 425-575 calories.

---

## When Estimation is Least Reliable

⚠️ **Be cautious with:**
- Homemade foods (recipes vary greatly)
- Restaurant meals (portions/ingredients unclear)
- Mixed/blended dishes (hard to identify components)
- Foods without reference objects in photos
- Descriptions without portion information

💡 **Workaround:** When in doubt, estimate LARGER portions rather than smaller - it's better to over-track than under-track when forming habits.

---

## Tracking Patterns Over Time

Even with ±30-40% variation per meal, **patterns become reliable over weeks:**

- Single meal estimates: ±30-40% error possible
- Week average: ±15% error likely
- Monthly patterns: ±5-10% accuracy
- Trend analysis: Very reliable despite individual variation

**Why?** Random overestimates and underestimates cancel out over time.

---

## Questions & Support

**Still unsure about portions?**
- Use our examples as templates
- When in doubt, describe in more detail
- Include reference measurements even if approximate
- Photos + text = most accurate combination

**Is my estimate reasonable?**
- Compare to your hunger/fullness level
- Common meals shouldn't vary drastically day-to-day
- Watch trends: sustained increase in calories should show weight changes

---

## Summary Checklist

For **TEXT DESCRIPTIONS:**
- [ ] Include specific measurements (grams, cups, tbsp)
- [ ] List each ingredient separately  
- [ ] Specify cooking method (grilled vs fried)
- [ ] Include sauces, oils, condiments
- [ ] Be as detailed as possible

For **PHOTOS:**
- [ ] Include size reference object
- [ ] Take from 45° angle
- [ ] Use good lighting
- [ ] Photograph before eating
- [ ] Add text description if possible

**Result:** Maximum accuracy for your nutrition tracking!
