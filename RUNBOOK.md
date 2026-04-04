# Incident Response Runbook 📖

_Last Updated: 2026-04-04 21:25_

This guide is for the 3 AM on-call engineer. Follow these steps calmly.

---

## 🚨 Incident 1: SERVICE_DOWN

**Symptoms**: `monitor_health.py` reports `ENDPOINT DOWN`.
**Dashboard**: "Traffic" chart drops to zero. "System Up" is 0.

### 🛠 Resolution Steps:

1.  **Check Docker Status**:
    ```bash
    docker compose ps
    ```
2.  **Restart the fleet**:
    ```bash
    docker compose restart app nginx
    ```
3.  **Check Postgres Health**: If `db` is down, check disk space:
    ```bash
    df -h
    ```

---

## 🚨 Incident 2: HIGH_ERROR_RATE (500s)

**Symptoms**: Sentry alerts firing. Monitor reports `💥 HIGH ERROR RATE`.
**Dashboard**: "Error Rate" chart spikes (red line).

### 🛠 Resolution Steps:

1.  **Inspect Logs**:
    ```bash
    docker compose logs -f app | grep ERROR
    ```
2.  **Check Sentry**: Log in to Sentry to find the specific line of code causing the crash.
3.  **Revert Last Deploy**: If this happened after a git pull, revert immediately.

---

## 🚨 Incident 3: HIGH_LATENCY / SATURATION

**Symptoms**: Users reporting "The app is slow."
**Dashboard**: "Latency" p95 is > 1000ms. "CPU/RAM" is > 90%.

### 🛠 Resolution Steps:

1.  **Identify the slow route**: Check Grafana "Latency by Route" chart.
2.  **Check Redis**: Is the cache working?
    ```bash
    docker compose exec redis redis-cli ping
    ```
3.  **Scale UP**: Add more replicas if saturation is high:
    ```bash
    docker compose up -d --scale app=5
    ```

---

## 🚑 Emergency Contact

- **Senior Architect**: [EMAIL_ADDRESS]
- **Database Lead**: [EMAIL_ADDRESS]
