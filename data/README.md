# Dataset notes

`raw/House_Rent_Dataset.csv` is the House Rent Prediction Dataset, attributed on Kaggle to Sourav Banerjee and commonly described as scraped from MagicBricks. It contains 4,746 listings from six Indian cities, posted April–July 2022. The original `City` value for Bengaluru is `Bangalore`; the training script filters to those rows.

The CSV was downloaded from a public GitHub mirror of the Kaggle dataset. The mirror does not establish redistribution rights. For a public release or commercial use, obtain the dataset from its original Kaggle page and verify its current terms: https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset

Source mirror: https://github.com/wajahathalinajmi/INDIAN-RENTAL-ANALYSIS/blob/main/House_Rent_Dataset.csv

These are historical advertised listings, not verified signed leases or current listings. They are suitable for an educational prototype, not for a reliable current-market valuation.

## Current market benchmark

`market/bengaluru-rent-index-2026-10.csv` is the October 2026 Bengaluru Rent Index from [bengaluru.rent](https://bengaluru.rent/bengaluru-rent-index). It summarizes tenant-reported rents from the 90 days ending 6 October 2026, including the area, BHK, median rent, and number of reports. The publisher permits reuse with attribution and a link, which this project provides.

This file has 31 area/BHK aggregates, not the 2,220 individual reports. It is useful as a current neighborhood benchmark, but it does not contain each home's size, bathroom count, or furnishing. It is therefore not enough to retrain the current property-level regression model. The app shows this benchmark separately from the older model prediction so their different meanings are clear.

