# Cloud Providers (AWS, Azure, Google Cloud)

## Arquitecturas Comparadas

### 1. AWS (Infrastructure as Code & Compute)
- **IaC First:** La creación manual desde la consola de AWS es un anti-patrón de seguridad operativa. Todo aprovisionamiento debe hacerse vía AWS CloudFormation, AWS CDK (TypeScript/Python) o Terraform (HCL).
- **IAM Principle of Least Privilege:** Roles granulares sin llaves de acceso estáticas (Access Keys) preferentemente. Los roles asumen permisos dinámicos atados a instancias EC2 o funciones Lambda, en lugar de pasar credenciales quemadas en código.
- **Micro-segmentación:** VPCs, Subnets privadas sin acceso externo a Internet para bases de datos, expuestas sólo vía Application Load Balancers (ALBs) o API Gateways en subnets públicas.

### 2. Azure (Enterprise Identity & Patterns)
- **Identity as the Perimeter:** Microsoft Entra ID (antes Azure AD). En la nube corp, el perímetro de seguridad ya no es la red (VPNs), sino la Identidad. Todo requiere autenticación RBAC y Acceso Condicional (MFA basado en riesgo).
- **Enterprise Design Patterns:** Microsoft empuja fuertemente a las arquitecturas CQS/CQRS (Command Query Responsibility Segregation) y Event Sourcing a escala global (Azure Cosmos DB) con integración masiva C#.

### 3. Google Cloud (Data & ML MLOps)
- **Pipeline-Driven AI:** Dominado por Vertex AI y BigQuery. Vertex centraliza el Jupyter Notebook, los Jobs de Training, Model Registry, y Feature Stores.
- **TFX & Kubeflow:** Los flujos de IA corren sobre *Vertex AI Pipelines* (el orchestrador serverless de Google basado en Kubeflow Pipelines). MLOps prioriza el CI/CD completo de la metadata del modelo hacia producción de la mano de Cloud Build de GCP.

## 2. Anti-patrones de Integración

- **Manual Click-Ops:** Configurar recursos (Clusters, S3/Buckets, Firewalls) a mano sin versionarlos en un repositorio de GitHub bajo `terraform/` o `aws-cdk/`. Rompe la trazabilidad y la reconstrucción en fallas críticas.
- **God-Mode IAM Roles:** Asignar `AdministratorAccess` a una Lambda solo porque está fallando al subir un archivo a un bucket S3.
- **Silos de Notebooks de IA:** En GCP/Vertex, un anti-patrón enorme es entrenar modelos sueltos en Jupyter y pasar los *weights* (.pt o .h5) manualmente por slack. Todo debe ejecutarse desde un *Pipeline* auditable.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-CLOUD-IAC-01 "The Code is the Truth"]:** "Si el recurso Cloud no existe bajo una definición Declarativa (Terraform/CDK), el recurso no existe formalmente. Todo script que altere componentes del Sistema Nervioso Gahenax en la nube debe pasar por IaC y Pipeline de CI/CD."
- **[HEURISTICA-CLOUD-IAM-01 "Ephemeral Access"]:** "Fuerza la negación de Access Keys fijas para interconexiones Server-to-Server. Utiliza protocolos OpenID Connect (OIDC) o Assumed Roles dinámicos controlando fuertemente las Policy Conditions."
- **[HEURISTICA-CLOUD-MLOPS-01 "Auditable Weights"]:** "Todos los modelos resultantes (Vertex AI u otra plataforma) deben trazar a sus datasets, configuración (Hyperparameters) y código fuente usados. Invalida cualquier modelo sin proveniencia registrada en un Feature/Model Registry."
