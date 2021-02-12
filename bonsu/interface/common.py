#############################################
##   Filename: common.py
##
##    Copyright (C) 2011 Marcus C. Newton
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
## Contact: Bonsu.Devel@gmail.com
#############################################
import wx
import os
import numpy
from wx.lib.embeddedimage import PyEmbeddedImage
from time import time
MAX_INT = 2**31 - 1
MIN_INT = -2**31
MAX_INT_16 = 2**15 - 1
MIN_INT_16 = -2**15
CNTR_CLIP = 0.999
FFTW_ESTIMATE = 1 << 6
FFTW_MEASURE = 0
FFTW_PATIENT = 1 << 5
FFTW_EXHAUSTIVE = 1 << 3
FFTW_TORECIP = 1
FFTW_TOREAL = -1
FFTW_PSLEEP = 0.1
#----------------------------------------------------------------------
maincollapse = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAAmJLR0QA/4ePzL8AAAAJcEhZ"
    "cwAACxMAAAsTAQCanBgAAAAHdElNRQfeBg0PMTvlwFMpAAACG0lEQVQoFQEQAu/9Af8AAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAivX6Cv8KffcAAAAAAAAAAAAAAgAA"
    "AAAAAAAAAAAAAAAA+gAZAPn2dwkAAAAAAAAAAAAAAf8AAAAAAI3//v77AP0AFwIkANYA3f77"
    "D5T0AAAAAAAABAAAAAAAAP0ANgL/AP8A/wDrACMA+QLa8WMSnfEAAAAABAAAAAAAAPoA/wDo"
    "AP4A/gD8APYAIwD3AtrtAAQAAAAABAAAAAAAAPoA/QAUAPsA/gDvAA0A3QDY6/xGAAAAAAAA"
    "BAAAAAAAAPz/twD+APsAGAEsANoA0uj8Q6jWAAAAAAAAAf8AAAAAAAAAAAAAAAAAY/UjCtTl"
    "/kOo2QAAAAAAAAAABAAAAAAAAAAAAAAAAAAA+QDUAP49qN8AAAAAAAAAAAAAAP8A/wD/AP8A"
    "/wD/AP8A/wBWCf8A/wD/AP8A/wD/AP8AAf8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYpBYZuTPgnEAAAAASUVORK5C"
    "YII=")
getmaincollapseData = maincollapse.GetData
getmaincollapseImage = maincollapse.GetImage
getmaincollapseBitmap = maincollapse.GetBitmap
#----------------------------------------------------------------------
mainexpand = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAAmJLR0QA/4ePzL8AAAAJcEhZ"
    "cwAACxMAAAsTAQCanBgAAAAHdElNRQfeBg0PMiKqhqgqAAACG0lEQVQoFQEQAu/9Af8AAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAB6/gQB"
    "BgAGAAMAcwEAAAAAAAAAAAAABAAAAAAAAAAAAAD5AEIAAwABAMv+AAAAAAAAAAAAAAAAAgAA"
    "AAAAAAAAAAD+AP8A6AD/APsAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAD7APsA/gD/AP0AAAAA"
    "AAAAAAAAAAAABAAAAAAAAFz1BwAhAf4A/gD/ABcChPUGAHYLAAAAAAAABAAAAABXCQMKIwAq"
    "AO8A/ADsACQAAwrnAAAAAAAAAAAAAgAAAACp9/4i1OXaAA0AAAAOANYA3wD/CgAAAAAAAAAA"
    "Af8AAAAAAAAAWCcEwDEYIwDdAOT+BgyJ9wAAAAAAAAAAAf8AAAAAAAAAAABYKgTAKBXj/gUP"
    "lPQAAAAAAAAAAAAAAf8AAAAAAAAAAAAAAFgwBswFE53xAAAAAAAAAAAAAAAAAf8AAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGiM1WQHuC8IAAAAASUVORK5C"
    "YII=")
getmainexpandData = mainexpand.GetData
getmainexpandImage = mainexpand.GetImage
getmainexpandBitmap = mainexpand.GetBitmap
#----------------------------------------------------------------------
mainhover = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAAmJLR0QA/4ePzL8AAAAJcEhZ"
    "cwAACxMAAAsTAQCanBgAAAAHdElNRQfeBg0PMwf4mU0sAAACG0lEQVQoFQEQAu/9Af8AAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAB6/gQB"
    "BgAGAAMAcwEAAAAAAAAAAAAAAgAAAAAAAAAAAAD5AAYAAAABAP7+AAAAAAAAAAAAAAAABAAA"
    "AAAAAAAAAAD+AAIAAAD7AAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAD7AP0AAAAAAAAAAAAA"
    "AAAAAAAAAAAAAf8AAAAAAFz1BwAJChcAAAAAAAIA//YGAHYLAAAAAAAABAAAAABXCQMKIwAA"
    "AP0AAAAAAP4AAwr6AAAAAAAAAAAAAgAAAACp9/4i1OUEAAAAAAAAAAAA9gD/CgAAAAAAAAAA"
    "AgAAAAAAAKjf/kPS6AoAAwAKAO7++wp99wAAAAAAAAAAAf8AAAAAAAAAAABYKgTAKBXj/gUP"
    "lPQAAAAAAAAAAAAAAf8AAAAAAAAAAAAAAFgwBswFE53xAAAAAAAAAAAAAAAAAf8AAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAvBwtGiqGJ+oAAAAASUVORK5C"
    "YII=")
getmainhoverData = mainhover.GetData
getmainhoverImage = mainhover.GetImage
getmainhoverBitmap = mainhover.GetBitmap
collapse = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QMBAywPNqBwggAAAU9JREFUOMvFU79LQmEU"
    "Pe8RhCKIlURWQyQuBUG2hTUIjTUF4R/Q2GpjQ9H/IERbq0FNzYEO0mAPwxSLLJLKwvC953vf"
    "d7/b0GKhgjh44E733MM994fGzBgEOgbE8AVGeiUPtjOmcMirFHuPL2N23x0IhzAd9qFlkrW3"
    "duXpxNHat3CYyDJJViQUhFCYmvPpkWgAt9cfKN89K0kt/0l2p9nVghSM1a2QrojBDLBivFUt"
    "RJYDcCypl8rFRmIlNXaW2210FBAOQRGj9mhCCgVFDCkY1rdAJBqA3ZzXS9WbenvdHwHXJpBk"
    "jIc8kO6vQP3Vhn9iFMXcF+6fcu9SORtdLbiC+OLUgGKCpBYmgzPa0noQhewnjFK2RsqNp/PJ"
    "Qtch/kdiJWWGZxe8RiXzwkzxdD5Z7OsOhLRgVDJQLGPn+f2HjiRm7hmbi0eeXnlt6N/4AxJs"
    "4oj1H51DAAAAAElFTkSuQmCC")
getcollapseData = collapse.GetData
getcollapseImage = collapse.GetImage
getcollapseBitmap = collapse.GetBitmap
#----------------------------------------------------------------------
expand = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QMBAy0Z22/0kgAAAVFJREFUOMvVk71LQmEY"
    "xc973/femzdBRIMcimpQ1DIhh6SlqbbCIWhpbW2vhqbALdpbXZrqDwgJ6QOMBoOgL4qyhL7B"
    "yw3vvc/b0pJoJU6d8Qw/OOd5DpNSoh0paFNtA0Qjc2F8hzSVM83DoeocQmVYzo2yPwNqjonJ"
    "uUFwwaBwhr3te2opAkkXRBKVaxPkSrg2tdaB437AqREcmyAlYP8A+BZhJrlmqsJAXyjGyJUg"
    "V0KSRKjfqyxNFUxV51jZTHc2BEwPrXq4ohnRnjjiY0E8P1hwbInHsoXwiB9CZUb5oto8wlZp"
    "0SLpDJxc7ZdPD1/gC+pgDPAFdJQKTzg/fgORNOoBrP4TM4lshCtafjia7o6k/Dg7esXtTYV0"
    "bnjXdyesXwFfkJhQ9Hy4N9V1V7kkoei+jYPZaqMSWbMtZBLZpMo9RcE7Arni/HuzK7D/P6ZP"
    "CTWCmkrllckAAAAASUVORK5CYII=")
