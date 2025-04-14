import tkinter as tk
from tkinter import messagebox
import sqlite3

# ==========================
# Question Class
# ==========================
class Question:
    def __init__(self, question_text, options, correct_answer):
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer

    def validate_answer(self, selected_answer):
        return selected_answer == self.correct_answer

# ==========================
# Database Operations
# ==========================
def connect_db():
    return sqlite3.connect("college_courses.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    courses = [
        "PrinciplesOfMarketing",
        "BusinessStatistics1",
        "BusinessDatabaseManagement",
        "BusinessApplicationsDevelopment",
        "ManagementOfInformationSystems"
    ]
    for course in courses:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {course} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_option TEXT
            )
        ''')
    conn.commit()
    conn.close()

def add_question(course, question_text, options, correct_answer):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {course} (question, option_a, option_b, option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (question_text, options[0], options[1], options[2], options[3], correct_answer))
    conn.commit()
    conn.close()

def get_all_questions(course):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT question, option_a, option_b, option_c, option_d, correct_option FROM {course}")
    rows = cursor.fetchall()
    questions = [Question(row[0], [row[1], row[2], row[3], row[4]], row[5]) for row in rows]
    conn.close()
    return questions

# ==========================
# GUI Application
# ==========================
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Quiz Application")
        self.logged_in = False
        self.current_score = 0
        self.course = ""
        self.quiz_questions = []
        self.current_question_idx = 0

        create_tables()
        self.login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_screen(self):
        self.clear_screen()
        self.root.geometry("400x300")

        self.admin_password = tk.Entry(self.root, width=30, show="*")

        tk.Label(self.root, text="Enter Admin Password:").pack(pady=10)
        self.admin_password.pack(pady=5)

        tk.Button(self.root, text="Login as Admin", command=self.admin_login).pack(pady=10)
        tk.Button(self.root, text="Take Quiz", command=self.select_course).pack(pady=10)

    def admin_login(self):
        if self.admin_password.get() == "admin":
            self.logged_in = True
            self.admin_dashboard()
        else:
            messagebox.showerror("Error", "Incorrect password")

    def admin_dashboard(self):
        self.clear_screen()
        self.root.geometry("600x400")

        tk.Label(self.root, text="Admin Dashboard", font=("Helvetica", 18)).pack(pady=20)
        tk.Button(self.root, text="Add Question", command=self.add_question_form).pack(pady=10)
        tk.Button(self.root, text="View Questions", command=self.view_questions).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.login_screen).pack(pady=10)

    def add_question_form(self):
        self.clear_screen()
        self.root.geometry("600x500")

        tk.Label(self.root, text="Add Question", font=("Helvetica", 18)).pack(pady=20)

        tk.Label(self.root, text="Select Course:").pack()
        self.course_select = tk.StringVar(self.root)
        self.course_select.set("PrinciplesOfMarketing")
        course_options = [
            "PrinciplesOfMarketing", "BusinessStatistics1", "BusinessDatabaseManagement",
            "BusinessApplicationsDevelopment", "ManagementOfInformationSystems"
        ]
        tk.OptionMenu(self.root, self.course_select, *course_options).pack(pady=5)

        self.question_text = tk.Entry(self.root, width=50)
        self.option_a = tk.Entry(self.root, width=50)
        self.option_b = tk.Entry(self.root, width=50)
        self.option_c = tk.Entry(self.root, width=50)
        self.option_d = tk.Entry(self.root, width=50)

        for label, entry in zip(["Question", "Option A", "Option B", "Option C", "Option D"],
                                [self.question_text, self.option_a, self.option_b, self.option_c, self.option_d]):
            tk.Label(self.root, text=label + ":").pack()
            entry.pack(pady=2)

        tk.Label(self.root, text="Correct Answer (A/B/C/D):").pack()
        self.correct_answer = tk.StringVar(self.root)
        self.correct_answer.set("A")
        tk.OptionMenu(self.root, self.correct_answer, "A", "B", "C", "D").pack(pady=5)

        tk.Button(self.root, text="Add Question", command=self.submit_new_question).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.admin_dashboard).pack(pady=5)

    def submit_new_question(self):
        try:
            add_question(
                self.course_select.get(),
                self.question_text.get(),
                [self.option_a.get(), self.option_b.get(), self.option_c.get(), self.option_d.get()],
                self.correct_answer.get()
            )
            messagebox.showinfo("Success", "Question added successfully!")
            self.admin_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_questions(self):
        self.clear_screen()
        self.root.geometry("600x400")

        tk.Label(self.root, text="Select Course to View Questions").pack(pady=10)
        self.course_select = tk.StringVar(self.root)
        self.course_select.set("PrinciplesOfMarketing")
        course_options = [
            "PrinciplesOfMarketing", "BusinessStatistics1", "BusinessDatabaseManagement",
            "BusinessApplicationsDevelopment", "ManagementOfInformationSystems"
        ]
        tk.OptionMenu(self.root, self.course_select, *course_options).pack(pady=5)

        tk.Button(self.root, text="Show Questions", command=self.display_questions).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.admin_dashboard).pack(pady=10)

    def display_questions(self):
        self.clear_screen()
        course = self.course_select.get()
        questions = get_all_questions(course)

        tk.Label(self.root, text=f"Questions for {course}", font=("Helvetica", 16)).pack(pady=10)

        for i, q in enumerate(questions):
            tk.Label(self.root, text=f"{i+1}. {q.question_text}").pack(anchor='w')

        tk.Button(self.root, text="Back", command=self.view_questions).pack(pady=10)

    def select_course(self):
        self.clear_screen()
        self.root.geometry("400x300")
        tk.Label(self.root, text="Select Course to Start Quiz", font=("Helvetica", 16)).pack(pady=20)
        self.course_select = tk.StringVar(self.root)
        self.course_select.set("PrinciplesOfMarketing")
        course_options = [
            "PrinciplesOfMarketing", "BusinessStatistics1", "BusinessDatabaseManagement",
            "BusinessApplicationsDevelopment", "ManagementOfInformationSystems"
        ]
        tk.OptionMenu(self.root, self.course_select, *course_options).pack(pady=10)
        tk.Button(self.root, text="Start Quiz", command=self.start_quiz).pack(pady=20)

    def start_quiz(self):
        self.course = self.course_select.get()
        self.quiz_questions = get_all_questions(self.course)
        self.current_question_idx = 0
        self.current_score = 0
        if self.quiz_questions:
            self.show_question(self.quiz_questions[self.current_question_idx])
        else:
            messagebox.showinfo("No Questions", "This course has no questions yet.")
            self.select_course()

    def show_question(self, question):
        self.clear_screen()
        self.root.geometry("600x400")
        tk.Label(self.root, text=question.question_text, font=("Helvetica", 14)).pack(pady=20)
        self.selected_option = tk.StringVar()
        options = question.options
        for i, label in enumerate(["A", "B", "C", "D"]):
            tk.Radiobutton(
                self.root,
                text=options[i],
                variable=self.selected_option,
                value=label
            ).pack(anchor="w")
        tk.Button(self.root, text="Submit Answer", command=self.submit_answer).pack(pady=20)

    def submit_answer(self):
        selected_answer = self.selected_option.get()
        question = self.quiz_questions[self.current_question_idx]

        if question.validate_answer(selected_answer):
            self.current_score += 1
            messagebox.showinfo("Correct!", "Your answer is correct!")
        else:
            messagebox.showinfo("Incorrect", f"Wrong answer. Correct was: {question.correct_answer}")

        self.current_question_idx += 1
        if self.current_question_idx < len(self.quiz_questions):
            self.show_question(self.quiz_questions[self.current_question_idx])
        else:
            messagebox.showinfo("Quiz Finished", f"Your Score: {self.current_score}/{len(self.quiz_questions)}")
            self.select_course()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
