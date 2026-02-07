import sys
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, QHBoxLayout,
                             QGroupBox, QGridLayout, QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QLabel { font-size: 14px; }
            QPushButton { 
                font-size: 14px; 
                padding: 8px 15px; 
                background-color: #007bff; 
                color: white; 
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                border: 1px solid #bbbbbb; 
                border-radius: 6px; 
                margin-top: 12px; 
                background-color: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: white;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.header = QLabel("Chemical Equipment Parameter Visualizer")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size: 22px; font-weight: bold; color: #333333; margin-bottom: 10px;")
        self.main_layout.addWidget(self.header)
        
        # Upload Section
        self.create_upload_section()
        
        # Stats Section
        self.create_stats_section()
        
        # Chart & PDF Section
        self.create_chart_section()

        # History Section
        self.create_history_section()
        
        self.file_path = None
        self.base_url = "http://127.0.0.1:8080" # Default Production
        self.auth = ('admin', 'admin123')

        # Initial fetch
        self.fetch_history()

    def create_upload_section(self):
        self.upload_group = QGroupBox("Data Source")
        layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666666; font-style: italic; border: 1px solid #ddd; padding: 5px; border-radius: 4px; background: #fafafa;")
        
        self.select_btn = QPushButton("Select CSV File")
        self.select_btn.setCursor(Qt.PointingHandCursor)
        self.select_btn.clicked.connect(self.select_file)
        
        self.upload_btn = QPushButton("Upload & Analyze")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setStyleSheet("""
            QPushButton { background-color: #28a745; }
            QPushButton:hover { background-color: #218838; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        
        layout.addWidget(self.select_btn)
        layout.addWidget(self.file_label, 1) 
        layout.addWidget(self.upload_btn)
        
        self.upload_group.setLayout(layout)
        self.main_layout.addWidget(self.upload_group)

    def create_stats_section(self):
        self.stats_group = QGroupBox("Summary Statistics")
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(15)
        
        self.stat_widgets = {}
        metrics = [
            ("Total Equipment", "0"),
            ("Avg Flowrate", "0 L/min"),
            ("Avg Pressure", "0 PSI"),
            ("Avg Temperature", "0 °C")
        ]
        
        for i, (label_text, value_text) in enumerate(metrics):
            container = QFrame()
            container.setStyleSheet("background-color: #f8f9fa; border-radius: 5px; border: 1px solid #e9ecef;")
            v_layout = QVBoxLayout(container)
            
            lbl = QLabel(label_text.upper())
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #6c757d; font-size: 11px; font-weight: bold;")
            
            val = QLabel(value_text)
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet("color: #212529; font-size: 20px; font-weight: bold;")
            
            v_layout.addWidget(lbl)
            v_layout.addWidget(val)
            
            self.stats_layout.addWidget(container, 0, i)
            self.stat_widgets[label_text] = val
            
        self.stats_group.setLayout(self.stats_layout)
        self.main_layout.addWidget(self.stats_group)

    def create_chart_section(self):
        self.chart_group = QGroupBox("Visualization")
        layout = QVBoxLayout()
        
        # Chart
        self.figure = plt.figure(figsize=(5, 3)) # Slightly smaller to fit History
        self.figure.patch.set_facecolor('#ffffff')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # PDF Button
        self.pdf_btn = QPushButton("Download PDF Report")
        self.pdf_btn.setCursor(Qt.PointingHandCursor)
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setFixedWidth(200)
        self.pdf_btn.setStyleSheet("background-color: #6c757d; margin-top: 5px;")
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.pdf_btn)
        layout.addLayout(btn_layout)

        self.chart_group.setLayout(layout)
        self.main_layout.addWidget(self.chart_group, 1)

    def create_history_section(self):
        self.history_group = QGroupBox("Recent Uploads")
        layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Filename", "Time", "Count", "Flow", "Pressure", "Temp"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setFixedHeight(150) # Fixed height for history

        layout.addWidget(self.history_table)
        self.history_group.setLayout(layout)
        self.main_layout.addWidget(self.history_group)

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path.split('/')[-1])
            self.file_label.setStyleSheet("color: #333333; font-weight: bold; border: 1px solid #28a745; padding: 5px; border-radius: 4px; background: #e8f5e9;")
            self.upload_btn.setEnabled(True)

    def upload_file(self):
        if not self.file_path:
            return
            
        urls_to_try = [f"{self.base_url}/api/upload/", "http://127.0.0.1:8000/api/upload/"]
        
        response = None
        
        try:
            with open(self.file_path, 'rb') as f:
                file_content = f.read()
            
            for target_url in urls_to_try:
                try:
                    files = {'file': (self.file_path.split('/')[-1], file_content, 'text/csv')}
                    print(f"Trying {target_url}...")
                    response = requests.post(target_url, files=files, auth=self.auth, timeout=2)
                    self.base_url = target_url.rsplit('/api', 1)[0] # Update base url if found
                    break
                except requests.exceptions.RequestException:
                    continue
            
            if not response:
                raise Exception("Could not connect to backend")

            if response.status_code == 201:
                data = response.json()
                self.update_ui(data)
                self.fetch_history() # Refresh history
                QMessageBox.information(self, "Success", "Upload successful!")
            else:
                try:
                    error_msg = response.json().get('error', response.text)
                except:
                    error_msg = response.text
                QMessageBox.warning(self, "Upload Failed", f"Server returned error:\n{error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"An error occurred:\n{str(e)}")

    def download_pdf(self):
        try:
            url = f"{self.base_url}/api/report/"
            response = requests.get(url, auth=self.auth, stream=True)
            
            if response.status_code == 200:
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "report.pdf", "PDF Files (*.pdf)", options=options)
                
                if file_path:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    QMessageBox.information(self, "Success", f"Report saved to:\n{file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate report. Make sure data is uploaded.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not download PDF:\n{str(e)}")

    def fetch_history(self):
        try:
            url = f"{self.base_url}/api/history/"
            # Try catch separate for history fetch to ensure main app logic continues
            try:
                response = requests.get(url, auth=self.auth, timeout=2)
            except:
                # Fallback check
                url = "http://127.0.0.1:8000/api/history/"
                response = requests.get(url, auth=self.auth, timeout=2)
                self.base_url = "http://127.0.0.1:8000"

            if response.status_code == 200:
                history = response.json()
                self.history_table.setRowCount(len(history))
                for i, item in enumerate(history):
                    self.history_table.setItem(i, 0, QTableWidgetItem(item['file_name']))
                    self.history_table.setItem(i, 1, QTableWidgetItem(item['uploaded_at'].split('T')[1].split('.')[0])) # Simple time parse
                    self.history_table.setItem(i, 2, QTableWidgetItem(str(item['total_equipment'])))
                    self.history_table.setItem(i, 3, QTableWidgetItem(str(item.get('avg_flowrate', '-'))))
                    self.history_table.setItem(i, 4, QTableWidgetItem(str(item.get('avg_pressure', '-'))))
                    self.history_table.setItem(i, 5, QTableWidgetItem(str(item.get('avg_temperature', '-'))))
        except Exception as e:
            print(f"Failed to fetch history: {e}")

    def update_ui(self, data):
        # Update Stats
        self.stat_widgets["Total Equipment"].setText(str(data['total_count']))
        self.stat_widgets["Avg Flowrate"].setText(f"{data['avg_flowrate']} L/min")
        self.stat_widgets["Avg Pressure"].setText(f"{data['avg_pressure']} PSI")
        self.stat_widgets["Avg Temperature"].setText(f"{data['avg_temperature']} °C")
        
        # Update Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        types = list(data['type_distribution'].keys())
        counts = list(data['type_distribution'].values())
        
        bars = ax.bar(types, counts, color='#3498db', edgecolor='#2980b9')
        
        ax.set_title('Equipment Type Distribution', fontsize=10, fontweight='bold', pad=10)
        ax.set_ylabel('Count', fontsize=9)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        self.figure.tight_layout()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