getexpandData = expand.GetData
getexpandImage = expand.GetImage
getexpandBitmap = expand.GetBitmap
#----------------------------------------------------------------------
hover = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QMBAzIwVIdiYAAAASJJREFUOMtj/P//PwMl"
    "gImBQkCxASzYBPMd9v1jY2VmZONkZmBlZ2ZgYWVkqFlmwUi0C379+crAxsnMwMDAwMDIyMDw"
    "98//fyS54N//vwzMzBAL//7+R7oX/vz9wfCbgEYYYESOxlCDCV9ZWbgYOFn4uMREpBH+ZGZk"
    "YPjP8I2VnZmhYbUlN1YX+Ou2cTIzsXFpymozMDAwoLjg39//DKysTFy/f/7FHYgbL1d9//f/"
    "j9KVe8efMrFghu3nD78Z/v37z4U3FjZcqrj///9f5yu3T7zg4mVlYGVlYuDmY2V49/7tv79/"
    "f3G1b7H9jjcMYCBQr1OLhYn9gJqcieiTF3f/sTCx8889EfGFYCCiGWLAysx5hoWZQ3jZmbSP"
    "RMXC0MxMAL8DZraItd7/AAAAAElFTkSuQmCC")
gethoverData = hover.GetData
gethoverImage = hover.GetImage
gethoverBitmap = hover.GetBitmap
#----------------------------------------------------------------------
spinup = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAAmJLR0QA/4ePzL8AAAAJcEhZ"
    "cwAACxMAAAsTAQCanBgAAAAHdElNRQffAhUUKx6l6zsxAAAAuUlEQVQoz2P8z4AfMDFQqoAF"
    "lZvM//vtL5MVF3CYkMPD8k6NmWVXhBZWBeWcrB/VmHQYDEVZ9kaoYyho5mT9psykxfCeQZlB"
    "T4Jpb4QimgLGb4oMWgyfGBgYPjOoMehIM90L50RxJNu35wx/uZQZnjEIMlxguP+NiWHZdwYG"
    "BgZG5IBq/mvN9JxBkGHb/ylMWH3BzMDIwMTAysCKK6BYGRgZJBgYUQRRAoqJ6RTDL4ZfDOxI"
    "Yoy0jywAPNsnwBy7iO0AAAAASUVORK5CYII=")
getspinupBitmap = spinup.GetBitmap
#----------------------------------------------------------------------
spindown = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAAmJLR0QA/4ePzL8AAAAJcEhZ"
    "cwAACxMAAAsTAQCanBgAAAAHdElNRQffAhUULhLRKoNfAAAAxElEQVQoz2P8z4AfMDFQqoAF"
    "waz6x8LIxsDGwMxQzIhVwU8GJwZmBkaG0/9wWPGP4T/DC4b/DL9xueE3w2+Gfwz/Gf5ic0PM"
    "V3YGRcZ/DP8Y/jOIM7V8ZWMo40ZSEM7JzKXMoMXwnuEPwxsGFQZmrueoVqz8/k/pytNbDLwM"
    "DAx8DNcY7jP854IpYISFZIQ6ywFDCWWGuwxP/rHxdH7HUMDAEKHFckBD9PE/Vv4pXxCOZESO"
    "iwgDtjOswnM/IvuCkfaRBQAaIzVZHwYwzgAAAABJRU5ErkJggg==")
getspindownBitmap = spindown.GetBitmap
#----------------------------------------------------------------------
start = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAATdEVYdFRpdGxlAE9wdGljYWwgRHJpdmU+Z7oMAAAC20lEQVRIid2VTWgTQRTH/7Pd2e5m"
    "k0bbdK2SboiJFqFFxC8MxZOfLQgiqAcvXu1BCgpSkBQPYk+5CB4UQZGKn1ik0YrRVtFWJUKx"
    "aMVK0lr0oG1sTJrJbrLjwQ/QRNMWPeiDdxmG34/3eG+GcM7xN0P4q/T/QiD+fEAIkQDIAEwA"
    "Wc659UcFAORbt7v7sobRd6HzSgchJPFVNLdp4Jz/kA6Ho+pWJMzH344Zkd6e5OWr51v9fn81"
    "APnnuzPJggo8Ho8NAGq0hdRVWU3HxkePnTh5vDUei7fV19ffTqfTH2OxGJtzi3RdV7LZLPJ5"
    "C8lPU6h2adLCmkW18yqcp452HHk2NDTc3tTUNAjgfTgczs5a4PP5FMYYODgM00B6OoVcPgeP"
    "x1u+2LtkpWpTr3q9tT2vRmKhlpaWEU3T3gWDwdyMBW63+4vAsmCaBgzTgJkzMJH4AEVWyJrV"
    "66RUKtWsyA83JWvdZycnkmdCoVA8mUy+CwaDBRNXsAd+v19hjMHi1nd4WZkIKlIQQpBKf4Ji"
    "k4Utm5vLA4HGvdUL5ofnVzn3NTQ0rAFASgp0XVdYhsGyrB/glFJQUQKlFAQElmXB6/WJO7bv"
    "qsjlzDZBwPpoNFpVskW6riu99xg4t4rCqUghSTIEImA0Hsvf7YtMuypdpwOBxkFN0yZKCjRN"
    "kxljIEQogEtUQrkkYzKR4N3dXaZqt1/fvXPPNVVVBwE8B1CwjMU2WfwiIN/hEpVgU1QwxviF"
    "rs58JsMGmrduu+h2u58CeAogU4TzSwFljEEQBFBRgl11gHPgxs1w7vXrkdiGjZvPrVi+4gmA"
    "RwAmfwUuWQEVKexqBaLRJ7k7vZGpwNrGzoMHDj0A0A9grBT4twJBEDD88oV1+colo65u2bXD"
    "be13KKUDAIZQpM+zFZiatuBNf//DV637D9xwOp0DAB4DMGYD/hakyCu8FMAqAFMA7gNIzgX8"
    "O8EfjX//T/4M1NpX34EMRzwAAAAASUVORK5CYII=")
getstartBitmap = start.GetBitmap
#----------------------------------------------------------------------
pause = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAATdEVYdFRpdGxlAE9wdGljYWwgRHJpdmU+Z7oMAAAB0UlEQVRIie2VwYrUQBBAX3WnQzLo"
    "7K4wOYWQITkoeF8UBcEfUFD0jwTxqv7CgoJ+gqIMeBf0G3QVHGFxU5O0h0zWzBAlgntYsE5F"
    "vVCvujtJi/ee0wxzqt3/C8ZEMFQUkRCIAOmVPfBjnQ8y7301SjCdTs89e3HwUWDW6/D5zq17"
    "lwCevzz4IMgGu3v7/kXg6yhBnucTgdmN6zfx3tM0DW8Wr2bz+TwGEGR2Zf8aIoIxhreL17M8"
    "zyejBWmaTlRXNN5z+OUTuzt7qK5I03QCoLpCRFh+/8be7oUNNkpQFEWsqjRNjWpFXdeoKkVR"
    "xK1AERGccxgxG2zsCmJVpa5rKq2om1aQpummIHCIMRtslKAsy/hYj9rJV+2LoaqUZRkDHOsR"
    "xhicCzFrQce2Y/A7yLJsvYIV1gaICKpKlmVxx4yxBIHDGnvC/lrAehvMkEAMoQvx3v9RMLhF"
    "SZJEWvUO0li0UpIkiQC0Uqy1dH/iPhslAIJ2SsEFIWLaFXTPqyre+1+CHhsrcO0+G6bnd7Bi"
    "uyau1/Ak+mysoLHGLp88fTztClEULbvcWrt8+OjBNmuGGslvbrTLwFUg7A8KvFvn+1sTV8AC"
    "eD9W8M/i7F84Z1/wE6NH3sjOlcYjAAAAAElFTkSuQmCC")
