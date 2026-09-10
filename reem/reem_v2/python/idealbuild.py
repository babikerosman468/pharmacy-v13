#!/usr/bin/env python3

"""
REEM V2 — IDEALBUILD

Fresh synthetic pharmacy supply-chain research environment.

Purpose:
    Generate a realistic longitudinal pharmacy dataset for development,
    testing and validation of REEM decision-science models.

IMPORTANT:
    ALL generated data are synthetic development data.
    They are NOT operational evidence.

Generated:
    schema/medicines.csv
    schema/suppliers.csv
    schema/calendar.csv
    schema/sales.csv
    schema/demand_requests.csv
    schema/stock_movements.csv
    schema/inventory_batches.csv
    schema/purchases.csv
    schema/deliveries.csv
    schema/stockouts.csv
    schema/returns.csv
    schema/adjustments.csv

    README.md
"""

import csv
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 20260909

random.seed(SEED)

ROOT = Path(".")
SCHEMA = ROOT / "schema"

START_DATE = date(2023, 1, 1)
END_DATE = date(2026, 9, 9)

MEDICINE_COUNT = 50
SUPPLIER_COUNT = 10

DATA_SOURCE = "SIMULATED_REEM_V2"
DATA_STATUS = "DEVELOPMENT"
NOT_OPERATIONAL = "TRUE"


# ============================================================
# HELPERS
# ============================================================

def write_csv(path, rows, fields):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {path}")


def clamp(value, low, high):

    return max(
        low,
        min(high, value)
    )


# ============================================================
# MEDICINES
# ============================================================

MEDICINE_NAMES = [
    "Acetylcysteine",
    "Albendazole",
    "Allopurinol",
    "Ambroxol",
    "Amikacin",
    "Amitriptyline",
    "Amlodipine",
    "Amoxicillin",
    "Apixaban",
    "ArtemetherLumefantrine",
    "Aspirin",
    "Atenolol",
    "Atorvastatin",
    "Azithromycin",
    "Bisoprolol",
    "Budesonide",
    "Captopril",
    "Carbamazepine",
    "Cefixime",
    "Ceftriaxone",
    "Cetirizine",
    "Ciprofloxacin",
    "Clopidogrel",
    "Dexamethasone",
    "Diclofenac",
    "Doxycycline",
    "Enalapril",
    "Esomeprazole",
    "Fluconazole",
    "FolicAcid",
    "Furosemide",
    "Gabapentin",
    "Gliclazide",
    "Hydrochlorothiazide",
    "Ibuprofen",
    "Insulin",
    "Losartan",
    "Metformin",
    "Montelukast",
    "Omeprazole",
    "Paracetamol",
    "Prednisolone",
    "Salbutamol",
    "Simvastatin",
    "Spironolactone",
    "Tramadol",
    "Valproate",
    "VitaminD",
    "Warfarin",
    "Zinc"
]

THERAPEUTIC_CLASSES = [
    "Analgesic",
    "Antibiotic",
    "Cardiovascular",
    "Gastrointestinal",
    "Respiratory",
    "Antidiabetic",
    "Neurological",
    "Antihistamine",
    "Antifungal",
    "Vitamins"
]

FORMS = [
    "Tablet",
    "Capsule",
    "Syrup",
    "Injection",
    "Sachet",
    "Cream"
]


def build_medicines():

    rows = []

    for i, name in enumerate(
        MEDICINE_NAMES[:MEDICINE_COUNT],
        start=1
    ):

        unit_cost = round(
            random.uniform(2.0, 80.0),
            2
        )

        margin = random.uniform(
            0.15,
            0.35
        )

        selling_price = round(
            unit_cost * (1 + margin),
            2
        )

        rows.append({

            "DrugID":
                f"D{i:04d}",

            "GenericName":
                name,

            "BrandName":
                f"{name}-Brand",

            "Strength":
                random.choice([
                    "10 mg",
                    "20 mg",
                    "50 mg",
                    "100 mg",
                    "200 mg",
                    "250 mg",
                    "500 mg"
                ]),

            "DosageForm":
                random.choice(FORMS),

            "PackSize":
                random.choice([
                    10,
                    20,
                    30,
                    50,
                    100
                ]),

            "TherapeuticClass":
                random.choice(
                    THERAPEUTIC_CLASSES
                ),

            "UnitCost":
                unit_cost,

            "SellingPrice":
                selling_price,

            "ShelfLifeDays":
                random.choice([
                    180,
                    365,
                    540,
                    730,
                    1095
                ]),

            "Criticality":
                random.choice([
                    "LOW",
                    "MEDIUM",
                    "HIGH"
                ]),

            "DataSource":
                DATA_SOURCE,

            "DataStatus":
                DATA_STATUS,

            "NotOperationalEvidence":
                NOT_OPERATIONAL
        })

    return rows


