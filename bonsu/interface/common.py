#############################################
##   Filename: common.py
##
##    Copyright (C) 2011 - 2026 Marcus C. Newton
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
MAX_INT = numpy.iinfo(numpy.int32).max
MIN_INT = numpy.iinfo(numpy.int32).min
MAX_INT_16 = numpy.iinfo(numpy.int16).max
MIN_INT_16 = numpy.iinfo(numpy.int16).min
CNTR_CLIP = 0.999
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
    b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAyCAYAAABcfPsmAAAACXBIWXMAAAJuAAACbgG3/vvg'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABHRJREFUSIntlUtMG0cY'
    b'x/+7s3aMbcAB80xpgBBjXgFKaXi1pQ2N5DZCGFEHAwdalFQ5Vu2tJ1ShVkpOvVCJC1WlHEKj'
    b'BqnlQk8g0ksVXKk1QipUojyEmqjyA9u7szPbA6yLwaww7aVSRhrt7szOT/+Zb/7fB03TcFIH'
    b'IIyOvv/gzp07nxr9d7iLMGgjIyMfvt0/8K7rSvMnw8PDbxj9q7cTgYODg/WvdHV/3tZUjxvX'
    b'e4QXq1wPfD5f3pmAvb291gsXK7679nqXyWKxINtmxTsej9ORl//VmYA5jvNTPT09F+3WLJhM'
    b'JphMJrxQXIiOV1+7MTQ09F5GQK/X62/r6BwqKymCpmlgjIFzDk3T0FRXg6rqmi8HBgbcpwJ6'
    b'vd7yiirXVGNdLRhjYIxBURQoigLGGDRNQ2dHuznPWfCtz+czGwLHx8dFi83+sL3tqo3zf2CJ'
    b'RAKyLINSCsYYzBJBe0enWxCECUNgIBD4rKO9/SW7NQuMMVBKk8BEIgFFUUApBecchfnn0dDU'
    b'/JHP53srLbC3t7erpq7+49LiopStyrIMWZaPqeScw3XpklBSeuF+f39/fgrQ6/U6iopLvnFX'
    b'u0TOOTjnKUBd4VEgoKG+vt6Z43B8nQLMycn5orHxSpF2ADrcD6tTFAWqqqbMmySCy1WXPbdv'
    b'3x7VgcLCwsLvy8uB8lg8DkIICCFwOHJRVFgISZIgCAIAJJVvbm0hFosnoWazGcVFhT/5/f5W'
    b'AJAWFxfbtra2mqPRqMo5FwghWeUVFbP5eXn7ZhfFFODa2trTZ0+f+nVFdrtdCv76y7Lfvz8k'
    b'HGSVZBsbG8uurKwMu91uEEJSFHLO8eTJk82JiYmydFcGAKSjA06nE4IgQFVVcM6TQN01knRs'
    b'iTEQAERRBKU0rcIzA9Mp5JyDEKKlW3MisLu7W7DZbDwQCIhHz1cURTQ0NBgm5WNAj8cTnpqa'
    b'qonFYtlH57KyskTG2J8ZAQEgGo3+kZubawmFQgAA/bmxsYFgMBjt6+s7PXB6etpS7a75i2va'
    b'uRJVTVpQTxTRSPhnAE2nBkYiEbPTWXCuutqVzDB6TlQUBfPzP9gy2nJ2drZIqYKdnZ0UEKUU'
    b'lFLs7UUzi3JXV5cpGAw+W1lZsYRCIe3wlhVFgcfjMQQesx4AEwArgAgAbrT4VAoB0MnJyQ7G'
    b'mF1RFMTjccTjcejvFotl8+7duz+eGnjv3j2bq9o9V1ZWBkopZFmGqqrJ7P348eNVACdWvWNA'
    b'q9UqaJxDIiI4E2CSCDTO9r8lAo1zQzMfmywoKCCMqSlR1iO8n7WpkBGwtbVVXlpaur++vm4J'
    b'h8NMLwEH5yjcvHlTMQKmi/K/aunOQ3j46NF8KBy1y7LuFBmJxH7VKy0u+O2DW7dGTg2cmZkx'
    b'2ez2a1fffDnFKfpZfj83V5qpQuzt7WF7ezsFpL/HYrHMrFdZWSnt7u5qq6urgm65w3W5orw8'
    b's2vT0tIiz87OXt/Z2REikYimRzmRSIAQQmpra0NGwP88yob14TnwOfA58H8D/BsXzPASWQvA'
    b'LAAAAABJRU5ErkJggg==')
getspinupBitmap = spinup.GetBitmap
#----------------------------------------------------------------------
spindown = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAyCAYAAABcfPsmAAAACXBIWXMAAAJOAAACTgEl1tp0'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABB1JREFUSIntlk1MY1UU'
    b'x//3vnfvu20Z040KDROYIQyEKCtjAqkfxCULyZgu1MQQdWLQnQvirsS4Vdnojg0SIbUQQwQS'
    b'42CZdASGIinUyiQMlorD9GNmbPhoX9v36oJ5TzrDE9+EGBe85CYvuff87jn3nP+5l1QqFZzm'
    b'Rx/DhgBwWU3KVhPj4+PXw+FwO+cciqJAURQIIVBTU0Pq6+u/7+7uvmwLGJqbkzs7OmoYY+Cc'
    b'V43fEoknbXsohCAej+cRGOcciWRSsw2s83g2lyLL54UQ4IoC5QGMMQaXw7VpZUdOO8uWHk5P'
    b'T38WDAbPMcZ0IQSEEHA4HHC73XJjY2O8p6fnU1vA76amnvN6vS8YYR5NTiqVugHAHpBzbpmU'
    b'dCaj2w6ZSnLx3v0/IYQAYwxCCHDOIUkSdF1XbQPz+3uvLy7Mn2eMwel0wul0wvhnjG1bOmI1'
    b'0dbWdk7TNDmXyyGXyyGbzSKXy+Hg4IDW1tY+YdvD3d3dr+rq6joopab0DPmpqroE4HlbwJ2d'
    b'nVJXV9exSYnH4/aVIisKferpWlMdiqKAcw5ZliHxDWIbeLGh4Zux0a/jR4va+G9ubl63svvv'
    b'pLe8vPzt7Oxsk7Ghrh/WMqUUnZ2da16v9w1bwJmZmVqPx/MMpRSEHB5ZpVKBrusIhUK7Xq/X'
    b'noelUokwxvAwUNM0lEol+0nRdf0wo5JUBaSUQtMsq8YaWC6XCWPsESAhBOVy+Z89JISQgYGB'
    b'pmQyaXYRt9stDA8ppabXhBCoquro7e1tkiSpAgAtLS3F/v7+beBB2QwODva5XK4v05ksKKWQ'
    b'JAkOhwMXGhsgy3IVsFwuY+PWJgqFAjRNg67raLl0SScEL/l8vrAMALlcbiqxldxvf7bdJQQ3'
    b'VcEYM8/RyDAANF28AFVVzRFdjZa3EomEz+c77DZ+vz+ZurPTm7mbMT2UZRmyLJsNweFw/C09'
    b'STJHOpPFzfX1D0dGRraBI+1rdHQ0GFtdGzvIF0yooWFDckazNWD5goroavRqMBj8wuBU9UNV'
    b'LVxZWVnZJpSCUgrj1WDAjG4jSRIqAJYikftqPl+lmCpgIBDYy6RTl2Pxdc0Im3NuAhVFgVHs'
    b'sfivle3k1psTExNpSyAAjI2NLa2uLH/y++07kGXZvE+Ohpu+ew/Rn1c+n5ycnHnY/tgroLW1'
    b'9eOF+Z8W9w7ykCTJDJVSioJaxFzoWmxzc+Oj42yPBfr9fj2bTr32w+yPe3rlUCFG2VwNzeUz'
    b'qduvRiKR0r8GAkAgEPjj5i9rb4UXbqBYLKJYLGIpGsN6bPXdYDBo+bYxd7cab79zZXj22vVK'
    b'eH6x8t77H4yctN6yORhfqVjom56ZfpESSSoV8n0nrT/xSTw8PLwvJPIKp/rLQ0NDuyetP/U7'
    b'5XEe7WfAM+AZ8P8H/Av8EN5wwb6AqgAAAABJRU5ErkJggg==')
