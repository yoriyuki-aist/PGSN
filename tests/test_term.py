import meta_info
import lambda_term


def test_meta_info():
    info = meta_info.MetaInfo()
    assert info is not None


def test_lambda_term_id():
    term = lambda_term.Term()
    assert term.meta_info is not None
    nameless = lambda_term.Nameless()
    assert nameless.meta_info is not None
    named = lambda_term.Named()
    assert named.meta_info is not None
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





