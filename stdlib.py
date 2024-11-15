from __future__ import annotations
import helpers
from typing import Sequence, Any
from attrs import frozen, evolve, field
from pgsn_term import BuiltinFunction, Term, Unary, Variable, Abs, App, String, Integer, \
    Boolean, List, Record, Constant
import pgsn_term


def check_type_list(arg: Term, types: list):
    if not isinstance(arg, List):
        return False
    return helpers.check_type_list(arg.terms, types)


def check_type_dict(arg: Term, types: dict):
    if not isinstance(arg, Record):
        return False
    return helpers.check_type_list(arg.attributes, types)


# List functions

@frozen
class Cons(BuiltinFunction):
    name = 'Cons'
    arity = 2

    def _applicable_args(self, args: Sequence[Term]):
        return isinstance(args[1], List)

    def _apply_args(self, args: tuple[Term, List]):
        return evolve(args[1], terms=(args[0],) + args[1].terms)

@frozen
class Head(Unary):
    name = 'Head'

    def _applicable(self, arg: Term):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> Term:
        return arg.terms[0]

@frozen
class Tail(Unary):
    name = 'Tail'

    def _applicable(self, arg: Term):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> List:
        return List(terms=arg.terms[1:], is_named=self.is_named)


class Index(BuiltinFunction):
    name = 'Index'
    arity = 2

    def _applicable_args(self, args: Sequence[Term]):
        return isinstance(args[0], List) and isinstance(args[1], Integer)

    def _apply_args(self, args: tuple[Term,...]) -> Term:
        return args[0].terms[args[1].value]


@frozen
class Fold(BuiltinFunction):
    name = 'Fold'
    arity = 3

    def _applicable_args(self, args: Sequence[Term]):
        if not len(args) >= 3:
            return False
        if not isinstance(args[2], List):
            return False
        return True

    def _apply_args(self, args: Sequence[Term]) -> Term:
        fun = args[0]
        init = args[1]
        arg_list = args[2].terms
        if len(arg_list) == 0:
            return init
        list_head = arg_list[0]
        list_rest = arg_list[1:]
        rest = List(terms=list_rest, is_named=self.is_named)
        return fun(list_head)(self(fun)(init)(rest))


@frozen
class Map(BuiltinFunction):
    name = 'Map'
    arity = 2

    def _applicable_args(self, args: Sequence[Term]):
        if not isinstance(args[1], List):
            return False
        return True

    def _apply_args(self, args: Sequence[Term]) -> Term:
        fun = args[0]
        arg = args[1]
        arg_list = arg.terms
        map_list = tuple((fun(t) for t in arg_list))
        map_result = List(terms=map_list, is_named=self.is_named)
        return map_result


# Integer functions
@frozen
class Plus(BuiltinFunction):
    arity = 2
    name = 'Plus'

    def _applicable_args(self, args: tuple[Term, ...]):
        return len(args) >= 2 and isinstance(args[0], Integer) and isinstance(args[1], Integer)

    def _apply_args(self, args: tuple[Term, ...]):
        i1 = args[0].value
        i2 = args[1].value
        return pgsn_term.Integer.nameless(value=i1 + i2)


# multi_arg function
@frozen
class MultiArgFunction(BuiltinFunction):
    # Hack: arity has a default argument but the default value is invalid.
    # The object must be created by build class method.
    arity = field(default=0)
    _keyword_args: dict[str, Term | None] = field(default={})
    # Hack: syntactically, body is an optional argument but must be specified otherwise
    # the runtime error occurs.
    main: Term | None = field(default=None, validator=helpers.not_none)

    def __attr_post_init__(self):
        assert all((var.is_named == self.is_named for var in self.positional_variable))
        assert all((var.is_named == self.is_named for var  in self._keyword_variable.keys()))
        assert all((t is None or t.is_named == self.is_named for _, t in self._keyword_variable.items()))
        assert self.main is not None
        assert self.arity >= 1

    @classmethod
    def build(cls,
              is_named: bool,
              positional_vars: tuple[Variable, ...],
              keyword_args: dict[str, Term | None],
              body: Term):
        keywords = sorted(keyword_args.keys())
        main = body
        for key in keywords:
            var = variable(key)
            main = lambda_abs(var, main)
        var_r = variable('r')
        for key in reversed(keywords):
            s = string(key)
            main = main(var_r(s))
        main = lambda_abs(var_r, main)
        for var in reversed(positional_vars):
            main = lambda_abs(var, main)
        return cls(is_named=is_named,
                   arity=len(positional_vars) + 1,
                   keyword_args=keyword_args.copy(),
                   main=main)

    def _remove_name_with_context(self, context: list[str]) -> Term:
        keyword_args = {k: t.remove_name_with_context(context) if t is not None else None for k, t in self._keyword_args.items()}
        main = self.main.remove_name_with_context(context)
        return self.evolve(is_named=False, keyword_args=keyword_args, main=main)

    def _applicable_args(self, args: tuple[Term,...]) -> bool:
        if not isinstance(args[self.arity-1], Record):
            return False
        r = args[self.arity-1].attributes()
        for k, v in self._keyword_args.items():
            if v is None and k not in r:
                return False
        return True

    def _apply_args(self, args: tuple[Term,...]):
        r = args[self.arity - 1].attributes()
        for k, v in self._keyword_args.items():
            if k not in r and v is not None:
                r[k] = v
        assert set(self._keyword_args.keys()).issubset(set(r.keys()))
        assert all(v is not None for v in r.values())
        r_term = Record.nameless(attributes=r)
        t = self.main
        for arg in args[:-1]:
            t = t(arg)
        return t(r_term)


