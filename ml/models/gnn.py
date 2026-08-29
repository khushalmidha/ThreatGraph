import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATv2Conv

class TemporalGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, edge_dim=None):
        super(TemporalGNN, self).__init__()
        self.conv1 = GATv2Conv(in_channels, hidden_channels, edge_dim=edge_dim)
        self.gru = nn.GRUCell(hidden_channels, hidden_channels)
        self.conv2 = GATv2Conv(hidden_channels, out_channels, edge_dim=edge_dim)
        
    def forward(self, x, edge_index, edge_attr=None, hidden_state=None):
        # Spatial message passing
        x_conv1 = self.conv1(x, edge_index, edge_attr=edge_attr)
        x_conv1 = F.relu(x_conv1)
        
        # Temporal update
        if hidden_state is None:
            hidden_state = torch.zeros_like(x_conv1)
        hidden_state = self.gru(x_conv1, hidden_state)
        
        # Output spatial message passing
        out = self.conv2(hidden_state, edge_index, edge_attr=edge_attr)
        
        return out, hidden_state