# ============================================================
# SUPPLIERS
# ============================================================

def build_suppliers():

    rows = []

    for i in range(
        1,
        SUPPLIER_COUNT + 1
    ):

        rows.append({

            "SupplierID":
                f"S{i:03d}",

            "SupplierName":
                f"Simulated Supplier {i:02d}",

            "Region":
                random.choice([
                    "Cairo",
                    "Giza",
                    "Alexandria",
                    "Delta"
                ]),

            "BaselineLeadTimeDays":
                random.randint(2, 14),

            "LeadTimeVariabilityDays":
                random.randint(1, 5),

            "Reliability":
                round(
                    random.uniform(
                        0.82,
                        0.99
                    ),
                    3
                ),

            "DataSource":
                DATA_SOURCE,

            "DataStatus":
                DATA_STATUS,

            "NotOperationalEvidence":
                NOT_OPERATIONAL
        })

    return rows


# ============================================================
# CALENDAR
# ============================================================

def build_calendar():

    rows = []

    current = START_DATE

    while current <= END_DATE:

        dow = current.weekday()

        doy = current.timetuple().tm_yday

        seasonal = (
            1.0
            +
            0.20
            *
            math.sin(
                2
                *
                math.pi
                *
                doy
                /
                365.25
            )
        )

        holiday = (
            (current.month, current.day)
            in {
                (1, 1),
                (5, 1),
                (12, 25)
            }
        )

        rows.append({

            "Date":
                current.isoformat(),

            "DayOfWeek":
                dow,

            "Week":
                current.isocalendar().week,

            "Month":
                current.month,

            "Quarter":
                ((current.month - 1) // 3) + 1,

            "Year":
                current.year,

            "Weekend":
                "TRUE"
                if dow >= 5
                else "FALSE",

            "SeasonalIndex":
                round(
                    seasonal,
                    4
                ),

            "Holiday":
                "TRUE"
                if holiday
                else "FALSE",

            "DataSource":
                DATA_SOURCE,

            "DataStatus":
                DATA_STATUS,

            "NotOperationalEvidence":
                NOT_OPERATIONAL
        })

        current += timedelta(
            days=1
        )

    return rows


# ============================================================
# DEMAND PARAMETERS
# ============================================================

def build_demand_parameters(
    medicines
):

    params = {}

    for medicine in medicines:

        drug_id = medicine["DrugID"]

        mean_daily = random.choice([

            random.uniform(
                0.05,
                0.25
            ),

            random.uniform(
                0.25,
                1.0
            ),

            random.uniform(
                1.0,
                3.0
            ),

            random.uniform(
                3.0,
                8.0
            )
        ])

        params[drug_id] = {

            "mean":
                mean_daily,

            "trend":
                random.uniform(
                    -0.00008,
                    0.00012
                ),

            "weekly":
                random.uniform(
                    0.05,
                    0.20
                ),

            "noise":
                random.uniform(
                    0.10,
                    0.40
                )
        }

    return params


# ============================================================
# INITIAL INVENTORY
# ============================================================

def build_initial_inventory(
    medicines
):

    inventory = []
    batches = []

    batch_number = 1

    for medicine in medicines:

        quantity = random.randint(
            50,
            500
        )

        expiry = (
            START_DATE
            +
            timedelta(
                days=random.randint(
                    180,
                    900
                )
            )
        )

        batch_id = (
            f"B{batch_number:06d}"
        )

        batch_number += 1

        supplier_id = (
            f"S{random.randint(1, SUPPLIER_COUNT):03d}"
        )

        batches.append({

            "BatchID":
                batch_id,

            "DrugID":
                medicine["DrugID"],

            "SupplierID":
                supplier_id,

            "QuantityReceived":
                quantity,

            "RemainingQuantity":
                quantity,

            "ManufactureDate":
                (
                    START_DATE
                    -
                    timedelta(
                        days=random.randint(
                            30,
                            300
                        )
                    )
                ).isoformat(),

            "ReceivedDate":
                START_DATE.isoformat(),

            "ExpiryDate":
                expiry.isoformat(),

            "DataSource":
                DATA_SOURCE,

            "DataStatus":
                DATA_STATUS,

            "NotOperationalEvidence":
                NOT_OPERATIONAL
        })

        inventory.append({

            "DrugID":
                medicine["DrugID"],

            "Quantity":
                quantity,

            "BatchID":
                batch_id
        })

    return (
        inventory,
        batches,
        batch_number
    )


# ============================================================
# DEMAND GENERATOR
# ============================================================

def demand_quantity(
    mean_daily,
    trend,
    weekly,
    noise,
    current
):

    days = (
        current
        -
        START_DATE
    ).days

    trend_factor = max(
        0.60,
        1.0 + trend * days
    )

    weekly_factor = (
        1.0 - weekly
        if current.weekday() >= 5
        else 1.0
    )

    seasonal_factor = (
        1.0
        +
        0.25
        *
        math.sin(
            2
            *
            math.pi
            *
            current.timetuple().tm_yday
            /
            365.25
        )
    )

    random_factor = (
        random.lognormvariate(
            0,
            noise
        )
    )

    expected = (
        mean_daily
        *
        trend_factor
        *
        weekly_factor
        *
        seasonal_factor
        *
        random_factor
    )

    # Intermittent demand.
    if expected < 0.35:

        probability = clamp(
            expected,
            0,
            0.90
        )

        return (
            1
            if random.random()
            <
            probability
            else 0
        )

    whole = int(expected)

    fraction = (
        expected
        -
        whole
    )

    return (
        whole
        +
        (
            1
            if random.random()
            <
            fraction
            else 0
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("REEM V2 — IDEALBUILD")
    print("FRESH SYNTHETIC PHARMACY WORLD")
    print("=" * 60)

    SCHEMA.mkdir(
        parents=True,
        exist_ok=True
    )

    medicines = build_medicines()

    suppliers = build_suppliers()

    calendar = build_calendar()

    demand_parameters = (
        build_demand_parameters(
            medicines
        )
    )

    # --------------------------------------------------------
    # MASTER DATA
    # --------------------------------------------------------

    write_csv(
        SCHEMA / "medicines.csv",
        medicines,
        list(
            medicines[0].keys()
        )
    )

    write_csv(
        SCHEMA / "suppliers.csv",
        suppliers,
        list(
            suppliers[0].keys()
        )
    )

    write_csv(
        SCHEMA / "calendar.csv",
        calendar,
        list(
            calendar[0].keys()
        )
    )

    # --------------------------------------------------------
    # INITIAL INVENTORY
    # --------------------------------------------------------

    inventory, batches, next_batch = (
        build_initial_inventory(
            medicines
        )
    )

    inventory_by_drug = {

        row["DrugID"]:
            row["Quantity"]

        for row in inventory
    }

    current_batch = {

        row["DrugID"]:
            row["BatchID"]

        for row in batches
    }

    # --------------------------------------------------------
    # TRANSACTION DATA
    # --------------------------------------------------------

    sales = []
    demand_requests = []
    stock_movements = []
    purchases = []
    deliveries = []
    stockouts = []
    returns = []
    adjustments = []

    sale_id = 1
    request_id = 1
    movement_id = 1
    purchase_id = 1
    delivery_id = 1
    stockout_id = 1
    return_id = 1
    adjustment_id = 1

    pending_deliveries = []

    open_stockouts = {}

    current = START_DATE

    while current <= END_DATE:

        # ----------------------------------------------------
        # Process deliveries due today
        # ----------------------------------------------------

        due = [

            item
            for item in pending_deliveries

            if item["DeliveryDate"]
            <= current
        ]

        for item in due:

            drug_id = item["DrugID"]

            received = (
                item["ReceivedQuantity"]
            )

            batch_id = (
                f"B{next_batch:06d}"
            )

            next_batch += 1

            medicine = next(
                m
                for m in medicines
                if m["DrugID"] == drug_id
            )

            expiry = (
                current
                +
                timedelta(
                    days=medicine[
                        "ShelfLifeDays"
                    ]
                )
            )

            batches.append({

                "BatchID":
                    batch_id,

                "DrugID":
                    drug_id,

                "SupplierID":
                    item["SupplierID"],

                "QuantityReceived":
                    received,

                "RemainingQuantity":
                    received,

                "ManufactureDate":
                    (
                        current
                        -
                        timedelta(
                            days=30
                        )
                    ).isoformat(),

                "ReceivedDate":
                    current.isoformat(),

                "ExpiryDate":
                    expiry.isoformat(),

                "DataSource":
                    DATA_SOURCE,

                "DataStatus":
                    DATA_STATUS,

                "NotOperationalEvidence":
                    NOT_OPERATIONAL
            })

            inventory_by_drug[
                drug_id
            ] += received

            current_batch[
                drug_id
            ] = batch_id

            stock_movements.append({

                "MovementID":
                    f"M{movement_id:09d}",

                "Timestamp":
                    current.isoformat(),

                "DrugID":
                    drug_id,

                "BatchID":
                    batch_id,

                "MovementType":
                    "PURCHASE_RECEIPT",

                "Quantity":
                    received,

                "ReferenceID":
                    item["PurchaseID"],

                "DataSource":
                    DATA_SOURCE,

                "DataStatus":
                    DATA_STATUS,

                "NotOperationalEvidence":
                    NOT_OPERATIONAL
            })

            movement_id += 1

            pending_deliveries.remove(
                item
            )

        # ----------------------------------------------------
        # Daily demand
        # ----------------------------------------------------

        for medicine in medicines:

            drug_id = medicine["DrugID"]

            params = (
                demand_parameters[
                    drug_id
                ]
            )

            requested = demand_quantity(

                params["mean"],
                params["trend"],
                params["weekly"],
                params["noise"],
                current
            )

            available = (
                inventory_by_drug[
                    drug_id
                ]
            )

            fulfilled = min(
                requested,
                available
            )

            unfulfilled = (
                requested
                -
                fulfilled
            )

            # ------------------------------------------------
            # Demand request
            # ------------------------------------------------

            if requested > 0:

                demand_requests.append({

                    "RequestID":
                        f"R{request_id:08d}",

                    "Timestamp":
                        current.isoformat(),

                    "DrugID":
                        drug_id,

                    "RequestedQuantity":
                        requested,

                    "FulfilledQuantity":
                        fulfilled,

                    "UnfulfilledQuantity":
                        unfulfilled,

                    "DataSource":
                        DATA_SOURCE,

                    "DataStatus":
                        DATA_STATUS,

                    "NotOperationalEvidence":
                        NOT_OPERATIONAL
                })

                request_id += 1

            # ------------------------------------------------
            # Sale
            # ------------------------------------------------

            if fulfilled > 0:

                sale_time = (
                    datetime.combine(
                        current,
                        datetime.min.time()
                    )
                    +
                    timedelta(
                        hours=random.randint(
                            8,
                            21
                        ),
                        minutes=random.randint(
                            0,
                            59
                        )
                    )
                )

                revenue = round(
                    fulfilled
                    *
                    medicine[
                        "SellingPrice"
                    ],
                    2
                )

                sale_key = (
                    f"SALE{sale_id:08d}"
                )

                sales.append({

                    "SaleID":
                        sale_key,

                    "Timestamp":
                        sale_time.isoformat(
                            timespec="seconds"
                        ),

                    "DrugID":
                        drug_id,

                    "Quantity":
                        fulfilled,

                    "UnitPrice":
                        medicine[
                            "SellingPrice"
                        ],

                    "Revenue":
                        revenue,

                    "BatchID":
                        current_batch[
                            drug_id
                        ],

                    "DataSource":
                        DATA_SOURCE,

                    "DataStatus":
                        DATA_STATUS,

                    "NotOperationalEvidence":
                        NOT_OPERATIONAL
                })

                sale_id += 1

                inventory_by_drug[
                    drug_id
                ] -= fulfilled

                stock_movements.append({

                    "MovementID":
                        f"M{movement_id:09d}",

                    "Timestamp":
                        sale_time.isoformat(
                            timespec="seconds"
                        ),

                    "DrugID":
                        drug_id,

                    "BatchID":
                        current_batch[
                            drug_id
                        ],

                    "MovementType":
                        "SALE",

                    "Quantity":
                        -fulfilled,

                    "ReferenceID":
                        sale_key,

                    "DataSource":
                        DATA_SOURCE,

                    "DataStatus":
                        DATA_STATUS,

                    "NotOperationalEvidence":
                        NOT_OPERATIONAL
                })

                movement_id += 1

            # ------------------------------------------------
            # Stockout tracking
            # ------------------------------------------------

            if unfulfilled > 0:

                if drug_id not in open_stockouts:

                    open_stockouts[
                        drug_id
                    ] = {

                        "start":
                            current,

                        "lost":
                            unfulfilled
                    }

                else:

                    open_stockouts[
                        drug_id
                    ]["lost"] += (
                        unfulfilled
                    )

            elif drug_id in open_stockouts:

                event = (
                    open_stockouts.pop(
                        drug_id
                    )
                )

                stockouts.append({

                    "StockoutID":
                        f"SO{stockout_id:07d}",

                    "DrugID":
                        drug_id,

                    "StartDate":
                        event[
                            "start"
                        ].isoformat(),

                    "EndDate":
                        current.isoformat(),

                    "DurationDays":
                        (
                            current
                            -
                            event[
                                "start"
                            ]
                        ).days,

                    "EstimatedLostDemand":
                        event["lost"],

                    "DataSource":
                        DATA_SOURCE,

                    "DataStatus":
                        DATA_STATUS,

                    "NotOperationalEvidence":
                        NOT_OPERATIONAL
                })

                stockout_id += 1

            # ------------------------------------------------
            # Simulated procurement policy
            # ------------------------------------------------

            reorder_level = max(

                20,

                int(
                    params["mean"]
                    *
                    25
                )
            )

            already_pending = any(

                x["DrugID"] == drug_id

                for x in pending_deliveries
            )

            if (
                inventory_by_drug[
                    drug_id
                ]
                <= reorder_level
                and not already_pending
            ):

                order_quantity = max(

                    50,

                    int(
                        params["mean"]
                        *
                        60
                    )
                )

                supplier_id = (
                    f"S{random.randint(1, SUPPLIER_COUNT):03d}"
                )

                supplier = next(

                    s
                    for s in suppliers

                    if s["SupplierID"]
                    ==
                    supplier_id
                )

                lead_time = max(

                    2,

                    int(
                        random.gauss(
                            supplier[
                                "BaselineLeadTimeDays"
                            ],
                            supplier[
                                "LeadTimeVariabilityDays"
                            ]
                        )
                    )
                )

                delivery_date = (
                    current
                    +
                    timedelta(
                        days=lead_time
                    )
                )

                received_quantity = (

                    order_quantity

                    if random.random()
                    <
                    float(
                        supplier[
                            "Reliability"
                        ]
                    )

                    else
                    int(
                        order_quantity
                        *
                        random.uniform(
                            0.80,
                            0.95
                        )
                    )
                )

                purchase_key = (
                    f"P{purchase_id:07d}"
                )

                purchases.append({

                    "PurchaseID":
                        purchase_key,

                    "OrderDate":
                        current.isoformat(),

                    "DrugID":
                        drug_id,

                    "SupplierID":
                        supplier_id,

                    "OrderQuantity":
                        order_quantity,

                    "UnitCost":
                        medicine[
                            "UnitCost"
                        ],

                    "TotalCost":
                        round(
                            order_quantity
                            *
                            medicine[
                                "UnitCost"
                            ],
                            2
                        ),

                    "DataSource":
                        DATA_SOURCE,

                    "DataStatus":
                        DATA_STATUS,

                    "NotOperationalEvidence":
                        NOT_OPERATIONAL
                })

                deliveries.append({

                    "DeliveryID":
                        f"DEL{delivery_id:07d}",

                    "PurchaseID":
                        purchase_key,

                    "DrugID":
                        drug_id,

                    "SupplierID":
                        supplier_id,

                    "OrderDate":
                        current.isoformat(),

                    "DeliveryDate":
                        delivery_date.isoformat(),

                    "LeadTimeDays":
                        lead_time,

                    "OrderedQuantity":
                        order_quantity,

                    "ReceivedQuantity":
                        received_quantity,

                    "OnTime":
                        "TRUE",

                    "DataSource":
                        DATA_SOURCE,

                    "DataStatus":
                        DATA_STATUS,

                    "NotOperationalEvidence":
                        NOT_OPERATIONAL
                })

                pending_deliveries.append({

                    "PurchaseID":
                        purchase_key,

                    "DrugID":
                        drug_id,

                    "SupplierID":
                        supplier_id,

                    "DeliveryDate":
                        delivery_date,

                    "ReceivedQuantity":
                        received_quantity
                })

                purchase_id += 1
                delivery_id += 1

        current += timedelta(
            days=1
        )

    # ========================================================
    # CLOSE OPEN STOCKOUTS
    # ========================================================

    for drug_id, event in (
        open_stockouts.items()
    ):

        stockouts.append({

            "StockoutID":
                f"SO{stockout_id:07d}",

            "DrugID":
                drug_id,

            "StartDate":
                event[
                    "start"
                ].isoformat(),

            "EndDate":
                END_DATE.isoformat(),

            "DurationDays":
                (
                    END_DATE
                    -
                    event[
                        "start"
                    ]
                ).days
                +
                1,

            "EstimatedLostDemand":
                event["lost"],

            "DataSource":
                DATA_SOURCE,

            "DataStatus":
                DATA_STATUS,

            "NotOperationalEvidence":
                NOT_OPERATIONAL
        })

        stockout_id += 1

    # ========================================================
    # RETURNS
    # ========================================================

    for sale in sales:

        if random.random() < 0.015:

            returns.append({

                "ReturnID":
                    f"RET{return_id:07d}",

                "Timestamp":
                    sale["Timestamp"],

                "SaleID":
                    sale["SaleID"],

                "DrugID":
                    sale["DrugID"],

                "Quantity":
                    1,

                "Reason":
                    random.choice([
                        "CustomerReturn",
                        "DamagedPackage",
                        "WrongItem"
                    ]),

                "DataSource":
                    DATA_SOURCE,

                "DataStatus":
                    DATA_STATUS,

                "NotOperationalEvidence":
                    NOT_OPERATIONAL
            })

            return_id += 1

    # ========================================================
    # INVENTORY ADJUSTMENTS
    # ========================================================

    total_days = (
        END_DATE
        -
        START_DATE
    ).days

    for medicine in medicines:

        if random.random() < 0.50:

            adjustment_date = (
                START_DATE
                +
                timedelta(
                    days=random.randint(
                        1,
                        total_days
                    )
                )
            )

            adjustments.append({

                "AdjustmentID":
                    f"A{adjustment_id:07d}",

                "Date":
                    adjustment_date.isoformat(),

                "DrugID":
                    medicine["DrugID"],

                "Quantity":
                    random.choice([
                        -3,
                        -2,
                        -1,
                        1,
                        2,
                        3
                    ]),

                "Reason":
                    random.choice([
                        "CycleCount",
                        "Damaged",
                        "DataCorrection"
                    ]),

                "DataSource":
                    DATA_SOURCE,

                "DataStatus":
                    DATA_STATUS,

                "NotOperationalEvidence":
                    NOT_OPERATIONAL
            })

            adjustment_id += 1

    # ========================================================
    # WRITE DATASETS
    # ========================================================

    datasets = [

        (
            "sales.csv",
            sales
        ),

        (
            "demand_requests.csv",
            demand_requests
        ),

        (
            "stock_movements.csv",
            stock_movements
        ),

        (
            "inventory_batches.csv",
            batches
        ),

        (
            "purchases.csv",
            purchases
        ),

        (
            "deliveries.csv",
            deliveries
        ),

        (
            "stockouts.csv",
            stockouts
        ),

        (
            "returns.csv",
            returns
        ),

        (
            "adjustments.csv",
            adjustments
        )
    ]

    for filename, rows in datasets:

        if not rows:
            continue

        write_csv(

            SCHEMA / filename,

            rows,

            list(
                rows[0].keys()
            )
        )

    # ========================================================
    # README
    # ========================================================

    readme = """
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
"""

    (
        ROOT / "README.md"
    ).write_text(
        readme.strip()
        + "\n",
        encoding="utf-8"
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 60)
    print("IDEALBUILD COMPLETE")
    print("=" * 60)

    print(
        f"Medicines       : {len(medicines)}"
    )

    print(
        f"Suppliers       : {len(suppliers)}"
    )

    print(
        f"Sales           : {len(sales)}"
    )

    print(
        f"Demand requests : {len(demand_requests)}"
    )

    print(
        f"Stock movements : {len(stock_movements)}"
    )

    print(
        f"Batches         : {len(batches)}"
    )

    print(
        f"Purchases       : {len(purchases)}"
    )

    print(
        f"Deliveries      : {len(deliveries)}"
    )

    print(
        f"Stockouts       : {len(stockouts)}"
    )

    print(
        f"Returns         : {len(returns)}"
    )

    print(
        f"Adjustments     : {len(adjustments)}"
    )

    print()
    print(
        f"DataSource      : {DATA_SOURCE}"
    )

    print(
        f"DataStatus      : {DATA_STATUS}"
    )

    print(
        "Operational use : PROHIBITED"
    )

    print()
    print(
        f"Output directory: {SCHEMA.resolve()}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
