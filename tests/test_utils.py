from pytest import raises
from spb import (
    plot, plot3d, plot_implicit, plot_vector, plot_complex, plot_complex_list,
    MB, plot_geometry
)
from spb.series import (
    LineInteractiveSeries, SurfaceInteractiveSeries, Vector2DInteractiveSeries,
    ComplexDomainColoringInteractiveSeries, ComplexPointInteractiveSeries,
    GeometryInteractiveSeries
)
from spb.utils import (
    _check_arguments, _create_ranges, _plot_sympify, _validate_kwargs
)
from sympy import symbols, Expr, Tuple, Integer, sin, cos, Matrix, I, Polygon


def test_plot_sympify():
    x, y = symbols("x, y")

    # argument is already sympified
    args = x + y
    r = _plot_sympify(args)
    assert r == args

    # one argument needs to be sympified
    args = (x + y, 1)
    r = _plot_sympify(args)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert isinstance(r[0], Expr)
    assert isinstance(r[1], Integer)

    # string and dict should not be sympified
    args = (x + y, (x, 0, 1), "str", 1, {1: 1, 2: 2.0})
    r = _plot_sympify(args)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 5
    assert isinstance(r[0], Expr)
    assert isinstance(r[1], Tuple)
    assert isinstance(r[2], str)
    assert isinstance(r[3], Integer)
    assert isinstance(r[4], dict) and isinstance(r[4][1], int) and isinstance(r[4][2], float)

    # nested arguments containing strings
    args = ((x + y, (y, 0, 1), "a"), (x + 1, (x, 0, 1), "$f_{1}$"))
    r = _plot_sympify(args)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert isinstance(r[0], Tuple)
    assert isinstance(r[0][1], Tuple)
    assert isinstance(r[0][1][1], Integer)
    assert isinstance(r[0][2], str)
    assert isinstance(r[1], Tuple)
    assert isinstance(r[1][1], Tuple)
    assert isinstance(r[1][1][1], Integer)
    assert isinstance(r[1][2], str)


def test_create_ranges():
    x, y = symbols("x, y")

    # user don't provide any range -> return a default range
    r = _create_ranges({x}, [], 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert isinstance(r[0], (Tuple, tuple))
    assert r[0] == (x, -10, 10)

    r = _create_ranges({x, y}, [], 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert isinstance(r[0], (Tuple, tuple))
    assert isinstance(r[1], (Tuple, tuple))
    assert r[0] == (x, -10, 10) or (y, -10, 10)
    assert r[1] == (y, -10, 10) or (x, -10, 10)
    assert r[0] != r[1]

    # not enough ranges provided by the user -> create default ranges
    r = _create_ranges(
        {x, y},
        [
            (x, 0, 1),
        ],
        2,
    )
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert isinstance(r[0], (Tuple, tuple))
    assert isinstance(r[1], (Tuple, tuple))
    assert r[0] == (x, 0, 1) or (y, -10, 10)
    assert r[1] == (y, -10, 10) or (x, 0, 1)
    assert r[0] != r[1]

    # too many free symbols
    raises(ValueError, lambda: _create_ranges({x, y}, [], 1))
    raises(ValueError, lambda: _create_ranges({x, y}, [(x, 0, 5), (y, 0, 1)], 1))


def test_check_arguments_plot():
    ### Test arguments for plot()

    x, y = symbols("x, y")

    # single expressions
    args = _plot_sympify((x + 1,))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, (x, -10, 10), None, None)

    # single expressions custom label
    args = _plot_sympify((x + 1, "label"))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, (x, -10, 10), "label", None)

    # single expressions with range
    args = _plot_sympify((x + 1, (x, -2, 2)))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, (x, -2, 2), None, None)

    # single expressions with range, label and rendering-kw dictionary
    args = _plot_sympify((x + 1, (x, -2, 2), "test", {0: 0, 1: 1}))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, (x, -2, 2), "test", {0: 0, 1: 1})

    # multiple expressions
    args = _plot_sympify((x + 1, x ** 2))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, (x, -10, 10), None, None)
    assert r[1] == (x ** 2, (x, -10, 10), None, None)

    # multiple expressions over the same range
    args = _plot_sympify((x + 1, x ** 2, (x, 0, 5)))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, (x, 0, 5), None, None)
    assert r[1] == (x ** 2, (x, 0, 5), None, None)

    # multiple expressions over the same range with the same rendering kws
    args = _plot_sympify((x + 1, x ** 2, (x, 0, 5), {0: 0, 1: 1}))
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, (x, 0, 5), None, {0: 0, 1: 1})
    assert r[1] == (x ** 2, (x, 0, 5), None, {0: 0, 1: 1})

    # multiple expressions with different ranges, labels and rendering kws
    args = _plot_sympify([(x + 1, (x, 0, 5)), (x ** 2, (x, -2, 2), "test", {0: 0, 1: 1})])
    r = _check_arguments(args, 1, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, (x, 0, 5), None, None)
    assert r[1] == (x ** 2, (x, -2, 2), "test", {0: 0, 1: 1})


