# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pygments.lexers import _mapping

def setup(*args):
    _mapping.LEXERS['BuildoutLexer'] = (
        'sphinxcontrib.infrae.buildout', 'BUILDOUT', ('buildout',), ('*.cfg',), ('text/x-buildout',))

