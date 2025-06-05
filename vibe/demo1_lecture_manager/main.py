import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import csv

DB_PATH = 'db.sqlite3'
MATERIALS_DIR = 'materials'
TEACHERS_DUMMY = 'teachers_dummy.csv'
LECTURES_DUMMY = 'lectures_dummy.csv'

# DB 초기화 함수
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 교원 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS teacher (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dept TEXT,
        contact TEXT
    )''')
    # 강의 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS lecture (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        day TEXT,
        time TEXT,
        room TEXT,
        teacher_id INTEGER,
        FOREIGN KEY(teacher_id) REFERENCES teacher(id)
    )''')
    # 강의자료 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS lecture_material (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lecture_id INTEGER,
        filename TEXT,
        filepath TEXT,
        uploaded_at TEXT,
        FOREIGN KEY(lecture_id) REFERENCES lecture(id)
    )''')
    conn.commit()
    # 더미데이터 자동 입력
    c.execute('SELECT COUNT(*) FROM teacher')
    if c.fetchone()[0] == 0 and os.path.exists(TEACHERS_DUMMY):
        with open(TEACHERS_DUMMY, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                c.execute('INSERT INTO teacher (name, dept, contact) VALUES (?, ?, ?)',
                          (row['이름'], row['소속'], row['연락처']))
        conn.commit()
    c.execute('SELECT COUNT(*) FROM lecture')
    if c.fetchone()[0] == 0 and os.path.exists(LECTURES_DUMMY):
        with open(LECTURES_DUMMY, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                c.execute('INSERT INTO lecture (subject, day, time, room, teacher_id) VALUES (?, ?, ?, ?, ?)',
                          (row['과목명'], row['요일'], row['시간'], row['강의실'], int(row['담당교원ID'])))
        conn.commit()
    conn.close()
    if not os.path.exists(MATERIALS_DIR):
        os.makedirs(MATERIALS_DIR)

# Tkinter 기본 창
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('교원 강의 관리 시스템')
        self.geometry('1100x650')
        
        # 탭 구조
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        
        # 교원 관리 탭
        self.teacher_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.teacher_tab, text='교원 관리')
        self.create_teacher_tab()
        
        # 강의 관리 탭
        self.lecture_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.lecture_tab, text='강의 관리')
        self.create_lecture_tab()

    def create_teacher_tab(self):
        frame = self.teacher_tab
        # 리스트(교원 목록)
        self.teacher_tree = ttk.Treeview(frame, columns=('id', 'name', 'dept', 'contact'), show='headings')
        self.teacher_tree.heading('id', text='ID')
        self.teacher_tree.heading('name', text='이름')
        self.teacher_tree.heading('dept', text='소속')
        self.teacher_tree.heading('contact', text='연락처')
        self.teacher_tree.column('id', width=40)
        self.teacher_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.teacher_tree.bind('<<TreeviewSelect>>', self.on_teacher_select)
        
        # 입력 폼
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=5)
        ttk.Label(form_frame, text='이름').grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(form_frame, width=15)
        self.name_entry.grid(row=0, column=1, padx=5)
        ttk.Label(form_frame, text='소속').grid(row=0, column=2, padx=5)
        self.dept_entry = ttk.Entry(form_frame, width=15)
        self.dept_entry.grid(row=0, column=3, padx=5)
        ttk.Label(form_frame, text='연락처').grid(row=0, column=4, padx=5)
        self.contact_entry = ttk.Entry(form_frame, width=15)
        self.contact_entry.grid(row=0, column=5, padx=5)
        
        # 버튼
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='추가', command=self.add_teacher).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='수정', command=self.update_teacher).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='삭제', command=self.delete_teacher).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='새로고침', command=self.load_teachers).pack(side='left', padx=5)
        
        self.selected_teacher_id = None
        self.load_teachers()

    def load_teachers(self):
        for row in self.teacher_tree.get_children():
            self.teacher_tree.delete(row)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, dept, contact FROM teacher')
        for row in c.fetchall():
            self.teacher_tree.insert('', 'end', values=row)
        conn.close()
        self.clear_teacher_form()

    def add_teacher(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        contact = self.contact_entry.get().strip()
        if not name:
            messagebox.showerror('오류', '이름을 입력하세요.')
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO teacher (name, dept, contact) VALUES (?, ?, ?)', (name, dept, contact))
        conn.commit()
        conn.close()
        self.load_teachers()
        self.load_teacher_options()  # 강의 관리 탭 콤보박스 갱신

    def on_teacher_select(self, event):
        selected = self.teacher_tree.selection()
        if selected:
            values = self.teacher_tree.item(selected[0])['values']
            self.selected_teacher_id = values[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.dept_entry.delete(0, tk.END)
            self.dept_entry.insert(0, values[2])
            self.contact_entry.delete(0, tk.END)
            self.contact_entry.insert(0, values[3])

    def update_teacher(self):
        if not self.selected_teacher_id:
            messagebox.showwarning('알림', '수정할 교원을 선택하세요.')
            return
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        contact = self.contact_entry.get().strip()
        if not name:
            messagebox.showerror('오류', '이름을 입력하세요.')
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE teacher SET name=?, dept=?, contact=? WHERE id=?', (name, dept, contact, self.selected_teacher_id))
        conn.commit()
        conn.close()
        self.load_teachers()
        self.load_teacher_options()  # 강의 관리 탭 콤보박스 갱신

    def delete_teacher(self):
        if not self.selected_teacher_id:
            messagebox.showwarning('알림', '삭제할 교원을 선택하세요.')
            return
        if messagebox.askyesno('확인', '정말 삭제하시겠습니까?'):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('DELETE FROM teacher WHERE id=?', (self.selected_teacher_id,))
            conn.commit()
            conn.close()
            self.load_teachers()
            self.load_teacher_options()  # 강의 관리 탭 콤보박스 갱신

    def clear_teacher_form(self):
        self.selected_teacher_id = None
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)

    # ------------------- 강의 관리 탭 -------------------
    def create_lecture_tab(self):
        frame = self.lecture_tab
        self.lecture_tree = ttk.Treeview(frame, columns=('id', 'subject', 'day', 'time', 'room', 'teacher'), show='headings')
        self.lecture_tree.heading('id', text='ID')
        self.lecture_tree.heading('subject', text='과목명')
        self.lecture_tree.heading('day', text='요일')
        self.lecture_tree.heading('time', text='시간')
        self.lecture_tree.heading('room', text='강의실')
        self.lecture_tree.heading('teacher', text='담당교원')
        self.lecture_tree.column('id', width=40)
        self.lecture_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.lecture_tree.bind('<<TreeviewSelect>>', self.on_lecture_select)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=5)
        ttk.Label(form_frame, text='과목명').grid(row=0, column=0, padx=5)
        self.subject_entry = ttk.Entry(form_frame, width=15)
        self.subject_entry.grid(row=0, column=1, padx=5)
        ttk.Label(form_frame, text='요일').grid(row=0, column=2, padx=5)
        self.day_entry = ttk.Entry(form_frame, width=10)
        self.day_entry.grid(row=0, column=3, padx=5)
        ttk.Label(form_frame, text='시간').grid(row=0, column=4, padx=5)
        self.time_entry = ttk.Entry(form_frame, width=10)
        self.time_entry.grid(row=0, column=5, padx=5)
        ttk.Label(form_frame, text='강의실').grid(row=0, column=6, padx=5)
        self.room_entry = ttk.Entry(form_frame, width=10)
        self.room_entry.grid(row=0, column=7, padx=5)
        ttk.Label(form_frame, text='담당교원').grid(row=0, column=8, padx=5)
        self.teacher_option = ttk.Combobox(form_frame, width=15, state='readonly')
        self.teacher_option.grid(row=0, column=9, padx=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='추가', command=self.add_lecture).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='수정', command=self.update_lecture).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='삭제', command=self.delete_lecture).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='새로고침', command=self.load_lectures).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='자료 업로드', command=self.upload_material).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='자료 다운로드', command=self.download_material).pack(side='left', padx=5)
        # 시간표/시수/리포트 버튼
        ttk.Button(btn_frame, text='시간표 보기', command=self.show_timetable).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='PDF로 저장', command=self.save_pdf_report).pack(side='left', padx=5)
        
        self.selected_lecture_id = None
        self.load_teacher_options()
        self.load_lectures()

    def load_teacher_options(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name FROM teacher')
        teachers = c.fetchall()
        conn.close()
        self.teacher_option['values'] = [f"{tid}:{name}" for tid, name in teachers]
        if teachers:
            self.teacher_option.current(0)
        else:
            self.teacher_option.set('')

    def load_lectures(self):
        for row in self.lecture_tree.get_children():
            self.lecture_tree.delete(row)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT l.id, l.subject, l.day, l.time, l.room, t.name FROM lecture l LEFT JOIN teacher t ON l.teacher_id = t.id''')
        for row in c.fetchall():
            self.lecture_tree.insert('', 'end', values=row)
        conn.close()
        self.clear_lecture_form()

    def add_lecture(self):
        subject = self.subject_entry.get().strip()
        day = self.day_entry.get().strip()
        time = self.time_entry.get().strip()
        room = self.room_entry.get().strip()
        teacher_val = self.teacher_option.get()
        if not subject:
            messagebox.showerror('오류', '과목명을 입력하세요.')
            return
        teacher_id = int(teacher_val.split(':')[0]) if teacher_val else None
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO lecture (subject, day, time, room, teacher_id) VALUES (?, ?, ?, ?, ?)',
                  (subject, day, time, room, teacher_id))
        conn.commit()
        conn.close()
        self.load_lectures()

    def on_lecture_select(self, event):
        selected = self.lecture_tree.selection()
        if selected:
            values = self.lecture_tree.item(selected[0])['values']
            self.selected_lecture_id = values[0]
            self.subject_entry.delete(0, tk.END)
            self.subject_entry.insert(0, values[1])
            self.day_entry.delete(0, tk.END)
            self.day_entry.insert(0, values[2])
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, values[3])
            self.room_entry.delete(0, tk.END)
            self.room_entry.insert(0, values[4])
            # 담당교원 콤보박스 값 설정
            for i, val in enumerate(self.teacher_option['values']):
                if val.endswith(f":{values[5]}"):
                    self.teacher_option.current(i)
                    break

    def update_lecture(self):
        if not self.selected_lecture_id:
            messagebox.showwarning('알림', '수정할 강의를 선택하세요.')
            return
        subject = self.subject_entry.get().strip()
        day = self.day_entry.get().strip()
        time = self.time_entry.get().strip()
        room = self.room_entry.get().strip()
        teacher_val = self.teacher_option.get()
        if not subject:
            messagebox.showerror('오류', '과목명을 입력하세요.')
            return
        teacher_id = int(teacher_val.split(':')[0]) if teacher_val else None
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE lecture SET subject=?, day=?, time=?, room=?, teacher_id=? WHERE id=?',
                  (subject, day, time, room, teacher_id, self.selected_lecture_id))
        conn.commit()
        conn.close()
        self.load_lectures()

    def delete_lecture(self):
        if not self.selected_lecture_id:
            messagebox.showwarning('알림', '삭제할 강의를 선택하세요.')
            return
        if messagebox.askyesno('확인', '정말 삭제하시겠습니까?'):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('DELETE FROM lecture WHERE id=?', (self.selected_lecture_id,))
            conn.commit()
            conn.close()
            self.load_lectures()

    def clear_lecture_form(self):
        self.selected_lecture_id = None
        self.subject_entry.delete(0, tk.END)
        self.day_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.room_entry.delete(0, tk.END)
        self.teacher_option.set('')

    # ------------------- 강의자료 업로드/다운로드 -------------------
    def upload_material(self):
        if not self.selected_lecture_id:
            messagebox.showwarning('알림', '자료를 첨부할 강의를 선택하세요.')
            return
        file_path = filedialog.askopenfilename(title='첨부할 파일 선택')
        if not file_path:
            return
        filename = os.path.basename(file_path)
        dest_path = os.path.join(MATERIALS_DIR, f"{self.selected_lecture_id}_{filename}")
        try:
            shutil.copy(file_path, dest_path)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO lecture_material (lecture_id, filename, filepath, uploaded_at) VALUES (?, ?, ?, ?)',
                      (self.selected_lecture_id, filename, dest_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
            messagebox.showinfo('성공', '자료가 업로드되었습니다.')
        except Exception as e:
            messagebox.showerror('오류', f'업로드 실패: {e}')

    def download_material(self):
        if not self.selected_lecture_id:
            messagebox.showwarning('알림', '자료를 다운로드할 강의를 선택하세요.')
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, filename, filepath FROM lecture_material WHERE lecture_id=? ORDER BY uploaded_at DESC', (self.selected_lecture_id,))
        materials = c.fetchall()
        conn.close()
        if not materials:
            messagebox.showinfo('알림', '첨부된 자료가 없습니다.')
            return
        # 가장 최근 자료 1개만 다운로드(확장 가능)
        mat_id, filename, filepath = materials[0]
        save_path = filedialog.asksaveasfilename(title='저장할 위치 선택', initialfile=filename)
        if not save_path:
            return
        try:
            shutil.copy(filepath, save_path)
            messagebox.showinfo('성공', '자료가 저장되었습니다.')
        except Exception as e:
            messagebox.showerror('오류', f'다운로드 실패: {e}')

    # ------------------- 시간표/시수/리포트 -------------------
    def show_timetable(self):
        # DB에서 강의 전체 조회
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT l.subject, l.day, l.time, l.room, t.name FROM lecture l LEFT JOIN teacher t ON l.teacher_id = t.id''')
        lectures = c.fetchall()
        conn.close()
        # 요일/시간별 정렬
        lectures_sorted = sorted(lectures, key=lambda x: (x[1], x[2]))
        # 교원별 강의 시수 집계
        teacher_hours = {}
        for lec in lectures:
            teacher = lec[4] if lec[4] else '미지정'
            teacher_hours[teacher] = teacher_hours.get(teacher, 0) + 1
        # 팝업 창에 시간표/시수 표시
        win = tk.Toplevel(self)
        win.title('시간표 및 강의 시수')
        text = tk.Text(win, width=90, height=25)
        text.pack(padx=10, pady=10)
        text.insert(tk.END, '[시간표]\n')
        text.insert(tk.END, '과목명 | 요일 | 시간 | 강의실 | 담당교원\n')
        text.insert(tk.END, '-'*60+'\n')
        for lec in lectures_sorted:
            text.insert(tk.END, f'{lec[0]:10} | {lec[1]:4} | {lec[2]:6} | {lec[3]:8} | {lec[4] or "-"}\n')
        text.insert(tk.END, '\n[교원별 강의 시수]\n')
        for t, cnt in teacher_hours.items():
            text.insert(tk.END, f'{t}: {cnt}회\n')
        text.config(state='disabled')

    def save_pdf_report(self):
        # DB에서 강의 전체 조회
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT l.subject, l.day, l.time, l.room, t.name FROM lecture l LEFT JOIN teacher t ON l.teacher_id = t.id''')
        lectures = c.fetchall()
        conn.close()
        lectures_sorted = sorted(lectures, key=lambda x: (x[1], x[2]))
        # 교원별 강의 시수 집계
        teacher_hours = {}
        for lec in lectures:
            teacher = lec[4] if lec[4] else '미지정'
            teacher_hours[teacher] = teacher_hours.get(teacher, 0) + 1
        # 파일 저장 경로
        save_path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')], title='PDF로 저장')
        if not save_path:
            return
        c = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4
        y = height - 40
        c.setFont('Helvetica-Bold', 16)
        c.drawString(40, y, '강의 시간표 및 교원별 강의 시수')
        y -= 30
        c.setFont('Helvetica', 11)
        c.drawString(40, y, '[시간표]')
        y -= 20
        c.setFont('Helvetica', 10)
        c.drawString(40, y, '과목명        요일    시간     강의실     담당교원')
        y -= 15
        c.line(40, y, width-40, y)
        y -= 10
        for lec in lectures_sorted:
            line = f'{lec[0]:10}  {lec[1]:4}  {lec[2]:6}  {lec[3]:8}  {lec[4] or "-"}'
            c.drawString(40, y, line)
            y -= 15
            if y < 80:
                c.showPage()
                y = height - 40
        y -= 10
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, '[교원별 강의 시수]')
        y -= 20
        c.setFont('Helvetica', 10)
        for t, cnt in teacher_hours.items():
            c.drawString(40, y, f'{t}: {cnt}회')
            y -= 15
            if y < 80:
                c.showPage()
                y = height - 40
        c.save()
        messagebox.showinfo('성공', 'PDF로 저장되었습니다!')

if __name__ == '__main__':
    init_db()
    app = MainApp()
    app.mainloop() 