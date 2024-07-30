# <img src="https://docs.lido.fi/img/logo.svg" alt="Lido" width="46"/>  Permissionless reward distributor

## Overview

Permissionless reward distribution bot for Lido staking module.
Operates with [Node Operator Registry](https://docs.lido.fi/contracts/node-operators-registry) smart contract.
After [Accounting Oracle](https://docs.lido.fi/guides/oracle-spec/accounting-oracle) completes the third phase,
anyone can initiate the reward distribution to allocate rewards among Node Operators in the Staking Module.

## Table of Contents

- [Description](#overview)
- [Table of Contents](#table-of-contents)
- [Development](#getting-started)
    - [Install](#install)
    - [Tests](#tests)
    - [Release flow](#release-flow)
- [Monitoring](#monitoring)
    - [Metrics](#metrics)
    - [Alerts](#alerts)
- [Variables](#variables)
    - [Required variables](#required)
    - [Additional variables](#optional)
- [Licence](#licence)

## Getting started

### Install

```bash
git clone git@github.com:lidofinance/nor-reward-distribution-bot.git
cd nor-reward-distribution-bot
poetry install
```

To run bot

```bash
poetry run python src/main.py
```

### Tests

#### Run unit tests

```bash
NODE_OPERATOR_REGISTRY_ADDRESSES='' WEB3_RPC_ENDPOINTS='' poetry run pytest tests -m unit
```

#### Run integration tests.

To run integration tests install Anvil.

Run integration tests on Holesky testnet fork:

```bash
export NODE_OPERATOR_REGISTRY_ADDRESSES=0xE12ABf35fA6f69C97Cc0AcF67B38D3000435790e
export WEB3_RPC_ENDPOINTS=https://holesky.infura.io/v3/<key>

poetry run pytest tests -m integration
```

In case of "command not found: anvil" error, provide `ANVIL_PATH` variable

```bash
export ANVIL_PATH='pathto/anvil'
```

### Release flow

To create a new release:

1. Merge all changes to the `main` branch.
2. After the merge, the `Prepare release draft` action will run automatically. When the action is complete, a release draft is created.
3. When you need to release, go to Repo → Releases.
4. Publish the desired release draft manually by clicking the edit button - this release is now the `Latest Published`.
5. After publication, the action to create a release bump will be triggered automatically.

## Monitoring

### Metrics

Metrics list could be found in [source code](src/metrics/metrics.py).
Prometheus server hosted on `http://localhost:${{PROMETHEUS_PORT}}/`.

### Alerts

Integrated with Alertmanager and Prometheus to provide real-time alerts based on predefined metrics.  
Alerts source code could be found [here](alerts).

Alerts list:

| Name                             | Description                               |
|----------------------------------|-------------------------------------------|
| DistributionBotLowAccountBalance | Account balance is low                    |
| DistributionBotStaleHeadBlock    | Block head didn't update for a while      |
| DistributionBotNoDistributions   | No reward distribution for a while        |
| DistributionBotUnexpectedErrors  | Unexpected errors. Check logs for details |
| DistributionBotHighELNodeLatency | Issues with EL node                       |

Run alerts tests with: `promtool test rules alerts/alerts.tests.yml`

## Variables

### Required

| Variable                         | Default                                    | Description                                                                                                                                               |
|----------------------------------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| WEB3_RPC_ENDPOINTS               | -                                          | List of rpc endpoints that will be used to send requests (comma separated)                                                                                |
| WALLET_PRIVATE_KEY               | -                                          | Account private key                                                                                                                                       |
| NODE_OPERATOR_REGISTRY_ADDRESSES | 0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5 | Lido Node Operator Registry module address (or based on it). Addresses could be found [here](https://docs.lido.fi/deployed-contracts/). Separate with `,` |

### Optional

| Variable                | Default | Description                   |
|-------------------------|---------|-------------------------------|
| PROMETHEUS_PORT         | 9000    | Port with metrics server      |
| HEALTHCHECK_SERVER_PORT | 9010    | Port with bot`s status server |

## License

2024 Lido <info@lido.fi>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the [GNU General Public License](LICENSE)
along with this program. If not, see <https://www.gnu.org/licenses/>.
