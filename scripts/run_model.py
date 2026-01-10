# scripts/run_model.py

import argparse
import os
import csv
import numpy as np
import gymnasium as gym
import ale_py
from typing import Optional
import warnings

gym.register_envs(ale_py)

from stable_baselines3 import DQN
from gymnasium.wrappers.atari_preprocessing import AtariPreprocessing
from gymnasium.wrappers import FrameStackObservation


# ======================== NOISE CLASSES ========================

def _gaussian_std(level):     return [2, 4, 8, 12, 16][level-1]
def _saltpepper_p(level):     return [0.002, 0.005, 0.01, 0.02, 0.05][level-1]
def _blur_kernel(level):      return [3, 5, 7, 9, 11][level-1]
def _framedrop_p(level):      return [0.05, 0.10, 0.20, 0.30, 0.50][level-1]
def _pixel_scale(level):      return [2, 3, 4, 6, 7][level-1]
def _occlusion_cfg(level, h=84, w=84):
    num_blocks = [1, 2, 3, 4, 6][level-1]
    side_min = int(0.10 * min(h, w))
    side_max = int(0.25 * min(h, w))
    side_min = max(1, side_min); side_max = max(side_min, side_max)
    return num_blocks, (side_min, side_max)

def _get_env_rng(env):
    rng = getattr(getattr(env, "unwrapped", env), "np_random", None)
    if rng is None:
        try:
            from gymnasium.utils import seeding
            rng, _ = seeding.np_random(None)
        except Exception:
            rng = np.random.default_rng()
    return rng

class _BaseNoise(gym.ObservationWrapper):
    def __init__(self, env, severity=3):
        super().__init__(env)
        if severity is None:
            severity = 0
        if not (0 <= severity <= 5):
            raise ValueError("severity must be in {0..5}")
        self.severity = severity
        self._orig_shape = getattr(env.observation_space, "shape", None)
        self._kind = _infer_kind(self._orig_shape)
        self.rng = _get_env_rng(env)

    def reset(self, **kwargs):
        obs, info = super().reset(**kwargs)
        self.rng = _get_env_rng(self.env)
        return obs, info

    def _as_chw(self, obs):
        arr = _to_chw(obs, self._kind).astype(np.uint8, copy=False)
        return arr

    def _to_orig(self, chw):
        return _from_chw(chw, self._kind, self._orig_shape)

def _infer_kind(shape):
    if shape is None:
        return "CHW"
    if len(shape) == 2:
        return "HW"
    if len(shape) == 3 and shape[0] in (1, 3, 4):
        return "CHW"
    if len(shape) == 3 and shape[-1] in (1, 3, 4):
        return "HWC"
    raise AssertionError(f"Unsupported obs shape: {shape}")

def _to_chw(obs, kind):
    arr = np.asarray(obs)
    if kind == "HW":
        return arr[None, ...]
    if kind == "CHW":
        return arr
    if kind == "HWC":
        return arr.transpose(2, 0, 1)
    return arr

def _from_chw(chw, kind, orig_shape):
    if kind == "HW":
        return chw[0]
    if kind == "CHW":
        return chw
    if kind == "HWC":
        return chw.transpose(1, 2, 0)
    return chw

def _clip_uint8(x):
    return np.clip(x, 0, 255).astype(np.uint8, copy=False)

class GaussianNoise(_BaseNoise):
    def __init__(self, env, mean=0.0, std=None, severity=3):
        super().__init__(env, severity=severity)
        self.mean = mean
        self._std = std

    def observation(self, obs):
        if self.severity == 0:
            return obs
        x = self._as_chw(obs).astype(np.float32)
        std = self._std if self._std is not None else float(_gaussian_std(self.severity))
        noise = self.rng.normal(self.mean, std, size=x.shape).astype(np.float32)
        y = _clip_uint8(x + noise)
        return self._to_orig(y)

class SaltPepperNoise(_BaseNoise):
    def __init__(self, env, salt_prob=None, pepper_prob=None, severity=3):
        super().__init__(env, severity=severity)
        self._sp = salt_prob
        self._pp = pepper_prob

    def observation(self, obs):
        if self.severity == 0:
            return obs
        x = self._as_chw(obs)
        sp = self._sp if self._sp is not None else _saltpepper_p(self.severity)
        pp = self._pp if self._pp is not None else sp
        salt_mask = self.rng.random(x.shape) < sp
        pepper_mask = self.rng.random(x.shape) < pp
        y = x.copy()
        y[salt_mask] = 255
        y[pepper_mask] = 0
        return self._to_orig(y)

