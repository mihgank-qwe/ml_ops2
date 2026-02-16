# Runbook — реагирование на инциденты

Руководство по реагированию на алерты мониторинга Credit Scoring API.

---

## Алерты по метрикам (Prometheus)

### CreditScoringAPIDown

**Severity:** critical  
**Описание:** Поды API не отдают метрики более 2 минут.

**Действия:**

1. Проверить статус подов:
   ```bash
   kubectl get pods -n production -l app=credit-scoring-api
   kubectl get pods -n staging -l app=credit-scoring-api
   ```

2. Проверить логи:
   ```bash
   kubectl logs -n production -l app=credit-scoring-api --tail=100
   ```

3. Проверить события:
   ```bash
   kubectl get events -n production --sort-by='.lastTimestamp'
   ```

4. Перезапустить deployment при необходимости:
   ```bash
   kubectl rollout restart deployment/credit-scoring-api -n production
   kubectl rollout status deployment/credit-scoring-api -n production
   ```

5. Проверить ресурсы нод:
   ```bash
   kubectl top nodes
   kubectl describe nodes
   ```

---

### CreditScoringAPIHighLatency

**Severity:** warning  
**Описание:** p99 latency > 2 секунд.

**Действия:**

1. Определить проблемный endpoint (labels в алерте).

2. Проверить нагрузку:
   ```bash
   kubectl top pods -n production -l app=credit-scoring-api
   ```

3. Увеличить реплики при нехватке мощности:
   ```bash
   kubectl scale deployment/credit-scoring-api -n production --replicas=4
   ```

4. Проверить модель и данные — возможна деградация inference.

5. Рассмотреть увеличение ресурсов в deployment (CPU/memory limits).

---

### CreditScoringAPIHighErrorRate

**Severity:** critical  
**Описание:** Более 5% запросов возвращают 5xx.

**Действия:**

1. Проверить логи на ошибки:
   ```bash
   kubectl logs -n production -l app=credit-scoring-api --tail=200 | grep -i error
   ```

2. В Loki/Grafana: `{app="credit-scoring-api"} |= "error"` или `|= "500"`

3. Проверить загрузку модели:
   - Ошибка «Модель не загружена» — проверить DVC pull, путь к модели в ConfigMap.

4. Проверить входные данные — возможны некорректные запросы.

5. Откатить deployment при необходимости:
   ```bash
   kubectl rollout undo deployment/credit-scoring-api -n production
   ```

---

### CreditScoringAPIHighMemory

**Severity:** warning  
**Описание:** Pod использует > 450MB RSS.

**Действия:**

1. Проверить утечки памяти — сравнить с baseline.

2. Увеличить memory limit в deployment при необходимости.

3. Проверить размер модели и кэширование.

---

### TargetDown

**Severity:** critical  
**Описание:** Любой scrape target недоступен.

**Действия:**

1. Определить target из labels (job, instance).

2. Для credit-scoring-api — см. CreditScoringAPIDown.

3. Для Prometheus — проверить под в namespace monitoring.

4. Для kubernetes-nodes — проверить состояние нод кластера.

---

## Алерты по логам (Loki / Grafana)

Настроить в Grafana: Alerting → Alert rules → New alert rule.

**Пример: ошибки в логах API**

- **Query:** `count_over_time({app="credit-scoring-api"} |= "error" [5m]) > 10`
- **Condition:** когда количество строк с "error" за 5 мин > 10

**Действия при срабатывании:**

1. Открыть Explore → Loki, запрос `{app="credit-scoring-api"} |= "error"`.

2. Проанализировать стек-трейсы и контекст.

3. Следовать процедурам для соответствующих ошибок (см. CreditScoringAPIHighErrorRate).

---

## Эскалация

| Уровень | Действие |
|---------|----------|
| L1 | Проверка по runbook, базовые команды |
| L2 | Глубокий анализ, изменение конфигурации |
| L3 | Откат, масштабирование, привлечение разработки |

**Контакты:** указать в настройках Alertmanager / Grafana contact points.

---

## Полезные команды

```bash
# Статус deployment
kubectl rollout status deployment/credit-scoring-api -n production

# Описание пода
kubectl describe pod -n production -l app=credit-scoring-api

# Логи с предыдущего контейнера (после crash)
kubectl logs -n production -l app=credit-scoring-api --previous

# Ресурсы
kubectl top pods -n production -l app=credit-scoring-api
kubectl top nodes
```
