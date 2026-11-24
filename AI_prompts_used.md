# AI Prompts Used – USD/INR IFM Project

## 1. Data cleaning
I am completing an undergraduate International Financial Management assignment using USD/INR data. Combine the five uploaded FRED CSV files into one monthly dataset from January 2020 onward. Convert daily USD/INR to the last available quote in each calendar month, align all monthly series by date, retain missing values as blank, and report the source coverage and missing observations. Do not impute data.

## 2. PPP
Using USD/INR quoted as INR per USD, calculate relative PPP using the first available month as the base month. Calculate misalignment as (actual spot / PPP-implied spot - 1) × 100. Explain the sign convention and plot actual versus PPP-implied exchange rates.

## 3. Interest rates and UIP comparison
Calculate the US-minus-India nominal interest-rate differential and trailing 12-month USD/INR percentage change. Explain the UIP sign convention for INR per USD and make clear that realised past changes are descriptive rather than expected future changes.

## 4. Carry trade
Model a simplified 12-month unhedged trade that borrows INR, invests in USD, and converts back into INR after 12 months. Calculate the realised return using the start and end spot rates and the two nominal rates. Calculate a base-100 profitability index and state all assumptions and limitations.

## 5. IFE
Calculate year-on-year US and India CPI inflation, the inflation differential and nominal interest-rate differential. Use complete paired observations only. Calculate Pearson correlation, OLS regression and R-squared, and explain that realised CPI inflation is only a proxy for expected inflation.

## 6. Dashboard
Create a Streamlit dashboard with three tabs: PPP and misalignment; interest-rate differential and carry trade; and International Fisher Effect. Include charts, metrics, formulas, data sources, interpretation rules, missing-data handling and limitations.

## 7. Report and validation
Prepare a findings report and methodology document using only the supplied dataset. Cross-check every reported figure and observation count against the actual merged data. Do not invent or impute missing data.
