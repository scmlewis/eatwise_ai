# Scripts Directory

This directory contains **essential** utility scripts for database setup and user maintenance.

## ✅ What's in This Branch (main)

### 🗄️ Database Setup
- **`database_setup.sql`** - Initial Supabase schema (run this first!)
- **`create_water_intake_table.sql`** - Create water tracking table

### 🔧 User Maintenance Tools
- **`create_missing_profiles.py`** - Fix missing user health profiles (user-facing tool)

## 📝 Important Notes

### What Happened to Other Scripts?
**Development/Testing scripts have been moved to the `dev` branch** to keep main clean:
- Diagnostic scripts (test_*.py, check_*.py, debug_*.py)
- Database utilities (fix_*.py, disable_*.py)
- Migration scripts (add_*.py)
- Design tools (design_*.py)

**To access dev tools**: `git checkout dev`

## 🚀 Quick Usage

### Initial Setup (First Time)
```bash
# 1. Run SQL setup first
# Open Supabase dashboard > SQL Editor > paste database_setup.sql > Run

# 2. Optional: Create water intake table
# Open Supabase dashboard > SQL Editor > paste create_water_intake_table.sql > Run
```

### User Maintenance
```bash
# Fix missing profiles for existing users
python scripts/create_missing_profiles.py
```

## 🔗 Development Tools

All development and testing scripts are in the `dev` branch:
```bash
git checkout dev
python scripts/test_azure_connection.py  # Test Azure
python scripts/check_schema.py            # Verify schema
python scripts/fix_rls.py                 # Fix RLS issues
# ... and many more
```

## 📋 Script Dependencies

All scripts require:
- Python 3.8+
- Dependencies from `requirements.txt`
- Configured `.env` file with:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`

## 🎯 Branch Strategy

| Branch | Purpose | Files |
|--------|---------|-------|
| **main** | Production | Core app, essential setup scripts |
| **dev** | Development | Testing, diagnostics, utilities |

---

**Main Branch Scripts Last Updated**: November 20, 2025
