import requests
import time
import os

# 设置 API Key（从环境变量读取或直接填写）
MESHY_API_KEY = os.getenv("MESHY_API_KEY") or "your_api_key_here"
headers = {
    "Authorization": f"Bearer {MESHY_API_KEY}",
    "Content-Type": "application/json"
}

# 指定图片 URL（IKEA 竹碗的公开 URL）
image_url = "https://www.ikea.com/eg/en/images/products/blanda-matt-serving-bowl-bamboo__0711988_pe728640_s5.jpg"

# Image-to-3D 请求 payload
payload = {
    "image_url": image_url,  # 使用公开可访问的图片 URL
    "enable_pbr": True,      # 启用 PBR 材质（更真实的纹理）
    "should_remesh": True,   # 重建网格以优化模型
    "should_texture": True   # 自动生成纹理
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
            model_url = task_data["model_urls"]["glb"]  # 获取 glb 格式模型
            print(f"模型下载链接: {model_url}")
            break
        elif status in ["FAILED", "EXPIRED"]:
            print(f"任务失败或过期: {status}")
            break
        else:
            print("任务仍在进行中，5秒后重试...")
            time.sleep(5)

    # 下载生成的模型
    if status == "SUCCEEDED":
        model_response = requests.get(model_url)
        model_response.raise_for_status()
        with open("bamboo_bowl_from_image.glb", "wb") as f:
            f.write(model_response.content)
        print("模型已下载至 bamboo_bowl_from_image.glb")

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
except KeyError as e:
    print(f"响应数据解析错误: {e}")