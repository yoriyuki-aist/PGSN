import meta_info
import lambda_term
# import string_term
# import list_term
# import record_term


def test_meta_info():
    info = meta_info.MetaInfo()
    assert info is not None


def test_var():
    info = meta_info.MetaInfo(name_info='x')
    var_x = lambda_term.Variable.named(name='x', meta_info=info)
    nameless_x = var_x.remove_name()
    assert nameless_x.meta_info.name_info == 'x'


def test_lambda_term_id():
    x = lambda_term.variable('x')
    id_f = lambda_term.lambda_abs(x, x)
    t = id_f(id_f)
    assert t.eval() == id_f.eval()


def test_lambda_term_const():
    c = lambda_term.constant('c')
    x = lambda_term.variable('x')
    id_f = lambda_term.lambda_abs(x, c)
    t = id_f(c)
    assert t.eval() == c.eval()


class Id(lambda_term.Unary):
    arity = 1

    def _applicable(self, args):
        return True

    def _apply_arg(self, arg):
        return arg


def test_builtin():
    id_f = Id.named().eval()
    c = lambda_term.constant('c').eval()
    assert id_f.applicable_args((c,))
    assert id_f.apply_args((c,)) == (c, tuple())
    assert id_f(c).eval() == c
