#############################################
##   Filename: pyscript.py
##
##    Copyright (C) 2018 Marcus C. Newton
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
from __future__ import print_function
import __builtin__
__print = __builtin__.print
def run_script(obj, global_dict, local_dict):
	global_dict.update(globals())
	local_dict.update(locals())
	self = global_dict['self']
	def printnew(w):
		self.ancestor.GetPage(0).queue_info.put(w)
	global_dict['print'] = printnew
	exec(obj, global_dict, local_dict)
