# File Audit Report - EatWise

## Core Files (KEEP in main)
### Application Entry Point
- ✅ `app.py` (3599 lines) - Main Streamlit application - **ESSENTIAL**

### Core Modules
- ✅ `auth.py` (193 lines) - Authentication manager - **ESSENTIAL**
- ✅ `database.py` (315 lines) - Supabase database interface - **ESSENTIAL**
- ✅ `config.py` (42 lines) - Configuration and secrets - **ESSENTIAL**
- ✅ `constants.py` - Static data and enums - **ESSENTIAL**
- ✅ `utils.py` (205 lines) - Helper functions - **ESSENTIAL**
- ✅ `nutrition_analyzer.py` - Nutrition analysis engine - **ESSENTIAL**
- ✅ `nutrition_components.py` - Reusable UI components - **ESSENTIAL**
- ✅ `recommender.py` - AI recommendation engine - **ESSENTIAL**

### Configuration Files
- ✅ `.env` - Environment variables (git-ignored) - **ESSENTIAL**
- ✅ `.streamlit/config.toml` - Streamlit config - **ESSENTIAL**
- ✅ `.streamlit/secrets.toml` - Secrets (git-ignored) - **ESSENTIAL**
- ✅ `requirements.txt` - Python dependencies - **ESSENTIAL**

### Documentation (Main)
- ✅ `README.md` - Main documentation - **KEEP**
- ✅ `PROJECT_STATUS.md` - Status report - **KEEP**
- ✅ `HOUSEKEEPING.md` - Maintenance guide - **KEEP**
- ✅ `PHASE_2_COMPLETE.md` - Completion summary - **KEEP**

### Documentation (Folder)
- ✅ `docs/` folder with guides - **KEEP**

---

## Optional/Development Files (MOVE to dev branch)
### Design & Preview
- ❌ `design_system.py` - Design tokens/system (reference, not runtime) - **MOVE**
- ❌ `design_preview.py` - Interactive design demo - **MOVE**

### Diagnostic & Setup Scripts
- ❌ `scripts/test_profile_loading.py` - Testing tool - **MOVE**
- ❌ `scripts/test_meals.py` - Testing tool - **MOVE**
- ❌ `scripts/test_food_history.py` - Testing tool - **MOVE**
- ❌ `scripts/test_azure_connection.py` - Testing tool - **MOVE**
- ❌ `scripts/test_azure.py` - Testing tool - **MOVE**
- ❌ `scripts/fix_rls.py` - Database utility - **MOVE**
- ❌ `scripts/fix_database.py` - Database utility - **MOVE**
- ❌ `scripts/disable_all_rls.py` - Database utility - **MOVE**
- ❌ `scripts/debug_meals.py` - Debug tool - **MOVE**
- ❌ `scripts/check_schema.py` - Inspection tool - **MOVE**
- ❌ `scripts/check_latest_meal.py` - Inspection tool - **MOVE**
- ❌ `scripts/add_timezone_column.py` - Migration script - **MOVE**
- ❌ `scripts/add_gender_column.py` - Migration script - **MOVE**

### Setup Scripts (KEEP - needed for initial setup)
- ✅ `scripts/create_missing_profiles.py` - User-facing fix tool - **KEEP in main**
- ✅ `scripts/database_setup.sql` - Initial database setup - **KEEP in main**
- ✅ `scripts/create_water_intake_table.sql` - Initial setup - **KEEP in main**

---

## Summary

### Files to KEEP in main (Core Production)
- 9 Python modules (app + 8 core modules)
- 4 configuration files
- 5 documentation files + docs/ folder
- 2 essential setup scripts
- **Total: Lean, production-ready codebase**

### Files to MOVE to dev branch (Development/Testing)
- 2 design files (design_system.py, design_preview.py)
- 11 diagnostic/testing scripts
- 4 database utility scripts
- **Total: 17 non-essential files**

### Benefits of This Split
✅ Main branch stays clean and focused on production
✅ Development tools don't clutter the main branch
✅ Easier to understand what's actually needed
✅ Dev branch can have different CI/CD rules
✅ Easier to deploy - fewer files to consider
✅ Clear separation of concerns

---

**Audit Date**: November 20, 2025
**Status**: Ready for branch reorganization
