import requests
import time
import os

# 设置你的 Meshy API Key（建议从环境变量中读取）
MESHY_API_KEY = os.getenv("MESHY_API_KEY")  # 请确保已设置环境变量
if not MESHY_API_KEY:
    MESHY_API_KEY = "your_api_key_here"  # 或者直接填入你的 API Key

# 请求头
headers = {
    "Authorization": f"Bearer {MESHY_API_KEY}",
    "Content-Type": "application/json"
}

# 1. Generate a preview model and get the task ID

generate_preview_request = {
    "mode": "preview",
    "prompt": "a monster mask, with red texture",
    "negative_prompt": "low quality, low resolution, low poly, ugly",
    "art_style": "realistic",
    "should_remesh": True,
}

generate_preview_response = requests.post(
    "https://api.meshy.ai/openapi/v2/text-to-3d",
    headers=headers,
    json=generate_preview_request,
)

generate_preview_response.raise_for_status()

preview_task_id = generate_preview_response.json()["result"]

print("Preview task created. Task ID:", preview_task_id)

# 你的任务 ID
task_id = preview_task_id

# Meshy API 任务状态查询接口
status_url = f"https://api.meshy.ai/openapi/v2/text-to-3d/{task_id}"

# 轮询任务状态
while True:
    response = requests.get(status_url, headers=headers)
    response.raise_for_status()  # 如果请求失败，抛出异常
    task_data = response.json()

    status = task_data["status"]
    print(f"任务状态: {status} | 进度: {task_data.get('progress', 0)}%")

    if status == "SUCCEEDED":
        print("任务完成！")
        # 获取模型下载链接
        model_url = task_data["model_urls"]["glb"]
        print(f"模型下载链接: {model_url}")
        break
    elif status in ["FAILED", "EXPIRED"]:
        print(f"任务失败或过期: {status}")
        break
    else:
        print("任务仍在进行中，5秒后重试...")
        time.sleep(50)  # 每隔50秒检查一次

# 下载模型文件（可选）
if status == "SUCCEEDED":
    model_response = requests.get(model_url)
    model_response.raise_for_status()
    model_name = "moster_mask_red.glb"
    with open(model_name, "wb") as f:
        f.write(model_response.content)
    print(f"模型已下载至{model_name}")