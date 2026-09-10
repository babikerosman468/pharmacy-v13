import json
import random
import statistics

with open("data/sales.json") as f:
    sales = json.load(f)

totals = [x["total"] for x in sales]

if len(totals) == 0:
    print("No sales data")
    quit()

mean_sales = statistics.mean(totals)

sim = []

for _ in range(1000):

    future = mean_sales * random.uniform(0.8,1.2)

    sim.append(future)

forecast = statistics.mean(sim)

print("\nPHARMACY FORECAST")
print("=================")
print("Historical Mean :", round(mean_sales,2))
print("Forecast Demand :", round(forecast,2))
print("Simulations     :", len(sim))
