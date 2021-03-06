import sys
import argparse
import datetime
import os

VARIABLES: list = list(set('XYZUVABCDNMLO'))
RETURN_TYPE: str = 'R'
FUNCTION_NAME: str = 'f'
HEADER: str = '''//
//  {file}
//  {project}
//
//  Created by {author} on {date}.
//
// Autogenerated by {script}

// swiftlint:disable all

/// Generated curry functions up to {arg_number} parameters.
'''


assert RETURN_TYPE not in VARIABLES, 'Should not be type name clashes'


def generate_parser():
    parser = argparse.ArgumentParser(description='Generate curry boilerplate')
    parser.add_argument(
        '--file_path', '-f',
        type=str,
        help='Output file path'
    )
    parser.add_argument(
        '--project', '-p',
        type=str, nargs='?',
        default='MonadicParser'
    )
    parser.add_argument(
        '--author', '-a',
        type=str, nargs='?',
        default='Artem Bobrov'
    )
    return parser


def get_datetime_str() -> str:
    now = datetime.datetime.today()
    return now.strftime('%d.%m.%Y')


def curry_function(type_params: list, return_type: str, body: str) -> str:
    type_args = ', '.join(type_params)
    return_type_args = ' -> '.join([f'({t})' for t in type_params])
    return f'''
/// Curry function from for function with {len(type_params)} arguments
public func curry<{type_args}, {return_type}>(_ f: @escaping ({type_args}) -> {return_type}) -> {return_type_args} -> {return_type} {{
    return {body}
}}
'''  # noqa: E501


def generate_function_body(variables: list, index=0) -> str:
    if not variables:
        return ''
    if index == len(variables):
        str_vars = ', '.join(variables)
        return f'{FUNCTION_NAME}({str_vars})'
    var = variables[index]
    return f'{{ {var} in {generate_function_body(variables, index + 1)} }}'


def generate_function(n_arguments: int) -> str:
    type_arguments = VARIABLES[:n_arguments]
    var_arguments = [arg.lower() for arg in type_arguments]
    body = generate_function_body(var_arguments)
    return curry_function(type_arguments, RETURN_TYPE, body)


def generate_file(file_path: str, header: str) -> str:
    with open(file_path, 'w') as file:
        file.write(header)
        for number in range(2, len(VARIABLES)):
            func = generate_function(number)
            file.write(func)


def generate_header(project_name: str, file_name: str, author: str) -> str:
    return HEADER.format(
        file=file_name,
        project=project_name,
        script=sys.argv[0],
        date=get_datetime_str(),
        arg_number=len(VARIABLES),
        author=author
    )


if __name__ == "__main__":
    parser = generate_parser()
    args = parser.parse_args()
    filename = os.path.basename(args.file_path)
    header = generate_header(args.project, filename, args.author)
    generate_file(args.file_path, header)
