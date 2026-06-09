package com.animal;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * CI/CD 流水线测试
 * 验证 Spring Boot 应用能正常启动
 */
@SpringBootTest
class AnimalRecognitionApplicationTests {

    @Test
    void contextLoads() {
        // 验证 Spring 上下文能正常加载
        System.out.println("✅ Spring Boot 上下文加载成功");
    }
}
