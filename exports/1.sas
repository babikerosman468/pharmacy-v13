PROC IMPORT DATAFILE="sales.csv"
OUT=sales_db
DBMS=CSV
REPLACE;
GETNAMES=YES;
RUN;

DATA sales_prepared;
SET sales_db;
date_num = INPUT(date, ANYDTDTE.);
FORMAT date_num DATE9.;
RUN;

PROC SORT DATA=sales_prepared;
BY date_num;
RUN;

PROC ESM DATA=sales_prepared
OUT=forecast_results
METHOD=WINTERS
TREND=LINEAR
SEASONAL=ADD;
ID date_num INTERVAL=DAY;
FORECAST total;
RUN;

PROC PRINT DATA=forecast_results;
RUN;


