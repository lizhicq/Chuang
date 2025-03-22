假设你已经通过 Meshy API 创建了一个 3D 模型生成任务，并获得了任务 ID（例如 YOUR_TASK_ID）。你可以使用以下步骤通过 API 获取任务详情并提取预览视频的 URL。

 1. API 端点使用 GET 请求访问以下端点来获取任务详情：
/openapi/v1/tasks/0195bc1d-c26a-7943-9317-a7d79fe05c17

 2. 请求示例使用 curl 发送 GET 请求，示例如下：
curl -X GET \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.meshy.ai/openapi/v1/tasks/YOUR_TASK_ID

 • 说明：
 • -H "Authorization: Bearer YOUR_API_KEY"：需要在请求头中包含你的 Meshy API 密钥，用于身份验证。
 • YOUR_TASK_ID：替换为实际的任务 ID。
 3. 响应示例API 将返回一个 JSON 格式的响应，包含任务的详细信息。以下是一个简化的响应示例：
{
  "id": "YOUR_TASK_ID",
  "model_urls": {
    "glb": "https://assets.meshy.ai/.../model.glb",
    "fbx": "https://assets.meshy.ai/.../model.fbx"
  },
  "thumbnail_url": "https://assets.meshy.ai/.../preview.png",
  "preview_video_url": "https://assets.meshy.ai/.../preview.mp4",
  "status": "SUCCEEDED",
  "progress": 100,
  "created_at": 1692771650657,
  "finished_at": 1692771669037
}

 • 关键字段：
 • "preview_video_url"：预览视频的 URL，可以通过此链接下载或播放视频。
 • "status"：任务状态，需为 "SUCCEEDED" 表示任务已完成。
 • "model_urls"：生成的 3D 模型文件 URL（如 .glb 或 .fbx 格式）。
 • "thumbnail_url"：模型的缩略图 URL，通常是静态图片。
 4. 视频内容
 • 预览视频通常是模型的旋转视图或简单动画，展示模型的外观和纹理细节。
 • 视频格式可能为 MP4 或其他常见格式，具体取决于 Meshy 的实现。