getpauseBitmap = pause.GetBitmap
#----------------------------------------------------------------------
pause2 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH3wIWCyEKQBFMZQAAAaFJREFUSMftlU1O3EAQ"
    "Rl+5bTM9OCOBcAZxAiKRWyQH4DDJFnKcbNkmJ0BZReLnCgiJxSiJCG5XZdE9jgcGpVmwiWip"
    "Jateu7/6utplMTOecxQ883gR+Oco1wVFpAYmgIzCBtym57XMzO7yBCrfbL87vgTaUfj65svR"
    "G4Dt958uHrCvx/vATZaAa+ZToN3YfRuTM+P31VnrXu36tKStX+8DgkgRWXwnU2BzZ4oGwNDb"
    "BVJvgoYYByITrPuFbDSrLEegnO150x7MMA0IhmlPOdvzAKY9iEBRRqERy3TQejRg1oP1oH3K"
    "svVLB0ISkGKV5TsIyUEfr4mGkYOQHDgQWWFZ34Fr5h5N2YvEqT2umfuBSYGkuWRPEGijAwQR"
    "B1JgGnBN6wcmgrgKMwaWXwO/NYk3BcRVLM/d+a3JUAMpGBrxmOUIAGXMsoiTeM7L9aYhba5D"
    "fR6t5yMClWkXj6Gaxmy1A6jiht3K4jHLFVARt/h5fjIb2oerF397lVv8+P75PtOnCJw2B4cf"
    "gHoU64BvAM3B4cd7Gd8Bp2v72ssv8/8X+AMi1rb5DCHJhwAAAABJRU5ErkJggg==")
getpause2Bitmap = pause2.GetBitmap
#----------------------------------------------------------------------
stop = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAATdEVYdFRpdGxlAE9wdGljYWwgRHJpdmU+Z7oMAAABcklEQVRIie2VzYrVQBBGT1WnLrkj"
    "d3QGblZNICQbH0IQ3IsLwSdzfIYBFzJvMCC+gnuX/mwG3KSSbhdeBpUk5oKzGPDbNHTBORRN"
    "80nOmbuM3in9v2BNiqlLEXkwN1vIkHP+vkqw2+3Kt+8uPwrs15AzfHn54tVjYJ2gaZqtwP7p"
    "k2fknEkpkXL6eaYRRFBRRARV5f2H633TNNsp1qQgxngy+EDKma/fPuPe03uPDz0hFFhhmBlW"
    "bDh7dM7gAzHGkynW5CO3bbvt3UlpXISbGSpK707btpMbTApijFt3ZxzHRbgVhqji7sQY1wu6"
    "rrsVLMHNNuhB0HXdekFd1wfBsAgvCiNowN2p6/p4ASKL8I1tyDkfL6iqqvTeEZG/wgG8d6qq"
    "KqdYc7+1cHdUZBF+K3CfZc0JzN1RVU53Dwka0BAIGggh8GeHHAR21AZBw83Fm9enM/PfUpbl"
    "zRxLZhrtOVCvgf+ST8DVWsE/y/0vnPsv+AGwA6cccTFpJwAAAABJRU5ErkJggg==")
getstopBitmap = stop.GetBitmap
#----------------------------------------------------------------------
animate = PyEmbeddedImage(
    "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")
getanimateBitmap = animate.GetBitmap
#----------------------------------------------------------------------
ruler = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3wIWAAMO7JshvQAAAfRJREFUSMet1U+IjGEc"
    "B/DPzsj6M8hBu1KT1BRFSZQstWyWdVhJbSvKXdrk6OTKwYG7qE3aUBy8pVY5vDnIgdlia2gz"
    "yRtpqVE7aVuXh9597Ww7M/se5336/J53nt/v++S1+XT3DPQViqUXhWLpY61amcy+72gXxxN0"
    "YhZDSRw9Tq/JLQM+hZ0oY6y7Z+Bk2wVS+Bz6kzh6j6N4my2SawOvYS2ud/cM5JM4mkZ/tki+"
    "RXwFduM7RvCuVq1M1KqVmUKx9ADHcLFQLJU7WsB/YDPGMYg9eJ3E0Uxq7XZM4HO+SXwl9uED"
    "LmA/bmTwLjzFOgznmsC/hkO9izu4hD7cyuDPsRWDSRyN55aIr8IpnMVenE/i6CaG8bARvuig"
    "pfAv2BL6/TAKqCZxVF9s54tOcgpfjQPYiEe4msTRtczahrjQbo3wKrpwH73YFtpyyfh/X5DZ"
    "+YkAPsNP9CZxNNUMPm+SU/gnfMMo6mE6N+Bes/i/Ail8Da7gCH7jTBJHr3Ao/N4UDh2ZVOzE"
    "JhzHG9STOJptZefpQ74d4NP4FSJgKImjl80eaKO/aCRcFqMhIXfg8nLgkAs30BB2hY5Zn8TR"
    "3HLg89o05PdYyPP+JI6m28UXmoO/Rco4F3KmZXzBqEgVyYc5aBlf8EarVSuThWKpjIMYbgeH"
    "P8qi8JmnhdKJAAAAAElFTkSuQmCC")
getrulerBitmap = ruler.GetBitmap
#----------------------------------------------------------------------
vcut = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4AIJETU6pIF/iwAAAAxpVFh0Q29tbWVudAAA"
    "AAAAvK6ymQAAASBJREFUaN7t1jFKA0EUxvH/m92I2EgaD2BrYRGwsLERbKysFC/gVvZiF+8Q"
    "u6TxBrYWQiCCBBTPYCliI8LuzLOxUbfJDiGz5P2qgeHN8A3zZheMMcYYY4wxDUnsAhu7B5cC"
    "m0D4O+e9p39ecHZyVFeaASMRuY/ZP29c2TtcY3r7CXIsIlu1pyOKiHA6KGqXuCkGEyAqgGta"
    "2OWr8zMsI/YPsTfAtb0HXPJNtugAWZbNdf18rqfvHHcPj+xs7+G9/z2pwtX1MO0AToTx9JnJ"
    "08u/OVUIGtIOAFBWFWVFbQBF0++B1r9CFsACLEGAlZjvXArP6FhV3wA/2/+F5AR5TSCAXgCd"
    "2UpAFSHIx8LuXre3v97qHnhntcQYY4wxxpil9g1+XkFB2eEyYQAAAABJRU5ErkJggg==")
getvcutBitmap = vcut.GetBitmap
#----------------------------------------------------------------------
colorpick = PyEmbeddedImage(
    "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")
getcolorpickBitmap = colorpick.GetBitmap
#----------------------------------------------------------------------
slider = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QANABBAGCRCCOWAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3wIWDSgb/+6rbAAAAB1pVFh0Q29tbWVudAAA"
    "AAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAAcUlEQVRIx2NgGOqAkRhFJo4J/3HJndm/AK8Z"
    "LMS65NGtExhicmoWBPUx0TqImOgeB7VzX1BsaHOyBO442L6k4j81Hc5CbIQSC9AjnuZxwEKM"
    "KwZ1JBOdk3FlNEI5eehntFELRi0YAhYQXWVSs3yiKgAAI68a/EHvLuYAAAAASUVORK5CYII=")
