# Options.py
# $Id: Options.py,v 1.18 2001/07/14 23:26:27 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# Eventually this will hold all program options, and maybe be incorporated
# into some sort of options editor.  (Hopefully)
#
# For now, it holds information about what the program should and shouldn't
# do.  Variable names should be pretty self explanatory.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#############################################################################
import os
from string import *
import Cache
import Associations

class Options:
    def __init__(self, *args):
        # Default values for some important options...
        self.ip_cache = {}
        self.cache = Cache.Cache()
        self.associations = Associations.Associations()
        self.setDefaultOpts()
        self.greenLight()
        return None

    # Accessors/Mutators
    
    def getCache(self):
        return self.cache
    
    def setCache(self, newcache):
        self.cache = newcache
        return self.getCache()
    
    def getAssociations(self):
        return self.associations
    
    def setAssociations(self, newassoc):
        self.associations = newassoc
        return self.getAssociations()

    def getIP(self, hostname):
        """Return the cached IP of hostname.  May throw KeyError"""
        return self.ip_cache[hostname]
    
    def setIP(self, hostname, IP):
        self.ip_cache[hostname] = IP
        return self.getIP(hostname)

    def save(self, alternate_filename=None):
        """Saves all options to the prefs directory/forgrc unless an
        alternate filename is specified.  Throws all IOErrors out"""
        if not alternate_filename:
            prefs = self.getOption('prefs_directory')
            filename = "%s%s%s" % (prefs, os.sep, "forgrc")
        else:
            filename = alternate_filename

        fp = open(filename, "w")
        fp.write(self.toString())
        fp.flush()
        fp.close()
        return 1
    
    def toggle(self, key):
        """Flip the value of the option specified by key.  If it was true,
        it becomes false, and if it was false, it becomes true."""
        try:
            val = self.opts[key]

            if val:
                print "Toggle(%s): FALSE" % key
                self.opts[key] = None
            else:
                print "Toggle(%s): TRUE" % key
                self.opts[key] = 1
        except:
            print "Toggle(%s): TRUE" % key
            self.opts[key] = 1
        return self.opts[key]
            
    def greenLight(self):
        """Set the green light.  This is used for thread synchronization"""
        self.GREEN_LIGHT = 1
        return self.GREEN_LIGHT
    
    def redLight(self):
        """Turn off the green light.  For thread synchronization."""
        self.GREEN_LIGHT = None
        return self.GREEN_LIGHT
    
    def exists(self, filename):
        """Returns true if filename exists, false otherwise."""
        try:
            stuff = os.stat(filename)
            return 1
        except OSError:
            return None
        return None
            
    def setDefaultOpts(self):
        """Sets default set of options so that the structure is not empty."""
        self.opts = {}

        if os.sep == '\\':
            # Ugly hack for windows.  Some versions of windows
            # yield c:\ for the home directory, and some return something
            # really screwed up like \ or c\ even.
            self.opts['prefs_directory'] = "C:\\FORG-DATA"
        else:
            self.opts['prefs_directory'] = "%s%s%s" % (os.path.expanduser("~"),
                                                       os.sep, ".forg")

        self.opts['home'] = "gopher://gopher.floodgap.com:70/1/"
            
        if not self.exists(self.opts['prefs_directory']):
            os.mkdir(self.opts['prefs_directory'])

        self.opts['use_cache']                   = 1
        self.opts['delete_cache_on_exit']        = None
        self.opts['use_url_format']              = 1
        self.opts['grab_resource_info']          = None
        self.opts['show_host_port']              = None
        self.opts['save_options_on_exit']        = 1
        self.opts['strip_carraige_returns']      = 1
        self.opts['show_cached']                 = None
        self.opts['display_info_in_directories'] = None
        self.opts['use_PIL']                     = 1  # Use PIL for images

        basedir = self.getOption('prefs_directory')

        pkey = 'prefs_directory'

        self.opts['cache_directory'] = "%s%s%s" % (self.opts[pkey],
                                                   os.sep,
                                                   "cache")

        if not self.exists(self.opts['cache_directory']):
            os.mkdir(self.opts['cache_directory'])
        
        self.opts['cache_prefix'] = "%s%s" % (self.opts['cache_directory'],
                                              os.sep)
        return None

    def makeToggleWrapper(self, keyname):
        """Returns a function which when called with no arguments toggles the
        value of keyname within the options structure.  This is used for menu
        callbacks connected to check buttons."""

        def toggle_wrapper(opts=self, key=keyname):
            return opts.toggle(key)
        
        return toggle_wrapper

    def setOption(self, optionname, optionvalue):
        """Set optionname to optionvalue"""
        self.opts[optionname] = optionvalue
        return self.getOption(optionname)
        
    def getOption(self, optionname):
        """Get an option named optionname."""
        try:
            optionname = lower(optionname)
            return self.opts[optionname]
        except KeyError:
            return None
        
    def toString(self):
        """Returns string representation of the object."""
        return self.__str__()

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        # God I love the map() function.
        lines = map(lambda x, self=self: "%s = %s" % (x, self.opts[x]),
                    self.opts.keys())
        comments = "%s%s%s" % ("# Options for the FORG\n",
                               "# Please don't edit me unless you know what\n",
                               "# you're doing.\n")
        return comments + join(lines, "\n") + "\n"
    
    def parseFile(self, filename):
        """Parse filename into a set of options.  Caller is responsible
        for catching IOError related to reading files."""
        print "Previously had %d keys" % len(self.opts.keys())
        self.setDefaultOpts()
        fp = open(filename, "r")

        line = fp.readline()
        line_num = 0
        while line != '':
            line_num = line_num + 1
            commentIndex = find(line, "#")
            if commentIndex != -1:
                line = line[0:commentIndex]

            line = strip(line)
            
            if line == '':             # Nothing to grokk
                line = fp.readline()   # Get next line...
                continue
            
            items = split(line, "=")
            if len(items) < 2:
                print "Options::parseFile: no '=' on line number %d" % line_num
                line = fp.readline()   # Get next line...
                continue
            if len(items) > 2:
                print("Options::parseFile: too many '=' on line number %d" %
                      line_num)
                line = fp.readline()   # Get next line...
                continue
            
            key = lower(strip(items[0]))       # Normalize and lowercase
            val = lower(strip(items[1]))

            # Figure out what the hell val should be
            if val == 'no' or val == 'none' or val == 0 or val == '0':
                val = None
                
            self.opts[key] = val
            line = fp.readline()

        return self

# Here is one instance of an options structure.
# This is used by TkGui and other modules as a centralized place
# to store program options.
program_options = Options()

