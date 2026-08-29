import torch
import torch.nn.functional as F
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ml.models.gnn import TemporalGNN

def train_dummy_step():
    # Setup model
    in_channels = 16
    hidden_channels = 32
    out_channels = 16
    edge_dim = 4
    
    model = TemporalGNN(in_channels, hidden_channels, out_channels, edge_dim=edge_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Dummy data: 10 nodes, 20 edges
    num_nodes = 10
    num_edges = 20
    
    x = torch.randn(num_nodes, in_channels)
    edge_index = torch.randint(0, num_nodes, (2, num_edges))
    edge_attr = torch.randn(num_edges, edge_dim)
    
    model.train()
    optimizer.zero_grad()
    
    # Forward pass (autoencoder/reconstruction setup)
    out, hidden_state = model(x, edge_index, edge_attr)
    
    # Dummy loss: reconstruction of input features
    loss = F.mse_loss(out, x)
    loss.backward()
    optimizer.step()
    
    print(f"Dummy training step completed. Loss: {loss.item():.4f}")
    
    # Export model to TorchScript
    os.makedirs(os.path.dirname(os.path.dirname(__file__)) + "/exports", exist_ok=True)
    export_path = os.path.dirname(os.path.dirname(__file__)) + "/exports/temporal_gnn.pt"
    
    # For torchscript tracing we need example inputs
    # Use JIT tracing
    with torch.no_grad():
        model.eval()
        traced_model = torch.jit.trace(model, (x, edge_index, edge_attr))
        torch.jit.save(traced_model, export_path)
        print(f"Model exported to {export_path}")

if __name__ == "__main__":
    train_dummy_step()
