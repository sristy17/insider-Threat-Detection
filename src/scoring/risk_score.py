def compute(row):
    return (
        0.35 * row["if_score"] +
        0.35 * row["svm_score"] +
        0.2  * row["sensitive_total"] +
        0.1  * row["failed_total"]
    )
