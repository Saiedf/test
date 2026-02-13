# -*- coding: utf-8 -*-
from __future__ import absolute_import
#
# Created by iet5
import sys
import gettext
from os import environ, path

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import getDesktop, addFont, eEnv

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


PluginLanguageDomain = path.split(path.dirname(path.realpath(__file__)))[-1]
isDreamOS = path.isdir(eEnv.resolve("${sysconfdir}/dpkg"))


def getFullPath(fname):
    """Get full path of a plugin file"""
    return resolveFilename(SCOPE_PLUGINS, path.join('Extensions', PluginLanguageDomain, fname))


def localeInit():
    """Initialize plugin language"""
    try:
        environ['LANGUAGE'] = language.getLanguage()[:2]
    except Exception:
        pass
    gettext.bindtextdomain(PluginLanguageDomain, getFullPath('locale'))


try:
    ScreenWidth = getDesktop(0).size().width()
except Exception:
    ScreenWidth = 720
ScreenWidth = '1080' if ScreenWidth >= 1920 else '720'


try:
    plugin_skin = ET.parse(getFullPath('skin/%s.xml' % ScreenWidth)).getroot()
except Exception as e:
    print("[EPGImport] Error loading skin: %s" % str(e))
    plugin_skin = None


def getSkin(skinName):
    """Retrieve specific skin XML element as string (Py2/Py3 safe)"""
    if plugin_skin is not None:
        try:
            skin_element = plugin_skin.find('.//screen[@name="%s"]' % skinName)
            if skin_element is not None:
                # Py3: tostring(..., encoding='utf-8') -> bytes
                # Py2: tostring(..., encoding='utf-8') -> str (bytes)
                data = ET.tostring(skin_element, encoding='utf-8', method='xml')
                # Py3: tostring returns bytes -> decode
                if sys.version_info[0] >= 3 and isinstance(data, (bytes, bytearray)):
                    return data.decode('utf-8', 'ignore')
                # Py2: return bytes/str
                return data
        except Exception as e:
            print("[EPGImport] Error getting skin %s: %s" % (skinName, str(e)))
    return ''


def _(txt):
    """Translation helper compatible with Python 2.7 and Python 3 (safe for DreamOS)"""
    if not txt:
        return ''

    try:
        t = gettext.dgettext(PluginLanguageDomain, txt)
    except Exception:
        return txt

    # Python 2 behavior differs between images:
    # - DreamOS (Dreambox): safest is to keep 'str' (bytes) and NOT return unicode
    # - Other images: decoding fixes Arabic mojibake (Ø§Ù...)
    if sys.version_info[0] < 3:
        if isDreamOS:
            return t  # keep bytes to avoid GS on DreamOS
        # Non-DreamOS: try to decode to unicode for correct Arabic rendering
        try:
            if isinstance(t, str):
                return t.decode('utf-8')
        except Exception:
            return t
        return t

    # Python 3: gettext returns str (unicode)
    return t


try:
    addFont(getFullPath('skin/epgimport.ttf'), 'EPGImport', 100, False)
except Exception as e:
    print("[EPGImport] Error adding font: %s" % str(e))
    try:
        # Fallback for openPLI-based images
        addFont(getFullPath('skin/epgimport.ttf'), 'EPGImport', 100, False, 0)
    except Exception as e2:
        print("[EPGImport] Error adding font (fallback): %s" % str(e2))


localeInit()
language.addCallback(localeInit)
