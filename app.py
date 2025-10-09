import streamlit as st
import os
import datetime
import uuid
import pandas as pd

# ----------------------------
# BASIC SETUP
# ----------------------------
st.set_page_config(page_title="College PYQ & Notes Portal", page_icon="📚", layout="wide")

# Disable typing in selectboxes (students can only click)
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

UPLOAD_FOLDER = "uploads"
SUGGESTIONS_FILE = "suggestions.csv"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(SUGGESTIONS_FILE):
    pd.DataFrame(columns=["Timestamp", "Course", "Semester", "Year", "Subject", "Suggestion", "Completed"]).to_csv(SUGGESTIONS_FILE, index=False)

ADMIN_USERNAME = "nish20"
ADMIN_PASSWORD = "45009Ni"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# ----------------------------
# FUNCTIONS
# ----------------------------
def save_file(uploaded_file, course, semester, year, subject, file_type):
    safe_course = course.replace(" ", "_")
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


def list_files(course=None, semester=None, year=None, subject=None):
    all_files = []
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, UPLOAD_FOLDER)
            parts = rel_path.split(os.sep)

            if len(parts) >= 4:
                c, s, y = parts[0], parts[1], parts[2]
                fname = parts[3]

                subject_name = "Unknown"
                ftype = "Unknown"
                if "_" in fname:
                    split_name = fname.split("_")
                    subject_name = split_name[0]
                    if len(split_name) > 1:
                        ftype = split_name[1]

                if (
                    (not course or c == course)
                    and (not semester or s == semester)
                    and (not year or y == year)
                    and (not subject or subject_name == subject)
                ):
                    all_files.append((c, s, y, subject_name, ftype, fname, file_path))
    return all_files


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        dir_path = os.path.dirname(file_path)
        while dir_path != UPLOAD_FOLDER and not os.listdir(dir_path):
            os.rmdir(dir_path)
            dir_path = os.path.dirname(dir_path)
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
# SEARCH MATERIALS (STUDENT)
# ----------------------------
elif choice == "Search Materials":
    st.subheader("🎓 Search or Browse Materials")

    course_options = sorted(["BSc Physical Science", "BCom (hons.)", "Bcom (Prog.)", "BA (hons.)", "BA (Prog.)"])
    subject_options = ["All", "Hindi", "English", "Maths", "Physics", "Computer Science",
                       "Political Science", "History", "Geography", "AEC", "DSE", "SEC", "VAC", "GE"]

    course = st.selectbox("Select Course", ["All"] + course_options)
    semester = st.selectbox("Select Semester", ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"])
    year = st.selectbox("Select Year", ["All", "2023", "2024", "2025"])
    subject = st.selectbox("Select Subject", subject_options)

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
                None if year == "All" else year,
                None if subject == "All" else subject,
            )

        if files:
            st.markdown("### 📚 Available Materials:")
            for c, s, y, sub, typ, fname, fpath in files:
                st.write(f"**📄 {fname}** — {c}, Sem {s}, Year {y}, Subject: {sub}, Type: {typ}")
                with open(fpath, "rb") as f:
                    st.download_button(label="⬇️ Download", data=f, file_name=fname, key=fpath)
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
        subject = st.selectbox("Subject", ["Hindi", "English", "Maths", "Physics", "Computer Science",
                                           "Political Science", "History", "Geography", "AEC", "DSE", "SEC", "VAC", "GE"])
        file_type = st.selectbox("Type", ["Notes", "PYQ", "Books"])

        if st.button("Upload"):
            if uploaded_file and course and semester and year and subject and file_type:
                try:
                    saved_path = save_file(uploaded_file, course, semester, year, subject, file_type)
                    st.success(f"✅ File uploaded successfully: {saved_path}")
                except Exception as e:
                    st.error(f"Error saving file: {e}")
            else:
                st.error("Please fill all fields and select a file.")

        st.markdown("---")
        st.markdown("### 📂 Uploaded Materials")

        files = list_files()
        if files:
            df = pd.DataFrame(files, columns=['Course', 'Semester', 'Year', 'Subject', 'Type', 'Filename', 'Path'])
            st.dataframe(df[['Course', 'Semester', 'Year', 'Subject', 'Type', 'Filename']])
        else:
            st.info("No files uploaded yet.")

        st.markdown("---")
        st.markdown("### 📨 Student Suggestions / Queries")

        suggestions_df = pd.read_csv(SUGGESTIONS_FILE)

        if suggestions_df.empty:
            st.info("No suggestions submitted yet.")
        else:
            filter_choice = st.radio(
                "👁️ Show Suggestions:",
                ["All", "Pending Only", "Completed Only"],
                horizontal=True
            )

            if filter_choice == "Pending Only":
                filtered_df = suggestions_df[suggestions_df["Completed"] == False].copy()
            elif filter_choice == "Completed Only":
                filtered_df = suggestions_df[suggestions_df["Completed"] == True].copy()
            else:
                filtered_df = suggestions_df.copy()

            filtered_df = filtered_df.reset_index()  # retain original index

            for _, row in filtered_df.iterrows():
                idx = row["index"]  # true index in CSV
                with st.expander(f"🕒 {row['Timestamp']} — {row['Course']} | {row['Semester']} | {row['Year']} | {row['Subject']}"):
                    st.write(f"**Suggestion:** {row['Suggestion']}")
                    completed = st.checkbox("✅ Mark as Completed", value=row["Completed"], key=f"comp_{idx}")
                    delete_btn = st.button("🗑️ Delete", key=f"del_{idx}")

                    if completed != row["Completed"]:
                        df = pd.read_csv(SUGGESTIONS_FILE)
                        df.at[idx, "Completed"] = completed
                        df.to_csv(SUGGESTIONS_FILE, index=False)
                        st.success("✅ Updated status!")
                        st.rerun()

                    if delete_btn:
                        df = pd.read_csv(SUGGESTIONS_FILE)
                        df = df.drop(index=idx).reset_index(drop=True)
                        df.to_csv(SUGGESTIONS_FILE, index=False)
                        st.success("🗑️ Deleted suggestion successfully!")
                        st.rerun()
