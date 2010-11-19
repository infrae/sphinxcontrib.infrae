# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pygments.lexers import _mapping
from sphinxcontrib.infrae.autointerface import InterfaceDesc, InterfaceDocumenter

def setup(app):
    app.add_directive_to_domain('py', 'interface', InterfaceDesc)
    app.add_autodocumenter(InterfaceDocumenter)

    _mapping.LEXERS['BuildoutLexer'] = (
        'sphinxcontrib.infrae.buildout', 'BUILDOUT', ('buildout',), ('*.cfg',), ('text/x-buildout',))

