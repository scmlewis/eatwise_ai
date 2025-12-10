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

### Backend & Data
- **Supabase**: PostgreSQL database & authentication
- **PostgreSQL**: Data storage with Row Level Security

### AI & ML
- **Azure OpenAI GPT-4**: Natural language processing
- **Azure OpenAI Vision**: Food image recognition & OCR

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation

### Python Libraries
- `supabase-py`: Supabase SDK
- `python-dotenv`: Configuration management
- `pillow`: Image handling
- `requests`: HTTP requests

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (free at supabase.com)
- OpenAI API key (openai.com)

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd eatwise_ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup Supabase
# - Create project at supabase.com
# - Copy URL & key from Settings > API
# - (Optional) Run database_setup.sql in SQL Editor for custom schema

# 5. Configure environment
cp .env.example .env
# Edit .env with your credentials:
# SUPABASE_URL=your_url
# SUPABASE_KEY=your_key
# AZURE_OPENAI_API_KEY=your_key
# AZURE_OPENAI_ENDPOINT=your_endpoint
# AZURE_OPENAI_DEPLOYMENT=your_deployment

# 6. Run application
streamlit run app.py
```

Open http://localhost:8501

---

## 📱 Features Overview

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

For complete methodology, see [PORTION_ESTIMATION_GUIDE.md](PORTION_ESTIMATION_GUIDE.md)

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

See [ARCHITECTURE.md](ARCHITECTURE.md) for full schema details.

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

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & architecture
- **[CHANGELOG.md](CHANGELOG.md)** - Recent updates & improvements
- **[PORTION_ESTIMATION_GUIDE.md](PORTION_ESTIMATION_GUIDE.md)** - Methodology & examples
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Feature documentation
- **[docs/guides/](docs/guides/)** - User guides & tutorials
- **[docs/setup/](docs/setup/)** - Deployment & setup guides

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

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

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
OPENAI_API_KEY=your_openai_api_key
```

6. **Run the app**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📱 User Interface

### Pages

#### 1. **Dashboard** 📊
- Daily nutrition summary at a glance
- Progress bars for each nutrition target
- Today's logged meals
- Quick access to meal logging
- Daily nutrition insight/trivia

#### 2. **Log Meal** 📝
- **Text Input**: Describe your meal naturally
- **Photo Upload**: Upload food photos for recognition
- AI analyzes and displays:
  - Detected foods
  - Nutritional breakdown
  - Healthiness score
  - Health notes
- Quick save to database

#### 3. **Analytics** 📈
- Customizable date range (1-30 days)
- Charts:
  - Daily calorie intake trends
  - Macronutrient distribution
  - Meal type pie chart
- Statistics:
  - Average daily calories
  - Total meals logged
  - Meals per day
  - Average protein intake
- Achievements:
  - Current & longest streaks
  - Earned badges

#### 5. **Insights** 💡
- Personalized meal recommendations
- 7-day meal plan generation
- Health pattern analysis:
  - Strengths
  - Areas for improvement
  - Specific recommendations
  - Red flags & motivational messages

#### 6. **Eating Out** 🍽️
- **Menu Text Input**: Paste restaurant menus for analysis
- **Photo Upload**: Upload menu photos with automatic OCR text extraction
- **Personalized Recommendations**: AI identifies best options for you
- **Nutrition Cards**: Beautiful visual breakdown of each meal
- **Items to Avoid**: Flagged dishes that don't align with your health goals
- **Special Recommendations**: Highlights best options (lowest calorie, highest protein, etc.)
- **Modification Tips**: Suggestions on how to order healthier versions
- **Smart Filtering**: Only shows recommendations based on your dietary preferences and health conditions

#### 6. **Coaching** 🎯
- **Chat with Coach**: Multi-turn conversational interface with your AI nutrition coach
  - Ask questions about nutrition, meals, and health goals
  - Get personalized guidance based on your profile
  - Maintain conversation history during the session
- **Pattern Analysis**: Automatic 7-day eating habit analysis
  - Key eating pattern identification
  - Strengths recognition
  - Areas for improvement
  - Top recommendations
  - Motivational messages
- **Ask Questions**: Direct Q&A with daily tips
  - Get personalized nutrition answers
  - Receive daily coaching tips
  - Tips are tailored to your current nutrition status and goals

#### 7. **My Profile** 👤
- User information
- Health profile setup/update:
  - Age group
  - Health conditions
  - Dietary preferences
  - Health goals

## 🔐 Authentication & Security

- **Secure Authentication**: Supabase Auth with email/password
- **Session Management**: Secure session handling with automatic logout
- **Supabase Auth**: Secure user authentication
- **Row Level Security (RLS)**: Database-level data isolation
- Users can only access their own data
- Secure password storage with bcrypt

## 📊 Database Schema

### Core Tables
- **users** - User authentication and profile
- **health_profiles** - Age, health conditions, dietary preferences, goals, XP progress, timezone
- **meals** - Meal entries with nutrition data
- **food_history** - Cached food items with nutrition

### Gamification Tables
- **daily_challenges** - Daily challenges (4 types: Meal Logger, Calorie Control, Protein Power, Hydration Hero)
  - Columns: id, user_id, challenge_date, challenge_type, challenge_name, description, target, current_progress, xp_reward, completed
- **weekly_goals** - Weekly nutrition goal tracking
  - Columns: id, user_id, week_start_date, target_days_with_nutrition_goals, days_completed, completed, xp_reward
- **water_intake** - Daily water tracking (linked to Hydration Hero challenge)
  - Columns: id, user_id, logged_date, glasses, created_at

## 🤖 AI Capabilities

