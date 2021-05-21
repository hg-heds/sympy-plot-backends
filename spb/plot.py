"""Plotting module for Sympy.

A plot is represented by the ``Plot`` class that contains a reference to the
backend and a list of the data series to be plotted. The data series are
instances of classes meant to simplify getting points and meshes from sympy
expressions. ``plot_backends`` is a dictionary with all the backends.

This module gives only the essential. For all the fancy stuff use directly
the backend. You can get the backend wrapper for every plot from the
``_backend`` attribute. Moreover the data series classes have various useful
methods like ``get_points``, ``get_meshes``, etc, that may
be useful if you wish to use another plotting library.

Especially if you need publication ready graphs and this module is not enough
for you - just get the ``_backend`` attribute and add whatever you want
directly to it. In the case of matplotlib (the common way to graph data in
python) just copy ``_backend.fig`` which is the figure and ``_backend.ax``
which is the axis and work on them as you would on any other matplotlib object.

Simplicity of code takes much greater importance than performance. Don't use it
if you care at all about performance. A new backend instance is initialized
every time you call ``show()`` and the old one is left to the garbage collector.
"""


from sympy import Expr, Tuple, Dummy, Symbol, oo

from spb.backends.base_backend import Plot
from spb.defaults import TWO_D_B, THREE_D_B
from spb.utils import _is_range, _plot_sympify

# N.B.
# When changing the minimum module version for matplotlib, please change
# the same in the `SymPyDocTestFinder`` in `sympy/testing/runtests.py`

from spb.series import (
    LineOver1DRangeSeries, Parametric2DLineSeries,
    Parametric3DLineSeries, SurfaceOver2DRangeSeries,
    ParametricSurfaceSeries, ContourSeries, ImplicitSeries,
    _set_discretization_points
)

def set_matplotlib_backend():
    """ Set MatplotlibBackend as the plotting backend for tests.
    """
    from spb.backends.matplotlib import MB
    global TWO_D_B, THREE_D_B
    TWO_D_B = MB
    THREE_D_B = MB

####New API for plotting module ####

# TODO: Add color arrays for plots.
# TODO: Add more plotting options for 3d plots.
# TODO: Adaptive sampling for 3D plots.

