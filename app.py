import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os

USER_FILE = "users.json"

# Create user file if not exists
if not os.path.exists(USER_FILE) or os.path.getsize(USER_FILE) == 0:
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)



# Load users
def load_users():
    with open(USER_FILE, 'r') as f:
        return json.load(f)
    


# Save new user
def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)



# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Sign In"



# Sign In Form
def signin():
    st.subheader("🔐 Sign In")
    username = st.text_input("Username", key="signin_user")
    password = st.text_input("Password", type="password", key="signin_pass")

    login_clicked = st.button("Login")
    if login_clicked:
        users = load_users()
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        
            st.rerun()
        else:
            st.error("Invalid username or password")



# Sign Up Form
def signup():
    st.subheader("📝 Sign Up")
    username = st.text_input("Choose Username", key="new_signup_user")
    password = st.text_input("Choose Password", type="password", key="new_signup_pass")
    confirm = st.text_input("Confirm Password", type="password", key="new_signup_confirm")

    if st.button("Create Account"):
        users = load_users()

        if username in users:
            st.warning("Username already exists. Please choose another.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        elif password != confirm:
            st.error("Passwords do not match. Try Again")
        else:
            save_user(username, password)
            st.success("Account created successfully! Please sign in.")
            st.session_state.page = "Sign In"



# Dashboard
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>🛡️ User Authentication</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("🔐 Sign In"):
                st.session_state.page = "Sign In"
        with btn2:
            if st.button("📝 Sign Up"):
                st.session_state.page = "Sign Up"

        st.write("---")
        if st.session_state.page == "Sign In":
            signin()
        else:
            signup()
    st.stop()


# after login
st.sidebar.success(f"✅ Logged in as {st.session_state.username}")
st.title(f"👋 Welcome, {st.session_state.username}")
st.write("You are now logged in!")


# Logout
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "Sign In"
    st.rerun()



st.title("📈 Stock Market Prediction Simulator")

# fie uploader
upload_file=st.file_uploader("Upload your stock CSV file (Date, Close)",type=["csv"])
if upload_file:
    df=pd.read_csv(upload_file)
else:
    df=pd.read_csv("sample_stock.csv")

#line chart
df['Date']=pd.to_datetime(df['Date'])
df.set_index('Date',inplace=True)
st.subheader("📉 Historical Stock Data")
st.line_chart(df['Close'])

#sidebar
st.sidebar.header("🔧 Simulation Settings")
days=st.sidebar.slider("Days to simulate",30,365,90)
runs=st.sidebar.slider("Number of simulation runs", 100, 1000, 500)

#simulations
last_price=df['Close'].iloc[-1]
returns=df['Close'].pct_change().dropna()
mu=returns.mean()
sigma=returns.std()

simulatedpath=[]
for run in range(runs):
    prices=[last_price]
    for d in range(days):
        next_prices=prices[-1]*(1+np.random.normal(mu,sigma))
        prices.append(next_prices)
        simulatedpath.append(prices)

#simulations result
final_prices=[path[-1] for path in simulatedpath]
gains=sum(1 for price in final_prices if price>last_price)
losses=sum(1 for price in final_prices if price<=last_price)

#piechart
st.header("🥧 Gain vs Loss After Simulation")
lables=['Gain','Loss']
size=[gains,losses]
colors=['lightgreen', 'salmon']

fig, ax=plt.subplots()
ax.pie(size,labels=lables,colors=colors,autopct='%1.1f%%',startangle=90)
ax.axis('equal')
plt.tight_layout()
st.pyplot(fig)

#final day distribution
final_prices = [path[-1] for path in simulatedpath]
st.subheader("📊 Final Price Distribution")
fig2, ax2 = plt.subplots()
ax2.hist(final_prices, bins=30, color='orange', edgecolor='black')
ax2.axvline(np.mean(final_prices), color='red', linestyle='--', label='Mean')
ax2.set_title("Histogram of Final Prices")
ax2.legend()
st.pyplot(fig2)

st.success(f"Average predicted price after {days} and:  ₹{np.mean(final_prices):.2f} ")
