# 🎯 Personalized Nutrition Coaching Assistant

## Overview

The **Personalized Nutrition Coaching Assistant** is an AI-powered feature that provides real-time, personalized nutrition guidance through conversational interactions. It leverages Azure OpenAI's GPT models to deliver context-aware coaching tailored to each user's health profile, goals, and eating habits.

## Features

### 1. **💬 Chat with Coach**
An interactive chat interface where users can have natural conversations with their AI nutrition coach.

**Capabilities:**
- Answer questions about nutrition, health, and fitness
- Provide real-time meal guidance and feedback
- Discuss health goals and strategies
- Offer motivational support and encouragement
- Reference user's personal health profile and nutrition targets

**Example Interactions:**
- "Is pasta good for me?" → Personalized answer based on health conditions
- "What should I eat for dinner?" → Suggestions based on daily nutrition gaps
- "How can I lose weight?" → Strategies tailored to their goals

### 2. **📊 Pattern Analysis**
Intelligent analysis of eating patterns over time with actionable insights.

**Analyzes:**
- Meal frequency and timing patterns
- Nutrient distribution trends
- Specific strengths in eating habits
- Areas needing improvement
- Red flags or concerning patterns
- Personalized recommendations

**Provides:**
- Eating pattern insights (e.g., "You tend to eat high-sodium meals on weekends")
- Celebration of strengths (e.g., "You're consistently hitting your protein targets!")
- Specific improvement areas (e.g., "Your fiber intake is 30% below target")
- One key actionable recommendation
- Motivational message based on progress

### 3. **❓ Ask Questions**
Dedicated Q&A section for nutrition knowledge and personalized advice.

**Features:**
- Answer any nutrition question with context-aware responses
- Reference user's specific health conditions and goals
- Provide practical, actionable advice
- Daily coaching tips optimized for current nutrition needs

**Example Questions:**
- "How much protein should I eat?"
- "What are good foods for my diabetes?"
- "Why is fiber important?"
- "Can I have this food with my hypertension?"

## Technical Architecture

### Core Module: `coaching_assistant.py`

```python
class CoachingAssistant:
    - get_meal_guidance()        # Real-time coaching on a specific meal
    - analyze_eating_patterns()  # 7-day pattern analysis with insights
    - answer_nutrition_question() # Answer user questions with personalization
    - get_daily_coaching_tip()   # Personalized daily tip
    - get_meal_alternative()     # Suggest healthier meal alternatives
    - get_conversation_response()# Conversational AI with history context
```

### Azure OpenAI Integration

The coach uses Azure OpenAI GPT models with:
- **Temperature**: 0.6-0.7 for conversational balance (helpful but not overly creative)
- **Max Tokens**: 300-400 for focused, concise responses
- **Context**: User profile, health conditions, current nutrition, dietary preferences
- **System Prompts**: Role-based prompts positioning the assistant as a "supportive nutrition coach"

### Data Flow

```
User Input
    ↓
CoachingAssistant Method
    ↓
Azure OpenAI API
    ↓
Response with User Context
    ↓
Display in UI
```

## Key Methods

### `get_meal_guidance(meal_name, meal_nutrition, daily_nutrition, targets, user_profile)`
Provides real-time coaching on a meal choice.

**Returns:**
1. Quick assessment (1-2 sentences)
2. Specific positives about the meal
3. Any concerns based on profile/goals
4. Suggestion for improvement
5. What to eat next to balance the day

**Example:**
```
"Great choice! This meal gives you excellent protein. However, it's a bit high in sodium 
given your hypertension. Next time, you could reduce salt and add more vegetables. For 
your next meal, focus on getting more fiber - aim for a salad or whole grain."
```

### `analyze_eating_patterns(meals, daily_nutrition, targets, user_profile, days=7)`
Analyzes 7-day eating patterns and provides structured insights.

**Returns JSON:**
```json
{
    "patterns": ["Pattern description 1", "Pattern description 2"],
    "strengths": ["You consistently log meals", "High protein at breakfast"],
    "challenges": ["Low fiber intake", "Inconsistent meal timing"],
    "red_flags": ["High sodium on certain days"],
    "key_recommendation": "Specific, actionable recommendation",
    "motivational_insight": "Encouraging observation"
}
```

