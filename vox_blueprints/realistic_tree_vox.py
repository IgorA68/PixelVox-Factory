DEFAULT_W = 96
DEFAULT_D = 96
DEFAULT_H = 128
BLUEPRINT_DISPLAY_NAME = 'Realistic Tree'
BLUEPRINT_DESCRIPTION = 'An expressive showcase tree with a layered canopy, visible branch structure, and asymmetric silhouette.'

import math
import random

from vox_art import engine as ev


BARK_DARK = 174
BARK_MID = 131
BARK_LIGHT = 88
LEAF_DARK = 167
LEAF_MID = 124
LEAF_LIGHT = 81
LEAF_CLUSTER_SEED = 42
LEAF_CLUSTER_COUNT = 18
BRANCH_SPECS = (
    (-0.05, 0.33, 0.19, 0.055, 0.21, 0.15, 0.12, 0.0),
    (0.62, 0.28, 0.10, 0.045, 0.16, 0.11, 0.10, 0.7),
    (1.85, 0.24, 0.08, 0.043, 0.15, 0.11, 0.09, 1.5),
    (2.85, 0.18, 0.13, 0.040, 0.14, 0.10, 0.09, 2.2),
    (3.7, 0.23, 0.17, 0.041, 0.15, 0.10, 0.10, 2.9),
    (5.1, 0.2, 0.2, 0.039, 0.13, 0.09, 0.08, 3.5),
)
HERO_LOBE_SPECS = (
    (0.07, 0.18, 0.72, 0.19, 0.15, 0.12, 0.2),
    (-0.18, -0.02, 0.67, 0.2, 0.16, 0.11, 1.1),
    (0.2, -0.16, 0.62, 0.17, 0.14, 0.1, 2.1),
)
DRAPE_SPECS = (
    (0.02, 0.05, 0.58, 0.1, 0.08, 0.09, 0.4),
    (0.16, -0.03, 0.56, 0.09, 0.07, 0.08, 1.3),
    (-0.08, -0.08, 0.54, 0.08, 0.07, 0.08, 2.2),
)
LEAF_CLUSTER_CACHE = {}


def _build_leaf_cluster_specs(seed=LEAF_CLUSTER_SEED, count=LEAF_CLUSTER_COUNT):
    rng = random.Random(seed)
    specs = []

    for _ in range(count):
        angle = rng.uniform(0.0, math.tau)
        spread = rng.uniform(0.04, 0.18)
        rise = rng.uniform(-0.08, 0.12)
        radius_x = rng.uniform(0.05, 0.09)
        radius_y = rng.uniform(0.05, 0.09)
        radius_z = rng.uniform(0.04, 0.08)
        phase = rng.uniform(0.0, math.tau)
        specs.append((angle, spread, rise, radius_x, radius_y, radius_z, phase))

    return tuple(specs)


def _get_leaf_cluster_specs(seed=None):
    resolved_seed = LEAF_CLUSTER_SEED if seed is None else seed
    if resolved_seed not in LEAF_CLUSTER_CACHE:
        LEAF_CLUSTER_CACHE[resolved_seed] = _build_leaf_cluster_specs(resolved_seed)
    return LEAF_CLUSTER_CACHE[resolved_seed]


LEAF_CLUSTER_SPECS = _build_leaf_cluster_specs()


def _trunk_center(cx, cy, z, width):
    sway_primary = math.sin(z * 0.08) * max(1.0, width * 0.02)
    sway_secondary = math.sin(z * 0.17) * max(0.5, width * 0.01)
    side_bend = math.cos(z * 0.06) * max(0.5, width * 0.012)
    return cx + sway_primary + sway_secondary, cy + side_bend


def _trunk_color(x, y, z):
    bark_noise = math.sin(z * 0.34 + x * 0.12) + math.cos(y * 0.16)
    if bark_noise > 0.8:
        return BARK_LIGHT
    if bark_noise < -0.5:
        return BARK_DARK
    return BARK_MID


