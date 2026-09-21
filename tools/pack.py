import base64

def pack(token: str, key: str) -> str:
    """Упаковка"""
    if not token or not key:
        return ""
    result = ""
    for i, c in enumerate(token):
        result += chr(ord(c) ^ ord(key[i % len(key)]))
    return base64.b64encode(result.encode()).decode()

if __name__ == "__main__":
    print("SHIFIER\n")
    token = input("Наречение:").strip()
    key = input("ВГО:").strip()

    if not token or not key:
        print("АШИБАЧКИ)))")
        exit(1)

    packed = pack(token, key)
    print(packed)

    print("I'm ready!")
    print(f"1. Упаковка:")
    print(f"   _TOKEN_PACKED = '{packed}'")
    print(f"\n2. Открывашка:")
    print(f"   _KEY_PACKED = '{key}'")