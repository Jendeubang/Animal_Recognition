package com.animal.service;

import com.animal.model.PredictionResult;
import com.google.gson.Gson;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

/**
 * 调用 Python FastAPI 推理服务的客户端
 *
 * 通信方式: HTTP POST multipart/form-data → http://python-server:8000/predict
 */
@Service
public class AnimalRecognitionService {

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    private final Gson gson = new Gson();

    /**
     * 上传图片并调用 Python AI 服务识别动物
     *
     * @param file 上传的图片文件
     * @return 识别结果（包含英文标签、中文名称、置信度）
     */
    public PredictionResult recognize(MultipartFile file) throws Exception {
        return recognize(file.getBytes(),
                file.getOriginalFilename(),
                file.getContentType());
    }

    /**
     * 直接传入字节数组进行识别（用于摄像头 Base64 场景）
     *
     * @param imageBytes 图片字节数据
     * @param filename   文件名（用于 HTTP 请求，随意）
     * @param contentType 图片类型，如 "image/jpeg"
     * @return 识别结果
     */
    public PredictionResult recognize(byte[] imageBytes, String filename, String contentType) throws Exception {
        String boundary = "Boundary-" + System.currentTimeMillis();
        byte[] multipartBody = buildMultipartBody(imageBytes, filename, contentType, boundary);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(aiServiceUrl + "/predict"))
                .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                .timeout(Duration.ofSeconds(30))
                .POST(HttpRequest.BodyPublishers.ofByteArray(multipartBody))
                .build();

        HttpResponse<String> response = httpClient.send(request,
                HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("AI 服务返回错误: HTTP " + response.statusCode()
                    + " - " + response.body());
        }

        // 解析 JSON → Java 对象
        PredictionResult result = gson.fromJson(response.body(), PredictionResult.class);

        if (result == null || !result.isSuccess()) {
            throw new RuntimeException("AI 服务识别失败");
        }

        return result;
    }

    /**
     * 健康检查：检测 Python AI 服务是否在线
     */
    public boolean checkHealth() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(aiServiceUrl + "/health"))
                    .timeout(Duration.ofSeconds(5))
                    .GET()
                    .build();
            HttpResponse<String> response = httpClient.send(request,
                    HttpResponse.BodyHandlers.ofString());
            return response.statusCode() == 200;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 构建 multipart/form-data 请求体（从 MultipartFile）
     */
    private byte[] buildMultipartBody(MultipartFile file, String boundary) throws Exception {
        return buildMultipartBody(file.getBytes(), file.getOriginalFilename(),
                file.getContentType(), boundary);
    }

    /**
     * 构建 multipart/form-data 请求体（从字节数组）
     */
    private byte[] buildMultipartBody(byte[] imageBytes, String filename,
                                      String contentType, String boundary) throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();

        // 文件部分的头
        String header = "--" + boundary + "\r\n"
                + "Content-Disposition: form-data; name=\"file\"; filename=\""
                + (filename != null ? filename : "camera.jpg") + "\"\r\n"
                + "Content-Type: " + (contentType != null ? contentType : "image/jpeg") + "\r\n\r\n";
        bos.write(header.getBytes(StandardCharsets.UTF_8));

        // 文件内容
        bos.write(imageBytes);

        // 结束分隔符
        String trailer = "\r\n--" + boundary + "--\r\n";
        bos.write(trailer.getBytes(StandardCharsets.UTF_8));

        return bos.toByteArray();
    }
}
