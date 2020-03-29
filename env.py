import gym
from gym import spaces

# Constants
N_DISCRETE_ACTIONS = 5  # Nothing, up, down, left, right


class PacmanEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, rows, columns):
        super(PacmanEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input:
        self.observation_space = spaces.Box(
            low=0, high=max(rows, columns), shape=((rows*columns) + (4*2) + 2), dtype=np.uint8)

    def step(self, action):
        # Execute one time step within the environment
        ...

    def reset(self):
        # Reset the state of the environment to an initial state
        ...

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        ...
