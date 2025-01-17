"""
Defines a pytorch policy as the agent's actor

Functions to edit:
    2. forward
    3. update
"""

import abc
import itertools
import sys
from typing import Any
from torch import nn
from torch.nn import functional as F
from torch import optim

import numpy as np
import torch
from torch import distributions, normal
from pathlib import Path

# Get the current file's directory
current_directory = Path(__file__).resolve().parent

# Move up one directory
parent_directory = current_directory.parent

# Add the parent directory to sys.path
sys.path.append(str(parent_directory))

from infrastructure import pytorch_util as ptu
from policies.base_policy import BasePolicy


def build_mlp(input_size: int, output_size: int, n_layers: int, size: int) -> nn.Module:
    """
    Builds a feedforward neural network

    arguments:
        n_layers: number of hidden layers
        size: dimension of each hidden layer
        activation: activation of each hidden layer

        input_size: size of the input layer
        output_size: size of the output layer
        output_activation: activation of the output layer

    returns:
        MLP (nn.Module)
    """
    layers = []
    in_size = input_size
    for _ in range(n_layers):
        layers.append(nn.Linear(in_size, size))
        layers.append(nn.Tanh())
        in_size = size
    layers.append(nn.Linear(in_size, output_size))

    mlp = nn.Sequential(*layers)
    return mlp


class MLPPolicySL(BasePolicy, nn.Module, metaclass=abc.ABCMeta):
    """
    Defines an MLP for supervised learning which maps observations to continuous
    actions.

    Attributes
    ----------
    mean_net: nn.Sequential
        A neural network that outputs the mean for continuous actions
    logstd: nn.Parameter
        A separate parameter to learn the standard deviation of actions

    Methods
    -------
    forward:
        Runs a differentiable forwards pass through the network
    update:
        Trains the policy with a supervised learning objective
    """

    def __init__(
        self,
        ac_dim,
        ob_dim,
        n_layers,
        size,
        learning_rate=1e-4,
        training=True,
        nn_baseline=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # init vars
        self.ac_dim = ac_dim
        self.ob_dim = ob_dim
        self.n_layers = n_layers
        self.size = size
        self.learning_rate = learning_rate
        self.training = training
        self.nn_baseline = nn_baseline

        self.mean_net = build_mlp(
            input_size=self.ob_dim,
            output_size=self.ac_dim,
            n_layers=self.n_layers,
            size=self.size,
        )
        self.mean_net.to(ptu.device)
        self.logstd = nn.Parameter(
            torch.zeros(self.ac_dim, dtype=torch.float32, device=ptu.device)
        )
        self.logstd.to(ptu.device)
        self.optimizer = optim.Adam(
            itertools.chain([self.logstd], self.mean_net.parameters()),
            self.learning_rate,
        )

    def save(self, filepath):
        """
        :param filepath: path to save MLP
        """
        torch.save(self.state_dict(), filepath)

    def forward(self, observation: torch.FloatTensor) -> Any:
        """
        Defines the forward pass of the network

        :param observation: observation(s) to query the policy
        :return:
            action: sampled action(s) from the policy
        """
        # TODO: implement the forward pass of the network.
        # You can return anything you want, but you should be able to differentiate
        # through it. For example, you can return a torch.FloatTensor. You can also
        # return more flexible objects, such as a
        # `torch.distributions.Distribution` object. It's up to you!

        # Calculate mean of policy distribution (mapping of states to actions)
        observation = np.array([observation])
        #print(observation.shape)
        observation_tensor = ptu.from_numpy(observation)
        #print(observation_tensor.shape)
        # breakpoint()
        self.mean_net.to(0)
        mean = self.mean_net(observation_tensor)
        # Take exp of log std to get std of distribution
        # log std and mean are learned separately but optimized together
        # Learn log std instead of std so it can always be exponentiated and made positive
        std = torch.exp(self.logstd)
        # Create distribution using torch.normal
        action = normal(mean, std)
        # Return the action sampled from the policy
        return action

    def update(self, observations, actions):
        """
        Updates/trains the policy

        :param observations: observation(s) to query the policy
        :param actions: actions we want the policy to imitate
        :return:
            dict: 'Training Loss': supervised learning loss
        """
        actions_tensor = ptu.from_numpy(actions)
        actions_tensor = actions_tensor.unsqueeze(0)
        # print(actions_tensor.shape)
        predicted_actions = self.forward(observations)
        # print(predicted_actions.shape)
        # print(f"actions_tensor: {actions_tensor}")
        # print(f"predicted actions: {predicted_actions}")

        # Compute the loss between the predicted actions and the expert actions
        # Using torch.functional.mse loss cause its function and no need to instantiat class
        # like you need to with torch.nn.mseloss
        loss = F.mse_loss(
            predicted_actions, actions_tensor
        )  # Using Mean Squared Error loss

        # Zero gradients before backpropagation
        self.optimizer.zero_grad()

        # Backpropagate the loss
        loss.backward()

        # Step the optimizer
        self.optimizer.step()

        return {
            # You can add extra logging information here, but keep this line
            "Training Loss": ptu.to_numpy(loss),
        }
