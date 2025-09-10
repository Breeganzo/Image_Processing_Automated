graph TD
    A[User Uploads Image] --> B[S3 Bucket - Original Images]
    B --> C[S3 Event Trigger]
    C --> D[Lambda: Image Processor]
    D --> E[Resize to 256x256]
    E --> F[SQS Queue - Rotation Tasks]
    F --> G[Lambda: Rotation Worker]
    G --> H[Generate 4 Rotations]
    H --> I[S3 Bucket - Augmented Images]
    
    I --> J[90-degree folder]
    I --> K[180-degree folder]
    I --> L[270-degree folder]
    I --> M[360-degree folder]
    
    subgraph "AWS Services Used"
        N[S3 - Storage]
        O[Lambda - Processing]
        P[SQS - Message Queue]
        Q[IAM - Permissions]
        R[CloudWatch - Monitoring]
    end
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style F fill:#f3e5f5
    style G fill:#e8f5e8
    style I fill:#fff8e1
