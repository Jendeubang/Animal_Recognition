package com.animal.repository;

import com.animal.entity.RecognitionLog;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 识别日志的数据库操作层
 */
@Repository
public interface RecognitionLogRepository extends JpaRepository<RecognitionLog, Long> {

    /** 查询最近的 N 条记录（按时间倒序） */
    List<RecognitionLog> findAllByOrderByCreatedAtDesc(Pageable pageable);

    /** 按来源查询（upload / camera） */
    List<RecognitionLog> findBySourceOrderByCreatedAtDesc(String source, Pageable pageable);

    /** 按识别结果查询 */
    List<RecognitionLog> findByLabelOrderByCreatedAtDesc(String label, Pageable pageable);

    /** 统计总识别次数 */
    long count();
}
