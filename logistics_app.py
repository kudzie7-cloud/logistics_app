import streamlit as st
import pandas as pd
import sqlite3
import datetime

# Database setup and connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('fieldlist.db', check_same_thread=False)

conn = get_connection()
c = conn.cursor()

# Function to create the table if it doesn't exist
def initialize_database():
    c.execute('''
        CREATE TABLE IF NOT EXISTS field (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            product_name TEXT NOT NULL,
            date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            weight REAL NOT NULL,
            driver_name TEXT NOT NULL,
            truck TEXT NOT NULL,
            toll_fees REAL NOT NULL,
            food_costs REAL NOT NULL,
            amount_charged REAL NOT NULL,
            driver_due REAL NOT NULL,
            owner_due REAL NOT NULL
        )
    ''')
    conn.commit()

# Initialize the database
initialize_database()

# Function to load data from the database
def load_data():
    query = 'SELECT * FROM field'
    df = pd.read_sql(query, conn)
    return df

# Function to add data to the database
def add_to_db(source, destination, product_name, date, quantity, weight, driver_name, truck, toll_fees, food_costs, amount_charged):
    total_expenses = toll_fees + food_costs
    driver_due = 0.10 * (amount_charged - total_expenses)  # Driver gets 10% of net earnings
    owner_due = amount_charged - total_expenses - driver_due  # Owner gets the remaining amount

    # Debugging: Print the values being inserted into the database (visible only to admin and manager)
    if st.session_state["role"] in ["admin", "manager"]:
        st.write("**Debug: Inserting the following values into the database:**")
        st.write(f"Source: {source}, Destination: {destination}, Product Name: {product_name}, Date: {date}")
        st.write(f"Quantity: {quantity}, Weight: {weight}, Driver Name: {driver_name}, Truck: {truck}")
        st.write(f"Toll Fees: {toll_fees}, Food Costs: {food_costs}, Amount Charged: {amount_charged}")
        st.write(f"Driver Due: {driver_due}, Owner Due: {owner_due}")

    # Insert into the database
    c.execute('''
        INSERT INTO field (
            source, destination, product_name, date, quantity, weight,
            driver_name, truck, toll_fees, food_costs, amount_charged, driver_due, owner_due
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''',
        (source, destination, product_name, date, quantity, weight, driver_name, truck, toll_fees, food_costs, amount_charged, driver_due, owner_due))
    conn.commit()

# Custom CSS for beautifying the app
st.markdown("""
    <style>
    body {
        background-color: #f4f6f9;
        font-family: 'Poppins', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #1abc9c;
        color: white;
        border-radius: 12px;
        padding: 8px 20px;
    }
    .stButton>button:hover {
        background-color: #16a085;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #ecf0f1;
        border-radius: 10px;
        border: none;
    }
    .container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication and login system
def login():
    st.title('Kai Logistics Solutions - Login')
    
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if st.button('Login'):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = users[username]["role"]
            st.experimental_rerun()  # Refresh the app to reflect the login state
        else:
            st.error('Invalid username or password')

# Function to check if user is logged in
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
    return st.session_state["logged_in"]

# Function to log out
def logout():
    st.session_state.clear()  # Clear the entire session state
    st.experimental_rerun()  # Refresh to go back to the login page

# User credentials and roles
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "driver": {"password": "driver123", "role": "driver"},
    "manager": {"password": "manager123", "role": "manager"}
}

# Role-based access control
def role_based_access():
    role = st.session_state["role"]
    
    if role in ["admin", "manager", "driver"]:
        st.markdown("### 🚚 **Add a New Record**")
        with st.container():
            st.write("Fill in the details for the new logistics record.")
            col1, col2 = st.columns(2)
            with col1:
                source = st.text_input('Enter Source Location')
                destination = st.text_input('Enter Destination Location')
                product_name = st.text_input('Product Name')
            with col2:
                date = st.date_input('Date of Shipment')
                quantity = st.number_input('Quantity (件)', min_value=1)
                weight = st.number_input('Weight (KG)', min_value=1.0)

            # Additional Information (toll fees, food costs, and charges)
            st.markdown("---")
            st.markdown("### 📝 **Additional Information**")
            driver_name = st.text_input('Driver Name')
            truck = st.selectbox('Truck', options=['Benz', 'Volvo'])
            toll_fees = st.number_input('Toll Fees', min_value=0.0)
            food_costs = st.number_input('Food Costs', min_value=0.0)
            amount_charged = st.number_input('Amount Charged for the Trip', min_value=0.0)

            # Validation to ensure all fields are filled in before adding the record
            if not source or not destination or not product_name or not driver_name or not truck or amount_charged <= 0:
                st.warning("Please fill in all the fields before submitting.")
            else:
                # Automatic Calculations for Driver and Owner Dues
                total_expenses = toll_fees + food_costs
                driver_due = 0.10 * (amount_charged - total_expenses)
                owner_due = amount_charged - total_expenses - driver_due

                st.markdown("---")
                st.markdown("### 📄 **Calculated Dues**")
                st.write(f"**Driver Due:** {driver_due:.2f}")
                st.write(f"**Owner Due:** {owner_due:.2f}")

                # Button to add record to the database
                if st.button("Add Record"):
                    add_to_db(
                        source, 
                        destination, 
                        product_name, 
                        date.strftime('%Y-%m-%d'), 
                        quantity, 
                        weight, 
                        driver_name, 
                        truck, 
                        toll_fees, 
                        food_costs, 
                        amount_charged
                    )
                    st.success("Record added successfully!")

    # Only admin and manager can view records
    if role in ["admin", "manager"]:
        st.markdown("---")
        st.markdown("### 📊 **Data Dashboard**")
        st.write("View and export your data records.")
        with st.expander("View Records"):
            data = load_data()
            st.dataframe(data)
        
        if st.button("Export to Excel"):
            export_path = export_to_excel(data)
            st.success(f"Data exported to `{export_path}`!")

# Function to export data to Excel
def export_to_excel(df):
    export_path = 'exported_data.xlsx'
    df.to_excel(export_path, index=False)
    return export_path

# Main app logic
if check_login():
    st.sidebar.write(f'Logged in as **{st.session_state["username"]}** ({st.session_state["role"].capitalize()})')
    
    # Add a logout button in the sidebar
    if st.sidebar.button("Logout"):
        logout()
    
    # Handle role-based access
    role_based_access()
else:
    login()
