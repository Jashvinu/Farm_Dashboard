import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Set page configuration with wide layout
st.set_page_config(page_title="Stall Management System", layout="wide")

# Custom CSS for styling using purple and yellow theme
st.markdown("""
    <style>
        /* Background and text colors for the main app */
        .stApp {
            background-color: #7e57c2;  /* Purple background */
            color: white;
            font-size: 30px;  /* Increase font size for general text */
        }
        /* Sidebar styling */
        .css-1v3fvcr {
            background-color: #5e35b1 !important;  /* Darker purple for sidebar */
        }
        .css-1v3fvcr .css-1d391kg {
            color: #d4af37 !important;  /* Yellow text in the sidebar */
            font-size: 30px !important;  /* Increase sidebar text size */
        }
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {
            color: #d4af37 !important;  /* Yellow headings */
            font-size: 24px !important;  /* Increase font size for headings */
        }
        /* Button styling */
        .stButton button {
            background-color: #ffeb3b;  /* Yellow buttons */
            color: #5e35b1;  /* Purple text on buttons */
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            font-size: 20px;  /* Larger font size for buttons */
        }
        .stButton button:hover {
            background-color: #d4af37;  /* Darker yellow on hover */
            color: white;
        }
        /* Dataframe styling */
        .stDataFrame {
            background-color: #b39ddb;  /* Lighter purple for dataframes */
            font-size: 18px;  /* Increase font size for data in dataframes */
        }
    </style>
""", unsafe_allow_html=True)



# Replace with your actual API endpoint
API_ENDPOINT = "https://stall-management.vercel.app/api"

# Helper function to get menu items from API
def get_menu_items():
    try:
        response = requests.get(f"{API_ENDPOINT}/inventory")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching menu items: {str(e)}")
        return []

# Helper function to get user info from API
def get_user_info(rfid):
    try:
        response = requests.get(f"{API_ENDPOINT}/user/getUser/{rfid}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching user info: {str(e)}")
        return None

# Helper function to process transaction
def process_transaction(rfid, items, total_amount):
    payload = {
        "RFID": rfid,
        "items": items
    }
    try:
        response = requests.post(f"{API_ENDPOINT}/user/purchase", json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get('message') == "Purchase successful":
            return True, result
        else:
            st.error(f"Transaction failed: {result.get('error', 'Unknown error')}")
            return False, None
    except requests.RequestException as e:
        st.error(f"Error processing transaction: {str(e)}")
        return False, None

# Helper function to poll for RFID
def poll_for_rfid():
    max_attempts = 60  # Adjust this value to set maximum polling time
    for _ in range(max_attempts):
        try:
            response = requests.get(f"{API_ENDPOINT}/latest-rfid")
            response.raise_for_status()
            data = response.json()
            if 'rfidCode' in data and data['rfidCode'] is not None:
                return data['rfidCode']
        except requests.RequestException:
            pass
        time.sleep(1)  # Poll every second
    return None 

# Helper function to delete RFID from server
def delete_rfid():
    try:
        response = requests.delete(f"{API_ENDPOINT}/rfid")
        response.raise_for_status()
    except requests.RequestException:
        pass

# Section 1: Add User
def show_add_user():
    st.header("Add User")
    st.write("Form to add a new user will go here.")
    # Add a sample form for demonstration
    with st.form("add_user_form"):
        name = st.text_input("Name")
        rfid = st.text_input("RFID")
        balance = st.number_input("Initial Balance", min_value=0)
        submitted = st.form_submit_button("Add User")
        if submitted:
            st.success(f"User {name} with RFID {rfid} and balance ${balance} added.")

# Section 2: Inventory Management
def show_inventory():
    st.header("Inventory")
    menu_items = get_menu_items()
    if menu_items:
        df = pd.DataFrame(menu_items)
        st.dataframe(df)

# Section 3: Billing
def show_billing():
    st.header("Billing")
    menu_items = get_menu_items()
    selected_items = []
    total_amount = 0

    for item in menu_items:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"{item['name']} - ${item['price']:.2f}")
        quantity = col2.number_input(f"Qty for {item['name']}", min_value=0, max_value=item['stock'], step=1, key=item['_id'])
        if quantity > 0:
            selected_items.append({"inventory_id": item['_id'], "quantity": quantity})
            total_amount += item['price'] * quantity

    st.write(f"Total Amount: ${total_amount:.2f}")

    if st.button("Proceed to Checkout"):
        if not selected_items:
            st.warning("Please select items to purchase")
        else:
            st.session_state.checkout_stage = 'scan_card'

    if 'checkout_stage' in st.session_state and st.session_state.checkout_stage == 'scan_card':
        st.info("Please scan your card now...")
        with st.spinner("Waiting for card scan..."):
            rfid = poll_for_rfid()
        
        if rfid:
            st.success(f"Card scanned successfully: {rfid}")
            delete_rfid()
            st.session_state.scanned_rfid = rfid
            st.session_state.checkout_stage = 'confirm_purchase'
        else:
            st.error("Card scan failed. Please try again.")
            del st.session_state.checkout_stage

    if 'checkout_stage' in st.session_state and st.session_state.checkout_stage == 'confirm_purchase':
        user_info = get_user_info(st.session_state.scanned_rfid)
        if user_info:
            st.write(f"Username: {user_info['userName']}")
            st.write(f"Balance: ${user_info['Balance']:.2f}")
        else:
            st.error("User not found")

        if st.button("Confirm Purchase"):
            success, result = process_transaction(st.session_state.scanned_rfid, selected_items, total_amount)
            if success:
                st.success(f"""
                Purchase Successful!
                Total Amount: ${result['totalAmount']:.2f}
                New Balance: ${result['newBalance']:.2f}
                Thank you for your purchase!
                """)
                del st.session_state.checkout_stage
                del st.session_state.scanned_rfid
                if st.button("Return to Main Menu"):
                    st.rerun()
            else:
                st.error("Purchase failed. Please try again.")

# Section 4: Dashboard
def show_dashboard():
    st.header("Dashboard")
    st.write("Overview of system performance will go here.")

# Sidebar-based table of contents for navigation
st.sidebar.title("Table of Contents")
section = st.sidebar.radio(
    "Navigate to", 
    ("Add User", "Inventory", "Billing", "Dashboard")
)

# Display the selected section
if section == "Add User":
    show_add_user()
elif section == "Inventory":
    show_inventory()
elif section == "Billing":
    show_billing()
elif section == "Dashboard":
    show_dashboard()

# Footer
st.sidebar.markdown("---")
st.sidebar.write("© 2024 Stall Management System")
