import copy
from urllib.parse import urlsplit, urlunsplit

from django.http import QueryDict
from django.urls import reverse


class URL:
    def __init__(
        self, url=None, netloc=None, path=None, port=None, query_string=None,
        query=None, scheme=None, viewname=None
    ):
        if path and viewname:
            raise RuntimeError(
                'The arguments `path` and `viewname` are mutually exclusive.'
            )

        if viewname:
            path = reverse(viewname=viewname)

        # `url` argument defaults to '' to force `urlsplit` to return empty
        # strings and not bytes.
        self._split_result = urlsplit(url=url or '')

        self._netloc = netloc
        self._path = path
        self._port = port
        self._scheme = scheme

        if self._split_result:
            if not self._netloc:
                self._netloc = self._split_result.netloc

            if not self._path:
                self._path = self._split_result.path

            if not self._scheme:
                self._scheme = self._split_result.scheme

        self.query_dict = QueryDict(mutable=True)

        self.query_dict.update(
            QueryDict(query_string=self._split_result.query)
        )

        query_string = query_string or ''

        self.query_dict.update(
            QueryDict(
                query_string=query_string.encode('utf-8')
            )
        )

        query = query or {}

        for key, value in query.items():
            # Strings are iterables so tests for them explicitly.
            if isinstance(value, str):
                self.query_dict[key] = value
            else:
                try:
                    # Iterables other than strings.
                    result = []
                    for item in value:
                        result.append(item)

                    self.query_dict.setlist(key=key, list_=result)
                except TypeError:
                    # Value is not iterable, add as is.
                    self.query_dict[key] = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.to_string()

    @property
    def args(self):
        return self.query_dict

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value.startswith('/'):
            root = ''
        else:
            root = '/'

        split_result = urlsplit(
            url='{}{}'.format(root, value)
        )
        self._path = split_result.path

    def to_string(self):
        if self.query_dict.keys():
            query_string = self.query_dict.urlencode()
        else:
            query_string = ''

        split_result = copy.copy(self._split_result)

        if self._scheme:
            split_result = split_result._replace(scheme=self._scheme)

        if self._path:
            split_result = split_result._replace(path=self._path)

        if not split_result.netloc and self._netloc:
            split_result = split_result._replace(netloc=self._netloc)

        if self._port:
            netloc_parts = split_result.netloc.split(':')
            split_result = split_result._replace(
                netloc='{}:{}'.format(netloc_parts[0], self._port)
            )

        split_result = split_result._replace(query=query_string)

        return urlunsplit(split_result)