getspindownBitmap = spindown.GetBitmap
#----------------------------------------------------------------------
start = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAALEAAACxAFbkZ0L'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAArpJREFUSInF1j9ME1Ec'
    b'B/Dve3f9c/bKEa4WatTEmDRNWKQjk6ubMWrYNXF1NTE2nRx6pAiEyYTEG0ggcZSBBBicYJBS'
    b'sKbRFptIiUSgCLbXd/eeAzkCWFvAEl9yyxu+n/v9fvkljwghcJGHNrqcn58PmaYZvhDANM2w'
    b'JMulQIdWTqfTL6ampqS2AoVCoWsll1N+/dylqtaZ/La+vmAYxo22AQBg2zYAQFX8uNzdHQ92'
    b'dq4YhjHQFsCyLAghQCkFpRReSUKoq+vS1WvXJ14ND08YhhH4J6Berx8DKKWghEDx+3AlEhlQ'
    b'FCWTSqVunRsA8CdAKSRJgqZpiMViN3VdXzAM4ykAcmbAsixwzkEIASHkEPD7/QgEAtA0DfF4'
    b'3NPb25seGRmZTaVSPeeqwAUIIfB4PPD5fFAUBYFAAKqqIhqNor+//3YkEvk0ODh459SAO4Oj'
    b'gCzL8Hg88Hq9UBQFwWAQqqpC13X09fVp0Vjs3fDo6OtkMuk9mSc3BDg/due2SpIkyLIMn88H'
    b'QggYY6CUoiccBoBH9TrrBHC/KQAA/AQghADnHI7jgDGGWq0G4GBfOOdgto0fW1tVZtXetKzA'
    b'siw4nEMIcfjZtg3GGCzLAqUUjuMAABhjKJfLWPmYy1a2t+4mEolCSwAAHMc5Brh/TQgB5/xw'
    b'GTOZDF8rlV7mVlcTk5OTTqOshjPgRypw2+WGMsawv7+PxcXFcqVSeTg0NPS+UXBLwN2Fo6dW'
    b'qyGfzyOXy70VQjweGxvbbhbeEAAOWnQSsCwL+Xy+WiwWn4yPj5utgv8KuK1wWyOEwHZlF8uZ'
    b'pWxlZ+eeaZqfTxvetAIAqNs21r6WeHbpgxEKhZ6bpsnOEt4QCOq6JASwsbmJ7HJ24/tG+cH0'
    b'9HTTQZ4JqO/tFYna8WV2ZmamWq0+m5ub2zlvOACQ//KqaOf5DSA5dJH1KTboAAAAAElFTkSu'
    b'QmCC')
getstartBitmap = start.GetBitmap
#----------------------------------------------------------------------
pause = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAALEAAACxAFbkZ0L'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAshJREFUSInVlj1rXEcU'
    b'ht/5vNpKlhqpUOUilokatwluVBnSujYGg36E6ySFq/TG+E8IVS7UCZwQCLizEAgUsfrigpC0'
    b'd2bOmZNCO5d7d+9alYsMbLGz75xn3vMxrBIRfM+lv2t0ALb7ZX9//5Ex5v1oNPppNBpVTdOk'
    b'29vbf4jozfb29r9d7cHBwbOc8x9LS0tPvPd2MplMbm5uPh0eHu7s7OykQUBd179WVfXy6Oio'
    b'3VteXl7XWn8A8KKrPT8//xBjfHZ3d9fubWxsvF5dXf0K4PdBwOXl5Y/OORERpbWGiKCua4jI'
    b'D7PW67p+LCJQSkEphZwzTk5OJKW01dX1anB2dgZmhvceVVXBew+lFM7GYzULuLi4UFrrnjal'
    b'hPF43IvZc9A0Day1qKoKWmvknAEAIcbZ+AghiPe+vQQzIzQNQgi9tuwBcs5wzsF7D2MMmLnd'
    b'n10i0mq11iAiOO/ntPMAa1tAzhkigpQSZhcRoTjQWrefcqlBADPDGAPvPay1YGYwM4aGkZl7'
    b'brXWPdcLAeVQARARmHmuyAB6AKUUrDFzl5lLkbEWzjk450BEsNYO1iDnDNtJJwBoY0BED6RI'
    b'azjn2k4KISwscgFYex+muP42wJjWOoDBvBat7bhl5rZdu6s3FOWmZRastYOdUbRa616a1NTZ'
    b'QgAzQ03brbSfUoP1Rc4ZSqm267TWwEMOmBl52pbdwLOFKwAR6Wlzzg+nqIiaprkHDhwCgJSS'
    b'Kr+FENqZeWiSM+cMIkLTNIgxlkGbm7QSPE7fKSJCvj+7+C0iogkRIcYIpRRijIgxgojmXjtm'
    b'pqLNORcdmPlmIUBE/rq6uvrFWiveezAzTk9PkVL6PAD4cnx8/HxtbQ3GGIQQcH19rZj5z4WA'
    b'zc3Nd3t7e84597OI6Gmgv9fX13+bBaysrLza3d19a4x5Or0cMfOnra2tj12d+t//q/gPWMve'
    b'HNr2EE8AAAAASUVORK5CYII=')