def plot(*args, show=True, **kwargs):
    """Plots a function of a single variable as a curve.

    Parameters
    ==========

    args :
        The first argument is the expression representing the function
        of single variable to be plotted.

        The next argument is a 3-tuple denoting the range of the free
        variable. e.g. ``(x, 0, 5)``

        The last optional argument is a string denoting the label of the
        expression to be visualized on the legend. If not provided, the label
        will be the string representation of the expression.

        Typical usage examples are in the followings:

        - Plotting a single expression with a single range.
            ``plot(expr, range, **kwargs)``
        - Plotting a single expression with the default range (-10, 10).
            ``plot(expr, **kwargs)``
        - Plotting multiple expressions with a single range.
            ``plot(expr1, expr2, ..., range, **kwargs)``
        - Plotting multiple expressions with multiple ranges.
            ``plot((expr1, range1), (expr2, range2), ..., **kwargs)``
        - Plotting multiple expressions with multiple ranges and custom labels.
            ``plot((expr1, range1, label1), (expr2, range2, label2), ..., legend=True, **kwargs)``

        It is best practice to specify range explicitly because default
        range may change in the future if a more advanced default range
        detection algorithm is implemented.

    show : bool, optional
        The default value is set to ``True``. Set show to ``False`` and
        the function will not display the plot. The returned instance of
        the ``Plot`` class can then be used to save or display the plot
        by calling the ``save()`` and ``show()`` methods respectively.

    line_color : string, or float, or function, optional
        Specifies the color for the plot.
        See ``Plot`` to see how to set color for the plots.
        Note that by setting ``line_color``, it would be applied simultaneously
        to all the series.

    title : str, optional
        Title of the plot. It is set to the latex representation of
        the expression, if the plot has only one expression.

    xlabel : str, optional
        Label for the x-axis.

    ylabel : str, optional
        Label for the y-axis.

    xscale : 'linear' or 'log', optional
        Sets the scaling of the x-axis.

    yscale : 'linear' or 'log', optional
        Sets the scaling of the y-axis.

    axis_center : (float, float), optional
        Tuple of two floats denoting the coordinates of the center or
        {'center', 'auto'}

    xlim : (float, float), optional
        Denotes the x-axis limits, ``(min, max)```.

    ylim : (float, float), optional
        Denotes the y-axis limits, ``(min, max)```.

    annotations : list, optional
        A list of dictionaries specifying the type of annotation
        required. The keys in the dictionary should be equivalent
        to the arguments of the matplotlib's annotate() function.

    markers : list, optional
        A list of dictionaries specifying the type the markers required.
        The keys in the dictionary should be equivalent to the arguments
        of the matplotlib's plot() function along with the marker
        related keyworded arguments.

    rectangles : list, optional
        A list of dictionaries specifying the dimensions of the
        rectangles to be plotted. The keys in the dictionary should be
        equivalent to the arguments of the matplotlib's
        patches.Rectangle class.

    fill : dict, optional
        A dictionary specifying the type of color filling required in
        the plot. The keys in the dictionary should be equivalent to the
        arguments of the matplotlib's fill_between() function.

    adaptive : bool, optional
        The default value is set to ``True``. Set adaptive to ``False``
        and specify ``n`` if uniform sampling is required.

        The plotting uses an adaptive algorithm which samples
        recursively to accurately plot. The adaptive algorithm uses a
        random point near the midpoint of two points that has to be
        further sampled. Hence the same plots can appear slightly
        different.

    depth : int, optional
        Recursion depth of the adaptive algorithm. A depth of value
        ``n`` samples a maximum of `2^{n}` points.

        If the ``adaptive`` flag is set to ``False``, this will be
        ignored.

    n : int, optional
        Used when the ``adaptive`` is set to ``False``. The function
        is uniformly sampled at ``n`` number of points.

        If the ``adaptive`` flag is set to ``True``, this will be
        ignored.

    size : (float, float), optional
        A tuple in the form (width, height) in inches to specify the size of
        the overall figure. The default value is set to ``None``, meaning
        the size will be set by the default backend.

    Examples
    ========

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> from sympy import symbols
       >>> from sympy.plotting import plot
       >>> x = symbols('x')

    Single Plot

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot(x**2, (x, -5, 5))
       Plot object containing:
       [0]: cartesian line: x**2 for x over (-5.0, 5.0)

    Multiple plots with single range.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot(x, x**2, x**3, (x, -5, 5))
       Plot object containing:
       [0]: cartesian line: x for x over (-5.0, 5.0)
       [1]: cartesian line: x**2 for x over (-5.0, 5.0)
       [2]: cartesian line: x**3 for x over (-5.0, 5.0)

    Multiple plots with different ranges and custom labels.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot((x**2, (x, -6, 6), "$f_{1}$"), (x, (x, -5, 5), "f2"), legend=True)
       Plot object containing:
       [0]: cartesian line: x**2 for x over (-6.0, 6.0)
       [1]: cartesian line: x for x over (-5.0, 5.0)

    No adaptive sampling.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot(x**2, adaptive=False, n=400)
       Plot object containing:
       [0]: cartesian line: x**2 for x over (-10.0, 10.0)

    See Also
    ========

    Plot, LineOver1DRangeSeries

    """
    args = _plot_sympify(args)
    free = set()
    for a in args:
        if isinstance(a, Expr):
            free |= a.free_symbols
            if len(free) > 1:
                raise ValueError(
                    'The same variable should be used in all '
                    'univariate expressions being plotted.')
    x = free.pop() if free else Symbol('x')
    kwargs.setdefault('backend', TWO_D_B)
    kwargs.setdefault('xlabel', x.name)
    kwargs.setdefault('ylabel', 'f(%s)' % x.name)
    kwargs = _set_discretization_points(kwargs, LineOver1DRangeSeries)
    series = []
    plot_expr = _check_arguments(args, 1, 1)
    series = [LineOver1DRangeSeries(*arg, **kwargs) for arg in plot_expr]

    plots = Plot(*series, **kwargs)
    if show:
        plots.show()
    return plots


