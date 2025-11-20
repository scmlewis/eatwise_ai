"""
EatWise Design System Demo
Showcase gradients, colors, typography, and UI components
"""

import streamlit as st

# Page config
st.set_page_config(
    page_title="EatWise Design Demo",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme styling
st.markdown("""
<style>
    :root {
        --primary-color: #10A19D;
        --primary-dark: #0D7A76;
        --primary-light: #52C4B8;
        --secondary-color: #FF6B6B;
        --success-color: #51CF66;
        --warning-color: #FFA500;
        --danger-color: #FF0000;
        --accent-purple: #845EF7;
        --accent-blue: #3B82F6;
    }
    
    .main {
        padding-top: 2rem;
        background: linear-gradient(135deg, #0a3a3a 0%, #1a4d4d 100%);
    }
    
    body {
        background: linear-gradient(135deg, #0a3a3a 0%, #1a4d4d 100%);
        color: #e0f2f1;
    }
    
    /* Gradient classes */
    .gradient-primary {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin: 16px 0;
    }
    
    .gradient-purple {
        background: linear-gradient(135deg, #845EF7 0%, #BE80FF 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin: 16px 0;
    }
    
    .gradient-blue {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin: 16px 0;
    }
    
    .gradient-success {
        background: linear-gradient(135deg, #51CF66 0%, #80C342 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin: 16px 0;
    }
    
    .gradient-warning {
        background: linear-gradient(135deg, #FFA500 0%, #FFB84D 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin: 16px 0;
    }
    
    .gradient-danger {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8A8A 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin: 16px 0;
    }
    
    .card {
        background: rgba(16, 161, 157, 0.1);
        border: 1px solid #10A19D;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }
    
    .card-title {
        color: #52C4B8;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    
    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(16, 161, 157, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 161, 157, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="
    background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
">
    <h1 style="color: white; margin: 0; font-size: 2.5em;">🎨 EatWise Design System</h1>
    <p style="color: rgba(255, 255, 255, 0.9); margin: 10px 0 0 0;">Gradient backgrounds, colors, and UI components showcase</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎨 Design Elements")
selected_section = st.sidebar.radio(
    "Choose a section",
    options=[
        "Gradient Backgrounds",
        "Color Palette",
        "Page Headers",
        "Cards & Components",
        "Typography",
        "Buttons & Interactions"
    ]
)

# ==================== SECTION 1: GRADIENT BACKGROUNDS ====================
if selected_section == "Gradient Backgrounds":
    st.header("🌈 Gradient Backgrounds")
    st.write("Showcase of all gradient backgrounds used in EatWise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="gradient-primary">
            <h3>Primary Gradient</h3>
            <p>Teal to Light Teal - Main brand gradient</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="gradient-blue">
            <h3>Blue Gradient</h3>
            <p>Royal Blue to Light Blue - Data & Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="gradient-warning">
            <h3>Warning Gradient</h3>
            <p>Orange to Light Orange - Alerts & Warnings</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="gradient-purple">
            <h3>Purple Gradient</h3>
            <p>Purple to Light Purple - Analytics & Insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="gradient-success">
            <h3>Success Gradient</h3>
            <p>Green to Lime - Positive & Achievements</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="gradient-danger">
            <h3>Danger Gradient</h3>
            <p>Red to Light Red - Errors & Warnings</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== SECTION 2: COLOR PALETTE ====================
elif selected_section == "Color Palette":
    st.header("🎯 Color Palette")
    st.write("All colors used in the EatWise design system")
    
    colors_data = {
        "Primary": {
            "Main": "#10A19D",
            "Dark": "#0D7A76",
            "Light": "#52C4B8"
        },
        "Semantic": {
            "Success": "#51CF66",
            "Warning": "#FFA500",
            "Danger": "#FF0000",
            "Info": "#3B82F6"
        },
        "Accents": {
            "Purple": "#845EF7",
            "Blue": "#3B82F6",
            "Secondary": "#FF6B6B"
        },
        "Backgrounds": {
            "Dark": "#0a0e27",
            "Darker": "#1a1f3a",
            "Card": "rgba(16, 161, 157, 0.1)"
        }
    }
    
    for category, colors in colors_data.items():
        st.subheader(category)
        cols = st.columns(len(colors))
        
        for col, (name, color) in zip(cols, colors.items()):
            with col:
                st.markdown(f"""
                <div style="
                    background: {color};
                    padding: 40px 20px;
                    border-radius: 8px;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    margin-bottom: 10px;
                ">
                    {name}
                </div>
                <div style="text-align: center; font-size: 12px; color: #a0a0a0;">
                    {color}
                </div>
                """, unsafe_allow_html=True)

# ==================== SECTION 3: PAGE HEADERS ====================
elif selected_section == "Page Headers":
    st.header("📄 Page Headers")
    st.write("Examples of page headers used throughout the app")
    
    # Dashboard header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">📊 Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Location:** Main dashboard page - welcomes users")
    
    # Log Meal header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8A8A 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">📝 Log Meal</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Location:** Meal logging page - action-oriented")
    
    # Analytics header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #845EF7 0%, #BE80FF 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">📈 Analytics & Insights</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Location:** Analytics page - data-focused")
    
    # Insights header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #51CF66 0%, #80C342 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">💡 Health Insights & Recommendations</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Location:** Insights page - personalized")
    
    # Profile header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FF6B16 0%, #FF8A4D 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">👤 My Profile</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Location:** Profile settings page - personal")

# ==================== SECTION 4: CARDS & COMPONENTS ====================
elif selected_section == "Cards & Components":
    st.header("🎴 Cards & Components")
    st.write("Reusable UI components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">📊 Metric Card</div>
            <p>Used for displaying key metrics and statistics</p>
            <div style="color: #FFB84D; font-size: 24px; font-weight: bold;">2200</div>
            <div style="color: #a0a0a0; font-size: 12px;">Calories Today</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #10A19D20 0%, #52C4B840 100%);
            border: 1px solid #10A19D;
            border-radius: 10px;
            padding: 12px 16px;
            text-align: center;
            margin: 16px 0;
        ">
            <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; margin-bottom: 4px; font-weight: 700;">Age Group</div>
            <div style="font-size: 16px; font-weight: 900; color: #60A5FA;">26-35</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">🏆 Achievement Card</div>
            <p>Shows user achievements and badges</p>
            <div style="color: #FFB84D; font-size: 24px;">🎉</div>
            <div style="color: #51CF66; font-size: 12px;">7-day streak achieved!</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid #FF6B6B;
            border-radius: 10px;
            padding: 12px 16px;
            text-align: center;
            margin: 16px 0;
        ">
            <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; margin-bottom: 4px; font-weight: 700;">Health Goal</div>
            <div style="font-size: 16px; font-weight: 900; color: #FF6B6B;">Weight Loss</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bars
    st.subheader("Progress Bars")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="margin: 20px 0;">
            <div style="color: #60A5FA; font-weight: bold; margin-bottom: 8px;">Calories: 1580 / 2200 (72%)</div>
            <div style="height: 8px; background: #333; border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: 72%; background: linear-gradient(90deg, #FF6715 0%, #FFB84D 100%);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="margin: 20px 0;">
            <div style="color: #60A5FA; font-weight: bold; margin-bottom: 8px;">Protein: 93g / 50g (186%)</div>
            <div style="height: 8px; background: #333; border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: 100%; background: linear-gradient(90deg, #FF6B6B 0%, #FF8A8A 100%);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== SECTION 5: TYPOGRAPHY ====================
elif selected_section == "Typography":
    st.header("📝 Typography")
    st.write("Text styles and hierarchy used in the app")
    
    st.markdown("""
    <div style="margin: 30px 0;">
        <h1 style="color: #e0f2f1; margin: 20px 0;">H1 - Page Title (2.5em)</h1>
        <p style="color: #a0a0a0;">Used for main page titles and headers</p>
        
        <h2 style="color: #e0f2f1; margin: 20px 0;">H2 - Section Title (2em)</h2>
        <p style="color: #a0a0a0;">Used for section headers within pages</p>
        
        <h3 style="color: #e0f2f1; margin: 20px 0;">H3 - Subsection Title (1.5em)</h3>
        <p style="color: #a0a0a0;">Used for subsections and component titles</p>
        
        <p style="color: #e0f2f1; font-size: 16px;">Body Text (1em) - Regular paragraph text</p>
        <p style="color: #a0a0a0; font-size: 14px;">Small Text (0.875em) - Secondary information</p>
        
        <p style="color: #52C4B8; font-weight: bold;">Accent Text - Important information (Teal)</p>
        <p style="color: #FFB84D; font-weight: bold;">Warning Text - Attention needed (Orange)</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SECTION 6: BUTTONS & INTERACTIONS ====================
else:  # Buttons & Interactions
    st.header("🔘 Buttons & Interactions")
    st.write("Interactive elements and their states")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Primary Button")
        if st.button("🔘 Primary Action", key="btn1", use_container_width=True):
            st.success("Primary button clicked!")
    
    with col2:
        st.markdown("### Secondary Button")
        if st.button("📝 Secondary Action", key="btn2", use_container_width=True):
            st.info("Secondary button clicked!")
    
    with col3:
        st.markdown("### Action Button")
        if st.button("✅ Confirm Action", key="btn3", use_container_width=True):
            st.success("Action confirmed!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(81, 207, 102, 0.1); border: 1px solid #51CF66; border-radius: 8px; padding: 16px; margin: 16px 0;">
            <div style="color: #51CF66; font-weight: bold; margin-bottom: 8px;">✅ Success Message</div>
            <div style="color: #e0f2f1;">Action completed successfully!</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid #FF6B6B; border-radius: 8px; padding: 16px; margin: 16px 0;">
            <div style="color: #FF6B6B; font-weight: bold; margin-bottom: 8px;">❌ Error Message</div>
            <div style="color: #e0f2f1;">Something went wrong. Please try again.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 165, 0, 0.1); border: 1px solid #FFA500; border-radius: 8px; padding: 16px; margin: 16px 0;">
            <div style="color: #FFB84D; font-weight: bold; margin-bottom: 8px;">⚠️ Warning Message</div>
            <div style="color: #e0f2f1;">Please review before proceeding.</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3B82F6; border-radius: 8px; padding: 16px; margin: 16px 0;">
            <div style="color: #60A5FA; font-weight: bold; margin-bottom: 8px;">ℹ️ Info Message</div>
            <div style="color: #e0f2f1;">Here's some helpful information.</div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a0a0a0; padding: 20px; font-size: 12px;">
    <p>EatWise Design System Demo • Built with Streamlit</p>
    <p>All gradients, colors, and components are production-ready</p>
</div>
""", unsafe_allow_html=True)
