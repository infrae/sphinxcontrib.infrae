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


class PyInterface(PyClasslike):
    objtype = 'interface'

    def get_index_text(self, modname, name):
        return '.'.join((modname, name[0])) + u' (interface)'


class InterfaceDocumenter(autodoc.ClassDocumenter):
    """Specialized Documenter directive for zope interfaces.
    """
    objtype = "interface"
    # Must be a higher priority than ClassDocumenter
    member_order = 10

    def __init__(self, *args, **kwargs):
        super(InterfaceDocumenter, self).__init__(*args, **kwargs)
        self.options.members=autodoc.ALL
        self.options.show_inheritance=True
        self.options.sort_members=True

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, types.ClassType) and \
                issubclass(member, Interface)

    def add_directive_header(self, sig):
        name = self.object.getName()
        module = self.object.__module__
        self.add_line(u'.. py:interface:: %s' % name, '<autointerface>')
        if self.options.noindex:
            self.add_line(u'   :noindex:', '<autointerface>')
        if self.objpath:
            self.add_line(u'   :module: %s' % module, '<autointerface>')

    def add_content(self, more_content, no_docstring=False):
        autodoc.ClassDocumenter.add_content(self, more_content, no_docstring)
        bases = [base for base in self.object.__bases__ if base is not Interface]
        if bases:
            self.add_line(u'This interface extends:', '<autointerface>')
            self.add_line(u'', '<autointerface>')
            for base in bases:
                self.add_line(u'- :py:interface:`%s.%s`' % (base.__module__, base.getName()), '<autointerface>')
                self.add_line(u'', '<autointerface>')

    def format_args(self):
        return ""

    def document_members(self, all_members=True):
        oldindent = self.indent
        members = self.object.namesAndDescriptions()
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
                self.add_line(u'', '<autointerface>')
                self.indent += self.content_indent
                source_name = u'docstring of %s.%s' % (self.fullname, name)
                docstring = [prepare_docstring(force_decode(docstring, None))]
                for i, line in enumerate(self.process_doc(docstring)):
                    self.add_line(line, source_name, i)
                self.add_line(u'', '<autointerface>')
                self.indent = oldindent

        if attributes:
            self.add_line(u'Interface attributes:', '<autointerface>')
            for name, description in attributes:
                self.add_line(u'', '<autointerface>')
                self.add_line(u'.. attribute:: %s' % name, '<autointerface>')
                add_docstring(description)

        if methods:
            self.add_line(u'Interface methods:', '<autointerface>')
            for name, description, signature in methods:
                self.add_line(u'', '<autointerface>')
                self.add_line(u'.. method:: %s%s' % (name, signature), '<autointerface>')
                add_docstring(description)


def setup(app):
    app.add_directive_to_domain('py', 'interface', PyInterface)
    app.add_role_to_domain('py', 'interface', PyXRefRole())
    app.add_autodocumenter(InterfaceDocumenter)

