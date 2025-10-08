# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.8.0](https://github.com/tks18/streamlit-synthetic-data/compare/v0.7.1...v0.8.0) (2025-10-08)


### Bug Fixes 🛠

* **generators:** customer master - update the UUID to 8 integers ([bbdcb80](https://github.com/tks18/streamlit-synthetic-data/commit/bbdcb80707adcae97740c902b34fc3518cc6e381))


### Features 🔥

* **generators:** debtors - add various numerical / categorical synthetic fields for analysis ([fe5f9dd](https://github.com/tks18/streamlit-synthetic-data/commit/fe5f9dd1ef64283d3e205272c9dba8ab1736cf94))
* **generators:** inventory - various new fields for analysis ([f7e1d98](https://github.com/tks18/streamlit-synthetic-data/commit/f7e1d98568a3a4b5c07e89ea04051f119225079c))
* **generators:** ppe - various new fields for analysis ([8c4a62f](https://github.com/tks18/streamlit-synthetic-data/commit/8c4a62f0498556079dc1ee24d87509445d76fe8d))
* **generators:** purchases / revenue / vendor master - fix the uuid to int 8 digits ([a628326](https://github.com/tks18/streamlit-synthetic-data/commit/a628326db00beefccda52470eefeb9a203c1bf32))

### [0.7.1](https://github.com/tks18/streamlit-synthetic-data/compare/v0.7.0...v0.7.1) (2025-10-06)


### Bug Fixes 🛠

* **generators:** fix vendor master with proper column name ([a537511](https://github.com/tks18/streamlit-synthetic-data/commit/a53751183338c99673d821336278b6567c08d764))
* **ui/sidebar:** fix unable to add new products in the sidebar ([f6bec37](https://github.com/tks18/streamlit-synthetic-data/commit/f6bec3781f918bae7cc89f4c10c1376ce40f7286))

## [0.7.0](https://github.com/tks18/streamlit-synthetic-data/compare/v0.6.0...v0.7.0) (2025-10-05)


### Code Refactoring 🖌

* **generators:** rename the region into state across all generators ([890be92](https://github.com/tks18/streamlit-synthetic-data/commit/890be9279609f7cf93b8f17103809bdb537a8a89))


### Features 🔥

* **generators/customers:** update customer master with robust categorical & num data ([b5963de](https://github.com/tks18/streamlit-synthetic-data/commit/b5963dea37dfe65786eb0ce4c3cfb4fde25f669e))
* **generators/vendors:** update vendor master with robust categorical & num data ([bf45b72](https://github.com/tks18/streamlit-synthetic-data/commit/bf45b7218fb61b3ce09f14e23cb5f3a0b7459ab3))

## [0.6.0](https://github.com/tks18/streamlit-synthetic-data/compare/v0.5.0...v0.6.0) (2025-10-05)


### Docs 📃

* **typing:** add static types to all functions ([6c6421b](https://github.com/tks18/streamlit-synthetic-data/commit/6c6421bc58dc3fd94ec6e616caa2f89fe7009018))


### Features 🔥

* **generators:** create a generator config in order to create the data automatically ([65d3209](https://github.com/tks18/streamlit-synthetic-data/commit/65d32095ab6ea76d8ca43162a96191f13d9c5f13))
* **generators:** make generators consistent so that it is possible to expand to more generators ([56e9e24](https://github.com/tks18/streamlit-synthetic-data/commit/56e9e24f0ae2e0e788f5e1d6bfdca7f2bc02c595))
* **generators:** use state api, allow customization of total rows to generate ([1640a1a](https://github.com/tks18/streamlit-synthetic-data/commit/1640a1ab3950bf2344de13675de4d36a75eb97e8))
* **helpers/config:** add caching for large data, add additional fields for state to hold ([ef6d4eb](https://github.com/tks18/streamlit-synthetic-data/commit/ef6d4ebd9e54268ea2eacef86f903c6f56c20247))
* **helpers/countries:** add caching to the countries data ([479edc1](https://github.com/tks18/streamlit-synthetic-data/commit/479edc17f7985b8b94867e9e7485c6a947a0b10e))
* **helpers/state:** add a state helper to get the config ([5e1a07e](https://github.com/tks18/streamlit-synthetic-data/commit/5e1a07e85a62d1f510d405506ab315c3751cc422))
* **types:** create static typing for the entire app using types.py file ([cf0fbb4](https://github.com/tks18/streamlit-synthetic-data/commit/cf0fbb4d7c202623823f0eb4a58344343c8c82c1))
* **ui/sidebar:** add customization of total rows, other misc fixes ([c5ca7bc](https://github.com/tks18/streamlit-synthetic-data/commit/c5ca7bc07d3bc081483a3805da9ab48ae657e2e5))


### Code Refactoring 🖌

* **ui/tabs:** refactor the generator code to do automatically, use state api ([f06193a](https://github.com/tks18/streamlit-synthetic-data/commit/f06193ae06c1f4da871c543604d07ce00b127657))
* **ui/tabs:** use the state api instead of passing parameters to get the data ([bf31e91](https://github.com/tks18/streamlit-synthetic-data/commit/bf31e917e9dbdbba676515d6ad039a13ed4840d7))
* **ui:** refactor to use the updated function signature ([4775581](https://github.com/tks18/streamlit-synthetic-data/commit/477558183072a20c0661e0b862e3741ad67ca80d))

## [0.5.0](https://github.com/tks18/streamlit-synthetic-data/compare/v0.4.0...v0.5.0) (2025-10-04)


### Bug Fixes 🛠

* **app:** remove default keys from input fields since its getting applied using session api ([d6dc670](https://github.com/tks18/streamlit-synthetic-data/commit/d6dc670d1b4bf948a77d59cf30a7adafd43a7f01))


### Build System 🏗

* **package:** add countryinfo package to dynamically get the countries / states ([3643473](https://github.com/tks18/streamlit-synthetic-data/commit/364347371d4dd0b07ee8c3de6e9236b1a79a72aa))


### Code Refactoring 🖌

* **app:** modularize the app & refactor the entire app ([a515ec6](https://github.com/tks18/streamlit-synthetic-data/commit/a515ec6e9a8ffe2689c96c3f1f8a6a38cde7b793))
* **app:** modularize the app: helper module ([e107cc6](https://github.com/tks18/streamlit-synthetic-data/commit/e107cc6c20fbe75f60c02bf50e2bc4186e8cdcc9))
* **generators:** modularize the app: generators module ([aa76f8e](https://github.com/tks18/streamlit-synthetic-data/commit/aa76f8edc948832e1dab30e28a64de43f3b688c4))
* **helper/countries:** remove statics/regions since its done through countryinfo package ([6ec612a](https://github.com/tks18/streamlit-synthetic-data/commit/6ec612a9d5ade2c9885e5b4f756315051fbde783))
* **mods:** modularize the app: scenarios module ([ea01a74](https://github.com/tks18/streamlit-synthetic-data/commit/ea01a74d019e987ad5be8a413c0051ecbb9151c7))
* **ui:** modularize the app: UI Module ([694a81a](https://github.com/tks18/streamlit-synthetic-data/commit/694a81a2cf5d74c36ff75d0feeb5fa8a8734771b))


### Others 🔧

* **profile:** update the sample profile ([0e038fb](https://github.com/tks18/streamlit-synthetic-data/commit/0e038fb7ed8a2c43e2ea2121ec8cb61facbf3102))

## [0.4.0](https://github.com/tks18/streamlit-synthetic-data/compare/v0.3.1...v0.4.0) (2025-10-03)


### Features 🔥

* **app/profiles:** robust profile data mapping with default values ([37e3665](https://github.com/tks18/streamlit-synthetic-data/commit/37e3665e267e4bbb0f1bcfc5d372cdb0fdd0b9f8))
* **profiles:** add keys to elements, enable loading of profiles for every config ([244f32f](https://github.com/tks18/streamlit-synthetic-data/commit/244f32f6aefd7e2ec7956999c04f6f9fb179faf1))
* **templates:** remove templates & structure profiles to handle everything ([9665d0e](https://github.com/tks18/streamlit-synthetic-data/commit/9665d0edbfab40477f879e014db54fcccac53fb9))


### Others 🔧

* remove unwanted imports ([783a82c](https://github.com/tks18/streamlit-synthetic-data/commit/783a82cfe0cf3223b273c970abb1dfc0f2fe1184))


### Bug Fixes 🛠

* **app:** remove the default columns table as its not showing properly ([9404a44](https://github.com/tks18/streamlit-synthetic-data/commit/9404a44bdde3e6d10bba1c9cea5b857259adaee3))


### Code Refactoring 🖌

* **statics:** remove json generators & move everything to statics folder ([c7fcd8b](https://github.com/tks18/streamlit-synthetic-data/commit/c7fcd8b315843e7cf63dc872863c886e32f02dc7))
* **statics:** remove templates, add statics for industry & regions ([092658b](https://github.com/tks18/streamlit-synthetic-data/commit/092658b7cd8950d7b6bb10e571d75d2470a84075))

### [0.3.1](https://github.com/tks18/streamlit-synthetic-data/compare/v0.3.0...v0.3.1) (2025-10-02)


### Others 🔧

* update readme ([2cba46f](https://github.com/tks18/streamlit-synthetic-data/commit/2cba46f16026433aa9790d85252c1f6065aaeef2))


### Bug Fixes 🛠

* **app:** fix the form not changing state based on col type ([80072dc](https://github.com/tks18/streamlit-synthetic-data/commit/80072dca3b3de78e2efd3779c641939ec51e6d04))

## [0.3.0](https://github.com/tks18/streamlit-synthetic-data/compare/v0.2.0...v0.3.0) (2025-10-01)


### Docs 📃

* **app:** add nice readme & gpl-3.0 license for the project ([095fe6a](https://github.com/tks18/streamlit-synthetic-data/commit/095fe6a4f252a261d35ea9298a1da05875dc6836))

## 0.2.0 (2025-10-01)


### Features 🔥

* **app:** initialize the app with commitlint, commitizen, husky for standard commit linting ([a60aecb](https://github.com/tks18/streamlit-synthetic-data/commit/a60aecb72d74b6cdb6d3c2bf40703808f5e9ad86))


### CI 🛠

* **app:** update the husky commit-msg hook ([61b43dc](https://github.com/tks18/streamlit-synthetic-data/commit/61b43dc8d864228fd21be6cde09d8a53a8bb8ff8))
