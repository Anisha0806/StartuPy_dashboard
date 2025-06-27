import streamlit as st
import pandas as pd
from scripts.data_cleaning import clean_startup_data
from scripts.ai_assistant import ask_ai_assistant, build_prompt
import plotly.express as px

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="StartuPy - Beautiful Startup Dashboard", layout="wide")
st.title(" StartuPy - Global Startup Growth & Funding Dashboard")

# ---------- LOAD & CLEAN DATA ----------
df = clean_startup_data("data/startup_growth_investment_data.csv")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("📊 Filter Data")
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
selected_year = st.sidebar.slider("Select Year Founded Range", min_year, max_year, (min_year, max_year))

industries = df["Industry Vertical"].dropna().unique().tolist()
selected_industries = st.sidebar.multiselect("Select Industries", industries, default=industries)

countries = df["Country"].dropna().unique().tolist() if "Country" in df.columns else []
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries) if countries else []

# ---------- APPLY FILTERS ----------
filtered_df = df[
    (df["Year"] >= selected_year[0]) & 
    (df["Year"] <= selected_year[1]) & 
    (df["Industry Vertical"].isin(selected_industries))
]
if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]
 # ---------- StartuPyGPT Assistant (Styled) ----------
st.markdown("""
    <style>
    .startupy-box {
        background-color: #f0fdf4;
        border: 2px solid #4CAF50;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .startupy-header {
        font-size: 24px;
        font-weight: bold;
        color: #2e7d32;
        margin-bottom: 10px;
    }
    .startupy-response {
        background-color: #e8f5e9;
        padding: 15px;
        border-left: 5px solid #4CAF50;
        border-radius: 8px;
        font-size: 16px;
        color: #1b5e20;
        margin-top: 10px;
    }
    </style>
    <div class="startupy-box">
    <div class="startupy-header">🤖 StartuPyGPT</div>
""", unsafe_allow_html=True)

user_query = st.text_area("Ask anything about your startup idea, funding, or roadmap:", height=130, key="startupy_input")

selected_industry = selected_industries[0] if selected_industries else None
selected_year_val = selected_year[0] if isinstance(selected_year, tuple) else selected_year
selected_country = selected_countries[0] if selected_countries else None

if st.button("🚀 Ask StartuPyGPT"):
    if user_query.strip():
        with st.spinner("Thinking..."):
            prompt = build_prompt(
                user_query,
                selected_industry=selected_industry,
                selected_year=selected_year_val,
                selected_country=selected_country
            )
            ai_response = ask_ai_assistant(prompt)

        # Styled response
        st.markdown(f'<div class="startupy-response">{ai_response}</div>', unsafe_allow_html=True)
    else:
        st.warning("Please enter a query.")

st.markdown("</div>", unsafe_allow_html=True)


# ---------- METRICS ----------
st.subheader(f"📍 Summary from {selected_year[0]} to {selected_year[1]}")
col1, col2, col3 = st.columns(3)
col1.metric("📌 Total Startups", filtered_df["Startup Name"].nunique())
col2.metric("💸 Total Funding (USD)", f"${filtered_df['Total Funding (USD)'].sum():,.0f}")
col3.metric("🌍 Countries Selected", len(selected_countries) if countries else "N/A")

# ---------- GRAPH 1: FUNDING BY INDUSTRY ----------
st.subheader("💼 Total Funding by Industry")
industry_funding = filtered_df.groupby("Industry Vertical")["Total Funding (USD)"].sum().reset_index()
fig_industry = px.bar(
    industry_funding.sort_values("Total Funding (USD)", ascending=False),
    x="Industry Vertical", y="Total Funding (USD)", color="Total Funding (USD)",
    title="💼 Total Funding by Industry", text_auto='.2s', color_continuous_scale="Viridis")
fig_industry.update_layout(
    template="seaborn", title_font_size=22,
    font=dict(family="Arial", size=14),
    plot_bgcolor="#F3EDED", paper_bgcolor="#403434",
    xaxis=dict(title_font=dict(size=16), tickangle=45),
    yaxis=dict(title_font=dict(size=16)),
)
st.plotly_chart(fig_industry, use_container_width=True)

# ---------- GRAPH 2: YEARLY FUNDING TREND ----------
st.subheader("📈 Yearly Funding Trend")
year_funding = filtered_df.groupby("Year")["Total Funding (USD)"].sum().reset_index()
fig_year = px.line(
    year_funding, x="Year", y="Total Funding (USD)", markers=True,
    title="📈 Yearly Funding Trend", color_discrete_sequence=["#EF553B"])
fig_year.update_layout(
    template="seaborn", title_font_size=22,
    plot_bgcolor="#F9F9F9", paper_bgcolor="#403434",
    xaxis_title="Year", yaxis_title="Funding Amount (USD)",
    font=dict(size=14, family="Arial")
)
st.plotly_chart(fig_year, use_container_width=True)

# ---------- GRAPH 3: FUNDING BY CITY ----------
if "City" in filtered_df.columns:
    st.subheader("🏙 Funding by City")
    city_funding = filtered_df.groupby("City")["Total Funding (USD)"].sum().reset_index()
    fig_city = px.pie(
        city_funding, names="City", values="Total Funding (USD)", hole=0.4,
        title="🏙 Funding by City")
    fig_city.update_layout(template="seaborn", font=dict(family="Arial", size=14))
    st.plotly_chart(fig_city, use_container_width=True)

# ---------- GRAPH 4: FUNDING BY COUNTRY ----------
if "Country" in filtered_df.columns:
    st.subheader("🌐 Funding by Country")
    country_funding = filtered_df.groupby("Country")["Total Funding (USD)"].sum().reset_index()
    fig_country = px.bar(
        country_funding.sort_values("Total Funding (USD)", ascending=False),
        x="Country", y="Total Funding (USD)", color="Total Funding (USD)",
        title="🌐 Total Funding by Country", text_auto='.2s', color_continuous_scale="Blues")
    fig_country.update_layout(
        template="seaborn", title_font_size=22,
        font=dict(family="Arial", size=14),
        plot_bgcolor="#F9F9F9", paper_bgcolor="#403434",
        xaxis=dict(title_font=dict(size=16)),
        yaxis=dict(title_font=dict(size=16)),
    )
    st.plotly_chart(fig_country, use_container_width=True)

# ---------- FOOTER: Contact Information ----------
st.markdown("""
<br><hr><br>
<div style="text-align:center; font-size:16px;">
    💬 <strong>Need help or want to collaborate?</strong><br>
    📧 Email: <a href="mailto:anishasharmacs@gmail.com">anishasharmacs@gmail.com</a><br>
    🔗 LinkedIn: <a href="https://www.linkedin.com/in/anisha-sharma-0bb465251" target="_blank">Anisha Sharma</a><br><br>
    © 2025 <b>StartuPy Dashboard</b> · Made with ❤️ by Anisha Sharma
</div>
""", unsafe_allow_html=True)
