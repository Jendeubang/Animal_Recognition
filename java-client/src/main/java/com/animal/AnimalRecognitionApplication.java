package com.animal;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 动物识别系统 - Java Spring Boot 入口
 *
 * 启动后访问: http://localhost:8080
 * 上传图片后自动调 Python AI 服务进行识别
 */
@SpringBootApplication
public class AnimalRecognitionApplication {

    public static void main(String[] args) {
        SpringApplication.run(AnimalRecognitionApplication.class, args);
        System.out.println("======================================");
        System.out.println("  🐾 动物识别系统已启动");
        System.out.println("  访问: http://localhost:8080");
        System.out.println("  Python AI 服务地址: http://localhost:8000");
        System.out.println("======================================");
    }
}
