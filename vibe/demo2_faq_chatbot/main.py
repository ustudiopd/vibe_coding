import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import csv

DB_PATH = 'faq_chatbot.db'
FAQ_DUMMY = 'faq_dummy.csv'

# NLTK 토크나이저 다운로드(최초 1회)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # FAQ 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )''')
    # 답변 이력 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_question TEXT,
        matched_question TEXT,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    # FAQ 더미데이터 자동 입력
    c.execute('SELECT COUNT(*) FROM faq')
    if c.fetchone()[0] == 0 and os.path.exists(FAQ_DUMMY):
        with open(FAQ_DUMMY, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                c.execute('INSERT INTO faq (question, answer) VALUES (?, ?)', (row['질문'], row['답변']))
        conn.commit()
    conn.close()

class FAQChatbotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('FAQ 챗봇 시스템')
        self.geometry('700x600')
        self.resizable(False, False)
        self.create_widgets()
        self.load_faq_data()

    def create_widgets(self):
        # 챗봇 대화창
        self.chat_text = tk.Text(self, height=25, width=80, state='disabled')
        self.chat_text.pack(padx=10, pady=10)
        # 질문 입력
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=5)
        self.user_entry = ttk.Entry(input_frame, width=60)
        self.user_entry.pack(side='left', padx=5)
        self.user_entry.bind('<Return>', lambda e: self.ask_question())
        ttk.Button(input_frame, text='질문하기', command=self.ask_question).pack(side='left', padx=5)
        # 답변 이력 보기 버튼
        ttk.Button(self, text='답변 이력 보기', command=self.show_history).pack(pady=5)

    def load_faq_data(self):
        # DB에서 FAQ 전체 불러오기
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query('SELECT * FROM faq', conn)
        conn.close()
        self.questions = df['question'].tolist()
        self.answers = df['answer'].tolist()
        # TF-IDF 벡터화
        self.vectorizer = TfidfVectorizer(tokenizer=nltk.word_tokenize)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)

    def ask_question(self):
        user_q = self.user_entry.get().strip()
        if not user_q:
            return
        self.user_entry.delete(0, tk.END)
        self.append_chat(f'사용자: {user_q}')
        # 유사도 기반 답변 찾기
        user_vec = self.vectorizer.transform([user_q])
        sims = cosine_similarity(user_vec, self.tfidf_matrix)[0]
        best_idx = sims.argmax()
        best_score = sims[best_idx]
        if best_score > 0.3:
            matched_q = self.questions[best_idx]
            answer = self.answers[best_idx]
            self.append_chat(f'챗봇: {answer}')
        else:
            matched_q = ''
            answer = '죄송합니다. 해당 질문에 대한 답변을 찾지 못했습니다.'
            self.append_chat(f'챗봇: {answer}')
        # 답변 이력 저장
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO history (user_question, matched_question, answer) VALUES (?, ?, ?)',
                  (user_q, matched_q, answer))
        conn.commit()
        conn.close()

    def append_chat(self, msg):
        self.chat_text.config(state='normal')
        self.chat_text.insert(tk.END, msg + '\n')
        self.chat_text.config(state='disabled')
        self.chat_text.see(tk.END)

    def show_history(self):
        win = tk.Toplevel(self)
        win.title('답변 이력')
        text = tk.Text(win, width=80, height=20)
        text.pack(padx=10, pady=10)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT user_question, matched_question, answer, created_at FROM history ORDER BY created_at DESC LIMIT 30')
        for row in c.fetchall():
            text.insert(tk.END, f'[{row[3]}]\nQ: {row[0]}\n매칭된 질문: {row[1]}\nA: {row[2]}\n---\n')
        conn.close()
        text.config(state='disabled')

if __name__ == '__main__':
    init_db()
    app = FAQChatbotApp()
    app.mainloop() 