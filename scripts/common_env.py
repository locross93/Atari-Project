# scripts/common_env.py
import numpy as np
import gymnasium as gym
import ale_py
from gymnasium.wrappers.atari_preprocessing import AtariPreprocessing
from gymnasium.wrappers import FrameStackObservation

gym.register_envs(ale_py)

class ChannelFirst(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)
        shape = env.observation_space.shape
        assert len(shape) == 3, f"Expected 3D obs, got {shape}"
        axes = list(shape)
        try:
            c_axis = axes.index(4)
        except ValueError:
            raise AssertionError(f"Expected one axis length 4 (stack), got {shape}")
        if c_axis == 0:
            C, H, W = shape
            self._perm = (0, 1, 2)
        elif c_axis == 1:
            H, C, W = shape
            self._perm = (1, 0, 2)
        else:
            H, W, C = shape
            self._perm = (2, 0, 1)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(4, H, W), dtype=np.uint8)

    def observation(self, obs):
        return np.transpose(obs, self._perm)

def make_env_clean(env_id: str, seed: int = 0):
    base = gym.make(
        env_id,
        render_mode=None,
        frameskip=1,                 # IMPORTANT: no skip here
        repeat_action_probability=0.25
    )
    env = AtariPreprocessing(
        base,
        screen_size=84,
        grayscale_obs=True,
        frame_skip=4,                # apply skip here (one place only)
        terminal_on_life_loss=True,
        scale_obs=False
    )
    env = FrameStackObservation(env, 4)  # produces one axis of size 4
    env = ChannelFirst(env)              # force (4, 84, 84) for SB3 DQN checkpoints
    env.reset(seed=seed)
    return env

class NoiseObs(gym.ObservationWrapper):
    def __init__(self, env, noise_fn):
        super().__init__(env); self.noise_fn = noise_fn
    def observation(self, obs):
        return self.noise_fn(obs)

def make_env_with_noise(env_id: str, noise_fn, seed: int = 0):
    base = gym.make(
        env_id,
        render_mode=None,
        frameskip=1,                 # IMPORTANT
        repeat_action_probability=0.25
    )
    base = NoiseObs(base, noise_fn)     # add noise on raw RGB frames
    env = AtariPreprocessing(
        base,
        screen_size=84,
        grayscale_obs=True,
        frame_skip=4,
        terminal_on_life_loss=True,
        scale_obs=False
    )
    env = FrameStackObservation(env, 4)
    env = ChannelFirst(env)
    env.reset(seed=seed)
    return env