getpauseBitmap = pause.GetBitmap
#----------------------------------------------------------------------
pause2 = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAALEAAACxAFbkZ0L'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAshJREFUSInVlj1rXEcU'
    b'ht/5vNpKlhqpUOUilokatwluVBnSujYGg36E6ySFq/TG+E8IVS7UCZwQCLizEAgUsfrigpC0'
    b'd2bOmZNCO5d7d+9alYsMbLGz75xn3vMxrBIRfM+lv2t0ALb7ZX9//5Ex5v1oNPppNBpVTdOk'
    b'29vbf4jozfb29r9d7cHBwbOc8x9LS0tPvPd2MplMbm5uPh0eHu7s7OykQUBd179WVfXy6Oio'
    b'3VteXl7XWn8A8KKrPT8//xBjfHZ3d9fubWxsvF5dXf0K4PdBwOXl5Y/OORERpbWGiKCua4jI'
    b'D7PW67p+LCJQSkEphZwzTk5OJKW01dX1anB2dgZmhvceVVXBew+lFM7GYzULuLi4UFrrnjal'
    b'hPF43IvZc9A0Day1qKoKWmvknAEAIcbZ+AghiPe+vQQzIzQNQgi9tuwBcs5wzsF7D2MMmLnd'
    b'n10i0mq11iAiOO/ntPMAa1tAzhkigpQSZhcRoTjQWrefcqlBADPDGAPvPay1YGYwM4aGkZl7'
    b'brXWPdcLAeVQARARmHmuyAB6AKUUrDFzl5lLkbEWzjk450BEsNYO1iDnDNtJJwBoY0BED6RI'
    b'azjn2k4KISwscgFYex+muP42wJjWOoDBvBat7bhl5rZdu6s3FOWmZRastYOdUbRa616a1NTZ'
    b'QgAzQ03brbSfUoP1Rc4ZSqm267TWwEMOmBl52pbdwLOFKwAR6Wlzzg+nqIiaprkHDhwCgJSS'
    b'Kr+FENqZeWiSM+cMIkLTNIgxlkGbm7QSPE7fKSJCvj+7+C0iogkRIcYIpRRijIgxgojmXjtm'
    b'pqLNORcdmPlmIUBE/rq6uvrFWiveezAzTk9PkVL6PAD4cnx8/HxtbQ3GGIQQcH19rZj5z4WA'
    b'zc3Nd3t7e84597OI6Gmgv9fX13+bBaysrLza3d19a4x5Or0cMfOnra2tj12d+t//q/gPWMve'
    b'HNr2EE8AAAAASUVORK5CYII=')
