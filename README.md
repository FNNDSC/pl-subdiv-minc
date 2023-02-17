# Subdivide Masks

[![Version](https://img.shields.io/docker/v/fnndsc/pl-subdiv-minc?sort=semver)](https://hub.docker.com/r/fnndsc/pl-subdiv-minc)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-subdiv-minc)](https://github.com/FNNDSC/pl-subdiv-minc/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-subdiv-minc/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-subdiv-minc/actions/workflows/ci.yml)

![Screenshot of cube](examples/img/cube.png)
![Screenshot of ball](examples/img/ball.png)

`pl-subdiv-minc` is a [_ChRIS_](https://chrisproject.org/)
_ds_ plugin which wraps `mincresample`.
It increases the resolution of binary mask images
using trilinear interpolation.
This is useful for fetal brain MRI where the voxel sizes
are very large relative to the shape of the mask.

See also: https://github.com/FNNDSC/ep-subdivide-mnc-methods

## Installation

`pl-subdiv-minc` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

[![Get it from chrisstore.co](https://raw.githubusercontent.com/FNNDSC/ChRIS_store_ui/963938c241636e4c3dc4753ee1327f56cb82d8b5/src/assets/public/badges/light.svg)](https://chrisstore.co/plugin/pl-subdiv-minc)

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-subdiv-minc` as a container:

```shell
apptainer exec docker://fnndsc/pl-subdiv-minc subdiv_mask [--args values...] input/ output/
```

To print its available options, run:

```shell
apptainer exec docker://fnndsc/pl-subdiv-minc subdiv_mask --help
```

## Examples

Some example input MINC files can be found in the datalad repository here:
https://github.com/FNNDSC/example_shapes/tree/master/minc

```shell
apptainer exec docker://fnndsc/pl-subdiv-minc:latest subdiv_mask incoming/ outgoing/
```

### Get JSON Representation

Run [`chris_plugin_info`](https://github.com/FNNDSC/chris_plugin#usage)
to produce a JSON description of this plugin, which can be uploaded to a _ChRIS Store_.

```shell
docker run --rm localhost/fnndsc/pl-subdiv-minc:dev chris_plugin_info > chris_plugin_info.json
```

