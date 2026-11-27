# pandas essentials for curation

Sources: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html, https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html (pandas 3.1 docs)

## read_csv for a large file
- `usecols` — "Subset of columns to select" (cuts memory a lot).
- `dtype` — set per column (e.g. `{"top_critic": "boolean"}`).
- `chunksize` — returns a `TextFileReader` to iterate chunks; filter each chunk to sci-fi links and concat.
- `nrows` — "Useful for reading pieces of large files" (quick schema checks).
- `parse_dates`, `na_values`, `keep_default_na`, `encoding="utf-8"`, `on_bad_lines`, `engine` ("C and pyarrow engines are faster"), `low_memory`.

## merge
`DataFrame.merge(right, how='inner', on=None, left_on=None, right_on=None, suffixes=('_x','_y'), indicator=False, validate=None)`
- `how`: left / right / outer / inner / cross; pandas 3.0 added `left_anti` / `right_anti`.
- `indicator=True` adds `_merge` (`left_only` / `right_only` / `both`) — use it to report unmatched reviews.
- `validate="m:1"` "check if merge keys are unique in right dataset" — use when joining reviews → movies.

```python
reviews = pd.concat(
    c[c.rotten_tomatoes_link.isin(scifi_links)]
    for c in pd.read_csv(path, usecols=[...], chunksize=200_000))
df = reviews.merge(movies, on="rotten_tomatoes_link", how="inner", validate="m:1")
```
