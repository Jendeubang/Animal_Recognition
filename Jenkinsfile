// ================================================================
// 动物识别系统 - Jenkins Pipeline
// 学号姓名: ____________
// ================================================================
pipeline {
    agent any

    // ── 环境变量 ──
    environment {
        PYTHON_DIR = "${WORKSPACE}/python"
        JAVA_DIR   = "${WORKSPACE}/java-client"
    }

    // ── 质量门禁：任何阶段失败即中止 ──
    options {
        timestamps()                // 控制台输出时间戳
        buildDiscarder(logRotator(numToKeepStr: '10'))  // 保留最近10次构建
        disableConcurrentBuilds()   // 禁止并发构建
    }

    // ── 触发方式：代码推送 + 手动触发 ──
    triggers {
        pollSCM('H/5 * * * *')      // 每5分钟检查代码变更
    }

    stages {
        // ── 阶段1: 拉取代码 ──
        stage('📥 拉取代码') {
            steps {
                checkout scm
                echo "✅ 代码已拉取，分支: ${env.BRANCH_NAME}"
            }
        }

        // ── 阶段2: 安装 Python 依赖 ──
        stage('📦 安装 Python 依赖') {
            steps {
                dir("${PYTHON_DIR}") {
                    sh 'pip install --upgrade pip -q'
                    sh 'pip install -r requirements.txt -q'
                    echo "✅ Python 依赖安装完成"
                }
            }
        }

        // ── 阶段3: Python 语法检查 ──
        stage('🔍 静态检查') {
            steps {
                dir("${PYTHON_DIR}") {
                    sh 'python -m py_compile train.py'
                    sh 'python -m py_compile predict_api.py'
                    echo "✅ Python 语法检查通过"
                }
            }
        }

        // ── 阶段4: 执行 Python 测试 ──
        stage('🧪 执行 Python 测试') {
            steps {
                dir("${WORKSPACE}") {
                    sh 'python -m pytest python/test_ci.py -v --tb=short'
                }
            }
            post {
                failure {
                    // 质量门禁：测试失败时中止流水线
                    error "❌ 测试失败，流水线中止（质量门禁触发）"
                }
            }
        }

        // ── 阶段5: Java 编译 ──
        stage('☕ Java 编译') {
            steps {
                dir("${JAVA_DIR}") {
                    sh 'mvn compile -q'
                    echo "✅ Java 编译通过"
                }
            }
        }

        // ── 阶段6: 打包归档 ──
        stage('📦 打包归档') {
            steps {
                dir("${JAVA_DIR}") {
                    sh 'mvn package -DskipTests -q'
                }
                archiveArtifacts artifacts: 'java-client/target/*.jar',
                             fingerprint: true
                echo "✅ 构建产物已归档"
            }
        }
    }

    // ── 构建后通知 ──
    post {
        success {
            echo "🎉 流水线全部通过！"
            // 可在这里配置邮件通知
            // mail to: 'team@example.com',
            //      subject: "✅ CI 成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            //      body: "所有阶段通过"
        }
        failure {
            echo "❌ 流水线失败，请检查日志"
            // mail to: 'team@example.com',
            //      subject: "❌ CI 失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            //      body: "请查看 ${env.BUILD_URL} 获取详情"
        }
    }
}