getsliderBitmap = slider.GetBitmap
#----------------------------------------------------------------------
sphere = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3wIaESEtvnxgEAAAA0xJREFUSMftVb9LJEkY"
    "fdVdPTpMMwyaeLixwq0IJicYaSQichuo+B+YzF6gs8lufCPIeomXGJgYGAwGdxgLmvgDBV1Q"
    "WTbeGdue6aGnf1T/rKpLdoZV0T130/2g4Cu++t6rx6O+An7Gj8bx8fGjta2trW/2k8cKp6en"
    "yGazGBoaAgAcHBwMcM5fRFEE13U/z8/PfwKA7e1tGIaBpaWl5xG04+zs7JWmaWVFUfo451oQ"
    "BHAcJ7Esy2g2m2+LxeI/z1Kwv7+P8fFxnJycdGUymfe6rhd1XYemaVIIQXzfR7PZlKZpEsMw"
    "UK/X/7Ztu1Qul6PFxUVsbGzcwaOPMhPyPpfLFXt7e5HP56EoCpFSQtd1KIpCkiQBYwy2bRc5"
    "5wDwOk3TBzjq15vd3V1MTk5ib2/vla7rf/X09KBQKEhKKSGEgBACSikIIQiCAIwxyRgjjuP8"
    "Njg4+GFzc/Pj7Owsrq+vO5jK1wQzMzPttKyqKiilUFWVSCnv3ErTNFBKQSklqqpCVVUIIf4E"
    "gJ2dnTtnlfuSKpXKAOe8TwghOeeQUoIQAillJ+ecd5YQAlJKyTn/ZWpqauA+3gOCJEn64zjW"
    "oigiQRDA9/0OMCEEcRzDcRwwxhAEAaIoQhzHJEkSLU3T/vt4D0xmjIFSiu7ubmiaBkIIkiRB"
    "JpOBEAKe58GyLLRaLXie1yEKwxBRFOGbBJ7nVQEkqqpKACRNU3ieB0opOOcIwxC2bcOyLNi2"
    "jVarBdd1pe/7CWOs+r8e2urq6lWhUPg1n88jl8uhq6sLqqqCc44gCOC6LmzbhmmaME0ThmHg"
    "9vb2+ujo6OWTHqysrAAAXNd9V6/X282yVquhVquhWq3i5uamDYhGoyEty0Kz2QRj7B0AjIyM"
    "PK1gbW0Ny8vLKJVK65qmFbPZLCilUBQFaZoiiiL4vg/HcWDbNhqNBlqt1vr5+fkfY2NjODw8"
    "fNoD0zTbKkpCCKkoyusvZss0TUmSJPB9X7quS74YvR6G4RsAcBzn+cNubm7udynlipSyj3Ou"
    "RVGEMAwTz/NugiB4e3l5+e93jeuFhQUIIVCpVAAAExMTA5zz/jiOEYZh9eLi4hMAjI6OwvM8"
    "XF1dfd+HMz09/WhteHj454/84/EfcS/toXYUG+YAAAAASUVORK5CYII=")
getsphereBitmap = sphere.GetBitmap
#----------------------------------------------------------------------
sphere2 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwY"
    "AAAAB3RJTUUH3wIaEgIZIyddnQAAAzZJREFUSMftVU1IXUcU/s7ce98PlYZmZbAttBQXrQhC"
    "ieAiuLNFpFJsEEpXXbjRLjTtIlll0biJ3dhF3ZpiQSxtcRMKBelCLFJoF9qQbiua53vWvHfv"
    "/M+cLhIlKpqabPPBwBnOzPfNN4eZA7zA82Jtbe3U3Pz8/FP302mJ9fV1VKtVdHV1AQA+HP2u"
    "M0b/aggWzsp/7i5P3AeAhYUF7OzsYHJy8nwCB7j6yQ/DiSjdAqEdzJn3GtbkTqm9Ha0fXv/1"
    "l5s/nsvBysoK+vv78dHH35eTtHQ7y6rjWakNiUg5ciDvNLT6l6VskCx2oeTe18Y0r/3+2zdm"
    "bGwMc3NzR/jSU5WJbqdpdbxSvYhSqQ1EgpgjQmYBEMUY4J2CNa1x5ggAE977EzzJk5Pl5WUM"
    "DAxg+Oqd4az00leVygVUyi+zSFIiIhAJCJGCiOC9gveGnZNkTevyKxff/PPnu9/eGxkZwebm"
    "5iGneFJgaGjoILxFJEAiAUgQMx85lRDpwSCiBCQSMMcvAWBpaeno2uOW3hua7WSO7WDmA2Ii"
    "AjODmR/HAcwRMXoADDBzjOHS629c6TzOd0IgRtcRgsm8NxSchnfykJiIELyFNTm8U/BeI3iL"
    "EB3F6LIYfMdxvhNFdk6BRII0yaGTFCBCjB4iycDMcLaAVvswpgVnJZyT8E7De4MYHZ4q4J3c"
    "AuAEJQyAOAZYm0OIFMwR3mtY3YTW+7CmBWtacDZn77RzTm39r4fWd+WLjXLlwtulchuyrIok"
    "KYNIPBJwCtYWMKYJJRtQsoGi2IUq6ps723+8c2YNpqenH19TcUPJBlTRQJHvcpE/QJE/QN7a"
    "RlHUIGUdStah5B5rtQ+jH8I5dQMAenp6znYwMzODqakp9Lz76awQ6XiaVUCUHDoIwcA5BWvy"
    "QxfW5rP12l+f9fX1YXV19ewa1Go1AIC1+TUADI0JITIQEccYKEYP5wp2VpIxTTgnZ73TnwNA"
    "s9k8/2f3Vuf7HzB4mjm2M8csBIvgtbNWbgdvru81/v7pmb7r0dFRxBixuLgIAOh47XInM3c8"
    "EjBb9d179wGgt7cXeZ5jY2Pj2RrO4ODgqbnu7u4XHfn58R8oZOdvSZVHKAAAAABJRU5ErkJg"
    "gg==")
getsphere2Bitmap = sphere2.GetBitmap
#----------------------------------------------------------------------
spectrum = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAIAAABvFaqvAAAACXBIWXMAABPXAAAT1wFjcfKR"
    "AAAAB3RJTUUH3wIaESoUAo0x0wAAAIdJREFUOMut0zkKg0AAQNEZN4hhoijDVBJSprPO/Zuk"
    "t3EJAQuJgp2R4DJe4v8DvO7LQueCyLPzjYHkfGWgMdAM1KYxBCWKgT5RxEC1gqCGgvrkzECr"
    "cRhoMy4D+emXgdTpxUCX8MlAmV8y0EP8IMiZGOi+/BlIDBaC+p2B9k5A0NuDpq2Y1w6tSx+G"
    "Ta9ccQAAAABJRU5ErkJggg==")
getspectrumBitmap = spectrum.GetBitmap
start48 = PyEmbeddedImage(
    "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")