### `answer_nutrition_question(question, user_profile, daily_nutrition, targets)`
Personalized answers to nutrition questions.

**Key Features:**
- References user's specific health conditions
- Considers current nutrition status
- Provides actionable, practical advice
- Keeps responses concise (<150 words)

### `get_daily_coaching_tip(user_profile, daily_nutrition, targets)`
Generates a daily coaching tip optimized for what the user needs today.

**Example Tips:**
- "You need 25g more fiber today - try adding vegetables to your next meal!"
- "Great job with protein! Focus on reducing sodium for your next meal."
- "You're doing well on calories. Don't forget your water intake!"

### `get_conversation_response(conversation_history, user_message, user_profile, daily_nutrition, targets)`
Maintains conversational context across multiple messages.

**Features:**
- Keeps last 6 messages for context
- Includes user's current nutrition status
- Personalizes based on health profile
- Natural, friendly conversation flow

## User Experience

### Chat Interface
```
┌─────────────────────────────────────┐
│  You: "Is this meal healthy?"       │
├─────────────────────────────────────┤
│  Coach: "Yes! This meal is rich in  │
│  protein and has good fiber content.│
│  One thing - it's a bit high in     │
│  sodium. Consider reducing salt..." │
└─────────────────────────────────────┘
```

### Pattern Analysis Display
- **Patterns Section**: Key eating patterns identified
- **Strengths Card**: Positive habits to celebrate
- **Areas to Improve Card**: Growth opportunities
- **Top Recommendation Card**: One key action item
- **Motivational Message**: Encouraging feedback

### Daily Tips
- One-sentence recommendations
- Context-aware based on current nutrition status
- Actionable within the day

## Configuration

### System Prompts

**Coaching Chat:**
```
"You are a friendly, supportive nutrition coach. Provide practical, 
personalized guidance without being judgmental. Always be encouraging."
```

**Pattern Analysis:**
```
"You are a data-driven nutrition analyst providing positive, 
specific feedback."
```

**Question Answering:**
```
"You are a friendly, knowledgeable nutrition expert providing 
personalized advice. Be helpful and supportive."
```

## API Configuration

- **Endpoint**: Azure OpenAI endpoint (from `config.py`)
- **Model**: GPT-3.5-turbo or GPT-4 (configurable via `AZURE_OPENAI_DEPLOYMENT`)
- **API Version**: "2023-05-15"

## Session State Management

The coaching assistant maintains conversation history in `st.session_state.coaching_conversation`:

```python
st.session_state.coaching_conversation = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
]
```

This allows the coach to maintain context across multiple turns.

## Integration Points

### 1. **Dashboard Integration**
Could display a "Quick Coaching Tip" in the sidebar or main dashboard.

### 2. **Meal Logging Integration**
Could provide instant coaching after a meal is logged.

### 3. **Analytics Integration**
Could suggest coaching topics based on identified nutrition gaps.

## Future Enhancements

### Phase 2 Possibilities:
1. **Meal Suggestion Integration**: Coach recommends meals from your history based on your current gaps
2. **Voice Coaching**: Accept voice input for hands-free interaction
3. **Predictive Coaching**: "If you continue this pattern, you'll be X by end of month"
4. **Habit Formation Coaching**: Multi-day coaching plans for specific nutrition goals
5. **Recipe Coaching**: Analyze recipes before cooking and suggest modifications
6. **Batch Meal Analysis**: Coach reviews a week of meals with one comprehensive report
7. **Accountability Buddy**: Daily check-ins with motivational messages
8. **Nutrition Education**: Mini-lessons on topics the coach detects are gaps

## Testing

### Manual Test Scenarios

1. **Chat Test**
   - Start a conversation with "What should I eat?"
   - Ask a health-specific question
   - Clear conversation and start fresh

2. **Pattern Analysis Test**
   - Log 5+ meals over several days
   - Open Pattern Analysis tab
   - Verify insights are specific to logged meals