getpause2Bitmap = pause2.GetBitmap
#----------------------------------------------------------------------
stop = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAALEAAACxAFbkZ0L'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAgpJREFUSInVlk1qG0EQ'
    b'hV9VdxsMgQxexSCTTVZZ5BQ+QNbJ+bIKvoNAhwi+gGSjaCk8SPWTRdRN90xPsghepKFgGNTv'
    b'61dvakbk7njNxa+qDiDmi81m88nMHsZxvIkxcoyRQwjEzBRjJGamEAIAQFVhZi4ibmauqi4i'
    b'JiIWY/zp7p/v7+9/NIDT6fQdwIfdbtecgACAqH88d0wbfHt7e6OqDwA+NoDHx8c319fXcxEi'
    b'LMjDAUwz3G63eHl5eTtr0X6/l9VqBWZuiohKtYf3UmbW1H6/lxlgHEcPISCl9E+A8/mMcRx9'
    b'BlBVpJSQUkIIoQEw86VbVMQBwMwagKoWrRnAzJBSwtXVFZi5QDKg56AGqCryU2Zmy4DaQQih'
    b'AdQOakAWV9Vyv9uiGGOpuk1/AphZESeiplUzB8xcHPQg9aqDzeJEBBFZbhERFfGek9rBVDyv'
    b'7KKfwUVwCogxdgEi0oi7O1KMfcD5fAYugeaAp7AaICKNcG4xiH5r9Ry4ezNYPRAAiEgTdL1n'
    b'+hSV5HLy9YTmWlpLv118inqjX4eYN+b+X17bper9M4CqQkRKcNNAa1AernrP9Lrr4PIRodp+'
    b'HqTeoE0hlxnwroNhGJ6Px+N7VfUYAjgEhM6ru3ZV2mgGU4Wo4nQ60TAMTzPAarX6sl6vvx0O'
    b'h3eLqf5lMbMPw/B8d3f3Nd+j//5fxS/fNiQKLaCqAgAAAABJRU5ErkJggg==')
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
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAA3WAAAN1gGQb3mc"
    "AAAACXZwQWcAAAAYAAAAGAB4TKWmAAAABmJLR0QA/gD+AP7rGNSCAAAFd0lEQVRIx9WUaUzU"
    "RxjGkYpSFN2DQ0E0WCSl9tC2lHg0VIGgwVYrQrQRW62KC1KpKOfusoAHlyBY7mtRKodcIpci"
    "xx7KucBCBUFYBBER0AXdBSp1nw6GD7Yq8KUfOskv/2TyzvO88/xnRknp/zRCd79n5Wut5jOr"
    "4nKO5sIKNs2G703P4XPoPTw2Xc5jUcH3pkkFHI0yHovC5LMXm4GjpDxZn+K83LU2frvCc/t8"
    "x5nFvagb+WzakDjJStYv4mJ0qA0TY1K8fCHH+HA3hlpz0V3mO9EQayHjs+ktcYfUk5sv2iDe"
    "2egeWT5nenEm3fz2GX35k7Y8jI/0QD7YivtlZ8frLmyAKHKDvK8mStEvTkJ/fSye9dYi228j"
    "cn1NkORsqHD5du7GGbsXeGvk9NdzIe0qIZ1mQMzd9pzHoh0G6YzsyrIqePVof0McmtO2guus"
    "i7BjX4DrtQnhTp+8zDhGE5dzlOZOa0Cylo097YCkxAmDLZfRlGj1T4Mgo9HeugjEMbRxwXUz"
    "0uM4YNlqoI6XgnrujlE+RyNqWgOhjyZ/+H4F+hsj0SPwxGMSR33MJhmPTUPN+c/lkjK2Isff"
    "EpHeNriayYXnTgrSTq9DU/5REtkt1IR+Jhew6XbvNKhgU7c2xFiMj3QLFfLBO2SREE87cvDk"
    "Xhb6xXHIDTBHvN9u5F/Lwumf9BHrtgZJ537AzqNnERzNxT1xEXhsDfm0UZFjaCjgaCaIfls/"
    "0FFwYnx06A4kpYfBPa4H7ilrFBXnI+LkZgQzDJFAxI3tzqOouhPJJXcRkduIKM7uMT6LYjqr"
    "+8DnaAqGuytwwcMckR5bcf1GIVLDGODs1UVpsi14V+yx1jYAzEsinExuxIlEEcKjYhTkX4TO"
    "ykB4Ru9h6Y1MxMRGoLziJhLCWXD7nobiJBu0XLdHt+AXrNlzHiYH4mDNzsP+0/loqskG30ez"
    "Zxa3mUIpC9syERUdjuFhKbjJ8fBw2oW86O8gLmagt9rlFWW5bqgpdgXzLAcRUT6QPa4EOXEv"
    "ZjQo89HeHh0RoHjQ24OCwqsIDPJDRiwD9UWO6BO5v0KSz0CJqSFu2a1DV6EDHtUzIRu4PWkw"
    "MaNBlO/exqqqW8i7lo2gQF8UpDig4boTEfYgQh54WOOGGwYrMHQlA4MB/sj/cAkeCj0h6+eB"
    "vFuKacU9WB4mXG6sIjMrA+eCOShJZ0BUwkB0/tfgFpqjvdoZrQl70elwBFIvT0hXr0a1pgba"
    "4l0weCcRAl9tybu096gvWtSno7NU7nfKG2HhAeBlMnCXfxxOmQbI6/RHcJMlHNN18EBI8qdR"
    "IDUywsCqVWjU1YUkMQTtV/f/xeNoBL1NXNPY2Hj0XEgomCyWQn/5Eohr8iCpdIWQvw9R9T+i"
    "sDsQ7s0rcLCYgmrhAVQ6moJPpaBo/Uo0uzvhDyaDnCAtWakXXfcNdWVl5XTjr0z+tLTahh3W"
    "1lBfqKZ4fDcLTzsvoqvWBfuuLIareBlcmrRgl60OSe2v6KtzR3uqPXkcL2O4KwuVgQbyvJM0"
    "NpFTfV17i4qKyu9UKlX+jdlmmFmYwegjo4lFC+YOVIWsHXvWW0qejAIUCA7CLpWCXRffh+1l"
    "NTTUuBDhNMgeleORKAS3g41G047RE4mePkHjdQNf0j0oVIqcSqOOqKqqjs2bN09M5tcnHKT4"
    "Ck7pjbddO/JiqPUSJO2X0NoSi9SKnzHYkY5uHlMh9F81Xuyp1cWxXuBO1qwhrJyM+98JfUqw"
    "mdwNYR3hg6lCg0ObVE1THCjBN9nanRXems8JI+XeWtIytvaTfHetKicLNXtS9yXh49fE33js"
    "5kxNTmanNvVVmZqbT1hIoExtXZugQ9AjLCMsJdAJC94m/J+OvwEvkUu50Y2CpgAAACV0RVh0"
    "ZGF0ZTpjcmVhdGUAMjAwOS0xMS0yM1QxNTo1NzoxOSswMTowMPI1r4YAAAAldEVYdGRhdGU6"
    "bW9kaWZ5ADIwMDktMTEtMjNUMTU6NTc6MTkrMDE6MDCDaBc6AAAAGXRFWHRTb2Z0d2FyZQB3"
    "d3cuaW5rc2NhcGUub3Jnm+48GgAAAABJRU5ErkJggg==")
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
    b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAWJAAAFiQFtaJ36'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABiJJREFUaIHtml1IXEcY'
    b'ht8zc0Z3XWOza1ZjlEiNRCkRUeiFkItSelNKe9OLXiRCyUVbQmkI9CbQsgklIe4flkDA0pBQ'
    b'EZKYi8ZSSKHQNI3WRmPVKkpMsmviD5v4V1fjz54z04tk1qOu7jnRjQn0hY89urOc551vvvlm'
    b'D6sIIfAqi2w1wEb1yhtQrQzu6Oh4PxKJuPv7+388evToRKqgrMhUBi5cuGBramr6o7CwsKmo'
    b'qOiczWYLBYPBj1INZ0amDMzOzr47NTW1P/TwISKTUyA2exbn/GIgEDjn9/sdqYZcT6YMTE5O'
    b'iqGhIdy5dx8P7g4gg6lw7coHYewQgNs+n68yxZxrypQBXdeh6zo0TQMAKADSuA7XDjccTlcJ'
    b'gFa/33/8xIkTL3xTMH1DzjmMPUNRFDAIZGXYkbu7kKmMeRwOxy+1tbV5KSFdQ6YMaJoGzvnS'
    b'hwiJh0oIbAqQv7sQ213Z78RisS6/3/9eyohXyFIGgKcznzB0DS6XE0V797oppT/5/f5vz5w5'
    b'k54y8mcyXQNJDSgKwDlUAEXFxUrmtm1fzM/PtwSDwb0vjYH14GUIIQDOsTN3J7Kzsys5552B'
    b'QODIlhoAli8h+bpeUEqQk5ODnJwcuxCo9fl8V06fPu3cEgNWMkAIeWaAgjGGvLw87NlTBMbY'
    b'h5TSzkAgsH/LDABLM2+8XgmvqioYY2CMIS0tDW63GxUVFcjOzt6t6/pvXq/3eGNjI31hBoDl'
    b'fWA9E3LmJbwMh8OB8vJylJWVqaqqesLh8K9er7fghRiQfYAoZBW48ZoQAlVVV2XAGAUFBaiq'
    b'qoLT6XyLENLj8/k2dCg0nQEhxDJgI7hx9qWBRCbS09ORnp4Ol8uFqqoqlJSUvGaz2S96vd4f'
    b'nvdQaLGIkdAE8LQ7U0qTmjCaKS4uRmVlBfILCqoBtNfU1JSn2EBieGnAGEYj0oDMgDTFGIPT'
    b'6URpaSne2FdW6sjM/Mvn8x3B0/OiKZn+RhY3kOAZgLEG1jLCGIOqqvEJicVi4JyDUoo0xpDr'
    b'3gGWxtJHRkZrfT7f25qmHTp27Nh4Mi5r2+g6TzAS1cWyQ58hE5TS+P+N4zPtduTn7UT+60Uf'
    b'qIx1m1lSljvxRpXsMQ5TVWx3ZMCWuW0XgKRHEFNLSNf1pXNOEjAhRDw45/HQNC2+k2maFs+q'
    b'cbwQAhrnmIjOIDoxPiGE+H5TDGiaBkppfPlLEOPrSmAZxm9yuq4DQNyQNCLNzMdiuBcKITI8'
    b'fJ1zXu3xeIY2xYC8qRBizf1hJbQEl7XBOQchJH4t35fxaHwc3Z2d2vzc3Mm+vr5vLl++rJvh'
    b'Mr2E5M0Tzb4RSo5dCU8pjf8ts6VpGqanp9HX349wKBQWQhw8depUsxkmSwaWADlAV8PL65Wz'
    b'boRfaUDXddwPhfBPdzfm5ubqMzIyDns8nhkr8KYNGItYCCSEN46TEkJAVdV4VuR7MzMzuH37'
    b'NkZHR6cBHPb7/Q1WwS0boJSCCw6AJoQ3jjXCy7UvDQwPD6OtrQ2Li4uthJADwWDw/vPCmzYA'
    b'LPUBI3CibVUWuyxo2bSEEOjq6kIoFNIURTkZiURMF+qGDcglILdLIPHsJzKi6zrGx8fR2dmJ'
    b'2dnZQQAH6+rqbm4UXMryNmpsWMmk6zoGBwfR29sLAI2qqn569uzZyeeFTSRLRQzAlAE58z09'
    b'PQiHw9OKonx+/vz5+k3gXSVLGeCcQyhL/SChFAVPnszhz5ZmRKPRW0KIA/X19Xc3hTaBTB8l'
    b'kmVACAHK0jA0MoLW5pu6EMKflZX1dV1dXWyTmZfJcicGljpp/NhMKZ4sLKKjuQWR0ZEHiqJU'
    b'X7p06UbKqA2yvI1KxZsXgMePxtB64zo0Tbtit9s/aWho2NRCXU+Wi9iomcUYent6EB64E1UU'
    b'5curV69+t+mESWQ6A8Y1zxUFo4/H0XrjOhYXFtoIIQeampoGUkKYRKYMOBwOlpGZiUUuEI1G'
    b'0d/bi/DdAZ0QUjM2Nna8vb09pYW6nkwZWFhYGCzdV4Z/Z2bR334LI0NDDwkh1deuXfs91YDJ'
    b'pJj9qcHHn3z2Va7b/WZv198/T0xM1Le0tMylmM2UTBt4WfXK/9TgfwNbrf8AeoCaaIytiJUA'
    b'AAAASUVORK5CYII=')