def _leaf_color(x, y, z, phase):
    leaf_noise = math.sin(x * 0.22 + phase) + math.cos(y * 0.18 - phase) + math.sin(z * 0.12)
    if leaf_noise > 1.0:
        return LEAF_LIGHT
    if leaf_noise < -0.2:
        return LEAF_DARK
    return LEAF_MID


def _inside_crown_layer(x, y, z, center_x, center_y, center_z, radius_x, radius_y, radius_z):
    if radius_x <= 0 or radius_y <= 0 or radius_z <= 0:
        return False

    dx = (x - center_x) / radius_x
    dy = (y - center_y) / radius_y
    dz = (z - center_z) / radius_z
    return dx * dx + dy * dy + dz * dz <= 1.0


def _ellipsoid_edge_factor(x, y, z, center_x, center_y, center_z, radius_x, radius_y, radius_z):
    if radius_x <= 0 or radius_y <= 0 or radius_z <= 0:
        return -1.0

    dx = (x - center_x) / radius_x
    dy = (y - center_y) / radius_y
    dz = (z - center_z) / radius_z
    return 1.0 - (dx * dx + dy * dy + dz * dz)


def _distance_to_segment(px, py, pz, ax, ay, az, bx, by, bz):
    abx = bx - ax
    aby = by - ay
    abz = bz - az
    apx = px - ax
    apy = py - ay
    apz = pz - az
    ab_len_sq = abx * abx + aby * aby + abz * abz

    if ab_len_sq == 0:
        return math.sqrt(apx * apx + apy * apy + apz * apz), 0.0

    t = (apx * abx + apy * aby + apz * abz) / ab_len_sq
    t = max(0.0, min(1.0, t))
    closest_x = ax + abx * t
    closest_y = ay + aby * t
    closest_z = az + abz * t
    dx = px - closest_x
    dy = py - closest_y
    dz = pz - closest_z
    return math.sqrt(dx * dx + dy * dy + dz * dz), t


def _leaf_mass_color(x, y, z, phase, edge_factor):
    breakup = (
        math.sin(x * 0.24 + phase)
        + math.cos(y * 0.19 - phase)
        + math.sin(z * 0.16 + phase * 0.6)
    )
    if edge_factor < 0.16 and breakup < 0.3:
        return 0
    if edge_factor < 0.09 and breakup < 1.0:
        return 0
    return _leaf_color(x, y, z, phase)


