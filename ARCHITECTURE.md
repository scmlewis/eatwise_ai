# EatWise Architecture & Design

## System Overview

EatWise is a Streamlit-based nutrition tracking application with a modular architecture separating concerns across authentication, data management, AI analysis, and gamification.

```
┌─────────────────────────────────────────────────────────┐
│         Streamlit Frontend (app.py)                     │
│    Dashboard | Log Meal | Analytics | Insights         │
│    Coaching | Eating Out | My Profile | Help            │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┴──────────────┬──────────────────────┐
    │                            │                      │
┌───▼─────────────────┐  ┌──────▼──────────┐  ┌────────▼───────┐
│ Nutrition Analysis  │  │ User Management │  │  Gamification  │
│ ├─ Analyzer         │  │ ├─ Auth         │  │ ├─ XP System   │
│ ├─ Hybrid Analyzer  │  │ ├─ Database     │  │ ├─ Challenges  │
│ ├─ Recommender      │  │ └─ Profiles     │  │ ├─ Streaks     │
│ └─ Restaurant Menu  │  │                │  │ └─ Badges      │
└──────┬──────────────┘  └──────┬─────────┘  └────────┬───────┘
       │                        │                     │
       └────────────┬───────────┴─────────────────────┘
                    │
          ┌─────────▼──────────┐
          │ Supabase Backend   │
          │ ├─ PostgreSQL      │
          │ ├─ Auth            │
          │ ├─ RLS Policies    │
          │ └─ Real-time Sync  │
          └────────────────────┘
```

---

## Core Modules

### 1. **Authentication (`auth.py`)**
Handles user authentication and session management.

**Key Functions:**
- `authenticate_user()` - Email/password login via Supabase
- `create_user()` - New user registration
- `get_current_user()` - Retrieve authenticated user
- `logout()` - Clear session state

**Security:**
- Supabase Auth manages password hashing (bcrypt)
- Session tokens stored securely
- Automatic logout on token expiry

---

### 2. **Database Layer (`database.py`)**
Supabase PostgreSQL operations with Row Level Security.

**Key Tables:**
```sql
users (id, email, created_at)
health_profiles (user_id, age_group, health_conditions, dietary_preferences, xp, level)
meals (user_id, meal_name, nutrition_data, healthiness_score, logged_at)
daily_challenges (user_id, challenge_type, progress, completed, xp_reward)
weekly_goals (user_id, days_completed, week_start, completed, xp_reward)
water_intake (user_id, glasses, logged_date)
```

**Key Operations:**
- `insert_meal()` - Log new meal with nutrition data
- `get_meals()` - Retrieve meals for date range
- `update_health_profile()` - Update user health data
- `add_xp()` - Award XP for actions
- Row Level Security ensures users see only their own data

---

### 3. **Nutrition Analysis** 

#### **A. Core Analyzer (`nutrition_analyzer.py`)**
Pure LLM-based meal analysis using Azure OpenAI.

**Functions:**
```python
analyze_text_meal(description: str, meal_type: str) → dict
# Returns: meal_name, nutrition, healthiness_score, health_notes

analyze_food_image(image_bytes: bytes) → dict
# Returns: detected_foods, nutrition, confidence
```

**Approach:**
- Sends meal description/image to GPT-4
- Requests structured JSON response
- Returns estimated nutrition values

---

#### **B. Hybrid Analyzer (`hybrid_nutrition_analyzer.py`)**
Combines LLM detection with USDA database accuracy.

**Architecture:**
```
Input (meal description)
    ↓
1. Extract Ingredients (LLM parsing)
2. Check Database (100+ common foods)
3. Calculate Coverage (% from DB vs estimated)
4. Return Results with Confidence Metadata
```

**Example Output:**
```python
{
    "meal_name": "Grilled Chicken with Rice",
    "nutrition": {calories: 450, protein: 40, ...},
    "coverage": {
        "coverage_percentage": 85.5,
        "in_database": 3,
        "estimated": 0,
        "sources": ["chicken_breast", "brown_rice", "broccoli"]
    },
    "confidence_level": "HIGH"
}
```

**Key Advantages:**
- Database values are USDA-validated (accurate)
- Only LLM estimates when necessary
- Transparent coverage reporting
- Confidence levels guide user trust

**Test Coverage:**
- 9 comprehensive unit tests covering:
  - Coverage calculation accuracy
  - Ingredient order independence
  - Consistency across runs
  - Realistic value ranges
  - Hallucination detection

---

#### **C. Nutrition Database (`nutrition_database.py`)**
USDA-based food nutrition database (~100 common foods).