getstart48Bitmap = start48.GetBitmap
#----------------------------------------------------------------------
pause48 = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAWJAAAFiQFtaJ36'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABg5JREFUaIHtmctrVFcc'
    b'x7/nvpyJEsk0SgUDJVIKA7bLUkoR0W6KumpTShfdCXUh3Yibdudf0GXALs3DSqWhq9KuXDeI'
    b'0mQI0kXQ0CTCjJm51zvn1UX7G39zcl+TBKzggWGGmTPf3/n8XuecGWGtxas8vJe9gP2O1wAv'
    b'ewRlE27fvh01Go3Poih6PwzDuhAi8DxPaK2VUipN07TV6/UWLl269Pcohu/evXvq6NGjn0dR'
    b'NOX7fuj7fmCMsVprqbXeSdP09/Pnz/9SpiOKinh5efnMkSNHfnr27NlEEAQIwxBBEEAIAaUU'
    b'pJSQUgJA0m63vzl37txslcWvrKzMA/g0SRI/DEOEYQjf92GtHWhqraG1/nNzc/PMhQsXtvO0'
    b'iiLg9Xq9HyYnJydWV1fRbreRBVur1XD69Ol6FEXfLy0t/Xrx4sW/ihZ/586dT5rN5gwA0Wq1'
    b'0O/3IYQYmiOEwLFjx9BsNptxHM8B+HhkgFu3br07Pj4+vbGxgW63m7ugXq+H5eVlNBqNQ2ma'
    b'fgngRhEAgK8ePXoknj59CmNM7qSNjQ0opWCt/Wh2dja8fPmyHAlAa93s9XpI03ToffIWj0aa'
    b'puh0OpBSvl2yeKRp+pZSatfis3Tb7TaCIDgE4BSA1ZEA4ji2UsqBsBACnucNGTLGDAzGcQwp'
    b'pS4DiOPYBMELs6RJusaYAZxSCmmawvM8kSlWBNDtdmUYhjh8+DB834fv+7sAhBADg91uF1LK'
    b'fhlAp9Ox9Xod9XodnucNdDnQfwUMKSXiOAaA3FzLBUiSRCVJglqthiiKcgHodbfbhTEmM08d'
    b'XWutxdjY2JBjaPAUSpIEOzs70FrnRraoBgah5Z6i9yiFyCh5rWzQPFo817XW7up0RYVeCEAL'
    b'E0IMGSJv0WdktMwQ17TWZgJkLbjssFkIYIwZeP8gAYwxuQA8LWkuT7HKAEqpIe/Tw60BMiSE'
    b'qJRCtCDXMVkAQRDsLwJuCuUBUDutEgVaUJZj3Mbged7eAaiIXW9RERtj9gxANeDqugDAvxF7'
    b'/vz56AAkwo3wlsdBqniKBsG6ui4Ad1DRKI2A6y0C8DwPSin4vg+tdWYLzHNKHgDZJQAOMjIA'
    b'GXNDzbsQTwdutEwTQGYK8TmUujwqIwHwGshqeTzvafuvAkDRytIlOF5Pxhi6c4wGQEKuMXc3'
    b'1lrD87yhQ1jZyGulHIAccmBdiBsDMIgCN16lBiineU25AHwDPZCjRBEARWCULlQWAa655xog'
    b'Y1neIgAyROmklCoFcJ3iRoA3DkpNsjkSAB0l8lIIwKB7FJ1VsgA4BC9kynnewq21u26FlQCA'
    b'F23RTSPes4uOwmWaLgTf4Xm3KxqlRcyNZRnKuh8UDZqXFd2stNz3cZoDEIRriICrAFARu5o8'
    b'Hbnj9nyc5hEgMe4x90xUJdxci78mCFcPOIALjStAi+dGgBc7bNnIunoSgNsyKVpF3S03NlUX'
    b'dFAjr9cfWATcqyN9xt+vsg9wx/Dv86MD19zzaZRqgIvSzkvC7mdVBr8AufAuBL3e107MPUEA'
    b'7mmUz6kC4H6Pa2Y5Zk+nUaXUYHvni6cdmorR/X2obLiLI136Po9wFc3SCLieovbJDY2SRsYY'
    b'7S6e3+jcFN33aZRE6cE3LnqMeKlX3CEUVYq2q7mfG5kGgH6/P2SMBi9o+rcGBT/CMgBDmjz/'
    b'aR/gAFJKGGMQBEHuD065+4AxpuV5HpIkGfIUdQt61lpje3ubQFfKAIwxq/1+H3EcD0WRa9Nj'
    b'Z2cH1tp4fX19PU8vNwILCwtrV69evQ/gvYcPH+L48eOo1WpDp0SlFLa2thDHMaanp3utVmup'
    b'DGBsbGx+amrq67W1NW98fByNRmPoPmCMQZIkePLkCU6ePIn19fWf5+bmcjeYXABrrb1+/foX'
    b'Dx48+HF7e7tJf+45cyClRBRFWydOnLiyuLj4uAzg5s2b965du/bt5ubmd0mS1MMw3DWHUmti'
    b'YuK3RqNxpUiv8F9KADh79mwwOTn5AYB3hBBZKfcYwL3FxcVO2eL5mJmZeVMI8aG19g33M2ut'
    b'9H3//vz8/B9lOqUA//fxyv9T/xrgZY9/AHkKG53TCUnyAAAAAElFTkSuQmCC')