def plot_parametric(*args, show=True, **kwargs):
    """
    Plots a 2D parametric curve.

    Parameters
    ==========

    args
        Common specifications are:

        - Plotting a single parametric curve with a range
            ``plot_parametric(expr_x, expr_y, range)``
        - Plotting multiple parametric curves with the same range
            ``plot_parametric((expr_x, expr_y), ..., range)``
        - Plotting multiple parametric curves with different ranges
            ``plot_parametric((expr_x, expr_y, range), ...)``
        - Plotting multiple parametric curves with different ranges and
            custom labels
            ``plot_parametric((expr_x, expr_y, range, label), ...)``

        ``expr_x`` is the expression representing $x$ component of the
        parametric function.

        ``expr_y`` is the expression representing $y$ component of the
        parametric function.

        ``range`` is a 3-tuple denoting the parameter symbol, start and
        stop. For example, ``(u, 0, 5)``. If the range is not specified, then
        a default range of (-10, 10) is used.

        However, if the arguments are specified as
        ``(expr_x, expr_y, range), ...``, you must specify the ranges
        for each expressions manually.

        Default range may change in the future if a more advanced
        algorithm is implemented.

        ``label`` : An optional string denoting the label of the expression
        to be visualized on the legend. If not provided, the label will be the
        string representation of the expression.

    adaptive : bool, optional
        Specifies whether to use the adaptive sampling or not.

        The default value is set to ``True``. Set adaptive to ``False``
        and specify ``n`` if uniform sampling is required.

    depth :  int, optional
        The recursion depth of the adaptive algorithm. A depth of
        value $n$ samples a maximum of $2^n$ points.

    n : int, optional
        Used when the ``adaptive`` flag is set to ``False``.

        Specifies the number of the points used for the uniform
        sampling.

    line_color : string, or float, or function, optional
        Specifies the color for the plot.
        See ``Plot`` to see how to set color for the plots.
        Note that by setting ``line_color``, it would be applied simultaneously
        to all the series.

    xlabel : str, optional
        Label for the x-axis.

    ylabel : str, optional
        Label for the y-axis.

    xscale : 'linear' or 'log', optional
        Sets the scaling of the x-axis.

    yscale : 'linear' or 'log', optional
        Sets the scaling of the y-axis.

    axis_center : (float, float), optional
        Tuple of two floats denoting the coordinates of the center or
        {'center', 'auto'}

    xlim : (float, float), optional
        Denotes the x-axis limits, ``(min, max)```.

    ylim : (float, float), optional
        Denotes the y-axis limits, ``(min, max)```.

    size : (float, float), optional
        A tuple in the form (width, height) in inches to specify the size of
        the overall figure. The default value is set to ``None``, meaning
        the size will be set by the default backend.

    Examples
    ========

    .. plot::
       :context: reset
       :format: doctest
       :include-source: True

       >>> from sympy import symbols, cos, sin
       >>> from sympy.plotting import plot_parametric
       >>> u = symbols('u')

    A parametric plot with a single expression:

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot_parametric((cos(u), sin(u)), (u, -5, 5))
       Plot object containing:
       [0]: parametric cartesian line: (cos(u), sin(u)) for u over (-5.0, 5.0)

    A parametric plot with multiple expressions with the same range:

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot_parametric((cos(u), sin(u)), (u, cos(u)), (u, -10, 10))
       Plot object containing:
       [0]: parametric cartesian line: (cos(u), sin(u)) for u over (-10.0, 10.0)
       [1]: parametric cartesian line: (u, cos(u)) for u over (-10.0, 10.0)

    A parametric plot with multiple expressions with different ranges and
    custom labels for each curve:

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot_parametric((cos(u), sin(u), (u, -5, 5), "a"),
       ...     (cos(u), u, "b"))
       Plot object containing:
       [0]: parametric cartesian line: (cos(u), sin(u)) for u over (-5.0, 5.0)
       [1]: parametric cartesian line: (cos(u), u) for u over (-10.0, 10.0)

    Notes
    =====

    The plotting uses an adaptive algorithm which samples recursively to
    accurately plot the curve. The adaptive algorithm uses a random point
    near the midpoint of two points that has to be further sampled.
    Hence, repeating the same plot command can give slightly different
    results because of the random sampling.

    If there are multiple plots, then the same optional arguments are
    applied to all the plots drawn in the same canvas. If you want to
    set these options separately, you can index the returned ``Plot``
    object and set it.

    For example, when you specify ``line_color`` once, it would be
    applied simultaneously to both series.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

        >>> from sympy import pi
        >>> expr1 = (u, cos(2*pi*u)/2 + 1/2)
        >>> expr2 = (u, sin(2*pi*u)/2 + 1/2)
        >>> p = plot_parametric(expr1, expr2, (u, 0, 1), line_color='blue')

    If you want to specify the line color for the specific series, you
    should index each item and apply the property manually.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

        >>> p[0].line_color = 'red'
        >>> p.show()

    See Also
    ========

    Plot, Parametric2DLineSeries
    """
    args = _plot_sympify(args)
    series = []
    kwargs.setdefault('backend', TWO_D_B)
    kwargs = _set_discretization_points(kwargs, Parametric2DLineSeries)
    plot_expr = _check_arguments(args, 2, 1)
    series = [Parametric2DLineSeries(*arg, **kwargs) for arg in plot_expr]
    plots = Plot(*series, **kwargs)
    if show:
        plots.show()
    return plots