class IfThenElse(BuiltinFunction):
    arity = 3
    name = 'IfThenElse'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Boolean)

    def _apply_args(self, terms: tuple[Term,...]):
        b = terms[0].value
        return terms[1] if b else terms[2]


# guard b t only progresses b is true
class Guard(BuiltinFunction):
    arity=2
    name='Guard'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Boolean) and terms[0].value

    def _apply_args(self, terms: tuple[Term,...]):
        return terms[1]


# Comparison. does not compare App and Abs
class Equal(BuiltinFunction):
    arity = 2
    name = 'Equal'

    def _applicable_args(self, args: tuple[Term,...]):
        return all((not isinstance(arg, App) and not isinstance(arg, Abs) for arg in args))

    def _apply_args(self, args: tuple[Term,...]):
        return Boolean.build(is_named=self.is_named, value=args[0] == args[1])


class HasLabel(BuiltinFunction):
    arity = 2
    name = 'HasLabel'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Record) and isinstance(terms[1], String)

    def _apply_args(self, terms: tuple[Record, String]):
        k = terms[1].value
        b = k in terms[0].attributes()
        return Boolean.build(is_named=self.is_named, value=b)


class AddAttribute(BuiltinFunction):
    arity = 3
    name = 'AddAttribute'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Record) and isinstance(terms[1], String)

    def _apply_args(self, terms: tuple[Term,...]):
        attrs = terms[0].attributes()
        attrs[terms[1].value] = terms[2]
        return Record.build(is_named=self.is_named, attributes=attrs)


class RemoveAttribute(BuiltinFunction):
    arity = 2
    name = 'RemoveAttribute'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Record) and isinstance(terms[1], String)

    def _apply_args(self, terms: tuple[Term,...]):
        attrs = terms[0].attributes()
        del attrs[terms[1].value]
        return Record.build(is_named=self.is_named, attributes=attrs)


class ListLabels(Unary):
    name = 'ListLabels'

    def _applicable(self, term: Term):
        return isinstance(term, Record)

    def _apply_arg(self, term: Term):
        labels = map(lambda l: String(is_named=self.is_named, value=l), term.attributes())
        return pgsn_term.List.build(is_named=self.is_named, terms=tuple(labels))


class OverwriteRecord(BuiltinFunction):
    arity = 2
    name = "OverwriteRecord"

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Record) and isinstance(terms[1], Record)

    def _apply_args(self, terms: tuple[Term,...]):
        r1 = terms[0].attributes()
        r2 = terms[1].attributes()
        r = r1
        for k, t in r2.items():
            r[k] = t
        return Record.build(is_named=self.is_named, attributes=r)


Printable = String | Integer


def _uncast(t: Term):
    match t:
        case pgsn_term.Data():
            return t.value
        case List():
            terms = t.terms
            return [value_of(t1) for t1 in terms]
        case Record():
            attr = t.attributes()
            return {k: value_of(t1) for k, t1 in attr.items()}
        case _:
            raise ValueError(f'PGSN term {type(t)} does not normalizes a Python value')