getpause48Bitmap = pause48.GetBitmap
#----------------------------------------------------------------------
pause482 = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAWJAAAFiQFtaJ36'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABg5JREFUaIHtmctrVFcc'
    b'x7/nvpyJEsk0SgUDJVIKA7bLUkoR0W6KumpTShfdCXUh3Yibdudf0GXALs3DSqWhq9KuXDeI'
    b'0mQI0kXQ0CTCjJm51zvn1UX7G39zcl+TBKzggWGGmTPf3/n8XuecGWGtxas8vJe9gP2O1wAv'
    b'ewRlE27fvh01Go3Poih6PwzDuhAi8DxPaK2VUipN07TV6/UWLl269Pcohu/evXvq6NGjn0dR'
    b'NOX7fuj7fmCMsVprqbXeSdP09/Pnz/9SpiOKinh5efnMkSNHfnr27NlEEAQIwxBBEEAIAaUU'
    b'pJSQUgJA0m63vzl37txslcWvrKzMA/g0SRI/DEOEYQjf92GtHWhqraG1/nNzc/PMhQsXtvO0'
    b'iiLg9Xq9HyYnJydWV1fRbreRBVur1XD69Ol6FEXfLy0t/Xrx4sW/ihZ/586dT5rN5gwA0Wq1'
    b'0O/3IYQYmiOEwLFjx9BsNptxHM8B+HhkgFu3br07Pj4+vbGxgW63m7ugXq+H5eVlNBqNQ2ma'
    b'fgngRhEAgK8ePXoknj59CmNM7qSNjQ0opWCt/Wh2dja8fPmyHAlAa93s9XpI03ToffIWj0aa'
    b'puh0OpBSvl2yeKRp+pZSatfis3Tb7TaCIDgE4BSA1ZEA4ji2UsqBsBACnucNGTLGDAzGcQwp'
    b'pS4DiOPYBMELs6RJusaYAZxSCmmawvM8kSlWBNDtdmUYhjh8+DB834fv+7sAhBADg91uF1LK'
    b'fhlAp9Ox9Xod9XodnucNdDnQfwUMKSXiOAaA3FzLBUiSRCVJglqthiiKcgHodbfbhTEmM08d'
    b'XWutxdjY2JBjaPAUSpIEOzs70FrnRraoBgah5Z6i9yiFyCh5rWzQPFo817XW7up0RYVeCEAL'
    b'E0IMGSJv0WdktMwQ17TWZgJkLbjssFkIYIwZeP8gAYwxuQA8LWkuT7HKAEqpIe/Tw60BMiSE'
    b'qJRCtCDXMVkAQRDsLwJuCuUBUDutEgVaUJZj3Mbged7eAaiIXW9RERtj9gxANeDqugDAvxF7'
    b'/vz56AAkwo3wlsdBqniKBsG6ui4Ad1DRKI2A6y0C8DwPSin4vg+tdWYLzHNKHgDZJQAOMjIA'
    b'GXNDzbsQTwdutEwTQGYK8TmUujwqIwHwGshqeTzvafuvAkDRytIlOF5Pxhi6c4wGQEKuMXc3'
    b'1lrD87yhQ1jZyGulHIAccmBdiBsDMIgCN16lBiineU25AHwDPZCjRBEARWCULlQWAa655xog'
    b'Y1neIgAyROmklCoFcJ3iRoA3DkpNsjkSAB0l8lIIwKB7FJ1VsgA4BC9kynnewq21u26FlQCA'
    b'F23RTSPes4uOwmWaLgTf4Xm3KxqlRcyNZRnKuh8UDZqXFd2stNz3cZoDEIRriICrAFARu5o8'
    b'Hbnj9nyc5hEgMe4x90xUJdxci78mCFcPOIALjStAi+dGgBc7bNnIunoSgNsyKVpF3S03NlUX'
    b'dFAjr9cfWATcqyN9xt+vsg9wx/Dv86MD19zzaZRqgIvSzkvC7mdVBr8AufAuBL3e107MPUEA'
    b'7mmUz6kC4H6Pa2Y5Zk+nUaXUYHvni6cdmorR/X2obLiLI136Po9wFc3SCLieovbJDY2SRsYY'
    b'7S6e3+jcFN33aZRE6cE3LnqMeKlX3CEUVYq2q7mfG5kGgH6/P2SMBi9o+rcGBT/CMgBDmjz/'
    b'aR/gAFJKGGMQBEHuD065+4AxpuV5HpIkGfIUdQt61lpje3ubQFfKAIwxq/1+H3EcD0WRa9Nj'
    b'Z2cH1tp4fX19PU8vNwILCwtrV69evQ/gvYcPH+L48eOo1WpDp0SlFLa2thDHMaanp3utVmup'
    b'DGBsbGx+amrq67W1NW98fByNRmPoPmCMQZIkePLkCU6ePIn19fWf5+bmcjeYXABrrb1+/foX'
    b'Dx48+HF7e7tJf+45cyClRBRFWydOnLiyuLj4uAzg5s2b965du/bt5ubmd0mS1MMw3DWHUmti'
    b'YuK3RqNxpUiv8F9KADh79mwwOTn5AYB3hBBZKfcYwL3FxcVO2eL5mJmZeVMI8aG19g33M2ut'
    b'9H3//vz8/B9lOqUA//fxyv9T/xrgZY9/AHkKG53TCUnyAAAAAElFTkSuQmCC')
