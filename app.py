import streamlit as st
from chatUI import chatbot_ui_page
from SpearHead_Library import spearhead_library

# Configuration
st.set_page_config(page_title="Squire", page_icon="ASSETS/pixel_pencil.png", layout='wide')

# Load user data from st.secrets
USERS = {user["username"]: {"password": user["password"], "is_admin": user["is_admin"]} for user in st.secrets["users"]}

def is_admin(username):
    return USERS.get(username, {}).get("is_admin", False)

def main():
    st.sidebar.title("Navigation")

    if "current_user" not in st.session_state:
        username = st.sidebar.text_input("Username:")
        password = st.sidebar.text_input("Password:", type="password")
        
        if st.sidebar.button("Login"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state["current_user"] = username
                st.sidebar.success(f"Logged in as {username}")
            else:
                st.sidebar.error("Invalid credentials")
        return

    selection = st.sidebar.radio("Go to", ["Brain_Storm", "Spear_Head_Library"])
    
    if selection == "Brain_Storm":
        chatbot_ui_page()
    elif selection == "Spear_Head_Library":
        spearhead_library()

if __name__ == "__main__":
    main()
