# -*- coding: utf-8 -*-
"""프린터 설정 디버깅 도구"""
import json
from pathlib import Path
from src.printer.manager import PrinterManager

def debug_printer_config():
    print("=== 프린터 설정 디버깅 ===")
    
    # 설정 파일 존재 확인
    config_file = Path("printer_config.json")
    print(f"설정 파일 존재: {config_file.exists()}")
    
    if config_file.exists():
        print("\n현재 설정 파일 내용:")
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # PrinterManager 인스턴스 생성 및 설정 확인
    print("\n=== PrinterManager 설정 확인 ===")
    manager = PrinterManager()
    
    print(f"기존 호환성 설정:")
    print(f"  printer_type: {getattr(manager, 'printer_type', 'None')}")
    print(f"  printer_name: {getattr(manager, 'printer_name', 'None')}")
    print(f"  usb_info: {getattr(manager, 'usb_info', 'None')}")
    print(f"  network_info: {getattr(manager, 'network_info', 'None')}")
    
    print(f"\n새로운 손님용 프린터 설정:")
    customer_config = manager.get_customer_printer_config()
    print(json.dumps(customer_config, indent=2, ensure_ascii=False))
    
    print(f"\n주방용 프린터 설정:")
    kitchen_config = manager.get_kitchen_printer_config()
    print(json.dumps(kitchen_config, indent=2, ensure_ascii=False))
    
    # 테스트 데이터 생성
    test_order = {
        "order_id": "DEBUG-001",
        "company_name": "디버그 테스트",
        "created_at": "2024-01-01 12:00:00",
        "is_dine_in": True,
        "items": [
            {"name": "디버그 메뉴", "quantity": 1, "price": 1000, "options": []}
        ]
    }
    
    print(f"\n=== 손님용 프린터 테스트 ===")
    try:
        result = manager.print_customer_receipt(test_order)
        print(f"테스트 결과: {result}")
    except Exception as e:
        print(f"테스트 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_printer_config() 