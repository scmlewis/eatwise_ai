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

### 7. **Gamification**
- Logging streaks (🔥 Current & Longest)
- Achievement badges
- Progress tracking
- Fun nutrition trivia

## 📋 Project Structure

```
eatwise_ai/
├── app.py                      # Main Streamlit application
├── auth.py                     # Authentication module
├── database.py                 # Supabase database operations
├── nutrition_analyzer.py       # Food analysis & recognition
├── recommender.py              # AI recommendation engine
├── config.py                   # Configuration & targets
├── constants.py                # App constants & translations
├── utils.py                    # Utility functions
├── database_setup.sql          # Supabase schema setup
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # This file
└── .gitignore                  # Git ignore file
```

## 🛠️ Tech Stack

### Backend & Data
- **Supabase**: Authentication and database
- **PostgreSQL**: Data storage (via Supabase)

### AI & ML
- **OpenAI GPT-3.5**: Natural language meal analysis
- **OpenAI Vision**: Food image recognition

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

### Users Table
- user_id, email, full_name, created_at

### Health Profiles Table
- user_id, age_group, health_conditions, dietary_preferences, health_goal, badges_earned

### Meals Table
- user_id, meal_name, description, meal_type, nutrition (JSONB), healthiness_score, logged_at

### Food History Table
- user_id, food_name, nutrition (JSONB), last_used, usage_count

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

### Streaks
- 🔥 Tracks consecutive days of meal logging
- Displayed on dashboard and analytics

### Badges
- **Early Bird**: 5 breakfasts logged
- **Night Owl**: 5 dinners logged
- **Streak Warrior**: 7-day streak
- **Health Champion**: 7 days meeting targets
- **Foodie**: 50 meals logged
- **Sodium Watchdog**: 5 days under sodium target

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
