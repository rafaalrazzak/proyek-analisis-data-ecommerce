import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")

st.set_page_config(page_title="Olist E-Commerce Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    geo_df = pd.read_csv(os.path.join(BASE_DIR, "geolocation_state.csv"))
    return df, geo_df


all_df, geo_state_df = load_data()

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.title("Olist E-Commerce Dashboard")
    st.caption("Brazilian E-Commerce Public Dataset (2016-2018)")
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

st.header("Olist E-Commerce Dashboard :bar_chart:")

# ---------------------------------------------------------------- KPI
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df.order_id.nunique()
    st.metric("Total Pesanan", value=f"{total_orders:,}")

with col2:
    total_revenue = main_df.price.sum()
    st.metric("Total Revenue", value=format_currency(total_revenue, "BRL", locale="pt_BR"))

with col3:
    total_customers = main_df.customer_unique_id.nunique()
    st.metric("Total Pelanggan", value=f"{total_customers:,}")

st.markdown("---")

# ---------------------------------------------------------------- Q1: monthly trend
st.subheader("Tren Jumlah Pesanan dan Revenue Bulanan")

monthly_df = main_df.resample(rule="ME", on="order_purchase_timestamp").agg({
    "order_id": "nunique",
    "price": "sum"
}).reset_index()
monthly_df.columns = ["order_month", "order_count", "revenue"]

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_df["order_month"], monthly_df["order_count"], marker="o", linewidth=2, color="#72BCD4")
    ax.set_title("Jumlah Pesanan per Bulan", fontsize=18)
    ax.tick_params(axis="x", labelrotation=45, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_df["order_month"], monthly_df["revenue"], marker="o", linewidth=2, color="#D3936A")
    ax.set_title("Revenue per Bulan (BRL)", fontsize=18)
    ax.tick_params(axis="x", labelrotation=45, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    st.pyplot(fig)

st.markdown("---")

# ---------------------------------------------------------------- Q2: category revenue
st.subheader("Kategori Produk dengan Revenue Tertinggi & Terendah")

cat_revenue_df = main_df.groupby("product_category_name_english").agg(
    order_count=("order_id", "nunique"),
    revenue=("price", "sum")
).sort_values("revenue", ascending=False)

col1, col2 = st.columns(2)

with col1:
    top_cat = cat_revenue_df.head(5).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x="revenue", y="product_category_name_english", hue="product_category_name_english",
                data=top_cat, palette=colors, legend=False, ax=ax)
    ax.set_title("5 Kategori Revenue Tertinggi", fontsize=18)
    ax.set_ylabel(None)
    ax.set_xlabel("Revenue (BRL)")
    st.pyplot(fig)

with col2:
    bottom_cat = cat_revenue_df.tail(5).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#E06666"]
    sns.barplot(x="revenue", y="product_category_name_english", hue="product_category_name_english",
                data=bottom_cat, palette=colors, legend=False, ax=ax)
    ax.set_title("5 Kategori Revenue Terendah", fontsize=18)
    ax.set_ylabel(None)
    ax.set_xlabel("Revenue (BRL)")
    st.pyplot(fig)

st.markdown("---")

# ---------------------------------------------------------------- Q3: geospatial
st.subheader("Sebaran Pelanggan Berdasarkan Negara Bagian (Geospatial Analysis)")

state_customer_df = main_df.groupby("customer_state").customer_unique_id.nunique().sort_values(ascending=False).reset_index()
state_customer_df.columns = ["customer_state", "customer_count"]

col1, col2 = st.columns([1, 1])

with col1:
    top10_state = state_customer_df.head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#72BCD4"] + ["#D3D3D3"] * 9
    sns.barplot(x="customer_count", y="customer_state", hue="customer_state",
                data=top10_state, palette=colors, legend=False, ax=ax)
    ax.set_title("10 Negara Bagian Pelanggan Terbanyak", fontsize=18)
    ax.set_xlabel("Jumlah Pelanggan")
    ax.set_ylabel(None)
    st.pyplot(fig)

with col2:
    geo_df = geo_state_df.merge(state_customer_df, on="customer_state", how="inner")
    st.map(geo_df.rename(columns={"lat": "latitude", "lng": "longitude"}),
           latitude="latitude", longitude="longitude", size="customer_count")

st.markdown("---")

# ---------------------------------------------------------------- Q4: RFM
st.subheader("Customer Segmentation berdasarkan RFM Analysis")

rfm_df = main_df.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "price": "sum"
})
rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
recent_date = main_df["order_purchase_timestamp"].dt.date.max()
rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

rfm_df["r_rank"] = rfm_df["recency"].rank(ascending=False)
rfm_df["f_rank"] = rfm_df["frequency"].rank(ascending=True)
rfm_df["m_rank"] = rfm_df["monetary"].rank(ascending=True)
rfm_df["r_rank_norm"] = (rfm_df["r_rank"] / rfm_df["r_rank"].max()) * 100
rfm_df["f_rank_norm"] = (rfm_df["f_rank"] / rfm_df["f_rank"].max()) * 100
rfm_df["m_rank_norm"] = (rfm_df["m_rank"] / rfm_df["m_rank"].max()) * 100
rfm_df["RFM_score"] = 0.15 * rfm_df["r_rank_norm"] + 0.28 * rfm_df["f_rank_norm"] + 0.57 * rfm_df["m_rank_norm"]
rfm_df["RFM_score"] *= 0.05
rfm_df = rfm_df.round(2)

rfm_df["customer_segment"] = np.where(
    rfm_df["RFM_score"] > 4.5, "Top customers", np.where(
        rfm_df["RFM_score"] > 4, "High value customers", np.where(
            rfm_df["RFM_score"] > 3, "Medium value customers", np.where(
                rfm_df["RFM_score"] > 1.6, "Low value customers", "Lost customers"))))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rata-rata Recency (hari)", value=round(rfm_df.recency.mean(), 1))
with col2:
    st.metric("Rata-rata Frequency", value=round(rfm_df.frequency.mean(), 2))
with col3:
    st.metric("Rata-rata Monetary", value=format_currency(rfm_df.monetary.mean(), "BRL", locale="pt_BR"))

customer_segment_df = rfm_df.groupby(by="customer_segment", as_index=False).customer_unique_id.nunique()
customer_segment_df.columns = ["customer_segment", "customer_count"]
customer_segment_df["customer_segment"] = pd.Categorical(customer_segment_df["customer_segment"], [
    "Lost customers", "Low value customers", "Medium value customers",
    "High value customers", "Top customers"
])
customer_segment_df = customer_segment_df.sort_values(by="customer_segment")

fig, ax = plt.subplots(figsize=(12, 5))
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]
sns.barplot(x="customer_count", y="customer_segment", hue="customer_segment",
            data=customer_segment_df, palette=colors, legend=False, ax=ax)
ax.set_title("Jumlah Pelanggan per Segmen RFM", fontsize=18)
ax.set_xlabel("Jumlah Pelanggan")
ax.set_ylabel(None)
st.pyplot(fig)

st.caption("Dashboard dibuat sebagai submission Proyek Analisis Data - Dicoding")