getstart48Bitmap = start48.GetBitmap
#----------------------------------------------------------------------
pause48 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAATdEVYdFRpdGxlAE9wdGljYWwgRHJpdmU+Z7oMAAAC7klEQVRoge2YT2sTQRjGn51pMEgS"
    "QUVJCh6SkNzWWz9DwaKePagIfgzPgkjIx+jRUw3VVs9+g6VQNGAOgjQVD/nTmfGQnc3uJDM7"
    "u1myFvaB0LAzD/29ed95Z3YcIQSus0jeAJuqCCBvFQHkrSKAvFUEkLd2kkx2HOcGgDIAapjG"
    "AEyEENOsvEYm26OED1ABcAVgDmCd0QFQwuKH+StBNvHGKUkGygCuPn8ZHHLO93WTCKGDVy9e"
    "PxsOh2UA07D30+nHQyGE1rtD6eDl8xWvWUIIqw+A2wBuHp8cCZOOT46E53kPXde9l4U37pNo"
    "Dbiu68jvFxe/wTgD5wyMcXDOsNt4AABot9v7vV7vFMCvdd7zH2cghIAQCur/rd/fDbz9fv9r"
    "2GtSoi5UrVYJYxwAVuAZZ4vnjIMQUmq1Wnd0XhWeEBLxNpvNu7ZMidso90FV+PBzAHAcx9F5"
    "VXhCaKw3wwD8DCjwzH8ux01eFZ76GTB5swuASdAofJABZgggKCGqlBGJ9WYWQFDrCjxjLDJu"
    "8qrwsoRM3swC4DycgSV8khJS4UkeJbQKLyLjJq8KTymN9eqUooRCGQjBB63Q8CsyHm2jEt7G"
    "q1OKDMh+H4UPWiHT17EcU+FtvDqlb6MKvE0r5KEMhOG3ugaWaRZQd9TouN6rwlMLr06pF7Hu"
    "OGC3D6zCx3l1Sn2UiDsOxHnD8PKdxOTVKXUJ6Y4Dtl1IhY/z6rRBCanHgfhevtwHovBBBrZb"
    "Qpo1YFFCgAqfQwnp1oBNCanwsoq2WkLaI7FFCQEq/FZLKOZIbLGRqfAyA2k2skTvxIt/sqhT"
    "+Q6rGzeNyWCTeHVKEgAbj8elSqX27d37t3u6SY1648z/eql6a9VbVl7G2KVujqokAUym02nt"
    "8cHTN/V6fQ/mGzZMJpPvqvfg0RMr73w+P7eFsl4D/k3ZH8/zRlh/syY1ms1mH7rd7iitt9Pp"
    "/LTlsr5a/F917W+niwDyVhFA3ioCyFtFAHnrHw8HyB3QuCDbAAAAAElFTkSuQmCC")
getpause48Bitmap = pause48.GetBitmap
#----------------------------------------------------------------------
pause482 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH3wIWCyEolXENgQAAAphJREFUaN7tmL1u1EAU"
    "hc8dr4WTwCJwGogU8Qo0UXgDk0eggwrxDjR0CS8ShYYyBUKkpUGiRUJIKMtPJGDJIu1u7LkU"
    "a3u9M/7PrMWKmcrSzJG+47n3zp0hZsYqD4EVH9aANWANWAPWwP9toNdkMRFdAeABcEqWRQDG"
    "zDwxpS1lqttKxABXAYQALgDkCQmAG/+YUQJyGa3JHfAAhP7ewSGYgxKnx79Onj+I/px5ACYL"
    "2vv7hwCCYqk4/nlyoGqNGXAAjMEceFt3CxeNT98F/t7+9o9Xz75oWqCN1lwO9G7coeRbTkZg"
    "Gc2igSXAEs7G5mxd/3ZwfffxawDf87Th+VcABBLOLHKI4KzfnGvvPXmT1RqrQsJdF+AIADT4"
    "NJc4ApFwe/0tv0irwoPEovbarc3lldE06RV4lso8qEirw1O11tw5kPxpBT4xAK7WKvAkRA2t"
    "IQMsZWpAh8/Ml2k1eKrUGgyhOAcU+FlOzOfLtBq8cKq1xlsJDb7J9ufAd9YLJX+pCL7GDqjw"
    "RB3uQDZOF+Gpfg6o8NRlDsTAKjwR1a9CKjx1WIX0chnDp4eRrKFV4BPz3EkV4sVk1CC4UqvC"
    "U2q+i3OAZQE8KfMl2jz4Cq3xEFLhKa3lNUJIgZ93Jx0a0OGpgYEc+M5zQIVvlAMqvOwyB8pb"
    "Yi45jLJzGnyF1uAOoKIlrtHI5sC3PAYu0UoUtcR1mrk8+O6aOS5tievdB2TxJWmZ70LZfiW5"
    "w5b1SkVz2dqfvX+16YWaGIjkdOQKd+3t+fujncKnizX/Q/w5bK/l4TIMjDma9r3t3afOhr9T"
    "8cIGjqafWmtl+NF4DsQvZb/D4edBRbAOOLp4+e3Fo0Fr7dHDU+NPi//qsM/r1oA1YA1YA9bA"
    "So+/P/qiKV2inxQAAAAASUVORK5CYII=")
getpause482Bitmap = pause482.GetBitmap
#----------------------------------------------------------------------
stop48 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAATdEVYdFRpdGxlAE9wdGljYWwgRHJpdmU+Z7oMAAACN0lEQVRoge2ZMWsbMRTH/0+yiSlx"
    "SgPFlOQGjx5q8NIpayHt0m9Q0qVfpEOhFH+HfoEOHUIJNVnyCTx1qsGhXUKJyeQDS8pw0sUp"
    "mEru04mC/mB0B6d3vz/vPZ11R8YY/M8SqQH+VdlAamUDqZUNpFY2kFqtkIuJaAdAB4CMgwMF"
    "YGmMKX0neBuw8LsAVgCWALj/gxCANoBdIoKviZAMdACsvp1//aS1frUN4d8kpfjy5vXbk/l8"
    "3gHglwVjjNcPwD6AB2eTUxNLZ5NTM51On45Go8e+XEE9MBwOyR1fX/+G0gpaKyilq9Gda3uu"
    "qmPAQAgBISSkHf88f9I7AAAMBoOX4/F4AuDKhyloFep2u0IpDQCs8EJUGEpptFqtdr/f7/ky"
    "BS+jWqt65IIXQt6LTUS06f4MBmwGGOGlzYCLHaJwA7aEOOFdCbnYUQ0om2ZOeFdCLnZUAy7N"
    "nPAiRQlxwksp78WOakCtZ4AJvl5Gm8mA7QFG+HoZVQ32ACd8oz1wl2Y+eFmvQg02MTf8euy4"
    "BuxazQnvXm/qJp4DLs3c8Ouxoxq4KyE++DoDzZYQJ3yCEuKEd1XUaAnxwjdaQpt6YHt4l4Ft"
    "HmRBe+LqJlWduj1siNxGa9OGa5seCDGgFotFe+/ho4sPH98fBd/JQ4cHh9/t4cJ3ToiBZVmW"
    "e8fPX7wriuIZ4r2dAxH98L3Wuwfsm7Kb2Wx2qbWO9WXwJ4DPRVH88p1A+StlYmUDqZUNpFY2"
    "kFrZQGrdAuMkYoPBsnXxAAAAAElFTkSuQmCC")
getstop48Bitmap = stop48.GetBitmap
#----------------------------------------------------------------------
pipelineok24 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAA3WAAAN1gGQb3mcAAAAB3RJTUUH4QgKDTIaVsv3egAAAkdJREFUSMftlE1PE1EU"
    "hp/pTGfmlsQalLYGFy4gAv0AlKVR4tqtoG78E0aj0IS4daHxL7ixdSO4MRG/ULDEuMLESGLE"
    "hbSdGYjBFiF05rqAiWNTPoyNbniTu7iZ3Od9z+ScA/v631KbwFCALqAdWAa8ZgZUgFQ6m8mf"
    "uDXwFhgAws2qQAGS6WwmaybEeUVV2uODif7SZPEdYPuVqH8DT42kR824GPLWPEW6EtVQ22On"
    "472lp8UCUAbQGjzWgOPAOvAJkI3gyevpETMmhtxVV/E/uK6L9ar8DdjY7hepQG/mZt/d1pOH"
    "ks6MPQ8s1cF7eq6lRkVcDLurroLciiBh8fHX8dJk8R4w5QdT6+CZzFjvba0lfEY/oPdFu6PC"
    "KTi+ySb8ampEJMSFWrX2G7z4ZPGh9bKcAx4EOylokExnM3e0lvCgu1rDW3cV47DZH+2Oms6s"
    "Mw/Ee64kb5hxcbH2fUNBSvxTelb04fn6Ng0atOkH9XNGq37MT7Vl0hftihqxU7GzZkxc2oT/"
    "Sl5+Xh63psr5RvB6g+WVjysypClG5GikM2hitol+rUXLbNTDX5Qn7NdWDshtN2BBAwnMVT5X"
    "NEULGeJIpFN6ID3wfrhKbc1V/Lv0wJqyxu1pK78TvFEXSWCuulDRQnrIiCREZzCxf6xpa8KZ"
    "sfPA/d1WQ6NB803CIUM1RUJ0BOH2tD3hvLFze4HvNMkSeO9XYsZEh/TAKdiPnIKzZ/huq8ID"
    "5qpfqrpqqEZ1ofJhafbP4HuVBlwGhpu03vf1j/UTiHEBhP1g7gkAAAAASUVORK5CYII=")
