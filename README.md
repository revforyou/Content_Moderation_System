## Smart AI-Based Content Moderation System

#### Value Proposition
Content moderation is a critical requirement for businesses that operate online platforms such as social media platforms, e-commerce marketplaces, discussion forums, and video-sharing platforms. These businesses ensure that harmful, offensive, or illegal content is not published, thereby maintaining compliance with policies, protecting users, and preventing reputational damage. A main area of focus our machine learning system that can identify toxicity in online conversations, where toxicity is defined as obscene, threatning, insulting, identity attack or sexually explicit. Our target customer is Twitter.

#### Current Status Quo (Non-ML Solution)
Twitter still relies on manual moderation teams or rule-based automated filters to monitor and flag inappropriate content. However, these approaches face several challenges:

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

Reduce moderation team size (cost savings)

Improve moderation latency (increase user satisfaction)


### Contributors

| Name                            | Responsible for                                             | Link to their commits in this repo |
|---------------------------------|-------------------------------------------------------------|------------------------------------|
| All team members                | Design, training, cloud infrastructure, CI/CD, documentation|                                    |
| Revanth Jyothula                | Model Training                                              | https://github.com/revforyou/Content_Moderation_System/commits/main/?author=revforyou                                   |
| Krish Panchal                   | Data Pipeline                                               |https://github.com/revforyou/Content_Moderation_System/commits/main/?author=krish9164                                   |
| Gaurav Kuwar                    | Model Serving                                               |                                    |

### System diagram

[Raw Dataset (Kaggle: Jigsaw + Annotations)]
↓
[Offline Data Pipeline (ETL: Pandas + Cleaning + Aggregation)]
↓
[Train/Val Split + Timestamp Ordering]
↓
[Model Training (BERT)]
↓
[Model Registry (MLflow + MinIO)]
↓
[Container Build (ONNX + Kaniko via Argo Workflows)]
↓
[Staged Deployment (ArgoCD + Helm: Staging → Canary → Prod)]
↓
[Inference API (FastAPI + ONNXRuntime)]
↕
[Simulated Production Requests (Python Script)]
↕
[Monitoring & Logging (Prometheus + Grafana)]
↕
[MLflow Feedback Loop for Weekly Retraining]




### Summary of outside materials

<!-- In a table, a row for each dataset, foundation model. 
Name of data/model, conditions under which it was created (ideally with links/references), 
conditions under which it may be used. -->

https://www.kaggle.com/competitions/jigsaw-unintended-bias-in-toxicity-classification/data

The comments in this dataset come from an archive of the Civil Comments platform, a commenting plugin for independent news sites. These public comments were created from 2015 - 2017 and appeared on approximately 50 English-language news sites across the world. When Civil Comments shut down in 2017, they chose to make the public comments available in a lasting open archive to enable future research. The original data, published on figshare, includes the public comment text, some associated metadata such as article IDs, timestamps and commenter-generated "civility" labels, but does not include user ids. Jigsaw extended this dataset by adding additional labels for toxicity and identity mentions.

|                     | How it was created                                                                                                                                                  | Conditions of use                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Training Dataset    | Subset of Jigsaw toxicity dataset (`train.csv`) with `target > 0` (toxic) and `target == 0` (non-toxic); includes subtype labels like `insult`, `obscene`, `threat`, `sexual_explicit` and so on  | Public dataset, CC BY 4.0 license |
| Production Dataset  | 10% split by latest timestamp from the training dataset for evaluation                                                                                                        | Same as above                     |
| Test Dataset        | `test.csv` from Jigsaw competition (comments without labels); optionally `test_public_expanded.csv` for labeled test results                                        | Public dataset, CC BY 4.0 license |
| Base model 1 (Text) | BERT-base (uncased) fine-tuned on training dataset for binary (toxic/non-toxic) and multi-label subtype classification                                              | Custom Implementation |
            |


### Planned Infrastructure
| Resource                 | Allocation Plan                          | Justification                                                               |
| ------------------------ | ---------------------------------------- | --------------------------------------------------------------------------- |
| `gpu_a100`               | 6-hour blocks, 2x per week               | Needed for fast multi-GPU training runs and MLflow experiment tracking      |
| `gpu_mi100`              | On-demand, during model evaluation phase | Cost-effective resource for real-time inference and model testing           |
| `m1.medium` VMs          | 3 VMs for full project duration          | Dedicated roles: (1) Data Pipeline, (2) Evaluation Scripts, (3) |
| Floating IPs (2x)        | Throughout project                       | (1) Access CHI\@TACC GPU training nodes, (2) Serve from KVM\@TACC endpoints |
| Persistent Volume (10GB) | Entire duration                          | Stores datasets, model checkpoints, training logs, and MLflow artifacts     |