def plot3d_parametric_line(*args, show=True, **kwargs):
    """
    Plots a 3D parametric line plot.

    Usage
    =====

    Single plot:

    ``plot3d_parametric_line(expr_x, expr_y, expr_z, range, label, **kwargs)``

    If the range is not specified, then a default range of (-10, 10) is used.

    Multiple plots.

    ``plot3d_parametric_line((expr_x, expr_y, expr_z, range, label), ..., **kwargs)``

    Ranges have to be specified for every expression.

    Default range may change in the future if a more advanced default range
    detection algorithm is implemented.

    Arguments
    =========

    ``expr_x`` : Expression representing the function along x.

    ``expr_y`` : Expression representing the function along y.

    ``expr_z`` : Expression representing the function along z.

    ``range``: ``(u, 0, 5)``, A 3-tuple denoting the range of the parameter
    variable.

    ``label`` : An optional string denoting the label of the expression
        to be visualized on the legend. If not provided, the label will be the
        string representation of the expression.

    Keyword Arguments
    =================

    Arguments for ``Parametric3DLineSeries`` class.

    ``n``: The range is uniformly sampled at ``n`` number of points.

    Aesthetics:

    ``line_color``: string, or float, or function, optional
        Specifies the color for the plot.
        See ``Plot`` to see how to set color for the plots.
        Note that by setting ``line_color``, it would be applied simultaneously
        to all the series.

    If there are multiple plots, then the same series arguments are applied to
    all the plots. If you want to set these options separately, you can index
    the returned ``Plot`` object and set it.

    Arguments for ``Plot`` class.

    ``title`` : str. Title of the plot.

    ``size`` : (float, float), optional
        A tuple in the form (width, height) in inches to specify the size of
        the overall figure. The default value is set to ``None``, meaning
        the size will be set by the default backend.

    Examples
    ========

    .. plot::
       :context: reset
       :format: doctest
       :include-source: True

       >>> from sympy import symbols, cos, sin
       >>> from sympy.plotting import plot3d_parametric_line
       >>> u = symbols('u')

    Single plot.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot3d_parametric_line(cos(u), sin(u), u, (u, -5, 5))
       Plot object containing:
       [0]: 3D parametric cartesian line: (cos(u), sin(u), u) for u over (-5.0, 5.0)


    Multiple plots with different ranges and custom labels.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot3d_parametric_line((cos(u), sin(u), u, (u, -5, 5), "a"),
       ...     (sin(u), u**2, u, (u, -3, 3), "b"), legend=True)
       Plot object containing:
       [0]: 3D parametric cartesian line: (cos(u), sin(u), u) for u over (-5.0, 5.0)
       [1]: 3D parametric cartesian line: (sin(u), u**2, u) for u over (-3.0, 3.0)


    See Also
    ========

    Plot, Parametric3DLineSeries

    """
    args = _plot_sympify(args)
    kwargs.setdefault('backend', THREE_D_B)
    kwargs = _set_discretization_points(kwargs, Parametric3DLineSeries)
    series = []
    plot_expr = _check_arguments(args, 3, 1)
    series = [Parametric3DLineSeries(*arg, **kwargs) for arg in plot_expr]
    kwargs.setdefault("xlabel", "x")
    kwargs.setdefault("ylabel", "y")
    kwargs.setdefault("zlabel", "z")
    plots = Plot(*series, **kwargs)
    if show:
        plots.show()
    return plots


