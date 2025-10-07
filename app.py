import streamlit as st
import os

# --- App Title ---
st.set_page_config(page_title="College PYQ & Notes Portal", page_icon="📘", layout="centered")
st.title("📘 College PYQ & Notes Portal")
st.write("Welcome to the online portal for Previous Year Question Papers and Notes!")

# --- Navigation Tabs ---
page = st.sidebar.radio("Go to", ["🏠 Home", "📤 Upload Materials", "🔍 Search Materials", "🔐 Admin Login"])

# --- Upload Section ---
if page == "📤 Upload Materials":
    st.header("📤 Upload and View Materials")
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "png", "jpg"])
    if uploaded_file is not None:
        with open(os.path.join(upload_folder, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ '{uploaded_file.name}' uploaded successfully!")

    st.subheader("Uploaded Files:")
    for file in os.listdir(upload_folder):
        st.write("📄", file)

# --- Search Section ---
elif page == "🔍 Search Materials":
    st.header("🔍 Search Materials")
    course = st.selectbox("Select Course", ["BCA", "BBA", "BTech"])
    semester = st.selectbox("Select Semester", [1, 2, 3, 4, 5, 6])
    year = st.selectbox("Select Year", [2021, 2022, 2023, 2024, 2025])

    if st.button("Search"):
        st.info(f"Showing results for {course} - Semester {semester} ({year})")
        st.write("🗂️ (Search results will be displayed here)")

# --- Admin Login Section ---
elif page == "🔐 Admin Login":
    st.header("🔐 Admin Login")
    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        if admin_user == "admin" and admin_pass == "1234":
            st.success("Welcome, Admin! 🎉 You are now logged in.")
            st.write("👉 Future features: Manage uploads, delete files, add notices, etc.")
        else:
            st.error("Invalid credentials! Please try again.")

# --- Home Page ---
else:
    st.header("🏠 Home")
    st.write("Use the sidebar to navigate through the portal.")
    st.markdown("""
    ### Features:
    - 📤 Upload and view materials  
    - 🔍 Search by course, semester, and year  
    - 🔐 Admin login (coming soon)
    """)
