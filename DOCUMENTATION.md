# EatWise Documentation Index

Welcome to EatWise! This document helps you navigate our comprehensive documentation.

## 📚 Documentation Structure

All detailed documentation has been organized in the `docs/` folder for better maintainability.

### 📖 Main Documentation Hub

**Start here:** [docs/INDEX.md](docs/INDEX.md) - Complete documentation directory with all guides organized by topic

### Quick Links

**For Users:**
- 📖 [README.md](README.md) - Start here! Overview of features and quick start guide
- ❓ **Help Page** - Available in the app (❓ Help menu) with features, usage guide, and FAQ
- 🎯 [Gamification Guide](docs/GAMIFICATION_QUICKSTART.md) - 5-minute guide to gamification features

**For Developers:**
- 📋 [Implementation Report](docs/IMPLEMENTATION_REPORT.md) - Technical implementation details
- 🔍 [Code Audit Report](docs/CODE_AUDIT_REPORT.md) - Code quality analysis
- 📊 [Code Quality Analysis](docs/CODE_QUALITY_ANALYSIS.md) - Quality metrics and recommendations
- 📂 [Workspace Structure](docs/guides/WORKSPACE_STRUCTURE.md) - Project file organization

**Documentation Library:**
- [docs/INDEX.md](docs/INDEX.md) - Complete navigation hub (recommended)
- `docs/guides/` - Developer guides and component documentation
- `docs/setup/` - Deployment and setup instructions

## 🎯 Key Features (Updated)

- Smart Meal Logging: text descriptions or food photos with AI-powered ingredient detection and hybrid nutrition estimation.
- Nutrition Tracking: calories, macronutrients and micronutrient tracking with daily summaries and targets.
- AI Health Insights: personalized recommendations, strengths/areas-to-improve, and weekly pattern analysis.
- Personalized Coaching: context-aware AI coach with multi-turn conversations and on-demand guidance.
- Restaurant Menu Analyzer: paste or upload menus (OCR supported) with tailored ordering suggestions.
- Visual Analytics: responsive, single-column nutrition breakdown, macro pie charts, and historical trends.
- Meal Quality & Insights: ranked healthiest meals and items to improve, presented as compact, styled cards.
- Gamification: XP, badges, daily streaks and lightweight challenges to boost engagement.

Note: This documentation focuses on the current stable features and recent UI/UX improvements — older experimental or deprecated features have been removed.

## 🚀 Getting Started

1. **Read** [README.md](README.md) for installation and basic setup
2. **Run** `streamlit run app.py` to start the application
3. **Create** your profile in the app
4. **Log** your first meal (text or photo)
5. **Open** the in-app Help page (❓) for quick tips and FAQ
6. **Use** the Coaching feature (🎯) for on-demand personalized guidance

## 📊 Project Status

**Current Version**: v2.6.2  
**Latest Update**: December 06, 2025

### Recent Changes (Dec 2025)
- UI/UX improvements: single-column Nutrition Breakdown, compact Most-Frequent-Meal insight, Meal Quality cards
- Performance: reduced unnecessary full-app reruns (`st.rerun()` minimization) and session-state optimizations
- Validation: added server-side and client-side meal validation to prevent bad entries
- Code refactor: extracted common helpers (`show_nutrition_facts`, `validate_meal_data`, stat cards)
- Bug fixes: profile-update UnboundLocalError fix, back-to-top hidden on login, sidebar reorganization
- Existing: OCR menu analyzer, AI coaching, gamification, nutrition analytics remain supported

### Verified Features
- ✅ Meal logging (text & photo)
- ✅ Nutrition tracking and analytics
- ✅ Personalized recommendations
- ✅ Restaurant menu analysis
- ✅ Gamification system (production ready)
- ✅ Secure authentication

## 🔗 External Resources

- **GitHub Repository**: https://github.com/scmlewis/eatwise_ai
- **Streamlit Documentation**: https://docs.streamlit.io
- **Supabase Documentation**: https://supabase.com/docs
- **OpenAI API Docs**: https://platform.openai.com/docs

## 📞 Support

Have questions? Check these resources in order:

1. **Help Page** - In-app help with FAQ and usage guide
2. **This Documentation** - Overview and guides
3. **GitHub Issues** - Report bugs or request features
4. **Documentation Files** - Detailed technical information

## 🎨 App Navigation

Once logged in, you'll see these pages:

- 📊 **Dashboard** - Daily nutrition overview
- 📝 **Log Meal** - Add meals with text or photos
- 📈 **Analytics** - View trends and statistics
- 📋 **Meal History** - Browse and edit past meals
- 💡 **Insights** - AI-powered recommendations
- 🍽️ **Eating Out** - Analyze restaurant menus
- 🎯 **Coaching** - Chat with AI nutrition coach
- 👤 **My Profile** - Update your health profile
- ❓ **Help** - Feature overview and FAQ

---

**Last Updated**: December 06, 2025  
**Documentation Version**: v2.1

For the most up-to-date information, see [docs/INDEX.md](docs/INDEX.md) or visit our GitHub repository.
