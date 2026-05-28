import pygame
from pathlib import Path

ASSET_EXTS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']

def find_asset(name: str, assets_dir: str = "assets") -> Path | None:
    p = Path(assets_dir) / name
    if p.exists():
        return p
    for ext in ASSET_EXTS:
        p2 = Path(assets_dir) / (name + ext)
        if p2.exists():
            return p2
    return None

def load_and_crop(name: str, size: tuple, assets_dir: str = "assets") -> pygame.Surface:
    tw, th = size
    path = find_asset(name, assets_dir)
    if path is None:
        surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        surf.fill((200, 50, 200))  # magenta placeholder
        return surf

    img = pygame.image.load(str(path)).convert_alpha()
    iw, ih = img.get_size()
    if iw == 0 or ih == 0:
        surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        surf.fill((200, 50, 200))
        return surf

    scale = max(tw / iw, th / ih)
    new_w, new_h = max(1, int(iw * scale)), max(1, int(ih * scale))
    img = pygame.transform.smoothscale(img, (new_w, new_h))

    x = (new_w - tw) // 2
    y = (new_h - th) // 2
    target = pygame.Surface((tw, th), pygame.SRCALPHA)
    target.blit(img, (-x, -y))
    return target

def load_tile(name: str, tile_size: int, assets_dir: str = "assets") -> pygame.Surface:
    return load_and_crop(name, (tile_size, tile_size), assets_dir)