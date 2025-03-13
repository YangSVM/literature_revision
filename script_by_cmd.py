import os
import subprocess

def run_command(cmd):
    """
    执行命令行命令并返回输出结果
    
    Args:
        cmd: 要执行的命令字符串
        
    Returns:
        命令执行结果的字符串
    """
    try:
        # 使用subprocess.run执行命令，capture_output=True捕获输出
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        # 检查命令是否成功执行
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"命令执行失败，错误信息：{result.stderr}")
            return None
            
    except Exception as e:
        print(f"执行命令时发生错误：{e}")
        return None
    

# 执行dir命令（Windows）或ls命令（Linux/Mac）
output = run_command("dir")  # Windows
# output = run_command("ls -l")  # Linux/Mac

if output:
    print("命令输出：")
    print(output)    
