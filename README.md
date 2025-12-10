# EatWise - AI-Powered Nutrition Hub

A Streamlit-based personalized nutrition assistant that helps busy professionals track, understand, and optimize their daily meals using AI.

**Status**: ✅ **Active Development** | Latest: Portion Estimation System & UX Improvements

---

## 🌟 Key Features

### 1. **Smart Meal Logging** 📝
- **Text-based logging**: Describe your meal in natural language with accuracy guidance
- **Photo-based logging**: Upload food photos for automatic recognition
- **Portion estimation system**: Clear accuracy ranges (±15% to ±50%) based on description detail
- **AI + Database**: AI detection combined with USDA nutrition database for maximum accuracy

### 2. **Nutritional Analysis** 📊
- Instant nutritional breakdown (calories, protein, carbs, fats, sodium, sugar, fiber)
- Healthiness scoring (0-100) with health recommendations
- Confidence levels for estimation accuracy
- USDA-validated nutrition data

### 3. **Habit Tracking** 📈
- Daily nutrition summary & progress bars
- Weekly and monthly trend analysis
- Meal type distribution insights
- Logging streaks & statistics

### 4. **AI-Powered Coaching** 🎯
- Multi-turn conversational coaching
- Real-time meal feedback & suggestions
- 7-day eating pattern analysis with insights
- Personalized nutrition Q&A

### 5. **Restaurant Menu Analyzer** 🍽️
- Paste menu text or upload menu photos (OCR)
- AI-powered personalized recommendations
- Flags items to avoid based on health profile
- Modification suggestions for healthier ordering

### 6. **Gamification System** 🎮
- XP & leveling system
- 4 daily challenges (Meal Logger, Calorie Control, Protein Power, Hydration Hero)
- Streaks & achievement badges
- Weekly nutrition goals

### 7. **Health Insights** 💡
- Personalized meal recommendations
- 7-day meal plan generation
- Pattern analysis with strengths & improvement areas
- Motivational coaching messages

---

## 🛠️ Tech Stack

### Backend & Data
- **Supabase**: Authentication and PostgreSQL database
- **PostgreSQL**: Data storage with Row Level Security

### AI & ML
- **Azure OpenAI GPT-4**: Natural language meal analysis and recommendations
- **Azure OpenAI Vision**: Food image recognition and menu OCR

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation

---

## 🔐 Security & Privacy

- ✅ **Secure Authentication**: Supabase email/password auth with bcrypt hashing
- ✅ **Row Level Security**: Users access only their own data
- ✅ **Secure Sessions**: Automatic logout & session management
- ✅ **Data Isolation**: Database-level access control

---

## 📊 Database Schema

### Core Tables
- **users** - Authentication & profiles
- **health_profiles** - Health data & preferences
- **meals** - Meal entries with nutrition

### Gamification
- **daily_challenges** - Challenge tracking
- **weekly_goals** - Weekly goal progress
- **water_intake** - Hydration tracking

---

## 🎯 Portion Estimation System

The app includes an intelligent portion estimation system to help users understand nutrition accuracy:

| Level | Accuracy Range | Description | Example |
|-------|---|---|---|
| **SPECIFIC** | ±15% | Exact measurements given | "150g grilled chicken, 200g brown rice" |
| **GENERAL** | ±25% | Portion descriptors used | "chicken with rice and vegetables" |
| **MEDIUM-LOW** | ±30-35% | Vague but some details | "some chicken, rice, and broccoli" |
| **VAGUE** | ±40-50% | Minimal detail | "some chicken and rice" |

---

## 🤖 AI Capabilities

```python
# Meal analysis from text
analyzer = NutritionAnalyzer()
result = analyzer.analyze_text_meal("Grilled chicken with rice")
# → meal name, nutrition, healthiness score, health notes

# Image recognition
result = analyzer.analyze_food_image(image_bytes)
# → detected foods, nutrition, confidence

# Personalized recommendations
recommender = RecommendationEngine()
meals = recommender.get_personalized_recommendations(user_profile, meals)
# → 5 meal suggestions with reasons
```

---

## 🎮 Gamification Features

### XP System
- Log meal: +25 XP
- Meet nutrition targets: +50 XP
- Complete daily challenges: +50 XP
- Complete weekly goal: +200 XP
- Streak milestones (3/7/30-day): +100/200/500 XP

### Daily Challenges
1. **Meal Logger** 📝 - Log 3 meals
2. **Calorie Control** 🎯 - Stay under target
3. **Protein Power** 💪 - Hit protein goal
4. **Hydration Hero** 💧 - Drink 8 glasses

### Achievements
- Early Bird, Night Owl
- Streak Warrior
- Health Champion
- Foodie
- Sodium Watchdog

---

## 🌍 Nutrition Targets

### Default Daily Targets
- Calories: 2000 | Protein: 50g | Carbs: 300g | Fat: 65g
- Sodium: 2300mg | Sugar: 50g | Fiber: 25g

### Age-Based Adjustments
- 20-25: Higher targets (2400 cal) | 26-35: Standard (2200 cal) | 36-45: Reduced (2000 cal)

### Health Condition Adjustments
- **Diabetes**: Lower carbs & sugar
- **Hypertension**: Lower sodium
- **Weight Loss**: Reduced calories, higher protein
- **Weight Gain**: Increased calories, higher protein

---

## 📈 Future Roadmap

- [ ] Mobile app (React Native)
- [ ] Voice input for logging
- [ ] Fitness tracker integration (Apple Health, Google Fit)
- [ ] Barcode scanning for packaged foods
- [ ] Recipe suggestions based on ingredients
- [ ] Family/group nutrition tracking
- [ ] Nutritionist consultation booking
- [ ] Real-time USDA FoodData API integration

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 & Vision APIs
- Supabase for backend infrastructure
- Streamlit for web framework
- Python community for libraries

---

**Made with ❤️ for health-conscious professionals**

Start optimizing your nutrition with EatWise today! 🥗
