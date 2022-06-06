<!--ig-start-->
### 实例组作为日志源

1. 登录 Log Hub 控制台。
2. 在左侧边栏中的 **日志分析管道** 下，选择**应用日志**。
3. 单击在**前提条件**期间创建的应用程序管道。
4. 转到 **Permission** 选项卡并复制提供的 JSON 策略。
5. 在 **AWS Console > IAM > Policies** 进行如下操作。

    - 点击**Create Policy**，选择**JSON**并替换文本块内的所有内容。请记住用您的帐户 ID 替换 `<YOUR ACCOUNT ID>`。
    - 选择**下一步**，再选择 **下一步**，然后输入此策略的名称。例如：**`loghub-ec2-policy`**。
    - 将策略附加到您的 EC2 实例角色，以允许日志代理有权将日志发送到应用程序日志管道。

6. 单击**创建日志摄取**下拉菜单，然后选择 "从实例组"。
7. 选择**选择存在**，然后选择**下一步**。
8. 选择您在**前提条件**中创建的实例组，然后选择**下一步**。
9. 选择**选择已存在**，并选择在先前设置中创建的日志配置。
10. 选择**下一步**，然后选择**创建**。

<!--ig-end-->

<!--eks-start-->
### EKS 集群作为日志源

1. 登录 Log Hub 控制台。
2. 在左侧边栏中的 **日志源** 下，选择 **EKS 集群**。
3. 单击已导入为日志源的 EKS 集群。
4. 转到 **应用日志摄取** 选项卡，然后单击 **创建日志摄取**。
    - 选择"选择已存在" 并选择在**前提条件**中创建的应用程序管道。选择**下一步**。
    - 选择之前设置中创建的日志配置，然后选择**下一步**。
    - 根据需要添加标签，然后选择**创建**完成创建摄取。
5. 按照 Log Hub 生成的指南部署 Fluent-bit 日志代理。
    - 选择刚刚创建的应用日志摄取。
    - 按照 **DaemonSet** 或 **Sidecar** 指南部署日志代理。

<!--eks-end-->

<!--s3-start-->
### S3 存储桶作为日志源

1. 登录 Log Hub 控制台。
2. 在左侧边栏中的 **日志分析管道** 下，选择 **应用日志**。
3. 单击在**前提条件**期间创建的应用程序管道。
4. 单击 **创建日志摄取**下拉菜单，然后选择 **从S3存储桶**。
5. 填写所有表单字段以指定 S3 日志源。选择**下一步**。
6. 选择之前设置中创建的日志配置，然后选择**下一步**。
7. 根据需要添加标签，然后选择**创建**完成创建摄取。

<!--s3-end-->