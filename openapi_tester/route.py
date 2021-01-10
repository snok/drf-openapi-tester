import re
from typing import List

from django.urls import ResolverMatch


class Route:
    def __init__(self, deparameterized_path: str, resolved_path: ResolverMatch) -> None:
        self.deparameterized_path = deparameterized_path
        self.parameterized_path = deparameterized_path
        self.resolved_path = resolved_path

        # Used to create a next() type logic
        self.counter = 0
        self.parameters = self.get_parameters(self.deparameterized_path)

    @staticmethod
    def get_parameters(path: str) -> List[str]:
        """
        Returns a count of parameters in a string.
        """
        pattern = re.compile(r'({[\w]+})')
        return list(re.findall(pattern, path))

    def get_path(self) -> str:
        """
        Given an original deparameterized path looking like this:

            /api/{version}/{parameter1}/{parameter2}

        This should return the path, with one parameter substituted every time it's called, until there are no more
        parameters to insert. Like this:

        > route.get_path()
        >> /api/{version}/{parameter1}/{parameter2}

        > route.get_path()
        >> /api/v1/{parameter1}/{parameter2}

        > route.get_path()
        >> /api/v1/cars/{parameter2}

        > route.get_path()
        >> /api/v1/cars/correct

        > route.get_path()
        >> IndexError('No more parameters to insert')
        """
        if self.counter == 0:
            self.counter += 1
            return self.replace_i18n_parameter(self.parameterized_path)
        if self.counter > len(self.parameters):
            raise IndexError('No more parameters to insert')

        path = self.parameterized_path
        parameter = self.parameters[self.counter - 1]
        parameter_name = parameter.replace('{', '').replace('}', '')
        starting_index = path.find(parameter)
        path = f'{path[:starting_index]}{self.resolved_path.kwargs[parameter_name]}{path[starting_index + len(parameter):]}'
        self.parameterized_path = path
        self.counter += 1

        return self.replace_i18n_parameter(path)

    def reset(self) -> None:
        """
        Resets parameterized path and counter.
        """
        self.parameterized_path = self.deparameterized_path
        self.counter = 0

    def route_matches(self, route: str) -> bool:
        """
        Checks whether a route matches any version of get_path.
        """
        if len(self.parameters) == 0:
            return self.deparameterized_path == route

        for _ in range(len(self.parameters) + 1):
            x = self.get_path()
            if x == route:
                self.reset()
                return True
        self.reset()
        return False

    @staticmethod
    def replace_i18n_parameter(route: str):
        """
        If PARAMETERIZED_I18N_NAME is set in the package settings,
        this function will replace a route with a parameter value.

        In short, this route

            /en/api/v1/items

        Would become

            /{language}/api/v1/items

        If PARAMETERIZED_I18N_NAME == 'language'. If it was 'lang', the route
        would become

            /{lang}/api/v1/items
        """
        from django.utils import translation

        from openapi_tester.configuration import settings

        if settings.parameterized_i18n_name:
            parameter = f'{{{settings.parameterized_i18n_name}}}'
            language = translation.get_language()
            route = route.replace(f'/{language}/', f'/{parameter}/')

        return route
