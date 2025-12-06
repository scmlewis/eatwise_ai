# Changelog

All notable changes to EatWise are documented in this file.

## [2.3.0] - December 6, 2025

### ✨ New Features

#### **Portion Estimation System** 🎯
- Added intelligent portion estimation confidence levels (4 tiers)
- Implemented automatic input assessment based on description detail
- Created confidence disclaimers showing accuracy ranges (±15% to ±50%)
- Added common portion size reference guide accessible after analysis
- Portion sizes grouped with confidence results for better UX

#### **UX/UI Redesign**
- Reorganized "Describe Your Meal" section for cleaner information hierarchy
- Added prominent warning box explaining accuracy vs. detail level
- Streamlined quick reference to 2-column ultra-concise format
- Reduced meal input text area height for tighter layout
- Moved portion examples to appear after confidence disclaimer (better grouping)
- Added emoji to section headers for visual recognition

### 🔧 Technical Improvements

#### **Hybrid Nutrition Analyzer**
- Created comprehensive TDD test suite with 9 tests
- Tests cover: coverage calculation, consistency, nutrition validation, hallucination detection
- All tests passing (execution time: 0.001s)
- Validated hybrid approach against pure LLM analysis

#### **Code Quality**
- Implemented portion estimation disclaimer module (270 lines, 8+ functions)
- Created reusable confidence assessment functions
- Added regex pattern matching for input analysis
- Improved code modularity and reusability

#### **Documentation**
- Created ARCHITECTURE.md (comprehensive system design)
- Created CHANGELOG.md (version history)
- Updated README.md (current features, recent updates)
- Created PORTION_ESTIMATION_GUIDE.md (methodology & examples)
- Archived intermediate test files & analysis reports to docs/archive

### 📚 Documentation Improvements
- Added detailed Portion Estimation section to README
- Created quick reference table for accuracy levels
- Documented portion estimation algorithm in ARCHITECTURE.md
- Added CHANGELOG for version tracking
- Improved project structure documentation

### 🎨 UI/UX Changes
- **Before**: Long scrollable section with multiple expandable items
- **After**: Clean warning box → concise quick tips → input field → reference material
- Better visual hierarchy with reduced cognitive load
- Clearer priority of information (critical vs. reference)
- Improved mobile responsiveness

### 🐛 Bug Fixes
- Fixed meal input label emoji visibility issues
- Corrected text area placeholder length
- Improved warning box formatting
- Fixed column layout spacing

### 📦 Repository Organization

**Files Archived to `docs/archive/`:**
- ANALYSIS_SUMMARY.md
- EATWISE_PAGE_ANALYSIS.md
- HYBRID_ANALYZER_STATUS.md
- HYBRID_ANALYZER_TEST_RESULTS.md
- test_nutrition_validation.py
- test_water_goal.py
- PHASE_2_COMPLETE.md
- PHASE_3_SUMMARY.md
- COACHING_COMPLETE.md
- GAMIFICATION_DEPLOY_CHECKLIST.md
- DELIVERY_SUMMARY.md
- IMPLEMENTATION_REPORT.md

**Files Kept in Root:**
- test_hybrid_analyzer.py (active TDD suite)
- DOCUMENTATION.md (feature documentation)
- PORTION_ESTIMATION_GUIDE.md (user methodology guide)
- README.md (updated project overview)

### 📊 Commits in This Release
```
757aeea - Make 'How to describe your meal' section collapsible
9d74b73 - Reorganize meal input section for better UX and visual hierarchy
d648831 - Make portion estimation rules more prominent
108c01f - Enhance 'Describe Your Meal' section with disclaimers
```

### 📋 Files Modified
- `app.py` - UX reorganization & portion estimation integration
- `README.md` - Updated features, new section on portion estimation
- `ARCHITECTURE.md` - New comprehensive design documentation
- `CHANGELOG.md` - New version history file
- `.gitignore` - Updated to exclude venv, cache, etc. (implicit)

### 📋 Files Created
- `ARCHITECTURE.md` - Complete system design & architecture
- `CHANGELOG.md` - This file
- `docs/archive/` - Directory for intermediate files

---

## [2.2.1] - November 2025

### Features
- Hybrid nutrition analyzer with database coverage tracking
- Comprehensive meal logging with text & photo analysis
- Health insights with eating pattern analysis
- AI nutrition coaching with multi-turn conversation
- Restaurant menu analyzer with personalized recommendations
- Gamification system with XP, challenges, streaks, and badges
- User health profiles with customizable targets

### Bug Fixes
- Fixed file encoding issues in test suite
- Improved error handling in database operations
- Enhanced session state management

---

## [2.0.0] - October 2025

### Major Features
- Complete nutrition tracking application
- Streamlit-based web interface
- Supabase backend with PostgreSQL
- OpenAI GPT-4 integration
- Meal analytics & visualization
- Achievement system

### Architecture
- Modular code organization
- Separation of concerns (auth, db, analysis)
- Reusable UI components
- Security with Row Level Security

---

## [1.0.0] - September 2025

### Initial Release
- Basic meal logging
- Text and photo meal analysis
- Nutrition tracking
- User authentication
- Profile management

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes or major features (2.x.x)
- **MINOR**: New features, backward compatible (2.3.x)
- **PATCH**: Bug fixes, documentation (2.3.0)

---

## Planned for v2.4.0

- [ ] Enhanced hybrid analyzer confidence metadata
- [ ] Hybrid vs LLM comparison testing suite
- [ ] Confidence metadata integration into app
- [ ] Advanced analytics with confidence filtering
- [ ] Mobile app foundation

---

## Contributing

When making changes:
1. Update relevant documentation
2. Follow version numbering scheme
3. Add entry to CHANGELOG.md
4. Include commit hash when releasing
5. Test thoroughly before releasing

---

**Last Updated:** December 6, 2025
**Current Version:** 2.3.0