getpause482Bitmap = pause482.GetBitmap
#----------------------------------------------------------------------
stop48 = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAWJAAAFiQFtaJ36'
    b'AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABI1JREFUaIHtmb9PJDcU'
    b'x589q50VixgKtAhtE5IrufwH/AVUtClPSmqkKMXpQpe0K6WKlP7yJ1DxF9AgURDlFKGtAAEj'
    b'YAaYXc2MneLyVm89zx577yKEdJYse3dm7O/H74c9u0JrDS+5yOcW8KnlC8Bzl47twsHBwess'
    b'y36YTCZfCyFkFEVSSimFEFJKKT52hcA+ANAWAEAYQ2qlFLYaW6WU1lrTvlJKqbquldZaxXH8'
    b'odfr/bG7u/sXp1NwQXx0dPT7YDD4vizL6O7uDrTWIKUEIQQIIWZ97jta59RrPVeVUo2++Z0Q'
    b'ApaXl0EIUV9fX/+2vb39YyvA4eHh683NzeNerxcdHx/D7e0t/Ldy1mKK9S1tGVBKCUmSwNbW'
    b'FhRFUY3H4293dnbmLNFwoYuLizdra2vR6ekp3NzcLCTscxWlFKRpCicnJzAcDjuXl5dvAOAn'
    b'ek8DIE3Tr87OziDP84Untllk0T3n/v4elFKQ5/kr81oDoCgKyLKsdTIUaWttBce1tVxRSkGW'
    b'ZVAUReMaB1DleQ79fr8hhgtSM2B9AbBPAWg1n3l4eICiKKpWgOl0WuV5DktLSw3BXKWifYOZ'
    b'W/22muc5TKfTdoC6rqGqPt4XRdHCAFwaXRRAKQVVVUFd143FaABgLpZSzqoPgI8b+bqPKV5K'
    b'Oet7ASilIIqimQVcECZASBC3AeBmhpq8AHBAKeWcC/lAhAL4iNdaQ13X1izVAMABOBeyQdgA'
    b'sB/q/1Q8dSEOwmoBlwuZn1FsSBBzABh/VLwQAqIo8reALYhdECZAWxBzAHTVTf8PCmKtNVRV'
    b'NRPpA/GpAC7xOF5VVWEuhKajIG3BzB2jubHN2iYer3PFmka51feFwGILYp+0ic+jluA0yon2'
    b'haDi6ZguAFM8fSbIAjR12azQBhEKwImnn9ECXjFAU5kZsDYo3zjwFY866HhBWQgf5kS7YiMU'
    b'AAXZ3AMLAgZnIdfqt0HgxFQgJ55bfU5HUBbCgW25PwSCivERT0XjBoZjBWUhWxxw/s4B2QCo'
    b'CNPPTdF09YOzEK4QtQbt+7iWbVxuTm4OqiEoC5npzAXhgjHHtYluE8/psgK4aE0gG6QJQbNN'
    b'2/NccVmv8eOu6W/c+Z22n6P4zOH9PoCmMk+Mtta1KZknTtrS6jNH8FmIm4gTy5mXXudEmIvk'
    b'M1dQFjKPuK6Tout526JwIGafzu1KpdYgxhfptk3HrHhf20bmqiZQXdfWILbuxNTnXNs9FWdu'
    b'TC5YmzU4iKCfVczAQwCbaGrikMOczXVsMFSbE0ApVUdR1DAb5yqc2/ge5kx3cgEQd278ttgA'
    b'6Ha7H5IkgcfHR1hZWWlddXz54YRzAHQcM2htME9PT5AkCWRZ9ncrwHA4/DOO47dlWfbOz8+h'
    b'3+9Dp9OZO9+YLzMo1nYMsFkBP1PR9LuyLGf/CQwGg0kcx+9NveyffKPR6F2WZT9fXV310jS1'
    b'5uD/u0gpYXV1FTY2NiZJkvyyt7f3q3kPCwAAsL+//814PP5uMpm8guf7P1l1u91/1tfX349G'
    b'ozPuBivASykv/p/6LwDPXf4FvGzk3242JygAAAAASUVORK5CYII=')
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
		self.SetToolTip(string)
class TextCtrlNew(wx.TextCtrl):
	def __init__(self, parent, id=wx.ID_ANY, value="", style=wx.ALIGN_LEFT|wx.TE_PROCESS_ENTER, size=(-1,-1)):
		wx.TextCtrl.__init__(self, parent, id, value=value, style=style, size=size)
	def SetToolTipNew(self, string):
		self.SetToolTip(string)
class ButtonNew(wx.Button):
	def __init__(self, parent, id=wx.ID_ANY, label="", style=wx.ALIGN_LEFT, size=(-1,-1)):
		wx.Button.__init__(self, parent, id, label=label, style=style, size=size)
	def SetToolTipNew(self, string):
		self.SetToolTip(string)
class BitmapButtonNew(wx.BitmapButton):
	def __init__(self, parent, id=wx.ID_ANY, bitmap=wx.NullBitmap, style=wx.ALIGN_LEFT, size=(-1,-1)):
		wx.BitmapButton.__init__(self, parent, id, bitmap=bitmap, style=style, size=size)
	def SetToolTipNew(self, string):
		self.SetToolTip(string)
class CheckBoxNew(wx.CheckBox):
	def __init__(self, parent, id=wx.ID_ANY, label="", style=wx.ALIGN_LEFT, size=(-1,-1)):
		wx.CheckBox.__init__(self, parent, id, label=label, style=style, size=size)
	def SetToolTipNew(self, string):
		self.SetToolTip(string)
