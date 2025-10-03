# Python Name-Matching Exercise

## Overview
This is a data analysis exercise designed to test your ability to match records across datasets based on name matching. You will work with congressional data to identify and link politicians across different datasets.

## Datasets
You will be working with two types of datasets:

1. **Primary Dataset**: `congress_members_with_parties.csv`
   - Contains information about congress members and their party affiliations
   - This is your reference dataset

2. **Election Datasets**: `congressional_elections_YYYY.csv` (where YYYY ranges from 1992 to 2025)
   - Contains congressional election data for each year
   - Multiple files covering elections from 1992 through 2025
   - **Important**: The `status` column in these datasets is unreliable and should be ignored

## Task Objective
Your goal is to **match as many people from the congress members dataset as possible** with records in the election datasets using **name-based matching only**. Use exact and fuzzy matching as you deem fit.

### Technical Specifications
- Implement your solution in Python
- Handle name variations and potential inconsistencies
- Consider different name formats (e.g., "John Smith" vs "Smith, John")
- Account for nicknames, middle names, and common name variations
- Document your matching strategy and assumptions

## Deliverables

1. **Python Script(s)**: Your name-matching implementation. Preferably a single .py script or a jupyter notebook.
2. **Results File**: A CSV or similar file showing:
   - Matched records
   - Confidence scores (if applicable)
   - Unmatched records from the primary dataset
3. **Minimal in-code documentation**: 
   - Explanation of your matching algorithm
   - Assumptions made
   - Challenges encountered and how you addressed them
   - In-code comments/markdown cells are perfectly fine, don't submit a separate document.

## Evaluation Criteria

- **Coverage**: How many congress members you successfully matched
- **Accuracy**: Quality of the matches (avoiding false positives)
- **Code Quality**: Clean, well-documented, and efficient code
- **Documentation**: Clear explanation of your approach and methodology

## Getting Started

1. Clone this repository or - if you prefer - create a private fork.
2. Explore the data structure and identify potential matching challenges
3. Develop and test your matching algorithm
4. Generate results and document your findings

Submit your solutions via email (a single python file and a csv file with your results).