**Structure:**
```python
{
    "chicken_breast": {
        "calories_per_100g": 165,
        "protein": 31.0,
        "carbs": 0,
        "fat": 3.6,
        "source": "USDA"
    },
    ...
}
```

**Coverage:** Proteins, grains, vegetables, fruits, oils, common prepared foods.

---

#### **D. Portion Estimation System (`portion_estimation_disclaimer.py`)**
Provides users with accuracy expectations based on meal description detail.

**Confidence Levels:**
| Level | Range | Criteria | Example |
|-------|-------|----------|---------|
| HIGH (85%) | ±15% | Exact measurements | "150g chicken, 200g rice" |
| MEDIUM (60%) | ±25% | Portion descriptors | "large chicken breast, cup of rice" |
| MEDIUM-LOW (40%) | ±30-35% | Vague with some detail | "some chicken and rice" |
| LOW (30%) | ±40-50% | Minimal detail or photo only | "chicken and rice" |

**Functions:**
```python
assess_input_confidence(text: str, has_photo: bool) → str
# Analyzes text patterns to determine confidence level

get_confidence_disclaimer(level: str, input_type: str) → str
# Returns formatted disclaimer with accuracy range

show_estimation_disclaimer(st, level: str, input_type: str)
# Displays colored box with disclaimer to user
```

**Algorithm:**
- Searches for measurement keywords (grams, cups, tablespoons)
- Detects portion descriptors (medium, large, small)
- Identifies vague language (some, a bit, few)
- Weights by specificity to assign confidence level

---

### 4. **Recommendation Engine (`recommender.py`)**
Provides personalized meal suggestions based on user profile and history.

**Inputs:**
- Recent meal history (7 days)
- Health profile (age, conditions, goals)
- Current nutrition status vs. targets
- Dietary preferences

**Algorithm:**
1. Analyze recent meals (identify patterns, gaps)
2. Generate recommendations matching health profile
3. Rank by nutritional value & alignment with targets
4. Filter by dietary preferences
5. Return 5 suggestions with explanations

---

### 5. **AI Coaching (`coaching_assistant.py`)**
Multi-turn conversational AI coach providing personalized nutrition guidance.

**Features:**
- Chat interface maintaining conversation history
- 7-day eating pattern analysis with insights
- Daily tips tailored to user profile
- Personalized Q&A on nutrition topics

**Pattern Analysis:**
- Identifies eating habits & patterns
- Highlights strengths (e.g., "High fiber intake!")
- Identifies improvement areas
- Suggests actionable changes
- Provides motivational messages

---

### 6. **Restaurant Menu Analyzer (`restaurant_analyzer.py`)**
Analyzes restaurant menus (text or photo) for personalized recommendations.

**Features:**
- Menu text parsing
- OCR for menu photos
- AI-powered menu item analysis
- Personalized recommendation scoring
- Items to avoid based on health profile
- Healthy modification suggestions

**Workflow:**
1. User provides menu (text or photo)
2. Extract menu items & descriptions
3. Analyze each item's nutrition & fit
4. Score based on user health profile
5. Display recommendations with reasoning

---

### 7. **Gamification (`gamification.py`)**
XP system, daily challenges, streaks, and achievement badges.

**Components:**

#### **XP & Leveling**
- Award XP for actions (meal logging, target achievement, challenges)
- Level = Total XP ÷ 100
- Display current level & progress

#### **Daily Challenges (4 Types)**
1. **Meal Logger** - Log 3 meals (+50 XP)
2. **Calorie Control** - Stay under calorie target (+50 XP)
3. **Protein Power** - Hit daily protein goal (+40 XP)
4. **Hydration Hero** - Drink 8 glasses water (+30 XP)

**Implementation:**
- Generate daily at midnight (user timezone)
- Track progress real-time as user logs meals
- Update color indicators (blue→yellow→green)
- Refresh with new challenges each day

#### **Streaks**
- Current streak: Consecutive days of meal logging
- Longest streak: Personal record
- Milestone bonuses: 3/7/14/30-day marks
- Motivational notifications

#### **Achievement Badges**
- Early Bird: 5 logged breakfasts
- Night Owl: 5 logged dinners
- Streak Warrior: 7-day streak
- Health Champion: 7-day goal achievement
- Foodie: 50+ meals logged
- Sodium Watchdog: 5 days under sodium target

---

### 8. **UI Components (`nutrition_components.py`)**
Reusable Streamlit components for consistent UI.

**Components:**
- `show_nutrition_facts()` - Nutrition card display
- `show_meal_history()` - Meal list with filters
- `show_health_insight()` - Insight cards
- `show_challenge_progress()` - Challenge visualizations

---

## Data Flow

