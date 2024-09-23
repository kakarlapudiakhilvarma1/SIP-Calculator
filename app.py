import streamlit as st
import pandas as pd
import requests
import json

def calculate_sip(monthly_investment, annual_return, years, annual_step_up):
    monthly_return = (annual_return / 12) / 100
    total_months = years * 12
    total_invested = 0
    future_value = 0

    for month in range(1, total_months + 1):
        if month % 12 == 1 and month > 1:
            monthly_investment *= (1 + annual_step_up / 100)
        
        total_invested += monthly_investment
        future_value = (future_value + monthly_investment) * (1 + monthly_return)

    return total_invested, future_value

def get_groq_explanation(api_key, investment_details):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Analyze the following SIP investment details and provide a detailed explanation of the returns,
    along with suggestions for the investor:

    {investment_details}

    Please include:
    1. An overview of the investment strategy
    2. A breakdown of the returns
    3. The power of compounding in this scenario
    4. The impact of the annual step-up
    5. Potential risks and considerations
    6. Suggestions for optimizing the investment strategy
    """

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

st.set_page_config(page_title="SIP Calculator with Analysis 💰📅", layout="wide")

st.title("SIP Calculator with Analysis")

# Sidebar for GROQ API key
st.sidebar.header("GROQ API Configuration")
groq_api_key = st.sidebar.text_input("Enter your GROQ API key", type="password")

# Main input form
st.header("Enter SIP Details")

col1, col2 = st.columns(2)

with col1:
    monthly_investment = st.number_input("Monthly Investment Amount (INR)", min_value=100, value=5000, step=100)
    annual_return = st.number_input("Expected Annual Return (%)", min_value=1.0, max_value=30.0, value=12.0, step=0.1)

with col2:
    years = st.number_input("Investment Duration (Years)", min_value=1, max_value=40, value=10, step=1)
    annual_step_up = st.number_input("Annual Step-up (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)

if st.button("Calculate and Analyze"):
    total_invested, future_value = calculate_sip(monthly_investment, annual_return, years, annual_step_up)
    
    st.header("SIP Calculation Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Amount Invested", f"₹{total_invested:,.2f}")
    col2.metric("Expected Future Value", f"₹{future_value:,.2f}")
    col3.metric("Wealth Gained", f"₹{future_value - total_invested:,.2f}")

    investment_details = f"""
    Monthly Investment: ₹{monthly_investment}
    Expected Annual Return: {annual_return}%
    Investment Duration: {years} years
    Annual Step-up: {annual_step_up}%
    Total Amount Invested: ₹{total_invested:,.2f}
    Expected Future Value: ₹{future_value:,.2f}
    Wealth Gained: ₹{future_value - total_invested:,.2f}
    """

    if groq_api_key:
        st.header("Analysis 🧠")
        with st.spinner("Generating analysis..."):
            groq_explanation = get_groq_explanation(groq_api_key, investment_details)
            st.markdown(groq_explanation)
    else:
        st.warning("Please enter your GROQ API key in the sidebar to get a detailed analysis.")

st.sidebar.info("This app uses the GROQ API to provide detailed investment analysis. Your API key is required for this functionality.")