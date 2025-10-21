import google.generativeai as genai

# 1. 配置你的 API 密钥
api_key = 'AIzaSyALFlkVqMr8OM7OULxHc7oox59b0xeEDBM'  # ⬅️ 在这里替换成你自己的API密钥
genai.configure(api_key=api_key)

# 2. 创建模型实例
# 我们同样使用 'gemini-1.5-flash-latest'
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. 调用模型生成内容
try:
    prompt = "Explain how AI works in a few words"
    response = model.generate_content(prompt)

    # 4. 打印结果
    print(response.text)

except Exception as e:
    print(f"error: {e}")
