from escpos.printer import Usb
import usb.core
import usb.util

# Zadig에서 확인한 USB ID 입력
VENDOR_ID = 0x0525
PRODUCT_ID = 0xA700

try:
    # USB 장치 찾기
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    
    if device is None:
        raise ValueError('프린터를 찾을 수 없습니다.')
    
    # 장치의 인터페이스와 엔드포인트 정보 출력
    print("장치 정보:")
    print(f"설정된 구성: {device.get_active_configuration()}")
    
    for cfg in device:
        print(f"\n구성 {cfg.bConfigurationValue}:")
        for intf_num in range(cfg.bNumInterfaces):
            # Windows 의 detach 는 생략
            print(f"인터페이스 {intf_num}:")
            
            # (인터페이스번호, alternate_setting) → 대부분 프린터는 alt=0
            interface = cfg[(intf_num, 0)]
            for ep in interface:
                direction = 'OUT' if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT else 'IN'
                print(f"  엔드포인트: 0x{ep.bEndpointAddress:02X} (방향: {direction})")
    
    # 프린터 초기화 (확인된 엔드포인트 사용)
    printer = Usb(VENDOR_ID, PRODUCT_ID, interface=0, out_ep=0x01)
    
    # 한글 출력을 위한 설정
    printer.set(align='center')
    printer.text("한글 테스트 출력\n")
    printer.text("================\n")
    printer.text("USB 프린터 연결 테스트\n")
    printer.text("================\n\n")
    printer.set(align='left')
    printer.text("엔드포인트: 0x01\n")
    printer.text("인터페이스: 0\n")
    printer.cut()
    
except usb.core.USBError as e:
    print(f"USB 오류 발생: {str(e)}")
except Exception as e:
    print(f"오류 발생: {str(e)}")