3. **Question Test**
   - Ask a general nutrition question
   - Ask a health-condition-specific question
   - Verify responses are personalized

4. **Daily Tip Test**
   - Click "Get Today's Tip"
   - Verify tip references current nutrition status

### Example Test Data

```python
# Minimal test: Health profile with meals
user_profile = {
    "age_group": "26-35",
    "health_goal": "weight_loss",
    "health_conditions": ["diabetes"],
    "dietary_preferences": ["vegetarian"]
}

meals = [
    {"meal_name": "Oatmeal with berries", "nutrition": {"calories": 350, "protein": 12, "carbs": 52}},
    {"meal_name": "Greek salad", "nutrition": {"calories": 280, "protein": 15, "carbs": 18}},
]
```

## Performance Considerations

- **API Calls**: Each coaching interaction calls Azure OpenAI once
- **Cost**: Monitor Azure OpenAI usage; consider implementing caching for common questions
- **Latency**: Most responses return in 2-5 seconds
- **Error Handling**: Gracefully handles API failures with fallback messages

## Error Handling

```python
try:
    response = coaching.get_meal_guidance(...)
except Exception as e:
    return f"Coaching unavailable: {str(e)}"
```

All methods include try/except blocks and return user-friendly error messages.

## User Guide

### How to Use the Coaching Assistant

**1. Chat with Coach**
   - Click the Chat tab
   - Type your question or comment
   - Read the coach's personalized response
   - Continue the conversation naturally
   - Click "Start New Conversation" to begin fresh

**2. View Pattern Analysis**
   - Log meals for at least 3-5 days
   - Go to the Coaching page
   - Click Pattern Analysis tab
   - Review insights about your eating habits

**3. Ask Questions**
   - Go to Ask Questions tab
   - Type your nutrition question
   - Click "Get Answer"
   - Optionally, get a daily coaching tip

## FAQ

**Q: How personalized are the responses?**
A: Very! The coach considers your age group, health conditions, dietary preferences, health goal, and current daily nutrition when responding.

**Q: Can the coach analyze my meals?**
A: Yes! Use the "Chat with Coach" tab to ask about meals you've logged. The coach can see your daily nutrition totals and targets.

**Q: Is this a replacement for a nutritionist?**
A: No. The coaching assistant is a helpful guide, but for medical advice or serious nutritional needs, consult a professional nutritionist or doctor.

**Q: How long does the coach remember my conversation?**
A: The coach keeps the last 6 messages for context. This helps maintain natural conversation flow.

**Q: Can I export conversation history?**
A: Currently, conversations are stored in your session. Future versions could add export functionality.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Coaching unavailable" error | Check Azure OpenAI API connection and credits |
| Responses take too long | API might be rate-limited; try again in a moment |
| Coach doesn't reference my profile | Make sure profile is complete in "My Profile" page |
| Chat history lost | Browser was refreshed; use "Start New Conversation" to reset |

## Code Examples

### Using the CoachingAssistant in code

```python
from coaching_assistant import CoachingAssistant

coach = CoachingAssistant()

# Get meal guidance
guidance = coach.get_meal_guidance(
    meal_name="Chicken rice bowl",
    meal_nutrition={"calories": 650, "protein": 35, "carbs": 75},
    daily_nutrition={"calories": 1200, "protein": 30, "carbs": 150},
    daily_targets={"calories": 2000, "protein": 50, "carbs": 300},
    user_profile={"health_conditions": ["diabetes"], "age_group": "26-35"}
)

# Analyze patterns
insights = coach.analyze_eating_patterns(
    meals=recent_meals,
    daily_nutrition=today_nutrition,
    daily_targets=targets,
    user_profile=user_profile
)

# Answer a question
answer = coach.answer_nutrition_question(
    question="How much fiber do I need?",
    user_profile=user_profile,
    daily_nutrition=today_nutrition,
    daily_targets=targets
)
```

---

**Created**: November 21, 2025  
**Version**: 1.0  
**Status**: ✅ Ready for Production
