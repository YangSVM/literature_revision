from ollama import chat
import os

import time

def chunk_lines_by_character_count(lines, chunk_size=1500):
    """
    将文本行按字符数分组，确保每组的字符数不超过给定值。

    Args:
        lines: 文本行列表
        chunk_size: 每组最大字符数 (默认为 1500)

    Returns:
        包含分组文本的列表
    """
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_length = len(line)
        if current_length + line_length > chunk_size:
            chunks.append(''.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(line)
        current_length += line_length

    if current_chunk:  # 添加最后一个chunk
        chunks.append(''.join(current_chunk))

    return chunks


print("脚本开始执行 (字符数 Chunking 模式)...")

# 1. 读取文件
thesis_content_list = []
try:
    print("开始读取 data  文件夹...")
    data_dir = 'data'
    for filename in sorted(os.listdir(data_dir)):
        file_path = os.path.join(data_dir, filename)
        chapter_content = []

        if os.path.isfile(file_path):
            print(f"正在读取文件: {filename}")
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    # 过滤掉以%开头的LaTeX注释行 和 空行
                    if not line.lstrip().startswith('%') and line.lstrip()!='':
                        chapter_content.append(line)
        
        thesis_content_list += chapter_content
        print("文件", filename, "读取成功")
        # 添加代码：打印部分读取的文档内容
        print("\n--- 文件内容预览 (前 100 个字符): ---")
        if len(chapter_content) > 100:
            print(chapter_content[:100] )
        else:
            print(chapter_content)
    print("\n--- 预览结束 ---")

except FileNotFoundError:
    print("错误: thesis.txt 文件未找到。请确保文件在脚本的同一目录下，或者提供完整的文件路径。")
    exit()
except Exception as e:
    print(f"读取文件时发生错误: {e}")
    exit()

# thesis_content = ''
# for content in thesis_content_list:
#     thesis_content += content

# 2. 分割文本成字符数 chunks
print("将文本按行分组，确保每组字符数不超过给定值...")
chunk_size_param = 1500
text_chunks = chunk_lines_by_character_count(thesis_content_list, chunk_size=chunk_size_param)
print(f"文本已分割成 {len(text_chunks)} 组，每组字符数不超过 {chunk_size_param}。")

full_response = "" # 用于存储所有chunk的响应
num_chunks_to_process = len(text_chunks) #  处理所有 chunk (可以根据需要修改)

# 3. 循环处理每个字符数 chunk
for i, chunk in enumerate(text_chunks):
    if i >= num_chunks_to_process: #  如果需要测试，可以限制处理的 chunk 数量
        print(f"\n---  跳过第 {i+1}/{len(text_chunks)} 字符数块 (超出处理范围) ---")
        continue

    # 构建强约束性提示词 (每个 chunk 使用相同的提示词)
    prompt_text = f"""
     请你扮演一个专业的中文校对员。你的任务是**严格检查**以下latex格式的文本中的**中文错别字和语病**。
     **请注意，这是论文的第 {i+1}/{len(text_chunks)} 部分 (字符数分块)**

     请按照以下格式**清晰地列出**你发现的所有错误：

     **错误列表：**
     - **[错误类型]:** [错误词语或句子]  **建议修改为:** [修改后的词语或句子]  **位置:** [错误所在段落或句子的大概位置]

     **注意：**
     - 你只需要输出错误列表，**不要进行任何内容总结、分析或评价**。
     - 请**只检查错别字和语病**，不要修改文本的原始意思。
     - **只使用简体中文** 回答。

     **待检查文本：**
     {chunk}
     """

    print(f"\n---  开始处理第 {i+1}/{len(text_chunks)} 字符数块  ---")
    print("正在调用 Ollama 模型进行错别字检查，请稍候...")
    try:
        stream = chat(
            model='qwq',  # 使用支持中文的模型
            messages=[{'role': 'user', 'content': prompt_text}],
            stream=True
        )

        chunk_response = "" # 存储当前 chunk 的响应
        print("模型响应开始 (Chunk {}):".format(i+1))
        for output_chunk in stream: # 为了避免变量名冲突，这里使用 output_chunk
            if 'message' in output_chunk and 'content' in output_chunk['message']:
                content = output_chunk['message']['content']
                print(content, end="", flush=True)  # 实时流式打印
                chunk_response += content # 累加当前 chunk 的响应

        chunk_response_added = f"\n\n--- 第 {i+1}/{len(text_chunks)} 字符数块检查结果 ---\n{chunk_response}" # 添加chunk分隔符和响应内容
        full_response += chunk_response_added
        print(f"\n第 {i+1}/{len(text_chunks)} 字符数块处理完成。")
        # 暂存当前chunk的最终结果
        print("当前字符数块的最终结果到 advice_chapters.txt...")
        try:
            with open("advice_chapters.txt", "a", encoding="utf-8") as f:
                f.write(chunk_response_added)
            print("结果已保存至 advice_chapters.txt")
        except Exception as e:
            print(f"保存结果到 advice_chapters.txt 失败: {e}")

    except Exception as e:
        print(f"处理第 {i+1}/{len(text_chunks)} 字符数块时 API 调用失败: {e}")

print("\n所有字符数块处理完成。")

# 4. 保存所有chunk的最终结果
print("保存所有字符数块的最终结果到 advice_11.txt...")
try:
    time_str = time.strftime('%Y_%m_%d_%H_%M_%s', time.localtime(time.time()))
    advice_fname = "advice_"+ time_str +".txt"
    with open(advice_fname, "w", encoding="utf-8") as f:
        f.write(full_response)
    print("结果已保存至 ", advice_fname)

except Exception as e:
    print(f"保存结果到 {advice_fname} 失败: {e}")

print("脚本执行完毕 (字符数 Chunking 模式)。")
