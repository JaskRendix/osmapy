import json
import multiprocessing
import random
import time
from io import BytesIO
from pathlib import Path
from queue import LifoQueue
from string import Template
from threading import Thread

import numpy as np
import requests
from PIL import Image
from PySide6.QtGui import QPixmap

from osmapy.TileLoader.Tile import Tile
from osmapy.utils.config import load_config

config = load_config()


class TileLoader:
    """Load slippy tiles in a LIFO queue with worker threads and a JSON-backed cache."""

    def __init__(self, viewer, config_id):
        self.name = config.slippy_tiles[config_id].name
        self.urls = config.slippy_tiles[config_id].urls

        self.path_cache = Path(__file__).parent / Path(f"../../cache/{self.name}")
        self.viewer = viewer

        self.cache_json = self.load_cache_json()

        self.queue = LifoQueue()
        self.lock = multiprocessing.Lock()

        num_workers = min(2, multiprocessing.cpu_count())
        for _ in range(num_workers):
            Thread(target=self.worker, daemon=True).start()

    def _build_request_url(self, tile: Tile) -> str:
        osm_tile_url = random.choice(self.urls)
        template = Template(osm_tile_url)
        return template.substitute(
            zoom=tile.zoom,
            int_xtile=tile.int_xtile,
            int_ytile=tile.int_ytile,
        )

    def _fetch_tile_image(self, tile: Tile) -> Image.Image:
        url = self._build_request_url(tile)
        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"Tile server returned {response.status_code} for {url}")

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            raise ValueError(
                f"Tile server returned non-image content ({content_type}) for {url}"
            )

        try:
            img = Image.open(BytesIO(response.content))
            img.verify()
            img = Image.open(BytesIO(response.content))
        except Exception as exc:
            raise ValueError(
                f"Tile server returned invalid image data for {url}"
            ) from exc

        return img

    def worker(self):
        """Download tiles, update cache, save images, and trigger viewer updates."""
        while True:
            tile = self.queue.get()
            try:
                image = self._fetch_tile_image(tile)

                with self.lock:
                    self.path_cache.mkdir(parents=True, exist_ok=True)
                    image.save(self.path_cache / f"{tile.name}.png")
                    expire_time = 60 * 60 * 24 * 7  # 7 days
                    self.cache_json.setdefault(tile.name, {})
                    self.cache_json[tile.name]["time"] = time.time() + expire_time
                    self.cache_json[tile.name]["state"] = "loaded"
                    self.viewer.update()

            except Exception as e:
                print("TileLoader error:", e)
                with self.lock:
                    self.path_cache.mkdir(parents=True, exist_ok=True)
                    self.cache_json[tile.name] = {
                        "state": "error",
                        "time": time.time() + 60,  # retry in 60 seconds
                    }
                    fallback = Image.open(self.viewer.asset_error_image)
                    fallback.save(self.path_cache / f"{tile.name}.png")

            finally:
                self.queue.task_done()

    def get_tile(self, tile: Tile):
        """Request a tile to be loaded and return its cache path, or None if it cannot exist."""
        if not tile.check_existance():
            return None

        now = time.time()
        name = tile.name

        with self.lock:
            entry = self.cache_json.get(name)

            if entry is None:
                self.cache_json[name] = {"state": "loading", "time": now}
                self.queue.put(tile)
            else:
                state = entry.get("state")
                ts = entry.get("time", 0.0)

                if state == "loading" and ts + config.retry_time_tile < now:
                    self.cache_json[name]["time"] = now
                    self.queue.put(tile)

                if state == "loaded" and ts < now:
                    self.cache_json[name] = {"state": "loading", "time": now}
                    self.queue.put(tile)

                if state == "error" and ts < now:
                    self.cache_json[name] = {"state": "loading", "time": now}
                    self.queue.put(tile)

        return str(self.path_cache / f"{name}.png")

    def load_cache_json(self):
        path = self.path_cache / "database.json"
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as json_file:
                json.dump({}, json_file)
        with open(path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def save_cache_json(self):
        path = self.path_cache / "database.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(self.cache_json, json_file)

    def close(self):
        with self.lock:
            self.save_cache_json()

    def draw(self, viewer, qpainter, alpha):
        qpainter.setOpacity(alpha)
        main_tile = Tile(viewer.lat, viewer.lon, viewer.zoom)
        offset_x = int((viewer.x - main_tile.center_x) * viewer.scale_x)
        offset_y = int((viewer.y - main_tile.center_y) * viewer.scale_y)

        num_x = int(
            np.ceil(
                int(np.ceil(viewer.frameGeometry().width() / config.image_size) + 1) / 2
            )
        )
        num_y = int(
            np.ceil(
                int(np.ceil(viewer.frameGeometry().height() / config.image_size) + 1)
                / 2
            )
        )

        for a in range(-num_x, num_x + 1):
            for b in range(-num_y, num_y + 1):
                tile = Tile.from_num(
                    main_tile.xtile + a, main_tile.ytile + b, main_tile.zoom
                )
                if not tile.check_existance():
                    continue

                path_image = self.get_tile(tile)
                if path_image is None:
                    pic = QPixmap(viewer.asset_error_image)
                else:
                    pic = QPixmap(str(path_image))
                    if pic.isNull():
                        pic = QPixmap(viewer.asset_error_image)

                pic = pic.scaled(config.image_size, config.image_size)
                qpainter.drawTiledPixmap(
                    -offset_x
                    + a * config.image_size
                    + viewer.frameGeometry().width() * 0.5
                    - config.image_size * 0.5,
                    offset_y
                    + b * config.image_size
                    + viewer.frameGeometry().height() * 0.5
                    - config.image_size * 0.5,
                    config.image_size,
                    config.image_size,
                    pic,
                )
