# Sample API – Service Level Objective (SLO)

## 1. Objective

The objective is to maintain reliable availability and successful
request processing for the Sample Orders API.

## 2. Service Level Indicator (SLI)

The primary SLI is the API request success ratio.

Formula:

Successful HTTP 200 requests / Total API requests

Prometheus metric:

sample_api:request_success_ratio:rate5m

## 3. Service Level Objective (SLO)

Target: 99.9% successful API requests.

The configured target is:

sample_api:slo_target = 0.999

## 4. Error Budget

Allowed error ratio: 0.1%.

Prometheus metric:

sample_api:error_budget_ratio

Remaining budget metric:

sample_api:error_budget_remaining_ratio

## 5. Monitoring

Prometheus evaluates the SLI and records the SLO-related metrics.
Grafana displays API success rate and reliability indicators.

## 6. Current Implementation Scope

The current SLI uses a rolling 5-minute request window.
It demonstrates success-rate and error-budget calculations.

It does not yet represent a validated rolling 30-day SLO.
Long-term compliance requires sufficient historical metrics data.

## 7. Validation

The implementation was tested by generating 20 successful API requests.

Observed results:
- Request success ratio: 100%
- SLO target: 99.9%
- Error budget: 0.1%
- Remaining error budget: 100%
