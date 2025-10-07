import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import datetime
import shutil
import uuid
import subprocess
import sys


DB_NAME = "college_materials.db"
UPLOAD_FOLDER = "uploads"


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            semester TEXT,
            year TEXT,
            subject TEXT,
            type TEXT,
            file_path TEXT,
            uploaded_on TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    c.execute("INSERT OR IGNORE INTO admins VALUES ('admin', 'admin123')")
    c.execute("INSERT OR IGNORE INTO courses (course_name) VALUES ('BSc Physical Science with Computer Science')")
    c.execute("INSERT OR IGNORE INTO courses (course_name) VALUES ('BCA')")
    c.execute("INSERT OR IGNORE INTO courses (course_name) VALUES ('BCom')")
    c.execute("INSERT OR IGNORE INTO courses (course_name) VALUES ('BA')")
    conn.commit()
    conn.close()


class CollegeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 College PYQ & Notes Portal")
        self.geometry("1000x650")
        self.configure(bg="#f8f9fa")
        self.selected_file_path = None
        self.admin_logged_in = False
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, pady=10)
        self.create_login_tab()
        self.create_student_tab()


    def create_login_tab(self):
        self.login_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.login_tab, text="🧑‍💻 Admin Login")
        self.login_frame = ttk.LabelFrame(self.login_tab, text="Admin Login", padding=20)
        self.login_frame.pack(pady=30)
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        self.admin_user_entry = ttk.Entry(self.login_frame, width=25)
        self.admin_user_entry.grid(row=0, column=1, pady=5)
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        self.admin_pass_entry = ttk.Entry(self.login_frame, width=25, show="*")
        self.admin_pass_entry.grid(row=1, column=1, pady=5)
        ttk.Button(self.login_frame, text="Login", command=self.verify_admin).grid(row=2, column=0, columnspan=2, pady=15)


    def create_admin_dashboard(self):
        if hasattr(self, 'admin_dashboard'):
            self.notebook.forget(self.admin_dashboard)
        self.admin_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_dashboard, text="🧑‍💻 Admin Dashboard")
        self.notebook.select(self.admin_dashboard)
        ttk.Button(self.admin_dashboard, text="Logout", command=self.logout_admin).pack(anchor="ne", pady=5, padx=10)


        upload_frame = ttk.LabelFrame(self.admin_dashboard, text="Upload Material", padding=15)
        upload_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(upload_frame, text="Course:").grid(row=0, column=0, padx=5, pady=5)
        self.upload_course_combo = ttk.Combobox(upload_frame, values=self.get_courses(), width=30)
        self.upload_course_combo.grid(row=0, column=1, padx=5)
        ttk.Label(upload_frame, text="Semester:").grid(row=0, column=2, padx=5)
        self.upload_sem_combo = ttk.Combobox(upload_frame, values=["1st","2nd","3rd","4th","5th","6th","7th","8th"], width=10)
        self.upload_sem_combo.grid(row=0, column=3, padx=5)
        ttk.Label(upload_frame, text="Year:").grid(row=1, column=0, padx=5)
        self.upload_year_combo = ttk.Combobox(upload_frame, values=["2022","2023","2024","2025","2026"], width=15)
        self.upload_year_combo.grid(row=1, column=1, padx=5)
        ttk.Label(upload_frame, text="Subject:").grid(row=1, column=2, padx=5)
        self.upload_sub_combo = ttk.Combobox(upload_frame, width=25)
        self.upload_sub_combo.grid(row=1, column=3, padx=5)
        self.upload_course_combo.bind("<<ComboboxSelected>>", self.update_subjects_list)
        self.upload_sem_combo.bind("<<ComboboxSelected>>", self.update_subjects_list)
        self.upload_year_combo.bind("<<ComboboxSelected>>", self.update_subjects_list)
        ttk.Label(upload_frame, text="Type:").grid(row=2, column=0, padx=5)
        self.upload_type_combo = ttk.Combobox(upload_frame, values=["Notes","PYQ","Other"], width=15)
        self.upload_type_combo.grid(row=2, column=1, padx=5)
        btn_frame = ttk.Frame(upload_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)
        ttk.Button(btn_frame, text="📂 Select File", command=self.select_file).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="⬆️ Upload File", command=self.upload_material).grid(row=0, column=1, padx=10)
        self.file_label = ttk.Label(upload_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=4, column=0, columnspan=4)


        materials_frame = ttk.LabelFrame(self.admin_dashboard, text="Uploaded Materials", padding=15)
        materials_frame.pack(padx=10, pady=10, fill="both", expand=True)
        columns = ("ID","Course","Subject","Type","Semester","Year","Uploaded On","File Path")
        self.admin_result_table = ttk.Treeview(materials_frame, columns=columns, show="headings")
        self.admin_result_table.heading("ID", text="ID")
        self.admin_result_table.column("ID", width=0, stretch=False)
        for col in columns[1:-1]:
            self.admin_result_table.heading(col, text=col)
            self.admin_result_table.column(col, width=125)
        self.admin_result_table.heading("File Path", text="File Path")
        self.admin_result_table.column("File Path", width=0, stretch=False)
        self.admin_result_table.pack(fill="both", expand=True, pady=10)
        ttk.Button(materials_frame, text="🗑️ Delete Selected Material", command=self.admin_delete_selected).pack(pady=5)
        self.admin_result_table.bind("<Double-1>", self.on_double_click_delete)
        self.load_admin_materials()


    def remove_admin_dashboard(self):
        if hasattr(self, 'admin_dashboard'):
            self.notebook.forget(self.admin_dashboard)
            del self.admin_dashboard


    def update_subjects_list(self, event=None):
        course = self.upload_course_combo.get().strip()
        semester = self.upload_sem_combo.get().strip()
        year = self.upload_year_combo.get().strip()
        if not all([course, semester, year]):
            self.upload_sub_combo["values"] = []
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT subject FROM materials m
            JOIN courses c ON m.course_id=c.id
            WHERE c.course_name=? AND m.semester=? AND m.year=?
        """, (course, semester, year))
        subjects = [row[0] for row in c.fetchall()]
        conn.close()
        self.upload_sub_combo["values"] = subjects


    def verify_admin(self):
        user = self.admin_user_entry.get().strip()
        pwd = self.admin_pass_entry.get().strip()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username=? AND password=?", (user, pwd))
        result = c.fetchone()
        conn.close()
        if result:
            messagebox.showinfo("Login Successful ✅", f"Welcome, {user}!")
            self.admin_logged_in = True
            self.create_admin_dashboard()
            self.notebook.hide(self.login_tab)
        else:
            messagebox.showerror("Invalid Credentials", "Incorrect username or password.")


    def logout_admin(self):
        self.remove_admin_dashboard()
        self.admin_logged_in = False
        self.notebook.add(self.login_tab, text="🧑‍💻 Admin Login")
        self.notebook.select(self.login_tab)
        self.admin_user_entry.delete(0, tk.END)
        self.admin_pass_entry.delete(0, tk.END)


    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
            self.selected_file_path = file_path
            self.file_label.config(text=f"Selected: {os.path.basename(file_path)}", foreground="green")


    def upload_material(self):
        if not self.selected_file_path:
            messagebox.showerror("Error", "Please select a file before uploading.")
            return
        if not os.path.exists(self.selected_file_path):
            messagebox.showerror("Error", f"File not found:\n{self.selected_file_path}\nPlease select a different file.")
            self.selected_file_path = None
            self.file_label.config(text="No file selected", foreground="gray")
            return
        course = self.upload_course_combo.get().strip()
        semester = self.upload_sem_combo.get().strip()
        year = self.upload_year_combo.get().strip()
        subject = self.upload_sub_combo.get().strip()
        mat_type = self.upload_type_combo.get().strip()
        if not all([course, semester, year, subject, mat_type]):
            messagebox.showerror("Error", "Please fill all fields before uploading.")
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id FROM courses WHERE course_name=?", (course,))
            result = c.fetchone()
            if not result:
                c.execute("INSERT INTO courses (course_name) VALUES (?)", (course,))
                conn.commit()
                c.execute("SELECT id FROM courses WHERE course_name=?", (course,))
                result = c.fetchone()
            cid = result[0]
            c.execute("""
                SELECT COUNT(*) FROM materials m JOIN courses c ON m.course_id=c.id
                WHERE c.course_name=? AND m.semester=? AND m.year=? AND LOWER(m.subject)=? AND m.type=?
            """, (course, semester, year, subject.lower(), mat_type))
            count = c.fetchone()[0]
            if count > 0:
                messagebox.showerror("Duplicate Entry", "This material already exists.")
                conn.close()
                return
            ext = os.path.splitext(self.selected_file_path)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            dest_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            shutil.copy2(self.selected_file_path, dest_path)
            uploaded_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("""
                INSERT INTO materials (course_id, semester, year, subject, type, file_path, uploaded_on)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cid, semester, year, subject, mat_type, dest_path, uploaded_on))
            conn.commit()
            conn.close()
            messagebox.showinfo("✅ Upload Successful", f"File '{os.path.basename(dest_path)}' uploaded.")
            self.selected_file_path = None
            self.file_label.config(text="No file selected", foreground="gray")
            self.upload_sub_combo.set('')
            self.upload_type_combo.set('')
            self.upload_course_combo["values"] = self.get_courses()
            self.update_subjects_list()
            self.load_admin_materials()
            self.search_materials()
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")


    def load_admin_materials(self):
        if not hasattr(self, 'admin_result_table'):
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT m.id, c.course_name, m.subject, m.type, m.semester, m.year, m.uploaded_on, m.file_path
            FROM materials m
            JOIN courses c ON m.course_id = c.id
            ORDER BY m.uploaded_on DESC
        """)
        rows = c.fetchall()
        conn.close()
        for item in self.admin_result_table.get_children():
            self.admin_result_table.delete(item)
        for row in rows:
            self.admin_result_table.insert("", tk.END, values=row)


    def on_double_click_delete(self, event):
        selected = self.admin_result_table.selection()
        if not selected:
            return
        answer = messagebox.askyesno("Confirm Delete", "Delete selected material?")
        if answer:
            self.admin_delete_selected()


    def admin_delete_selected(self):
        selected = self.admin_result_table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a material to delete.")
            return
        material_id = self.admin_result_table.item(selected[0])["values"][0]
        try:
            file_path = self.admin_result_table.item(selected[0])["values"][-1]
            # Only delete from uploads folder, never original user locations
            if os.path.commonpath([os.path.abspath(file_path), os.path.abspath(UPLOAD_FOLDER)]) == os.path.abspath(UPLOAD_FOLDER):
                if os.path.exists(file_path):
                    os.remove(file_path)
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM materials WHERE id=?", (material_id,))
            conn.commit()
            conn.close()
            self.admin_result_table.delete(selected[0])
            messagebox.showinfo("Deleted", "Material deleted from the application.")
            self.search_materials()
            self.load_admin_materials()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")


    def get_courses(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in c.fetchall()]
        conn.close()
        return courses


    def create_student_tab(self):
        student_tab = ttk.Frame(self.notebook)
        self.notebook.add(student_tab, text="🎓 Student / Visitor")
        ttk.Label(student_tab, text="📖 Search Materials", font=("Arial", 14, "bold")).pack(pady=10)
        filter_frame = ttk.Frame(student_tab)
        filter_frame.pack(pady=5)
        ttk.Label(filter_frame, text="Course:").grid(row=0, column=0, padx=5)
        self.search_course_combo = ttk.Combobox(filter_frame, values=self.get_courses(), width=25, state="readonly")
        self.search_course_combo.grid(row=0, column=1)
        ttk.Label(filter_frame, text="Semester:").grid(row=0, column=2, padx=5)
        self.search_sem_combo = ttk.Combobox(filter_frame, values=["1st","2nd","3rd","4th","5th","6th","7th","8th"], width=10, state="readonly")
        self.search_sem_combo.grid(row=0, column=3)
        ttk.Label(filter_frame, text="Year:").grid(row=0, column=4, padx=5)
        self.search_year_combo = ttk.Combobox(filter_frame, values=["2022","2023","2024","2025","2026"], width=15, state="readonly")
        self.search_year_combo.grid(row=0, column=5)
        ttk.Label(filter_frame, text="Type:").grid(row=0, column=6, padx=5)
        self.filter_type_combo = ttk.Combobox(filter_frame, values=["All","Notes","PYQ","Other"], width=10, state="readonly")
        self.filter_type_combo.current(0)
        self.filter_type_combo.grid(row=0, column=7)
        ttk.Label(filter_frame, text="Search Subject:").grid(row=1, column=0, padx=5, pady=5)
        # Changed from Entry to Combobox, state readonly
        self.subject_search_combo = ttk.Combobox(filter_frame, width=30, state="readonly")
        self.subject_search_combo.grid(row=1, column=1, columnspan=3, padx=5)
        ttk.Button(filter_frame, text="🔍 Search", command=self.search_materials).grid(row=1, column=4, padx=5)

        # Bind changes to update subjects dynamically
        self.search_course_combo.bind("<<ComboboxSelected>>", self.update_student_subjects)
        self.search_sem_combo.bind("<<ComboboxSelected>>", self.update_student_subjects)
        self.search_year_combo.bind("<<ComboboxSelected>>", self.update_student_subjects)

        table_frame = ttk.Frame(student_tab)
        table_frame.pack(pady=15, fill="both", expand=True)
        columns = ("Subject","Type","Semester","Year","File Path","Uploaded On")
        self.result_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, width=140)
        self.result_table.pack(fill="both", expand=True)

        # Buttons frame with Download and View buttons only (Open button removed)
        button_frame = ttk.Frame(student_tab)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="⬇️ Download Selected File", command=self.download_selected_file).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="👁️ View Selected File", command=self.view_selected_file).grid(row=0, column=1, padx=5)

        # Load all materials by default
        self.search_materials()


    def update_student_subjects(self, event=None):
        course = self.search_course_combo.get().strip()
        semester = self.search_sem_combo.get().strip()
        year = self.search_year_combo.get().strip()
        if not all([course, semester, year]):
            self.subject_search_combo["values"] = []
            self.subject_search_combo.set('')
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT subject FROM materials m
            JOIN courses c ON m.course_id=c.id
            WHERE c.course_name=? AND m.semester=? AND m.year=?
        """, (course, semester, year))
        subjects = [row[0] for row in c.fetchall()]
        conn.close()
        self.subject_search_combo["values"] = subjects
        self.subject_search_combo.set('')


    def search_materials(self):
        course = self.search_course_combo.get().strip()
        semester = self.search_sem_combo.get().strip()
        year = self.search_year_combo.get().strip()
        mat_type = self.filter_type_combo.get().strip()
        subject = self.subject_search_combo.get().strip().lower()  # changed here to combobox value
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = """
            SELECT m.subject, m.type, m.semester, m.year, m.file_path, m.uploaded_on
            FROM materials m
            JOIN courses c2 ON m.course_id = c2.id
            WHERE 1=1
        """
        params = []
        if course:
            query += " AND c2.course_name LIKE ?"
            params.append(f"%{course}%")
        if semester:
            query += " AND m.semester LIKE ?"
            params.append(f"%{semester}%")
        if year:
            query += " AND m.year LIKE ?"
            params.append(f"%{year}%")
        if mat_type and mat_type != "All":
            query += " AND m.type=?"
            params.append(mat_type)
        if subject:
            query += " AND LOWER(m.subject) LIKE ?"
            params.append(f"%{subject}%")
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        for item in self.result_table.get_children():
            self.result_table.delete(item)
        for row in rows:
            self.result_table.insert("", tk.END, values=row)


    def download_selected_file(self):
        selected = self.result_table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a file to download.")
            return
        file_path = self.result_table.item(selected[0])["values"][4]
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found on the server.")
            return
        dest = filedialog.asksaveasfilename(
            initialfile=os.path.basename(file_path),
            title="Save File As"
        )
        if dest:
            try:
                shutil.copy2(file_path, dest)
                messagebox.showinfo("Downloaded", f"File saved to: {dest}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download file:\n{e}")


    def view_selected_file(self):
        selected = self.result_table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a file to view.")
            return
        file_path = self.result_table.item(selected[0])["values"][4]
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found on your system.")
            return
        try:
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(('open', file_path))
            elif os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Linux
                subprocess.call(('xdg-open', file_path))
            else:
                messagebox.showerror("Error", "Unsupported OS.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")


if __name__ == "__main__":
    init_db()
    app = CollegeApp()
    app.mainloop()
