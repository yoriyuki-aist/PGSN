import meta_info
# from lambda_term import App, Constant, Abs, NamedVariable
# from string_term import String
# from list_term import List, NamedList
# import record_term
# import stdlib
#
#
# def test_empty_list():
#     assert stdlib.empty_list.terms == []
#
#
# def test_add_head():
#     c = Constant('c')
#     args = List([c, stdlib.empty_list])
#     t = App(stdlib.add_head, args)
#     assert t.eval().terms[0] == c
#     t1 = App(stdlib.add_head, c)
#     assert t1.eval() == t1
#
#
# def test_head():
#     c = Constant('c')
#     args = List([c, stdlib.empty_list])
#     t0 = App(stdlib.add_head, args)
#     t = App(stdlib.head, t0)
#     assert t.eval() == c
#     t1 = App(stdlib.head, c)
#     assert t1.eval() == t1
#
#
# def test_tail():
#     c = Constant('c')
#     args = List([c, stdlib.empty_list])
#     t0 = App(stdlib.add_head, args)
#     t = App(stdlib.tail, t0)
#     assert t.eval() == stdlib.empty_list
#     t1 = App(stdlib.tail, c)
#     assert t1.eval() == t1
#
#
# def test_index():
#     c1 = Constant('c1')
#     c2 = Constant('c2')
#     ll = List([c1, c2])
#     i0 = String('0')
#     i1 = String('1')
#     i2 = String('2')
#     not_int = String('xxx')
#     assert App(stdlib.index, List([ll, i0])).eval() == c1
#     assert App(stdlib.index, List([ll, i1])).eval() == c2
#     out_of_bound = App(stdlib.index, List([ll, i2]))
#     assert out_of_bound.eval() == out_of_bound
#     non_int_index = App(stdlib.index, List([ll, not_int]))
#     assert non_int_index.eval() == non_int_index
#     single_arg = App(stdlib.index, c1)
#     assert single_arg.eval() == single_arg
#
#
# def test_fold():
#     c = Constant('c')
#     var_x = NamedVariable.from_name('x')
#     var_y = NamedVariable.from_name('y')
#     arg = NamedList([var_x, var_y])
#     body =
