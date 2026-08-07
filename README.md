# Spotify Data Platform

An end-to-end Data Engineering project that simulates the data platform of a modern music streaming service.

The project demonstrates how streaming data is generated, ingested, transformed and prepared for analytics using a Medallion Architecture approach (Bronze → Silver → Gold).

The main focus is on building production-inspired data pipelines, applying data modeling principles, implementing data quality practices and creating analytics-ready datasets.

---

# Architecture

![Spotify Data Platform Architecture](images/architecture.png)

The platform follows a layered data architecture:

* **Data Generation:** Synthetic catalog data and listening events generated using Python.
* **Raw Data Layer:** Event data stored as JSON batch files.
* **Ingestion Layer:** Python pipelines load and validate raw data into PostgreSQL.
* **Bronze Layer:** Raw ingested data with minimal transformations.
* **Silver Layer:** Cleaned and transformed datasets using SQL/dbt models.
* **Gold Layer:** Analytics-ready models containing aggregated metrics.
* **Analytics Layer:** Business insights and reporting through visualization tools.

Apache Airflow will be used for workflow orchestration and pipeline scheduling.

---

# Technology Stack

| Category         | Technology     |
| ---------------- | -------------- |
| Programming      | Python         |
| Database         | PostgreSQL     |
| Query Language   | SQL            |
| Data Format      | JSON           |
| Transformations  | dbt            |
| Orchestration    | Apache Airflow |
| Analytics        | Power BI       |
| Containerization | Docker Compose |
| Version Control  | Git & GitHub   |

---

# Data Pipeline

The platform follows a batch-oriented data processing workflow:

| Stage           | Description                                           |
| --------------- | ----------------------------------------------------- |
| Data Generation | Generate artists, albums, tracks and listening events |
| Raw Data        | Store generated events as JSON batch files            |
| Ingestion       | Load raw data into PostgreSQL                         |
| Bronze Layer    | Store raw ingested data                               |
| Transformation  | Clean and transform data using SQL/dbt models         |
| Silver Layer    | Create curated datasets with business logic           |
| Gold Layer      | Build analytical models and metrics                   |
| Analytics       | Visualize insights through dashboards and reports     |

---

# Project Progress & Roadmap

## Completed

* Synthetic data generation using Python
* Batch-based raw data creation
* PostgreSQL database setup
* Bronze layer ingestion
* Initial relational data model
* Data quality validation rules

## In Progress

* Silver layer transformations
* Expansion of data models
* Improved documentation

## Future Improvements

* Complete dbt transformation layer
* Build Gold analytical models
* Introduce Apache Airflow orchestration
* Create Power BI dashboards
* Add automated testing
* Improve monitoring and data quality framework

---

This project is continuously evolving as new Data Engineering concepts and technologies are introduced.