def test_check_arguments_plot_parametric():
    ### Test arguments for plot_parametric()

    x, y = symbols("x, y")

    # single parametric expression
    args = _plot_sympify((x + 1, x))
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, x, (x, -10, 10), None, None)

    # single parametric expression with custom range, label and rendering kws
    args = _plot_sympify((x + 1, x, (x, -2, 2), "test", {0: 0, 1: 1}))
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, x, (x, -2, 2), "test", {0: 0, 1: 1})

    args = _plot_sympify(((x + 1, x), (x, -2, 2), "test"))
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, x, (x, -2, 2), "test", None)

    # multiple parametric expressions same symbol
    args = _plot_sympify([(x + 1, x), (x ** 2, x + 1)])
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, (x, -10, 10), None, None)
    assert r[1] == (x ** 2, x + 1, (x, -10, 10), None, None)

    # multiple parametric expressions different symbols
    args = _plot_sympify([(x + 1, x), (y ** 2, y + 1, "test")])
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, (x, -10, 10), None, None)
    assert r[1] == (y ** 2, y + 1, (y, -10, 10), "test", None)

    # multiple parametric expressions same range
    args = _plot_sympify([(x + 1, x), (x ** 2, x + 1), (x, -2, 2)])
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, (x, -2, 2), None, None)
    assert r[1] == (x ** 2, x + 1, (x, -2, 2), None, None)

    # multiple parametric expressions, custom ranges and labels
    args = _plot_sympify([(x + 1, x, (x, -2, 2), "test1"), (x ** 2, x + 1, (x, -3, 3), "test2", {0: 0, 1: 1})])
    r = _check_arguments(args, 2, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, (x, -2, 2), "test1", None)
    assert r[1] == (x ** 2, x + 1, (x, -3, 3), "test2", {0: 0, 1: 1})


def test_check_arguments_plot3d_parametric_line():
    ### Test arguments for plot3d_parametric_line()

    x, y = symbols("x, y")

    # single parametric expression
    args = _plot_sympify((x + 1, x, sin(x)))
    r = _check_arguments(args, 3, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, x, sin(x), (x, -10, 10), None, None)

    # single parametric expression with custom range, label and rendering kws
    args = _plot_sympify((x + 1, x, sin(x), (x, -2, 2), "test", {0: 0, 1: 1}))
    r = _check_arguments(args, 3, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, x, sin(x), (x, -2, 2), "test", {0: 0, 1: 1})

    args = _plot_sympify(((x + 1, x, sin(x)), (x, -2, 2), "test"))
    r = _check_arguments(args, 3, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + 1, x, sin(x), (x, -2, 2), "test", None)

    # multiple parametric expression same symbol
    args = _plot_sympify([(x + 1, x, sin(x)), (x ** 2, 1, cos(x), {0: 0, 1: 1})])
    r = _check_arguments(args, 3, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, sin(x), (x, -10, 10), None, None)
    assert r[1] == (x ** 2, Integer(1), cos(x), (x, -10, 10), None, {0: 0, 1: 1})

    # multiple parametric expression different symbols
    args = _plot_sympify([(x + 1, x, sin(x)), (y ** 2, 1, cos(y))])
    r = _check_arguments(args, 3, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, sin(x), (x, -10, 10), None, None)
    assert r[1] == (y ** 2, Integer(1), cos(y), (y, -10, 10), None, None)

    # multiple parametric expression, custom ranges and labels
    args = _plot_sympify([(x + 1, x, sin(x)), (x ** 2, 1, cos(x), (x, -2, 2), "test", {0: 0, 1: 1})])
    r = _check_arguments(args, 3, 1)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + 1, x, sin(x), (x, -10, 10), None, None)
    assert r[1] == (x ** 2, Integer(1), cos(x), (x, -2, 2), "test", {0: 0, 1: 1})