getpipelineok24Bitmap = pipelineok24.GetBitmap
#----------------------------------------------------------------------
pipelineignore24 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/gD+AP7rGNSCAAAA"
    "CXBIWXMAAA3WAAAN1gGQb3mcAAAACXZwQWcAAAAYAAAAGAB4TKWmAAAC5klEQVRIx+2T30uT"
    "URjHv++Pza3YyF/Fm1s2CbrRESo2h5QI3QRRQtEPG9KNNxWJXdgf4K03QlAEUZQ1mXWxiCiK"
    "wGqWpmRGJDn7oamvNp3bO7d5POd042Stdyld1E0PPLyc8+X9fM/z8DzA//jXIf1GEwDkArAC"
    "IABohm4EULDyTWaDiL+DD7c0eUJtrXfqHA5lBbQKr3M4lFBba/dwS5Nn5SHCeisQAOQOnTt1"
    "sniDqV1QJ7fX11S5Br5MP/wUDscBSHUOh+JtrPcaJsfdmyyWfcfLS6cvvXrzEUBCD5YZuYOn"
    "Gz3bN5ra6diIDM4hbsoDUewvT3T6jgHArYYjXsPUuIuF5wBBgFSyc/lzLHG+/OL1GwDm02Gy"
    "joHxm6o2bCVRGZwDAOisCpEQV+fRei8AiF/HXCQ8t/oDHXknfzNYGgB0radF5O6HMXOl1Wy1"
    "5ch2zig4o2CLGoSlhA0L8zYamkXqnjOKFzPhwLEn/V2U82eZw6BnQCnnQ/6peXOlxWQtMsp2"
    "Thk4ZWAxDSymIXXmlKH3eyTgGQz6koxd1pumbGO6TDkf8qsL5gqL0VpkkOzpL05l73wk0Pj2"
    "awoe1wNlG1MAoM7CQn/+thIDJQR6mb+txOAsLPTj1x1ZswKjW1GUzoN7b+eGpndTLQq9CvJz"
    "5KLDrvLdryfnHo5rWlzPSMoGv7bf7eWjIy4yo/7U8/SkWhRCfNF2qGqXa2A6rGuitwdbhk8e"
    "6Ja/jNYsf5/5SeiLkQAAVG00uNPv5YLNWC7e8bzs5r3DANQ1KwhOTFTsobFSgTGJMwbOGPpi"
    "S4HTk5rvfiT53mkUrIoIe0pLalHS+jb4NBgnD5CxzXoGyWCczI4miFBrQpnAqNS/SAJn1YQv"
    "yXCZcgw8ihGzU+ZWRWR2wii5oMavP44sXQUwinWGAMBdaxKvdORJPTkimgGY03Rzjojmjjyp"
    "p9YkXgHgztLuNU2qAZzJgK+arGjVfwL/H38vfgDg6YtTZYxtNAAAACV0RVh0ZGF0ZTpjcmVh"
    "dGUAMjAxMS0xMS0xNFQxMzozMDoyMSswMTowMGmKh8AAAAAldEVYdGRhdGU6bW9kaWZ5ADIw"
    "MTEtMTEtMTRUMTM6MzA6MjErMDE6MDAY1z98AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2Nh"
    "cGUub3Jnm+48GgAAAABJRU5ErkJggg==")
getpipelineignore24Bitmap = pipelineignore24.GetBitmap
class StaticTextNew(wx.StaticText):
	def __init__(self, parent, id=wx.ID_ANY, label="", style=wx.ALIGN_LEFT, size=(-1,-1), autotip=False, trunc=". : "):
		oldlabel = label
		if autotip and size[0] > 0:
			font = wx.Font()
			dc = wx.ScreenDC()
			dc.SetFont(parent.GetFont())
			width = dc.GetTextExtent(label)[0]
			if width > size[0]:
				label = label[0:int(len(label)*(float(size[0])/float(width)))-len(trunc)]+trunc
		wx.StaticText.__init__(self, parent, id, label=label, style=style, size=size)
		if autotip:
			self.SetToolTipNew(oldlabel)
	def SetToolTipNew(self, string):
		if IsNotWX4():
			self.SetToolTipString(string)
		else:
			self.SetToolTip(string)
class TextCtrlNew(wx.TextCtrl):
	def __init__(self, parent, id=wx.ID_ANY, value="", style=wx.ALIGN_LEFT|wx.TE_PROCESS_ENTER, size=(-1,-1)):
		wx.TextCtrl.__init__(self, parent, id, value=value, style=style, size=size)
	def SetToolTipNew(self, string):
		if IsNotWX4():
			self.SetToolTipString(string)
		else:
			self.SetToolTip(string)
class ButtonNew(wx.Button):
	def __init__(self, parent, id=wx.ID_ANY, label="", style=wx.ALIGN_LEFT, size=(-1,-1)):
		wx.Button.__init__(self, parent, id, label=label, style=style, size=size)
	def SetToolTipNew(self, string):
		if IsNotWX4():
			self.SetToolTipString(string)
		else:
			self.SetToolTip(string)
class BitmapButtonNew(wx.BitmapButton):
	def __init__(self, parent, id=wx.ID_ANY, bitmap=wx.NullBitmap, style=wx.ALIGN_LEFT, size=(-1,-1)):
		wx.BitmapButton.__init__(self, parent, id, bitmap=bitmap, style=style, size=size)
	def SetToolTipNew(self, string):
		if IsNotWX4():
			self.SetToolTipString(string)
		else:
			self.SetToolTip(string)
class CheckBoxNew(wx.CheckBox):
	def __init__(self, parent, id=wx.ID_ANY, label="", style=wx.ALIGN_LEFT, size=(-1,-1)):
		wx.CheckBox.__init__(self, parent, id, label=label, style=style, size=size)
	def SetToolTipNew(self, string):
		if IsNotWX4():
			self.SetToolTipString(string)
		else:
			self.SetToolTip(string)
class RadioBoxNew(wx.RadioBox):
	def __init__(self, parent, id=wx.ID_ANY, label="", size=(-1,-1), choices=[], majorDimension=0, style=wx.ALIGN_LEFT):
		wx.RadioBox.__init__(self, parent, id, label=label, size=size, choices=choices, majorDimension=majorDimension, style=style)
	def SetToolTipNew(self, string):
		if IsNotWX4():
			self.SetToolTipString(string)
		else:
			self.SetToolTip(string)
class DummyEvent():
	def __init__(self):
		pass
	def GetEventCategory(self):
		return wx.EVT_CATEGORY_UI
	def GetId(self):
		return 0
	def Skip(self):
		pass
class SpinButtonNew(wx.SpinButton):
	def __init__(self, parent, id=wx.ID_ANY , style=wx.SP_VERTICAL, size=(-1,-1), spinfunc=None):
		wx.SpinButton.__init__(self,parent, style=style, size=size)
		self.Bind(wx.EVT_SPIN, self.OnSpin)
		self.spinfunc=spinfunc
		self.MiscFunc = None
		self.event = DummyEvent()
	def OnSpin(self, event):
		self.spinfunc(event.GetPosition())
		if self.MiscFunc is not None:
			self.MiscFunc(self.event)
	def SetEventFunc(self, miscfunc):
		self.MiscFunc = miscfunc