### Text Analysis
```python
analyzer = NutritionAnalyzer()
analysis = analyzer.analyze_text_meal("Grilled chicken with rice and broccoli")
```

Returns:
- Meal name and description
- Nutrition facts (calories, macros, micros)
- Healthiness score
- Health notes

### Image Recognition
```python
analysis = analyzer.analyze_food_image(image_bytes)
```

Detects:
- Food items and quantities
- Total nutrition
- Confidence score
- Relevant notes

### Recommendations
```python
recommender = RecommendationEngine()
recommendations = recommender.get_personalized_recommendations(
    user_profile, recent_meals, daily_nutrition, targets
)
```

Provides:
- 5 meal suggestions for next meal
- Why each meal is recommended
- Health benefits
- Preparation time

## 🎮 Gamification System

### XP & Leveling
- **Earn XP** for various actions:
  - Logging a meal: +25 XP
  - Meeting nutrition targets: +50 XP
  - Completing daily challenges: +50 XP
  - Completing weekly goals: +200 XP
  - Streak milestones (3-day, 7-day, 30-day): +100/200/500 XP
- **Leveling System**: Progress through levels (Level = Total XP ÷ 100)
- **Real-time Tracking**: Dashboard displays current level and XP progress

### Daily Challenges (4 Types)
- **Meal Logger** 📝 - Log 3 meals today (+50 XP)
- **Calorie Control** 🎯 - Stay under calorie target (+50 XP)
- **Protein Power** 💪 - Hit daily protein goal (+40 XP)
- **Hydration Hero** 💧 - Drink 8 glasses of water (+30 XP)

**Features:**
- Progress bars showing completion percentage
- Real-time progress updates as you log meals
- Color-coded indicators (blue=in progress, yellow=75%+ complete, green=completed)
- Refresh daily with new challenges

### Weekly Goals
- **Objective**: Complete nutrition logging goals for 5 days
- **Reward**: 200 XP upon completion
- **Tracking**: Visual progress bar and day counter
- **Reset**: New goal starts each week (Sunday-Saturday)

### Streaks
- **Current Streak** 🔥 - Consecutive days of meal logging
- **Longest Streak** 🏅 - Personal record for streak length
- **Milestone Bonuses**: Special notifications at 3-day, 7-day, 14-day, 30-day marks
- **Motivation**: Streaks drive habit formation through psychological commitment

### Achievement Badges
- **Early Bird**: Logged 5 breakfasts
- **Night Owl**: Logged 5 dinners
- **Streak Warrior**: Achieved 7-day logging streak
- **Health Champion**: Met nutrition targets for 7 consecutive days
- **Foodie**: Logged 50+ meals total
- **Sodium Watchdog**: Stayed under sodium target for 5 days

### Dashboard Integration
- **XP & Level Display**: Shows current level and progress to next level
- **Daily Challenges Section**: All 4 challenges with progress tracking
- **Weekly Goal Card**: Visual progress and days completed
- **Streak Counter**: Current streak with motivational messages
- **Hydration Tracker**: Integrated water intake logging with quick buttons

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

## 🔌 API Integration

### OpenAI
- **Model**: GPT-3.5-turbo
- **Capabilities**: Text analysis, meal recommendations, insights
- **Vision (Optional)**: GPT-4V for image analysis (requires upgrade)

### Supabase
- Authentication via email/password
- PostgreSQL database with real-time updates
- File storage (optional for meal photos)

## 📈 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] Voice input for meal logging
- [ ] Social features (sharing meals, competing streaks)
- [ ] Integration with fitness trackers (Apple Health, Google Fit)
- [ ] Advanced meal planning with restaurant menus
- [ ] Barcode scanning for packaged foods
- [ ] Recipe suggestions based on available ingredients
- [ ] Family/group nutrition tracking
- [ ] Nutritionist consultation booking
- [ ] Real-time nutrition API (USDA FoodData Central)

## 📝 Changelog

### v1.0.0 (Initial Release)
- 🌟 Core meal logging features (text and photo)
- 📊 Nutrition tracking and analytics
- 💡 AI-powered insights and recommendations
- 🎮 Gamification system with badges and streaks
- 🔐 Secure authentication with Supabase

## 🐛 Troubleshooting

### "Invalid Credentials" Error
- Check your Supabase URL and key are correct
- Ensure .env file is in project root
- Restart the Streamlit app

### "OpenAI API Error"
- Verify your API key is active
- Check your OpenAI account has credits
- Ensure OPENAI_API_KEY is set correctly

### "No module named 'supabase'"
- Run `pip install -r requirements.txt` again
- Activate your virtual environment

### Database Connection Issues
- Verify Supabase project is active
- Check internet connection
- Ensure RLS policies are correctly set up

## 📝 Usage Tips

### For Best Results
1. Be detailed when describing meals
2. Take clear, well-lit food photos
3. Complete your health profile for personalized recommendations
4. Log meals consistently for accurate trends
5. Review insights regularly for pattern identification

### Meal Logging Best Practices
- Log meals shortly after eating (recall accuracy)
- Be specific about portions
- Include cooking methods (fried vs. baked)
- Log beverages as separate entries
- Update meal description if more details remembered

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Support

For issues, questions, or suggestions:
1. Check existing issues in repository
2. Create a new issue with detailed description
3. Contact development team

## 🙏 Acknowledgments

- OpenAI for GPT and Vision APIs
- Supabase for backend infrastructure
- Streamlit for web framework
- Python community for amazing libraries

---

**Made with ❤️ for health-conscious professionals**

Start your journey to better nutrition today with EatWise! 🥗