def test_check_arguments_plot3d_plot_contour():
    ### Test arguments for plot3d() and plot_contour()

    x, y = symbols("x, y")

    # single expression
    args = _plot_sympify((x + y,))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert len(r[0]) == 5
    assert r[0][0] == x + y
    assert r[0][1] == (x, -10, 10) or (y, -10, 10)
    assert r[0][2] == (y, -10, 10) or (x, -10, 10)
    assert r[0][1] != r[0][2]
    assert r[0][3] is None
    assert r[0][4] is None

    # single expression, custom range, label and rendering kws
    args = _plot_sympify((x + y, (x, -2, 2), "test", {0: 0, 1: 1}))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert len(r[0]) == 5
    assert r[0][0] == x + y
    assert r[0][1] == (x, -2, 2) or (y, -10, 10)
    assert r[0][2] == (y, -10, 10) or (x, -2, 2)
    assert r[0][1] != r[0][2]
    assert r[0][3] == "test"
    assert r[0][4] == {0: 0, 1: 1}

    args = _plot_sympify((x + y, (x, -2, 2), (y, -4, 4), "test"))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + y, (x, -2, 2), (y, -4, 4), "test", None)

    # multiple expressions
    args = _plot_sympify((x + y, x * y))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert len(r[0]) == 5
    assert len(r[1]) == 5
    assert r[0][0] == x + y
    assert r[0][1] == (x, -10, 10) or (y, -10, 10)
    assert r[0][2] == (y, -10, 10) or (x, -10, 10)
    assert r[0][1] != r[0][2]
    assert r[0][3] is None
    assert r[0][4] == None
    assert r[1][0] == x * y
    assert r[1][1] == (x, -10, 10) or (y, -10, 10)
    assert r[1][2] == (y, -10, 10) or (x, -10, 10)
    assert r[1][1] != r[0][2]
    assert r[1][3] is None
    assert r[1][4] == None

    # multiple expressions, same custom ranges
    args = _plot_sympify((x + y, x * y, (x, -2, 2), (y, -4, 4)))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + y, (x, -2, 2), (y, -4, 4), None, None)
    assert r[1] == (x * y, (x, -2, 2), (y, -4, 4), None, None)

    # multiple expressions, custom ranges, labels and rendering kws
    args = _plot_sympify(
        [(x + y, (x, -2, 2), (y, -4, 4)),
        (x * y, (x, -3, 3), (y, -6, 6), "test", {0: 0, 1: 1})]
    )
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert r[0] == (x + y, (x, -2, 2), (y, -4, 4), None, None)
    assert r[1] == (x * y, (x, -3, 3), (y, -6, 6), "test", {0: 0, 1: 1})


