import streamlit as st

st.set_page_config(page_title="Liquid Glass Preview", layout="wide", initial_sidebar_state="collapsed")
st.title("🎨 Liquid Glass Design Preview")
st.markdown("Compare different liquid glass styles for your EatWise app")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Style 1: Light Frosted")
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <div style="text-align: center; color: #e0f2f1;">
            <div style="font-size: 28px; margin-bottom: 8px;">💪</div>
            <div style="font-weight: bold;">Light Frosted</div>
            <div style="font-size: 12px; margin-top: 8px;">Modern & subtle</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Pros: Clean, minimal\nCons: Less branded")

with col2:
    st.subheader("Style 2: Teal Tinted ⭐")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(16, 161, 157, 0.15) 0%, rgba(82, 196, 184, 0.08) 100%);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(16, 161, 157, 0.3);
        border-radius: 12px;
        padding: 20px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <div style="text-align: center; color: #e0f2f1;">
            <div style="font-size: 28px; margin-bottom: 8px;">🔥</div>
            <div style="font-weight: bold;">Teal Tinted</div>
            <div style="font-size: 12px; margin-top: 8px;">Brand-aligned</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Pros: Perfect branding\nCons: Slightly more saturated")

with col3:
    st.subheader("Style 3: Dark Edge")
    st.markdown("""
    <div style="
        background: rgba(10, 14, 39, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(16, 161, 157, 0.2);
        border-radius: 12px;
        padding: 20px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.05), 0 8px 32px rgba(0, 0, 0, 0.3);
    ">
        <div style="text-align: center; color: #e0f2f1;">
            <div style="font-size: 28px; margin-bottom: 8px;">🥗</div>
            <div style="font-weight: bold;">Dark Edge</div>
            <div style="font-size: 12px; margin-top: 8px;">High contrast</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Pros: High contrast\nCons: More dramatic")

st.divider()

st.subheader("📊 Card Examples")
st.markdown("How each style looks as nutrition cards:")

st.markdown("#### Style 2 (Teal Tinted) - Nutrition Cards")
card_cols = st.columns(3, gap="small")

cards = [
    ("🔥", "Calories", "158", "cal"),
    ("💪", "Protein", "45.2", "g"),
    ("🥗", "Carbs", "156.8", "g"),
]

for col, (icon, label, value, unit) in zip(card_cols, cards):
    with col:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(16, 161, 157, 0.15) 0%, rgba(82, 196, 184, 0.08) 100%);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(16, 161, 157, 0.3);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <div>
                <div style="font-size: 24px; margin-bottom: 6px;">{icon}</div>
                <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;">{label}</div>
            </div>
            <div>
                <div style="font-size: 22px; font-weight: 900; color: #FFB84D; margin-bottom: 6px;">{value}{unit}</div>
                <div style="background: #0a0e27; border-radius: 4px; height: 3px;"><div style="background: linear-gradient(90deg, #10A19D 0%, #52C4B8 100%); height: 100%; width: 60%; border-radius: 4px;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.success("✅ This is **Style 2 (Teal Tinted)** - Ready to apply to your dashboard!")
st.info("When you're satisfied, I'll apply this liquid glass design to:")
st.markdown("""
- 🔥 Nutrition cards (calories, protein, carbs, fat, etc.)
- 💧 Water tracker card
- 🏆 Achievement cards
- 📊 Statistics cards
- 🎯 All dashboard components
""")
