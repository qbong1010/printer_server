from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QMessageBox,
    QRadioButton,
    QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from ..printer.manager import PrinterManager

class PrinterWidget(QWidget):
    printer_changed = Signal(str)  # 프린터 변경 시그널

    def __init__(self):
        super().__init__()
        self.printer_manager = PrinterManager()
        self.setup_ui()
        self.load_printers()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 프린터 선택 그룹
        printer_group = QGroupBox("프린터 설정")
        printer_layout = QVBoxLayout()

        # 프린터 목록
        printer_list_layout = QHBoxLayout()
        printer_list_layout.addWidget(QLabel("프린터:"))
        self.printer_combo = QComboBox()
        self.printer_combo.currentTextChanged.connect(self.on_printer_changed)
        printer_list_layout.addWidget(self.printer_combo)
        
        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.load_printers)
        printer_list_layout.addWidget(refresh_btn)
        
        printer_layout.addLayout(printer_list_layout)

        # 프린터 타입 선택
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("프린터 타입:"))
        
        self.type_group = QButtonGroup()
        self.default_radio = QRadioButton("일반 프린터")
        self.escpos_radio = QRadioButton("ESC/POS 프린터")
        self.default_radio.setChecked(True)
        
        self.type_group.addButton(self.default_radio)
        self.type_group.addButton(self.escpos_radio)
        
        type_layout.addWidget(self.default_radio)
        type_layout.addWidget(self.escpos_radio)
        type_layout.addStretch()
        
        printer_layout.addLayout(type_layout)

        # 테스트 출력 버튼
        test_layout = QHBoxLayout()
        test_btn = QPushButton("테스트 출력")
        test_btn.clicked.connect(self.print_test)
        test_layout.addWidget(test_btn)
        test_layout.addStretch()
        
        printer_layout.addLayout(test_layout)
        printer_group.setLayout(printer_layout)
        layout.addWidget(printer_group)

        # 스타일 설정
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
        """)

    def load_printers(self):
        """사용 가능한 프린터 목록을 로드합니다."""
        try:
            self.printer_combo.clear()
            printers = self.printer_manager.list_printers()
            if printers:
                self.printer_combo.addItems(printers)
                # 현재 선택된 프린터가 있다면 해당 프린터 선택
                current_printer = self.printer_manager.get_current_printer()
                if current_printer in printers:
                    self.printer_combo.setCurrentText(current_printer)
            else:
                QMessageBox.warning(self, "경고", "사용 가능한 프린터가 없습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"프린터 목록 로드 중 오류가 발생했습니다: {str(e)}")

    def on_printer_changed(self, printer_name):
        """프린터가 변경되었을 때 호출됩니다."""
        if printer_name:
            self.printer_manager.set_printer(printer_name)
            self.printer_changed.emit(printer_name)

    def print_test(self):
        """테스트 페이지를 출력합니다."""
        try:
            printer_type = "escpos" if self.escpos_radio.isChecked() else "default"
            self.printer_manager.set_printer_type(printer_type)
            
            test_data = {
                "order_id": "TEST-001",
                "customer_name": "테스트 고객",
                "items": [
                    {"name": "테스트 메뉴 1", "quantity": 1, "price": 1000},
                    {"name": "테스트 메뉴 2", "quantity": 2, "price": 2000}
                ],
                "payment_method": "테스트 결제"
            }
            
            success = self.printer_manager.print_receipt(test_data)
            if success:
                QMessageBox.information(self, "성공", "테스트 출력이 완료되었습니다.")
            else:
                QMessageBox.warning(self, "실패", "테스트 출력에 실패했습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"테스트 출력 중 오류가 발생했습니다: {str(e)}") 