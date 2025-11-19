# Scripts Directory

This directory contains utility scripts for database setup, testing, and maintenance.

## 📁 Script Categories

### 🗄️ Database Setup & Migration
- **`database_setup.sql`** - Initial Supabase schema setup (run this first!)
- **`add_gender_column.py`** - Add gender column to health profiles
- **`add_timezone_column.py`** - Add timezone column to health profiles

### 🔧 Database Maintenance
- **`fix_database.py`** - General database repair script
- **`fix_rls.py`** - Fix Row Level Security policies
- **`disable_all_rls.py`** - Temporarily disable RLS (development only)

### 🧪 Testing & Debugging
- **`test_azure.py`** - Test Azure OpenAI connection
- **`test_azure_connection.py`** - Verify Azure API integration
- **`test_meals.py`** - Test meal logging functionality
- **`test_food_history.py`** - Test food history operations
- **`check_schema.py`** - Verify database schema
- **`check_latest_meal.py`** - Check latest logged meal
- **`debug_meals.py`** - Debug meal-related issues

## 🚀 Quick Usage

### Initial Setup
```bash
# 1. Run SQL setup first
# Open Supabase dashboard > SQL Editor > paste database_setup.sql > Run

# 2. Run Python setup scripts if needed
python scripts/add_gender_column.py
python scripts/add_timezone_column.py
```

### Testing
```bash
# Test Azure/OpenAI connection
python scripts/test_azure_connection.py

# Test meal operations
python scripts/test_meals.py

# Verify database schema
python scripts/check_schema.py
```

### Maintenance
```bash
# Fix database issues
python scripts/fix_database.py

# Fix RLS policies
python scripts/fix_rls.py

# Check latest meal entry
python scripts/check_latest_meal.py
```

## ⚠️ Important Notes

### Development Only Scripts
- `disable_all_rls.py` - **Only for development!** Never run on production
- Always enable RLS before deploying

### Database Modifications
- Always backup database before running migration scripts
- Test scripts on development database first
- Run `check_schema.py` after modifications to verify

### Testing Scripts
- Ensure `.env` file is configured
- Verify Azure/OpenAI credentials before testing
- Check database connection first

## 📝 Script Dependencies

All scripts require:
- Python 3.8+
- Dependencies from `requirements.txt`
- Configured `.env` file with:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `OPENAI_API_KEY` (for Azure tests)

## 🔍 Troubleshooting

### Script not finding modules
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database connection fails
```bash
# Check .env file
# Verify SUPABASE_URL and SUPABASE_KEY
# Ensure Supabase project is active
```

### RLS errors
```bash
# Run to check status
python scripts/check_schema.py

# Fix policies
python scripts/fix_rls.py
```

---

**Maintenance Scripts Last Updated**: November 19, 2025
