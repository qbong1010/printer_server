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
    QButtonGroup,
    QLineEdit
)
from PySide6.QtCore import Qt, Signal
from src.printer.manager import PrinterManager

class PrinterWidget(QWidget):
    printer_changed = Signal(str)  # 프린터 변경 시그널

    def __init__(self):
        super().__init__()
        self.printer_manager = PrinterManager()
        self.setup_ui()
        self.load_printers()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 프린터 타입 선택 (최상단)
        type_group = QGroupBox("프린터 타입")
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup()
        self.default_radio = QRadioButton("일반 프린터")
        self.escpos_radio = QRadioButton("ESC/POS 프린터")
        self.network_radio = QRadioButton("네트워크 프린터")
        self.default_radio.setChecked(True)
        self.type_group.addButton(self.default_radio)
        self.type_group.addButton(self.escpos_radio)
        self.type_group.addButton(self.network_radio)
        type_layout.addWidget(self.default_radio)
        type_layout.addWidget(self.escpos_radio)
        type_layout.addWidget(self.network_radio)
        type_layout.addStretch()
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # 프린터 설정 그룹 (아래쪽)
        self.printer_group = QGroupBox("프린터 설정")
        self.printer_layout = QVBoxLayout()
        self.printer_group.setLayout(self.printer_layout)
        layout.addWidget(self.printer_group)

        # 동적 위젯 영역 초기화
        self.init_printer_section()

        # 프린터 타입 변경 시 동적 UI 변경
        self.default_radio.toggled.connect(self.init_printer_section)
        self.escpos_radio.toggled.connect(self.init_printer_section)
        self.network_radio.toggled.connect(self.init_printer_section)

        # 테스트 출력 버튼
        test_layout = QHBoxLayout()
        test_btn = QPushButton("테스트 출력")
        test_btn.clicked.connect(self.print_test)
        test_layout.addWidget(test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

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

    def init_printer_section(self):
        # 기존 위젯 및 레이아웃 완전 제거
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget is not None:
                    widget.deleteLater()
                elif child_layout is not None:
                    clear_layout(child_layout)
                    child_layout.deleteLater()
        clear_layout(self.printer_layout)

        if self.default_radio.isChecked():
            # 일반 프린터: 기존 콤보박스
            printer_list_layout = QHBoxLayout()
            printer_list_layout.addWidget(QLabel("프린터:"))
            self.printer_combo = QComboBox()
            self.printer_combo.currentTextChanged.connect(self.on_printer_changed)
            printer_list_layout.addWidget(self.printer_combo)
            refresh_btn = QPushButton("새로고침")
            refresh_btn.clicked.connect(self.load_printers)
            printer_list_layout.addWidget(refresh_btn)
            self.printer_layout.addLayout(printer_list_layout)
            self.load_printers()
            # 확인 버튼
            confirm_btn = QPushButton("확인")
            confirm_btn.clicked.connect(self.confirm_default_printer)
            self.printer_layout.addWidget(confirm_btn)
        elif self.escpos_radio.isChecked():
            # ESC/POS 프린터: Vendor ID, Product ID, Interface
            escpos_layout = QVBoxLayout()
            vid_layout = QHBoxLayout()
            vid_layout.addWidget(QLabel("Vendor ID:"))
            self.vendor_id_edit = QLineEdit()
            self.vendor_id_edit.setText("0525")  # 0x0525
            vid_layout.addWidget(self.vendor_id_edit)
            escpos_layout.addLayout(vid_layout)
            pid_layout = QHBoxLayout()
            pid_layout.addWidget(QLabel("Product ID:"))
            self.product_id_edit = QLineEdit()
            self.product_id_edit.setText("A700")  # 0xA700
            pid_layout.addWidget(self.product_id_edit)
            escpos_layout.addLayout(pid_layout)
            iface_layout = QHBoxLayout()
            iface_layout.addWidget(QLabel("Interface:"))
            self.interface_edit = QLineEdit()
            self.interface_edit.setText("0")
            iface_layout.addWidget(self.interface_edit)
            escpos_layout.addLayout(iface_layout)
            self.printer_layout.addLayout(escpos_layout)
            # 확인 버튼
            confirm_btn = QPushButton("확인")
            confirm_btn.clicked.connect(self.confirm_escpos_printer)
            self.printer_layout.addWidget(confirm_btn)
        elif self.network_radio.isChecked():
            # 네트워크 프린터: 네트워크 주소, 포트
            net_layout = QVBoxLayout()
            addr_layout = QHBoxLayout()
            addr_layout.addWidget(QLabel("네트워크 주소:"))
            self.network_addr_edit = QLineEdit()
            self.network_addr_edit.setText("192.168.0.100")
            addr_layout.addWidget(self.network_addr_edit)
            net_layout.addLayout(addr_layout)
            port_layout = QHBoxLayout()
            port_layout.addWidget(QLabel("포트:"))
            self.network_port_edit = QLineEdit()
            self.network_port_edit.setText("9100")
            port_layout.addWidget(self.network_port_edit)
            net_layout.addLayout(port_layout)
            self.printer_layout.addLayout(net_layout)
            # 확인 버튼
            confirm_btn = QPushButton("확인")
            confirm_btn.clicked.connect(self.confirm_network_printer)
            self.printer_layout.addWidget(confirm_btn)

    def load_printers(self):
        if not hasattr(self, 'printer_combo'):
            return
        try:
            self.printer_combo.clear()
            printers = self.printer_manager.list_printers()
            if printers:
                self.printer_combo.addItems(printers)
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

    def confirm_default_printer(self):
        value = self.printer_combo.currentText() if hasattr(self, 'printer_combo') else ''
        self.printer_manager.set_printer(value)
        self.printer_manager.set_printer_type("default")
        QMessageBox.information(self, "적용 완료", f"선택된 프린터가 저장되었습니다: {value}")

    def confirm_escpos_printer(self):
        vid = self.vendor_id_edit.text() if hasattr(self, 'vendor_id_edit') else ''
        pid = self.product_id_edit.text() if hasattr(self, 'product_id_edit') else ''
        iface = self.interface_edit.text() if hasattr(self, 'interface_edit') else ''
        self.printer_manager.set_printer_type("escpos", {"vendor_id": vid, "product_id": pid, "interface": iface})
        QMessageBox.information(self, "적용 완료", f"ESC/POS 정보가 저장되었습니다:\nVendor ID: {vid}\nProduct ID: {pid}\nInterface: {iface}")

    def confirm_network_printer(self):
        addr = self.network_addr_edit.text() if hasattr(self, 'network_addr_edit') else ''
        port = self.network_port_edit.text() if hasattr(self, 'network_port_edit') else ''
        self.printer_manager.set_printer_type("network", {"address": addr, "port": port})
        QMessageBox.information(self, "적용 완료", f"네트워크 프린터 정보가 저장되었습니다:\n주소: {addr}\n포트: {port}") 