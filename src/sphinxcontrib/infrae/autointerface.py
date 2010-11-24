# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator
import types
from sphinx.util.docstrings import prepare_docstring
from sphinx.util import force_decode
from sphinx.domains.python import PyClasslike, PyXRefRole
from sphinx.ext import autodoc

from zope.interface import Interface
from zope.component.interfaces import IObjectEvent


class PyInterface(PyClasslike):
    objtype = 'interface'

    def get_index_text(self, modname, name):
        return '%s (interface in %s)' % (name[0], modname)

class PyEvent(PyClasslike):
    objtype = 'event'

    def get_index_text(self, modname, name):
        return '%s (event in %s)' % (name[0], modname)


class AbstractInterfaceDocumenter(autodoc.ClassDocumenter):
    """Abstract documenter directive for interfaces.
    """
    _document_members = True
    _document_interface = Interface
    objtype = 'interface'
    # Must be a higher priority than ClassDocumenter and InterfaceDocumenter
    member_order = 10

    option_spec = dict(autodoc.ClassDocumenter.option_spec)
    option_spec['sort-members'] = autodoc.bool_option
    option_spec['nodocstring'] = autodoc.bool_option

    def __init__(self, *args, **kwargs):
        super(AbstractInterfaceDocumenter, self).__init__(*args, **kwargs)
        self.options.members = autodoc.ALL
        self.options.show_inheritance = True
        self.options.sort_members = True

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return (isinstance(member, types.ClassType) and
                issubclass(member, cls._document_interface))

    def add_directive_header(self, sig):
        name = self.object.getName()
        module = self.object.__module__
        objtype = self.objtype
        directive_name = '<auto%s>' % objtype

        self.add_line(u'.. py:%s:: %s' % (objtype, name), directive_name)
        if self.options.noindex:
            self.add_line(u'   :noindex:', directive_name)
        if self.objpath:
            self.add_line(u'   :module: %s' % module, directive_name)

    def add_content(self, more_content, no_docstring=False):
        autodoc.Documenter.add_content(self, more_content, self.options.nodocstring)
        objtype = self.objtype
        directive_name = '<auto%s>' % objtype
        bases = [base for base in self.object.__bases__
                 if base.extends(self._document_interface)]

        if bases:
            self.add_line(u'', directive_name)
            self.add_line(u'This %s extends:' % objtype, directive_name)
            self.add_line(u'', directive_name)
            for base in bases:
                self.add_line(
                    u'- :py:%s:`%s.%s`' % (objtype, base.__module__, base.getName()),
                    directive_name)
                self.add_line(u'', directive_name)

    def format_args(self):
        return ""

    def document_members(self, all_members=True):
        if not self._document_members:
            return

        oldindent = self.indent
        members = self.object.namesAndDescriptions()
        directive_name = '<auto%s>' % self.objtype

        if self.options.sort_members:
            members.sort(key=operator.itemgetter(0))

        attributes = []
        methods = []
        for name, description in members:
            signature = getattr(description, 'getSignatureString', None)
            if signature is None:
                attributes.append((name, description))
            else:
                methods.append((name, description, signature()))

        def add_docstring(description):
            docstring = description.getDoc()
            if docstring:
                self.add_line(u'', directive_name)
                self.indent += self.content_indent
                source_name = u'docstring of %s.%s' % (self.fullname, name)
                docstring = [prepare_docstring(force_decode(docstring, None))]
                for i, line in enumerate(self.process_doc(docstring)):
                    self.add_line(line, source_name, i)
                self.add_line(u'', directive_name)
                self.indent = oldindent

        if attributes:
            self.add_line(u'Available attributes:', directive_name)
            for name, description in attributes:
                self.add_line(u'', directive_name)
                self.add_line(u'.. attribute:: %s' % name, directive_name)
                add_docstring(description)

        if methods:
            self.add_line(u'Available methods:', directive_name)
            for name, description, signature in methods:
                self.add_line(u'', directive_name)
                self.add_line(u'.. method:: %s%s' % (name, signature), directive_name)
                add_docstring(description)


class EventDocumenter(AbstractInterfaceDocumenter):
    """Specialized Documenter directive for zope events.
    """
    _document_members = False
    _document_interface = IObjectEvent
    objtype = 'event'
    # Must be a higher priority than ClassDocumenter and InterfaceDocumenter
    member_order = 5


class InterfaceDocumenter(AbstractInterfaceDocumenter):
    """Specialized Documenter directive for zope events.
    """
    _document_members = True
    _document_interface = Interface
    objtype = 'interface'
    # Must be a higher priority than ClassDocumenter
    member_order = 10



def setup(app):
    app.add_directive_to_domain('py', 'interface', PyInterface)
    app.add_role_to_domain('py', 'interface', PyXRefRole())
    app.add_autodocumenter(InterfaceDocumenter)
    app.add_directive_to_domain('py', 'event', PyEvent)
    app.add_role_to_domain('py', 'event', PyXRefRole())
    app.add_autodocumenter(EventDocumenter)