def test_check_arguments_plot3d_parametric_surface():
    ### Test arguments for plot3d_parametric_surface()

    x, y = symbols("x, y")

    # single parametric expression
    args = _plot_sympify((x + y, cos(x + y), sin(x + y)))
    r = _check_arguments(args, 3, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert len(r[0]) == 7
    assert r[0][0] == x + y
    assert r[0][1] == cos(x + y)
    assert r[0][2] == sin(x + y)
    assert r[0][3] == (x, -10, 10) or (y, -10, 10)
    assert r[0][4] == (y, -10, 10) or (x, -10, 10)
    assert r[0][3] != r[0][4]
    assert r[0][5] == None
    assert r[0][6] == None

    # single parametric expression, custom ranges, labels and rendering kws
    args = _plot_sympify(
        (x + y, cos(x + y), sin(x + y), (x, -2, 2), (y, -4, 4), "test", {0: 0})
    )
    r = _check_arguments(args, 3, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert r[0] == (x + y, cos(x + y), sin(x + y), (x, -2, 2), (y, -4, 4), "test", {0: 0})

    # multiple parametric expressions
    args = _plot_sympify(
        [(x + y, cos(x + y), sin(x + y)), (x - y, cos(x - y), sin(x - y), "test")]
    )
    r = _check_arguments(args, 3, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert len(r[0]) == 7
    assert len(r[1]) == 7
    assert r[0][0] == x + y
    assert r[0][1] == cos(x + y)
    assert r[0][2] == sin(x + y)
    assert r[0][3] == (x, -10, 10) or (y, -10, 10)
    assert r[0][4] == (y, -10, 10) or (x, -10, 10)
    assert r[0][3] != r[0][4]
    assert r[0][5] == None
    assert r[0][6] == None
    assert r[1][0] == x - y
    assert r[1][1] == cos(x - y)
    assert r[1][2] == sin(x - y)
    assert r[1][3] == (x, -10, 10) or (y, -10, 10)
    assert r[1][4] == (y, -10, 10) or (x, -10, 10)
    assert r[1][3] != r[0][4]
    assert r[1][5] == "test"
    assert r[1][6] == None

    # multiple parametric expressions, custom ranges and labels
    args = _plot_sympify(
        [
            (x + y, cos(x + y), sin(x + y), (x, -2, 2), "test"),
            (x - y, cos(x - y), sin(x - y), (x, -3, 3), (y, -4, 4), "test2", {0: 0, 1: 1}),
        ]
    )
    r = _check_arguments(args, 3, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert len(r[0]) == 7
    assert r[0][0] == x + y
    assert r[0][1] == cos(x + y)
    assert r[0][2] == sin(x + y)
    assert r[0][3] == (x, -2, 2) or (y, -10, 10)
    assert r[0][4] == (y, -10, 10) or (x, -2, 2)
    assert r[0][3] != r[0][4]
    assert r[0][5] == "test"
    assert r[0][6] == None
    assert r[1] == (x - y, cos(x - y), sin(x - y), (x, -3, 3), (y, -4, 4), "test2", {0: 0, 1: 1})


def test_check_arguments_plot_implicit():
    ### Test arguments for plot_implicit

    x, y = symbols("x, y")

    # single expression with both ranges
    args = _plot_sympify((x > 0, (x, -2, 2), (y, -3, 3)))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert len(r[0]) == 5
    assert r[0] == (x > 0, (x, -2, 2), (y, -3, 3), None, None)

    # single expression with one missing range
    args = _plot_sympify((x > 0, (x, -2, 2), "test", {0: 0, 1: 1}))
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 1
    assert len(r[0]) == 5
    assert r[0][:2] == (x > 0, (x, -2, 2))
    assert r[0][-2] == "test"
    assert r[0][-1] == {0: 0, 1: 1}
    assert (r[0][2][1] == Integer(-10)) and (r[0][2][2] == Integer(10))

    # multiple expressions
    args = _plot_sympify([(x > 0, (x, -2, 2), (y, -3, 3)), ((x > 0) & (y < 0), "test", {0: 0, 1: 1})])
    r = _check_arguments(args, 1, 2)
    assert isinstance(r, (list, tuple, Tuple)) and len(r) == 2
    assert len(r[0]) == 5
    assert r[0] == (x > 0, (x, -2, 2), (y, -3, 3), None, None)
    assert len(r[1]) == 5
    assert r[1][0] == ((x > 0) & (y < 0))
    assert (r[1][1] == Tuple(x, -10, 10)) or (r[1][1] == Tuple(y, -10, 10))
    assert (r[1][2] == Tuple(x, -10, 10)) or (r[1][2] == Tuple(y, -10, 10))
    assert r[1][-2] == "test"
    assert r[1][-1] == {0: 0, 1: 1}

    # incompatible free symbols between expression and ranges
    z = symbols("z")
    args = _plot_sympify((x * y > 0, (x, -2, 2), (z, -3, 3)))
    raises(ValueError, lambda: _check_arguments(args, 1, 2))


def test_raise_warning_keyword_validation():
    # verify that plotting functions raise warning when a mispelled keyword
    # argument is provided.
    # NOTE: there is pytest.warn, however I can't get it to work here. I don't
    # understand its error message :|
    # Hence, I'm going to do it my own way: execute the _validate_kwargs
    # function and check that the warning message contains the expected
    # misspelled keywords.

    x, y, z = symbols("x:z")

    def do_test(p, kw, keys):
        msg = _validate_kwargs(p, **kw)
        assert all(k in msg for k in keys)

    # x_label should be xlabel: this is a Backend-related keyword
    kw = dict(adaptive=False, x_label="a")
    p = plot(sin(x), backend=MB, show=False, **kw)
    do_test(p, kw, ["x_label", "xlabel"])

    # adapt should be adaptive: this is a LineOver1DRangeSeries keyword
    kw = dict(adapt=False)
    p = plot(sin(x), backend=MB, show=False, **kw)
    do_test(p, kw, ["adapt", "adaptive"])

    # surface_colors should be surface_color: this is a SurfaceBaseSeries
    # keyword
    kw = dict(surface_colors="r")
    p = plot3d(cos(x**2 + y**2), backend=MB, show=False, **kw)
    do_test(p, kw, ["surface_colors", "surface_color"])

    # deptt should be depth: this is a ImplicitSeries keyword
    kw = dict(deptt=2)
    p = plot_implicit(cos(x), backend=MB, show=False, **kw)
    do_test(p, kw, ["deptt", "depth"])

    # streamline should be streamlines: this is a VectorBase keyword
    kw = dict(streamline=True)
    p = plot_vector(Matrix([sin(y), cos(x)]), backend=MB, show=False, **kw)
    do_test(p, kw, ["streamline", "streamlines"])

    # phase_res should be phaseres
    kw = dict(phase_res=3)
    p = plot_complex(z, (z, -2-2j, 2+2j), backend=MB, show=False, **kw)
    do_test(p, kw, ["phase_res", "phaseres"])

    # render_kw should be rendering_kw
    kw = dict(render_kw={"color": "r"})
    p = plot_complex_list(3 + 2 * I, backend=MB, show=False, **kw)
    do_test(p, kw, ["render_kw", "rendering_kw"])

    # is_fille should be is_filled
    kw = dict(is_fille=False)
    p = plot_geometry(Polygon((4, 0), 4, n=5), backend=MB, show=False)
    do_test(p, kw, ["is_fille", "is_filled"])


    # test interactive: since the backend is ab attribute of InteractivePlot,
    # it is easier to perform tests with the following procedure.
    # This is not future proof, but it's a good start.

    # is_points should be is_point
    kw = dict(is_points=True)
    s = LineInteractiveSeries([cos(x * y)], [(x, 0, 5)], params={y: 1}, **kw)
    p = MB(s, **kw)
    do_test(p, kw, ["is_points", "is_point"])

    # surface_colors should be surface_color
    kw = dict(surface_colors="r")
    s = SurfaceInteractiveSeries(
        [cos(z * x**2 + y**2)], [(x, -2, 2), (y, -2, 2)], params={z: 1}, **kw)
    p = MB(s, **kw)
    do_test(p, kw, ["surface_colors", "surface_color"])

    # streamline should be streamlines: this is a VectorBase keyword
    kw = dict(streamline=True)
    s = Vector2DInteractiveSeries([y, x * z], [(x, -2, 2), (y, -2, 2)],
        params={z: 1}, **kw)
    p = MB(s, **kw)
    do_test(p, kw, ["streamline", "streamlines"])

    # phase_res should be phaseres
    kw = dict(phase_res=3)
    s = ComplexDomainColoringInteractiveSeries(
        z*y, (z, -2-2j, 2+2j), params={y: 1}, **kw)
    p = MB(s, **kw)
    do_test(p, kw, ["phase_res", "phaseres"])

    # render_kw should be rendering_kw
    kw = dict(render_kw={"color": "r"})
    s = ComplexPointInteractiveSeries([x * 3 + 2 * I], params={x: 1}, **kw)
    p = MB(s, show=False, **kw)
    do_test(p, kw, ["render_kw", "rendering_kw"])

    # is_fille should be is_filled
    kw = dict(is_fille=False)
    s = GeometryInteractiveSeries([Polygon((4, 0), x, n=5)], [],
        params={x: 1}, **kw)
    p = MB(s, show=False, **kw)
    do_test(p, kw, ["is_fille", "is_filled"])
    