def plot3d(*args, show=True, **kwargs):
    """
    Plots a 3D surface plot.

    Usage
    =====

    Single plot

    ``plot3d(expr, range_x, range_y, **kwargs)``

    If the ranges are not specified, then a default range of (-10, 10) is used.

    Multiple plot with the same range.

    ``plot3d(expr1, expr2, range_x, range_y, **kwargs)``

    If the ranges are not specified, then a default range of (-10, 10) is used.

    Multiple plots with different ranges.

    ``plot3d((expr1, range_x, range_y), (expr2, range_x, range_y), ..., **kwargs)``

    Ranges have to be specified for every expression.

    Default range may change in the future if a more advanced default range
    detection algorithm is implemented.

    Arguments
    =========

    ``expr`` : Expression representing the function along x.

    ``range_x``: (x, 0, 5), A 3-tuple denoting the range of the x
    variable.

    ``range_y``: (y, 0, 5), A 3-tuple denoting the range of the y
     variable.

    Keyword Arguments
    =================

    Arguments for ``SurfaceOver2DRangeSeries`` class:

    ``n1``: int. The x range is sampled uniformly at ``n1`` of points.

    ``n2``: int. The y range is sampled uniformly at ``n2`` of points.

    ``n``: int. The x and y ranges are sampled uniformly at ``n`` of points.
    It overrides ``n1`` and ``n2``.

    Aesthetics:

    ``surface_color``: Function which returns a float. Specifies the color for
    the surface of the plot. See ``sympy.plotting.Plot`` for more details.

    If there are multiple plots, then the same series arguments are applied to
    all the plots. If you want to set these options separately, you can index
    the returned ``Plot`` object and set it.

    Arguments for ``Plot`` class:

    ``title`` : str. Title of the plot.
    ``size`` : (float, float), optional
    A tuple in the form (width, height) in inches to specify the size of the
    overall figure. The default value is set to ``None``, meaning the size will
    be set by the default backend.

    Examples
    ========

    .. plot::
       :context: reset
       :format: doctest
       :include-source: True

       >>> from sympy import symbols
       >>> from sympy.plotting import plot3d
       >>> x, y = symbols('x y')

    Single plot

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot3d(x*y, (x, -5, 5), (y, -5, 5))
       Plot object containing:
       [0]: cartesian surface: x*y for x over (-5.0, 5.0) and y over (-5.0, 5.0)


    Multiple plots with same range

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot3d(x*y, -x*y, (x, -5, 5), (y, -5, 5))
       Plot object containing:
       [0]: cartesian surface: x*y for x over (-5.0, 5.0) and y over (-5.0, 5.0)
       [1]: cartesian surface: -x*y for x over (-5.0, 5.0) and y over (-5.0, 5.0)


    Multiple plots with different ranges.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot3d((x**2 + y**2, (x, -5, 5), (y, -5, 5)),
       ...     (x*y, (x, -3, 3), (y, -3, 3)))
       Plot object containing:
       [0]: cartesian surface: x**2 + y**2 for x over (-5.0, 5.0) and y over (-5.0, 5.0)
       [1]: cartesian surface: x*y for x over (-3.0, 3.0) and y over (-3.0, 3.0)


    See Also
    ========

    Plot, SurfaceOver2DRangeSeries

    """

    args = _plot_sympify(args)
    kwargs.setdefault('backend', THREE_D_B)
    kwargs = _set_discretization_points(kwargs, SurfaceOver2DRangeSeries)
    series = []
    plot_expr = _check_arguments(args, 1, 2)
    series = [SurfaceOver2DRangeSeries(*arg, **kwargs) for arg in plot_expr]
    xlabel = series[0].var_x.name
    ylabel = series[0].var_y.name
    kwargs.setdefault("xlabel", xlabel)
    kwargs.setdefault("ylabel", ylabel)
    kwargs.setdefault("zlabel", "f(%s, %s)" % (xlabel, ylabel))
    plots = Plot(*series, **kwargs)
    if show:
        plots.show()
    return plots


def plot3d_parametric_surface(*args, show=True, **kwargs):
    """
    Plots a 3D parametric surface plot.

    Explanation
    ===========

    Single plot.

    ``plot3d_parametric_surface(expr_x, expr_y, expr_z, range_u, range_v, **kwargs)``

    If the ranges is not specified, then a default range of (-10, 10) is used.

    Multiple plots.

    ``plot3d_parametric_surface((expr_x, expr_y, expr_z, range_u, range_v), ..., **kwargs)``

    Ranges have to be specified for every expression.

    Default range may change in the future if a more advanced default range
    detection algorithm is implemented.

    Arguments
    =========

    ``expr_x``: Expression representing the function along ``x``.

    ``expr_y``: Expression representing the function along ``y``.

    ``expr_z``: Expression representing the function along ``z``.

    ``range_u``: ``(u, 0, 5)``,  A 3-tuple denoting the range of the ``u``
    variable.

    ``range_v``: ``(v, 0, 5)``,  A 3-tuple denoting the range of the v
    variable.

    Keyword Arguments
    =================

    Arguments for ``ParametricSurfaceSeries`` class:

    ``n1``: int. The ``u`` range is sampled uniformly at ``n1`` of points

    ``n2``: int. The ``v`` range is sampled uniformly at ``n2`` of points

    ``n``: int. The u and v ranges are sampled uniformly at ``n`` of points.
    It overrides ``n1`` and ``n2``.

    Aesthetics:

    ``surface_color``: Function which returns a float. Specifies the color for
    the surface of the plot. See ``sympy.plotting.Plot`` for more details.

    If there are multiple plots, then the same series arguments are applied for
    all the plots. If you want to set these options separately, you can index
    the returned ``Plot`` object and set it.


    Arguments for ``Plot`` class:

    ``title`` : str. Title of the plot.
    ``size`` : (float, float), optional
    A tuple in the form (width, height) in inches to specify the size of the
    overall figure. The default value is set to ``None``, meaning the size will
    be set by the default backend.

    Examples
    ========

    .. plot::
       :context: reset
       :format: doctest
       :include-source: True

       >>> from sympy import symbols, cos, sin
       >>> from sympy.plotting import plot3d_parametric_surface
       >>> u, v = symbols('u v')

    Single plot.

    .. plot::
       :context: close-figs
       :format: doctest
       :include-source: True

       >>> plot3d_parametric_surface(cos(u + v), sin(u - v), u - v,
       ...     (u, -5, 5), (v, -5, 5))
       Plot object containing:
       [0]: parametric cartesian surface: (cos(u + v), sin(u - v), u - v) for u over (-5.0, 5.0) and v over (-5.0, 5.0)


    See Also
    ========

    Plot, ParametricSurfaceSeries

    """

    args = _plot_sympify(args)
    kwargs.setdefault('backend', THREE_D_B)
    kwargs = _set_discretization_points(kwargs, ParametricSurfaceSeries)
    plot_expr = _check_arguments(args, 3, 2)
    kwargs.setdefault("xlabel", "x")
    kwargs.setdefault("ylabel", "y")
    kwargs.setdefault("zlabel", "z")
    series = [ParametricSurfaceSeries(*arg, **kwargs) for arg in plot_expr]
    plots = Plot(*series, **kwargs)
    if show:
        plots.show()
    return plots

