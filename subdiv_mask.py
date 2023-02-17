#!/usr/bin/env python

import os
import sys
import subprocess as sp
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Tuple, List, Optional, Sequence
from loguru import logger

from chris_plugin import chris_plugin, PathMapper

__version__ = '1.0.0'

DISPLAY_TITLE = r"""
       _                  _         _ _                        _            
      | |                | |       | (_)                      (_)           
 _ __ | |______ ___ _   _| |__   __| |___   ________ _ __ ___  _ _ __   ___ 
| '_ \| |______/ __| | | | '_ \ / _` | \ \ / /______| '_ ` _ \| | '_ \ / __|
| |_) | |      \__ \ |_| | |_) | (_| | |\ V /       | | | | | | | | | | (__ 
| .__/|_|      |___/\__,_|_.__/ \__,_|_| \_/        |_| |_| |_|_|_| |_|\___|
| |                                                                         
|_|                                                                         
"""

parser = ArgumentParser(description='A ChRIS plugin wrapper around mincresample '
                                    'for increasing the resolution of mask images.',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-d', '--divisions', type=float, default=2.0,
                    help='number of cuts along voxel edge. Float values are accepted, mincresample '
                         'performs interpolation.')
parser.add_argument('-o', '--options', type=str, default='-tricubic',
                    help='Additional options to pass to mincresample as space-separated list, e.g.'
                         ' specify interpolation as -tricubic or -trilinear')
parser.add_argument('-n', '--no-binarize', dest='binarize', action='store_false',
                    help='Skip extra step minccalc -expr A[0]>0.5, '
                         'allowing for floating point values')

parser.add_argument('-t', '--threads', type=int, default=0,
                    help='number of threads to use (pass 0 to use number of visible CPU cores)')
parser.add_argument('--no-fail', dest='no_fail', action='store_true',
                    help='Exit normally even when failed to process a subject')
parser.add_argument('-p', '--pattern', default='**/*.mnc', type=str,
                    help='input file filter glob')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')


@chris_plugin(
    parser=parser,
    title='Subdivide Masks',
    category='MRI Processing',
    min_memory_limit='2Gi',
    min_cpu_limit='1000m',
    min_gpu_limit=0
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    print(DISPLAY_TITLE, file=sys.stderr, flush=True)

    def curried_resample(t: tuple[Path, Path]):
        resample(
            *t,
            divisions=options.divisions,
            binarize=options.binarize,
            verbose=False,
            options=ssv_str(options.options)
        )
        logger.info('{} -> {}', *t)

    suffix = __suffix(options.divisions, options.pattern)
    mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix=suffix)
    proc = len(os.sched_getaffinity(0)) if options.threads <= 0 else options.threads
    with ThreadPoolExecutor(max_workers=proc) as pool:
        results = pool.map(curried_resample, mapper)

    if not options.no_fail:
        for _ in results:
            pass


def __suffix(divisions: float, pattern: str) -> str:
    ext = pattern.split('.')[-1]
    if divisions - int(divisions) < 0.001:
        d = int(divisions)
    else:
        d = divisions
    return f'.subdiv.{d}.{ext}'


SPACES = ('xspace', 'yspace', 'zspace')


@dataclass(frozen=True)
class MincInfo:
    """
    Dimensional information of 3D volume. 3-tuples are always in the order of
    (xspace, yspace, zspace)
    """
    length: Tuple[int, int, int]
    step: Tuple[int, int, int]


@dataclass(frozen=True)
class MincFile:
    fname: str

    def dimlength(self, dim: str) -> int:
        cmd = ['mincinfo', '-dimlength', dim, self.fname]
        length = sp.check_output(cmd, text=True)
        return int(length)

    def step(self, dim: str) -> float:
        cmd = ['mincinfo', '-attvalue', f'{dim}:step', self.fname]
        step = sp.check_output(cmd, text=True)
        return float(step)

    def mincinfo(self) -> MincInfo:
        # noinspection PyTypeChecker
        return MincInfo(
            length=tuple(map(self.dimlength, SPACES)),
            step=tuple(map(self.step, SPACES))
        )


def resample(input_file: Union[str, os.PathLike], output_file: Union[str, os.PathLike], divisions: float,
             binarize: bool = True,
             verbose: bool = False, options: Optional[Sequence[str]] = None) -> None:
    """
    Wrapper for ``mincresample``.
    """
    info = MincFile(input_file).mincinfo()
    quiet_flag = [] if verbose else ['-quiet']
    cmd = [
        'mincresample',
        *quiet_flag,
        '-nelements',
        *(str(int(divisions * l)) for l in info.length),
        '-step',
        *(str(s / divisions) for s in info.step),
        *(options if options else []),
        input_file,
        output_file
    ]
    sp.run(cmd, check=True)

    if binarize:
        tmp = str(output_file) + '.binarized.mnc'
        cmd = ['minccalc', *quiet_flag, '-unsigned', '-byte', '-expression', 'A[0]>0.5', output_file, tmp]
        sp.run(cmd, check=True)
        os.rename(tmp, output_file)


def ssv_str(s: str) -> List[str]:
    """
    Parse a space-separated list of strings.
    """
    return s.strip().split()


if __name__ == '__main__':
    main()