def make_model(x, y, z, W, D, H, seed=None):
    cx, cy = W / 2.0, D / 2.0
    leaf_cluster_specs = _get_leaf_cluster_specs(seed)
    trunk_top = H * 0.78
    trunk_cx, trunk_cy = _trunk_center(cx, cy, z, W)

    trunk_progress = min(1.0, z / trunk_top) if trunk_top else 1.0
    trunk_radius = max(2.0, W * 0.11 * (1.0 - trunk_progress) + W * 0.03)
    root_flare = max(0.0, (H * 0.12 - z) * 0.06)
    dist_trunk = math.hypot(x - trunk_cx, y - trunk_cy)

    if z <= trunk_top and dist_trunk <= trunk_radius + root_flare:
        return _trunk_color(x, y, z)

    if z < H * 0.44:
        return 0

    canopy_origin_x, canopy_origin_y = _trunk_center(cx, cy, H * 0.64, W)
    top_anchor_x, top_anchor_y = _trunk_center(cx, cy, H * 0.77, W)
    top_anchor_x += W * 0.03
    top_anchor_y -= D * 0.015
    top_phase = 0.35
    branch_base_z = H * 0.58
    branch_base_x, branch_base_y = _trunk_center(cx, cy, branch_base_z, W)

    if _inside_crown_layer(x, y, z, top_anchor_x, top_anchor_y, H * 0.83, W * 0.12, D * 0.12, H * 0.09):
        edge_factor = _ellipsoid_edge_factor(x, y, z, top_anchor_x, top_anchor_y, H * 0.83, W * 0.12, D * 0.12, H * 0.09)
        color = _leaf_mass_color(x, y, z, top_phase, edge_factor)
        if color:
            return color

    for offset_x, offset_y, center_z_factor, radius_x, radius_y, radius_z, phase in HERO_LOBE_SPECS:
        lobe_x = canopy_origin_x + W * offset_x
        lobe_y = canopy_origin_y + D * offset_y
        lobe_z = H * center_z_factor
        radius_w = W * radius_x
        radius_d = D * radius_y
        radius_h = H * radius_z
        if not _inside_crown_layer(x, y, z, lobe_x, lobe_y, lobe_z, radius_w, radius_d, radius_h):
            continue

        edge_factor = _ellipsoid_edge_factor(x, y, z, lobe_x, lobe_y, lobe_z, radius_w, radius_d, radius_h)
        color = _leaf_mass_color(x, y, z, phase, edge_factor)
        if color:
            return color

    for angle, length, rise, thickness, leaf_rx, leaf_ry, leaf_rz, phase in BRANCH_SPECS:
        tip_x = canopy_origin_x + math.cos(angle) * W * length
        tip_y = canopy_origin_y + math.sin(angle) * D * length
        tip_z = H * (0.63 + rise)

        branch_dist, branch_t = _distance_to_segment(
            x, y, z,
            branch_base_x, branch_base_y, branch_base_z,
            tip_x, tip_y, tip_z,
        )
        branch_radius = max(1.2, W * thickness * (1.0 - branch_t * 0.7))
        if branch_dist <= branch_radius:
            return _trunk_color(x, y, z)

        primary_hit = _inside_crown_layer(
            x, y, z,
            tip_x,
            tip_y,
            tip_z,
            W * leaf_rx,
            D * leaf_ry,
            H * leaf_rz,
        )
        secondary_hit = _inside_crown_layer(
            x, y, z,
            (tip_x + branch_base_x) / 2.0,
            (tip_y + branch_base_y) / 2.0,
            tip_z - H * 0.03,
            W * (leaf_rx * 0.95),
            D * (leaf_ry * 0.9),
            H * (leaf_rz * 0.82),
        )

        if primary_hit or secondary_hit:
            if primary_hit:
                edge_factor = _ellipsoid_edge_factor(x, y, z, tip_x, tip_y, tip_z, W * leaf_rx, D * leaf_ry, H * leaf_rz)
            else:
                edge_factor = 0.45

            color = _leaf_mass_color(x, y, z, phase, edge_factor)
            if color:
                return color

            if math.cos(angle) > 0.4:
                for drop_x, drop_y, drop_z, drop_rx, drop_ry, drop_rz, drop_phase in DRAPE_SPECS:
                    curtain_x = tip_x + W * drop_x
                    curtain_y = tip_y + D * drop_y
                    curtain_z = H * drop_z
                    radius_w = W * drop_rx
                    radius_d = D * drop_ry
                    radius_h = H * drop_rz
                    if not _inside_crown_layer(x, y, z, curtain_x, curtain_y, curtain_z, radius_w, radius_d, radius_h):
                        continue

                    edge_factor = _ellipsoid_edge_factor(x, y, z, curtain_x, curtain_y, curtain_z, radius_w, radius_d, radius_h)
                    color = _leaf_mass_color(x, y, z, drop_phase + phase, edge_factor)
                    if color:
                        return color

            for cluster_angle, spread, rise_offset, radius_x, radius_y, radius_z, cluster_phase in leaf_cluster_specs:
                local_x = tip_x + math.cos(cluster_angle + phase) * W * spread
                local_y = tip_y + math.sin(cluster_angle + phase) * D * spread
                local_z = tip_z + H * rise_offset
                if not _inside_crown_layer(
                    x, y, z,
                    local_x,
                    local_y,
                    local_z,
                    W * radius_x,
                    D * radius_y,
                    H * radius_z,
                ):
                    continue

                fringe_edge = _ellipsoid_edge_factor(x, y, z, local_x, local_y, local_z, W * radius_x, D * radius_y, H * radius_z)
                color = _leaf_mass_color(x, y, z, cluster_phase, fringe_edge)
                if color:
                    return color

    return 0


high_res_tree = make_model


if __name__ == "__main__":
    print('Generating showcase tree...')
    ev.save_as_vox("realistic_tree_vox", DEFAULT_W, DEFAULT_D, DEFAULT_H, make_model)
    print('Done!')