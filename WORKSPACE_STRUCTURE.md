# EatWise Workspace Structure

```
eatwise_ai/
│
├── 📄 Core Application Files (Root)
│   ├── app.py                    # Main Streamlit application
│   ├── auth.py                   # Authentication system
│   ├── database.py               # Database operations (Supabase)
│   ├── nutrition_analyzer.py     # AI meal analysis (Azure OpenAI)
│   ├── recommender.py            # AI recommendations
│   ├── config.py                 # Configuration & constants
│   ├── constants.py              # App constants
│   ├── utils.py                  # Utility functions
│   ├── requirements.txt          # Python dependencies
│   ├── README.md                 # Project overview
│   ├── .env                      # Environment variables (private)
│   ├── .gitignore                # Git ignore rules
│   │
│
├── 📁 scripts/                   # Setup & Testing Scripts
│   ├── setup_database.py         # Create database schema
│   ├── fix_database.py           # Database fixes
│   ├── fix_rls.py                # RLS policy fixes
│   ├── disable_all_rls.py        # Disable RLS for development
│   ├── test_azure.py             # Test Azure OpenAI connection
│   ├── test_meals.py             # Test meal logging
│   ├── test_food_history.py      # Test food history
│   ├── check_schema.py           # Check table schema
│   └── database_setup.sql        # SQL schema definition
│   
├── 📁 docs/                      # Documentation
│   ├── .env.example              # Example environment variables
│   └── (Other documentation files as needed)
│
├── 📁 .streamlit/                # Streamlit configuration
│
├── 📁 venv/                      # Virtual environment
│
└── 📁 __pycache__/               # Python cache
```

## Key Directories

### Root Level
- **Core Python files** for the application
- Directly executed by Streamlit
- All files needed for deployment

### `scripts/`
- Database setup and initialization
- Testing and validation scripts
- Database schema files
- **Not needed for deployment** - Streamlit Cloud ignores this

### `docs/`
- Documentation files
- Configuration examples
- Reference materials
- **Not needed for deployment**

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   - Copy `.env.example` to `.env`
   - Add your credentials:
     - Supabase URL & Key
     - Azure OpenAI endpoint & key
     - Email/password auth credentials

3. **Run the app:**
   ```bash
   python -m streamlit run app.py
   ```

## Deployment to Streamlit Cloud

1. Push to GitHub (this structure is perfect for it)
2. Connect repo to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Done! Streamlit Cloud will automatically deploy

## Scripts Usage

All scripts in `scripts/` are optional and only needed for:
- Initial setup (`setup_database.py`)
- Testing specific features (`test_*.py`)
- Debugging issues (`fix_*.py`)

After initial setup, you typically don't need to run these scripts.
