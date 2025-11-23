# EatWise - AI-Powered Nutrition Hub

A Streamlit-based personalized nutrition assistant that helps busy professionals track, understand, and optimize their daily meals using AI.

## 🌟 Features

### 1. **Smart Meal Logging**
- **Text-based logging**: Describe your meal in natural language
- **Photo-based logging**: Upload photos for automatic food recognition
- AI-powered meal analysis using OpenAI

### 2. **Nutritional Analysis**
- Instant nutritional breakdown (calories, protein, carbs, fats, sodium, sugar, fiber)
- Healthiness scoring
- Health recommendations for each meal

### 3. **Habit Tracking**
- Daily nutrition summary
- Weekly and monthly trends
- Meal type distribution analysis
- Logging streaks and statistics

### 4. **Personalized Suggestions**
- AI-powered meal recommendations based on:
  - Recent eating habits
  - Age group
  - Health conditions
  - Dietary preferences
  - Health goals
- 7-day personalized meal plans

### 5. **Health Insights**
- Pattern analysis of eating habits
- Red-flag detection for concerning patterns
- Strength and improvement area identification
- Motivational coaching

### 6. **AI Nutrition Coaching** 🎯
- **Multi-turn conversational coaching** with your AI nutrition coach
- **Real-time meal guidance** - Get feedback on meals as you log them
- **Pattern analysis** - 7-day eating pattern insights with strengths and improvement areas
- **Personalized Q&A** - Ask nutrition questions tailored to your health profile
- **Daily coaching tips** - Motivational, actionable nutrition advice
- **Meal alternatives** - Discover healthier swaps for your favorite foods
- All coaching is personalized based on your health conditions, goals, and dietary preferences

### 7. **Restaurant Menu Analyzer** 🍽️
- **Menu Text Analysis** - Paste restaurant menus for personalized recommendations
- **Photo Upload & OCR** - Upload menu photos and extract text automatically
- **Healthy Recommendations** - AI identifies best options based on your profile
- **Items to Avoid** - Flags problematic items for your health goals
- **Special Recommendations** - Highlights lowest-calorie, highest-protein, etc. options
- **Modification Suggestions** - Get tips on how to order healthier versions
- **Nutrition Cards** - Beautiful visual breakdown of each meal option

### 8. **Gamification System** 🎮
- **XP & Leveling** - Earn XP with every meal, progress through levels
- **Daily Challenges** (4 types) - Meal Logger, Calorie Control, Protein Power, Hydration Hero
- **Weekly Goals** - Complete 5 days of nutrition goals for 200 XP bonus
- **Streaks** - Track current & longest consecutive logging days
- **Achievement Badges** - Unlock badges for milestones (Early Bird, Night Owl, Streak Warrior, etc.)
- **Progress Tracking** - Real-time challenge progress bars and goal completion
- **Motivational Notifications** - Celebrate milestones and encourage continued engagement

## 📋 Project Structure

```
eatwise_ai/
├── app.py                      # Main Streamlit application
├── auth.py                     # Authentication module
├── database.py                 # Supabase database operations
├── nutrition_analyzer.py       # Food analysis & recognition
├── recommender.py              # AI recommendation engine
├── coaching_assistant.py       # AI nutrition coaching
├── restaurant_analyzer.py      # Restaurant menu analysis
├── gamification.py             # Gamification system (XP, challenges, streaks)
├── config.py                   # Configuration & nutrition targets
├── constants.py                # App constants & translations
├── utils.py                    # Utility functions
├── nutrition_components.py     # UI components for nutrition
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── DOCUMENTATION.md            # Detailed feature documentation
├── GAMIFICATION_SUMMARY.md     # Gamification implementation details
├── PRESENTATION_OUTLINE.md     # Presentation slides outline
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore file
├── assets/                     # Images and static files
├── docs/                       # Documentation and guides
│   ├── guides/                 # User guides and tutorials
│   └── setup/                  # Deployment and setup guides
└── scripts/                    # Database and setup scripts
    ├── database_setup.sql      # Supabase schema setup
    ├── gamification_migration.sql # Gamification tables migration
    └── create_missing_profiles.py # Profile creation script
```

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
