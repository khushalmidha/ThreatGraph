import torch
import torch.nn as nn
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ml.models.gnn import TemporalGNN

class TransformerEncoder(nn.Module):
    def __init__(self, in_features, hidden_dim, num_layers=2):
        super().__init__()
        encoder_layer = nn.TransformerEncoderLayer(d_model=in_features, nhead=4, dim_feedforward=hidden_dim, batch_first=False)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(in_features, hidden_dim)

    def forward(self, x):
        # x is (seq_len, batch, features)
        out = self.transformer(x)
        return self.fc(out[-1]) # take last sequence element

class FusionModel(nn.Module):
    def __init__(self, node_features, edge_features, seq_features, hidden_dim, num_classes=3):
        super().__init__()
        self.gnn = TemporalGNN(node_features, hidden_dim, hidden_dim, edge_dim=edge_features)
        self.transformer = TransformerEncoder(seq_features, hidden_dim)
        
        # Fusion layer
        self.fusion_fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Classification Heads
        self.threat_prob = nn.Sequential(nn.Linear(hidden_dim, 1), nn.Sigmoid())
        self.anomaly_score = nn.Linear(hidden_dim, 1)
        self.threat_class = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, gnn_x, gnn_edge_index, gnn_edge_attr, seq_x, hidden_state=None):
        # 1. GNN path
        gnn_out, next_hidden = self.gnn(gnn_x, gnn_edge_index, edge_attr=gnn_edge_attr, hidden_state=hidden_state)
        # Pool GNN out (mean over nodes) to get graph embedding
        gnn_pooled = gnn_out.mean(dim=0, keepdim=True)
        
        # 2. Transformer path
        trans_out = self.transformer(seq_x)
        
        # 3. Fusion
        # Handle batch dim correctly
        if gnn_pooled.dim() == 2 and trans_out.dim() == 2:
            if gnn_pooled.size(0) == 1 and trans_out.size(0) > 1:
                 gnn_pooled = gnn_pooled.expand(trans_out.size(0), -1)
            elif trans_out.size(0) == 1 and gnn_pooled.size(0) > 1:
                 trans_out = trans_out.expand(gnn_pooled.size(0), -1)

        fused = torch.cat([gnn_pooled, trans_out], dim=-1)
        fused_embedding = self.fusion_fc(fused)
        
        prob = self.threat_prob(fused_embedding)
        anomaly = self.anomaly_score(fused_embedding)
        classes = self.threat_class(fused_embedding)
        
        return {
            "threat_probability": prob,
            "anomaly_score": anomaly,
            "threat_class": classes,
            "threat_embedding": fused_embedding,
            "hidden_state": next_hidden
        }