class RadioBoxNew(wx.RadioBox):
	def __init__(self, parent, id=wx.ID_ANY, label="", size=(-1,-1), choices=[], majorDimension=0, style=wx.ALIGN_LEFT):
		wx.RadioBox.__init__(self, parent, id, label=label, size=size, choices=choices, majorDimension=majorDimension, style=style)
	def SetToolTipNew(self, string):
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
		self.value = TextCtrlNew(parent, value=str(sinit),size=(sinitw, -1), style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT)
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
	def SetToolTip(self, string):
		self.label.SetToolTipNew(string)
		self.value.SetToolTipNew(string)
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
		self.value = TextCtrlNew(parent, value=str(init), style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT)
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
class CheckListCtrlAutoWidth:
	def __init__(self):
		self._resizeColMinWidth = None
		self._resizeColStyle = "LAST"
		self._resizeCol = 0
		self.Bind(wx.EVT_SIZE, self._onResize)
		self.Bind(wx.EVT_LIST_COL_END_DRAG, self._onResize, self)
	def setResizeColumn(self, col):
		if col == "LAST":
			self._resizeColStyle = "LAST"
		else:
			self._resizeColStyle = "COL"
			self._resizeCol = col
	def resizeLastColumn(self, minWidth):
		self.resizeColumn(minWidth)
	def resizeColumn(self, minWidth):
		self._resizeColMinWidth = minWidth
		self._doResize()
	def _onResize(self, event):
		if 'gtk2' in wx.PlatformInfo or 'gtk3' in wx.PlatformInfo:
			self._doResize()
		else:
			wx.CallAfter(self._doResize)
		event.Skip()
	def _doResize(self):
		if not self:
			return
		if self.GetSize().height < 32:
			return
		numCols = self.GetColumnCount()
		if numCols == 0: return
		if(self._resizeColStyle == "LAST"):
			resizeCol = self.GetColumnCount()
		else:
			resizeCol = self._resizeCol
		resizeCol = max(1, resizeCol)
		if self._resizeColMinWidth is None:
			self._resizeColMinWidth = self.GetColumnWidth(resizeCol - 1)
		listWidth = self.GetClientSize().width
		totColWidth = 0
		for col in range(numCols):
			if col != (resizeCol-1):
				totColWidth = totColWidth + self.GetColumnWidth(col)
		resizeColWidth = self.GetColumnWidth(resizeCol - 1)
		if totColWidth + self._resizeColMinWidth > listWidth:
			self.SetColumnWidth(resizeCol-1, self._resizeColMinWidth)
			return
		self.SetColumnWidth(resizeCol-1, listWidth - totColWidth)
class CheckListCtrlImg(object):
	def __init__(self, check_image=None, uncheck_image=None, imgsz=(16,16)):
		if check_image is not None:
			imgsz = check_image.GetSize()
		elif uncheck_image is not None:
			imgsz = check_image.GetSize()
		self.__imagelist_ = wx.ImageList(*imgsz)
		if check_image is None:
			check_image = self.__CreateBitmap(wx.CONTROL_CHECKED, imgsz)
		if uncheck_image is None:
			uncheck_image = self.__CreateBitmap(0, imgsz)
		self.uncheck_image = self.__imagelist_.Add(uncheck_image)
		self.check_image = self.__imagelist_.Add(check_image)
		self.AssignImageList(self.__imagelist_, wx.IMAGE_LIST_SMALL)
		self.__last_check_ = None
		self.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown_)
		self._origInsertItem = self.InsertItem
		self.InsertItem = self.__InsertItem_
	def __InsertItem_(self, *args, **kw):
		index = self._origInsertItem(*args, **kw)
		self.SetItemImage(index, self.uncheck_image)
		return index
	def __CreateBitmap(self, flag=0, size=(16, 16)):
		bmp = wx.Bitmap(*size)
		dc = wx.MemoryDC(bmp)
		dc.SetBackground(wx.WHITE_BRUSH)
		dc.Clear()
		wx.RendererNative.Get().DrawCheckBox(self, dc,
											 (0, 0, size[0], size[1]), flag)
		dc.SelectObject(wx.NullBitmap)
		return bmp
	def __OnLeftDown_(self, evt):
		(index, flags) = self.HitTest(evt.GetPosition())
		if flags == wx.LIST_HITTEST_ONITEMICON:
			img_idx = self.GetItem(index).GetImage()
			flag_check = img_idx == 0
			begin_index = index
			end_index = index
			if self.__last_check_ is not None \
					and wx.GetKeyState(wx.WXK_SHIFT):
				last_index, last_flag_check = self.__last_check_
				if last_flag_check == flag_check:
					item_count = self.GetItemCount()
					if last_index < item_count:
						if last_index < index:
							begin_index = last_index
							end_index = index
						elif last_index > index:
							begin_index = index
							end_index = last_index
						else:
							assert False
			while begin_index <= end_index:
				self.CheckItem(begin_index, flag_check)
				begin_index += 1
			self.__last_check_ = (index, flag_check)
		else:
			evt.Skip()
	def OnCheckItem(self, index, flag):
		pass
	def IsChecked(self, index):
		return self.GetItem(index).GetImage() == 1
	def CheckItem(self, index, check=True):
		img_idx = self.GetItem(index).GetImage()
		if img_idx == 0 and check:
			self.SetItemImage(index, 1)
			self.OnCheckItem(index, True)
		elif img_idx == 1 and not check:
			self.SetItemImage(index, 0)
			self.OnCheckItem(index, False)
	def ToggleItem(self, index):
		self.CheckItem(index, not self.IsChecked(index))
class CheckListCtrl(wx.ListCtrl, CheckListCtrlImg, CheckListCtrlAutoWidth):
	def __init__(self, parent, id, bmpsize=(24,24), size=(180,1)):
		wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL, size=(180,1))
		CheckListCtrlAutoWidth.__init__(self)
		bmpchk = getpipelineok24Bitmap()
		bmpunchk = getpipelineignore24Bitmap()
		CheckListCtrlImg.__init__(self,check_image=bmpchk,uncheck_image=bmpunchk, imgsz=bmpsize)
	def CheckItem(self, idx, check=True):
		CheckListCtrlImg.CheckItem(self, idx, check)
class CustomAboutDialog(wx.Dialog):
	def __init__(self, parent, info):
		wx.Dialog.__init__(self, parent, title="About Bonsu", size=(460,300))
		self.SetSizeHints(450,300,-1,-1)
		self.parent = parent
		self.info  = info
		self.vboxborder = wx.BoxSizer(wx.VERTICAL)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.icon = wx.Image(os.path.join(os.path.dirname(os.path.dirname(__file__)),'image',  'bonsu.ico'), wx.BITMAP_TYPE_ICO)
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
