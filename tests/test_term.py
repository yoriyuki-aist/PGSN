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
    var_x = lambda_term.Variable.from_name('x')
    id_f = lambda_term.Abs.named(v=var_x, t=var_x)
    assert id_f == lambda_term.Abs.named(v=var_x, t=var_x)
    t = lambda_term.App.named(t1=id_f, t2=id_f)
    assert t == lambda_term.App.named(t1=id_f, t2=id_f)
    nameless_t = t.remove_name()
    reduced = nameless_t.eval()
    assert reduced == id_f.remove_name()


def test_lambda_term_const():
    c = lambda_term.Constant.nameless('c')
    var_x = lambda_term.Variable.from_name('x')
    id_f = lambda_term.Abs.named(v=var_x, t=var_x).remove_name()
    t = lambda_term.App.nameless(t1=id_f, t2=c)
    assert t.eval() == c


class Id(lambda_term.Builtin):
    def _applicable(self, _):
        return True

    def _apply_arg(self, arg):
        return arg


def test_builtin():
    id_f = Id.nameless('id')
    c = lambda_term.Constant.nameless('c')
    assert id_f.applicable(c)
    assert id_f.apply_arg(c) == c
    t = lambda_term.App.nameless(id_f, c)
    assert t.eval() == c
    assert id_f(c).eval() == c
