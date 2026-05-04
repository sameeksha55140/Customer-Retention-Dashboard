import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Bank Retention Dashboard", layout="wide")

st.title("🏦 Customer Engagement & Retention Analytics")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("European_Bank.csv")
    return df

df = load_data()

# ---------------------------
# FEATURE ENGINEERING
# ---------------------------
df['Engagement'] = df['IsActiveMember'].map({1:'Active', 0:'Inactive'})
df['ProductSegment'] = df['NumOfProducts'].apply(
    lambda x: 'Single' if x == 1 else 'Multiple'
)

# ---------------------------
# SIDEBAR (USER CONTROLS)
# ---------------------------
st.sidebar.header("🔧 Filters")

# Engagement filter
engagement_filter = st.sidebar.selectbox(
    "Select Engagement",
    ["All", "Active", "Inactive"]
)

# Product slider
product_filter = st.sidebar.slider(
    "Minimum Products",
    1, 4, 1
)

# Balance filter
balance_filter = st.sidebar.slider(
    "Minimum Balance",
    0, int(df['Balance'].max()), 0
)

# Salary filter
salary_filter = st.sidebar.slider(
    "Minimum Salary",
    0, int(df['EstimatedSalary'].max()), 0
)

# ---------------------------
# APPLY FILTERS
# ---------------------------
filtered_df = df.copy()

if engagement_filter == "Active":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 1]
elif engagement_filter == "Inactive":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 0]

filtered_df = filtered_df[
    (filtered_df['NumOfProducts'] >= product_filter) &
    (filtered_df['Balance'] >= balance_filter) &
    (filtered_df['EstimatedSalary'] >= salary_filter)
]

# ---------------------------
# KPI PANEL
# ---------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

churn_rate = filtered_df['Exited'].mean()
avg_balance = filtered_df['Balance'].mean()
avg_products = filtered_df['NumOfProducts'].mean()
active_rate = filtered_df['IsActiveMember'].mean()

col1.metric("Churn Rate", f"{churn_rate:.2f}")
col2.metric("Avg Balance", f"{avg_balance:.0f}")
col3.metric("Avg Products", f"{avg_products:.2f}")
col4.metric("Active Rate", f"{active_rate:.2f}")

# ---------------------------
# 1️⃣ ENGAGEMENT vs CHURN
# ---------------------------
st.subheader("👥 Engagement vs Churn Overview")

fig1 = px.bar(
    filtered_df,
    x='Engagement',
    y='Exited',
    color='Engagement',
    title="Churn by Engagement"
)

st.plotly_chart(fig1, use_container_width=True)

# ---------------------------
# 2️⃣ PRODUCT UTILIZATION
# ---------------------------
st.subheader("📦 Product Utilization Impact")

fig2 = px.bar(
    filtered_df,
    x='NumOfProducts',
    y='Exited',
    color='NumOfProducts',
    title="Churn vs Product Count"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# 3️⃣ HIGH-VALUE DISENGAGED
# ---------------------------
st.subheader("⚠️ High-Value Disengaged Customers")

high_risk = filtered_df[
    (filtered_df['IsActiveMember'] == 0) &
    (filtered_df['Balance'] > filtered_df['Balance'].median())
]

st.metric("High-Risk Customers", len(high_risk))
st.dataframe(high_risk.head(10))

# ---------------------------
# 4️⃣ RETENTION STRENGTH SCORE
# ---------------------------
st.subheader("🧠 Retention Strength Analysis")

filtered_df['RSI'] = (
    filtered_df['IsActiveMember'] * 0.4 +
    (filtered_df['NumOfProducts']/4) * 0.3 +
    filtered_df['HasCrCard'] * 0.3
)

fig3 = px.histogram(
    filtered_df,
    x='RSI',
    nbins=20,
    title="Relationship Strength Distribution"
)

st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# DATA TABLE
# ---------------------------
st.subheader("📄 Data Preview")
st.dataframe(filtered_df.head())