class SpinButtonNew2(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, style=wx.ALIGN_LEFT, size=(-1,-1), spinfunc=None):
		wx.Panel.__init__(self, parent)
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.buttonP = wx.Button(self, -1, label="+", size=size)
		self.buttonM = wx.Button(self, -1, label="-", size=size)
		self.buttonP.Bind(wx.EVT_BUTTON, self.OnP)
		self.buttonM.Bind(wx.EVT_BUTTON, self.OnM)
		self.repeatTimerP = wx.Timer(self)
		self.repeatTimerM = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.RepeatValueP, self.repeatTimerP)
		self.Bind(wx.EVT_TIMER, self.RepeatValueM, self.repeatTimerM)
		self.buttonP.Bind(wx.EVT_LEFT_DOWN, self.OnButPDown)
		self.buttonM.Bind(wx.EVT_LEFT_DOWN, self.OnButMDown)
		self.buttonP.Bind(wx.EVT_LEFT_UP, self.OnButPUp)
		self.buttonM.Bind(wx.EVT_LEFT_UP, self.OnButMUp)
		self.hbox.Add(self.buttonM, 0)
		self.hbox.Add(self.buttonP, 0)
		self.SetSizer(self.hbox)
		self.Fit()
		self.Layout()
		self.Show()
		self.max = 0
		self.min = 0
		self.range = 0
		self.value = 0
		self.SpinFunc = spinfunc
		self.n = 1
		self.t1 = time()
		self.t2 = time()
	def SetEventFunc(self, miscfunc):
		self.MiscFunc = miscfunc
		self.event = DummyEvent()
		if miscfunc != None:
			self.n = 2
		else:
			self.n = 1
	def GetRange(self):
		return (self.min,self.max)
	def SetRange(self,min,max):
		self.max = max
		self.min = min
	def GetValue(self):
		return self.value
	def SetValue(self,value):
		self.value = value
	def PostCall(self):
		self.SpinFunc(self.value)
		for i in range(1, self.n, 1):
			self.MiscFunc(self.event)
	def OnM(self, event):
		if self.value > self.min:
			self.value -= 1
		if event != None:
			self.t1 = time()
		self.PostCall()
	def OnP(self, event):
		if self.value < self.max:
			self.value += 1
		if event != None:
			self.t1 = time()
		self.PostCall()
	def RepeatValueM(self, event):
		self.t2 = time()
		if (self.t2-self.t1) > 0.75:
			self.OnM(None)
	def RepeatValueP(self, event):
		self.t2 = time()
		if (self.t2-self.t1) > 0.75:
			self.OnP(None)
	def OnButMDown(self, event):
		self.repeatTimerM.Start(100)
		event.Skip()
	def OnButMUp(self, event):
		self.repeatTimerM.Stop()
		event.Skip()
	def OnButPDown(self, event):
		self.repeatTimerP.Start(100)
		event.Skip()
	def OnButPUp(self, event):
		self.repeatTimerP.Stop()
		event.Skip()
def IsNumber(input):
	try:
		float(input)
		return True
	except:
		return False
