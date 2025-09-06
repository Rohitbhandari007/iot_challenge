# IoT Challenge Setup Guide

## Cluster Setup
1. Create a cluster using k3d:
    ```bash
    k3d cluster create iot
    ```

## Service Deployment

### Backend Service (FastAPI)
1. Build the FastAPI Docker image:
    ```bash
    cd service/fastapi
    docker build -t fastapi-demo:latest .
    ```

2. Import the image to the k3d cluster:
    ```bash
    k3d image import fastapi-demo:latest -c iot
    ```

3. Deploy the API resources:
    ```bash
    kubectl apply -f k8s/api/
    ```

### Frontend Service (Next.js)
1. Build the UI Docker image:
    ```bash
    cd service/ui/ui-app
    docker build -t nextjs-demo:latest .
    ```

2. Import the image to the k3d cluster:
    ```bash
    k3d image import nextjs-demo:latest -c iot
    ```

## Database Setup

### PostgreSQL Configuration
1. Identify the Postgres pod:
    ```bash
    kubectl get pods -l app=postgres
    ```

2. Connect to the database:
    ```bash
    kubectl exec -it <postgres-pod-name> -- psql -U postgres -d iot_pv
    ```

3. Initialize the database schema:
    ```sql
    CREATE TABLE pv_readings (
      timestamp timestamptz NOT NULL,
      time timestamptz NOT NULL,
      device_id text NOT NULL,
      site text NOT NULL,
      lat double precision NOT NULL,
      lon double precision NOT NULL,
      ac_power double precision NOT NULL,
      dc_voltage double precision NOT NULL,
      dc_current double precision NOT NULL,
      temperature_module double precision NOT NULL,
      temperature_ambient double precision NOT NULL,
      operational boolean NOT NULL,
      fault_code integer,
      metadata jsonb
    );
    ```

## Accessing the Application

### Backend API
```bash
kubectl port-forward svc/fastapi 8000:80
```
Access the API documentation at: http://localhost:8000/docs

### Frontend UI
```bash
kubectl port-forward svc/nextjs 3000:80
```
Access the UI at: http://localhost:3000

## Additional Information

- The Kubernetes configuration files are located in the `k8s/` directory
- Backend code is available in `service/api/`
- Frontend code is available in `service/ui/`
- The repository includes an autoscaling demo for the FastAPI service
- Ingress configuration is provided but requires additional setup

> Note: Integration with Grafana/Tafekik for advanced dashboarding is planned for future implementation.


