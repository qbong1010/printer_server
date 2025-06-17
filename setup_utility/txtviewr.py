def is_printable_ascii(byte):
    return 32 <= byte <= 126 or byte == 10  # 10은 줄바꿈

with open("C:/Users/dohwa/Desktop/MyPlugin/posprinter_supabase/test_print_output.bin", "rb") as f:
    content = f.read()
    print("=== 16진수로 출력 ===")
    print(' '.join(f'{b:02x}' for b in content))
    print("\n=== 프린터 제어 문자 제거 후 출력 ===")
    # 프린터 제어 문자(ESC, GS 등) 제거하고 출력 가능한 ASCII 문자만 필터링
    filtered = bytes(b for b in content if is_printable_ascii(b))
    print(filtered.decode('ascii', errors="ignore"))
