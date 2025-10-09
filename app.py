import streamlit as st
import pandas as pd
import os
import time
from pathlib import Path

# ==================== CONFIG ==================== #
st.set_page_config(page_title="Student Material Portal", page_icon="🎓", layout="wide")

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
SUGGESTIONS_FILE = BASE_DIR / "suggestions.csv"
MATERIALS_FILE = BASE_DIR / "materials.csv"

UPLOAD_FOLDER.mkdir(exist_ok=True)

# Ensure CSVs exist
if not SUGGESTIONS_FILE.exists():
    pd.DataFrame(columns=["Course", "Semester", "Year", "Subject", "Suggestion", "Timestamp", "Completed"]).to_csv(SUGGESTIONS_FILE, index=False)

if not MATERIALS_FILE.exists():
    pd.DataFrame(columns=["Filename", "Course", "Semester", "Year", "Subject", "Type", "Uploader", "Path"]).to_csv(MATERIALS_FILE, index=False)

# ==================== HELPERS ==================== #
def save_file(uploaded_file, course, semester, year, subject, file_type):
    folder_path = UPLOAD_FOLDER / course / semester / year / subject / file_type
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)

def delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        return False

def save_suggestion(course, semester, year, subject, suggestion):
    df = pd.read_csv(SUGGESTIONS_FILE)
    new_entry = {
        "Course": course,
        "Semester": semester,
        "Year": year,
        "Subject": subject,
        "Suggestion": suggestion,
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "Completed": False
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(SUGGESTIONS_FILE, index=False)

# ==================== SIDEBAR ==================== #
st.sidebar.title("🎓 Navigation")
choice = st.sidebar.radio("Go to:", ["Student Dashboard", "Admin Dashboard"])
st.sidebar.markdown("---")

# ==================== STUDENT DASHBOARD ==================== #
if choice == "Student Dashboard":
    st.title("🎓 Student Dashboard")

    course_options = sorted(["BSc Physical Science", "BCom (hons.)", "Bcom (Prog.)", "BA (hons.)", "BA (Prog.)"])
    subject_options = ["All", "Hindi", "English", "Maths", "Physics", "Computer Science",
                       "Political Science", "History", "Geography", "AEC", "DSE", "SEC", "VAC", "GE"]

    course = st.selectbox("Select Course", ["All"] + course_options)
    semester = st.selectbox("Select Semester", ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"])
    year = st.selectbox("Select Year", ["All", "2023", "2024", "2025"])
    subject = st.selectbox("Select Subject", subject_options)

    if st.button("🔍 Search Materials"):
        if MATERIALS_FILE.exists():
            df = pd.read_csv(MATERIALS_FILE)

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
                    with open(row["Path"], "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download {row['Filename']}",
                            data=f,
                            file_name=row["Filename"],
                            key=row["Path"]
                        )
            else:
                st.warning("No matching files found.")
        else:
            st.warning("No materials available yet.")

    st.markdown("---")
    st.markdown("### 💬 Suggestion Box")
    suggestion_text = st.text_area("Enter your query or suggestion:")
    if st.button("📨 Submit Suggestion"):
        if suggestion_text.strip():
            save_suggestion(course, semester, year, subject, suggestion_text.strip())
            st.success("✅ Your suggestion has been sent to the admin!")
        else:
            st.warning("Please write something before submitting.")

# ==================== ADMIN DASHBOARD ==================== #
elif choice == "Admin Dashboard":
    st.title("🧑‍💻 Admin Dashboard")

    admin_password = st.text_input("Enter admin password:", type="password")
    if admin_password != "admin123":
        st.warning("Enter the correct admin password to continue.")
        st.stop()

    st.success("Welcome, Admin! ✅")
    st.markdown("---")

    # ---------- Upload Section ----------
    st.subheader("📤 Upload New Material")
    uploaded_file = st.file_uploader("Choose a file")
    course = st.selectbox("Course", sorted(["BSc Physical Science", "BCom (hons.)", "Bcom (Prog.)", "BA (hons.)", "BA (Prog.)"]))
    semester = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th"])
    year = st.selectbox("Year", ["2023", "2024", "2025"])
    subject = st.selectbox("Subject", ["Hindi", "English", "Maths", "Physics", "Computer Science",
                                       "Political Science", "History", "Geography", "AEC", "DSE", "SEC", "VAC", "GE"])
    file_type = st.selectbox("Type", ["Notes", "PYQ", "Books"])
    uploader_name = st.text_input("👤 Uploaded by (Author / Teacher Name)", placeholder="Enter uploader name")

    if st.button("Upload"):
        if uploaded_file and uploader_name.strip():
            saved_path = save_file(uploaded_file, course, semester, year, subject, file_type)
            df = pd.read_csv(MATERIALS_FILE)
            new_entry = {
                "Filename": os.path.basename(saved_path),
                "Course": course,
                "Semester": semester,
                "Year": year,
                "Subject": subject,
                "Type": file_type,
                "Uploader": uploader_name.strip(),
                "Path": saved_path
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(MATERIALS_FILE, index=False)
            st.success(f"✅ File uploaded successfully by {uploader_name.strip()}")
        else:
            st.warning("Please select a file and enter uploader name.")

    st.markdown("---")

    # ---------- Uploaded Materials Section ----------
    st.subheader("📘 Uploaded Materials")
    if MATERIALS_FILE.exists():
        materials_df = pd.read_csv(MATERIALS_FILE)
        if not materials_df.empty:
            st.dataframe(materials_df[['Filename', 'Course', 'Semester', 'Year', 'Subject', 'Type', 'Uploader']])
            st.markdown("### 🗑️ Delete Uploaded Material")
            filename_to_delete = st.selectbox("Select file to delete", materials_df['Filename'].tolist())
            if st.button("Confirm Delete"):
                file_path = materials_df.loc[materials_df['Filename'] == filename_to_delete, 'Path'].values[0]
                if delete_file(file_path):
                    materials_df = materials_df[materials_df['Filename'] != filename_to_delete]
                    materials_df.to_csv(MATERIALS_FILE, index=False)
                    st.success(f"✅ Deleted {filename_to_delete}")
                    st.rerun()
                else:
                    st.error("Could not delete file.")
        else:
            st.info("No uploaded materials yet.")
    else:
        st.info("No uploaded materials found.")

    st.markdown("---")

    # ---------- Suggestions Section ----------
    st.subheader("💬 Student Suggestions / Queries")
    df = pd.read_csv(SUGGESTIONS_FILE)

    def _to_bool(x):
        if isinstance(x, bool):
            return x
        if pd.isna(x):
            return False
        s = str(x).strip().lower()
        return s in ("true", "1", "yes", "y", "t")

    if "Completed" in df.columns:
        df["Completed"] = df["Completed"].apply(_to_bool)
    else:
        df["Completed"] = False

    if df.empty:
        st.info("No suggestions submitted yet.")
    else:
        filter_choice = st.radio("👁️ Show Suggestions:", ["All", "Pending Only", "Completed Only"], horizontal=True)

        if filter_choice == "Pending Only":
            filtered_df = df[df["Completed"] == False].copy()
        elif filter_choice == "Completed Only":
            filtered_df = df[df["Completed"] == True].copy()
        else:
            filtered_df = df.copy()

        filtered_df = filtered_df.reset_index().rename(columns={"index": "orig_index"})

        for _, row in filtered_df.iterrows():
            orig_idx = int(row["orig_index"])
            with st.expander(f"🕒 {row['Timestamp']} — {row['Course']} | {row['Semester']} | {row['Year']} | {row['Subject']}"):
                st.write(f"**Suggestion:** {row['Suggestion']}")
                completed = st.checkbox("✅ Mark as Completed", value=bool(row["Completed"]), key=f"comp_{orig_idx}")
                delete_btn = st.button("🗑️ Delete", key=f"del_{orig_idx}")

                if completed != bool(row["Completed"]):
                    df.loc[orig_idx, "Completed"] = bool(completed)
                    df.to_csv(SUGGESTIONS_FILE, index=False)
                    st.success("✅ Updated status!")
                    st.rerun()

                if delete_btn:
                    df = df.drop(index=orig_idx).reset_index(drop=True)
                    df.to_csv(SUGGESTIONS_FILE, index=False)
                    st.success("🗑️ Deleted suggestion successfully!")
                    st.rerun()
