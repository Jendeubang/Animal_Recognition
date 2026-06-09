package com.animal.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * 与 Python AI 服务返回 JSON 结构对应的模型类
 */
public class PredictionResult {

    private boolean success;
    private String label;           // 英文标签，如 "dog"

    @SerializedName("label_cn")
    private String labelCn;         // 中文名称，如 "狗"

    @SerializedName("label_en")
    private String labelEn;         // 英文名称，如 "dog"

    private double confidence;      // 置信度 0~1
    private List<Top3Item> top3;    // Top-3 预测
    private String device;          // 运行设备 CPU/GPU

    // ── getter / setter ──
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }

    public String getLabelCn() { return labelCn; }
    public void setLabelCn(String labelCn) { this.labelCn = labelCn; }

    public String getLabelEn() { return labelEn; }
    public void setLabelEn(String labelEn) { this.labelEn = labelEn; }

    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }

    public List<Top3Item> getTop3() { return top3; }
    public void setTop3(List<Top3Item> top3) { this.top3 = top3; }

    public String getDevice() { return device; }
    public void setDevice(String device) { this.device = device; }

    /**
     * Top-3 预测内部类
     */
    public static class Top3Item {
        private String label;

        @SerializedName("label_cn")
        private String labelCn;

        @SerializedName("label_en")
        private String labelEn;

        private double confidence;

        public String getLabel() { return label; }
        public void setLabel(String label) { this.label = label; }

        public String getLabelCn() { return labelCn; }
        public void setLabelCn(String labelCn) { this.labelCn = labelCn; }

        public String getLabelEn() { return labelEn; }
        public void setLabelEn(String labelEn) { this.labelEn = labelEn; }

        public double getConfidence() { return confidence; }
        public void setConfidence(double confidence) { this.confidence = confidence; }
    }

    @Override
    public String toString() {
        return String.format("Prediction{label='%s'(%s), confidence=%.2f%%}",
                label, labelCn, confidence * 100);
    }
}
