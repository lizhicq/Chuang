import requests
import time
import os
import base64

# 设置 API Key
MESHY_API_KEY = os.getenv("MESHY_API_KEY") or "your_api_key_here"
headers = {
    "Authorization": f"Bearer {MESHY_API_KEY}",
    "Content-Type": "application/json"
}

# 本地图片路径
local_image_path = "model/WechatIMG25.jpg"  # 替换为你的本地图片路径

# 检查文件是否存在
if not os.path.exists(local_image_path):
    print(f"错误：文件 {local_image_path} 不存在")
    exit()

# 将本地图片转换为 Base64 Data URI
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        mime_type = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        return f"data:{mime_type};base64,{encoded_string}"

image_url = image_to_base64(local_image_path)

# Image-to-3D 请求 payload
payload = {
    "image_url": image_url,  # 使用 Base64 Data URI
    "enable_pbr": False,
    "should_remesh": False,
    "should_texture": False
}

# 发送 Image-to-3D 请求
try:
    response = requests.post(
        "https://api.meshy.ai/openapi/v1/image-to-3d",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    task_id = response.json()["result"]
    print("Image-to-3D task created. Task ID:", task_id)

    # 轮询任务状态
    status_url = f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}"
    while True:
        status_response = requests.get(status_url, headers=headers)
        status_response.raise_for_status()
        task_data = status_response.json()
        status = task_data["status"]
        print(f"任务状态: {status} | 进度: {task_data.get('progress', 0)}%")

        if status == "SUCCEEDED":
            print("任务完成！")
            model_url = task_data["model_urls"]["glb"]
            print(f"模型下载链接: {model_url}")
            break
        elif status in ["FAILED", "EXPIRED"]:
            print(f"任务失败或过期: {status}")
            break
        else:
            print("任务仍在进行中，20秒后重试...")
            time.sleep(20)

    # 下载生成的模型
    if status == "SUCCEEDED":
        model_response = requests.get(model_url)
        model_response.raise_for_status()
        with open("model_from_local_image.glb", "wb") as f:
            f.write(model_response.content)
        print("模型已下载至 model_from_local_image.glb")

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
except KeyError as e:
    print(f"响应数据解析错误: {e}")