def plot_contour(*args, show=True, **kwargs):
    """
    Draws contour plot of a function

    Usage
    =====

    Single plot

    ``plot_contour(expr, range_x, range_y, **kwargs)``

    If the ranges are not specified, then a default range of (-10, 10) is used.

    Multiple plot with the same range.

    ``plot_contour(expr1, expr2, range_x, range_y, **kwargs)``

    If the ranges are not specified, then a default range of (-10, 10) is used.

    Multiple plots with different ranges.

    ``plot_contour((expr1, range_x, range_y), (expr2, range_x, range_y), ..., **kwargs)``

    Ranges have to be specified for every expression.

    Default range may change in the future if a more advanced default range
    detection algorithm is implemented.

    Arguments
    =========

    ``expr`` : Expression representing the function along x.

    ``range_x``: (x, 0, 5), A 3-tuple denoting the range of the x
    variable.

    ``range_y``: (y, 0, 5), A 3-tuple denoting the range of the y
     variable.

    Keyword Arguments
    =================

    Arguments for ``ContourSeries`` class:

    ``n1``: int. The x range is sampled uniformly at ``n1`` of points.

    ``n2``: int. The y range is sampled uniformly at ``n2`` of points.

    ``n``: int. The x and y ranges are sampled uniformly at ``n`` of points.
    It overrides ``n1`` and ``n2``.

    Aesthetics:

    ``surface_color``: Function which returns a float. Specifies the color for
    the surface of the plot. See ``sympy.plotting.Plot`` for more details.

    If there are multiple plots, then the same series arguments are applied to
    all the plots. If you want to set these options separately, you can index
    the returned ``Plot`` object and set it.

    Arguments for ``Plot`` class:

    ``title`` : str. Title of the plot.
    ``size`` : (float, float), optional
        A tuple in the form (width, height) in inches to specify the size of
        the overall figure. The default value is set to ``None``, meaning
        the size will be set by the default backend.

    See Also
    ========

    Plot, ContourSeries

    """

    args = _plot_sympify(args)
    kwargs.setdefault('backend', TWO_D_B)
    kwargs = _set_discretization_points(kwargs, ContourSeries)
    plot_expr = _check_arguments(args, 1, 2)
    series = [ContourSeries(*arg, **kwargs) for arg in plot_expr]
    xlabel = series[0].var_x.name
    ylabel = series[0].var_y.name
    kwargs.setdefault("xlabel", xlabel)
    kwargs.setdefault("ylabel", ylabel)
    plot_contours = Plot(*series, **kwargs)
    if show:
        plot_contours.show()
    return plot_contours


def _create_ranges(free_symbols, ranges, npar):
    """ This function does two things:
    1. Check if the number of free symbols is in agreement with the type of plot
        chosen. For example, plot() requires 1 free symbol; plot3d() requires 2
        free symbols.
    2. Sometime users create plots without providing ranges for the variables.
        Here we create the necessary ranges.

    free_symbols
        The free symbols contained in the expressions to be plotted

    ranges
        The limiting ranges provided by the user

    npar
        The number of free symbols required by the plot functions. For example,
        npar=1 for plot, npar=2 for plot3d, ...

    """

    get_default_range = lambda symbol: Tuple(symbol, -10, 10)

    if len(free_symbols) > npar:
        raise ValueError(
            "Too many free symbols.\n" +
            "Expected {} free symbols.\n".format(npar) +
            "Received {}: {}".format(len(free_symbols), free_symbols)
        )

    # TODO: should I keep it?
    if len(ranges) > npar:
        raise ValueError(
            "Too many ranges. Received %s, expected %s" % (len(ranges), npar))

    # free symbols in the ranges provided by the user
    rfs = set().union([r[0] for r in ranges])
    if len(rfs) != len(ranges):
        raise ValueError("Multiple ranges with the same symbol")

    if len(ranges) < npar:
        symbols = free_symbols.difference(rfs)
        if symbols != set():
            # add a range for each missing free symbols
            for s in symbols:
                ranges.append(get_default_range(s))
        # if there is still room, fill them with dummys
        for i in range(npar - len(ranges)):
            ranges.append(get_default_range(Dummy()))
    
    if len(free_symbols) == npar:
        # there could be times when this condition is not met, for example
        # plotting the function f(x, y) = x (which is a plane); in this case,
        # free_symbols = {x} whereas rfs = {x, y} (or x and Dummy)
        rfs = set().union([r[0] for r in ranges])
        if free_symbols.difference(rfs) != set():
            raise ValueError(
                "Incompatible free symbols of the expressions with the ranges.\n" +
                "Free symbols in the expressions: {}\n".format(free_symbols) +
                "Free symbols in the ranges: {}".format(rfs)
            )
    return ranges

