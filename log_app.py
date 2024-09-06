import streamlit as st
import streamlit_authenticator as stauth

# Define user credentials
credentials = {
    "usernames": {
        "driver1": {
            "name": "Driver One",
            "password": stauth.Hasher(["password1"]).generate()[0],  # Hashed password
        },
        "driver2": {
            "name": "Driver Two",
            "password": stauth.Hasher(["password2"]).generate()[0],  # Hashed password
        },
        "manager1": {
            "name": "Manager One",
            "password": stauth.Hasher(["password3"]).generate()[0],  # Hashed password
        }
    }
}

# Create the authenticator object without location or optional parameters
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="logistics_app",  # Optional
    cookie_key="some_random_secret_key",  # Optional
    cookie_expiry_days=1  # Optional
)

# Login form (without the location argument)
name, authentication_status, username = authenticator.login('Login')  # No location argument

# Dummy trip logs
trip_logs = []

# After successful authentication
if authentication_status:
    st.write(f'Welcome, {name}!')

    if username == "driver1" or username == "driver2":
        # Driver dashboard
        st.header("Driver Dashboard - Log Your Trip")
        start = st.text_input("Enter Starting Point")
        destination = st.text_input("Enter Destination")
        amount = st.number_input("Amount Charged", min_value=0.0)

        if st.button("Log Trip"):
            if start and destination:
                trip_logs.append({
                    "driver": name,
                    "start": start,
                    "destination": destination,
                    "amount": amount
                })
                st.success(f"Trip logged for {name}!")
            else:
                st.error("Enter both starting point and destination.")

    elif username == "manager1":
        # Manager dashboard
        st.header("Manager Dashboard")
        if trip_logs:
            st.write(trip_logs)
        else:
            st.write("No trips logged yet.")

# If login fails
elif authentication_status == False:
    st.error("Incorrect username or password")

# If login is not attempted yet
elif authentication_status == None:
    st.warning("Please enter your username and password")
