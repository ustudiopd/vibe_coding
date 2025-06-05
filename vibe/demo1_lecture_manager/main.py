import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                           QPushButton, QFileDialog, QMessageBox, QLabel, QLineEdit,
                           QFrame, QScrollArea, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

DB_PATH = 'excel_manager.db'
UPLOADED_FILES_DIR = 'uploaded_files'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS file_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        columns TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
    if not os.path.exists(UPLOADED_FILES_DIR):
        os.makedirs(UPLOADED_FILES_DIR)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('엑셀 파일 관리 시스템')
        self.setGeometry(100, 100, 1200, 700)
        
        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 탭 위젯
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 파일 관리 탭
        self.file_tab = QWidget()
        self.tabs.addTab(self.file_tab, '파일 관리')
        self.create_file_tab()
        
        # 데이터 관리 탭
        self.data_tab = QWidget()
        self.tabs.addTab(self.data_tab, '데이터 관리')
        self.create_data_tab()
        
        self.current_file_id = None
        self.current_columns = []
        self.current_data = None
        
        # 스타일 설정
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #e1e1e1;
                border: 1px solid #cccccc;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e5f3ff;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

    def create_file_tab(self):
        layout = QVBoxLayout(self.file_tab)
        
        # 파일 목록 테이블
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(5)
        self.file_table.setHorizontalHeaderLabels(['ID', '저장된 파일명', '원본 파일명', '업로드 날짜', '컬럼 목록'])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setSelectionMode(QTableWidget.SingleSelection)
        self.file_table.itemSelectionChanged.connect(self.on_file_select)
        layout.addWidget(self.file_table)
        
        # 버튼
        btn_layout = QHBoxLayout()
        upload_btn = QPushButton('엑셀 파일 업로드')
        upload_btn.clicked.connect(self.upload_excel)
        delete_btn = QPushButton('파일 삭제')
        delete_btn.clicked.connect(self.delete_file)
        refresh_btn = QPushButton('새로고침')
        refresh_btn.clicked.connect(self.load_files)
        
        btn_layout.addWidget(upload_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_files()

    def create_data_tab(self):
        layout = QVBoxLayout(self.data_tab)
        
        # 상단 프레임 (필터 및 검색)
        top_frame = QWidget()
        top_layout = QHBoxLayout(top_frame)
        
        # 필터 그룹
        filter_group = QGroupBox('필터')
        filter_layout = QGridLayout()
        self.filter_entries = {}
        self.filter_frame = filter_layout
        filter_group.setLayout(filter_layout)
        top_layout.addWidget(filter_group)
        
        # 검색 그룹
        search_group = QGroupBox('검색')
        search_layout = QHBoxLayout()
        search_label = QLabel('검색어:')
        self.search_entry = QLineEdit()
        search_btn = QPushButton('검색')
        search_btn.clicked.connect(self.search_data)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(search_btn)
        search_group.setLayout(search_layout)
        top_layout.addWidget(search_group)
        
        layout.addWidget(top_frame)
        
        # 데이터 테이블
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)
        
        # 하단 버튼
        btn_layout = QHBoxLayout()
        export_btn = QPushButton('엑셀로 내보내기')
        export_btn.clicked.connect(self.export_to_excel)
        reset_btn = QPushButton('필터 초기화')
        reset_btn.clicked.connect(self.reset_filters)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def upload_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '엑셀 파일 선택', '', 'Excel files (*.xlsx *.xls)'
        )
        if not file_path:
            return
            
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            if df.empty:
                QMessageBox.critical(self, '오류', '파일에 데이터가 없습니다.')
                return
                
            # 파일 저장
            original_filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{timestamp}_{original_filename}"
            saved_path = os.path.join(UPLOADED_FILES_DIR, saved_filename)
            
            # 엑셀 파일 저장
            df.to_excel(saved_path, index=False)
            
            # DB에 파일 정보 저장
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''INSERT INTO file_info (filename, original_filename, upload_date, columns)
                        VALUES (?, ?, ?, ?)''',
                     (saved_filename, original_filename, 
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      ','.join(df.columns.tolist())))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, '성공', '파일이 성공적으로 업로드되었습니다.')
            self.load_files()
            
        except Exception as e:
            QMessageBox.critical(self, '오류', f'파일 업로드 중 오류가 발생했습니다: {str(e)}')

    def load_files(self):
        self.file_table.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, filename, original_filename, upload_date, columns FROM file_info')
        for row in c.fetchall():
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            for col, value in enumerate(row):
                self.file_table.setItem(row_position, col, QTableWidgetItem(str(value)))
        conn.close()
        
        # 컬럼 너비 조정
        self.file_table.resizeColumnsToContents()

    def on_file_select(self):
        selected_items = self.file_table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        self.current_file_id = int(self.file_table.item(row, 0).text())
        filename = self.file_table.item(row, 1).text()
        
        try:
            # 엑셀 파일 읽기
            file_path = os.path.join(UPLOADED_FILES_DIR, filename)
            self.current_data = pd.read_excel(file_path)
            self.current_columns = self.current_data.columns.tolist()
            
            # 데이터 테이블 설정
            self.setup_data_table()
            
            # 필터 프레임 업데이트
            self.update_filter_frame()
            
            # 데이터 표시
            self.display_data()
            
        except Exception as e:
            QMessageBox.critical(self, '오류', f'파일 로드 중 오류가 발생했습니다: {str(e)}')

    def setup_data_table(self):
        self.data_table.setColumnCount(len(self.current_columns))
        self.data_table.setHorizontalHeaderLabels(self.current_columns)
        self.data_table.horizontalHeader().setStretchLastSection(True)

    def update_filter_frame(self):
        # 기존 필터 위젯 제거
        while self.filter_frame.count():
            item = self.filter_frame.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 새 필터 위젯 생성
        self.filter_entries = {}
        for i, col in enumerate(self.current_columns):
            label = QLabel(f'{col}:')
            entry = QLineEdit()
            self.filter_entries[col] = entry
            self.filter_frame.addWidget(label, i//3, (i%3)*2)
            self.filter_frame.addWidget(entry, i//3, (i%3)*2+1)

    def display_data(self, filtered_data=None):
        data_to_display = filtered_data if filtered_data is not None else self.current_data
        self.data_table.setRowCount(len(data_to_display))
        
        for i, (_, row) in enumerate(data_to_display.iterrows()):
            for j, value in enumerate(row):
                self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        self.data_table.resizeColumnsToContents()

    def search_data(self):
        if self.current_data is None:
            return
            
        search_term = self.search_entry.text().strip().lower()
        if not search_term:
            self.display_data()
            return
            
        # 모든 컬럼에서 검색
        mask = pd.DataFrame(False, index=self.current_data.index, columns=['match'])
        for col in self.current_columns:
            mask['match'] |= self.current_data[col].astype(str).str.lower().str.contains(search_term)
        
        filtered_data = self.current_data[mask['match']]
        self.display_data(filtered_data)

    def reset_filters(self):
        # 필터 초기화
        for entry in self.filter_entries.values():
            entry.clear()
        self.search_entry.clear()
        self.display_data()

    def export_to_excel(self):
        if self.current_data is None:
            QMessageBox.warning(self, '알림', '내보낼 데이터가 없습니다.')
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, '엑셀 파일로 저장', '', 'Excel files (*.xlsx)'
        )
        if not file_path:
            return
            
        try:
            self.current_data.to_excel(file_path, index=False)
            QMessageBox.information(self, '성공', '파일이 성공적으로 저장되었습니다.')
        except Exception as e:
            QMessageBox.critical(self, '오류', f'파일 저장 중 오류가 발생했습니다: {str(e)}')

    def delete_file(self):
        if not self.current_file_id:
            QMessageBox.warning(self, '알림', '삭제할 파일을 선택하세요.')
            return
            
        reply = QMessageBox.question(
            self, '확인', '정말 삭제하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # DB에서 파일 정보 삭제
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('SELECT filename FROM file_info WHERE id=?', (self.current_file_id,))
                filename = c.fetchone()[0]
                c.execute('DELETE FROM file_info WHERE id=?', (self.current_file_id,))
                conn.commit()
                conn.close()
                
                # 실제 파일 삭제
                file_path = os.path.join(UPLOADED_FILES_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                self.current_file_id = None
                self.current_columns = []
                self.current_data = None
                self.load_files()
                self.setup_data_table()
                self.update_filter_frame()
                self.display_data()
                
                QMessageBox.information(self, '성공', '파일이 삭제되었습니다.')
            except Exception as e:
                QMessageBox.critical(self, '오류', f'파일 삭제 중 오류가 발생했습니다: {str(e)}')

if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 