# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)

## [v2.0.1] - 2022-02-15

- [PR 43](https://github.com/nasa/cumulus-message-adapter-python/pull/43)
  - Fixed issue with duplicate instances of `CumulusLogger`

## [v2.0.0] - 2021-12-21

- **CUMULUS-2577**
  - Update to match call signatures in [cumulus-message-adapter](https://github.com/nasa/cumulus-message-adapter) 2.0.0.  This release requires `cumulus-message-adapter` > 2.0.0.
  - Update test fixture to remove deprecated 'workflow_config' config key

## [v1.2.2] - 2021-11-04

- [Issue #38](https://github.com/nasa/cumulus-message-adapter-python/issues/38)
  - Update `CumulusLogger.createMessage` to allow logging messages with curly braces

## [v1.2.1] - 2019-02-19

- **CUMULUS-2078**
  - Update release requirements to require cumulus-message-adapter >=1.2.0, <
    1.4.x as cumulus-message-adapter 1.3.x is compatible with this module

## [v1.2.0] - 2019-02-19

- **CUMULUS-1486**
  - Updated target python versions to more accurately reflect python 3
    compatibility/cumulus-message adapter versions
  - Updated requirements to require cumulus-message-adapter >= 1.2.0, < 1.3.x

## [v1.1.1] - 2019-12-03

### Added

- **CUMULUS-1635** - Enhanced the messages logged by `CumulusLogger` to include
  the following additional information obtained from the CMA (if available):
  `asyncOperationId`, `granules` (granule IDs only), `parentArn`, and
  `stackName`

## [v1.1.0] - 2019-11-18

### Added

- **CUMULUS-1656** - Updated requirements to allow CMA 1.0.13 *or* the 1.1.x
  release branch of the CMA. It is expected that CMA 1.2.x will not be backward
  compatible with the 1.1.x client library.

- **CUMULUS-1488** - Updated CMA client to respect `CUMULUS_MESSAGE_ADAPTER_DIR`

## [v1.0.9] - 2019-09-16

### Added

- Updated CMA client to handle parameterized configuration, set execution env
  variable regardless of message format
