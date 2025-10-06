## **Overview**

The goal was to match candidate names from several congressional election files to a master list of congressional members using only name information. The available data included a primary dataset (`congress_members_with_parties.csv`) with roughly 2,900 members and several year‑specific election datasets (`congressional_elections_YYYY.csv` for 2019–2025). Each election file contained candidate names, party affiliations and basic metadata; however, the “status” column was considered unreliable and was ignored.

## **Approach**

1.  **Data Loading and Inspection.** All members were read into a pandas DataFrame. Each member’s canonical name was constructed by concatenating the `first_name` and `last_name` fields and normalised by lowercasing, stripping whitespace and removing punctuation. A dictionary mapping these normalised names to their row indices was built to enable constant‑time exact matching.

2.  **Election File Handling.** All election files matching the prescribed pattern were discovered. To prevent processing empty or malformed datasets, files were filtered out if reading them produced an empty DataFrame or raised an exception. Only files with data were retained.

3.  **Exact and Fuzzy Matching.** For each candidate in the election data, the candidate’s name was normalised in the same way as the members’. An exact match check was performed against the lookup dictionary. If an exact match was found, the candidate was linked to the corresponding member with full confidence. For names without an exact match, a fuzzy match was attempted using `rapidfuzz.fuzz.token_sort_ratio`, which is robust to token reordering (e.g., `Nyajuoga, Joseph` vs. `Joseph Nyajuoga`). The candidate was linked to the member with the highest similarity score if that score exceeded 85%; otherwise it was left unmatched.

4.  **Result Compilation.** The matching process produced a list of results containing the candidate’s name, party, year, whether a match was found, the matched member’s details (if any) and a confidence score. A summary of members who were never matched in any election file was also generated. All results were saved to CSV files for reporting.

## **Challenges and Mitigations**

-   **Name Variations and Punctuation.** Candidate names appeared in various formats (e.g., with commas, initials or suffixes). Normalisation included removing punctuation and collapsing extra spaces, allowing consistent comparison between “John A. Smith” and “Smith, John.”

-   **Data Completeness.** Some election files were missing or contained no data. Skipping empty files prevented errors and false negatives.

-   **Duplicate Names.** Occasionally multiple members shared the same name. The matching process retained the first occurrence for exact matches and used the highest fuzzy score to select among potential matches, although this could still conflate distinct individuals with identical names.

-   **Performance.** Fuzzy matching all remaining candidates against \~2,900 members could be computationally intensive. Precomputing normalised member names and using the efficient `rapidfuzz` library reduced the overhead.

Overall, combining a normalised exact match with token‑based fuzzy matching provided good coverage while avoiding many false positives.

## **Summary Results** 
> [!summary] 
> 1. Total candidates compared: 24244 
> 2. Number of matches: 7615 
> 3. Number of exact matches: 4377 
> 4. Number of fuzzy matches: 3238 
> 5. Number of unmatched candidates: 16629 
> 6. Unique members matched: 1576 of 2873 
> 7. Members unmatched: 1297