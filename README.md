## Smart AI-Based Content Moderation System

#### Value Proposition
Content moderation is a critical requirement for businesses that operate online platforms such as social media platforms, e-commerce marketplaces, discussion forums, and video-sharing platforms. These businesses ensure that harmful, offensive, or illegal content is not published, thereby maintaining compliance with policies, protecting users, and preventing reputational damage. A main area of focus our machine learning system that can identify toxicity in online conversations, where toxicity is defined as obscene, threatning, insulting, identity attack or sexually explicit

#### Current Status Quo (Non-ML Solution)
Many companies still rely on manual moderation teams or rule-based automated filters to monitor and flag inappropriate content. However, these approaches face several challenges:

1. High operational cost – Hiring and maintaining large teams of human moderators is expensive and inefficient.

2. Scalability issues – As content volume grows, human moderation cannot keep up in real time.

3. Inconsistency in decision-making: Different moderators may interpret rules differently, leading to inconsistencies and bias.

4. Limited adaptability – Rule-based systems struggle with new types of harmful content, requiring constant manual updates.

Our AI-powered Content Moderation System leverages Deep Learning & NLP to automate moderation on text, ensuring:
Scalability – Can handle millions of content pieces in real time.
Consistency – This removes human bias from decision-making.
Faster Response Time – Immediate flagging of harmful content.
Adaptive Learning – Model continuously improves using new input data.

This system is designed to be cloud-native, scalable, and compliant with content policies, making it ideal for social media platforms, online forums, and enterprise collaboration tools.

#### Business Metrics
We will be judged on:

The hiring budget required for content moderation will go down.

Latency will be less, so customer satisfaction will increase.


### Contributors

| Name                            | Responsible for                                             | Link to their commits in this repo |
|---------------------------------|-------------------------------------------------------------|------------------------------------|
| All team members                | Design, training, cloud infrastructure, CI/CD, documentation|                                    |
| Revanth Jyothula                | Model Training                                              | https://github.com/revforyou/Content_Moderation_System/commits/main/?author=revforyou                                   |
| Krish Panchal                   | Data Pipeline                                               |https://github.com/revforyou/Content_Moderation_System/commits/main/?author=krish9164                                   |
| Gaurav Kuwar                    | Model Serving                                               |                                    |

### System diagram

![image](https://github.com/user-attachments/assets/462df420-26af-4b75-b763-0a049bccd2d8)


### Summary of outside materials

<!-- In a table, a row for each dataset, foundation model. 
Name of data/model, conditions under which it was created (ideally with links/references), 
conditions under which it may be used. -->

|                     | How it was created                                                                                                                                                  | Conditions of use                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Training Dataset    | Subset of Jigsaw toxicity dataset (`train.csv`) with `target > 0` (toxic) and `target == 0` (non-toxic); includes subtype labels like `insult`, `obscene`, `threat`, `sexual_explicit` and so on  | Public dataset, CC BY 4.0 license |
| Production Dataset  | 10% split by latest timestamp from the training dataset for evaluation                                                                                                        | Same as above                     |
| Test Dataset        | `test.csv` from Jigsaw competition (comments without labels); optionally `test_public_expanded.csv` for labeled test results                                        | Public dataset, CC BY 4.0 license |
| Base model 1 (Text) | BERT-base (uncased) fine-tuned on training dataset for binary (toxic/non-toxic) and multi-label subtype classification                                              | Custom Implementation |
            |



### Planned Infrastructure Requirements  

| Requirement       | How many/when                                     | Justification |
|------------------|---------------------------------------------------|---------------|
| `gpu_a100`      | 6-hour block, 3x per week              | High-speed training for models  and Mlflow|

| `gpu_mi100`        |                             | Cost-effective real-time inference serving |
| `m1.medium` VMs  | 3 for entire project duration                     | 1 for Data Pipeline, 1 for Evaluation, 1 for Serving) |
| Floating IPs 2x   | entire project duration | 1 for CHI@TACC (GPU Instances), 1 for KVM@TACC
| Persistent Volume (10GB) | Full duration                          | Stores training data, logs, model artifacts from MLflow) |




### Detailed design plan

#### Model training and training platforms

Strategy: Fine-tune existing models (BERT base for text) on curated moderation datasets.

Diagram section: Training scripts → ONNX converter → model registry.

Platform: Chameleon Cloud w/ gpu_a100 for training.

Justification: Reduces compute cost by leveraging transfer learning.

MLOps link: Use MLflow to track experiments, metrics, and versions.

#### Difficulty points attempted:

Use of multiple model types (text + vision).

Conversion to ONNX for cross-platform serving

#### Model serving and monitoring platforms

Strategy: Serve ONNX models using FastAPI + onnxruntime in lightweight containers.

Diagram section: Serving pods, API Gateway, Prometheus integration.

Justification: It ensures modularity, minimal latency, and GPU-optional inference.

Platform: Chameleon m1.medium VMs + Docker + ArgoCD for deployment.

Monitoring: Prometheus + Grafana dashboards; logs collected with Loki.



#### Data pipeline

Strategy:

Store incoming moderation requests in PostgreSQL.

Store training datasets in MinIO buckets (S3-compatible).

Use data versioning tools (DVC, optionally).

Diagram section: Ingest pipeline → storage → model trainer.

Justification: Enables retraining pipelines + audit trails.

#### Difficulty points attempted:

Intermediate data staging in pipeline.

Data reuse for retraining/evaluation cycles.

#### Continuous X

Strategy:

CI: GitHub Actions runs model tests, ONNX conversion, and image builds.

CD: ArgoCD triggers deployment on Chameleon after model pass.

Monitoring: Slack notifications on model failure or deploy failure.

Diagram section: CI/CD box + integration with version control.

Justification: It promotes automation and reproducibility.