class Formatter(BuiltinFunction):
    arity = 2
    name = 'Format string'

    def _applicable_args(self, terms: tuple[Term,...]):
        if not len(terms) == 2:
            return False
        if not isinstance(terms[0], String):
            return False
        if not isinstance(terms[1], Record):
            return False
        try:
            python_vals = _uncast(terms[1])
            _ = terms[0].value.format(**python_vals)
            return True
        except (KeyError, TypeError, ValueError):
            return False

    def _apply_args(self, terms: tuple[Term,...]):
        python_vals = _uncast(terms[1])
        return String.build(is_named=self.is_named, value=terms[0].value.format(**python_vals))


format_string = Formatter.named()


# Interface by lambda terms
# identifiers starting _ is reserved for internal uses.
def variable(name: str) -> Variable:
    return Variable.named(name=name)


_x = variable('x')
_y = variable('y')
_z = variable('z')
_w = variable('w')
_f = variable('f')
_label = variable('label')


def constant(name: str) -> Constant:
    return Constant.named(name=name)


undefined = constant('undefined')


# let var = t1 in t2
def let(var: Variable, t1: Term, t2: Term):
    return (lambda_abs(var, t2))(t1)


# let v1 = t1, v2 = t2, ... in t
def let_vars(assigns: tuple[tuple[Variable, Term],...], t: Term):
    for v, t1 in reversed(assigns):
        t = let(v, t1, t)
    return t


# fixed point operator
# fixed point operator
def lambda_abs(v: Variable, t: Term) -> Term:
    return Abs.named(v=v, t=t)


fix = lambda_abs(_f,
                 lambda_abs(_x, _f(_x(_x)))(lambda_abs(_x, _f(_x(_x))))
                 )

# Boolean related
def boolean(b: bool) -> Boolean:
    return Boolean.named(value=b)


true = boolean(True)
false = boolean(False)
if_then_else = IfThenElse.named()
guard = Guard.named()


def lambda_abs_vars(vs: tuple[Variable,...], t) -> Term:
    t1 = t
    for v in reversed(vs):
        t1 = lambda_abs(v, t1)
    return t1


boolean_and = lambda_abs_vars(
    (_x, _y),
    if_then_else(_x)(_y)(false)
)
boolean_or = lambda_abs_vars(
    (_x, _y),
    if_then_else(_x)(true)(_y)
)
boolean_not = lambda_abs(_x, if_then_else(_x)(false)(true))

equal = Equal.named()


# Integer related
plus = Plus.named()


# List related
cons = Cons.named()
head = Head.named()
tail = Tail.named()
index = Index.named()
#fold = Fold.named()
map_term = Map.named()

_elem = variable('elem')
_list = variable('list')
_acc = variable('acc')
_foldr = variable('_foldr')
empty: List = List.named(terms=tuple())
_F = lambda_abs_vars((_foldr, _f, _acc, _list),
                     if_then_else(equal(_list)(empty))
                     (_acc)
                     (_f(head(_list))(_foldr(_f)(_acc)(tail(_list))) )
                     )
foldr = fix(_F)
fold = foldr

list_all = lambda_abs_vars(
    (_x, _y),
    let(
        _f,
        lambda_abs_vars((_z, _w), boolean_and(_x(_z))(_w)),
        fold(_f)(_y)(true)
    )
)


def integer(i: int) -> Integer:
    return Integer.named(value=i)


integer_sum = fold(plus)(integer(0))


# Record
def record(d: dict[str, Term]):
    return Record.named(attributes=d)


empty_record = record({})
has_label = HasLabel.named()
list_labels = ListLabels.named()
add_attribute = AddAttribute.named()
remove_attribute = RemoveAttribute.named()
overwrite_record = OverwriteRecord.named()


# keyword_args_function
def lambda_abs_keywords(arguments: dict[str,Variable],
                        body: Term,
                        defaults: Record = empty_record) -> Term:
    sorted_arguments = sorted(arguments.items(), key=lambda x: x[0])
    variables = tuple((v for _, v in sorted_arguments))
    t = lambda_abs_vars(variables, body)
    _args = variable('args')
    for k, _ in sorted_arguments:
        _k = string(k)
        t = t(_args(_k))
    return lambda_abs(_args, let(_args, overwrite_record(defaults)(_args), t))


def string(s: str) -> String:
    return String.named(value=s)


def list_term(terms: tuple[Term,...]) -> List:
    return List.named(terms=terms)


# Extract python values from pgsn term
def value_of(term: Term, steps=1000) -> Any:
    t = term.fully_eval(steps)
    return _uncast(t)