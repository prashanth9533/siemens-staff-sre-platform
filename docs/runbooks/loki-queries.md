# Loki LogQL Queries

## 1. All Sample API logs
{namespace="sample-api"}

## 2. Sample API error logs
{namespace="sample-api"} |= "ERROR"

## 3. Logs from a specific API container
{namespace="sample-api", container="sample-api"}

## 4. Successful order requests
{namespace="sample-api"} |= "/api/orders" |= "200"
