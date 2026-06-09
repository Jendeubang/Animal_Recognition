package com.animal.controller;

import com.animal.entity.RecognitionLog;
import com.animal.model.PredictionResult;
import com.animal.service.AnimalRecognitionService;
import com.animal.service.RecognitionLogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.*;

/**
 * 动物识别控制器
 *
 * 入口:
 *   1. GET  /               → HTML 页面
 *   2. POST /predict        → 上传图片识别 + 页面返回
 *   3. POST /api/predict    → REST API 识别（JSON 返回）
 *   4. POST /api/predict/base64 → 摄像头 Base64 识别（JSON 返回）
 *   5. GET  /api/history    → 历史记录 JSON
 *   6. GET  /api/stats      → 统计数据 JSON
 */
@Controller
public class AnimalController {

    @Autowired
    private AnimalRecognitionService recognitionService;

    @Autowired
    private RecognitionLogService logService;

    /**
     * 首页
     */
    @GetMapping("/")
    public String index(Model model) {
        boolean aiOnline = recognitionService.checkHealth();
        model.addAttribute("aiOnline", aiOnline);

        // 最近 10 条识别历史
        List<RecognitionLog> recentLogs = logService.getRecentLogs(10);
        model.addAttribute("recentLogs", recentLogs);

        // 总识别次数
        model.addAttribute("totalCount", logService.getTotalCount());

        // 统计每种动物识别次数
        List<Object[]> stats = logService.getLabelStatistics();
        model.addAttribute("labelStats", stats);

        return "index";
    }

    /**
     * REST API - 上传图片识别（JSON）
     */
    @PostMapping("/api/predict")
    @ResponseBody
    public ResponseEntity<?> predictApi(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(errorMap("请选择图片文件"));
        }

        try {
            PredictionResult result = recognitionService.recognize(file);

            // 保存日志
            String filename = file.getOriginalFilename();
            logService.saveLog(filename, result.getLabel(), result.getLabelCn(),
                    result.getConfidence(), result.getDevice(), "upload");

            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(errorMap("识别失败: " + e.getMessage()));
        }
    }

    /**
     * REST API - 摄像头 Base64 识别
     */
    @PostMapping("/api/predict/base64")
    @ResponseBody
    public ResponseEntity<?> predictBase64(@RequestBody Map<String, String> body) {
        String imageData = body.get("image");
        if (imageData == null || imageData.isEmpty()) {
            return ResponseEntity.badRequest().body(errorMap("缺少 image 字段"));
        }

        try {
            String base64Str = imageData.substring(imageData.indexOf(",") + 1);
            byte[] bytes = java.util.Base64.getDecoder().decode(base64Str);

            PredictionResult result = recognitionService.recognize(bytes, "camera.jpg", "image/jpeg");

            // 保存日志
            logService.saveLog("camera_" + System.currentTimeMillis() + ".jpg",
                    result.getLabel(), result.getLabelCn(),
                    result.getConfidence(), result.getDevice(), "camera");

            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(errorMap("识别失败: " + e.getMessage()));
        }
    }

    /**
     * HTML 页面 - 上传图片识别
     */
    @PostMapping("/predict")
    public String predictHtml(@RequestParam("file") MultipartFile file, Model model) {
        boolean aiOnline = recognitionService.checkHealth();
        model.addAttribute("aiOnline", aiOnline);

        if (file.isEmpty()) {
            model.addAttribute("error", "请选择图片文件");
            addHistoryToModel(model);
            return "index";
        }

        try {
            // Base64 用于页面回显
            byte[] bytes = file.getBytes();
            String base64 = java.util.Base64.getEncoder().encodeToString(bytes);
            String mimeType = file.getContentType() != null ? file.getContentType() : "image/jpeg";
            model.addAttribute("imageData", "data:" + mimeType + ";base64," + base64);

            // 调用 AI 识别
            PredictionResult result = recognitionService.recognize(file);
            model.addAttribute("result", result);

            // 保存日志
            logService.saveLog(file.getOriginalFilename(), result.getLabel(),
                    result.getLabelCn(), result.getConfidence(),
                    result.getDevice(), "upload");

        } catch (Exception e) {
            model.addAttribute("error", "识别失败: " + e.getMessage());
        }

        addHistoryToModel(model);
        return "index";
    }

    /**
     * API - 获取最近识别历史（JSON）
     */
    @GetMapping("/api/history")
    @ResponseBody
    public ResponseEntity<?> getHistory(@RequestParam(defaultValue = "20") int limit) {
        try {
            List<RecognitionLog> logs = logService.getRecentLogs(limit);
            return ResponseEntity.ok(logs);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(errorMap("查询失败: " + e.getMessage()));
        }
    }

    /**
     * API - 统计数据（JSON）
     */
    @GetMapping("/api/stats")
    @ResponseBody
    public ResponseEntity<?> getStats() {
        try {
            Map<String, Object> stats = new LinkedHashMap<>();
            stats.put("totalCount", logService.getTotalCount());
            stats.put("labelDistribution", logService.getLabelStatistics());
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(errorMap("查询失败: " + e.getMessage()));
        }
    }

    // ── 私有辅助方法 ──

    private void addHistoryToModel(Model model) {
        model.addAttribute("recentLogs", logService.getRecentLogs(10));
        model.addAttribute("totalCount", logService.getTotalCount());
        model.addAttribute("labelStats", logService.getLabelStatistics());
    }

    private Map<String, Object> errorMap(String message) {
        Map<String, Object> err = new HashMap<>();
        err.put("success", false);
        err.put("message", message);
        return err;
    }
}
