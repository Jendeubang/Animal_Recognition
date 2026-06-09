-- 动物识别日志表（MySQL / PostgreSQL 通用）
CREATE TABLE IF NOT EXISTS recognition_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    image_name  VARCHAR(255)    NOT NULL COMMENT '图片文件名',
    label       VARCHAR(50)     NOT NULL COMMENT '识别的英文标签',
    label_cn    VARCHAR(50)     NOT NULL COMMENT '中文名称',
    confidence  DECIMAL(5,4)    NOT NULL COMMENT '置信度 0~1',
    device      VARCHAR(10)     DEFAULT 'CPU' COMMENT '推理设备',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '识别时间',

    INDEX idx_created_at (created_at),
    INDEX idx_label (label)
) COMMENT='动物识别历史记录';
