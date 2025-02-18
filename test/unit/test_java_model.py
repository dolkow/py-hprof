# Copyright (C) 2019 Snild Dolkow
# Licensed under the LICENSE.

import unittest

import hprof
from hprof import heap

class CommonClassTests(object):
	def setUp(self):
		_, self.obj = heap._create_class(self, self.names['obj'], None, {}, ('shadow',))
		_, self.cls = heap._create_class(self, self.names['cls'], self.obj, {}, ('secret',))
		_, self.lst = heap._create_class(self, self.names['lst'], self.obj, {}, ('next',))
		_, self.inr = heap._create_class(self, self.names['inn'], self.obj, {}, ('this$0',))
		_, self.shd = heap._create_class(self, self.names['shd'], self.lst, {}, ('shadow','unique'))

	def test_duplicate_class(self):
		old = self.java.lang.Class
		_, newcls = heap._create_class(self, self.names['cls'], self.obj, {}, ('secret',))
		self.assertIs(old, self.java.lang.Class) # same name object
		self.assertIsNot(newcls, self.cls)

	def test_setup_basics(self):
		self.assertIsInstance(self.java, heap.JavaPackage)
		self.assertIsInstance(self.java.lang, heap.JavaPackage)
		self.assertIsInstance(self.java.util, heap.JavaPackage)

		self.assertFalse(issubclass(self.obj, self.cls))
		self.assertFalse(issubclass(self.obj, self.lst))
		self.assertFalse(issubclass(self.obj, self.inr))
		self.assertFalse(issubclass(self.obj, self.shd))
		self.assertTrue( issubclass(self.cls, self.obj))
		self.assertFalse(issubclass(self.cls, self.lst))
		self.assertFalse(issubclass(self.cls, self.inr))
		self.assertFalse(issubclass(self.cls, self.shd))
		self.assertTrue( issubclass(self.lst, self.obj))
		self.assertFalse(issubclass(self.lst, self.cls))
		self.assertFalse(issubclass(self.lst, self.inr))
		self.assertFalse(issubclass(self.lst, self.shd))
		self.assertTrue( issubclass(self.inr, self.obj))
		self.assertFalse(issubclass(self.inr, self.cls))
		self.assertFalse(issubclass(self.inr, self.lst))
		self.assertFalse(issubclass(self.inr, self.shd))
		self.assertTrue( issubclass(self.shd, self.obj))
		self.assertFalse(issubclass(self.shd, self.cls))
		self.assertTrue( issubclass(self.shd, self.lst))
		self.assertFalse(issubclass(self.shd, self.inr))

		self.assertIsInstance(self.obj, heap.JavaClass)
		self.assertIsInstance(self.cls, heap.JavaClass)
		self.assertIsInstance(self.lst, heap.JavaClass)
		self.assertIsInstance(self.inr, heap.JavaClass)
		self.assertIsInstance(self.shd, heap.JavaClass)

	def test_package_eq(self):
		self.assertEqual(self.java,      'java')
		self.assertEqual(self.java.lang, 'java.lang')
		self.assertEqual(self.java.util, 'java.util')

	def test_package_str(self):
		self.assertEqual(str(self.java),      'java')
		self.assertEqual(str(self.java.lang), 'java.lang')
		self.assertEqual(str(self.java.util), 'java.util')

	def test_package_repr(self):
		self.assertEqual(repr(self.java),      "<JavaPackage 'java'>")
		self.assertEqual(repr(self.java.lang), "<JavaPackage 'java.lang'>")
		self.assertEqual(repr(self.java.util), "<JavaPackage 'java.util'>")

	def test_class_name_eq(self):
		self.assertEqual(self.java.lang.Object,     'java.lang.Object')
		self.assertEqual(self.java.lang.Class,      'java.lang.Class')
		self.assertEqual(self.java.util.List,       'java.util.List')
		self.assertEqual(self.java.util.List.Inner, 'java.util.List.Inner')
		self.assertEqual(self.Shadower,             'Shadower')

	def test_class_name_hash(self):
		self.assertEqual(hash(self.java.lang.Object),     hash('java.lang.Object'))
		self.assertEqual(hash(self.java.lang.Class),      hash('java.lang.Class'))
		self.assertEqual(hash(self.java.util.List),       hash('java.util.List'))
		self.assertEqual(hash(self.java.util.List.Inner), hash('java.util.List.Inner'))
		self.assertEqual(hash(self.Shadower),             hash('Shadower'))

	def test_class_str(self):
		self.assertEqual(str(self.obj), "java.lang.Object")
		self.assertEqual(str(self.cls), "java.lang.Class")
		self.assertEqual(str(self.lst), "java.util.List")
		self.assertEqual(str(self.inr), "java.util.List.Inner")
		self.assertEqual(str(self.shd), "Shadower")

	def test_class_name_str(self):
		self.assertEqual(str(self.java.lang.Object),     'java.lang.Object')
		self.assertEqual(str(self.java.lang.Class),      'java.lang.Class')
		self.assertEqual(str(self.java.util.List),       'java.util.List')
		self.assertEqual(str(self.java.util.List.Inner), 'java.util.List.Inner')
		self.assertEqual(str(self.Shadower),             'Shadower')

	def test_class_repr(self):
		self.assertEqual(repr(self.obj), "<JavaClass 'java.lang.Object'>")
		self.assertEqual(repr(self.cls), "<JavaClass 'java.lang.Class'>")
		self.assertEqual(repr(self.lst), "<JavaClass 'java.util.List'>")
		self.assertEqual(repr(self.inr), "<JavaClass 'java.util.List.Inner'>")
		self.assertEqual(repr(self.shd), "<JavaClass 'Shadower'>")

	def test_class_name_repr(self):
		self.assertEqual(repr(self.java.lang.Object),     "<JavaClassName 'java.lang.Object'>")
		self.assertEqual(repr(self.java.lang.Class),      "<JavaClassName 'java.lang.Class'>")
		self.assertEqual(repr(self.java.util.List),       "<JavaClassName 'java.util.List'>")
		self.assertEqual(repr(self.java.util.List.Inner), "<JavaClassName 'java.util.List.Inner'>")
		self.assertEqual(repr(self.Shadower),             "<JavaClassName 'Shadower'>")

	def test_object_instance(self):
		o = self.obj(0xf00d)
		with self.assertRaises(AttributeError):
			o.blah = 3
		self.obj._hprof_ifieldvals.__set__(o, (3,))
		self.assertEqual(o.shadow, 3)
		self.assertIsInstance(o, heap.JavaObject)
		self.assertIsInstance(o, self.obj)
		self.assertNotIsInstance(o, self.cls)
		self.assertNotIsInstance(o, self.lst)
		self.assertNotIsInstance(o, heap.JavaArray)
		self.assertEqual(str(o), '<java.lang.Object 0xf00d>')
		self.assertEqual(repr(o), str(o))
		self.assertCountEqual(dir(o), ('shadow',))
		with self.assertRaisesRegex(TypeError, 'has no len'):
			len(o)
		with self.assertRaisesRegex(TypeError, 'does not support indexing'):
			o[3]

	def test_class_instance(self):
		c = self.cls(0xdead)
		with self.assertRaises(AttributeError):
			c.next = 3
		self.obj._hprof_ifieldvals.__set__(c, (72,))
		self.cls._hprof_ifieldvals.__set__(c, (78,))
		self.assertEqual(c.shadow, 72)
		self.assertEqual(c.secret, 78)
		self.assertIsInstance(c, heap.JavaObject)
		self.assertIsInstance(c, self.obj)
		self.assertIsInstance(c, self.cls)
		self.assertNotIsInstance(c, self.lst)
		self.assertEqual(str(c), '<java.lang.Class 0xdead>')
		self.assertEqual(repr(c), str(c))
		self.assertCountEqual(dir(c), ('shadow', 'secret'))

	def test_inner_instance(self):
		i = self.inr(0x1)
		with self.assertRaises(AttributeError):
			i.missing
		self.obj._hprof_ifieldvals.__set__(i, (101,))
		self.inr._hprof_ifieldvals.__set__(i, (102,))
		self.assertEqual(i.shadow, 101)
		self.assertEqual(getattr(i, 'this$0'), 102)
		self.assertIsInstance(i, heap.JavaObject)
		self.assertIsInstance(i, self.obj)
		self.assertIsInstance(i, self.inr)
		self.assertNotIsInstance(i, self.lst)
		self.assertEqual(str(i), '<java.util.List.Inner 0x1>')
		self.assertEqual(repr(i), str(i))
		self.assertCountEqual(dir(i), ('shadow', 'this$0'))


	def test_double_dollar(self):
		_, lambdacls = heap._create_class(self, self.names['lam'], self.obj, {'line': 79}, ('closure_x', 'closure_y'))
		self.assertEqual(str(lambdacls), 'com.example.Vehicle$$Lambda$1/455659002')
		lambdaobj = lambdacls(33)
		self.obj._hprof_ifieldvals.__set__(lambdaobj, (11,))
		lambdacls._hprof_ifieldvals.__set__(lambdaobj, (10, 20))
		with self.assertRaises(AttributeError):
			lambdaobj.missing
		with self.assertRaises(AttributeError):
			lambdaobj.missing = 3
		with self.assertRaises(AttributeError):
			lambdaobj.closure_x = 3
		self.assertEqual(lambdaobj.shadow, 11)
		self.assertEqual(lambdaobj.closure_x, 10)
		self.assertEqual(lambdaobj.closure_y, 20)
		self.assertEqual(lambdaobj.line, 79)
		self.assertIsInstance(lambdaobj, heap.JavaObject)
		self.assertIsInstance(lambdaobj, self.obj)
		self.assertIsInstance(lambdaobj, lambdacls)
		self.assertEqual(str(lambdaobj), '<com.example.Vehicle$$Lambda$1/455659002 0x21>')
		self.assertEqual(repr(lambdaobj), str(lambdaobj))
		self.assertCountEqual(dir(lambdaobj), ('shadow', 'closure_x', 'closure_y', 'line'))

	def test_obj_array(self):
		# the base array class...
		_, oacls = heap._create_class(self, self.names['oar'], self.obj, {}, ('extrastuff',))
		self.assertEqual(str(oacls), 'java.lang.Object[]')
		self.assertEqual(repr(oacls), "<JavaClass 'java.lang.Object[]'>")
		self.assertTrue(isinstance(oacls, heap.JavaClass))
		self.assertTrue(isinstance(oacls, heap.JavaArrayClass))
		self.assertTrue(issubclass(oacls, heap.JavaObject))
		self.assertTrue(issubclass(oacls, heap.JavaArray))
		self.assertTrue(issubclass(oacls, self.obj))

		oarr = oacls(73)
		self.obj._hprof_ifieldvals.__set__(oarr, (0xbeef,))
		oarr._hprof_ifieldvals = (49,)
		oarr._hprof_array_data = (10, 55, 33)
		self.assertEqual(len(oarr), 3)
		self.assertEqual(oarr[0], 10)
		self.assertEqual(oarr[1], 55)
		self.assertEqual(oarr[2], 33)
		self.assertEqual(oarr[-1], 33)
		self.assertEqual(oarr[-2], 55)
		self.assertEqual(oarr[-3], 10)
		self.assertEqual(oarr[:], (10, 55, 33))
		self.assertEqual(oarr[1:], (55, 33))
		self.assertEqual(oarr[:2], (10, 55))
		self.assertEqual(oarr[:-1], (10, 55))
		self.assertEqual(oarr[2:], (33,))
		self.assertEqual(oarr[:0], ())
		self.assertEqual(oarr[:1], (10,))
		with self.assertRaises(IndexError):
			oarr[3]
		with self.assertRaises(IndexError):
			oarr[-4]
		with self.assertRaises(TypeError):
			oarr['hello']
		self.assertIn(10, oarr)
		self.assertIn(55, oarr)
		self.assertIn(33, oarr)
		self.assertNotIn(11, oarr)
		self.assertNotIn(12, oarr)
		self.assertNotIn(49, oarr)
		self.assertNotIn(32, oarr)
		for i, x in enumerate(oarr):
			self.assertEqual(x, oarr[i])
		self.assertEqual(i, 2)
		self.assertCountEqual(dir(oarr), ('shadow','extrastuff'))
		self.assertEqual(oarr.shadow, 0xbeef)
		self.assertEqual(oarr.extrastuff, 49)

		# ...and a subclass
		_, lacls = heap._create_class(self, self.names['lar'], oacls, {}, ('more',))
		self.assertEqual(str(lacls), 'List$$lambda[]')
		self.assertEqual(repr(lacls), "<JavaClass 'List$$lambda[]'>")
		self.assertTrue(isinstance(lacls, heap.JavaClass))
		self.assertTrue(isinstance(lacls, heap.JavaArrayClass))
		self.assertTrue(issubclass(lacls, heap.JavaObject))
		self.assertTrue(issubclass(lacls, self.obj))
		self.assertTrue(issubclass(lacls, oacls))

		larr = lacls(97)
		oacls._hprof_ifieldvals.__set__(larr, (56,))
		lacls._hprof_ifieldvals.__set__(larr, (99,))
		larr._hprof_array_data = (1, 3, 5, 7, 9)
		self.assertEqual(len(larr), 5)
		self.assertEqual(larr[0], 1)
		self.assertEqual(larr[1], 3)
		self.assertEqual(larr[2], 5)
		self.assertEqual(larr[3], 7)
		self.assertEqual(larr[4], 9)
		self.assertEqual(larr[-1], 9)
		self.assertEqual(larr[-2], 7)
		self.assertEqual(larr[-3], 5)
		self.assertEqual(larr[-4], 3)
		self.assertEqual(larr[-5], 1)
		self.assertEqual(larr[:], (1,3,5,7,9))
		self.assertEqual(larr[1:], (3,5,7,9))
		self.assertEqual(larr[:2], (1,3))
		self.assertEqual(larr[:-1], (1,3,5,7))
		self.assertEqual(larr[2:], (5,7,9))
		self.assertEqual(larr[:0], ())
		self.assertEqual(larr[:1], (1,))
		with self.assertRaises(IndexError):
			larr[5]
		with self.assertRaises(IndexError):
			larr[-6]
		with self.assertRaises(TypeError):
			larr['world']
		self.assertIn(1, larr)
		self.assertIn(3, larr)
		self.assertIn(5, larr)
		self.assertIn(7, larr)
		self.assertIn(9, larr)
		self.assertNotIn(0, larr)
		self.assertNotIn(2, larr)
		self.assertNotIn(4, larr)
		self.assertNotIn(6, larr)
		self.assertNotIn(8, larr)
		self.assertNotIn(100, larr)
		for i, x in enumerate(larr):
			self.assertEqual(x, larr[i])
		self.assertEqual(i, 4)
		self.assertEqual(larr.extrastuff, 56)
		self.assertEqual(larr.more, 99)

	def test_prim_array_types(self):
		def check(name, expected):
			clsname, cls = heap._create_class(self, name, self.obj, {}, ())
			self.assertIsNone(cls.__module__)
			self.assertEqual(clsname, expected)
			self.assertEqual(str(cls), expected)
			self.assertEqual(repr(cls), "<JavaClass '%s'>" % expected)
		#single
		check(self.names['Zar'], 'boolean[]')
		check(self.names['Car'], 'char[]')
		check(self.names['Far'], 'float[]')
		check(self.names['Dar'], 'double[]')
		check(self.names['Bar'], 'byte[]')
		check(self.names['Sar'], 'short[]')
		check(self.names['Iar'], 'int[]')
		check(self.names['Jar'], 'long[]')
		#double
		check(self.names['Zarar'], 'boolean[][]')
		check(self.names['Carar'], 'char[][]')
		check(self.names['Farar'], 'float[][]')
		check(self.names['Darar'], 'double[][]')
		check(self.names['Barar'], 'byte[][]')
		check(self.names['Sarar'], 'short[][]')
		check(self.names['Iarar'], 'int[][]')
		check(self.names['Jarar'], 'long[][]')
		#triple
		check(self.names['Zararar'], 'boolean[][][]')
		check(self.names['Cararar'], 'char[][][]')
		check(self.names['Fararar'], 'float[][][]')
		check(self.names['Dararar'], 'double[][][]')
		check(self.names['Bararar'], 'byte[][][]')
		check(self.names['Sararar'], 'short[][][]')
		check(self.names['Iararar'], 'int[][][]')
		check(self.names['Jararar'], 'long[][][]')

	def test_prim_array(self):
		_, sacls = heap._create_class(self, self.names['Sar'], self.obj, {}, ())
		self.assertEqual(str(sacls), 'short[]')
		self.assertEqual(repr(sacls), "<JavaClass 'short[]'>")
		self.assertTrue(isinstance(sacls, heap.JavaClass))
		self.assertTrue(isinstance(sacls, heap.JavaArrayClass))
		self.assertTrue(issubclass(sacls, heap.JavaObject))
		self.assertTrue(issubclass(sacls, heap.JavaArray))
		self.assertTrue(issubclass(sacls, self.obj))

		sarr = sacls(1)
		self.obj._hprof_ifieldvals.__set__(sarr, (0xf00d,))
		sarr._hprof_array_data = (1,2,9)

		self.assertCountEqual(dir(sarr), ('shadow',))
		self.assertEqual(sarr.shadow, 0xf00d)

		self.assertEqual(len(sarr), 3)
		self.assertEqual(sarr[0], 1)
		self.assertEqual(sarr[1], 2)
		self.assertEqual(sarr[2], 9)
		self.assertEqual(sarr[-1], 9)
		self.assertEqual(sarr[-2], 2)
		self.assertEqual(sarr[-3], 1)
		self.assertEqual(sarr[:], (1, 2, 9))
		self.assertEqual(sarr[1:], (2,9))
		self.assertEqual(sarr[:2], (1, 2))
		self.assertEqual(sarr[:-1], (1, 2))
		self.assertEqual(sarr[2:], (9,))
		self.assertEqual(sarr[:0], ())
		self.assertEqual(sarr[:1], (1,))
		with self.assertRaises(IndexError):
			sarr[3]
		with self.assertRaises(IndexError):
			sarr[-4]
		with self.assertRaises(TypeError):
			sarr['hello']
		self.assertIn(1, sarr)
		self.assertIn(2, sarr)
		self.assertIn(9, sarr)
		self.assertNotIn(3, sarr)
		self.assertNotIn(4, sarr)
		self.assertNotIn(5, sarr)
		self.assertNotIn(-1, sarr)
		for i, x in enumerate(sarr):
			self.assertEqual(x, sarr[i])
		self.assertEqual(i, 2)


	def test_prim_array_deferred_bool(self):
		_, acls = heap._create_class(self, self.names['Zar'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.boolean, b'\x23\x10\xff\x10\x00\x00\x21\x78')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 8)
		self.assertIs(arr[0], True)
		self.assertIs(arr[1], True)
		self.assertIs(arr[2], True)
		self.assertIs(arr[3], True)
		self.assertIs(arr[4], False)
		self.assertIs(arr[5], False)
		self.assertIs(arr[6], True)
		self.assertIs(arr[7], True)
		with self.assertRaises(IndexError):
			arr[8]

	def test_prim_array_deferred_char(self):
		_, acls = heap._create_class(self, self.names['Car'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.char, b'\0\x57\0\xf6\0\x72\0\x6c\xd8\x01\xdc\x00\0\x21')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 7)
		self.assertEqual(arr[0], 'W')
		self.assertEqual(arr[1], 'ö')
		self.assertEqual(arr[2], 'r')
		self.assertEqual(arr[3], 'l')
		self.assertEqual(arr[4], '\ud801')
		self.assertEqual(arr[5], '\udc00')
		self.assertEqual(arr[6], '!')
		with self.assertRaises(IndexError):
			arr[7]

	def test_prim_array_deferred_byte(self):
		_, acls = heap._create_class(self, self.names['Bar'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.byte, b'\x23\x10\xff\x80\x00\x00\x7f\x78\x84')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 9)
		self.assertEqual(arr[0], 0x23)
		self.assertEqual(arr[1], 0x10)
		self.assertEqual(arr[2], -1)
		self.assertEqual(arr[3], -128)
		self.assertEqual(arr[4], 0x00)
		self.assertEqual(arr[5], 0x00)
		self.assertEqual(arr[6], 127)
		self.assertEqual(arr[7], 0x78)
		self.assertEqual(arr[8], -124)
		with self.assertRaises(IndexError):
			arr[9]

	def test_prim_array_deferred_short(self):
		_, sacls = heap._create_class(self, self.names['Sar'], self.obj, {}, ())
		sarr = sacls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.short, b'\x23\x10\xff\x10\x00\x00\x21\x78')

		sarr._hprof_array_data = data
		self.assertEqual(len(sarr), 4)
		self.assertEqual(sarr[0], 0x2310)
		self.assertEqual(sarr[1], 0xff10-0x10000)
		self.assertEqual(sarr[2], 0)
		self.assertEqual(sarr[3], 0x2178)

		sarr._hprof_array_data = data
		self.assertEqual(sarr[1], 0xff10-0x10000)
		self.assertEqual(sarr[3], 0x2178)
		self.assertEqual(len(sarr), 4)
		self.assertEqual(sarr[2], 0)
		self.assertEqual(sarr[0], 0x2310)

		with self.assertRaises(IndexError):
			sarr[4]

	def test_prim_array_deferred_int(self):
		_, acls = heap._create_class(self, self.names['Iar'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.int, b'\x23\x10\xff\x80\x00\x00\x7f\x78\x84\x25\x66\x76')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 3)
		self.assertEqual(arr[0], 0x2310ff80)
		self.assertEqual(arr[1], 0x00007f78)
		self.assertEqual(arr[2], 0x84256676 - 0x100000000)
		with self.assertRaises(IndexError):
			arr[3]

	def test_prim_array_deferred_long(self):
		_, acls = heap._create_class(self, self.names['Jar'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.long, b'\x23\x10\xff\x80\x00\x00\x7f\x78\x84\x25\x66\x76\x12\x34\x56\x78')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 2)
		self.assertEqual(arr[0], 0x2310ff8000007f78)
		self.assertEqual(arr[1], 0x8425667612345678 - 0x10000000000000000)
		with self.assertRaises(IndexError):
			arr[2]

	def test_prim_array_deferred_float(self):
		_, acls = heap._create_class(self, self.names['Far'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.float, b'\x23\x10\xff\x80\x00\x00\x7f\x78\x84\x25\x66\x76')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 3)
		self.assertEqual(arr[0], 7.8603598714015e-18)
		self.assertEqual(arr[1], 4.572717148784743e-41)
		self.assertEqual(arr[2], -1.944270454372837e-36)
		with self.assertRaises(IndexError):
			arr[3]

	def test_prim_array_deferred_double(self):
		_, acls = heap._create_class(self, self.names['Dar'], self.obj, {}, ())
		arr = acls(1)
		data = hprof.heap._DeferredArrayData(hprof.jtype.double, b'\x23\x10\xff\x80\x00\x00\x7f\x78\x84\x25\x66\x76\x12\x34\x56\x78')

		arr._hprof_array_data = data
		self.assertEqual(len(arr), 2)
		self.assertEqual(arr[0], 8.921154138878651e-140)
		self.assertEqual(arr[1], -1.0979758629196027e-288)
		with self.assertRaises(IndexError):
			arr[2]


	def test_static_vars(self):
		c = self.cls(11)
		l = self.lst(22)
		self.obj._hprof_sfields['sGlobalLock'] = 10
		self.assertEqual(self.obj.sGlobalLock, 10)
		self.assertEqual(self.cls.sGlobalLock, 10)
		self.assertEqual(self.lst.sGlobalLock, 10)
		self.assertEqual(c.sGlobalLock, 10)
		self.assertEqual(l.sGlobalLock, 10)
		self.lst._hprof_sfields['sGlobalLock'] = 20 # shadow the one in Object
		self.assertEqual(self.obj.sGlobalLock, 10)
		self.assertEqual(self.cls.sGlobalLock, 10)
		self.assertEqual(self.lst.sGlobalLock, 20)
		self.assertEqual(c.sGlobalLock, 10)
		self.assertEqual(l.sGlobalLock, 20)
		with self.assertRaises(AttributeError):
			self.obj.sMissing
		with self.assertRaises(AttributeError):
			self.cls.sMissing
		with self.assertRaises(AttributeError):
			self.lst.sMissing
		with self.assertRaises(AttributeError):
			self.c.sMissing
		with self.assertRaises(AttributeError):
			self.l.sMissing

	def test_refs(self):
		_, extraclass = heap._create_class(self, self.names['ext'], self.shd, {}, ('shadow',))
		e = extraclass(0xbadf00d)
		self.obj._hprof_ifieldvals.__set__(e, (1111,))
		self.lst._hprof_ifieldvals.__set__(e, (708,))
		self.shd._hprof_ifieldvals.__set__(e, (2223, 33))
		extraclass._hprof_ifieldvals.__set__(e, (10,))

		self.assertEqual(e.shadow, 10)
		self.assertEqual(e.unique, 33)
		self.assertEqual(e.next, 708)
		self.assertCountEqual(dir(e), ('shadow', 'unique', 'next'))
		self.assertEqual(str(e), '<Extra 0xbadf00d>')
		self.assertEqual(repr(e), str(e))

		r = heap.Ref(e, extraclass)
		self.assertIs(r, e) # no reason to use Ref when reftype matches exactly.

		s = hprof.cast(e, self.shd)
		self.assertEqual(s, e)
		self.assertEqual(s.shadow, 2223)
		self.assertEqual(s.unique, 33)
		self.assertEqual(s.next, 708)
		self.assertCountEqual(dir(s), ('shadow', 'unique', 'next'))
		self.assertEqual(str(s), '<Ref of type Shadower to Extra 0xbadf00d>')
		self.assertEqual(repr(s), str(s))
		self.assertIsInstance(s, self.obj)
		self.assertIsInstance(s, self.lst)
		self.assertIsInstance(s, self.shd)
		self.assertIsInstance(s, extraclass)
		self.assertNotIsInstance(s, self.cls)

		l = hprof.cast(e, self.lst)
		self.assertEqual(l.shadow, 1111)
		self.assertEqual(l, e)
		with self.assertRaises(AttributeError):
			self.assertEqual(l.unique, 33)
		self.assertEqual(l.next, 708)
		self.assertCountEqual(dir(l), ('shadow', 'next'))
		self.assertEqual(str(l), '<Ref of type java.util.List to Extra 0xbadf00d>')
		self.assertEqual(repr(l), str(l))
		self.assertIsInstance(l, self.obj)
		self.assertIsInstance(l, self.lst)
		self.assertIsInstance(l, self.shd)
		self.assertIsInstance(l, extraclass)
		self.assertNotIsInstance(l, self.cls)

		o = hprof.cast(e, self.obj)
		self.assertEqual(o, e)
		self.assertEqual(o.shadow, 1111)
		with self.assertRaises(AttributeError):
			self.assertEqual(o.unique, 33)
		with self.assertRaises(AttributeError):
			self.assertEqual(o.next, 708)
		self.assertCountEqual(dir(o), ('shadow',))
		self.assertEqual(str(o), '<Ref of type java.lang.Object to Extra 0xbadf00d>')
		self.assertEqual(repr(o), str(o))
		self.assertIsInstance(o, self.obj)
		self.assertIsInstance(o, self.lst)
		self.assertIsInstance(o, self.shd)
		self.assertIsInstance(o, extraclass)
		self.assertNotIsInstance(o, self.cls)

	def test_casting(self):
		s = self.shd(1001)
		l = hprof.cast(s, self.lst)
		o = hprof.cast(s, self.obj)
		# casting upward
		self.assertIs(hprof.cast(s, self.shd), s)
		self.assertEqual(hprof.cast(s, self.lst), s)
		self.assertEqual(hprof.cast(s, self.obj), s)
		# casting downward
		self.assertEqual(hprof.cast(o, self.obj), s)
		self.assertEqual(hprof.cast(o, self.lst), s)
		self.assertIs(hprof.cast(o, self.shd), s)

	def test_bad_cast(self):
		s = self.shd(1020)
		with self.assertRaises(TypeError):
			hprof.cast(s, self.java.lang.Class)

	def test_bad_downcast(self):
		s = self.shd(1033)
		o = hprof.cast(s, self.obj)
		with self.assertRaises(TypeError):
			hprof.cast(o, self.cls)

	def test_unref(self):
		s = self.shd(1234)
		o = hprof.cast(s, self.obj)
		self.assertIs(hprof.cast(o), s)

	def test_refs_to_class(self):
		_, string = heap._create_class(self, self.names['str'], self.obj, {}, ('chars',))
		o = hprof.cast(string, self.obj)
		c = hprof.cast(string, self.cls)
		self.assertIs(o, string)
		self.assertIs(c, string)
		with self.assertRaises(TypeError):
			hprof.cast(string, string)
		with self.assertRaises(TypeError):
			hprof.cast(string, self.lst)

