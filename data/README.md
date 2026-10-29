# Data sources, collection and limitations

## Bengaluru tenant-paid rent index

`market/bengaluru-rent-index-2026-10.csv` is the October 2026 [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index). It summarizes tenant-reported rents from the 90 days ending 6 October 2026. The publisher reports 2,220 citywide reports and permits reuse with attribution. The CSV contains 31 locality/BHK summary rows, not individual property records.

For Koramangala 2 BHK, this source reports a ₹25,000 median from 22 paid-rent reports, down from ₹35,000 in the previous 90-day period. This measures what a small set of tenants reported paying. It does not mean every current 2 BHK is listed or available at that rent; it has no size, block, furnishing or building-quality adjustment.

## Dated asking-price research snapshot

`market/koramangala-asking-listings-2026-10.csv` contains 17 numeric examples manually transcribed from the publicly rendered [Magicbricks Koramangala 2 BHK results page](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr) on 29 October 2026. It stores rents and visible features, not listing text, photos, phone numbers, owner names or exact addresses. Some area fields use carpet, covered or super-area measurements; some page-result rows do not say which basis they use. Many entries have no post date visible. Duplicate reposts, continued availability, negotiated rent and listing authenticity were not independently verified.

The app uses this small file only to display close same-area-basis comparables for Koramangala 2 BHK. It reports the sample count and refuses to show a middle-half range unless there are at least five matches. This is not enough data to train a machine-learning model or to characterize all of Bengaluru.

The source page's FAQ says rents range approximately ₹32,300–₹1.1 lakh, while the current page cards include lower and higher individual examples. These broad figures include different blocks, size, furnishing, quality and charges. Do not read the page-wide range as the expected value of a particular unit.

## Cross-source comparison

`market/koramangala-source-snapshots-2026-10.csv` records published summaries captured on 29 October 2026:

- [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index): 90-day tenant-paid median.
- [MyBharat Rent](https://mybharat.rent/rent-in/bengaluru/koramangala/2-bhk-for-rent): paid-rent p25/median/p75 from 41 reports, with the latest report dated 23 August 2026.
- [Ghar4 Rent](https://www.ghar4.rent/areas/koramangala-bengaluru/2-bhk): asking-post median based on 8 priced posts, 9 live posts, as of 28 October; its source page says it aggregates social posts and rental-site posts.
- [Magicbricks](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr): broad portal asking range, with mixed listing ages and property types.
- [PropertiesNOW](https://propertiesnow.in/bangalore/koramangala): its page reports both an 80-listing median and a separate 100-listing band. Both values are preserved with a note because the source's own estimates differ substantially.

These sources should not be averaged. Paid rents are not asking prices. Community posts can be sparse and unverified. Portal asking ranges include different quality tiers and can include stale or duplicated records. The dashboard exposes their definitions, dates, sample counts and links side by side.

## Why we do not scrape Reddit or portals

This project does not run a crawler. Magicbricks' [terms](https://property.magicbricks.com/terms/terms.html) require prior written consent for automated extraction. Reddit's [Data API terms](https://redditinc.com/policies/data-api-terms) say user content may not be used to train an ML model without express permission from the applicable rights-holder. The published aggregate numbers above are used as research comparisons; Reddit comments and listing descriptions are not copied into a training corpus.

For a future full property-level dataset, use a source that grants collection and reuse rights, or obtain written permission/API access. Record a stable source ID, scrape/collection timestamp, posted date, deduplication key, rent, BHK, exact sublocality, area size and measurement basis, furnishing, bathrooms, maintenance, availability and asking-vs-agreed status. Remove personal data. Retrain only after broad, clean coverage across areas and enough dated observations for a time-based holdout.

## Historical model training data

The old `House_Rent_Dataset.csv` came from the House Rent Prediction Dataset attributed to Sourav Banerjee on [Kaggle](https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset). It covers 4,746 listings from six cities posted April–July 2022; Bengaluru is labelled `Bangalore`. It is kept out of Git because the public mirror does not establish redistribution rights. The 2022 model remains an educational artifact and is not used for the current dashboard estimate.

