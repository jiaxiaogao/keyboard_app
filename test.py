# test_keyboard.py
import keyboard
import time

print("测试 keyboard 库...")

# 测试基本功能
try:
    print("测试按键模拟...")
    keyboard.press('a')
    keyboard.release('a')
    print("按键模拟成功!")
    
    print("等待5秒，请按一些键测试记录功能...")
    time.sleep(5)
    
except Exception as e:
    print(f"错误: {e}")
    print("请检查辅助功能权限!")