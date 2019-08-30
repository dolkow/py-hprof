import unittest
import hprof

class TestPrimitiveReader(unittest.TestCase):

	def setUp(self):
		self.r = hprof._parsing.PrimitiveReader(b'hi you\0\xc3\x9czx')

	def test_bytes(self):
		self.assertEqual(self.r.bytes(4), b'hi y')
		self.assertEqual(self.r.bytes(5), b'ou\0\xc3\x9c')
		self.assertEqual(self.r.bytes(1), b'z')
		self.assertEqual(self.r.bytes(1), b'x')
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(1)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(2)

	def test_bytes_oob(self):
		self.assertEqual(self.r.bytes(11), b'hi you\0\xc3\x9czx')
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(2)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(1)

	def test_bytes_half_oob(self):
		self.assertEqual(self.r.bytes(8), b'hi you\0\xc3')
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(4)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(7)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(7)
		self.assertEqual(self.r.bytes(3), b'\x9czx')

	def test_bytes_all_oob(self):
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(12)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(22)

	def test_bytes_none(self):
		self.assertEqual(self.r.bytes(0), b'')
		self.assertEqual(self.r.bytes(0), b'')
		self.assertEqual(self.r.bytes(5), b'hi yo')
		self.assertEqual(self.r.bytes(0), b'')
		self.assertEqual(self.r.bytes(0), b'')
		self.assertEqual(self.r.bytes(6), b'u\0\xc3\x9czx')
		self.assertEqual(self.r.bytes(0), b'')
		self.assertEqual(self.r.bytes(0), b'')
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.bytes(1)

	def test_ascii(self):
		self.assertEqual(self.r.ascii(), 'hi you')
		self.assertEqual(self.r.bytes(4), b'\xc3\x9czx')

	def test_ascii_later(self):
		self.assertEqual(self.r.bytes(1), b'h')
		self.assertEqual(self.r.ascii(), 'i you')
		self.assertEqual(self.r.bytes(1), b'\xc3')
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.ascii()
		self.assertEqual(self.r.bytes(1), b'\x9c')

	def test_ascii_invalid(self):
		r = hprof._parsing.PrimitiveReader(b'abc\xc3\x9czx\0')
		with self.assertRaises(hprof.error.FormatError):
			r.ascii()
		self.assertEqual(r.bytes(4), b'abc\xc3')

	def test_unsigned_4(self):
		self.assertEqual(self.r.u(4), 0x68692079)
		self.assertEqual(self.r.u(4), 0x6f7500c3)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.u(4)

	def test_unsigned_5(self):
		self.assertEqual(self.r.u(5), 0x686920796f)
		self.assertEqual(self.r.u(5), 0x7500c39c7a)
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.u(5)

	def test_unsigned_unaligned(self):
		self.r.bytes(3)
		self.assertEqual(self.r.u(4), 0x796f7500)
		self.assertEqual(self.r.u(4), 0xc39c7a78)

	def test_signed_3(self):
		self.r.bytes(4)
		self.assertEqual(self.r.i(3), 0x6f7500)
		self.assertEqual(self.r.i(3), 0xc39c7a - 0x1000000)

	def test_signed_unaligned(self):
		self.r.bytes(3)
		self.assertEqual(self.r.i(4), 0x796f7500)
		self.assertEqual(self.r.i(4), 0xc39c7a78 - 0x100000000)

	def test_invalid_utf8_does_not_consume(self):
		r = hprof._parsing.PrimitiveReader(b'abc\xed\x00\xbddef')
		with self.assertRaises(hprof.error.FormatError):
			r.utf8(9)
		self.assertEqual(r.bytes(3), b'abc')

	def test_utf8_oob(self):
		with self.assertRaises(hprof.error.UnexpectedEof):
			self.r.utf8(20)
		self.assertEqual(self.r.bytes(5), b'hi yo')


class TestMutf8(unittest.TestCase):

	def decode(self, bytes):
		r = hprof._parsing.PrimitiveReader(bytes)
		return r.utf8(len(bytes))

	def test_encoded_null(self):
		self.assertEqual(self.decode(b'\xc0\x80'), '\0')
		self.assertEqual(self.decode(b'hello\xc0\x80world'), 'hello\0world')

	def test_plain_null(self):
		self.assertEqual(self.decode(b'\0'), '\0')
		self.assertEqual(self.decode(b'hello\0world'), 'hello\0world')

	def test_surrogate_pair(self):
		# "🜚" after being run through javac: 0xeda0bd 0xedbc9a
		self.assertEqual(self.decode(b'\xed\xa0\xbd\xed\xbc\x9a'), '🜚')
		self.assertEqual(self.decode(b'g\xed\xa0\xbd\xed\xbc\x9ald'), 'g🜚ld')
		self.assertEqual(self.decode(b'\xed\xa0\xbd\xed\xbc\x9b'), '🜛')
		self.assertEqual(self.decode(b'sil\xed\xa0\xbd\xed\xbc\x9bver'), 'sil🜛ver')

	def test_invalid_surrogate_pair(self):
		with self.assertRaises(hprof.error.FormatError):
			self.decode(b'\xed\x00\xbd\xed\xbc\x9a')
		with self.assertRaises(hprof.error.FormatError):
			self.decode(b'\xed\xa0\x00\xed\xbc\x9a')
		with self.assertRaises(hprof.error.FormatError):
			self.decode(b'\xed\xa0\xbd\x00\xbc\x9a')
		with self.assertRaises(hprof.error.FormatError):
			self.decode(b'\xed\xa0\xbd\xed\x00\x9a')
		with self.assertRaises(hprof.error.FormatError):
			self.decode(b'\xed\xa0\xbd\xed\xbc\x00')

	def test_truncated_surrogate(self):
		for i in range(1,6):
			with self.subTest(i):
				with self.assertRaises(hprof.error.FormatError):
					self.decode(b'\xed\xa0\xbd\xed\xbc'[:i])
				with self.assertRaises(hprof.error.FormatError):
					self.decode(b'g\xed\xa0\xbd\xed\xbc'[:i+1])

	def test_4byte_utf8(self):
		# real utf8!
		self.assertEqual(self.decode(b'\xf0\x9f\x9c\x9a'), '🜚')
		self.assertEqual(self.decode(b'g\xf0\x9f\x9c\x9ald'), 'g🜚ld')
		self.assertEqual(self.decode(b'\xf0\x9f\x9c\x9b'), '🜛')
		self.assertEqual(self.decode(b'sil\xf0\x9f\x9c\x9bver'), 'sil🜛ver')