class OcclusionNoise(_BaseNoise):
    def __init__(self, env, num_blocks=None, block_size_range=None, severity=3):
        super().__init__(env, severity=severity)
        self._num_blocks = num_blocks
        self._range = block_size_range

    def observation(self, obs):
        if self.severity == 0:
            return obs
        x = self._as_chw(obs)
        C, H, W = x.shape
        if self._num_blocks is None or self._range is None:
            nb, rng = _occlusion_cfg(self.severity, H, W)
        else:
            nb, rng = self._num_blocks, self._range
        y = x.copy()
        for _ in range(nb):
            hsize = self.rng.integers(rng[0], rng[1] + 1)
            wsize = self.rng.integers(rng[0], rng[1] + 1)
            y0 = self.rng.integers(0, max(1, H - hsize + 1))
            x0 = self.rng.integers(0, max(1, W - wsize + 1))
            y[:, y0:y0 + hsize, x0:x0 + wsize] = 0
        return self._to_orig(y)

class BlurNoise(_BaseNoise):
    def __init__(self, env, kernel_size=None, severity=3):
        super().__init__(env, severity=severity)
        self._ks = kernel_size

    def observation(self, obs):
        if self.severity == 0:
            return obs
        
        # Use faster cv2 if available, otherwise fall back to scipy
        try:
            import cv2
            x = self._as_chw(obs)
            ks = int(self._ks) if self._ks is not None else int(_blur_kernel(self.severity))
            # Ensure kernel size is odd
            ks = ks if ks % 2 == 1 else ks + 1
            
            y = np.empty_like(x, dtype=np.uint8)
            for c in range(x.shape[0]):
                y[c] = cv2.blur(x[c], (ks, ks))
            return self._to_orig(y)
        except ImportError:
            # Fallback to scipy (slower)
            from scipy.ndimage import uniform_filter
            x = self._as_chw(obs).astype(np.float32)
            ks = int(self._ks) if self._ks is not None else int(_blur_kernel(self.severity))
            y = np.empty_like(x, dtype=np.float32)
            for c in range(x.shape[0]):
                y[c] = uniform_filter(x[c], size=ks, mode="nearest")
            y = _clip_uint8(y)
            return self._to_orig(y)

class FrameDropNoise(_BaseNoise):
    def __init__(self, env, drop_prob=None, severity=3):
        super().__init__(env, severity=severity)
        self._p = drop_prob
        self._last_obs_chw = None

    def observation(self, obs):
        if self.severity == 0:
            return obs
        p = float(self._p) if self._p is not None else float(_framedrop_p(self.severity))
        x_chw = self._as_chw(obs)
        if (self._last_obs_chw is None) or (self.rng.random() > p):
            self._last_obs_chw = x_chw.copy()
            return obs
        else:
            return self._to_orig(self._last_obs_chw)

    def reset(self, **kwargs):
        self._last_obs_chw = None
        return super().reset(**kwargs)

class PixelationNoise(_BaseNoise):
    def __init__(self, env, scale_factor=None, severity=3):
        super().__init__(env, severity=severity)
        self._scale = scale_factor

    def observation(self, obs):
        if self.severity == 0:
            return obs
        from scipy.ndimage import zoom
        x = self._as_chw(obs)
        C, H, W = x.shape
        s = int(self._scale) if self._scale is not None else int(_pixel_scale(self.severity))
        s = max(2, int(s))
        small = zoom(x, (1, 1 / s, 1 / s), order=0)
        y = zoom(small, (1, s, s), order=0)
        y = y[:, :H, :W]
        y = _clip_uint8(y)
        return self._to_orig(y)

def make_noise(env, noise_name, severity=3, **maybe_params):
    if noise_name is None:
        return env
    name = str(noise_name).lower()
    p = maybe_params or {}

    if name == "gaussian":
        return GaussianNoise(env, severity=severity, **p)
    if name == "saltpepper":
        return SaltPepperNoise(env, severity=severity, **p)
    if name == "occlusion":
        return OcclusionNoise(env, severity=severity, **p)
    if name == "blur":
        return BlurNoise(env, severity=severity, **p)
    if name == "framedrop":
        return FrameDropNoise(env, severity=severity, **p)
    if name == "pixelation":
        return PixelationNoise(env, severity=severity, **p)

    raise ValueError(f"Unknown noise: {noise_name}")