def _check_arguments(args, nexpr, npar):
    """ Checks the arguments and converts into tuples of the
    form (exprs, ranges, name_expr).
    
    Parameters
    ==========

    args
        The arguments provided to the plot functions

    nexpr
        The number of sub-expression forming an expression to be plotted. For
        example:
        nexpr=1 for plot.
        nexpr=2 for plot_parametric: a curve is represented by a tuple of two
            elements.
        nexpr=1 for plot3d.
        nexpr=3 for plot3d_parametric_line: a curve is represented by a tuple
            of three elements.

    npar
        The number of free symbols required by the plot functions. For example,
        npar=1 for plot, npar=2 for plot3d, ...

    Examples
    ========

    .. plot::
       :context: reset
       :format: doctest
       :include-source: True

       >>> from sympy import cos, sin, symbols
       >>> from sympy.plotting.plot import _check_arguments
       >>> x = symbols('x')
       >>> _check_arguments([cos(x), sin(x)], 2, 1)
           [(cos(x), sin(x), (x, -10, 10), '(cos(x), sin(x))')]

       >>> _check_arguments([x, x**2], 1, 1)
           [(x, (x, -10, 10), 'x'), (x**2, (x, -10, 10), 'x**2')]
    """
    if not args:
        return []
    output = []

    from sympy.core.relational import Relational
    from sympy.logic.boolalg import BooleanFunction

    if all([isinstance(a, (Expr, Relational, BooleanFunction)) for a in args[:nexpr]]):
        # In this case, with a single plot command, we are plotting either:
        #   1. one expression
        #   2. multiple expressions over the same range

        res = [not (_is_range(a) or isinstance(a, str)) for a in args]
        exprs = [a for a, b in zip(args, res) if b]
        ranges = [r for r in args[nexpr:] if _is_range(r)]
        label = args[-1] if isinstance(args[-1], str) else ""

        if not all([_is_range(r) for r in ranges]):
            raise ValueError(
                        "Expressions must be followed by ranges. Received:\n"
                        "Expressions: %s\n"
                        "Others: %s" % (exprs, ranges))
        free_symbols = set().union(*[e.free_symbols for e in exprs])
        ranges = _create_ranges(free_symbols, ranges, npar)

        if nexpr > 1:
            # in case of plot_parametric or plot3d_parametric_line, there will
            # be 2 or 3 expressions defining a curve. Group them together.
            if len(exprs) == nexpr:
                exprs = (tuple(exprs),)
        for expr in exprs:
            # need this if-else to deal with both plot/plot3d and
            # plot_parametric/plot3d_parametric_line
            e = ((expr,) if isinstance(expr, (Expr, Relational, BooleanFunction)) 
                    else expr)
            current_label = (label if label else (str(expr)
                if isinstance(expr, (Expr, Relational, BooleanFunction))
                    else str(e)))
            output.append((*e, *ranges, current_label))


    else:
        # In this case, we are plotting multiple expressions, each one with its
        # range. Each "expression" to be plotted has the following form:
        # (expr, range, label) where label is optional

        # look for "global" range and label
        labels = [a for a in args if isinstance(a, str)]
        ranges = [a for a in args if _is_range(a)]
        n = len(ranges) + len(labels)
        new_args = args[:-n] if n > 0 else args

        # Each arg has the form (expr1, expr2, ..., range1 [optional], ...,
        #   label [optional])
        for arg in new_args:
            # look for "local" range and label. If there is not, use "global".
            l = [a for a in arg if isinstance(a, str)]
            if not l:
                l = labels
            r = [a for a in arg if _is_range(a)]
            if not r:
                r = ranges.copy()

            arg = arg[:nexpr]
            free_symbols = set().union(*[a.free_symbols for a in arg])
            if len(r) != npar:
                r = _create_ranges(free_symbols, r, npar)
            label = (str(arg[0]) if nexpr == 1 else str(arg)) if not l else l[0]
            output.append((*arg, *r, label))
    
    return output