### Detailed design plan

#### Model training and training platforms

Strategy:
The project focuses on detecting toxic comments in social media using a fine-tuned transformer-based language model. It integrates real-time and batch pipelines for data ingestion, model retraining, and deployment using MLOps best practices. We simulate production traffic to mimic a live environment, ensuring a realistic model deployment and feedback loop. The model is retrained weekly using the latest labeled and production data, with versioning and promotion handled via Argo Workflows and MLflow.


Relevant Parts of the Diagram:

Model Training & Retraining: Scheduled weekly using Ray and tracked via MLflow
ETL Pipeline: Docker Compose-based ingestion and transformation into object store
Model Registry: MLflow + MinIO used for artifact management and alias tagging
CI/CD Deployment: Argo Workflows automate container image build, test, and Helm-based rollout to staging/canary/production
Serving: Inference API served on Kubernetes via FastAPI container
Online Data Simulation: Python script streams production.csv to the REST endpoint
Monitoring & Feedback Loop: Production predictions can be routed for re-labeling and used in retraining


Justification for Strategy:

Transformer Model (e.g., BERT): Well-suited for text classification; handles large-scale social media data
ETL with Docker Compose: Easy reproducibility and encapsulation of extract-transform-load steps
Object Store (MinIO via RClone): Efficient persistent storage accessible across nodes and workflows
MLflow for Experiment Tracking: Provides audit trails and comparison across model versions
Argo Workflows: Modular, repeatable automation for training, promotion, and deployment
Ray Train: Enables multi-node distributed training with built-in fault tolerance
Canary + Staging + Prod: Follows industry-standard CI/CD for safe deployment transitions


Unit 2 – Cloud Computing: We used Chameleon Cloud’s KVM@TACC for provisioning three nodes and persistent storage.

Unit 3 – DevOps: Terraform provisioned GPU/VM nodes. Ansible used for installation Kubernetes, and ArgoCD handled continuous deployment to staging/canary/production environments.

Unit 4 – Model Training: BERT was trained on Jigsaw dataset using PyTorch using A100 gpu.

Unit 5 – MLOps Platform: MLflow managed model versions, tracked experiments, and stored metrics/artifacts in MinIO.

Unit 6 – Serving: FastAPI container exposed a /predict endpoint. Canary/staging/production environments were created with Helm.

Unit 7 – Monitoring: A simulation script streams data from production.csv to emulate real-world load. Logs and responses are tracked.

Unit 8 – Data Pipeline: Docker Compose ETL system downloaded, preprocessed, split, and loaded the Jigsaw dataset into persistent object store. Provisioned block volume to store model artifacts and logs. Wrote a script to generate send data from production set to inference endpoin, similar to what it could be expected to see in production use.

#### Difficulty points attempted:

Develop multiple options for serving.

Monitor for data drift.

#### Model serving and monitoring platforms





#### Data pipeline

In the data_pipeline part of our project, we built a full ETL (Extract, Transform, Load) pipeline to handle the Jigsaw toxicity dataset. Using Docker Compose, we automated downloading the dataset from Kaggle, transforming it by splitting into train/val/production sets using timestamps, and uploading it to Chameleon’s object store using rclone. This object store was then mounted as a virtual file system on our compute nodes, allowing all services (like training or inference) to access the latest data without duplication. The pipeline is reproducible and portable, making it easy to rerun or scale as needed. 

We cleaned and prepared the dataset by combining individual annotations using the most common label (mode). Unwanted columns were removed, and missing values were filled—strings with "none" and numbers with 0. We also fixed date formats and sorted the data by time. Then, we split it into training (90%) and validation (10%) based on the latest timestamps to reflect a real-world scenario. 


#### Continuous X

We automated our machine learning system's setup and deployment using tools like Terraform, Ansible, Helm, ArgoCD, and Argo Workflows. We used Terraform to create four virtual machines (for training, inference, data pipeline, and monitoring), and Ansible to install Kubernetes and important tools like MLflow and ArgoCD. Helm helped us define how our app should run on Kubernetes. With ArgoCD, any changes pushed to Git were automatically deployed to staging, canary, and production environments. Argo Workflows managed tasks like training, building Docker images, and promoting the model to production. This setup helped us deploy and update the system easily, reliably, and in a repeatable way.


#### Difficulty points attempted:

Intermediate data staging in pipeline.

Data reuse for retraining/evaluation cycles.