class TextPanelObject(wx.BoxSizer):
	def __init__(self, parent, name, objectpath, textwidth, file_extension):
		def assign(input):
			self.objectpath.ChangeValue(input)
		def OnBrowse(self):
			if IsNotWX4():
				dlg = wx.FileDialog(parent, 'Choose a file', os.getcwd(), '',  file_extension, wx.OPEN)
			else:
				dlg = wx.FileDialog(parent, 'Choose a file', os.getcwd(), '',  file_extension, wx.FD_OPEN)
			if dlg.ShowModal() == wx.ID_OK:
				assign(dlg.GetPath())
			dlg.Destroy()
		def OnEdit(event):
			self.objectpath.ChangeValue(event.GetString())
		fontpointsize=wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPointSize()
		self.font = wx.Font(fontpointsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.ScreenDC()
		dc.SetFont(self.font)
		textw,texth = dc.GetTextExtent(name)
		if textw > textwidth:
			labelw = textw
		else:
			labelw = textwidth
		wx.BoxSizer.__init__(self, wx.HORIZONTAL)
		self.label = StaticTextNew(parent, -1, name, style =wx.ALIGN_RIGHT, size=(labelw,-1) )
		self.label.SetFont(self.font)
		self.Add( self.label, 0, wx.CENTER )
		self.objectpath = TextCtrlNew(parent, -1)
		self.objectpath.SetFont(self.font)
		self.objectpath.SetValue(objectpath)
		self.objectpath.SetToolTipNew("Browse for file or type "+os.linesep+"path and name")
		self.objectpath.Bind(wx.EVT_TEXT_ENTER, OnEdit)
		self.Add( self.objectpath, 1, wx.CENTER |wx.EXPAND )
		self.button = ButtonNew(parent, -1, "Browse")
		self.button.SetFont(self.font)
		self.button.SetToolTipNew("Browse for file or type "+os.linesep+"path and name")
		self.button.Bind(wx.EVT_BUTTON, OnBrowse)
		self.Add( self.button, 0, wx.LEFT|wx.CENTER)
	def Hide(self):
		self.label.Hide()
		self.objectpath.Hide()
		self.button.Hide()
	def Show(self):
		self.label.Show()
		self.objectpath.Show()
		self.button.Show()
	def Enable(self):
		self.label.Enable(True)
		self.objectpath.Enable(True)
		self.button.Enable(True)
	def Disable(self):
		self.label.Enable(False)
		self.objectpath.Enable(False)
		self.button.Enable(False)
class SpinnerObject(wx.BoxSizer):
	def __init__(self, parent, name, smax, smin, sinc, sinit, stextwidth, swidth):
		if abs(sinc) < 1.0:
			self.precision = "%."+str(str(sinc)[::-1].find('.'))+"f"
		else:
			self.precision = "%d"
		def OnSpin(pos):
			self.value.ChangeValue(self.precision%(sinc * pos + self.remainder))
		def OnEdit(event):
			text = event.GetString()
			point = self.value.GetInsertionPoint()
			if (IsNumber(self.value.GetValue()) == False):
				self.value.SetBackgroundColour( "Pink" )
				self.value.SetForegroundColour( "Black" )
			else:
				self.value.SetBackgroundColour(wx.NullColour)
				self.value.SetForegroundColour(wx.NullColour)
				self.value.ChangeValue(text)
				self.value.SetInsertionPoint(point)
				if ( text == '' or  text == '.'): self.spin.SetValue(smin/sinc);
				try:
					self.spin.SetValue(int(float(text)/sinc))
				except:
					pass
				event.Skip()
		fontpointsize=wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPointSize()
		self.font = wx.Font(fontpointsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.ScreenDC()
		dc.SetFont(self.font)
		textw,texth = dc.GetTextExtent(name)
		if textw > stextwidth:
			labelw = int(textw + 70)
		else:
			labelw = stextwidth
		textw,texth = dc.GetTextExtent(str(sinit))
		if textw > swidth:
			sinitw = int(textw *1.5)
		else:
			sinitw = swidth
		wx.BoxSizer.__init__(self, wx.HORIZONTAL)
		self.label = StaticTextNew(parent, -1, name, style=wx.ALIGN_RIGHT, size=(labelw,-1) )
		self.label.SetFont(self.font)
		self.Add( self.label, 0, wx.CENTER )
		self.value = TextCtrlNew(parent, value=str(sinit),size=(sinitw, -1), style=wx.TE_PROCESS_ENTER)
		self.value.SetWindowStyle(wx.TE_RIGHT)
		self.value.SetFont(self.font)
		self.value.Bind(wx.EVT_TEXT, OnEdit)
		self.Add( self.value, 0, wx.CENTER )
		bw,bh = dc.GetTextExtent("0")
		spinh = int(1.4*bh)
		spinw = -1
		self.spin = SpinButtonNew(parent, size=(spinw,spinh), spinfunc=OnSpin)
		self.spin.SetRange(int(smin/sinc), int(smax/sinc))
		self.spin.SetValue(int(sinit/sinc))
		self.remainder = smin%sinc
		self.Add( self.spin, 0, wx.CENTER )
		self.IsEnabled = True
		self.Layout()
		self.Show()
	def Hide(self):
		self.label.Hide()
		self.value.Hide()
		self.spin.Hide()
	def Show(self):
		self.label.Show()
		self.value.Show()
		self.spin.Show()
	def Disable(self):
		self.label.Enable(False)
		self.label.Refresh()
		self.value.Enable(False)
		self.value.Refresh()
		self.spin.Enable(False)
		self.spin.Refresh()
		self.IsEnabled = False
	def Enable(self):
		self.label.Enable(True)
		self.label.Refresh()
		self.value.Enable(True)
		self.value.Refresh()
		self.spin.Enable(True)
		self.spin.Refresh()
		self.IsEnabled = True
class NumberObject(wx.BoxSizer):
	def __init__(self, parent, name, init, stextwidth):
		def OnEdit(event):
			text = event.GetString()
			point = self.value.GetInsertionPoint()
			if (IsNumber(self.value.GetValue()) == False):
				self.value.SetBackgroundColour( "Pink" )
				self.value.SetForegroundColour( "Black" )
			else:
				self.value.SetBackgroundColour(wx.NullColour)
				self.value.SetForegroundColour(wx.NullColour)
				self.value.ChangeValue(text)
				self.value.SetInsertionPoint(point)
		fontpointsize=wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPointSize()
		self.font = wx.Font(fontpointsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		wx.BoxSizer.__init__(self, wx.HORIZONTAL)
		dc = wx.ScreenDC()
		dc.SetFont(self.font)
		textw,texth = dc.GetTextExtent(name)
		if textw > stextwidth:
			labelw = textw
		else:
			labelw = stextwidth
		self.label = StaticTextNew(parent, -1, name, style =wx.ALIGN_RIGHT, size=(labelw,-1) )
		self.label.SetFont(self.font)
		self.Add( self.label, 0, wx.CENTER )
		self.value = TextCtrlNew(parent, value=str(init), style=wx.TE_PROCESS_ENTER)
		self.value.SetWindowStyle(wx.TE_RIGHT)
		self.value.SetFont(self.font)
		self.value.Bind(wx.EVT_TEXT, OnEdit)
		self.Add( self.value, 1, wx.CENTER|wx.EXPAND )
	def Hide(self):
		self.label.Hide()
		self.value.Hide()
	def Show(self):
		self.label.Show()
		self.value.Show()
	def Disable(self):
		self.label.Enable(False)
		self.label.Refresh()
		self.value.Enable(False)
		self.value.Refresh()
	def Enable(self):
		self.label.Enable(True)
		self.label.Refresh()
		self.value.Enable(True)
		self.value.Refresh()
def IsPy3():
	from sys import version
	return version[0] == '3'
def IsNotVTK6():
	from vtk import vtkVersion
	VTKMajor = vtkVersion().GetVTKMajorVersion()
	if VTKMajor < 6:
		return True
	else:
		return False
def IsNotVTK7():
	from vtk import vtkVersion
	VTKMajor = vtkVersion().GetVTKMajorVersion()
	if VTKMajor < 7:
		return True
	else:
		return False
def IsNotWX4():
	if wx.VERSION[0] < 4:
		return True
	else:
		return False
def OptIconSize():
	displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
	sizes = [display.GetGeometry().GetSize() for display in displays]
	x,y = sizes[0]
	iconsize = int(2.5*(x)/100.0)
	if iconsize < 30:
		iconsize = 30
	if iconsize > 60:
		iconsize = 60
	return iconsize
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, id, bmpsize=(24,24), size=(180,1)):
		wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL, size=(180,1))
		ListCtrlAutoWidthMixin.__init__(self)
		bmpchk = getpipelineok24Bitmap()
		bmpunchk = getpipelineignore24Bitmap()
		CheckListCtrlMixin.__init__(self,check_image=bmpchk,uncheck_image=bmpunchk, imgsz=bmpsize)
	def CheckItem(self, idx, check=True):
		CheckListCtrlMixin.CheckItem(self, idx, check)
class CustomAboutDialog(wx.Dialog):
	def __init__(self, parent, info):
		wx.Dialog.__init__(self, parent, title="About Bonsu", size=(460,300))
		self.SetSizeHints(450,300,-1,-1)
		self.parent = parent
		self.info  = info
		self.vboxborder = wx.BoxSizer(wx.VERTICAL)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.icon = wx.Image(os.path.join(os.path.dirname(os.path.dirname(__file__)),'image',  'bonsu.ico'), wx.BITMAP_TYPE_ICO)
		if IsNotWX4():
			self.bitmap = wx.BitmapFromImage(self.icon)
		else:
			self.bitmap = wx.Bitmap(self.icon)
		self.staticbmp = wx.StaticBitmap(self, -1, self.bitmap)
		self.vbox.Add(self.staticbmp, 0, flag=wx.CENTER, border=5)
		namestr = info.GetName()+" "+info.GetVersion()
		self.namefont = wx.Font((parent.font.GetPointSize()+8),parent.font.GetFamily(),wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		self.name = wx.StaticText(self, label=namestr)
		self.name.SetFont(self.namefont)
		self.vbox.Add((-1, 5))
		self.vbox.Add(self.name, 0, flag=wx.CENTER, border=5)
		self.vbox.Add((-1, 5))
		self.description = wx.StaticText(self, label=info.GetDescription(), style=wx.ALIGN_CENTRE_HORIZONTAL)
		self.description.Wrap(400)
		self.vbox.Add(self.description, 0, flag=wx.CENTER, border=5)
		self.vbox.Add((-1, 5))
		self.copyright = wx.StaticText(self, label=info.GetCopyright())
		self.vbox.Add(self.copyright, 0, flag=wx.CENTER, border=5)
		self.vbox.Add((-1, 5))
		if IsNotWX4():
			self.web = wx.StaticText(self, label=info.GetWebSite()[0])
		else:
			self.web = wx.StaticText(self, label=info.GetWebSiteURL())
		self.vbox.Add(self.web, 0, flag=wx.CENTER, border=5)
		self.vbox.Add((-1, 10))
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.credits =wx.Button(self, label="More")
		self.Bind(wx.EVT_BUTTON, self.OnCredits, self.credits)
		self.hbox.Add(self.credits)
		self.hbox.Add((10, -1))
		self.license =wx.Button(self, label="License")
		self.Bind(wx.EVT_BUTTON, self.OnLicense, self.license)
		self.hbox.Add(self.license)
		self.hbox.Add((10, -1))
		self.close =wx.Button(self, label="Close")
		self.Bind(wx.EVT_BUTTON, self.OnClose, self.close)
		self.hbox.Add(self.close)
		self.vbox.Add(self.hbox, 0, flag=wx.CENTER, border=5)
		self.vbox.Add((-1, 10))
		self.vboxborder.Add(self.vbox, 1, flag=wx.CENTER|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=20)
		self.SetSizer( self.vboxborder )
		self.SetAutoLayout(True)
		self.Fit()
		self.Layout()
	def OnCredits(self, event):
		msg = ""
		for name in self.parent.version_str_list:
			msg += name+os.linesep
		dlg = wx.MessageDialog(self, msg,"Lib Info", wx.OK)
		result = dlg.ShowModal()
		dlg.Destroy()
	def OnLicense(self, event):
		lines = self.info.GetLicence().splitlines()
		msg = ''
		for line in lines:
			if line == "":
				msg += os.linesep+os.linesep
			else:
				msg += line+" "
		dlg = wx.MessageDialog(self, msg,"License", wx.OK)
		result = dlg.ShowModal()
		dlg.Destroy()
	def OnClose(self, event):
		if self.IsModal():
			self.EndModal(event.EventObject.Id)
		else:
			self.Close()
