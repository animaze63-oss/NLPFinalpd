# scikit-learn classification metrics

Source: https://scikit-learn.org/stable/modules/model_evaluation.html (scikit-learn 1.9)

```python
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, f1_score,
                             classification_report, confusion_matrix, cohen_kappa_score,
                             balanced_accuracy_score)
```
- `accuracy_score` — "the fraction (default) or the count (normalize=False) of correct predictions."
- `precision_recall_fscore_support` — "Compute precision, recall, F-measure and support for each class."
- `f1_score(average=...)`:
  - `"binary"` — positive class only.
  - `"macro"` — "mean of the binary metrics, giving equal weight to each class."
  - `"weighted"` — weighted "by its presence in the true data sample."
  - `"micro"` — sums the dividends and divisors across classes.
- `classification_report` — text report of the main metrics (use `output_dict=True` for JSON).
- `confusion_matrix` — "each row corresponding to the true class" (columns = predicted).
- `cohen_kappa_score` — agreement beyond chance (use for two human annotators on the aspect sample).
- `balanced_accuracy_score` — "avoids inflated performance estimates on imbalanced datasets… macro-average of recall scores per class." **Report it**: RT reviews are mostly Fresh.

scikit-learn is a build/eval-time dependency only (it is also available in Pyodide 314.0.8, but not needed there).
