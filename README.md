# aioinfluxdb

[![PyPI](https://img.shields.io/pypi/v/aioinfluxdb?style=flat-square&logo=pypi)](https://pypi.org/project/aioinfluxdb/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aioinfluxdb?style=flat-square&logo=pypi)](https://pypi.org/project/aioinfluxdb/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/aioinfluxdb?style=flat-square&logo=pypi)](https://pypi.org/project/aioinfluxdb/)
[![PyPI - Status](https://img.shields.io/pypi/status/aioinfluxdb?style=flat-square)](https://pypi.org/project/aioinfluxdb/)
![Codecov](https://img.shields.io/codecov/c/gh/isac322/aioinfluxdb?style=flat-square&logo=codecov)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/isac322/aioinfluxdb/CI?style=flat-square&logo=github)
![License](https://img.shields.io/github/license/isac322/aioinfluxdb?style=flat-square&logo=github)
![GitHub last commit](https://img.shields.io/github/last-commit/isac322/aioinfluxdb?logo=github&style=flat-square)
![Dependabpt Status](https://flat.badgen.net/github/dependabot/isac322/aioinfluxdb?icon=github)

The Python client for InfluxDB v2 supports asyncio.

**This is early-stage project**

## Why aioinfluxdb?

[The official client](https://pypi.org/project/influxdb-client/) does not supports asyncio that can get significant
performance. and [aioinflux](https://pypi.org/project/aioinflux/) does not supports InfluxDB v2.

## Feature table

| Feature               | Sub category                                                 | ✅ / ⚠ / 🚧 |
|:----------------------|:-------------------------------------------------------------|:----------:|
| Query                 | Query Data                                                   |     ✅      |
| Query                 | Analyzer Flux Query                                          |     🚧     |
| Query                 | Generate AST from Query                                      |     🚧     |
| Query                 | Retrieve query suggestions                                   |     🚧     |
| Query                 | Retrieve query suggestions <br /> for a branching suggestion |     🚧     |
| Write                 |                                                              |     ✅      |
| Buckets               |                                                              |     ⚠      |
| Dashboards            |                                                              |     🚧     |
| Tasks                 |                                                              |     🚧     |
| Resources             |                                                              |     🚧     |
| Authorizations        |                                                              |     🚧     |
| Organizations         |                                                              |     ⚠      |
| Users                 |                                                              |     🚧     |
| Health                |                                                              |     🚧     |
| Ping                  |                                                              |     ✅      |
| Ready                 |                                                              |     🚧     |
| Routes                |                                                              |     🚧     |
| Backup                |                                                              |     🚧     |
| Cells                 |                                                              |     🚧     |
| Checks                |                                                              |     🚧     |
| DBRPs                 |                                                              |     🚧     |
| Delete                |                                                              |     🚧     |
| Labels                |                                                              |     🚧     |
| NotificationEndpoints |                                                              |     🚧     |
| NotificationRules     |                                                              |     🚧     |
| Restore               |                                                              |     🚧     |
| Rules                 |                                                              |     🚧     |
| Scraper Targets       |                                                              |     🚧     |
| Secrets               |                                                              |     🚧     |
| Setup                 |                                                              |     🚧     |
| Signin                |                                                              |     🚧     |
| Signout               |                                                              |     🚧     |
| Sources               |                                                              |     🚧     |
| Telegraf Plugins      |                                                              |     🚧     |
| Telegrafs             |                                                              |     🚧     |
| Templates             |                                                              |     🚧     |
| Variables             |                                                              |     🚧     |
| Views                 |                                                              |     🚧     |

---

This project borrows some de/serialization code from [influxdb-client](https://github.com/influxdata/influxdb-client-python).