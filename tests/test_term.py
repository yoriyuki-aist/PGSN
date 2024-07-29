import meta_info
import lambda_term
import string_term
import list_term
import record_term


def test_meta_info():
    info = meta_info.MetaInfo()
    assert info is not None


def test_var():
    var_x = lambda_term.NamedVariable.from_name('x')
    assert var_x.meta_info.name_info == 'x'
    nameless_x = var_x.remove_name()
    assert nameless_x.meta_info.name_info == 'x'


def test_lambda_term_id():
    var_x = lambda_term.NamedVariable.from_name('x')
    id_f = lambda_term.NamedAbs(v=var_x, t=var_x)
    assert id_f == lambda_term.NamedAbs(v=var_x, t=var_x)
    t = lambda_term.NamedApp(t1=id_f, t2=id_f)
    assert t == lambda_term.NamedApp(t1=id_f, t2=id_f)
    nameless_t = t.remove_name()
    reduced = nameless_t.eval()
    assert reduced == id_f.remove_name()


def test_lambda_term_const():
    c = lambda_term.Constant('c')
    var_x = lambda_term.NamedVariable.from_name('x')
    id_f = lambda_term.NamedAbs(v=var_x, t=var_x).remove_name()
    t = lambda_term.App(t1=id_f, t2=c)
    assert t.eval() == c


class Id(lambda_term.Builtin):
    def applicable(self, _):
        return True

    def apply_arg(self, arg):
        return arg


def test_builtin():
    id_f = Id('id')
    c = lambda_term.Constant('c')
    assert id_f.applicable(c)
    assert id_f.apply_arg(c) == c
    t = lambda_term.App(id_f, c)
    assert t.eval() == c


def test_string():
    s = string_term.String('x')
    assert s.value == 'x'


def test_list():
    var_x = lambda_term.NamedVariable.from_name('x')
    id_f = lambda_term.NamedAbs(v=var_x, t=var_x)
    t = lambda_term.NamedApp(id_f, var_x)
    ll = list_term.NamedList([var_x, id_f, t])
    ll1 = ll.remove_name()
    reduced = ll1.eval()
    assert isinstance(reduced, list_term.List)
    assert reduced.terms[0] == var_x.remove_name()
    assert reduced.terms[1] == id_f.remove_name()
    assert reduced.terms[2] == var_x.remove_name()


def test_record():
    var_x = lambda_term.NamedVariable.from_name('x')
    id_f = lambda_term.NamedAbs(v=var_x, t=var_x)
    t = lambda_term.NamedApp(id_f, var_x)
    r = record_term.NamedRecord({'x': var_x, 'id_f': id_f, 't':t})
    reduced = r.remove_name().eval()
    assert isinstance(reduced, record_term.Record)
    assert reduced.terms['x'] == var_x.remove_name()
    assert reduced.terms['id_f'] == id_f.remove_name()
    assert reduced.terms['t'] == var_x.remove_name()
#
# def test_lambda_term_data():
#     s1 = lambda_term.ConstantNamed('test')
#     assert s1.value == 'test'
#     s2 = s1.remove_name()
#     assert s2.value == s1.value   # type inference error
#
#
# def test_lambda_term_list():
#     context = ['x', 'y']
#     var_x = lambda_term.NamedVariable('x')
#     var_y = lambda_term.NamedVariable('y')
#     list_term_1 = lambda_term.ListNameless([var_x.remove_name_with_context(context),
#                                             var_y.remove_name_with_context(context)])
#     list_term_2 = lambda_term.ListNamed([var_x, var_y])
#     assert list_term_1 == list_term_2.remove_name_with_context(context)
#
#
# def test_lambda_term_record():
#     context = ['x', 'y']
#     var_x = lambda_term.NamedVariable('x')
#     var_y = lambda_term.NamedVariable('y')
#     list_term_1 = lambda_term.RecordNameless({'a': var_x.remove_name_with_context(context),
#                                               'b': var_y.remove_name_with_context(context)})
#     list_term_2 = lambda_term.RecordNamed({'a':var_x, 'b':var_y})
#     assert list_term_1 == list_term_2.remove_name_with_context(context)

