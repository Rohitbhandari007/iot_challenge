# IoT Challenge Setup Guide

## Cluster Setup
1. Create a cluster using k3d:
    ```bash
    k3d cluster create iot
    ```

## Service Deployment

### Build and Import FastAPI Service
1. Build the FastAPI Docker image:
    ```bash
    cd service/fastapi
    docker build -t fastapi-demo:latest .
    ```

2. Import the image to the k3d cluster:
    ```bash
    k3d image import fastapi-demo:latest -c iot
    ```

### Deploy Kubernetes Resources
1. Apply all Kubernetes configurations:
    ```bash
    kubectl apply -f k8s/api/
    ```

## Database Setup

### Connect to PostgreSQL
1. Find the Postgres pod:
    ```bash
    kubectl get pods -l app=postgres
    ```

2. Connect to the database:
    ```bash
    kubectl exec -it <postgres-pod-name> -- psql -U postgres -d iot_pv
    ```

### Create Database Schema
Execute the following SQL to create the PV readings table:
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

## Testing the Application
To access the FastAPI service locally:
```bash
kubectl port-forward svc/fastapi 8000:80
```
You can now access the API at http://localhost:8000