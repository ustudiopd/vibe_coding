import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')

font_path = 'C:/Windows/Fonts/malgun.ttf'  # 윈도우 기본 맑은 고딕 경로
fontprop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False

DATA_FILE = 'staff_dummy.csv'


class StaffDashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('교직원 데이터 분석 대시보드')
        self.geometry('1400x900')
        self.resizable(False, False)
        self.df = None
        self.filtered_df = None
        self.create_widgets()
        self.load_data()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        plt.close('all')
        self.destroy()

    def create_widgets(self):
        # 상단: 필터/검색
        filter_frame = ttk.LabelFrame(self, text='필터/검색', padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(filter_frame, text='부서').pack(side='left')
        self.dept_var = tk.StringVar()
        self.dept_combo = ttk.Combobox(
            filter_frame, textvariable=self.dept_var,
            state='readonly', width=10)
        self.dept_combo.pack(side='left', padx=5)
        ttk.Label(filter_frame, text='직급').pack(side='left')
        self.rank_var = tk.StringVar()
        self.rank_combo = ttk.Combobox(
            filter_frame, textvariable=self.rank_var,
            state='readonly', width=10)
        self.rank_combo.pack(side='left', padx=5)
        ttk.Label(filter_frame, text='성별').pack(side='left')
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(
            filter_frame, textvariable=self.gender_var,
            state='readonly', width=7)
        self.gender_combo.pack(side='left', padx=5)
        ttk.Button(filter_frame, text='적용',
                   command=self.apply_filter).pack(
            side='left', padx=10)
        ttk.Button(filter_frame, text='초기화',
                   command=self.reset_filter).pack(
            side='left', padx=5)
        ttk.Button(filter_frame, text='Excel로 내보내기',
                   command=self.export_excel).pack(
            side='right', padx=5)

        # 그래프 옵션 체크박스
        chart_frame = ttk.LabelFrame(
            self, text='그래프 그룹화 옵션 (복수 선택 가능)', padding=10)
        chart_frame.pack(fill='x', padx=10, pady=5)
        self.opt_dept = tk.BooleanVar(value=True)
        self.opt_gender = tk.BooleanVar(value=False)
        self.opt_age = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            chart_frame, text='부서별', variable=self.opt_dept,
            command=self.update_stats_and_chart).pack(side='left', padx=10)
        ttk.Checkbutton(
            chart_frame, text='성별', variable=self.opt_gender,
            command=self.update_stats_and_chart).pack(side='left', padx=10)
        ttk.Checkbutton(
            chart_frame, text='연령대별', variable=self.opt_age,
            command=self.update_stats_and_chart).pack(side='left', padx=10)

        # 중단: 표(데이터 테이블)
        table_frame = ttk.LabelFrame(self, text='교직원 데이터', padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        columns = ['이름', '부서', '직급', '입사년도', '성별', '나이']
        self.tree = ttk.Treeview(
            table_frame, columns=columns,
            show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill='both', expand=True)

        # 하단: 통계/차트
        stat_frame = ttk.LabelFrame(self, text='통계 및 시각화', padding=10)
        stat_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.stat_text = tk.Text(stat_frame, height=7, width=60)
        self.stat_text.pack(side='left', fill='y', padx=5)
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=stat_frame)
        self.canvas.get_tk_widget().pack(side='left', fill='both', expand=True)

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            messagebox.showerror('오류', f'{DATA_FILE} 파일이 없습니다.')
            return
        self.df = pd.read_csv(DATA_FILE)
        self.filtered_df = self.df.copy()
        self.update_filter_options()
        self.update_table()
        self.update_stats_and_chart()

    def update_filter_options(self):
        self.dept_combo['values'] = ['전체'] + sorted(self.df['부서'].unique())
        self.rank_combo['values'] = ['전체'] + sorted(self.df['직급'].unique())
        self.gender_combo['values'] = ['전체'] + sorted(self.df['성별'].unique())
        self.dept_combo.set('전체')
        self.rank_combo.set('전체')
        self.gender_combo.set('전체')

    def apply_filter(self):
        df = self.df.copy()
        if self.dept_var.get() != '전체':
            df = df[df['부서'] == self.dept_var.get()]
        if self.rank_var.get() != '전체':
            df = df[df['직급'] == self.rank_var.get()]
        if self.gender_var.get() != '전체':
            df = df[df['성별'] == self.gender_var.get()]
        self.filtered_df = df
        self.update_table()
        self.update_stats_and_chart()

    def reset_filter(self):
        self.filtered_df = self.df.copy()
        self.update_filter_options()
        self.update_table()
        self.update_stats_and_chart()

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in self.filtered_df.iterrows():
            self.tree.insert('', 'end', values=list(row))

    def update_stats_and_chart(self):
        df = self.filtered_df.copy()
        self.stat_text.config(state='normal')
        self.stat_text.delete(1.0, tk.END)
        self.stat_text.insert(
            tk.END, f'총 인원: {len(df)}명\n')
        self.stat_text.insert(
            tk.END, f"부서별 인원: {df['부서'].value_counts().to_dict()}\n")
        self.stat_text.insert(
            tk.END, f"직급별 인원: {df['직급'].value_counts().to_dict()}\n")
        self.stat_text.insert(
            tk.END, f"성별 인원: {df['성별'].value_counts().to_dict()}\n")
        self.stat_text.insert(
            tk.END, f"평균 나이: {df['나이'].mean():.1f}세\n")
        self.stat_text.insert(
            tk.END, f"평균 입사년도: {df['입사년도'].mean():.0f}년\n")
        self.stat_text.config(state='disabled')
        # 차트 옵션별 시각화
        self.ax.clear()
        group_cols = []
        if self.opt_dept.get():
            group_cols.append('부서')
        if self.opt_age.get():
            bins = [0, 29, 39, 200]
            labels = ['20대', '30대', '40대 이상']
            df['연령대'] = pd.cut(df['나이'], bins=bins, labels=labels, right=True)
            group_cols.append('연령대')
        if self.opt_gender.get():
            group_cols.append('성별')
        # 체크박스 모두 해제 시 안내 문구만 표시하고 return
        if not group_cols:
            self.ax.text(
                0.5, 0.5, '옵션을 1개 이상 선택하세요.',
                ha='center', va='center', fontsize=14
            )
            self.canvas.draw()
            return
        # 그룹화 및 시각화
        if self.opt_gender.get() and len(group_cols) > 1:
            # 성별 포함 + 다른 그룹도 선택: grouped bar chart (남: 파랑, 여: 빨강)
            groupby_cols = [col for col in group_cols if col != '성별']
            grouped = df.groupby(groupby_cols + ['성별']).size().unstack(
                fill_value=0)
            x_labels = [
                '/'.join(map(str, idx)) if isinstance(idx, tuple) else str(idx)
                for idx in grouped.index
            ]
            x = range(len(x_labels))
            width = 0.35
            self.ax.bar(
                [i - width/2 for i in x],
                grouped.get('남', [0]*len(x)),
                width, label='남', color='royalblue')
            self.ax.bar(
                [i + width/2 for i in x],
                grouped.get('여', [0]*len(x)),
                width, label='여', color='crimson')
            self.ax.set_xticks(list(x))
            self.ax.set_xticklabels(x_labels, rotation=30, ha='right')
            self.ax.legend()
            self.ax.set_ylabel('인원수')
            self.ax.set_title(' / '.join(groupby_cols + ['성별']) + ' 인원수')
        else:
            # 성별만 단독 or 성별 미포함: 단일 bar chart
            grouped = df.groupby(group_cols).size()
            x_labels = [
                '/'.join(map(str, idx)) if isinstance(idx, tuple) else str(idx)
                for idx in grouped.index
            ]
            color = [
                'royalblue' if x == '남' else 'crimson' if x == '여'
                else 'mediumseagreen' for x in x_labels
            ]
            bars = self.ax.bar(x_labels, grouped.values, color=color)
            # x축 라벨 개수와 bar 개수가 다를 경우 set_xticklabels 생략
            if len(x_labels) == len(bars):
                self.ax.set_xticks(range(len(x_labels)))
                self.ax.set_xticklabels(x_labels, rotation=30, ha='right')
            self.ax.set_ylabel('인원수')
            self.ax.set_title(' / '.join(group_cols) + ' 인원수')
        self.canvas.draw()

    def export_excel(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx')],
            title='Excel로 내보내기')
        if not save_path:
            return
        try:
            self.filtered_df.to_excel(save_path, index=False)
            messagebox.showinfo('성공', 'Excel 파일로 저장되었습니다!')
        except Exception:
            messagebox.showerror('오류', '저장 실패!')


if __name__ == '__main__':
    try:
        app = StaffDashboardApp()
        app.mainloop()
    except Exception:
        import traceback
        traceback.print_exc() 