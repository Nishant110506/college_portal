import streamlit as st
import os
import shutil
import datetime
import uuid


# ----------------------------
# BASIC SETUP
# ----------------------------
st.set_page_config(page_title="College PYQ & Notes Portal", page_icon="📚", layout="wide")

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ADMIN_USERNAME = "nish20"
ADMIN_PASSWORD = "45009Ni"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# ----------------------------
# FUNCTIONS
# ----------------------------
def save_file(uploaded_file, course, semester, year, subject, file_type):
    """Save uploaded file with structured naming."""
    safe_course = course.replace(" ", "_").replace("\\", "_").replace("/", "_")
    safe_semester = semester.replace(" ", "_")
    safe_year = year.replace(" ", "_")
    safe_subject = subject.replace(" ", "_")
    safe_type = file_type.replace(" ", "_")

    folder_path = os.path.join(UPLOAD_FOLDER, safe_course, safe_semester, safe_year)
    os.makedirs(folder_path, exist_ok=True)

    unique_name = f"{safe_subject}_{safe_type}_{uuid.uuid4().hex}{os.path.splitext(uploaded_file.name)[1]}"
    file_path = os.path.join(folder_path, unique_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def list_files(course=None, semester=None, year=None):
    """List uploaded files filtered by course, semester, year."""
    all_files = []
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, UPLOAD_FOLDER)
            parts = rel_path.split(os.sep)
            if len(parts) >= 4:
                c, s, y, fname = parts[0], parts[1], parts[2], parts[3]
                if (not course or c == course) and (not semester or s == semester) and (not year or y == year):
                    all_files.append((c, s, y, fname, file_path))
    return all_files


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        # Remove empty folders up to UPLOAD_FOLDER
        dir_path = os.path.dirname(file_path)
        while dir_path != UPLOAD_FOLDER and not os.listdir(dir_path):
            os.rmdir(dir_path)
            dir_path = os.path.dirname(dir_path)
        return True
    return False


# ----------------------------
# HEADER
# ----------------------------
st.markdown("<h1 style='text-align:center;'>📚 College PYQ & Notes Portal</h1>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# SIDEBAR NAVIGATION
# ----------------------------
menu = ["Home", "Search Materials", "Admin Login", "Admin Dashboard"]
choice = st.sidebar.radio("Navigation", menu)


# ----------------------------
# HOME
# ----------------------------
if choice == "Home":
    st.image("https://cdn-icons-png.flaticon.com/512/4228/4228813.png", width=120)
    st.markdown("### Welcome to the College Portal")
    st.write("Upload, view, and search for PYQs and notes easily!")
    st.info("Use the sidebar to navigate between student and admin sections.")


# ----------------------------
# SEARCH MATERIALS
# ----------------------------
elif choice == "Search Materials":
    st.subheader("🎓 Search or Browse Materials")

    course_options = sorted([d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))])
    course = st.selectbox("Select Course (optional)", ["All"] + course_options)
    semester = st.selectbox("Select Semester (optional)", ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"])
    year = st.selectbox("Select Year (optional)", ["All", "2023", "2024", "2025"])

    col1, col2 = st.columns(2)
    with col1:
        search_btn = st.button("🔍 Search")
    with col2:
        show_all = st.button("📂 Show All Files")

    if search_btn or show_all:
        if show_all:
            files = list_files()
        else:
            files = list_files(
                None if course == "All" else course,
                None if semester == "All" else semester,
                None if year == "All" else year
            )

        if files:
            st.markdown("### 📚 Available Materials:")
            for c, s, y, fname, fpath in files:
                st.write(f"**📄 {fname}** — {c}, Sem {s}, Year {y}")
                with open(fpath, "rb") as f:
                    st.download_button(label="⬇️ Download", data=f, file_name=fname, key=fpath)
        else:
            st.warning("No files found.")


# ----------------------------
# ADMIN LOGIN
# ----------------------------
elif choice == "Admin Login":
    st.subheader("🧑‍💻 Admin Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Login successful!")
            st.rerun
        else:
            st.error("Invalid credentials")


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
elif choice == "Admin Dashboard":
    if not st.session_state.admin_logged_in:
        st.error("Please login as admin to access this section.")
    else:
        st.success(f"Welcome Admin 👋 ({ADMIN_USERNAME})")

        if st.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.success("You have been logged out.")
            st.experimental_rerun()

        st.markdown("### ⬆️ Upload New Material")

        uploaded_file = st.file_uploader("Choose a file")
        course = st.selectbox("Course", sorted([d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))] + ["BSc", "BCA", "BCom", "BA"]))
        semester = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th"])
        year = st.selectbox("Year", ["2023", "2024", "2025"])
        subject = st.text_input("Subject")
        file_type = st.selectbox("Type", ["Notes", "PYQ", "Other"])

        if st.button("Upload"):
            if uploaded_file and course and semester and year and subject and file_type:
                try:
                    saved_path = save_file(uploaded_file, course, semester, year, subject, file_type)
                    st.success(f"File uploaded successfully: {saved_path}")
                except Exception as e:
                    st.error(f"Error saving file: {e}")
            else:
                st.error("Please fill all fields and select a file.")

        st.markdown("---")
        st.markdown("### 📂 Uploaded Materials")

        files = list_files()
        if files:
            for c, s, y, fname, fpath in files:
                st.write(f"**{fname}** — {c}, Sem {s}, Year {y}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"Delete {fname}", key=f"del_{fpath}"):
                        if delete_file(fpath):
                            st.success(f"Deleted {fname}")
                            st.rerun
                        else:
                            st.error(f"Failed to delete {fname}")
                with col2:
                    with open(fpath, "rb") as f:
                        st.download_button(label="⬇️ Download", data=f, file_name=fname, key=f"dl_{fpath}")
        else:
            st.info("No files uploaded yet.")
