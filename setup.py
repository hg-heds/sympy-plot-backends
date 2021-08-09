from setuptools import setup, find_packages
import os

# TODO:
# 1. can I remove msgpack as a dependency? It should be included with
#    K3D. If not, do a commit on K3D to fix the issue.
#    Once its time to remove it, also remove it from conda/meta.yaml

def readme():
    with open("README.md") as f:
        return f.read()

here = os.path.dirname(os.path.abspath(__file__))
version_ns = {}
with open(os.path.join(here, 'spb', '_version.py')) as f:
    exec (f.read(), {}, version_ns)

setup(
    name="sympy_plot_backends",
    version=version_ns["__version__"],
    description="Backends for plotting with SymPy",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    keywords="sympy plot plotting backend plotly bokeh mayavi k3d panel",
    url="https://github.com/Davide-sd/sympy-plot-backends",
    author="Davide Sandona",
    author_email="sandona.davide@gmail.com",
    license="BSD License",
    packages=find_packages(exclude=("tests", )),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "appdirs==1.4.4",
        "numpy==1.21.1",
        "scipy==1.7.1",  # helps when lambdifying expressions
        "sympy==1.8",
        "matplotlib==3.4.2",
        "mergedeep==1.3.4",
        "ipympl==0.7.0",
        "plotly>=4.14.3",
        "colorcet",
        "param==1.11.1",
        "panel==0.12.0",
        "holoviews==1.14.5",
        "bokeh==2.3.3",
        "ipyevents==2.0.1",
        "k3d==2.9.7",
        "vtk",  # needed for streamlines in k3d
        "msgpack", # in order to export K3D to html
    ],
)
