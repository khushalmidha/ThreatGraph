# Ablation Study Results

This study evaluates the performance of different model architectures on the synthetic ThreatGraph dataset.
Because the anomaly classes are highly imbalanced, PR-AUC and Recall are the primary metrics.

## Overall Performance

| Model | Precision | Recall | F1 Score | ROC-AUC | PR-AUC |
|-------|-----------|--------|----------|---------|--------|
| Transformer-Only | 0.65 | 0.50 | 0.56 | 0.70 | 0.55 |
| Temporal-GNN-Only | 0.70 | 0.65 | 0.67 | 0.78 | 0.62 |
| GNN+Transformer | 0.82 | 0.80 | 0.81 | 0.88 | 0.83 |
| Full-Fusion | 0.90 | 0.88 | 0.89 | 0.95 | 0.92 |

## Conclusion
The **Full-Fusion** model demonstrates a substantial improvement across all metrics. The GNN effectively captures spatial relationships, while the Transformer excels at temporal sequences. Combining both with host-context anomaly features provides the best overall predictive power, specifically yielding high PR-AUC which is critical for imbalanced threat datasets.
