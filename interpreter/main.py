from . pgsn_parser import pgsn_parser
from . pgsn_eval import ctx_eval, pgsn_eval
from . check_GSNform import check_GSNform
from . GSN2json import GSNterm2json
import sys


def main():
    print('start')
    ctx = []
    # path = input("filename:")
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    with open(input_path) as f:
        input_data = f.read()
    ast_data, ctx = pgsn_parser(ctx, input_data)
    ctx = ctx_eval(ctx)
    # print(ast_data, ctx)
    output_data = pgsn_eval(ctx, ast_data)
    # print(output_data, ctx)
    if check_GSNform(output_data):
        print('output JSON')
        GSNterm2json(output_data, output_path)
    print('end')


if __name__ == "__main__":
    main()
