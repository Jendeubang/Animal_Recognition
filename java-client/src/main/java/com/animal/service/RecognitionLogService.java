package com.animal.service;

import com.animal.entity.RecognitionLog;
import com.animal.repository.RecognitionLogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 识别日志业务层——记录每次识别结果 + 提供历史查询
 */
@Service
public class RecognitionLogService {

    @Autowired
    private RecognitionLogRepository logRepository;

    /**
     * 保存一条识别日志
     *
     * @param imageName 图片文件名
     * @param label     英文标签
     * @param labelCn   中文名称
     * @param confidence 置信度
     * @param device    推理设备
     * @param source    来源 (upload / camera)
     * @return 保存后的日志
     */
    public RecognitionLog saveLog(String imageName, String label, String labelCn,
                                  Double confidence, String device, String source) {
        RecognitionLog log = new RecognitionLog(imageName, label, labelCn,
                confidence, device, source);
        return logRepository.save(log);
    }

    /**
     * 保存日志（从 PredictionResult Map 提取字段）
     */
    public RecognitionLog saveLogFromResult(String imageName, Map<String, Object> resultMap, String source) {
        String label = (String) resultMap.get("label");
        String labelCn = (String) resultMap.get("labelCn");
        Double confidence = (Double) resultMap.get("confidence");
        String device = (String) resultMap.get("device");
        return saveLog(imageName, label, labelCn, confidence, device, source);
    }

    /**
     * 获取最近的 N 条识别记录
     */
    public List<RecognitionLog> getRecentLogs(int limit) {
        return logRepository.findAllByOrderByCreatedAtDesc(PageRequest.of(0, limit));
    }

    /**
     * 获取总识别次数
     */
    public long getTotalCount() {
        return logRepository.count();
    }

    /**
     * 获取统计数据：每种动物被识别了多少次
     */
    public List<Object[]> getLabelStatistics() {
        // 用 JPQL 查询，由 Repository 提供
        // 这里直接调用自定义查询
        return logRepository.findAll()
                .stream()
                .collect(java.util.stream.Collectors.groupingBy(
                        log -> log.getLabelCn(),
                        java.util.stream.Collectors.counting()))
                .entrySet()
                .stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .map(entry -> new Object[]{entry.getKey(), entry.getValue()})
                .toList();
    }
}
