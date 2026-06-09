package com.animal.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 动物识别日志——每次识别都会记录到 MySQL
 */
@Entity
@Table(name = "recognition_log")
public class RecognitionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 图片文件名（上传的文件名 或 "camera.jpg"） */
    @Column(name = "image_name", length = 255, nullable = false)
    private String imageName;

    /** 识别的英文标签，如 "dog" */
    @Column(name = "label", length = 50, nullable = false)
    private String label;

    /** 中文名称，如 "狗" */
    @Column(name = "label_cn", length = 50, nullable = false)
    private String labelCn;

    /** 置信度 0~1 */
    @Column(name = "confidence", nullable = false)
    private Double confidence;

    /** 推理设备 CPU / GPU */
    @Column(name = "device", length = 10)
    private String device;

    /** 来源：upload / camera */
    @Column(name = "source", length = 20, nullable = false)
    private String source;

    /** 识别时间 */
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    // ── 构造方法 ──
    public RecognitionLog() {}

    public RecognitionLog(String imageName, String label, String labelCn,
                          Double confidence, String device, String source) {
        this.imageName = imageName;
        this.label = label;
        this.labelCn = labelCn;
        this.confidence = confidence;
        this.device = device;
        this.source = source;
    }

    // ── getter / setter ──
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getImageName() { return imageName; }
    public void setImageName(String imageName) { this.imageName = imageName; }

    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }

    public String getLabelCn() { return labelCn; }
    public void setLabelCn(String labelCn) { this.labelCn = labelCn; }

    public Double getConfidence() { return confidence; }
    public void setConfidence(Double confidence) { this.confidence = confidence; }

    public String getDevice() { return device; }
    public void setDevice(String device) { this.device = device; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
