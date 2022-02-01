# Generated from D:/Documents/pycharm_workspace/Qrogue/dungeon_editor\QrogueDungeon.g4 by ANTLR 4.9.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2E")
        buf.write("\u0228\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23")
        buf.write("\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30")
        buf.write("\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36")
        buf.write("\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%")
        buf.write("\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.")
        buf.write("\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63\4\64")
        buf.write("\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\49\t9\4:\t:")
        buf.write("\4;\t;\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@\4A\tA\4B\tB\4C\t")
        buf.write("C\4D\tD\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3")
        buf.write("\7\3\b\3\b\3\t\3\t\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3")
        buf.write("\13\3\13\3\13\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\r\3\r")
        buf.write("\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\16\3\16\3\17\3\17\3")
        buf.write("\20\3\20\3\20\3\20\3\20\3\20\3\20\3\21\3\21\3\21\3\21")
        buf.write("\3\21\3\21\3\21\3\21\3\22\3\22\3\22\3\22\3\22\3\22\3\22")
        buf.write("\3\22\3\23\3\23\3\24\3\24\3\24\6\24\u00d6\n\24\r\24\16")
        buf.write("\24\u00d7\3\25\5\25\u00db\n\25\3\25\3\25\6\25\u00df\n")
        buf.write("\25\r\25\16\25\u00e0\3\26\7\26\u00e4\n\26\f\26\16\26\u00e7")
        buf.write("\13\26\3\26\5\26\u00ea\n\26\3\26\3\26\3\27\3\27\5\27\u00f0")
        buf.write("\n\27\3\30\3\30\3\31\3\31\3\32\3\32\5\32\u00f8\n\32\3")
        buf.write("\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\3\35\3\35\3\35\3\35\3\35\3\36\3\36\3\36")
        buf.write("\3\36\3\36\3\36\3\36\3\37\3\37\3\37\3\37\3\37\3\37\3\37")
        buf.write("\3 \3 \3 \3 \3 \3 \3!\3!\3!\3!\3!\3!\3!\3!\3!\3!\3\"\3")
        buf.write("\"\3\"\3\"\3\"\3\"\3#\3#\3#\3#\3#\3$\3$\3$\3$\3$\3%\3")
        buf.write("%\3%\3%\3%\3%\3%\3&\3&\3&\3&\3&\3\'\3\'\3\'\3\'\3\'\3")
        buf.write("(\3(\3(\3(\3)\3)\3)\3)\3)\3*\3*\3*\3*\3*\3*\3*\3+\3+\3")
        buf.write("+\3+\3+\3,\3,\3-\3-\3.\3.\3.\3.\3.\3.\3.\3.\3/\3/\3/\3")
        buf.write("/\3/\3/\3/\3/\3\60\3\60\3\60\3\60\3\60\3\60\3\60\3\60")
        buf.write("\3\60\3\61\3\61\3\61\3\61\3\61\3\61\3\61\3\61\3\61\3\61")
        buf.write("\3\61\3\61\3\61\3\61\3\61\3\62\3\62\3\62\3\62\3\62\3\62")
        buf.write("\3\62\3\62\3\62\3\62\3\62\3\63\3\63\3\63\3\63\3\63\3\63")
        buf.write("\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63")
        buf.write("\3\63\3\63\3\63\3\64\3\64\3\64\3\64\3\64\3\64\3\64\3\64")
        buf.write("\3\64\3\64\3\64\3\64\3\64\3\64\3\64\3\65\3\65\3\66\3\66")
        buf.write("\3\67\3\67\38\38\39\39\39\3:\3:\3:\3;\3;\3;\3;\3;\3;\3")
        buf.write(";\3;\3;\3;\3;\3;\3;\3;\3;\3;\3;\3;\5;\u01db\n;\3<\3<\3")
        buf.write("<\3<\3<\3<\3<\3<\3=\3=\3=\3=\3=\3=\3=\3>\3>\5>\u01ee\n")
        buf.write(">\3>\3>\3?\3?\3?\3?\5?\u01f6\n?\3?\5?\u01f9\n?\3@\3@\3")
        buf.write("@\6@\u01fe\n@\r@\16@\u01ff\3A\6A\u0203\nA\rA\16A\u0204")
        buf.write("\3A\3A\3B\6B\u020a\nB\rB\16B\u020b\3B\3B\3C\3C\3C\3C\7")
        buf.write("C\u0214\nC\fC\16C\u0217\13C\3C\3C\3C\3C\3C\3D\3D\3D\3")
        buf.write("D\7D\u0222\nD\fD\16D\u0225\13D\3D\3D\3\u0215\2E\3\3\5")
        buf.write("\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r\31\16\33")
        buf.write("\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30/\31\61\32")
        buf.write("\63\33\65\34\67\359\36;\37= ?!A\"C#E$G%I&K\'M(O)Q*S+U")
        buf.write(",W-Y.[/]\60_\61a\62c\63e\64g\65i\66k\67m8o9q:s;u<w=y>")
        buf.write("{?}@\177A\u0081B\u0083C\u0085D\u0087E\3\2\7\3\2\62;\3")
        buf.write("\2c|\3\2C\\\5\2\13\f\17\17\"\"\4\2\f\f\17\17\2\u023a\2")
        buf.write("\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3")
        buf.write("\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2")
        buf.write("\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2")
        buf.write("\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#\3\2\2\2\2%")
        buf.write("\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2+\3\2\2\2\2-\3\2\2\2")
        buf.write("\2/\3\2\2\2\2\61\3\2\2\2\2\63\3\2\2\2\2\65\3\2\2\2\2\67")
        buf.write("\3\2\2\2\29\3\2\2\2\2;\3\2\2\2\2=\3\2\2\2\2?\3\2\2\2\2")
        buf.write("A\3\2\2\2\2C\3\2\2\2\2E\3\2\2\2\2G\3\2\2\2\2I\3\2\2\2")
        buf.write("\2K\3\2\2\2\2M\3\2\2\2\2O\3\2\2\2\2Q\3\2\2\2\2S\3\2\2")
        buf.write("\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2\2[\3\2\2\2\2]\3\2")
        buf.write("\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2\2\2\2e\3\2\2\2\2g\3")
        buf.write("\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3\2\2\2\2o\3\2\2\2\2q")
        buf.write("\3\2\2\2\2s\3\2\2\2\2u\3\2\2\2\2w\3\2\2\2\2y\3\2\2\2\2")
        buf.write("{\3\2\2\2\2}\3\2\2\2\2\177\3\2\2\2\2\u0081\3\2\2\2\2\u0083")
        buf.write("\3\2\2\2\2\u0085\3\2\2\2\2\u0087\3\2\2\2\3\u0089\3\2\2")
        buf.write("\2\5\u008b\3\2\2\2\7\u008d\3\2\2\2\t\u008f\3\2\2\2\13")
        buf.write("\u0091\3\2\2\2\r\u0093\3\2\2\2\17\u0095\3\2\2\2\21\u0097")
        buf.write("\3\2\2\2\23\u0099\3\2\2\2\25\u009b\3\2\2\2\27\u00a3\3")
        buf.write("\2\2\2\31\u00ab\3\2\2\2\33\u00b5\3\2\2\2\35\u00b7\3\2")
        buf.write("\2\2\37\u00b9\3\2\2\2!\u00c0\3\2\2\2#\u00c8\3\2\2\2%\u00d0")
        buf.write("\3\2\2\2\'\u00d2\3\2\2\2)\u00da\3\2\2\2+\u00e9\3\2\2\2")
        buf.write("-\u00ef\3\2\2\2/\u00f1\3\2\2\2\61\u00f3\3\2\2\2\63\u00f7")
        buf.write("\3\2\2\2\65\u00f9\3\2\2\2\67\u0101\3\2\2\29\u0107\3\2")
        buf.write("\2\2;\u010c\3\2\2\2=\u0113\3\2\2\2?\u011a\3\2\2\2A\u0120")
        buf.write("\3\2\2\2C\u012a\3\2\2\2E\u0130\3\2\2\2G\u0135\3\2\2\2")
        buf.write("I\u013a\3\2\2\2K\u0141\3\2\2\2M\u0146\3\2\2\2O\u014b\3")
        buf.write("\2\2\2Q\u014f\3\2\2\2S\u0154\3\2\2\2U\u015b\3\2\2\2W\u0160")
        buf.write("\3\2\2\2Y\u0162\3\2\2\2[\u0164\3\2\2\2]\u016c\3\2\2\2")
        buf.write("_\u0174\3\2\2\2a\u017d\3\2\2\2c\u018c\3\2\2\2e\u0197\3")
        buf.write("\2\2\2g\u01ab\3\2\2\2i\u01ba\3\2\2\2k\u01bc\3\2\2\2m\u01be")
        buf.write("\3\2\2\2o\u01c0\3\2\2\2q\u01c2\3\2\2\2s\u01c5\3\2\2\2")
        buf.write("u\u01da\3\2\2\2w\u01dc\3\2\2\2y\u01e4\3\2\2\2{\u01ed\3")
        buf.write("\2\2\2}\u01f8\3\2\2\2\177\u01fa\3\2\2\2\u0081\u0202\3")
        buf.write("\2\2\2\u0083\u0209\3\2\2\2\u0085\u020f\3\2\2\2\u0087\u021d")
        buf.write("\3\2\2\2\u0089\u008a\7<\2\2\u008a\4\3\2\2\2\u008b\u008c")
        buf.write("\7*\2\2\u008c\6\3\2\2\2\u008d\u008e\7+\2\2\u008e\b\3\2")
        buf.write("\2\2\u008f\u0090\7e\2\2\u0090\n\3\2\2\2\u0091\u0092\7")
        buf.write("v\2\2\u0092\f\3\2\2\2\u0093\u0094\7g\2\2\u0094\16\3\2")
        buf.write("\2\2\u0095\u0096\7t\2\2\u0096\20\3\2\2\2\u0097\u0098\7")
        buf.write("&\2\2\u0098\22\3\2\2\2\u0099\u009a\7a\2\2\u009a\24\3\2")
        buf.write("\2\2\u009b\u009c\7v\2\2\u009c\u009d\7t\2\2\u009d\u009e")
        buf.write("\7k\2\2\u009e\u009f\7i\2\2\u009f\u00a0\7i\2\2\u00a0\u00a1")
        buf.write("\7g\2\2\u00a1\u00a2\7t\2\2\u00a2\26\3\2\2\2\u00a3\u00a4")
        buf.write("\7q\2\2\u00a4\u00a5\7p\2\2\u00a5\u00a6\7g\2\2\u00a6\u00a7")
        buf.write("\7\"\2\2\u00a7\u00a8\7y\2\2\u00a8\u00a9\7c\2\2\u00a9\u00aa")
        buf.write("\7{\2\2\u00aa\30\3\2\2\2\u00ab\u00ac\7g\2\2\u00ac\u00ad")
        buf.write("\7p\2\2\u00ad\u00ae\7v\2\2\u00ae\u00af\7c\2\2\u00af\u00b0")
        buf.write("\7p\2\2\u00b0\u00b1\7i\2\2\u00b1\u00b2\7n\2\2\u00b2\u00b3")
        buf.write("\7g\2\2\u00b3\u00b4\7f\2\2\u00b4\32\3\2\2\2\u00b5\u00b6")
        buf.write("\7]\2\2\u00b6\34\3\2\2\2\u00b7\u00b8\7_\2\2\u00b8\36\3")
        buf.write("\2\2\2\u00b9\u00ba\7e\2\2\u00ba\u00bb\7w\2\2\u00bb\u00bc")
        buf.write("\7u\2\2\u00bc\u00bd\7v\2\2\u00bd\u00be\7q\2\2\u00be\u00bf")
        buf.write("\7o\2\2\u00bf \3\2\2\2\u00c0\u00c1\7f\2\2\u00c1\u00c2")
        buf.write("\7g\2\2\u00c2\u00c3\7h\2\2\u00c3\u00c4\7c\2\2\u00c4\u00c5")
        buf.write("\7w\2\2\u00c5\u00c6\7n\2\2\u00c6\u00c7\7v\2\2\u00c7\"")
        buf.write("\3\2\2\2\u00c8\u00c9\7t\2\2\u00c9\u00ca\7g\2\2\u00ca\u00cb")
        buf.write("\7y\2\2\u00cb\u00cc\7c\2\2\u00cc\u00cd\7t\2\2\u00cd\u00ce")
        buf.write("\7f\2\2\u00ce\u00cf\7u\2\2\u00cf$\3\2\2\2\u00d0\u00d1")
        buf.write("\t\2\2\2\u00d1&\3\2\2\2\u00d2\u00d3\5%\23\2\u00d3\u00d5")
        buf.write("\5%\23\2\u00d4\u00d6\5%\23\2\u00d5\u00d4\3\2\2\2\u00d6")
        buf.write("\u00d7\3\2\2\2\u00d7\u00d5\3\2\2\2\u00d7\u00d8\3\2\2\2")
        buf.write("\u00d8(\3\2\2\2\u00d9\u00db\5%\23\2\u00da\u00d9\3\2\2")
        buf.write("\2\u00da\u00db\3\2\2\2\u00db\u00dc\3\2\2\2\u00dc\u00de")
        buf.write("\7\60\2\2\u00dd\u00df\5%\23\2\u00de\u00dd\3\2\2\2\u00df")
        buf.write("\u00e0\3\2\2\2\u00e0\u00de\3\2\2\2\u00e0\u00e1\3\2\2\2")
        buf.write("\u00e1*\3\2\2\2\u00e2\u00e4\5%\23\2\u00e3\u00e2\3\2\2")
        buf.write("\2\u00e4\u00e7\3\2\2\2\u00e5\u00e3\3\2\2\2\u00e5\u00e6")
        buf.write("\3\2\2\2\u00e6\u00ea\3\2\2\2\u00e7\u00e5\3\2\2\2\u00e8")
        buf.write("\u00ea\5)\25\2\u00e9\u00e5\3\2\2\2\u00e9\u00e8\3\2\2\2")
        buf.write("\u00ea\u00eb\3\2\2\2\u00eb\u00ec\7l\2\2\u00ec,\3\2\2\2")
        buf.write("\u00ed\u00f0\5W,\2\u00ee\u00f0\5Y-\2\u00ef\u00ed\3\2\2")
        buf.write("\2\u00ef\u00ee\3\2\2\2\u00f0.\3\2\2\2\u00f1\u00f2\t\3")
        buf.write("\2\2\u00f2\60\3\2\2\2\u00f3\u00f4\t\4\2\2\u00f4\62\3\2")
        buf.write("\2\2\u00f5\u00f8\5/\30\2\u00f6\u00f8\5\61\31\2\u00f7\u00f5")
        buf.write("\3\2\2\2\u00f7\u00f6\3\2\2\2\u00f8\64\3\2\2\2\u00f9\u00fa")
        buf.write("\7x\2\2\u00fa\u00fb\7k\2\2\u00fb\u00fc\7u\2\2\u00fc\u00fd")
        buf.write("\7k\2\2\u00fd\u00fe\7d\2\2\u00fe\u00ff\7n\2\2\u00ff\u0100")
        buf.write("\7g\2\2\u0100\66\3\2\2\2\u0101\u0102\7h\2\2\u0102\u0103")
        buf.write("\7q\2\2\u0103\u0104\7i\2\2\u0104\u0105\7i\2\2\u0105\u0106")
        buf.write("\7{\2\2\u01068\3\2\2\2\u0107\u0108\7q\2\2\u0108\u0109")
        buf.write("\7r\2\2\u0109\u010a\7g\2\2\u010a\u010b\7p\2\2\u010b:\3")
        buf.write("\2\2\2\u010c\u010d\7e\2\2\u010d\u010e\7n\2\2\u010e\u010f")
        buf.write("\7q\2\2\u010f\u0110\7u\2\2\u0110\u0111\7g\2\2\u0111\u0112")
        buf.write("\7f\2\2\u0112<\3\2\2\2\u0113\u0114\7n\2\2\u0114\u0115")
        buf.write("\7q\2\2\u0115\u0116\7e\2\2\u0116\u0117\7m\2\2\u0117\u0118")
        buf.write("\7g\2\2\u0118\u0119\7f\2\2\u0119>\3\2\2\2\u011a\u011b")
        buf.write("\7g\2\2\u011b\u011c\7x\2\2\u011c\u011d\7g\2\2\u011d\u011e")
        buf.write("\7p\2\2\u011e\u011f\7v\2\2\u011f@\3\2\2\2\u0120\u0121")
        buf.write("\7r\2\2\u0121\u0122\7g\2\2\u0122\u0123\7t\2\2\u0123\u0124")
        buf.write("\7o\2\2\u0124\u0125\7c\2\2\u0125\u0126\7p\2\2\u0126\u0127")
        buf.write("\7g\2\2\u0127\u0128\7p\2\2\u0128\u0129\7v\2\2\u0129B\3")
        buf.write("\2\2\2\u012a\u012b\7U\2\2\u012b\u012c\7r\2\2\u012c\u012d")
        buf.write("\7c\2\2\u012d\u012e\7y\2\2\u012e\u012f\7p\2\2\u012fD\3")
        buf.write("\2\2\2\u0130\u0131\7Y\2\2\u0131\u0132\7k\2\2\u0132\u0133")
        buf.write("\7n\2\2\u0133\u0134\7f\2\2\u0134F\3\2\2\2\u0135\u0136")
        buf.write("\7U\2\2\u0136\u0137\7j\2\2\u0137\u0138\7q\2\2\u0138\u0139")
        buf.write("\7r\2\2\u0139H\3\2\2\2\u013a\u013b\7T\2\2\u013b\u013c")
        buf.write("\7k\2\2\u013c\u013d\7f\2\2\u013d\u013e\7f\2\2\u013e\u013f")
        buf.write("\7n\2\2\u013f\u0140\7g\2\2\u0140J\3\2\2\2\u0141\u0142")
        buf.write("\7D\2\2\u0142\u0143\7q\2\2\u0143\u0144\7u\2\2\u0144\u0145")
        buf.write("\7u\2\2\u0145L\3\2\2\2\u0146\u0147\7I\2\2\u0147\u0148")
        buf.write("\7c\2\2\u0148\u0149\7v\2\2\u0149\u014a\7g\2\2\u014aN\3")
        buf.write("\2\2\2\u014b\u014c\7m\2\2\u014c\u014d\7g\2\2\u014d\u014e")
        buf.write("\7{\2\2\u014eP\3\2\2\2\u014f\u0150\7e\2\2\u0150\u0151")
        buf.write("\7q\2\2\u0151\u0152\7k\2\2\u0152\u0153\7p\2\2\u0153R\3")
        buf.write("\2\2\2\u0154\u0155\7j\2\2\u0155\u0156\7g\2\2\u0156\u0157")
        buf.write("\7c\2\2\u0157\u0158\7n\2\2\u0158\u0159\7v\2\2\u0159\u015a")
        buf.write("\7j\2\2\u015aT\3\2\2\2\u015b\u015c\7i\2\2\u015c\u015d")
        buf.write("\7c\2\2\u015d\u015e\7v\2\2\u015e\u015f\7g\2\2\u015fV\3")
        buf.write("\2\2\2\u0160\u0161\7-\2\2\u0161X\3\2\2\2\u0162\u0163\7")
        buf.write("/\2\2\u0163Z\3\2\2\2\u0164\u0165\7S\2\2\u0165\u0166\7")
        buf.write("t\2\2\u0166\u0167\7q\2\2\u0167\u0168\7i\2\2\u0168\u0169")
        buf.write("\7w\2\2\u0169\u016a\7g\2\2\u016a\u016b\7>\2\2\u016b\\")
        buf.write("\3\2\2\2\u016c\u016d\7@\2\2\u016d\u016e\7S\2\2\u016e\u016f")
        buf.write("\7t\2\2\u016f\u0170\7q\2\2\u0170\u0171\7i\2\2\u0171\u0172")
        buf.write("\7w\2\2\u0172\u0173\7g\2\2\u0173^\3\2\2\2\u0174\u0175")
        buf.write("\7]\2\2\u0175\u0176\7N\2\2\u0176\u0177\7c\2\2\u0177\u0178")
        buf.write("\7{\2\2\u0178\u0179\7q\2\2\u0179\u017a\7w\2\2\u017a\u017b")
        buf.write("\7v\2\2\u017b\u017c\7_\2\2\u017c`\3\2\2\2\u017d\u017e")
        buf.write("\7]\2\2\u017e\u017f\7E\2\2\u017f\u0180\7w\2\2\u0180\u0181")
        buf.write("\7u\2\2\u0181\u0182\7v\2\2\u0182\u0183\7q\2\2\u0183\u0184")
        buf.write("\7o\2\2\u0184\u0185\7\"\2\2\u0185\u0186\7T\2\2\u0186\u0187")
        buf.write("\7q\2\2\u0187\u0188\7q\2\2\u0188\u0189\7o\2\2\u0189\u018a")
        buf.write("\7u\2\2\u018a\u018b\7_\2\2\u018bb\3\2\2\2\u018c\u018d")
        buf.write("\7]\2\2\u018d\u018e\7J\2\2\u018e\u018f\7c\2\2\u018f\u0190")
        buf.write("\7n\2\2\u0190\u0191\7n\2\2\u0191\u0192\7y\2\2\u0192\u0193")
        buf.write("\7c\2\2\u0193\u0194\7{\2\2\u0194\u0195\7u\2\2\u0195\u0196")
        buf.write("\7_\2\2\u0196d\3\2\2\2\u0197\u0198\7]\2\2\u0198\u0199")
        buf.write("\7U\2\2\u0199\u019a\7v\2\2\u019a\u019b\7c\2\2\u019b\u019c")
        buf.write("\7v\2\2\u019c\u019d\7g\2\2\u019d\u019e\7X\2\2\u019e\u019f")
        buf.write("\7g\2\2\u019f\u01a0\7e\2\2\u01a0\u01a1\7v\2\2\u01a1\u01a2")
        buf.write("\7q\2\2\u01a2\u01a3\7t\2\2\u01a3\u01a4\7\"\2\2\u01a4\u01a5")
        buf.write("\7R\2\2\u01a5\u01a6\7q\2\2\u01a6\u01a7\7q\2\2\u01a7\u01a8")
        buf.write("\7n\2\2\u01a8\u01a9\7u\2\2\u01a9\u01aa\7_\2\2\u01aaf\3")
        buf.write("\2\2\2\u01ab\u01ac\7]\2\2\u01ac\u01ad\7T\2\2\u01ad\u01ae")
        buf.write("\7g\2\2\u01ae\u01af\7y\2\2\u01af\u01b0\7c\2\2\u01b0\u01b1")
        buf.write("\7t\2\2\u01b1\u01b2\7f\2\2\u01b2\u01b3\7\"\2\2\u01b3\u01b4")
        buf.write("\7R\2\2\u01b4\u01b5\7q\2\2\u01b5\u01b6\7q\2\2\u01b6\u01b7")
        buf.write("\7n\2\2\u01b7\u01b8\7u\2\2\u01b8\u01b9\7_\2\2\u01b9h\3")
        buf.write("\2\2\2\u01ba\u01bb\7\u0080\2\2\u01bbj\3\2\2\2\u01bc\u01bd")
        buf.write("\7~\2\2\u01bdl\3\2\2\2\u01be\u01bf\7.\2\2\u01bfn\3\2\2")
        buf.write("\2\u01c0\u01c1\7%\2\2\u01c1p\3\2\2\2\u01c2\u01c3\7\60")
        buf.write("\2\2\u01c3\u01c4\7\60\2\2\u01c4r\3\2\2\2\u01c5\u01c6\7")
        buf.write("a\2\2\u01c6\u01c7\7a\2\2\u01c7t\3\2\2\2\u01c8\u01c9\7")
        buf.write("P\2\2\u01c9\u01ca\7q\2\2\u01ca\u01cb\7t\2\2\u01cb\u01cc")
        buf.write("\7v\2\2\u01cc\u01db\7j\2\2\u01cd\u01ce\7G\2\2\u01ce\u01cf")
        buf.write("\7c\2\2\u01cf\u01d0\7u\2\2\u01d0\u01db\7v\2\2\u01d1\u01d2")
        buf.write("\7U\2\2\u01d2\u01d3\7q\2\2\u01d3\u01d4\7w\2\2\u01d4\u01d5")
        buf.write("\7v\2\2\u01d5\u01db\7j\2\2\u01d6\u01d7\7Y\2\2\u01d7\u01d8")
        buf.write("\7g\2\2\u01d8\u01d9\7u\2\2\u01d9\u01db\7v\2\2\u01da\u01c8")
        buf.write("\3\2\2\2\u01da\u01cd\3\2\2\2\u01da\u01d1\3\2\2\2\u01da")
        buf.write("\u01d6\3\2\2\2\u01dbv\3\2\2\2\u01dc\u01dd\7q\2\2\u01dd")
        buf.write("\u01de\7t\2\2\u01de\u01df\7f\2\2\u01df\u01e0\7g\2\2\u01e0")
        buf.write("\u01e1\7t\2\2\u01e1\u01e2\7g\2\2\u01e2\u01e3\7f\2\2\u01e3")
        buf.write("x\3\2\2\2\u01e4\u01e5\7t\2\2\u01e5\u01e6\7c\2\2\u01e6")
        buf.write("\u01e7\7p\2\2\u01e7\u01e8\7f\2\2\u01e8\u01e9\7q\2\2\u01e9")
        buf.write("\u01ea\7o\2\2\u01eaz\3\2\2\2\u01eb\u01ee\7a\2\2\u01ec")
        buf.write("\u01ee\5\63\32\2\u01ed\u01eb\3\2\2\2\u01ed\u01ec\3\2\2")
        buf.write("\2\u01ee\u01ef\3\2\2\2\u01ef\u01f0\5\63\32\2\u01f0|\3")
        buf.write("\2\2\2\u01f1\u01f2\7?\2\2\u01f2\u01f9\7?\2\2\u01f3\u01f6")
        buf.write("\7a\2\2\u01f4\u01f6\5%\23\2\u01f5\u01f3\3\2\2\2\u01f5")
        buf.write("\u01f4\3\2\2\2\u01f6\u01f7\3\2\2\2\u01f7\u01f9\5%\23\2")
        buf.write("\u01f8\u01f1\3\2\2\2\u01f8\u01f5\3\2\2\2\u01f9~\3\2\2")
        buf.write("\2\u01fa\u01fd\7,\2\2\u01fb\u01fe\5\63\32\2\u01fc\u01fe")
        buf.write("\5%\23\2\u01fd\u01fb\3\2\2\2\u01fd\u01fc\3\2\2\2\u01fe")
        buf.write("\u01ff\3\2\2\2\u01ff\u01fd\3\2\2\2\u01ff\u0200\3\2\2\2")
        buf.write("\u0200\u0080\3\2\2\2\u0201\u0203\t\5\2\2\u0202\u0201\3")
        buf.write("\2\2\2\u0203\u0204\3\2\2\2\u0204\u0202\3\2\2\2\u0204\u0205")
        buf.write("\3\2\2\2\u0205\u0206\3\2\2\2\u0206\u0207\bA\2\2\u0207")
        buf.write("\u0082\3\2\2\2\u0208\u020a\7=\2\2\u0209\u0208\3\2\2\2")
        buf.write("\u020a\u020b\3\2\2\2\u020b\u0209\3\2\2\2\u020b\u020c\3")
        buf.write("\2\2\2\u020c\u020d\3\2\2\2\u020d\u020e\bB\2\2\u020e\u0084")
        buf.write("\3\2\2\2\u020f\u0210\7\61\2\2\u0210\u0211\7,\2\2\u0211")
        buf.write("\u0215\3\2\2\2\u0212\u0214\13\2\2\2\u0213\u0212\3\2\2")
        buf.write("\2\u0214\u0217\3\2\2\2\u0215\u0216\3\2\2\2\u0215\u0213")
        buf.write("\3\2\2\2\u0216\u0218\3\2\2\2\u0217\u0215\3\2\2\2\u0218")
        buf.write("\u0219\7,\2\2\u0219\u021a\7\61\2\2\u021a\u021b\3\2\2\2")
        buf.write("\u021b\u021c\bC\2\2\u021c\u0086\3\2\2\2\u021d\u021e\7")
        buf.write("\61\2\2\u021e\u021f\7\61\2\2\u021f\u0223\3\2\2\2\u0220")
        buf.write("\u0222\n\6\2\2\u0221\u0220\3\2\2\2\u0222\u0225\3\2\2\2")
        buf.write("\u0223\u0221\3\2\2\2\u0223\u0224\3\2\2\2\u0224\u0226\3")
        buf.write("\2\2\2\u0225\u0223\3\2\2\2\u0226\u0227\bD\2\2\u0227\u0088")
        buf.write("\3\2\2\2\24\2\u00d7\u00da\u00e0\u00e5\u00e9\u00ef\u00f7")
        buf.write("\u01da\u01ed\u01f5\u01f8\u01fd\u01ff\u0204\u020b\u0215")
        buf.write("\u0223\3\b\2\2")
        return buf.getvalue()


class QrogueDungeonLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    T__9 = 10
    T__10 = 11
    T__11 = 12
    T__12 = 13
    T__13 = 14
    T__14 = 15
    T__15 = 16
    T__16 = 17
    DIGIT = 18
    INTEGER = 19
    FLOAT = 20
    IMAG_NUMBER = 21
    SIGN = 22
    CHARACTER_LOW = 23
    CHARACTER_UP = 24
    CHARACTER = 25
    VISIBLE_LITERAL = 26
    FOGGY_LITERAL = 27
    OPEN_LITERAL = 28
    CLOSED_LITERAL = 29
    LOCKED_LITERAL = 30
    EVENT_LITERAL = 31
    PERMANENT_LITERAL = 32
    SPAWN_LITERAL = 33
    WILD_LITERAL = 34
    SHOP_LITERAL = 35
    RIDDLE_LITERAL = 36
    BOSS_LITERAL = 37
    GATE_ROOM_LITERAL = 38
    KEY_LITERAL = 39
    COIN_LITERAL = 40
    HEALTH_LITERAL = 41
    GATE_LITERAL = 42
    PLUS_SIGN = 43
    MINUS_SIGN = 44
    HEADER = 45
    ENDER = 46
    LAYOUT = 47
    ROOMS = 48
    HALLWAYS = 49
    STV_POOLS = 50
    REWARD_POOLS = 51
    HORIZONTAL_SEPARATOR = 52
    VERTICAL_SEPARATOR = 53
    LIST_SEPARATOR = 54
    WALL = 55
    EMPTY_HALLWAY = 56
    EMPTY_ROOM = 57
    DIRECTION = 58
    ORDERED_DRAW = 59
    RANDOM_DRAW = 60
    ROOM_ID = 61
    HALLWAY_ID = 62
    REFERENCE = 63
    WS = 64
    UNIVERSAL_SEPARATOR = 65
    COMMENT = 66
    LINE_COMMENT = 67

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "':'", "'('", "')'", "'c'", "'t'", "'e'", "'r'", "'$'", "'_'", 
            "'trigger'", "'one way'", "'entangled'", "'['", "']'", "'custom'", 
            "'default'", "'rewards'", "'visible'", "'foggy'", "'open'", 
            "'closed'", "'locked'", "'event'", "'permanent'", "'Spawn'", 
            "'Wild'", "'Shop'", "'Riddle'", "'Boss'", "'Gate'", "'key'", 
            "'coin'", "'health'", "'gate'", "'+'", "'-'", "'Qrogue<'", "'>Qrogue'", 
            "'[Layout]'", "'[Custom Rooms]'", "'[Hallways]'", "'[StateVector Pools]'", 
            "'[Reward Pools]'", "'~'", "'|'", "','", "'#'", "'..'", "'__'", 
            "'ordered'", "'random'" ]

    symbolicNames = [ "<INVALID>",
            "DIGIT", "INTEGER", "FLOAT", "IMAG_NUMBER", "SIGN", "CHARACTER_LOW", 
            "CHARACTER_UP", "CHARACTER", "VISIBLE_LITERAL", "FOGGY_LITERAL", 
            "OPEN_LITERAL", "CLOSED_LITERAL", "LOCKED_LITERAL", "EVENT_LITERAL", 
            "PERMANENT_LITERAL", "SPAWN_LITERAL", "WILD_LITERAL", "SHOP_LITERAL", 
            "RIDDLE_LITERAL", "BOSS_LITERAL", "GATE_ROOM_LITERAL", "KEY_LITERAL", 
            "COIN_LITERAL", "HEALTH_LITERAL", "GATE_LITERAL", "PLUS_SIGN", 
            "MINUS_SIGN", "HEADER", "ENDER", "LAYOUT", "ROOMS", "HALLWAYS", 
            "STV_POOLS", "REWARD_POOLS", "HORIZONTAL_SEPARATOR", "VERTICAL_SEPARATOR", 
            "LIST_SEPARATOR", "WALL", "EMPTY_HALLWAY", "EMPTY_ROOM", "DIRECTION", 
            "ORDERED_DRAW", "RANDOM_DRAW", "ROOM_ID", "HALLWAY_ID", "REFERENCE", 
            "WS", "UNIVERSAL_SEPARATOR", "COMMENT", "LINE_COMMENT" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "T__4", "T__5", "T__6", 
                  "T__7", "T__8", "T__9", "T__10", "T__11", "T__12", "T__13", 
                  "T__14", "T__15", "T__16", "DIGIT", "INTEGER", "FLOAT", 
                  "IMAG_NUMBER", "SIGN", "CHARACTER_LOW", "CHARACTER_UP", 
                  "CHARACTER", "VISIBLE_LITERAL", "FOGGY_LITERAL", "OPEN_LITERAL", 
                  "CLOSED_LITERAL", "LOCKED_LITERAL", "EVENT_LITERAL", "PERMANENT_LITERAL", 
                  "SPAWN_LITERAL", "WILD_LITERAL", "SHOP_LITERAL", "RIDDLE_LITERAL", 
                  "BOSS_LITERAL", "GATE_ROOM_LITERAL", "KEY_LITERAL", "COIN_LITERAL", 
                  "HEALTH_LITERAL", "GATE_LITERAL", "PLUS_SIGN", "MINUS_SIGN", 
                  "HEADER", "ENDER", "LAYOUT", "ROOMS", "HALLWAYS", "STV_POOLS", 
                  "REWARD_POOLS", "HORIZONTAL_SEPARATOR", "VERTICAL_SEPARATOR", 
                  "LIST_SEPARATOR", "WALL", "EMPTY_HALLWAY", "EMPTY_ROOM", 
                  "DIRECTION", "ORDERED_DRAW", "RANDOM_DRAW", "ROOM_ID", 
                  "HALLWAY_ID", "REFERENCE", "WS", "UNIVERSAL_SEPARATOR", 
                  "COMMENT", "LINE_COMMENT" ]

    grammarFileName = "QrogueDungeon.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


