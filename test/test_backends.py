import paysage.backends.python_backend.matrix as py_matrix
import paysage.backends.python_backend.nonlinearity as py_func
import paysage.backends.python_backend.rand as py_rand

import paysage.backends.pytorch_backend.matrix as torch_matrix
import paysage.backends.pytorch_backend.nonlinearity as torch_func
import paysage.backends.pytorch_backend.rand as torch_rand

from numpy import allclose
import pytest

# ---- testing utility functions ----- #

def assert_close(pymat, torchmat, name, rtol=1e-05, atol=1e-08):

    pytorchmat = torch_matrix.to_numpy_array(torchmat)
    torchpymat = torch_matrix.float_tensor(pymat)

    py_vs_torch = py_matrix.allclose(pymat, pytorchmat, rtol=rtol, atol=atol)
    torch_vs_py = torch_matrix.allclose(torchmat, torchpymat, rtol=rtol, atol=atol)

    if py_vs_torch and torch_vs_py:
        return
    if py_vs_torch and not torch_vs_py:
        assert False,\
        "{}: failure at torch allclose".format(name)
    elif not py_vs_torch and torch_vs_py:
        assert False, \
        "{}: failure at python allclose".format(name)
    else:
        assert False, \
        "{}: failure at both python and torch allclose".format(name)


# ----- Tests ------ #


def test_conversion():

    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)
    py_torch_x = torch_matrix.to_numpy_array(torch_x)

    assert py_matrix.allclose(py_x, py_torch_x), \
    "python -> torch -> python failure"

    torch_rand.set_seed()
    torch_y = torch_rand.rand(shape)
    py_y = torch_matrix.to_numpy_array(torch_y)
    torch_py_y = torch_matrix.float_tensor(py_y)

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure"

def test_transpose():

    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_x_T = py_matrix.transpose(py_x)
    py_torch_x_T = torch_matrix.to_numpy_array(torch_matrix.transpose(torch_x))

    assert py_matrix.allclose(py_x_T, py_torch_x_T), \
    "python -> torch -> python failure: transpose"

    torch_rand.set_seed()
    torch_y = torch_rand.rand(shape)
    py_y = torch_matrix.to_numpy_array(torch_y)

    torch_y_T = torch_matrix.transpose(torch_y)
    torch_py_y_T = torch_matrix.float_tensor(py_matrix.transpose(py_y))

    assert torch_matrix.allclose(torch_y_T, torch_py_y_T), \
    "torch -> python -> torch failure: transpose"

def test_zeros():
    shape = (100, 100)

    py_zeros = py_matrix.zeros(shape)
    torch_zeros = torch_matrix.zeros(shape)
    assert_close(py_zeros, torch_zeros, "zeros")

def test_ones():
    shape = (100, 100)

    py_ones = py_matrix.ones(shape)
    torch_ones = torch_matrix.ones(shape)
    assert_close(py_ones, torch_ones, "ones")

def test_diag():
    shape = (100,)

    py_rand.set_seed()
    py_vec = py_rand.randn(shape)
    py_mat = py_matrix.diagonal_matrix(py_vec)
    py_diag = py_matrix.diag(py_mat)

    assert py_matrix.allclose(py_vec, py_diag), \
    "python vec -> matrix -> vec failure: diag"

    torch_vec = torch_rand.randn(shape)
    torch_mat = torch_matrix.diagonal_matrix(torch_vec)
    torch_diag = torch_matrix.diag(torch_mat)

    assert torch_matrix.allclose(torch_vec, torch_diag), \
    "torch vec -> matrix -> vec failure: diag"

def test_fill_diagonal():

    n = 10

    py_mat = py_matrix.identity(n)
    torch_mat = torch_matrix.identity(n)

    fill_value = 2.0

    py_mult = fill_value * py_mat
    py_matrix.fill_diagonal(py_mat, fill_value)

    assert py_matrix.allclose(py_mat, py_mult), \
    "python fill != python multiplly for diagonal matrix"

    torch_mult = fill_value * torch_mat
    torch_matrix.fill_diagonal(torch_mat, fill_value)

    assert torch_matrix.allclose(torch_mat, torch_mult), \
    "torch fill != python multiplly for diagonal matrix"

    assert_close(py_mat, torch_mat, "fill_diagonal")

