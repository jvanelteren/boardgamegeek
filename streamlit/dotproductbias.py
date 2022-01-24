from torch.nn import Module

class DotProductBias(Module):
    def __init__(self, n_users, n_games, n_factors, y_range=(0.5,10.5)):
        super().__init__()
        self.user_factors = create_params([n_users, n_factors])
        self.user_bias = create_params([n_users])
        self.game_factors = create_params([n_games, n_factors])
        self.game_bias = create_params([n_games])
        self.y_range = y_range
        
    def forward(self, x):
        users = self.user_factors[x[:,0]]
        games = self.game_factors[x[:,1]]
        res = (users*games).sum(dim=1)
        res += self.user_bias[x[:,0]] + self.game_bias[x[:,1]]
        return sigmoid_range(res, *self.y_range)