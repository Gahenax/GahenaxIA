"""
Atlas kNN Frontier Builder
--------------------------
Verbatim port from github.com/Gahenax/P-ATLAS-NP/src/atlas.py
Identifies the frontier region: points with high local std(H) among kNN
in the compressed feature space. The frontier is where the Governor's UA cost
is most unpredictable — the P≈NP boundary for Gahenax inference.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List


def _euclidean_sq(a: List[float], b: List[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def knn_indices(vmat: List[List[float]], k: int) -> List[List[int]]:
    """k-NN by Euclidean distance, O(N²). Sufficient for N < 10k."""
    n = len(vmat)
    out: List[List[int]] = []
    for i in range(n):
        dists = [(j, _euclidean_sq(vmat[i], vmat[j])) for j in range(n) if j != i]
        dists.sort(key=lambda x: x[1])
        out.append([j for j, _ in dists[:k]])
    return out


def _zscore_normalize(vmat: List[List[float]]) -> List[List[float]]:
    if not vmat:
        return vmat
    dims = len(vmat[0])
    n = len(vmat)
    means = [sum(row[d] for row in vmat) / n for d in range(dims)]
    stds = [
        (sum((row[d] - means[d]) ** 2 for row in vmat) / n) ** 0.5 + 1e-8
        for d in range(dims)
    ]
    return [[(row[d] - means[d]) / stds[d] for d in range(dims)] for row in vmat]


def _std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = sum(values) / len(values)
    return (sum((v - mu) ** 2 for v in values) / len(values)) ** 0.5


def build_frontier_knn(
    records: List[Dict[str, float]],
    coords: List[str],
    k: int = 5,
    quantile: float = 0.8,
) -> Dict[str, Any]:
    """
    frontier = points with high std(target_H) among their kNN in feature space.

    Args:
        records:  list of dicts, each must contain coords + 'target_H'
        coords:   feature dimension names (subset of record keys)
        k:        neighbourhood size
        quantile: frontier threshold (top (1-q)*100% of local_std)

    Returns:
        dict with frontier metadata + per-point local_std and frontier_mask
    """
    n = len(records)
    if n < k + 1:
        return {
            "k": k, "quantile": quantile,
            "threshold": 0.0, "frontier_fraction": 0.0, "frontier_width": 0.0,
            "law_of_frontier": "insufficient data",
            "local_std_summary": {"min": 0.0, "median": 0.0, "max": 0.0},
            "frontier_mask": [False] * n,
            "local_std": [0.0] * n,
        }

    vmat_raw = [[float(r.get(c, 0.0)) if isinstance(r.get(c), (int, float)) else 0.0
                 for c in coords] for r in records]
    vmat_z = _zscore_normalize(vmat_raw)
    H = [float(r.get("target_H", 0.0)) for r in records]

    neighbours = knn_indices(vmat_z, k=k)
    local_std = [_std([H[j] for j in ns]) if ns else 0.0 for ns in neighbours]

    sorted_ls = sorted(local_std)
    thr_idx = int(math.floor(quantile * n))
    thr_idx = min(thr_idx, n - 1)
    thr = sorted_ls[thr_idx]

    frontier_mask = [ls >= thr for ls in local_std]
    frontier_vals = [ls for ls, fm in zip(local_std, frontier_mask) if fm]
    frontier_width = _std(frontier_vals) if len(frontier_vals) > 1 else 0.0
    frontier_frac = sum(frontier_mask) / n

    mid = sorted_ls[n // 2]

    return {
        "k": k,
        "quantile": quantile,
        "threshold": round(thr, 6),
        "frontier_fraction": round(frontier_frac, 6),
        "frontier_width": round(frontier_width, 6),
        "law_of_frontier": (
            f"Frontier = top {int((1 - quantile) * 100)}% "
            f"local-std(H) in kNN(v), width≈{frontier_width:.4f}"
        ),
        "local_std_summary": {
            "min": round(sorted_ls[0], 6),
            "median": round(mid, 6),
            "max": round(sorted_ls[-1], 6),
        },
        "frontier_mask": frontier_mask,
        "local_std": local_std,
    }


def lookup_frontier_score(
    query_vec: List[float],
    atlas_vmat_z: List[List[float]],
    local_std: List[float],
    k: int = 5,
) -> float:
    """
    Given a new query vector (already z-scored), estimate its local_std(H)
    by averaging the local_std of its k nearest atlas neighbours.
    Returns a score in [0, max(local_std)].
    """
    if not atlas_vmat_z or not local_std:
        return 0.0
    dists = [(i, _euclidean_sq(query_vec, v)) for i, v in enumerate(atlas_vmat_z)]
    dists.sort(key=lambda x: x[1])
    neighbours = [i for i, _ in dists[:k]]
    return sum(local_std[i] for i in neighbours) / max(len(neighbours), 1)