# ======================== ENVIRONMENT CREATION ========================

class ChannelFirst(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)
        shape = env.observation_space.shape
        assert len(shape) == 3, f"Expected 3D obs, got {shape}"

        axes = list(shape)
        try:
            c_axis = axes.index(4)
        except ValueError:
            raise AssertionError(f"Expected one axis of size 4 (stack), got shape {shape}")

        if c_axis == 0:
            C, H, W = shape
            self._perm = (0, 1, 2)
        elif c_axis == 1:
            H, C, W = shape
            self._perm = (1, 0, 2)
        else:
            H, W, C = shape
            self._perm = (2, 0, 1)

        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=(4, H, W), dtype=np.uint8
        )
        
    def observation(self, obs):
        return np.transpose(obs, self._perm)


def make_env(env_id: str, seed: int = 0, noise_type: Optional[str] = None, 
             noise_params: Optional[dict] = None, severity: int = 3):
    """
    Create environment with optional noise.
    CRITICAL: Noise is applied AFTER FrameStack to match training setup.
    """
    base = gym.make(
        env_id,
        render_mode=None,
        frameskip=1,
        repeat_action_probability=0.0  # Changed from 0.25 - check your training config
    )
    
    env = AtariPreprocessing(
        base,
        screen_size=84,
        grayscale_obs=True,
        frame_skip=4,
        terminal_on_life_loss=True,
        scale_obs=False
    )
    
    # Stack frames FIRST (this is what the model was trained on)
    env = FrameStackObservation(env, 4)
    env = ChannelFirst(env)
    
    # Apply noise AFTER frame stacking
    # This way the model still sees the format it was trained on
    if noise_type:
        params = dict(noise_params or {})
        params.pop("severity", None)
        env = make_noise(env, noise_name=noise_type, severity=severity, **params)

    env.reset(seed=seed)
    return env


