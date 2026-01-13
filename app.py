import streamlit as st
import pandas as pd

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Disease Impact on Hospital Visits",
    layout="wide"
)

st.title("🏥 Disease Impact on Hospital Visits Dashboard")

# =============================
# LOAD EXCEL FILE
# =============================
FILE_NAME = "diagnosis_encounter.xlsx"

try:
    xls = pd.ExcelFile(FILE_NAME)
    diagnosis = pd.read_excel(xls, sheet_name=0)
    encounters = pd.read_excel(xls, sheet_name=1)
except Exception as e:
    st.error(f"❌ Error loading Excel file: {e}")
    st.stop()

# =============================
# VALIDATE REQUIRED COLUMNS
# =============================
required_diag_cols = {"DiagnosisID", "DiagnosisDescription", "EncounterID"}
required_enc_cols = {"EncounterID", "EncounterDate", "EncounterType", "FacilityID"}

if not required_diag_cols.issubset(diagnosis.columns):
    st.error("❌ Diagnosis sheet missing required columns")
    st.stop()

if not required_enc_cols.issubset(encounters.columns):
    st.error("❌ Encounters sheet missing required columns")
    st.stop()

# =============================
# MERGE DATA
# =============================
df = diagnosis.merge(encounters, on="EncounterID", how="inner")

if df.empty:
    st.warning("⚠ No matching EncounterID found between sheets")
    st.stop()

# =============================
# DATE PROCESSING
# =============================
df["EncounterDate"] = pd.to_datetime(df["EncounterDate"], errors="coerce")
df = df.dropna(subset=["EncounterDate"])

if df.empty:
    st.warning("⚠ No valid dates available after parsing EncounterDate")
    st.stop()

df["Year"] = df["EncounterDate"].dt.year
df["Month"] = df["EncounterDate"].dt.to_period("M")

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("Filters")

years = sorted(df["Year"].unique())

if not years:
    st.warning("⚠ No year values found in data")
    st.stop()

selected_year = st.sidebar.selectbox("Select Year", years)
df = df[df["Year"] == selected_year]

if df.empty:
    st.warning("⚠ No data available for selected year")
    st.stop()

# =============================
# 📊 GRAPHS ONLY
# =============================

# 1️⃣ Monthly Disease Trend
st.subheader("📈 Monthly Disease Trend")
monthly_disease = df.groupby("Month")["DiagnosisID"].count().sort_index()
st.line_chart(monthly_disease)

# 2️⃣ Top Diagnosed Diseases
st.subheader("🩺 Top Diagnosed Diseases")
top_diseases = df["DiagnosisDescription"].value_counts().head(5)
st.bar_chart(top_diseases)

# 3️⃣ Monthly Hospital Visits
st.subheader("🏥 Monthly Hospital Visits")
monthly_visits = df.groupby("Month")["EncounterID"].nunique().sort_index()
st.line_chart(monthly_visits)

# 4️⃣ Disease Surge Impact
st.subheader("⚖ Disease Surge Impact on Hospital Visits")

threshold = monthly_disease.mean()
phase_map = monthly_disease.apply(
    lambda x: "Before Surge" if x < threshold else "After Surge"
)

df["DiseasePhase"] = df["Month"].map(phase_map)

impact = df.groupby("DiseasePhase")["EncounterID"].nunique()
st.bar_chart(impact)

# 5️⃣ Encounter Type Distribution
st.subheader("🚑 Encounter Type Distribution")
encounter_type_counts = df["EncounterType"].value_counts()
st.bar_chart(encounter_type_counts)

# 6️⃣ Facility-wise Disease Load
st.subheader("🏨 Facility-wise Disease Load")
facility_load = (
    df.groupby("FacilityID")["DiagnosisID"]
    .count()
    .sort_values(ascending=False)
    .head(5)
)
st.bar_chart(facility_load)
