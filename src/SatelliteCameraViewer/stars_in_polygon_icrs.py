"""
stars_in_polygon_icrs - Spherical point-in-polygon test.
"""

from multiprocessing import Pool
import numpy as np

def stars_in_polygon_icrs(stars_vec, poly_vec, multiprocessing_method=False):
    """
    stars_in_polygon_icrs() - Spherical point-in-polygon test.
    """
    if multiprocessing_method:
        # multiprocesssing
        inside_mask = _stars_in_polygon_icrs_multiprocesssing(stars_vec, poly_vec)
    else:
        # single thread
        inside_mask = _stars_in_polygon_icrs_fast(stars_vec, poly_vec)
    return inside_mask

#
# Fork isn't considered safe in modern Python and hence we know that spawn is used.
# Hence the arg creation for this function.
# On a Python spawn only the _worker() function is imported and run, plus the imports above - so keep them simple!
#
# HOWEVER: The multiprocessing version runs way slower than the non-multiprocessing version because of overhead.
#
def _worker(args):
    """ _worker """
    stars_vec_chunk, poly_vec = args
    return _stars_in_polygon_icrs_fast(stars_vec_chunk, poly_vec)

def _stars_in_polygon_icrs_multiprocesssing(stars_vec, poly_vec, n_proc=4):
    """ _stars_in_polygon_icrs_multiprocessing """
    stars_vec_chunk = np.array_split(stars_vec, n_proc)
    args = [(chunk, poly_vec) for chunk in stars_vec_chunk]
    with Pool() as p:
        results = p.map(_worker, args)
    inside_mask = np.concatenate(results)
    return inside_mask

#
# fast version fully using numpy methodology (needs stars and poly in specific numpy format)
#
def _stars_in_polygon_icrs_fast(stars_vec, poly_vecs):
    """ _stars_in_polygon_icrs_fast """

    # Close polygon
    poly_vecs = np.vstack([poly_vecs, poly_vecs[0]])

    # Build edges
    A = poly_vecs[:-1]          # shape (M, 3)
    B = poly_vecs[1:]           # shape (M, 3)

    # For each star, compute vectors to each polygon vertex
    # stars_vec[:,None,:] -> shape (N,1,3)
    # A[None,:,:]         -> shape (1,M,3)
    VA = A[None,:,:] - stars_vec[:,None,:]   # shape (N,M,3)
    VB = B[None,:,:] - stars_vec[:,None,:]

    # Normalize
    VA /= np.linalg.norm(VA, axis=2, keepdims=True)
    VB /= np.linalg.norm(VB, axis=2, keepdims=True)

    # Dot products -> angles
    dots = np.sum(VA * VB, axis=2)
    dots = np.clip(dots, -1.0, 1.0)
    angles = np.arccos(dots)                 # shape (N,M)

    # Signed angle using triple product
    cross_ab = np.cross(A, B)                # shape (M,3)
    signs = np.sign(np.dot(stars_vec, cross_ab.T))  # shape (N,M)

    total = np.sum(signs * angles, axis=1)

    return np.abs(total) > np.pi
