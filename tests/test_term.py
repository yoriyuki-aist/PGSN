import meta_info
import lambda_term


def test_meta_info():
    info = meta_info.MetaInfo()
    assert info is not None


def test_lambda_term_id():
    var_x = lambda_term.NamedVariable('x')
    assert var_x.meta_info is not None
    id_f = lambda_term.NamedAbs(v=var_x, t=var_x)
    assert id_f.meta_info is not None
    assert id_f == lambda_term.NamedAbs(v=var_x, t=var_x)
    t = lambda_term.NamedApp(t1=id_f, t2=id_f)
    assert t.meta_info is not None
    assert t == lambda_term.NamedApp(t1=id_f, t2=id_f)
    nameless_t = t.remove_name()
    assert nameless_t.meta_info is not None
    reduced = nameless_t.eval()
    assert reduced.meta_info is not None
    assert reduced == id_f.remove_name()


def test_lambda_term_data():
    s1 = lambda_term.DataInNamed('test')
    assert s1.value == 'test'
    s2 = s1.remove_name()
    assert s2.value == s1.value   # type inference error


def test_lambda_term_list():
    context = ['x', 'y']
    var_x = lambda_term.NamedVariable('x')
    var_y = lambda_term.NamedVariable('y')
    list_term_1 = lambda_term.ListInNameless([var_x.remove_name_with_context(context),
                                            var_y.remove_name_with_context(context)])
    list_term_2 = lambda_term.ListInNamed([var_x, var_y])
    assert list_term_1 == list_term_2.remove_name_with_context(context)



