import streamlit as st
import os
import datetime
import uuid
import pandas as pd
from pathlib import Path

# ----------------------------
# BASIC SETUP
# ----------------------------
st.set_page_config(page_title="College PYQ & Notes Portal", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    div[data-baseweb="select"] input {
        pointer-events: none;
    }
    div[data-baseweb="select"] input:focus {
        outline: none;
    }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = Path(".")
UPLOAD_FOLDER = BASE_DIR / "uploads"
SUGGESTIONS_FILE = BASE_DIR / "suggestions.csv"
SUBJECTS_FILE = BASE_DIR / "subjects.csv"
METADATA_FILE = BASE_DIR / "uploads_metadata.csv"

# Ensure required directories/files exist
UPLOAD_FOLDER.mkdir(exist_ok=True)

if not SUGGESTIONS_FILE.exists():
    pd.DataFrame(columns=["Timestamp", "Course", "Semester", "Year", "Subject", "Suggestion", "Completed"]).to_csv(SUGGESTIONS_FILE, index=False)

if not METADATA_FILE.exists():
    pd.DataFrame(columns=["Timestamp", "Course", "Semester", "Year", "Subject", "Type", "Filename", "Path", "Uploader"]).to_csv(METADATA_FILE, index=False)

default_subjects = [
    "Hindi", "English", "Maths", "Physics", "Computer Science",
    "Political Science", "History", "Geography", "AEC", "DSE", "SEC", "VAC", "GE"
]
if not SUBJECTS_FILE.exists():
    pd.DataFrame({"Subject": default_subjects}).to_csv(SUBJECTS_FILE, index=False)

ADMIN_USERNAME = "nish20"
ADMIN_PASSWORD = "45009Ni"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def save_file(uploaded_file, course, semester, year, subject, file_type, uploader):
    """Save the uploaded file and record its metadata."""
    safe_course = course.replace(" ", "_")
    safe_semester = semester.replace(" ", "_")
    safe_year = year.replace(" ", "_")
    safe_subject = subject.replace(" ", "_")
    safe_type = file_type.replace(" ", "_")

    folder_path = UPLOAD_FOLDER / safe_course / safe_semester / safe_year
    folder_path.mkdir(parents=True, exist_ok=True)

    unique_name = f"{safe_subject}_{safe_type}_{uuid.uuid4().hex}{os.path.splitext(uploaded_file.name)[1]}"
    file_path = folder_path / unique_name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Save metadata
    meta_df = pd.read_csv(METADATA_FILE)
    new_entry = {
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Course": course,
        "Semester": semester,
        "Year": year,
        "Subject": subject,
        "Type": file_type,
        "Filename": unique_name,
        "Path": str(file_path),
        "Uploader": uploader.strip() or "Unknown"
    }
    meta_df = pd.concat([meta_df, pd.DataFrame([new_entry])], ignore_index=True)
    meta_df.to_csv(METADATA_FILE, index=False)

    return file_path


def delete_file(file_path):
    """Delete the file and remove its metadata entry."""
    file_path = Path(file_path)
    if file_path.exists():
        file_path.unlink()
        # Remove metadata
        meta_df = pd.read_csv(METADATA_FILE)
        meta_df = meta_df[meta_df["Path"] != str(file_path)]
        meta_df.to_csv(METADATA_FILE, index=False)

        # Clean empty folders
        dir_path = file_path.parent
        while dir_path != UPLOAD_FOLDER and not any(dir_path.iterdir()):
            dir_path.rmdir()
            dir_path = dir_path.parent
        return True
    return False


def save_suggestion(course, semester, year, subject, suggestion):
    df = pd.read_csv(SUGGESTIONS_FILE)
    new_row = {
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Course": course,
        "Semester": semester,
        "Year": year,
        "Subject": subject,
        "Suggestion": suggestion,
        "Completed": False
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(SUGGESTIONS_FILE, index=False)


def update_suggestion_status(idx, completed):
    df = pd.read_csv(SUGGESTIONS_FILE)
    if 0 <= idx < len(df):
        df.at[idx, "Completed"] = bool(completed)
        df.to_csv(SUGGESTIONS_FILE, index=False)


def delete_suggestion(idx):
    df = pd.read_csv(SUGGESTIONS_FILE)
    if 0 <= idx < len(df):
        df = df.drop(index=idx)
        df.to_csv(SUGGESTIONS_FILE, index=False)


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
# HOME PAGE
# ----------------------------
if choice == "Home":
    st.image("https://cdn-icons-png.flaticon.com/512/4228/4228813.png", width=120)
    st.markdown("### Welcome to the College Portal")
    st.write("Upload, view, and search for PYQs and notes easily!")
    st.info("Use the sidebar to navigate between student and admin sections.")

# ----------------------------
# STUDENT SECTION
# ----------------------------
elif choice == "Search Materials":
    st.subheader("🎓 Search or Browse Materials")

    course_options = sorted(["BSc Physical Science", "BCom (hons.)", "Bcom (Prog.)", "BA (hons.)", "BA (Prog.)"])
    subject_df = pd.read_csv(SUBJECTS_FILE)
    subject_options = ["All"] + sorted(subject_df["Subject"].tolist())

    course = st.selectbox("Select Course", ["All"] + course_options)
    semester = st.selectbox("Select Semester", ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"])
    year = st.selectbox("Select Year", ["All", "2023", "2024", "2025"])
    subject = st.selectbox("Select Subject", subject_options)

    col1, col2 = st.columns(2)
    with col1:
        search_btn = st.button("🔍 Search")
    with col2:
        show_all = st.button("📂 Show All Files")

    meta_df = pd.read_csv(METADATA_FILE)

    if search_btn or show_all:
        df = meta_df.copy()
        if not show_all:
            if course != "All":
                df = df[df["Course"] == course]
            if semester != "All":
                df = df[df["Semester"] == semester]
            if year != "All":
                df = df[df["Year"] == year]
            if subject != "All":
                df = df[df["Subject"] == subject]

        if not df.empty:
            st.markdown("### 📘 Available Materials")
            st.dataframe(df[['Filename', 'Course', 'Semester', 'Year', 'Subject', 'Type', 'Uploader']])

            for _, row in df.iterrows():
                st.download_button(label=f"⬇️ Download {row['Filename']}",
                                   data=open(row["Path"], "rb"),
                                   file_name=row["Filename"],
                                   key=row["Path"])
        else:
            st.warning("No files found.")

    st.markdown("---")
    st.markdown("### 💬 Suggestion Box (For Students)")
    st.info("Submit your queries, issues, or suggestions to the admin here.")
    suggestion_text = st.text_area("Enter your suggestion or query here:")
    if st.button("📨 Submit Suggestion"):
        if suggestion_text.strip():
            save_suggestion(course, semester, year, subject, suggestion_text.strip())
            st.success("✅ Your suggestion has been sent to the admin!")
        else:
            st.warning("Please write something before submitting.")

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
            st.rerun()
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
            st.rerun()

        st.markdown("### ⬆️ Upload New Material")
        uploaded_file = st.file_uploader("Choose a file")
        course = st.selectbox("Course", sorted(["BSc Physical Science", "BCom (hons.)", "Bcom (Prog.)", "BA (hons.)", "BA (Prog.)"]))
        semester = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th"])
        year = st.selectbox("Year", ["2023", "2024", "2025"])
        uploader_name = st.text_input("👤 Enter your name (Uploader)", placeholder="e.g. Dr. Nishant Sharma")

        # SUBJECT MANAGEMENT
        st.markdown("### 📘 Subject Management")
        subject_df = pd.read_csv(SUBJECTS_FILE)
        subject_list = sorted(subject_df["Subject"].tolist())
        subject = st.selectbox("Select Subject", subject_list)

        with st.expander("➕ Add New Subject"):
            new_subject = st.text_input("Enter new subject name:")
            if st.button("Add Subject"):
                if new_subject.strip():
                    new_subject_clean = new_subject.strip().title()
                    if new_subject_clean not in subject_list:
                        subject_list.append(new_subject_clean)
                        pd.DataFrame({"Subject": sorted(subject_list)}).to_csv(SUBJECTS_FILE, index=False)
                        st.success(f"✅ Added '{new_subject_clean}' to subjects list!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Subject already exists.")
                else:
                    st.error("Please enter a valid subject name.")

        file_type = st.selectbox("Type", ["Notes", "PYQ", "Books"])

        if st.button("Upload"):
            if uploaded_file and uploader_name.strip() and course and semester and year and subject and file_type:
                try:
                    saved_path = save_file(uploaded_file, course, semester, year, subject, file_type, uploader_name)
                    st.success(f"✅ File uploaded successfully by {uploader_name}: {saved_path}")
                except Exception as e:
                    st.error(f"Error saving file: {e}")
            else:
                st.error("Please fill all fields and select a file (including uploader name).")

        # Uploaded Materials
        st.markdown("---")
        st.markdown("### 📘 Uploaded Materials")
        meta_df = pd.read_csv(METADATA_FILE)
        if not meta_df.empty:
            st.dataframe(meta_df[['Filename', 'Course', 'Semester', 'Year', 'Subject', 'Type', 'Uploader']])

            st.markdown("### 🗑️ Delete Uploaded Material")
            filename_to_delete = st.selectbox("Select file to delete", meta_df['Filename'].tolist())
            if st.button("Confirm Delete"):
                file_path = meta_df.loc[meta_df['Filename'] == filename_to_delete, 'Path'].values[0]
                if delete_file(file_path):
                    st.success(f"✅ Deleted {filename_to_delete}")
                    st.rerun()
                else:
                    st.error("Could not delete file.")
        else:
            st.info("No uploaded materials found.")

        # Suggestions Section
        st.markdown("---")
        st.markdown("### 📨 Student Suggestions / Queries")
        suggestions_df = pd.read_csv(SUGGESTIONS_FILE)
        if suggestions_df.empty:
            st.info("No suggestions submitted yet.")
        else:
            filter_choice = st.radio("👁️ Show Suggestions:", ["All", "Pending Only", "Completed Only"], horizontal=True)
            if filter_choice == "Pending Only":
                suggestions_df = suggestions_df[suggestions_df["Completed"] == False]
            elif filter_choice == "Completed Only":
                suggestions_df = suggestions_df[suggestions_df["Completed"] == True]

            for idx, row in suggestions_df.iterrows():
                with st.expander(f"🕒 {row['Timestamp']} — {row['Course']} | {row['Semester']} | {row['Year']} | {row['Subject']}"):
                    st.write(f"**Suggestion:** {row['Suggestion']}")
                    completed = st.checkbox("✅ Mark as Completed", value=bool(row["Completed"]), key=f"comp_{idx}")
                    delete_btn = st.button("🗑️ Delete", key=f"del_{idx}")

                    if completed != bool(row["Completed"]):
                        update_suggestion_status(idx, completed)
                        st.success("✅ Status updated successfully!")
                        st.rerun()

                    if delete_btn:
                        delete_suggestion(idx)
                        st.success("🗑️ Suggestion deleted successfully!")
                        st.rerun()
