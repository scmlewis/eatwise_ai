# EatWise - AI-Powered Nutrition Hub

A Streamlit-based personalized nutrition assistant that helps busy professionals track, understand, and optimize their daily meals using AI.

**Status**: ✅ **Active Development** | Latest: Portion Estimation System & UX Improvements

---

## 🌟 Key Features

### 1. **Smart Meal Logging** 📝
- **Text-based logging**: Describe your meal in natural language with accuracy guidance
- **Photo-based logging**: Upload food photos for automatic recognition
- **Portion estimation system**: Clear accuracy ranges (±15% to ±50%) based on description detail
- **Hybrid Nutrition System**: AI detection + USDA database for maximum accuracy

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

## 📋 Project Structure

```
eatwise_ai/
├── Core Application
│   ├── app.py                           # Main Streamlit app
│   ├── auth.py                          # Authentication
│   ├── database.py                      # Supabase operations
│   └── config.py                        # Configuration & targets
│
├── Nutrition & Analysis
│   ├── nutrition_analyzer.py            # AI-powered meal analysis
│   ├── portion_estimation_disclaimer.py # Portion confidence system
│   ├── restaurant_analyzer.py           # Restaurant menu analysis
│   ├── recommender.py                   # Meal recommendation engine
│   └── nutrition_components.py          # UI components
│
├── Features
│   ├── gamification.py                  # XP, challenges, streaks, badges
│   ├── coaching_assistant.py            # AI nutrition coach
│   └── utils.py                         # Utility functions
│
├── Configuration
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.example                     # Environment template
│   ├── constants.py                     # App constants
│   └── .gitignore
│
└── Assets
    └── assets/                          # Images & static files
```

> **Note**: This repository contains only production code. Development documentation, database scripts, and test files are maintained locally but not tracked in Git.

---

## ✨ Recent Updates

### **v2.5.1 - Clean Repository Release** (Dec 2025)
- ✅ **Production-Ready Codebase**: Removed 60+ internal documentation files
- ✅ **Clean Git History**: Streamlined repository for users
- ✅ **Maintained Locally**: Development docs, scripts, and tests available locally
- ✅ **Focus on Code**: Repository showcases core functionality

### **v2.3.0 - Portion Estimation & UX Redesign** (Dec 2025)
- ✅ **Portion Estimation System**: 4 confidence levels with accuracy ranges (±15%-50%)
- ✅ **Prominent Disclaimers**: Warning boxes show accuracy expectations
- ✅ **Streamlined Meal Input**: Reorganized layout reduces information overload
- ✅ **UX Improvements**: Better visual hierarchy, grouped related content
- ✅ **TDD Test Suite**: 9 comprehensive hybrid analyzer tests

---

## 🛠️ Tech Stack

### **Dashboard** 📊
Daily nutrition summary with progress bars, quick meal access, and today's logged meals.

### **Log Meal** 📝
- **Text**: Describe meal with accuracy guidance (SPECIFIC ±15%, GENERAL ±25%, VAGUE ±40-50%)
- **Photo**: Upload food photos for recognition
- Real-time confidence level display
- Quick save to database

### **Analytics** 📈
- Customizable date range (1-30 days)
- Calorie & macronutrient trend charts
- Meal distribution analysis
- Statistics & achievements

### **Insights** 💡
- AI-powered meal recommendations
- 7-day meal plan generation
- Health pattern analysis with recommendations

### **Coaching** 🎯
- Chat with AI nutrition coach
- Pattern analysis from meal history
- Personalized Q&A & daily tips

### **Eating Out** 🍽️
- Menu analysis (text or photo with OCR)
- Personalized recommendations
- Items to avoid based on health profile
- Healthy modification suggestions

### **My Profile** 👤
- Health profile setup
- Age, health conditions, dietary preferences
- Nutrition targets configuration

---

## 🎯 Portion Estimation System

The app now includes an intelligent portion estimation system to help users understand nutrition accuracy:

### **Accuracy Levels**
| Level | Accuracy Range | Description | Example |
|-------|---|---|---|
| **SPECIFIC** | ±15% | Exact measurements given | "150g grilled chicken, 200g brown rice" |
| **GENERAL** | ±25% | Portion descriptors used | "chicken with rice and vegetables" |
| **MEDIUM-LOW** | ±30-35% | Vague but some details | "some chicken, rice, and broccoli" |
| **VAGUE** | ±40-50% | Minimal detail | "some chicken and rice" |

### **How It Works**
1. User provides meal description
2. System assesses input detail level using pattern matching
3. Confidence level & accuracy range displayed
4. Common portion sizes available for reference
5. Users understand estimation accuracy before saving

