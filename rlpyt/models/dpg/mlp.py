
import torch
import torch.nn.function as F

from rlpyt.utils.tensor import infer_leading_dims, restore_leading_dims


class MlpMuModel(torch.nn.Module):

    def __init__(
            self,
            observation_size,
            action_size,
            hidden_sizes,
            output_max=1,
            nonlinearity=F.relu,
            obs_n_dim=1,
            ):
        super().__init__()
        self.obs_n_dim = obs_n_dim
        self.output_max = output_max
        hidden_layers = [torch.nn.Linear(observation_size, hidden_sizes[0]),
            nonlinearity]
        for h_in, h_out in zip(hidden_sizes[:-1], hidden_sizes[1:]):
            hidden_layers.extend([torch.nn.Linear(h_in, h_out), nonlinearity])
        self.hidden_layers = torch.nn.Sequential(hidden_layers)
        self.output = torch.nn.Linear(hidden_sizes[-1], action_size)

    def forward(self, observation, prev_action, prev_reward):
        obs_shape, T, B, has_T, has_B = infer_leading_dims(observation,
            self.obs_n_dim)
        fc_input = observation.view(T * B, -1)
        fc_output = self.hidden_layers(fc_input)
        mu = self.output_max * F.tanh(self.output(fc_output))
        mu = restore_leading_dims(mu, T, B, has_T, has_B)
        return mu


class MlpQModel(torch.nn.Module):

    def __init__(
            self,
            observation_size,
            action_size,
            hidden_sizes,
            nonlinearity=F.relu,
            obs_n_dim=1,
            ):
        super().__init__()
        self.obs_n_dim
        hidden_layers = [torch.nn.Linear(observation_size + action_size,
            hidden_sizes[0]), nonlinearity]
        for h_in, h_out in zip(hidden_sizes[:-1], hidden_sizes[1:]):
            hidden_layers.extend([torch.nn.Linear(h_in, h_out), nonlinearity])
        self.hidden_layers = torch.nn.Sequential(hidden_layers)
        self.output = torch.nn.Linear(hidden_sizes[-1], 1)

    def forward(self, observation, prev_action, prev_reward, action):
        obs_shape, T, B, has_T, has_B = infer_leading_dims(observation,
            self.obs_n_dim)
        fc_input = torch.cat([observation.view(T * B, -1),
            action.view(T * B, -1)], dim=-1)
        fc_output = self.hidden_layers(fc_input)
        q = self.output(fc_output).squeeze(-1)
        q = restore_leading_dims(q, T, B, has_T, has_B)
        return q