# ======================== MAIN EVALUATION ========================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env_id", required=True, help="ALE/Breakout-v5 | ALE/Enduro-v5 | ALE/SpaceInvaders-v5")
    ap.add_argument("--model_path", required=True, help="Path to SB3 .zip")
    ap.add_argument("--episodes", type=int, default=10)
    ap.add_argument("--severity", type=int, default=3,
                help="Noise severity level in [1..5]")
    ap.add_argument("--noise_type", default=None, 
                    choices=["gaussian", "saltpepper", "occlusion", "blur", 
                             "framedrop", "pixelation"],
                    help="Type of noise to apply (None for clean)")
    
    # Noise-specific parameters
    ap.add_argument("--gaussian_std", type=float, default=None)
    ap.add_argument("--salt_prob", type=float, default=None)
    ap.add_argument("--pepper_prob", type=float, default=None)
    ap.add_argument("--num_blocks", type=int, default=None)
    ap.add_argument("--block_size_min", type=int, default=None)
    ap.add_argument("--block_size_max", type=int, default=None)
    ap.add_argument("--blur_kernel", type=int, default=None)
    ap.add_argument("--drop_prob", type=float, default=None)
    ap.add_argument("--scale_factor", type=int, default=None)
    
    args = ap.parse_args()

    # Build noise parameters - only include if explicitly set
    noise_params = {}
    if args.noise_type == "gaussian" and args.gaussian_std is not None:
        noise_params["std"] = args.gaussian_std
    elif args.noise_type == "saltpepper":
        if args.salt_prob is not None:
            noise_params["salt_prob"] = args.salt_prob
        if args.pepper_prob is not None:
            noise_params["pepper_prob"] = args.pepper_prob
    elif args.noise_type == "occlusion":
        if args.num_blocks is not None:
            noise_params["num_blocks"] = args.num_blocks
        if args.block_size_min is not None and args.block_size_max is not None:
            noise_params["block_size_range"] = (args.block_size_min, args.block_size_max)
    elif args.noise_type == "blur" and args.blur_kernel is not None:
        noise_params["kernel_size"] = args.blur_kernel
    elif args.noise_type == "framedrop" and args.drop_prob is not None:
        noise_params["drop_prob"] = args.drop_prob
    elif args.noise_type == "pixelation" and args.scale_factor is not None:
        noise_params["scale_factor"] = args.scale_factor

    # First test without noise to ensure model loads correctly
    print("Creating evaluation environment...")
    env = make_env(args.env_id, seed=0, noise_type=args.noise_type, 
                   noise_params=noise_params, severity=args.severity)    
    print("Observation space:", env.observation_space)
    
    noise_label = args.noise_type if args.noise_type else "clean"
    print(f"Running with noise type: {noise_label}, severity: {args.severity}")

    # Load model with better error handling
    print(f"Loading model from {args.model_path}...")
    try:
        # Fix the replay buffer incompatibility issue
        custom_objects = {
            "learning_rate": 0.0,  # Placeholder, not used during inference
            "lr_schedule": lambda _: 0.0,
            "clip_range": lambda _: 0.0,
            "optimize_memory_usage": False,  # Disable to avoid incompatibility
            "handle_timeout_termination": True  # Keep this enabled
        }
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            model = DQN.load(
                args.model_path, 
                env=env, 
                device="auto",
                custom_objects=custom_objects
            )
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Make sure the model file exists and matches the environment configuration.")
        return

    # Test single step before full evaluation
    print("\nTesting model with single step...")
    obs, _ = env.reset(seed=0)
    print(f"Observation shape: {obs.shape}, dtype: {obs.dtype}")
    print(f"Observation range: [{obs.min()}, {obs.max()}]")
    
    action, _ = model.predict(obs, deterministic=True)
    print(f"Predicted action: {action}")
    
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step reward: {reward}, terminated: {terminated}, truncated: {truncated}")
    
    # Run full evaluation
    print(f"\nRunning {args.episodes} episodes...")
    ep_returns, ep_steps = [], []
    
    import time
    start_time = time.time()

    for ep in range(args.episodes):
        ep_start = time.time()
        obs, _ = env.reset(seed=ep)
        done = False
        ret, steps = 0.0, 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, r, terminated, truncated, _ = env.step(action)
            ret += r
            steps += 1
            done = terminated or truncated
            
            # Prevent infinite loops
            if steps > 50000:
                print(f"Episode {ep+1} exceeded 50000 steps, terminating...")
                break
        
        ep_time = time.time() - ep_start
        ep_returns.append(ret)
        ep_steps.append(steps)
        print(f"[{args.env_id}] Episode {ep+1}/{args.episodes}: return={ret:.1f}, steps={steps}, time={ep_time:.1f}s")
    
    total_time = time.time() - start_time
    print(f"\nTotal evaluation time: {total_time:.1f}s ({total_time/args.episodes:.1f}s per episode)")

    # Summary statistics
    mean_ret = float(np.mean(ep_returns)) if ep_returns else 0.0
    std_ret = float(np.std(ep_returns)) if ep_returns else 0.0
    print(f"[{args.env_id}] Summary over {args.episodes} eps: mean_return={mean_ret:.2f}, std={std_ret:.2f}")

    # Save results
    os.makedirs("results", exist_ok=True)
    
    # Extract game name from env_id (e.g., "Breakout" from "ALE/Breakout-v5")
    game_raw = args.env_id.split("/")[-1]  # "Breakout-v5"
    model_name = game_raw.split("-")[0]     # "Breakout"
    
    # Create filename based on noise type
    if args.noise_type:
        noise_label_file = args.noise_type.capitalize()
        csv_filename = f"results/{model_name}_{noise_label_file}_{args.severity}.csv"
    else:
        csv_filename = f"results/{model_name}_Clean.csv"
    
    with open(csv_filename, "w", newline="") as f:
        w = csv.writer(f)
        # Header with metadata
        w.writerow(["env_id", args.env_id])
        w.writerow(["noise_type", args.noise_type if args.noise_type else "None"])
        w.writerow(["severity", args.severity if args.noise_type else "N/A"])
        w.writerow(["episodes", args.episodes])
        w.writerow([])  # Blank line
        
        # Episode results
        w.writerow(["episode", "return", "steps"])
        for i, (r, s) in enumerate(zip(ep_returns, ep_steps), start=1):
            w.writerow([i, float(r), int(s)])
    
    print(f"\nSaved results to {csv_filename}")
    env.close()


if __name__ == "__main__":
    main()