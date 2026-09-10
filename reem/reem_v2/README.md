# REEM V2 — Ideal Synthetic Pharmacy Dataset

## Purpose

Fresh synthetic longitudinal pharmacy supply-chain data for REEM research,
model development, simulation and validation.

## Evidence boundary

ALL records are synthetic development data.

DataSource = SIMULATED_REEM_V2
DataStatus = DEVELOPMENT
NotOperationalEvidence = TRUE

The data must NOT be represented as real pharmacy observations.

## Time horizon

2023-01-01 through 2026-09-09.

## Datasets

medicines.csv
    Medicine master data.

suppliers.csv
    Supplier characteristics and reliability.

calendar.csv
    Daily temporal and seasonal context.

sales.csv
    Fulfilled demand transactions.

demand_requests.csv
    Requested, fulfilled and unfulfilled demand.

stock_movements.csv
    Longitudinal inventory movements.

inventory_batches.csv
    Batch-level stock, supplier and expiry information.

purchases.csv
    Purchase orders and procurement cost.

deliveries.csv
    Delivery dates, quantities and lead times.

stockouts.csv
    Stockout periods and estimated lost demand.

returns.csv
    Operational and customer returns.

adjustments.csv
    Inventory corrections and losses.

## Model portfolio

Demand Forecasting
Intermittent Demand
Reorder Point
Safety Stock
EOQ
Supplier Performance
Expiry Risk
Stockout Prediction
Monte Carlo Risk
Inventory Optimisation

## Scientific principle

Operational reality
    ->
Data
    ->
Evidence
    ->
Features
    ->
Models
    ->
Model Assessment
    ->
Management Intelligence
    ->
Decision
    ->
New Evidence

Synthetic data supports development and testing.
It does not constitute operational evidence.
