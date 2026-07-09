"""LingBot-World-v2 (LingBot-World-Infinity) adapter for the shared demo.

Lives OUTSIDE baselines/demo so the demo repo stays unmodified. Loaded via:
  WM_DEMO_MODEL=lingbot
  WM_DEMO_ADAPTER=ext_adapters.lingbot_world_v2:LingBotWorldV2Adapter
  PYTHONPATH=<this directory's parent>
  LINGBOT_WORLD_ROOT=<lingbot-world-v2 repo>          (pipeline code, `wan` package)
  LINGBOT_WORLD_CKPT_DIR=<lingbot-world-v2-14b-causal-fast checkpoint>
  LINGBOT_DEMO_LOCAL_ATTN_SIZE=18 LINGBOT_DEMO_SINK_SIZE=6   (official run_fast.sh values)

Subclasses the v1 adapter: the interactive protocol, control-file format
(poses/intrinsics npy), and generate() signature are identical. Differences:
  - pipeline class is wan.WanI2VCausal (infer_mode="causal_fast")
  - checkpoint layout: transformers/ shards + T5 + VAE at the root
  - the action-string -> trajectory helpers (wasd_ijkl_to_c2ws) are not shipped
    in v2, so they are loaded from the v1 repo (pure numpy/torch, model-agnostic).
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from adapters.lingbot_world import LingBotWorldAdapter

_V1_ROOT_DEFAULT = Path(__file__).resolve().parents[2] / "lingbot-world"


class LingBotWorldV2Adapter(LingBotWorldAdapter):
    name = "lingbot-world-v2"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("model_size", "small")  # take the fast/causal code path
        self.v1_root = Path(os.environ.get("LINGBOT_V1_ROOT") or _V1_ROOT_DEFAULT).resolve()
        self.infer_mode = os.environ.get("LINGBOT_V2_INFER_MODE", "causal_fast")
        self._traj_mod = None
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------- helpers
    def _trajectory_module(self):
        if self._traj_mod is None:
            path = self.v1_root / "wan" / "utils" / "wasd_ijkl_to_c2ws.py"
            spec = importlib.util.spec_from_file_location("lingbot_v1_wasd_ijkl_to_c2ws", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._traj_mod = mod
        return self._traj_mod

    def combined_video_name(self, sid: str) -> str:
        return f"lingbot_world_v2_{self.infer_mode}_{sid}.mp4"

    # ------------------------------------------------------------ validation
    def _validate_paths(self) -> None:
        required = [
            self.lingbot_root / "wan" / "__init__.py",
            self.ckpt_dir / "Wan2.1_VAE.pth",
            self.ckpt_dir / "models_t5_umt5-xxl-enc-bf16.pth",
            self.ckpt_dir / "transformers",
            self.v1_root / "wan" / "utils" / "wasd_ijkl_to_c2ws.py",
        ]
        missing = [str(p) for p in required if not p.exists()]
        if missing:
            raise FileNotFoundError("Missing LingBot-World-v2 files: " + ", ".join(missing))

    # ---------------------------------------------------------------- load
    def load(self) -> None:
        if self.dry_run:
            print("[LingBotV2][load] dry run enabled; skipping model load", flush=True)
            self.pipeline = "dry-run"
            return

        def log(step: str) -> None:
            print(f"[LingBotV2][load] {step}", flush=True)

        log("validate paths")
        self._validate_paths()
        if str(self.lingbot_root) not in sys.path:
            sys.path.insert(0, str(self.lingbot_root))

        import torch
        import torch.distributed as dist
        import wan
        from wan.configs import MAX_AREA_CONFIGS, WAN_CONFIGS

        if not torch.cuda.is_available():
            raise RuntimeError("LingBot-World-v2 inference requires CUDA")
        if dist.is_available() and dist.is_initialized():
            self.rank = dist.get_rank()
            world_size = dist.get_world_size()
            self.device_id = int(os.environ.get("LOCAL_RANK", self.device_id))
            self.t5_fsdp = self.t5_fsdp or world_size > 1
            self.dit_fsdp = self.dit_fsdp or world_size > 1
            self.use_sp = self.use_sp or world_size > 1
            log(f"distributed world size={world_size}")
        log(f"set CUDA device {self.device_id}")
        torch.cuda.set_device(self.device_id)

        log(f"load config for task {self.task}")
        cfg = WAN_CONFIGS[self.task]
        self._wan = wan
        self._wan_configs = WAN_CONFIGS
        self._max_area_configs = MAX_AREA_CONFIGS
        if self.sample_steps is None:
            self.sample_steps = cfg.sample_steps
        if self.sample_shift is None:
            self.sample_shift = cfg.sample_shift
        if self.sample_guide_scale is None:
            self.sample_guide_scale = cfg.sample_guide_scale

        log(
            f"build WanI2VCausal infer_mode={self.infer_mode} "
            f"local_attn_size={self.local_attn_size} sink_size={self.sink_size}"
        )
        self.pipeline = wan.WanI2VCausal(
            config=cfg,
            checkpoint_dir=str(self.ckpt_dir),
            device_id=self.device_id,
            rank=self.rank,
            t5_fsdp=self.t5_fsdp,
            dit_fsdp=self.dit_fsdp,
            use_sp=self.use_sp,
            t5_cpu=self.t5_cpu,
            init_on_cpu=False,
            convert_model_dtype=self.convert_model_dtype,
            local_attn_size=self.local_attn_size,
            sink_size=self.sink_size,
            infer_mode=self.infer_mode,
        )
        log("pipeline ready")

    # ------------------------------------------- trajectory helpers from v1
    def _frame_count_from_action_string(self, action_string: str) -> int:
        if self.dry_run:
            return super()._frame_count_from_action_string(action_string)
        total = self._trajectory_module().infer_frame_num_from_action_string(action_string)
        return self._snap_frame_count(total)

    def _write_control_files(self, output_dir: Path, idx: int, action_dsl: str, frame_num: int):
        import numpy as np

        mod = self._trajectory_module()
        control_dir = output_dir / f"control_{idx:04d}"
        control_dir.mkdir(parents=True, exist_ok=True)

        np.save(control_dir / "intrinsics.npy", self._intrinsics_for(frame_num))
        wasd, ijkl, total = mod.action_string_to_wasd_ijkl(action_dsl)
        if total > frame_num:
            raise ValueError(f"action string expands to {total} frames, but target frame_num is {frame_num}")
        if total < frame_num:
            pad = ((0, frame_num - total), (0, 0))
            wasd = np.pad(wasd, pad, mode="constant")
            ijkl = np.pad(ijkl, pad, mode="constant")

        frame_keys = mod.wasd_array_to_frame_keys(wasd, ijkl)
        c2ws = np.asarray(mod.generate_and_save_trajectory(frame_keys), dtype=np.float32)
        np.save(control_dir / "poses.npy", c2ws)
        np.save(control_dir / "wasd_action.npy", wasd.astype(np.float32))
        np.save(control_dir / "ijkl_action.npy", ijkl.astype(np.float32))
        return control_dir