class TestJavaClass(CommonClassTests, unittest.TestCase):
	def setUp(self):
		self.names = {
			'obj': 'java/lang/Object',
			'cls': 'java/lang/Class',
			'lst': 'java/util/List',
			'inn': 'java/util/List$Inner',
			'shd': 'Shadower',
			'ext': 'Extra',
			'str': 'java/lang/String',
			'lam': 'com/example/Vehicle$$Lambda$1/455659002',
			'oar': '[Ljava/lang/Object;',
			'lar': '[LList$$lambda;',
			'Zar': '[Z', 'Zarar': '[[Z', 'Zararar': '[[[Z',
			'Bar': '[B', 'Barar': '[[B', 'Bararar': '[[[B',
			'Sar': '[S', 'Sarar': '[[S', 'Sararar': '[[[S',
			'Iar': '[I', 'Iarar': '[[I', 'Iararar': '[[[I',
			'Jar': '[J', 'Jarar': '[[J', 'Jararar': '[[[J',
			'Far': '[F', 'Farar': '[[F', 'Fararar': '[[[F',
			'Dar': '[D', 'Darar': '[[D', 'Dararar': '[[[D',
			'Car': '[C', 'Carar': '[[C', 'Cararar': '[[[C',
		}
		super().setUp()

class TestAndroidClass(CommonClassTests, unittest.TestCase):
	def setUp(self):
		self.names = {
			'obj': 'java.lang.Object',
			'cls': 'java.lang.Class',
			'lst': 'java.util.List',
			'inn': 'java.util.List$Inner',
			'shd': 'Shadower',
			'ext': 'Extra',
			'str': 'java.lang.String',
			'lam': 'com.example.Vehicle$$Lambda$1/455659002',
			'oar': 'java.lang.Object[]',
			'lar': 'List$$lambda[]',
			'Zar': 'boolean[]', 'Zarar': 'boolean[][]', 'Zararar': 'boolean[][][]',
			'Bar':    'byte[]', 'Barar':    'byte[][]', 'Bararar':    'byte[][][]',
			'Sar':   'short[]', 'Sarar':   'short[][]', 'Sararar':   'short[][][]',
			'Iar':     'int[]', 'Iarar':     'int[][]', 'Iararar':     'int[][][]',
			'Jar':    'long[]', 'Jarar':    'long[][]', 'Jararar':    'long[][][]',
			'Far':   'float[]', 'Farar':   'float[][]', 'Fararar':   'float[][][]',
			'Dar':  'double[]', 'Darar':  'double[][]', 'Dararar':  'double[][][]',
			'Car':    'char[]', 'Carar':    'char[][]', 'Cararar':    'char[][][]',
		}
		super().setUp()
