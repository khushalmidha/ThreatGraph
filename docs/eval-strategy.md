# Training and Evaluation Strategy

## Data Split
- **Time-based 60/20/20 split**: Data is divided temporally rather than randomly. 
- *Rationale*: Random splitting in network traffic leads to data leakage (future events predicting past events). A time-based split correctly evaluates the model's ability to generalize to unseen, future attacks.

## Metrics
- Precision
- Recall
- F1-Score
- ROC-AUC
- PR-AUC (Priority metric due to severe class imbalance of threat vs normal)
- FPR (False Positive Rate)
- FNR (False Negative Rate)
- Latency (inference time per event/window)

## Ablation Matrix
We evaluate multiple architectural configurations against classical ML baselines:

1. **Transformer-only**: Per-host temporal behavioral sequences.
2. **GNN-only**: Temporal graph network (spatial relationships only).
3. **GNN + Transformer**: Fusion of spatial and temporal embeddings.
4. **GNN + Transformer + Anomaly Detector**: Supervised fusion augmented with unsupervised graph autoencoder scores.

*Baselines for comparison*: XGBoost, Random Forest, Logistic Regression, MLP, Isolation Forest.