### **Hybrid Nutrition System**
The app uses AI for ingredient detection combined with a comprehensive nutrition database for maximum accuracy. Portion estimation includes confidence levels (±15% to ±50%) based on description detail.

For more details on methodology, see the features section below.

---

## 🔐 Security & Privacy

- ✅ **Secure Authentication**: Supabase email/password auth
- ✅ **Row Level Security**: Users access only their own data
- ✅ **Secure Sessions**: Automatic logout & session management
- ✅ **Password Security**: Bcrypt hashing
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

## 🎮 Gamification

### XP System
- Log meal: +25 XP
- Meet nutrition targets: +50 XP
- Daily challenges: +50 XP
- Weekly goal: +200 XP
- Streaks (3/7/30-day): +100/200/500 XP

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

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid Credentials | Check Supabase URL/key, verify .env |
| OpenAI API Error | Verify API key active & has credits |
| Module Not Found | Run `pip install -r requirements.txt` |
| Database Connection | Check Supabase active, verify RLS policies |

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

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push and submit pull request

---

## 📄 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 & Vision APIs
- Supabase for backend infrastructure
- Streamlit for web framework
- Python community for libraries

---

**Made with ❤️ for health-conscious professionals**

Start optimizing your nutrition with EatWise today! 🥗

## 🛠️ Tech Stack

### Backend & Data
- **Supabase**: Authentication and database
- **PostgreSQL**: Data storage (via Supabase)

### AI & ML
- **Azure OpenAI GPT-4**: Natural language meal analysis and recommendations
- **Azure OpenAI Vision**: Food image recognition and menu OCR

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation

### Python Libraries
- `python-dotenv`: Environment configuration
- `pillow`: Image handling
- `requests`: API requests

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (free tier available at supabase.com)
- OpenAI API key (get from openai.com)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd eatwise_ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Supabase**
   - Create a new project at supabase.com
   - Go to SQL Editor and run all queries from `database_setup.sql`
   - Copy your Supabase URL and anon key from Settings > API
   - **Important**: Go to Authentication > URL Configuration
     - Set Site URL to your app URL (e.g., `https://eatwise-ai.streamlit.app`)
     - Add Redirect URLs for password reset functionality

5. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

6. **Run the app**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🔐 Security & Privacy

- ✅ **Secure Authentication**: Supabase email/password auth
- ✅ **Row Level Security**: Users access only their own data
- ✅ **Secure Sessions**: Automatic logout & session management
- ✅ **Password Security**: Bcrypt hashing
- ✅ **Data Isolation**: Database-level access control

---

## 🎯 Key Capabilities

### AI-Powered Analysis
- **Text Analysis**: Describe meals in natural language
- **Image Recognition**: Automatic food detection from photos
- **Nutrition Calculation**: Instant macro & micronutrient breakdown
- **Health Scoring**: 0-100 healthiness rating with recommendations

### Personalization
- **User Profiles**: Age, health conditions, dietary preferences
- **Custom Targets**: Nutrition goals adjusted by health profile
- **Smart Recommendations**: Meals tailored to your profile
- **7-Day Analysis**: Eating pattern insights with actionable advice

### Engagement Features
- **XP & Leveling**: Earn points for logging meals and hitting targets
- **Daily Challenges**: 4 rotating missions (Meal Logger, Calorie Control, Protein Power, Hydration Hero)
- **Streaks**: Track consecutive days of meal logging
- **Badges**: Unlock achievements for consistency and progress

---

## 🌍 Nutrition Targets

### Default Daily Targets
- Calories: 2000
- Protein: 50g
- Carbs: 300g
- Fat: 65g
- Sodium: 2300mg
- Sugar: 50g
- Fiber: 25g

### Age-Based Adjustments
- 20-25: Higher calorie targets (2400)
- 26-35: Standard targets (2200)
- 36-45: Reduced targets (2000)

### Health Condition Adjustments
- **Diabetes**: Lower carbs & sugar
- **Hypertension**: Lower sodium
- **Weight Loss**: Reduced calories, higher protein
- **Weight Gain**: Increased calories, higher protein

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
- Early Bird & Night Owl
- Streak Warrior
- Health Champion
- Foodie
- Sodium Watchdog

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid Credentials | Check Supabase URL/key in .env |
| Azure OpenAI Error | Verify API key active & endpoint correct |
| Module Not Found | Run `pip install -r requirements.txt` |
| Database Connection | Check Supabase project active & RLS policies |

---

## 📄 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 & Vision APIs
- Supabase for backend infrastructure
- Streamlit for web framework
- Python community for amazing libraries

---

**Made with ❤️ for health-conscious professionals**

Start optimizing your nutrition with EatWise today! 🥗