### Meal Logging Flow
```
User Input (Text or Photo)
    ↓
Portion Assessment (confidence level)
    ↓
Hybrid Analysis
├─ AI ingredient detection
├─ Database lookup
└─ Coverage calculation
    ↓
Display Results
├─ Nutrition facts
├─ Confidence level & accuracy range
└─ Health notes
    ↓
User saves meal
    ↓
Database insertion + RLS check
    ↓
XP award (+25) + challenge update
```

### Recommendation Flow
```
User clicks "Insights"
    ↓
Fetch 7-day meal history
    ↓
Analyze patterns
├─ Macro/micro trends
├─ Gap identification
└─ Goal alignment
    ↓
Generate recommendations
├─ Score based on health profile
├─ Filter by preferences
└─ Rank by value
    ↓
Display with explanations
```

### Gamification Flow
```
Daily reset (midnight user timezone)
    ↓
Generate 4 new challenges
    ↓
Display on dashboard
    ↓
User logs meal/completes action
    ↓
Real-time progress update
    ↓
Challenge completion detection
    ↓
Award XP + update level
    ↓
Check milestone/achievement
    ↓
Display notifications
```

---

## Security Architecture

### Authentication
- **Supabase Auth**: Email/password with bcrypt hashing
- **Session Management**: Token-based with expiry
- **Secure Logout**: Clear session state & tokens

### Database Security
- **Row Level Security (RLS)**: Users access only their data
- **Authenticated Role**: Operations require valid JWT
- **Policy Rules**: `auth.uid() = user_id` on all tables

Example RLS Policy:
```sql
CREATE POLICY "Users access own data" ON meals
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

### API Keys
- Stored in `.env` (not committed)
- Environment variables at runtime
- OpenAI & Supabase keys protected

---

## Error Handling

### Graceful Degradation
```python
try:
    result = analyzer.analyze_text_meal(description)
except OpenAIError:
    st.error("Analysis unavailable, please try again")
except DatabaseError:
    st.error("Database connection issue")
```

### User Feedback
- Toast notifications for quick actions
- Error messages with suggestions
- Validation errors with guidance

---

## Performance Optimization

### Caching
- Streamlit `@st.cache_data` for static data
- Session state for user preferences
- Database query caching where applicable

### API Calls
- Batch requests when possible
- Rate limiting awareness
- Error retry logic

### UI Responsiveness
- Spinner messages during long operations
- Progressive content loading
- Lazy loading for analytics/charts

---

## Testing Strategy

### Unit Tests (`test_hybrid_analyzer.py`)
9 comprehensive tests covering:
- Database coverage calculations
- Consistency & determinism
- Nutrition value validation
- Hallucination detection
- Confidence level assignment

**Run Tests:**
```bash
python test_hybrid_analyzer.py
```

### Integration Testing
- End-to-end meal logging flow
- Database transaction validation
- Authentication flow
- Gamification logic

---

## Development Guidelines

### Code Organization
- **One responsibility per module**
- **Pure functions where possible**
- **Clear function signatures**
- **Comprehensive docstrings**

### Naming Conventions
- `snake_case` for functions/variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive, self-documenting names

### Documentation
- Module docstring at top
- Function docstrings with parameters/returns
- Inline comments for complex logic
- Architecture decisions in ARCHITECTURE.md

### Version Control
- Descriptive commit messages
- Logical commits (one feature per commit)
- Reference issues/features in commits
- Keep CHANGELOG.md updated

---

## Future Architecture Improvements

### Planned Enhancements
- [ ] Caching layer (Redis) for frequent queries
- [ ] Background job queue (Celery) for async tasks
- [ ] GraphQL API for mobile apps
- [ ] Real-time notifications (WebSockets)
- [ ] Machine learning models for better predictions
- [ ] Advanced analytics with BigQuery

### Scalability Considerations
- Supabase handles horizontal scaling
- Streamlit Cloud auto-scaling
- CDN for static assets
- Database indexes for frequent queries

---

## Debugging & Troubleshooting

### Common Issues

**Issue: "Invalid Credentials"**
- Check `.env` has correct Supabase URL & key
- Verify project is active on Supabase
- Test connection manually

**Issue: "OpenAI API Error"**
- Verify API key is active
- Check account has credits
- Review API usage limits

**Issue: "RLS policy violations"**
- Ensure `auth.uid()` is correctly set
- Check RLS policy syntax
- Verify user is authenticated

### Debugging Tools
- Streamlit's `st.write()` for inspection
- Browser DevTools for frontend
- Supabase dashboard for database
- OpenAI API logs for AI issues

---

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Supabase PostgreSQL Guide](https://supabase.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Python Best Practices](https://pep8.org/)

---

**Last Updated:** December 2025
**Version:** 2.3.0