def plot_implicit(*args, show=True, **kwargs):
    """Plot implicit equations / inequalities.

    plot_implicit, by default, uses interval arithmetic to plot functions. If
    the expression cannot be plotted using interval arithmetic, it defaults to
    a generating a contour using a mesh grid of fixed number of points. By
    setting `adaptive=False`, you can force plot_implicit to use the mesh
    grid. The mesh grid method can be effective when adaptive plotting using
    interval arithmetic fails to plot with small line width.

    Arguments
    =========
        expr : Expr, Relational, BooleanFunction
            The equation / inequality that is to be plotted.
        
        ranges : tuples
            Two tuple denoting the discretization domain, for example:
            `(x, -10, 10), (y, -10, 10)`
            If no range is given, then the free symbols in the expression will
            be assigned in the order they are sorted.
        
        label : str
            The name of the expression to be eventually shown on the legend.
            If none is provided, the string representation will be used.

    Keyword Arguments
    =================

        adaptive : Boolean
            The default value is set to False, meaning that the internal
            algorithm uses a mesh grid approach. In such case,
            Boolean combinations of expressions cannot be plotted.
            If set to True, the internal algorithm uses interval arithmetic.
            It switches to a fall back algorithm (meshgrid approach) if the
            expression cannot be plotted using interval arithmetic.
            Set to adaptive=False if you want to use a mesh grid. 

        depth : integer
            The depth of recursion for adaptive mesh grid. Default value is 0.
            Takes value in the range (0, 4).
            Think of the resulting plot as a picture composed by pixels. By
            increasing `depth` we are increasing the number of pixels, thus
            obtaining a more accurate plot.

        n : integer
            The number of discretization points when `adaptive=False`. 
            Default value is 300. The greater the value the more accurate the
            plot, but the more memory will be used.

        show : Boolean
            Default value is True. If set to False, the plot will not be shown.
            See ``Plot`` for further information.

        title : string
            The title for the plot.

        xlabel : string
            The label for the x-axis

        ylabel : string
            The label for the y-axis

    Examples
    ========

    Plot expressions:

    .. plot::
        :context: reset
        :format: doctest
        :include-source: True

        >>> from sympy import plot_implicit, symbols, Eq, And
        >>> x, y = symbols('x y')

    Without any ranges for the symbols in the expression:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p1 = plot_implicit(Eq(x**2 + y**2, 5))

    With the range for the symbols:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p2 = plot_implicit(
        ...     Eq(x**2 + y**2, 3), (x, -3, 3), (y, -3, 3))

    With depth of recursion as argument:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p3 = plot_implicit(
        ...     Eq(x**2 + y**2, 5), (x, -4, 4), (y, -4, 4), depth = 2)

    Using mesh grid and not using adaptive meshing:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p4 = plot_implicit(
        ...     Eq(x**2 + y**2, 5), (x, -5, 5), (y, -2, 2),
        ...     adaptive=False)

    Using mesh grid without using adaptive meshing with number of points
    specified:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p5 = plot_implicit(
        ...     Eq(x**2 + y**2, 5), (x, -5, 5), (y, -2, 2),
        ...     adaptive=False, n=400)

    Plotting regions:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p6 = plot_implicit(y > x**2)

    Plotting Using boolean conjunctions:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p7 = plot_implicit(And(y > x, y > -x))

    When plotting an expression with a single variable (y - 1, for example),
    specify the x or the y variable explicitly:

    .. plot::
        :context: close-figs
        :format: doctest
        :include-source: True

        >>> p8 = plot_implicit(y - 1)
        >>> p9 = plot_implicit(x - 1)
    """
    
    args = _plot_sympify(args)
    args = _check_arguments(args, 1, 2)
    
    n = kwargs.pop("n", 300)
    adaptive = kwargs.pop("adaptive", True)
    depth = kwargs.pop("depth", 0)

    series = []
    xmin, xmax, ymin, ymax = oo, -oo, oo, -oo
    for a in args:
        s = ImplicitSeries(*a, adaptive, depth, n)
        if s.start_x < xmin: xmin = s.start_x
        if s.end_x > xmax: xmax = s.end_x
        if s.start_y < ymin: ymin = s.start_y
        if s.end_y > ymax: ymax = s.end_y
        series.append(s)

    kwargs.setdefault('backend', TWO_D_B)
    kwargs.setdefault('xlim', (xmin, xmax))
    kwargs.setdefault('ylim', (ymin, ymax))
    kwargs.setdefault('xlabel', series[-1].var_x.name)
    kwargs.setdefault('ylabel', series[-1].var_y.name)
    p = Plot(*series, **kwargs)
    if show:
        p.show()
    return p
