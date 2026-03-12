import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Server Monitoring Dashboard")

# Errors per hour
data = requests.get("http://localhost:8000/errors_per_hour").json()
df = pd.DataFrame(data)

st.subheader("Errors Per Hour")

fig = px.line(df, x="hour", y="errors", title="Errors Over Time")
st.plotly_chart(fig)


# Server failure rate
data = requests.get("http://localhost:8000/server_failure_rate").json()
df = pd.DataFrame(data)

st.subheader("Server Failure Rate")

fig = px.bar(df, x="server_name", y="failure_rate")
st.plotly_chart(fig)


# Top failing services
data = requests.get("http://localhost:8000/top_failing_services").json()
df = pd.DataFrame(data)

st.subheader("Top Failing Services")

fig = px.bar(df, x="process_name", y="errors")
st.plotly_chart(fig)