def test_sign():

    shape = (100,100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_sign = py_matrix.sign(py_mat)
    torch_sign = torch_matrix.sign(torch_mat)
    assert_close(py_sign, torch_sign, "sign")

def test_clip():

    shape = (100,100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # test two sided clip
    py_clipped = py_matrix.clip(py_mat, a_min=0, a_max=1)
    torch_clipped = torch_matrix.clip(torch_mat, a_min=0, a_max=1)
    assert_close(py_clipped, torch_clipped, "clip (two-sided)")

    # test lower clip
    py_clipped = py_matrix.clip(py_mat, a_min=0)
    torch_clipped = torch_matrix.clip(torch_mat, a_min=0)
    assert_close(py_clipped, torch_clipped, "clip (lower)")

    # test upper clip
    py_clipped = py_matrix.clip(py_mat, a_max=1)
    torch_clipped = torch_matrix.clip(torch_mat, a_max=1)
    assert_close(py_clipped, torch_clipped, "clip (upper)")

def test_clip_inplace():

    shape = (100,100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # test two sided clip
    py_matrix.clip_inplace(py_mat, a_min=0, a_max=1)
    torch_matrix.clip_inplace(torch_mat, a_min=0, a_max=1)

    assert_close(py_mat, torch_mat, "clip_inplace (two-sided)")

    # test lower clip
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_matrix.clip_inplace(py_mat, a_min=0)
    torch_matrix.clip_inplace(torch_mat, a_min=0)

    assert_close(py_mat, torch_mat, "clip_inplace (lower)")

    # test upper clip
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_matrix.clip_inplace(py_mat, a_max=1)
    torch_matrix.clip_inplace(torch_mat, a_max=1)

    assert_close(py_mat, torch_mat, "clip_inplace (upper)")

def test_tround():

    shape = (100,100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_round = py_matrix.tround(py_mat)
    torch_round = torch_matrix.tround(torch_mat)

    assert_close(py_round, torch_round, "tround")

def test_flatten():
    # flatten a scalar
    # in contrast to numpy (which returns a 1 element array)
    # the backend flatten functions do nothing to scalars
    scalar = 5.7
    py_scalar = py_matrix.flatten(scalar)
    torch_scalar = torch_matrix.flatten(scalar)

    assert py_scalar == torch_scalar, \
    "error applying flatten to a scalar"

    # flatten a tensor
    shape = (100,100)
    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_flatten = py_matrix.flatten(py_mat)
    torch_flatten = torch_matrix.flatten(torch_mat)

    assert_close(py_flatten, torch_flatten, "flatten")

def test_reshape():
    shape = (100,100)
    newshape = (5, 2000)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_new = py_matrix.reshape(py_mat, newshape)
    torch_new = torch_matrix.reshape(torch_mat, newshape)

    assert_close(py_new, torch_new, "reshape")

def test_mix_inplace():
    shape = (100,100)
    torch_w = 0.1
    py_w = py_matrix.float_scalar(torch_w)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_matrix.mix_inplace(py_w, py_x, py_y)
    torch_matrix.mix_inplace(torch_w, torch_x, torch_y)

    assert_close(py_x, torch_x, "mix_inplace")

def test_square_mix_inplace():
    shape = (100,100)
    torch_w = 0.1
    py_w = py_matrix.float_scalar(torch_w)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_matrix.square_mix_inplace(py_w, py_x, py_y)
    torch_matrix.square_mix_inplace(torch_w, torch_x, torch_y)

    assert_close(py_x, torch_x, "square_mix_inplace")

def test_sqrt_div():
    shape = (100,100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape) ** 2

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_sqrt_div = py_matrix.sqrt_div(py_x, py_y)
    torch_sqrt_div = torch_matrix.sqrt_div(torch_x, torch_y)

    assert_close(py_sqrt_div, torch_sqrt_div, "sqrt_div")

def test_normalize():
    shape = (100,)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)

    torch_x = torch_matrix.float_tensor(py_x)

    py_norm = py_matrix.normalize(py_x)
    torch_norm = torch_matrix.normalize(torch_x)

    assert_close(py_norm, torch_norm, "normalize")

def test_norm():
    shape = (100,)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_norm = py_matrix.norm(py_x)
    torch_norm = torch_matrix.norm(torch_x)

    assert allclose(py_norm, torch_norm), \
    "python l2 norm != torch l2 norm"

def test_tmax():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall max
    py_max = py_matrix.tmax(py_mat)
    torch_max = torch_matrix.tmax(torch_mat)

    assert allclose(py_max, torch_max), \
    "python overal max != torch overall max"

    # max over axis 0
    py_max = py_matrix.tmax(py_mat, axis=0)
    torch_max = torch_matrix.tmax(torch_mat, axis=0)
    assert_close(py_max, torch_max, "tmax (axis-0)")

    # max over axis 1
    py_max = py_matrix.tmax(py_mat, axis=1)
    torch_max = torch_matrix.tmax(torch_mat, axis=1)
    assert_close(py_max, torch_max, "tmax (axis-1)")

    # max over axis 0, keepdims = True
    py_max = py_matrix.tmax(py_mat, axis=0, keepdims=True)
    torch_max = torch_matrix.tmax(torch_mat, axis=0)
    assert_close(py_max, torch_max, "tmax (axis-0, keepdims)")

    # max over axis 1, keepdims = True
    py_max = py_matrix.tmax(py_mat, axis=1, keepdims=True)
    torch_max = torch_matrix.tmax(torch_mat, axis=1, keepdims=True)
    assert_close(py_max, torch_max, "tmax (axis-1, keepdims)")

def test_tmin():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall min
    py_min = py_matrix.tmin(py_mat)
    torch_min = torch_matrix.tmin(torch_mat)

    assert allclose(py_min, torch_min), \
    "python overal min != torch overall min"

    # min over axis 0
    py_min = py_matrix.tmin(py_mat, axis=0)
    torch_min = torch_matrix.tmin(torch_mat, axis=0)
    assert_close(py_min, torch_min, "tmin (axis-0)")

    # min over axis 1
    py_min = py_matrix.tmin(py_mat, axis=1)
    torch_min = torch_matrix.tmin(torch_mat, axis=1)
    assert_close(py_min, torch_min, "tmin (axis-1)")

    # min over axis 0, keepdims = True
    py_min = py_matrix.tmin(py_mat, axis=0, keepdims=True)
    torch_min = torch_matrix.tmin(torch_mat, axis=0)
    assert_close(py_min, torch_min, "tmin (axis-0, keepdims)")

    # min over axis 1, keepdims = True
    py_min = py_matrix.tmin(py_mat, axis=1, keepdims=True)
    torch_min = torch_matrix.tmin(torch_mat, axis=1, keepdims=True)
    assert_close(py_min, torch_min, "tmin (axis-1, keepdims)")

def test_mean():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall mean
    py_mean = py_matrix.mean(py_mat)
    torch_mean = torch_matrix.mean(torch_mat)

    assert allclose(py_mean, torch_mean), \
    "python overal mean != torch overall mean"

    # mean over axis 0
    py_mean = py_matrix.mean(py_mat, axis=0)
    torch_mean = torch_matrix.mean(torch_mat, axis=0)
    assert_close(py_mean, torch_mean, "mean (axis-0)")

    # mean over axis 1
    py_mean = py_matrix.mean(py_mat, axis=1)
    torch_mean = torch_matrix.mean(torch_mat, axis=1)
    assert_close(py_mean, torch_mean, "mean (axis-1)")

    # mean over axis 0, keepdims = True
    py_mean = py_matrix.mean(py_mat, axis=0, keepdims=True)
    torch_mean = torch_matrix.mean(torch_mat, axis=0)
    assert_close(py_mean, torch_mean, "mean (axis-0, keepdims)")

    # mean over axis 1, keepdims = True
    py_mean = py_matrix.mean(py_mat, axis=1, keepdims=True)
    torch_mean = torch_matrix.mean(torch_mat, axis=1, keepdims=True)
    assert_close(py_mean, torch_mean, "mean (axis-1, keepdims)")

def test_var():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall var
    py_var = py_matrix.var(py_mat)
    torch_var = torch_matrix.var(torch_mat)

    assert allclose(py_var, torch_var), \
    "python overal var != torch overall var"

    # var over axis 0
    py_var = py_matrix.var(py_mat, axis=0)
    torch_var = torch_matrix.var(torch_mat, axis=0)
    assert_close(py_var, torch_var, "var (axis-0)")

    # var over axis 1
    py_var = py_matrix.var(py_mat, axis=1)
    torch_var = torch_matrix.var(torch_mat, axis=1)
    assert_close(py_var, torch_var, "var (axis-1)")

    # var over axis 0, keepdims = True
    py_var = py_matrix.var(py_mat, axis=0, keepdims=True)
    torch_var = torch_matrix.var(torch_mat, axis=0)
    assert_close(py_var, torch_var, "var (axis-0, keepdims)")

    # var over axis 1, keepdims = True
    py_var = py_matrix.var(py_mat, axis=1, keepdims=True)
    torch_var = torch_matrix.var(torch_mat, axis=1, keepdims=True)
    assert_close(py_var, torch_var, "var (axis-1, keepdims)")

def test_std():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall std
    py_std = py_matrix.std(py_mat)
    torch_std = torch_matrix.std(torch_mat)

    assert allclose(py_std, torch_std), \
    "python overal std != torch overall std"

    # std over axis 0
    py_std = py_matrix.std(py_mat, axis=0)
    torch_std = torch_matrix.std(torch_mat, axis=0)
    assert_close(py_std, torch_std, "std (axis-0)")

    # std over axis 1
    py_std = py_matrix.std(py_mat, axis=1)
    torch_std = torch_matrix.std(torch_mat, axis=1)
    assert_close(py_std, torch_std, "std (axis-1)")

    # std over axis 0, keepdims = True
    py_std = py_matrix.std(py_mat, axis=0, keepdims=True)
    torch_std = torch_matrix.std(torch_mat, axis=0)
    assert_close(py_std, torch_std, "std (axis-0, keepdims)")

    # std over axis 1, keepdims = True
    py_std = py_matrix.std(py_mat, axis=1, keepdims=True)
    torch_std = torch_matrix.std(torch_mat, axis=1, keepdims=True)
    assert_close(py_std, torch_std, "std (axis-1, keepdims)")

def test_tsum():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall tsum
    py_tsum = py_matrix.tsum(py_mat)
    torch_tsum = torch_matrix.tsum(torch_mat)

    assert allclose(py_tsum, torch_tsum), \
    "python overal tsum != torch overall tsum"

    # tsum over axis 0
    py_tsum = py_matrix.tsum(py_mat, axis=0)
    torch_tsum = torch_matrix.tsum(torch_mat, axis=0)
    assert_close(py_tsum, torch_tsum, "tsum (axis-0)")

    # tsum over axis 1
    py_tsum = py_matrix.tsum(py_mat, axis=1)
    torch_tsum = torch_matrix.tsum(torch_mat, axis=1)
    assert_close(py_tsum, torch_tsum, "tsum (axis-1)")

    # tsum over axis 0, keepdims = True
    py_tsum = py_matrix.tsum(py_mat, axis=0, keepdims=True)
    torch_tsum = torch_matrix.tsum(torch_mat, axis=0)
    assert_close(py_tsum, torch_tsum, "tsum (axis-0, keepdims)")

    # tsum over axis 1, keepdims = True
    py_tsum = py_matrix.tsum(py_mat, axis=1, keepdims=True)
    torch_tsum = torch_matrix.tsum(torch_mat, axis=1, keepdims=True)
    assert_close(py_tsum, torch_tsum, "tsum (axis-1, keepdims)")

def test_tprod():
    shape = (100, 100)

    py_rand.set_seed()
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # overall tprod
    py_tprod = py_matrix.tprod(py_mat)
    torch_tprod = torch_matrix.tprod(torch_mat)

    assert allclose(py_tprod, torch_tprod), \
    "python overal tprod != torch overall tprod"

    # tprod over axis 0
    py_tprod = py_matrix.tprod(py_mat, axis=0)
    torch_tprod = torch_matrix.tprod(torch_mat, axis=0)
    assert_close(py_tprod, torch_tprod, "tprod (axis-0)")

    # tprod over axis 1
    py_tprod = py_matrix.tprod(py_mat, axis=1)
    torch_tprod = torch_matrix.tprod(torch_mat, axis=1)
    assert_close(py_tprod, torch_tprod, "tprod (axis-1)")

    # tprod over axis 0, keepdims = True
    py_tprod = py_matrix.tprod(py_mat, axis=0, keepdims=True)
    torch_tprod = torch_matrix.tprod(torch_mat, axis=0)
    assert_close(py_tprod, torch_tprod, "tprod (axis-0, keepdims)")

    # tprod over axis 1, keepdims = True
    py_tprod = py_matrix.tprod(py_mat, axis=1, keepdims=True)
    torch_tprod = torch_matrix.tprod(torch_mat, axis=1, keepdims=True)
    assert_close(py_tprod, torch_tprod, "tprod (axis-1, keepdims)")

def test_equal():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_eq = py_matrix.equal(py_x, py_y)
    torch_eq = torch_matrix.equal(torch_x, torch_y)
    py_torch_eq = torch_matrix.to_numpy_array(torch_eq)

    assert py_matrix.allclose(py_eq, py_torch_eq), \
    "python equal != torch equal"

def test_not_equal():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_neq = py_matrix.not_equal(py_x, py_y)
    torch_neq = torch_matrix.not_equal(torch_x, torch_y)
    py_torch_neq = torch_matrix.to_numpy_array(torch_neq)

    assert py_matrix.allclose(py_neq, py_torch_neq), \
    "python not equal != torch not equal"

def test_greater():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.greater(py_x, py_y)
    torch_res = torch_matrix.greater(torch_x, torch_y)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python greater != torch greater"

def test_greater_equal():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.greater_equal(py_x, py_y)
    torch_res = torch_matrix.greater_equal(torch_x, torch_y)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python greater_equal != torch greater_equal"

def test_lesser():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.lesser(py_x, py_y)
    torch_res = torch_matrix.lesser(torch_x, torch_y)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python lesser != torch lesser"

def test_lesser_equal():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.lesser_equal(py_x, py_y)
    torch_res = torch_matrix.lesser_equal(torch_x, torch_y)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python lesser_equal != torch lesser_equal"

def test_tany():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.lesser_equal(py_x, py_y)
    torch_res = torch_matrix.lesser_equal(torch_x, torch_y)

    # overall
    py_any = py_matrix.tany(py_res)
    torch_any = torch_matrix.tany(torch_res)
    assert py_any == torch_any, \
    "python tany != torch tany: overall"

    # axis = 0
    py_any = py_matrix.tany(py_res, axis=0)
    torch_any = torch_matrix.tany(torch_res, axis=0)
    py_torch_any = torch_matrix.to_numpy_array(torch_any)

    assert py_matrix.allclose(py_any, py_torch_any), \
    "python tany != torch tany: (axis-0)"

    # axis = 1
    py_any = py_matrix.tany(py_res, axis=1)
    torch_any = torch_matrix.tany(torch_res, axis=1)
    py_torch_any = torch_matrix.to_numpy_array(torch_any)

    assert py_matrix.allclose(py_any, py_torch_any), \
    "python tany != torch tany: (axis-1)"

    # axis = 0, keepdims
    py_any = py_matrix.tany(py_res, axis=0, keepdims=True)
    torch_any = torch_matrix.tany(torch_res, axis=0, keepdims=True)
    py_torch_any = torch_matrix.to_numpy_array(torch_any)

    assert py_matrix.allclose(py_any, py_torch_any), \
    "python tany != torch tany: (axis-0, keepdims)"

    # axis = 1, keepdims
    py_any = py_matrix.tany(py_res, axis=1, keepdims=True)
    torch_any = torch_matrix.tany(torch_res, axis=1, keepdims=True)
    py_torch_any = torch_matrix.to_numpy_array(torch_any)

    assert py_matrix.allclose(py_any, py_torch_any), \
    "python tany != torch tany: (axis-1, keepdim)"

def test_tall():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.lesser_equal(py_x, py_y)
    torch_res = torch_matrix.lesser_equal(torch_x, torch_y)

    # overall
    py_all = py_matrix.tall(py_res)
    torch_all = torch_matrix.tall(torch_res)
    assert py_all == torch_all, \
    "python tall != torch tall: overall"

    # axis = 0
    py_all = py_matrix.tall(py_res, axis=0)
    torch_all = torch_matrix.tall(torch_res, axis=0)
    py_torch_all = torch_matrix.to_numpy_array(torch_all)

    assert py_matrix.allclose(py_all, py_torch_all), \
    "python tall != torch tall: (axis-0)"

    # axis = 1
    py_all = py_matrix.tall(py_res, axis=1)
    torch_all = torch_matrix.tall(torch_res, axis=1)
    py_torch_all = torch_matrix.to_numpy_array(torch_all)

    assert py_matrix.allclose(py_all, py_torch_all), \
    "python tall != torch tall: (axis-1)"

    # axis = 0, keepdims
    py_all = py_matrix.tall(py_res, axis=0, keepdims=True)
    torch_all = torch_matrix.tall(torch_res, axis=0, keepdims=True)
    py_torch_all = torch_matrix.to_numpy_array(torch_all)

    assert py_matrix.allclose(py_all, py_torch_all), \
    "python tall != torch tall: (axis-0, keepdims)"

    # axis = 1, keepdims
    py_all = py_matrix.tall(py_res, axis=1, keepdims=True)
    torch_all = torch_matrix.tall(torch_res, axis=1, keepdims=True)
    py_torch_all = torch_matrix.to_numpy_array(torch_all)

    assert py_matrix.allclose(py_all, py_torch_all), \
    "python tall != torch tall: (axis-1, keepdim)"

def test_maximum():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.maximum(py_x, py_y)
    torch_res = torch_matrix.maximum(torch_x, torch_y)

    assert_close(py_res, torch_res, "maximum")

def test_minimum():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    py_y = py_rand.randn(shape)

    torch_x = torch_matrix.float_tensor(py_x)
    torch_y = torch_matrix.float_tensor(py_y)

    py_res = py_matrix.minimum(py_x, py_y)
    torch_res = torch_matrix.minimum(torch_x, torch_y)

    assert_close(py_res, torch_res, "minimum")

def test_argmax():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    # axis=0
    py_res = py_matrix.argmax(py_x, axis=0)
    torch_res = torch_matrix.argmax(torch_x, axis=0)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python argmax != torch argmax: (axis-0)"

    # axis=1
    py_res = py_matrix.argmax(py_x, axis=1)
    torch_res = torch_matrix.argmax(torch_x, axis=1)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python argmax != torch argmax: (axis-1)"

def test_argmin():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    # axis=0
    py_res = py_matrix.argmin(py_x, axis=0)
    torch_res = torch_matrix.argmin(torch_x, axis=0)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python argmin != torch argmin: (axis-0)"

    # axis=1
    py_res = py_matrix.argmin(py_x, axis=1)
    torch_res = torch_matrix.argmin(torch_x, axis=1)
    py_torch_res = torch_matrix.to_numpy_array(torch_res)

    assert py_matrix.allclose(py_res, py_torch_res), \
    "python argmin != torch argmin: (axis-1)"

def test_dot():
    # vector-vector
    a_shape = (100,)
    b_shape = (100,)

    py_rand.set_seed()
    py_a = py_rand.randn(a_shape)
    py_b = py_rand.randn(b_shape)
    torch_a = torch_matrix.float_tensor(py_a)
    torch_b = torch_matrix.float_tensor(py_b)

    py_dot = py_matrix.dot(py_a, py_b)
    torch_dot = torch_matrix.dot(torch_a, torch_b)

    assert allclose(py_dot, torch_dot), \
    "python dot != torch_dot: vector-vector"

    # matrix-vector
    a_shape = (100,100)
    b_shape = (100,)

    py_rand.set_seed()
    py_a = py_rand.randn(a_shape)
    py_b = py_rand.randn(b_shape)
    torch_a = torch_matrix.float_tensor(py_a)
    torch_b = torch_matrix.float_tensor(py_b)

    py_dot = py_matrix.dot(py_a, py_b)
    torch_dot = torch_matrix.dot(torch_a, torch_b)

    assert_close(py_dot, torch_dot, "dot: matrix-vector")

    # matrix-matrix
    a_shape = (100,100)
    b_shape = (100,100)

    py_rand.set_seed()
    py_a = py_rand.randn(a_shape)
    py_b = py_rand.randn(b_shape)
    torch_a = torch_matrix.float_tensor(py_a)
    torch_b = torch_matrix.float_tensor(py_b)

    py_dot = py_matrix.dot(py_a, py_b)
    torch_dot = torch_matrix.dot(torch_a, torch_b)

    assert_close(py_dot, torch_dot, "dot: matrix-matrix")

def test_outer():
    a_shape = (100,)
    b_shape = (100,)

    py_rand.set_seed()
    py_a = py_rand.randn(a_shape)
    py_b = py_rand.randn(b_shape)
    torch_a = torch_matrix.float_tensor(py_a)
    torch_b = torch_matrix.float_tensor(py_b)

    py_res = py_matrix.outer(py_a, py_b)
    torch_res = torch_matrix.outer(torch_a, torch_b)

    assert_close(py_res, torch_res, "outer")

# ----- Nonlinearities ----- #

def test_tabs():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.tabs(py_x)
    torch_y = torch_func.tabs(torch_x)
    assert_close(py_y, torch_y, "tabs")

def test_exp():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.exp(py_x)
    torch_y = torch_func.exp(torch_x)
    assert_close(py_y, torch_y, "exp")

def test_log():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.log(py_x)
    torch_y = torch_func.log(torch_x)
    assert_close(py_y, torch_y, "log")

def test_tanh():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.tanh(py_x)
    torch_y = torch_func.tanh(torch_x)
    assert_close(py_y, torch_y, "tanh")

def test_expit():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.expit(py_x)
    torch_y = torch_func.expit(torch_x)
    assert_close(py_y, torch_y, "expit")

def test_reciprocal():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.reciprocal(py_x)
    torch_y = torch_func.reciprocal(torch_x)
    assert_close(py_y, torch_y, "reciprocal")

def test_atanh():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = 2 * py_rand.rand(shape) - 1
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.atanh(py_x)
    torch_y = torch_func.atanh(torch_x)
    # the atanh function is a bit less precise than the others
    # so the tolerance is a bit more flexible
    assert_close(py_y, torch_y, "atanh", rtol=1e-05, atol=1e-07)

def test_sqrt():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.sqrt(py_x)
    torch_y = torch_func.sqrt(torch_x)
    assert_close(py_y, torch_y, "sqrt")

def test_square():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.square(py_x)
    torch_y = torch_func.square(torch_x)
    assert_close(py_y, torch_y, "square")

def test_tpow():
    shape = (100, 100)
    power = 3

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.tpow(py_x, power)
    torch_y = torch_func.tpow(torch_x, power)
    assert_close(py_y, torch_y, "tpow")

def test_cosh():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.cosh(py_x)
    torch_y = torch_func.cosh(torch_x)
    assert_close(py_y, torch_y, "cosh")

def test_logaddexp():
    shape = (100, 100)

    py_rand.set_seed()
    py_x_1 = py_rand.randn(shape)
    py_x_2 = py_rand.randn(shape)

    torch_x_1 = torch_matrix.float_tensor(py_x_1)
    torch_x_2 = torch_matrix.float_tensor(py_x_2)

    py_y = py_func.logaddexp(py_x_1, py_x_2)
    torch_y = torch_func.logaddexp(torch_x_1, torch_x_2)
    assert_close(py_y, torch_y, "logaddexp")

def test_logcosh():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.logcosh(py_x)
    torch_y = torch_func.logcosh(torch_x)
    assert_close(py_y, torch_y, "logcosh")

def test_acosh():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = 1 + py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.acosh(py_x)
    torch_y = torch_func.acosh(torch_x)
    assert_close(py_y, torch_y, "acosh")

def test_logit():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.logit(py_x)
    torch_y = torch_func.logit(torch_x)
    assert_close(py_y, torch_y, "logit")

def test_softplus():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.softplus(py_x)
    torch_y = torch_func.softplus(torch_x)
    assert_close(py_y, torch_y, "softplus")

def test_cos():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.cos(py_x)
    torch_y = torch_func.cos(torch_x)
    assert_close(py_y, torch_y, "cos")

def test_sin():
    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.sin(py_x)
    torch_y = torch_func.sin(torch_x)
    assert_close(py_y, torch_y, "sin")


if __name__ == "__main__":
    pytest.main([__file__])
