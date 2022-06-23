## Веб-сервер на сокетах

Данный веб-сервер реализован на базе сокетов без использования специальных библиотек для сетевых запросов.

Точкой входа является файл `httpd.py`, который и помогает запускать тесты:

```commandline
python httpd.py -w=<workers> -p=<port> -r=<document root>
```

В файле `httptest.py` хранятся тесты для данного сервера, которые можно запустить при помощи команды:

```commandline
python -m unittest httptest.py
```

### Нагрузочное тестирование

```commandline
wrk -t6 -c20 -d2m http://localhost:8080/
```

### Результаты нагрузочного тестирования wrk

```
Running 2m test @ http://localhost:8080/
  6 threads and 20 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   617.06us  374.12us  27.64ms   97.63%
    Req/Sec     1.81k     1.25k    4.10k    64.86%
  65470 requests in 2.00m, 9.68MB read
  Socket errors: connect 0, read 28, write 0, timeout 17
Requests/sec:    545.32
Transfer/sec:     82.54KB
```
