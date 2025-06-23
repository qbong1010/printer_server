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
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QTabWidget
)
from PySide6.QtCore import Qt, Signal
from src.printer.manager import PrinterManager

class CustomerPrinterWidget(QWidget):
    """손님용 프린터 설정 위젯"""
    printer_changed = Signal(str)

    def __init__(self, printer_manager):
        super().__init__()
        self.printer_manager = printer_manager
        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 프린터 타입 선택
        type_group = QGroupBox("손님용 프린터 타입")
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

        # 프린터 설정 그룹
        self.printer_group = QGroupBox("손님용 프린터 설정")
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
        test_btn = QPushButton("손님용 프린터 테스트")
        test_btn.clicked.connect(self.print_test)
        test_layout.addWidget(test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

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

    def load_current_config(self):
        """현재 손님용 프린터 설정을 로드하여 UI에 반영합니다."""
        config = self.printer_manager.get_customer_printer_config()
        printer_type = config.get("printer_type", "escpos")
        
        if printer_type == "default":
            self.default_radio.setChecked(True)
        elif printer_type == "escpos":
            self.escpos_radio.setChecked(True)
        elif printer_type == "network":
            self.network_radio.setChecked(True)

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
        """손님용 프린터 테스트 페이지를 출력합니다."""
        try:
            test_data = {
                "order_id": "TEST-CUSTOMER-001",
                "company_name": "테스트 업체",
                "created_at": "2024-01-01 12:00:00",
                "is_dine_in": True,
                "items": [
                    {"name": "손님용 테스트 메뉴 1", "quantity": 1, "price": 1000, "options": []},
                    {"name": "손님용 테스트 메뉴 2", "quantity": 2, "price": 2000, "options": [{"name": "추가 옵션", "price": 500}]}
                ]
            }
            
            success = self.printer_manager.print_customer_receipt(test_data)
            if success:
                QMessageBox.information(self, "성공", "손님용 프린터 테스트 출력이 완료되었습니다.")
            else:
                QMessageBox.warning(self, "실패", "손님용 프린터 테스트 출력에 실패했습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"손님용 프린터 테스트 출력 중 오류가 발생했습니다: {str(e)}")

    def confirm_default_printer(self):
        value = self.printer_combo.currentText() if hasattr(self, 'printer_combo') else ''
        self.printer_manager.set_printer(value)
        self.printer_manager.set_customer_printer_type("default")
        QMessageBox.information(self, "적용 완료", f"손님용 프린터가 저장되었습니다: {value}")

    def confirm_escpos_printer(self):
        vid = self.vendor_id_edit.text() if hasattr(self, 'vendor_id_edit') else ''
        pid = self.product_id_edit.text() if hasattr(self, 'product_id_edit') else ''
        iface = self.interface_edit.text() if hasattr(self, 'interface_edit') else ''
        
        if not vid or not pid:
            QMessageBox.warning(self, "경고", "Vendor ID와 Product ID를 모두 입력해주세요.")
            return
            
        self.printer_manager.set_customer_printer_type("escpos", {"vendor_id": vid, "product_id": pid, "interface": iface})
        QMessageBox.information(self, "적용 완료", f"손님용 ESC/POS 정보가 저장되었습니다:\nVendor ID: {vid}\nProduct ID: {pid}\nInterface: {iface}")

    def confirm_network_printer(self):
        addr = self.network_addr_edit.text() if hasattr(self, 'network_addr_edit') else ''
        port = self.network_port_edit.text() if hasattr(self, 'network_port_edit') else ''
        self.printer_manager.set_customer_printer_type("network", {"address": addr, "port": port})
        QMessageBox.information(self, "적용 완료", f"손님용 네트워크 프린터 정보가 저장되었습니다:\n주소: {addr}\n포트: {port}")

class KitchenPrinterWidget(QWidget):
    """주방용 프린터 설정 위젯"""
    
    def __init__(self, printer_manager):
        super().__init__()
        self.printer_manager = printer_manager
        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 주방 프린터 활성화 체크박스
        self.enabled_checkbox = QCheckBox("주방 프린터 사용")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.stateChanged.connect(self.on_enabled_changed)
        layout.addWidget(self.enabled_checkbox)

        # 프린터 설정 그룹
        self.printer_group = QGroupBox("주방용 프린터 설정 (COM 포트)")
        printer_layout = QVBoxLayout()

        # COM 포트 설정
        com_layout = QHBoxLayout()
        com_layout.addWidget(QLabel("COM 포트:"))
        self.com_port_edit = QLineEdit()
        self.com_port_edit.setText("COM3")
        com_layout.addWidget(self.com_port_edit)
        printer_layout.addLayout(com_layout)

        # 통신 속도 설정
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("통신 속도:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combo.setCurrentText("9600")
        baud_layout.addWidget(self.baudrate_combo)
        printer_layout.addLayout(baud_layout)

        # 설정 저장 버튼
        save_btn = QPushButton("주방 프린터 설정 저장")
        save_btn.clicked.connect(self.save_config)
        printer_layout.addWidget(save_btn)

        self.printer_group.setLayout(printer_layout)
        layout.addWidget(self.printer_group)

        # 테스트 버튼
        test_layout = QHBoxLayout()
        test_btn = QPushButton("주방용 프린터 테스트")
        test_btn.clicked.connect(self.print_test)
        test_layout.addWidget(test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

    def load_current_config(self):
        """현재 주방용 프린터 설정을 로드하여 UI에 반영합니다."""
        config = self.printer_manager.get_kitchen_printer_config()
        self.enabled_checkbox.setChecked(config.get("enabled", True))
        self.com_port_edit.setText(config.get("com_port", "COM3"))
        self.baudrate_combo.setCurrentText(str(config.get("baudrate", 9600)))
        self.on_enabled_changed()

    def on_enabled_changed(self):
        """주방 프린터 활성화 상태 변경시 호출됩니다."""
        enabled = self.enabled_checkbox.isChecked()
        self.printer_group.setEnabled(enabled)

    def save_config(self):
        """주방용 프린터 설정을 저장합니다."""
        try:
            com_port = self.com_port_edit.text().strip()
            baudrate = int(self.baudrate_combo.currentText())
            enabled = self.enabled_checkbox.isChecked()
            
            if not com_port:
                QMessageBox.warning(self, "경고", "COM 포트를 입력해주세요.")
                return
            
            self.printer_manager.set_kitchen_printer_config(com_port, baudrate, enabled)
            QMessageBox.information(self, "성공", f"주방용 프린터 설정이 저장되었습니다.\nCOM 포트: {com_port}\n통신 속도: {baudrate}\n활성화: {'예' if enabled else '아니오'}")
        except ValueError:
            QMessageBox.warning(self, "오류", "올바른 통신 속도를 선택해주세요.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"설정 저장 중 오류가 발생했습니다: {str(e)}")

    def print_test(self):
        """주방용 프린터 테스트 페이지를 출력합니다."""
        try:
            test_data = {
                "order_id": "TEST-KITCHEN-001",
                "company_name": "테스트 업체",
                "created_at": "2024-01-01 12:00:00",
                "is_dine_in": True,
                "items": [
                    {"name": "주방 테스트 메뉴 1", "quantity": 1, "price": 1000, "options": []},
                    {"name": "주방 테스트 메뉴 2", "quantity": 2, "price": 2000, "options": [{"name": "매운맛", "price": 0}]}
                ]
            }
            
            success = self.printer_manager.print_kitchen_receipt(test_data)
            if success:
                QMessageBox.information(self, "성공", "주방용 프린터 테스트 출력이 완료되었습니다.")
            else:
                QMessageBox.warning(self, "실패", "주방용 프린터 테스트 출력에 실패했습니다.\nCOM 포트 연결을 확인해주세요.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"주방용 프린터 테스트 출력 중 오류가 발생했습니다: {str(e)}")

class PrinterWidget(QWidget):
    """통합 프린터 설정 위젯 (탭으로 분리)"""
    printer_changed = Signal(str)  # 기존 호환성을 위한 시그널

    def __init__(self):
        super().__init__()
        self.printer_manager = PrinterManager()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 탭 위젯 생성
        tab_widget = QTabWidget()

        # 손님용 프린터 탭
        self.customer_widget = CustomerPrinterWidget(self.printer_manager)
        self.customer_widget.printer_changed.connect(self.printer_changed.emit)  # 시그널 연결
        tab_widget.addTab(self.customer_widget, "손님용 프린터")

        # 주방용 프린터 탭
        self.kitchen_widget = KitchenPrinterWidget(self.printer_manager)
        tab_widget.addTab(self.kitchen_widget, "주방용 프린터")

        layout.addWidget(tab_widget)

        # 전체 테스트 버튼
        test_layout = QHBoxLayout()
        both_test_btn = QPushButton("양쪽 프린터 동시 테스트")
        both_test_btn.clicked.connect(self.print_both_test)
        test_layout.addWidget(both_test_btn)
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
        """)

    def print_both_test(self):
        """양쪽 프린터에 동시 테스트 출력을 수행합니다."""
        try:
            test_data = {
                "order_id": "TEST-BOTH-001",
                "company_name": "테스트 업체",
                "created_at": "2024-01-01 12:00:00",
                "is_dine_in": True,
                "items": [
                    {"name": "동시 테스트 메뉴 1", "quantity": 1, "price": 1000, "options": []},
                    {"name": "동시 테스트 메뉴 2", "quantity": 2, "price": 2000, "options": [{"name": "옵션 테스트", "price": 500}]}
                ]
            }
            
            results = self.printer_manager.print_both_receipts(test_data)
            
            customer_status = "성공" if results["customer"] else "실패"
            kitchen_status = "성공" if results["kitchen"] else "실패"
            
            message = f"동시 테스트 출력 결과:\n손님용 프린터: {customer_status}\n주방용 프린터: {kitchen_status}"
            
            if results["customer"] and results["kitchen"]:
                QMessageBox.information(self, "성공", message)
            elif results["customer"] or results["kitchen"]:
                QMessageBox.warning(self, "부분 성공", message)
            else:
                QMessageBox.warning(self, "실패", message)
                
        except Exception as e:
            QMessageBox.warning(self, "오류", f"동시 테스트 출력 중 오류가 발생했습니다: {str(e)}")

    # 기존 호환성을 위한 메서드들
    def print_test(self):
        """기존 호환성을 위한 테스트 메서드"""
        self.customer_widget.print_test()

    def load_printers(self):
        """기존 호환성을 위한 프린터 로드 메서드"""
        self.customer_widget.load_printers() 