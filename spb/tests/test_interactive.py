from sympy import symbols, cos, sin, Tuple
import param
import panel as pn
import bokeh.models as bm
from spb.interactive import iplot, DynamicParam, MyList
from spb.series import InteractiveSeries
from spb.backends.plotly import PB

def test_DynamicParam():
    a, b, c, d, e, f = symbols("a, b, c, d, e, f")

    # test _tuple_to_dict
    t = DynamicParam(params = {
        a: (1, (0, 5)),
        b: (2, (1.5, 4.5), 20),
        c: (3, (2, 5), 30, "test1"),
        d: (1, (1, 10), 10, "test2", "log"),
    }, use_latex=False)
    p1 = getattr(t.param, "dyn_param_0")
    p2 = getattr(t.param, "dyn_param_1")
    p3 = getattr(t.param, "dyn_param_2")
    p4 = getattr(t.param, "dyn_param_3")

    def test_number(p, d, sb, l, st):
        assert isinstance(p, param.Number)
        assert p.default == d
        assert p.softbounds == sb
        assert p.label == l
        assert p.step == st
    
    def test_log_slider(p, d, sb, n, l):
        assert isinstance(p, MyList)
        assert p.default == 1
        assert p.objects[0] == sb[0]
        assert p.objects[-1] == sb[1]
        assert len(p.objects) == 10
        assert p.label == l

    test_number(p1, 1, (0, 5), "a", 0.125)
    test_number(p2, 2, (1.5, 4.5), "b", 0.15)
    test_number(p3, 3, (2, 5), "test1", 0.1)
    test_log_slider(p4, 1, (1, 10), 10, "test2")

    # test mix tuple and parameters
    t = DynamicParam(params = {
        a: (1, (0, 5)),
        b: (1, (1, 10), 10, "test3", "log"),
        c: param.Boolean(default=True, label="test4"),
        d: param.ObjectSelector(default=5, objects=[1, 2, 3, 4, 5], label="test5"),
        e: param.Number(default=6.1, softbounds=(1.1, 10.1), label="test6"),
        f: param.Integer(default=6, softbounds=(1, None), label="test7"),
    }, use_latex=False)
    p1 = getattr(t.param, "dyn_param_0")
    p2 = getattr(t.param, "dyn_param_1")
    p3 = getattr(t.param, "dyn_param_2")
    p4 = getattr(t.param, "dyn_param_3")
    p5 = getattr(t.param, "dyn_param_4")
    p6 = getattr(t.param, "dyn_param_5")
    test_number(p1, 1, (0, 5), "a", 0.125)
    test_log_slider(p2, 1, (1, 10), 10, "test3")
    assert isinstance(p3, param.Boolean)
    assert p3.default == True
    assert p3.label == "test4"
    assert isinstance(p4, param.ObjectSelector)
    assert p4.label == "test5"
    assert p4.default == 5
    assert isinstance(p5, param.Number)
    assert p5.default == 6.1
    assert p5.softbounds == (1.1, 10.1)
    assert p5.label == "test6"
    assert isinstance(p6, param.Integer)
    assert p6.default == 6
    assert p6.label == "test7"

    r = { a: 1, b: 1, c: True, d: 5, e: 6.1, f: 6 }
    assert t.read_parameters() == r


def test_iplot():
    a, b, c, d = symbols("a, b, c, d")
    x, y, u, v = symbols("x, y, u, v")

    t = iplot(
        ((a + b + c + d) * cos(x), (x, -5, 5)),
        params = {
            a: (2, (1, 3), 5),
            b: (3, (2, 4000), 10, "label", "log"),
            c: param.Number(0.15, softbounds=(0, 1), label="test", step=0.025),
            d: param.Integer(1, softbounds=(0, 10)),
            y: param.Integer(1, softbounds=(0, None)),
            u: param.Boolean(default=True),
            v: param.ObjectSelector(default=2, objects=[1, 2, 3, 4]),
        }, show=False, layout="tb", ncols=2
    )

    # there are 4 parameters in this plot
    assert len(t.mapping) == 7
    
    # c1 wraps the controls, c2 wraps the plot
    c1, c2 = t.show().get_root().children
    gridbox = c1.children[0].children[0]
    print(type(gridbox.children[0][0]))
    assert isinstance(gridbox.children[0][0], bm.Slider)
    assert isinstance(gridbox.children[1][0].children[1], bm.Slider)
    assert isinstance(gridbox.children[2][0], bm.Slider)
    assert isinstance(gridbox.children[3][0], bm.Slider)
    assert isinstance(gridbox.children[4][0], bm.Slider)
    assert isinstance(gridbox.children[5][0], bm.CheckboxGroup)
    assert isinstance(gridbox.children[6][0], bm.Select)


def test_interactiveseries():
    # test for the instantiation of InteractiveSeries
    from sympy.vector import CoordSys3D
    N = CoordSys3D("N")
    i, j, k = N.base_vectors()
    x, y, z = N.base_scalars()
    a, b, c, xs, ys, zs = symbols("a:c, x:z")
    v1 = -a * sin(y) * i + b * cos(x) * j
    m1 = v1.to_matrix(N)
    m1 = m1[:-1]
    l1 = list(m1)
    v2 = -a * sin(y) * i + b * cos(x) * j + c * cos(z) * k
    m2 = v2.to_matrix(N)
    l2 = list(m2)

    def test_vector(v, ranges, params, expr, label, symbol, shape, n=10):
        t = iplot(
            (v, *ranges),
            params = params,
            fig_kw = dict(
                n = n,
                backend = PB
            ),
            show=False
        )

        s = t._backend.series[0]
        assert isinstance(s, InteractiveSeries)
        assert s.expr == expr
        assert s.label == label
        assert len(s.ranges) == len(ranges)
        assert s.ranges[symbol].shape == shape
        if len(ranges) == 2:
            assert s.is_2Dvector
            assert not s.is_3Dvector
        else:
            assert not s.is_2Dvector
            assert s.is_3Dvector
    
    # 2D vectors
    params = {
        a: (2, (0, 3)),
        b: (3, (1, 4)),
    }
    ranges = (x, -5, 5), (y, -4, 4)
    test_vector(v1, ranges, params, Tuple(-a * sin(ys), b * cos(xs)), str(v1),
            xs, (10, 10))
    test_vector(m1, ranges, params, Tuple(-a * sin(y), b * cos(x)),
            str(tuple(m1)), x, (10, 10))
    test_vector(l1, ranges, params, Tuple(-a * sin(y), b * cos(x)),
            str(tuple(l1)), x, (8, 8), 8)
    
    # 3D vectors
    params = {
        a: (2, (0, 3)),
        b: (3, (1, 4)),
        c: (4, (2, 5)),
    }
    ranges = (x, -5, 5), (y, -4, 4), (z, -6, 6)
    test_vector(v2, ranges, params, Tuple(-a * sin(ys), b * cos(xs), c * cos(zs)),
            str(v2), xs, (10, 10, 10))
    test_vector(m2, ranges, params, Tuple(-a * sin(y), b * cos(x), c * cos(z)),
            str(m2), x, (10, 10, 10))
    test_vector(l2, ranges, params, Tuple(-a * sin(y), b * cos(x), c * cos(z)),
            str(tuple(l2)), x, (10, 10, 10))
